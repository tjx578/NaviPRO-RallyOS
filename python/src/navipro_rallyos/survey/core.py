"""Deterministic, provider-neutral RallyOS field-survey task planning.

Clean-room NaviPRO code, informed by StreetComplete's *ideas*, not a translation
or copy of GPL source. No direct OpenStreetMap writes or route authority.
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Mapping, Any
import hashlib
import json

# Curated rally-focused questions. Source tagging is OSM vocabulary, not OSM authority.
# A question is asked only if corresponding tag is absent; individual evidence
# doesn't automatically update the OSM database, graph, route or masterpos.
QUESTS: dict[str, dict[str, Any]] = {
    "road_surface": {"tag": "surface", "question": "Apa permukaan jalan di lokasi ini?", "priority": 95, "osm_types": ["way"]},
    "road_smoothness": {"tag": "smoothness", "question": "Bagaimana kondisi kehalusan jalan?", "priority": 90, "osm_types": ["way"]},
    "oneway": {"tag": "oneway", "question": "Apakah jalan ini satu arah?", "priority": 100, "osm_types": ["way"]},
    "road_name": {"tag": "name", "question": "Apa nama jalan pada papan jalan?", "priority": 75, "osm_types": ["way"]},
    "lanes": {"tag": "lanes", "question": "Berapa jumlah lajur yang terlihat?", "priority": 70, "osm_types": ["way"]},
    "maxspeed_sign": {"tag": "maxspeed", "question": "Apakah ada rambu batas kecepatan dan berapa nilainya?", "priority": 70, "osm_types": ["way"]},
    "road_width": {"tag": "width", "question": "Berapa lebar jalan terukur/perkiraan dan metodenya?", "priority": 75, "osm_types": ["way"]},
    "access": {"tag": "access", "question": "Apakah ada pembatasan akses yang terlihat?", "priority": 98, "osm_types": ["way"]},
    "bridge": {"tag": "bridge", "question": "Apakah segmen ini melalui jembatan?", "priority": 65, "osm_types": ["way"]},
    "tunnel": {"tag": "tunnel", "question": "Apakah segmen ini melalui terowongan?", "priority": 65, "osm_types": ["way"]},
    "road_lighting": {"tag": "lit", "question": "Apakah jalan memiliki penerangan?", "priority": 40, "osm_types": ["way"]},
    "traffic_calming": {"tag": "traffic_calming", "question": "Apa jenis pengendali kecepatan di titik ini?", "priority": 60, "osm_types": ["node"]},
    "barrier": {"tag": "barrier", "question": "Apakah ada penghalang jalan dan apa jenisnya?", "priority": 99, "osm_types": ["node"]},
}
ROAD_TYPES = frozenset({"primary", "secondary", "tertiary", "unclassified", "residential", "living_street", "service", "track", "primary_link", "secondary_link", "tertiary_link"})

def _string(value: Any, key: str) -> str:
    if not isinstance(value, str) or not value.strip():
        raise ValueError(f"{key} must be a non-empty string")
    return value.strip()

def _id(q: str, element_type: str, element_id: int, version: int, route_revision_id: str) -> str:
    payload = json.dumps([q,element_type,element_id,version,route_revision_id],separators=(",", ":"))
    return "SVY-"+hashlib.sha256(payload.encode()).hexdigest()[:20]

def plan_survey_tasks(elements: list[Mapping[str,Any]], route_revision_id: str, max_tasks: int=200) -> list[dict[str, Any]]:
    """Return deterministic, idempotent PREP/REVIEW tasks from supplied OSM snapshots.

    Input elements require element_type, element_id, osm_version, tags and E7 coordinates.
    Upstream caller is responsible for selecting the actual rally route/corridor. The
    function never guesses a survey coordinate or treats a skipped quest as evidence.
    """
    route_revision_id = _string(route_revision_id, 'route_revision_id')
    if not isinstance(max_tasks,int) or isinstance(max_tasks,bool) or not 1 <= max_tasks <= 5000:
        raise ValueError('max_tasks must be an integer 1..5000')
    tasks=[]
    ids=set()
    for element in elements:
        etype=element.get('element_type')
        eid=element.get('element_id')
        version=element.get('osm_version')
        lat=element.get('lat_e7'); lon=element.get('lon_e7')
        if etype not in ('node','way') or not isinstance(eid,int) or isinstance(eid,bool) or eid<=0 or not isinstance(version,int) or isinstance(version,bool) or version<1:
            raise ValueError('invalid OSM element identity or version')
        if not isinstance(lat,int) or isinstance(lat,bool) or not isinstance(lon,int) or isinstance(lon,bool) or not(-900000000<=lat<=900000000) or not(-1800000000<=lon<=1800000000):
            raise ValueError('lat_e7 / lon_e7 must be valid integer coordinates')
        tags=element.get('tags')
        if not isinstance(tags,dict) or any(not isinstance(k,str) or not isinstance(v,str) for k,v in tags.items()):
            raise ValueError('tags must be a string-string mapping')
        # By default, do not generate tasks for inaccessible/private roads.
        if tags.get('access') in ('private','no') or tags.get('motor_vehicle') in ('private','no'):
            continue
        if etype=='way' and tags.get('highway') not in ROAD_TYPES:
            continue
        if etype=='node' and not ('highway' in tags or 'barrier' in tags):
            continue
        flags=element.get('candidate_flags',[])
        if not isinstance(flags,list) or any(not isinstance(x,str) for x in flags):
            raise ValueError('candidate_flags must be a string list')
        flag_set=set(flags)
        for q,defn in QUESTS.items():
            if etype not in defn['osm_types'] or defn['tag'] in tags:
                continue
            # conservative, type-specific predicates. OSM-specific nuance
            # should later be served by a reviewed rule registry.
            if q=='road_smoothness' and tags.get('surface') not in ('asphalt','concrete','concrete:plates','sett','paving_stones','compacted','gravel','fine_gravel'):
                continue  # avoid redundant survey before a known eligible surface
            if q=='oneway':
                # Emulate StreetComplete's cautious applicability idea; do not
                # guess one-way from absent tag alone, especially without topology.
                try:
                    width=float(tags['width']); lanes=int(tags.get('lanes','1'))
                except (KeyError,ValueError,OverflowError):
                    continue
                if width>4 or lanes>1 or 'both_ends_connected' not in flag_set:
                    continue
            if q=='traffic_calming' and tags.get('highway')!='traffic_calming':continue
            if q=='barrier' and 'barrier_suspected' not in flag_set:continue
            if q=='access' and 'restricted_access_suspected' not in flag_set:continue
            if q in ('bridge','tunnel') and (q+'_suspected') not in flag_set:continue
            if q=='maxspeed_sign' and tags.get('surface') in ('gravel','dirt','ground','sand'):
                continue
            key=_id(q,etype,eid,version,route_revision_id)
            if key in ids: continue
            ids.add(key)
            tasks.append({
                'task_id':key, 'quest_type':q,'question':defn['question'],
                'priority':defn['priority'],'status':'PROPOSED',
                'route_revision_id':route_revision_id,'osm_tag_key':defn['tag'],
                'lat_e7':lat,'lon_e7':lon,'source':{'source_kind':'OSM_SNAPSHOT','osm_element_type':etype, 'osm_element_id':eid,'osm_version':version},
                'route_authority':False, 'authority':'SURVEY_PROPOSAL_ONLY', 'mode':'PREP',
                'human_survey_required':True,
            })
    tasks.sort(key=lambda t:(-t['priority'],t['source']['osm_element_type'],t['source']['osm_element_id'],t['quest_type'],t['task_id']))
    return tasks[:max_tasks]


def assess_version_conflict(observed_osm_version:int, current_osm_version:int|None)->dict[str,Any]:
    """Only a version comparison. A match is never proof of ground truth."""
    if not isinstance(observed_osm_version,int) or isinstance(observed_osm_version,bool) or observed_osm_version<1:
        raise ValueError('invalid observed version')
    if current_osm_version is None:
        return {'status':'HOLD','reason':'CURRENT_OSM_VERSION_UNKNOWN','route_authority':False}
    if not isinstance(current_osm_version,int) or isinstance(current_osm_version,bool) or current_osm_version<1:
        raise ValueError('invalid current version')
    return {'status':'REVIEW_REQUIRED' if observed_osm_version==current_osm_version else 'CONFLICT',
            'reason':'SOURCE_VERSION_MATCH' if observed_osm_version==current_osm_version else 'SOURCE_VERSION_CHANGED',
            'route_authority':False}
