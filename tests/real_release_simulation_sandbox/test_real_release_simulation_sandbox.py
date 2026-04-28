from __future__ import annotations

import json
import subprocess
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[2]
BUILDER = (
    ROOT
    / "real_release_simulation_sandbox"
    / "tools"
    / "build_real_release_simulation_sandbox.py"
)

REQUIRED_DIRECTORIES = [
    "real_release_simulation_sandbox",
    "sandbox_release_authority_fixture",
    "simulated_durable_approval_record",
    "sandbox_release_snapshot",
    "sandbox_release_execution_plan",
    "sandbox_release_execution_result",
    "sandbox_post_release_validation",
    "sandbox_release_projection_and_mcp_preview",
    "sandbox_release_rollback_drill",
    "original_release_rollback_comparison",
    "release_simulation_cieu_residual",
    "real_release_simulation_readiness",
]

REQUIRED_FILES = [
    "real_release_simulation_sandbox/README.md",
    "real_release_simulation_sandbox/tools/build_real_release_simulation_sandbox.py",
    "real_release_simulation_sandbox/real_release_simulation_sandbox_contract.json",
    "real_release_simulation_sandbox/real_release_simulation_input_fixture.json",
    "real_release_simulation_sandbox/real_release_simulation_run.json",
    "real_release_simulation_sandbox/real_release_simulation_summary.json",
    "real_release_simulation_sandbox/real_release_simulation_report.md",
    "sandbox_release_authority_fixture/sandbox_release_authority_fixture.json",
    "sandbox_release_authority_fixture/simulated_release_operator_confirmation.json",
    "sandbox_release_authority_fixture/simulated_rollback_operator_confirmation.json",
    "sandbox_release_authority_fixture/sandbox_release_authority_denied_scope.json",
    "sandbox_release_authority_fixture/sandbox_release_authority_summary.json",
    "sandbox_release_authority_fixture/sandbox_release_authority_report.md",
    "simulated_durable_approval_record/simulated_durable_approval_record.json",
    "simulated_durable_approval_record/simulated_approval_record_integrity_check.json",
    "simulated_durable_approval_record/simulated_approval_record_scope_check.json",
    "simulated_durable_approval_record/simulated_approval_record_storage_blocker.json",
    "simulated_durable_approval_record/simulated_approval_record_summary.json",
    "simulated_durable_approval_record/simulated_approval_record_report.md",
    "sandbox_release_snapshot/sandbox_release_snapshot_manifest.json",
    "sandbox_release_snapshot/sandbox_pre_release_projection_policy_snapshot.json",
    "sandbox_release_snapshot/sandbox_pre_release_mcp_boundary_snapshot.json",
    "sandbox_release_snapshot/sandbox_pre_release_y_star_lineage_snapshot.json",
    "sandbox_release_snapshot/sandbox_snapshot_integrity_check.json",
    "sandbox_release_snapshot/sandbox_release_snapshot_summary.json",
    "sandbox_release_snapshot/sandbox_release_snapshot_report.md",
    "sandbox_release_execution_plan/sandbox_release_execution_plan.json",
    "sandbox_release_execution_plan/sandbox_release_operation_sequence.json",
    "sandbox_release_execution_plan/sandbox_release_allowed_operations.json",
    "sandbox_release_execution_plan/sandbox_release_denied_operations.json",
    "sandbox_release_execution_plan/sandbox_release_execution_summary.json",
    "sandbox_release_execution_plan/sandbox_release_execution_report.md",
    "sandbox_release_execution_result/sandbox_release_execution_result.json",
    "sandbox_release_execution_result/sandbox_released_projection_policy_snapshot.json",
    "sandbox_release_execution_result/sandbox_released_mcp_boundary_policy_snapshot.json",
    "sandbox_release_execution_result/sandbox_released_learning_policy_snapshot.json",
    "sandbox_release_execution_result/sandbox_real_state_unchanged_check.json",
    "sandbox_release_execution_result/sandbox_release_execution_receipt.json",
    "sandbox_release_execution_result/sandbox_release_execution_result_summary.json",
    "sandbox_release_execution_result/sandbox_release_execution_result_report.md",
    "sandbox_post_release_validation/sandbox_post_release_validation_result.json",
    "sandbox_post_release_validation/sandbox_post_release_test_matrix_result.json",
    "sandbox_post_release_validation/sandbox_post_release_y_star_non_mutation_check.json",
    "sandbox_post_release_validation/sandbox_post_release_mcp_non_bypass_check.json",
    "sandbox_post_release_validation/sandbox_post_release_writeback_boundary_check.json",
    "sandbox_post_release_validation/sandbox_post_release_validation_summary.json",
    "sandbox_post_release_validation/sandbox_post_release_validation_report.md",
    "sandbox_release_projection_and_mcp_preview/sandbox_post_release_projection_input.json",
    "sandbox_release_projection_and_mcp_preview/sandbox_post_release_behavior_y_star.json",
    "sandbox_release_projection_and_mcp_preview/sandbox_post_release_behavior_y_star_delta.json",
    "sandbox_release_projection_and_mcp_preview/sandbox_post_release_mcp_pre_u_candidate.json",
    "sandbox_release_projection_and_mcp_preview/sandbox_post_release_mcp_gate_preview.json",
    "sandbox_release_projection_and_mcp_preview/sandbox_post_release_mcp_receipt_preview.json",
    "sandbox_release_projection_and_mcp_preview/sandbox_release_projection_mcp_summary.json",
    "sandbox_release_projection_and_mcp_preview/sandbox_release_projection_mcp_report.md",
    "sandbox_release_rollback_drill/sandbox_release_rollback_plan_instance.json",
    "sandbox_release_rollback_drill/sandbox_release_rollback_result.json",
    "sandbox_release_rollback_drill/sandbox_post_rollback_projection_policy_snapshot.json",
    "sandbox_release_rollback_drill/sandbox_post_rollback_validation_result.json",
    "sandbox_release_rollback_drill/sandbox_release_rollback_delta.json",
    "sandbox_release_rollback_drill/sandbox_release_rollback_summary.json",
    "sandbox_release_rollback_drill/sandbox_release_rollback_report.md",
    "original_release_rollback_comparison/original_vs_sandbox_release_vs_rollback_comparison.json",
    "original_release_rollback_comparison/sandbox_release_effect_summary.json",
    "original_release_rollback_comparison/sandbox_release_rollback_effect_summary.json",
    "original_release_rollback_comparison/sandbox_release_safety_summary.json",
    "original_release_rollback_comparison/original_release_rollback_comparison_report.md",
    "release_simulation_cieu_residual/release_simulation_cieu_event_fixture.json",
    "release_simulation_cieu_residual/release_simulation_predicted_outcome.json",
    "release_simulation_cieu_residual/release_simulation_mock_actual_outcome.json",
    "release_simulation_cieu_residual/release_simulation_residual_delta.json",
    "release_simulation_cieu_residual/release_simulation_cieu_summary.json",
    "release_simulation_cieu_residual/release_simulation_cieu_report.md",
    "real_release_simulation_readiness/real_release_simulation_readiness.json",
    "real_release_simulation_readiness/real_release_simulation_readiness.md",
    "real_release_simulation_readiness/l5_13_recommended_next_step.json",
]

JSON_FILES = [path for path in REQUIRED_FILES if path.endswith(".json")]

REQUIRED_STAGES = [
    "load_l5_11_release_preflight",
    "load_release_candidate_package",
    "load_release_blocker_decision",
    "create_sandbox_release_authority_fixture",
    "create_simulated_durable_approval_record",
    "create_sandbox_pre_application_snapshot",
    "confirm_simulated_release_operator",
    "confirm_simulated_rollback_operator",
    "assemble_sandbox_release_execution_plan",
    "execute_sandbox_release_only",
    "verify_real_canonical_state_unchanged",
    "run_sandbox_post_release_validation",
    "run_sandbox_release_mcp_non_bypass_check",
    "run_sandbox_release_y_star_non_mutation_check",
    "emit_sandbox_release_receipt",
    "run_sandbox_rollback_drill",
    "verify_sandbox_rollback_restores_baseline",
    "compare_original_vs_sandbox_release_vs_rollback",
    "emit_release_simulation_cieu_like_fixture",
    "produce_l5_13_recommendation",
]

SAFETY_FLAG_FIELDS = {
    "live_execution_enabled",
    "behavior_execution_enabled",
    "external_action_enabled",
    "network_enabled",
    "scheduler_enabled",
    "daemon_enabled",
    "mcp_server_execution_enabled",
    "mcp_tool_execution_enabled",
    "cieu_persistence_enabled",
    "durable_approval_persistence_enabled",
    "real_approval_record_write_enabled",
    "brain_writeback_enabled",
    "memory_ingestion_enabled",
    "strategy_mutation_enabled",
    "candidate_auto_approval_enabled",
    "real_candidate_approval_enabled",
    "real_canonical_policy_mutation_enabled",
    "real_canonical_update_application_enabled",
    "real_release_execution_enabled",
    "real_y_star_direct_mutation_enabled",
    "y_star_gov_modification_enabled",
    "gov_mcp_modification_enabled",
    "semantic_truth_scoring_enabled",
    "raw_runtime_artifact_reading_enabled",
    "revenue_opportunity_discovery_enabled",
}

FALSE_FIELDS = SAFETY_FLAG_FIELDS | {
    "real_release_authorized",
    "real_release_performed",
    "real_approval_granted",
    "real_durable_record_written",
    "durable_db_write_performed",
    "durable_approval_record_written",
    "release_execution_allowed_now",
    "release_applied_to_real_canonical_policy",
    "real_canonical_policy_mutated",
    "brain_writeback_performed",
    "memory_ingestion_performed",
    "strategy_mutation_performed",
    "direct_y_star_mutation_performed",
    "mcp_execution_performed",
    "live_execution_performed",
    "network_called",
    "real_canonical_snapshot_created",
    "raw_db_dump_read",
    "log_content_read",
    "active_agent_marker_read",
    "secrets_captured",
    "mcp_server_started",
    "mcp_tool_called",
    "mcp_resource_mutated",
    "db_write_performed",
    "persistence_enabled",
    "ready_for_l6_revenue_opportunity_discovery",
}

SIMULATION_TRUE_FIELDS = {
    "sandbox_release_authority_fixture_created",
    "simulated_durable_record_created",
    "sandbox_snapshot_created",
    "simulated_release_operator_confirmed",
    "simulated_rollback_operator_confirmed",
    "sandbox_release_executed",
    "sandbox_post_validation_performed",
    "sandbox_rollback_drill_performed",
}

REQUIRED_INPUT_REFS = {
    "release_candidate_package/release_candidate_package.json",
    "release_candidate_package/release_candidate_scope.json",
    "release_scope_validation/release_scope_validation_result.json",
    "approval_record_preflight_validation/approval_record_preflight_validation_result.json",
    "snapshot_and_rollback_preflight/snapshot_preflight_validation_result.json",
    "snapshot_and_rollback_preflight/rollback_preflight_validation_result.json",
    "invariant_preflight_validation/y_star_non_mutation_preflight_result.json",
    "invariant_preflight_validation/mcp_non_bypass_preflight_result.json",
    "post_release_validation_matrix/post_release_validation_matrix.json",
    "release_operator_handoff_packet/release_operator_handoff_packet.json",
    "release_blocker_decision/release_blocker_decision.json",
    "controlled_real_release_preflight_readiness/controlled_real_release_preflight_readiness.json",
    "canonical_update_package_candidate/canonical_update_package_candidate.json",
    "versioned_canonical_patch_plan/versioned_canonical_patch_plan.json",
    "y_star_non_mutation_invariant/y_star_non_mutation_invariant.json",
    "controlled_approval_record_readiness/controlled_approval_record_readiness.json",
}

MCP_CHECKS = {
    "no_mcp_call_without_behavior_y_star",
    "no_mcp_call_without_pre_u_candidate",
    "no_mcp_call_without_governance_decision",
    "no_mcp_call_without_bridge_receipt",
    "no_mcp_call_without_cieu_receipt",
    "no_mcp_call_without_residual_delta",
    "no_mcp_direct_brain_writeback",
    "no_mcp_direct_memory_ingestion",
}

RESIDUAL_CLASSES = {
    "simulated_authority_residual",
    "simulated_approval_record_residual",
    "sandbox_snapshot_residual",
    "sandbox_release_execution_residual",
    "y_star_invariant_residual",
    "mcp_non_bypass_residual",
    "post_release_validation_residual",
    "rollback_residual",
    "real_state_unchanged_residual",
    "real_release_blocker_residual",
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


def load_json(relative_path: str) -> Any:
    with (ROOT / relative_path).open("r", encoding="utf-8") as f:
        return json.load(f)


def walk_values(value: Any):
    if isinstance(value, dict):
        for key, item in value.items():
            yield key, item
            yield from walk_values(item)
    elif isinstance(value, list):
        for item in value:
            yield from walk_values(item)


def test_builder_regenerates_artifacts() -> None:
    result = run_command(["python3", str(BUILDER.relative_to(ROOT))])
    assert result.returncode == 0, result.stderr
    assert "L5.12 real release simulation sandbox artifacts generated." in result.stdout


def test_required_directories_and_json_parse() -> None:
    for directory in REQUIRED_DIRECTORIES:
        assert (ROOT / directory).is_dir(), directory
    for path in REQUIRED_FILES:
        assert (ROOT / path).exists(), path
    for path in JSON_FILES:
        assert load_json(path)


def test_contract_stages_and_flags() -> None:
    contract = load_json("real_release_simulation_sandbox/real_release_simulation_sandbox_contract.json")
    assert set(REQUIRED_STAGES).issubset(contract["simulation_stages"])
    assert set(SAFETY_FLAG_FIELDS).issubset(contract["safety_flags"])
    assert all(contract["safety_flags"][field] is False for field in SAFETY_FLAG_FIELDS)
    assert set(SIMULATION_TRUE_FIELDS).issubset(contract["simulation_flags"])
    assert all(contract["simulation_flags"][field] is True for field in SIMULATION_TRUE_FIELDS)


def test_all_real_safety_flags_remain_false() -> None:
    for path in JSON_FILES:
        payload = load_json(path)
        for key, value in walk_values(payload):
            if key in FALSE_FIELDS:
                assert value is False, f"{path}: {key} should be false"
            if key == "safety_flags":
                assert set(SAFETY_FLAG_FIELDS).issubset(value)
                assert all(value[field] is False for field in SAFETY_FLAG_FIELDS)


def test_input_fixture_references_l5_7_to_l5_11_artifacts() -> None:
    fixture = load_json("real_release_simulation_sandbox/real_release_simulation_input_fixture.json")
    refs = set(fixture["input_refs"].values())
    assert REQUIRED_INPUT_REFS.issubset(refs)


def test_sandbox_release_authority_and_simulated_record() -> None:
    authority = load_json("sandbox_release_authority_fixture/sandbox_release_authority_fixture.json")
    assert authority["authority_mode"] == "sandbox_release_simulation_only"
    assert authority["simulated_release_authority_present"] is True
    assert authority["real_release_authority_present"] is False
    assert authority["real_approval_granted"] is False
    assert authority["real_release_authorized"] is False

    release_operator = load_json("sandbox_release_authority_fixture/simulated_release_operator_confirmation.json")
    rollback_operator = load_json("sandbox_release_authority_fixture/simulated_rollback_operator_confirmation.json")
    assert release_operator["confirmation_mode"] == "sandbox_only"
    assert release_operator["confirmed_for_sandbox_release_simulation"] is True
    assert release_operator["confirmed_for_real_release"] is False
    assert rollback_operator["confirmation_mode"] == "sandbox_only"
    assert rollback_operator["confirmed_for_sandbox_rollback_drill"] is True
    assert rollback_operator["confirmed_for_real_rollback"] is False

    denied = load_json("sandbox_release_authority_fixture/sandbox_release_authority_denied_scope.json")
    for required in [
        "real release",
        "real approval",
        "durable approval persistence",
        "real canonical update",
        "brain writeback",
        "memory ingestion",
        "strategy mutation",
        "direct Y* mutation",
        "MCP execution",
        "external action",
        "network",
        "L6 revenue opportunity discovery",
    ]:
        assert required in denied["denied_scope"]

    record = load_json("simulated_durable_approval_record/simulated_durable_approval_record.json")
    assert record["record_mode"] == "simulated_durable_record_fixture"
    assert record["simulated_durable_record_created"] is True
    assert record["real_durable_record_written"] is False
    assert record["durable_db_write_performed"] is False
    assert record["real_approval_granted"] is False
    assert record["real_release_authorized"] is False
    assert load_json("simulated_durable_approval_record/simulated_approval_record_storage_blocker.json")


def test_sandbox_snapshot_and_release_plan_boundaries() -> None:
    snapshot = load_json("sandbox_release_snapshot/sandbox_release_snapshot_manifest.json")
    assert snapshot["snapshot_mode"] == "sandbox_pre_application_snapshot"
    assert snapshot["raw_db_dump_read"] is False
    assert snapshot["log_content_read"] is False
    assert snapshot["active_agent_marker_read"] is False
    assert snapshot["secrets_captured"] is False
    assert snapshot["real_canonical_snapshot_created"] is False

    lineage = load_json("sandbox_release_snapshot/sandbox_pre_release_y_star_lineage_snapshot.json")
    assert lineage["projection_derived_relationship"] is True
    assert lineage["residual_did_not_directly_mutate_y_star"] is True
    assert lineage["release_must_preserve_lineage"] is True

    plan = load_json("sandbox_release_execution_plan/sandbox_release_execution_plan.json")
    assert plan["release_mode"] == "sandbox_release_simulation"
    assert plan["real_release_authorized"] is False
    assert plan["real_application_authorized"] is False

    denied = load_json("sandbox_release_execution_plan/sandbox_release_denied_operations.json")
    for field in [
        "real_canonical_policy_mutation_denied",
        "real_canonical_update_application_denied",
        "real_brain_writeback_denied",
        "real_memory_ingestion_denied",
        "real_strategy_mutation_denied",
        "direct_y_star_mutation_denied",
        "mcp_execution_denied",
        "external_action_denied",
        "network_api_call_denied",
        "y_star_gov_modification_denied",
        "gov_mcp_modification_denied",
        "l6_revenue_opportunity_discovery_denied",
    ]:
        assert denied[field] is True


def test_sandbox_release_execution_and_real_state_unchanged() -> None:
    result = load_json("sandbox_release_execution_result/sandbox_release_execution_result.json")
    assert result["release_applied_to_sandbox"] is True
    assert result["release_applied_to_real_canonical_policy"] is False
    for field in [
        "real_canonical_policy_mutated",
        "brain_writeback_performed",
        "memory_ingestion_performed",
        "strategy_mutation_performed",
        "direct_y_star_mutation_performed",
        "mcp_execution_performed",
        "live_execution_performed",
        "network_called",
    ]:
        assert result[field] is False

    unchanged = load_json("sandbox_release_execution_result/sandbox_real_state_unchanged_check.json")
    for field in [
        "real_canonical_policy_unchanged",
        "real_brain_unchanged",
        "real_memory_unchanged",
        "real_strategy_unchanged",
        "y_star_gov_unmodified",
        "gov_mcp_unmodified",
    ]:
        assert unchanged[field] is True


def test_post_release_validation_and_projection_mcp_preview() -> None:
    validation = load_json("sandbox_post_release_validation/sandbox_post_release_validation_result.json")
    assert validation["validation_status"] == "sandbox_post_release_validated"
    assert validation["real_state_unchanged"] is True
    assert validation["mission_y_star_lineage_preserved"] is True
    assert validation["behavior_y_star_still_projection_derived"] is True
    assert validation["residual_did_not_directly_mutate_y_star"] is True
    assert validation["MCP_non_bypass_preserved"] is True
    assert validation["brain_writeback_still_blocked"] is True
    assert validation["memory_ingestion_still_blocked"] is True
    assert validation["rollback_drill_available"] is True

    y_star = load_json("sandbox_post_release_validation/sandbox_post_release_y_star_non_mutation_check.json")
    assert y_star["mission_y_star_not_rewritten"] is True
    assert y_star["behavior_y_star_not_directly_overwritten"] is True
    assert y_star["release_changes_are_policy_mediated"] is True
    assert y_star["residual_did_not_become_new_y_star"] is True
    assert y_star["actual_y_did_not_become_new_y_star"] is True

    mcp = load_json("sandbox_post_release_validation/sandbox_post_release_mcp_non_bypass_check.json")
    for field in MCP_CHECKS:
        assert mcp[field] is True

    behavior = load_json("sandbox_release_projection_and_mcp_preview/sandbox_post_release_behavior_y_star.json")
    assert behavior["pre_u_validation_still_required"] is True
    assert behavior["live_behavior_authorized"] is False
    assert behavior["behavior_execution_enabled"] is False
    assert behavior["applied_to_real_canonical_policy"] is False
    assert behavior["applied_to_brain"] is False
    assert behavior["applied_to_memory"] is False
    assert behavior["direct_y_star_mutation_performed"] is False

    delta = load_json("sandbox_release_projection_and_mcp_preview/sandbox_post_release_behavior_y_star_delta.json")
    assert delta["no_direct_y_star_mutation"] is True

    receipt = load_json("sandbox_release_projection_and_mcp_preview/sandbox_post_release_mcp_receipt_preview.json")
    assert receipt["real_execution_performed"] is False
    assert receipt["mcp_server_started"] is False
    assert receipt["mcp_tool_called"] is False
    assert receipt["mcp_resource_mutated"] is False
    assert receipt["network_called"] is False
    assert receipt["persistence_mode"] == "none"


def test_rollback_drill_and_comparison() -> None:
    rollback = load_json("sandbox_release_rollback_drill/sandbox_release_rollback_result.json")
    assert rollback["rollback_performed_in_sandbox"] is True
    assert rollback["real_canonical_policy_modified"] is False
    assert rollback["brain_modified"] is False
    assert rollback["memory_modified"] is False
    assert rollback["strategy_modified"] is False
    assert rollback["y_star_direct_mutation_performed"] is False
    assert rollback["mcp_execution_performed"] is False

    post = load_json("sandbox_release_rollback_drill/sandbox_post_rollback_validation_result.json")
    assert post["baseline_restored"] is True
    assert post["no_real_canonical_change"] is True
    assert post["no_brain_memory_change"] is True
    assert post["no_y_star_direct_mutation"] is True
    assert post["no_mcp_execution"] is True
    assert post["no_live_execution"] is True

    comparison = load_json(
        "original_release_rollback_comparison/original_vs_sandbox_release_vs_rollback_comparison.json"
    )
    assert comparison["real_canonical_system_changed"] is False
    assert comparison["brain_memory_changed"] is False
    assert comparison["gov_repos_changed"] is False
    assert comparison["mcp_execution_performed"] is False


def test_release_simulation_cieu_residual_and_readiness() -> None:
    event = load_json("release_simulation_cieu_residual/release_simulation_cieu_event_fixture.json")
    for field in ["X_t", "U_t", "Y_star_t", "Y_t_plus_1", "R_t_plus_1"]:
        assert field in event
    assert event["event_mode"] == "real_release_simulation_sandbox_fixture"
    assert event["persistence_enabled"] is False
    assert event["db_write_performed"] is False
    assert event["durable_approval_record_written"] is False
    assert event["real_release_performed"] is False

    residual = load_json("release_simulation_cieu_residual/release_simulation_residual_delta.json")
    classes = {item["class"] for item in residual["residual_classes"]}
    assert RESIDUAL_CLASSES.issubset(classes)

    readiness = load_json("real_release_simulation_readiness/real_release_simulation_readiness.json")
    for field in [
        "real_release_still_blocked",
        "real_approval_still_blocked",
        "durable_persistence_still_blocked",
        "real_canonical_application_still_blocked",
        "brain_writeback_still_blocked",
        "memory_ingestion_still_blocked",
        "y_star_direct_mutation_still_blocked",
        "mcp_execution_still_blocked",
        "y_star_gov_unmodified",
        "gov_mcp_unmodified",
        "ready_for_l5_13_live_boundary_no_go_decision_framework",
    ]:
        assert readiness[field] is True
    assert readiness["ready_for_l6_revenue_opportunity_discovery"] is False


def test_console_command_reports_release_simulation() -> None:
    result = run_command(["python3", "console_read_model/cli/team_console.py", "release-simulation-sandbox"])
    assert result.returncode == 0, result.stderr
    assert "L5.12 real release simulation sandbox defined: True" in result.stdout
    assert "no real release authorized: True" in result.stdout
    assert "ready for L6 revenue opportunity discovery: False" in result.stdout
