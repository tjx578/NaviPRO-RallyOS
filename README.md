# NaviPRO RallyOS vNext

**Status:** WORKING_REPOSITORY_SKELETON / OPENAPI_VNEXT_DRAFT / NOT_RACE_READY

This repository continues the earlier NaviPRO RallyOS monorepo design and adds a concrete **Unified OpenAPI vNext** plus an **OpenAPI → MCP tool registry generator**.


## Cockpit architecture: Page 1/2/3 + Driver 1/2 (2026-10-20)

The canonical UI design now follows the user-approved v3.0 specification: **one Navigator app with three swipe pages** and **one separate Driver app with two switchable read-only modes**. This is a **design and contract alignment**, not a working Android build.

- **Page 1 Data Rally:** source/OCR review, start & starting list, sub timing and numeric speeds, external TSD Cadencer with real ACK.
- **Page 2 Offline Map & Route Editor:** selected-sub immutable source steps, map/evidence and draft-only route changes, human confirmation gates, driver NaviPack send.
- **Page 3 Rally Agent:** research/voice/local search, evidence provenance, propose-only Page 2 inbox; no confirm/publish or generative LIVE.
- **Driver 1 Overview:** selected sub full course, cue list and read-only TSD dashboard.
- **Driver 2 Driving:** course-up lower-third look-ahead, cue FSM, offline OSM context, off-route freeze, read-only TSD.

**Source and build guidance:** [Five-Surface Cockpit SSOT](docs/architecture/COCKPIT-FIVE-SURFACE-SSOT-v1.md) · [Build Plan](docs/implementation/COCKPIT-FIVE-SURFACE-BUILD-PLAN-v1.md) · [UI registry](contracts/ui/cockpit-surface-registry.yaml) · [Action authority policy](governance/cockpit-role-action-policy.yaml).

```bash
python -m pytest -q tests/contracts/test_cockpit_five_surfaces.py
```

Existing Kepler/Cesium/Routing Lab web scaffolds remain **supporting Page 2 PREP/REVIEW tools**, not additional navigator pages. Driver buttons shown in early mockups that send links are expressly excluded by the v3.0 Driver read-only requirements. The Rally engine's invariant remains **ordered roadbook + official distance/KM PAL + event-governed time**. No GitHub push or deployed runtime is implied by these docs.

## What is implemented in this artifact

- Unified OpenAPI 3.1 contract across Rally, Location, Evidence, Route, Timing, Validation, Integration, Workflow, and Release.
- Canonical schemas for event/sub-trayek, E7 coordinates, route revisions, coverage bindings, timing rules, gate receipts, delivery envelopes, and release manifests.
- NaviPRO vendor extensions: `x-navipro-mcp`, `x-navipro-mode`, `x-navipro-authority`, and `x-navipro-side-effect`.
- Legacy operation migration registry for the eight historical NaviPRO APIs.
- MCP tool-registry generator that exposes only permitted operations.
- Explicit PREP/REVIEW vs LIVE and human-authority boundaries.

## Important

This is not yet a production implementation. The contract exists; endpoint business logic, real authentication, road graph resolver, reviewer service, Android build, NaviPack publication, and field validation still require implementation and evidence.

## Verify

```bash
python tools/validate_openapi.py
python tools/build_mcp_registry.py
```

## Key files

- `contracts/openapi/navipro-rallyos.openapi.yaml`
- `contracts/openapi/legacy-operation-migration.yaml`
- `services/mcp/generated-tool-registry.yaml`
- `docs/architecture/OPENAPI-VNEXT-MAPPING.md`

## Spatial Intelligence REA baseline

The repository now includes a capability-level REA of `tjx578/kepler.gl-_mapas_rally` (Kepler.gl `3.3.0-alpha.11`). See `docs/rea/KEPLER-GL-REA-v1.md`. The added `apps/map-lab-web/` workbench targets Kepler-grade PREP/REVIEW geospatial analytics while all rally authority remains in canonical NaviPRO contracts and human-reviewed revisions.

Verification:

```bash
python tools/validate_spatial_rea.py
python tools/validate_openapi.py
python tools/build_mcp_registry.py
```

## CesiumJS 3D / Terrain Intelligence REA

`docs/rea/CESIUMJS-REA-v1.md` audits `tjx578/cesium_maps_rally` (`cesium@1.145.0`). This adds an isolated `apps/terrain-lab-web/` scaffold and **69 source-indexed Cesium capabilities** to the Kepler-grade PREP/REVIEW Map Lab architecture. It introduces explicit WGS84/ECEF numerical helpers, 3D asset/snapshot policy, 9 `spatial3d` OpenAPI definitions, and generated MCP registry entries. The rest of the authoritative route/timing/evidence/NaviPack system is unchanged. See `docs/rea/SPATIAL-RECONCILIATION-KEPLER-CESIUM-v1.md`.

```bash
python tools/validate_cesium_rea.py
python tools/validate_spatial_rea.py
python tools/validate_openapi.py
python tools/build_mcp_registry.py
python -m pytest -q tests/contracts
```

**Important:** neither Kepler nor Cesium WebGL frontend has been built in this environment, and OpenAPI/MCP service implementations are not present. The static Cesium app is a prototype; the numerical geodesy helper is tested. No dependency is added to Driver LIVE.

## StreetComplete Field Survey REA (third spatial capability)

- [Source audit](docs/rea/STREETCOMPLETE-REA-v1.md) and [Kepler/Cesium/StreetComplete reconciliation](docs/rea/SPATIAL-RECONCILIATION-KEPLER-CESIUM-STREETCOMPLETE-v1.md).
- Source: `tjx578/StreetComplete_rally-maps`, GPL-3.0-only, SHA `e6b04da98028d34c1e49625edd7095f7008106a6`. **Patterns only; no GPL source copied.**
- [Registry](contracts/spatial/streetcomplete-capability-registry.yaml), [policy](governance/streetcomplete-field-survey-policy.yaml), [Android scaffold](apps/field-survey-android/README.md).
- Python deterministic survey planner and SQLite offline outbox are prototypes, not production or race-ready services. `LIVE` remains deny.

## OSRM Backend + Frontend REA (2026-10-20)

- Sources: `tjx578/osrm-backend-maps-rally` (`f0a7a2ff`) and `tjx578/osrm-frontend-rally-maps` (`067092c0`). Both are general-purpose Project-OSRM forks; **not** Time Rally-specific implementations.
- [Detailed dual repo audit](docs/rea/OSRM-BACKEND-FRONTEND-REA-v1.md), [source manifest](docs/rea/OSRM-SOURCE-MANIFEST.yaml), [five-engine reconciliation](docs/rea/SPATIAL-RECONCILIATION-FIVE-ENGINES-v1.md), [capability registry](contracts/routing/osrm-capability-registry.yaml), [policy](governance/osrm-routing-policy.yaml).
- `python/src/navipro_rallyos/route/osrm_adapter.py` provides **tested PREP/REVIEW prototype** request builders and a response adapter for route/table/match, not an OSRM engine or deployed API.
- `apps/routing-lab-web/` is a small standalone JS **read-only state prototype**; there is no Leaflet/MapLibre graphical frontend yet.
- No `Trip`/TSP in NaviPRO MCP, no official source waypoint reorder; OSRM results always candidate-only. Driver LIVE does not call OSRM.
- Verify locally: `python tools/validate_openapi.py && python tools/build_mcp_registry.py && python -m pytest -q tests/contracts && node --test apps/routing-lab-web/test/*.test.mjs`.
- **Status:** OSRM dataset/build/CH/MLD, real network server, browser UI, field accuracy and end-to-end routing parity are **NOT VERIFIED**.

## Leaflet Routing Machine REA — Page 2 Route Editor (2026-10-20)

- [Source audit](docs/rea/LEAFLET-ROUTING-MACHINE-REA-v1.md), [38-capability registry](contracts/routing/lrm-capability-registry.yaml), [source manifest](docs/rea/LEAFLET-ROUTING-MACHINE-SOURCE-MANIFEST.yaml) and [policy](governance/lrm-routing-ui-policy.yaml).
- Source `tjx578/leaflet-routing-machine-rally` is identical to upstream `perliedman/leaflet-routing-machine` at `8dc939a314...` (LRM `3.3.0`, ISC license); not a rally-specific codebase. The separate OSRM Frontend uses LRM `3.2.12`; no dependency upgrade was done.
- A clean-room LRM review-state prototype in `apps/routing-lab-web/src/lrm-rally-review.mjs` and a server-side proposal validator in `python/src/navipro_rallyos/route/lrm_review.py` **reject official anchor edits/changes to graph/revision ID and LIVE**. New UI contract only adds 5 OpenAPI operations, with UI-only alternative selection blocked from MCP.
- No Leaflet browser application, backend endpoint, authenticated review service or official route confirmation is implemented. Driver LIVE uses only previously confirmed offline NaviPack; **NOT_RACE_READY**.

### God's Eye View REA — Spatial Context Fusion

See [`docs/rea/GODS-EYE-VIEW-REA-v1.md`](docs/rea/GODS-EYE-VIEW-REA-v1.md) and the [eight-source reconciliation](docs/rea/SPATIAL-RECONCILIATION-EIGHT-SOURCES-v1.md). A trusted-source PREP/REVIEW prototype adds context freshness/rights checks without route mutation. This **does not** install or duplicate the God's Eye View application and **does not** enable individual surveillance feeds, real-time Driver services, or authoritative route decisions.

## Route–Distance–Time + Physical Location Intelligence SSOT (2026-10-20)

The project decisions from the latest navigator review are now recorded in the [Route–Distance–Time & Physical Location SSOT](docs/architecture/ROUTE-DISTANCE-TIME-PHYSICAL-LOCATION-SSOT-v1.md), accompanied by a [fail-closed policy](governance/route-distance-time-location-policy.yaml) and a [non-authoritative physical location assessment JSON Schema](contracts/jsonschema/physical-location-assessment.schema.json).

**Key invariant:** NaviPRO reasons over **official ordered route instructions + distance/KM PAL + event-governed time**, not a shortest or fastest map route. Satellite imagery helps evaluate physical POI plausibility, not verify place identity on its own. `POI_REFERENCE`, `PHYSICAL_LOCATION`, and `ROUTE_ACCESS_POINT` must be distinguished, with provenance, uncertainty and human review. Distance domains (`D_auth`, `D_graph`, `D_odo`, `D_geo`) are never conflated.

The previously standalone [React Native Maps audit](docs/rea/REACT-NATIVE-MAPS-REA-v1.md) is now included **as documentation**, not as a mobile build or installed adapter.

**Status:** governance + draft schema + schema unit tests only; no satellite POI matcher, time solver, REST/MCP endpoints or live Driver integration. `NOT_RACE_READY`.
