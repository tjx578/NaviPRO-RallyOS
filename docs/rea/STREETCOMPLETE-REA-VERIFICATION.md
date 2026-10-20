# Field Survey REA verification evidence

- Source inspection: connected GitHub repository `tjx578/StreetComplete_rally-maps`, default `master`, `e6b04da98028d34c1e49625edd7095f7008106a6`.
- Direct paths sampled: README, quest guidance, registry, road surface/smoothness/oneway/maxspeed, overlay registry, download/autosync/SQLite/edit/upload, OSM API/conflicts, notes/photo, GPS track and data sources.
- Capability registry entries: 60. They represent **mapping only**, not proven implementation parity.
- OpenAPI: 65 paths and 65 operations; 85 component schemas; 0 unresolved component refs; operation IDs unique; **55 MCP tool definitions** and **10 blocked operations**.
- Survey contracts added: 12 operations; 9 agent-facing metadata definitions and 3 blocked human-only mutations.
- Deterministic survey Python: task planner, strict E7/source version validation, one-way applicability guard, local SQLite idempotency and conflict HOLD.
- Standalone JSON Schema: Draft 2020-12 with `mode PREP|REVIEW` and `route_authority=false`.
- Python test command: `python -m pytest -q tests/contracts`.
- Test suite: 24 passed (including 14 StreetComplete survey tests). Build/deployment status remains `NOT_RACE_READY`.
- **Not tested:** Android APK, GPS driver, external OSM APIs, server authentication/authorization, file/media upload, secure at-rest storage, event-scoped tenant access, real-world precision/false-positive benchmarks, UI performance, remote MCP HTTP execution.

This record deliberately distinguishes **SOURCE-INSPECTED**, **CONTRACT-DEFINITION**, **PROTOTYPE-TESTED**, **BUILD-UNVERIFIED**, and **DEPLOYMENT-UNVERIFIED**. A registry cannot prove StreetComplete parity.
