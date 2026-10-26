# Agent 7 / Division 6 — Source-linked Turn Cue Proposals (proposed v1.2)
STATUS: DESIGN/TEST CONTRACT. Does not create published driver instructions.

## Two separate pipelines
**PREP/REVIEW / blind:** Agent 7 receives ordered roadbook event IDs from Agent 2, RouteRevisionProposal directed-edge occurrences from Agent 4, approved geographic evidence from Agent 5, and a compatible Agent 3 TimingPlan. Organizer Master Pos, post-event KML and result card are NOT present. Generate turn proposals only with verified graph continuity, correct incoming/outgoing legal edges and reviewed sign/landmark identity. Missing geometry or sign arrow => turn UNKNOWN and cue HOLD. Agent 3 provides mathematically derived seconds based on supported chainage, never a manufactured official Master time.

**POST_EVENT:** After a trayek is finished, compare *frozen PREP/REVIEW cue proposals* with Master Pos and actual KML to diagnose errors. 18 Master anchors and 17 historical corridors are EVALUATION OVERLAYS, not hidden cue-generation anchors or extra official roadbook instructions. Comparing to Master does not automatically change a cue to VERIFIED or cause Driver release.

## Required cue identity and evidence
Each proposed cue holds immutable source_instruction_id, sub_id, cp/landmark occurrence ID when relevant, visit_index, route_revision_id, timing_plan_revision, directed_edge_occurrence_id, inbound/outbound edges, chainage_graph_mm, physical evidence refs, event-rule version, cue_proposal_status and unresolved evidence. Arrival/cue timestamp requires Agent 3's supported CP distance projection.

Critical regression (Trayek 1): one CSV "Arah Gilimanuk STRAIGHT" must become TWO distinct signed decision events, separated by any number of unrelated junctions, and not assign arrow without proof. Do not copy user-reported historical second-right-LR rule as a universal new-stage maneuver. START and zero-trip distinct; POI center vs roadside access distinct; F/G boundary and finish identity require evidence.

## Release and invalidation
No AI-generated cue may be sent to LIVE Driver. Only independent QG-01..16 validation, authenticated navigator review bound to exact revisions and release manager publishing an immutable NaviPack authorize a deterministic local cue FSM; review-only status is NOT device ACK. Route, source, location or TSD timing changes invalidate related cues and receipts.

## Learning
Agent 7 learns from approved error classes, e.g. repeated-sign collapse, wrong approach, duplicate location pin, temporal KML mismatch, missing CP second timing. Learn validation/check algorithms and better prompt/test coverage; never encode the 18 Master coordinates, KML route or participant result-card offsets as new course-agnostic commands. Trayek 2 remains blind.
