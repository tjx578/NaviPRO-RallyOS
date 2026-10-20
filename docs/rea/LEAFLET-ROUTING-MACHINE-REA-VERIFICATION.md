# Leaflet Routing Machine REA — Verification Ledger

**Date:** 2026-10-20. **Repo local baseline:** `33970b8` (previous OSRM REA). **Source LRM:** `8dc939a314425684883dc6f016b3aa9d04c8b7ca`. 

## Verified source assertions

- The GitHub repository metadata identifies a fork of `perliedman/leaflet-routing-machine`.
- Source fork head and upstream head at audit were **identical**; GitHub compare returned `identical`, `ahead=0`, `behind=0`, `changed files=0`.
- The repository `package.json` declares `leaflet-routing-machine` **3.3.0**, and `LICENSE.md` / package state ISC. GitHub license metadata reported `NOASSERTION`.
- Source includes `Control`, `Plan`, `Line`, `Itinerary`, `Formatter`, geocoder/autocomplete, localization, `OSRMv1`, Mapbox, Waypoint and ErrorControl.
- The source `npm test` script exits with code 1; its ancient test/spec code cannot be equated to current CI parity.
- Third-party source was **not cloned, compiled or copied** into NaviPRO. File-indexed capability mapping contains **38** records.

## Runtime / contract checks executed locally

| Check | Result | Interpretation |
|---|---|---|
| `python tools/validate_openapi.py` | PASS | Every operation has unique ID and NaviPRO metadata |
| `python tools/build_mcp_registry.py` | PASS | 68 tool definitions enabled, 11 operations excluded |
| All internal `#/components/schemas/*` refs | PASS | 103 schemas resolved within aggregate |
| `python -m pytest -q tests/contracts` | **44 passed** | Python prototypes, contracts, governance, numeric tests |
| `node --test apps/routing-lab-web/test/*.test.mjs` | **11 passed** | Review state and LRM safe state events |
| JS payload → JSON Schema → Python reviewer → JSON Schema | PASS | Source order immutable, proposal staging, `route_authority=false` |
| Real Leaflet browser/DOM build | **NOT RUN** | Dependency/build compatibility unknown |
| Real OSRM graph and geographic coverage | **NOT RUN** | No road accuracy or runtime parity claim |
| Authenticated REST/MCP service | **NOT BUILT** | Tool list is metadata, no functioning remote MCP runtime |
| Offline Android Driver | **NOT RUN** | `NOT_RACE_READY` |

## Security tests performed and limitations

**Pass:** `LIVE` blocked; source anchor reversal/deletion rejected; duplicate anchors rejected; graph/profile/revision mismatch rejected; candidate ID unrecognized rejected; unexpected authority and publish-related fields rejected; `shaping_point` is proposal-only with strict E7 coordinates; no route approval endpoint added to MCP.

**Not proven:** real server authorization, direct LRM controls or DOM, XSS safety in itinerary HTML display, browser provider credential isolation, browser version regression 3.2.12→3.3.0, network rate limiting, concurrent writes/revision race locking, offline graph or NaviPack release.

## How to repeat

```bash
cd navipro-rallyos-vnext
python tools/validate_openapi.py
python tools/build_mcp_registry.py
python -m pytest -q tests/contracts
node --test apps/routing-lab-web/test/*.test.mjs
```

Overall status: `AUDITED + CONTRACT_GENERATED + PURE_ADAPTER_TESTED / NO_BROWSER_PARITY / NO_REAL_GRAPH / NOT_RACE_READY`.
