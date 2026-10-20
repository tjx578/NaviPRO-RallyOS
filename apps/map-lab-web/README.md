# NaviPRO Map Lab Web — Kepler REA Adapter

Status: **SCAFFOLD / PREP-REVIEW ONLY / NOT RACE READY**.

This app is the capability-parity workbench for high-end geospatial exploration. It intentionally does **not** replace NaviPRO Canonical Route, authority gates, NaviPack, or Driver LIVE.

Baseline dependency is pinned to `3.3.0-alpha.11` to match the inspected fork snapshot. Before production, run an upstream compatibility campaign and pin a reviewed release/commit.

## Boundary

- Kepler-style datasets/layers/filters/drawings/annotations = analytic workspace state.
- Confirmed NaviPRO `RouteRevision` is mounted read-only as an overlay.
- Any geometry drawn/edited in Map Lab becomes a **proposal** and must pass route/location validation + human review.
- External basemap/tile/raster services are provider evidence, not rally authority.
- Driver LIVE never loads this application.

## Initial capability flags

The scaffold enables raster tiles, WMS, Flow, Bitmap, A5, GeoHash, annotations, drawing, scale/navigation controls, swipe/globe/layer groups, column statistics and all file formats exposed by the inspected fork.
