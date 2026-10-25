# ADR-0001 — Navigator Web/PWA and Driver Android Native

Date: 2026-10-25 (Asia/Makassar). State: selected implementation direction under the user's instruction to continue the repository audit; runtime remains DESIGN_ONLY / NOT_RACE_READY.

## Context and decision

The uploaded 2026-10-25 audit identifies conflicting Navigator platform ownership: the older cockpit v3.0 design points to Android, while the recommended implementation is Web/PWA. Maintain one implementation target per role:

| Role | Surface | Owner | Renderer target |
|---|---|---|---|
| Navigator | Page 1–3 | `apps/navigator-web` | MapLibre GL JS on Page 2 |
| Driver | Overview / Driving | `android/apps/driver` | MapLibre Native |

Preserve the five-surface behavior and role restrictions. Keep earlier Android Navigator placeholders as historical pointers, not competing build targets. Supporting Kepler, Cesium and routing labs are research/review tools consumed by Page 2, not extra product pages.

## Implementation boundaries

- Python owns deterministic domain/routing/validation services; TypeScript UI consumes canonical API contracts. No authoritative computation is delegated to a generative agent.
- Navigator caches reviewed source/drafts and local map assets in a future tested PWA implementation. Browser storage eviction, offline startup, asset limits and target browser support are **unverified**. PWA designation alone does not prove offline functionality.
- WebGL renders Navigator maps; Android renders the confirmed Driver package. Neither renderer selects an authoritative route.
- TSD and Driver delivery have service/bridge owners under `services/integrations` and device counterparts under `android/integrations`. A browser is not assumed to have arbitrary filesystem, USB or Bluetooth access. Transport selection remains an engineering follow-up.
- Driver LIVE uses an already checked, signed, immutable NaviPack. No API, map server, routing engine, PWA or LLM is required for LIVE progression. GPS, clock, cue FSM and journal are deterministic Android runtime responsibilities.
- Source and route changes during PREP/REVIEW create revisions; stale gate/review results become invalid. No active LIVE revision is silently replaced. Queued delivery is not an ACK.

## Consequences and acceptance

The registry is amended to version 1.1.0 with explicit platform owners, renderer targets and service/device boundaries. Its original document hash remains provenance for the historical input; it is not a hash of the amended contract.

This decision creates no working frontend or backend. Demonstrate Navigator offline cold start, editing and evidence review; bridge delivery with real ACK; and Android offline replay before claiming those capabilities. Authentication, all 16 evaluators, pack signing and field validation remain separate required work. Existing authority policy still applies on both platforms.
