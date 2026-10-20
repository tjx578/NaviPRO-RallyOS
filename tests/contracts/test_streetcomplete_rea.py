from pathlib import Path
import sys, json
import pytest
import yaml

ROOT=Path(__file__).resolve().parents[2]
sys.path.insert(0,str(ROOT/'python/src'))
from navipro_rallyos.survey.core import QUESTS,plan_survey_tasks,assess_version_conflict
from navipro_rallyos.survey.queue import ObservationQueue

SAMPLE_WAY={'element_type':'way','element_id':123456,'osm_version':7,
    'lat_e7':-86700000,'lon_e7':1152100000,'tags':{'highway':'residential','lanes':'2'}}
SAMPLE_OBS={
    'observation_id':'OBS-DEMO-001','task_id':'SVY-TEST-01','route_revision_id':'ROUTE-REV-001',
    'actor_id':'SURVEYOR-001','quest_type':'road_surface','answer':'asphalt',
    'observed_at':'2026-10-19T14:30:00+08:00',
    'osm_element_type':'way','osm_element_id':123456,'observed_osm_version':7,
    'lat_e7':-86700000,'lon_e7':1152100000, 'gps_accuracy_m':8.5,'evidence_sha256':'a'*64,
    'mode':'PREP','route_authority':False
}

def test_survey_registry_unique_prep_review_only():
    x=yaml.safe_load((ROOT/'contracts/spatial/streetcomplete-capability-registry.yaml').read_text())
    c=x['capabilities']
    assert len(c)>=55 and len({v['id'] for v in c})==len(c)
    assert all(v['allowed_modes']==['PREP','REVIEW'] and v['route_authority'] is False and v['osm_publish'] is False for v in c)
    assert all(v['implementation_status']=='MAPPED_NOT_PARITY_VERIFIED' for v in c)

def test_task_planning_deterministic_dedup_and_order():
    a=plan_survey_tasks([SAMPLE_WAY,SAMPLE_WAY], 'ROUTE-REV-001')
    b=plan_survey_tasks([SAMPLE_WAY], 'ROUTE-REV-001')
    assert a==b
    assert len(a)==len({t['task_id'] for t in a})
    assert all(x['route_revision_id']=='ROUTE-REV-001' and x['human_survey_required'] and x['authority']=='SURVEY_PROPOSAL_ONLY' for x in a)
    assert 'oneway' not in [x['quest_type'] for x in a]  # insufficient narrow-road topology evidence
    assert 'lanes' not in [x['quest_type'] for x in a]
    assert 'road_surface' in [x['quest_type'] for x in a]

def test_oneway_requires_width_lane_topology_evidence():
    hint={**SAMPLE_WAY,'tags':{'highway':'residential','width':'3.4','lanes':'1'},'candidate_flags':['both_ends_connected']}
    tasks=plan_survey_tasks([hint], 'REV-A')
    assert any(t['quest_type']=='oneway' for t in tasks)
    assert all(t['quest_type']!='oneway' for t in plan_survey_tasks([{**hint,'candidate_flags':[]}], 'REV-A'))

def test_skip_private_and_non_road():
    private={**SAMPLE_WAY,'tags':{'highway':'residential','access':'private'}}
    farmland={**SAMPLE_WAY,'tags':{'landuse':'farmland'}}
    assert plan_survey_tasks([private,farmland], 'REV')==[]

def test_bad_source_coordinates_and_version_fail_closed():
    with pytest.raises(ValueError):plan_survey_tasks([{**SAMPLE_WAY,'lat_e7':-8.67}], 'REV')
    with pytest.raises(ValueError):plan_survey_tasks([{**SAMPLE_WAY,'osm_version':None}], 'REV')
    with pytest.raises(ValueError):plan_survey_tasks([SAMPLE_WAY], 'REV', max_tasks=0)

def test_osm_conflict_versions_not_verify():
    assert assess_version_conflict(7,7)['status']=='REVIEW_REQUIRED'
    assert assess_version_conflict(7,8)['status']=='CONFLICT'
    assert assess_version_conflict(7,None)['status']=='HOLD'
    assert all(assess_version_conflict(7,x)['route_authority'] is False for x in (7,8,None))

def test_offline_queue_idempotent_and_staging_ack(tmp_path):
    q=ObservationQueue(tmp_path/'surveys.sqlite')
    rec=q.enqueue(SAMPLE_OBS)
    assert rec['status']=='PENDING_SYNC' and rec['route_authority'] is False
    assert q.enqueue(SAMPLE_OBS)['idempotent'] is True
    assert len(q.list_pending())==1
    staged=q.acknowledge_staging(SAMPLE_OBS['observation_id'],7,'SERVER-ACK-1')
    assert staged['status']=='STAGED_REVIEW' and staged['route_authority'] is False
    assert q.list_pending()==[]
    with pytest.raises(ValueError):q.acknowledge_staging(SAMPLE_OBS['observation_id'],7,'SERVER-ACK-2')
    q.close()

def test_offline_queue_conflict_and_unknown_versions(tmp_path):
    q=ObservationQueue(tmp_path/'queue.sqlite')
    q.enqueue(SAMPLE_OBS)
    assert q.acknowledge_staging(SAMPLE_OBS['observation_id'],9,'ACK-1')['status']=='CONFLICT'
    other={**SAMPLE_OBS,'observation_id':'OBS-2'}
    q.enqueue(other)
    assert q.acknowledge_staging('OBS-2',None,'ACK-2')['status']=='HOLD'
    q.close()

def test_offline_queue_rejects_payload_collision_and_unspecified_time(tmp_path):
    q=ObservationQueue(tmp_path/'queue.sqlite')
    q.enqueue(SAMPLE_OBS)
    with pytest.raises(ValueError):q.enqueue({**SAMPLE_OBS,'answer':'gravel'})
    with pytest.raises(ValueError):q.enqueue({**SAMPLE_OBS,'observation_id':'OBS-NAIVE','observed_at':'2026-10-19T14:30:00'})
    with pytest.raises(ValueError):q.enqueue({**SAMPLE_OBS,'observation_id':'OBS-LIVE','mode':'LIVE'})
    with pytest.raises(ValueError):q.enqueue({**SAMPLE_OBS,'observation_id':'OBS-AUTH','route_authority':True})
    q.close()

def test_field_survey_schema_never_live_or_authority():
    from jsonschema import Draft202012Validator, FormatChecker
    schema=json.loads((ROOT/'contracts/jsonschema/field-survey-observation.schema.json').read_text())
    Draft202012Validator.check_schema(schema)
    obs=json.loads((ROOT/'tests/fixtures/field-survey-observation.demo.json').read_text())
    v=Draft202012Validator(schema,format_checker=FormatChecker())
    assert list(v.iter_errors(obs))==[]
    assert list(v.iter_errors({**obs,'mode':'LIVE'}))
    assert list(v.iter_errors({**obs,'route_authority':True}))

def test_openapi_survey_mcp_policy_and_integration():
    spec=yaml.safe_load((ROOT/'contracts/openapi/navipro-rallyos.openapi.yaml').read_text())
    ops=[op for p,items in spec['paths'].items() if p.startswith('/survey/') for op in items.values()]
    assert len(ops)==12
    assert len({op['operationId'] for op in ops})==12
    assert all(op['x-navipro-mode']==['PREP','REVIEW'] for op in ops)
    assert all(op['x-navipro-side-effect']!='AUTHORITY_MUTATION' for op in ops if op['x-navipro-mcp']['enabled'])
    by_id={op['operationId']:op for op in ops}
    assert all(not by_id[oid]['x-navipro-mcp']['enabled'] for oid in ('captureSurveyObservation','commitSurveySync','decideSurveyEvidence'))

def test_survey_policy_safe_and_no_publish():
    policy=yaml.safe_load((ROOT/'governance/streetcomplete-field-survey-policy.yaml').read_text())
    assert policy['modes']['LIVE']['survey_app']=='DENY'
    assert policy['modes']['LIVE']['network_sync']=='DENY'
    assert policy['modes']['PREP']['agent_auto_capture']=='DENY'
    assert 'publish_osm_changeset' in policy['agent_denied_actions']

def test_generated_survey_task_matches_contract():
    from jsonschema import Draft202012Validator
    spec=yaml.safe_load((ROOT/'contracts/openapi/navipro-rallyos.openapi.yaml').read_text())
    schema=spec['components']['schemas']['SurveyTask']
    item=plan_survey_tasks([SAMPLE_WAY], 'REV-EXAMPLE')[0]
    from referencing import Registry, Resource
    registry=Registry().with_resource('urn:openapi:components', Resource.from_contents({'$schema':'https://json-schema.org/draft/2020-12/schema','$defs':spec['components']['schemas']}))
    # No nested remote refs required for our sample; inline resolved source schema.
    import copy
    local=copy.deepcopy(schema)
    local['properties']['source']=spec['components']['schemas']['SurveySourceRef']
    assert not list(Draft202012Validator(local).iter_errors(item))

def test_observation_draft_schema_matches_python_queue_fixture():
    from jsonschema import Draft202012Validator,FormatChecker
    spec=yaml.safe_load((ROOT/'contracts/openapi/navipro-rallyos.openapi.yaml').read_text())
    schema=spec['components']['schemas']['SurveyObservationDraft']
    v=Draft202012Validator(schema,format_checker=FormatChecker())
    assert not list(v.iter_errors(SAMPLE_OBS))
    assert list(v.iter_errors({**SAMPLE_OBS,'route_authority':True}))
