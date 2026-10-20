"""Run deterministic roadbook checks, optionally against BOTH local providers.

No coordinates are invented. Real routing requires explicit candidate bindings
and successful build receipts referencing a common OSM PBF hash.
"""
import argparse
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import re
import sys
from urllib.error import URLError

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'python/src'))

from navipro_rallyos.rally.roadbook import parse_roadbook, RoadbookError
from navipro_rallyos.rally.constraints import evaluate_roadbook, assess_candidate
from navipro_rallyos.route.osrm_adapter import OSRMAdapter, RouteAnchor, RouteCandidateError
from navipro_rallyos.route.valhalla_adapter import ValhallaAdapter
from navipro_rallyos.route.provider_comparison import compare_provider_candidates


def sha256(path):
    digest = hashlib.sha256()
    with path.open('rb') as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b''):
            digest.update(chunk)
    return digest.hexdigest()


def candidate_anchors(section, bindings):
    source_order = [item['instruction_id'] for item in section['instructions']]
    ids = [item['instruction_id'] for item in bindings]
    if any(item not in source_order for item in ids):
        raise RoadbookError('candidate binding references unknown instruction')
    if len(set(ids)) != len(ids) or ids != sorted(ids, key=source_order.index):
        raise RoadbookError('candidate anchor occurrence order changed')
    if any(not isinstance(item.get('evidence_ref'), str) or not item['evidence_ref'].strip() for item in bindings):
        raise RoadbookError('candidate coordinate evidence required')
    return [RouteAnchor(item['instruction_id'], item['lat_e7'], item['lon_e7']) for item in bindings]


def load_runtime(path):
    manifest = json.loads(path.read_text(encoding='utf-8'))
    common = manifest['source_pbf_sha256']
    if not isinstance(common, str) or not re.fullmatch(r'[0-9a-f]{64}', common):
        raise RoadbookError('common OSM hash required')
    if (manifest.get('benchmark_eligible') is not True
            or manifest.get('driving_side_status') != 'VERIFIED_LEFT_HAND_TRAFFIC'
            or not isinstance(manifest.get('driving_side_evidence'), str)
            or not manifest['driving_side_evidence'].strip()):
        raise RoadbookError('administrative/driving-side validation evidence required')
    for provider in ('OSRM', 'VALHALLA'):
        record = manifest['providers'][provider]
        if record['status'] != 'BUILT' or record['source_pbf_sha256'] != common:
            raise RoadbookError('both providers must be built from the same source PBF')
        if (not re.fullmatch(r'ghcr\.io/[\w/-]+@sha256:[0-9a-f]{64}', record['image'])
                or not re.fullmatch(r'[0-9a-f]{64}', record['profile_sha256'])):
            raise RoadbookError('pinned provider image and profile required')
    return manifest


def recording_transport(output, section_id, provider):
    native = (OSRMAdapter._native_http_transport if provider == 'OSRM'
              else OSRMAdapter._http_transport)

    def transport(url, payload):
        # Preserve native maneuvers, snap locations and geometry BEFORE normalization.
        # "request" records semantic options; OSRM serializes these into GET query parameters.
        request_path = output / f'{section_id}-{provider}-request.json'
        request_path.write_text(json.dumps({'url': url, 'payload': payload}, indent=2), encoding='utf-8')
        response = native(url, payload)
        response_path = output / f'{section_id}-{provider}-native-response.json'
        response_path.write_text(json.dumps(response, indent=2), encoding='utf-8')
        return response
    return transport


def run(fixture, output, mode, anchors_file=None, runtime_file=None):
    if mode not in ('PREP', 'REVIEW'):
        raise RoadbookError('M1 accepts PREP/REVIEW only')
    source = json.loads((fixture / 'source.json').read_text(encoding='utf-8'))
    if sha256(fixture / source['source_image']) != source['source_image_sha256']:
        raise RoadbookError('source image digest mismatch')
    text = (fixture / source['transcription_file']).read_text(encoding='utf-8')
    roadbook = parse_roadbook(text)
    result = evaluate_roadbook(roadbook, source)
    result['source_image_sha256'] = source['source_image_sha256']
    result['mode'] = mode
    result['created_at_utc'] = datetime.now(timezone.utc).isoformat()
    result['provider_results'] = []
    if bool(anchors_file) != bool(runtime_file):
        raise RoadbookError('candidate anchors and runtime manifest must be supplied together')
    runtime = load_runtime(runtime_file) if runtime_file else None
    bindings_by_section = json.loads(anchors_file.read_text(encoding='utf-8')) if anchors_file else {}
    output.mkdir(parents=True, exist_ok=False)
    (output / 'source-transcription.txt').write_text(text, encoding='utf-8')
    (output / 'source-metadata.json').write_text(json.dumps(source, indent=2), encoding='utf-8')
    if runtime:
        result['runtime_manifest_sha256'] = sha256(runtime_file)
        result['candidate_bindings_sha256'] = sha256(anchors_file)
        (output / 'runtime-manifest.json').write_text(json.dumps(runtime, indent=2), encoding='utf-8')
        (output / 'candidate-bindings.json').write_text(json.dumps(bindings_by_section, indent=2), encoding='utf-8')
        for section in roadbook['sections']:
            key = section['section_id']
            if key not in bindings_by_section:
                continue
            anchors = candidate_anchors(section, bindings_by_section[key])
            results = {}
            for provider in ('OSRM', 'VALHALLA'):
                record = runtime['providers'][provider]
                try:
                    if provider == 'OSRM':
                        native = OSRMAdapter(record['base_url'], transport=recording_transport(output, key, provider)).route(
                            anchors, runtime['source_pbf_sha256'], record['profile_sha256'], mode=mode)
                    else:
                        native = ValhallaAdapter(record['base_url'], transport=recording_transport(output, key, provider)).route(
                            anchors, mode=mode, graph_dataset_id=runtime['source_pbf_sha256'],
                            profile_digest=record['profile_sha256'], valhalla_build=record['image'])
                    results[provider] = native
                    (output / f'{key}-{provider}.json').write_text(json.dumps(native, indent=2), encoding='utf-8')
                    result['provider_results'].append({
                        'section_id': key, 'provider': provider, 'status': 'RESPONSE_RECEIVED',
                        'candidates': [assess_candidate(section, c) for c in native['candidates']],
                    })
                except (URLError, TimeoutError, OSError, RouteCandidateError, ValueError) as exc:
                    result['provider_results'].append({
                        'section_id': key, 'provider': provider, 'status': 'FAILED',
                        'error_type': type(exc).__name__, 'error': str(exc),
                    })
            if len(results) == 2:
                comparison = compare_provider_candidates(
                    osrm=results['OSRM'], valhalla=results['VALHALLA'],
                    official_distance_mm=section['d_auth_mm'])
                (output / f'{key}-comparison.json').write_text(json.dumps(comparison, indent=2), encoding='utf-8')
        responses = result['provider_results']
        expected = {(section, provider) for section in ('B', 'C', 'D') for provider in ('OSRM', 'VALHALLA')}
        actual = {(item['section_id'], item['provider']) for item in responses if item['status'] == 'RESPONSE_RECEIVED'}
        result['provider_benchmark_status'] = 'RESPONSES_RECEIVED_NOT_VALIDATED' if expected <= actual else 'INCOMPLETE'
    result['evidence_files_sha256'] = {
        p.name: sha256(p) for p in sorted(output.glob('*.json'))
    }
    (output / 'benchmark.json').write_text(json.dumps(result, indent=2, ensure_ascii=False), encoding='utf-8')
    print(json.dumps({key: result[key] for key in (
        'status', 'arithmetic_status', 'total_declared_leg_distance_mm',
        'total_duration_ms', 'provider_benchmark_status')}, indent=2))
    return result


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--fixture', type=Path, default=ROOT / 'tests/fixtures/rotr_surabaya')
    parser.add_argument('--output', type=Path, required=True)
    parser.add_argument('--mode', choices=['PREP', 'REVIEW'], required=True)
    parser.add_argument('--anchors', type=Path)
    parser.add_argument('--runtime-manifest', type=Path)
    args = parser.parse_args()
    result = run(args.fixture, args.output, args.mode, args.anchors, args.runtime_manifest)
    return 2 if result['arithmetic_status'] != 'ARITHMETIC_VALID' or result['provider_benchmark_status'] == 'INCOMPLETE' else 0


if __name__ == '__main__':
    raise SystemExit(main())
