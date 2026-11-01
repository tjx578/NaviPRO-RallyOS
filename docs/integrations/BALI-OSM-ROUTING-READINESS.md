# Bali OSM routing — staged integration (2026-11-01)
Status: PROTOTYPE_GRAPH_BUILT_LOCALLY / OSRM_NOT_BUILT / NOT_DEPLOYED / RELEASE_HOLD

Source: uploaded BBBike OSM GeoPackage extract, 2026-11-01; NaviPRO boundary-clipped reference SQLite. Full source and graph **are not included in this Git branch** due to file size and independent license/provenance requirements.

Measured local graph extraction (endpoints/segments, not a routed OSRM graph):
- 1,203,288 unique coordinate nodes
- 1,235,286 directedness-tagged segments, one record per geometry segment; direction may be bidirectional
- 1,076,162 CANDIDATE_ONLY, 92,412 BLOCK_HIGHWAY and 66,712 BLOCK_ACCESS segments
- OSM turn restriction relations NOT imported; OSM interchanges/bridges/edge topology NOT validated.
- No authenticated release, reviewer authorization or Driver runtime integration.

TomTom comparisons (provider estimates only; not event-authoritative):
- A partial via 4 observed POI coordinates: 6,482 m; **not** full Sub A official 15.8 km.
- C partial via 3 observed POI coordinates: 3,728 m; **not** full Sub C official 10.6 km.
- Provider routing alone cannot confirm mandatory BKR/BKN, LR, 30 km/h DKT or race legality.

Required engineering work:
1. Acquire the **raw .osm.pbf** from an authorized OSM provider. A GeoPackage export with no relation turn restrictions is insufficient for full OSRM turn-aware correctness.
2. Build separately with pinned OSRM version and car.lua: `osrm-extract bali.osm.pbf -p car.lua`, then `osrm-partition`, `osrm-customize`, and `osrm-routed --algorithm mld`.
3. Apply versioned roadbook constraint solver on ordered event occurrences; no TSP or route reordering.
4. Bind source/graph/location/timing/restriction hashes; record graph/profile version, one-way and access at each road movement; unknown => HOLD.
5. Run all 16 authoritative quality gates against frozen revision, authenticated human review, and separate release-manager publication.
6. Reconcile actual deployment environment and credentialed storage. The current available Supabase project is unrelated/inactive; no production DB selected; Railway listing requires user authorization.

See `tools/bali_routing/guard.py` for negative policy smoke checks. This is not an OSRM routing server or authorization engine.
