"""Gate-report and eight-division contracts, not execution of 16 route gates.

All reports below are synthetic. Schema acceptance cannot establish input truth,
authenticate a reviewer, run a routing engine, or authorize a NaviPack release.
"""
import copy
from pathlib import Path

import pytest
import yaml
from jsonschema import Draft202012Validator

ROOT = Path(__file__).resolve().parents[2]


def read_yaml(path):
    return yaml.safe_load((ROOT / path).read_text(encoding="utf-8"))


SPEC = read_yaml("contracts/openapi/navipro-rallyos.openapi.yaml")
GATES = read_yaml("governance/release-gates.yaml")
AGENTS = read_yaml("governance/agent-divisions.yaml")
COCKPIT = read_yaml("governance/cockpit-role-action-policy.yaml")
GATE_NAMES = SPEC["components"]["schemas"]["GateResult"]["properties"]["gate"]["enum"]
REPORT_SCHEMA = {
    "$schema": SPEC["jsonSchemaDialect"],
    "$ref": "#/components/schemas/ValidationReport",
    "components": SPEC["components"],
}
VALIDATOR = Draft202012Validator(REPORT_SCHEMA)
OPERATIONS = {
    operation["operationId"]: operation
    for item in SPEC["paths"].values()
    for operation in item.values()
    if isinstance(operation, dict) and "operationId" in operation
}


def report():
    return {
        "report_id": "SYNTHETIC-REPORT",
        "subject_id": "SYNTHETIC-REVISION",
        "release_status": "PASS",
        "gates": [{"gate": name, "result": "PASS"} for name in GATE_NAMES],
    }


def test_complete_report_accepts_any_gate_order_and_optional_messages():
    Draft202012Validator.check_schema(REPORT_SCHEMA)
    example = report()
    example["gates"].reverse()
    example["gates"][0]["message"] = "Synthetic result, not runtime evidence"
    VALIDATOR.validate(example)


@pytest.mark.parametrize("result", ["FAIL", "NOT_RUN"])
def test_each_nonpass_gate_blocks_pass_but_can_be_reported_as_hold(result):
    for index, name in enumerate(GATE_NAMES):
        example = report()
        example["gates"][index]["result"] = result
        assert not VALIDATOR.is_valid(example), name
        example["release_status"] = "HOLD"
        VALIDATOR.validate(example)


def test_duplicate_gate_cannot_hide_a_missing_gate_even_with_distinct_messages():
    for index, name in enumerate(GATE_NAMES):
        example = report()
        example["gates"][index] = copy.deepcopy(example["gates"][(index + 1) % 16])
        example["gates"][index]["message"] = "Different object, same gate identity"
        assert not VALIDATOR.is_valid(example), name
        example["release_status"] = "HOLD"
        assert not VALIDATOR.is_valid(example), name


def test_sixteen_duplicate_failed_gates_cannot_claim_pass():
    example = report()
    example["gates"] = [
        {"gate": "SCHEMA_DOMAIN", "result": "FAIL", "message": str(index)}
        for index in range(16)
    ]
    assert not VALIDATOR.is_valid(example)


@pytest.mark.parametrize("count", [0, 15, 17])
def test_partial_or_overfull_report_is_invalid_even_when_hold(count):
    example = report()
    example["release_status"] = "HOLD"
    example["gates"] = (example["gates"] * 2)[:count]
    assert not VALIDATOR.is_valid(example)


@pytest.mark.parametrize("row", [
    {"gate": "INVENTED_GATE", "result": "PASS"},
    {"gate": "SCHEMA_DOMAIN", "result": "APPROVED"},
    {"gate": "SCHEMA_DOMAIN", "result": True},
    {"gate": "SCHEMA_DOMAIN"},
    {"result": "PASS"},
])
def test_unknown_or_malformed_gate_result_is_rejected(row):
    example = report()
    example["gates"][0] = row
    assert not VALIDATOR.is_valid(example)


def test_all_pass_does_not_force_release_when_an_external_hold_remains():
    example = report()
    example["release_status"] = "HOLD"
    VALIDATOR.validate(example)
    example["release_status"] = "PUBLISHED"
    assert not VALIDATOR.is_valid(example)


def test_gate_registry_matches_canonical_api_and_real_specialist_ids():
    assert [gate["name"] for gate in GATES["gates"]] == GATE_NAMES
    assert [gate["id"] for gate in GATES["gates"]] == [f"QG-{n:02d}" for n in range(1, 17)]
    assert [division["division_id"] for division in AGENTS["divisions"]] == list(range(1, 9))
    specialist_ids = {division["role_id"] for division in AGENTS["divisions"]}
    assert specialist_ids == set(range(2, 10))
    assert AGENTS["orchestrator"]["role_id"] == 1
    for gate in GATES["gates"]:
        assert gate["evidence_lead_role_id"] in specialist_ids
        assert set(gate["supporting_role_ids"]) <= specialist_ids
        assert gate["evidence_lead_role_id"] not in gate["supporting_role_ids"]
        assert gate["required_evidence"]


def test_agent_allowlists_resolve_to_proposal_safe_api_contracts_only():
    denied = set(AGENTS["shared_agent_policy"]["forbidden_operations"])
    for role in [AGENTS["orchestrator"], *AGENTS["divisions"]]:
        assert len(role["operations"]) == len(set(role["operations"]))
        for operation_id in role["operations"]:
            assert operation_id not in denied
            operation = OPERATIONS[operation_id]
            assert operation["x-navipro-mcp"]["enabled"] is True
            assert set(operation["x-navipro-mode"]) <= {"PREP", "REVIEW"}
            assert operation["x-navipro-authority"] in {"READ", "AGENT_PROPOSE"}
            assert operation["x-navipro-side-effect"] in {"NONE", "STAGING_MUTATION", "DRAFT_MUTATION", "PROPOSAL_ONLY"}
    for operation_id in denied:
        assert OPERATIONS[operation_id]["x-navipro-mcp"]["enabled"] is False


def test_gate_pass_and_live_control_cannot_be_delegated_to_ai():
    policy = AGENTS["shared_agent_policy"]
    assert policy["may_set_authoritative_gate_result"] is False
    assert policy["may_mutate_active_pack"] is False
    assert policy["live"]["generative_agent_execution"] == "DENY"
    assert policy["live"]["gps_timer_cue_execution"] == "DETERMINISTIC_DEVICE_SERVICES_ONLY"
    for action in ("agent_approve_route", "agent_publish_navipack", "live_route_reroute"):
        assert COCKPIT["actions"][action]["allow"] == []
    assert GATES["evaluation_policy"]["authoritative_evaluator"] == "DETERMINISTIC_VALIDATOR"
    assert GATES["evaluation_policy"]["valid_report_is_release_authorization"] is False
    assert GATES["evaluation_policy"]["release_on_fail_or_not_run"] == "HOLD"


def test_thresholds_and_revisions_preserve_existing_route_time_authority():
    source_policy = read_yaml("governance/route-distance-time-location-policy.yaml")
    assert source_policy["time_constraints"]["universal_tolerance"] == "NOT_DEFINED"
    assert GATES["threshold_policy"]["universal_distance_residual_percent"] is None
    assert GATES["threshold_policy"]["universal_inter_sub_gap_mm"] is None
    assert GATES["threshold_policy"]["missing_required_profile"] == "HOLD"
    assert GATES["revision_policy"]["before_compile"] == "RERUN_ALL_16_ON_SAME_FROZEN_INPUTS"
    assert GATES["revision_policy"]["stale_report"] == "HOLD"
    assert AGENTS["handoff"]["stale_revision"] == "REJECT_AND_REPLAN"
    assert AGENTS["handoff"]["active_pack_revision"] == "NEVER_CHANGED_BY_HANDOFF"


def test_declarations_do_not_claim_implemented_evaluators_or_agent_services():
    for registry in (GATES, AGENTS):
        assert registry["status"] == "CONTRACT_ONLY"
        assert registry["runtime"] == "NOT_IMPLEMENTED"
    assert AGENTS["handoff"]["status"] == "DESIGN_ONLY"
