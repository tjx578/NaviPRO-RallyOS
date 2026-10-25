import importlib.util
import json
from pathlib import Path
from unittest.mock import patch

import pytest

ROOT = Path(__file__).resolve().parents[2]


def module(name):
    spec = importlib.util.spec_from_file_location(name, ROOT / 'tools' / (name + '.py'))
    result = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(result)
    return result


def test_runtime_compose_uses_pins_loopback_and_separate_readonly_volumes(tmp_path):
    runtime = module('routing_runtime')
    images = json.loads((ROOT / 'infra/routing/images.lock.json').read_text())
    runtime.validate_images(images)
    config = runtime.compose_config(tmp_path, images)
    assert set(config['services']) == {'osrm', 'valhalla'}
    sources = []
    for service in config['services'].values():
        assert service['ports'][0].startswith('127.0.0.1:')
        assert service['volumes'][0]['read_only'] is True
        assert '@sha256:' in service['image']
        sources.append(service['volumes'][0]['source'])
    assert len(set(sources)) == 2
    images['OSRM']['image'] = 'ghcr.io/project-osrm/osrm-backend:latest'
    with pytest.raises(ValueError):
        runtime.validate_images(images)


def test_road_only_extract_cannot_admit_graph_build(tmp_path):
    runtime = module('routing_runtime')
    source = tmp_path / 'fake.pbf'
    source.write_bytes(b'synthetic')
    provenance = {'source_pbf_sha256': runtime.digest(source),
                  'admin_pbf_sha256': runtime.digest(source),
                  'source_url': 'synthetic', 'osm_base': 'synthetic',
                  'admin_source_url': 'synthetic', 'admin_coverage_evidence': 'synthetic',
                  'administrative_coverage': 'NOT_VERIFIED'}
    with pytest.raises(ValueError, match='administrative coverage'):
        runtime.validate_inputs(source, source, provenance)
    provenance['source_pbf_sha256'] = '0' * 64
    with pytest.raises(ValueError, match='digest'):
        runtime.validate_inputs(source, source, provenance)


def test_missing_engine_stops_before_any_build_or_pull(tmp_path):
    runtime = module('routing_runtime')
    source = tmp_path / 'synthetic.pbf'
    source.write_bytes(b'synthetic')
    provenance = {'source_pbf_sha256': runtime.digest(source),
                  'admin_pbf_sha256': runtime.digest(source),
                  'source_url': 'synthetic', 'osm_base': 'synthetic',
                  'admin_source_url': 'synthetic', 'admin_coverage_evidence': 'synthetic',
                  'administrative_coverage': 'REVIEWED_COMPLETE_FOR_SURABAYA'}
    metadata = tmp_path / 'source.json'
    metadata.write_text(json.dumps(provenance))
    images = json.loads((ROOT / 'infra/routing/images.lock.json').read_text())
    with patch.object(runtime, 'preflight', return_value={'status': 'BLOCKED'}), patch.object(runtime.subprocess, 'run') as run:
        receipt = runtime.build(source, source, metadata, tmp_path / 'result', images)
    run.assert_not_called()
    assert receipt['status'] == 'BLOCKED'
    assert receipt['providers'] == {}


def test_benchmark_rejects_unvalidated_driving_side_and_mixed_snapshots(tmp_path):
    benchmark = module('m1_benchmark')
    images = json.loads((ROOT / 'infra/routing/images.lock.json').read_text())
    manifest = {'source_pbf_sha256': 'a' * 64, 'providers': {}}
    for provider in ('OSRM', 'VALHALLA'):
        manifest['providers'][provider] = {
            'status': 'BUILT', 'source_pbf_sha256': 'a' * 64,
            'image': images[provider]['image'], 'profile_sha256': 'b' * 64}
    path = tmp_path / 'manifest.json'
    path.write_text(json.dumps(manifest))
    with pytest.raises(ValueError, match='driving-side'):
        benchmark.load_runtime(path)
    manifest.update(benchmark_eligible=True, driving_side_status='VERIFIED_LEFT_HAND_TRAFFIC',
                    driving_side_evidence='synthetic fixture only')
    path.write_text(json.dumps(manifest))
    assert benchmark.load_runtime(path) == manifest
    manifest['providers']['OSRM']['source_pbf_sha256'] = 'c' * 64
    path.write_text(json.dumps(manifest))
    with pytest.raises(ValueError, match='same source PBF'):
        benchmark.load_runtime(path)


def test_native_maneuver_evidence_is_saved_before_normalization(tmp_path):
    benchmark = module('m1_benchmark')
    response = {'code': 'Ok', 'routes': [{'legs': [{'steps': [{'maneuver': {'type': 'turn'}}]}]}]}
    with patch.object(benchmark.OSRMAdapter, '_native_http_transport', return_value=response):
        transport = benchmark.recording_transport(tmp_path, 'B', 'OSRM')
        assert transport('http://127.0.0.1:5000/route/v1/driving', {'coordinates': [[0, 0], [1, 1]]}) == response
    saved = json.loads((tmp_path / 'B-OSRM-native-response.json').read_text())
    assert saved == response
