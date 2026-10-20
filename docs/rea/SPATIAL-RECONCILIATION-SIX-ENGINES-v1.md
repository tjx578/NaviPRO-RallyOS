# NaviPRO RallyOS — Six Source Engine Reconciliation

**Date:** 2026-10-20. **Scope:** Integration architecture decision, not runtime parity certification.

## Capability boundaries

| Source | What it is good at | Where in NaviPRO | Not allowed to do |
|---|---|---|---|
| Kepler.gl | Spatial exploration, advanced layer filters, visual comparison, time playback | Map Lab (Page 2 PREP/REVIEW) | Declare an official route/landmark VERIFIED |
| CesiumJS | WGS84 globe, terrain sampling, 3D Tiles / imagery / scene | Terrain Lab (PREP/REVIEW) | Convert image/terrain position to rally/odo authority |
| StreetComplete | OSM quest patterns, local observation, offline survey changes | Field Survey + Evidence Staging | Auto-edit canonical route or OSM without separate OSM authorization |
| OSRM Backend | Directed road graph, restrictions, routing candidates, map matching, matrix | Routing service (PREP/REVIEW) | Reorder official points, claim D_auth, auto-confirm |
| OSRM Frontend | Leaflet map/routing deployment configuration, geocoding, entrance picker, GPX, debug UI | Routing Lab host application patterns | Publish source waypoint modifications |
| Leaflet Routing Machine | Routing control, Plan, waypoint UI, alternative routes, itinerary, geocoder events, line hit-testing | Routing Lab component (Page 2) | Perform routing itself, rewrite official ordered source, auto-approve |

## Interaction architecture

```text
        OFFICIAL SOURCE / AUTHORITY PROFILE
                        |
                Canonical Roadbook
                        |
              immutable source sequence
                        |
                  RouteRevision
                        |
        +---------------+----------------+
        |                                |
    Candidate plane                  Evidence plane
    OSRM directed graph           StreetComplete-style survey
        |                                |
        v                                v
   OSRM REST adapter                 Staging review
        |
        v
    Page 2 Routing Lab  <── Kepler analytics / Cesium context
        |
   LRM UI (view only) + candidate alternatives
        |
   Shaping-point PROPOSALS (not source edits)
        |
   NaviPRO schema + server snapshot revision/order gate
        |
     Authenticated Navigator authority + Quality Gates
        |
    Confirmed RouteRevision → NaviPack → Offline Driver

Page 3 Rally Agent → MCP gateway → read/plan/propose tools only
```

## Why two separate OSRM/Leaflet frontend concepts?

OSRM Frontend is the **host routing map application** (`Leaflet`, geocoder, URL state, GPX, multiple backends, tile providers). Leaflet Routing Machine is one of its underlying **UI control dependencies**. They overlap, so do not make two independent route editors or expose duplicated MCP tools. Use a single NaviPRO Page 2 Routing Lab with injected UI presentation and a shared OSRM adapter. LRM fork version `3.3.0`, existing OSRM frontend dependency `3.2.12`: check compatibility before upgrading. The UI should integrate with the canonical RouteRevision and evidence/approval boundary, not become a source of truth.

## Source data quality and precision

- Official order = source-ordered RoadbookEvents, not a drag-and-drop waypoint array.
- Official distance (`D_auth`) = roadbook; route graph candidate distance = OSRM, not LRM formatter output.
- Official timing = event timing rule and duration; OSRM duration/ETA can only be used for operational analysis, not Time Rally scoring logic.
- Survey tags, elevation, road names, snap geometry, geocoder place names = candidate/evidence; no direct authority promotion.
- Map project revision, routing preview state, route revision, and NaviPack release are **different lifecycles**.
- Driver LIVE requires confirmed offline package only; no Kepler/Cesium/LRM or online OSRM calls.

## Implementation order and measurable milestones

**M1 UI skeleton wired to session guard:** Pin JS LRM dependency, create authenticated Page 2 review host, display map and ordered official anchor list as read-only, alternative selection no source writes, browser automated test.

**M2 graph-backed route candidates:** Boot local OSRM graph for a selected Bali OSM extract, test route/NoRoute/nearest and graph/profile versions, show dashed disconnections as HOLD, compare with official anchors and mandatory landmarks.

**M3 evidence-aware editing:** Tap line to create shaping point proposal (never modify official anchors), validate with server trusted snapshot, compare original vs snapped location, GateReceipt, audit log.

**M4 final verification:** Replay a test event/sub-trayek, inspect geometry coverage against original roadbook, confirm only through authenticated navigator, build verified offline NaviPack, test Driver independent of network.

No above milestone is declared complete by the LRM REA artifacts alone. Current result is a static source audit + contract + proposal validator + unit tests.
