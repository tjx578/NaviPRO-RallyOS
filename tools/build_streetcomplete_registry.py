#!/usr/bin/env python3
"""Clean-room source-traceable REA capability matrix."""
from pathlib import Path
import yaml
repo=Path(__file__).resolve().parents[1]
sc='app/src/commonMain/kotlin/de/westnordost/streetcomplete/'
# category, id, source relative path, mapping, phase
ROWS=[
('quest','atomic_quest','data/quest/QuestType.kt','atomic survey question/card','P0'),
('quest','osm_attribute_filter','data/osm/osmquests/OsmFilterQuestType.kt','missing-tag based task planning','P0'),
('quest','quest_registry','quests/QuestTypesRegistry.kt','registry with stable quest IDs','P0'),
('quest','road_surface','quests/surface/AddRoadSurface.kt','surface evidence','P0'),
('quest','road_smoothness','quests/smoothness/AddRoadSmoothness.kt','road passability context','P0'),
('quest','oneway','quests/oneway/AddOneway.kt','directional restrictions candidate','P0'),
('quest','max_speed','quests/max_speed/AddMaxSpeed.kt','posted legal speed only','P1'),
('quest','road_name','quests/road_name/AddRoadName.kt','landmark street names','P0'),
('quest','lanes','quests/lanes','lane count','P1'),
('quest','lane_markings','quests/lane_markings','road markings','P1'),
('quest','width','quests/width','road width','P1'),
('quest','barrier','quests/barrier_type','barrier candidate','P0'),
('quest','crossing','quests/crossing','crossing metadata','P1'),
('quest','traffic_calming','quests/traffic_calming_type','traffic calming candidate','P1'),
('quest','construction','quests/construction','temporary topology risk','P0'),
('quest','bridge_structure','quests/bridge_structure','bridge identification','P1'),
('quest','lighting','quests/way_lit','lighting observations','P2'),
('quest','signboard','quests/board_name','roadside signs context','P1'),
('quest','opening_hours_signed','quests/opening_hours_signed','information-board observation','P2'),
('quest','road_ref','quests/access_point_ref','road access reference','P1'),
('overlay','overlay_registry','overlays/OverlaysRegistry.kt','thematic overlay menu','P0'),
('overlay','surface_overlay','overlays/surface','surface continuity map','P0'),
('overlay','lighting_overlay','overlays/way_lit','lighting thematic layer','P2'),
('overlay','sidewalk_overlay','overlays/sidewalk','sidewalk context','P2'),
('overlay','cycleway_overlay','overlays/cycleway','cycleway context','P2'),
('overlay','parking_overlay','overlays/street_parking','parking/access context','P2'),
('overlay','address_overlay','overlays/address','address references','P1'),
('overlay','places_overlay','overlays/places','POI landmark reference','P0'),
('overlay','buildings_overlay','overlays/buildings','building landmarks','P1'),
('overlay','things_overlay','overlays/things','infrastructure references','P1'),
('overlay','mtb_scale_overlay','overlays/mtb_scale','track steepness context (non motor use)','P2'),
('offline','tile_area_download','data/download/DownloadController.kt','corridor offline area','P0'),
('offline','download_orchestration','data/download/Downloader.kt','map+notes+mapdata acquisition','P0'),
('offline','download_strategy','data/download/strategy','network-aware scheduled download','P1'),
('offline','map_tile_cache','data/maptiles','vector basemap cache','P0'),
('offline','preloader','data/Preloader.kt','initial data preload','P1'),
('offline','autosync','data/quest/AutoSyncer.kt','network and GPS-aware sync policy','P0'),
('offline','persistence','data/Database.kt','durable SQLite observations','P0'),
('edit','local_edit','data/osm/edits/ElementEdit.kt','audit observation provenance','P0'),
('edit','undo','data/osm/edits/ElementEditsControllerImpl.kt','correction/retraction events','P1'),
('edit','pending_queue','data/osm/edits/ElementEditsControllerImpl.kt','offline survey outbox','P0'),
('edit','osm_version_conflict','data/osm/mapdata/MapDataApiClientImpl.kt','stale source hold/compare','P0'),
('edit','upload_orchestration','data/upload/Uploader.kt','separate upload-to-staging','P0'),
('edit','source_changeset','data/osm/edits/upload','audit bundle metadata','P1'),
('edit','edit_history','data/edithistory','survey change timeline','P0'),
('edit','tag_diff','data/osm/edits/update_tags','candidate OSM tag diff only','P1'),
('field','osm_notes','data/osmnotes','annotation capture','P0'),
('field','photo_evidence','data/osmnotes/PhotoServiceApiClientImpl.kt','photo evidence with consent and hashes','P0'),
('field','gps_tracks','data/osmtracks','recon trace input','P0'),
('field','geo_quest_map','screens/main/map','map quest pin workflow','P0'),
('field','team_mode','data/visiblequests/TeamModeQuestFilterSource.kt','survey assignment/filter','P1'),
('field','quest_presets','data/presets','event-specific survey template','P1'),
('field','quest_filter_visibility','data/visiblequests','quest types by event','P1'),
('field','main_map_context','screens/main/MapContextMenu.kt','survey/context quick actions','P1'),
('interoperability','osm_nodes_ways_relations','data/osm/mapdata/MapDataRepository.kt','provider OSM identifiers and types','P0'),
('interoperability','osm_api_client','data/osm/mapdata/MapDataApiClientImpl.kt','read OSM snapshot with version','P0'),
('interoperability','element_filter_parser','data/elementfilter','curated deterministic quest predicates','P1'),
('interoperability','country_rules','data/meta','country-specific road metadata checks','P1'),
('interoperability','android_shared_kotlin','data/quest/QuestType.kt','Kotlin/Android architecture path','P0'),
('interoperability','ios_work_in_progress','../iosApp','evaluate later: not field-ready','P2'),
]
cap=[]
for category,id,path,desc,priority in ROWS:
    # one source points to repo root rather than commonMain path
    src='iosApp' if path=='../iosApp' else sc+path
    cap.append({'id':'SC_'+id.upper(),'domain':category.upper(),'source_path':src,'source_capability':id,
                'navipro_target':desc,'priority':priority,'allowed_modes':['PREP','REVIEW'],
                'route_authority':False,'osm_publish':False,'implementation_status':'MAPPED_NOT_PARITY_VERIFIED'})
assert len({c['id'] for c in cap})==len(cap)
output={'id':'NAVIPRO-STREETCOMPLETE-REA-CAPABILITIES-V1','version':'0.1.0','source_repo':'tjx578/StreetComplete_rally-maps',
  'source_sha':'e6b04da98028d34c1e49625edd7095f7008106a6','source_license':'GPL-3.0-only',
  'rule':'Architecture patterns only; no GPL source copied into NaviPRO code',
  'capabilities':cap}
p=repo/'contracts/spatial/streetcomplete-capability-registry.yaml';p.write_text(yaml.safe_dump(output,sort_keys=False,allow_unicode=True),encoding='utf8')
print(f'{len(cap)} capabilities mapped (not implemented)')
