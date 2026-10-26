"""PREP route proposal assessment, independent of post-event Master Pos and KML.

Contract-only evaluator. Requires already-produced directed graph candidates from routing
services; this module does not generate a road graph or authorize Driver cues.
"""
from decimal import Decimal, InvalidOperation
from hashlib import sha256
import json

class RouteBoundaryError(ValueError):
    pass

_FORBIDDEN_PREP_KEYS = frozenset({
    "master_pos", "master_anchors", "master_coordinates",
    "master_time", "master_pos_time", "zero_car_master_time",
    "post_event_kml", "historical_kml", "kml_trace",
    "organizer_results", "result_card", "penalty_card",
    "post_event_labels", "training_ground_truth",
})
_GENERAL_RULES = {
    "MISSING_ROADBOOK_OCCURRENCE": "REQUIRE_COMPLETE_SOURCE_COVERAGE",
    "REPEATED_SIGN_COLLAPSED": "SEPARATE_PHYSICAL_SIGN_OCCURRENCES",
    "WRONG_EDGE_OR_TURN": "ENFORCE_DIRECTED_EDGE_AND_APPROACH",
    "WRONG_CP_ACCESS": "REQUIRE_PHYSICAL_ACCESS_EDGE_EVIDENCE",
    "INCORRECT_SUB_BOUNDARY": "VERIFY_BOUNDARY_IDENTITY_AND_ORDER",
    "DISTANCE_DOMAIN_MIXED": "KEEP_OFFICIAL_GRAPH_AND_ODOMETER_SEPARATE",
    "GPS_PROXIMITY_FALSE_POSITIVE": "REQUIRE_CHRONOLOGICAL_DIRECTED_MATCH",
    "CUE_WITHOUT_EVIDENCE": "HOLD_UNVERIFIED_TURN_CUES",
    "TIMING_RULE_ERROR": "VERSION_EVENT_TIMING_RULES",
}

def _reject_post_event_data(value):
    if isinstance(value, dict):
        for key, child in value.items():
            if str(key).lower() in _FORBIDDEN_PREP_KEYS:
                raise RouteBoundaryError("POST_EVENT_DATA_FORBIDDEN_IN_PREP:" + str(key))
            _reject_post_event_data(child)
    elif isinstance(value, (list, tuple)):
        for child in value:
            _reject_post_event_data(child)

def _distance(value):
    try:
        n = Decimal(str(value))
    except (InvalidOperation, ValueError, TypeError) as exc:
        raise RouteBoundaryError("INVALID_DISTANCE") from exc
    if not n.is_finite() or n < 0:
        raise RouteBoundaryError("INVALID_DISTANCE")
    return n

def assess_pre_event_candidates(*, event_id, mode, source_ledger, candidates):
    """Ranks only source/graph candidates; never consumes an organizer Master Pos.

    Required instruction events must be represented individually by Agent 2. For example,
    'Arah Gilimanuk 2 kali' means two source occurrence IDs, not one STRAIGHT cue.
    """
    if mode not in ("PREP", "REVIEW"):
        raise RouteBoundaryError("INVALID_PRE_EVENT_MODE")
    if not isinstance(event_id, str) or not event_id.strip():
        raise RouteBoundaryError("EVENT_ID_REQUIRED")
    _reject_post_event_data(source_ledger)
    _reject_post_event_data(candidates)
    if not isinstance(source_ledger, list) or not source_ledger:
        raise RouteBoundaryError("SOURCE_LEDGER_REQUIRED")
    if not isinstance(candidates, list):
        raise RouteBoundaryError("CANDIDATES_LIST_REQUIRED")
    source_ids = [s.get("source_instruction_id") for s in source_ledger]
    if any(not isinstance(x,str) or not x for x in source_ids) or len(set(source_ids))!=len(source_ids):
        raise RouteBoundaryError("SOURCE_EVENT_OCCURRENCE_IDS_NOT_UNIQUE")
    required = [s for s in source_ledger if s.get("mandatory",True)]
    known = set(source_ids)
    sign_sources = [s for s in required if s.get("kind")=="SIGNED_DIRECTION_OCCURRENCE"]
    scored = []
    for route in candidates:
        cid = route.get("candidate_id")
        if not isinstance(cid,str) or not cid:
            raise RouteBoundaryError("CANDIDATE_ID_REQUIRED")
        bindings=route.get("bindings",[])
        if not isinstance(bindings,list):
            raise RouteBoundaryError("BINDINGS_LIST_REQUIRED")
        ids=[b.get("source_instruction_id") for b in bindings]
        if len(ids)!=len(set(ids)) or any(i not in known for i in ids):
            raise RouteBoundaryError("DUPLICATE_OR_UNKNOWN_INSTRUCTION_BINDING")
        bound={b["source_instruction_id"]: b for b in bindings}
        missing=[s["source_instruction_id"] for s in required if s["source_instruction_id"] not in bound]
        unproven=[]
        decisions=set()
        for s in required:
            b=bound.get(s["source_instruction_id"])
            if b is None:
                continue
            if not b.get("directed_edge_occurrence_id") or b.get("binding_status")!="REVIEWED":
                unproven.append(s["source_instruction_id"])
            if s.get("kind")=="SIGNED_DIRECTION_OCCURRENCE":
                decision=b.get("physical_decision_id")
                if not decision or decision in decisions:
                    unproven.append(s["source_instruction_id"])
                else:
                    decisions.add(decision)
                if b.get("sign_review_receipt") is None or not b.get("arrow_edge_reviewed"):
                    unproven.append(s["source_instruction_id"])
        graph=route.get("directed_graph_status","UNKNOWN")
        if graph not in ("CONNECTED_REVIEWED","UNKNOWN","DISCONNECTED","ACCESS_VIOLATION"):
            raise RouteBoundaryError("UNRECOGNIZED_GRAPH_STATUS")
        rejected=graph in ("DISCONNECTED","ACCESS_VIOLATION")
        residuals={}
        per_sub=route.get("distances_per_sub",{})
        if not isinstance(per_sub,dict):
            raise RouteBoundaryError("INVALID_SUB_DISTANCES")
        for sub,vals in per_sub.items():
            if "official_m" not in vals or "graph_m" not in vals:
                continue
            official=_distance(vals["official_m"])
            graph_m=_distance(vals["graph_m"])
            residuals[sub]=str(graph_m-official)
        abs_res=sum((abs(Decimal(v)) for v in residuals.values()),Decimal(0))
        errors=sorted(set(unproven))
        status="REJECTED_GRAPH_VIOLATION" if rejected else "PROPOSAL_PENDING_VALIDATION"
        # Rank proposal by hard roadbook coverage and evidence gaps; distance is secondary.
        score=(int(rejected),len(missing),len(errors),
               int(graph!="CONNECTED_REVIEWED"),abs_res,cid)
        scored.append({"candidate_id":cid,"status":status,"missing_source_ids":missing,
                       "unproven_source_ids":errors,"signed_direction_sources":len(sign_sources),
                       "distance_residual_by_sub_m":residuals,"graph_status":graph,
                       "rank_factors":{"unmapped":len(missing),"unproven":len(errors)},
                       "_score":score})
    scored.sort(key=lambda r:r["_score"])
    for row in scored:
        row.pop("_score")
    return {"event_id":event_id,"mode":mode,"master_pos_used":False,
            "release_status":"HOLD","gate_results":"NOT_RUN","ranked_candidates":scored}

def propose_post_event_lessons(*, mode, finished, frozen_prediction_sha256, findings):
    """Post-event feedback proposes *general rules*, NEVER coordinate-specific shortcuts."""
    if mode!="POST_EVENT" or finished is not True:
        raise RouteBoundaryError("POST_EVENT_NOT_AUTHORIZED")
    if not isinstance(frozen_prediction_sha256,str) or len(frozen_prediction_sha256)!=64:
        raise RouteBoundaryError("FROZEN_PRE_EVENT_PREDICTION_REQUIRED")
    try:
        int(frozen_prediction_sha256,16)
    except ValueError as exc:
        raise RouteBoundaryError("INVALID_HASH") from exc
    if not isinstance(findings,list):
        raise RouteBoundaryError("FINDINGS_LIST_REQUIRED")
    lessons=[]
    for f in findings:
        category=f.get("category")
        if category not in _GENERAL_RULES or not f.get("evidence_ref"):
            raise RouteBoundaryError("UNSUPPORTED_OR_UNSOURCED_FINDING")
        lessons.append({"rule_id":_GENERAL_RULES[category],
                        "evidence_ref":f["evidence_ref"],"status":"PROPOSED_FOR_REVIEW"})
    return {"status":"REQUIRES_HUMAN_REVIEW_AND_OUT_OF_SAMPLE_TEST",
            "frozen_prediction_sha256":frozen_prediction_sha256,
            "coordinate_values_carried":False,"lessons":lessons}
