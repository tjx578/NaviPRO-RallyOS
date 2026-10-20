"""Server-side validation for LRM-originated Page 2 review proposals.

Clean-room implementation. This does not approve routes, publish NaviPacks,
or call Leaflet / OSRM. Input is checked against a trusted source snapshot.
"""
from __future__ import annotations

from collections.abc import Mapping


class ReviewGateError(ValueError):
    """Review proposal does not respect immutable roadbook/route authority."""


ALLOWED_KEYS = frozenset({
    'mode', 'route_revision_id', 'graph_dataset_id', 'profile_digest',
    'official_anchor_ids', 'selected_candidate_id', 'proposed_shaping_points',
})
SHAPING_KEYS = frozenset({'after_anchor_id','lat_e7','lon_e7','reason','authority','status'})


def _text(value: object, label: str) -> str:
    if not isinstance(value, str) or not value.strip() or len(value) > 180:
        raise ReviewGateError(f'{label} must be nonempty text <=180 characters')
    return value


def validate_lrm_proposal(payload: Mapping, official_snapshot: Mapping) -> dict:
    """Return a non-authoritative plan iff revision, graph and order match trusted snapshot.

    `official_snapshot` MUST be obtained from authenticated server-side storage,
    never copied from the caller's own payload.
    """
    if not isinstance(payload, Mapping) or not isinstance(official_snapshot, Mapping):
        raise ReviewGateError('Review and trusted official snapshot required')
    if set(payload) - ALLOWED_KEYS:
        raise ReviewGateError('Unsupported or authoritative field in review payload')
    if payload.get('mode') not in ('PREP', 'REVIEW'):
        raise ReviewGateError('LIVE not supported')
    for field in ('route_revision_id', 'graph_dataset_id', 'profile_digest'):
        if _text(payload.get(field), field) != _text(official_snapshot.get(field),f'trusted_{field}'):
            raise ReviewGateError(f'{field} mismatch with trusted snapshot')
    trusted_order = official_snapshot.get('official_anchor_ids')
    incoming = payload.get('official_anchor_ids')
    if (not isinstance(trusted_order, (tuple,list)) or len(trusted_order)<2 or
        len(set(trusted_order))!=len(trusted_order) or
        not all(isinstance(a,str) and a.strip() for a in trusted_order)):
        raise ReviewGateError('Trusted source anchor order invalid')
    if type(incoming) is not list or incoming!=list(trusted_order):
        raise ReviewGateError('Official source anchor order changed')
    candidate_id=payload.get('selected_candidate_id')
    if candidate_id is not None:
        _text(candidate_id,'selected_candidate_id')
        if candidate_id not in official_snapshot.get('candidate_ids', []):
            raise ReviewGateError('Candidate not registered for reviewed revision')
    shapes=payload.get('proposed_shaping_points',[])
    if not isinstance(shapes,list) or len(shapes)>100:
        raise ReviewGateError('Shaping proposal list must be <=100')
    accepted=[]
    for point in shapes:
        if not isinstance(point,Mapping) or set(point)-SHAPING_KEYS:
            raise ReviewGateError('Unexpected shaping-point fields')
        after=_text(point.get('after_anchor_id'),'after_anchor_id')
        if after not in trusted_order[:-1]:
            raise ReviewGateError('Shaping point must follow a non-terminal official anchor')
        lat,lon=point.get('lat_e7'),point.get('lon_e7')
        if type(lat) is not int or abs(lat)>900_000_000 or type(lon) is not int or abs(lon)>1_800_000_000:
            raise ReviewGateError('Strict E7 coordinates required')
        reason=_text(point.get('reason'),'reason')
        if point.get('authority')!='AGENT_PROPOSE' or point.get('status')!='DRAFT_PROPOSAL':
            raise ReviewGateError('Shaping point must have proposal-only status')
        accepted.append({'after_anchor_id':after,'lat_e7':lat,'lon_e7':lon,'reason':reason,
                         'authority':'AGENT_PROPOSE','status':'DRAFT_PROPOSAL'})
    return {
        'status':'PROPOSAL_ONLY','route_authority':False,'mode':payload['mode'],
        'route_revision_id':payload['route_revision_id'],
        'graph_dataset_id':payload['graph_dataset_id'],
        'profile_digest':payload['profile_digest'],
        'official_anchor_ids':list(trusted_order),
        'selected_candidate_id':candidate_id,
        'shaping_proposals':accepted,
        'warning':'Navigator review required; no route/roadbook mutation or verification performed',
    }
