# NaviPRO RallyOS Unified OpenAPI vNext — Architecture Mapping

## Purpose

Consolidate eight historical NaviPRO OpenAPI contracts into canonical RallyOS domains without treating them as eight independent systems.

## Canonical domains

- Rally: event, roadbook, sub-trayek, source order.
- Location: search, KM PAL parse/estimate/assess.
- Evidence: proposal observations and human decisions.
- Route: directed-edge dense revisions, route profiles, coverage bindings.
- Timing: authority-profile-driven deterministic timing.
- Validation: 16 fail-closed gates.
- Integration: Google Maps preview, TSD delivery, Driver delivery/ACK.
- Workflow/Release: thin orchestration and frozen release lifecycle.

## Runtime boundary

OpenAPI/MCP is a PREP/REVIEW interface. Driver LIVE consumes a confirmed offline package and must not require cloud/MCP for the control loop.

## Authority boundary

AI is propose-only. `location-decisions`, route confirmation, external delivery, compile, and publication remain human/role gated and are explicitly blocked from MCP generation.

## Legacy migration

See `contracts/openapi/legacy-operation-migration.yaml`. The historical Sub-Trayek API is the primary migration seed; Ultimate Championship is decomposed to preserve requirements without preserving its monolithic service boundary.
