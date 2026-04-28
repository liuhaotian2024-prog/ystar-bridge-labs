from __future__ import annotations

import json
import subprocess
from pathlib import Path
from typing import Any

import pytest


ROOT = Path(__file__).resolve().parents[2]
BUILDER = (
    ROOT
    / "review_gated_shadow_learning_cycle"
    / "tools"
    / "build_review_gated_shadow_learning_cycle.py"
)

REQUIRED_DIRECTORIES = [
    "review_gated_shadow_learning_cycle",
    "residual_review_gate",
    "learning_target_classifier",
    "projection_policy_update_candidate",
    "shadow_projection_policy_patch",
    "shadow_reprojection_preview",
    "shadow_updated_projection_cycle",
    "shadow_cycle_cieu_residual",
    "original_vs_shadow_cycle_comparison",
    "integrated_learning_cycle_cieu_fixture",
    "integrated_shadow_learning_readiness",
]

REQUIRED_FILES = [
    "review_gated_shadow_learning_cycle/README.md",
    "review_gated_shadow_learning_cycle/tools/build_review_gated_shadow_learning_cycle.py",
    "review_gated_shadow_learning_cycle/review_gated_shadow_learning_contract.json",
    "review_gated_shadow_learning_cycle/review_gated_shadow_learning_input_fixture.json",
    "review_gated_shadow_learning_cycle/review_gated_shadow_learning_run.json",
    "review_gated_shadow_learning_cycle/review_gated_shadow_learning_summary.json",
    "review_gated_shadow_learning_cycle/review_gated_shadow_learning_report.md",
    "residual_review_gate/normalized_projection_residual.json",
    "residual_review_gate/residual_review_policy.json",
    "residual_review_gate/residual_review_gate_decision.json",
    "residual_review_gate/residual_review_decision_packet.json",
    "residual_review_gate/residual_review_summary.json",
    "residual_review_gate/residual_review_report.md",
    "learning_target_classifier/learning_target_classification.json",
    "learning_target_classifier/learning_scope_matrix.json",
    "learning_target_classifier/learning_target_trace.json",
    "learning_target_classifier/learning_target_summary.json",
    "learning_target_classifier/learning_target_report.md",
    "projection_policy_update_candidate/projection_policy_update_candidate.json",
    "projection_policy_update_candidate/behavior_y_star_generation_update_candidate.json",
    "projection_policy_update_candidate/pre_u_mapping_update_candidate.json",
    "projection_policy_update_candidate/work_alignment_update_candidate.json",
    "projection_policy_update_candidate/residual_classification_update_candidate.json",
    "projection_policy_update_candidate/evidence_collection_update_candidate.json",
    "projection_policy_update_candidate/projection_policy_update_summary.json",
    "projection_policy_update_candidate/projection_policy_update_report.md",
    "shadow_projection_policy_patch/shadow_projection_policy_patch.json",
    "shadow_projection_policy_patch/shadow_patch_application_plan.json",
    "shadow_projection_policy_patch/shadow_patch_denied_operations.json",
    "shadow_projection_policy_patch/shadow_patch_summary.json",
    "shadow_projection_policy_patch/shadow_patch_report.md",
    "shadow_reprojection_preview/next_cycle_projection_input_candidate.json",
    "shadow_reprojection_preview/shadow_reprojected_behavior_y_star_preview.json",
    "shadow_reprojection_preview/original_vs_shadow_behavior_y_star_comparison.json",
    "shadow_reprojection_preview/shadow_reprojection_gap_map.json",
    "shadow_reprojection_preview/shadow_reprojection_summary.json",
    "shadow_reprojection_preview/shadow_reprojection_report.md",
    "shadow_updated_projection_cycle/shadow_cycle_contract.json",
    "shadow_updated_projection_cycle/shadow_cycle_input_fixture.json",
    "shadow_updated_projection_cycle/shadow_projection_checked_work_intent.json",
    "shadow_updated_projection_cycle/shadow_autonomous_work_proposal_candidate.json",
    "shadow_updated_projection_cycle/shadow_work_proposal_to_behavior_y_star_alignment.json",
    "shadow_updated_projection_cycle/shadow_work_proposal_gate_decision.json",
    "shadow_updated_projection_cycle/shadow_cycle_pre_u_packet_candidate.json",
    "shadow_updated_projection_cycle/shadow_cycle_pre_u_gate_decision.json",
    "shadow_updated_projection_cycle/shadow_dry_run_work_result.json",
    "shadow_updated_projection_cycle/shadow_dry_run_work_receipt.json",
    "shadow_updated_projection_cycle/shadow_updated_projection_cycle_run.json",
    "shadow_updated_projection_cycle/shadow_updated_projection_cycle_summary.json",
    "shadow_updated_projection_cycle/shadow_updated_projection_cycle_report.md",
    "shadow_cycle_cieu_residual/shadow_cycle_cieu_event_fixture.json",
    "shadow_cycle_cieu_residual/shadow_cycle_predicted_outcome.json",
    "shadow_cycle_cieu_residual/shadow_cycle_mock_actual_outcome.json",
    "shadow_cycle_cieu_residual/shadow_cycle_residual_delta.json",
    "shadow_cycle_cieu_residual/shadow_cycle_residual_summary.json",
    "shadow_cycle_cieu_residual/shadow_cycle_residual_report.md",
    "original_vs_shadow_cycle_comparison/original_vs_shadow_cycle_comparison.json",
    "original_vs_shadow_cycle_comparison/original_vs_shadow_cycle_delta.json",
    "original_vs_shadow_cycle_comparison/shadow_learning_effect_summary.json",
    "original_vs_shadow_cycle_comparison/original_vs_shadow_cycle_report.md",
    "integrated_learning_cycle_cieu_fixture/integrated_learning_cycle_cieu_event_fixture.json",
    "integrated_learning_cycle_cieu_fixture/integrated_learning_cycle_predicted_outcome.json",
    "integrated_learning_cycle_cieu_fixture/integrated_learning_cycle_mock_actual_outcome.json",
    "integrated_learning_cycle_cieu_fixture/integrated_learning_cycle_residual_delta.json",
    "integrated_learning_cycle_cieu_fixture/integrated_learning_cycle_cieu_summary.json",
    "integrated_learning_cycle_cieu_fixture/integrated_learning_cycle_cieu_report.md",
    "integrated_shadow_learning_readiness/integrated_shadow_learning_readiness.json",
    "integrated_shadow_learning_readiness/integrated_shadow_learning_readiness.md",
    "integrated_shadow_learning_readiness/l5_5_or_l6_recommended_next_step.json",
]

JSON_FILES = [path for path in REQUIRED_FILES if path.endswith(".json")]

REQUIRED_LOOP_STAGES = [
    "load_l5_3_projection_checked_residual_delta",
    "load_l5_3_learning_candidate",
    "normalize_residual_for_review",
    "classify_learning_target",
    "run_deterministic_review_gate",
    "produce_review_decision_packet",
    "generate_projection_policy_update_candidate",
    "generate_shadow_projection_policy_patch",
    "generate_next_cycle_projection_input_candidate",
    "generate_shadow_behavior_y_star_preview",
    "run_shadow_updated_projection_checked_cycle",
    "generate_shadow_cycle_cieu_like_fixture",
    "compute_shadow_cycle_residual_delta",
    "compare_original_vs_shadow_behavior_y_star",
    "compare_original_vs_shadow_cycle",
    "emit_integrated_learning_cycle_cieu_like_fixture",
    "produce_final_l5_4_readiness",
]

FALSE_FLAG_FIELDS = {
    "live_execution_enabled",
    "behavior_execution_enabled",
    "external_action_enabled",
    "network_enabled",
    "scheduler_enabled",
    "daemon_enabled",
    "cieu_persistence_enabled",
    "brain_writeback_enabled",
    "memory_ingestion_enabled",
    "candidate_auto_approval_enabled",
    "canonical_policy_mutation_enabled",
    "semantic_truth_scoring_enabled",
    "raw_runtime_artifact_reading_enabled",
    "revenue_opportunity_discovery_enabled",
    "shadow_patch_live_application_enabled",
    "approved_for_live_application",
    "approved_for_brain_writeback",
    "approved_for_memory_ingestion",
    "approved_for_canonical_policy_mutation",
    "can_apply_to_canonical_policy_now",
    "can_write_to_brain_now",
    "can_write_to_memory_now",
    "applied_to_canonical_policy",
    "applied_to_brain",
    "applied_to_memory",
    "canonical_policy_mutation",
    "brain_writeback",
    "memory_ingestion",
    "live_application",
    "live_behavior_authorized",
    "behavior_execution_enabled",
    "real_execution_performed",
    "live_tool_called",
    "external_action_performed",
    "network_called",
    "db_log_runtime_content_read",
    "canonical_policy_mutated",
    "brain_writeback_performed",
    "memory_ingestion_performed",
    "live_execution_authorized",
    "behavior_execution_authorized",
    "external_action_authorized",
    "production_ready",
    "persistence_enabled",
    "db_write_performed",
    "canonical_system_changed",
    "brain_memory_changed",
    "eligible_for_direct_brain_writeback",
    "eligible_for_direct_memory_ingestion",
    "eligible_for_candidate_auto_approval",
    "approved",
    "applied",
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
def generated_shadow_learning_cycle() -> None:
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


def assert_safety_flags_false(document: Any) -> None:
    for node in walk_json(document):
        for field in FALSE_FLAG_FIELDS:
            if field in node:
                assert node[field] is False, f"{field} must remain false"


def test_required_l5_4_directories_files_and_json_parse() -> None:
    for directory in REQUIRED_DIRECTORIES:
        assert (ROOT / directory).is_dir()
    for relative_path in REQUIRED_FILES:
        assert (ROOT / relative_path).exists(), f"missing file: {relative_path}"
    for relative_path in JSON_FILES:
        load_json(relative_path)


def test_contract_contains_required_loop_stages_and_false_safety_flags() -> None:
    contract = load_json("review_gated_shadow_learning_cycle/review_gated_shadow_learning_contract.json")
    assert contract["loop_stages"] == REQUIRED_LOOP_STAGES
    for field in [
        "review_gate_requirements",
        "learning_scope_requirements",
        "shadow_update_requirements",
        "shadow_cycle_requirements",
        "comparison_requirements",
        "safety_flags",
        "forbidden_operations",
        "non_goals",
    ]:
        assert field in contract
    assert all(value is False for value in contract["safety_flags"].values())


def test_input_fixture_references_l5_3_and_l5_2_artifacts() -> None:
    fixture = load_json(
        "review_gated_shadow_learning_cycle/review_gated_shadow_learning_input_fixture.json"
    )
    assert fixture["l5_3_projection_checked_residual_delta_ref"] == (
        "projection_checked_cieu_residual_cycle/projection_checked_residual_delta.json"
    )
    assert fixture["l5_3_learning_candidate_ref"] == (
        "projection_checked_learning_review_queue/projection_checked_learning_candidate.json"
    )
    assert fixture["l5_3_review_queue_entry_ref"] == (
        "projection_checked_learning_review_queue/projection_checked_review_queue_entry.json"
    )
    assert fixture["l5_3_cycle_run_ref"] == (
        "projection_checked_autonomous_work_cycle/projection_checked_cycle_run.json"
    )
    assert fixture["behavior_y_star_ref"] == (
        "mission_to_behavior_y_star_projection/behavior_level_y_star_candidate.json"
    )
    assert fixture["projection_trace_ref"] == (
        "mission_to_behavior_y_star_projection/mission_to_behavior_projection_trace.json"
    )


def test_residual_review_gate_is_deterministic_and_shadow_only() -> None:
    normalized = load_json("residual_review_gate/normalized_projection_residual.json")
    decision = load_json("residual_review_gate/residual_review_gate_decision.json")
    packet = load_json("residual_review_gate/residual_review_decision_packet.json")

    assert normalized["source_residual_delta_id"] == "projection-checked-residual-delta-001"
    assert normalized["affected_y_star_layer"] == "behavior"
    assert decision["decision"] in {
        "eligible_for_shadow_update_candidate",
        "requires_revision_before_shadow_update",
        "blocked_from_learning",
        "context_only_no_learning",
    }
    assert decision["decision"] == "eligible_for_shadow_update_candidate"
    assert decision["eligible_for_shadow_update_candidate"] is True
    assert decision["eligible_for_shadow_cycle_preview"] is True
    assert decision["required_human_or_governance_review"] is True
    assert decision["approved_for_live_application"] is False
    assert decision["approved_for_brain_writeback"] is False
    assert decision["approved_for_memory_ingestion"] is False
    assert decision["approved_for_canonical_policy_mutation"] is False
    assert packet["approved"] is False
    assert packet["applied"] is False
    assert packet["canonical_policy_mutation_allowed"] is False


def test_learning_targets_and_scope_matrix_keep_learning_shadow_only() -> None:
    classification = load_json("learning_target_classifier/learning_target_classification.json")
    matrix = load_json("learning_target_classifier/learning_scope_matrix.json")
    expected_targets = {
        "projection_policy",
        "behavior_y_star_generation",
        "pre_u_mapping",
        "work_proposal_alignment",
        "residual_classification",
        "evidence_collection_policy",
        "live_blocker_tracking",
        "writeback_boundary_tracking",
    }
    actual_targets = {target["target_name"] for target in classification["targets"]}
    assert actual_targets == expected_targets
    for target in classification["targets"]:
        assert target["can_apply_to_canonical_policy_now"] is False
        assert target["can_write_to_brain_now"] is False
        assert target["can_write_to_memory_now"] is False
        assert target["requires_review_before_application"] is True
    for field in [
        "denied_live_learning",
        "denied_brain_writeback",
        "denied_memory_ingestion",
        "denied_candidate_auto_approval",
        "denied_external_action",
        "denied_revenue_discovery",
        "denied_canonical_policy_mutation",
    ]:
        assert matrix[field] is True


def test_update_candidates_are_not_approved_or_applied() -> None:
    for relative_path in [
        "projection_policy_update_candidate/projection_policy_update_candidate.json",
        "projection_policy_update_candidate/behavior_y_star_generation_update_candidate.json",
        "projection_policy_update_candidate/pre_u_mapping_update_candidate.json",
        "projection_policy_update_candidate/work_alignment_update_candidate.json",
        "projection_policy_update_candidate/residual_classification_update_candidate.json",
        "projection_policy_update_candidate/evidence_collection_update_candidate.json",
    ]:
        candidate = load_json(relative_path)
        assert candidate["approval_status"] == "not_approved"
        assert candidate["applied_to_canonical_policy"] is False
        assert candidate["applied_to_brain"] is False
        assert candidate["applied_to_memory"] is False
        assert candidate["requires_human_or_governance_review_before_application"] is True


def test_shadow_patch_is_preview_only_and_denies_canonical_mutation() -> None:
    patch = load_json("shadow_projection_policy_patch/shadow_projection_policy_patch.json")
    denied = load_json("shadow_projection_policy_patch/shadow_patch_denied_operations.json")
    denied_ops = set(denied["denied_operations"])

    assert patch["preview_only"] is True
    assert patch["canonical_policy_mutation"] is False
    assert patch["brain_writeback"] is False
    assert patch["memory_ingestion"] is False
    assert patch["live_application"] is False
    for expected in [
        "modifying canonical projection operator policy",
        "modifying brain",
        "modifying memory",
        "modifying Y-star-gov",
        "writing CIEU DB",
        "enabling live behavior execution",
        "enabling network/external action",
        "approving candidates",
    ]:
        assert expected in denied_ops


def test_shadow_reprojection_preview_preserves_boundaries_and_blocks_application() -> None:
    candidate = load_json("shadow_reprojection_preview/next_cycle_projection_input_candidate.json")
    preview = load_json("shadow_reprojection_preview/shadow_reprojected_behavior_y_star_preview.json")
    comparison = load_json(
        "shadow_reprojection_preview/original_vs_shadow_behavior_y_star_comparison.json"
    )

    assert candidate["original_behavior_y_star_ref"] == (
        "mission_to_behavior_y_star_projection/behavior_level_y_star_candidate.json"
    )
    assert preview["pre_u_validation_still_required"] is True
    assert preview["live_behavior_authorized"] is False
    assert preview["behavior_execution_enabled"] is False
    assert preview["applied_to_canonical_policy"] is False
    assert preview["applied_to_brain"] is False
    assert preview["applied_to_memory"] is False
    assert comparison["inherited_obligations_preserved"] is True
    assert comparison["safety_boundaries_preserved"] is True
    assert comparison["acceptable_for_shadow_cycle_dry_run_consumption"] is True


def test_shadow_updated_cycle_is_dry_run_only_and_consumes_shadow_behavior_y_star() -> None:
    contract = load_json("shadow_updated_projection_cycle/shadow_cycle_contract.json")
    intent = load_json("shadow_updated_projection_cycle/shadow_projection_checked_work_intent.json")
    proposal = load_json("shadow_updated_projection_cycle/shadow_autonomous_work_proposal_candidate.json")
    alignment = load_json(
        "shadow_updated_projection_cycle/shadow_work_proposal_to_behavior_y_star_alignment.json"
    )
    gate = load_json("shadow_updated_projection_cycle/shadow_work_proposal_gate_decision.json")

    assert contract["shadow_cycle_only"] is True
    assert contract["canonical_policy_mutation"] is False
    assert contract["real_execution_performed"] is False
    assert intent["source_shadow_behavior_y_star_preview_id"] == "shadow-behavior-y-star-preview-001"
    assert proposal["internal_only"] is True
    assert proposal["dry_run_only"] is True
    assert proposal["revenue_opportunity_discovery_requested"] is False
    assert alignment["decision"] == "shadow_projection_gate_passed_for_dry_run"
    assert gate["dry_run_only"] is True
    assert gate["live_execution_authorized"] is False
    assert gate["behavior_execution_authorized"] is False


def test_shadow_pre_u_packet_and_gate_remain_non_production() -> None:
    packet = load_json("shadow_updated_projection_cycle/shadow_cycle_pre_u_packet_candidate.json")
    decision = load_json("shadow_updated_projection_cycle/shadow_cycle_pre_u_gate_decision.json")

    assert packet["declared_Y_star"] == (
        "Prepare a projection-checked autonomous work-cycle candidate for future Pre-U validation. "
        "Shadow preview adds explicit residual-review obligations, no-execution residual labeling, "
        "and evidence sufficiency checks before any future canonical learning design."
    )
    assert packet["candidate_U"]["shadow_work_intent"] == (
        "refresh mission dashboard using shadow-updated behavior-level Y* context"
    )
    assert packet["dry_run_only"] is True
    assert packet["production_ready"] is False
    assert packet["requires_y_star_gov_validation_before_execution"] is True
    assert packet["live_execution_authorized"] is False
    assert packet["behavior_execution_authorized"] is False
    assert packet["external_action_authorized"] is False
    assert decision["decision"] == "allow_shadow_dry_run_only"
    assert decision["dry_run_only"] is True


def test_shadow_dry_run_result_and_receipt_confirm_no_effects() -> None:
    result = load_json("shadow_updated_projection_cycle/shadow_dry_run_work_result.json")
    receipt = load_json("shadow_updated_projection_cycle/shadow_dry_run_work_receipt.json")

    assert result["execution_mode"] == "shadow_dry_run_static_fixture"
    assert result["real_execution_performed"] is False
    assert result["live_tool_called"] is False
    assert result["external_action_performed"] is False
    assert result["network_called"] is False
    assert result["db_log_runtime_content_read"] is False
    assert result["canonical_policy_mutated"] is False
    assert result["brain_writeback_performed"] is False
    assert result["memory_ingestion_performed"] is False
    for field in [
        "no_live_behavior_execution",
        "no_external_action",
        "no_network",
        "no_scheduler_or_daemon",
        "no_cieu_persistence",
        "no_canonical_policy_mutation",
        "no_brain_writeback",
        "no_memory_ingestion",
        "no_candidate_approval",
    ]:
        assert receipt[field] is True


def test_shadow_cieu_fixture_and_residual_are_structural_only() -> None:
    event = load_json("shadow_cycle_cieu_residual/shadow_cycle_cieu_event_fixture.json")
    residual = load_json("shadow_cycle_cieu_residual/shadow_cycle_residual_delta.json")

    for field in ["X_t", "U_t", "Y_star_t", "Y_t_plus_1", "R_t_plus_1"]:
        assert field in event
    assert event["event_mode"] == "shadow_dry_run_fixture"
    assert event["persistence_enabled"] is False
    assert event["db_write_performed"] is False
    for field in [
        "shadow_projection_alignment_residual",
        "shadow_pre_u_gate_residual",
        "shadow_dry_run_execution_residual",
        "behavior_boundary_residual",
        "evidence_gap_residual",
        "learning_queue_residual",
        "live_blocker_residual",
        "writeback_blocker_residual",
        "canonical_policy_mutation_blocker_residual",
    ]:
        assert field in residual
    assert residual["semantic_truth_scoring_used"] is False


def test_original_vs_shadow_comparison_records_shadow_only_learning_effect() -> None:
    comparison = load_json("original_vs_shadow_cycle_comparison/original_vs_shadow_cycle_comparison.json")
    effect = load_json("original_vs_shadow_cycle_comparison/shadow_learning_effect_summary.json")

    assert comparison["canonical_system_changed"] is False
    assert comparison["brain_memory_changed"] is False
    assert comparison["safety_boundaries_preserved"] is True
    assert comparison["learning_effect_observed_in_shadow_only"] is True
    assert effect["effect_class"] in {
        "no_visible_shadow_effect",
        "documentation_only_shadow_effect",
        "projection_policy_shadow_effect",
        "behavior_y_star_shadow_effect",
        "pre_u_mapping_shadow_effect",
        "work_alignment_shadow_effect",
        "residual_classification_shadow_effect",
    }


def test_integrated_cieu_fixture_and_readiness_keep_l6_blocked() -> None:
    event = load_json(
        "integrated_learning_cycle_cieu_fixture/integrated_learning_cycle_cieu_event_fixture.json"
    )
    readiness = load_json("integrated_shadow_learning_readiness/integrated_shadow_learning_readiness.json")

    for field in ["X_t", "U_t", "Y_star_t", "Y_t_plus_1", "R_t_plus_1"]:
        assert field in event
    assert event["event_mode"] == "integrated_review_gated_shadow_cycle_fixture"
    assert event["persistence_enabled"] is False
    assert event["db_write_performed"] is False
    assert readiness["l5_3_residual_consumed"] is True
    assert readiness["residual_normalized"] is True
    assert readiness["review_gate_decision_generated"] is True
    assert readiness["learning_target_classified"] is True
    assert readiness["shadow_behavior_y_star_preview_generated"] is True
    assert readiness["shadow_updated_projection_cycle_generated"] is True
    assert readiness["original_vs_shadow_cycle_comparison_generated"] is True
    assert readiness["previous_residual_influenced_shadow_projection"] is True
    assert readiness["ready_for_controlled_canonical_learning_design"] is True
    assert readiness["ready_for_l6_revenue_opportunity_discovery"] is False


def test_all_safety_flags_remain_false_in_generated_json() -> None:
    for relative_path in JSON_FILES:
        assert_safety_flags_false(load_json(relative_path))


def test_builder_static_safety_constraints() -> None:
    source = BUILDER.read_text(encoding="utf-8")
    assert "shell=True" not in source
    assert "subprocess.run" not in source
    assert "requests." not in source
    assert "urllib.request" not in source
    for forbidden in [".db-wal", ".db-shm", ".sqlite3", "scripts/.logs"]:
        assert forbidden not in source


def test_console_read_model_integration_passes() -> None:
    loader = run_command(["python3", "console_read_model/loader/build_team_console_snapshot.py"])
    assert loader.returncode == 0, loader.stdout + loader.stderr
    validator = run_command(["python3", "console_read_model/validation/validate_team_read_model.py"])
    assert validator.returncode == 0, validator.stdout + validator.stderr
    console = run_command(["python3", "console_read_model/cli/team_console.py", "shadow-learning-cycle"])
    assert console.returncode == 0, console.stdout + console.stderr
    assert "L5.4 integrated review-gated shadow learning cycle defined: True" in console.stdout
    assert "ready for controlled canonical learning design: True" in console.stdout
    assert "ready for L6 revenue opportunity discovery: False" in console.stdout
