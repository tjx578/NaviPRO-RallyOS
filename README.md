# NaviPRO RallyOS vNext

**Status:** WORKING_REPOSITORY_SKELETON / OPENAPI_VNEXT_DRAFT / NOT_RACE_READY

This repository continues the earlier NaviPRO RallyOS monorepo design and adds a concrete **Unified OpenAPI vNext** plus an **OpenAPI → MCP tool registry generator**.

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
