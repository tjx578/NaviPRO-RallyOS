"""Blind routing contract: all examples synthetic, NO organizer Master or KML."""
import sys
from pathlib import Path
import pytest
sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "python" / "src"))
from navipro_rallyos.route.pre_event_route_workflow import (
    RouteBoundaryError, assess_pre_event_candidates, propose_post_event_lessons)

def ledger():
    return [
        {"source_instruction_id":"S1","kind":"SIGNED_DIRECTION_OCCURRENCE",
         "destination":"GILIMANUK","mandatory":True},
        {"source_instruction_id":"J","kind":"INTERSECTION","mandatory":False},
        {"source_instruction_id":"S2","kind":"SIGNED_DIRECTION_OCCURRENCE",
         "destination":"GILIMANUK","mandatory":True},
        {"source_instruction_id":"CP","kind":"LANDMARK","mandatory":True}
    ]

def bindings():
    return [
      {"source_instruction_id":"S1","directed_edge_occurrence_id":"e1",
       "binding_status":"REVIEWED","physical_decision_id":"board1",
       "sign_review_receipt":"receipt1","arrow_edge_reviewed":True},
      {"source_instruction_id":"S2","directed_edge_occurrence_id":"e7",
       "binding_status":"REVIEWED","physical_decision_id":"board2",
       "sign_review_receipt":"receipt2","arrow_edge_reviewed":True},
      {"source_instruction_id":"CP","directed_edge_occurrence_id":"e9",
       "binding_status":"REVIEWED"}
    ]

def candidate(cid="c1",bs=None):
    return {"candidate_id":cid,
      "directed_graph_status":"CONNECTED_REVIEWED",
      "bindings":bindings() if bs is None else bs,
      "distances_per_sub":{"B":{"official_m":7120,"graph_m":7100},
                           "C":{"official_m":11050,"graph_m":11090}}}

def evaluate(candidates):
    return assess_pre_event_candidates(event_id="SYNTHETIC_NEW_RALLY",
           mode="PREP",source_ledger=ledger(),candidates=candidates)

def test_pre_event_no_master_required():
    r=evaluate([candidate()])
    assert r["master_pos_used"] is False
    assert r["release_status"]=="HOLD"
    assert r["gate_results"]=="NOT_RUN"
    assert r["ranked_candidates"][0]["missing_source_ids"]==[]
    assert r["ranked_candidates"][0]["signed_direction_sources"]==2

def test_two_signs_not_adjacent_still_counted():
    c=candidate()
    assert len(c["bindings"])==3 and len(ledger())==4
    assert evaluate([c])["ranked_candidates"][0]["unproven_source_ids"]==[]

def test_same_sign_two_photos_does_not_count_twice():
    b=bindings()
    b[1]["physical_decision_id"]="board1"
    r=evaluate([candidate(bs=b)])
    assert "S2" in r["ranked_candidates"][0]["unproven_source_ids"]

def test_no_default_false_straight_or_missing_cp():
    b=bindings()[:2]
    r=evaluate([candidate(bs=b)])
    assert "CP" in r["ranked_candidates"][0]["missing_source_ids"]
    assert r["release_status"]=="HOLD"

def test_missing_landmark_more_important_than_distance():
    bad=candidate("bad",bindings()[:2])
    bad["distances_per_sub"]={"B":{"official_m":7120,"graph_m":7120}}
    good=candidate("good")
    r=evaluate([bad,good])
    assert r["ranked_candidates"][0]["candidate_id"]=="good"

def test_residual_kept_by_sub_not_cancelled():
    r=evaluate([candidate()])["ranked_candidates"][0]
    assert r["distance_residual_by_sub_m"]=={"B":"-20","C":"40"}

def test_graph_access_violation_rejected():
    c=candidate()
    c["directed_graph_status"]="ACCESS_VIOLATION"
    assert evaluate([c])["ranked_candidates"][0]["status"]=="REJECTED_GRAPH_VIOLATION"

@pytest.mark.parametrize("field",["master_pos","historical_kml","result_card","zero_car_master_time"])
def test_forbidden_ground_truth_rejected_in_nested_payload(field):
    c=candidate()
    c["metadata"]={"nested":{field:"secret"}}
    with pytest.raises(RouteBoundaryError,match="POST_EVENT_DATA_FORBIDDEN_IN_PREP"):
        evaluate([c])

def test_no_ground_truth_accepted_as_prep_mode():
    with pytest.raises(RouteBoundaryError,match="INVALID_PRE_EVENT_MODE"):
        assess_pre_event_candidates(event_id="SYNTH",mode="POST_EVENT",
                                    source_ledger=ledger(),candidates=[])

def test_post_event_requires_frozen_prediction():
    with pytest.raises(RouteBoundaryError,match="POST_EVENT_NOT_AUTHORIZED"):
        propose_post_event_lessons(mode="PREP",finished=True,
           frozen_prediction_sha256="a"*64,findings=[])

def test_post_event_generates_transferable_rule_not_coordinate():
    r=propose_post_event_lessons(mode="POST_EVENT",finished=True,
       frozen_prediction_sha256="b"*64,
       findings=[{"category":"REPEATED_SIGN_COLLAPSED","evidence_ref":"T1_RB_SIGN_EVIDENCE"},
                 {"category":"WRONG_CP_ACCESS","evidence_ref":"T1_FIELD_ACCESS_REVIEW"}])
    assert r["lessons"][0]["rule_id"]=="SEPARATE_PHYSICAL_SIGN_OCCURRENCES"
    assert r["coordinate_values_carried"] is False
    assert r["status"]=="REQUIRES_HUMAN_REVIEW_AND_OUT_OF_SAMPLE_TEST"

def test_unsourced_post_event_finding_rejected():
    with pytest.raises(RouteBoundaryError,match="UNSUPPORTED_OR_UNSOURCED_FINDING"):
        propose_post_event_lessons(mode="POST_EVENT",finished=True,
           frozen_prediction_sha256="c"*64,
           findings=[{"category":"WRONG_EDGE_OR_TURN"}])
