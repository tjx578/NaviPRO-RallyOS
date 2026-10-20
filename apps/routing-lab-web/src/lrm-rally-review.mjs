/**
 * NaviPRO clean-room Leaflet Routing Machine PREP/REVIEW adapter.
 * Pure JS; no Leaflet code imported. Enforces view/proposal authority only.
 * IMPORTANT: LRM options are UI defense-in-depth, not server authorization.
 */
const MODES = new Set(['PREP', 'REVIEW']);

export class LrmReviewError extends Error { constructor(msg) { super(msg); this.name='LrmReviewError'; } }

function token(value, name) {
  if (typeof value !== 'string' || !value.trim() || value.length > 180) {
    throw new LrmReviewError(`${name} must be a nonempty short string`);
  }
  return value;
}
function coordinate(lat_e7, lon_e7) {
  if (!Number.isSafeInteger(lat_e7) || Math.abs(lat_e7) > 900_000_000 ||
      !Number.isSafeInteger(lon_e7) || Math.abs(lon_e7) > 1_800_000_000) {
    throw new LrmReviewError('Coordinates must be valid signed E7 integers');
  }
  return Object.freeze({lat_e7,lon_e7});
}
function anchorsFrom(input) {
  if (!Array.isArray(input) || input.length < 2 || input.length > 100) {
    throw new LrmReviewError('2-100 official ordered anchors required');
  }
  const anchors=input.map(a=> {
    if (!a || typeof a!=='object') throw new LrmReviewError('Official anchor object required');
    return Object.freeze({anchor_id:token(a.anchor_id,'anchor_id'),...coordinate(a.lat_e7,a.lon_e7)});
  });
  if (new Set(anchors.map(a=>a.anchor_id)).size!==anchors.length) {
    throw new LrmReviewError('Duplicate authoritative anchor ID');
  }
  return Object.freeze(anchors);
}
/** Immutable Page 2 review snapshot bound to official route revision. */
export function newLrmReview({mode,routeRevisionId,graphDatasetId,profileDigest,officialAnchors,candidateIds=[]}) {
  if (!MODES.has(mode)) throw new LrmReviewError('LIVE forbidden');
  const oa=anchorsFrom(officialAnchors);
  if (!Array.isArray(candidateIds) || candidateIds.some(x=>typeof x!=='string'||!x.trim()) ||
      new Set(candidateIds).size !== candidateIds.length) throw new LrmReviewError('Unique candidate IDs required');
  return Object.freeze({
    mode, routeRevisionId:token(routeRevisionId,'routeRevisionId'),
    graphDatasetId:token(graphDatasetId,'graphDatasetId'),profileDigest:token(profileDigest,'profileDigest'),
    officialAnchors:oa,candidateIds:Object.freeze([...candidateIds]),selectedCandidateId:null,
    shapingProposals:Object.freeze([]),routeAuthority:false,status:'REVIEW_ONLY'
  });
}
/** Hardened static UI configuration. Must not be relied upon as the only guard. */
export function lockedLrmOptions() {
  return Object.freeze({
    autoRoute:false, routeWhileDragging:false, addWaypoints:false,
    draggableWaypoints:false, reverseWaypoints:false,
    waypointMode:'connect', showAlternatives:true, fitSelectedRoutes:false,
    useZoomParameter:false
  });
}
/** Fresh Leaflet LatLng-compatible copies. Never expose reference to authoritative model. */
export function lrmDisplayWaypoints(session) {
  return session.officialAnchors.map(a=>({anchor_id:a.anchor_id,
    latLng:{lat:a.lat_e7/1e7,lng:a.lon_e7/1e7},name:a.anchor_id}));
}
export function previewAlternative(session, candidateId) {
  if (!session.candidateIds.includes(candidateId)) throw new LrmReviewError('Unknown route candidate');
  return Object.freeze({...session,selectedCandidateId:candidateId});
}
/** A tapped line/drag is NOT allowed to edit official anchors. Create a separate proposal. */
export function proposeShapingPoint(session, {afterAnchorId,lat_e7,lon_e7,reason}) {
  if (!session.officialAnchors.slice(0,-1).some(a=>a.anchor_id===afterAnchorId)) {
    throw new LrmReviewError('Shaping point must lie between source anchors');
  }
  const point=Object.freeze({after_anchor_id:afterAnchorId,...coordinate(lat_e7,lon_e7),
    reason:token(reason,'reason'),authority:'AGENT_PROPOSE',status:'DRAFT_PROPOSAL'});
  return Object.freeze({...session,shapingProposals:Object.freeze([...session.shapingProposals,point])});
}
/** Translate events as display-only. Mutating events are rejected even if LRM emits them. */
export function acceptLrmEvent(session, eventType, detail={}) {
  if (eventType==='routeselected') return previewAlternative(session,detail.candidateId);
  if (['waypointschanged','waypointsspliced','waypointdrag','waypointdragend',
      'linetouched','reversewaypoints','routeconfirm','publish'].includes(eventType)) {
    throw new LrmReviewError(`Event ${eventType} cannot change official route`);
  }
  if (eventType==='routingerror') return session; // show a message, do not mutate authority
  throw new LrmReviewError('Unsupported event');
}
/** For the agent/backend: metadata-bound plan, never a release or authority mutation. */
export function prepareReviewRequest(session) {
  return {
    mode:session.mode,route_revision_id:session.routeRevisionId,
    graph_dataset_id:session.graphDatasetId,profile_digest:session.profileDigest,
    official_anchor_ids:session.officialAnchors.map(a=>a.anchor_id),
    selected_candidate_id:session.selectedCandidateId,
    proposed_shaping_points:session.shapingProposals.map(p=>({...p}))
  };
}
