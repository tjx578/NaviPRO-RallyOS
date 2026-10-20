"""Safe context-fusion planning: pure functions, no external network calls or route mutations.

Third-party provider allowlisting is server-trusted; client observations cannot authorize their own source.
"""
from datetime import datetime, timezone
from typing import Mapping

ALLOWED_KINDS = frozenset({
    "WEATHER_OBSERVED", "WEATHER_FORECAST", "AIR_QUALITY", "TERRAIN", "IMAGERY",
    "EARTHQUAKE", "AGGREGATE_TRAFFIC", "GEOJSON_ANNOTATION", "RECORDED_ROUTE"
})
ALLOWED_MODES = frozenset({"PREP", "REVIEW"})
LAYER_FIELDS = frozenset({"source_id", "kind", "observed_at", "issued_at", "valid_until"})
PLAN_FIELDS = frozenset({"mode", "route_revision_id", "official_anchor_ids", "layers"})

class ContextGateError(ValueError):
    """An input or source failed a context-only admission policy."""


def _utc_timestamp(value, name):
    if not isinstance(value, str) or not value:
        raise ContextGateError(f"{name} must be an ISO8601 UTC timestamp")
    try:
        parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
    except ValueError as exc:
        raise ContextGateError(f"{name} invalid") from exc
    if parsed.tzinfo is None or parsed.utcoffset() is None:
        raise ContextGateError(f"{name} must have timezone")
    return parsed.astimezone(timezone.utc)


def _id(value, name):
    if not isinstance(value, str) or not (0 < len(value) <= 128):
        raise ContextGateError(f"{name} must be nonempty and <=128 characters")
    return value


def _official_snapshot(snapshot):
    if not isinstance(snapshot, dict) or set(snapshot) != {"route_revision_id", "official_anchor_ids"}:
        raise ContextGateError("trusted route snapshot missing or malformed")
    revision = _id(snapshot["route_revision_id"], "route_revision_id")
    anchors = snapshot["official_anchor_ids"]
    if not isinstance(anchors, list) or len(anchors) < 2 or len(anchors) > 500:
        raise ContextGateError("trusted anchor list must have 2..500 anchors")
    for a in anchors:
        _id(a, "official anchor ID")
    if len(anchors) != len(set(anchors)):
        raise ContextGateError("duplicate official anchor ID")
    return revision, tuple(anchors)


def _source_record(source_id, kind, trusted_catalog):
    if not isinstance(trusted_catalog, Mapping):
        raise ContextGateError("trusted catalog required")
    record = trusted_catalog.get(source_id)
    if not isinstance(record, Mapping):
        raise ContextGateError(f"untrusted source: {source_id}")
    if record.get("kind") != kind:
        raise ContextGateError("source kind mismatch")
    if record.get("terms_approved") is not True or record.get("data_rights_reviewed") is not True:
        raise ContextGateError("source terms have not been approved")
    maximum_age = record.get("max_age_seconds")
    if type(maximum_age) is not int or not 1 <= maximum_age <= 31_536_000:
        raise ContextGateError("trusted max_age_seconds invalid")
    attribution = record.get("attribution")
    if not isinstance(attribution, str) or not attribution.strip():
        raise ContextGateError("trusted attribution required")
    return record


def assess_layers(observations, *, trusted_catalog, as_of):
    """Read-only layer status with provenance and no inferred authoritative truth."""
    now = _utc_timestamp(as_of, "as_of")
    if not isinstance(observations, list) or len(observations) > 100:
        raise ContextGateError("layer count must be <=100")
    out, seen = [], set()
    for item in observations:
        if not isinstance(item, dict) or set(item) - LAYER_FIELDS or not {"source_id", "kind", "observed_at"} <= set(item):
            raise ContextGateError("malformed layer observation or forbidden extra fields")
        source_id = _id(item["source_id"], "source_id")
        kind = item["kind"]
        if not isinstance(kind, str) or kind not in ALLOWED_KINDS:
            raise ContextGateError("disallowed context kind")
        if source_id in seen:
            raise ContextGateError("duplicate source in context scene")
        seen.add(source_id)
        source = _source_record(source_id, kind, trusted_catalog)
        at = _utc_timestamp(item["observed_at"], "observed_at")
        if at > now:
            raise ContextGateError("future observed_at")
        age_seconds = int((now - at).total_seconds())
        if "issued_at" in item:
            issued = _utc_timestamp(item["issued_at"], "issued_at")
            if issued > now or issued > at:
                raise ContextGateError("invalid issuance timestamp")
        valid_until = None
        if "valid_until" in item:
            valid_until = _utc_timestamp(item["valid_until"], "valid_until")
            if valid_until < at:
                raise ContextGateError("valid_until before observation")
        if kind == "WEATHER_FORECAST" and ("issued_at" not in item or valid_until is None):
            raise ContextGateError("forecast requires issued_at and valid_until")
        stale = age_seconds > source["max_age_seconds"] or (valid_until is not None and valid_until < now)
        out.append({
            "source_id": source_id, "kind": kind, "observed_at": at.isoformat().replace('+00:00','Z'),
            "freshness": "STALE" if stale else "CURRENT", "age_seconds": age_seconds,
            "attribution": source["attribution"], "route_authority": False,
            "data_status": "CONTEXT_ONLY", "model_status": str(source.get("model_status", "SOURCE_REPORTED"))
        })
    return {"status": "CONTEXT_ONLY", "route_authority": False, "as_of": now.isoformat().replace('+00:00','Z'), "layers": out}


def plan_scene(request, *, trusted_route_snapshot, trusted_catalog, as_of):
    """Construct a non-authoritative review scene while preserving trusted anchors."""
    if not isinstance(request, dict) or set(request) != PLAN_FIELDS:
        raise ContextGateError("unexpected scene plan keys or missing keys")
    if request["mode"] not in ALLOWED_MODES:
        raise ContextGateError("scene fusion is PREP/REVIEW only")
    revision, trusted_anchors = _official_snapshot(trusted_route_snapshot)
    if request["route_revision_id"] != revision:
        raise ContextGateError("route revision mismatch")
    anchors = request["official_anchor_ids"]
    if not isinstance(anchors, list) or anchors != list(trusted_anchors):
        raise ContextGateError("source order mismatch")
    sources = assess_layers(request["layers"], trusted_catalog=trusted_catalog, as_of=as_of)
    return {
        "status": "DRAFT_CONTEXT_SCENE", "mode": request["mode"],
        "route_revision_id": revision, "official_anchor_ids": list(trusted_anchors),
        "route_authority": False, "confirmed": False,
        "as_of": sources["as_of"], "layers": sources["layers"],
        "warnings": ["External context does not verify roads, KM PAL, distance or timing."] + [
            f"STALE:{l['source_id']}" for l in sources["layers"] if l["freshness"] == "STALE"
        ],
    }
