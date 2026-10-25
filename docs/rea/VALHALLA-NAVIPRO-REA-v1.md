# Valhalla REA for NaviPRO RallyOS — routing provider #2

**Audit date:** 2026-10-20

**Fork:** https://github.com/tjx578/valhalla-navipro

**Pinned commit:** `618cad5eb6a12c7787c3480851eda07c99eb5c74` (branch `master`)

**Original:** https://github.com/valhalla/valhalla

**Upstream comparison:** `valhalla/valhalla:master...tjx578/valhalla-navipro:master` = `identical`, 0 ahead/0 behind at audit. **No NaviPRO custom code found.**

**Code license:** MIT (`COPYING`); OSM dataset licenses and attribution are separate (ODbL).

**Status:** PREP/REVIEW request, native-result and provider-comparison **Python prototypes with mock/fixture tests**. Neither a compiled Valhalla engine nor a real OSM graph service has been installed or benchmarked by this integration.

## 1. Reverse-engineered layout (source evidence)

| Source | Capability documented or implemented upstream | Adaptation decision |
|---|---|---|
| `src/loki/route_action.cc` | Pre-route location correlation | Coordinate candidates only; no place-name geocoding |
| `src/thor/route_action.cc` and `bidirectional_astar.cc` | Directed route computation | Candidate graph distance, not official rally `D_auth` |
| `src/thor/matrix_action.cc` | Matrix calculation | Comparing location candidates; unreachable remains null |
| `src/thor/trace_attributes_action.cc` | Detailed path/road attributes | Future intersection evidence; not live driver requirement |
| `src/meili/map_matcher.cc` | Trace map matching | Future post-event REVIEW, never mutate approved NaviPack |
| `src/odin/maneuversbuilder.cc` | Turn narrative construction | Non-authoritative proposal compared with official DSL |
| `src/sif/autocost.cc` and `dynamiccost.cc` | Automotive costing | Only versioned allowlisted profile; cannot replace time-rally rules |
| `src/baldr/` and `src/mjolnir/` | Tiled graph and tile construction | Candidate self-hosted Valhalla service for graph experiments |
| `docs/docs/api/route/api-reference.md` | Ordered locations; `break`, `through`, `via`, `break_through`; `format`, `units`, alternates | Intermediate `break_through`, first/last `break`; no auto-reordering |
| `docs/docs/api/matrix.md` | `sources_to_targets` directed time/distance matrix | Index, unit, unreachable-cell validation |
| `docs/docs/api/map-matching.md` | `trace_route` and `trace_attributes` semantics | Deferred to REVIEW after provenance and privacy rules |
| `docs/docs/api/optimized.md` | `optimized_route` can reorder intermediate locations | **Forbidden for authoritative roadbook anchors** |
| `docs/docs/api/locate.md` | Streets/intersections adjacent to known coordinates | Useful for physical access validation, **not** POI name geocoding |

**Source links:** Prefix all paths with `https://github.com/tjx578/valhalla-navipro/blob/618cad5eb6a12c7787c3480851eda07c99eb5c74/`.

## 2. Differential value relative to OSRM

**Documented facts:** Valhalla natively supports route, matrix, locate, map matching/trace attribution, isochrone, time-dependent and dynamic costing, and various waypoint types. OSRM in the NaviPRO baseline already supports Route/Table/Nearest/Match services, and OSRM routing UI/LRM concepts are modeled. Neither is a roadbook solver.

**Engineering hypothesis, unproven:** Valhalla waypoint semantics, intersection/edge details and profile experiments may be more expressive for ambiguous text-based Time Rally instructions than one unconstrained OSRM route result. Neither source establishes superior accuracy or performance on Indonesian roads. An apples-to-apples benchmark with the same OSM snapshot, coverage, constraints, and hardware is mandatory before selecting the primary provider.

**Policy:** keep OSRM, add Valhalla as selectable provider for Page 2. Do not introduce a second map renderer. MapLibre/PMTiles remain 2D, Cesium/God's Eye satellite inspector remain geospatial evidence renderers, LRM is a route-editor interaction pattern; providers only compute/attribute candidate directed paths.

## 3. Workflow across five surfaces

| Surface | Valhalla role | Authority boundary |
|---|---|---|
| Page 1 Data Rally | None directly; parser supplies immutable roadbook constraints to Page 2 | Never infer official distance from graph |
| **Page 2 Routing Workbench** | Route / matrix candidate calls, compare with OSRM; propose geometry and maneuver evidence | Navigator review/confirmation required |
| Page 2 Satellite/3D Inspector | Display same candidate geometry against dated imagery/terrain | Visually plausible feature cannot alone confirm landmark identity |
| Page 3 Rally Agent | May request read-only explanation/proposal from Page 2 provider gateway | No direct publish, route edit or provider URL selection |
| Driver 1/2 | **No Valhalla HTTP call in LIVE**; read immutable confirmed NaviPack offline | No reroute or authority promotion |

## 4. Prototype implemented in this REA

- `python/src/navipro_rallyos/route/valhalla_adapter.py`: native `POST /route` and `/sources_to_targets` builders; enforces ordered `RouteAnchor` (integer E7), intermediate `break_through`, `units: kilometers`, `costing: auto`, no trip optimization. Validates native `trip` status/legs/length/duration/shape; decodes full polyline6 into WGS84 GeoJSON; preserves Valhalla maneuvers as **proposals**, records graph dataset/profile/build; matrix validates row/column indices and rejects silent missing-cell substitutions.
- `python/src/navipro_rallyos/route/provider_comparison.py`: displays unranked OSRM/Valhalla graph-distance residuals against supplied official distance without modifying it, requiring matching source-anchor order and graph dataset labels. Equality of dataset labels is **insufficient to prove graph equivalence**.
- `tests/contracts/test_valhalla_rea.py`: mocked native response, negative path and authority tests. Tests do **not** start or compile Valhalla.
- `governance/valhalla-routing-policy.yaml` and `contracts/routing/valhalla-capability-registry.yaml`: source/rights/action constraints, release gates, deferred endpoints.

### Provider route contract

Input: ordered canonical anchor IDs + E7 WGS84, `graph_dataset_id`, `profile_digest`, `valhalla_build`.

Output: `source_anchor_order`, `graph_distance_mm_candidate`, `estimated_travel_seconds`, `geometry`, `provider_maneuvers_proposal`, `route_authority:false`, provenance and warnings.

`format=json` retains native Valhalla; `alternates` deliberately disabled at adapter execution in this prototype until a native alternate-trip normalization contract is reviewed. Multipoint alternates are unsupported by the Valhalla API per documented constraints.

### Integration review corrections

The two supplied patches were replayed on the logo commit `af0f4e5`. Their 120 existing Python contract tests passed, but three additional negative/preservation tests exposed accepted reordered native locations, missing matrix values being interpreted as unreachable, and discarded matrix warnings.

The separate correction commit:

- Requires native `locations[].original_index` to be the exact ordered integer index before assigning source-anchor IDs. It does not equate snapped coordinates with official source coordinates.
- Requires both `distance` and `time` keys in every matrix cell. Only explicit paired `null` values indicate an unreachable provider result; absent fields are malformed evidence.
- Preserves route warnings from `trip.warnings` and matrix warnings from the top-level `warnings` array. A malformed warning array is rejected.
- Requires `graph_dataset_id`, `profile_digest` and `valhalla_build` for both route and matrix calls, rejects empty provenance before transport, and retains it in normalized output. These caller-supplied labels do not independently attest the server's actual build.

Native serialization was checked at pinned upstream commit `618cad5eb6a12c7787c3480851eda07c99eb5c74` in [`route_serializer_valhalla.cc`](https://github.com/tjx578/valhalla-navipro/blob/618cad5eb6a12c7787c3480851eda07c99eb5c74/src/tyr/route_serializer_valhalla.cc) and [`matrix_serializer.cc`](https://github.com/tjx578/valhalla-navipro/blob/618cad5eb6a12c7787c3480851eda07c99eb5c74/src/tyr/matrix_serializer.cc). Regression tests are in `tests/contracts/test_valhalla_response_integrity.py`.

Local tests require the RFC3339 format checker used by the pre-existing location schema tests (for example `rfc3339-validator==0.1.4` and its `six` dependency). UTF-8 mode (`python -X utf8 -m pytest -q tests/contracts`) avoids locale-dependent reads on Windows. Neither local test success nor declaration-only PREP/REVIEW labels prove authenticated runtime enforcement.

### Known technical caveats

1. Intermediate `break_through` forbids U-turn at that anchor. A legitimate U-turn instruction requires an explicit, reviewed waypoint policy enhancement. Do not quietly change it to `break`.
2. Valhalla returns directions based on its graph/costing; the maneuver labels do not prove a roadbook instruction was obeyed.
3. The matrix can estimate provider travel time but not rally-target time. `T_graph_estimate` must be separate from `T_auth`.
4. This clean-room prototype reuses bounded HTTP transport from the OSRM adapter for optional trusted loopback requests. **No running service is claimed**.
5. Provider warnings, snapped candidate geometry, and road graph may omit/alter landmarks. A site name still requires dedicated NaviPRO POI/physical-location resolution and independent evidence.
6. Current native route adapter handles only the primary route and assumes ordinary successful native JSON responses. Protocol fixture mocks are not substitutes for integration tests with actual Valhalla versions.
7. The same declared OSM dataset ID does not ensure matching graph topology: OSRM and Valhalla perform different graph preprocessing, speed/access filtering and edge costing.

## 5. Required independent benchmark — ROTR Surabaya

Source of truth: manually reviewed image transcription of the 2025 ROTR Surabaya roadbook; do not infer missing geographic positions. Use sections B/C/D with official `7.57 / 5.75 / 6.28 km`, `25 / 20 / 22 min`; total `19.60 km`, total event allocation `120 min` including A and E; note `2.93 km` reference unresolved, ending/starting gaps, repeated Jl. Jawa. Evaluate realistic pinned graph snapshots of Surabaya using both OSRM and Valhalla.

| Gate | Expected behavior | Metric |
|---|---|---|
| G1 Pinned provenance | OSM extract, build SHA, profile digest, Valhalla/OSRM versions | Reproducible builds |
| G2 Ordered instructions | Every roadbook anchor/turn constraint keeps its original order, including loops | 0 silent anchor changes |
| G3 Physical locations | Site centroid vs access point explicitly distinguished | Reviewed POI identity correctness |
| G4 Distance | `D_auth`, `D_graph`, `D_geo`, `D_odo` never merged | Per-section residual distributions |
| G5 Time | Rally `T_auth` stays independent of provider ETA | 0 target-time overwrites |
| G6 Edge cases | One-way, U-turn, bridge, multilevel, ambiguous turn, disconnected path | Detailed fail/review evidence |
| G7 Latency/resources | Repeat under same server hardware/data | p50/p95 latency and memory |
| G8 Offline | Driver loads signed NaviPack without routing HTTP | No service call in LIVE |
| G9 Regression | Contract + real server integration + field data | All gates pass before promotion |

**Decision: keep BOTH as PREP/REVIEW candidates. No claim that Valhalla replaces OSRM or that route evidence is confirmed.**
