# NaviPRO RallyOS — 3 Navigator Pages + 2 Driver Modes: Implementation Plan

**Platform amendment (2026-10-25):** [ADR-0001](../architecture/ADR-0001-HYBRID-PLATFORMS.md) selects Navigator Web/PWA and Driver Android Native. The original source digest records the historical design input, not this amended registry. UI and delivery remain DESIGN_ONLY.

**State:** Proposed roadmap, not a schedule commitment and not yet built. Follows `docs/architecture/COCKPIT-FIVE-SURFACE-SSOT-v1.md` and the source v3.0 specification.

## Dependency-first incremental build

| Slice | Implemented when | Owner/source tree | Primary demonstration | Exit / negative test |
|---|---|---|---|---|
| **F0 Contract baseline** | First | `contracts/ui`, `governance`, `tests/contracts` | Reproducible five-surface registry + permissions | Forbidden Driver/agent actions blocked by policy validator; source/mode traceable |
| **F1 Page 1 deterministic** | Second | `python/.../rally`, `python/.../timing`, `apps/navigator-web/features/data-rally` | ROTR Surabaya A–E fixture → timing & distance table | 19.60km B–D / 120min A–E; no inferred route, modes distinct; preserve source; OCR-review gate |
| **F2 Page 2 map & route review** | Third | `apps/navigator-web/features/offline-map-editor`, `python/.../route`, `.../locations` | Selected-sub list ↔ route candidates + spatial evidence | Zero reorder; graph vs official distance separate; revision diff/confirm gate; no public tile reliance offline |
| **F3 Driver 1/2 deterministic preview** | In parallel after F1/F2 contracts | `android/apps/driver`, `android/features/driver-runtime` | Same confirmed test NaviPack displayed in Overview and Driving | No editing/agent/send controls; shared immutable revision; pack check; mode toggle and cue-frozen test |
| **F4 Page 3 proposal integration** | After F1/F2 API and read-only evidence | `apps/navigator-web/features/rally-agent`, `services/mcp`, `services/api` | Candidate location with physical evidence → Page 2 proposal | Tool denylist; never automatically verify, mutate/approve/publish; offline no hallucinated success |
| **F5 Device/system integration** | Only when real integrations are available | `android/integrations`, `services/integrations`, `release`, `tests` | Page1 plan → TSD ACK; Page2 signed pack → Driver ACK; recorded sensor replay | Cold-start offline, real hardware performance, reproducible release receipts and human sign-off |

**Do not infer progress from scaffolding:** existing `apps/navigator-web` and `android/apps/driver` are design ownership only; no validated Navigator browser/PWA build or Driver Gradle build. Existing JS map labs are PREP/REVIEW prototypes; registry contains no deployed API/MCP server. F0 is the only slice implemented by this architecture change.

## First concrete deterministic benchmark — ROTR Surabaya image

- The user-provided ROTR Surabaya sample provides A 2min; B 7.57km/25min (Tetap Detik); C 5.75km/20min (Tetap Menit); D 6.28km/22min (Rata-Rata); E 51min (ordered sponsor/social stops and route free).
- **Mathematical structure:** `7.57+5.75+6.28 = 19.60 km`, `2+25+20+22+51 = 120 min`; these are reported **source-stated totals** and arithmetic checks, not road length validation.
- Distinct timing modes and source textual instruction ordering must persist. The meaning/reference of *2.93 km* in part B, B→C and C→D transitions, physical landmark coordinates and Finish are **unresolved** until evidence/briefing; a solver must never invent them.
- Acceptance classification while map/candidates unresolved: `ARITHMETIC_VALID / ROUTE_UNRESOLVED`.
- Start with hand-reviewed data fixture; OCR service can be layered on after deterministic parsing is tested.

## Repository ownership and delivery

- OpenAPI (`contracts/openapi/navipro-rallyos.openapi.yaml`) remains API SSOT; five-surface YAML governs UI composition and role/mode policy but does not duplicate endpoint payloads.
- Page 2 draws from `apps/routing-lab-web`/`map-lab-web`/`terrain-lab-web` as ancillary workbench/adapters; avoid five independent rendering engines.
- External TSD Cadencer has an independent application/repository: use versioned envelope, outbox, idempotency and **actual** ACK; Driver consumes TSD only as read-only telemetry.
- Self-hosted or local OSM data/PMTiles and styling preserve offline capability. OSM/Humanitarian is layer evidence; `D_graph` cannot overwrite `D_auth`.
- Confirm/pack release always authenticates navigator, validates all gates, and freezes RouteRevision before Driver activation.

## Delivery matrix

| Artifact | Now | Production goal |
|---|---|---|
| UI surface registry and role policy | PRESENT (design declarations) | Runtime enforced policy + UI tests |
| Web/PWA Page 1/2/3 and Android Driver 1/2 | README scaffolds only | Navigator Web/PWA and Driver Kotlin/Compose with five tested surfaces |
| Page 1 parser/time core | ROTR parser + exact draft arithmetic; event rules NOT IMPLEMENTED | Deterministic corpus with timing acceptance |
| Graph-backed route review | Candidate state prototypes only | Pinned OSRM graph, real Page 2 map/editor and review gates |
| Humanitarian & satellite validation | Design only | Rights-reviewed ingest + dated imagery review/evidence |
| Driver NaviPack and cue FSM | NOT BUILT | Signed local package + offline replay on real tablet |
| REST/MCP / TSD & Driver ACK | Contract only | Authorized endpoints and field-tested delivery receipts |
