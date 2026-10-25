# Status

## Audit integration follow-up — 2026-10-25

- PR #1/#2/#3: reconciled in an isolated integration branch; main is unchanged.
- CI: workflow defined for Python 3.11/3.12, JavaScript, schema, MCP drift and static prompt checks. Hosted run results must be read separately; branch protection is not configured by this patch.
- Dependencies: requirements-test.txt delegates to the pinned requirements-test.lock.
- Valhalla: exact polyline6 leg joins and source-anchor endpoint proximity guards added. Directed-edge traversal and physical identity remain NOT_VERIFIED.
- Platform: Navigator Web/PWA, Driver Android Native (ADR-0001); ownership declarations only, no frontend build.
- Timing: exact Fraction arithmetic, separate raw/corrected odometer functions and date-less draft schedule implemented. Event-rule engine and TimingCompute API remain NOT_IMPLEMENTED.
- Current container: Docker executable unavailable; real graph benchmark BLOCKED. The 20 October Docker Desktop OOM below is historical evidence from a different host.
- Race readiness: NOT_RACE_READY. Authenticated review, all 16 evaluators, location write service, signed packs and device/field tests remain open.

## Component history and remaining gaps

- M1 ROTR Surabaya: PARSER_AND_DIAGNOSTIC_FOUNDATION_TESTED, ROUTE_UNRESOLVED.
- Original Trayek 2 image preserved; visual transcription PENDING_OPERATOR_REVIEW.
- B-D 19.60 km and A-E 120 minutes: ARITHMETIC_VALID; not route or timing-rule validation.
- OSRM/Valhalla build recipes and pinned image manifests: PRESENT, REAL_BUILD_NOT_EXECUTED.
- Local Docker engine: BLOCKED (backend memory failure observed 2026-10-20).
- Exploratory Surabaya OSM extract: PREPARED; administrative/driving-side coverage NOT_VERIFIED.
- M1 real provider comparison, directed-edge solver and Page 2 evidence GUI: NOT_EXECUTED / NOT_IMPLEMENTED.
- M1 implementation and reproducible commands: `docs/implementation/M1-ROTR-SURABAYA.md`.

- Repository skeleton: PRESENT
- Git repository: LOCAL INITIALIZED
- Unified OpenAPI vNext: DRAFT GENERATED
- OpenAPI structural validation: PASS
- MCP registry generation: PASS
- REST implementation: NOT_IMPLEMENTED
- MCP runtime server: NOT_IMPLEMENTED (generated registry only)
- Android runtime: NOT_BUILT
- Race readiness: NOT_RACE_READY

- Canonical 16 gate identities: PRESENT_IN_OPENAPI
- Gate-to-eight-division mapping and operation allowlists: CONTRACT_ONLY, governance registries added
- ValidationReport schema: EXACTLY_ONE_OF_EACH_GATE; FAIL/NOT_RUN cannot claim PASS
- Deterministic 16-gate evaluators / compiler: NOT_IMPLEMENTED
- Eight specialist agents and revision-bound handoff: DECLARED_ONLY, NO_AGENT_RUNTIME
- Agent permissions / reviewer authentication / release enforcement: NOT_RUNTIME_ENFORCED
- Gate assessment: docs/architecture/QUALITY-GATES-EIGHT-DIVISIONS-v1.md

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

- Physical Location Intelligence / Route–Distance–Time SSOT: DOCUMENTED, policy and candidate assessment JSON Schema added; **NO physical resolver, imagery acquisition, travel-time solver, human approval backend, or runtime implementation**.
- Route–Distance–Time source-of-truth rule: official ordered roadbook + separate distance domains + event-specific timing rules; AI/imagery/map pins remain non-authoritative.
- React Native Maps source audit: report now INCLUDED in repo under docs/rea; renderer still NOT_BUILT/NOT_INTEGRATED.

- Cockpit v3.0 UI architecture: FIVE_SURFACES_CONTRACTED (three Navigator pages, two Driver modes)
- Cockpit source: NAVIPRO-MAPOS-COCKPIT-UNIFIED-V3.0, external attachment SHA-256 pinned in UI registry
- Cockpit UI role/action policy: DECLARED_AND_CONTRACT_TESTED; NOT_RUNTIME_AUTH_ENFORCED
- Navigator Web/PWA and Driver Android features: README_MODULE_SCAFFOLDS_ONLY, NO_FRONTEND_BUILD
- TSD Cadencer/Driver ACK adapters: DESIGN_ONLY, NOT_INTEGRATED
- Driver overview/driving mode and cue FSM: NOT_BUILT

### Valhalla REA scope (2026-10-20)

- Source: `tjx578/valhalla-navipro@618cad5`, upstream-identical MIT fork.
- Added: clean-room Valhalla native candidate/matrix adapter, provider-distance diagnostics, REA source manifest, governance and fixture tests.
- **Not built/deployed:** Valhalla graph tiles, live HTTP integration, Page 2 route workbench, comparative performance benchmark, live Driver runtime, production release. No replacement of OSRM. `NOT_RACE_READY` remains.
- Integration response guards: native source indices validated, missing matrix values rejected, provider warnings preserved, and route/matrix provenance required before transport; fixture-only regression coverage.
