from __future__ import annotations

import json
import subprocess
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
PACK = ROOT / "manual_recurring_observation_tick_runner"
GENERATED = PACK / "generated"
BUILDER = PACK / "tools" / "build_manual_tick_runner.py"
RUNNER = PACK / "tools" / "run_manual_observation_tick.py"

JSON_OUTPUTS = [
    "manual_tick_runner_contract.json",
    "manual_tick_request.json",
    "manual_tick_preflight.json",
    "manual_tick_source_validation.json",
    "manual_tick_governance_decision.json",
    "manual_tick_result.json",
    "manual_tick_dashboard_delta.json",
    "manual_tick_work_candidates.json",
    "manual_tick_cieu_event.json",
    "manual_tick_residual_delta.json",
    "manual_tick_run_receipt.json",
    "manual_tick_history_index.json",
    "manual_tick_next_recommendations.json",
    "manual_tick_runner_readiness_summary.json",
]


def run_script(*args: str) -> subprocess.CompletedProcess[str]:
    result = subprocess.run(
        ["python3", *args],
        cwd=ROOT,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        check=False,
    )
    assert result.returncode == 0, result.stdout + result.stderr
    return result


def run_builder() -> None:
    run_script(str(BUILDER.relative_to(ROOT)))


def load_json(name: str) -> dict:
    path = GENERATED / name
    assert path.exists(), f"missing generated file: {name}"
    return json.loads(path.read_text(encoding="utf-8"))


def assert_false_flags(payload: dict, fields: list[str]) -> None:
    for field in fields:
        assert payload[field] is False, f"{field} should remain false"


def test_generated_json_outputs_are_valid() -> None:
    run_builder()
    for name in JSON_OUTPUTS:
        load_json(name)


def test_contract_request_preflight_source_validation_and_governance() -> None:
    run_builder()

    contract = load_json("manual_tick_runner_contract.json")
    request = load_json("manual_tick_request.json")
    preflight = load_json("manual_tick_preflight.json")
    source_validation = load_json("manual_tick_source_validation.json")
    decision = load_json("manual_tick_governance_decision.json")

    assert contract["manual_tick_runner_id"] == "manual_recurring_observation_tick_runner_v0"
    assert contract["manual_trigger_required"] is True
    assert contract["one_tick_per_invocation"] is True
    assert contract["recurrence_enabled"] is False
    assert contract["scheduler_enabled"] is False
    assert contract["daemon_enabled"] is False
    assert contract["auto_run_enabled"] is False
    assert request["manual_trigger"] is True
    assert request["requested_tick_number"] == 1
    assert request["recurrence_requested"] is False
    assert request["scheduler_requested"] is False
    assert request["daemon_requested"] is False
    assert request["auto_run_requested"] is False
    assert preflight["preflight_decision"] == "allow_manual_local_tick"
    assert preflight["unsafe_request_detected"] is False
    assert source_validation["all_sources_safe"] is True
    assert source_validation["raw_runtime_artifacts_requested"] is False
    assert source_validation["db_or_log_sources_requested"] is False
    assert source_validation["network_sources_requested"] is False
    assert source_validation["credentials_required"] is False
    assert source_validation["validation_decision"] == "allow"
    assert decision["decision"] == "allow_manual_local_tick"
    assert decision["allowed_only_as_manual_local_readonly_tick"] is True
    assert decision["scheduler_enabled"] is False
    assert decision["daemon_enabled"] is False


def test_runner_can_run_one_manual_tick() -> None:
    run_builder()
    run_script(
        str(RUNNER.relative_to(ROOT)),
        "--request",
        "manual_recurring_observation_tick_runner/generated/manual_tick_request.json",
        "--output-dir",
        "manual_recurring_observation_tick_runner/generated",
    )

    result = load_json("manual_tick_result.json")
    dashboard_delta = load_json("manual_tick_dashboard_delta.json")
    work_candidates = load_json("manual_tick_work_candidates.json")

    assert result["status"] == "success"
    assert result["tick_number"] == 1
    assert result["manual_trigger"] is True
    assert result["one_tick_per_invocation"] is True
    assert result["recurrence_enabled"] is False
    assert result["scheduler_used"] is False
    assert result["daemon_used"] is False
    assert result["real_action_executed"] is False
    assert result["external_action_executed"] is False
    assert result["live_action_enabled"] is False
    assert dashboard_delta["state_change_level"] == "meaningful"
    assert dashboard_delta["requires_review"] is True
    assert work_candidates["candidate_count"] >= 3
    assert work_candidates["candidates"][0]["title"] == "L5.0 Review-Gated Learning Candidate Queue v0"
    for candidate in work_candidates["candidates"]:
        assert candidate["live_enabled"] is False
        assert candidate["external_action_enabled"] is False


def test_manual_tick_cieu_event_and_residual_delta_are_dry_run_only() -> None:
    run_builder()

    event = load_json("manual_tick_cieu_event.json")
    residual = load_json("manual_tick_residual_delta.json")

    assert event["dry_run_only"] is True
    assert event["persistence_enabled"] is False
    assert event["learning_eligibility"] is False
    assert event["curation_required"] is True
    assert event["direct_brain_writeback_allowed"] is False
    assert event["direct_memory_ingestion_allowed"] is False
    assert event["raw_artifact_ingestion_allowed"] is False
    assert residual["curation_required"] is True
    assert residual["learning_eligibility"] is False
    assert residual["direct_brain_writeback_allowed"] is False
    assert residual["direct_memory_ingestion_allowed"] is False
    assert residual["next_review_required"] is True


def test_receipt_history_recommendations_and_readiness() -> None:
    run_builder()

    receipt = load_json("manual_tick_run_receipt.json")
    history = load_json("manual_tick_history_index.json")
    recommendations = load_json("manual_tick_next_recommendations.json")
    summary = load_json("manual_tick_runner_readiness_summary.json")

    assert receipt["status"] == "success"
    assert receipt["manual_trigger"] is True
    assert receipt["scheduler_used"] is False
    assert receipt["daemon_used"] is False
    assert history["total_recorded_ticks"] == 1
    assert history["scheduler_enabled"] is False
    assert history["daemon_enabled"] is False
    assert history["recurrence_enabled"] is False
    assert recommendations["recommendation_count"] >= 3
    assert recommendations["recommendations"][0]["title"] == "L5.0 Review-Gated Learning Candidate Queue v0"
    assert summary["next_required_milestone"] == "L5.0 Review-Gated Learning Candidate Queue v0"
    assert summary["manual_recurring_observation_tick_runner_defined"] is True
    assert summary["manual_tick_runner_contract_defined"] is True
    assert summary["manual_tick_request_defined"] is True
    assert summary["manual_tick_preflight_defined"] is True
    assert summary["manual_tick_source_validation_defined"] is True
    assert summary["manual_tick_governance_decision_defined"] is True
    assert summary["manual_tick_result_defined"] is True
    assert summary["manual_tick_run_receipt_defined"] is True
    assert summary["manual_tick_history_index_defined"] is True
    assert summary["manual_trigger_required"] is True
    assert summary["one_tick_per_invocation"] is True
    assert summary["total_recorded_ticks"] == 1
    assert summary["step_by_step_human_prompting_required"] is False


def test_all_live_external_and_writeback_flags_remain_false() -> None:
    run_builder()

    summary = load_json("manual_tick_runner_readiness_summary.json")
    contract = load_json("manual_tick_runner_contract.json")

    disabled = [
        "recurrence_enabled",
        "scheduler_enabled",
        "daemon_enabled",
        "auto_run_enabled",
        "real_action_executed",
        "external_action_executed",
        "live_action_enabled",
        "network_enabled",
        "git_push_enabled",
        "daemon_control_enabled",
        "cieu_persistence_enabled",
        "brain_writeback_enabled",
        "memory_ingestion_enabled",
        "email_or_external_communication_enabled",
    ]
    assert_false_flags(summary, disabled)
    assert_false_flags(contract, disabled)


def test_builder_and_runner_sources_are_non_runtime() -> None:
    for path in [BUILDER, RUNNER]:
        source = path.read_text(encoding="utf-8")
        assert "shell=True" not in source
        assert "import sqlite3" not in source
        assert "requests." not in source
        assert "urllib.request" not in source
        assert "scripts/.logs" not in source
        assert ".db-wal" not in source
        assert ".db-shm" not in source

