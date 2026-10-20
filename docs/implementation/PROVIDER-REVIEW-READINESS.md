# Provider review and execution boundary

Review base: `b4e28580cc1fe43f4ddfca43104033c78e5d44b1` (draft PR #1).

## Reproducible local checks

Use CPython 3.11, a fresh virtual environment, and the exact dependency set:

```text
python -m venv .venv
.venv/Scripts/python -m pip install -r requirements-test.lock
.venv/Scripts/python -X utf8 -m pytest -q
.venv/Scripts/python -m pip check
```

On Linux use `.venv/bin/python`. Pytest sets `python/src` through pyproject.toml. The RFC3339 checker is an explicit dependency, so invalid timestamps are not accepted due to a missing optional package.

Fresh Windows CPython 3.11 environment verification: **198 tests passed**, `pip check` reported no broken requirements. The environment was installed from PyPI wheels whose SHA-256 values were checked against release metadata, without global packages or PYTHONPATH overrides.

## Actual IO guards

Every provider operation requires an explicit `mode="PREP"` or `mode="REVIEW"`. Missing, LIVE, CONFIRMED, lowercase, boolean, or unknown modes fail before transport. The normalized output retains the requested mode. This is an API-level execution guard; it does not authenticate a caller or substitute for a future trusted service/session mode controller.

OSRM native transport now uses GET with ordered `lon,lat;lon,lat` path coordinates and encoded query options. Valhalla still uses native JSON POST. Local HTTP fixture tests verify the actual HTTP methods, paths, payloads and normalized outputs for both.

The fixture HTTP server is not a real routing engine. Real OSRM/Valhalla graph and native-server response compatibility remain required checks.

## Host preflight on 20 October 2026

Docker Desktop was started for the requested development work. The Linux engine became briefly ready but the backend exited. The host monitor log recorded `VirtualAlloc of 1048576 bytes failed with errno=1455` and `fatal error: out of memory`; Docker subsequently had no reachable Linux engine pipe.

No graph build or provider benchmark completed. No pagefile, WSL resource configuration, unrelated container, or other application was changed to force the build.

Readiness: **LOCAL_REGRESSION_PASS / REAL_ENGINE_BLOCKED / PR_REMAINS_DRAFT**. Do not merge based solely on these local tests or mark M1 complete.
