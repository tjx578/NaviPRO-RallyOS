# NaviPRO RallyOS — PREP-first solving / POST_EVENT-only ground truth
Revision 2026-10-26. This policy **supersedes prior wording "MASTER-ANCHOR-FIRST" as a route solving method**.

## Timeline (event-specific ground truth)
1. **BEFORE START (PREP)**: source roadbook + official competition instructions, starting list, digital road graph, prior independently proven geographic knowledge. Agent 2 extracts full ledger; Agent 3 produces sub schedule and per-second Cadencer timing; Agent 4 solves source-constrained directed routes by sub then CP; Agent 5 reviews location candidates; Agent 7 prepares cues; Agent 8 checks only validated evidence. NO organizer Master Pos locations, zero-car Master Pos times, post-event KML or result cards.
2. **BEFORE RELEASE (REVIEW)**: navigator edits/approves exact revisions; independent deterministic validator must run QG-01..16. Missing providers or evidence => HOLD; no fake verified coordinates or invented signs.
3. **DURING EVENT**: deterministic offline Driver and time/cue services only. This is not a generative-agent routing phase, and current repository still lacks a complete release runtime.
4. **AFTER FINISH (POST_EVENT)**: organizer releases Master Pos, zero-car Master Pos targets and results; historical KML can be reconciled to those locations. Evaluate immutable frozen pre-event route/cues against ground truth. This is the ONLY role of master_anchor_reconcile.py.
5. **LEARNING**: taxonomy of errors and evidence receipts produce reviewer-approved general rules and unit tests, not explicit copied Master coordinates or KML polylines. Validate on separate historical cases and a sealed Trayek 2 blind benchmark; never access its Master before evaluation.

## Cross-agent knowledge flow
Agent 1 orchestrates mode-locked dependency graph and source access; Agent 2 fully enumerates steps, distinct START/Zero Trip and repeated sign decisions; Agent 3 preserves official distance, time version and CP seconds; Agent 4 searches legal directed graph in sub->CP order without Master; Agent 5 resolves independently available POI/sign/access evidence; Agent 6 replay is available for post-event error diagnosis; Agent 7 proposes cue only from source-linked graph and evidence; Agent 8 provides legal/quality diagnostics and invokes the independent validator; Agent 9 journals authenticated source versions and real receipts. Any revision triggers downstream invalidation.

## Durable lessons extracted from Trayek 1
- Two Gilimanuk directional sign occurrences must not collapse to one STRAIGHT cue; they can be nonconsecutive intersections.
- POI names/coordinates are not graph access edges; start != zero-trip; sub boundary identities require independent source and directed graph checks.
- Per-sub authority distance, dense graph and raw GPS observed distance are separate measurement domains. Agent 3 derives CP seconds only after sufficient binding evidence.
- Chronological GPS closest-approach vs unrestricted geometric nearest prevents falsely attaching wrong revisits, but **only POST_EVENT**.
- Master Pos are ground truth for assessment, NOT graph waypoints during pre-event route solving; 18/18 near GPS is not evidence of correct all turns.
- Historical F/G PR8, named finish, timing penalties and user-reported second Gilimanuk right turn are event-specific *examples*, never coordinates or signs to hardcode as a new blind solution.

## Quality gates and completion
Pre-event candidates remain PROPOSAL_PENDING_VALIDATION; independent QG gates must use truthful sources and receipt-bound decisions. Real graph execution, sign imaging verification, learned rule calibration and LIVE driver readiness are NOT established by draft skills or synthetic tests.
