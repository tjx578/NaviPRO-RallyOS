# NaviPRO RallyOS — Repo Skeleton Blueprint v1

## 1. Node pusat

**Tujuan:** menyediakan struktur monorepo yang mampu menampung intake roadbook, review manusia, ordered routing, 16 blocking gates, NaviPack, Navigator Workspace, Driver Runtime, TSD integration, spatial data, knowledge/RAG, dan evidence lifecycle tanpa mencampur authority.

**Status:** `PLAN_ONLY / NOT_RACE_READY`.

## 2. Struktur tingkat atas

```text
navipro-rallyos/
├── apps/                 # executable non-Android surfaces
├── python/               # deterministic domain/compiler libraries + CLI
├── android/              # navigator + driver Gradle workspace
├── services/             # production boundaries not embedded in agent/runtime
├── contracts/            # JSON Schema, OpenAPI, SQL, examples, compatibility
├── governance/           # authority, capability, mode, network, release gates
├── config/               # versioned authority/validation/device/deployment profiles
├── data/                 # spatial/event/device/test data layout; large binaries external/LFS
├── knowledge/            # authority/guidance/derived chunks/evals; never runtime authority
├── tests/                # cross-language contract, e2e, replay, security, field corpus
├── tools/                # safe bootstrapping and verification
├── scripts/              # developer/operator commands
├── release/              # manifest, receipt, checklist, trust/SBOM templates
├── docs/                 # architecture, ADR, operations, evidence, security, testing
└── .github/              # CI and issue templates; workflow files remain templates until pinned
```

## 3. Cabang utama

### A. Authority & Evidence

- `governance/authority-matrix.yaml`
- `config/authority/`
- `knowledge/authority/`
- `services/review-authority/`
- `docs/evidence/`

**Output:** authority profile, authenticated decision target, conflict receipt, release sign-off.

### B. Preparation & Deterministic Compilation

- `python/src/navipro_rallyos/ingest/`
- `authority/`, `routing/`, `locations/`, `timing/`
- `gates/`, `compiler/`, `exporters/`, `navipack/`

**Control:** one `FAIL` or `NOT_RUN` produces `HOLD`; no partial publish.

### C. Cockpit Runtime

- `android/apps/navigator/`
- `android/apps/driver/`
- shared `core/`, `features/`, `runtime/`, and `integrations/`

**Control:** confirmed revision is read-only; LIVE has no dynamic rerouting or network dependency.

### D. Data & Knowledge

- `data/spatial/` for PMTiles, graph, locations, style, glyphs, sprites, manifests.
- `data/events/` for per-event source/review/workspace/release.
- `knowledge/` for authority/guidance/derived/evaluation layers.

**Control:** derived chunks cannot promote evidence or override roadbook/authority profile.

### E. Delivery, Verification, and Operations

- `contracts/` defines payloads.
- `integrations/` uses version, hash, idempotency, timeout, retry policy, and ACK.
- `release/` stores templates; generated release goes to ignored `build/` or external artifact store.
- `tests/` and `docs/operations/` define rehearsal, rollback, and field evidence.

## 4. Dependency direction

```text
contracts + domain
      ↓
authority / locations / timing / routing
      ↓
gates → compiler → exporters → navipack
      ↓
verified package
      ↓
Android navipack loader → map/cue/timing/sensors/blackbox
```

Forbidden paths:

```text
agent ─X→ approve/promote/publish
LIVE runtime ─X→ OCR/editor/external maps/network router
Android driver ─X→ navigator editing feature
external candidate data ─X→ source-of-truth status
```

## 5. Recommended implementation order

1. P0 authority, source registry, strict contracts, and corpus.
2. P1 preserve/import the verified deterministic MVP into `python/`.
3. P2 offline graph adapter and ordered route solver.
4. P5 location evidence + propose-only agent in parallel.
5. P3 Android pack loader, navigator, driver, map, cue, timing, blackbox.
6. P4 sensor fusion and degraded modes.
7. P6 field hardening and failure injection.
8. P7 event-specific frozen release and three-role sign-off.

## 6. Acceptance criteria for this skeleton

- Exact 16 gate names registered.
- Gate stubs fail closed with `NOT_RUN`.
- Agent allowlist/denylist is testable.
- JSON contracts parse.
- SQL migrations apply and pass `PRAGMA integrity_check`.
- Safe event bootstrap rejects invalid IDs and overwrite.
- No remote URL appears in race-bundle style template.
- Python skeleton tests pass.
