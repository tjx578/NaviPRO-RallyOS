# NaviPRO Terrain Lab — CesiumJS REA v1

**Classification:** PREP/REVIEW-only, experimental visualization scaffold; **not** a production app and **not** part of Android Driver LIVE.

This app is separate from `apps/map-lab-web` (Kepler) and **does not** give Cesium route-authority privileges. It targets the inspected `cesium_maps_rally` fork API version `cesium@1.145.0` and uses an explicit no-online-provider default (bare WGS84 ellipsoid). **Ellipsoid is not measured terrain.** Camera opens over a DEMONSTRATION extent, not an official route.

Supports initial local GeoJSON visualization. `bridge.ts` also contains draft 3D Tiles and terrain adapters, but they are not yet wired into an authenticated server-backed asset manager; their origin is allowlisted to same-origin by default, with source hash/provider/license metadata required. User-supplied manifest SHA is metadata, **not proof** that remote content was cryptographically verified. Authority boundaries remain on NaviPRO canonical core.

## Build after dependencies are installed

```sh
cd apps/terrain-lab-web
npm install
npm run typecheck
npm run build
npm run dev
```

Bundling follows Cesium's official Vite example: static-copy `Assets`, `ThirdParty`, `Workers`, and `Widgets`, plus `CESIUM_BASE_URL`. See https://github.com/CesiumGS/cesium-vite-example . Network access may be required to install npm packages; at runtime the default app disables imagery-picker/geocoder and remote imagery. Verify **zero external requests** before claiming offline support.

## Acceptance work before production

1. Install/build/typecheck, test in real WebGL browsers, inspect Cesium worker/asset URL resolution.
2. Add approved source manifest API and actual SHA verification; enforce external provider TOS and credits.
3. Add 3D Tiles/GPX/KML/CZML ingest UI and fixtures; measure 3D asset memory/performance.
4. Add terrain profiles with source/vertical datum/resolution/uncertainty, no implicit 0m heights.
5. Add Kepler⇄Cesium read-only selection/timeline linkage via immutable object IDs.
6. Confirm snapshot schema round-trip and no LIVE route-authority mutation.

Do not run the app as a driver real-time pacing tool. Terrain profile and line-of-sight output are decision-support views, not survey-certified truth.
