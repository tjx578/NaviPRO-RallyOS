# NaviPRO RallyOS — REA Kepler.gl `tjx578/kepler.gl-_mapas_rally`

**REA:** Reverse Engineering Anything at capability/architecture level.  
**Status:** `IMPLEMENTATION_BASELINE / PREP_REVIEW / NOT_RACE_READY`  
**Source snapshot:** `tjx578/kepler.gl-_mapas_rally@d63c07d4` (`3.3.0-alpha.11`)

## 1. Executive finding

The inspected repository is **not a rally-specific mapping engine yet**. GitHub metadata identifies it as a public fork of `keplergl/kepler.gl`, and the inspected `master` head is the same upstream Kepler.gl release commit `3.3.0-alpha.11`. No additional rally-specific branch or custom fork commit was observed in the inspected fork. Therefore its value to NaviPRO is the complete Kepler.gl geospatial workbench architecture: large-data rendering, multi-layer visualization, filtering, drawing, time playback, tiles, raster/WMS, local analytics, schema save/load, export and extensibility.

As observed on 2026-10-20, upstream Kepler.gl had moved **130 commits** beyond the fork head with **300 changed files** in the compare result. NaviPRO must therefore extract capabilities from the fork but use a controlled dependency-upgrade process rather than blindly freezing all implementation details at alpha.11.

## 2. Architecture extracted from the source

```text
DATA INPUT
 CSV / GeoJSON / KML / GPX / TCX / Arrow / Parquet / URL / tiles
        │
        ▼
PROCESSORS + TABLE MODEL
 type inference / geometry inference / Arrow / data containers / DuckDB
        │
        ▼
STATE + TASK ENGINE
 actions → reducers/updaters → async tasks
        │
        ▼
LAYER ENGINE
 Point Arc Line Grid Hex GeoJSON Cluster Icon Heatmap H3 S2 A5
 GeoHash Flow Trip VectorTile RasterTile WMS Tile3D Bitmap Scenegraph
        │
        ▼
DECK.GL + LUMA.GL GPU RENDERING
        │
        ├── filters / selection / tooltip / brushing
        ├── drawing / annotations / measurements
        ├── time playback / trip animation
        ├── 2D / 3D / globe / split / swipe
        └── MapLibre / Mapbox basemap abstraction
        │
        ▼
SAVE / LOAD / EXPORT
 schema manager / JSON / HTML / image / CSV / video
```

## 3. What NaviPRO adopts

NaviPRO adopts the **capability set**, but places it inside a stricter rally boundary:

```text
                         NAVIPRO RALLYOS
                               │
                 ┌─────────────┴─────────────┐
                 │                           │
       SPATIAL INTELLIGENCE PLANE       RALLY AUTHORITY PLANE
       (Kepler-derived Map Lab)          (NaviPRO canonical core)
                 │                           │
       PREP / REVIEW only                    │
                 │                           │
 dataset/layers/filters/draw              RoadbookRevision
 tiles/raster/WMS/3D                     LocationDecision
 playback/SQL/analytics                  RouteRevision
 comparison/annotations                  TimingPlan
 export/project snapshot                 Validation gates
                 │                           │
                 └──── proposal/evidence ────┤
                                             ▼
                                      Human confirmation
                                             ▼
                                          NaviPack
                                             ▼
                                        Driver LIVE
```

**Critical boundary:** Kepler-style state is not route truth. A drawn line, a visual match, a SQL result, a heatmap, or a provider tile can generate evidence/proposals, but cannot reorder the roadbook, confirm a route, promote a location to VERIFIED, override a validation gate, publish a release, or mutate Driver LIVE.

## 4. Capability parity plan

The machine-readable source of this plan is `contracts/spatial/kepler-capability-registry.yaml`. It covers:

- multi-format ingest: CSV/TSV/DSV, JSON/GeoJSON, GeoJSONL/NDJSON, KML, GPX, TCX, Arrow/Feather, Parquet;
- WKT/geometry/type detection and visual layer proposals;
- 21 layer families including point/line/GeoJSON/trip/H3/vector/raster/WMS/3D;
- MVT and PMTiles; raster PMTiles; COG/STAC; WMS; 3D tiles;
- attribute, spatial and temporal filters;
- drawing/editing/measurement;
- tooltips, brushing, cursor coordinates, annotations;
- split maps, swipe, 3D, globe, legends, custom styles;
- time playback, trip animation and distance-vs-time charting;
- polling, host-row upsert and host WebSocket pattern;
- local DuckDB SQL, aggregations, table/column stats;
- map project schema/versioning;
- image/CSV/HTML/JSON/video export;
- component/state plugin architecture, feature flags, custom icons, localization/theme;
- GPU rendering and progressive/abortable data/tile workloads.

## 5. Rally-specific enhancements beyond Kepler

Capability parity is necessary but not sufficient. NaviPRO must exceed the source for Time Rally by adding:

1. **Roadbook-ordered route semantics** — no TSP/reordering.
2. **Directed-edge canonical route** — dense geometry with edge IDs and cumulative offsets.
3. **Distance domains** — `D_auth`, `D_graph`, `D_odo`, diagnostic geodesic distance kept separate.
4. **Evidence lifecycle** — candidate/observation/reviewer decision, not visual truth by assumption.
5. **KM PAL reasoning** — parser + corridor + reverse-distance evidence with explicit ambiguity handling.
6. **Timing authority profiles** — absolute timing, mode, clock scale and rounding bound to event authority.
7. **16 blocking validation gates** — fail closed to HOLD.
8. **Immutable route revision and human confirmation**.
9. **NaviPack compile/release** with hashes, receipts and version binding.
10. **Driver offline runtime** — no Map Lab, agent, cloud provider, or dynamic reroute in LIVE.

## 6. Layer role in Time Rally

| Layer family | Rally use | Authority |
|---|---|---|
| Point/Icon | landmark, KM PAL, control point, observation | evidence only until reviewed |
| Line/GeoJSON | official route overlay, candidate route, actual track | confirmed route only after route gates |
| Trip | GPS replay / recce / actual-vs-plan playback | observed track, not route authority |
| Heatmap/Grid/Hex/H3 | ambiguity density, GPS quality, event coverage | analytics only |
| Vector Tile/PMTiles | offline basemap/context and very large spatial datasets | map context, graph authority separate |
| Raster/WMS/COG | satellite/aerial/topographic evidence | provider evidence only |
| 3D/Scenegraph | terrain/building/landmark inspection | review aid |
| Flow/Arc | relation/OD visualization | analytics only |

## 7. State separation

NaviPRO keeps two independent revision lines:

- `MapProjectSnapshot` — mutable PREP/REVIEW visualization state.
- `RouteRevision` — canonical rally route state with human authority.

A Map Lab snapshot may refer to a `RouteRevision` read-only. It cannot silently overwrite it. Geometry edits produce new proposals or draft route revisions and force re-validation.

## 8. Implementation artifacts created by this REA

- `docs/rea/KEPLER-GL-SOURCE-MANIFEST.yaml` — source provenance and upstream delta.
- `contracts/spatial/kepler-capability-registry.yaml` — machine-readable parity registry.
- `governance/spatial-capability-policy.yaml` — PREP/REVIEW/LIVE restrictions.
- `contracts/jsonschema/spatial-map-project.schema.json` — versioned Map Lab snapshot contract.
- `apps/map-lab-web/` — Kepler integration scaffold pinned to the inspected fork release.
- `python/src/navipro_rallyos/spatial/` — read-only capability registry API.
- `tools/validate_spatial_rea.py` and contract tests.
- Unified OpenAPI receives a Spatial domain and MCP-safe proposal/read operations.

## 9. Acceptance criteria for actual parity

A capability changes from `SCAFFOLDED` to `VERIFIED` only after a receipt exists. Minimum receipts:

- ingest fixtures for every accepted format;
- layer render golden tests and large-dataset stress tests;
- filter/drawing/measurement correctness tests;
- MVT/PMTiles/raster/WMS source tests including cancellation/retry;
- map snapshot round-trip compatibility tests;
- playback/trip timing tests;
- SQL query sandbox tests;
- split/swipe/3D/globe visual tests;
- no-authority-mutation tests;
- PREP/REVIEW network policy tests and LIVE network-deny tests;
- Android Driver confirmation that no Map Lab/Kepler dependency ships in LIVE.

## 10. Decision

**Adopt:** Kepler's spatial workbench architecture and capabilities.  
**Do not adopt as authority:** Kepler's generic map state as rally truth.  
**Do not embed in Driver LIVE:** the high-flexibility web mapping workbench.  
**Optimal NaviPRO position:** Kepler-grade spatial analysis in PREP/REVIEW + NaviPRO-grade deterministic rally authority, route compilation, timing, evidence, validation and offline cockpit.
