from __future__ import annotations

import json
import subprocess
from pathlib import Path
from typing import Any

import pytest


ROOT = Path(__file__).resolve().parents[2]
BUILDER = (
    ROOT
    / "governed_mcp_dry_run_adapter"
    / "tools"
    / "build_governed_mcp_dry_run_adapter.py"
)

REQUIRED_DIRECTORIES = [
    "governed_mcp_dry_run_adapter",
    "mcp_request_intent_projection",
    "mcp_pre_u_packet_candidate",
    "mcp_governance_decision_envelope",
    "mcp_bridge_authorization_receipt",
    "governed_mcp_call_candidate",
    "mcp_dry_run_receipt_and_cieu",
    "mcp_residual_and_learning_candidate",
    "governed_mcp_adapter_readiness",
]

REQUIRED_FILES = [
    "governed_mcp_dry_run_adapter/README.md",
    "governed_mcp_dry_run_adapter/tools/build_governed_mcp_dry_run_adapter.py",
    "governed_mcp_dry_run_adapter/governed_mcp_dry_run_adapter_contract.json",
    "governed_mcp_dry_run_adapter/governed_mcp_dry_run_input_fixture.json",
    "governed_mcp_dry_run_adapter/governed_mcp_dry_run_adapter_run.json",
    "governed_mcp_dry_run_adapter/governed_mcp_dry_run_adapter_summary.json",
    "governed_mcp_dry_run_adapter/governed_mcp_dry_run_adapter_report.md",
    "mcp_request_intent_projection/mcp_request_intent.json",
    "mcp_request_intent_projection/mcp_request_context_fixture.json",
    "mcp_request_intent_projection/mcp_requested_operation_boundary.json",
    "mcp_request_intent_projection/mcp_request_intent_summary.json",
    "mcp_request_intent_projection/mcp_request_intent_report.md",
    "mcp_pre_u_packet_candidate/mcp_call_pre_u_packet_candidate.json",
    "mcp_pre_u_packet_candidate/mcp_pre_u_to_y_star_gov_expectation_map.json",
    "mcp_pre_u_packet_candidate/mcp_pre_u_gap_report.md",
    "mcp_pre_u_packet_candidate/mcp_pre_u_summary.json",
    "mcp_governance_decision_envelope/mcp_governance_decision_envelope.json",
    "mcp_governance_decision_envelope/mcp_decision_reason_trace.json",
    "mcp_governance_decision_envelope/mcp_governance_decision_gap_report.md",
    "mcp_governance_decision_envelope/mcp_governance_decision_summary.json",
    "mcp_bridge_authorization_receipt/mcp_bridge_authorization_receipt.json",
    "mcp_bridge_authorization_receipt/mcp_bridge_denied_scope.json",
    "mcp_bridge_authorization_receipt/mcp_bridge_receipt_summary.json",
    "mcp_bridge_authorization_receipt/mcp_bridge_receipt_report.md",
    "governed_mcp_call_candidate/governed_mcp_call_candidate.json",
    "governed_mcp_call_candidate/governed_mcp_call_execution_plan.json",
    "governed_mcp_call_candidate/mcp_real_execution_blocker.json",
    "governed_mcp_call_candidate/governed_mcp_call_summary.json",
    "governed_mcp_call_candidate/governed_mcp_call_report.md",
    "mcp_dry_run_receipt_and_cieu/mcp_dry_run_receipt.json",
    "mcp_dry_run_receipt_and_cieu/mcp_cieu_event_fixture.json",
    "mcp_dry_run_receipt_and_cieu/mcp_predicted_outcome.json",
    "mcp_dry_run_receipt_and_cieu/mcp_mock_actual_outcome.json",
    "mcp_dry_run_receipt_and_cieu/mcp_receipt_cieu_summary.json",
    "mcp_dry_run_receipt_and_cieu/mcp_receipt_cieu_report.md",
    "mcp_residual_and_learning_candidate/mcp_residual_delta.json",
    "mcp_residual_and_learning_candidate/mcp_residual_classification.json",
    "mcp_residual_and_learning_candidate/mcp_learning_candidate.json",
    "mcp_residual_and_learning_candidate/mcp_review_queue_entry.json",
    "mcp_residual_and_learning_candidate/mcp_residual_learning_summary.json",
    "mcp_residual_and_learning_candidate/mcp_residual_learning_report.md",
    "governed_mcp_adapter_readiness/governed_mcp_adapter_readiness.json",
    "governed_mcp_adapter_readiness/governed_mcp_adapter_readiness.md",
    "governed_mcp_adapter_readiness/l5_7_recommended_next_step.json",
]

JSON_FILES = [path for path in REQUIRED_FILES if path.endswith(".json")]

REQUIRED_STAGES = [
    "load_behavior_level_y_star",
    "load_cross_repo_non_bypass_contract",
    "derive_mcp_request_intent",
    "generate_mcp_call_pre_u_packet_candidate",
    "map_pre_u_candidate_to_y_star_gov_expectations",
    "generate_dry_run_governance_decision_envelope",
    "generate_bridge_authorization_receipt",
    "generate_governed_mcp_call_candidate",
    "block_real_mcp_execution",
    "generate_mcp_dry_run_receipt",
    "emit_mcp_cieu_like_event_fixture",
    "compute_mcp_residual_delta",
    "create_review_only_mcp_learning_candidate",
    "produce_l5_7_recommendation",
]

REQUIRED_RESIDUAL_CLASSES = {
    "mcp_projection_alignment_residual",
    "mcp_pre_u_mapping_residual",
    "governance_decision_residual",
    "bridge_receipt_residual",
    "mcp_execution_blocker_residual",
    "cieu_receipt_residual",
    "evidence_gap_residual",
    "learning_queue_residual",
    "live_blocker_residual",
    "writeback_blocker_residual",
}

FALSE_FLAG_FIELDS = {
    "live_execution_enabled",
    "behavior_execution_enabled",
    "external_action_enabled",
    "network_enabled",
    "scheduler_enabled",
    "daemon_enabled",
    "mcp_server_execution_enabled",
    "mcp_tool_execution_enabled",
    "mcp_resource_mutation_enabled",
    "cieu_persistence_enabled",
    "brain_writeback_enabled",
    "memory_ingestion_enabled",
    "candidate_auto_approval_enabled",
    "canonical_policy_mutation_enabled",
    "y_star_gov_modification_enabled",
    "gov_mcp_modification_enabled",
    "semantic_truth_scoring_enabled",
    "raw_runtime_artifact_reading_enabled",
    "revenue_opportunity_discovery_enabled",
    "production_ready",
    "live_execution_authorized",
    "behavior_execution_authorized",
    "external_action_authorized",
    "mcp_tool_execution_authorized",
    "canonical_y_star_gov_validation_performed",
    "real_mcp_execution_authorized",
    "real_execution_performed",
    "mcp_server_started",
    "mcp_tool_called",
    "mcp_resource_mutated",
    "network_called",
    "persistence_enabled",
    "db_write_performed",
    "eligible_for_direct_brain_writeback",
    "eligible_for_direct_memory_ingestion",
    "eligible_for_candidate_auto_approval",
    "eligible_for_canonical_policy_mutation",
    "approved",
    "applied",
    "live_learning_enabled",
    "ready_for_l6_revenue_opportunity_discovery",
}


def run_command(args: list[str]) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        args,
        cwd=ROOT,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        check=False,
    )


@pytest.fixture(scope="module", autouse=True)
def generated_governed_mcp_dry_run_adapter() -> None:
    result = run_command(["python3", str(BUILDER.relative_to(ROOT))])
    assert result.returncode == 0, result.stdout + result.stderr


def load_json(relative_path: str) -> Any:
    path = ROOT / relative_path
    assert path.exists(), f"missing file: {relative_path}"
    return json.loads(path.read_text(encoding="utf-8"))


def walk_json(value: Any):
    if isinstance(value, dict):
        yield value
        for child in value.values():
            yield from walk_json(child)
    elif isinstance(value, list):
        for child in value:
            yield from walk_json(child)


def assert_false_flags(document: Any) -> None:
    for node in walk_json(document):
        for field in FALSE_FLAG_FIELDS:
            if field in node:
                assert node[field] is False, f"{field} must remain false"


def test_required_l5_6_directories_and_files_exist() -> None:
    for directory in REQUIRED_DIRECTORIES:
        assert (ROOT / directory).is_dir(), f"missing directory: {directory}"
    for relative_path in REQUIRED_FILES:
        assert (ROOT / relative_path).exists(), f"missing file: {relative_path}"


def test_all_required_json_artifacts_parse_and_keep_flags_false() -> None:
    for relative_path in JSON_FILES:
        document = load_json(relative_path)
        assert_false_flags(document)


def test_adapter_contract_contains_required_stages_and_disabled_flags() -> None:
    contract = load_json("governed_mcp_dry_run_adapter/governed_mcp_dry_run_adapter_contract.json")
    assert contract["adapter_stages"] == REQUIRED_STAGES
    for field in [
        "mcp_non_bypass_requirements",
        "governance_boundary_requirements",
        "bridge_receipt_requirements",
        "cieu_receipt_requirements",
        "residual_requirements",
        "forbidden_operations",
        "non_goals",
    ]:
        assert contract[field]
    assert_false_flags(contract)


def test_input_fixture_references_l5_5_non_bypass_and_interface_artifacts() -> None:
    fixture = load_json("governed_mcp_dry_run_adapter/governed_mcp_dry_run_input_fixture.json")
    refs = fixture["input_refs"]
    assert refs["governed_mcp_interface_contract"] == (
        "governed_mcp_interface_contract/governed_mcp_interface_contract.json"
    )
    assert refs["mcp_call_pre_u_boundary_contract"] == (
        "governed_mcp_interface_contract/mcp_call_pre_u_boundary_contract.json"
    )
    assert refs["mcp_call_cieu_receipt_contract"] == (
        "governed_mcp_interface_contract/mcp_call_cieu_receipt_contract.json"
    )
    assert refs["required_gate_sequence"] == "cross_repo_non_bypass_proof/required_gate_sequence.json"
    assert refs["forbidden_bypass_path_matrix"] == (
        "cross_repo_non_bypass_proof/forbidden_bypass_path_matrix.json"
    )


def test_mcp_request_intent_is_internal_dry_run_and_boundary_denies_unsafe_patterns() -> None:
    intent = load_json("mcp_request_intent_projection/mcp_request_intent.json")
    context = load_json("mcp_request_intent_projection/mcp_request_context_fixture.json")
    boundary = load_json("mcp_request_intent_projection/mcp_requested_operation_boundary.json")

    assert intent["source_behavior_y_star_id"]
    assert intent["internal_only"] is True
    assert intent["dry_run_only"] is True
    assert context["internal_only"] is True
    assert context["dry_run_only"] is True
    assert context["no_real_mcp_server"] is True
    assert context["no_real_tool_execution"] is True
    denied = " ".join(boundary["forbidden_operations"]).lower()
    for term in ["external", "network", "db/log/raw", "brain", "memory", "revenue"]:
        assert term in denied
    assert boundary["mcp_execution_forbidden_now"] is True


def test_mcp_pre_u_packet_candidate_requires_y_star_gov_validation_and_no_tool_execution() -> None:
    packet = load_json("mcp_pre_u_packet_candidate/mcp_call_pre_u_packet_candidate.json")
    assert packet["declared_Y_star"]
    assert packet["Xt"]
    assert packet["X_t"]
    assert packet["candidate_U"]
    assert packet["requested_operation"]
    assert packet["execution_boundary"]
    assert packet["safety_flags"]
    assert packet["dry_run_only"] is True
    assert packet["requires_y_star_gov_validation_before_execution"] is True
    assert packet["mcp_tool_execution_authorized"] is False
    assert packet["live_execution_authorized"] is False


def test_decision_and_bridge_authorize_dry_run_only() -> None:
    decision = load_json("mcp_governance_decision_envelope/mcp_governance_decision_envelope.json")
    bridge = load_json("mcp_bridge_authorization_receipt/mcp_bridge_authorization_receipt.json")
    denied = load_json("mcp_bridge_authorization_receipt/mcp_bridge_denied_scope.json")

    assert decision["decision"] in {"allow_mcp_dry_run_only", "require_revision", "deny"}
    assert decision["decision"] == "allow_mcp_dry_run_only"
    assert decision["canonical_y_star_gov_validation_performed"] is False
    assert decision["y_star_gov_validation_required_before_live"] is True
    assert bridge["authorization_mode"] == "dry_run_adapter_only"
    assert bridge["real_mcp_execution_authorized"] is False
    assert bridge["cieu_receipt_required"] is True
    assert bridge["residual_delta_required"] is True
    for field in [
        "real_mcp_execution_denied",
        "external_action_denied",
        "network_api_call_denied",
        "db_log_raw_runtime_artifact_read_denied",
        "brain_writeback_denied",
        "memory_ingestion_denied",
        "canonical_policy_mutation_denied",
        "candidate_approval_denied",
    ]:
        assert denied[field] is True


def test_governed_mcp_call_candidate_blocks_real_execution() -> None:
    call = load_json("governed_mcp_call_candidate/governed_mcp_call_candidate.json")
    blocker = load_json("governed_mcp_call_candidate/mcp_real_execution_blocker.json")
    assert call["real_execution_performed"] is False
    assert call["mcp_server_started"] is False
    assert call["mcp_tool_called"] is False
    assert call["mcp_resource_mutated"] is False
    assert call["network_called"] is False
    assert blocker["real_mcp_execution_blocked"] is True


def test_mcp_dry_run_receipt_and_cieu_fixture_are_structural_only() -> None:
    receipt = load_json("mcp_dry_run_receipt_and_cieu/mcp_dry_run_receipt.json")
    cieu = load_json("mcp_dry_run_receipt_and_cieu/mcp_cieu_event_fixture.json")
    for field in [
        "source_pre_u_packet_id",
        "source_decision_envelope_id",
        "source_bridge_receipt_id",
        "requested_U",
        "allowed_U",
        "actual_result_summary",
    ]:
        assert receipt[field]
    assert receipt["real_execution_performed"] is False
    assert receipt["mcp_server_started"] is False
    assert receipt["mcp_tool_called"] is False
    assert receipt["mcp_resource_mutated"] is False
    assert receipt["network_called"] is False
    for field in ["X_t", "U_t", "Y_star_t", "Y_t_plus_1", "R_t_plus_1"]:
        assert field in cieu
    assert cieu["persistence_enabled"] is False
    assert cieu["db_write_performed"] is False


def test_mcp_residual_and_learning_candidate_are_review_only() -> None:
    residual = load_json("mcp_residual_and_learning_candidate/mcp_residual_delta.json")
    candidate = load_json("mcp_residual_and_learning_candidate/mcp_learning_candidate.json")
    assert set(residual["residual_classes"]) == REQUIRED_RESIDUAL_CLASSES
    assert candidate["eligible_for_review_queue"] is True
    assert candidate["eligible_for_direct_brain_writeback"] is False
    assert candidate["eligible_for_direct_memory_ingestion"] is False
    assert candidate["eligible_for_candidate_auto_approval"] is False
    assert candidate["eligible_for_canonical_policy_mutation"] is False
    assert candidate["approved"] is False
    assert candidate["applied"] is False


def test_readiness_marks_reference_repos_unmodified_mcp_not_executed_and_l6_blocked() -> None:
    readiness = load_json("governed_mcp_adapter_readiness/governed_mcp_adapter_readiness.json")
    assert readiness["y_star_gov_unmodified"] is True
    assert readiness["gov_mcp_unmodified"] is True
    assert readiness["mcp_server_not_started"] is True
    assert readiness["mcp_tool_not_executed"] is True
    assert readiness["mcp_resource_not_mutated"] is True
    assert readiness["ready_for_l5_7_controlled_canonical_learning_design"] is True
    assert readiness["ready_for_l6_revenue_opportunity_discovery"] is False


def test_builder_static_safety_constraints() -> None:
    source = BUILDER.read_text(encoding="utf-8")
    assert "shell=True" not in source
    assert "subprocess.run" not in source
    assert "requests." not in source
    assert "urllib.request" not in source
    assert ".open(" not in source


def test_console_read_model_integration_passes() -> None:
    loader = run_command(["python3", "console_read_model/loader/build_team_console_snapshot.py"])
    assert loader.returncode == 0, loader.stdout + loader.stderr
    validator = run_command(["python3", "console_read_model/validation/validate_team_read_model.py"])
    assert validator.returncode == 0, validator.stdout + validator.stderr
    console = run_command(["python3", "console_read_model/cli/team_console.py", "governed-mcp-adapter"])
    assert console.returncode == 0, console.stdout + console.stderr
    assert "L5.6 governed MCP dry-run adapter defined: True" in console.stdout
    assert "real MCP execution blocked: True" in console.stdout
    assert "no MCP server/tool executed: True" in console.stdout
    assert "ready for L5.7 controlled canonical learning design: True" in console.stdout
    assert "ready for L6 revenue opportunity discovery: False" in console.stdout
