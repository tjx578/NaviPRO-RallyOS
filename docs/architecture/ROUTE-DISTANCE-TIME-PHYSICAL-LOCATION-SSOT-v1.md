# NaviPRO RallyOS — Route–Distance–Time + Physical Location Intelligence SSOT v1

**Decision recorded:** 2026-10-20  
**Status:** Architecture / governance **design only**; no production feature implemented by this document.  
**Priority:** P0 reasoning invariant, P0 physical location review workflow.  
**Authority:** official roadbook + event regulations + navigator-governed review; neither third-party maps nor AI can silently confirm a route.

## Why this document exists

A Time Rally instruction is **not** a conventional shortest/fastest-route request. Correct interpretation requires jointly satisfying the roadbook instruction, the **specified distances / KM PAL**, **time/speed/control rules**, physical landmark evidence, and a continuous/legal directed path. A POI with the correct text label can have a misleading map pin — for example, a `Kantor Kepala Desa` geocoder result may be shown in a rice field when the actual office is elsewhere. An image of a plausible building, however, does not prove the office's identity. All ambiguity and source provenance must be explicit.

### Separation of facts, assumptions and judgments

- **Project decision (normative):** Always reason over **route + distance + time**, never routing shortest/fastest path alone; retain the official source ordering. This is a NaviPRO requirement, not an externally verified rally result.
- **Observed risk (user-supplied scenario):** map POI pins can mismatch the actual object. No specific office/address/coordinate is proven by that example.
- **Technology/source fact:** God's Eye View recent-imagery source uses NASA HLS/VIIRS and supports an imagery A/B view; its orbit-tracking module does **not** provide live visual satellite video. See SHA-pinned source: https://github.com/tjx578/gods-eye-view-maps/blob/de2138e84c1778fd98a48b7c9fd0b9788c318946/src/layers/recentImagery/index.js and https://github.com/tjx578/gods-eye-view-maps/blob/de2138e84c1778fd98a48b7c9fd0b9788c318946/src/layers/satellites/index.js.
- **Design hypothesis (not measured):** comparing imagery, place names, road access, roadbook distances, and relevant timing constraints can reduce false POI selection. There are **no** field accuracy measurements in this repository.

## Non-negotiable invariants

1. `OFFICIAL_ROADBOOK` dictates ordered instruction/anchor IDs. Never TSP-sort, reorder or insert official anchors automatically. Only a new reviewed `RouteRevision` can change an approved interpretation; the underlying original text/order remains retained.
2. Preserve distance domains independently, with explicit units and provenance: `D_auth` (roadbook/official), `D_graph` (directed routing candidate), `D_odo` (independent tripmeter), `D_geo` (geodetic diagnostic). Never overwrite `D_auth` with map/network/snapping distances.
3. Time is a **first-class constraint**: model section rules, prescribed/changed speeds, clock origin, time-of-day rules, allowed waits/neutralization, control points and event regulations as versioned inputs. No invented target times, speed tolerances or distance tolerances.
4. Evaluate **directed topological continuity**, path restrictions, access, route coverage and physical feasibility before candidate-ranking. A route that looks visually close but violates an instruction or rule must remain rejected/held.
5. `POI_REFERENCE` (third-party pin), `PHYSICAL_LOCATION` (building/feature), and `ROUTE_ACCESS_POINT` (road-side access/anchor) are distinct objects. They may be different coordinates. None gets verified merely because an image looks plausible.
6. Satellite imagery is **contextual evidence**: record `provider`, `capture_time`, `resolution_m` if known, `license/rights`, `coverage`, `cloud_quality` if known, and original asset reference; show `UNKNOWN` rather than assuming current/high resolution.
7. Candidate AI scores are advisory and must include interpretable evidence, unknowns and competing hypotheses. Missing imagery, missing ground-truth or ambiguous identity => `NEEDS_FIELD_CHECK`/`HOLD`, never automatic `VERIFIED`.
8. Human navigator authorization is required to promote a location decision; route approval follows the existing release/validation gates. No POI, satellite layer, OSRM candidate, field survey or AI action can directly publish a NaviPack.
9. All above PREP/REVIEW logic is **outside Driver LIVE**. Driver consumes signed/confirmed offline NaviPack with independent distance/time sensor path; no cloud/camera/geocoder/OSRM/AI service required at LIVE.

## Physical-location interpretation workflow (proposed)

1. **Extract question:** parse roadbook instruction verbatim, `source_instruction_id`, source order and official distance/time references; preserve provenance and OCR/interpretation uncertainty.
2. **Collect reference candidates:** POI names/coordinates from approved geocoders, OSM, government sources and NaviPRO database; capture source name and lookup time.
3. **Visual plausibility:** overlay image(s), inspect land use, visible building or site boundary, access road, intersection geometry, and date/resolution limits. Reject the inference “looks like an office therefore is this office.”
4. **Access binding:** distinguish building centroid from entrance/roadside route access and inspect actual directed graph connectivity.
5. **Constrained evaluation:** keep roadbook ordering fixed; check candidate graph paths against official distance interval, known route rules, and time constraints. Model each speed-rule segment separately rather than treating a total distance/average speed as authoritative.
6. **Evidence comparison:** show two or more candidates with provenance, imagery date and *distance/time residuals*; flag missing data and inconsistent interpretations.
7. **Human review:** navigator may record an evidence-backed location decision. Corrections are append-only versioned review records; never rewrite third-party data or the original roadbook silently.
8. **Feedback loop:** retain confirmed source reference, historical conflicting pins and evidence; invalidate/re-review when roadbook, place, graph, imagery, or time-rule versions change.

## Mathematical diagnostics, not approval formulas

For candidate sub-trayek `i`:

- `ΔD_i = D_graph_candidate_i - D_auth_i` (reported in **mm** with an explicit length source/uncertainty; positive/negative preserved).
- `T_candidate = Σ_j (D_rule_j / V_rule_j)` **only** for constant-speed portions where the applicable rally regulation specifies a positive speed; add separately documented stops/neutralized intervals/clock adjustments **per governing rules**. Actual legality and event-specific scoring may require a different time model.
- `ΔT = T_candidate - T_target_roadbook`, **only** when both are defined and comparable in the same clock/rule domain.

**Never make** `ΔD == 0` or `ΔT == 0` an automatic confirmation. No universal cut-off or tolerance is specified by NaviPRO until proven by official event rules, coordinate error model and instrument calibration.

## Canonical object design

- `RoadbookInstruction` (immutable source text/ordinal, event/rule version, official references).
- `LocationReference` (`POI_REFERENCE` source coordinate + data authority/provenance).
- `PhysicalLocationCandidate` (`PHYSICAL_LOCATION` geometry, verification status, imagery and documentary evidence).
- `RouteAccessCandidate` (`ROUTE_ACCESS_POINT` road-side candidate, graph version, one-way and entrance constraints).
- `ConstrainedRouteCandidate` (ordered anchor IDs, directed edges, graph profile/data digests, *separate* distance/time diagnostic domains).
- `LocationAssessment` (non-authoritative evidence, competing candidates, reviewer state, audit trail).
- `LocationDecision` (future design, human-confirmed, immutable revision tied to route snapshot; **not implemented**).

Contract-only starter: `contracts/jsonschema/physical-location-assessment.schema.json` (no REST operation, no human approval implementation).

## Source responsibility boundaries

| System | Evidence or calculation | Not permitted |
| --- | --- | --- |
| God's Eye View imagery / Cesium | Dated imagery, comparison, visible geometry | Decide building name, authoritative roadbook distance/time |
| OSM / Google / geocoder | POI name and candidate map pin | Auto-confirm physical truth |
| OSRM | Directed candidate geometry, connectivity, `D_graph` | Source anchor reorder, official mileage or speed-rule substitution |
| StreetComplete survey / field photography | Observed physical attributes and entrance details | Modify confirmed route without review |
| Kepler / map UI / React Native Maps | Presentation, candidate comparison, visualization | Mutate canonical route authority |
| NaviPRO deterministic core + navigator | Official rule evaluation, decision and audit | Claim verified without evidence/rule basis |

## Acceptance gates for a future implementation

- A mismatched POI pin is shown as `SUSPECT` rather than silently moved; at least two distinguishable candidates can be compared when evidence supports them.
- `POI_REFERENCE`, `PHYSICAL_LOCATION` and `ROUTE_ACCESS_POINT` are represented separately in persisted records and API responses.
- Independent `D_auth`, `D_graph`, `D_odo`, `D_geo`, and timing-rule inputs stay unmodified by visual map tools.
- Negative tests cover reordered anchors, wrong route revision, graph mismatch, ambiguous imagery, no capture date, impossible/missing time rules, unsupported provider rights and unauthorized approval.
- Human decision and later changes are traceable to source snapshot and evidence provenance.
- End-to-end tests include actual labeled ground-truth location(s) with safe, stationary evidence collection and real roadbook distance/time constraints.

**CURRENT STATUS: DESIGN + SCHEMA TESTS ONLY; `NOT_RACE_READY`.** No imagery acquisition/recognition, physical POI resolver, time solver, or field-validated correctness is delivered by this architecture note.
