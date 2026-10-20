# StreetComplete → NaviPRO: 60-Capability Traceability Matrix

**Interpretation:** MAPPED_NOT_PARITY_VERIFIED = inspected source family and proposed target; **not implemented parity**. Source paths are fork-relative, and some entries point to audited directory families rather than fully audited individual source files.

Source: `tjx578/StreetComplete_rally-maps` · SHA `e6b04da98028d34c1e49625edd7095f7008106a6` · GPL-3.0-only.

## Coverage by domain

| Domain | Entries |
|---|---:|
| EDIT | 8 |
| FIELD | 8 |
| INTEROPERABILITY | 6 |
| OFFLINE | 7 |
| OVERLAY | 11 |
| QUEST | 20 |

**Priority counts:** {'P0': 29, 'P1': 23, 'P2': 8}.

## Capability-by-capability mapping

| # | Capability ID | Proposed NaviPRO function | Priority | Source path |
|---:|---|---|---|---|
| 1 | `SC_ATOMIC_QUEST` | atomic survey question/card | P0 | `app/src/commonMain/kotlin/de/westnordost/streetcomplete/data/quest/QuestType.kt` |
| 2 | `SC_OSM_ATTRIBUTE_FILTER` | missing-tag based task planning | P0 | `app/src/commonMain/kotlin/de/westnordost/streetcomplete/data/osm/osmquests/OsmFilterQuestType.kt` |
| 3 | `SC_QUEST_REGISTRY` | registry with stable quest IDs | P0 | `app/src/commonMain/kotlin/de/westnordost/streetcomplete/quests/QuestTypesRegistry.kt` |
| 4 | `SC_ROAD_SURFACE` | surface evidence | P0 | `app/src/commonMain/kotlin/de/westnordost/streetcomplete/quests/surface/AddRoadSurface.kt` |
| 5 | `SC_ROAD_SMOOTHNESS` | road passability context | P0 | `app/src/commonMain/kotlin/de/westnordost/streetcomplete/quests/smoothness/AddRoadSmoothness.kt` |
| 6 | `SC_ONEWAY` | directional restrictions candidate | P0 | `app/src/commonMain/kotlin/de/westnordost/streetcomplete/quests/oneway/AddOneway.kt` |
| 7 | `SC_MAX_SPEED` | posted legal speed only | P1 | `app/src/commonMain/kotlin/de/westnordost/streetcomplete/quests/max_speed/AddMaxSpeed.kt` |
| 8 | `SC_ROAD_NAME` | landmark street names | P0 | `app/src/commonMain/kotlin/de/westnordost/streetcomplete/quests/road_name/AddRoadName.kt` |
| 9 | `SC_LANES` | lane count | P1 | `app/src/commonMain/kotlin/de/westnordost/streetcomplete/quests/lanes` |
| 10 | `SC_LANE_MARKINGS` | road markings | P1 | `app/src/commonMain/kotlin/de/westnordost/streetcomplete/quests/lane_markings` |
| 11 | `SC_WIDTH` | road width | P1 | `app/src/commonMain/kotlin/de/westnordost/streetcomplete/quests/width` |
| 12 | `SC_BARRIER` | barrier candidate | P0 | `app/src/commonMain/kotlin/de/westnordost/streetcomplete/quests/barrier_type` |
| 13 | `SC_CROSSING` | crossing metadata | P1 | `app/src/commonMain/kotlin/de/westnordost/streetcomplete/quests/crossing` |
| 14 | `SC_TRAFFIC_CALMING` | traffic calming candidate | P1 | `app/src/commonMain/kotlin/de/westnordost/streetcomplete/quests/traffic_calming_type` |
| 15 | `SC_CONSTRUCTION` | temporary topology risk | P0 | `app/src/commonMain/kotlin/de/westnordost/streetcomplete/quests/construction` |
| 16 | `SC_BRIDGE_STRUCTURE` | bridge identification | P1 | `app/src/commonMain/kotlin/de/westnordost/streetcomplete/quests/bridge_structure` |
| 17 | `SC_LIGHTING` | lighting observations | P2 | `app/src/commonMain/kotlin/de/westnordost/streetcomplete/quests/way_lit` |
| 18 | `SC_SIGNBOARD` | roadside signs context | P1 | `app/src/commonMain/kotlin/de/westnordost/streetcomplete/quests/board_name` |
| 19 | `SC_OPENING_HOURS_SIGNED` | information-board observation | P2 | `app/src/commonMain/kotlin/de/westnordost/streetcomplete/quests/opening_hours_signed` |
| 20 | `SC_ROAD_REF` | road access reference | P1 | `app/src/commonMain/kotlin/de/westnordost/streetcomplete/quests/access_point_ref` |
| 21 | `SC_OVERLAY_REGISTRY` | thematic overlay menu | P0 | `app/src/commonMain/kotlin/de/westnordost/streetcomplete/overlays/OverlaysRegistry.kt` |
| 22 | `SC_SURFACE_OVERLAY` | surface continuity map | P0 | `app/src/commonMain/kotlin/de/westnordost/streetcomplete/overlays/surface` |
| 23 | `SC_LIGHTING_OVERLAY` | lighting thematic layer | P2 | `app/src/commonMain/kotlin/de/westnordost/streetcomplete/overlays/way_lit` |
| 24 | `SC_SIDEWALK_OVERLAY` | sidewalk context | P2 | `app/src/commonMain/kotlin/de/westnordost/streetcomplete/overlays/sidewalk` |
| 25 | `SC_CYCLEWAY_OVERLAY` | cycleway context | P2 | `app/src/commonMain/kotlin/de/westnordost/streetcomplete/overlays/cycleway` |
| 26 | `SC_PARKING_OVERLAY` | parking/access context | P2 | `app/src/commonMain/kotlin/de/westnordost/streetcomplete/overlays/street_parking` |
| 27 | `SC_ADDRESS_OVERLAY` | address references | P1 | `app/src/commonMain/kotlin/de/westnordost/streetcomplete/overlays/address` |
| 28 | `SC_PLACES_OVERLAY` | POI landmark reference | P0 | `app/src/commonMain/kotlin/de/westnordost/streetcomplete/overlays/places` |
| 29 | `SC_BUILDINGS_OVERLAY` | building landmarks | P1 | `app/src/commonMain/kotlin/de/westnordost/streetcomplete/overlays/buildings` |
| 30 | `SC_THINGS_OVERLAY` | infrastructure references | P1 | `app/src/commonMain/kotlin/de/westnordost/streetcomplete/overlays/things` |
| 31 | `SC_MTB_SCALE_OVERLAY` | track steepness context (non motor use) | P2 | `app/src/commonMain/kotlin/de/westnordost/streetcomplete/overlays/mtb_scale` |
| 32 | `SC_TILE_AREA_DOWNLOAD` | corridor offline area | P0 | `app/src/commonMain/kotlin/de/westnordost/streetcomplete/data/download/DownloadController.kt` |
| 33 | `SC_DOWNLOAD_ORCHESTRATION` | map+notes+mapdata acquisition | P0 | `app/src/commonMain/kotlin/de/westnordost/streetcomplete/data/download/Downloader.kt` |
| 34 | `SC_DOWNLOAD_STRATEGY` | network-aware scheduled download | P1 | `app/src/commonMain/kotlin/de/westnordost/streetcomplete/data/download/strategy` |
| 35 | `SC_MAP_TILE_CACHE` | vector basemap cache | P0 | `app/src/commonMain/kotlin/de/westnordost/streetcomplete/data/maptiles` |
| 36 | `SC_PRELOADER` | initial data preload | P1 | `app/src/commonMain/kotlin/de/westnordost/streetcomplete/data/Preloader.kt` |
| 37 | `SC_AUTOSYNC` | network and GPS-aware sync policy | P0 | `app/src/commonMain/kotlin/de/westnordost/streetcomplete/data/quest/AutoSyncer.kt` |
| 38 | `SC_PERSISTENCE` | durable SQLite observations | P0 | `app/src/commonMain/kotlin/de/westnordost/streetcomplete/data/Database.kt` |
| 39 | `SC_LOCAL_EDIT` | audit observation provenance | P0 | `app/src/commonMain/kotlin/de/westnordost/streetcomplete/data/osm/edits/ElementEdit.kt` |
| 40 | `SC_UNDO` | correction/retraction events | P1 | `app/src/commonMain/kotlin/de/westnordost/streetcomplete/data/osm/edits/ElementEditsControllerImpl.kt` |
| 41 | `SC_PENDING_QUEUE` | offline survey outbox | P0 | `app/src/commonMain/kotlin/de/westnordost/streetcomplete/data/osm/edits/ElementEditsControllerImpl.kt` |
| 42 | `SC_OSM_VERSION_CONFLICT` | stale source hold/compare | P0 | `app/src/commonMain/kotlin/de/westnordost/streetcomplete/data/osm/mapdata/MapDataApiClientImpl.kt` |
| 43 | `SC_UPLOAD_ORCHESTRATION` | separate upload-to-staging | P0 | `app/src/commonMain/kotlin/de/westnordost/streetcomplete/data/upload/Uploader.kt` |
| 44 | `SC_SOURCE_CHANGESET` | audit bundle metadata | P1 | `app/src/commonMain/kotlin/de/westnordost/streetcomplete/data/osm/edits/upload` |
| 45 | `SC_EDIT_HISTORY` | survey change timeline | P0 | `app/src/commonMain/kotlin/de/westnordost/streetcomplete/data/edithistory` |
| 46 | `SC_TAG_DIFF` | candidate OSM tag diff only | P1 | `app/src/commonMain/kotlin/de/westnordost/streetcomplete/data/osm/edits/update_tags` |
| 47 | `SC_OSM_NOTES` | annotation capture | P0 | `app/src/commonMain/kotlin/de/westnordost/streetcomplete/data/osmnotes` |
| 48 | `SC_PHOTO_EVIDENCE` | photo evidence with consent and hashes | P0 | `app/src/commonMain/kotlin/de/westnordost/streetcomplete/data/osmnotes/PhotoServiceApiClientImpl.kt` |
| 49 | `SC_GPS_TRACKS` | recon trace input | P0 | `app/src/commonMain/kotlin/de/westnordost/streetcomplete/data/osmtracks` |
| 50 | `SC_GEO_QUEST_MAP` | map quest pin workflow | P0 | `app/src/commonMain/kotlin/de/westnordost/streetcomplete/screens/main/map` |
| 51 | `SC_TEAM_MODE` | survey assignment/filter | P1 | `app/src/commonMain/kotlin/de/westnordost/streetcomplete/data/visiblequests/TeamModeQuestFilterSource.kt` |
| 52 | `SC_QUEST_PRESETS` | event-specific survey template | P1 | `app/src/commonMain/kotlin/de/westnordost/streetcomplete/data/presets` |
| 53 | `SC_QUEST_FILTER_VISIBILITY` | quest types by event | P1 | `app/src/commonMain/kotlin/de/westnordost/streetcomplete/data/visiblequests` |
| 54 | `SC_MAIN_MAP_CONTEXT` | survey/context quick actions | P1 | `app/src/commonMain/kotlin/de/westnordost/streetcomplete/screens/main/MapContextMenu.kt` |
| 55 | `SC_OSM_NODES_WAYS_RELATIONS` | provider OSM identifiers and types | P0 | `app/src/commonMain/kotlin/de/westnordost/streetcomplete/data/osm/mapdata/MapDataRepository.kt` |
| 56 | `SC_OSM_API_CLIENT` | read OSM snapshot with version | P0 | `app/src/commonMain/kotlin/de/westnordost/streetcomplete/data/osm/mapdata/MapDataApiClientImpl.kt` |
| 57 | `SC_ELEMENT_FILTER_PARSER` | curated deterministic quest predicates | P1 | `app/src/commonMain/kotlin/de/westnordost/streetcomplete/data/elementfilter` |
| 58 | `SC_COUNTRY_RULES` | country-specific road metadata checks | P1 | `app/src/commonMain/kotlin/de/westnordost/streetcomplete/data/meta` |
| 59 | `SC_ANDROID_SHARED_KOTLIN` | Kotlin/Android architecture path | P0 | `app/src/commonMain/kotlin/de/westnordost/streetcomplete/data/quest/QuestType.kt` |
| 60 | `SC_IOS_WORK_IN_PROGRESS` | evaluate later: not field-ready | P2 | `iosApp` |

**Gate:** No registry entry is allowed in LIVE, no OSM-public upload allowed, and no observation creates route authority. See `governance/streetcomplete-field-survey-policy.yaml`.
