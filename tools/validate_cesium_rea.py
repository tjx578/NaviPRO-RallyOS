#!/usr/bin/env python3
"""Validate REA registry, mode boundaries, schemas and OpenAPI/MCP contract metadata."""
from pathlib import Path
import json, yaml
ROOT=Path(__file__).resolve().parents[1]
reg=yaml.safe_load((ROOT/'contracts/spatial/cesium-capability-registry.yaml').read_text())
pol=yaml.safe_load((ROOT/'governance/cesium-3d-capability-policy.yaml').read_text())
sc=json.loads((ROOT/'contracts/jsonschema/cesium-3d-project.schema.json').read_text())
api=yaml.safe_load((ROOT/'contracts/openapi/navipro-rallyos.openapi.yaml').read_text())
caps=reg['capabilities']
assert len(caps)>=65
assert len(set(c['id'] for c in caps))==len(caps)
assert not any('LIVE' in c['allowed_modes'] for c in caps)
assert all(c['authority']=='VISUAL_ANALYTIC_ONLY' for c in caps)
assert pol['mode_denylist']==['LIVE']
assert sc['properties']['authority']['properties']['route_authority']['const'] is False
assert sc['properties']['height_policy']['properties']['terrain_height_is_authoritative']['const'] is False
assert sc['$defs']['asset']['properties']['authority']['const']=='VISUAL_ANALYTIC_ONLY'
ops=[(p,m,o) for p,methods in api['paths'].items() for m,o in methods.items() if isinstance(o,dict) and o.get('operationId','').startswith('cesium')]
assert len(ops)>=8, f'Cesium API operations missing: {len(ops)}'
assert all(o['x-navipro-mode']==['PREP','REVIEW'] for _,_,o in ops)
assert all(o['x-navipro-authority'] in {'READ','AGENT_PROPOSE'} for _,_,o in ops)
assert all(o['x-navipro-side-effect'] in {'NONE','DRAFT_MUTATION'} for _,_,o in ops)
assert not any('confirm' in o['operationId'].lower() or 'publish' in o['operationId'].lower() for _,_,o in ops)
print(f'Cesium REA OK: {len(caps)} capabilities; {len(ops)} OpenAPI ops; PREP/REVIEW only, authority=FALSE')
