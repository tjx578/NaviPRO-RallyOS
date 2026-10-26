"""Synthetic-only tests: no Trayek 1 Master Pos or private KML in source control."""
import sys
from pathlib import Path
import pytest
sys.path.insert(0,str(Path(__file__).resolve().parents[2]/"python"/"src"))
from navipro_rallyos.route.cue_review_contract import (
    CueContractError, distinct_signed_directions, assert_directed_occurrence_order,
    derive_cp_time, preview_cues)

def test_gilimanuk_twice_not_consecutive():
    events=[
      {"occurrence_id":"s1","kind":"SIGNED_DIRECTION_OCCURRENCE","destination":"GILIMANUK",
       "decision_id":"one","sign_evidence_reviewed":True,"arrow_out_edge_verified":True},
      {"occurrence_id":"other","kind":"INTERSECTION"},
      {"occurrence_id":"s2","kind":"SIGNED_DIRECTION_OCCURRENCE","destination":"GILIMANUK",
       "decision_id":"two","sign_evidence_reviewed":True,"arrow_out_edge_verified":True}]
    assert distinct_signed_directions(events)["verified"]==2

def test_duplicate_image_same_decision_not_two():
    events=[{"occurrence_id":str(n),"kind":"SIGNED_DIRECTION_OCCURRENCE",
      "destination":"GILIMANUK","decision_id":"same","sign_evidence_reviewed":True,
      "arrow_out_edge_verified":True} for n in (1,2)]
    assert distinct_signed_directions(events)["verified"]==1

def test_same_geo_distinct_visits_and_monotonic():
    assert assert_directed_occurrence_order([
      {"occurrence_id":"a","sub_id":"B","directed_edge_occurrence_id":"a","chainage_m":100},
      {"occurrence_id":"b","sub_id":"B","directed_edge_occurrence_id":"b","chainage_m":100}])
    with pytest.raises(CueContractError):
      assert_directed_occurrence_order([
      {"occurrence_id":"a","sub_id":"B","directed_edge_occurrence_id":"a","chainage_m":120},
      {"occurrence_id":"b","sub_id":"B","directed_edge_occurrence_id":"b","chainage_m":110}])

def test_cp_seconds_never_master_and_integer_minutes_only():
    c=derive_cp_time("2026-08-29T08:26:00+08:00",46,11050,3000,True)
    assert c["target_timestamp"].endswith("08:38:29+08:00")
    assert c["authority"]=="DERIVED_NOT_MASTER"
    assert derive_cp_time("2026-08-29T08:26:00+08:00",46,11050,3000,False)["status"]=="HOLD"
    with pytest.raises(CueContractError):
        derive_cp_time("2026-08-29T08:26:00+08:00",46.5,11050,3000,True)

def test_unverified_turn_never_sent_to_driver():
    route={"route_revision_id":"r1","status":"PROPOSAL_PENDING_VALIDATION",
      "occurrences":[{"occurrence_id":"x","sub_id":"B","source_instruction_id":"src1",
        "directed_edge_occurrence_id":"e1","chainage_m":123,"turn":"RIGHT",
        "directed_connected":True,"access_reviewed":True}]}
    result=preview_cues(route,{"route_revision_id":"r1"},{})
    assert result["cues"][0]["turn_proposal"]=="UNKNOWN"
    assert result["driver_release"]=="HOLD"
    with pytest.raises(CueContractError): preview_cues(route,{"route_revision_id":"r2"},{})
