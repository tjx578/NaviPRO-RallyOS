"""Synthetic-only NaviPRO survey planner and outbox demo; no network/OSM writes."""
from pathlib import Path
from tempfile import TemporaryDirectory
import sys
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'python/src'))
from navipro_rallyos.survey.core import plan_survey_tasks
from navipro_rallyos.survey.queue import ObservationQueue

# Fictional OSM reference, not a real survey observation.
way={'element_type':'way','element_id':8888888,'osm_version':3,
     'lat_e7':-86700000,'lon_e7':1152100000,'tags':{'highway':'residential'}}
tasks=plan_survey_tasks([way], 'DEMO-ROUTE-REV-1',max_tasks=4)
print('Proposed tasks:',[(t['quest_type'],t['priority']) for t in tasks])
surface_task=next(t for t in tasks if t['quest_type']=='road_surface')
obs={'observation_id':'DEMO-OBS-1','task_id':surface_task['task_id'],
     'route_revision_id':'DEMO-ROUTE-REV-1','actor_id':'DEMO-SURVEYOR',
     'quest_type':'road_surface','answer':'asphalt','observed_at':'2026-10-20T10:00:00+08:00',
     'osm_element_type':'way','osm_element_id':way['element_id'],'observed_osm_version':3,
     'lat_e7':way['lat_e7'],'lon_e7':way['lon_e7'],'mode':'PREP','route_authority':False}
with TemporaryDirectory() as d:
    queue=ObservationQueue(Path(d)/'outbox.db')
    print('Capture:',queue.enqueue(obs))
    print('Pending:',queue.list_pending())
    print('Staging receipt, no authority:',queue.acknowledge_staging('DEMO-OBS-1',3,'DEMO-ACK'))
    queue.close()
