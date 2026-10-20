from pathlib import Path
import json, math, sys, yaml
import pytest

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0,str(ROOT/'python/src'))
from navipro_rallyos.spatial.geodesy3d import (
 GeodeticWGS84,ECEF,WGS84_A_M,WGS84_B_M,
 wgs84_to_ecef,ecef_to_wgs84,geopoint_e7_to_wgs84,validate_height_observation
)

def test_cesium_capability_registry_is_unique_and_never_live():
    caps = yaml.safe_load((ROOT/'contracts/spatial/cesium-capability-registry.yaml').read_text())['capabilities']
    assert len(caps)>=65
    assert len({x['id'] for x in caps})==len(caps)
    assert all(x['allowed_modes']==['PREP','REVIEW'] for x in caps)
    assert all(x['authority']=='VISUAL_ANALYTIC_ONLY' and x['target_status']=='IMPLEMENTATION_PENDING' for x in caps)
    assert all(x['source_path'] and x['evidence_required'] for x in caps)

def test_cesium_project_snapshot_forbids_route_authority():
    s=json.loads((ROOT/'contracts/jsonschema/cesium-3d-project.schema.json').read_text())
    assert s['properties']['authority']['properties']['route_authority']['const'] is False
    assert s['properties']['height_policy']['properties']['terrain_height_is_authoritative']['const'] is False
    assert 'LIVE' not in s['properties']['mode']['enum']
    assert s['$defs']['asset']['properties']['authority']['const']=='VISUAL_ANALYTIC_ONLY'

def test_known_wgs84_equator_and_pole_vectors():
    assert wgs84_to_ecef(GeodeticWGS84(0,0,0)).x_m==WGS84_A_M
    assert abs(wgs84_to_ecef(GeodeticWGS84(0,90,0)).z_m-WGS84_B_M)<1e-7

def test_geodesy_roundtrip_terrestrial_points():
    for p in [GeodeticWGS84(115.2100,-8.6700,100.0),GeodeticWGS84(179.9,65.5,3900.5),GeodeticWGS84(-120.2,40.1,-50),GeodeticWGS84(0,0,0)]:
        q=ecef_to_wgs84(wgs84_to_ecef(p))
        assert abs(p.latitude_deg-q.latitude_deg)<1e-8
        assert abs(p.longitude_deg-q.longitude_deg)<1e-8
        assert abs(p.height_ellipsoid_m-q.height_ellipsoid_m)<0.002

def test_height_unknown_must_not_be_zero_or_promoted():
    with pytest.raises(ValueError):
        geopoint_e7_to_wgs84(lat_e7=-86700000,lon_e7=1152100000,height_ellipsoid_m=None)
    h=validate_height_observation(height_m=None, vertical_datum='UNKNOWN',provider_id='test-dem',source_sha256='a'*64,resolution_m=None)
    assert h['sample_status']=='NO_DATA' and h['height_m'] is None and h['route_authority'] is False
    h=validate_height_observation(height_m=125, vertical_datum='EGM96',provider_id='test-dem',source_sha256='b'*64,resolution_m=30)
    assert h['sample_status']=='SAMPLED' and h['eligible_for_authority_promotion'] is False

def test_vertical_datum_mismatch_is_rejected():
    with pytest.raises(ValueError):
        GeodeticWGS84(0,0,3,datum='EGM96')
    with pytest.raises(ValueError):
        ecef_to_wgs84(ECEF(0,0,0))
    with pytest.raises(TypeError):
        geopoint_e7_to_wgs84(lat_e7=-8.67,lon_e7=1152100000,height_ellipsoid_m=0)

def test_cesium_demo_snapshot_json_schema_roundtrip():
    from jsonschema import Draft202012Validator
    s=json.loads((ROOT/'contracts/jsonschema/cesium-3d-project.schema.json').read_text())
    Draft202012Validator.check_schema(s)
    fixture=json.loads((ROOT/'tests/fixtures/cesium-3d-project.demo.json').read_text())
    assert list(Draft202012Validator(s).iter_errors(fixture))==[]
    fixture['mode']='LIVE'
    assert list(Draft202012Validator(s).iter_errors(fixture))

def test_cesium_api_contract_tools_are_non_authoritative():
    spec=yaml.safe_load((ROOT/'contracts/openapi/navipro-rallyos.openapi.yaml').read_text())
    cesium=[v for path,item in spec['paths'].items() if path.startswith('/spatial3d/') for v in item.values()]
    assert len(cesium)==9
    assert all(op['x-navipro-mcp']['enabled'] and op['x-navipro-mode']==['PREP','REVIEW'] for op in cesium)
    assert all(op['x-navipro-side-effect']!='AUTHORITY_MUTATION' for op in cesium)
