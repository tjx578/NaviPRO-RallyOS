"""Fixture-only protocol tests: they do NOT imply a running Valhalla service."""
import pytest

from navipro_rallyos.route.osrm_adapter import RouteAnchor
from navipro_rallyos.route.valhalla_adapter import (
    ValhallaAdapter, ValhallaCandidateError, build_valhalla_matrix_request,
    build_valhalla_route_request, normalize_valhalla_matrix,
    normalize_valhalla_route, validate_valhalla_base_url,
)


ANCHORS = [RouteAnchor('A', -86749800, 1152041800), RouteAnchor('B', -86739900, 1152055000), RouteAnchor('C', -86722200, 1152110000)]
# Encoded polyline6 for two coordinates: (0,0) -> (0.001,0.001).
SHAPE = '??o}@o}@'
PROVENANCE = {
    'graph_dataset_id': 'osm-test',
    'profile_digest': 'auto-test',
    'valhalla_build': 'test-build',
}


def route_result(n=3):
    return {'trip': {'status': 0, 'units': 'kilometers',
                     'locations': [{'lat': a.lat_e7/1e7, 'lon': a.lon_e7/1e7,
                                    'original_index': i} for i, a in enumerate(ANCHORS[:n])],
                     'summary': {'length': 1.2, 'time': 120},
                     'legs': [{'shape': SHAPE, 'maneuvers': [{'type': 1, 'street_names': ['Jl. Jawa']}]} for _ in range(n-1)]}}


def matrix_result(n=3):
    return {'units': 'kilometers', 'sources_to_targets': [
        [{'from_index': i, 'to_index': j, 'distance': 0.0 if i==j else 1.125,
          'time': 0 if i==j else 360} for j in range(n)] for i in range(n)]}


def test_valhalla_route_order_and_break_through():
    p = build_valhalla_route_request(ANCHORS)
    assert p['locations'][1]['type'] == 'break_through'
    assert p['locations'][0]['type'] == p['locations'][-1]['type'] == 'break'
    assert p['costing'] == 'auto' and p['units'] == 'kilometers'
    assert [x['lat'] for x in p['locations']] == [a.lat_e7 / 1e7 for a in ANCHORS]


def test_valhalla_alternates_multipoint_fail_closed():
    with pytest.raises(ValhallaCandidateError):
        build_valhalla_route_request(ANCHORS, alternates=1)


def test_route_provenance_units_geometry_and_maneuvers():
    r = normalize_valhalla_route(route_result(), ANCHORS,
                                 graph_dataset_id='osm-bali-20261020', profile_digest='auto-abc', valhalla_build='v3-x')
    c = r['candidates'][0]
    assert c['graph_distance_mm_candidate'] == 1_200_000
    assert c['source_anchor_order'] == ['A', 'B', 'C']
    assert c['legs_count'] == 2
    assert c['geometry']['coordinates'][0] == [0.0, 0.0]
    assert c['geometry']['coordinates'][1] == [0.001, 0.001]
    assert c['provider_maneuvers_proposal'][0]['street_names'] == ['Jl. Jawa']
    assert not c['route_authority'] and r['graph_dataset_id'] == 'osm-bali-20261020'


def test_bad_units_rejected():
    r = route_result()
    r['trip']['units'] = 'miles'
    with pytest.raises(ValhallaCandidateError):
        normalize_valhalla_route(r, ANCHORS, graph_dataset_id='d', profile_digest='p', valhalla_build='v')


def test_legs_cannot_be_elided_or_reordered():
    r = route_result()
    r['trip']['legs'].pop()
    with pytest.raises(ValhallaCandidateError):
        normalize_valhalla_route(r, ANCHORS, graph_dataset_id='d', profile_digest='p', valhalla_build='v')


def test_nonfinite_distance_rejected():
    r = route_result()
    r['trip']['summary']['length'] = float('nan')
    with pytest.raises(ValhallaCandidateError):
        normalize_valhalla_route(r, ANCHORS, graph_dataset_id='d', profile_digest='p', valhalla_build='v')


def test_unsafe_polyline_rejected():
    r = route_result()
    r['trip']['legs'][0]['shape'] = '?'
    with pytest.raises(ValhallaCandidateError):
        normalize_valhalla_route(r, ANCHORS, graph_dataset_id='d', profile_digest='p', valhalla_build='v')


def test_matrix_dimensions_units_and_meters_to_mm():
    m = normalize_valhalla_matrix(matrix_result(), ANCHORS, **PROVENANCE)
    assert m['distances_mm_candidate'][0][1] == 1_125_000
    assert m['estimated_durations_s'][2][1] == 360.0
    assert m['unreachable_cells'] == []
    assert not m['route_authority']


def test_matrix_unreachable_remains_null():
    m = matrix_result()
    m['sources_to_targets'][0][2]['distance'] = None
    m['sources_to_targets'][0][2]['time'] = None
    out = normalize_valhalla_matrix(m, ANCHORS, **PROVENANCE)
    assert out['unreachable_cells'] == [[0, 2]]
    assert out['distances_mm_candidate'][0][2] is None


def test_matrix_reordered_index_rejected():
    m = matrix_result()
    m['sources_to_targets'][0][1]['from_index'] = 1
    with pytest.raises(ValhallaCandidateError):
        normalize_valhalla_matrix(m, ANCHORS, **PROVENANCE)


def test_matrix_half_missing_rejected():
    m = matrix_result()
    m['sources_to_targets'][0][1]['time'] = None
    with pytest.raises(ValhallaCandidateError):
        normalize_valhalla_matrix(m, ANCHORS, **PROVENANCE)


def test_prohibit_arbitrary_remote_endpoint():
    for uri in ('http://169.254.169.254', 'https://valhalla.openstreetmap.de',
                'http://localhost:8002/redirect', 'http://user:pw@localhost:8002'):
        with pytest.raises(ValhallaCandidateError):
            validate_valhalla_base_url(uri)


def test_mock_provider_transport_only():
    paths = []
    def fake(url, body):
        paths.append((url, body))
        return route_result()
    adapter = ValhallaAdapter(transport=fake)
    out = adapter.route(ANCHORS, graph_dataset_id='osm-version', profile_digest='auto-version', valhalla_build='build-version')
    assert out['provider'] == 'VALHALLA'
    assert paths[0][0] == 'http://127.0.0.1:8002/route'
    assert paths[0][1]['locations'][1]['type'] == 'break_through'


def test_provider_matrix_mock_transport():
    adapter = ValhallaAdapter(transport=lambda url, body: matrix_result())
    assert adapter.matrix(ANCHORS, **PROVENANCE)['provider'] == 'VALHALLA'


def test_native_alternate_endpoint_unimplemented_by_design():
    adapter = ValhallaAdapter(transport=lambda url, body: route_result(2))
    with pytest.raises(ValhallaCandidateError):
        adapter.route(ANCHORS[:2], graph_dataset_id='d', profile_digest='p', valhalla_build='v', alternates=1)


def test_matrix_request_preserves_order_no_optimization():
    p = build_valhalla_matrix_request(ANCHORS)
    assert len(p['sources']) == 3 and len(p['targets']) == 3
    assert 'optimized_route' not in p


def test_compare_providers_preserves_official_distance_and_order():
    from navipro_rallyos.route.provider_comparison import compare_provider_candidates
    val = normalize_valhalla_route(route_result(), ANCHORS,
                                   graph_dataset_id='osm-x', profile_digest='v-p', valhalla_build='v3')
    osrm = {'mode': 'PREP', 'route_authority': False, 'source_anchor_order': ['A', 'B', 'C'],
            'graph_dataset_id': 'osm-x',
            'candidates': [{'candidate_id': 'OSRM-CAND-001', 'route_authority': False,
                            'source_anchor_order': ['A', 'B', 'C'], 'graph_distance_mm_candidate': 1_250_000}]}
    d = compare_provider_candidates(osrm=osrm, valhalla=val, official_distance_mm=1_240_000)
    assert d['official_distance_mm_unchanged'] == 1_240_000
    assert d['diagnostics'][0]['distance_residual_mm'] == 10_000
    assert d['diagnostics'][1]['distance_residual_mm'] == -40_000
    assert d['status'].startswith('NEEDS_')


def test_compare_providers_reject_different_anchor_order():
    from navipro_rallyos.route.provider_comparison import compare_provider_candidates
    from navipro_rallyos.route.osrm_adapter import RouteCandidateError
    val = normalize_valhalla_route(route_result(), ANCHORS,
                                   graph_dataset_id='osm-x', profile_digest='v-p', valhalla_build='v3')
    osrm = {'mode': 'PREP', 'route_authority': False, 'source_anchor_order': ['C', 'B', 'A'],
            'graph_dataset_id': 'osm-x', 'candidates': []}
    with pytest.raises(RouteCandidateError):
        compare_provider_candidates(osrm=osrm, valhalla=val, official_distance_mm=1_200_000)


def test_compare_providers_reject_different_dataset():
    from navipro_rallyos.route.provider_comparison import compare_provider_candidates
    from navipro_rallyos.route.osrm_adapter import RouteCandidateError
    val = normalize_valhalla_route(route_result(), ANCHORS,
                                   graph_dataset_id='osm-x', profile_digest='v-p', valhalla_build='v3')
    osrm = {'mode': 'PREP', 'route_authority': False, 'source_anchor_order': ['A', 'B', 'C'],
            'graph_dataset_id': 'osm-y', 'candidates': []}
    with pytest.raises(RouteCandidateError):
        compare_provider_candidates(osrm=osrm, valhalla=val, official_distance_mm=1_200_000)


def test_bool_status_cannot_masquerade_as_success():
    r = route_result()
    r['trip']['status'] = False
    with pytest.raises(ValhallaCandidateError):
        normalize_valhalla_route(r, ANCHORS, graph_dataset_id='d', profile_digest='p', valhalla_build='v')


def test_invalid_returned_location_rejected():
    r = route_result()
    r['trip']['locations'][0]['lat'] = 120.0
    with pytest.raises(ValhallaCandidateError):
        normalize_valhalla_route(r, ANCHORS, graph_dataset_id='d', profile_digest='p', valhalla_build='v')
