from pathlib import Path
import yaml
p=Path(__file__).resolve().parents[1]/'contracts/openapi/navipro-rallyos.openapi.yaml'
s=yaml.safe_load(p.read_text()); c=s['components']['schemas']
S={'type':'string','minLength':1}
C=lambda typ:{'$ref':'#/components/schemas/'+typ}
obj=lambda req,props:{'type':'object','additionalProperties':False,'required':req,'properties':props}
truth={'type':'boolean','const':False}
mode={'type':'string','enum':['PREP','REVIEW']}
# Align the OpenAPI human-capture payload with the Python outbox + JSON Schema;
# OSM source fields are flat in the canonical observation payload.
c['SurveyObservationDraft']=obj([
 'observation_id','task_id','route_revision_id','actor_id','quest_type','answer','observed_at','osm_element_type','osm_element_id','observed_osm_version','lat_e7','lon_e7','mode','route_authority'
],{
 'observation_id':S,'task_id':S,'route_revision_id':S,'actor_id':S,'quest_type':S,
 'answer':{'oneOf':[{'type':'string','minLength':1},{'type':'object','minProperties':1}]},
 'observed_at':{'type':'string','format':'date-time'},
 'osm_element_type':{'type':'string','enum':['node','way']},
 'osm_element_id':{'type':'integer','minimum':1}, 'observed_osm_version':{'type':'integer','minimum':1},
 'lat_e7':{'type':'integer','minimum':-900000000,'maximum':900000000},
 'lon_e7':{'type':'integer','minimum':-1800000000,'maximum':1800000000},
 'mode':mode,'route_authority':truth,
 'gps_accuracy_m':{'type':['number','null'],'minimum':0},
 'evidence_sha256':{'type':'string','pattern':'^[0-9a-f]{64}$'},
 'source_snapshot_id':S, 'notes':{'type':'string','maxLength':3000},
})
c['SurveyTask']['properties']['osm_tag_key']=S
c['SurveyTask']['properties']['mode']=mode
c['SurveyTask']['properties']['authority']={'type':'string','const':'SURVEY_PROPOSAL_ONLY'}
c['SurveyCapabilitiesResult']=obj(['mode','route_authority','quest_types'],{'mode':mode,'route_authority':truth,'quest_types':{'type':'array','items':S},'source_sha':S})
c['SurveyTaskPlanResult']=obj(['mode','route_authority','tasks'],{'mode':mode,'route_authority':truth,'tasks':{'type':'array','items':C('SurveyTask')},'warnings':{'type':'array','items':S}})
c['SurveyTaskReadResult']=obj(['mode','route_authority','task'],{'mode':mode,'route_authority':truth,'task':C('SurveyTask')})
c['SurveyObservationReadResult']=obj(['mode','route_authority','observation'],{'mode':mode,'route_authority':truth,'observation':C('SurveyObservationDraft'),'staging_status':{'type':'string','enum':['PENDING_SYNC','STAGED_REVIEW','CONFLICT','HOLD']}})
c['SurveyConflictResult']=obj(['status','route_authority','reason'],{'status':{'type':'string','enum':['REVIEW_REQUIRED','CONFLICT','HOLD']},'route_authority':truth,'reason':S,'observation_id':S})
c['SurveySyncPlanResult']=obj(['mode','route_authority','destination','pending_count'],{'mode':mode,'route_authority':truth,'destination':{'const':'NAVIPRO_STAGING_ONLY'},'pending_count':{'type':'integer','minimum':0},'warnings':{'type':'array','items':S}})
c['SurveyOverlayPlanResult']=obj(['mode','route_authority','overlay_types'],{'mode':mode,'route_authority':truth,'overlay_types':{'type':'array','items':S},'warnings':{'type':'array','items':S}})
response_schemas={
 'getSurveyCapabilities':'SurveyCapabilitiesResult','planSurveyTasks':'SurveyTaskPlanResult','getSurveyTask':'SurveyTaskReadResult',
 'assessSurveyRouteGaps':'SurveyTaskPlanResult','captureSurveyObservation':'SurveyTaskResult',
 'getSurveyObservation':'SurveyObservationReadResult','assessSurveyObservation':'SurveyTaskResult',
 'assessSurveyConflict':'SurveyConflictResult','planSurveySync':'SurveySyncPlanResult','commitSurveySync':'SurveyTaskResult',
 'planSurveyOverlays':'SurveyOverlayPlanResult','decideSurveyEvidence':'SurveyTaskResult'
}
for url,methods in s['paths'].items():
 if not url.startswith('/survey/'):continue
 for method,op in methods.items():
  ref=response_schemas[op['operationId']]
  op['responses']['200']['content']['application/json']['schema']=C(ref)
  # error operation is existing structural response only; not executable
p.write_text(yaml.safe_dump(s,sort_keys=False,allow_unicode=True,width=115))
print('Survey response schemas:',len(response_schemas),'new component schemas:',7)
