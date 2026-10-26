# Agent No. 5 Divisi 4 — Capability-Aware Location Intelligence v4.9 (PROPOSED)

STATUS: SPEC AND CLEAN-ROOM TESTS ONLY. No live production providers or field DB.

## Scope and five-stage reasoning
1. SOURCE/MODE: Agent 1 sets PREP/REVIEW; Agent 2 provides exact ordered roadbook text, sub/occurrence, original names and source revision. No released organizer Master, participant historical KML, or result card may enter PREP or blind Trayek 2.
2. DISCOVER: read separately reviewed prior location DB entries first, then check availability of licensed OSM/Overpass, geocoder, government admin data and other providers. Catalog availability is not a successful API call. Missing provider is UNAVAILABLE and cannot create fictional coordinates.
3. RECOGNIZE: record three separate roles: POI_REFERENCE, PHYSICAL_LOCATION, ROUTE_ACCESS_POINT; all may be NULL. Store source provider, date, accuracy, licensing, named identity evidence, approach and access constraints. God's Eye imagery / Cesium 3D / Kepler layers are context tools, not proof of physical identity. Dated Street View/field photographs support signed-road arrows only after real review.
4. CONSTRAIN: Agent 4 supplies candidate OSRM/Valhalla directed graph corridors (if real service available), legal access/heading/visit identity and source-ordered CP. Repeated Gilimanuk signs require two different physical decisions, possibly not adjacent; no STRAIGHT default. KM PAL is lossless raw text; origin/datum/reference route and direction must be independently established before distance residual check; no universal reverse inequality or exclusion of village roads.
5. EVIDENCE/HANDOFF: Agent 5 outputs source-linked alternatives, unknown locations, request queues, and evidence, not QG PASS. Agent 3 derives CP second targets only after reviewed distance binding; Agent 7 emits preview cues only. Independent validator owns QG-07/08; Agent 9 trusted journal service owns actual receipts. Location or source changes invalidate downstream route/time/cue review.

## Verified repo technology states, 2026-10-26
- OSM/Overpass/geocoder: contract only, no working Agent5 service.
- OSRM: adapter mock-tested; no real routing graph. Valhalla: assessed separately, no runtime parity.
- God's Eye: registry and context prototype; live imagery integration absent. Street View provider: not connected.
- Kepler Map Lab / Cesium Terrain Lab: visual scaffolds, not verified live.
- Leaflet Routing Machine: read-only route-review policy prototype, no working browser UI.
- React Native Maps: source audit only; Android renderer not integrated.
- StreetComplete-inspired survey: prototype planner/outbox only, no Android APK or production secure server; GPL source not copied.
- Private location database: local SQLite v2 proposal not deployed.
- MCP: generated registry, not running server. Independent validator and receipt-issuing persistence runtime: not implemented.

## Transferable Trayek 1 observations, not answer leakage
Eight legacy candidate CSVs are NOT original official OCR and NOT truly frozen before the 2026 race. 60 source rows produce 61 occurrences after splitting two Gilimanuk sign decisions. 32 have no coordinate, 29 only old POI candidates, 10 marked VERIFIED without required receipts. In POST_EVENT diagnostic only, old candidate pins within 30m of historical KML are 14/29 while released organizer Master Pos near KML are 18/18. This is proximity, not verified route/turn compliance.

Learn general constraints: START differs from Zero Trip; signs counted by physical decision; POI center not roadside access; KM PAL datum cannot be guessed; locality/name dedup requires admin codes and visit IDs. Never put Master coordinates or historical route into future PREP solving. Prior reviewed real-world landmark knowledge may be reused as a normal database entry, never as secret organizer control/time answer.

No generative Agent5 in Driver LIVE. A separate deterministic navigator-triggered field recorder cannot claim a remote save until actual storage confirms. All Agent5 outputs remain proposals and Driver HOLD until independent gates and authorized review.
