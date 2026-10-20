from pathlib import Path
import json, yaml

ROOT = Path(__file__).resolve().parents[2]

def test_spatial_capabilities_are_prep_review_only():
    reg = yaml.safe_load((ROOT / 'contracts/spatial/kepler-capability-registry.yaml').read_text())
    assert reg['capabilities']
    assert all('LIVE' not in c['allowed_modes'] for c in reg['capabilities'])

def test_spatial_map_project_cannot_be_route_authority():
    schema = json.loads((ROOT / 'contracts/jsonschema/spatial-map-project.schema.json').read_text())
    assert schema['properties']['authority']['properties']['route_authority']['const'] is False
