from copy import deepcopy
from fractions import Fraction
from pathlib import Path

import pytest

from navipro_rallyos.rally.roadbook import parse_roadbook
from navipro_rallyos.timing.core import (
    TimingError, calibration_factor, corrected_distance_mm, draft_schedule,
    raw_target_mm, speed_kmh, travel_duration_ms,
)

FIXTURE = Path(__file__).resolve().parents[1] / 'fixtures/rotr_surabaya/roadbook.txt'


def test_known_calibration_conversion_and_inverse():
    factor = calibration_factor(10_000_000, 9_410_000)
    assert factor == Fraction(1000, 941)
    assert raw_target_mm(10_790_000, factor) == 10_153_390
    assert corrected_distance_mm(10_153_390, factor) == 10_790_000
    assert corrected_distance_mm(0, factor) == raw_target_mm(0, factor) == 0


def test_exact_schedule_speed_does_not_round_trip_through_display_speed():
    exact = speed_kmh(10_790_000, 35 * 60_000)
    assert exact == Fraction(3237, 175)
    assert travel_duration_ms(10_790_000, exact) == 2_100_000
    rounded_duration = travel_duration_ms(10_790_000, Fraction(37, 2))
    assert 2_100_000 - rounded_duration == Fraction(12_000, 37)


def test_solo_example_is_exact():
    assert speed_kmh(110_000, 60_000) == Fraction(33, 5)


def test_rotr_schedule_preserves_time_authority_and_unknown_distances():
    sections = parse_roadbook(FIXTURE.read_text())['sections']
    before = deepcopy(sections)
    result = draft_schedule(sections, start_time='10:00:00')
    assert result['arrival_time'] == '12:00:00.000'
    assert result['total_duration_ms'] == 7_200_000
    assert [row['arrival_time'] for row in result['sections']] == [
        '10:02:00.000', '10:27:00.000', '10:47:00.000', '11:09:00.000', '12:00:00.000']
    assert result['sections'][0]['speed_kmh_ratio'] is None
    assert result['sections'][-1]['d_auth_mm'] is None
    assert result['sections'][1]['speed_kmh_ratio'] == {'num': 2271, 'den': 125}
    assert result['release_status'] == 'HOLD' and result['timing_rule_status'] == 'NOT_VERIFIED'
    assert not result['route_authority']
    assert sections == before


@pytest.mark.parametrize('start', ['22:00:00', '23:59:59.999'])
def test_undated_midnight_never_silently_wraps(start):
    with pytest.raises(TimingError, match='midnight'):
        draft_schedule(parse_roadbook(FIXTURE.read_text())['sections'], start_time=start)


@pytest.mark.parametrize('start', ['10:00', '24:00:00', '10:60:00', '10:00:00.1', None, True])
def test_invalid_clock_rejected(start):
    with pytest.raises(TimingError):
        draft_schedule([{'section_id': 'A', 'timing_mode': 'UNKNOWN', 't_auth_ms': 1}], start_time=start)


@pytest.mark.parametrize('value', [True, -1, 1.5, '100', None])
def test_distance_not_coerced(value):
    with pytest.raises(TimingError):
        speed_kmh(value, 1000)


def test_invalid_denominators_and_float_factors_rejected():
    for operation in (lambda: speed_kmh(1, 0), lambda: calibration_factor(1, 0),
                      lambda: raw_target_mm(1, Fraction(0)), lambda: travel_duration_ms(1, Fraction(0)),
                      lambda: corrected_distance_mm(1, 1.0627)):
        with pytest.raises(TimingError):
            operation()


def test_duplicate_section_identity_rejected():
    sections = parse_roadbook(FIXTURE.read_text())['sections']
    sections[1]['section_id'] = sections[0]['section_id']
    with pytest.raises(TimingError, match='unique'):
        draft_schedule(sections, start_time='10:00:00')
