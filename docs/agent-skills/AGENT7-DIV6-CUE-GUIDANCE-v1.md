# Agent 7 Divisi 6 — Navigation Guidance & Voice v1 (PROPOSED)

Agent 7 does NOT independently choose routing. It transforms version-locked Agent 4 directed graph occurrences, Agent 3 TSD plans, Agent 2 instruction IDs and Agent 5 reviewed physical evidence into REVIEW-ONLY cue proposals for Navigator Page 2 and Page 3.

## Mandatory cue contract
- source_instruction_id, route_revision_id, graph_release, timing_plan_revision, sub_id, cp_id when applicable, visit_index, directed_edge_occurrence_id, incoming edge, outgoing edge, graph chainage and evidence receipt.
- Turn matches source roadbook and legal connected incoming/outgoing edge. A GPS heading change on an actual KML track alone is NOT enough to issue LEFT/RIGHT. Do not count duplicate photo evidence of the same sign as separate Gilimanuk occurrences.
- Keep time categories separate: official event start and zero car, whole-minute sub schedule, calculated per-second Cadencer target, and organizer Master Pos actual time (POST_EVENT only). Never repeat the sub time window as a fabricated timestamp on every cue.
- Missing CP distance reconciliation or source time rule => per-cue target time UNKNOWN; unverified map/landmark/sign evidence => maneuver UNKNOWN/HOLD even if a legacy CSV says VERIFIED.
- Each proposed cue MUST remain preview_only=true, gate_results=NOT_RUN, driver_release=HOLD until exact RouteRevision, TimingPlan, authentic navigator review and all independent quality gates clear.
- Driver live runs only local deterministic offline route cue FSM/TTS with immutable confirmed NaviPack; no AI auto-rerouting during event.

Historical regression: original 60 cue rows need 61 review occurrences because Gilimanuk must split into two signed decisions; F/G candidate endpoint fails time-aware GPS inspection; two G POIs share one unreviewed coordinate; Master overlay is separate from source instructions and is NEVER part of PREP or Trayek 2 benchmark inputs.

Update dependencies: source/graph/location/time revision changes invalidate old cue and any previously bound review/delivery acknowledgment. Only a real journal/transport receipt proves persistence or delivery.


## Amendment v1.1 — Master-anchored historical cue review

Agent 7 reads Agent 4 historical corridors with MASTER_LOCATION_REFERENCE, GPS_CORRIDOR_OBSERVATION, and VERIFIED_ROADBOOK_MANEUVER as THREE distinct evidence classes. The first two do not authorize a turn cue by geographic proximity.

Render 18 Master markers and 17 observed corridors only on TRAINING_POST_EVENT Page 2; these are not newly invented roadbook cues. Keep the 61 original source-linked cue occurrences and two separate Gilimanuk sign decisions.

A-01 START references official START; A-02 Zero Trip has a separate unknown/verified physical identity. F-11 and G-01 may share the historical PR8 location but cannot acquire RIGHT/LEFT solely from this mapping; H-03 reference FINISH Master. When graph/physical turn proof is absent, return turn UNKNOWN and Driver HOLD. Timestamps on official Master Pos cannot be reused as the times of other landmarks. Agent 3 adds computed cue seconds only after binding valid CP chainage and event timing authority.

Any revision to roadbook, graph, physical evidence, master anchor snapshot or Cadencer TimingPlan invalidates dependent cue previews and requires independent gate and navigator review.
