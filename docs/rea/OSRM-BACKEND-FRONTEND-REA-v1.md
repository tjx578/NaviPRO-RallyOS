# REA v1 — OSRM Backend + Frontend → NaviPRO RallyOS

**Audit date:** 2026-10-20. **Status:** SOURCE_INSPECTED, CONTRACT_GENERATED, ADAPTER_PROTOTYPE_TESTED, NOT_BUILD_VERIFIED, NOT_RACE_READY.

## 1. Scope and method

Repositories:

- [tjx578/osrm-backend-maps-rally](https://github.com/tjx578/osrm-backend-maps-rally) at `f0a7a2ff0877c534316a2a0a16830228fe45178f`, upstream Project-OSRM/osrm-backend, BSD-2-Clause. At audit, upstream was 8 commits newer (not custom rally divergence).
- [tjx578/osrm-frontend-rally-maps](https://github.com/tjx578/osrm-frontend-rally-maps) at `067092c0c01efd57c2bf1c2b1e9fc1da4a193871`, upstream Project-OSRM/osrm-frontend, repository BSD-2-Clause; package.json declares ISC (dependency/file-level license review required). At audit upstream was 5 commits newer.

Audited directly from GitHub metadata, tree and key source files, unit test listings, README and API docs. No full source clone/build/OSM dataset was run. `contracts/routing/osrm-capability-registry.yaml` indexes **56 individually attributed capabilities** (34 backend / 22 frontend); indexed ≠ equivalent or implemented. Unlike the user repo name, upstream code is general-purpose routing, **not a Time Rally engine**.

## 2. Source architecture, backend

```
PBF/OSM dataset + Lua profile + optional location-dependent data
            |
         osrm-extract   (directed, edge-based graph; restrictions)
            |
      +-----+-----+
      |           |
  osrm-contract   osrm-partition → osrm-customize
       CH                      MLD
      |                         |
      +-----------+-------------+
                  |
             osrm-routed
                  |
     Route / Nearest / Table / Match / Trip / Tile
```

### 2.1 Profile semantics: important limitation

Source `profiles/car.lua` sets `weight_name='routability'`, enabling penalties for road preference, U-turns, turns, vehicle dimension/access exclusions, and turn restrictions. This means the returned route is *optimized by configured weight*, **not necessarily shortest distance**, and not a correct official roadbook by construction. The source car.lua additionally includes `lane_markings_penalty` and `priority_penalty` routing preferences. `profile_digest` and dataset identity MUST be recorded; different profiles can yield different answers.

### 2.2 Route

OSRM `route/v1` searches ordered supplied coordinates; supports alternatives, steps, full GeoJSON/polyline geometry, bearings, approaches and annotations. We must supply **all immutable official anchors in source order**, request `geometries=geojson, overview=full`, keep alternatives separate, and block unapproved shaping/pin changes. A route may be fast yet violate ambiguous roadbook semantics, intermediate landmark coverage, or exact approach orientation. OSRM legs do not by themselves prove all source events are covered; a graph edge/turn matcher and `CoverageBinding` validator remain required.

### 2.3 Nearest

OSRM `nearest` supplies snap candidates on the network (not a 'verified physical position'). Preserve original vs snapped coordinates, displacement, approach and profile. Do not silently replace surveyed/verified POIs or KM PAL anchors with graph snaps.

### 2.4 Table

An asymmetric distance/duration matrix represents travel on the **cost-optimal route per pair**; its distances are not necessarily minimum-distance paths. Null cells mean disconnected/unreachable. `fallback_speed` can produce synthetic great-circle-derived matrix cells; NaviPRO forbids this for compliance or evidence claims. `scale_factor` modifies durations and must not silently leak into rally timing authority.

### 2.5 Match

GPS sample map matching may split into subtraces, reject outliers, or have multiple plausible paths. Use source timestamps in UTC seconds, provided GNSS precision, and preserve `tracepoints` null locations and per-matching confidence. A high confidence number is not ground-truth validation. Do not change source order or route revision on a match response; display it next to recorded track and immutable confirmed route for navigator review.

### 2.6 Trip

Trip solves TSP and **changes point order**. It is explicitly prohibited for Rally Official, even when `source=first` and `destination=last`, since intermediate source-order constraints may still be broken. Its availability in upstream source does not imply we should expose a NaviPRO MCP tool for it.

### 2.7 Tile & graph debug

`tile` emits graph-related MVT debug data, not the authoritative NaviPRO map or proof of routability alone. Use review-only overlay for strongly connected components, restriction anomalies, edge class/speeds, investigation of `NoSegment`/`NoRoute` and coverage gaps. Such debug tile data may depend on build/profile/graph version.

### 2.8 CH vs MLD

The source recommends **MLD as default**, with **CH sometimes stronger for very large matrices**. Choose per measured workload; neither replaces data quality checks. Graph builds and source PBF must be pinned (SHA/dataset ID, UTC version, Lua profile SHA, algorithm). MLD `customize` permits speed/turn changes but a mutated weight model changes results: publish a new immutable graph manifest. The OSRM graph on server is **not yet a NaviPRO offline Android SDK**.

## 3. Source architecture, frontend

Source uses `Leaflet`, `leaflet-routing-machine`, geocoder, Vite, `osrm-text-instructions`, GPX generator and several thin client modules. It supports runtime `OSRM_MODES` (multiple backends), `OSRM_GEOCODERS` including no-geocoder coordinates-only, self-hosted `OSRM_TILE_URL`, backend same-origin proxy guidance for credentials, mode selection, alternative route selection, interactive waypoints, place entrances, GPX export, URL share state, localized instructions and debug map. `src/router_patches.js` prevents stale/aborted requests overwriting newer results and normalizes antimeridian coordinates; `src/route_throttle.js` limits preview request bursts. It can reorder waypoint rows with drag handles (`src/waypoint_reorder.js`), **which NaviPRO must disable** for official anchors.

**Human choice feature:** `src/entrance_waypoints.js` deliberately avoids assuming the nearest/main entrance is correct. NaviPRO can use the pattern for candidate physical entrance/finish anchors while preserving evidence/source links and review authority. A geocoded centroid is not a verified road-access anchor.

### 3.1 Frontend boundary

Create `apps/routing-lab-web` as isolated Page 2 review UI. Source-driven route list is locked; only explicitly separate user shaping points can be offered for a candidate leg. Alternative selection never mutates the confirmed route. GUI status currently `NOT_BUILT`; included `review-policy.mjs` is a tested state-only prototype, not a port of Leaflet Routing Machine.

### 3.2 Secret handling and unavailable providers

The source README warns that backend credentials must not be embedded in `OSRM_MODES`/browser `config.json`; use a server-side reverse proxy. Prevent accidental live calls to public Nominatim/map tile servers when offline. A true offline Page 2 must use local tiles/geocoder and local/self-hosted routing (or prepared data with no network). Driver LIVE consumes confirmed NaviPack, not a browser OSRM request.

## 4. Mapping into the NaviPRO canonical architecture

| NaviPRO layer | Adopts from source | Protection |
|---|---|---|
| Page 1 / Data Rally | None directly; consume `D_auth` and event timing separately | Do not use OSRM duration to determine official TSD time |
| Page 2 / Route Editor | Ordered candidate routing, debug graph, alternatives, review UI, snapping | Roadbook source immutable, human approval and gates |
| Page 3 / Rally Agent | MCP read/plan tools for route/matrix/match/snapshot | Read/propose only; no route confirmation |
| Evidence | Original vs snapped anchor, track match confidence, graph provenance | Not VERIFIED from provider response |
| StreetComplete Field Survey | Detect missing road signs/oneway/surface and create targeted human survey tasks | Review before modifications of graph data |
| Kepler Map Lab | Show candidate vs confirmed, matrix/filter, histograms, GPS replay | Presentation/analysis only |
| Cesium Terrain Lab | 3D render route candidates, elevation context | Terrain measurements not official odo or graph distances |
| Graph build plane | OSM PBF snapshot → extraction → CH/MLD processing | Preserve independent versioned graph manifests |
| Validation gates | Signed revision review, ordered events, directed-edge continuity, mandatory landmarks, residuals | Fail closed until verified |
| Offline Driver | Existing NaviPack confirmed geometry | No REST/MCP/cloud routing dependency in LIVE |

## 5. Canonical data contract and distance model

`OfficialSourceEvent(seq, source_hash, instruction)` → `PhysicalAnchor(id, coordinate evidence, status)` → `OSRMGraphManifest(dataset, OSM digest, Lua profile digest, CH/MLD)` → `RoutingCandidate(ordered anchors, geometry, leg count, estimated distance/time, graph digest)` → `ReviewResult` → `RouteRevision(DRAFT)` → validation → navigator confirm.

**No equivalence:** `D_auth` (roadbook declared target) ≠ `D_graph_candidate` (OSRM generated route distance) ≠ `D_odo` (tripmeter) ≠ `D_geo` (geodesic). OSRM `distance` in meters becomes `graph_distance_mm_candidate` ONLY. Authoritative `D_graph` and `CoverageBinding` require the separate NaviPRO directed-edge validation pipeline, *not implemented here*. OSRM durations assume routability/profile objective and cannot substitute event-specific `clock_scale` and timing rounding rules.

Example `GraphManifest` fields: `graph_dataset_id`, `osm_source_sha256`, `osm_data_version` (nullable), `lua_profile_sha256`, `algorithm`, `prepare_pipeline`, `build_binary_digest`, `prepared_at`, `region_bbox`. Responses may omit `data_version`; mark missing version warning, do not invent.

## 6. API / MCP consolidation

New `/routing/*` OpenAPI paths:

| operationId | MCP tool | Intent |
|---|---|---|
| inspectRoutingGraph | navipro.routing.graph.inspect | Dataset/provenance plan |
| inspectRoutingProfile | navipro.routing.profile.inspect | Profile/rules plan |
| planNearestRoadSnaps | navipro.routing.nearest.plan | Non-authoritative snapping |
| calculateOrderedRouteCandidates | navipro.routing.route.candidates | Ordered candidates; no Trip |
| calculateRoutingMatrix | navipro.routing.matrix.calculate | Non-fallback matrix |
| matchReviewTrace | navipro.routing.trace.match | Trace review |
| assessMatchedTrace | navipro.routing.trace.assess | Gaps/outliers assessment plan |
| planRoutingDebugTiles | navipro.routing.debug.tiles.plan | Review debug layer |
| planRoutingReviewSession | navipro.routing.frontend.session.plan | Page 2 UI session plan |

All allow only `PREP`, `REVIEW`, never `LIVE`; `x-navipro-mcp: true` is an **interface registry entry**, not a deployed tool or authenticated runtime. No `trip`, `route.confirm`, or route-order edit MCP tool added. Authenticated navigator confirmation remains a separate existing guarded operation.

## 7. Actual prototype work in NaviPRO repo

- `python/src/navipro_rallyos/route/osrm_adapter.py`: self-contained ordered anchor immutable input validation, deterministic payload constructors for OSRM HTTP POST `route/table/match`, response normalizers, loopback-only default origin, injectable transport for tests. Strict result validation: `code=Ok`, full GeoJSON LineString, correct legs and waypoint count, positive finite values, nonduplicated source anchor IDs, graph/profile identity, no inferred compliant status.
- `apps/routing-lab-web/src/review-policy.mjs`: immutable source anchor order, candidate alternatives, no approval/reorder/trip in review state. No GUI yet.
- `contracts/routing/osrm-capability-registry.yaml`: 56 indexed source capabilities with file links.
- `governance/osrm-routing-policy.yaml`: boundary rules and denied actions.
- `contracts/openapi/navipro-rallyos.openapi.yaml`: +9 conceptual operations and associated schemas.
- `services/mcp/generated-tool-registry.yaml`: generated metadata, not functioning server.

The adapter uses actual Python code and mocked/injected backend responses in unit tests; no OSRM binary, road graph, real PBF, browser routing UI, or comparative route benchmark has been executed.

## 8. Risk assessment (critical)

**R1 route authority contamination:** frontend waypoint drag and backend Trip can silently reorder mandatory roadbook steps. Deny and test independently in API/backend/client; a UI switch alone does not enforce permission.

**R2 graph/survey mismatch:** StreetComplete observations/OSM data are not guaranteed synchronized with OSRM graph. The source timestamp/hash + Lua profile + graph digest must be displayed and checked on every candidate.

**R3 nearest/centroid error:** snapping may land on the wrong side of divided roads or wrong physical entrance. Preserve source and snapped coordinates separately. Restrict radius/bearing/approach where evidenced; human review mandatory.

**R4 false precision:** return meters/seconds vs official millimeters/milliseconds; never round-to-fit. No valid road route ⇒ `NoRoute/HOLD`; disable table fallback and avoid Haversine-based compliance.

**R5 GPS ambiguity:** route match can split segments, omit outliers, report confidence. Do not treat confidence as verified route or use it as a replacement for field evidence.

**R6 external service security:** restrict URLs to server-side approved OSRM origins; no user-supplied agent URLs, require TLS/auth, rate limits, max body, redirect rejection, logging redaction, timeouts and response quotas. Prototype uses loopback default; production API gateway security is NOT built.

**R7 offline semantics:** self-hosted OSRM on preparation computer is possible; **OSRM C++ server is not automatically an embedded Android offline routing library**. Driver does not need to recalculate official routes. If mobile recalculation is later required it must be designed separately, confined to authorized modes and independently validated.

**R8 license:** OSRM repository BSD-2-Clause; frontend package manifest says ISC despite repository LICENSE reporting BSD-2-Clause. Audit third-party submodules/dependencies before copying/distribution; attribute OSM ODbL data. Clean-room examples have no copied OSRM code.

## 9. Delivery milestones and acceptance criteria

1. **M0 provenance/contracts (COMPLETE):** source manifests, capability registry, policy, nine REST/MCP contracts; tests validate unique operationIDs, no LIVE exposure and forbidden Trip.
2. **M1 candidate adapter prototype (COMPLETE with mocked OSRM only):** coordinates lon/lat, ordered anchor lineage, full geometry, graph version, fail closed. Unit tests verify.
3. **M2 real graph runtime (NOT STARTED):** extract pinned Bali OSM PBF, pin car profile, build MLD and CH, use OSRM Docker, graph health, data checksums, request limits; measure routing results on representative sub-trayeks.
4. **M3 Page 2 GUI and map provider (NOT STARTED):** Leaflet or MapLibre visualization, locked official source, alternatives, snapping and debug MVT; verify with browser test and no third-party map dependency in offline prep.
5. **M4 validation parity (NOT STARTED):** directed-edge chain continuity, event source coverage, distance residual gates, GPS trace split/outlier and OSM stale graph tests; human decisions and immutable signed revisions.
6. **M5 driver evidence / integration (NOT STARTED):** pack manifest, referential hash checks, offline replay/performance and field review. No network routing in LIVE.

## 10. Decision

Reuse OSRM C++ as **version-pinned, separately deployed routing provider** after graph validation; do not rewrite CH/MLD in Python and do not vendor the entire source into NaviPRO Core. Reimplement/adapt frontend interaction patterns in Page 2 with immutable roadbook controls. Keep Kepler, Cesium, StreetComplete and OSRM as complementary planes over a shared canonical route/evidence model.

**Status: REA_COMPLETE_AT_SOURCE_AND_CONTRACT_LEVEL / NOT_RUNTIME_PARITY_VERIFIED / NOT_RACE_READY.**
