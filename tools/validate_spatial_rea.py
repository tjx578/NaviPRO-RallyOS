#!/usr/bin/env python3
from pathlib import Path
import json, yaml

repo = Path(__file__).resolve().parents[1]
reg = yaml.safe_load((repo / 'contracts/spatial/kepler-capability-registry.yaml').read_text(encoding='utf-8'))
policy = yaml.safe_load((repo / 'governance/spatial-capability-policy.yaml').read_text(encoding='utf-8'))
schema = json.loads((repo / 'contracts/jsonschema/spatial-map-project.schema.json').read_text(encoding='utf-8'))

caps = reg['capabilities']
ids = [c['id'] for c in caps]
assert len(ids) == len(set(ids)), 'duplicate capability id'
assert len(caps) >= 60, f'capability coverage too small: {len(caps)}'
assert all(c['implementation_status'] in {'SCAFFOLDED','IMPLEMENTED','VERIFIED','DEFERRED'} for c in caps)
assert not any('LIVE' in c['allowed_modes'] for c in caps), 'Kepler-derived Map Lab capability leaked into LIVE'
assert policy['modes']['LIVE']['mapping_workbench'] == 'DENY'
assert policy['modes']['LIVE']['geometry_edit'] == 'DENY'
assert schema['properties']['authority']['properties']['route_authority']['const'] is False
required_layers = {'POINT','ARC','LINE','GRID','HEXBIN','GEOJSON','CLUSTER','ICON','HEATMAP','H3','SCENEGRAPH_3D','TRIP','S2','A5','GEOHASH','FLOW','VECTOR_TILE','RASTER_TILE','WMS','TILE_3D','BITMAP'}
layer_enum = set(schema['$defs']['layer']['properties']['type']['enum'])
assert required_layers <= layer_enum, required_layers-layer_enum
print(f"Spatial REA OK: {len(caps)} capabilities; LIVE exposure=0; layers={len(layer_enum)}")
