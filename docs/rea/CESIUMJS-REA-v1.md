# NaviPRO RallyOS — REA CesiumJS `tjx578/cesium_maps_rally`

**Audit tanggal:** 2026-10-20. **Status target:** `CAPABILITY_REGISTRY + CONTRACTS + EXPERIMENTAL VIEWER SCAFFOLD + VERIFIED NUMERIC GEODESY`, bukan 3D runtime parity maupun race readiness.

## Ringkasan faktual

GitHub repo `https://github.com/tjx578/cesium_maps_rally` adalah fork `CesiumGS/cesium`, branch default `main`, SHA `7f17be4c05c0cc2f4bc6405f16ce521f620b0112` dan `cesium@1.145.0` (`@cesium/engine@26.3.0`, `@cesium/widgets@16.2.0`). Lisensi sumber Apache-2.0. Compare dengan upstream main SHA `621826db344eb7f1248f6bd50ed4770563127f12` menunjukkan upstream maju 204 commit dari commit fork; **bukan** bukti ada fitur rally custom pada fork. Tidak ditemukan custom rally commit pada head yang diinspeksi; cabang lain belum dibandingkan satu per satu.

**REA = capability reverse engineering**, bukan menyalin seluruh sumber. Fork berada sekitar 1 juta GitHub repository-size units (unit GitHub repo size dalam KB), sehingga menyalin keseluruhan repo sebagai submodule ke core NaviPRO akan menambah risiko maintenance. Lisensi Apache-2.0 berbeda dengan Kepler MIT dan atribusi harus tetap benar.

## Source architecture extracted

```text
CesiumJS root (node >=22)
├── packages/engine/Source/Core
│   ├── WGS84 ellipsoid, Cartesian3/Cartographic, Transforms (ECEF/ENU)
│   ├── Geodesic and geometry primitives
│   ├── terrain providers + sampleTerrainMostDetailed
│   └── clock, time and request scheduling
├── packages/engine/Source/Scene
│   ├── Globe/Camera/Scene; imagery + WMS/WMTS/XYZ
│   ├── 3D Tiles, I3S, glTF, point clouds, Gaussian splats, voxels
│   ├── clipping, picking, shadows and visibility context
│   └── terrain-aware primitives and rendering lifecycle
├── packages/engine/Source/DataSources
│   ├── GeoJSON / GPX / KML / CZML
│   ├── Entity / SampledPositionProperty / PathGraphics
│   └── time-dynamic entity relationships
├── packages/engine/Source/Renderer & Workers
│   └── WebGL draw pipeline and parallel terrain/geometry processing
├── packages/widgets/Source
│   └── Viewer / Timeline / Animation / Basemap / Scene modes
├── packages/sandcastle
│   └── examples/editor playground
└── Documentation/OfflineGuide/README.md
    └── offline provider replacement, geocoder disable, static file hosting
```

## Kemampuan spesifik untuk NaviPRO

| Source domain | Temuan terverifikasi | Adopsi NaviPRO dan batas |
|---|---|---|
| Earth coordinates | `Cartesian3`, `Cartographic`, `Ellipsoid`, `Transforms`, `EllipsoidGeodesic` | Canonical WGS84/ECEF/ENU bridge; geodesic distance hanya diagnostik, bukan D_auth |
| Terrain | `CesiumTerrainProvider`, `ArcGISTiledElevationTerrainProvider`, `sampleTerrainMostDetailed` | Elevation profile *proposal*, kualitas DEM/vertical datum/provider metadata wajib |
| 3D geometry | ground polyline, polygon/corridor, intersection tests | 3D route overlay dan route-corridor visualization; tidak mengedit route authoritative |
| 3D datasets | `Cesium3DTileset`, `Cesium3DTileStyle`, `I3SDataProvider`, `Model/Model` | building/landmark/context 3D, scene pick/read-only |
| Advanced 3D | `PointCloudShading`, `GaussianSplatPrimitive`, `VoxelPrimitive` | experimental P2; butuh dataset/benchmark, bukan default |
| Imagery | `ImageryLayer`, URL template, WMS, WMTS, ArcGIS, OSM | imagery provider adapters dengan allowlist dan attribution |
| DataSources | `GpxDataSource`, `KmlDataSource`, `GeoJsonDataSource`, `CzmlDataSource` | recce and observed trajectories, route overlays, time-dynamic view |
| Time | `Clock`, `JulianDate`, `SampledPositionProperty`, `PathGraphics` | PREP/REVIEW replay dan synchronized Kepler timeline, bukan live pacing |
| Camera | `Camera`, `SceneMode`, screen input, `Viewer` | 2D/3D camera inspections and repeatable camera bookmarks |
| Offline | `Documentation/OfflineGuide/README.md` | explicit offline defaults, no ion token required for empty ellipsoid, local asset server for 3D Tiles |
| Performance | request scheduling, workers, 3D cache, screen space error | rendering budget, frustum-dependent loading, visibility tests |

**Important nuance:** source library has APIs supporting parts of terrain profiling / line-of-sight style studies, but the fork is **not** an out-of-the-box survey-certified elevation-profile engine, GIS desktop editor, rally timing engine, or guaranteed network-free 3D application. Those are **NaviPRO-derived features to implement**, not source parity assertions.

## Coordinate and precision model

```text
NaviPRO GeoPointE7 (lat_e7, lon_e7)       => canonical horizontal coordinates
      |
      +--> WGS84 lon/lat radians --------> Cesium Cartographic
      |                                         |
      |                                         +-> Ellipsoid ECEF (x,y,z metres)
      |                                         +-> local ENU (for visual checks)
      |
      +--> RouteRevision/D_auth ----------> core authoritative value (unchanged)
      |
      +--> height sample + metadata -----> analytic-only elevation proposal
```

Never conflate **WGS84 ellipsoidal height** with **orthometric/geoid height** or arbitrary provider terrain height. Never substitute 3D straight-line distance or Cesium geodesic interpolation for authoritative roadbook or graph distance. An unknown altitude is `null/unknown`, **not 0m**. The standalone WGS84/ECEF converter added in the Python package is numeric domain code and is testable independently of the graphical renderer.

## Relative position of Kepler/Cesium/NaviPRO

```text
                     NaviPRO RallyOS (SSOT)
                 /            |              \
        Kepler Map Lab   Cesium Terrain Lab   Rally Core
        2D data analysis  3D terrain/globe     Directed graph
        H3/Heatmap/SQL   3D Tiles/WGS84       Roadbook/chainage
        Filters/editing  WMS/I3S/replay       Evidence/validation
                 \            /              |
                   visual context --------> Proposal only
                                               |
                                          HUMAN REVIEW
                                               |
                                           RouteRevision
                                               |
                                            NaviPack
                                               |
                                        Driver LIVE offline
```

A Kepler map snapshot and a Cesium scene snapshot refer to one immutable `RouteRevision` read-only. Synchronize data by **IDs**, not by mutating either renderer's internal state. Use scene-friendly normalized GeoJSON (WGS84 lon/lat) and GPX/CZML adapters, avoiding attempts to share mutable Redux state with Cesium EntityCollection.

## 3D decision workflow examples

1. **Landmark visibility**: load georeferenced scene/imagery → label its date/resolution/provider → camera viewpoints → potential candidate visibility; reviewer checks physical reality. 3D imagery/scene can be stale, occluded or horizontally/vertically misregistered; never infer survey-grade visibility.
2. **Terrain profile**: sample a read-only canonical route copy at fixed chainage reference points → terrain elevations carrying datum/resolution/status; missing samples remain unknown → analytic map preview; cannot revise D_auth, timing or route automatically.
3. **Recce replay**: load GPX, store source SHA/dates → synchronized Cesium camera/Clock and Kepler Trip/SQL timeline → review differences against canonical route with explicit GNSS uncertainties.
4. **Context comparison**: 3D tiles imagery date A vs provider date B; comparison is evidence and not official route geometry.

## Capability registry and phase gates

`contracts/spatial/cesium-capability-registry.yaml` records **69** source-indexed capabilities. Their source existence is **not** equivalent to working NaviPRO implementation. In phases:

- P0: coordinate bridge, controlled Cesium Viewer, GeoJSON/GPX/CZML loader contract, WMS/local imagery, terrain provider/height sampling, route overlay and provenance.
- P1: terrain profile with uncertainty, synchronized Kepler comparison, I3S/models, visual snapping, performance tests.
- P2: voxels/splats/advanced volumetric visualization and enhanced environmental effects.

**Approval gate** for real parity: successful `npm install/build`, offline zero-network tests, browser WebGL rendering screenshots, file fixtures for every claimed loader, 3D Tiles terrain and cache tests, height datum checks, large tiles stress, no-authority-mutation checks, Android Driver dependency audit, license/attribution/ion access review.

## Concrete artifacts

- `contracts/spatial/cesium-capability-registry.yaml`
- `docs/rea/CESIUMJS-SOURCE-MANIFEST.yaml`
- `contracts/jsonschema/cesium-3d-project.schema.json`
- `governance/cesium-3d-capability-policy.yaml`
- `apps/terrain-lab-web/` experimental CesiumJS viewer adapter scaffold
- `python/src/navipro_rallyos/spatial/geodesy3d.py` deterministic WGS84/ECEF conversion/validation
- `tests/contracts/test_cesium_rea.py` and `tools/validate_cesium_rea.py`
- Unified OpenAPI and generated MCP registry operations, proposals not execution

## Limitations and not-implemented statements

- Fork head is not independently rally-specific; source capabilities do not imply native rally logic.
- `Terrain Lab` packages are pinned but **not necessarily installed or built**; viewer rendering not yet proven.
- Cesium ion default imagery/terrain depends on external services/tokens. Demo defaults intentionally disable them; browser assets/workers need bundling and server configuration verified.
- All API operation definitions and generated MCP tools are **contracts**, not deployed endpoint handlers or an operative MCP server.
- No 3D data provider is authorized to promote location/route status or issue driver instructions.
- No live driving assistance / speed optimization is introduced by REA.
