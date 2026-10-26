# Agent 4 / Division 3 — Blind Roadbook Route Solver (proposed v4.8)
STATUS: SPECIFICATION + contract prototype only; NOT an OSRM/Valhalla deployment.

## Correct authority and modes
- **PREP** (before start): no Master Pos, organizer post-event results, historical KML, or secretly injected answer. Sources: Agent 2 reviewed roadbook ledger, Agent 3 official distances and timing constraints, Agent 5 prior location database and public/approved spatial evidence, versioned directed-graph and vehicle/access profile.
- **REVIEW**: inspect route proposals with navigator, retaining unknowns; same no-ground-truth rule for a blind event.
- **POST_EVENT** (only after finish and authorized release of ground truth): use organizer Master Pos, official zero-car timing, participant KML and result card **only to evaluate frozen earlier predictions**. The evaluation utility may use Master anchors to segment actual historical KML into corridors, but this is NOT the algorithm for producing route candidates.
- **LEARNING**: promote approved and documented *generalizable rules* into source interpretation, candidate search, location retrieval, graph evaluation and cue checks. Never hardcode learned Master coordinates, shortcut through historical trip lines, reveal future Master, or assume a case-specific turn in new stages.
- **BLIND_TEST**: new roadbook (Trayek 2) and pre-event published data only; freeze output before opening any post-event labels.

## Agent 4 independent problem solving
1. Agent 2 delivers ordered source instruction occurrences with true source IDs and mandatory flags. START and Zero Trip are different events; repeated signs are separate physical decisions, even when separated by unnamed junctions. One "Arah Gilimanuk 2 kali" source token expands to **two** occurrences; never compress to STRAIGHT.
2. Agent 3 delivers D_authority, per-sub integer-minute schedule and second-resolution TSD constraints separately; Master Pos time and sample GPS must not be sources in PREP.
3. Beginning at Sub A, build bounded **directed graph** alternatives with OSRM/Valhalla / offline graph. State: (sub, required source occurrence index, physical edge occurrence, visit index, seen sign decisions, graph cumulative offset, location-evidence state). Honor vehicle access, mandatory maneuver order, road topology, source end points. No artificial detours to match distance; reject prohibited paths.
4. For each sub, divide candidate search by required CP/landmark/decision events, not arbitrary equal pieces. Resolve named landmarks using Agent 5 identities AND roadside access; use street-level evidence where authorized. A graph proximity to a POI center does not establish physical visit, legal entry or a signed turn.
5. For unknown CPs retain constraints and candidate graph corridors. Apply distance residual per sub and per CP where authority measurements are available. Monte Carlo may test stated uncertainties but survival frequency is NOT true route probability. Never invent missing CP coordinates or signage.
6. Two direction signs for Gilimanuk require two distinct decision nodes (not necessarily consecutive graph nodes) and approach-relative arrows. User-observed second-right-at-LR in Trayek 1 is historical learning feedback, **not** a universal rule and not proof of an unobserved sign in Trayek 2.
7. Rank candidates lexicographically by legal directed continuity + mandatory instruction coverage + missing evidence, then per-sub distance diagnostics, preserving multiple alternatives. Avoid total-distance-only route optimization and universal invented thresholds. Never cancel errors between B–H.
8. Emit proposal only: ordered directed-edge occurrences, source-to-edge bindings, chainage per CP, D_graph residual by sub, unresolved list, evidence and versioned graph/time refs. Never emit "QG PASS" based on AI confidence or hardcoded Master locations.
9. Agent 4 leads evidence for QG-09/10/11/12/14/15; QG-13/16 are Agent 3-led. Gate results are issued only by independent validator, with navigator review and release. Agent 7 consumes a version-matched proposal; Driver LIVE does not accept unverified route proposals.
10. Any change in source, CP evidence, graph, timing or review state invalidates dependent route, CP time, cue and NAVIPack release snapshots.

## Post-finish evaluator only (NOT a route solver)
See master_anchor_reconcile.py: optional minimum-cost chronological matching to 18 Master Pos on completed historical Trayek 1. Those anchors can partition the *recorded* KML into 17 assessment intervals for classifying prior errors. Observed KML 18/18 geographic proximity does NOT prove roadbook maneuver compliance. Any aliases such as F/G at PR8 require independent identity review. This module must never be invoked by the PREP/BLIND route builder.

## Transferable Trayek 1 lessons and test criteria
- Separate START from Polres zero-trip even if old CSV used same coordinates.
- Split two Gilimanuk signed-direction occurrences; duplicated photo(s) are not two decisions.
- Check correct edge visit, source order, physical access and sign arrow by approach.
- Investigate per-CP and F/G chained boundaries; do not hardcode historical Perbekel Banjar positions.
- Compute CP second targets with Agent 3 only once distance and rule provenance are sufficient; never invent official Master timestamps.
- Agent 7 holds questionable legacy cue locations and turn instructions, including historical Sulanyah and finish ambiguities.
- Regression suites use general synthetic cases plus *separate* post-event Trayek 1 fixtures. The completely independent Trayek 2 blind benchmark contains no outcome labels or Master locations.

REFERENCE IMPLEMENTATION: pre_event_route_workflow.py is a ranking and data-boundary prototype, NOT directed-road candidate generation. master_anchor_reconcile.py is a historical evaluation helper ONLY.
