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
