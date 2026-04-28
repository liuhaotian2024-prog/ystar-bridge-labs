from __future__ import annotations

import json
import subprocess
from pathlib import Path
from typing import Any

import pytest


ROOT = Path(__file__).resolve().parents[2]
BUILDER = (
    ROOT
    / "projection_checked_autonomous_work_cycle"
    / "tools"
    / "build_projection_checked_autonomous_work_cycle.py"
)

REQUIRED_FILES = [
    "projection_checked_autonomous_work_cycle/README.md",
    "projection_checked_autonomous_work_cycle/tools/build_projection_checked_autonomous_work_cycle.py",
    "projection_checked_autonomous_work_cycle/projection_checked_cycle_contract.json",
    "projection_checked_autonomous_work_cycle/projection_checked_cycle_input_fixture.json",
    "projection_checked_autonomous_work_cycle/projection_checked_cycle_run.json",
    "projection_checked_autonomous_work_cycle/projection_checked_cycle_summary.json",
    "projection_checked_autonomous_work_cycle/projection_checked_cycle_report.md",
    "projection_checked_work_proposal/projection_checked_work_intent.json",
    "projection_checked_work_proposal/autonomous_work_proposal_candidate.json",
    "projection_checked_work_proposal/work_proposal_to_behavior_y_star_alignment.json",
    "projection_checked_work_proposal/work_proposal_projection_gate_decision.json",
    "projection_checked_work_proposal/projection_checked_work_proposal_summary.json",
    "projection_checked_work_proposal/projection_checked_work_proposal_report.md",
    "behavior_projection_pre_u_cycle_gate/cycle_pre_u_packet_candidate.json",
    "behavior_projection_pre_u_cycle_gate/cycle_pre_u_mapping_from_behavior_y_star.json",
    "behavior_projection_pre_u_cycle_gate/cycle_pre_u_gate_decision.json",
    "behavior_projection_pre_u_cycle_gate/cycle_pre_u_gap_report.md",
    "behavior_projection_pre_u_cycle_gate/cycle_pre_u_gate_summary.json",
    "projection_checked_dry_run_work_result/dry_run_work_execution_plan.json",
    "projection_checked_dry_run_work_result/dry_run_work_result.json",
    "projection_checked_dry_run_work_result/dry_run_work_receipt.json",
    "projection_checked_dry_run_work_result/dry_run_work_result_summary.json",
    "projection_checked_dry_run_work_result/dry_run_work_result_report.md",
    "projection_checked_cieu_residual_cycle/projection_checked_cieu_event_fixture.json",
    "projection_checked_cieu_residual_cycle/projection_checked_predicted_outcome.json",
    "projection_checked_cieu_residual_cycle/projection_checked_mock_actual_outcome.json",
    "projection_checked_cieu_residual_cycle/projection_checked_residual_delta.json",
    "projection_checked_cieu_residual_cycle/projection_checked_residual_summary.json",
    "projection_checked_cieu_residual_cycle/projection_checked_residual_report.md",
    "projection_checked_learning_review_queue/projection_checked_learning_candidate.json",
    "projection_checked_learning_review_queue/projection_checked_review_queue_entry.json",
    "projection_checked_learning_review_queue/projection_learning_policy_update_candidate_stub.json",
    "projection_checked_learning_review_queue/projection_learning_review_summary.json",
    "projection_checked_learning_review_queue/projection_learning_review_report.md",
    "projection_checked_cycle_readiness/projection_checked_cycle_readiness.json",
    "projection_checked_cycle_readiness/projection_checked_cycle_readiness.md",
    "projection_checked_cycle_readiness/l5_4_recommended_next_step.json",
]

JSON_FILES = [path for path in REQUIRED_FILES if path.endswith(".json")]

REQUIRED_STAGES = [
    "load_mission_y_star",
    "load_behavior_y_star_candidate",
    "load_projection_trace",
    "derive_projection_checked_work_intent",
    "generate_or_select_autonomous_work_proposal",
    "check_work_proposal_against_behavior_y_star",
    "generate_pre_u_packet_candidate",
    "run_dry_run_governance_decision",
    "produce_dry_run_work_result",
    "emit_cieu_like_cycle_event",
    "compute_projection_cycle_residual_delta",
    "create_review_queue_learning_candidate",
    "produce_next_cycle_recommendation",
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
    "semantic_truth_scoring_enabled",
    "raw_runtime_artifact_reading_enabled",
    "revenue_opportunity_discovery_enabled",
    "live_execution_authorized",
    "behavior_execution_authorized",
    "external_action_authorized",
    "production_ready",
    "real_execution_performed",
    "live_tool_called",
    "external_action_performed",
    "network_called",
    "db_log_runtime_content_read",
    "persistence_enabled",
    "db_write_performed",
    "eligible_for_direct_brain_writeback",
    "eligible_for_direct_memory_ingestion",
    "eligible_for_candidate_auto_approval",
    "approved",
    "applied",
    "live_learning_enabled",
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
def generated_projection_checked_cycle() -> None:
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


def test_required_l5_3_directories_files_and_json_parse() -> None:
    for directory in [
        "projection_checked_autonomous_work_cycle",
        "projection_checked_work_proposal",
        "behavior_projection_pre_u_cycle_gate",
        "projection_checked_dry_run_work_result",
        "projection_checked_cieu_residual_cycle",
        "projection_checked_learning_review_queue",
        "projection_checked_cycle_readiness",
    ]:
        assert (ROOT / directory).is_dir()
    for relative_path in REQUIRED_FILES:
        assert (ROOT / relative_path).exists(), f"missing file: {relative_path}"
    for relative_path in JSON_FILES:
        load_json(relative_path)


def test_cycle_contract_has_required_stages_and_false_safety_flags() -> None:
    contract = load_json(
        "projection_checked_autonomous_work_cycle/projection_checked_cycle_contract.json"
    )
    assert contract["cycle_stages"] == REQUIRED_STAGES
    for field in [
        "required_inputs",
        "required_outputs",
        "projection_gate_requirements",
        "work_cycle_requirements",
        "residual_loop_requirements",
        "learning_queue_requirements",
        "safety_flags",
        "forbidden_operations",
        "non_goals",
    ]:
        assert field in contract
    for value in contract["safety_flags"].values():
        assert value is False


def test_input_fixture_references_l5_2_behavior_y_star_and_projection_trace() -> None:
    fixture = load_json(
        "projection_checked_autonomous_work_cycle/projection_checked_cycle_input_fixture.json"
    )
    assert fixture["behavior_y_star_candidate_ref"] == (
        "mission_to_behavior_y_star_projection/behavior_level_y_star_candidate.json"
    )
    assert fixture["projection_trace_ref"] == (
        "mission_to_behavior_y_star_projection/mission_to_behavior_projection_trace.json"
    )
    assert fixture["behavior_pre_u_packet_candidate_ref"] == (
        "behavior_y_star_to_pre_u_candidate/pre_u_packet_candidate_from_behavior_y_star.json"
    )
    assert fixture["behavior_y_star_required_before_work_allowed"] is True


def test_work_intent_and_proposal_are_behavior_derived_and_dry_run_internal_only() -> None:
    behavior = load_json("mission_to_behavior_y_star_projection/behavior_level_y_star_candidate.json")
    intent = load_json("projection_checked_work_proposal/projection_checked_work_intent.json")
    proposal = load_json("projection_checked_work_proposal/autonomous_work_proposal_candidate.json")

    assert intent["source_behavior_y_star_id"] == behavior["behavior_y_star_id"]
    assert intent["required_behavior_y_star_alignment"] == behavior["declared_behavior_y_star"]
    assert proposal["source_behavior_y_star_id"] == behavior["behavior_y_star_id"]
    assert proposal["internal_only"] is True
    assert proposal["dry_run_only"] is True
    assert proposal["read_model_only"] is True
    assert proposal["live_execution_requested"] is False
    assert proposal["behavior_execution_requested"] is False
    assert proposal["external_action_requested"] is False
    assert proposal["network_requested"] is False
    assert proposal["db_or_runtime_content_requested"] is False
    assert proposal["revenue_opportunity_discovery_requested"] is False


def test_projection_gate_passes_only_for_dry_run_and_denies_live_behavior() -> None:
    alignment = load_json(
        "projection_checked_work_proposal/work_proposal_to_behavior_y_star_alignment.json"
    )
    gate = load_json(
        "projection_checked_work_proposal/work_proposal_projection_gate_decision.json"
    )

    assert alignment["decision"] in {
        "projection_gate_passed_for_dry_run",
        "projection_gate_requires_revision",
        "projection_gate_blocked",
    }
    assert alignment["decision"] == "projection_gate_passed_for_dry_run"
    assert gate["decision"] == "projection_gate_passed_for_dry_run"
    assert gate["dry_run_only"] is True
    assert gate["live_execution_authorized"] is False
    assert gate["behavior_execution_authorized"] is False


def test_cycle_pre_u_packet_maps_behavior_y_star_and_work_intent() -> None:
    behavior = load_json("mission_to_behavior_y_star_projection/behavior_level_y_star_candidate.json")
    intent = load_json("projection_checked_work_proposal/projection_checked_work_intent.json")
    packet = load_json("behavior_projection_pre_u_cycle_gate/cycle_pre_u_packet_candidate.json")
    decision = load_json("behavior_projection_pre_u_cycle_gate/cycle_pre_u_gate_decision.json")

    assert packet["declared_Y_star"] == behavior["declared_behavior_y_star"]
    assert packet["candidate_U"]["work_intent"] == intent["declared_work_intent"]
    assert packet["dry_run_only"] is True
    assert packet["production_ready"] is False
    assert packet["requires_y_star_gov_validation_before_execution"] is True
    assert packet["live_execution_authorized"] is False
    assert packet["behavior_execution_authorized"] is False
    assert packet["external_action_authorized"] is False
    assert decision["decision"] == "allow_dry_run_only"
    assert decision["dry_run_only"] is True
    assert decision["live_execution_authorized"] is False
    assert decision["behavior_execution_authorized"] is False


def test_dry_run_work_result_and_receipt_confirm_no_execution_or_runtime_reads() -> None:
    result = load_json("projection_checked_dry_run_work_result/dry_run_work_result.json")
    receipt = load_json("projection_checked_dry_run_work_result/dry_run_work_receipt.json")

    assert result["execution_mode"] == "dry_run_static_fixture"
    assert result["real_execution_performed"] is False
    assert result["live_tool_called"] is False
    assert result["external_action_performed"] is False
    assert result["network_called"] is False
    assert result["db_log_runtime_content_read"] is False
    assert receipt["no_live_behavior_execution"] is True
    assert receipt["no_external_action"] is True
    assert receipt["no_network"] is True
    assert receipt["no_scheduler_or_daemon"] is True
    assert receipt["no_cieu_persistence"] is True
    assert receipt["no_brain_writeback"] is True
    assert receipt["no_memory_ingestion"] is True
    assert receipt["no_candidate_approval"] is True


def test_cieu_like_event_and_residual_delta_are_dry_run_structural() -> None:
    event = load_json("projection_checked_cieu_residual_cycle/projection_checked_cieu_event_fixture.json")
    residual = load_json("projection_checked_cieu_residual_cycle/projection_checked_residual_delta.json")

    for field in ["X_t", "U_t", "Y_star_t", "Y_t_plus_1", "R_t_plus_1"]:
        assert field in event
    assert event["event_mode"] == "dry_run_fixture"
    assert event["persistence_enabled"] is False
    assert event["db_write_performed"] is False
    for field in [
        "projection_alignment_residual",
        "pre_u_gate_residual",
        "dry_run_execution_residual",
        "behavior_boundary_residual",
        "evidence_gap_residual",
        "learning_queue_residual",
        "live_blocker_residual",
        "writeback_blocker_residual",
    ]:
        assert field in residual
    assert residual["semantic_truth_scoring_used"] is False
    assert residual["real_behavior_executed"] is False


def test_learning_candidate_is_review_queue_only_and_not_approved_or_applied() -> None:
    candidate = load_json(
        "projection_checked_learning_review_queue/projection_checked_learning_candidate.json"
    )
    assert candidate["eligible_for_review_queue"] is True
    assert candidate["eligible_for_direct_brain_writeback"] is False
    assert candidate["eligible_for_direct_memory_ingestion"] is False
    assert candidate["eligible_for_candidate_auto_approval"] is False
    assert candidate["requires_human_or_governance_review"] is True
    assert candidate["approved"] is False
    assert candidate["applied"] is False
    assert candidate["live_learning_enabled"] is False


def test_readiness_marks_blocked_safety_and_l5_4_readiness() -> None:
    readiness = load_json("projection_checked_cycle_readiness/projection_checked_cycle_readiness.json")

    assert readiness["behavior_y_star_consumed_by_cycle"] is True
    assert readiness["work_proposal_checked_against_behavior_y_star"] is True
    assert readiness["pre_u_packet_candidate_generated"] is True
    assert readiness["dry_run_gate_decision_generated"] is True
    assert readiness["dry_run_result_generated"] is True
    assert readiness["cieu_like_event_fixture_generated"] is True
    assert readiness["residual_delta_generated"] is True
    assert readiness["learning_review_candidate_generated"] is True
    assert readiness["learning_review_candidate_approved"] is False
    assert readiness["live_execution_still_blocked"] is True
    assert readiness["writeback_still_blocked"] is True
    assert readiness["external_action_still_blocked"] is True
    assert readiness["ready_for_l5_4_review_gated_learning_loop"] is True
    assert readiness["next_required_milestone"] == "L5.4 Review-Gated Learning Loop v0"


def test_no_live_external_network_scheduler_daemon_writeback_or_runtime_flags_enabled() -> None:
    for relative_path in JSON_FILES:
        payload = load_json(relative_path)
        for node in walk_json(payload):
            for field in FALSE_FLAG_FIELDS:
                if field in node:
                    assert node[field] is False, f"{relative_path}: {field} must be false"


def test_console_read_model_integration_passes() -> None:
    loader = run_command(["python3", "console_read_model/loader/build_team_console_snapshot.py"])
    assert loader.returncode == 0, loader.stdout + loader.stderr

    summary = load_json("console_read_model/generated/projection_cycle_summary.json")
    assert summary["projection_checked_autonomous_work_cycle_defined"] is True
    assert summary["behavior_y_star_consumed_by_cycle"] is True
    assert summary["behavior_execution_enabled"] is False
    assert summary["ready_for_l5_4_review_gated_learning_loop"] is True

    cli = run_command(["python3", "console_read_model/cli/team_console.py", "projection-cycle"])
    assert cli.returncode == 0, cli.stdout + cli.stderr
    assert "Projection-Checked Autonomous Work Cycle" in cli.stdout

    validator = run_command(["python3", "console_read_model/validation/validate_team_read_model.py"])
    assert validator.returncode == 0, validator.stdout + validator.stderr


def test_builder_source_is_static_and_non_runtime() -> None:
    source = BUILDER.read_text(encoding="utf-8")
    assert "shell=True" not in source
    assert "import sqlite3" not in source
    assert "subprocess.run" not in source
    assert "requests." not in source
    assert "urllib.request" not in source
    assert ".db-wal" not in source
    assert ".db-shm" not in source
    assert ".sqlite3" not in source
    assert "scripts/.logs" not in source
