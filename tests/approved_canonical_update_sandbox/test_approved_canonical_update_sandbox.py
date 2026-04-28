from __future__ import annotations

import json
import subprocess
from pathlib import Path
from typing import Any

import pytest


ROOT = Path(__file__).resolve().parents[2]
BUILDER = (
    ROOT
    / "approved_canonical_update_sandbox"
    / "tools"
    / "build_approved_canonical_update_sandbox.py"
)

REQUIRED_DIRECTORIES = [
    "approved_canonical_update_sandbox",
    "sandbox_approval_fixture",
    "sandbox_canonical_state_baseline",
    "sandbox_patch_application",
    "sandbox_post_update_validation",
    "sandbox_reprojection_and_mcp_preview",
    "sandbox_update_cieu_residual",
    "sandbox_rollback_validation",
    "original_sandbox_rollback_comparison",
    "approved_sandbox_update_readiness",
]

REQUIRED_FILES = [
    "approved_canonical_update_sandbox/README.md",
    "approved_canonical_update_sandbox/tools/build_approved_canonical_update_sandbox.py",
    "approved_canonical_update_sandbox/approved_canonical_update_sandbox_contract.json",
    "approved_canonical_update_sandbox/approved_canonical_update_sandbox_input_fixture.json",
    "approved_canonical_update_sandbox/approved_canonical_update_sandbox_run.json",
    "approved_canonical_update_sandbox/approved_canonical_update_sandbox_summary.json",
    "approved_canonical_update_sandbox/approved_canonical_update_sandbox_report.md",
    "sandbox_approval_fixture/sandbox_approval_protocol.json",
    "sandbox_approval_fixture/sandbox_approval_decision_fixture.json",
    "sandbox_approval_fixture/sandbox_approval_scope_boundary.json",
    "sandbox_approval_fixture/sandbox_approval_denied_scope.json",
    "sandbox_approval_fixture/sandbox_approval_summary.json",
    "sandbox_approval_fixture/sandbox_approval_report.md",
    "sandbox_canonical_state_baseline/sandbox_canonical_baseline_manifest.json",
    "sandbox_canonical_state_baseline/sandbox_projection_policy_baseline.json",
    "sandbox_canonical_state_baseline/sandbox_learning_policy_baseline.json",
    "sandbox_canonical_state_baseline/sandbox_mcp_boundary_policy_baseline.json",
    "sandbox_canonical_state_baseline/sandbox_y_star_lineage_baseline.json",
    "sandbox_canonical_state_baseline/sandbox_baseline_summary.json",
    "sandbox_canonical_state_baseline/sandbox_baseline_report.md",
    "sandbox_patch_application/sandbox_patch_application_plan.json",
    "sandbox_patch_application/sandbox_patch_application_result.json",
    "sandbox_patch_application/sandbox_updated_projection_policy_snapshot.json",
    "sandbox_patch_application/sandbox_updated_learning_policy_snapshot.json",
    "sandbox_patch_application/sandbox_updated_mcp_boundary_policy_snapshot.json",
    "sandbox_patch_application/sandbox_patch_application_blocker_for_real.json",
    "sandbox_patch_application/sandbox_patch_application_summary.json",
    "sandbox_patch_application/sandbox_patch_application_report.md",
    "sandbox_post_update_validation/sandbox_post_update_validation_plan.json",
    "sandbox_post_update_validation/sandbox_post_update_validation_result.json",
    "sandbox_post_update_validation/sandbox_invariant_validation_result.json",
    "sandbox_post_update_validation/sandbox_y_star_non_mutation_check.json",
    "sandbox_post_update_validation/sandbox_mcp_non_bypass_check.json",
    "sandbox_post_update_validation/sandbox_post_update_validation_summary.json",
    "sandbox_post_update_validation/sandbox_post_update_validation_report.md",
    "sandbox_reprojection_and_mcp_preview/sandbox_next_cycle_projection_input.json",
    "sandbox_reprojection_and_mcp_preview/sandbox_reprojected_behavior_y_star.json",
    "sandbox_reprojection_and_mcp_preview/sandbox_behavior_y_star_delta_from_baseline.json",
    "sandbox_reprojection_and_mcp_preview/sandbox_mcp_request_intent_preview.json",
    "sandbox_reprojection_and_mcp_preview/sandbox_mcp_pre_u_candidate_preview.json",
    "sandbox_reprojection_and_mcp_preview/sandbox_mcp_governance_decision_preview.json",
    "sandbox_reprojection_and_mcp_preview/sandbox_mcp_bridge_receipt_preview.json",
    "sandbox_reprojection_and_mcp_preview/sandbox_mcp_dry_run_receipt_preview.json",
    "sandbox_reprojection_and_mcp_preview/sandbox_reprojection_mcp_summary.json",
    "sandbox_reprojection_and_mcp_preview/sandbox_reprojection_mcp_report.md",
    "sandbox_update_cieu_residual/sandbox_update_cieu_event_fixture.json",
    "sandbox_update_cieu_residual/sandbox_update_predicted_outcome.json",
    "sandbox_update_cieu_residual/sandbox_update_mock_actual_outcome.json",
    "sandbox_update_cieu_residual/sandbox_update_residual_delta.json",
    "sandbox_update_cieu_residual/sandbox_update_learning_candidate_preview.json",
    "sandbox_update_cieu_residual/sandbox_update_cieu_summary.json",
    "sandbox_update_cieu_residual/sandbox_update_cieu_report.md",
    "sandbox_rollback_validation/sandbox_rollback_plan_instance.json",
    "sandbox_rollback_validation/sandbox_rollback_result.json",
    "sandbox_rollback_validation/sandbox_post_rollback_projection_policy_snapshot.json",
    "sandbox_rollback_validation/sandbox_post_rollback_validation_result.json",
    "sandbox_rollback_validation/sandbox_rollback_delta.json",
    "sandbox_rollback_validation/sandbox_rollback_summary.json",
    "sandbox_rollback_validation/sandbox_rollback_report.md",
    "original_sandbox_rollback_comparison/original_vs_sandbox_vs_rollback_comparison.json",
    "original_sandbox_rollback_comparison/sandbox_update_effect_summary.json",
    "original_sandbox_rollback_comparison/rollback_effect_summary.json",
    "original_sandbox_rollback_comparison/sandbox_learning_safety_summary.json",
    "original_sandbox_rollback_comparison/original_sandbox_rollback_report.md",
    "approved_sandbox_update_readiness/approved_sandbox_update_readiness.json",
    "approved_sandbox_update_readiness/approved_sandbox_update_readiness.md",
    "approved_sandbox_update_readiness/l5_9_recommended_next_step.json",
]

JSON_FILES = [path for path in REQUIRED_FILES if path.endswith(".json")]

REQUIRED_STAGES = [
    "load_l5_7_canonical_update_package_candidate",
    "load_l5_7_versioned_patch_plan",
    "load_l5_7_y_star_non_mutation_invariant",
    "create_sandbox_approval_fixture",
    "create_sandbox_canonical_baseline",
    "apply_patch_to_sandbox_canonical_state_only",
    "verify_real_canonical_state_unchanged",
    "run_sandbox_post_update_validation",
    "generate_sandbox_projection_policy_snapshot",
    "run_sandbox_behavior_y_star_reprojection",
    "run_sandbox_governed_mcp_dry_run_preview",
    "compute_sandbox_update_residual_delta",
    "run_sandbox_rollback_plan",
    "verify_sandbox_rollback_restores_baseline",
    "compare_original_vs_sandbox_vs_rollback",
    "emit_sandbox_update_cieu_like_fixture",
    "produce_l5_9_recommendation",
]

REAL_FALSE_FIELDS = {
    "live_execution_enabled",
    "behavior_execution_enabled",
    "external_action_enabled",
    "network_enabled",
    "scheduler_enabled",
    "daemon_enabled",
    "mcp_server_execution_enabled",
    "mcp_tool_execution_enabled",
    "cieu_persistence_enabled",
    "brain_writeback_enabled",
    "memory_ingestion_enabled",
    "strategy_mutation_enabled",
    "candidate_auto_approval_enabled",
    "real_candidate_approval_enabled",
    "real_canonical_policy_mutation_enabled",
    "real_canonical_update_application_enabled",
    "real_y_star_direct_mutation_enabled",
    "semantic_truth_scoring_enabled",
    "raw_runtime_artifact_reading_enabled",
    "revenue_opportunity_discovery_enabled",
    "real_application_approved",
    "candidate_real_approved",
    "real_candidate_approved",
    "real_candidate_applied",
    "real_canonical_policy_mutation_performed",
    "real_canonical_update_application_performed",
    "real_canonical_files_modified",
    "real_canonical_policy_modified",
    "brain_writeback_performed",
    "memory_ingestion_performed",
    "strategy_mutation_performed",
    "direct_y_star_mutation_performed",
    "mcp_server_started",
    "mcp_tool_called",
    "mcp_resource_mutated",
    "network_called",
    "persistence_enabled",
    "db_write_performed",
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
def generated_approved_canonical_update_sandbox() -> None:
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


def assert_real_false_flags(document: Any) -> None:
    for node in walk_json(document):
        for field in REAL_FALSE_FIELDS:
            if field in node:
                assert node[field] is False, f"{field} must remain false"
        if "safety_flags" in node:
            assert all(value is False for value in node["safety_flags"].values())


def test_required_l5_8_directories_and_files_exist() -> None:
    for directory in REQUIRED_DIRECTORIES:
        assert (ROOT / directory).is_dir(), f"missing directory: {directory}"
    for relative_path in REQUIRED_FILES:
        assert (ROOT / relative_path).exists(), f"missing file: {relative_path}"


def test_all_required_json_artifacts_parse_and_keep_real_flags_false() -> None:
    for relative_path in JSON_FILES:
        document = load_json(relative_path)
        assert_real_false_flags(document)


def test_contract_contains_required_stages_and_sandbox_flags() -> None:
    contract = load_json(
        "approved_canonical_update_sandbox/approved_canonical_update_sandbox_contract.json"
    )
    assert contract["sandbox_stages"] == REQUIRED_STAGES
    assert all(value is False for value in contract["safety_flags"].values())
    sandbox_flags = contract["sandbox_flags"]
    assert sandbox_flags["sandbox_approval_fixture_created"] is True
    assert sandbox_flags["sandbox_patch_application_performed"] is True
    assert sandbox_flags["sandbox_projection_preview_generated"] is True
    assert sandbox_flags["sandbox_mcp_dry_run_preview_generated"] is True
    assert sandbox_flags["sandbox_rollback_performed"] is True
    for field in [
        "sandbox_approval_requirements",
        "sandbox_application_requirements",
        "y_star_non_mutation_requirements",
        "rollback_validation_requirements",
        "post_update_validation_requirements",
        "forbidden_operations",
        "non_goals",
    ]:
        assert contract[field]


def test_input_fixture_references_l5_7_l5_6_sources() -> None:
    fixture = load_json(
        "approved_canonical_update_sandbox/approved_canonical_update_sandbox_input_fixture.json"
    )
    refs = fixture["input_refs"]
    assert refs["canonical_update_package_candidate"] == (
        "canonical_update_package_candidate/canonical_update_package_candidate.json"
    )
    assert refs["versioned_patch_plan"] == (
        "versioned_canonical_patch_plan/versioned_canonical_patch_plan.json"
    )
    assert refs["rollback_plan"] == "rollback_and_audit_lineage/rollback_plan.json"
    assert refs["post_promotion_validation_plan"] == (
        "post_promotion_validation_plan/post_promotion_validation_plan.json"
    )
    assert refs["y_star_non_mutation_invariant"] == (
        "y_star_non_mutation_invariant/y_star_non_mutation_invariant.json"
    )
    assert refs["governed_mcp_adapter_readiness"] == (
        "governed_mcp_adapter_readiness/governed_mcp_adapter_readiness.json"
    )


def test_sandbox_approval_authorizes_only_sandbox_application() -> None:
    decision = load_json("sandbox_approval_fixture/sandbox_approval_decision_fixture.json")
    assert decision["approval_mode"] == "sandbox_only"
    assert decision["sandbox_application_approved"] is True
    assert decision["real_application_approved"] is False
    assert decision["candidate_real_approved"] is False
    denied = load_json("sandbox_approval_fixture/sandbox_approval_denied_scope.json")
    denied_text = " ".join(denied["denied_operations"])
    for phrase in [
        "real canonical policy mutation",
        "real canonical update application",
        "brain writeback",
        "memory ingestion",
        "strategy mutation",
        "direct Y* mutation",
        "live execution",
        "MCP execution",
        "external action",
        "network",
        "candidate auto-approval",
    ]:
        assert phrase in denied_text


def test_sandbox_baseline_and_patch_do_not_touch_real_state() -> None:
    manifest = load_json("sandbox_canonical_state_baseline/sandbox_canonical_baseline_manifest.json")
    assert manifest["baseline_mode"] == "generated_sandbox_copy"
    assert manifest["copied_into_sandbox_only"] is True
    assert manifest["real_canonical_files_modified"] is False
    lineage = load_json("sandbox_canonical_state_baseline/sandbox_y_star_lineage_baseline.json")
    assert lineage["mission_level_y_star_source"]
    assert lineage["behavior_level_y_star_source"]
    assert lineage["projection_derived_relationship_preserved"] is True
    result = load_json("sandbox_patch_application/sandbox_patch_application_result.json")
    assert result["applied_to_sandbox"] is True
    assert result["applied_to_real_canonical_policy"] is False
    assert result["applied_to_brain"] is False
    assert result["applied_to_memory"] is False
    assert result["applied_to_strategy"] is False
    assert result["direct_y_star_mutation_performed"] is False
    assert result["y_star_lineage_preserved"] is True
    assert (ROOT / "sandbox_patch_application/sandbox_patch_application_blocker_for_real.json").exists()


def test_sandbox_post_update_validation_preserves_invariants() -> None:
    result = load_json("sandbox_post_update_validation/sandbox_post_update_validation_result.json")
    for field in [
        "sandbox_patch_applied",
        "real_canonical_state_unchanged",
        "y_star_non_mutation_invariant_preserved",
        "mission_y_star_lineage_preserved",
        "behavior_y_star_still_projection_derived",
        "Pre-U_validation_still_required",
        "bridge_receipt_still_required",
        "CIEU_receipt_still_required",
        "MCP_non_bypass_preserved",
        "brain_writeback_still_blocked",
        "memory_ingestion_still_blocked",
        "live_execution_still_blocked",
        "external_action_still_blocked",
        "rollback_plan_available",
    ]:
        assert result[field] is True
    y_star = load_json("sandbox_post_update_validation/sandbox_y_star_non_mutation_check.json")
    for field in [
        "residual_did_not_become_new_y_star",
        "actual_y_did_not_become_new_y_star",
        "mission_y_star_not_rewritten",
        "behavior_y_star_not_directly_overwritten",
        "projected_behavior_y_star_changes_are_policy_mediated",
        "projection_lineage_preserved",
    ]:
        assert y_star[field] is True
    mcp = load_json("sandbox_post_update_validation/sandbox_mcp_non_bypass_check.json")
    for field in [
        "no_mcp_call_without_behavior_y_star",
        "no_mcp_call_without_pre_u_candidate",
        "no_mcp_call_without_governance_decision",
        "no_mcp_call_without_bridge_receipt",
        "no_mcp_call_without_cieu_receipt",
        "no_mcp_call_without_residual_delta",
        "no_mcp_direct_brain_writeback",
        "no_mcp_direct_memory_ingestion",
    ]:
        assert mcp[field] is True


def test_sandbox_reprojection_and_mcp_preview_are_dry_run_only() -> None:
    behavior = load_json("sandbox_reprojection_and_mcp_preview/sandbox_reprojected_behavior_y_star.json")
    assert behavior["pre_u_validation_still_required"] is True
    assert behavior["live_behavior_authorized"] is False
    assert behavior["behavior_execution_enabled"] is False
    assert behavior["applied_to_real_canonical_policy"] is False
    assert behavior["applied_to_brain"] is False
    assert behavior["applied_to_memory"] is False
    assert behavior["direct_y_star_mutation_performed"] is False
    delta = load_json(
        "sandbox_reprojection_and_mcp_preview/sandbox_behavior_y_star_delta_from_baseline.json"
    )
    assert delta["no_direct_y_star_mutation"] is True
    for field in [
        "projection_policy_mediated_delta",
        "evidence_requirement_delta",
        "boundary_contraction_delta",
        "pre_u_mapping_delta",
        "mcp_non_bypass_delta",
        "residual_classification_delta",
    ]:
        assert delta[field]
    pre_u = load_json("sandbox_reprojection_and_mcp_preview/sandbox_mcp_pre_u_candidate_preview.json")
    assert pre_u["requires_y_star_gov_validation_before_live_execution"] is True
    receipt = load_json("sandbox_reprojection_and_mcp_preview/sandbox_mcp_dry_run_receipt_preview.json")
    assert receipt["real_execution_performed"] is False
    assert receipt["mcp_server_started"] is False
    assert receipt["mcp_tool_called"] is False
    assert receipt["mcp_resource_mutated"] is False
    assert receipt["network_called"] is False
    assert receipt["persistence_mode"] == "none"


def test_sandbox_update_cieu_residual_and_learning_preview() -> None:
    cieu = load_json("sandbox_update_cieu_residual/sandbox_update_cieu_event_fixture.json")
    for field in ["X_t", "U_t", "Y_star_t", "Y_t_plus_1", "R_t_plus_1"]:
        assert field in cieu
    assert cieu["persistence_enabled"] is False
    assert cieu["db_write_performed"] is False
    residual = load_json("sandbox_update_cieu_residual/sandbox_update_residual_delta.json")
    classes = residual["residual_classes"]
    for field in [
        "sandbox_patch_application_residual",
        "y_star_lineage_residual",
        "projection_policy_delta_residual",
        "mcp_non_bypass_residual",
        "post_update_validation_residual",
        "rollback_residual",
        "evidence_gap_residual",
        "live_blocker_residual",
        "real_application_blocker_residual",
    ]:
        assert field in classes
    learning = load_json("sandbox_update_cieu_residual/sandbox_update_learning_candidate_preview.json")
    assert learning["review_only_preview"] is True
    assert learning["approved"] is False
    assert learning["applied"] is False
    assert learning["eligible_for_direct_brain_writeback"] is False
    assert learning["eligible_for_direct_memory_ingestion"] is False


def test_sandbox_rollback_and_comparison_keep_real_state_unchanged() -> None:
    rollback = load_json("sandbox_rollback_validation/sandbox_rollback_result.json")
    assert rollback["rollback_performed_in_sandbox"] is True
    assert rollback["real_canonical_policy_modified"] is False
    assert rollback["brain_modified"] is False
    assert rollback["memory_modified"] is False
    assert rollback["strategy_modified"] is False
    assert rollback["y_star_direct_mutation_performed"] is False
    assert rollback["rollback_restored_baseline"] is True
    validation = load_json("sandbox_rollback_validation/sandbox_post_rollback_validation_result.json")
    for field in [
        "baseline_restored",
        "sandbox_patch_removed_or_neutralized",
        "mission_y_star_lineage_preserved",
        "behavior_y_star_projection_lineage_preserved",
        "no_real_canonical_change",
        "no_brain_memory_change",
        "no_y_star_direct_mutation",
        "no_mcp_execution",
        "no_live_execution",
    ]:
        assert validation[field] is True
    comparison = load_json(
        "original_sandbox_rollback_comparison/original_vs_sandbox_vs_rollback_comparison.json"
    )
    assert comparison["real_canonical_system_changed"] is False
    assert comparison["brain_memory_changed"] is False
    assert comparison["gov_repos_changed"] is False
    effect = load_json("original_sandbox_rollback_comparison/sandbox_update_effect_summary.json")
    assert effect["effect_class"] in {
        "no_visible_sandbox_effect",
        "documentation_only_sandbox_effect",
        "projection_policy_sandbox_effect",
        "behavior_y_star_projection_sandbox_effect",
        "pre_u_mapping_sandbox_effect",
        "mcp_boundary_sandbox_effect",
        "residual_classification_sandbox_effect",
    }


def test_readiness_marks_l5_9_ready_and_l6_blocked() -> None:
    readiness = load_json("approved_sandbox_update_readiness/approved_sandbox_update_readiness.json")
    for field in [
        "sandbox_approval_fixture_generated",
        "sandbox_canonical_baseline_generated",
        "sandbox_patch_applied",
        "real_canonical_state_unchanged",
        "y_star_non_mutation_invariant_preserved",
        "sandbox_post_update_validation_passed",
        "sandbox_reprojection_generated",
        "sandbox_mcp_preview_generated",
        "sandbox_update_cieu_fixture_generated",
        "sandbox_rollback_performed",
        "rollback_restored_or_gap_recorded",
        "original_sandbox_rollback_comparison_generated",
        "real_approval_still_blocked",
        "real_canonical_application_still_blocked",
        "brain_writeback_still_blocked",
        "memory_ingestion_still_blocked",
        "y_star_direct_mutation_still_blocked",
        "y_star_gov_unmodified",
        "gov_mcp_unmodified",
        "ready_for_l5_9_real_approval_workflow_boundary",
    ]:
        assert readiness[field] is True
    assert readiness["ready_for_l6_revenue_opportunity_discovery"] is False


def test_console_read_model_command_passes() -> None:
    build = run_command(["python3", "console_read_model/loader/build_team_console_snapshot.py"])
    assert build.returncode == 0, build.stdout + build.stderr
    result = run_command(["python3", "console_read_model/cli/team_console.py", "approved-sandbox-update"])
    assert result.returncode == 0, result.stdout + result.stderr
    assert "L5.8 approved canonical update sandbox defined: True" in result.stdout
    assert "ready for L6 revenue opportunity discovery: False" in result.stdout
