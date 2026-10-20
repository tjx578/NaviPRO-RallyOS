import test from 'node:test';
import assert from 'node:assert/strict';
import {LrmReviewError,newLrmReview,lockedLrmOptions,lrmDisplayWaypoints,
  previewAlternative,proposeShapingPoint,acceptLrmEvent,prepareReviewRequest} from '../src/lrm-rally-review.mjs';
const input={mode:'REVIEW',routeRevisionId:'RR-7',graphDatasetId:'bali-pbf-2026',profileDigest:'sha256:car-v1',
  officialAnchors:[{anchor_id:'A',lat_e7:-86700000,lon_e7:1152100000},
                   {anchor_id:'B',lat_e7:-86720000,lon_e7:1152200000},
                   {anchor_id:'C',lat_e7:-86740000,lon_e7:1152300000}],candidateIds:['OSRM-1','OSRM-2']};
const make=()=>newLrmReview(input);
test('immutable source ordered anchors and bound provenance',()=>{
  const s=make();assert.deepEqual(s.officialAnchors.map(x=>x.anchor_id),['A','B','C']);
  assert.ok(Object.isFrozen(s.officialAnchors));assert.ok(Object.isFrozen(s.officialAnchors[0]));
  assert.equal(s.graphDatasetId,'bali-pbf-2026');assert.equal(s.routeAuthority,false);
  input.officialAnchors[0].lat_e7=999;
  assert.equal(s.officialAnchors[0].lat_e7,-86700000);input.officialAnchors[0].lat_e7=-86700000;
});
test('strict block LIVE, invalid E7, duplicates, missing graph or route revision',()=>{
  for(const bad of [
    {...input,mode:'LIVE'}, {...input,graphDatasetId:''}, {...input,routeRevisionId:''},
    {...input,officialAnchors:[input.officialAnchors[0],input.officialAnchors[0]]},
    {...input,officialAnchors:[{...input.officialAnchors[0],lon_e7:1810000000},input.officialAnchors[1]]},
    {...input,officialAnchors:input.officialAnchors.slice(0,1)},
    {...input,candidateIds:['one','one']}
  ]) assert.throws(()=>newLrmReview(bad),LrmReviewError);
});
test('routing control automatically disables unsafe editing and auto routing',()=>{
 const opts=lockedLrmOptions();
 for(const x of ['autoRoute','routeWhileDragging','addWaypoints','draggableWaypoints','reverseWaypoints']) assert.equal(opts[x],false);
 assert.equal(opts.waypointMode,'connect');assert.equal(opts.showAlternatives,true);
 assert.equal(opts.fitSelectedRoutes,false);assert.ok(Object.isFrozen(opts));
});
test('display coordinates lat lng fresh and cannot mutate source',()=>{
 const s=make();const w=lrmDisplayWaypoints(s);
 assert.deepEqual(w[0].latLng,{lat:-8.67,lng:115.21});w[0].latLng.lat=0;
 assert.equal(lrmDisplayWaypoints(s)[0].latLng.lat,-8.67);
});
test('alternative selection only changes preview not source or authority',()=>{
 const s=make(),n=previewAlternative(s,'OSRM-2');
 assert.equal(n.selectedCandidateId,'OSRM-2');assert.equal(n.routeAuthority,false);
 assert.deepEqual(n.officialAnchors.map(x=>x.anchor_id),['A','B','C']);assert.equal(s.selectedCandidateId,null);
 assert.throws(()=>previewAlternative(s,'UNKNOWN'),LrmReviewError);
});
test('new shaping point proposal keeps official ordered source immutable',()=>{
 const n=proposeShapingPoint(make(),{afterAnchorId:'A',lat_e7:-86705000,lon_e7:1152105000,reason:'review candidate alignment'});
 assert.equal(n.shapingProposals[0].status,'DRAFT_PROPOSAL');assert.equal(n.shapingProposals[0].authority,'AGENT_PROPOSE');
 assert.deepEqual(n.officialAnchors.map(x=>x.anchor_id),['A','B','C']);
 assert.equal(n.routeAuthority,false);assert.equal(n.shapingProposals.length,1);
});
test('shaping point rejects finish anchor, invalid reason or coordinates',()=>{
 const s=make();for(const bad of [
  {afterAnchorId:'C',lat_e7:0,lon_e7:0,reason:'x'},
  {afterAnchorId:'unknown',lat_e7:0,lon_e7:0,reason:'x'},
  {afterAnchorId:'A',lat_e7:0.1,lon_e7:0,reason:'x'},
  {afterAnchorId:'A',lat_e7:0,lon_e7:0,reason:''}
 ])assert.throws(()=>proposeShapingPoint(s,bad),LrmReviewError);
});
test('UI event rejects all official mutations and accepts preview only',()=>{
 const s=make();for(const e of ['waypointschanged','waypointsspliced','waypointdrag','waypointdragend','linetouched','reversewaypoints','routeconfirm','publish'])
 assert.throws(()=>acceptLrmEvent(s,e,{}),LrmReviewError);
 assert.equal(acceptLrmEvent(s,'routingerror'),s);
 assert.equal(acceptLrmEvent(s,'routeselected',{candidateId:'OSRM-1'}).selectedCandidateId,'OSRM-1');
});
test('request export does not contain authority mutation/reordering',()=>{
 const s=previewAlternative(proposeShapingPoint(make(),{afterAnchorId:'B',lat_e7:-86730000,lon_e7:1152250000,reason:'candidate path'}),'OSRM-1');
 const p=prepareReviewRequest(s);
 assert.deepEqual(p.official_anchor_ids,['A','B','C']);assert.equal(p.selected_candidate_id,'OSRM-1');
 assert.ok(!('status' in p) && !('route_authority' in p));
 assert.ok(!('approval' in p) && !('reorder' in p) && !('confirm' in p));
});
