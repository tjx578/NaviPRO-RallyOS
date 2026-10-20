import test from 'node:test';
import assert from 'node:assert/strict';
import {createReviewSession,chooseCandidate,applyOfficialOrderChange} from '../src/review-policy.mjs';
const base={mode:'REVIEW',sourceAnchorOrder:['START','KM-PAL','FINISH'], graphDatasetId:'bali-2026-v1', candidateIds:['C1','C2']};
test('review session readonly order and disabled trip/approval',()=>{
 const s=createReviewSession(base);
 assert.deepEqual(s.sourceAnchorOrder,['START','KM-PAL','FINISH']);
 assert.equal(s.tripOptimizerEnabled,false);
 assert.equal(s.approvalActionsEnabled,false);
 assert.equal(s.routeAuthority,false);
 assert.equal(s.routeReorderingEnabled,false);
 assert.ok(Object.isFrozen(s.sourceAnchorOrder));
 const t=chooseCandidate(s,'C2');
 assert.equal(t.selectedCandidateId,'C2');
 assert.deepEqual(t.sourceAnchorOrder,s.sourceAnchorOrder);
});
test('LIVE, duplicate anchors, unknown candidates blocked',()=>{
 assert.throws(()=>createReviewSession({...base,mode:'LIVE'}));
 assert.throws(()=>createReviewSession({...base,sourceAnchorOrder:['A','A']}));
 assert.throws(()=>chooseCandidate(createReviewSession(base),'WRONG'));
 assert.throws(()=>applyOfficialOrderChange());
});
