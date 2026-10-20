# REA consolidation — Kepler.gl + CesiumJS + NaviPRO RallyOS

**Status:** DESIGN/CONTRACT CONSOLIDATED, WEBGL RUNTIME NOT VERIFIED, NOT_RACE_READY.

## Complementary responsibility model

| Plane | Kepler Map Lab | Cesium Terrain Lab | NaviPRO Rally Authority |
|---|---|---|---|
| Primary role | Dataset-centric 2D spatial analysis | Earth/terrain/3D scene inspection | Approved rally truth and deterministic geometry |
| Coordinates | WGS84 lon/lat data / Web Mercator display | WGS84 ellipsoid + ECEF + local ENU | GeoPointE7, versioned route geometry and distance domains |
| Large data | Arrow/Parquet/DuckDB, PMTiles, MVT | 3D Tiles, I3S, terrain mesh, models, Gaussian splats, voxel | Approved route graph, evidence and reference manifests |
| User interaction | Filters, H3, drawings, SQL, split maps | Camera, 3D picks, model/terrain clipping and viewpoints | Human review and explicit confirmation workflow |
| Time | Trip playback | Clock, CZML, animated entities | Timing rule profile remains immutable |
| Outputs | MapProjectSnapshot | Cesium3DProjectSnapshot | RouteRevision, NaviPack, release receipts |

## Cross-plane data exchange contract (proposed)

```text
[MapProjectSnapshot] -----> SpatialSceneEnvelope <----- [Cesium3DProjectSnapshot]
            |                       |                            |
            |               same event_id                         |
            |               same route_revision_id               |
            |               selection by stable feature ID       |
            |               timestamp UTC for review             |
            |               horizontal WGS84 lon/lat             |
            |                       |                            |
            +-----------------------+----------------------------+
                                    |
                              read-only preview
                                    |
                                 proposals
                                    |
                        human reviewer + validation
                                    |
                           canonical RouteRevision
```

**Invariants:** Replay time and camera are ephemeral visualization state; do not use them as official distance or timing. `GeoPointE7` serialization is identical across tools and keeps lat/lon explicit. Cesium `Cartographic.height` must have a named vertical datum and is *not* automatically present in 2D Kepler datasets. Kepler's 3D/Globe support overlaps with Cesium but does not replace Cesium's advanced terrain/scene APIs. Do not duplicate route-authority logic inside either viewer.

## Planned boundaries

- **Dataset Service:** File/URL ingest, checksum and source permission evidence. Kepler can handle Arrow/Parquet/GeoJSON; Cesium handles GeoJSON, KML, GPX, CZML and 3D-tile assets. Cross-conversion uses provider-neutral canonical DTOs.
- **Spatial Asset Service:** Managed registry of imagery/terrain/3D datasets with provider terms, capture timestamp, CRS, vertical datum, resolution, retrieval/caching policy. No arbitrary network URL can bypass allowlist.
- **Geometry Engine:** Stable route revision read service; 3D overlay is generated from route read model. Terrain samples can annotate a review copy but cannot change segment chainage.
- **Scene Bridge:** Browser PREP/REVIEW only, selection and time synchronization by immutable entity/dataset IDs; adapter no direct authority writes.
- **Validation:** Asset checksum, coordinate range, geometry revision binding, datum conversion proof, no-LIVE-dependency and offline network-deny receipts. No 3D view is authoritative without reviewer decision.

## Dependency and upgrade strategy

Inspect/pin version source (`Kepler 3.3.0-alpha.11` and `Cesium 1.145.0`) only as REA traceability snapshots. Before production, resolve stable compatible npm versions, test Vite bundling, WebGL browser support and license attribution. Both forks lag upstream as of audit; do not blindly merge upstream into NaviPRO. Put 3D lab in a separate route/bundle and lazy-load only in PREP/REVIEW; keep Driver Android free of Kepler, Cesium and React dependencies.

## Acceptance and verification levels

`SOURCE_INDEXED` means we observed a file/module, not a deployed capability. `CONTRACT_GENERATED` means OpenAPI and machine registry exist. `NUMERIC_TESTED` means offline Python geodesy tests pass. `VIEWER_SCAFFOLDED` means HTML/Vite/TS sources exist; not enough for runtime parity. `WEBGL_VERIFIED` requires clean install/typecheck/build, automated browser tests and fixture receipts. `FIELD_VALIDATED` requires reviewer-controlled accuracy checks in real conditions. Race-readiness is **not** inferred from any of these levels.

## Consolidated target 3D-specific acceptance scenarios

| Scenario | Minimum measurable receipt |
|---|---|
| Coordinate | WGS84↔ECEF numerical fixtures, correct longitude/latitude order |
| Terrain | Known DEM fixture, missing tile, vertical datum mismatch, resolution/provenance retained |
| 3D Tiles | Local tileset loaded and removed, memory budget and attribution test |
| Multi-format | GPX/KML/GeoJSON/CZML test datasets and replay exports |
| Asset policy | Unauthorized provider URL rejected and zero external requests offline |
| Kepler bridge | Same revision ID, selection ID and UTC replay frame on both viewers |
| Authority | Synthetic proposed line/picked object cannot confirm/overwrite RouteRevision |
| Driver isolation | Android Driver dependency graph contains no Terrain Lab/Kepler packages |

## Source links

- https://github.com/tjx578/kepler.gl-_mapas_rally
- https://github.com/tjx578/cesium_maps_rally
- https://github.com/CesiumGS/cesium-vite-example
- docs/rea/CESIUMJS-SOURCE-MANIFEST.yaml
- docs/rea/KEPLER-GL-SOURCE-MANIFEST.yaml
