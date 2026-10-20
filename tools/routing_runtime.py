"""Prepare two isolated development engines from identical road PBF bytes.

Commands are argv lists, never shell-built strings. This experimental recipe
must be exercised on a healthy Docker host before claiming runtime readiness.
"""
import argparse
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import re
import shutil
import subprocess

ROOT = Path(__file__).resolve().parents[1]


def digest(path):
    value = hashlib.sha256()
    with path.open('rb') as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b''):
            value.update(chunk)
    return value.hexdigest()


def write_json(path, value):
    path.write_text(json.dumps(value, indent=2) + '\n', encoding='utf-8')


def validate_images(images):
    for name in ('OSRM', 'VALHALLA'):
        record = images[name]
        if not re.fullmatch(r'ghcr\.io/[\w/-]+@sha256:[0-9a-f]{64}', record['image']):
            raise ValueError('immutable GHCR image digest required')
        if record['platform'] != 'linux/amd64':
            raise ValueError('recipe currently validated structurally for linux/amd64 only')


def preflight():
    try:
        proc = subprocess.run(['docker', 'info', '--format', '{{json .}}'],
                              capture_output=True, text=True, timeout=25)
        if proc.returncode:
            return {'status': 'BLOCKED', 'reason': 'DOCKER_ENGINE_UNAVAILABLE',
                    'detail': proc.stderr[-4000:]}
        info = json.loads(proc.stdout)
        if info.get('OSType') != 'linux':
            return {'status': 'BLOCKED', 'reason': 'LINUX_ENGINE_REQUIRED'}
        return {'status': 'ENGINE_REACHABLE_NOT_BENCHMARKED',
                'server_version': info.get('ServerVersion'),
                'engine_memory_bytes': info.get('MemTotal')}
    except (OSError, subprocess.TimeoutExpired, ValueError) as exc:
        return {'status': 'BLOCKED', 'reason': 'DOCKER_PREFLIGHT_FAILED',
                'detail': str(exc)}


def validate_inputs(roads, admins, provenance):
    for file in (roads, admins):
        if not file.is_file() or file.stat().st_size == 0:
            raise ValueError('nonempty road and administrative PBF inputs required')
    if provenance.get('source_pbf_sha256') != digest(roads):
        raise ValueError('road PBF digest does not match source manifest')
    if provenance.get('admin_pbf_sha256') != digest(admins):
        raise ValueError('administrative PBF digest does not match source manifest')
    for field in ('source_url', 'osm_base', 'admin_source_url', 'admin_coverage_evidence'):
        if not isinstance(provenance.get(field), str) or not provenance[field].strip():
            raise ValueError(f'{field} required')
    if provenance.get('administrative_coverage') != 'REVIEWED_COMPLETE_FOR_SURABAYA':
        raise ValueError('administrative coverage review is required; road-only extracts are insufficient')


def compose_config(output, images):
    services = {}
    for provider, port, command in (
        ('OSRM', 5000, ['osrm-routed', '--algorithm', 'mld', '--threads', '2', '/data/roads.osrm']),
        ('VALHALLA', 8002, ['valhalla_service', '/data/valhalla.json', '2']),
    ):
        services[provider.lower()] = {
            'image': images[provider]['image'], 'platform': 'linux/amd64',
            'ports': [f'127.0.0.1:{port}:{port}'],
            'volumes': [{'type': 'bind', 'source': str((output / provider.lower()).resolve()),
                         'target': '/data', 'read_only': True}],
            'command': command, 'cpus': 2, 'mem_limit': '2g',
            'restart': 'no',
        }
    return {'name': 'navipro-m1', 'services': services}


def build(roads, admins, provenance_path, output, images):
    validate_images(images)
    provenance = json.loads(provenance_path.read_text(encoding='utf-8'))
    validate_inputs(roads, admins, provenance)
    output.mkdir(parents=True, exist_ok=False)
    receipt = {'status': 'NOT_BUILT', 'created_at_utc': datetime.now(timezone.utc).isoformat(),
               'source_pbf_sha256': digest(roads), 'admin_pbf_sha256': digest(admins),
               'source_provenance': provenance, 'providers': {},
               'benchmark_eligible': False, 'driving_side_status': 'NOT_VERIFIED'}
    health = preflight()
    receipt['preflight'] = health
    if health['status'] == 'BLOCKED':
        receipt['status'] = 'BLOCKED'
        write_json(output / 'runtime-manifest.json', receipt)
        return receipt
    steps = []

    def run(argv, log_name):
        steps.append({'argv': argv, 'log': log_name, 'status': 'RUNNING'})
        write_json(output / 'build-steps.json', steps)
        with (output / log_name).open('wb') as log:
            subprocess.run(argv, stdout=log, stderr=subprocess.STDOUT, check=True, timeout=7200)
        steps[-1]['status'] = 'SUCCEEDED'
        write_json(output / 'build-steps.json', steps)

    def container(provider, mounts, command):
        argv = ['docker', 'run', '--rm', '--platform', 'linux/amd64',
                '--cpus', '2', '--memory', '4g']
        for source, target, readonly in mounts:
            argv.extend(['--mount', f'type=bind,source={source.resolve()},target={target}' +
                         (',readonly' if readonly else '')])
        return argv + [images[provider]['image']] + command

    try:
        for provider in ('OSRM', 'VALHALLA'):
            run(['docker', 'pull', '--platform', 'linux/amd64', images[provider]['image']],
                provider.lower() + '-pull.log')
        osrm = output / 'osrm'
        valhalla = output / 'valhalla'
        osrm.mkdir()
        valhalla.mkdir()
        shutil.copyfile(roads, osrm / 'roads.osm.pbf')
        mounts = [(osrm, '/data', False)]
        run(container('OSRM', mounts, ['sh', '-c', 'cp /opt/car.lua /data/car.lua']),
            'osrm-profile.log')
        for binary, args in (
            ('osrm-extract', ['-p', '/opt/car.lua', '/data/roads.osm.pbf']),
            ('osrm-partition', ['/data/roads.osrm']),
            ('osrm-customize', ['/data/roads.osrm']),
        ):
            run(container('OSRM', mounts, [binary, '--threads', '2'] + args), binary + '.log')
        run(container('VALHALLA', [
            (valhalla, '/data', False), (roads, '/input/roads.osm.pbf', True),
            (admins, '/input/admin.osm.pbf', True),
            (ROOT / 'infra/routing/build-valhalla.sh', '/build.sh', True),
        ], ['sh', '/build.sh']), 'valhalla-build.log')
        if not (osrm / 'roads.osrm.partition').is_file() or not (valhalla / 'tiles.tar').is_file():
            raise ValueError('expected graph artifacts missing after build')
        # Detect source changes while building; preserve failed outputs for investigation.
        validate_inputs(roads, admins, provenance)
        if digest(osrm / 'roads.osm.pbf') != receipt['source_pbf_sha256']:
            raise ValueError('OSRM source copy digest mismatch')
        for provider, folder, profile, port in (
            ('OSRM', osrm, 'car.lua', 5000),
            ('VALHALLA', valhalla, 'valhalla.json', 8002),
        ):
            artifacts = {str(p.relative_to(folder)): digest(p) for p in sorted(folder.rglob('*')) if p.is_file()}
            receipt['providers'][provider] = {
                'status': 'BUILT', 'source_pbf_sha256': receipt['source_pbf_sha256'],
                'image': images[provider]['image'], 'profile_sha256': digest(folder / profile),
                'vehicle_profile': 'car' if provider == 'OSRM' else 'auto (static default costing)',
                'artifacts_sha256': artifacts, 'base_url': f'http://127.0.0.1:{port}',
            }
        receipt['status'] = 'BUILT_NOT_STARTED'
        write_json(output / 'compose.json', compose_config(output, images))
    except (OSError, ValueError, subprocess.SubprocessError) as exc:
        receipt['status'] = 'BUILD_FAILED'
        receipt['error'] = str(exc)
    write_json(output / 'runtime-manifest.json', receipt)
    return receipt


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('action', choices=['preflight', 'build'])
    parser.add_argument('--output', type=Path, required=True)
    parser.add_argument('--roads', type=Path)
    parser.add_argument('--admins', type=Path)
    parser.add_argument('--source-manifest', type=Path)
    args = parser.parse_args()
    if args.action == 'preflight':
        args.output.mkdir(parents=True, exist_ok=False)
        result = preflight()
        write_json(args.output / 'preflight.json', result)
    else:
        if not all((args.roads, args.admins, args.source_manifest)):
            parser.error('build requires --roads, --admins, --source-manifest')
        images = json.loads((ROOT / 'infra/routing/images.lock.json').read_text(encoding='utf-8'))
        result = build(args.roads.resolve(), args.admins.resolve(), args.source_manifest, args.output, images)
    print(json.dumps(result, indent=2))
    return 0 if result['status'] not in ('BLOCKED', 'BUILD_FAILED') else 2


if __name__ == '__main__':
    raise SystemExit(main())
