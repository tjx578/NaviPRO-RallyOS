"""Exact arithmetic primitives and draft schedules; no event-rule authorization.

Integer millimetres/milliseconds in, rational results until a caller applies an
explicit rule. Date-less schedules reject midnight rollover. No provider ETA,
graph length, scoring rule or rounded speed can silently replace source values.
"""
from fractions import Fraction
import re
from typing import Any, Mapping, Sequence


class TimingError(ValueError):
    pass


def _integer(value: int, name: str, minimum: int = 0) -> int:
    if type(value) is not int or value < minimum:
        raise TimingError(f'{name} must be an integer >= {minimum}')
    return value


def speed_kmh(distance_mm: int, duration_ms: int) -> Fraction:
    return Fraction(_integer(distance_mm, 'distance_mm') * 18,
                    _integer(duration_ms, 'duration_ms', 1) * 5)


def travel_duration_ms(distance_mm: int, speed: Fraction) -> Fraction:
    _integer(distance_mm, 'distance_mm')
    if not isinstance(speed, Fraction) or speed <= 0:
        raise TimingError('speed must be a positive exact Fraction in km/h')
    return Fraction(distance_mm * 18, 5) / speed


def calibration_factor(reference_mm: int, raw_odometer_mm: int) -> Fraction:
    return Fraction(_integer(reference_mm, 'reference_mm', 1),
                    _integer(raw_odometer_mm, 'raw_odometer_mm', 1))


def _factor(cf: Fraction) -> Fraction:
    if not isinstance(cf, Fraction) or cf <= 0:
        raise TimingError('calibration factor must be a positive exact Fraction')
    return cf


def corrected_distance_mm(raw_odometer_mm: int, cf: Fraction) -> Fraction:
    return _integer(raw_odometer_mm, 'raw_odometer_mm') * _factor(cf)


def raw_target_mm(corrected_target_mm: int, cf: Fraction) -> Fraction:
    return _integer(corrected_target_mm, 'corrected_target_mm') / _factor(cf)


def _clock_ms(value: str) -> int:
    if not isinstance(value, str) or not re.fullmatch(r'([01][0-9]|2[0-3]):[0-5][0-9]:[0-5][0-9](\.[0-9]{3})?', value):
        raise TimingError('start_time must be HH:MM:SS or HH:MM:SS.mmm')
    clock, _, millis = value.partition('.')
    h, m, s = map(int, clock.split(':'))
    return ((h * 60 + m) * 60 + s) * 1000 + int(millis or 0)


def _clock_text(value: int) -> str:
    h, rem = divmod(value, 3_600_000)
    m, rem = divmod(rem, 60_000)
    s, ms = divmod(rem, 1000)
    return f'{h:02}:{m:02}:{s:02}.{ms:03}'


def draft_schedule(sections: Sequence[Mapping[str, Any]], *, start_time: str) -> dict[str, Any]:
    """Accumulate authoritative durations, preserving every section and timing mode.

    This diagnostic deliberately cannot validate event clock scales, rounding,
    neutralizations or permission to send a TSD plan. It is not TimingComputeResult.
    """
    cursor = _clock_ms(start_time)
    if not sections:
        raise TimingError('nonempty ordered sections required')
    rows = []
    seen = set()
    for section in sections:
        ident = section.get('section_id')
        if not isinstance(ident, str) or not ident.strip() or ident in seen:
            raise TimingError('unique section occurrence IDs required')
        seen.add(ident)
        duration = _integer(section.get('t_auth_ms'), 't_auth_ms', 1)
        distance = section.get('d_auth_mm')
        speed = None if distance is None else speed_kmh(distance, duration)
        mode = section.get('timing_mode')
        if not isinstance(mode, str) or not mode.strip():
            raise TimingError('source timing_mode required; semantics may remain unresolved')
        end = cursor + duration
        if end >= 86_400_000:
            raise TimingError('date-less midnight rollover requires dated event model')
        rows.append({'section_id': ident, 'start_time': _clock_text(cursor),
                     'arrival_time': _clock_text(end), 'duration_ms': duration,
                     'd_auth_mm': distance, 'timing_mode': mode,
                     'speed_kmh_ratio': None if speed is None else {'num': speed.numerator, 'den': speed.denominator}})
        cursor = end
    return {'status': 'DRAFT', 'release_status': 'HOLD', 'route_authority': False,
            'timing_rule_status': 'NOT_VERIFIED', 'start_time': _clock_text(_clock_ms(start_time)),
            'arrival_time': _clock_text(cursor), 'total_duration_ms': cursor - _clock_ms(start_time),
            'sections': rows}
