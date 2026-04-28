from __future__ import annotations

import json
import subprocess
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
PACK = ROOT / "recurring_observation_loop_contract"
GENERATED = PACK / "generated"
BUILDER = PACK / "tools" / "build_recurring_observation_contract.py"
SIMULATOR = PACK / "tools" / "simulate_recurring_observation_tick.py"

JSON_OUTPUTS = [
    "recurring_loop_contract.json",
    "recurrence_schedule_draft.json",
    "allowed_observation_sources.json",
    "tick_governance_gate.json",
    "simulated_observation_tick_001.json",
    "simulated_tick_dashboard_delta.json",
    "simulated_tick_work_candidates.json",
    "simulated_tick_cieu_event.json",
    "simulated_tick_residual_delta.json",
    "stop_abort_conditions.json",
    "escalation_conditions.json",
    "manual_enablement_checklist.json",
    "recurring_loop_readiness_summary.json",
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


def test_contract_and_schedule_keep_recurrence_disabled() -> None:
    run_builder()

    contract = load_json("recurring_loop_contract.json")
    schedule = load_json("recurrence_schedule_draft.json")

    assert contract["recurring_loop_id"] == "governed_recurring_observation_loop_contract_v0"
    assert contract["recurrence_defined"] is True
    assert contract["recurrence_enabled"] is False
    assert contract["scheduler_enabled"] is False
    assert contract["daemon_enabled"] is False
    assert contract["auto_run_enabled"] is False
    assert contract["manual_local_simulation_only"] is True
    assert contract["tick_requires_governance_gate"] is True
    assert contract["tick_requires_cieu_event"] is True
    assert contract["tick_requires_residual_delta"] is True
    assert contract["tick_requires_dashboard_refresh"] is True
    assert contract["tick_requires_work_candidate_generation"] is True
    assert contract["tick_requires_stop_abort_check"] is True
    assert contract["tick_requires_escalation_check"] is True
    assert schedule["schedule_type"] == "draft_only"
    assert schedule["operator_enablement_required"] is True
    assert schedule["recurrence_enabled"] is False
    assert schedule["scheduler_enabled"] is False
    assert schedule["daemon_enabled"] is False


def test_allowed_sources_and_governance_gate_are_safe() -> None:
    run_builder()

    sources = load_json("allowed_observation_sources.json")
    gate = load_json("tick_governance_gate.json")

    assert sources["source_count"] > 0
    for source in sources["sources"]:
        assert source["safe_to_read_now"] is True
        assert source["raw_runtime_artifact"] is False
        assert source["requires_network"] is False
        assert source["requires_credentials"] is False
        assert source["source_path"].endswith(".json")
    assert gate["tick_type"] == "recurring_observation_tick"
    assert gate["decision"] == "allow_manual_local_simulated_tick"
    assert gate["allowed_only_as_manual_local_simulation"] is True
    assert gate["recurrence_enabled"] is False
    assert gate["scheduler_enabled"] is False
    assert gate["daemon_enabled"] is False
    assert gate["live_action_allowed"] is False
    assert gate["external_action_allowed"] is False
    assert gate["cieu_persistence_allowed"] is False
    assert gate["brain_writeback_allowed"] is False
    assert gate["memory_ingestion_allowed"] is False


def test_simulated_tick_delta_and_work_candidates() -> None:
    run_builder()
    run_script(
        str(SIMULATOR.relative_to(ROOT)),
        "--output-dir",
        "recurring_observation_loop_contract/generated",
    )

    tick = load_json("simulated_observation_tick_001.json")
    dashboard_delta = load_json("simulated_tick_dashboard_delta.json")
    candidates = load_json("simulated_tick_work_candidates.json")

    assert tick["manual_local_simulation_only"] is True
    assert tick["recurrence_enabled"] is False
    assert tick["scheduler_used"] is False
    assert tick["daemon_used"] is False
    assert tick["real_action_executed"] is False
    assert tick["external_action_executed"] is False
    assert tick["live_action_enabled"] is False
    assert dashboard_delta["state_change_level"] == "meaningful"
    assert dashboard_delta["requires_review"] is True
    assert candidates["candidate_count"] >= 3
    assert candidates["candidates"][0]["title"] == "L4.9 Manual Recurring Observation Tick Runner v0"
    for candidate in candidates["candidates"]:
        assert candidate["live_enabled"] is False
        assert candidate["external_action_enabled"] is False


def test_tick_cieu_event_and_residual_delta_are_dry_run_only() -> None:
    run_builder()

    event = load_json("simulated_tick_cieu_event.json")
    residual = load_json("simulated_tick_residual_delta.json")

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


def test_stop_abort_escalation_and_manual_enablement_are_defined_disabled() -> None:
    run_builder()

    stop_abort = load_json("stop_abort_conditions.json")
    escalation = load_json("escalation_conditions.json")
    checklist = load_json("manual_enablement_checklist.json")

    assert stop_abort["condition_count"] >= 10
    for condition in stop_abort["conditions"]:
        assert condition["action"] == "stop_or_abort"
        assert condition["requires_operator_review"] is True
    assert escalation["condition_count"] >= 8
    for condition in escalation["conditions"]:
        assert condition["requires_operator_review"] is True
    disallowed = {"enabled", "approved", "complete", "live", "active"}
    for item in checklist["checklist_items"]:
        assert item["status"] in {"not_started", "defined_disabled"}
        assert item["status"] not in disallowed


def test_readiness_summary_and_all_disable_flags() -> None:
    run_builder()

    summary = load_json("recurring_loop_readiness_summary.json")
    contract = load_json("recurring_loop_contract.json")

    for field in [
        "recurring_observation_loop_contract_defined",
        "recurrence_policy_defined",
        "manual_local_simulation_only",
        "allowed_observation_sources_defined",
        "tick_governance_gate_defined",
        "simulated_observation_tick_defined",
        "simulated_tick_dashboard_delta_defined",
        "simulated_tick_work_candidates_defined",
        "simulated_tick_cieu_event_defined",
        "simulated_tick_residual_delta_defined",
        "stop_abort_conditions_defined",
        "escalation_conditions_defined",
        "manual_enablement_checklist_defined",
        "mission_bounded_autonomy_supported",
        "founder_sets_mission_agent_team_drives",
    ]:
        assert summary[field] is True

    assert summary["next_required_milestone"] == "L4.9 Manual Recurring Observation Tick Runner v0"
    assert summary["step_by_step_human_prompting_required"] is False

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


def test_builder_and_simulator_sources_are_non_runtime() -> None:
    for path in [BUILDER, SIMULATOR]:
        source = path.read_text(encoding="utf-8")
        assert "shell=True" not in source
        assert "import sqlite3" not in source
        assert "requests." not in source
        assert "urllib.request" not in source
        assert "scripts/.logs" not in source
        assert ".db-wal" not in source
        assert ".db-shm" not in source

