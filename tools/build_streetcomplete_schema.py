from pathlib import Path
import json
root=Path(__file__).resolve().parents[1]
schema={
 '$schema':'https://json-schema.org/draft/2020-12/schema',
 '$id':'https://navipro.invalid/schemas/field-survey-observation.v1.json',
 'title':'NaviPRO field survey observation (non-authoritative)',
 'type':'object','additionalProperties':False,
 'required':['observation_id','task_id','route_revision_id','actor_id','quest_type','answer','observed_at','osm_element_type','osm_element_id','observed_osm_version','lat_e7','lon_e7','mode','route_authority'],
 'properties':{
  'observation_id':{'type':'string','minLength':1},'task_id':{'type':'string','minLength':1},'route_revision_id':{'type':'string','minLength':1},
  'actor_id':{'type':'string','minLength':1},'quest_type':{'type':'string','minLength':1},
  'answer':{'oneOf':[{'type':'string','minLength':1},{'type':'object','minProperties':1}]},
  'observed_at':{'type':'string','format':'date-time'},'osm_element_type':{'enum':['way','node']},
  'osm_element_id':{'type':'integer','minimum':1},'observed_osm_version':{'type':'integer','minimum':1},
  'lat_e7':{'type':'integer','minimum':-900000000,'maximum':900000000},
  'lon_e7':{'type':'integer','minimum':-1800000000,'maximum':1800000000},
  'gps_accuracy_m':{'type':['number','null'],'minimum':0,'maximum':100000},
  'evidence_sha256':{'type':'string','pattern':'^[a-f0-9]{64}$'},
  'mode':{'enum':['PREP','REVIEW']},
  'route_authority':{'type':'boolean','const':False},
  'capture_method':{'enum':['HUMAN_VISUAL','HUMAN_MEASURED','DOCUMENT_REFERENCE']},
  'survey_safety_attested':{'type':'boolean'},
  'notes':{'type':'string','maxLength':3000},
 }
}
(root/'contracts/jsonschema/field-survey-observation.schema.json').write_text(json.dumps(schema,indent=2,ensure_ascii=False)+'\n')
(root/'tests/fixtures/field-survey-observation.demo.json').write_text(json.dumps({
 'observation_id':'OBS-DEM-001','task_id':'SVY-DEM-001','route_revision_id':'ROUTE-REV-DEMO','actor_id':'SURVEYOR-DEMO',
 'quest_type':'road_surface','answer':'asphalt','observed_at':'2026-10-19T14:30:00+08:00',
 'osm_element_type':'way','osm_element_id':123456,'observed_osm_version':7,
 'lat_e7':-86700000,'lon_e7':1152100000,'gps_accuracy_m':12.0,
 'evidence_sha256':'a'*64,'mode':'PREP','route_authority':False,'capture_method':'HUMAN_VISUAL',
 'survey_safety_attested':True},indent=2,ensure_ascii=False)+'\n')
