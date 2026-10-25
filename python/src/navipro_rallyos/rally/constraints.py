"""Diagnostic constraint evaluation. No shortest-route choice or confirmation."""
from collections import Counter
from typing import Any, Mapping

from .roadbook import RoadbookError


def evaluate_roadbook(roadbook: Mapping[str, Any], source: Mapping[str, Any]) -> dict[str, Any]:
    sections = roadbook['sections']
    distance_sections = [s for s in sections if s['d_auth_mm'] is not None]
    distance = sum(s['d_auth_mm'] for s in distance_sections)
    duration = sum(s['t_auth_ms'] for s in sections)
    declared_distance = source.get('declared_distance_mm')
    declared_duration = source.get('declared_duration_ms')
    if any(value is not None and (type(value) is not int or value < 0)
           for value in (declared_distance, declared_duration)):
        raise RoadbookError('declared totals must be nonnegative integer units')
    arithmetic = ('ARITHMETIC_UNVERIFIED' if None in (declared_distance, declared_duration)
                  else 'ARITHMETIC_VALID' if (distance, duration) == (declared_distance, declared_duration)
                  else 'ARITHMETIC_MISMATCH')
    return {
        'status': 'ROUTE_UNRESOLVED', 'route_authority': False,
        'arithmetic_status': arithmetic,
        'distance_sections': [s['section_id'] for s in distance_sections],
        'total_declared_leg_distance_mm': distance, 'total_duration_ms': duration,
        'source_text_sha256': roadbook['source_text_sha256'],
        'operator_confirmed': source.get('operator_confirmed') is True,
        'timing_rule_status': 'NOT_VERIFIED',
        'unresolved_inline_distances': [
            {'section_id': s['section_id'], **ref}
            for s in sections for ref in s['inline_distance_references']
        ],
        'uncertainties': list(source.get('uncertainties', [])),
        'provider_benchmark_status': 'NOT_EXECUTED',
        'sections': sections,
    }


def assess_candidate(section: Mapping[str, Any], candidate: Mapping[str, Any],
                     traversal_evidence: Mapping[str, Any] | None = None) -> dict[str, Any]:
    """Require separate occurrence evidence; copied request IDs are not traversal proof.

    An observation can expose missing/reordered occurrences, but never grants route
    authority. Physical access, scoring rules and navigator approval remain open.
    """
    distance = candidate.get('graph_distance_mm_candidate')
    if type(distance) is not int or distance < 0 or candidate.get('route_authority') is not False:
        raise RoadbookError('non-authoritative candidate with integer graph distance required')
    required = [i['instruction_id'] for i in section['instructions']]
    observed = None if traversal_evidence is None else traversal_evidence.get('observed_instruction_ids')
    evidence_ref = None if traversal_evidence is None else traversal_evidence.get('evidence_ref')
    if observed is not None and (not isinstance(observed, list) or not all(isinstance(x, str) for x in observed)):
        raise RoadbookError('traversal occurrence IDs must be a list of strings')
    missing = list((Counter(required) - Counter(observed)).elements()) if observed is not None else None
    coverage = ('NOT_MEASURED' if observed is None or not isinstance(evidence_ref, str) or not evidence_ref.strip()
                else 'ORDER_AND_OCCURRENCES_RECORDED' if observed == required
                else 'ORDER_OR_COVERAGE_MISMATCH')
    return {
        'status': 'ROUTE_UNRESOLVED', 'route_authority': False,
        'section_id': section['section_id'],
        'candidate_id': candidate.get('candidate_id'),
        'd_auth_mm': section['d_auth_mm'], 'd_graph_mm': distance,
        'distance_residual_mm': None if section['d_auth_mm'] is None else distance - section['d_auth_mm'],
        't_auth_ms': section['t_auth_ms'],
        'provider_eta_seconds': candidate.get('estimated_travel_seconds'),
        'timing_mode': section['timing_mode'],
        'timing_rule_status': 'NOT_VERIFIED',
        'instruction_coverage': coverage, 'missing_instruction_occurrences': missing,
        'physical_location_status': 'UNRESOLVED', 'access_point_status': 'UNRESOLVED',
        'uncertainty_requires_navigator': True,
    }
