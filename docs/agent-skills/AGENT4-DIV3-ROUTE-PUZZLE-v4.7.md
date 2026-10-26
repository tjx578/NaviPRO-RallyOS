# Agent 4 Divisi 3 — Route Puzzle & Geometry v4.7 (PROPOSED)

Scope: PREP/REVIEW only. Agent 4 makes route revision proposals. Agent 8 cannot self-authorize; independent deterministic validator and human reviewer are required.

## Execution pipeline
1. Read reviewed verbatim roadbook source ledger from Agent 2; preserve every instruction ID and chronological occurrence. Start and Zero Trip are different source events.
2. Read versioned Agent 3 TSD constraints and source-authoritative distances. Never overwrite D_authority with D_graph or raw KML GPS.
3. Resolve directed legal graph paths one sub at a time, beginning Sub A. Within a sub, attach source CP/landmark/instruction occurrences by order. Only chain to the next sub after source endpoint identities and traversable edges are checked.
4. State is (sub_id, ordered_instruction_index, incoming_edge_occurrence, visit_index, sign_occurrences, accumulated_D_graph, physical_evidence_state). Repeated coordinates do not imply the same visit.
5. Arah Gilimanuk 2 kali: two physically distinct directional-sign decision events, possibly separated by other intersections. Never compress to STRAIGHT or assume both turns identical. The reported second sign RIGHT at LR is user-reported context until externally checked; the subsequent BKN di LR arah Pantai remains an independent instruction until a shared location is demonstrated.
6. Location proposals from Agent 5 need physical access-edge, date, orientation, and genuine reviewer receipt. Globe/satellite/3D assists geometric layout; street-level views may read signs. KML nearest-point alone does not verify road sign text or a legal turn.
7. For missing CP, preserve unresolved corridors and bounded route candidates. Monte Carlo checks uncertainty/robustness only after hard roadbook constraints; record seed, assumptions, distributions, N and surviving alternatives. Never convert a score into physical certification.
8. Per sub track D_authority, D_graph, D_odo, D_geo as different domains. Do not cancel residuals across subs and do not assume universal 20m/50m/2pct thresholds.
9. Output complete RouteRevisionProposal: roadbook revision, graph release, directed edge sequence, source-to-occurrence bindings, ordered chainage by CP, unresolved constraints, distance residual per sub, evidence refs, source & method versions, PROPOSAL_PENDING_VALIDATION and gate_results NOT_RUN.
10. Agent 4 supports QG-09 route continuity, QG-10 landmark road access binding, QG-11 dense geometry, QG-12 monotonic sequence, QG-14 inter-sub chaining, QG-15 reviewed endpoints. Agent 3 leads QG-13/16; Agent 2 leads QG-05/06. The independent validator computes gate results.

## POST_EVENT Trayek 1 regression
Actual KML participant #35 has 14,535 points (~69.242km raw polyline); historic KML approaches 18/18 Master Pos within 30m. This proves neither roadbook turn compliance nor organizer intended route. Source CSV had 60 cues including one oversimplified Gilimanuk STRAIGHT instruction, identical false START/Zero Trip location, disputed F/G boundary Perbekel Banjar, and conflated Sulanyah coordinates. Strict chronological matching, not global nearest point, is necessary.

Master Pos and KML are permitted in Trayek 1 training evaluation only, not PREP and not Trayek 2 blind benchmark. Never auto-promote legacy VERIFIED labels to physical VERIFIED or publish unapproved Driver cues.


## Amendment v4.7.1 — MASTER-ANCHOR-FIRST in TRAINING_POST_EVENT

Trayek 1 official Master Pos locations are first-priority geographic anchors during retrospective training. They are NOT only optional score checkpoints. KML from participant 35 is observed travel and cannot by itself validate every roadbook maneuver.

Procedure:
1. Read all 18 ordered organizer Master Pos coordinates and timed KML in POST_EVENT mode only, with authoritative source provenance and strict revision isolation from PREP and Trayek 2.
2. Run minimum-cost monotone alignment of all 18 Master anchors to KML samples by time and location (implementation: master_anchor_reconcile.py). Missing anchor or impossible order means HOLD. The 30-meter match radius is a diagnostic search limit, not a universal validation tolerance.
3. Partition the observation into 17 Master-to-Master corridors. Keep observed GPS polylines and distances separate from official distance, graph distance, and odometer.
4. Search for each ordered roadbook occurrence, signed direction and CP INSIDE its correct corridor with directed legal graph edges, inbound/outbound heading, landmark identity and official per-sub constraints. No invented intersection turns.
5. Rebind source events with historical identity evidence: A-01 to START Master, F-11 and G-01 to PR8 Perbekel Banjar as ONE boundary location but TWO source instructions, H-03 to FINISH Master. They remain REVIEW_REQUIRED pending graph/physical evidence. A-02 Polres Zero Trip remains separate.
6. Preserve Master times only for their actual organizer Master event IDs. No Master time for unobserved/intermediate roadbook cue. Derived CP time belongs to Agent 3, not Agent 4.
7. Recompute all dependent chainage, sub residuals, CP time and Agent 7 cue previews after re-binding. All route proposals remain proposed, never released to Driver without independent gates and authenticated review.

Acceptance: all official anchors accounted for in order; all source instructions preserved; every unproven turn labelled UNKNOWN; missing real graph validation = HOLD.
