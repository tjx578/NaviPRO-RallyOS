verify:
	python tools/validate_openapi.py
	python tools/validate_spatial_rea.py
	python tools/build_mcp_registry.py

verify-spatial:
	python tools/validate_spatial_rea.py

verify-cockpit:
	python -m pytest -q tests/contracts/test_cockpit_five_surfaces.py

verify-gates:
	python tools/validate_openapi.py
	python -m pytest -q tests/contracts/test_release_gate_divisions.py
