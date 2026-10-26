"""TRAINING_POST_EVENT-only authoritative Master Pos -> observed KML geo matching.

Pure Python, no private coordinates; proximity and time DO NOT validate a legal turn or roadbook route.\nA caller must explicitly supply historical mode and a nonempty finish receipt; only the external orchestrator can authenticate that receipt.
"""
from bisect import bisect_right
from math import atan2, cos, radians, sin, sqrt

class AnchorError(ValueError):
    pass

def haversine_m(lat1, lon1, lat2, lon2):
    p1, p2 = radians(float(lat1)), radians(float(lat2))
    dp, dl = p2-p1, radians(float(lon2)-float(lon1))
    v = sin(dp/2)**2 + cos(p1)*cos(p2)*sin(dl/2)**2
    return 2*6371008.8*atan2(sqrt(v), sqrt(max(0, 1-v)))

def match_master_anchors(masters, trace, mode=None, radius_m=30.0, finish_receipt=None):
    """Min-cost monotonic match of EVERY master anchor to one chrono GPS sample.

    masters: [{id,lat,lon},...] in official order
    trace: [{lat,lon,time},...] in strictly increasing time.
    radius_m: only a search diagnostic, NEVER a QG pass/review threshold.
    """
    if mode != "TRAINING_POST_EVENT" or not finish_receipt:
        raise AnchorError("MASTER_POS_LEAKAGE_FORBIDDEN")
    if not masters or len(trace) < len(masters):
        raise AnchorError("MISSING_ANCHOR_OR_TRACE")
    if not 0 < radius_m <= 100:
        raise AnchorError("INVALID_DIAGNOSTIC_SEARCH_RADIUS")
    if any(trace[i]["time"] >= trace[i+1]["time"] for i in range(len(trace)-1)):
        raise AnchorError("TRACE_NOT_STRICTLY_CHRONOLOGICAL")
    if len({m["id"] for m in masters}) != len(masters):
        raise AnchorError("DUPLICATE_MASTER_ID")
    previous = []
    for k, master in enumerate(masters):
        candidates = []
        for index, point in enumerate(trace):
            distance = haversine_m(master["lat"], master["lon"], point["lat"], point["lon"])
            if distance <= radius_m:
                candidates.append((index, distance))
        if not candidates:
            raise AnchorError("MASTER_UNMATCHED:" + master["id"])
        next_layer = []
        best_score, best_node, pointer = float("inf"), None, 0
        for index, distance in candidates:
            if k == 0:
                next_layer.append((index, distance, None, distance))
            else:
                while pointer < len(previous) and previous[pointer][0] < index:
                    if previous[pointer][1] < best_score:
                        best_score, best_node = previous[pointer][1], previous[pointer]
                    pointer += 1
                if best_node is not None:
                    next_layer.append((index, best_score+distance, best_node, distance))
        if not next_layer:
            raise AnchorError("MASTER_ORDER_CANNOT_BE_MATCHED:" + master["id"])
        previous = next_layer
    chain = []
    node = min(previous, key=lambda item: item[1])
    while node is not None:
        chain.append(node)
        node = node[2]
    chain.reverse()
    if len(chain) != len(masters):
        raise AnchorError("INCOMPLETE_MASTER_CHAIN")
    return [{**dict(master), "trace_index": match[0],
             "near_m": round(match[3], 2),
             "observed_time": trace[match[0]]["time"],
             "match_status": "GEO_PROXIMITY_POST_EVENT_ONLY"}
            for master, match in zip(masters, chain)]

def master_bracket(matches, trace_index, mode=None):
    if mode != "TRAINING_POST_EVENT":
        raise AnchorError("MASTER_POS_LEAKAGE_FORBIDDEN")
    indices = [m["trace_index"] for m in matches]
    if indices != sorted(indices) or len(indices) != len(set(indices)):
        raise AnchorError("MASTER_MATCH_CHAIN_NOT_MONOTONE")
    pos = bisect_right(indices, int(trace_index))
    if pos and indices[pos-1] == trace_index:
        ref = matches[pos-1]["id"]
        return {"anchor_id":ref, "before":ref, "after":ref,
                "status":"MASTER_ANCHOR_AT_TRACE_POINT"}
    if not pos or pos == len(indices):
        return {"anchor_id":None,
                "before":matches[pos-1]["id"] if pos else None,
                "after":matches[pos]["id"] if pos<len(indices) else None,
                "status":"OUTSIDE_MASTER_ENVELOPE"}
    return {"anchor_id":None, "before":matches[pos-1]["id"],
            "after":matches[pos]["id"], "status":"BETWEEN_OFFICIAL_MASTER_ANCHORS"}

def bind_cue_to_master(cue, master, allow_historical_alias=False, mode=None, finish_receipt=None):
    """Historical candidate identity association; not a reviewed graph/turn binding."""
    if mode != "TRAINING_POST_EVENT" or not finish_receipt:
        raise AnchorError("MASTER_POS_LEAKAGE_FORBIDDEN")
    kind = cue.get("CueType", "").upper()
    label = (cue.get("LandmarkName") or "").casefold()
    description = (master.get("description") or "").casefold()
    same_identity = (
        (kind == "START" and master["id"] == "START" and cue.get("SubTrayek") == "A")
        or (kind in ("FINISH", "START") and
            "perbekel banjar" in label and "perbekel banjar" in description)
        or (kind == "FINISH" and cue.get("SubTrayek") == "H"
            and master["id"] == "FINISH" and "krisna" in label and "krisna" in description)
    )
    if not same_identity:
        return {"status":"NOT_SAME_SOURCE_IDENTITY","master_id":None}
    if not allow_historical_alias:
        return {"status":"REVIEW_REQUIRED_TO_BIND","master_id":master["id"]}
    return {"status":"POST_EVENT_MASTER_LOCATION_REFERENCE", "master_id":master["id"],
            "lat":master["lat"],"lon":master["lon"],
            "cue_direction":"UNKNOWN", "driver_release":"HOLD"}
