# NaviPRO RallyOS — Eight-source geospatial architecture reconciliation

**Status:** design map + prototype boundaries; full runtime parity not established.

| Source repository | Source role | NaviPRO target role | Current evidence |
|---|---|---|---|
| Kepler.gl mapas rally | Geospatial table/layer analytics | Kepler Map Lab | Registry/scaffold only |
| Cesium maps rally | Globe, terrain, imagery, 3D Tiles | Cesium Terrain Lab | Schema/geodesy prototype, web build unverified |
| StreetComplete rally maps | OSM road-attribute micro-survey | Field Survey evidence staging | Quest plan/SQLite prototype, mobile unbuilt |
| OSRM backend maps rally | Directed routing graph | Candidate route/trace matching | Mock-tested adapter; no running graph |
| OSRM frontend rally maps | Leaflet-based OSRM UI | Routing Lab host UX | State prototype, browser unbuilt |
| Leaflet Routing Machine rally | Waypoint controls, itinerary UX | Locked route review UI | JS/Python guard tested; DOM unbuilt |
| React Native Maps RallyOS | Android/iOS native map presentation | Optional Navigator/mobile research adapter | Standalone REA only; no repo integration/build |
| God's Eye View maps | 3D fusion, source health, scenes, imagery comparison | PREP/REVIEW Spatial Context Fusion on existing Cesium/Kepler | Source REA + Python policy prototype + OpenAPI contract |

## Authority rule

The only route truth flows from official sources into immutable RouteRevision and navigator-governed reviews. None of the eight codebases is authoritative for rally semantics by itself. Every geographic point/route candidate/scene/survey remains non-authoritative until authorized evidence workflow. No live cloud/AI dependency in Driver NaviPack. Environmental context cannot change official distance or timing.

## Integration recommendation

Do **not** adopt each upstream as its own app: build a common `MapProjectSnapshot` representation + authoritative `RouteRevision` refs; deploy Kepler and Cesium as separate analytic views with a single route/evidence gateway, OSRM as routing candidate backend, StreetComplete-inspired offline evidence capture, LRM interaction adapter for Page 2, and approved environmental source-health adapter from God's Eye View. React Native Maps remains a conditional mobile rendering experiment, not a replacement for the MapLibre-based Driver plan.

## Operational readiness

Contracts and prototypes are tested in isolation; no end-to-end online/offline spatial system, production REST/MCP, native driver build, real OSRM graph or authoritative terrain calibration is deployed. **NOT_RACE_READY**.
