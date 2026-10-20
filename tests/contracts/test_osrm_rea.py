from pathlib import Path
import sys
import pytest
import yaml
ROOT=Path(__file__).resolve().parents[2]
sys.path.insert(0,str(ROOT/'python/src'))
from navipro_rallyos.route.osrm_adapter import (RouteAnchor, RouteCandidateError, OSRMAdapter,
    build_route_payload,build_matrix_payload,build_match_payload,route_candidates,normalize_matrix,validate_osrm_base_url)

A=RouteAnchor('START',-86700000,1152100000)
B=RouteAnchor('MANDATORY-A',-86702000,1152300000)
C=RouteAnchor('FINISH',-86705000,1152500000)
ANCHORS=[A,B,C]
RESPONSE={'code':'Ok','data_version':'2026-09-01T00:00:00Z',
 'waypoints':[{'location':a.as_lonlat()} for a in ANCHORS],
 'routes':[{'distance':1234.567,'duration':200.2,
   'geometry':{'type':'LineString','coordinates':[a.as_lonlat() for a in ANCHORS]},
   'legs':[{},{}]}]}


def test_build_ordered_and_lonlat():
    p=build_route_payload(ANCHORS)
    assert p['coordinates']==[a.as_lonlat() for a in ANCHORS]
    assert p['geometries']=='geojson' and p['overview']=='full'
    assert p['generate_hints'] is False
    assert 'waypoints' not in p # no TSP reordering; all anchors mandatory


def test_route_candidates_preserve_source_order_and_candidate_only():
    out=route_candidates(RESPONSE,ANCHORS,graph_dataset_id='osm-bali-20260901',profile_digest='sha256:123')
    assert out['source_anchor_order']==['START','MANDATORY-A','FINISH']
    assert out['route_authority'] is False
    c=out['candidates'][0]
    assert c['source_anchor_order']==out['source_anchor_order']
    assert c['graph_distance_mm_candidate']==1_234_567
    assert c['route_authority'] is False and c['status']=='CANDIDATE_REVIEW'
    assert c['legs_count']==2
    assert out['osm_data_version']=='2026-09-01T00:00:00Z'


def test_missing_graph_identity_or_failed_osrm_response():
    with pytest.raises(RouteCandidateError):route_candidates(RESPONSE,ANCHORS,graph_dataset_id='',profile_digest='profile')
    with pytest.raises(RouteCandidateError):route_candidates({'code':'NoRoute'},ANCHORS,graph_dataset_id='g',profile_digest='p')


def test_missing_legs_or_geometry_fails_closed():
    for key,val in [('legs',[{}]),('geometry',None),('distance',float('nan'))]:
        result={**RESPONSE,'routes':[{**RESPONSE['routes'][0],key:val}]}
        with pytest.raises(RouteCandidateError):route_candidates(result,ANCHORS,graph_dataset_id='g',profile_digest='p')


def test_route_rejects_invalid_source_and_duplicate_anchor():
    with pytest.raises(RouteCandidateError):RouteAnchor('x',1.1,2)
    with pytest.raises(RouteCandidateError):RouteAnchor('x',True,0)
    with pytest.raises(RouteCandidateError):RouteAnchor('',0,0)
    with pytest.raises(RouteCandidateError):build_route_payload([A,A])
    with pytest.raises(RouteCandidateError):build_route_payload([A])


def test_matrix_no_fallback_and_no_route_cells():
    m={'code':'Ok','distances':[[0,12,None],[21,0,30],[None,33,0]],'durations':[[0,3,None],[4,0,5],[None,6,0]]}
    out=normalize_matrix(m,ANCHORS)
    assert out['unreachable_cells']==[[0,2],[2,0]]
    assert out['route_authority'] is False
    with pytest.raises(RouteCandidateError):normalize_matrix({**m,'fallback_speed_cells':[[0,2]]},ANCHORS)
    assert 'fallback_speed' not in build_matrix_payload(ANCHORS)


def test_matrix_shape_invalid():
    with pytest.raises(RouteCandidateError):normalize_matrix({'code':'Ok','distances':[[1]],'durations':[[1]]},ANCHORS)


def test_gps_match_strict_timestamps_accuracy():
    p=build_match_payload(ANCHORS,[100,105,109],[3.,4.,5.])
    assert p['gaps']=='split' and p['tidy'] is False
    with pytest.raises(RouteCandidateError):build_match_payload(ANCHORS,[100,105,105],[3,4,5])
    with pytest.raises(RouteCandidateError):build_match_payload(ANCHORS,[100,105,109],[3,0,5])
    with pytest.raises(RouteCandidateError):build_match_payload(ANCHORS,[100,105],[3,4])


def test_osrm_client_injected_http_keeps_route_prep_only():
    requested=[]
    def fake(url,payload):requested.append((url,payload));return RESPONSE
    adapter=OSRMAdapter(transport=fake)
    out=adapter.route(ANCHORS,'bali-graph','sha256:foo',mode='PREP')
    assert requested[0][0]=='http://127.0.0.1:5000/route/v1/driving'
    assert out['route_authority'] is False
    assert requested[0][1]['coordinates']==[a.as_lonlat() for a in ANCHORS]


def test_client_match_outliers_no_verification():
    def fake(url,payload):return {'code':'Ok','tracepoints':[{'foo':1},None,{'foo':2}],'matchings':[{'confidence':0.8}]}
    out=OSRMAdapter(transport=fake).match(ANCHORS,[101,102,103],[4,5,6],mode='REVIEW')
    assert out['status']=='MATCH_PROPOSAL_ONLY' and out['outlier_indices']==[1]
    assert out['route_authority'] is False


def test_url_allowlist_and_no_embedded_credentials():
    assert validate_osrm_base_url('http://127.0.0.1:5000')=='http://127.0.0.1:5000'
    for url in ['https://evil.net','file:///etc/passwd','http://localhost:5000/a','http://user:pw@localhost:5000','http://localhost:5000?next=evil','http://localhost:5000#fragment']:
        with pytest.raises(RouteCandidateError):validate_osrm_base_url(url)


def test_contract_mcp_restrictions_no_trip():
    spec=yaml.safe_load((ROOT/'contracts/openapi/navipro-rallyos.openapi.yaml').read_text())
    routing=[(p,m,op) for p,path in spec['paths'].items() if p.startswith('/routing/') for m,op in path.items()]
    assert len(routing)>=8
    assert not any('/trip' in p or 'tripOptimize' in op['operationId'] for p,m,op in routing)
    for p,m,op in routing:
        assert op['x-navipro-mode']==['PREP','REVIEW']
        assert op['x-navipro-authority'] in ('READ','AGENT_PROPOSE','SYSTEM')
        assert op['x-navipro-side-effect']!='AUTHORITY_MUTATION'
        assert op['x-navipro-mcp']['enabled'] is True


def test_source_registry_unique_and_no_live():
    x=yaml.safe_load((ROOT/'contracts/routing/osrm-capability-registry.yaml').read_text())
    capabilities=x['capabilities']
    assert len(capabilities)>=30
    assert len({c['id'] for c in capabilities})==len(capabilities)
    assert all(c['authority']=='CANDIDATE_ONLY' and c['modes']==['PREP','REVIEW'] for c in capabilities)
    assert x['forbidden_automatic_actions']
    assert 'trip' in x['forbidden_automatic_actions']
