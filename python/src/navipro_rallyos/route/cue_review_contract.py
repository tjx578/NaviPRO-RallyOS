"""Agent 4 -> Agent 7 clean-room evidence contract.
This is propose-only logic; NOT a route matcher, official clock, QG validator, or Driver runtime.
"""
from decimal import Decimal, ROUND_HALF_UP
from datetime import datetime, timedelta

class CueContractError(ValueError):
    pass

def distinct_signed_directions(events, target="GILIMANUK"):
    """Count separate evidenced physical decisions, not individual photo uploads."""
    ids = set()
    decisions = set()
    verified = 0
    for e in events:
        oid = e.get("occurrence_id")
        if not oid or oid in ids:
            raise CueContractError("DUPLICATE_OR_MISSING_OCCURRENCE_ID")
        ids.add(oid)
        if e.get("kind") != "SIGNED_DIRECTION_OCCURRENCE" or e.get("destination") != target:
            continue  # intervening intersections are legal
        decision = e.get("decision_id")
        if decision and decision not in decisions:
            decisions.add(decision)
            if e.get("sign_evidence_reviewed") is True and e.get("arrow_out_edge_verified") is True:
                verified += 1
    return {"required": 2, "verified": verified, "status": "EVIDENCE_COMPLETE" if verified == 2 else "REVIEW_REQUIRED"}

def assert_directed_occurrence_order(occurrences):
    seen = set()
    previous = {}
    for e in occurrences:
        oid = e.get("occurrence_id")
        sub = e.get("sub_id")
        edge = e.get("directed_edge_occurrence_id")
        if not oid or oid in seen or not sub or not edge:
            raise CueContractError("MISSING_ROUTE_OCCURRENCE_IDENTITY")
        seen.add(oid)
        if e.get("chainage_m") is None:
            raise CueContractError("MISSING_CHAINAGE")
        pos = Decimal(str(e["chainage_m"]))
        if not pos.is_finite() or pos < 0:
            raise CueContractError("INVALID_CHAINAGE")
        if sub in previous and pos < previous[sub]:
            raise CueContractError("NON_MONOTONIC_CHAINAGE")
        previous[sub] = pos
    return True

def derive_cp_time(start_timestamp, duration_minutes, authority_distance_m, cp_offset_m,
                   official_distance_reconciled=False):
    """Return mathematical estimate, not an official Master Pos time."""
    if not official_distance_reconciled:
        return {"status": "HOLD", "target_timestamp": None}
    if type(duration_minutes) is not int or duration_minutes <= 0:
        raise CueContractError("DURATION_NOT_INTEGER_MINUTES")
    t = datetime.fromisoformat(start_timestamp)
    if t.utcoffset() is None:
        raise CueContractError("MISSING_TIME_ZONE")
    whole = Decimal(str(authority_distance_m))
    part = Decimal(str(cp_offset_m))
    if not whole.is_finite() or not part.is_finite() or whole <= 0 or part < 0 or part > whole:
        raise CueContractError("INVALID_OFFICIAL_DISTANCE_BINDING")
    sec = (part / whole * Decimal(duration_minutes * 60)).quantize(Decimal("1"), rounding=ROUND_HALF_UP)
    return {"status": "DERIVED_CP_TARGET_SECOND", "authority": "DERIVED_NOT_MASTER",
            "target_timestamp": (t + timedelta(seconds=int(sec))).isoformat()}

def preview_cues(route_proposal, timing_revision, physical_evidence):
    """Never return actionable directions or QG PASS based on AI/self-declared status."""
    rid = route_proposal.get("route_revision_id")
    if not rid or route_proposal.get("status") != "PROPOSAL_PENDING_VALIDATION" or timing_revision.get("route_revision_id") != rid:
        raise CueContractError("ROUTE_TIMING_REVISION_MISMATCH")
    occurrences = route_proposal.get("occurrences", [])
    assert_directed_occurrence_order(occurrences)
    cues = []
    for e in occurrences:
        reviewed = physical_evidence.get(e["occurrence_id"], {})
        eligible = bool(e.get("directed_connected") is True and e.get("access_reviewed") is True
                        and e.get("turn") in ("LEFT", "RIGHT", "STRAIGHT", "UTURN", "ARRIVE")
                        and reviewed.get("status") == "REVIEWED" and reviewed.get("receipt"))
        cues.append({"occurrence_id": e["occurrence_id"], "sub_id": e["sub_id"],
                     "source_instruction_id": e.get("source_instruction_id"),
                     "chainage_m": e["chainage_m"], "turn_proposal": e.get("turn") if eligible else "UNKNOWN",
                     "quality": "REVIEW_READY" if eligible else "HOLD_UNVERIFIED",
                     "driver_release": "HOLD", "master_time": None})
    return {"route_revision_id": rid, "status": "PROPOSE_ONLY", "gate_results": "NOT_RUN",
            "driver_release": "HOLD", "cues": cues}
