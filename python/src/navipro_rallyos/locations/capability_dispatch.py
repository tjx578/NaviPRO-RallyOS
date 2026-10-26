"""Agent5 PREP/REVIEW capability request planner. No provider is executed by this module.
The implementation/status registry comes from GitHub STATUS.md 2026-10-26.
"""
from collections.abc import Mapping
import re

class LocationCapabilityError(ValueError): pass

TECH={
 "PRIVATE_DB":"NOT_DEPLOYED", "OSM_OVERPASS":"CONTRACT_ONLY",
 "GEOCODER":"CONTRACT_ONLY","OSRM":"MOCK_TESTED_ONLY",
 "VALHALLA":"NOT_RUNTIME_VERIFIED","GODS_EYE":"CONTEXT_PROTOTYPE_ONLY",
 "STREET_VIEW":"NOT_CONNECTED","CESIUM_3D":"SCAFFOLD_ONLY",
 "KEPLER":"SCAFFOLD_ONLY","STREETCOMPLETE_SURVEY":"PLANNER_PROTOTYPE_ONLY",
 "LEAFLET_ROUTING_MACHINE":"READ_ONLY_UI_POLICY_PROTOTYPE",
 "REACT_NATIVE_MAPS":"SOURCE_AUDIT_ONLY",
 "MCP_GATEWAY":"REGISTRY_ONLY","REVIEW_DECISION":"NOT_IMPLEMENTED",
 "JOURNAL_RECEIPT":"NOT_IMPLEMENTED",
}
FORBIDDEN={"master_pos","master_anchors","master_coordinates","master_time",
 "historical_kml","post_event_kml","kml_trace","result_card","penalty_card",
 "organizer_results","post_event_labels","training_ground_truth","timed_pos"}
def _scan(x):
 if isinstance(x,Mapping):
  for k,v in x.items():
   if str(k).casefold() in FORBIDDEN: raise LocationCapabilityError("POST_EVENT_DATA_IN_PREP")
   _scan(v)
 elif isinstance(x,(tuple,list)):
  for v in x: _scan(v)

def propose_location_tools(source_ledger, *, mode="PREP"):
 """Return source-attached proposed calls; never claim provider or physical VERIFICATION."""
 if mode not in ("PREP","REVIEW"):raise LocationCapabilityError("PRE_EVENT_MODE_REQUIRED")
 _scan(source_ledger)
 if not isinstance(source_ledger,list) or not source_ledger:raise LocationCapabilityError("SOURCE_LEDGER_REQUIRED")
 out=[]; ids=set()
 for x in source_ledger:
  instruction=x.get("source_instruction_id");text=x.get("raw_text");kind=x.get("kind","UNKNOWN")
  if not instruction or instruction in ids or not text:raise LocationCapabilityError("SOURCE_OCCURRENCE_INVALID")
  ids.add(instruction)
  tools=["PRIVATE_DB","GEOCODER","OSM_OVERPASS"]
  marker=(kind=="MARKER" or bool(re.search(r"\b(?:PAL|KM)\b",text,re.I)))
  sign=(kind=="SIGNED_DIRECTION_OCCURRENCE")
  if marker:tools+=["OSRM","STREET_VIEW","STREETCOMPLETE_SURVEY"]
  elif sign:tools+=["OSRM","VALHALLA","STREET_VIEW","STREETCOMPLETE_SURVEY"]
  else:tools+=["OSRM","GODS_EYE","STREET_VIEW"]
  tools+=["KEPLER","CESIUM_3D","LEAFLET_ROUTING_MACHINE",
          "REACT_NATIVE_MAPS","MCP_GATEWAY","REVIEW_DECISION"]
  out.append({"source_instruction_id":instruction,"kind":kind,
    "location_status":"UNRESOLVED_SPATIAL","poi_reference":None,
    "physical_location":None,"route_access_point":None,
    "is_official_control_point":None,"qg_07":"NOT_RUN","qg_08":"NOT_RUN",
    "driver_release":"HOLD",
    "capability_requests":[{"name":name,"implementation":TECH[name],
       "execution":"NOT_EXECUTED_UNAVAILABLE"} for name in dict.fromkeys(tools)]})
 return {"mode":mode,"master_data_used":False,"provider_success_count":0,
   "gate_results":"NOT_RUN","driver_release":"HOLD","locations":out}

def split_repeated_sign(*, sub_id, source_instruction_id, text, count):
 if type(count) is not int or count<1 or count>30:raise LocationCapabilityError("INVALID_SIGN_COUNT")
 if not source_instruction_id or not text:raise LocationCapabilityError("SOURCE_REQUIRED")
 return [{"source_instruction_id":source_instruction_id,
  "occurrence_id":source_instruction_id+"-SIGN-"+str(i),
  "sub_id":sub_id,"kind":"SIGNED_DIRECTION_OCCURRENCE",
  "physical_decision_id":None,"inbound_approach":None,
  "arrow_direction":"UNKNOWN","raw_text":text} for i in range(1,count+1)]

def marker_hypotheses(inscription):
 if not isinstance(inscription,str) or not inscription.strip():raise LocationCapabilityError("EMPTY_MARKER")
 return {"raw":inscription,"tokens":[p.strip() for p in inscription.split("/") if p.strip()],
    "stationing_datum":"UNKNOWN","road_reference":"UNKNOWN","status":"REFERENCE_UNRESOLVED"}
