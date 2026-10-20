# CesiumJS → NaviPRO — 69-capability coverage matrix

**Basis:** inspected fork `7f17be4c05c0cc2f4bc6405f16ce521f620b0112` (`1.145.0`). **All target statuses `IMPLEMENTATION_PENDING`**: source exists, but functional NaviPRO parity is not yet proven. Status numeric geodesy separate from source library parity.

## Priority groups

| Priority | Count | Gate |
|---|---:|---|
| P0 | 27 | required baseline |
| P1 | 32 | second wave |
| P2 | 10 | experimental/advanced |

| Group | Source capabilities |
|---|---:|
| camera | 8 |
| geodesy | 8 |
| geometry | 7 |
| imagery | 7 |
| offline | 4 |
| terrain | 9 |
| tiles3d | 11 |
| time_data | 10 |
| widgets | 5 |

## Detailed source-to-target traceability

| ID | Source component | Source capability | NaviPRO target | Priority | Status |
|---|---|---|---|---|---|
| `CESIUM-3D-001` | [Cartesian3.js](https://github.com/tjx578/cesium_maps_rally/blob/7f17be4c05c0cc2f4bc6405f16ce521f620b0112/packages/engine/Source/Core/Cartesian3.js) | Geographic degrees to Earth-centered Earth-fixed Cartesian positions | `spatial3d.coordinates.ecef` | P0 | PLANNED |
| `CESIUM-3D-002` | [Cartesian3.js](https://github.com/tjx578/cesium_maps_rally/blob/7f17be4c05c0cc2f4bc6405f16ce521f620b0112/packages/engine/Source/Core/Cartesian3.js) | Cartesian 3D coordinate vector operations | `spatial3d.coordinates.cartesian` | P1 | PLANNED |
| `CESIUM-3D-003` | [Cartographic.js](https://github.com/tjx578/cesium_maps_rally/blob/7f17be4c05c0cc2f4bc6405f16ce521f620b0112/packages/engine/Source/Core/Cartographic.js) | Geodetic longitude latitude and ellipsoidal height representation | `spatial3d.coordinates.cartographic` | P0 | PLANNED |
| `CESIUM-3D-004` | [Ellipsoid.js](https://github.com/tjx578/cesium_maps_rally/blob/7f17be4c05c0cc2f4bc6405f16ce521f620b0112/packages/engine/Source/Core/Ellipsoid.js) | WGS84 reference ellipsoid and cartographic/cartesian transforms | `spatial3d.coordinates.ellipsoid` | P0 | PLANNED |
| `CESIUM-3D-005` | [EllipsoidGeodesic.js](https://github.com/tjx578/cesium_maps_rally/blob/7f17be4c05c0cc2f4bc6405f16ce521f620b0112/packages/engine/Source/Core/EllipsoidGeodesic.js) | Surface geodesic interpolation and diagnostic distance | `spatial3d.geodesic.inspect` | P1 | PLANNED |
| `CESIUM-3D-006` | [EllipsoidRhumbLine.js](https://github.com/tjx578/cesium_maps_rally/blob/7f17be4c05c0cc2f4bc6405f16ce521f620b0112/packages/engine/Source/Core/EllipsoidRhumbLine.js) | Rhumb-line representation and geometry comparison | `spatial3d.rhumb.inspect` | P2 | PLANNED |
| `CESIUM-3D-007` | [Transforms.js](https://github.com/tjx578/cesium_maps_rally/blob/7f17be4c05c0cc2f4bc6405f16ce521f620b0112/packages/engine/Source/Core/Transforms.js) | Local ENU and Earth fixed reference frame transformations | `spatial3d.frames` | P0 | PLANNED |
| `CESIUM-3D-008` | [SceneTransforms.js](https://github.com/tjx578/cesium_maps_rally/blob/7f17be4c05c0cc2f4bc6405f16ce521f620b0112/packages/engine/Source/Scene/SceneTransforms.js) | 3D world coordinate to screen and back projection context | `spatial3d.projection` | P1 | PLANNED |
| `CESIUM-3D-009` | [CorridorGeometry.js](https://github.com/tjx578/cesium_maps_rally/blob/7f17be4c05c0cc2f4bc6405f16ce521f620b0112/packages/engine/Source/Core/CorridorGeometry.js) | 3D georeferenced corridor geometry and width styling | `spatial3d.corridor.visualize` | P1 | PLANNED |
| `CESIUM-3D-010` | [PolylineGeometry.js](https://github.com/tjx578/cesium_maps_rally/blob/7f17be4c05c0cc2f4bc6405f16ce521f620b0112/packages/engine/Source/Core/PolylineGeometry.js) | Georeferenced polyline geometry representation | `spatial3d.route.overlay` | P0 | PLANNED |
| `CESIUM-3D-011` | [PolygonGeometry.js](https://github.com/tjx578/cesium_maps_rally/blob/7f17be4c05c0cc2f4bc6405f16ce521f620b0112/packages/engine/Source/Core/PolygonGeometry.js) | 3D polygon geometry overlays | `spatial3d.polygon` | P1 | PLANNED |
| `CESIUM-3D-012` | [RectangleGeometry.js](https://github.com/tjx578/cesium_maps_rally/blob/7f17be4c05c0cc2f4bc6405f16ce521f620b0112/packages/engine/Source/Core/RectangleGeometry.js) | Bounding rectangle spatial region geometry | `spatial3d.rectangle` | P2 | PLANNED |
| `CESIUM-3D-013` | [IntersectionTests.js](https://github.com/tjx578/cesium_maps_rally/blob/7f17be4c05c0cc2f4bc6405f16ce521f620b0112/packages/engine/Source/Core/IntersectionTests.js) | Geometric intersections and ray math primitives | `spatial3d.intersections` | P1 | PLANNED |
| `CESIUM-3D-014` | [GroundPolylinePrimitive.js](https://github.com/tjx578/cesium_maps_rally/blob/7f17be4c05c0cc2f4bc6405f16ce521f620b0112/packages/engine/Source/Scene/GroundPolylinePrimitive.js) | Terrain-draped 3D line rendering | `spatial3d.route.ground_overlay` | P0 | PLANNED |
| `CESIUM-3D-015` | [GroundPrimitive.js](https://github.com/tjx578/cesium_maps_rally/blob/7f17be4c05c0cc2f4bc6405f16ce521f620b0112/packages/engine/Source/Scene/GroundPrimitive.js) | Ground clamped geometric primitives | `spatial3d.geometry.ground` | P1 | PLANNED |
| `CESIUM-3D-016` | [CesiumTerrainProvider.js](https://github.com/tjx578/cesium_maps_rally/blob/7f17be4c05c0cc2f4bc6405f16ce521f620b0112/packages/engine/Source/Core/CesiumTerrainProvider.js) | Quantized-mesh terrain streaming | `spatial3d.terrain.provider` | P0 | PLANNED |
| `CESIUM-3D-017` | [ArcGISTiledElevationTerrainProvider.js](https://github.com/tjx578/cesium_maps_rally/blob/7f17be4c05c0cc2f4bc6405f16ce521f620b0112/packages/engine/Source/Core/ArcGISTiledElevationTerrainProvider.js) | ArcGIS terrain elevation integration | `spatial3d.terrain.arcgis` | P1 | PLANNED |
| `CESIUM-3D-018` | [sampleTerrainMostDetailed.js](https://github.com/tjx578/cesium_maps_rally/blob/7f17be4c05c0cc2f4bc6405f16ce521f620b0112/packages/engine/Source/Core/sampleTerrainMostDetailed.js) | Most-detailed elevation query respecting terrain tile availability | `spatial3d.terrain.sample` | P0 | PLANNED |
| `CESIUM-3D-019` | [Terrain.js](https://github.com/tjx578/cesium_maps_rally/blob/7f17be4c05c0cc2f4bc6405f16ce521f620b0112/packages/engine/Source/Scene/Terrain.js) | Asynchronous terrain-provider lifecycle | `spatial3d.terrain.lifecycle` | P0 | PLANNED |
| `CESIUM-3D-020` | [Globe.js](https://github.com/tjx578/cesium_maps_rally/blob/7f17be4c05c0cc2f4bc6405f16ce521f620b0112/packages/engine/Source/Scene/Globe.js) | 3D globe terrain/imagery surface management | `spatial3d.globe` | P0 | PLANNED |
| `CESIUM-3D-021` | [Globe.js](https://github.com/tjx578/cesium_maps_rally/blob/7f17be4c05c0cc2f4bc6405f16ce521f620b0112/packages/engine/Source/Scene/Globe.js) | Globe transparency and terrain/globe visibility | `spatial3d.globe.transparency` | P2 | PLANNED |
| `CESIUM-3D-022` | [Scene.js](https://github.com/tjx578/cesium_maps_rally/blob/7f17be4c05c0cc2f4bc6405f16ce521f620b0112/packages/engine/Source/Scene/Scene.js) | Scene view and geometry picking against rendered surface | `spatial3d.picking` | P0 | PLANNED |
| `CESIUM-3D-023` | [Scene.js](https://github.com/tjx578/cesium_maps_rally/blob/7f17be4c05c0cc2f4bc6405f16ce521f620b0112/packages/engine/Source/Scene/Scene.js) | Scene height sampling and camera-aware spatial inspection | `spatial3d.scene.height` | P1 | PLANNED |
| `CESIUM-3D-024` | [Scene.js](https://github.com/tjx578/cesium_maps_rally/blob/7f17be4c05c0cc2f4bc6405f16ce521f620b0112/packages/engine/Source/Scene/Scene.js) | Request-render scheduling and scene resource lifecycle | `spatial3d.scene.lifecycle` | P0 | PLANNED |
| `CESIUM-3D-025` | [ImageryLayer.js](https://github.com/tjx578/cesium_maps_rally/blob/7f17be4c05c0cc2f4bc6405f16ce521f620b0112/packages/engine/Source/Scene/ImageryLayer.js) | Raster imagery layer compositing opacity/order | `spatial3d.imagery.layer` | P0 | PLANNED |
| `CESIUM-3D-026` | [UrlTemplateImageryProvider.js](https://github.com/tjx578/cesium_maps_rally/blob/7f17be4c05c0cc2f4bc6405f16ce521f620b0112/packages/engine/Source/Scene/UrlTemplateImageryProvider.js) | XYZ/URL template imagery provider | `spatial3d.imagery.xyz` | P0 | PLANNED |
| `CESIUM-3D-027` | [WebMapServiceImageryProvider.js](https://github.com/tjx578/cesium_maps_rally/blob/7f17be4c05c0cc2f4bc6405f16ce521f620b0112/packages/engine/Source/Scene/WebMapServiceImageryProvider.js) | OGC WMS imagery and GetFeatureInfo handling | `spatial3d.imagery.wms` | P0 | PLANNED |
| `CESIUM-3D-028` | [WebMapTileServiceImageryProvider.js](https://github.com/tjx578/cesium_maps_rally/blob/7f17be4c05c0cc2f4bc6405f16ce521f620b0112/packages/engine/Source/Scene/WebMapTileServiceImageryProvider.js) | OGC WMTS tiled imagery integration | `spatial3d.imagery.wmts` | P1 | PLANNED |
| `CESIUM-3D-029` | [ArcGisMapServerImageryProvider.js](https://github.com/tjx578/cesium_maps_rally/blob/7f17be4c05c0cc2f4bc6405f16ce521f620b0112/packages/engine/Source/Scene/ArcGisMapServerImageryProvider.js) | ArcGIS MapServer imagery integration | `spatial3d.imagery.arcgis` | P1 | PLANNED |
| `CESIUM-3D-030` | [OpenStreetMapImageryProvider.js](https://github.com/tjx578/cesium_maps_rally/blob/7f17be4c05c0cc2f4bc6405f16ce521f620b0112/packages/engine/Source/Scene/OpenStreetMapImageryProvider.js) | OpenStreetMap imagery context provider | `spatial3d.imagery.osm` | P1 | PLANNED |
| `CESIUM-3D-031` | [TimeDynamicImagery.js](https://github.com/tjx578/cesium_maps_rally/blob/7f17be4c05c0cc2f4bc6405f16ce521f620b0112/packages/engine/Source/Scene/TimeDynamicImagery.js) | Time-varying imagery requests and playback | `spatial3d.imagery.temporal` | P1 | PLANNED |
| `CESIUM-3D-032` | [Cesium3DTileset.js](https://github.com/tjx578/cesium_maps_rally/blob/7f17be4c05c0cc2f4bc6405f16ce521f620b0112/packages/engine/Source/Scene/Cesium3DTileset.js) | 3D Tiles tileset loading and traversal | `spatial3d.tiles.load` | P0 | PLANNED |
| `CESIUM-3D-033` | [Cesium3DTileset.js](https://github.com/tjx578/cesium_maps_rally/blob/7f17be4c05c0cc2f4bc6405f16ce521f620b0112/packages/engine/Source/Scene/Cesium3DTileset.js) | 3D Tiles screen-space-error level-of-detail and streaming cache | `spatial3d.tiles.lod` | P0 | PLANNED |
| `CESIUM-3D-034` | [Cesium3DTileset.js](https://github.com/tjx578/cesium_maps_rally/blob/7f17be4c05c0cc2f4bc6405f16ce521f620b0112/packages/engine/Source/Scene/Cesium3DTileset.js) | 3D Tiles bounding volumes and culling | `spatial3d.tiles.culling` | P1 | PLANNED |
| `CESIUM-3D-035` | [Cesium3DTileStyle.js](https://github.com/tjx578/cesium_maps_rally/blob/7f17be4c05c0cc2f4bc6405f16ce521f620b0112/packages/engine/Source/Scene/Cesium3DTileStyle.js) | Feature-level 3D tile styling and filtering | `spatial3d.tiles.style` | P1 | PLANNED |
| `CESIUM-3D-036` | [ClippingPlaneCollection.js](https://github.com/tjx578/cesium_maps_rally/blob/7f17be4c05c0cc2f4bc6405f16ce521f620b0112/packages/engine/Source/Scene/ClippingPlaneCollection.js) | 3D geometry clipping with planes | `spatial3d.tiles.clipping_plane` | P1 | PLANNED |
| `CESIUM-3D-037` | [ClippingPolygonCollection.js](https://github.com/tjx578/cesium_maps_rally/blob/7f17be4c05c0cc2f4bc6405f16ce521f620b0112/packages/engine/Source/Scene/ClippingPolygonCollection.js) | 3D geometry clipping with polygons | `spatial3d.tiles.clipping_polygon` | P1 | PLANNED |
| `CESIUM-3D-038` | [I3SDataProvider.js](https://github.com/tjx578/cesium_maps_rally/blob/7f17be4c05c0cc2f4bc6405f16ce521f620b0112/packages/engine/Source/Scene/I3SDataProvider.js) | I3S indexed 3D scene layer ingestion | `spatial3d.tiles.i3s` | P2 | PLANNED |
| `CESIUM-3D-039` | [GaussianSplatPrimitive.js](https://github.com/tjx578/cesium_maps_rally/blob/7f17be4c05c0cc2f4bc6405f16ce521f620b0112/packages/engine/Source/Scene/GaussianSplatPrimitive.js) | 3D Gaussian splat scene rendering | `spatial3d.splats` | P2 | PLANNED |
| `CESIUM-3D-040` | [VoxelPrimitive.js](https://github.com/tjx578/cesium_maps_rally/blob/7f17be4c05c0cc2f4bc6405f16ce521f620b0112/packages/engine/Source/Scene/VoxelPrimitive.js) | Voxel data rendering and traversal | `spatial3d.voxels` | P2 | PLANNED |
| `CESIUM-3D-041` | [Model.js](https://github.com/tjx578/cesium_maps_rally/blob/7f17be4c05c0cc2f4bc6405f16ce521f620b0112/packages/engine/Source/Scene/Model/Model.js) | glTF and 3D model display | `spatial3d.models.gltf` | P1 | PLANNED |
| `CESIUM-3D-042` | [PointCloudShading.js](https://github.com/tjx578/cesium_maps_rally/blob/7f17be4c05c0cc2f4bc6405f16ce521f620b0112/packages/engine/Source/Scene/PointCloudShading.js) | Point-cloud shading/point sizes and visual classification | `spatial3d.pointcloud` | P1 | PLANNED |
| `CESIUM-3D-043` | [GpxDataSource.js](https://github.com/tjx578/cesium_maps_rally/blob/7f17be4c05c0cc2f4bc6405f16ce521f620b0112/packages/engine/Source/DataSources/GpxDataSource.js) | GPS GPX track waypoints/routes loading | `spatial3d.data.gpx` | P0 | PLANNED |
| `CESIUM-3D-044` | [KmlDataSource.js](https://github.com/tjx578/cesium_maps_rally/blob/7f17be4c05c0cc2f4bc6405f16ce521f620b0112/packages/engine/Source/DataSources/KmlDataSource.js) | KML and KMZ geospatial data ingestion | `spatial3d.data.kml` | P1 | PLANNED |
| `CESIUM-3D-045` | [GeoJsonDataSource.js](https://github.com/tjx578/cesium_maps_rally/blob/7f17be4c05c0cc2f4bc6405f16ce521f620b0112/packages/engine/Source/DataSources/GeoJsonDataSource.js) | GeoJSON feature loading into entities | `spatial3d.data.geojson` | P0 | PLANNED |
| `CESIUM-3D-046` | [CzmlDataSource.js](https://github.com/tjx578/cesium_maps_rally/blob/7f17be4c05c0cc2f4bc6405f16ce521f620b0112/packages/engine/Source/DataSources/CzmlDataSource.js) | CZML time-dynamic 3D scene description | `spatial3d.data.czml` | P1 | PLANNED |
| `CESIUM-3D-047` | [SampledPositionProperty.js](https://github.com/tjx578/cesium_maps_rally/blob/7f17be4c05c0cc2f4bc6405f16ce521f620b0112/packages/engine/Source/DataSources/SampledPositionProperty.js) | Timestamped position interpolation | `spatial3d.time.position` | P0 | PLANNED |
| `CESIUM-3D-048` | [PathGraphics.js](https://github.com/tjx578/cesium_maps_rally/blob/7f17be4c05c0cc2f4bc6405f16ce521f620b0112/packages/engine/Source/DataSources/PathGraphics.js) | Animated spatial path/track visualization | `spatial3d.time.path` | P0 | PLANNED |
| `CESIUM-3D-049` | [VelocityOrientationProperty.js](https://github.com/tjx578/cesium_maps_rally/blob/7f17be4c05c0cc2f4bc6405f16ce521f620b0112/packages/engine/Source/DataSources/VelocityOrientationProperty.js) | Orientation derived from motion data | `spatial3d.time.orientation` | P1 | PLANNED |
| `CESIUM-3D-050` | [JulianDate.js](https://github.com/tjx578/cesium_maps_rally/blob/7f17be4c05c0cc2f4bc6405f16ce521f620b0112/packages/engine/Source/Core/JulianDate.js) | Precision time representation for scene timelines | `spatial3d.time.julian` | P1 | PLANNED |
| `CESIUM-3D-051` | [Clock.js](https://github.com/tjx578/cesium_maps_rally/blob/7f17be4c05c0cc2f4bc6405f16ce521f620b0112/packages/engine/Source/Core/Clock.js) | Time-dependent playback clock and speed | `spatial3d.time.clock` | P0 | PLANNED |
| `CESIUM-3D-052` | [Entity.js](https://github.com/tjx578/cesium_maps_rally/blob/7f17be4c05c0cc2f4bc6405f16ce521f620b0112/packages/engine/Source/DataSources/Entity.js) | Dynamic entity/graphics binding | `spatial3d.entities` | P0 | PLANNED |
| `CESIUM-3D-053` | [Camera.js](https://github.com/tjx578/cesium_maps_rally/blob/7f17be4c05c0cc2f4bc6405f16ce521f620b0112/packages/engine/Source/Scene/Camera.js) | 3D camera position heading pitch roll and flights | `spatial3d.camera` | P0 | PLANNED |
| `CESIUM-3D-054` | [ScreenSpaceCameraController.js](https://github.com/tjx578/cesium_maps_rally/blob/7f17be4c05c0cc2f4bc6405f16ce521f620b0112/packages/engine/Source/Scene/ScreenSpaceCameraController.js) | 3D input interaction/pan/zoom/tilt constraints | `spatial3d.camera.controls` | P1 | PLANNED |
| `CESIUM-3D-055` | [SceneMode.js](https://github.com/tjx578/cesium_maps_rally/blob/7f17be4c05c0cc2f4bc6405f16ce521f620b0112/packages/engine/Source/Scene/SceneMode.js) | 2D/Columbus/3D scene modes | `spatial3d.scene.modes` | P1 | PLANNED |
| `CESIUM-3D-056` | [ShadowMap.js](https://github.com/tjx578/cesium_maps_rally/blob/7f17be4c05c0cc2f4bc6405f16ce521f620b0112/packages/engine/Source/Scene/ShadowMap.js) | Shadow casting for visual context, not survey proof | `spatial3d.lighting.shadow` | P2 | PLANNED |
| `CESIUM-3D-057` | [SkyAtmosphere.js](https://github.com/tjx578/cesium_maps_rally/blob/7f17be4c05c0cc2f4bc6405f16ce521f620b0112/packages/engine/Source/Scene/SkyAtmosphere.js) | Atmospheric environment visual context | `spatial3d.atmosphere` | P2 | PLANNED |
| `CESIUM-3D-058` | [PostProcessStageCollection.js](https://github.com/tjx578/cesium_maps_rally/blob/7f17be4c05c0cc2f4bc6405f16ce521f620b0112/packages/engine/Source/Scene/PostProcessStageCollection.js) | 3D scene post-processing effects | `spatial3d.effects` | P2 | PLANNED |
| `CESIUM-3D-059` | [Picking.js](https://github.com/tjx578/cesium_maps_rally/blob/7f17be4c05c0cc2f4bc6405f16ce521f620b0112/packages/engine/Source/Scene/Picking.js) | GPU picking and object interaction | `spatial3d.pick_features` | P0 | PLANNED |
| `CESIUM-3D-060` | [Snapping.js](https://github.com/tjx578/cesium_maps_rally/blob/7f17be4c05c0cc2f4bc6405f16ce521f620b0112/packages/engine/Source/Scene/Snapping.js) | Interactive geometry snapping building blocks | `spatial3d.snap.visual` | P1 | PLANNED |
| `CESIUM-3D-061` | [Viewer.js](https://github.com/tjx578/cesium_maps_rally/blob/7f17be4c05c0cc2f4bc6405f16ce521f620b0112/packages/widgets/Source/Viewer/Viewer.js) | Viewer composition/controls | `spatial3d.viewer` | P0 | PLANNED |
| `CESIUM-3D-062` | [Timeline.js](https://github.com/tjx578/cesium_maps_rally/blob/7f17be4c05c0cc2f4bc6405f16ce521f620b0112/packages/widgets/Source/Timeline/Timeline.js) | Visual timeline scrub and preview | `spatial3d.ui.timeline` | P1 | PLANNED |
| `CESIUM-3D-063` | [Animation.js](https://github.com/tjx578/cesium_maps_rally/blob/7f17be4c05c0cc2f4bc6405f16ce521f620b0112/packages/widgets/Source/Animation/Animation.js) | Animation controls | `spatial3d.ui.animation` | P1 | PLANNED |
| `CESIUM-3D-064` | [SceneModePicker.js](https://github.com/tjx578/cesium_maps_rally/blob/7f17be4c05c0cc2f4bc6405f16ce521f620b0112/packages/widgets/Source/SceneModePicker/SceneModePicker.js) | Scene-mode picker controls | `spatial3d.ui.modepicker` | P2 | PLANNED |
| `CESIUM-3D-065` | [BaseLayerPicker.js](https://github.com/tjx578/cesium_maps_rally/blob/7f17be4c05c0cc2f4bc6405f16ce521f620b0112/packages/widgets/Source/BaseLayerPicker/BaseLayerPicker.js) | Basemap and terrain layer selection | `spatial3d.ui.basemap` | P1 | PLANNED |
| `CESIUM-3D-066` | [README.md](https://github.com/tjx578/cesium_maps_rally/blob/7f17be4c05c0cc2f4bc6405f16ce521f620b0112/Documentation/OfflineGuide/README.md) | Offline 3D globe runtime with local imagery/3D assets and disabled geocoder | `spatial3d.offline.assets` | P0 | PLANNED |
| `CESIUM-3D-067` | [RequestScheduler.js](https://github.com/tjx578/cesium_maps_rally/blob/7f17be4c05c0cc2f4bc6405f16ce521f620b0112/packages/engine/Source/Core/RequestScheduler.js) | Network request scheduling and throttling | `spatial3d.network.scheduler` | P1 | PLANNED |
| `CESIUM-3D-068` | [Cesium3DTilesetCache.js](https://github.com/tjx578/cesium_maps_rally/blob/7f17be4c05c0cc2f4bc6405f16ce521f620b0112/packages/engine/Source/Scene/Cesium3DTilesetCache.js) | 3D tiles eviction and memory cache management | `spatial3d.performance.cache` | P1 | PLANNED |
| `CESIUM-3D-069` | [createVerticesFromQuantizedTerrainMesh.js](https://github.com/tjx578/cesium_maps_rally/blob/7f17be4c05c0cc2f4bc6405f16ce521f620b0112/packages/engine/Source/Workers/createVerticesFromQuantizedTerrainMesh.js) | Worker-based terrain mesh processing | `spatial3d.performance.worker` | P1 | PLANNED |

## Validation semantics

`SOURCE_INDEXED` is not the same as `IMPLEMENTED`, `BUILD_VERIFIED`, or `RACE_READY`. To promote a capability, attach a source fixture, unit/integration test receipt and browser or numerical validation. All marked PREP/REVIEW, no LIVE authority.

For cross-tool responsibility and planned bridges, see [SPATIAL-RECONCILIATION-KEPLER-CESIUM-v1.md](SPATIAL-RECONCILIATION-KEPLER-CESIUM-v1.md).
