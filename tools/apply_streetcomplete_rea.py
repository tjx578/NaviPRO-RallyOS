#!/usr/bin/env python3
"""Idempotently add StreetComplete-inspired survey contracts to NaviPRO.

The content below is designed for NaviPRO and is not a translation of GPL source.
"""
from pathlib import Path
import yaml, json
ROOT=Path(__file__).resolve().parents[1]
spec_file=ROOT/'contracts/openapi/navipro-rallyos.openapi.yaml'
spec=yaml.safe_load(spec_file.read_text())
spec['info']['version']='0.4.0-vnext-streetcomplete-rea'
spec['info']['description']+=' StreetComplete REA adds clean-room, PREP/REVIEW-only field-survey contracts; observational data is not OSM-tag editing, verified road truth, or route authority.' if 'StreetComplete REA' not in spec['info']['description'] else ''
if 'FieldSurvey' not in [t['name'] for t in spec['tags']]:
    spec['tags'].append({'name':'FieldSurvey','description':'Quest-inspired offline survey planning and staging (no direct OSM publish)'})
components=spec.setdefault('components',{}).setdefault('schemas',{})
strid={'type':'string','minLength':1}
e7lat={'type':'integer','minimum':-900000000,'maximum':900000000}
e7lon={'type':'integer','minimum':-1800000000,'maximum':1800000000}
base_obj=lambda req,props:{'type':'object','additionalProperties':False,'required':req,'properties':props}
components.update({
'SurveySourceRef':base_obj(['source_kind','osm_element_type','osm_element_id','osm_version'],{
  'source_kind':{'type':'string','const':'OSM_SNAPSHOT'},
  'osm_element_type':{'type':'string','enum':['node','way','relation']},
  'osm_element_id':{'type':'integer','minimum':1},
  'osm_version':{'type':'integer','minimum':1},
  'snapshot_id':strid,'dataset_sha256':{'type':'string','pattern':'^[0-9a-f]{64}$'},
}),
'SurveyTaskPlanRequest':base_obj(['route_revision_id','event_id','mode','source_snapshot_id','quest_types'],{
 'route_revision_id':strid,'event_id':strid,'mode':{'type':'string','enum':['PREP','REVIEW']},
 'source_snapshot_id':strid,'quest_types':{'type':'array','minItems':1,'items':strid,'uniqueItems':True},
 'max_tasks':{'type':'integer','minimum':1,'maximum':5000},
 'corridor_filter_ref':strid,
}),
'SurveyTask':base_obj(['task_id','quest_type','question','source','status','route_revision_id','priority','human_survey_required','route_authority'],{
  'task_id':strid,'quest_type':strid,'question':strid,
  'source':{'$ref':'#/components/schemas/SurveySourceRef'},
  'status':{'type':'string','enum':['PROPOSED','ASSIGNED','IN_PROGRESS','ANSWERED','SKIPPED','CLOSED']},
  'route_revision_id':strid,'priority':{'type':'integer','minimum':0,'maximum':100},
  'lat_e7':e7lat,'lon_e7':e7lon,'human_survey_required':{'type':'boolean','const':True},
  'route_authority':{'type':'boolean','const':False},'reasons':{'type':'array','items':strid},
}),
'SurveyObservationDraft':base_obj(['observation_id','task_id','route_revision_id','actor_id','quest_type','answer','observed_at','source','lat_e7','lon_e7','mode'],{
  'observation_id':strid,'task_id':strid,'route_revision_id':strid,
  'actor_id':strid,'quest_type':strid,'answer':{'oneOf':[strid,{'type':'object'}]},
  'observed_at':{'type':'string','format':'date-time'},
  'source':{'$ref':'#/components/schemas/SurveySourceRef'},
  'lat_e7':e7lat,'lon_e7':e7lon,
  'gps_accuracy_m':{'type':['number','null'],'minimum':0},
  'photo_sha256':{'type':'string','pattern':'^[0-9a-f]{64}$'},
  'notes':{'type':'string','maxLength':3000},
  'mode':{'type':'string','enum':['PREP','REVIEW']},
  'route_authority':{'type':'boolean','const':False},
}),
'SurveyAssessmentRequest':base_obj(['observation_id','route_revision_id','mode'],{
  'observation_id':strid,'route_revision_id':strid,'mode':{'type':'string','enum':['PREP','REVIEW']},
  'current_osm_version':{'type':['integer','null'],'minimum':1},
  'source_snapshot_id':strid,
}),
'SurveyConflictCheckRequest':base_obj(['observation_id','observed_osm_version','current_osm_version','mode'],{
 'observation_id':strid,'observed_osm_version':{'type':'integer','minimum':1},
 'current_osm_version':{'type':['integer','null'],'minimum':1},
 'mode':{'type':'string','enum':['PREP','REVIEW']},
}),
'SurveyGapAnalysisRequest':base_obj(['route_revision_id','source_snapshot_id','mode'],{
 'route_revision_id':strid,'source_snapshot_id':strid,'mode':{'type':'string','enum':['PREP','REVIEW']},
 'include_kmpal':{'type':'boolean'},'include_mandatory_landmarks':{'type':'boolean'},
}),
'SurveySyncPlanRequest':base_obj(['device_id','batch_id','mode'],{
 'device_id':strid,'batch_id':strid,'mode':{'type':'string','enum':['PREP','REVIEW']},
 'pending_observation_ids':{'type':'array','items':strid,'uniqueItems':True},
 'network_preference':{'type':'string','enum':['WIFI_ONLY','ANY_NETWORK','MANUAL']},
 'destination':{'type':'string','const':'NAVIPRO_STAGING_ONLY'},
}),
'SurveyOverlayPlanRequest':base_obj(['route_revision_id','mode','overlay_types'],{
 'route_revision_id':strid,'mode':{'type':'string','enum':['PREP','REVIEW']},
 'overlay_types':{'type':'array','items':{'type':'string','enum':['surface','smoothness','oneway','maxspeed','access','road_name','width','quests','observations','conflicts','kmpal']}},
 'source_snapshot_id':strid,
}),
'SurveyTaskResult':base_obj(['status','route_authority','mode'],{
  'status':{'type':'string','enum':['PROPOSED','PENDING_SYNC','STAGED_REVIEW','CONFLICT','HOLD','NEEDS_REVIEW']},
  'route_authority':{'type':'boolean','const':False},
  'mode':{'type':'string','enum':['PREP','REVIEW']},
  'task_id':strid,'observation_id':strid,'plan_id':strid,
  'warnings':{'type':'array','items':{'type':'string'}},
  'requires_human_review':{'type':'boolean'},
}),
})

# Explicit allowlist: staging writes from human clients are not exposed to Page 3 AI.
def add(path,method,opid,summary,tool,req=None,enabled=True,authority='READ',side='NONE',params=None):
    response={'200':{'description':'PREP/REVIEW assessment or proposal only; not authoritative','content':{'application/json':{'schema':{'$ref':'#/components/schemas/SurveyTaskResult'}}}},
              '400':{'description':'Invalid input','content':{'application/json':{'schema':{'$ref':'#/components/schemas/ApiError'}}}},
              '401':{'description':'Authentication required'},'403':{'description':'Forbidden'},'409':{'description':'Stale source/conflict'}}
    op={'operationId':opid,'summary':summary,'tags':['FieldSurvey'],'x-navipro-mcp':{'enabled':enabled},'x-navipro-mode':['PREP','REVIEW'],
      'x-navipro-authority':authority,'x-navipro-side-effect':side,'responses':response}
    if enabled:op['x-navipro-mcp']['tool']=tool
    if req:op['requestBody']={'required':True,'content':{'application/json':{'schema':{'$ref':f'#/components/schemas/{req}'}}}}
    if params:op['parameters']=[{'in':'path','name':p,'required':True,'schema':strid} for p in params]
    if path not in spec['paths']:spec['paths'][path]={}
    if method in spec['paths'][path]:raise ValueError('duplicate operation '+path)
    spec['paths'][path][method]=op

add('/survey/capabilities','get','getSurveyCapabilities','List survey capability registry','navipro.survey.capabilities.get')
add('/survey/tasks/plan','post','planSurveyTasks','Propose atomic road/landmark surveys','navipro.survey.tasks.plan','SurveyTaskPlanRequest',True,'AGENT_PROPOSE','PROPOSAL_ONLY')
add('/survey/tasks/{taskId}','get','getSurveyTask','Read a survey task','navipro.survey.task.get',params=['taskId'])
add('/survey/gaps/route','post','assessSurveyRouteGaps','Find route evidence gaps and propose survey tasks','navipro.survey.gaps.assess','SurveyGapAnalysisRequest',True,'AGENT_PROPOSE','NONE')
add('/survey/observations','post','captureSurveyObservation','Record human field observation to local staging','', 'SurveyObservationDraft',False,'HUMAN_SURVEYOR','STAGING_WRITE')
add('/survey/observations/{observationId}','get','getSurveyObservation','Read staging observation','navipro.survey.observation.get',params=['observationId'])
add('/survey/observations/assess','post','assessSurveyObservation','Assess candidate observation, do not promote verified','navipro.survey.observation.assess','SurveyAssessmentRequest',True,'AGENT_PROPOSE','NONE')
add('/survey/conflicts/assess','post','assessSurveyConflict','Version-aware OSM survey conflict assessment','navipro.survey.conflicts.assess','SurveyConflictCheckRequest',True,'READ','NONE')
add('/survey/sync/plan','post','planSurveySync','Plan offline to NaviPRO staging sync','navipro.survey.sync.plan','SurveySyncPlanRequest',True,'AGENT_PROPOSE','NONE')
add('/survey/sync/commit','post','commitSurveySync','Authenticated field client uploads staged observations','', 'SurveySyncPlanRequest',False,'HUMAN_SURVEYOR','STAGING_WRITE')
add('/survey/overlays/plan','post','planSurveyOverlays','Plan thematic road-attribute review overlays','navipro.survey.overlays.plan','SurveyOverlayPlanRequest',True,'AGENT_PROPOSE','NONE')
add('/survey/decisions/{observationId}','post','decideSurveyEvidence','Navigator alone issues a scoped evidence decision','', 'SurveyAssessmentRequest',False,'NAVIGATOR_ONLY','AUTHORITY_MUTATION',params=['observationId'])
spec_file.write_text(yaml.safe_dump(spec,sort_keys=False,allow_unicode=True,width=115),encoding='utf-8')
print('StreetComplete REA OpenAPI routes:',len([p for p in spec['paths'] if p.startswith('/survey/')]))
