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

- OSRM Backend+Frontend REA: DIRECT_GITHUB_SOURCE_INSPECTED, 56 capability mappings, both forks tracked with exact commits.
- OSRM Routing contract: 9 PREP/REVIEW operations added; generated MCP tool definitions only, not a running MCP server.
- OSRM Python route/table/match adapter: PROTOTYPE_UNIT_TESTED_WITH_MOCK_PROVIDER; no real OSM graph, no OSRM server, no routing parity.
- Routing Lab JavaScript: READ_ONLY_STATE_TESTED; full Leaflet/MapLibre GUI NOT_BUILT.
- OSRM profile and dataset manifest: REQUIRED_BUT_NOT_BUILT; no MLD/CH preprocessing executed.
- OSRM Driver offline integration: NOT_BUILT; LIVE provider calls prohibited.

- Leaflet Routing Machine REA: SOURCE_INSPECTED at `8dc939a314425684883dc6f016b3aa9d04c8b7ca` (fork identical to upstream at audit, ISC source, v3.3.0).
- LRM source capability map: 38 SOURCE_MAPPED / NOT_BROWSER_VERIFIED; no upstream source copied.
- LRM UI review-state JS / server-side Python proposal guard: UNIT_TESTED; no Leaflet DOM/graphical build.
- LRM OpenAPI: +5 CONTRACT_ONLY operations, +4 agent-safe MCP definitions, +1 UI-only excluded operation.
- Version compatibility (separate OSRM Frontend LRM v3.2.12 vs v3.3.0): NOT_TESTED.
- Route confirmation permission service: NOT_IMPLEMENTED. LIVE LRM calls: FORBIDDEN.

- God's Eye View REA: DIRECT_SOURCE_INSPECTED at `de2138e84c1778fd98a48b7c9fd0b9788c318946` (fork matches upstream at audit; MIT source but third-party data rights vary).
- God's Eye View capability registry: 32 SOURCE_MAPPED, non-authoritative PREP/REVIEW only; no CCTV, ALPR or individual tracking imported.
- Spatial Context Fusion: CLEAN_ROOM_PYTHON_PROTOTYPE_TESTED for source age, rights, forecast validity, trusted route anchors, and privacy/authority policy.
- OpenAPI context fusion: +3 CONTRACT_ONLY operations and generated MCP definitions; NO deployed endpoints.
- Browser imagery comparison / environmental provider runtime / Android parity: NOT_BUILT.
- React Native Maps REA: prior STANDALONE_ANALYSIS_ONLY, not integrated in local git repo.
