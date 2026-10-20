"""Native-response boundary regressions; no routing service is contacted."""
import pytest

from test_valhalla_rea import ANCHORS, PROVENANCE, matrix_result, route_result
from navipro_rallyos.route.valhalla_adapter import (
    ValhallaAdapter,
    ValhallaCandidateError,
    normalize_valhalla_matrix,
    normalize_valhalla_route,
)


def test_reversed_native_locations_cannot_claim_original_anchor_order():
    response = route_result()
    response['trip']['locations'].reverse()
    with pytest.raises(ValhallaCandidateError, match='indices'):
        normalize_valhalla_route(response, ANCHORS, **PROVENANCE)


@pytest.mark.parametrize('index', [None, True, '1', 0, -1, 3])
def test_location_identity_requires_exact_integer_source_index(index):
    response = route_result()
    response['trip']['locations'][1]['original_index'] = index
    with pytest.raises(ValhallaCandidateError, match='indices'):
        normalize_valhalla_route(response, ANCHORS, **PROVENANCE)


def test_missing_location_identity_is_rejected():
    response = route_result()
    del response['trip']['locations'][1]['original_index']
    with pytest.raises(ValhallaCandidateError, match='indices'):
        normalize_valhalla_route(response, ANCHORS, **PROVENANCE)


def test_snapped_coordinates_do_not_replace_source_identity():
    response = route_result()
    response['trip']['locations'][1]['lat'] += 0.00001
    result = normalize_valhalla_route(response, ANCHORS, **PROVENANCE)
    assert result['source_anchor_order'] == ['A', 'B', 'C']
    assert result['route_authority'] is False


@pytest.mark.parametrize('missing', [('distance',), ('time',), ('distance', 'time')])
def test_missing_matrix_fields_are_not_unreachable_evidence(missing):
    response = matrix_result()
    cell = response['sources_to_targets'][0][1]
    cell.update(distance=None, time=None)
    for key in missing:
        del cell[key]
    with pytest.raises(ValhallaCandidateError, match='fields required'):
        normalize_valhalla_matrix(response, ANCHORS, **PROVENANCE)


@pytest.mark.parametrize('kind', ['route', 'matrix'])
def test_native_provider_warnings_are_preserved(kind):
    response = route_result() if kind == 'route' else matrix_result()
    payload = response['trip'] if kind == 'route' else response
    warnings = [{'code': 999, 'description': 'Synthetic protocol warning'}]
    payload['warnings'] = warnings
    normalizer = normalize_valhalla_route if kind == 'route' else normalize_valhalla_matrix
    result = normalizer(response, ANCHORS, **PROVENANCE)
    assert result['provider_warnings'] == warnings
    assert result['route_authority'] is False


@pytest.mark.parametrize('kind', ['route', 'matrix'])
@pytest.mark.parametrize('warnings', [None, {}, ['invalid warning']])
def test_malformed_warnings_are_not_silently_discarded(kind, warnings):
    response = route_result() if kind == 'route' else matrix_result()
    payload = response['trip'] if kind == 'route' else response
    payload['warnings'] = warnings
    normalizer = normalize_valhalla_route if kind == 'route' else normalize_valhalla_matrix
    with pytest.raises(ValhallaCandidateError, match='warnings'):
        normalizer(response, ANCHORS, **PROVENANCE)


@pytest.mark.parametrize('method', ['route', 'matrix'])
@pytest.mark.parametrize('field', list(PROVENANCE))
def test_missing_provenance_is_rejected_before_transport(method, field):
    calls = []

    def transport(url, body):
        calls.append(url)
        return route_result() if method == 'route' else matrix_result()

    provenance = {**PROVENANCE, field: ''}
    adapter = ValhallaAdapter(transport=transport)
    with pytest.raises(ValhallaCandidateError, match='identities required'):
        getattr(adapter, method)(ANCHORS, **provenance)
    assert calls == []


def test_matrix_preserves_declared_build_and_graph_provenance():
    adapter = ValhallaAdapter(transport=lambda url, body: matrix_result())
    result = adapter.matrix(ANCHORS, **PROVENANCE)
    assert result['graph_dataset_id'] == PROVENANCE['graph_dataset_id']
    assert result['profile_digest'] == PROVENANCE['profile_digest']
    assert result['provider_build'] == PROVENANCE['valhalla_build']
    assert result['source_anchor_order'] == ['A', 'B', 'C']
    assert result['provider_warnings'] == []
    assert result['route_authority'] is False


@pytest.mark.parametrize('field', list(PROVENANCE))
def test_matrix_normalizer_itself_rejects_missing_provenance(field):
    with pytest.raises(ValhallaCandidateError, match='identities required'):
        normalize_valhalla_matrix(matrix_result(), ANCHORS, **{**PROVENANCE, field: None})
