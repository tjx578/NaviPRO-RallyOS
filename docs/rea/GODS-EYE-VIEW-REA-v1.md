# REA God's Eye View — Spatial Context Fusion for NaviPRO RallyOS

**Status:** SOURCE_INSPECTED + CLEAN-ROOM CONTRACT/PROTOTYPE; **NOT_RUNTIME_PARITY**; **NOT_RACE_READY**  
**Source:** [`tjx578/gods-eye-view-maps`](https://github.com/tjx578/gods-eye-view-maps)  
**Audited ref:** `de2138e84c1778fd98a48b7c9fd0b9788c318946` (main; identical to upstream `bilawalsidhu/gods-eye-view` as inspected 2026-10-20).  
**Package:** `gods-eye-view` `0.2.1` (MIT source license).  
**Dataset/assets:** NOT generally MIT; the repo's `LICENSE`, `DATA_SOURCES.md`, `THIRD_PARTY_NOTICES.md`, and `public/models/README.md` impose independent conditions. Do not copy datasets or 3D assets by default.

## Executive determination

**ADOPT ARCHITECTURE/PATTERNS; DON'T FORK THE APPLICATION AS NAVIPRO CORE.** God's Eye View is a comprehensive *browser-based Cesium geospatial context/visualization application*, not a rally/TSD route authority engine. NaviPRO already has Kepler (data analytics), Cesium (3D), OSRM (road graph), StreetComplete (field survey), and Leaflet Routing Machine (route review UI). Adding the entire God's Eye View would duplicate Cesium rendering and introduce unnecessary API, license, privacy, and resource costs. Add **Spatial Context Fusion** as a bounded PREP/REVIEW adapter to existing Cesium Terrain Lab, rather than a seventh renderer.

## Evidence from inspected sources (pinned links)

| Evidence | Observed fact | Consequence |
|---|---|---|
| [package.json](https://github.com/tjx578/gods-eye-view-maps/blob/de2138e84c1778fd98a48b7c9fd0b9788c318946/package.json) | Vite + CesiumJS, local Node provider infrastructure, test entrypoint, optional external integrations | Do not assume the entire app is offline or field-deployable |
| [src/app/constructCatalog.js](https://github.com/tjx578/gods-eye-view-maps/blob/de2138e84c1778fd98a48b7c9fd0b9788c318946/src/app/constructCatalog.js) | Catalog constructs multiple independent layers and modules | Reuse catalog/source adapter pattern |
| [docs/CODE-BOUNDARIES.md](https://github.com/tjx578/gods-eye-view-maps/blob/de2138e84c1778fd98a48b7c9fd0b9788c318946/docs/CODE-BOUNDARIES.md) | Browser, portable sources, Node providers, UI and app composition separated | Keep provider acquisition away from Rally Authority Core |
| [src/data/feedState.js](https://github.com/tjx578/gods-eye-view-maps/blob/de2138e84c1778fd98a48b7c9fd0b9788c318946/src/data/feedState.js) | Distinguishes nominal/loading/degraded/stale/partial/fallback/unavailable | Add provenance and honest freshness UI badges/text, not implicit truth |
| [src/maps/imageryComparison.js](https://github.com/tjx578/gods-eye-view-maps/blob/de2138e84c1778fd98a48b7c9fd0b9788c318946/src/maps/imageryComparison.js) & [src/ui/imagerySplit.js](https://github.com/tjx578/gods-eye-view-maps/blob/de2138e84c1778fd98a48b7c9fd0b9788c318946/src/ui/imagerySplit.js) | Map-source comparison and split UI | Compare source/revision imagery in Page 2/3 without promoting an inferred alignment |
| [src/ui/geoFileImport.js](https://github.com/tjx578/gods-eye-view-maps/blob/de2138e84c1778fd98a48b7c9fd0b9788c318946/src/ui/geoFileImport.js) | Geo file import handles lifetime/abort/focus | Adopt bounded file import staging, provenance, and cleanup |
| [src/annotations/drawTool.js](https://github.com/tjx578/gods-eye-view-maps/blob/de2138e84c1778fd98a48b7c9fd0b9788c318946/src/annotations/drawTool.js) | Shared annotation workflow between interactive and agent paths | Treat any drawn geometry as review-only evidence proposal |
| [src/director/document.js](https://github.com/tjx578/gods-eye-view-maps/blob/de2138e84c1778fd98a48b7c9fd0b9788c318946/src/director/document.js) | Versioned scene document with validator, current constant **6** | An explicit NaviPRO versioning/migration adapter is necessary |
| [docs/SCENE-DOCUMENT.md](https://github.com/tjx578/gods-eye-view-maps/blob/de2138e84c1778fd98a48b7c9fd0b9788c318946/docs/SCENE-DOCUMENT.md) | Documentation describes scene format **5**, contradicting code constant 6 | **Source discrepancy**: do not copy docs-format as runtime contract |
| [src/director/playback.js](https://github.com/tjx578/gods-eye-view-maps/blob/de2138e84c1778fd98a48b7c9fd0b9788c318946/src/director/playback.js) | Cancellable frame/shot phases and resource cleanup | Build optional PREP/REVIEW replay, not Driver control flow |
| [src/layers/weather/clock.js](https://github.com/tjx578/gods-eye-view-maps/blob/de2138e84c1778fd98a48b7c9fd0b9788c318946/src/layers/weather/clock.js) | Weather-specific observation clocks and allowed gaps | Weather *timestamp* and validity must remain visible |
| [src/agent/worldPacket.js](https://github.com/tjx578/gods-eye-view-maps/blob/de2138e84c1778fd98a48b7c9fd0b9788c318946/src/agent/worldPacket.js) | Produces bounded world/context summaries | Implement an **environment-only** agent context packet, not subject tracking |
| [server/mcp/plugin.js](https://github.com/tjx578/gods-eye-view-maps/blob/de2138e84c1778fd98a48b7c9fd0b9788c318946/server/mcp/plugin.js) | Own MCP transport/permission surface | NavaPRO's existing REST→MCP governance remains separate and authoritative |
| [docs/PERFORMANCE.md](https://github.com/tjx578/gods-eye-view-maps/blob/de2138e84c1778fd98a48b7c9fd0b9788c318946/docs/PERFORMANCE.md) | Single Apple M5 Chrome150 2026-08-22 baseline; advanced overlays can lower FPS dramatically | Never generalize FPS to Driver Android hardware |
| [LICENSE](https://github.com/tjx578/gods-eye-view-maps/blob/de2138e84c1778fd98a48b7c9fd0b9788c318946/LICENSE) | MIT code, separately restricted data/models; noncommercial examples | License provenance is a P0 gate for any asset ingestion |

## Detailed capability coverage

Source-specific **32 mapped capability classes** are registered at `contracts/spatial/gods-eye-capability-registry.yaml`. A mapping is **not** evidence of an implemented renderer, verified data source, hosted API, or parity. Most mapped capabilities are already conceptually covered by NaviPRO's Cesium/Kepler workbenches; the unique REA value is *composition, observable source health, scene lifecycle, and a bounded context interface*.

## Integration boundaries

```text
Existing field-survey/OSRM/RouteRevision
     │    (immutable official anchor sequence)
     ▼
NaviPRO PREP/REVIEW Context Fusion (clean-room, guarded)
     ├── Trusted provider manifest (server-side; approved data rights)
     ├── Source Health + Freshness + Attribution
     ├── Environmental overlays & terrain/imagery
     ├── Scene snapshot (proposal only, never route confirmation)
     └── Page 3 Agent reads bounded context; no source fetching by tool metadata
     │
     ▼
Cesium Terrain Lab / Kepler Map Lab / Page 2 routing review

   X No Driver LIVE calls
   X No arbitrary feed URLs, CCTV or ALPR, individual tracking
   X No route/timing/official-distance promotion
```

A weather/traffic overlay is a temporary contextual observation, **not** a time-rally rule or verified road closure. Existing `D_auth` / `D_graph` / `D_odo` / `D_geo` remain distinct. Unless a navigator-approved roadbook authority record says otherwise, contextual data does not affect official course length, average-speed/time calculations, or NaviPack contents.

## What is implemented in this REA

- `python/src/navipro_rallyos/context/fusion.py`: pure local validation and PREP/REVIEW-only context scene planning. Validates trusted server-provided source manifest, license review, timestamps, age, forecast validity, anchor order, and rejects unknown/surveillance fields. **Does not fetch third-party data.**
- `governance/gods-eye-spatial-context-policy.yaml`: explicit permissions, modes, source kinds and exclusions.
- `contracts/spatial/gods-eye-capability-registry.yaml`: 32 pinned-source capability mappings.
- `contracts/openapi/navipro-rallyos.openapi.yaml`: three **CONTRACT_ONLY** endpoints (`/context-fusion/capabilities`, `/layers/assess`, `/scenes/plan`) and three generated MCP tool definitions; these do **not** constitute a functioning HTTP/MCP server.
- `tests/contracts/test_gods_eye_rea.py`: unit tests for read-only boundary and schema behavior.

## Security, accuracy and privacy gates

1. Server-controlled source catalog and provider allowlist, with documented data rights. Client cannot approve its own source/license.
2. Hard-reject unsupported layer kind, arbitrary client URL/data payload, personally targeted monitoring, and any request bearing route confirmation or publish directives.
3. Require ISO-8601 timezone timestamps, explicit as-of time, age limit and forecast valid-until.
4. Return `CURRENT`/`STALE` context status, `CONTEXT_ONLY`, `route_authority=false`, `confirmed=false`.
5. Preserve trusted immutable official route revision ID and ordered anchors. No reordering, snapping authority, or graph/route mutation.
6. Any route-relevant observation must go through human evidence review; raw weather/imagery alone cannot produce verified KM PAL.
7. Production platform needs authentication/authorization, source rights service, ingestion pipeline, service health, secure cache, quota and refresh policies. Current prototype does not implement those services.

## Roadmap and acceptance criteria

| Priority | Build | Acceptance gate |
|---|---|---|
| P0 | Trusted provider/source manifests, release/license audit, source refresh status | Unauthorized source rejected; no stale data labelled live |
| P0 | Page 2 contextual overlay adapter for Cesium Terrain Lab | Maintains RouteRevision anchors immutably under interaction |
| P0 | Page 3 agent context read-only transport | No privileged MCP operations, no individual surveillance fields |
| P1 | Imagery comparison + documented provenance/datum | Visually inspected against known imagery benchmarks; view data not promoted to route truth |
| P1 | Scene save/replay version adapter and cancellation | Migration tested against v5/v6/unknown version fixtures, rollback on invalid import |
| P1 | End-to-end terrain/weather/aggregate traffic with licensed provider | Offline fallback and gap/coverage detection verified |
| P1 | Performance/robustness harness | Device-specific GPU, FPS, memory, 100+ layer status transitions, network cut tests |
| P2 | Configurable safe environment summary & analytics | Independent coverage/freshness thresholds and operator consent |

**Remaining blockers:** no provider deployment, no browser app build, no offline map packages, no real datasource connection, no production authentication, no mobile field tests, no proof of performance parity. **Race readiness: NOT_RACE_READY.**
