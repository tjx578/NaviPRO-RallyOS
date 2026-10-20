from pathlib import Path
import sys
import copy
import pytest
import yaml
from jsonschema import Draft202012Validator

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / 'python/src'))
from navipro_rallyos.context.fusion import assess_layers, plan_scene, ContextGateError

CATALOG = {
  'weather-bali': {'kind':'WEATHER_OBSERVED', 'terms_approved':True, 'data_rights_reviewed':True, 'max_age_seconds':1800, 'attribution':'Example provider / test fixture'},
  'terrain-bali': {'kind':'TERRAIN', 'terms_approved':True, 'data_rights_reviewed':True, 'max_age_seconds':365*86400, 'attribution':'Test terrain source'},
  'forecast-bali': {'kind':'WEATHER_FORECAST', 'terms_approved':True, 'data_rights_reviewed':True, 'max_age_seconds':3600, 'attribution':'Example forecast fixture'},
}
TRUST = {'route_revision_id':'RR-009','official_anchor_ids':['START','KM-PAL-1','FINISH']}
NOW = '2026-10-20T05:00:00Z'
WEATHER = {'source_id':'weather-bali', 'kind':'WEATHER_OBSERVED', 'observed_at':'2026-10-20T04:50:00Z'}
SCENE = {'mode':'REVIEW','route_revision_id':'RR-009','official_anchor_ids':['START','KM-PAL-1','FINISH'],'layers':[WEATHER]}


def test_valid_scene_preserves_authoritative_anchor_order():
    result=plan_scene(SCENE,trusted_route_snapshot=TRUST,trusted_catalog=CATALOG,as_of=NOW)
    assert result['status']=='DRAFT_CONTEXT_SCENE'
    assert result['route_authority'] is False and result['confirmed'] is False
    assert result['official_anchor_ids']==TRUST['official_anchor_ids']
    result['official_anchor_ids'].reverse()
    assert TRUST['official_anchor_ids']==['START','KM-PAL-1','FINISH']


def test_staleness_is_visible_without_inventing_verified_truth():
    out=assess_layers([WEATHER,{**WEATHER,'source_id':'terrain-bali','kind':'TERRAIN','observed_at':'2026-01-01T00:00:00Z'}],trusted_catalog=CATALOG,as_of=NOW)
    assert [x['freshness'] for x in out['layers']]==['CURRENT','CURRENT']
    stale=assess_layers([{**WEATHER,'observed_at':'2026-10-20T04:00:00Z'}],trusted_catalog=CATALOG,as_of=NOW)
    assert stale['layers'][0]['freshness']=='STALE'
    assert stale['layers'][0]['route_authority'] is False


def test_forecast_validity_and_issuance():
    valid={'source_id':'forecast-bali','kind':'WEATHER_FORECAST','observed_at':'2026-10-20T04:30:00Z','issued_at':'2026-10-20T04:10:00Z','valid_until':'2026-10-20T06:00:00Z'}
    assert assess_layers([valid],trusted_catalog=CATALOG,as_of=NOW)['layers'][0]['freshness']=='CURRENT'
    assert assess_layers([{**valid,'valid_until':'2026-10-20T04:45:00Z'}],trusted_catalog=CATALOG,as_of=NOW)['layers'][0]['freshness']=='STALE'
    for bad in [{**valid,'issued_at':'2026-10-20T07:00:00Z'}, {**valid,'valid_until':'2026-10-20T03:00:00Z'}, {k:v for k,v in valid.items() if k!='issued_at'}]:
        with pytest.raises(ContextGateError): assess_layers([bad],trusted_catalog=CATALOG,as_of=NOW)


def test_live_and_revision_anchor_mutation_rejected():
    for update in [{'mode':'LIVE'},{'route_revision_id':'RR-OLD'}, {'official_anchor_ids':['FINISH','KM-PAL-1','START']}, {'official_anchor_ids':['START','FINISH']}, {'confirmed':True}, {'publish':True}]:
        with pytest.raises(ContextGateError):plan_scene({**SCENE,**update},trusted_route_snapshot=TRUST,trusted_catalog=CATALOG,as_of=NOW)


def test_sensitive_tracking_and_extra_fields_rejected():
    for kind in ('PERSON_TRACKING','ALPR','CCTV','INDIVIDUAL_VEHICLE_TRACKING','MILITARY_ASSET_TRACKING','REALTIME_SUBJECT_FOCUS'):
        with pytest.raises(ContextGateError):assess_layers([{**WEATHER,'kind':kind}],trusted_catalog=CATALOG,as_of=NOW)
    for field, value in [('route_authority',True),('url','http://localhost/internal'),('coordinates',[115.1,-8.5]),('publish',False)]:
        with pytest.raises(ContextGateError):assess_layers([{**WEATHER,field:value}],trusted_catalog=CATALOG,as_of=NOW)


def test_source_catalog_is_trusted_and_rights_required():
    for catalog in ({}, {'weather-bali':{**CATALOG['weather-bali'],'terms_approved':False}}, {'weather-bali':{**CATALOG['weather-bali'],'data_rights_reviewed':False}}, {'weather-bali':{**CATALOG['weather-bali'],'attribution':''}}):
        with pytest.raises(ContextGateError):assess_layers([WEATHER],trusted_catalog=catalog,as_of=NOW)


def test_reject_future_naive_and_invalid_timestamp():
    for timestamp in ['2026-10-20T05:00:01Z','2026-10-20T05:00:00','invalid','']:
        with pytest.raises(ContextGateError):assess_layers([{**WEATHER,'observed_at':timestamp}],trusted_catalog=CATALOG,as_of=NOW)


def test_duplicate_sources_and_layer_count_limit():
    with pytest.raises(ContextGateError):assess_layers([WEATHER,WEATHER],trusted_catalog=CATALOG,as_of=NOW)
    with pytest.raises(ContextGateError):assess_layers([WEATHER]*101,trusted_catalog=CATALOG,as_of=NOW)


def test_catalog_cannot_be_self_certified_through_request():
    with pytest.raises(ContextGateError):plan_scene({**SCENE,'trusted_catalog':CATALOG},trusted_route_snapshot=TRUST,trusted_catalog={},as_of=NOW)


def test_openapi_schema_and_mcp_policy():
    spec=yaml.safe_load((ROOT/'contracts/openapi/navipro-rallyos.openapi.yaml').read_text())
    for path in ['/context-fusion/capabilities','/context-fusion/layers/assess','/context-fusion/scenes/plan']:
        meth=next(iter(spec['paths'][path]));o=spec['paths'][path][meth]
        assert o['x-navipro-mode']==['PREP','REVIEW']
        assert o['x-navipro-side-effect']=='NONE'
        assert o['x-navipro-mcp']['enabled'] is True
        assert o['x-navipro-authority']=='READ'
    for schema in spec['components']['schemas'].values():
        if isinstance(schema,dict): Draft202012Validator.check_schema(schema)
    payload=spec['components']['schemas']['ContextScenePlanRequest']
    assert payload['additionalProperties'] is False
    assert payload['properties']['mode']['enum']==['PREP','REVIEW']


def test_response_schema_accepts_valid_result_and_rejects_authority():
    spec=yaml.safe_load((ROOT/'contracts/openapi/navipro-rallyos.openapi.yaml').read_text())
    schemas=spec['components']['schemas']
    v=Draft202012Validator({
        '$schema':'https://json-schema.org/draft/2020-12/schema',
        'components': {'schemas':schemas},
        '$ref':'#/components/schemas/ContextScenePlanResult',
    })
    result=plan_scene(SCENE,trusted_route_snapshot=TRUST,trusted_catalog=CATALOG,as_of=NOW)
    assert not list(v.iter_errors(result))
    bad={**result,'route_authority':True}
    assert list(v.iter_errors(bad))


def test_registry_has_32_grounded_capabilities_and_no_live():
    reg=yaml.safe_load((ROOT/'contracts/spatial/gods-eye-capability-registry.yaml').read_text())
    assert len(reg['capabilities'])==32
    assert len({x['id'] for x in reg['capabilities']})==32
    assert all(x['source_url'].startswith('https://github.com/tjx578/gods-eye-view-maps/blob/') and x['modes']==['PREP','REVIEW'] and x['authority']=='CONTEXT_ONLY' for x in reg['capabilities'])
    assert reg['adoption_policy']['driver_live'] is False
