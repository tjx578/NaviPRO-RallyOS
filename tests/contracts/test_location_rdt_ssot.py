"""Contract-only checks for the proposed physical-location + RDT SSOT.

These tests validate a schema and governance declaration, not a working
satellite imagery detector, route solver, or Time Rally correctness.
"""
import copy
import json
from pathlib import Path

import pytest
import yaml
from jsonschema import Draft202012Validator, FormatChecker

ROOT = Path(__file__).resolve().parents[2]
SCHEMA = json.loads((ROOT / 'contracts/jsonschema/physical-location-assessment.schema.json').read_text())
POLICY = yaml.safe_load((ROOT / 'governance/route-distance-time-location-policy.yaml').read_text())
VALIDATOR = Draft202012Validator(SCHEMA, format_checker=FormatChecker())


def example_assessment():
    """Fully synthetic case; coordinates do not identify a real POI."""
    return {
      'assessment_id': 'DEMO-001', 'mode': 'PREP', 'route_revision_id': 'REV-DEMO',
      'source_instruction_id': 'ROADBOOK-DEMO-02',
      'source_instruction_text': 'Contoh sintetis: kantor desa',
      'official_anchor_ids': ['START', 'CONTROL', 'FINISH'],
      'location_references': [{
        'reference_id': 'SRC-01', 'kind': 'POI_REFERENCE', 'name': 'Bangunan contoh',
        'source_id': 'SYNTHETIC-POI', 'coordinate': {'lat_e7': -80000000, 'lon_e7': 1150000000},
        'verification_status': 'SUSPECT', 'source_capture_at': None,
      }],
      'physical_candidates': [{
        'candidate_id': 'CAND-01', 'kind': 'PHYSICAL_LOCATION',
        'coordinate': {'lat_e7': -80000100, 'lon_e7': 1150000100},
        'physical_status': 'NEEDS_FIELD_CHECK',
        'access_status': 'NEEDS_FIELD_CHECK',
        'evidence': [{
          'evidence_id': 'E-01', 'kind': 'SATELLITE_IMAGE',
          'provider': 'SYNTHETIC', 'capture_time': None, 'resolution_m': None,
          'source_ref': 'synthetic-test-image-not-a-real-provider',
          'rights_reviewed': False,
          'observation': 'An image alone cannot establish a place name',
        }],
      }],
      'distance_time_checks': [{
        'segment_id': 'SEG-1', 'distance_domain': 'D_graph_vs_D_auth',
        'd_auth_mm': 1500000, 'd_graph_mm': None, 'delta_distance_mm': None,
        'timing_status': 'RULES_UNKNOWN', 'rule_version': None,
        'status': 'UNKNOWN',
      }],
      'status': 'NEEDS_FIELD_CHECK', 'route_authority': False, 'confirmed': False,
    }


def test_schema_is_valid_and_synthetic_proposal_passes():
    Draft202012Validator.check_schema(SCHEMA)
    VALIDATOR.validate(example_assessment())


@pytest.mark.parametrize('change', [
    {'route_authority': True}, {'confirmed': True}, {'mode': 'LIVE'},
    {'official_anchor_ids': ['START', 'START']},
    {'official_anchor_ids': ['START']},
    {'publish': True}, {'status': 'VERIFIED'},
])
def test_no_authority_or_unsupported_stage(change):
    record = {**example_assessment(), **change}
    assert not VALIDATOR.is_valid(record)


def test_reference_physical_access_types_distinct():
    rec = example_assessment()
    candidate = rec['physical_candidates'][0]
    candidate['access_point'] = {
      'kind': 'ROUTE_ACCESS_POINT', 'coordinate': {'lat_e7': -80000050, 'lon_e7': 1150000050},
      'status': 'UNVERIFIED',
    }
    VALIDATOR.validate(rec)
    bad = copy.deepcopy(rec)
    bad['physical_candidates'][0]['access_point']['kind'] = 'POI_REFERENCE'
    assert not VALIDATOR.is_valid(bad)


def test_require_evidence_metadata_and_nonnegative_distances():
    sample = example_assessment()
    for patch in [
        {'provider': ''},
        {'resolution_m': -1},
        {'capture_time': 'yesterday'},
    ]:
        bad = copy.deepcopy(sample)
        bad['physical_candidates'][0]['evidence'][0].update(patch)
        assert not VALIDATOR.is_valid(bad)
    bad = copy.deepcopy(sample)
    bad['distance_time_checks'][0]['d_auth_mm'] = -5
    assert not VALIDATOR.is_valid(bad)


def test_governance_retains_separate_domains_and_no_autoverify():
    assert POLICY['route_invariants']['official_anchor_order'] == 'IMMUTABLE'
    assert POLICY['independent_distance_domains']['never_overwrite_D_auth'] is True
    assert set(['D_auth', 'D_graph', 'D_odo', 'D_geo']) <= set(POLICY['independent_distance_domains'])
    assert POLICY['physical_location']['no_auto_verify'] is True
    assert 'LIVE' not in POLICY['allowed_modes']
    assert POLICY['runtime'] == 'NOT_IMPLEMENTED'
