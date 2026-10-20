# NaviPRO Multi-Spatial System: Kepler + Cesium + StreetComplete REA

## Decision record SPATIAL-ADR-003

Three REA source stacks are complementary **not interchangeable**:

```text
 OFFICIAL ROADBOOK/BRIEFING
            |
   NaviPRO Rally/Route/Timing Core ------> immutable confirmed NaviPack -> DRIVER OFFLINE
            ^
            | reviewed evidence only
            |
      Navigator Authority Gate
            ^
            |
    Local Evidence Staging
            ^
            |
     +------+-----------------------------+
     |                   |                |
     v                   v                v
StreetComplete-style    Kepler Map Lab   Cesium Terrain Lab
Field Survey           2D analytics      3D context
(offline quests)       datasets/maps     terrain/imagery
     |                   |                |
     +------------ PAGE 3 AGENT ----------+
                 (propose only)
```

## Ownership matrix

| Data/behavior | Source of truth | May reference |
|---|---|---|
| Official route order | Official source/roadbook version | Survey risk flags |
| Confirmed route geometry | Immutable RouteRevision with validation receipts | OSM/Kepler/Cesium candidate geometry |
| GPS observation | Recorded survey/track evidence with precision and consent | Kepler trip and Cesium replay |
| Human field answer | SurveyObservation audit receipt | OSM feature identifier and source version |
| Public OSM tags | OSM snapshot/external provider | Field survey as separate independent observation |
| Road signage | Dated ground survey evidence candidate | Legal speed sign distinct from mean rally speed |
| Time Rally clock | Timing authority profile | Road observation risk warnings |
| 3D height | Terrain source/vertical datum | Not authoritative distance/road graph |
| Map styling | Kepler MapProjectSnapshot | Not RouteRevision |
| Driver runtime | Confirmed NaviPack only | No MCP/HTTP/survey |

## Sequence for uncertain directed road in Sub C

1. Page 2 validation detects unresolved one-way or road access restriction on prospective edge.
2. Page 3 agent retrieves OSMap snapshot and asks Field Survey to propose *targeted* inspection, not blindly mark road one-way.
3. Surveyor records a stopped field observation with OSM way/version, location accuracy, evidence hash, time and answer.
4. Observation stays in local outbox, syncs to NaviPRO staging when permitted.
5. Server checks OSM element version against current snapshot. Mismatch -> CONFLICT, unknown -> HOLD, same -> STAGED_REVIEW.
6. Navigator examines conflicting evidence and adopts/denies an explicit evidence decision.
7. If geometry interpretation changes, propose NEW RouteRevision, rerun validation, timing and coverage-binding gates. Source order remains unchanged.
8. Only reviewed, confirmed revisions can be compiled into Driver NaviPack.

## Query and visibility

MCP is not the execution engine. `navipro.survey.tasks.plan`, `navipro.survey.gaps.assess`, `navipro.survey.conflicts.assess` are agent-side analytical contracts. Real field capture and publication are human-only endpoints behind authorization. Kepler is allowed to read staging layers scoped by event/role; Cesium can overlay reviewed evidence/route for 3D spatial analysis. No tool is admitted in LIVE.

## License/compliance conflict

Kepler REA target is MIT ecosystem; CesiumJS Apache-2.0; StreetComplete GPL-3.0-only. This draft integrates **ideas/architecture**, not StreetComplete GPL implementation files. OSM data has independent ODbL conditions. Before directly importing external code, perform dependency/license and OSM data processing review; keep source notice for any reused open-source components, respect provider contracts.

## Verification honesty

- Field Survey Python deterministic prototype: unit tested (not remote runtime).
- Android Field Survey: README scaffold only, not build tested.
- OpenAPI 12 survey operations: structural contract only.
- Generated MCP: tool names registry only, not deployed endpoints.
- StreetComplete full feature parity: NOT_MEASURED/NOT_CLAIMED.
- Confirmed NaviPRO RallyOS race readiness: NOT_RACE_READY.
