# Android Cockpit Surface Layout (DESIGN_ONLY)

One Android **Navigator** app (`apps/navigator`) owns swipe pages 1–3; a **separate Driver** app (`apps/driver`) owns the Overview/Driving toggle. The 5 canonical surfaces are registered in `../contracts/ui/cockpit-surface-registry.yaml` and documented in `../docs/architecture/COCKPIT-FIVE-SURFACE-SSOT-v1.md`.

- Navigator Page 1: `features/data-rally` (OCR review, schedule, TSD send)
- Navigator Page 2: `features/offline-map-editor` (route review, map, human confirmation/driver send)
- Navigator Page 3: `features/rally-agent` (read/search/plan/propose-only)
- Driver 1: `features/driver-runtime/overview` (sub route + cue list + TSD telemetry)
- Driver 2: `features/driver-runtime/driving` (course-up, next cue, sensor state, freeze)

Common offline data modules will live in `core/navipack`, `core/offline-map`, `core/location-db`. TSD/driver delivery lives in `integrations/`, not Driver UI.

**These directories are planned module boundaries and README scaffolding only; they are not installed Gradle modules or a working Android binary.**
