"""Synthetic negative cases; proximity/continuity cannot certify real roads."""
import pytest

from navipro_rallyos.route.osrm_adapter import RouteAnchor
from navipro_rallyos.route.valhalla_adapter import ValhallaAdapter, ValhallaCandidateError, normalize_valhalla_route
from test_valhalla_rea import ANCHORS, PROVENANCE, encode_shape, route_result


def test_disconnected_legs_never_create_a_straight_bridge():
    response = route_result()
    near_b = RouteAnchor('offset', ANCHORS[1].lat_e7 + 100, ANCHORS[1].lon_e7)
    response['trip']['legs'][1]['shape'] = encode_shape([near_b, ANCHORS[2]])
    with pytest.raises(ValhallaCandidateError, match='disconnected'):
        normalize_valhalla_route(response, ANCHORS, **PROVENANCE)


def test_swapped_legs_cannot_claim_source_order():
    response = route_result()
    response['trip']['legs'].reverse()
    with pytest.raises(ValhallaCandidateError):
        normalize_valhalla_route(response, ANCHORS, **PROVENANCE)


def test_continuous_reversed_route_is_rejected_by_endpoint_binding():
    response = route_result()
    for i, pair in enumerate(([ANCHORS[2], ANCHORS[1]], [ANCHORS[1], ANCHORS[0]])):
        response['trip']['legs'][i]['shape'] = encode_shape(pair)
    with pytest.raises(ValhallaCandidateError, match='ordered anchors'):
        normalize_valhalla_route(response, ANCHORS, **PROVENANCE)


def test_continuous_geometry_in_wrong_region_is_rejected():
    response = route_result()
    wrong = [RouteAnchor(str(i), i * 10_000, i * 10_000) for i in range(3)]
    for i in range(2):
        response['trip']['legs'][i]['shape'] = encode_shape(wrong[i:i+2])
    with pytest.raises(ValhallaCandidateError, match='ordered anchors'):
        normalize_valhalla_route(response, ANCHORS, **PROVENANCE)


def test_close_snaps_allowed_but_not_physical_or_directed_verification():
    response = route_result()
    shifted = [RouteAnchor(a.anchor_id, a.lat_e7 + 100, a.lon_e7) for a in ANCHORS]
    for i in range(2):
        response['trip']['legs'][i]['shape'] = encode_shape(shifted[i:i+2])
    result = normalize_valhalla_route(response, ANCHORS, max_anchor_snap_m=5, **PROVENANCE)
    candidate = result['candidates'][0]
    assert not candidate['route_authority']
    assert candidate['geometry_diagnostics']['max_anchor_snap_m'] == 5
    assert candidate['geometry_diagnostics']['directed_traversal_status'] == 'NOT_VERIFIED'
    with pytest.raises(ValhallaCandidateError):
        normalize_valhalla_route(response, ANCHORS, max_anchor_snap_m=0, **PROVENANCE)


def test_repeated_point_and_loop_inside_a_leg_are_preserved():
    response = route_result()
    response['trip']['legs'][0]['shape'] = encode_shape([ANCHORS[0], ANCHORS[1], ANCHORS[0], ANCHORS[1]])
    result = normalize_valhalla_route(response, ANCHORS, **PROVENANCE)
    coords = result['candidates'][0]['geometry']['coordinates']
    assert len(coords) == 5
    assert coords[0] == coords[2] and coords[1] == coords[3]


@pytest.mark.parametrize('value', [True, None, -1, float('inf'), float('nan'), '50'])
def test_bad_snap_policy_rejected_before_io(value):
    calls = []
    adapter = ValhallaAdapter(transport=lambda *args: calls.append(args))
    with pytest.raises(ValhallaCandidateError, match='max_anchor_snap_m'):
        adapter.route(ANCHORS, mode='PREP', max_anchor_snap_m=value, **PROVENANCE)
    assert calls == []
