# NaviPRO Routing Lab (OSRM-inspired)

A clean-room **policy/UI state prototype** for Page 2 PREP/REVIEW. The view should consume canonical route anchors and OSRM `CANDIDATE_REVIEW` responses via NaviPRO's API gateway, not call public routing services directly. Graph manifest, Lua profile digest and routing result provenance must appear on screen.

## Planned UI

- Locked sequence of official roadbook anchors (cannot reorder)
- Alternative route selection changes **candidate preview only**
- Separate shaping-points inserted within a specific official leg, never source order
- A local/self-hosted basemap with attribution and optional OSRM debug vector tiles
- Match confidence/outlier review against recorded GPS traces
- High-level compare to current immutable `RouteRevision`; delta never implies compliance
- Route approval only in navigator-authorized Page 2 canonical workflow, not this preview

## What exists

`src/review-policy.mjs` and `test/review-policy.test.mjs` implement/test a deterministic read-only state boundary. No Leaflet UI, no browser build, no REST service, no map tiles, no screenshots, and no live OSRM server are bundled. Run `npm test` with a recent Node.js. This module does **not** make NaviPRO equivalent to `osrm-frontend`.

## Source inspiration and license

Pattern analysis from BSD-2-Clause `Project-OSRM/osrm-frontend` at fork `tjx578/osrm-frontend-rally-maps` commit `067092c0c01efd57c2bf1c2b1e9fc1da4a193871`. No vendor source copied. If third-party code is later copied, preserve applicable license and attributions.

## Leaflet Routing Machine REA: Source-order safe review (2026-10-20)

`src/lrm-rally-review.mjs` is a **clean-room, pure JavaScript prototype** that consumes an authoritative snapshot and exposes only locked review state. It does **not** bundle Leaflet or LRM and does **not** provide a web map by itself. A future browser integration must call `lockedLrmOptions()`, display fresh waypoint DTOs, and send `prepareReviewRequest()` to an authenticated backend using the source revision from trusted storage. `routeselected` is preview-only; line touches/marker dragging cannot mutate roadbook anchors.

The corresponding backend validation helper is `python/src/navipro_rallyos/route/lrm_review.py`. It compares all route/graph IDs, official anchor order and candidate IDs against a **server-trusted snapshot**, not client-supplied authority. See `docs/rea/LEAFLET-ROUTING-MACHINE-REA-v1.md` for the full source audit and compatibility cautions (LRM v3.3.0 source vs OSRM Frontend v3.2.12 dependency).

Run: `npm test` in this subdirectory (uses Node built-in tests; no external packages needed).
