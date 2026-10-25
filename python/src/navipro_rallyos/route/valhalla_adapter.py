"""Clean-room Valhalla provider adapter for NaviPRO PREP/REVIEW only.

Source protocol: valhalla/valhalla docs/docs/api/route/api-reference.md and
matrix.md, audited against tjx578/valhalla-navipro@618cad5.
No live routing service or routing graph is shipped by this adapter.
"""
from __future__ import annotations

from decimal import Decimal, ROUND_HALF_UP
from math import asin, cos, isfinite, radians, sin, sqrt
from typing import Any, Callable, Mapping, Sequence
from urllib.parse import urlsplit

from .osrm_adapter import OSRMAdapter, RouteAnchor, RouteCandidateError, validate_anchors, require_routing_mode


class ValhallaCandidateError(RouteCandidateError):
    """Invalid Valhalla request, graph response, or candidate evidence."""


def _nonnegative_number(value: Any, field: str) -> Decimal:
    if isinstance(value, bool) or not isinstance(value, (float, int, Decimal)):
        raise ValhallaCandidateError(f'{field}: finite nonnegative number required')
    n = Decimal(str(value))
    if not n.is_finite() or n < 0:
        raise ValhallaCandidateError(f'{field}: invalid number')
    return n


def _distance_mm(km: Any) -> int:
    return int((_nonnegative_number(km, 'distance km') * 1_000_000).quantize(Decimal('1'), rounding=ROUND_HALF_UP))


def _validate_provenance(graph_dataset_id: str, profile_digest: str, valhalla_build: str) -> None:
    if not all(isinstance(s, str) and s.strip() for s in (graph_dataset_id, profile_digest, valhalla_build)):
        raise ValhallaCandidateError('dataset, costing profile and Valhalla build identities required')


def _provider_warnings(payload: Mapping[str, Any]) -> list[dict[str, Any]]:
    warnings = payload.get('warnings', [])
    if not isinstance(warnings, list) or any(not isinstance(w, Mapping) for w in warnings):
        raise ValhallaCandidateError('provider warnings must be an array of objects')
    return [dict(w) for w in warnings]


def build_valhalla_route_request(anchors: Sequence[RouteAnchor], *, alternates: int = 0) -> dict[str, Any]:
    """Preserve official input order. Intermediate break_through disallows U-turns.

    A distinct reviewed roadbook instruction must authorize any intentional U-turn;
    request construction itself does not attempt to infer these maneuvers.
    """
    ordered = validate_anchors(anchors)
    if type(alternates) is not int or not 0 <= alternates <= 2:
        raise ValhallaCandidateError('alternates must be integer 0-2')
    if len(ordered) > 2 and alternates:
        raise ValhallaCandidateError('Valhalla alternate routes unsupported for multipoint routes')
    locs = [{'lat': a.lat_e7 / 10_000_000,
             'lon': a.lon_e7 / 10_000_000,
             'type': 'break' if i in (0, len(ordered)-1) else 'break_through'}
            for i, a in enumerate(ordered)]
    return {'locations': locs, 'costing': 'auto', 'units': 'kilometers',
            'directions_type': 'maneuvers', 'alternates': alternates,
            'format': 'json', 'id': 'navipro-prep-candidate'}


def build_valhalla_matrix_request(anchors: Sequence[RouteAnchor]) -> dict[str, Any]:
    ordered = validate_anchors(anchors)
    locs = [{'lat': a.lat_e7 / 10_000_000, 'lon': a.lon_e7 / 10_000_000} for a in ordered]
    return {'sources': locs, 'targets': locs, 'costing': 'auto',
            'units': 'kilometers', 'verbose': True, 'id': 'navipro-review-matrix'}


def _decode_polyline6(shape: str) -> list[list[float]]:
    """Decode standard Valhalla polyline6 into GeoJSON [longitude, latitude]."""
    if not isinstance(shape, str) or not shape or len(shape) > 2_000_000:
        raise ValhallaCandidateError('encoded polyline6 missing or oversized')
    result: list[list[float]] = []
    lat = lon = pos = 0
    while pos < len(shape):
        coords = []
        for _ in range(2):
            shift = value = 0
            while True:
                if pos >= len(shape) or shift > 30:
                    raise ValhallaCandidateError('malformed polyline6')
                code = ord(shape[pos]) - 63
                pos += 1
                if not 0 <= code <= 63:
                    raise ValhallaCandidateError('invalid polyline6 byte')
                value |= (code & 31) << shift
                shift += 5
                if code < 32:
                    break
            coords.append((value >> 1) ^ (-(value & 1)))
        lat += coords[0]
        lon += coords[1]
        if abs(lat) > 90_000_000 or abs(lon) > 180_000_000:
            raise ValhallaCandidateError('polyline coordinate out of WGS84 bounds')
        result.append([lon / 1_000_000, lat / 1_000_000])
        if len(result) > 500_000:
            raise ValhallaCandidateError('polyline contains too many points')
    if len(result) < 2:
        raise ValhallaCandidateError('route geometry requires at least two points')
    return result


def _snap_limit(value: float) -> float:
    if isinstance(value, bool) or not isinstance(value, (int, float)) or not isfinite(value) or value < 0:
        raise ValhallaCandidateError('max_anchor_snap_m must be finite and nonnegative')
    return float(value)


def _endpoint_distance_m(point: list[float], anchor: RouteAnchor) -> float:
    """Spherical proximity diagnostic only; never a road distance or verification."""
    lon, lat = map(radians, point)
    target_lat = radians(anchor.lat_e7 / 10_000_000)
    target_lon = radians(anchor.lon_e7 / 10_000_000)
    h = sin((lat - target_lat) / 2) ** 2 + cos(lat) * cos(target_lat) * sin((lon - target_lon) / 2) ** 2
    return 2 * 6_371_008.8 * asin(sqrt(min(1.0, max(0.0, h))))


def normalize_valhalla_route(
    response: Mapping[str, Any], anchors: Sequence[RouteAnchor], *,
    graph_dataset_id: str, profile_digest: str, valhalla_build: str,
    max_anchor_snap_m: float = 50.0,
) -> dict[str, Any]:
    ordered = validate_anchors(anchors)
    snap_limit = _snap_limit(max_anchor_snap_m)
    _validate_provenance(graph_dataset_id, profile_digest, valhalla_build)
    if not isinstance(response, Mapping):
        raise ValhallaCandidateError('Valhalla returned an invalid response')
    trip = response.get('trip')
    if (not isinstance(trip, Mapping) or type(trip.get('status')) not in (int, str)
            or trip.get('status') not in (0, '0')):
        raise ValhallaCandidateError('Valhalla route did not succeed')
    if trip.get('units') != 'kilometers':
        raise ValhallaCandidateError('Valhalla response unit mismatch')
    locations = trip.get('locations')
    legs = trip.get('legs')
    if not isinstance(locations, list) or len(locations) != len(ordered):
        raise ValhallaCandidateError('route location count changed')
    for index, loc in enumerate(locations):
        if not isinstance(loc, Mapping) or any(
            k not in loc or isinstance(loc[k], bool) or not isinstance(loc[k], (float, int)) or not isfinite(loc[k])
            for k in ('lat','lon')
        ):
            raise ValhallaCandidateError('route location invalid')
        if abs(loc['lat']) > 90 or abs(loc['lon']) > 180:
            raise ValhallaCandidateError('route location outside WGS84 bounds')
        if type(loc.get('original_index')) is not int or loc['original_index'] != index:
            raise ValhallaCandidateError('route source location indices missing or reordered')
    # Valhalla may snap response locations to nearby edges. Do not compare snapped
    # coordinates to source anchors for identity: verify native original_index
    # before binding the response to immutable source-anchor IDs.
    if not isinstance(legs, list) or len(legs) != len(ordered)-1:
        raise ValhallaCandidateError('route leg count differs from ordered input anchors')
    summary = trip.get('summary')
    if not isinstance(summary, Mapping):
        raise ValhallaCandidateError('route summary missing')
    length_mm = _distance_mm(summary.get('length'))
    seconds = _nonnegative_number(summary.get('time'), 'travel seconds')
    lines: list[list[float]] = []
    maneuvers: list[dict[str, Any]] = []
    endpoint_residuals: list[dict[str, float | int]] = []
    for i, leg in enumerate(legs):
        if not isinstance(leg, Mapping):
            raise ValhallaCandidateError('route leg invalid')
        pts = _decode_polyline6(leg.get('shape'))
        # A LineString must not invent an unmeasured bridge between separate legs.
        # Require an identical shared polyline6 point, not an event tolerance.
        if lines and pts[0] != lines[-1]:
            raise ValhallaCandidateError(f'leg {i}: disconnected geometry')
        start_error = _endpoint_distance_m(pts[0], ordered[i])
        end_error = _endpoint_distance_m(pts[-1], ordered[i + 1])
        if start_error > snap_limit or end_error > snap_limit:
            raise ValhallaCandidateError(f'leg {i}: geometry endpoints do not match ordered anchors within snap policy')
        endpoint_residuals.append({'leg_index': i, 'start_m': start_error, 'end_m': end_error})
        # Remove only the duplicate join; preserve loops and repeated coordinates.
        lines.extend(pts if not lines else pts[1:])
        ms = leg.get('maneuvers')
        if not isinstance(ms, list):
            raise ValhallaCandidateError('route maneuvers missing')
        for m in ms:
            if not isinstance(m, Mapping) or type(m.get('type')) is not int:
                raise ValhallaCandidateError('invalid maneuver record')
            maneuvers.append({'leg_index': i, 'provider_type': m['type'],
                              'street_names': [s for s in m.get('street_names', []) if isinstance(s, str)]
                              if isinstance(m.get('street_names', []), list) else []})
    if len(lines) < 2:
        raise ValhallaCandidateError('decoded geometry is insufficient')
    return {
        'mode': 'PREP', 'route_authority': False, 'status': 'CANDIDATE_REVIEW',
        'provider': 'VALHALLA', 'graph_dataset_id': graph_dataset_id,
        'profile_digest': profile_digest, 'provider_build': valhalla_build,
        'source_anchor_order': [a.anchor_id for a in ordered],
        'candidates': [{
            'candidate_id': 'VALHALLA-CAND-001', 'source': 'VALHALLA',
            'route_authority': False, 'status': 'CANDIDATE_REVIEW',
            'source_anchor_order': [a.anchor_id for a in ordered],
            'graph_distance_mm_candidate': length_mm,
            'estimated_travel_seconds': float(seconds), 'legs_count': len(legs),
            'geometry': {'type': 'LineString', 'coordinates': lines},
            'geometry_diagnostics': {
                'leg_continuity': 'EXACT_POLYLINE6_JOIN',
                'max_anchor_snap_m': snap_limit,
                'endpoint_residuals_m': endpoint_residuals,
                'directed_traversal_status': 'NOT_VERIFIED',
            },
            'provider_maneuvers_proposal': maneuvers,
        }],
        'provider_warnings': _provider_warnings(trip),
        'warnings': ['Candidate only; official KM PAL and timing require separate solver & navigator approval',
                     'Provider turn maneuvers are suggestions, not authoritative roadbook instructions'],
    }


def normalize_valhalla_matrix(
    response: Mapping[str, Any], anchors: Sequence[RouteAnchor], *,
    graph_dataset_id: str, profile_digest: str, valhalla_build: str,
) -> dict[str, Any]:
    ordered = validate_anchors(anchors)
    _validate_provenance(graph_dataset_id, profile_digest, valhalla_build)
    if not isinstance(response, Mapping) or response.get('units') != 'kilometers':
        raise ValhallaCandidateError('Valhalla matrix units missing or not kilometers')
    n = len(ordered)
    rows = response.get('sources_to_targets')
    if not isinstance(rows, list) or len(rows) != n:
        raise ValhallaCandidateError('matrix row count mismatch')
    distances: list[list[int | None]] = []
    durations: list[list[float | None]] = []
    missing: list[list[int]] = []
    for i, row in enumerate(rows):
        if not isinstance(row, list) or len(row) != n:
            raise ValhallaCandidateError('matrix column count mismatch')
        drow: list[int | None] = []
        trow: list[float | None] = []
        for j, cell in enumerate(row):
            if not isinstance(cell, Mapping) or type(cell.get('from_index')) is not int or type(cell.get('to_index')) is not int or cell['from_index'] != i or cell['to_index'] != j:
                raise ValhallaCandidateError('matrix source/target indices reordered')
            if 'distance' not in cell or 'time' not in cell:
                raise ValhallaCandidateError('matrix distance and time fields required; null must be explicit')
            d, t = cell['distance'], cell['time']
            if (d is None) != (t is None):
                raise ValhallaCandidateError('partial unreachable cell not allowed')
            if d is None:
                missing.append([i, j])
                drow.append(None)
                trow.append(None)
            else:
                drow.append(_distance_mm(d))
                trow.append(float(_nonnegative_number(t, 'matrix time')))
        distances.append(drow)
        durations.append(trow)
    return {'mode': 'REVIEW', 'route_authority': False, 'provider': 'VALHALLA',
            'graph_dataset_id': graph_dataset_id, 'profile_digest': profile_digest,
            'provider_build': valhalla_build,
            'source_anchor_order': [a.anchor_id for a in ordered],
            'distances_mm_candidate': distances, 'estimated_durations_s': durations,
            'unreachable_cells': missing,
            'provider_warnings': _provider_warnings(response),
            'warnings': ['Matrix estimates are graph costs, not official rally distances/times']}


def validate_valhalla_base_url(base_url: str, *, allowed_hosts: frozenset[str] = frozenset({'127.0.0.1', 'localhost', '::1'})) -> str:
    p = urlsplit(base_url)
    if (p.scheme not in ('http', 'https') or not p.hostname or p.hostname not in allowed_hosts
        or p.username or p.password or p.query or p.fragment or p.path not in ('', '/')):
        raise ValhallaCandidateError('Valhalla endpoint must be a preapproved origin')
    return f'{p.scheme}://{p.netloc}'


class ValhallaAdapter:
    """Opt-in provider IO; default localhost only, no arbitrary external destinations.

    Reuses the already tested bounded, redirect-denying POST transport from the
    OSRM adapter. Production needs a trusted authenticated routing gateway.
    """
    def __init__(self, base_url: str = 'http://127.0.0.1:8002', *,
                 allowed_hosts: frozenset[str] = frozenset({'127.0.0.1', 'localhost', '::1'}),
                 transport: Callable[[str, dict[str, Any]], Mapping[str, Any]] | None = None):
        self.base_url = validate_valhalla_base_url(base_url, allowed_hosts=allowed_hosts)
        self.transport = transport or OSRMAdapter._http_transport

    def route(self, anchors: Sequence[RouteAnchor], *, graph_dataset_id: str,
              profile_digest: str, valhalla_build: str, mode: str, alternates: int = 0,
              max_anchor_snap_m: float = 50.0) -> dict[str, Any]:
        require_routing_mode(mode)
        _snap_limit(max_anchor_snap_m)
        if alternates:
            raise ValhallaCandidateError('alternate native trip normalization not enabled: review contract first')
        _validate_provenance(graph_dataset_id, profile_digest, valhalla_build)
        payload = build_valhalla_route_request(anchors, alternates=alternates)
        response = self.transport(self.base_url + '/route', payload)
        result = normalize_valhalla_route(response, anchors, graph_dataset_id=graph_dataset_id,
                                         profile_digest=profile_digest, valhalla_build=valhalla_build,
                                         max_anchor_snap_m=max_anchor_snap_m)
        result['mode'] = mode
        return result

    def matrix(self, anchors: Sequence[RouteAnchor], *, graph_dataset_id: str,
               profile_digest: str, valhalla_build: str, mode: str) -> dict[str, Any]:
        require_routing_mode(mode)
        _validate_provenance(graph_dataset_id, profile_digest, valhalla_build)
        payload = build_valhalla_matrix_request(anchors)
        response = self.transport(self.base_url + '/sources_to_targets', payload)
        result = normalize_valhalla_matrix(response, anchors, graph_dataset_id=graph_dataset_id,
                                          profile_digest=profile_digest, valhalla_build=valhalla_build)
        result['mode'] = mode
        return result
