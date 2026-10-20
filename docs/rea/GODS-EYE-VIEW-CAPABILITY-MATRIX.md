# God's Eye View capability coverage — NaviPRO RallyOS

Source: [`tjx578/gods-eye-view-maps`](https://github.com/tjx578/gods-eye-view-maps) · pinned at `de2138e84c1778fd98a48b7c9fd0b9788c318946`. **Mapping is not runtime parity.**

| # | Capability | Source | Priority | Status |
|---:|---|---|---|---|
| 1 | `gev.sources.catalog` — Modular provider and source catalog | [`src/app/constructCatalog.js`](https://github.com/tjx578/gods-eye-view-maps/blob/de2138e84c1778fd98a48b7c9fd0b9788c318946/src/app/constructCatalog.js) | P0 | MAPPED |
| 2 | `gev.sources.boundaries` — Browser/provider/service module boundaries | [`docs/CODE-BOUNDARIES.md`](https://github.com/tjx578/gods-eye-view-maps/blob/de2138e84c1778fd98a48b7c9fd0b9788c318946/docs/CODE-BOUNDARIES.md) | P0 | MAPPED |
| 3 | `gev.sources.feed_state` — Honest feed health states including stale and fallback | [`src/data/feedState.js`](https://github.com/tjx578/gods-eye-view-maps/blob/de2138e84c1778fd98a48b7c9fd0b9788c318946/src/data/feedState.js) | P0 | MAPPED |
| 4 | `gev.sources.pack_provenance` — Data source licensing and attribution inventory | [`DATA_SOURCES.md`](https://github.com/tjx578/gods-eye-view-maps/blob/de2138e84c1778fd98a48b7c9fd0b9788c318946/DATA_SOURCES.md) | P0 | MAPPED |
| 5 | `gev.maps.stacks` — Map stack and imagery selection | [`src/maps/catalog.js`](https://github.com/tjx578/gods-eye-view-maps/blob/de2138e84c1778fd98a48b7c9fd0b9788c318946/src/maps/catalog.js) | P0 | MAPPED |
| 6 | `gev.maps.comparison` — Imagery before/after comparison | [`src/maps/imageryComparison.js`](https://github.com/tjx578/gods-eye-view-maps/blob/de2138e84c1778fd98a48b7c9fd0b9788c318946/src/maps/imageryComparison.js) | P0 | MAPPED |
| 7 | `gev.maps.split` — Interactive split comparison viewport | [`src/ui/imagerySplit.js`](https://github.com/tjx578/gods-eye-view-maps/blob/de2138e84c1778fd98a48b7c9fd0b9788c318946/src/ui/imagerySplit.js) | P0 | MAPPED |
| 8 | `gev.maps.terrain` — Terrain providers and retry policy | [`src/maps/terrain.js`](https://github.com/tjx578/gods-eye-view-maps/blob/de2138e84c1778fd98a48b7c9fd0b9788c318946/src/maps/terrain.js) | P0 | MAPPED |
| 9 | `gev.maps.3d` — 3D Tiles hosted world | [`src/maps/google3d.js`](https://github.com/tjx578/gods-eye-view-maps/blob/de2138e84c1778fd98a48b7c9fd0b9788c318946/src/maps/google3d.js) | P1 | MAPPED |
| 10 | `gev.maps.camera` — Camera controller and transitions | [`src/camera.js`](https://github.com/tjx578/gods-eye-view-maps/blob/de2138e84c1778fd98a48b7c9fd0b9788c318946/src/camera.js) | P1 | MAPPED |
| 11 | `gev.maps.ground_guard` — Terrain camera-floor safety guard | [`src/cameraGroundGuard.js`](https://github.com/tjx578/gods-eye-view-maps/blob/de2138e84c1778fd98a48b7c9fd0b9788c318946/src/cameraGroundGuard.js) | P1 | MAPPED |
| 12 | `gev.maps.source_lifecycle` — Map-source subscription and disposal | [`src/maps/controller.js`](https://github.com/tjx578/gods-eye-view-maps/blob/de2138e84c1778fd98a48b7c9fd0b9788c318946/src/maps/controller.js) | P0 | MAPPED |
| 13 | `gev.import.geo_files` — Local geospatial file import and abort handling | [`src/ui/geoFileImport.js`](https://github.com/tjx578/gods-eye-view-maps/blob/de2138e84c1778fd98a48b7c9fd0b9788c318946/src/ui/geoFileImport.js) | P0 | MAPPED |
| 14 | `gev.annotations.draw` — Interactive geospatial annotation drawing | [`src/annotations/drawTool.js`](https://github.com/tjx578/gods-eye-view-maps/blob/de2138e84c1778fd98a48b7c9fd0b9788c318946/src/annotations/drawTool.js) | P0 | MAPPED |
| 15 | `gev.annotations.engine` — Annotation engine and mutation boundary | [`src/annotations/annotationEngine.js`](https://github.com/tjx578/gods-eye-view-maps/blob/de2138e84c1778fd98a48b7c9fd0b9788c318946/src/annotations/annotationEngine.js) | P0 | MAPPED |
| 16 | `gev.director.scene_document` — Versioned scene document validation and migration | [`src/director/document.js`](https://github.com/tjx578/gods-eye-view-maps/blob/de2138e84c1778fd98a48b7c9fd0b9788c318946/src/director/document.js) | P0 | MAPPED |
| 17 | `gev.director.scene_camera` — Scene camera geometry and altitude semantics | [`docs/SCENE-DOCUMENT.md`](https://github.com/tjx578/gods-eye-view-maps/blob/de2138e84c1778fd98a48b7c9fd0b9788c318946/docs/SCENE-DOCUMENT.md) | P0 | MAPPED |
| 18 | `gev.director.playback` — Cancellable scene playback queue | [`src/director/playback.js`](https://github.com/tjx578/gods-eye-view-maps/blob/de2138e84c1778fd98a48b7c9fd0b9788c318946/src/director/playback.js) | P1 | MAPPED |
| 19 | `gev.director.data_packs` — Scene data packs and source separation | [`docs/DIRECTOR-DATA-PACKS.md`](https://github.com/tjx578/gods-eye-view-maps/blob/de2138e84c1778fd98a48b7c9fd0b9788c318946/docs/DIRECTOR-DATA-PACKS.md) | P1 | MAPPED |
| 20 | `gev.weather.clock` — Observation/forecast timeline and gap constraints | [`src/layers/weather/clock.js`](https://github.com/tjx578/gods-eye-view-maps/blob/de2138e84c1778fd98a48b7c9fd0b9788c318946/src/layers/weather/clock.js) | P0 | MAPPED |
| 21 | `gev.weather.raster` — Raster weather overlays and imagery playback | [`src/layers/weather/rasterTiles.js`](https://github.com/tjx578/gods-eye-view-maps/blob/de2138e84c1778fd98a48b7c9fd0b9788c318946/src/layers/weather/rasterTiles.js) | P1 | MAPPED |
| 22 | `gev.environment.air_quality` — Environmental air quality layer | [`src/layers/airQuality/index.js`](https://github.com/tjx578/gods-eye-view-maps/blob/de2138e84c1778fd98a48b7c9fd0b9788c318946/src/layers/airQuality/index.js) | P1 | MAPPED |
| 23 | `gev.environment.earthquakes` — Earthquake layer for contextual analysis | [`src/layers/earthquakes/index.js`](https://github.com/tjx578/gods-eye-view-maps/blob/de2138e84c1778fd98a48b7c9fd0b9788c318946/src/layers/earthquakes/index.js) | P1 | MAPPED |
| 24 | `gev.traffic.aggregate` — Aggregate road traffic visualization | [`src/layers/traffic/index.js`](https://github.com/tjx578/gods-eye-view-maps/blob/de2138e84c1778fd98a48b7c9fd0b9788c318946/src/layers/traffic/index.js) | P1 | MAPPED |
| 25 | `gev.terrain.height` — Height data cache and terrain proxy | [`src/services/terrainHeights.js`](https://github.com/tjx578/gods-eye-view-maps/blob/de2138e84c1778fd98a48b7c9fd0b9788c318946/src/services/terrainHeights.js) | P1 | MAPPED |
| 26 | `gev.search.coordinates` — Coordinate parsing and geographic input | [`src/search/coordinateParser.js`](https://github.com/tjx578/gods-eye-view-maps/blob/de2138e84c1778fd98a48b7c9fd0b9788c318946/src/search/coordinateParser.js) | P0 | MAPPED |
| 27 | `gev.search.places` — Keyless geocoder fallback support | [`src/search/keylessGeocoder.js`](https://github.com/tjx578/gods-eye-view-maps/blob/de2138e84c1778fd98a48b7c9fd0b9788c318946/src/search/keylessGeocoder.js) | P1 | MAPPED |
| 28 | `gev.hud.readability` — On-screen HUD layout and information structure | [`src/hudLayoutPolicy.js`](https://github.com/tjx578/gods-eye-view-maps/blob/de2138e84c1778fd98a48b7c9fd0b9788c318946/src/hudLayoutPolicy.js) | P2 | MAPPED |
| 29 | `gev.performance.measure` — Hardware-specific performance baseline methodology | [`docs/PERFORMANCE.md`](https://github.com/tjx578/gods-eye-view-maps/blob/de2138e84c1778fd98a48b7c9fd0b9788c318946/docs/PERFORMANCE.md) | P0 | MAPPED |
| 30 | `gev.security.source_terms` — Third-party data and asset rights separation | [`LICENSE`](https://github.com/tjx578/gods-eye-view-maps/blob/de2138e84c1778fd98a48b7c9fd0b9788c318946/LICENSE) | P0 | MAPPED |
| 31 | `gev.agent.world_packet` — Bounded map context packet representation | [`src/agent/worldPacket.js`](https://github.com/tjx578/gods-eye-view-maps/blob/de2138e84c1778fd98a48b7c9fd0b9788c318946/src/agent/worldPacket.js) | P1 | MAPPED |
| 32 | `gev.mcp.local_boundary` — Local MCP request and transport boundary | [`server/mcp/plugin.js`](https://github.com/tjx578/gods-eye-view-maps/blob/de2138e84c1778fd98a48b7c9fd0b9788c318946/server/mcp/plugin.js) | P1 | MAPPED |

## Exclusions

These source capabilities are not added to NaviPRO: individual tracking, CCTV/ALPR ingestion, military/sensitive installation monitoring, LIVE Driver feed fetching, route auto-confirmation, bundled unreviewed third-party data.

## Coverage versus implementation

Pure context preflight exists in `python/src/navipro_rallyos/context/fusion.py`; no native globe, data provider, HTTP/MCP runtime or visual parity verified.
