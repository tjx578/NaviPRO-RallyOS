"""NaviPRO route legal-access preliminary policy; advisory, not road-law certification."""
MOTOR_DENY = frozenset(("footway","path","steps","cycleway","pedestrian","bridleway","corridor","construction","proposed","platform","raceway"))
ACCESS_DENY = frozenset(("private","no"))
def classify_osm_segment(highway: str, tags: dict) -> str:
    if highway in MOTOR_DENY:
        return "BLOCK_HIGHWAY"
    if any(tags.get(key) in ACCESS_DENY for key in ("motor_vehicle","motorcar","vehicle","access")):
        return "BLOCK_ACCESS"
    return "CANDIDATE_ONLY"
def release_decision(authoritative_gates, authenticated_review, same_revision: bool) -> str:
    """A candidate cannot be released by this module. Always HOLD."""
    return "HOLD"
