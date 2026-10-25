# NaviPRO RallyOS — Five-Surface Cockpit Architecture SSOT v1

**Platform amendment (2026-10-25):** [ADR-0001](ADR-0001-HYBRID-PLATFORMS.md) selects Navigator Web/PWA and Driver Android Native. The original source digest records the historical design input, not this amended registry. UI and delivery remain DESIGN_ONLY.

**Decision:** 2026-10-20 | **State:** SPECIFIED / DESIGN_ONLY / NOT_RACE_READY.

## Evidence basis and authority

1. Primary visual/behavioral source: `NaviPRO_RallyOS_Map_OS_Specification_v3.0.docx` (Document ID `NAVIPRO-MAPOS-COCKPIT-UNIFIED-V3.0`, dated 2026-09-03; SHA-256 `74594f143481b953e9fb8b62486069f3244eb83627b650d368e8780e020d1c5a`). Document is a project attachment and is **not** silently installed in this repository.
2. Domain invariant: `docs/architecture/ROUTE-DISTANCE-TIME-PHYSICAL-LOCATION-SSOT-v1.md`; official roadbook route, official distance/KM PAL, and governed time **jointly constrain** routing.
3. Repo baseline: `docs/source-notes/NaviPRO_RallyOS_Repo_Skeleton_Blueprint_v1.md` and current source tree; the published skeleton supplies app/layer boundaries but **no working Android app**.
4. Approved visual mockups are embedded in the v3.0 DOCX; images are design references and contain sample numbers, not measured telemetry or a functioning UI.

**Design conflict resolution:** the Driver mockups still depict a **“Kirim Link Driver”** button. V3.0 §7.1 and §16.4 explicitly prohibit all sending/editing controls on Driver, so **remove this button from both Driver modes**. Navigator Page 2 owns the send action. Do not port visual mockup labels literally where they contradict functional governance.

## One navigator app, one driver app — five UI surfaces

| UI surface | Platform entry and feature owner | Responsibility | Trust/mode |
|---|---|---|---|
| **Page 1 — Data Rally** | `apps/navigator-web` → `apps/navigator-web/features/data-rally` | Intake photo/text roadbook, OCR review, starting list, briefing evidence, sub timing, numeric speed and schedule; send plan to external TSD Cadencer with ACK | Navigator PREP/REVIEW, guarded CONFIRMED start override; LIVE read-only |
| **Page 2 — Offline Map & Route Editor** | Navigator → `apps/navigator-web/features/offline-map-editor` | Per-sub source-order list + offline map + evidence, create reviewed draft edits, calculate graph/time discrepancies, confirm under gates and send signed NaviPack to Driver | Navigator PREP/REVIEW edit; CONFIRMED locked; LIVE no active route mutation |
| **Page 3 — NaviPRO Rally Agent** | Navigator → `apps/navigator-web/features/rally-agent` | Voice/chat, local/external candidate search, explain evidence, proposal to Page 2 via allowlisted MCP tools | PREP/REVIEW propose-only; generative agent disabled LIVE |
| **Driver 1 — Overview** | `android/apps/driver` → `android/features/driver-runtime/overview` | Full selected sub, start/finish, primary POIs, ordered cue list, TSD read-only status | Separate Driver role; signed confirmed NaviPack; default overview |
| **Driver 2 — Driving Mode** | Driver → `android/features/driver-runtime/driving` | Course-up lower-third look-ahead, next turn, cue FSM, building/landmark OSM at high zoom, off-route freeze, read-only TSD | LIVE read-only deterministic runtime |

The Navigator app uses **horizontal swipe with three indicators (1/3, 2/3, 3/3)**; map/marker gestures must not swipe the page. Driver 1/2 use a **mode toggle**, **not** navigator Page 4/5 or independent driver applications. Baseline shell is landscape 16:9, Indonesian UI, official NaviPRO brand, minimum touch targets 48 CSS px (Web) / dp (Android); critical actions 56 CSS px / dp. No “Muted Cockpit Style” label.

## Source-to-driver data flow and bounded authority

```text
PDF/photo/text + starting list + briefing + event timing rules
  │
  ▼  Page 1 Data Rally (source bytes preserved; OCR human reviewed)
Canonical Roadbook IR + SubTimingPlan (D_auth + rule version + start schedule)
  │                           └─ TSD plan envelope → external TSD Cadencer → ACK
  ▼
Page 2 Offline Map & Route Editor ← Page 3 propose-only evidence/candidate inbox
  │                          ↑                │
  │                          └─ local POI/OSM/Humanitarian/imagery review
  ├─ OSM directed graph/OSRM candidate D_graph (never D_auth)
  ├─ Human-reviewed route draft/revision; original source/order retained
  └─ Quality gates → authenticated navigator confirmation → release/signing
             │
             ▼ Signed confirmed NaviPack + transfer receipt/Driver ACK
       Driver runtime: shared verified data, no live OSRM/MCP/OCR/network
          ├─ Driver 1 Overview
          └─ Driver 2 Driving → cue FSM / sensor / TSD read-only adapter
```

No derived distance or time result becomes official merely because its arithmetic is consistent. Keep `D_auth`, `D_graph`, `D_odo`, and `D_geo` separate; store mm/ms/E7 integers and provenance. **TSD Cadencer is an external independent system**; NaviPRO sends a versioned plan and must not claim ACK before receipt.

## Page-level view composition and actions

### Page 1 — Data Rally

- Left: foto soal / OCR review. Middle top: jam start/no. start Manual/Auto. Right top: **Jadwal Mulai Sub Trayek** + mode in *Ket.*. Bottom: numeric distance, **calculated km/jam**, duration, start–finish. Footer: **Kirim ke TSD Cadencer** with `NOT_READY / READY / SENDING / ACKED / QUEUED_OFFLINE / REJECTED`.
- Manual start overrides Auto while active; new verified starting list auto-updates only when Auto selected. Briefing is hidden evidence, not a permanent extra panel. On start change, recalculate all following sub schedules, not roadbook distance or duration.
- Broken/ambiguous OCR, source-order loss, missing time-rule version or unknown start list blocks send; timing needs event/regulation evidence. Section-level timing modes remain distinct: `TETAP_DETIK`, `TETAP_MENIT`, `RATA_RATA`, `BEBAS`.

### Page 2 — Offline Map & Route Editor

- Independently scrollable left list of subs and middle list of **raw ordered steps**. Header right displays **selected sub** metrics; map draws **selected sub only**. Step↔map feature highlight is bidirectional.
- Add by text/map click, selection, draft insert/delete/undo, reroute **affected legs only**. Edits never rewrite original OCR/source bytes or source sequence: store an interpretation binding plus new `RouteRevision` draft and change receipt. Deleting a mandatory source binding forces `HOLD_SOURCE_COVERAGE` until resolved, never silent removal.
- Confirmation only via navigator review and all applicable mandatory gates; export/sending requires signed NaviPack and driver ACK. Google link-out is non-authoritative and only uses human-verified physical anchors, preserves ordered waypoints, and honors provider limits; unavailable offline.
- Page 2 hosts/consumes **one routing review experience**. Existing `apps/routing-lab-web/` is a policy/state prototype, `apps/map-lab-web/` and `apps/terrain-lab-web/` are supporting PREP/REVIEW tools, **not extra Navigator pages**.

### Page 3 — NaviPRO Rally Agent

- Chat/voice, result sources, provenance, ambiguity, evidence requests and **Kirim ke Page 2** for a specific sub. It does not itself edit, verify, confirm, send to Driver or TSD, or publish a pack.
- Use the **same canonical OpenAPI** as REST and generated MCP allowlist; `services/mcp/generated-tool-registry.yaml` is definition-only, **not a running MCP server**. Local curated database searches survive internet loss; external services clearly become unavailable.

### Driver 1 and Driver 2 (shared Driver runtime)

- Both load the **same immutable, checked, confirmed, signed NaviPack**. Overview shows selected sub and cue list; Driving uses course-up vehicle lower-third, next turn, look-ahead, building detail z16+ where available.
- Driver TSD panel reads adapter state and sensor/odometer values; distance remaining and route progress derive from confirmed sub length plus authoritative measured progress with explicit source/status; it **must not fabricate live TSD values**.
- Cue advancement is deterministic on locked route offset, heading, snap confidence and monotonic cue ordering; off-route (>30m threshold from v3.0, subject to test/event policy) freezes cue, no dynamic reroute. No editor, freeform agent, approval or send button on either Driver view.
- LIVE network independence includes local PMTiles, style, glyphs, sprites, fonts and locations SQLite/R*Tree. Raster satellite imagery and public Humanitarian tile servers are never required by Driver LIVE.

## Offline Map OS and Humanitarian layer integration

| Layer/engine | Surface | Authority |
|---|---|---|
| PMTiles/MapLibre GL JS (Navigator), MapLibre Native (Driver), local assets | Page 2, Driver 1/2 | Render only; no network in LIVE |
| OSM/Overpass raw POI, buildings, roads, tags | Page 2 prep/curated DB | Geospatial candidate/evidence; ODbL attribution/derivative data obligations |
| Humanitarian style (local/self-hosted, rights-reviewed) | Page 2 optional style | Visual prominence, not an independent source or physical truth |
| OSRM directed graph pinned by version/digest | Page 2 PREP/REVIEW | Candidate graph length/turn topology, not official distance/time |
| God's Eye imagery / Cesium / Kepler | Page 2 ancillary PREP/REVIEW | Dated spatial context only; avoid pretending NASA HLS identifies small buildings |
| Local location DB: POI_REFERENCE/PHYSICAL_LOCATION/ROUTE_ACCESS_POINT | Page 2 + read-only released snapshot | Human confirmation and provenance required |

V3.0 cockpit display remains dark (`#0B0E12`) with red route accent (`#FF003F`). Humanitarian is an optional **local style/data overlay**, not a forced replacement for approved cockpit design. Driver map reduces clutter and only shows relevant offline landmarks.

## Traceable acceptance and status

- Page 1: photo/input→reviewed source steps, distances/times, numeric speed, start list precedence, cumulative schedule and TSD ACK state tested with fixtures.
- Page 2: per-sub map/list binding, no instruction reordering, revisioned draft edits, unresolved blocks confirmation and signed-driver-pack pipeline.
- Page 3: proposal inbox and MCP deny tests (`approve`, `confirm`, `publish`, `LIVE`); offline local search status.
- Driver 1/2: toggle without revision changes; no forbidden action; deterministic cue replay, freeze and offline cold start validated on device.
- Cross-flow: 16 blocking gates from baseline authority requirements must be integrated with production compiler; an incomplete/NOT_RUN gate **HOLDs** release. Actual Android build, authenticated approval, source-byte ingestion, TSD ACK, PMTiles rendering, and GPS cue tests are **NOT_IMPLEMENTED**.

**Design proof artifacts:** `contracts/ui/cockpit-surface-registry.yaml`, `governance/cockpit-role-action-policy.yaml`, `tests/contracts/test_cockpit_five_surfaces.py`. Their checks validate **declarations**, not operational readiness.
