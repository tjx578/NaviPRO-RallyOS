from copy import deepcopy
import hashlib
import importlib.util
import json
from pathlib import Path

import pytest

from navipro_rallyos.rally.roadbook import parse_roadbook, RoadbookError
from navipro_rallyos.rally.constraints import evaluate_roadbook, assess_candidate

ROOT = Path(__file__).resolve().parents[2]
FIXTURE = ROOT / 'tests/fixtures/rotr_surabaya'
TEXT = (FIXTURE / 'roadbook.txt').read_text(encoding='utf-8')
SOURCE = json.loads((FIXTURE / 'source.json').read_text(encoding='utf-8'))


def test_original_source_digest_and_manual_transcription_status():
    assert hashlib.sha256((FIXTURE / 'source.jpeg').read_bytes()).hexdigest() == SOURCE['source_image_sha256']
    assert SOURCE['operator_confirmed'] is False
    assert SOURCE['transcription_status'] == 'PENDING_OPERATOR_REVIEW'


def test_three_distance_stages_and_five_time_allocations():
    result = evaluate_roadbook(parse_roadbook(TEXT), SOURCE)
    assert result['distance_sections'] == ['B', 'C', 'D']
    assert result['total_declared_leg_distance_mm'] == 19_600_000
    assert result['total_duration_ms'] == 120 * 60_000
    assert result['arithmetic_status'] == 'ARITHMETIC_VALID'
    assert result['status'] == 'ROUTE_UNRESOLVED'
    assert result['provider_benchmark_status'] == 'NOT_EXECUTED'


def test_ordered_jawa_occurrences_are_never_deduplicated():
    roadbook = parse_roadbook(TEXT)
    section = roadbook['sections'][1]
    jawa = [item for item in section['instructions'] if 'Jl. Jawa' in item['raw_text']]
    assert len(jawa) == 3
    assert [item['instruction_id'] for item in jawa] == ['B-003', 'B-004', 'B-005']
    assert roadbook['source_text'] == TEXT


def test_inline_293_km_remains_ambiguous():
    section = parse_roadbook(TEXT)['sections'][1]
    assert section['d_auth_mm'] == 7_570_000
    assert section['inline_distance_references'] == [
        {'value_mm': 2_930_000, 'meaning': 'UNKNOWN', 'cumulative': None}
    ]


def test_distinct_timing_modes_and_unknown_coordinates():
    sections = parse_roadbook(TEXT)['sections']
    assert [s['timing_mode'] for s in sections[1:]] == [
        'TETAP_DETIK', 'TETAP_MENIT', 'RATA_RATA', 'BEBAS_ORDERED_VISITS']
    assert len(sections[-1]['instructions']) == 3
    assert 'tidak perlu masuk gang' in sections[-1]['instructions'][2]['raw_text']
    assert 'berhenti di tepi jalan' in sections[-1]['instructions'][2]['raw_text']
    assert 'MedicElle' in sections[0]['instructions'][0]['raw_text']
    assert sections[-1]['finish_reference'] == 'Finish (location unconfirmed)'
    for section in sections:
        for step in section['instructions']:
            assert step['physical_location'] is None
            assert step['route_access_point'] is None
            assert step['poi_reference']['source_text'] == step['raw_text']


def test_distance_match_and_provider_eta_cannot_confirm_route():
    section = parse_roadbook(TEXT)['sections'][1]
    candidate = {'candidate_id': 'synthetic', 'route_authority': False,
                 'graph_distance_mm_candidate': section['d_auth_mm'],
                 'estimated_travel_seconds': 99}
    result = assess_candidate(section, candidate)
    assert result['distance_residual_mm'] == 0
    assert result['t_auth_ms'] == 25 * 60_000
    assert result['provider_eta_seconds'] == 99
    assert result['instruction_coverage'] == 'NOT_MEASURED'
    assert result['status'] == 'ROUTE_UNRESOLVED'
    assert result['route_authority'] is False


def test_deleted_loop_occurrence_and_reordered_occurrences_fail_coverage():
    section = parse_roadbook(TEXT)['sections'][1]
    ids = [step['instruction_id'] for step in section['instructions']]
    candidate = {'route_authority': False, 'graph_distance_mm_candidate': 1}
    for observed in (ids[:3] + ids[4:], list(reversed(ids))):
        result = assess_candidate(section, candidate, {
            'evidence_ref': 'synthetic-test-traversal', 'observed_instruction_ids': observed})
        assert result['instruction_coverage'] == 'ORDER_OR_COVERAGE_MISMATCH'
        assert result['status'] == 'ROUTE_UNRESOLVED'


def test_copied_request_ids_without_traversal_evidence_are_not_proof():
    section = parse_roadbook(TEXT)['sections'][1]
    ids = [s['instruction_id'] for s in section['instructions']]
    result = assess_candidate(section, {'route_authority': False, 'graph_distance_mm_candidate': 0},
                              {'observed_instruction_ids': ids})
    assert result['instruction_coverage'] == 'NOT_MEASURED'


def test_unknown_totals_and_mismatched_totals_are_distinct():
    roadbook = parse_roadbook(TEXT)
    assert evaluate_roadbook(roadbook, {})['arithmetic_status'] == 'ARITHMETIC_UNVERIFIED'
    assert evaluate_roadbook(roadbook, {**SOURCE, 'declared_distance_mm': 1})['arithmetic_status'] == 'ARITHMETIC_MISMATCH'


@pytest.mark.parametrize('text', [
    '', TEXT.replace('C. Kecepatan', 'B. Kecepatan'),
    TEXT.replace('Waktu 25 menit', 'Waktu tidak terbaca'),
    TEXT.replace('Jarak 7,57km', 'Jarak tidak terbaca'),
])
def test_ambiguous_source_fails_instead_of_inventing_constraints(text):
    with pytest.raises(RoadbookError):
        parse_roadbook(text)


def test_headings_are_parsed_not_replaced_with_expected_answers():
    edited = TEXT.replace('7,57km', '8,57km').replace('Waktu 25 menit', 'Waktu 26 menit')
    result = evaluate_roadbook(parse_roadbook(edited), SOURCE)
    assert result['total_declared_leg_distance_mm'] == 20_600_000
    assert result['total_duration_ms'] == 121 * 60_000
    assert result['arithmetic_status'] == 'ARITHMETIC_MISMATCH'


def load_runner():
    spec = importlib.util.spec_from_file_location('m1_benchmark', ROOT / 'tools/m1_benchmark.py')
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def test_cli_core_writes_evidence_and_refuses_overwrite(tmp_path):
    runner = load_runner()
    target = tmp_path / 'result'
    result = runner.run(FIXTURE, target, 'REVIEW')
    assert (target / 'benchmark.json').is_file()
    assert result['status'] == 'ROUTE_UNRESOLVED'
    with pytest.raises(FileExistsError):
        runner.run(FIXTURE, target, 'REVIEW')


def test_candidate_bindings_preserve_occurrence_ids_and_require_evidence():
    runner = load_runner()
    section = parse_roadbook(TEXT)['sections'][1]
    records = [
        {'instruction_id': 'B-003', 'lat_e7': 0, 'lon_e7': 0, 'evidence_ref': 'synthetic'},
        {'instruction_id': 'B-004', 'lat_e7': 1, 'lon_e7': 1, 'evidence_ref': 'synthetic'},
    ]
    assert [a.anchor_id for a in runner.candidate_anchors(section, records)] == ['B-003', 'B-004']
    with pytest.raises(RoadbookError):
        runner.candidate_anchors(section, list(reversed(records)))
    bad = deepcopy(records)
    bad[0]['evidence_ref'] = ''
    with pytest.raises(RoadbookError):
        runner.candidate_anchors(section, bad)
