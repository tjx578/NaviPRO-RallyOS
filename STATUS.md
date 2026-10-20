# Status

- Repository skeleton: PRESENT
- Git repository: LOCAL INITIALIZED
- Unified OpenAPI vNext: DRAFT GENERATED
- OpenAPI structural validation: PASS
- MCP registry generation: PASS
- REST implementation: NOT_IMPLEMENTED
- MCP runtime server: NOT_IMPLEMENTED (generated registry only)
- Android runtime: NOT_BUILT
- Race readiness: NOT_RACE_READY

- Kepler capability REA: SCAFFOLDED (capability registry + Map Lab web adapter)
- Spatial PREP/REVIEW capability policy: PRESENT
- Spatial runtime parity verification: NOT_MEASURED
- Map Lab web build: NOT_BUILT

- CesiumJS REA (fork `1.145.0`): SOURCE_INDEXED, 69 capabilities, NOT_RUNTIME_VERIFIED
- Cesium3D registry/policy/schema: CONTRACT_GENERATED
- Cesium Terrain Lab web: SCAFFOLDED, NPM_INSTALL/TYPECHECK/BUILD_NOT_RUN (npm registry DNS unavailable)
- WGS84 ECEF geodesy: NUMERIC_TESTED (tests in tests/contracts/test_cesium_rea.py)
- OpenAPI Spatial3D: 9 operations, CONTRACT_ONLY, NOT_IMPLEMENTED
- MCP Spatial3D: TOOL_DEFINITIONS_GENERATED_ONLY, NO_RUNTIME_SERVER
- Kepler+Cesium coordination: DESIGN_ONLY
- LICENSE REVIEW: Apache-2.0 notices + separate ion/provider usage terms required

- StreetComplete REA: SOURCE_INSPECTED fork at `e6b04da9`, 60 capability mappings, GPL-3.0-only. No GPL code copied.
- Field Survey Android: DESIGN_SCAFFOLD_ONLY (no Gradle build).
- Field Survey Python planner/outbox: PROTOTYPE_NUMERIC_AND_QUEUE_TESTED, no field-auth/staging server/encrypted storage.
- OpenAPI Field Survey: 12 CONTRACT_ONLY endpoints; no HTTP implementation.
- MCP Field Survey: registry definitions only; human capture/sync/decision explicitly excluded.
- Real field-survey parity and ground-truth validation: NOT_MEASURED.
