verify:
	python -m pytest -q
	python tools/validate_openapi.py
	python tools/validate_spatial_rea.py
	python tools/validate_cesium_rea.py
	python tools/build_mcp_registry.py --check
	python tools/validate_prompt_pack.py
	node --test apps/routing-lab-web/test/*.test.mjs

verify-spatial:
	python tools/validate_spatial_rea.py

verify-cockpit:
	python -m pytest -q tests/contracts/test_cockpit_five_surfaces.py

verify-gates:
	python tools/validate_openapi.py
	python -m pytest -q tests/contracts/test_release_gate_divisions.py
