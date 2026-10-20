# M1 ROTR Surabaya: diagnostic implementation, routing still unresolved

The fixture is a visual transcription of the supplied ROTR Ramadhan On The
Road 2025, Surabaya, 22 March 2025, Trayek 2 image. The original image is
preserved byte-for-byte in `tests/fixtures/rotr_surabaya/source.jpeg`.
SHA-256: `e51ca2d91c7cf7c8c1e0c668b65b114f0a42d08efd0ff819d191de53b929124c`.
Its filename and review status are in `source.json`. Non-routing prose was
omitted from the transcription. Human transcription review is pending.

## Implemented and locally testable

- The bounded A–E text parser retains raw text and ordered instruction occurrences.
  It is a parser for this transcription dialect, not an OCR engine or general
  natural-language parser.
- B, C and D parse as 7.57 + 5.75 + 6.28 = 19.60 km.
  A–E parse as 2 + 25 + 20 + 22 + 51 = 120 minutes.
- Three Jalan Jawa occurrences remain separate. The inline 2.93 km reference
  remains `UNKNOWN`; it is not added to the official total or treated as cumulative.
- Source POI references, physical locations and road access points are separate.
  No coordinate or road access point is claimed as confirmed.
- Diagnostic evaluation separates official distance/time from graph distance/ETA.
  It can flag missing/reordered occurrence evidence, but cannot infer traversal
  from request anchor IDs.
- The optional provider runner saves semantic requests, native JSON responses
  (including maneuvers), normalized candidates, residual comparisons, failures,
  provenance, and evidence hashes. It requires PREP/REVIEW and both providers.
  This path has not been exercised against real routing servers.

Run from the repository root with the pinned test environment:

```powershell
python -m pip install -r requirements-test.lock
python -m pytest -q
python tools/m1_benchmark.py --mode REVIEW --output .local/m1-run-001
```

Output folders must be new. Default output is `ROUTE_UNRESOLVED` and provider
status is `NOT_EXECUTED`. Arithmetic success does not validate the transcription,
timing rules, road topology, physical access or route.

## Reproducible routing preparation

`infra/routing/images.lock.json` pins Linux amd64 manifests resolved from public
GHCR on 2026-10-20: OSRM v26.4.1-debian and Valhalla 3.9.1. These versions are
chosen reproducible inputs, not a claim that they are the newest versions.

```powershell
python tools/routing_runtime.py preflight --output .local/preflight-001
```

Preflight only observes Docker. A failed engine check stops the build before
pulling images or running containers. The local host's Docker backend crashed
with `VirtualAlloc ... errno=1455` / `out of memory` on 2026-10-20. No graph build
or service deployment was completed. Host memory/pagefile settings and unrelated
containers were not modified. Build recipes remain unverified at runtime.

`tools/prepare_surabaya_osm.py --output .local/osm-001` uses `osmium==4.3.2`
in a separate preprocessing environment. It downloads a bounded, timestamped
Overpass extract and records XML/PBF/query hashes. It is an exploratory
road/name/restriction extract, not a complete regional extract. Its manifest
explicitly says `benchmark_eligible: false`: complete administrative coverage is
missing. Overpass `osm_base` is the retrieval snapshot, not the event-date map.

For actual graph building, supply a reviewed road PBF covering all possible
routes and an administrative PBF with complete relevant boundaries. Both engines
receive the same road PBF bytes. The administrative PBF is a separate auxiliary
input to Valhalla and is also hashed. No automatic global or hidden map download
occurs during the recipe.

Create a source manifest with these fields, backed by actual evidence:

```json
{
  "source_pbf_sha256": "<64 lowercase hex characters>",
  "source_url": "<actual road PBF source>",
  "osm_base": "<actual snapshot timestamp>",
  "admin_pbf_sha256": "<64 lowercase hex characters>",
  "admin_source_url": "<actual administrative PBF source>",
  "administrative_coverage": "REVIEWED_COMPLETE_FOR_SURABAYA",
  "admin_coverage_evidence": "<review artifact identifying complete boundaries>"
}
```

Then run:

```powershell
python tools/routing_runtime.py build --roads D:/data/roads.osm.pbf --admins D:/data/admin.osm.pbf --source-manifest D:/data/source.json --output .local/runtime-001
```

The recipe builds sequentially with two threads and a 4 GiB container limit,
records command logs and graph artifact hashes, and emits `compose.json` only
after both builds succeed. A memory limit is a ceiling, not a capacity guarantee.
OSRM uses the pinned image's car.lua and bundled Lua libraries; Valhalla uses
static auto costing. No timezone database is built and time-dependent routing
is not supported by this recipe.

After reviewing a successful build, start only the named project:

```powershell
docker compose -f .local/runtime-001/compose.json up -d
```

Services expose only `127.0.0.1:5000` and `127.0.0.1:8002`; graph mounts are read
only. Starting containers does not verify health or route accuracy. Do not use
project-wide or system-wide cleanup commands to manage these services.

Validate administrative coverage and left-side driving with inspectable graph
and real-response evidence before setting these runtime-manifest fields:
`benchmark_eligible: true`, `driving_side_status: VERIFIED_LEFT_HAND_TRAFFIC`,
and a nonempty `driving_side_evidence` reference. These are explicit reviewer
attestations, not automated proof or cryptographic server attestation. The build
tool leaves them unverified. Do not change them just to bypass the benchmark gate.

Candidate bindings are a JSON object keyed by section ID (B, C, D), each holding
an ordered array of objects containing `instruction_id`, integer `lat_e7`,
integer `lon_e7` and `evidence_ref`. Repeated roads need distinct occurrence IDs.
At least two anchors per requested provider route are required. Coordinates
remain candidate hypotheses until navigator review. No confirmed anchor file is
included because the source provides no confirmed coordinates.

```powershell
python tools/m1_benchmark.py --mode REVIEW --runtime-manifest .local/runtime-001/runtime-manifest.json --anchors D:/data/candidate-bindings.json --output .local/m1-real-001
```

## Remaining work

This is a deterministic parsing and diagnostic foundation, not the complete
Rally Constraint Solver. Real graph builds, provider smoke tests, road maneuver
interpretation, KM PAL semantics, directed-edge traversal/loop proof, event timing
rules, navigator confirmation, and the Page 2 map/evidence UI remain incomplete.
Neither distance equality nor six received provider responses can confirm a route.
NaviPack and Driver offline operation are outside this change.

References:

- [OSRM backend build/run documentation](https://github.com/Project-OSRM/osrm-backend)
- [Valhalla image and administrative-data documentation](https://github.com/valhalla/valhalla/blob/master/docker/README.md)
- [Geofabrik Java regional source](https://download.geofabrik.de/asia/indonesia/java.html)
- [OpenStreetMap attribution and ODbL](https://www.openstreetmap.org/copyright)
