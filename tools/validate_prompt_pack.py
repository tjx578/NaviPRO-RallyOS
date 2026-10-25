"""Static prompt assembly checks only; never an AI behavior evaluation."""
from pathlib import Path
import yaml

ROOT = Path(__file__).resolve().parents[1]
PACK = ROOT / 'knowledge/prompts/time-rally-navigator-v1'


def validate():
    manifest = yaml.safe_load((PACK / 'manifest.yaml').read_text())
    registry = yaml.safe_load((ROOT / manifest['source_binding']['division_registry']).read_text())
    expected = [(registry['orchestrator']['role_id'], None, registry['orchestrator']['name'])]
    expected += [(d['role_id'], d['division_id'], d['name']) for d in registry['divisions']]
    actual = [(r['role_id'], r['division_id'], r['name']) for r in manifest['roles']]
    if actual != expected or len(actual) != 9:
        raise ValueError('role/division identity mismatch')
    for key in ('division_registry', 'gate_registry', 'cockpit_policy', 'route_time_policy', 'api_contract'):
        if not (ROOT / manifest['source_binding'][key]).is_file():
            raise ValueError(f'missing source binding: {key}')
    for name in [manifest['assembly']['shared_prompt']] + [r['file'] for r in manifest['roles']]:
        path = (PACK / name).resolve()
        if not path.is_relative_to(PACK.resolve()) or not path.is_file() or not path.read_text().strip():
            raise ValueError('missing or out-of-pack prompt file')
    if manifest['status'] != 'TEMPLATE_ONLY' or manifest['assembly']['allowed_workspace_modes'] != ['PREP', 'REVIEW']:
        raise ValueError('unreviewed prompt authority/state change')
    for filename in manifest['examples']:
        example = yaml.safe_load((PACK / filename).read_text())
        if example['authority'] != 'PROPOSE_ONLY' or example['validation']['release_eligibility'] != 'HOLD':
            raise ValueError('example claims release authority')
    cases = yaml.safe_load((PACK / manifest['evaluation']['cases']).read_text())
    ids = [case['id'] for case in cases['cases']]
    if len(ids) != len(set(ids)) or not ids:
        raise ValueError('empty or duplicate evaluation cases')
    if any(not set(case['roles']) <= set(range(1, 10)) for case in cases['cases']):
        raise ValueError('evaluation case references unknown role')
    print(f'PASS: 9 prompt roles; {len(ids)} behavioral cases structurally checked, behavior NOT_EXECUTED')


if __name__ == '__main__':
    validate()
