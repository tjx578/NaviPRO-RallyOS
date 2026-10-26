import sys
from pathlib import Path
import pytest
sys.path.insert(0,str(Path(__file__).resolve().parents[2]/"python"/"src"))
from navipro_rallyos.locations.capability_dispatch import (
 LocationCapabilityError,propose_location_tools,split_repeated_sign,marker_hypotheses)

def ledger():
 return [{"source_instruction_id":"B-03-sign1","kind":"SIGNED_DIRECTION_OCCURRENCE",
  "raw_text":"Ikuti papan Gilimanuk pertama"},
  {"source_instruction_id":"B-03-sign2","kind":"SIGNED_DIRECTION_OCCURRENCE",
  "raw_text":"Ikuti papan Gilimanuk kedua"},
  {"source_instruction_id":"D-02","kind":"MARKER",
  "raw_text":"PAL TMK 10 / DPS 84 / SGR 5"}]

def test_prep_without_master_or_real_provider():
 r=propose_location_tools(ledger())
 assert r["master_data_used"] is False and r["provider_success_count"]==0
 assert all(x["route_access_point"] is None for x in r["locations"])
 assert all(x["qg_08"]=="NOT_RUN" and x["driver_release"]=="HOLD" for x in r["locations"])
 assert all(y["execution"]=="NOT_EXECUTED_UNAVAILABLE" for x in r["locations"] for y in x["capability_requests"])

def test_sign_has_visual_and_graph_evidence_requests():
 r=propose_location_tools(ledger())
 x=r["locations"][0]
 names={z["name"] for z in x["capability_requests"]}
 assert {"OSRM","VALHALLA","STREET_VIEW"} <= names

def test_signs_are_distinct_even_if_not_adjacent():
 e=split_repeated_sign(sub_id="B",source_instruction_id="B-03",
   text="Arah Gilimanuk dua kali",count=2)
 assert len(e)==2 and e[0]["occurrence_id"]!=e[1]["occurrence_id"]
 assert all(x["arrow_direction"]=="UNKNOWN" for x in e)

def test_km_pal_ambiguous_not_reversed_distance_certified():
 x=marker_hypotheses("SMG 127 27 / KRA 12")
 assert x["stationing_datum"]=="UNKNOWN"
 assert x["tokens"][0]=="SMG 127 27"

def test_nobody_hallucinates_ground_truth():
 with pytest.raises(LocationCapabilityError):
  propose_location_tools(ledger()+[{"source_instruction_id":"x","raw_text":"test",
    "master_pos":{"lat":-8.1}}])
 with pytest.raises(LocationCapabilityError):
  propose_location_tools(ledger(),mode="POST_EVENT")

def test_ambiguous_duplicate_source_ids_rejected():
 with pytest.raises(LocationCapabilityError):
  propose_location_tools(ledger()+[ledger()[0]])
