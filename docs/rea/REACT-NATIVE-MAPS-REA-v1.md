# REA — `tjx578/react-native-maps_rallyos` → NaviPRO RallyOS

**Tanggal audit:** 2026-10-20  
**Tahap:** `SOURCE_AUDIT_AND_ADOPTION_DESIGN` — **belum diintegrasikan ke repo NaviPRO, belum build-tested**  
**Sumber:** [`tjx578/react-native-maps_rallyos`](https://github.com/tjx578/react-native-maps_rallyos)  
**SHA sumber yang diperiksa:** `863dc3c53aa17c0aac8c80415b91ed30d6a4f478` (`master`)  
**Hasil audit didasarkan pada pembacaan repo melalui koneksi GitHub**, bukan pada eksekusi aplikasi.

## 1. Executive decision

**Putusan:** **ADOPT SELECTIVELY, DO NOT REPLACE MAPLIBRE-NATIVE DRIVER.**

Fork ini membungkus native maps Android/iOS untuk React Native. Kemampuan kunci yang layak diambil adalah React declarative map composition, marker/callout, polylines/polygons/circles, tile overlays, camera control, map events, GeoJSON rendering, user-location visualization, dan Expo/Fabric integration. **Repo bukan routing engine, roadbook compiler, offline road graph, atau Time Rally authority system.** Untuk Android, renderer bergantung pada Google Maps SDK; `LocalTile` hanya tile overlay. Karena Driver NaviPRO dirancang offline-first, deterministic dan read-only confirmed NaviPack, **MapLibre Native/PMTiles tetap pilihan arsitektur utama**. React Native Maps cocok sebagai **opsional Navigator mobile UI/preview adapter** atau prototipe visual, setelah kompatibilitas dan lisensi diuji.

## 2. Identitas dan provenance

| Properti | Terverifikasi |
|---|---|
| Repository | `tjx578/react-native-maps_rallyos` |
| Upstream | `react-native-maps/react-native-maps` |
| Jenis | GitHub fork |
| Branch | `master` |
| HEAD | `863dc3c53aa17c0aac8c80415b91ed30d6a4f478` |
| Release deklaratif | `react-native-maps@1.29.0` (`package.json`) |
| Lisensi source | MIT (`LICENSE`, `package.json`) |
| Upstream `master` saat audit | `39c6fd177d6c91ea087fcf083fd484f2499b6ea8` |
| Dibanding upstream | 25 commit lanjutan di upstream; tidak ditemukan commit khusus RallyOS dalam HEAD fork yang merupakan release upstream 1.29.0 |
| Platform | Android Google Maps SDK; iOS Apple MapKit atau Google Maps |
| Mobile ecosystem | React Native, Fabric/New Architecture, React Native Codegen, Expo config plugin |
| Persyaratan paket | React Native peer `>=0.76.0`; README menyatakan Fabric untuk `1.26.1+` butuh RN `>=0.81.1`. Keputusan akhir harus berdasar matrix kompatibilitas pada versi yang akan dibangun. |
| Web | `src/MapView.web.ts` mengekspor `UnimplementedView`; bukan implementasi map web |

**Tidak ada klaim ada implementasi RallyOS tersendiri.** Nama repository berakhiran `rallyos` tidak menambah fitur Time Rally pada source yang diperiksa.

## 3. Architecture reverse engineering

```text
React Native application
  │
  ├── src/MapView.tsx + MapView.types.ts (props/events/camera)
  ├── src/MapMarker.tsx / MapCallout.tsx
  ├── src/MapPolyline.tsx / MapPolygon.tsx / MapCircle.tsx
  ├── src/Geojson.tsx / MapOverlay.tsx / MapHeatmap.tsx
  ├── src/MapLocalTile.tsx / MapUrlTile.tsx / MapWMSTile.tsx
  ├── src/specs/* (React Native Codegen / Fabric bindings)
  ├── plugin/src/* (Expo config)
  │
  └── Native bridge / Fabric
      ├── android/src/main/java/com/rnmaps/maps/*
      │      ├── MapView extends Google Maps MapView
      │      ├── GoogleMap overlays/markers/tiles
      │      └── MapTileProvider (cache + offlineMode for UrlTile)
      └── ios/
             ├── AirMaps/* (MapKit)
             ├── AirGoogleMaps/* (Google Maps)
             └── generated/*
```

**Temuan arsitektural:** declarative visual overlays, bukan backend navigasi; tidak ada route optimization, TSD logic, road graph preprocessing, verified landmark evidence, atau NaviPack acceptance gates di fitur yang diperiksa.

## 4. Capability coverage — verified in source/docs, not runtime-validated

| ID | Capability | Status sumber | Penggunaan NaviPRO | Batasan |
|---|---|---|---|---|
| RNM-01 | Native `MapView` | source verified | Navigator map pane | Android Google SDK |
| RNM-02 | Native marker | source verified | POI, checkpoint, candidate anchor | hanya visual |
| RNM-03 | Marker image, anchor, callout | source verified | simbol/keterangan roadbook | jangan jadikan authority |
| RNM-04 | Drag marker | source verified | usulan posisi lokasi PREP | tidak ubah authoritative anchor langsung |
| RNM-05 | Polyline | source verified | render confirmed route/read-only overlay | geometry harus dari canonical contract |
| RNM-06 | `strokeColors` / gradient | source verified | visualisasi deviasi/segmen | dukungan provider bervariasi |
| RNM-07 | Polygon | source verified | corridor/survey region | data perlu datum/provenance |
| RNM-08 | Circle | source verified | visual proximity/uncertainty | bukan error bound pasti |
| RNM-09 | GeoJSON helper | source verified | import preview artifacts | tidak sama dengan data parser authoritative |
| RNM-10 | Ground/image overlay | source verified | referensi peta/survey | licensing/georeference |
| RNM-11 | Heatmap | source verified (Google only) | analytics uncertainty | bukan Driver realtime |
| RNM-12 | UrlTile XYZ/TMS | source verified | PREP map tiles | network/provider terms |
| RNM-13 | WMSTile | source verified | GIS overlays | external provider |
| RNM-14 | LocalTile raster XYZ | source verified | offline **visual tile overlay** | bukan full offline engine |
| RNM-15 | `offlineMode` UrlTile cache | source verified | fallback raster | tidak menonaktifkan semua network |
| RNM-16 | Camera/heading/pitch/zoom | source verified | preview/UI | jangan bergantung pada JS frame timing |
| RNM-17 | Region/animated region | source verified | viewport/sync | controlled region event load |
| RNM-18 | `fitToCoordinates` | source verified | overview candidate/route | visual-only |
| RNM-19 | `pointForCoordinate` & reverse | source verified | placement/UI affordances | projection not authoritative location |
| RNM-20 | `onPress`, `onLongPress` | source verified | candidate suggestion | no direct decision |
| RNM-21 | Region gesture events | source verified | interaction analytics | throttle JS bridge updates |
| RNM-22 | `onUserLocationChange` | source verified | display sensor fix | not trusted high-rate GNSS recorder |
| RNM-23 | `takeSnapshot` | source verified | report/map evidence screenshot | screenshot alone insufficient evidence |
| RNM-24 | Map type (street, satellite, terrain, none) | source verified | base context | provider/billing constraints |
| RNM-25 | KML entry (`kmlSrc`) | source verified, platform-limited | visual GPX/KML workflow adapter | not canonical parser |
| RNM-26 | Fabric/Codegen | source verified | modern RN component integration | RN version compatibility |
| RNM-27 | Expo config plugin | source verified | builds/prototyping | not needed for native Kotlin Driver |
| RNM-28 | iOS MapKit option | source verified | optional iOS Navigator | inconsistent feature parity |
| RNM-29 | Android lite mode | source verified | static/low-resource map view | limited gestures/interaction |
| RNM-30 | Google SDK renderer | source verified | optional mobile Google context | licensing/keys/cost |
| RNM-31 | Custom marker view | source verified | icon/cue bubble prototypes | marker update cost |
| RNM-32 | No full web MapView | source verified (`UnimplementedView`) | web workbench uses other engine | web support absent |

These 32 categories are **audit groupings**, not “32 NaviPRO features implemented”.

## 5. Platform/API nuance: must not silently assume parity

1. `MapView` Android extends `com.google.android.gms.maps.MapView`, and native `MapLocalTile` adds `TileOverlay` to `GoogleMap` rather than replacing its map engine.
2. README states Android `LocalTile` is an overlay; while online, the underlying map may still request base tiles. Setting `mapType="none"` can suppress the native basemap on Android, **but full offline readiness still needs actual device validation**.
3. `LocalTile` accesses uncompressed file/Android assets raster XYZ. No PMTiles/MBTiles/native vector tile engine is provided by the examined core API. Do not describe `LocalTile` as a PMTiles reader.
4. `UrlTile` supports `tileCachePath` and `offlineMode` (cache-only overlay). Android `MapTileProvider` has WorkManager/futures and explicit wait/sleep in its online cache-miss implementation; a profiling and ANR/jank review is necessary before intensive use.
5. `MapHeatmap` is Google-only on iOS; provider support for 3D, KML, polyline gradients and marker interactions differs.
6. `src/MapView.web.ts` is `UnimplementedView`, so this is not a replacement for Kepler/Cesium/OSRM's web visualizations.
7. The fork's `src/MapView.types.ts` exposes user-location accuracy/time/speed/heading, but that's an event format, not a complete integrity-protected odometer/timing telemetry pipeline.
8. README and package version constraints need crosschecking in the actual target lockfile: `1.29.0`, RN `>=0.81.1` for Fabric, Android Play Services and iOS Pod versions.

## 6. Architectural mapping against NaviPRO RallyOS planes

| NaviPRO plane | React Native Maps contribution | Decision |
|---|---|---|
| Navigator Page 1 (roadbook & time) | small visual location preview, checkpoint overlays | **OPTIONAL**: never derive rally time from map camera callback |
| Navigator Page 2 (route editing/review) | marker selection, geometry overlays, camera and candidate visualization | **CONDITIONAL ADOPT** via mobile visual adapter; official route locked |
| Navigator Page 3 (Rally Agent/MCP) | render proposals and evidence highlights | **OPTIONAL DISPLAY ONLY**; no automatic verification |
| Field Survey | capture candidate at pressed map location; display questions | **USEFUL** alongside StreetComplete-inspired survey core |
| Kepler Map Lab (web) | None: no web map implementation | **DO NOT REPLACE** |
| Cesium Terrain Lab (web) | no Cesium 3D Tiles/terrain analysis engine | **DO NOT REPLACE** |
| Routing Lab (web, OSRM+LRM) | None: unrelated mobile renderer | **DO NOT REPLACE** |
| Android Driver LIVE | could render route as map overlay but violates preferred independent offline renderer path unless carefully proved | **DO NOT REPLACE MAPLIBRE NATIVE** |
| Authoritative route/timing/evidence | none | **FORBID DIRECT MUTATION** |

### Suggested component boundary

```text
NaviPRO canonical route (server hash + immutable revision)
     │
     ├── Navipack / MapLibre native Android Driver (OFFLINE, read-only)
     │
     └── PREP/REVIEW mobile presentation adapter
             │
             └── [optional] React Native Maps 1.29.x
                     ├── route polyline presentation
                     ├── source/candidate markers
                     ├── map gesture -> PROPOSAL only
                     └── raster tile overlay if licensing allows
```

No `RouteRevision` write, `LocationDecision` create, `NaviPack` publish or LIVE reroute may originate from this renderer by itself. Map coordinates crossing RN JavaScript are presentation values, while canonical coordinates remain `lat_e7`/`lon_e7` and distance `_mm` with an explicit conversion boundary.

## 7. Target adapter contracts (proposal, not yet implemented)

**Rendering input:** `MobileMapSceneV1` `{map_project_id, route_id, route_revision_id, route_digest, view_mode: PREP|REVIEW, layers:[...], tile_manifest_ref?, map_camera, source_provenance}`.

**Immutable route layer:** `ConfirmedRouteOverlayV1` `{geometry_e7, edges_hash, style, selection_enabled: false}`. If rendering large dense route, transform to batched native polyline and visually simplify **without changing original canonical geometry**.

**User interaction output:** `MapInteractionProposalV1` `{proposal_id, source_revision_id, type: SELECT|INSPECT|PROPOSE_ANCHOR|PROPOSE_SHAPING_POINT, point_e7?, context, actor, created_at}`. Server checks route revision and permission; no `CONFIRM` type.

**Observability:** map renderer type/provider/platform/version, package capability flags, actual offline basemap behavior, GPU/RAM/thermal metrics, UI frame pacing, event rates, map-ready failure modes.

**Do not add arbitrary MCP tools for rendering state.** Agent safe interface is an existing proposed-layer/inspection contract, not permissions to modify route.

## 8. High-priority risk register

| Risk | Consequence | Mitigation/acceptance |
|---|---|---|
| R1 — Android Google SDK dependency | Internet, service, and provider constraints | Offline airplane-mode test, fallback policy, provider licensing review |
| R2 — `LocalTile` is raster overlay | No PMTiles/graph handling | Keep MapLibre Native/PMTiles engine; optional raster adapter only |
| R3 — mutating draggable markers | Roadbook sequence drift | Read-only official markers; proposal event with server validation |
| R4 — JS camera and location callbacks | Frame jitter / missed events | Separate GNSS+timing native pipeline; events are presentation hints |
| R5 — native tile online cache misses | jank, blocking calls, memory pressure | benchmark cold/warm/offline, inspect thread usage; never ship unmeasured |
| R6 — visual simplification | path looks different from authoritative graph | render revision-hash-matched geometry; never use visual geometry for compliance |
| R7 — provider support differences | Android/iOS feature divergence | capability matrix per platform and automated/device tests |
| R8 — Google tile usage & attribution | compliance/cost | separate keys, platform restrictions, licenses, audit billing |
| R9 — RN version/Fabric support | failed builds | explicit pinned version matrix, Android/iOS build gates |
| R10 — large custom marker counts | jank | image-based marker, tracking toggles, LOD, native profiling |
| R11 — GPS accuracy misuse | false verification | uncertainty, provenance, NMEA/odometer separately |
| R12 — absent web MapView | incomplete web parity | keep Kepler/Cesium/MapLibre stack on web |

## 9. Recommended P0/P1/P2 adoption roadmap

**P0 — architecture decision and feasibility gate**
- Pin source version and license, inspect Google SDK and React Native compatibility.
- Build isolated RN Android sandbox with basemap/tiles/route/marker only; do NOT modify Driver.
- Confirm disconnected cold boot + flight/airplane-mode map renderer characteristics in a safe stationary test environment, including no unexpected network requirement.
- Compare same `RouteRevision` dense polyline across MapLibre and React Native Maps and verify pixel-level rendering/coordinate boundary.
- Record framerate, memory, app cold start, offline tile cache, heat, and battery measurements on relevant devices.

**P1 — optional Navigator mobile adapter**
- Convert canonical `lat_e7`, `lon_e7` to map props only at UI boundary; keep authoritative structures immutable.
- Overlay verified/candidate markers with distinct style plus evidence ID, uncertainty and provenance.
- Wire gestures to proposal-only API with server permission checks, version checking and conflict handling.
- Smoke tests for zoom/pan, many markers, selected route and offline restart.

**P2 — if accepted**
- Offline raster tiles only if they have independent checksums, manifest metadata, licensing rights, and measured performance.
- Side-by-side RN map/MapLibre compatibility report; no forced engine migration.
- iOS Navigator parity only when there is a concrete iOS product requirement.

## 10. Acceptance criteria before declaring production capability

1. Both online/offline map viewer start and render correctly under selected target provider; precise offline requirements tested with connectivity fully disabled.
2. Canonical route hash/source ordering never changes due to pinch/drag/marker events.
3. Map interactions result solely in proposals until navigator-authorized backend gate acts.
4. Visual map remains operational for target area and no unlicensed tile requests occur.
5. Profiling artifacts exist for FPS, main/UI thread stalls, tile I/O, memory, battery, and thermal behavior.
6. Build pipeline pins RN/Fabric/provider SDKs, includes Android integration tests and license inventory.
7. GNSS, timing, TSD and route progress use NaviPRO native independent clock/sensor pipeline; map view is display-only.
8. No deployment or race-ready claim without device results.

## 11. Recommended final architecture decision

**Decision record:** `REA_RNM_20261020_ADOPT_CONDITIONALLY_AS_PRESENTATION_ADAPTER`.

React Native Maps' verified benefit to NaviPRO is **cross-platform native visualization and map interactions**. It does not close the critical gaps in canonical roadbook compilation, deterministic TSD, graph routing, KM PAL reasoning, PMTiles/vector offline rendering, or driver offline reliability. Preserve `MapLibre Native + PMTiles` as preferred Driver rendering path and `OSRM + canonical validation` as routing domain; use React Native Maps only if a React Native Navigator client is actually being built, or a benchmark proves it preferable for a specifically scoped visualization component.

**Status at report creation:** source reviewed and mappings completed. No files changed in the NaviPRO Git repository; no RN Android/iOS builds, benchmark, real GNSS tests or offline tests executed. This report is a completed analysis artifact, **not a runtime integration**.

## 12. Source anchors (SHA-pinned)

- [Fork README](https://github.com/tjx578/react-native-maps_rallyos/blob/863dc3c53aa17c0aac8c80415b91ed30d6a4f478/README.md)
- [package.json](https://github.com/tjx578/react-native-maps_rallyos/blob/863dc3c53aa17c0aac8c80415b91ed30d6a4f478/package.json)
- [MapView TypeScript implementation](https://github.com/tjx578/react-native-maps_rallyos/blob/863dc3c53aa17c0aac8c80415b91ed30d6a4f478/src/MapView.tsx)
- [MapView typed events/camera](https://github.com/tjx578/react-native-maps_rallyos/blob/863dc3c53aa17c0aac8c80415b91ed30d6a4f478/src/MapView.types.ts)
- [MapLocalTile TypeScript](https://github.com/tjx578/react-native-maps_rallyos/blob/863dc3c53aa17c0aac8c80415b91ed30d6a4f478/src/MapLocalTile.tsx)
- [Android local tile native](https://github.com/tjx578/react-native-maps_rallyos/blob/863dc3c53aa17c0aac8c80415b91ed30d6a4f478/android/src/main/java/com/rnmaps/maps/MapLocalTile.java)
- [Android tile cache implementation](https://github.com/tjx578/react-native-maps_rallyos/blob/863dc3c53aa17c0aac8c80415b91ed30d6a4f478/android/src/main/java/com/rnmaps/maps/MapTileProvider.java)
- [Android MapView native](https://github.com/tjx578/react-native-maps_rallyos/blob/863dc3c53aa17c0aac8c80415b91ed30d6a4f478/android/src/main/java/com/rnmaps/maps/MapView.java)
- [Cross-platform installation](https://github.com/tjx578/react-native-maps_rallyos/blob/863dc3c53aa17c0aac8c80415b91ed30d6a4f478/docs/installation.md)
- [Tile component docs](https://github.com/tjx578/react-native-maps_rallyos/blob/863dc3c53aa17c0aac8c80415b91ed30d6a4f478/docs/tiles.md)
- [Marker docs/performance note](https://github.com/tjx578/react-native-maps_rallyos/blob/863dc3c53aa17c0aac8c80415b91ed30d6a4f478/docs/marker.md)
- [Map web placeholder](https://github.com/tjx578/react-native-maps_rallyos/blob/863dc3c53aa17c0aac8c80415b91ed30d6a4f478/src/MapView.web.ts)
- [Polyline capabilities](https://github.com/tjx578/react-native-maps_rallyos/blob/863dc3c53aa17c0aac8c80415b91ed30d6a4f478/src/MapPolyline.tsx)
- [Expo config plugin](https://github.com/tjx578/react-native-maps_rallyos/blob/863dc3c53aa17c0aac8c80415b91ed30d6a4f478/plugin/src/index.ts)
