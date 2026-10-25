# 16 quality gates and eight NaviPRO specialist divisions

**Assessment date:** 2026-10-22. **Inspected upstream:** `tjx578/NaviPRO-RallyOS`, `main`, commit `af0f4e5292af388489a0514865e8b59cfd49b721`.  
**Status:** contract alignment and report-schema checks; **NOT_RACE_READY**. No compiler, eight-agent runtime, authenticated review service or Driver runtime is introduced here.

## 1. What actually exists

| Item | Evidence in the inspected repository | Assessment |
| --- | --- | --- |
| All 16 canonical gate names | `GateResult.properties.gate.enum` in `contracts/openapi/navipro-rallyos.openapi.yaml` | PRESENT, contract only |
| Gate results and release status | `GateResult`, `ValidationReport`; `runRouteValidation`, `getValidationReport` | API declarations, no deployed evaluator |
| Full gate implementation | `python/src/navipro_rallyos/validation/` contains only `.gitkeep` at the inspected commit | NOT_IMPLEMENTED |
| Workflow/compile/publication | `reviewRouteWorkflow`, `compileWorkflow`, `publishRelease` | Contracts; compile/publication excluded from MCP |
| Existing technology | Python OSRM adapter, LRM proposal guard, geodesy, context assessment and survey outbox prototypes; OpenAPI/MCP generator | Reusable building blocks, not proof of complete gate execution |
| Cockpit integration | Five-surface registry and role-action policy; Android README scaffolds | DESIGN_ONLY, not wired to runtime authorization |
| Claim of 121 compiler tests | No matching 121-test compiler suite in this upstream snapshot | Cannot transfer an older artifact's result to this repository |

The previous `ValidationReport` required 16 rows but did not require 16 distinct gate identities. A synthetic report containing 16 `SCHEMA_DOMAIN / FAIL` rows with `release_status: PASS` was accepted by its JSON Schema. The revised contract rejects duplicate/missing gates and inconsistent PASS status. It still cannot prove that an evaluator ran or that supplied facts are true.

## 2. Eight divisions, with one separate orchestrator

Role identities follow **navipro-orchestrator 1.2.0 (Skill 1)**. The historical simulation's Agent 1–8 correspond to **division 1–8 / role 2–9**. Role 1 is the orchestrator. These are capability boundaries, not an assertion that nine services are installed, and their numbers are not execution order.

| Division | Role ID | Specialist | Output and gate contribution |
| --- | --- | --- | --- |
| 1 | 2 | Roadbook Interpretation | Source ledger, verbatim text, DSL ambiguity, official order; leads evidence for QG-02/05/06 |
| 2 | 3 | TSD, Distance & Calibration | Separate official/graph/odometer distances, calibration convention, exact timing; QG-13/16 |
| 3 | 4 | Route Puzzle & Geometry Solver | Directed paths and occurrences, dense geometry, access bindings; QG-09/10/11/12/14/15 |
| 4 | 5 | Location & Geospatial Evidence | Candidate identity, physical evidence, provenance and human-review requests; QG-07/08 |
| 5 | 6 | Live Position & Rally Progress | PREP/REVIEW telemetry replay and uncertainty; supports QG-07/08/12/15/16 |
| 6 | 7 | Navigation Guidance & Voice | PREP/REVIEW cue coverage and ordering; supports QG-06/12/16 |
| 7 | 8 | Road Legality, Access & Quality | Contract/legality findings, validator requests and human-review evidence; QG-01/04, cross-gate audit |
| 8 | 9 | Session, Evidence & Rally Journal | Dependency snapshots, provenance and real receipts; QG-03 and cross-cutting audit trail |

All rows describe **evidence responsibility**. Only a deterministic validator may compute authoritative gate results. Division 7 cannot replace QG-04 with its own approval. Division 8 must not claim a saved journal entry, verified official CP arrival or delivery ACK without an actual persistence/receipt source.

Divisions 5 and 6 do not insert an LLM into GPS, timer, sensor fusion or cue advancement. Their proposed LIVE counterparts are deterministic device services consuming the same confirmed offline package. Those services remain unimplemented. Current Page 3 agent operations are PREP/REVIEW only; Driver has no agent interface.

Machine-readable mapping and proposed operation allowlists: [`agent-divisions.yaml`](../../governance/agent-divisions.yaml). Every listed operation resolves to an existing MCP-enabled READ/AGENT_PROPOSE declaration. These lists still need enforcement in an authenticated runtime gateway.

## 3. Exact gate mapping and corrections

[`release-gates.yaml`](../../governance/release-gates.yaml) preserves the existing names. All are blocking. Unknown or unavailable evaluation yields `NOT_RUN`, not invented PASS. A malformed/incomplete report must keep the release on HOLD; the producer must return all gate identities, filling unexecuted gates with NOT_RUN.

| Gate | Evidence lead division | Required correction or implementation boundary |
| --- | --- | --- |
| QG-01 SCHEMA_DOMAIN | 7 | Strict schemas and explicit units/clock domains are required. Existing timing fields include plain strings; the repo does not enforce an all-UTC or all-millisecond rule throughout. |
| QG-02 SOURCE_INTEGRITY | 1, supported by 8 | Hash actual source bytes against a trusted record. A SHA-256 digest is not encryption, a digital signature, or proof of an official publisher. |
| QG-03 RELEASE_BINDING | 8 | Resolve compatible source/route/graph/location/time versions, not just nonempty IDs or assumed database presence. |
| QG-04 REVIEW_AUTHORIZATION | 7, supported by 8 | Authenticated human review must bind the exact snapshot. Identity, permissions and receipt verification need a service; an agent-provided flag is insufficient. |
| QG-05 SOURCE_ORDER | 1 | Preserve original instruction order. Route candidate generation must retain ordered anchors; no TSP reorder. |
| QG-06 SOURCE_COVERAGE | 1 | One final MAPPED binding per required source instruction. This cannot discover text omitted before the source ledger was created; human source/OCR review remains necessary. |
| QG-07 MANDATORY_LANDMARK | 4 | Validate known mandatory landmark coverage and identity evidence. A compiler does not physically detect a sign or building. |
| QG-08 SPATIAL_VERIFICATION | 4 | Require traceable human decisions for active nodes. No promotion from CANDIDATE based on confidence, imagery or a map pin. |
| QG-09 ROUTE_CONTINUITY | 3 | Validate directed graph connectivity and access. Nearby coordinates or a small chord gap do not establish a legal connected road. |
| QG-10 LANDMARK_ROUTE_BINDING | 3, supported by 4 | Distinguish POI reference, physical landmark and roadside access; bind the correct edge occurrence, including parallel-road cases. |
| QG-11 DENSE_GEOMETRY_MEASURE | 3, supported by 2 | Use an explicit geometry/distance model and tolerance profile. Keep graph diagnostics separate from official distance. |
| QG-12 MONOTONIC_SEQUENCE | 3 | Route progress is nondecreasing, with stable ordering for events at the same offset. A legitimate U-turn or repeated coordinate is allowed through distinct route occurrences; offsets need not be equally spaced. |
| QG-13 DISTANCE_RESIDUAL_PER_SUB | 2 | Evaluate each sub independently. The current RDT SSOT defines no universal ±2% tolerance. Use the versioned event/engineering profile; missing required profile means HOLD. |
| QG-14 INTER_SUB_CHAINING | 3 | Check adjacent finish/start bindings and explicit transition rules. The current SSOT does not establish a universal 20 m gap tolerance. A broken inter-sub chain belongs here, not QG-06. |
| QG-15 ROUTE_ENDPOINT_BINDING | 3 | Bind start/finish events to reviewed physical and graph positions. Proximity alone is insufficient. |
| QG-16 TIMING_CONSISTENCY | 2 | Apply versioned time authority, speed segments, neutralization and precision. Keep date-less midnight rollover on HOLD; a future date-aware model needs explicit date/time-zone handling and tests. |

No new default tolerance is inferred from the simulation. An event's official rule or reviewed engineering profile may specify 2%, 20 m or another value, but the source/version and units must be bound before use.

## 4. Workflow, dependencies and review

1. **Bind inputs.** The orchestrator fixes event, sub, source/briefing revision, graph/location snapshots, timing authority and policy versions. Division 8 records only receipts that actually exist.
2. **Extract and review source.** Division 1 preserves text and order and exposes unresolved DSL/OCR issues. A place token or missing instruction cannot silently disappear.
3. **Resolve dependent proposals.** Divisions 3 and 4 iterate over constrained geometry and location evidence. Division 2 computes official timing once its authoritative inputs are available; graph-distance residuals wait for the candidate path. Independent evidence tasks may proceed concurrently. Division 7 checks restrictions and conflicts.
4. **Run preliminary validation.** Division 7 requests the deterministic validator. Missing inputs, unavailable evaluator, ambiguous active nodes or absent review leave relevant gates NOT_RUN/FAIL and the release HOLD. A preliminary check is not release approval.
5. **Obtain bound human review.** A navigator reviews source/location/route evidence and an authorized reviewer supplies a receipt for the exact frozen input snapshot. Signing a review is distinct from package publication. An agent cannot produce this authorization.
6. **Revalidate and compile.** Rerun all 16 gates on those same frozen inputs. Complete PASS is necessary but does not confer publication rights. Confirmation, compile/publication and delivery follow existing navigator/release-manager boundaries and actual ACK contracts.
7. **Execute deterministic LIVE.** Driver consumes the checked, confirmed offline pack; position, clock and cue services operate without cloud/LLM dependency. Record observations separately from immutable pack data; geofence crossing is not proof of official CP stamping.

Human review may be recorded while a draft is held; it does not itself clear the HOLD. This avoids a circular rule in which QG-04 requires a release that itself requires QG-04. Final confirmation/publication remains gated.

**Recompute Chain:** any change to source, route, graph, location decisions, time rules, tolerance profile or review authority invalidates the old report and review binding. Targeted recalculation may refresh draft diagnostics, but final compilation requires a complete rerun on a consistent snapshot. A map edit can affect QG-03/04/06–16; limiting invalidation to QG-11/13/14 is insufficient. Recompute `D_graph` and dependent diagnostics without overwriting `D_auth` or official timing authority. Candidate changes never replace `active_pack_revision`.

**Handoff:** use revision-scoped requests/results and the conceptual fields in the division registry. The single state integrator rejects stale responses and uses idempotency keys for retries. COMPLETE/PARTIAL/CONFLICT/UNAVAILABLE describe specialist work; they are not gate PASS/FAIL/NOT_RUN and cannot authorize a release. No handoff transport or durable checkpointer is implemented by this mapping.

## 5. Technology use and acceptance evidence

- **Python + OpenAPI 3.1 + JSON Schema:** enforce the report contract now. Future typed domain validators must calculate gates from trusted bytes/graph/review services, not accept an AI-generated report as proof. No permissive PASS stub is added.
- **OSRM adapter + LRM review prototype:** candidate ordered graph paths and draft shaping proposals in PREP/REVIEW; no Trip/TSP, no automatic confirmation, no Driver rerouting.
- **Kepler/Cesium/context/survey prototypes:** geometry and physical-evidence support only. Imagery availability, network providers and map renderers are not mandatory LIVE dependencies.
- **Existing MCP generator:** retain proposal/read operation boundaries; generating a tool registry does not start a server. No additional orchestration framework is required for this contract change.
- **SQLite/outbox:** retain separate observations/receipts and immutable pack versions in the future runtime. SQLite or an R*Tree does not itself supply immutability, certification or source authenticity.

The listed `.navipack` members, sealed manifest and byte-identical output remain compiler acceptance requirements. This change does not build them. Reproducibility needs canonical serialization, stable archive metadata and deterministic database construction tested across repeated builds; signatures/verification require actual key and trust management.

Verification for this change:

```bash
python -m pip install -r requirements-test.txt
make verify-gates
python tools/build_mcp_registry.py
python -m pytest -q tests/contracts
```

Local verification on 2026-10-22: **118 contract tests passed**, comprising the existing 99 and 19 new cases. OpenAPI structural validation passed with 82 operations and 110 schemas; MCP regeneration remained byte-identical with 71 tool definitions and 11 blocked operations. Spatial/Cesium registry validation also passed. The test requirements include JSON Schema's optional format checkers so date-time assertions are actually evaluated.

The new tests exercise duplicate/missing/unknown gate identities, malformed rows, FAIL/NOT_RUN with false PASS, and the eight-division operation/authority boundaries against current contracts. Tests use synthetic reports. Passing them establishes contract behavior only; field navigation, complete 16-gate evaluation, authorization services, pack reproducibility, live GPS and Driver delivery require separate implementation and evidence.
