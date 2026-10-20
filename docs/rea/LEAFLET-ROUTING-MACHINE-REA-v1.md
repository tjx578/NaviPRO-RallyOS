# Reverse Engineering Anything (REA): Leaflet Routing Machine → NaviPRO RallyOS

**Audit date:** 2026-10-20  
**Source:** [`tjx578/leaflet-routing-machine-rally`](https://github.com/tjx578/leaflet-routing-machine-rally)  
**Pinned source SHA:** `8dc939a314425684883dc6f016b3aa9d04c8b7ca`  
**Status:** `SOURCE_INSPECTED / CONTRACT_GENERATED / REVIEW_GUARDS_UNIT_TESTED / NOT_BROWSER_VERIFIED / NOT_RACE_READY`

## Executive verdict

This repository is a **byte-for-byte identical Git commit** to the available `perliedman/leaflet-routing-machine` upstream `master` at audit (`ahead=0`, `behind=0`), rather than a rally-specific modification. Package version **3.3.0**, source licence **ISC** (GitHub metadata does not provide a recognized SPDX identifier). The upstream README calls the plugin "barely maintained", and `npm test` in the source `package.json` exits with an error rather than running a test suite. Jasmine test source files exist but are old and do not establish a current reproducible CI suite. Integration risk: the separately audited `osrm-frontend-rally-maps` uses `leaflet-routing-machine: 3.2.12`; no upgrade to 3.3.0 was performed here.

**What it is:** a Leaflet map **routing interaction / presentation control**, not an alternative directed road-graph solver. It delegates route computation to OSRM v5 or other injected backends. Its value is UX around candidate routes. **Do not** treat it as roadbook parser, TSD time authority, KM PAL truth, verified GPS source, NaviPack compiler or Driver LIVE engine.

**Source method:** GitHub connector metadata; commit and upstream comparison; direct inspection of `src/index.js`, `control.js`, `plan.js`, `line.js`, `itinerary.js`, `formatter.js`, `osrm-v1.js`, `waypoint.js`, `geocoder-element.js`, `autocomplete.js`, `localization.js`, `mapbox.js`, and test files. Entire source tree indexed. No local clone/build of the third-party LRM repo; no browser integration benchmark. The indexed registry enumerates **38** independent source-level capabilities, not 38 functioning NaviPRO features.

## 1. Architecture reconstructed from code

```text
Official Roadbook + RouteRevision (immutable source order)
            |
            v
NaviPRO Page 2 Routing Lab -- review-only session state
    |       |             |
    |       +--- Waypoint UI / LRM Plan / geocoder
    |       +--- RouteLines & Alternatives
    |       +--- Itinerary / localizer / formatter
    |       +--- Events / error / request cancellation
    |
    +--- NaviPRO route candidate service (existing OSRMAdapter)
                |
                +--- OSRM graph + source data manifest + Lua profile digest
                |
                +--- full directed route geometry / legs / distance candidate
                            |
                    NaviPRO proposal/validation boundary
                            |
                    Authenticated Navigator Review
                            |
                    Confirmed RouteRevision → NaviPack
```

**Call graph derived from `src/index.js`:** `L.Routing.Control` is built from `Itinerary` + `Plan` + backend router (`OSRMv1` by default) + route display (`Line`), with `Waypoint`, `GeocoderElement`, `Autocomplete`, `Formatter` and localized instruction builder. The `L.Routing.Mapbox` implementation is a backend subclass, not a separate route authority.

## 2. Source component audit

| Source file | Verified responsibility | NaviPRO adoption | Boundary / caveat |
|---|---|---|---|
| [`src/control.js`](https://github.com/tjx578/leaflet-routing-machine-rally/blob/8dc939a314425684883dc6f016b3aa9d04c8b7ca/src/control.js) | Lifecycle; router injection; request cancellation; async request counts; auto-reroute; alternatives; map zoom; line/plan integration | Page 2 preview controller, async stale-result protection | `autoRoute`, drag reroute and `waypointMode='snap'` disabled on official source |
| [`src/plan.js`](https://github.com/tjx578/leaflet-routing-machine-rally/blob/8dc939a314425684883dc6f016b3aa9d04c8b7ca/src/plan.js) | Waypoint list, draggable marker, add/reverse, geocoder, line insertion | Candidate-only shaping-point editor | Never splice/reverse/mutate confirmed roadbook anchors |
| [`src/line.js`](https://github.com/tjx578/leaflet-routing-machine-rally/blob/8dc939a314425684883dc6f016b3aa9d04c8b7ca/src/line.js) | Styled routing line, missing-route connector, touched-segment event | Display candidate vs authoritative polyline; mark gaps visually | Dashed missing connector must NEVER be counted as navigable graph distance |
| [`src/itinerary.js`](https://github.com/tjx578/leaflet-routing-machine-rally/blob/8dc939a314425684883dc6f016b3aa9d04c8b7ca/src/itinerary.js) | Route summary, selectable alternatives, maneuver steps, UI collapse | Non-authoritative candidate instructions review | Do not replace official roadbook instructions |
| [`src/formatter.js`](https://github.com/tjx578/leaflet-routing-machine-rally/blob/8dc939a314425684883dc6f016b3aa9d04c8b7ca/src/formatter.js) | Distance / duration formatting | Display labels | Do not apply LRM display rounding to rally timing core |
| [`src/osrm-v1.js`](https://github.com/tjx578/leaflet-routing-machine-rally/blob/8dc939a314425684883dc6f016b3aa9d04c8b7ca/src/osrm-v1.js) | OSRM route request, hint caching, encoded polyline decode, turn instructions | Presentation adapter over existing NaviPRO OSRM service | Prefer existing server-side OSRM adapter, full GeoJSON and dataset+profile identity |
| [`src/geocoder-element.js`](https://github.com/tjx578/leaflet-routing-machine-rally/blob/8dc939a314425684883dc6f016b3aa9d04c8b7ca/src/geocoder-element.js) | Input / reverse geocode / fallback coordinates | Page 2 anchor candidate picker | Geocode centroid ≠ verified physical entrance |
| [`src/autocomplete.js`](https://github.com/tjx578/leaflet-routing-machine-rally/blob/8dc939a314425684883dc6f016b3aa9d04c8b7ca/src/autocomplete.js) | Autocomplete and keyboard selection | Reuse existing location-search contracts | Depend on authorized provider and independent evidence gate |
| [`src/localization.js`](https://github.com/tjx578/leaflet-routing-machine-rally/blob/8dc939a314425684883dc6f016b3aa9d04c8b7ca/src/localization.js) | UI translations | Localization interface | Indonesian translations and domain-specific rally terms require additional work |
| [`src/mapbox.js`](https://github.com/tjx578/leaflet-routing-machine-rally/blob/8dc939a314425684883dc6f016b3aa9d04c8b7ca/src/mapbox.js) | Provider-specific Mapbox Directions adapter | Abstract router interface | External terms, secrets, and request limits; never embed tokens in public UI |
| [`src/error-control.js`](https://github.com/tjx578/leaflet-routing-machine-rally/blob/8dc939a314425684883dc6f016b3aa9d04c8b7ca/src/error-control.js) | Route error presentation | Error/HOLD display | Errors do not alter existing confirmed revision |
| [`src/waypoint.js`](https://github.com/tjx578/leaflet-routing-machine-rally/blob/8dc939a314425684883dc6f016b3aa9d04c8b7ca/src/waypoint.js) | Waypoint latLng, label and options | Presentation DTO | Presentation waypoint ≠ RoadbookEvent / PhysicalAnchor |

### 2.1 Events and temporal consistency

`control.js` increments `_requestCount` and aborts pending requests; the latest request count prevents an out-of-order route response from replacing a newer one. **Adopt this pattern** for candidate preview. Server-side work must additionally bind every response to `route_revision_id`, `graph_dataset_id`, `profile_digest` and authorized session; client cancellations alone are not reliable security boundaries. The previous OSRM Frontend REA also discovered its `router_patches.js` and `route_throttle.js` for antimeridian handling, stale responses and burst backoff. Integrate these patterns in a shared frontend adapter rather than duplicating conflicting patches.

### 2.2 LRM official-anchor controls to disable

`Plan` permits add/delete, reverse and drag, including `dragNewWaypoint` from `linetouched`. `Control` can auto-reroute and use snapped coordinates to replace input waypoints. All are **incorrect when applied directly to immutable official rally source**. The Page 2 trusted-source view must use `addWaypoints=false`, `draggableWaypoints=false`, `reverseWaypoints=false`, `autoRoute=false`, `routeWhileDragging=false`, `waypointMode='connect'`; alternate route selection may remain a PREVIEW only. Shaping points are submitted through a **separate proposal resource** and cannot be inserted into `OfficialSourceEvent` sequence.

The UI switches are **defense in depth**, not access control. A caller could invoke `.spliceWaypoints()` or modify a JS object despite them. Therefore `python/src/navipro_rallyos/route/lrm_review.py` checks every proposal against a **trusted server-side snapshot** and rejects any attempt to modify the official order/revision/graph identity, add authority fields or perform an unapproved selection. It does not persist/approve proposals; production service must implement authentication and ACID revision transactions.

### 2.3 Presentation should preserve distinct distance/time domains

- `D_auth`: official target distance from roadbook; never computed by LRM.
- `D_graph_candidate`: distance returned by OSRM on candidate route, dependent on road graph and Lua routing profile.
- `D_odo`: tripmeter/recorded distance, separate from LRM.
- `D_geo`: geodesic diagnostic, separate from routable length.

Likewise, LRM summary duration from OSRM is **not** the authoritative Time Rally schedule; timing rules remain governed by event authority profile (`clock_scale`, rounding, sub-trayek start).

### 2.4 LRM-specific compatibility bugs/risk

- Fork's `src/osrm-v1.js` `_leftOrRight(d)` classifies a modifier without `left` as `Right`; the separately audited modern OSRM Frontend `src/router_patches.js` handles `straight` correctly. Do not copy old maneuver arrow logic into NaviPRO.
- Source version 3.3.0 vs OSRM Frontend dependency 3.2.12: test with real Leaflet DOM/map, alternative selection, geocoder, touch drag, abort and no-network behavior **before** any library upgrade.
- `npm test` in upstream 3.3.0 deliberately fails. The existence of Jasmine source tests does not mean modern Node/CI tests pass.
- Default demo routing/backend is not a production provider; Page 2 should connect to the self-hosted OSRM adapter with pinned graph data, while Driver LIVE remains offline and consumes NaviPack.
- LRM is a UI/plugin, not a multi-vehicle Time Rally routing solver. `Trip`/TSP from OSRM Backend remains excluded; no official waypoint reorder UI.
- SVG/polyline color distinctions and dashed missing route segments are visualization only; do not treat appearance as spatial compliance.

## 3. NaviPRO architecture mapping

| Component | Where | Imported/adopted concept | State |
|---|---|---|---|
| Roadbook IR | Page 1 | None (authority already owned by NaviPRO) | Existing design boundary |
| LRM Review Session | Page 2 | Source-ordered presentation of waypoints + alternatives | Pure JS prototype tested |
| Candidate shaping point | Page 2 | Click route line → separate proposal | JS/Python prototype tested |
| Candidate OSRM route | Page 2 | Existing OSRM adapter supplies ordered full geometry | Existing mock-provider tests |
| Itinerary display | Page 2 | Maneuver steps / alternative summary | OpenAPI contract only |
| Map Lab | Kepler | Display analytics and candidate comparisons | Earlier REA scaffold |
| Terrain Lab | Cesium | Contextual 3D terrain and geometry | Earlier REA scaffold |
| Field Survey | StreetComplete | Road/landmark evidence collection | Earlier REA prototype |
| Rally Agent | Page 3 | Tool call to session/candidate/shaping plan | Tool metadata generated only |
| Navigator authority | Review service | Explicit authenticated decisions and validation gates | Not implemented by LRM |
| Driver LIVE | Android | Confirmed NaviPack only | LRM not used |

## 4. OpenAPI and MCP integration

Only **five** new OpenAPI operations (rather than one per internal UI method) reduce MCP tool overload:

| Method / path | operationId | MCP | Semantic |
|---|---|---|---|
| `GET /routing-ui/lrm/capabilities` | `getLrmUiCapabilities` | `navipro.routing.ui.lrm.capabilities.get` | Read capability metadata |
| `POST /routing-ui/lrm/sessions/plan` | `planLrmReviewSession` | `navipro.routing.ui.lrm.session.plan` | Plan source-locked review |
| `POST /routing-ui/lrm/shaping-points/propose` | `proposeLrmShapingPoint` | `navipro.routing.ui.lrm.shaping.propose` | Non-authoritative proposal |
| `POST /routing-ui/lrm/itineraries/preview` | `previewLrmItinerary` | `navipro.routing.ui.lrm.itinerary.preview` | Read-only instructions |
| `POST /routing-ui/lrm/alternatives/preview` | `previewLrmAlternativeSelection` | **DISABLED / UI ONLY** | Local candidate selection |

No direct MCP tool for `waypoint.reorder`, `route.confirm`, `snap-to-authority`, `route.publish`, `driver.send` or `Trip`. Existing `navipro.location.search` is reused rather than adding a duplicate LRM geocoding tool. Tool generation is **registry-only**, not an operational MCP runtime.

## 5. Code added and verification

- `contracts/routing/lrm-capability-registry.yaml`: **38** source-indexed capabilities with precise file permalink, P0/P1/P2 and PREP/REVIEW-only flags.
- `docs/rea/LEAFLET-ROUTING-MACHINE-SOURCE-MANIFEST.yaml`: identity, upstream identical comparison, version, license and compatibility.
- `governance/lrm-routing-ui-policy.yaml`: safe options and action policy.
- `apps/routing-lab-web/src/lrm-rally-review.mjs`: immutable JS review snapshot, locked LRM option generation, candidate preview, separate shaping-point proposals, reject mutating events, normalized request payload.
- `python/src/navipro_rallyos/route/lrm_review.py`: server-side proposal validation requiring injected **trusted** source snapshot; never executes approval.
- `tests/contracts/test_lrm_rea.py` + `apps/routing-lab-web/test/lrm-rally-review.test.mjs`: cross-layer contract and safe state tests; unit-tested, not browser-tested.
- Unified OpenAPI aggregate + generated MCP registry are updated. Real HTTP/MCP endpoints, authentication and the Leaflet-rendered graphical Page 2 are **not implemented**.

## 6. Priority migration plan with exit criteria

**P0: route review correctness.** Build isolated LRM adapter in `apps/routing-lab-web` against a pinned compatible LRM, plug into existing NaviPRO OSRM route service, render ordered anchors and candidate geometry, show alternatives, retain last known view if provider errors, disable official mutations. Require true end-to-end test asserting source order, ID, hashes and `route_authority=false` survive browser interactions and backend requests.

**P1: precision review UX.** Mark dashed disconnected spans as HOLD, add shaping point proposals, reveal original vs snapped anchors, turn/leg coverage, confidence+provenance, graph identity; install localized itinerary; compare with Kepler/3D/Survey evidence. Capture audit receipts before human decision.

**P2: performance/mobile and upgrade.** Browser touchscreen/accessibility testing, version compatibility 3.2.12 vs 3.3.0, request throttling/retry, antimeridian, geocoder privacy, local tile and offline behavior, profiling big itineraries.

**Production exit criteria:** verified browser build; route backend against real Bali OSM graph; correct display of at least one real pinned sub-trayek; gap/NoRoute handling; approval boundary penetration tests; localization; test on mobile devices; no network requests in Driver LIVE; offline NaviPack tested; provenance and roadbook coverage validated. Until then `NOT_RACE_READY`.

## 7. License / code-reuse notes

This REA uses source **architecture and interfaces**, implementing a clean-room NaviPRO adapter (no upstream third-party source code embedded). Upstream source `LICENSE.md` and `package.json` state **ISC**, although GitHub repository metadata reports `NOASSERTION`. If the UI later bundles/copies upstream LRM, preserve the ISC license/copyright notice and check distribution of third-party icons/fonts/dependencies. More important than license is maintenance risk and the separate OSRM Frontend's pinned 3.2.12 dependency.

## Decision

**Adopt the LRM UX ideas** (route control, geocoder, alternatives, itinerary, waypoints, line touch, async request safety), **not its default route authority behavior**. NaviPRO's Page 2 remains a guarded RouteRevision review tool. Page 3 remains propose-only via OpenAPI→MCP. The confirmed Driver uses independent, validated offline NaviPack geometry.
