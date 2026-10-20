/** NaviPRO clean-room read-only UI state. Not the OSRM frontend code. */
export function createReviewSession({mode, sourceAnchorOrder, graphDatasetId, candidateIds}) {
  if (!['PREP', 'REVIEW'].includes(mode)) throw new Error('Only PREP/REVIEW allowed');
  if (!Array.isArray(sourceAnchorOrder) || sourceAnchorOrder.length < 2 ||
      sourceAnchorOrder.some(a => typeof a !== 'string' || !a.trim()) ||
      new Set(sourceAnchorOrder).size !== sourceAnchorOrder.length) {
    throw new Error('Unique ordered source anchors required');
  }
  if (typeof graphDatasetId !== 'string' || !graphDatasetId.trim()) throw new Error('Graph identity required');
  if (!Array.isArray(candidateIds) || candidateIds.some(x=>typeof x!=='string')) throw new Error('Candidate ids required');
  return Object.freeze({
    mode, graphDatasetId, sourceAnchorOrder:Object.freeze([...sourceAnchorOrder]),
    candidateIds:Object.freeze([...candidateIds]),
    selectedCandidateId:null, routeAuthority:false, officialRouteEditable:false,
    routeReorderingEnabled:false, tripOptimizerEnabled:false,
    approvalActionsEnabled:false,
  });
}

/** Candidate selection for comparison only; no source anchor changes. */
export function chooseCandidate(session, candidateId) {
  if (!session.candidateIds.includes(candidateId)) throw new Error('Unknown candidate');
  return Object.freeze({...session, selectedCandidateId:candidateId});
}

/** UI must not expose or accept official-order modification. */
export function applyOfficialOrderChange() { throw new Error('Immutable roadbook source order'); }
