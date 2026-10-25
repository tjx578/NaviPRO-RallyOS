"""Bounded deterministic parser for the A–E ROTR text dialect.

Retains source text and each ordered occurrence. It does not geocode, interpret
unconfirmed turn abbreviations, or infer cumulative distances from inline notes.
"""
from decimal import Decimal
import hashlib
import re
from typing import Any


class RoadbookError(ValueError):
    pass


def _scaled_number(text: str, scale: int) -> int:
    value = Decimal(text.replace(',', '.')) * scale
    if value != value.to_integral_value() or value < 0:
        raise RoadbookError('number cannot be represented exactly in integer units')
    return int(value)


def parse_roadbook(text: str) -> dict[str, Any]:
    if not isinstance(text, str) or not text.strip() or len(text) > 200_000:
        raise RoadbookError('nonempty bounded roadbook text required')
    headings = list(re.finditer(r'^([A-E])\.\s+([^\n]+)', text, re.MULTILINE))
    if [m[1] for m in headings] != list('ABCDE'):
        raise RoadbookError('A-E sections must each occur exactly once in source order')
    sections = []
    for index, match in enumerate(headings):
        end = headings[index + 1].start() if index + 1 < len(headings) else len(text)
        raw = text[match.start():end]
        heading = match[2]
        duration = re.findall(r'\bwaktu\s+(\d+(?:[,.]\d+)?)\s*menit', heading, re.I)
        distance = re.findall(r'\bjarak\s+(\d+(?:[,.]\d+)?)\s*km', heading, re.I)
        if len(duration) != 1 or len(distance) > 1:
            raise RoadbookError(f'{match[1]} requires one unambiguous heading duration')
        modes = [('tetap detik', 'TETAP_DETIK'), ('tetap menit', 'TETAP_MENIT'),
                 ('rata-rata', 'RATA_RATA')]
        mode = next((value for label, value in modes if label in heading.lower()), 'UNSPECIFIED')
        body = text[match.end():end].strip()
        if match[1] == 'E' and 'rute bebas' in body.lower():
            mode = 'BEBAS_ORDERED_VISITS'
        if match[1] in 'BCD' and not distance:
            raise RoadbookError(f'{match[1]} missing official heading distance')
        if match[1] == 'A':
            parts = [re.split(r'\bwaktu\b', heading, flags=re.I)[0].strip()]
        elif match[1] == 'E':
            parts = [part.strip() for part in re.findall(
                r'^\d+\.\s+([\s\S]*?)(?=^\d+\.\s+|^Setelah|\Z)', body, re.MULTILINE)]
        else:
            parts = [part.strip() for part in re.split(r'\s+–\s+', body) if part.strip()]
        instructions = [
            {'instruction_id': f'{match[1]}-{i + 1:03}', 'ordinal': i + 1,
             'raw_text': part, 'location_status': 'UNRESOLVED',
             'poi_reference': {'source_text': part},
             'physical_location': None, 'route_access_point': None}
            for i, part in enumerate(parts)
        ]
        inline_distances = [
            {'value_mm': _scaled_number(value, 1_000_000),
             'meaning': 'UNKNOWN', 'cumulative': None}
            for value in re.findall(r'\bjarak\s+(\d+(?:[,.]\d+)?)\s*km', body, re.I)
        ]
        sections.append({
            'section_id': match[1], 'raw_text': raw, 'timing_mode': mode,
            'd_auth_mm': _scaled_number(distance[0], 1_000_000) if distance else None,
            't_auth_ms': _scaled_number(duration[0], 60_000),
            'instructions': instructions, 'inline_distance_references': inline_distances,
            'finish_reference': ('Finish (location unconfirmed)'
                                 if match[1] == 'E' and re.search(r'\bfinish\b', body, re.I) else None),
        })
    return {
        'source_text': text,
        'source_text_sha256': hashlib.sha256(text.encode('utf-8')).hexdigest(),
        'parser': 'ROTR_A_E_TEXT_V1',
        'sections': sections,
        'route_authority': False,
        'status': 'TRANSCRIPTION_PENDING_REVIEW',
    }
