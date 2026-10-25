"""Five cockpit *declaration* and governance tests (not browser/Android UI tests)."""
from pathlib import Path
import re

import pytest
import yaml

ROOT = Path(__file__).resolve().parents[2]
REGISTRY = yaml.safe_load((ROOT / 'contracts/ui/cockpit-surface-registry.yaml').read_text())
POLICY = yaml.safe_load((ROOT / 'governance/cockpit-role-action-policy.yaml').read_text())


def permitted(action: str, surface: str, mode: str) -> bool:
    """Pure declarative policy lookup, not authenticated runtime enforcement."""
    spec = POLICY['actions'][action]
    return any(s['surface'] == surface and mode in s['modes'] for s in spec['allow'])


def test_exact_three_navigator_pages_two_driver_modes():
    assert REGISTRY['surface_order'] == ['PAGE_1', 'PAGE_2', 'PAGE_3', 'DRIVER_1', 'DRIVER_2']
    assert list(REGISTRY['surfaces']) == REGISTRY['surface_order']
    assert REGISTRY['roles']['navigator']['surfaces'] == ['PAGE_1', 'PAGE_2', 'PAGE_3']
    assert REGISTRY['roles']['driver']['surfaces'] == ['DRIVER_1', 'DRIVER_2']
    assert REGISTRY['roles']['navigator']['navigation'] == 'SWIPE'
    assert REGISTRY['roles']['driver']['navigation'] == 'MODE_TOGGLE'
    assert REGISTRY['layout']['target'] == 'HYBRID_TABLET_LANDSCAPE_16_9'


def test_registry_is_source_traceable_and_honest():
    assert REGISTRY['status'] == 'DESIGN_ONLY'
    assert REGISTRY['source_spec'] == 'NAVIPRO-MAPOS-COCKPIT-UNIFIED-V3.0'
    assert re.fullmatch('[a-f0-9]{64}', REGISTRY['source_sha256'])
    assert POLICY['status'] == 'DESIGN_ONLY'


@pytest.mark.parametrize('surface', REGISTRY['surface_order'])
def test_surface_has_valid_owned_readme_and_role(surface):
    spec = REGISTRY['surfaces'][surface]
    assert (ROOT / spec['owner'] / 'README.md').is_file()
    assert spec['role'] in REGISTRY['roles']
    assert spec['app'] == spec['role']
    assert surface in REGISTRY['roles'][spec['role']]['surfaces']
    assert set(spec['modes']) <= set(POLICY['modes'])
    assert spec['ui'] and spec['input'] and spec['output']


def test_driver_views_are_same_app_same_immutable_pack():
    a, b = (REGISTRY['surfaces'][key] for key in ('DRIVER_1', 'DRIVER_2'))
    assert a['app'] == b['app'] == 'driver'
    assert a['input'][0] == b['input'][0] == 'SIGNED_CONFIRMED_NAVIPACK'
    assert REGISTRY['roles']['driver']['source_revision_mutation'] == 'DENY'
    assert all('SEND_LINK' in x['forbidden'] for x in (a, b))
    assert all('EDIT_ROUTE' in x['forbidden'] for x in (a, b))


def test_source_authority_and_timing_domains_are_separate():
    shared = REGISTRY['shared_authority']
    assert shared['official_roadbook'] == 'PAGE_1_SOURCE'
    assert shared['canonical_route_revision'] == 'NAVIGATOR_PAGE_2_HUMAN_GATE'
    assert shared['automated_assistant'] == 'PAGE_3_PROPOSE_ONLY'
    assert set(shared['distance_domains']) == {'D_auth', 'D_graph', 'D_odo', 'D_geo'}
    assert {'ORDERED_INSTRUCTIONS', 'OFFICIAL_DISTANCE_KM_PAL', 'EVENT_TIME_RULES'} <= set(shared['route_reasoning_constraints'])
    assert shared['no_network_dependencies_in_live'] is True
    assert 'D_AUTH_SEPARATE_FROM_D_GRAPH' in REGISTRY['surfaces']['PAGE_1']['required_rules']
    assert 'GRAPH_DISTANCE_NEVER_REPLACES_D_AUTH' in REGISTRY['surfaces']['PAGE_2']['required_rules']


def test_delivery_ownership_and_reality():
    assert REGISTRY['integration_boundaries']['tsd_cadencer']['sender'] == 'PAGE_1_NAVIGATOR'
    assert REGISTRY['integration_boundaries']['driver_navipack']['sender'] == 'PAGE_2_NAVIGATOR_AFTER_CONFIRMATION'
    assert REGISTRY['integration_boundaries']['tsd_cadencer']['contract_status'] == 'NOT_IMPLEMENTED'
    assert REGISTRY['integration_boundaries']['agent_mcp']['server_status'] == 'NOT_IMPLEMENTED'
    assert permitted('send_tsd_plan', 'PAGE_1', 'REVIEW')
    assert permitted('send_driver_pack', 'PAGE_2', 'CONFIRMED')
    assert not permitted('send_driver_pack', 'PAGE_2', 'PREP')
    assert not permitted('send_tsd_plan', 'PAGE_3', 'REVIEW')
    assert not permitted('send_driver_pack', 'DRIVER_1', 'LIVE')


@pytest.mark.parametrize('surface', ['DRIVER_1', 'DRIVER_2'])
@pytest.mark.parametrize('action', ['edit_route_draft', 'confirm_route', 'send_tsd_plan', 'send_driver_pack', 'propose_candidate', 'driver_send_link'])
def test_driver_never_receives_authoring_or_send_rights(surface, action):
    for mode in POLICY['modes']:
        assert not permitted(action, surface, mode)


@pytest.mark.parametrize('action', ['confirm_route', 'send_tsd_plan', 'send_driver_pack', 'agent_approve_route', 'agent_publish_navipack'])
def test_page_3_never_approves_or_sends(action):
    for mode in POLICY['modes']:
        assert not permitted(action, 'PAGE_3', mode)


def test_page_3_generative_proposal_not_allowed_live():
    assert REGISTRY['surfaces']['PAGE_3']['modes'] == ['PREP', 'REVIEW']
    assert permitted('propose_candidate', 'PAGE_3', 'REVIEW')
    assert not permitted('propose_candidate', 'PAGE_3', 'LIVE')
    assert not permitted('propose_candidate', 'PAGE_2', 'REVIEW')


def test_live_no_dynamic_rerouting_or_agent_publish():
    for action in ['live_route_reroute', 'agent_approve_route', 'agent_publish_navipack', 'driver_send_link']:
        assert POLICY['actions'][action]['allow'] == []
    assert REGISTRY['surfaces']['DRIVER_2']['camera'] == 'COURSE_UP_LOWER_THIRD_LOOKAHEAD'
    assert 'OFF_ROUTE_FREEZE_NO_AUTO_REROUTE' in REGISTRY['surfaces']['DRIVER_2']['required_rules']


def test_humanitarian_and_satellite_are_only_review_layers():
    layer = REGISTRY['surfaces']['PAGE_2']['map_layers']
    assert 'OSM_HUMANITARIAN_STYLE_OPTIONAL' in layer
    assert 'SATELLITE_CONTEXT_REVIEW_ONLY' in layer
    for key in ('DRIVER_1', 'DRIVER_2'):
        assert 'SATELLITE_CONTEXT_REVIEW_ONLY' not in REGISTRY['surfaces'][key].get('map_layers', [])


def test_no_uncontrolled_action_grants_or_mode_escapes():
    assert set(POLICY['workspaces']['NAVIGATOR']) == {'PAGE_1', 'PAGE_2', 'PAGE_3'}
    assert set(POLICY['workspaces']['DRIVER']) == {'DRIVER_1', 'DRIVER_2'}
    for action, record in POLICY['actions'].items():
        for grant in record['allow']:
            assert grant['surface'] in REGISTRY['surfaces'], action
            assert set(grant['modes']) <= set(REGISTRY['surfaces'][grant['surface']]['modes']), action
    assert POLICY['actions']['confirm_route']['authority'] == 'AUTHENTICATED_HUMAN_NAVIGATOR'


def test_page_2_has_no_direct_source_order_mutation():
    spec = REGISTRY['surfaces']['PAGE_2']
    assert 'ORIGINAL_ROADBOOK_TEXT_AND_SEQUENCE_IMMUTABLE' in spec['required_rules']
    assert 'SILENT_DELETE_OFFICIAL_STEP' in spec['forbidden']
    assert POLICY['actions']['edit_route_draft']['mutates'] == 'DRAFT_REVISION_ONLY'


def test_hybrid_ownership_and_renderers_have_one_target_per_role():
    assert REGISTRY['roles']['navigator']['app'] == 'apps/navigator-web'
    assert REGISTRY['roles']['navigator']['platform'] == 'WEB_PWA'
    assert REGISTRY['roles']['driver']['platform'] == 'ANDROID_NATIVE'
    assert (ROOT / REGISTRY['platform_decision']).is_file()
    assert REGISTRY['integration_boundaries']['offline_map']['renderer_targets'] == {
        'navigator': 'MAPLIBRE_GL_JS', 'driver': 'MAPLIBRE_NATIVE'}
    for key in ('PAGE_1', 'PAGE_2', 'PAGE_3'):
        assert REGISTRY['surfaces'][key]['owner'].startswith('apps/navigator-web/features/')
    for name in ('tsd_cadencer', 'driver_navipack'):
        boundary = REGISTRY['integration_boundaries'][name]
        assert (ROOT / boundary['adapter'] / 'README.md').is_file()
        assert (ROOT / boundary['device_adapter'] / 'README.md').is_file()
