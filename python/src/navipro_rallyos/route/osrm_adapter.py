"""NaviPRO OSRM PREP/REVIEW adapter (clean-room).

Never confirms official RallyOS routes. OSRM optimizes graph cost, not roadbook truth.
No network is needed to construct or validate requests/responses.
"""
from __future__ import annotations

from dataclasses import dataclass
from decimal import Decimal, ROUND_HALF_UP
import ipaddress
import json
import math
from typing import Any, Callable, Mapping, Sequence
from urllib.parse import urlsplit, urlencode
from urllib.request import Request, build_opener, HTTPRedirectHandler


class RouteCandidateError(ValueError):
    """Input, graph, or provider result not suitable even for a route candidate."""


def require_routing_mode(mode: str) -> None:
    """Reject untrusted/missing execution modes before any provider IO.

    This enforces the adapter API boundary, not caller authentication.
    """
    if not isinstance(mode, str) or mode not in ('PREP', 'REVIEW'):
        raise RouteCandidateError('routing providers accept PREP or REVIEW only')


@dataclass(frozen=True)
class RouteAnchor:
    anchor_id: str
    lat_e7: int
    lon_e7: int

    def __post_init__(self):
        if not isinstance(self.anchor_id, str) or not self.anchor_id.strip():
            raise RouteCandidateError('anchor_id required')
        if type(self.lat_e7) is not int or abs(self.lat_e7) > 900_000_000:
            raise RouteCandidateError('lat_e7 must be integer in [-90,90] degrees')
        if type(self.lon_e7) is not int or abs(self.lon_e7) > 1_800_000_000:
            raise RouteCandidateError('lon_e7 must be integer in [-180,180] degrees')

    def as_lonlat(self) -> list[float]:
        return [self.lon_e7 / 10_000_000, self.lat_e7 / 10_000_000]


def validate_anchors(anchors: Sequence[RouteAnchor]) -> tuple[RouteAnchor, ...]:
    if not isinstance(anchors, (list, tuple)) or not 2 <= len(anchors) <= 100:
        raise RouteCandidateError('2-100 ordered anchors required')
    if not all(isinstance(a, RouteAnchor) for a in anchors):
        raise RouteCandidateError('anchor must be RouteAnchor')
    if len({a.anchor_id for a in anchors}) != len(anchors):
        raise RouteCandidateError('duplicate anchor_id')
    return tuple(anchors)


def build_route_payload(anchors: Sequence[RouteAnchor]) -> dict[str, Any]:
    ordered = validate_anchors(anchors)
    return {
        'coordinates': [a.as_lonlat() for a in ordered],
        'steps': True,
        'geometries': 'geojson',
        'overview': 'full',  # no simplified geometry accepted for NaviPRO review
        'annotations': ['distance', 'duration', 'nodes'],
        'alternatives': True,
        'generate_hints': False,
    }


def build_matrix_payload(anchors: Sequence[RouteAnchor]) -> dict[str, Any]:
    ordered = validate_anchors(anchors)
    # No fallback_speed: straight-line estimation must not silently fill NoRoute cells.
    return {'coordinates': [a.as_lonlat() for a in ordered],
            'annotations': ['distance', 'duration'], 'generate_hints': False}


def build_match_payload(anchors: Sequence[RouteAnchor], timestamps: Sequence[int], accuracies_m: Sequence[float]) -> dict[str, Any]:
    ordered = validate_anchors(anchors)
    if len(timestamps) != len(ordered) or len(accuracies_m) != len(ordered):
        raise RouteCandidateError('timestamp/accuracy must match coordinates')
    if any(type(t) is not int for t in timestamps) or any(b <= a for a,b in zip(timestamps,timestamps[1:])):
        raise RouteCandidateError('timestamps must be strictly increasing integers')
    if any(isinstance(x,bool) or not isinstance(x,(float,int)) or not math.isfinite(x) or x <= 0 for x in accuracies_m):
        raise RouteCandidateError('GPS accuracies must be positive finite meters')
    return {'coordinates':[a.as_lonlat() for a in ordered], 'timestamps':list(timestamps),
            'radiuses':list(accuracies_m),'gaps':'split','tidy':False,
            'steps':False,'geometries':'geojson','overview':'full', 'generate_hints':False}


def _positive_distance_mm(value: Any) -> int:
    if isinstance(value, bool) or not isinstance(value, (int,float)) or not math.isfinite(value) or value < 0:
        raise RouteCandidateError('distance invalid/missing in OSRM result')
    return int((Decimal(str(value)) * 1000).quantize(Decimal('1'),rounding=ROUND_HALF_UP))


def _validate_linestring(geometry: Any) -> list[list[float]]:
    if not isinstance(geometry, Mapping) or geometry.get('type') != 'LineString':
        raise RouteCandidateError('full GeoJSON LineString required (not simplified, no missing geometry)')
    coords = geometry.get('coordinates')
    if not isinstance(coords,list) or len(coords)<2:
        raise RouteCandidateError('at least 2 line positions required')
    for c in coords:
        if not isinstance(c,list) or len(c)<2 or any(isinstance(v,bool) or not isinstance(v,(float,int)) or not math.isfinite(v) for v in c[:2]) or not (-180<=c[0]<=180 and -90<=c[1]<=90):
            raise RouteCandidateError('invalid route geometry coordinates')
    return [[float(x[0]),float(x[1])] for x in coords]


def route_candidates(
    result: Mapping[str,Any], anchors: Sequence[RouteAnchor], *,
    graph_dataset_id: str, profile_digest: str,
) -> dict[str,Any]:
    """Normalize OSRM candidates; preserve immutable input source order & provenance."""
    ordered=validate_anchors(anchors)
    if not graph_dataset_id or not profile_digest:
        raise RouteCandidateError('graph manifest identity + Lua profile digest required')
    if not isinstance(result,Mapping) or result.get('code') != 'Ok':
        raise RouteCandidateError('OSRM did not report Ok')
    routes=result.get('routes')
    waypoints=result.get('waypoints')
    if not isinstance(routes,list) or not routes:
        raise RouteCandidateError('no routes returned')
    if not isinstance(waypoints,list) or len(waypoints)!=len(ordered):
        raise RouteCandidateError('waypoint count mismatch (order uncertain)')
    normalized=[]
    for i,route in enumerate(routes):
        if not isinstance(route,Mapping): raise RouteCandidateError('invalid route object')
        geom=_validate_linestring(route.get('geometry'))
        legs=route.get('legs')
        if not isinstance(legs,list) or len(legs)!=len(ordered)-1:
            raise RouteCandidateError('route legs do not match ordered anchors')
        if any(not isinstance(x,Mapping) for x in legs):
            raise RouteCandidateError('invalid leg')
        distance_mm=_positive_distance_mm(route.get('distance'))
        if type(route.get('duration')) not in (float,int) or not math.isfinite(route['duration']) or route['duration']<0:
            raise RouteCandidateError('invalid duration')
        normalized.append({
            'candidate_id':f'OSRM-CAND-{i+1:03}', 'source':'OSRM',
            'route_authority':False,'status':'CANDIDATE_REVIEW',
            'graph_distance_mm_candidate':distance_mm,
            'estimated_travel_seconds':float(route['duration']),
            'source_anchor_order':[a.anchor_id for a in ordered],
            'legs_count':len(legs),
            'geometry':{'type':'LineString','coordinates':geom},
            'warnings':['Not official distance/arrival time; directed-edge/coverage validation required'],
        })
    return {'mode':'PREP','route_authority':False,'graph_dataset_id':graph_dataset_id,
            'profile_digest':profile_digest,'osm_data_version':result.get('data_version'),
            'source_anchor_order':[a.anchor_id for a in ordered],
            'candidates':normalized,
            'warnings':([] if result.get('data_version') else ['OSM_DATA_VERSION_NOT_PROVIDED'])}


def normalize_matrix(result: Mapping[str,Any], anchors: Sequence[RouteAnchor]) -> dict[str,Any]:
    ordered=validate_anchors(anchors)
    if not isinstance(result,Mapping) or result.get('code')!='Ok':
        raise RouteCandidateError('OSRM table did not return Ok')
    if result.get('fallback_speed_cells'):
        raise RouteCandidateError('estimated fallback cells forbidden for authoritative evaluation')
    n=len(ordered)
    ds=result.get('distances')
    ts=result.get('durations')
    if any(not isinstance(matrix,list) or len(matrix)!=n or any(not isinstance(row,list) or len(row)!=n for row in matrix) for matrix in (ds,ts)):
        raise RouteCandidateError('matrix dimensions mismatch')
    def valid_matrix(m):
        for row in m:
            for v in row:
                if v is not None and (isinstance(v,bool) or not isinstance(v,(int,float)) or not math.isfinite(v) or v<0):
                    raise RouteCandidateError('invalid matrix cell')
        return m
    return {'mode':'REVIEW','route_authority':False,'anchor_order':[a.anchor_id for a in ordered],
            'distances_m':valid_matrix(ds),'durations_s':valid_matrix(ts),
            'unreachable_cells':[[i,j] for i in range(n) for j in range(n) if ds[i][j] is None or ts[i][j] is None]}


def validate_osrm_base_url(base_url: str, allowed_hosts: frozenset[str]=frozenset({'127.0.0.1','localhost','::1'})) -> str:
    parsed=urlsplit(base_url)
    if parsed.scheme not in ('http','https') or not parsed.hostname or parsed.hostname not in allowed_hosts or parsed.username or parsed.password or parsed.query or parsed.fragment or parsed.path not in ('','/'):
        raise RouteCandidateError('OSRM endpoint must be a preapproved origin (no credentials/query/path)')
    return f'{parsed.scheme}://{parsed.netloc}'


class OSRMAdapter:
    """Optional actual IO; never accepts target URL from user/agent input.

    For production inject trusted reverse proxy HTTP transport with auth, limits and TLS.
    Default config permits only loopback endpoints. This is a prototype, not a hardened gateway.
    """
    def __init__(self, base_url: str='http://127.0.0.1:5000', *, allowed_hosts: frozenset[str]=frozenset({'127.0.0.1','localhost','::1'}), transport: Callable|None=None):
        self.base_url=validate_osrm_base_url(base_url,allowed_hosts)
        self.transport=transport or self._native_http_transport

    @staticmethod
    def _read_response(req: Request) -> dict[str, Any]:
        class NoRedirects(HTTPRedirectHandler):
            def redirect_request(self, req, fp, code, msg, headers, newurl):
                raise RouteCandidateError('provider redirect denied; only configured origin is allowed')
        opener=build_opener(NoRedirects)
        with opener.open(req, timeout=8) as resp:
            if resp.status != 200:
                raise RouteCandidateError('routing service returned non-200')
            body=resp.read(8_000_001)
            if len(body) > 8_000_000:
                raise RouteCandidateError('response too large')
            return json.loads(body)

    @staticmethod
    def _native_http_transport(url: str, payload: dict[str, Any]) -> dict[str, Any]:
        """OSRM native API uses GET /service/v1/profile/lon,lat;lon,lat."""
        coordinates = payload['coordinates']
        encoded_coordinates = ';'.join(','.join(format(v, '.7f') for v in point) for point in coordinates)
        options = {}
        for key, value in payload.items():
            if key == 'coordinates':
                continue
            if isinstance(value, bool):
                options[key] = str(value).lower()
            elif isinstance(value, list):
                separator = ',' if key == 'annotations' else ';'
                options[key] = separator.join(str(v) for v in value)
            else:
                options[key] = value
        request = Request(url + '/' + encoded_coordinates + '?' + urlencode(options), method='GET')
        return OSRMAdapter._read_response(request)

    @staticmethod
    def _http_transport(url:str,payload:dict[str,Any]) -> dict[str,Any]:
        data=json.dumps(payload,separators=(',',':')).encode()
        req=Request(url,data=data,headers={'Content-Type':'application/json'},method='POST')
        return OSRMAdapter._read_response(req)

    def route(self, anchors:Sequence[RouteAnchor],graph_dataset_id:str,profile_digest:str, *, mode: str)->dict[str,Any]:
        require_routing_mode(mode)
        if not all(isinstance(v, str) and v.strip() for v in (graph_dataset_id, profile_digest)):
            raise RouteCandidateError('graph manifest identity + profile digest required')
        # Fixed trusted target and fixed profile; separate instances for other profiles.
        data=self.transport(self.base_url+'/route/v1/driving',build_route_payload(anchors))
        result = route_candidates(data,anchors,graph_dataset_id=graph_dataset_id,profile_digest=profile_digest)
        result['mode'] = mode
        return result

    def table(self, anchors:Sequence[RouteAnchor], *, mode: str)->dict[str,Any]:
        require_routing_mode(mode)
        data=self.transport(self.base_url+'/table/v1/driving',build_matrix_payload(anchors))
        result = normalize_matrix(data,anchors)
        result['mode'] = mode
        return result

    def match(self, anchors:Sequence[RouteAnchor],timestamps:Sequence[int],accuracies_m:Sequence[float], *, mode: str)->dict[str,Any]:
        require_routing_mode(mode)
        result=self.transport(self.base_url+'/match/v1/driving',build_match_payload(anchors,timestamps,accuracies_m))
        if not isinstance(result,Mapping) or result.get('code')!='Ok':raise RouteCandidateError('OSRM Match failed')
        matched=result.get('matchings')
        tp=result.get('tracepoints')
        if not isinstance(matched,list) or not isinstance(tp,list) or len(tp)!=len(anchors):
            raise RouteCandidateError('OSRM matching geometry / tracepoint result mismatch')
        return {'mode':mode,'route_authority':False,'status':'MATCH_PROPOSAL_ONLY',
                'input_anchor_order':[a.anchor_id for a in anchors],
                'matched_segments':len(matched),
                'outlier_indices':[i for i,x in enumerate(tp) if x is None],
                'confidence_per_segment':[x.get('confidence') for x in matched],
                'warning':'GPS matching must not automatically verify source or change route revision'}
