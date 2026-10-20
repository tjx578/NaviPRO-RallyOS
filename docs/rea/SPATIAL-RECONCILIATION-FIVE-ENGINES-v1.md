# NaviPRO RallyOS — Five-engine geospatial reconciliation

Snapshot: 2026-10-20; design/contract status, not delivered application parity.

| Capability plane | Upstream source | NaviPRO target | Authority |
|---|---|---|---|
| Spatial analytics | Kepler.gl | Map Lab / visual analytics / filters | NONE |
| Terrain & 3D | CesiumJS | Terrain Lab / height evidence proposals | NONE |
| Field surveys | StreetComplete | Survey questions / observations / staging | SURVEY_PROPOSAL_ONLY |
| Directed graph routing | OSRM Backend | Graph Provider / routing, snap, table, match | ROUTE_CANDIDATE_ONLY |
| Routing review UX | OSRM Frontend | Routing Lab locked source order and alternatives | NONE |
| Official Time Rally | NaviPRO own canonical core | Source order / route revision / timing / validation | NAVIGATOR_AUTHORITY_ONLY |
| Driver | NaviPRO own Android package | Confirmed offline NaviPack | CONSUMER_ONLY |

### Read/write lines

1. Page 1 owns canonical roadbook and event timing authoritative inputs; none of these five providers can edit it.
2. Page 2 consumes graph candidates, UI overlays, survey/evidence and human confirmations via authenticated NavaPRO authority services.
3. Page 3 uses generated tools for PREP/REVIEW read/plan/propose; a generated tool registry does not itself serve MCP.
4. `RouteRevision.CONFIRMED` immutable; analytic layer selection, OSRM alternatives, matched tracks, and Kepler/Cesium scene changes are separate derived `MapProjectSnapshot` / `ReviewSession` revisions.
5. `NaviPack` contains confirmed route geometry, cues and timing; LIVE driver loop does not access OSRM/Kepler/Cesium/StreetComplete remote APIs.

### Full chain

Official roadbook → ordered source events → candidate physical anchors (StreetComplete survey & OSM evidence) → locally versioned OSRM directed graph → ordered route candidates → NaviPRO directed-edge coverage/residual gates → navigator-confirmed RouteRevision → versioned NaviPack → offline driver.

Parallel visualization: Kepler filters/compares route/event/track datasets; Cesium shows terrain, imagery, 3D context; OSRM Frontend patterns power candidate preview. None of these can mutate confirmed route without a new authoritative revision.

### Graph asset/data consistency rules

- Pin OSM source snapshot and explicit graph build digest, Lua profile digest, CH/MLD version; record OSRM `data_version` where available.
- Reprocessing after new StreetComplete/OSM tags must create a new graph manifest; never silently mutate existing analyses.
- Preserve `D_auth`, `D_graph_candidate`, `D_odo`, and `D_geo` as separate domains.
- `Trip` and official-source drag reordering are forbidden. `Table` fallback_speed is forbidden for compliance.
- Route matching confidence and road classifications are not evidence promotions.

### Work remaining

Production API, actual MCP server, dataset ingestion, CH/MLD build, browser application, mobile cockpit, field tests and gate authority are not implemented by REA documents or prototype unit tests.
