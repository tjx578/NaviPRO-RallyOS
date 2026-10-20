# REA-03 · StreetComplete_rally-maps → NaviPRO RallyOS Field Survey Intelligence

**Audit date:** 2026-10-20 · **status:** SOURCE-INSPECTED + CONTRACT-IMPLEMENTED + DETERMINISTIC-SURVEY-PROTOTYPE; **not** Android/runtime parity or race ready.

## 0. Executive decision

**Source observed:** `https://github.com/tjx578/StreetComplete_rally-maps`, branch `master`, SHA `e6b04da98028d34c1e49625edd7095f7008106a6` (2026-09-10), license **GPL-3.0-only**, direct fork of `streetcomplete/StreetComplete`. Comparison against upstream `5ed9bcd0685e81f7a00a334b0bebf5b8f91b1e8c` (2026-10-19) showed **462 upstream commits** beyond the fork. This is an upstream snapshot, not a separately demonstrated rally-specific implementation. Treat precise claims about fork-local features conservatively.

**Architectural conclusion:** StreetComplete provides a high-quality *human-in-the-loop field-survey pattern* for filling missing OpenStreetMap attributes via atomic quests, spatial overlays, offline download/edit/upload, and conflict-aware edit history. It is **neither a rally routing core nor a canonical roadbook authority**. Adopt its **capabilities and workflow patterns** into independent NaviPRO code, do not casually transplant GPL source files into the NaviPRO monorepo. Adoption of GPL code could impose GPL obligations; obtain proper license analysis before any direct code redistribution or linking.

## 1. Grounded source audit by component

| Source path in fork | Observed implementation behavior | Target in NaviPRO |
|---|---|---|
| `README.md` | Survey questions on map, offline OSM contributions, user account changesets | Human field survey PREP/REVIEW |
| `QUEST_GUIDELINES.md` | Atomic, answerable, low false-positive quests; avoid inaccessible/private places | Survey quality rules, candidate thresholds, safe collection |
| `app/src/commonMain/.../data/quest/QuestType.kt` | Quest card interface: help, hint images, quest-specific UI | `SurveyTask` / form registry |
| `.../data/osm/osmquests/OsmFilterQuestType.kt` | OSM filter-driven applicable elements | Deterministic *curated* task planner |
| `.../quests/QuestTypesRegistry.kt` | Many quest types, including road attributes | Event-specific rally-relevant quest catalog |
| `.../quests/surface/AddRoadSurface.kt` | Surface question using highway type, missing/old surface tags, access conditions | Surface evidence task |
| `.../quests/smoothness/AddRoadSmoothness.kt` | Smoothness question only for eligible surfaces, stale/missing tags | Roughness and handling context, not official speed |
| `.../quests/oneway/AddOneway.kt` | Narrow-road heuristic; topology connectivity at endpoints | Directed routing candidate, MUST validate geometry and sign |
| `.../quests/max_speed/AddMaxSpeed.kt` | Legal speed-limit sign question with exclusion filters | Speed-limit attribute, NOT Time Rally target speed |
| `.../overlays/OverlaysRegistry.kt` | Ten overlay implementations mapped to stable ordinals | Thematic overlay layers in Map Lab & Field Survey |
| `.../data/download/Downloader.kt` | Concurrent downloads of notes, map data, basemap tiles; freshness tracking | Offline area preload and completeness receipt |
| `.../data/quest/AutoSyncer.kt` | Network preference/lifecycle/GPS-aware download+upload | Sync policy, **never in Driver LIVE** |
| `.../data/Database.kt` | Platform-neutral CRUD/transaction interface | Durable, encrypted per-device outbox |
| `.../data/osm/edits/ElementEdit.kt` | Source, timestamp, sync status, near-location field | Immutable observation/provenance receipt |
| `.../data/osm/edits/ElementEditsControllerImpl.kt` | Ordered queued edits, sync markings, undo or revert | Offline staging queue, correction lifecycle |
| `.../data/osm/mapdata/MapDataApiClientImpl.kt` | OSM API, source versions, HTTP 409/412/404 conflict handling | Compare OSM version, quarantine conflicts |
| `.../data/upload/Uploader.kt` | Serializes element/note upload, failure/dirty-area invalidation | Idempotent NaviPRO staging transport, not OSM upload |
| `.../data/osmnotes/PhotoServiceApiClientImpl.kt` | Note-associated photo upload | Restricted evidence attachment hash + privacy controls |
| `.../data/osmtracks/` | GPX/trace upload | Field recce GPS evidence into Kepler/Cesium replay |
| `.../data/visiblequests/TeamModeQuestFilterSource.kt` | Quest team visibility/assignment concept | Survey team task partitioning |
| `.../data/osm/mapdata/MapDataRepository.kt` | Node, way, relation + topology refs | OSM provider references, explicitly non-authoritative |
| `.../data/elementfilter/` | Declarative expressions for selecting OSM elements | Reviewed deterministic predicate registry |

Source repo is a Kotlin/Compose cross-platform codebase with `androidApp`, `app` common/Android/iOS source sets and an `iosApp` folder. **iOS directory existence does not imply a validated iOS production build.** `OVERLAY_GUIDELINES.md` limits overlays to network/contextual attribute views with one aspect at a time. `QUEST_GUIDELINES.md` describes quests primarily as tag editing of existing elements, not unrestricted new geometry drafting. This is important: StreetComplete alone cannot replace Page 2 NaviPRO route graph editing.

## 2. Capability inventory

`contracts/spatial/streetcomplete-capability-registry.yaml` and [60-capability matrix](STREETCOMPLETE-CAPABILITY-MATRIX.md) contain **60 source-path-associated capability mappings**, grouped under:

- **Quest Engine:** atomic task, eligibility, stable registry, road surface, smoothness, one-way, restrictions, lanes, width, traffic calming, signs, bridge, construction.
- **Overlays:** ten thematic overlay groups, for targeted analysis rather than indiscriminate feature overload.
- **Offline:** local data, area download, tile cache, network awareness, autosync, preload.
- **Edits and change management:** record, queue, history, undo/reversion, version conflict, staged upload.
- **Field context:** notes/photo/GPX, task assignment, presets, map context actions.
- **Interoperability:** OSM node/way/relation, filter parser, localization, Kotlin architecture path.

**Important:** 60 is the number of curated *mapped capabilities in our audit*, **not** the count of all upstream quest types, nor a claim that 60 features are deployed in NaviPRO.

## 3. NaviPRO field-survey model

```text
Confirmed RouteRevision (READ ONLY)
   |
   v
Evidence Gap Finder + OSM Snapshot (not authority)
   |
   v
SurveyTaskPlan (strict applicability + priorities)
   |
   v
Human surveyor on safe accessible ground
   |
   +-- answer one question
   +-- observation time and GPS accuracy
   +-- optional photo/document hash
   +-- source OSM element id/version
   |
   v
Offline SQLite Outbox (PENDING_SYNC)
   |
   v
Authenticated, idempotent NaviPRO Staging Sync
   |
   +-- current OSM version missing -> HOLD
   +-- version changed -> CONFLICT
   +-- version equal -> STAGED_REVIEW
   |
   v
Evidence Assessment (Page 3 agent proposes/explains)
   |
   v
Navigator Authority Review (separate human control)
   |
   v
LocationDecision / New RouteRevision proposal
   |
   v
Original route immutable; rerun directed route + timing gates
```

Field observations have statuses, not canonical release states. A match of OSM version is NOT proof that field observation is correct. A staging ACK is NOT equivalent to `VERIFIED`. Only a separately authenticated navigator workflow can promote evidence; changing a confirmed route creates a **new** revision and invalidates dependent package/timing receipts.

### Canonical entities

`SurveyTask` (`task_id`, `quest_type`, `question`, `osm_element_type`, `osm_element_id`, `osm_version`, `source_snapshot_id`, `lat_e7`, `lon_e7`, `route_revision_id`, `priority`, `status`, `human_survey_required`) ; `SurveyObservation` (`observation_id`, `task_id`, `answer`, `actor_id`, `observed_at` with timezone, `gps_accuracy_m`, `photo_sha256`, `source_osm_version`, `route_revision_id`, `status`); `SurveySyncReceipt` (batch/source hashes, staging ack, conflict status); `EvidenceDecision` (navigator principal, scope, provenance, reason, audit signature); `SurveyCampaign` (event, target sub, corridor, presurvey completeness, coverage and assignments). Consider adding `location_accuracy_source`, `consent`, `photo_exif_removed`, `observed_direction`, `sensor_method` before use in the field.

## 4. Crucial street-survey reasoning rules

1. **One-way:** do NOT ask every road lacking `oneway`. StreetComplete itself checks narrow width, lane count, and both-end connectivity. NaviPRO's proof-of-concept task generator uses those stricter requirements; directional road edges need additional survey verification before routing.
2. **Surface/smoothness:** if surface is unknown, first request surface. Smoothness of a road should not be assumed from visual satellite imagery.
3. **Speed:** OSM `maxspeed` is **legal posted maximum** and never substitutes for Time Rally's prescribed mean speed or authority profile.
4. **Bridge/tunnel/barrier/access:** no blanket assumptions from missing tags. Only create follow-up tasks when a prior signal indicates likely need for survey (`candidate_flags`).
5. **Roadbook:** source event order is immutable. Local survey observations can flag a questionable edge or waypoint; they do not authorize reordering or automatically rerouting.
6. **KM PAL:** use survey photos, signage readings, odometer context and corridor evidence as candidates; distance from an OSM geodesic is not an authoritative KM PAL measurement.
7. **No false-precision:** timestamp, accuracy, source version, photo-hash or explicit missing flags; no automatically promoted VERIFIED status.
8. **Survey safety:** use the survey UI only when stationary, at safely accessible/public places; no restricted roads/private areas or interacting with it while driving.

## 5. Reconciliation with Kepler, Cesium and NaviPRO Core

| Platform | Owns | Does NOT own |
|---|---|---|
| **StreetComplete-inspired Field Survey** | Field observations, offline queues, road attribute tasks | Official route authority or public OSM publishing |
| **Kepler Map Lab** | Attribute QA, filter, heatmap, route comparison, large dataset map | Human field truth, release authority |
| **Cesium Terrain Lab** | Elevation context, WGS84/3D, terrain and imagery checks | Road graph compliance, legal sign observations |
| **NaviPRO Rally Agent Page 3** | Gap detection, task planning, evidence comparison and explanation | Invent human measurements, verify itself, send to LIVE |
| **NaviPRO Route/Timing Core** | Canonical route/timing/validation, revisions, gate receipts | Treat an OSM tag/photograph as unchallengeable authority |
| **Navigator human** | Approved evidence decisions, route confirmation, release | Unchecked automatic bypass of gates |
| **Driver LIVE** | Read confirmed offline NaviPack | Network survey, MCP, exploratory editing |

### Page mapping

- **Page 1:** roadbook intake creates route/landmark evidence needs; official timing is unaffected by unsurveyed data except risk flags.
- **Page 2:** route overlay shows survey coverage, missing attributes, conflicts, evidence provenance; navigator reviews and issues a new route revision only when justified.
- **Page 3:** Page 3 asks e.g. “Tampilkan jalan Sub C yang surface atau oneway belum jelas,” calls gap planning/assessment MCP, returns proposals for human field survey.
- **Field Survey Android:** separate companion PREP/REVIEW app for safe stationery survey; intentionally not an extension of Driver LIVE.
- **Kepler/Cesium:** can ingest *reviewed observation layers* and track for replay but cannot mutate confirmed revision.

## 6. OpenAPI + MCP contract additions

This change adds 12 OpenAPI operations under `/survey/`:

| Method | Endpoint | MCP? | Authority |
|---|---|---|---|
| GET | `/survey/capabilities` | yes | read |
| POST | `/survey/tasks/plan` | yes | agent propose |
| GET | `/survey/tasks/{taskId}` | yes | read |
| POST | `/survey/gaps/route` | yes | agent propose |
| POST | `/survey/observations` | **no** | human surveyor |
| GET | `/survey/observations/{observationId}` | yes | read (role-filter required) |
| POST | `/survey/observations/assess` | yes | agent assess only |
| POST | `/survey/conflicts/assess` | yes | read/assess |
| POST | `/survey/sync/plan` | yes | propose only |
| POST | `/survey/sync/commit` | **no** | human/client authenticated |
| POST | `/survey/overlays/plan` | yes | propose only |
| POST | `/survey/decisions/{observationId}` | **no** | navigator-only |

**Endpoints are contract definitions, not deployed services.** The MCP tool registry only describes tool names, not a runnable Streamable HTTP MCP server.

## 7. Actual prototype code delivered

- `python/src/navipro_rallyos/survey/core.py`: deterministic task planner and source-version conflict assessment; preconditions enforce conservative quest eligibility, privacy-related access exclusions, valid numeric E7 positions, stable IDs and PREP mode.
- `python/src/navipro_rallyos/survey/queue.py`: SQLite outbox, idempotent observation enqueue, collision detection, `PENDING_SYNC` -> `STAGED_REVIEW`/`CONFLICT`/`HOLD` by source-version receipt, no direct OSM writes or VERIFIED state.
- `contracts/jsonschema/field-survey-observation.schema.json`: strongly typed, mode PREP/REVIEW only, `route_authority=false`.
- `governance/streetcomplete-field-survey-policy.yaml`: agent limitations, privacy, data/provenance requirements, OSM licensing and LIVE denial.
- `tests/contracts/test_streetcomplete_rea.py`: reproducible contract + unit tests.
- `apps/field-survey-android/README.md`: Kotlin/Android companion-app design, **not** executable APK.

Prototypes deliberately do not implement HTTP endpoints, field photo upload, authentication, cryptographic signing, secure at-rest encryption, GPS capture on device or external OSM publishing. Therefore they are *not deployable production services* and cannot claim parity with StreetComplete.

## 8. Licensing, safety and data rights

- **Source code:** StreetComplete is **GPL-3.0-only**, unlike MIT-licensed Kepler and Apache-2.0 Cesium. NaviPRO uses conceptual patterns and independently written code; do not import source wholesale without legal review of redistribution/linking obligations.
- **Map data:** OpenStreetMap data is separately covered by ODbL; source attribution, derivative database obligations and tile provider terms may apply. A GPL code license is not permission to republish OSM-derived data without complying with ODbL.
- **Data protection:** GPS route traces and geotagged photographs can reveal sensitive patterns; use minimum viable retention, authenticated access, consent, stripping unnecessary EXIF, and encryption. Do not auto-upload a private trace publicly.
- **Physical operation:** survey only from safe publicly accessible places while stopped; no interactive task completion while driving.
- **Authority:** never expose `publish_osm_changeset`, `promote_location_verified`, `confirm_route`, `publish_navipack`, `override_gate` to agent.

## 9. Acceptance plan: practical implementation not capability theater

### P0 — Verified MVP
1. Curated rule registry with `osm_version`, `_snapshot_hash`, source bounds; false-positive regression fixtures for private roads/oneway/narrowness.
2. Android Compose stationary survey UI and safe permissions, no data leakage to Driver.
3. Durable device outbox with encryption/transaction/retry/duplicate collision tests.
4. Authentication + authorization + idempotent staging REST service + actual MCP runtime authorization.
5. OSM source-version conflict quarantine and explicit Navigator Review UI.
6. Kepler overlays show unanswered/conflicted road attributes on sub-trayek, not unsourced guesses.

### P1 — Expert evidence operations
1. KM PAL inspection form with independently measured observations and map corridor context.
2. Survey campaign assignment, completion/coverage metrics and anti-duplicate team partitions.
3. Location candidate correlation across local OSM, photos, GNSS and 3D Cesium context with uncertainty tracking.
4. Source-verified tags/warnings mapped onto directed graph as *candidate* restrictions; no mutation of confirmed routes.
5. OSM data replication/version refresh, QA and provenance validation; optional public OSM edit workflow only with license, policy and explicit user intent.

### P2 — Advanced
1. Structured vision-assisted review of survey photo content with explicit uncertain candidate output.
2. Advanced change impact analysis comparing surveyed road conditions to stored offline graph revisions.
3. Offline terrain/visibility cross-check from Cesium and time-stamped GPS 3D replay.
4. Multiplatform port only after Android and legal requirements are satisfied.

### Acceptance gates
- No survey module reachable from Driver LIVE.
- No unreviewed survey observation can become VERIFIED or modify a confirmed route.
- Conflicts are quarantined and shown with before/after source versions.
- Offline queue handles duplicate deliveries, version changes, restarts and missing timestamps.
- Road attribute tasks are generated only when predicates are justified; no blanket questions on all segments.
- Field GPS/media privacy controls and offline package attribution tests pass.
- At least one real test corridor with ground-truth field inspection and coverage metrics validated by navigator.

## 10. Final REA decision

**Adopt as separate PREP/REVIEW module** under `apps/field-survey-android` + `python/.../survey` + `/survey/*` contract. **Do not fork the whole StreetComplete application into NaviPRO Core.** Keep Kepler for desk-based 2D analyses, Cesium for terrain/3D, StreetComplete-style UX for human field evidence, and deterministic NaviPRO authority core for route/timing/release. Source/parity boundary must remain honest and measurable.
