verify:
	python tools/validate_openapi.py
	python tools/validate_spatial_rea.py
	python tools/build_mcp_registry.py

verify-spatial:
	python tools/validate_spatial_rea.py
