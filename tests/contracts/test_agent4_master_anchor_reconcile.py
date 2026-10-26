"""Synthetic tests only: no private Master Pos or KML is shipped to source control."""
import sys
from pathlib import Path
import pytest
sys.path.insert(0,str(Path(__file__).resolve().parents[2]/"python"/"src"))
from navipro_rallyos.route.master_anchor_reconcile import (
    AnchorError, match_master_anchors, master_bracket, bind_cue_to_master
)

@pytest.fixture
def synthetic():
    return (
        [{"id":"P1","lat":-8.0,"lon":115.0},
         {"id":"P2","lat":-8.02,"lon":115.02}],
        [{"lat":-8.0,"lon":115.0,"time":1},
         {"lat":-8.01,"lon":115.01,"time":2},
         {"lat":-8.02,"lon":115.02,"time":3}]
    )

def test_ordered_anchors(synthetic):
    masters, trace=synthetic
    result=match_master_anchors(masters,trace,mode="TRAINING_POST_EVENT",finish_receipt="POST_FINISH_SOURCE_RECEIPT")
    assert [m["trace_index"] for m in result] == [0,2]
    assert master_bracket(result,1,mode="TRAINING_POST_EVENT")["before"]=="P1"
    assert master_bracket(result,1,mode="TRAINING_POST_EVENT")["after"]=="P2"

def test_no_partial_pass_when_anchor_missing(synthetic):
    masters,trace=synthetic
    with pytest.raises(AnchorError,match="MASTER_UNMATCHED"):
        match_master_anchors(masters+[{"id":"UNKNOWN","lat":-9.0,"lon":115}],trace,mode="TRAINING_POST_EVENT",finish_receipt="POST_FINISH_SOURCE_RECEIPT")

def test_ground_truth_never_in_prep(synthetic):
    with pytest.raises(AnchorError,match="MASTER_POS_LEAKAGE_FORBIDDEN"):
        match_master_anchors(*synthetic,mode="PREP")

def test_unsorted_gps_rejected(synthetic):
    masters,trace=synthetic
    with pytest.raises(AnchorError,match="CHRONOLOGICAL"):
        match_master_anchors(masters,trace[::-1],mode="TRAINING_POST_EVENT",finish_receipt="POST_FINISH_SOURCE_RECEIPT")

def test_same_master_as_sub_transition_does_not_authorize_turn():
    master={"id":"PR8","description":"Perbekel Banjar","lat":-8.2,"lon":115.0}
    f=bind_cue_to_master({"CueType":"FINISH","SubTrayek":"F","LandmarkName":"Kantor Perbekel Banjar"},master,True,mode="TRAINING_POST_EVENT",finish_receipt="POST_FINISH_SOURCE_RECEIPT")
    g=bind_cue_to_master({"CueType":"START","SubTrayek":"G","LandmarkName":"Kantor Perbekel Banjar"},master,True,mode="TRAINING_POST_EVENT",finish_receipt="POST_FINISH_SOURCE_RECEIPT")
    assert f["master_id"]==g["master_id"]=="PR8"
    assert f["cue_direction"]==g["cue_direction"]=="UNKNOWN"
    assert f["driver_release"]=="HOLD"

def test_unsourced_name_cannot_bind_to_master():
    master={"id":"PR8","description":"Perbekel Banjar","lat":-8.2,"lon":115.0}
    bad=bind_cue_to_master({"CueType":"FINISH","SubTrayek":"F","LandmarkName":"Polsek Banjar"},master,True,mode="TRAINING_POST_EVENT",finish_receipt="POST_FINISH_SOURCE_RECEIPT")
    assert bad["master_id"] is None

def test_master_location_reference_requires_separate_review():
    master={"id":"FINISH","description":"Krisna Oleh Oleh","lat":-8.0,"lon":115.0}
    cue={"CueType":"FINISH","SubTrayek":"H","LandmarkName":"Krisna Oleh-Oleh Khas Bali Temukus"}
    assert bind_cue_to_master(cue,master,mode="TRAINING_POST_EVENT",finish_receipt="POST_FINISH_SOURCE_RECEIPT")["status"]=="REVIEW_REQUIRED_TO_BIND"

def test_master_helpers_fail_closed_without_finish_receipt(synthetic):
    masters,trace=synthetic
    with pytest.raises(AnchorError,match="MASTER_POS_LEAKAGE_FORBIDDEN"):
        match_master_anchors(masters,trace)
    with pytest.raises(AnchorError,match="MASTER_POS_LEAKAGE_FORBIDDEN"):
        match_master_anchors(masters,trace,mode="TRAINING_POST_EVENT")
    with pytest.raises(AnchorError,match="MASTER_POS_LEAKAGE_FORBIDDEN"):
        bind_cue_to_master({"CueType":"START","SubTrayek":"A","LandmarkName":"Start"},
                           {"id":"START","lat":-8.0,"lon":115.0})
