"""Provider-neutral *diagnostic* only; never sorts or approves roadbook routes."""
from __future__ import annotations

from typing import Any, Mapping
from .osrm_adapter import RouteCandidateError


def compare_provider_candidates(*, osrm: Mapping[str, Any] | None,
                                valhalla: Mapping[str, Any] | None,
                                official_distance_mm: int | None) -> dict[str, Any]:
    """Compare distance residuals without equating them with a passing rally route.

    Both providers MUST use the same graph_dataset_id and anchor source order;
    this does not prove identical OSM import/extraction or costing semantics.
    """
    if osrm is None and valhalla is None:
        raise RouteCandidateError('at least one provider result required')
    if official_distance_mm is not None and (type(official_distance_mm) is not int or official_distance_mm < 0):
        raise RouteCandidateError('official distance must be a nonnegative integer mm or null')
    provided = [(name, resp) for name, resp in (('OSRM', osrm), ('VALHALLA', valhalla)) if resp is not None]
    anchor_order = None
    dataset = None
    diagnostics = []
    for name, resp in provided:
        if not isinstance(resp, Mapping) or resp.get('route_authority') is not False or resp.get('mode') != 'PREP':
            raise RouteCandidateError('only PREP non-authoritative provider results can be compared')
        if resp.get('provider', 'OSRM' if name == 'OSRM' else None) != name:
            raise RouteCandidateError('provider result mismatch')
        order = resp.get('source_anchor_order')
        if not isinstance(order, list) or len(order) < 2:
            raise RouteCandidateError('source anchor order required')
        graph = resp.get('graph_dataset_id')
        if not isinstance(graph, str) or not graph:
            raise RouteCandidateError('graph dataset identity missing')
        if anchor_order is not None and order != anchor_order:
            raise RouteCandidateError('provider results use different source anchor order')
        if dataset is not None and graph != dataset:
            raise RouteCandidateError('provider graph dataset versions do not match')
        anchor_order, dataset = order, graph
        for candidate in resp.get('candidates', []):
            if not isinstance(candidate, Mapping) or candidate.get('route_authority') is not False:
                raise RouteCandidateError('authoritative candidate forbidden')
            mm = candidate.get('graph_distance_mm_candidate')
            if type(mm) is not int or mm < 0:
                raise RouteCandidateError('invalid graph distance')
            if candidate.get('source_anchor_order') != anchor_order:
                raise RouteCandidateError('candidate anchor order differs from source')
            diagnostics.append({
                'provider': name,
                'candidate_id': candidate.get('candidate_id'),
                'graph_distance_mm_candidate': mm,
                'distance_residual_mm': None if official_distance_mm is None else mm - official_distance_mm,
                'authority': 'CANDIDATE_ONLY',
            })
    return {'mode': 'REVIEW', 'route_authority': False, 'anchor_order': anchor_order,
            'graph_dataset_id': dataset, 'official_distance_mm_unchanged': official_distance_mm,
            'diagnostics': diagnostics,
            'status': 'NEEDS_ROADBOOK_TOPOLOGY_TIMING_AND_NAVIGATOR_REVIEW',
            'warnings': ['matching graph IDs are necessary but do not guarantee identical graph builds or profile costs',
                         'distance residual alone must never confirm, reject or reorder an official rally route']}
