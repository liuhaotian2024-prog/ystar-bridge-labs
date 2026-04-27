from __future__ import annotations

import json
import subprocess
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
PACK = ROOT / "mission_dashboard_refresh_loop"
GENERATED = PACK / "generated"
BUILDER = PACK / "tools" / "build_mission_dashboard_refresh_loop.py"
RUNNER = PACK / "tools" / "run_dashboard_refresh_loop.py"

JSON_OUTPUTS = [
    "refresh_loop_contract.json",
    "previous_dashboard_snapshot.json",
    "current_observation_input.json",
    "refreshed_mission_dashboard.json",
    "company_state_delta.json",
    "refreshed_autonomous_backlog.json",
    "refresh_loop_trace.json",
    "refresh_cieu_event.json",
    "refresh_residual_delta.json",
    "next_loop_recommendations.json",
    "refresh_loop_readiness_summary.json",
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


def test_refresh_contract_previous_current_and_dashboard_exist() -> None:
    run_builder()

    contract = load_json("refresh_loop_contract.json")
    previous = load_json("previous_dashboard_snapshot.json")
    current = load_json("current_observation_input.json")
    dashboard = load_json("refreshed_mission_dashboard.json")
    delta = load_json("company_state_delta.json")

    assert contract["refresh_loop_id"] == "mission_dashboard_refresh_loop_v0"
    assert contract["mission_bounded_autonomy_supported"] is True
    assert contract["manual_local_run_only"] is True
    assert contract["scheduler_enabled"] is False
    assert contract["daemon_enabled"] is False
    assert previous["snapshot_id"]
    assert previous["known_capabilities"]
    assert current["observation_input_id"]
    assert current["real_action_executed"] is False
    assert current["external_action_executed"] is False
    assert dashboard["dashboard_id"]
    assert dashboard["governed_tooling_state"]["first_governed_readonly_tool_exists"] is True
    assert dashboard["governed_tooling_state"]["pre_u_bridge_invocation_chain_exists"] is True
    assert dashboard["agent_team_work_state"]["agent_team_generated_work_proposal"] is True
    assert delta["state_change_level"] == "meaningful"
    assert delta["requires_review"] is True


def test_refreshed_backlog_and_trace_are_manual_and_disabled() -> None:
    run_builder()
    run_script(
        str(RUNNER.relative_to(ROOT)),
        "--output-dir",
        "mission_dashboard_refresh_loop/generated",
    )

    backlog = load_json("refreshed_autonomous_backlog.json")
    trace = load_json("refresh_loop_trace.json")

    assert backlog["backlog_count"] >= 5
    assert backlog["items"][0]["title"] == "L4.8 Governed Recurring Observation Loop Contract v0"
    for item in backlog["items"]:
        assert item["live_enabled"] is False
        assert item["external_action_enabled"] is False
    assert trace["runner_used"] is True
    assert trace["scheduler_used"] is False
    assert trace["daemon_used"] is False
    assert trace["real_action_executed"] is False
    assert trace["external_action_executed"] is False


def test_refresh_cieu_event_and_residual_delta_are_dry_run_only() -> None:
    run_builder()

    event = load_json("refresh_cieu_event.json")
    delta = load_json("refresh_residual_delta.json")

    assert event["dry_run_only"] is True
    assert event["persistence_enabled"] is False
    assert event["learning_eligibility"] is False
    assert event["curation_required"] is True
    assert event["direct_brain_writeback_allowed"] is False
    assert event["direct_memory_ingestion_allowed"] is False
    assert event["raw_artifact_ingestion_allowed"] is False
    assert delta["curation_required"] is True
    assert delta["direct_brain_writeback_allowed"] is False
    assert delta["direct_memory_ingestion_allowed"] is False
    assert delta["next_review_required"] is True


def test_next_recommendations_and_readiness_summary() -> None:
    run_builder()

    recommendations = load_json("next_loop_recommendations.json")
    summary = load_json("refresh_loop_readiness_summary.json")

    assert recommendations["recommendation_count"] >= 3
    assert recommendations["recommendations"][0]["title"] == "L4.8 Governed Recurring Observation Loop Contract v0"
    for recommendation in recommendations["recommendations"]:
        assert recommendation["live_enabled"] is False
        assert recommendation["external_action_enabled"] is False

    for field in [
        "mission_dashboard_refresh_loop_defined",
        "refresh_loop_contract_defined",
        "previous_dashboard_snapshot_defined",
        "current_observation_input_defined",
        "refreshed_mission_dashboard_defined",
        "company_state_delta_defined",
        "refreshed_autonomous_backlog_defined",
        "refresh_loop_trace_defined",
        "refresh_cieu_event_defined",
        "refresh_residual_delta_defined",
        "next_loop_recommendations_defined",
        "mission_bounded_autonomy_supported",
        "founder_sets_mission_agent_team_drives",
        "dashboard_refresh_loop_ran",
        "manual_local_run_only",
    ]:
        assert summary[field] is True

    assert summary["step_by_step_human_prompting_required"] is False
    assert summary["scheduler_used"] is False
    assert summary["daemon_used"] is False
    assert summary["next_required_milestone"] == "L4.8 Governed Recurring Observation Loop Contract v0"


def test_all_live_external_and_writeback_flags_remain_false() -> None:
    run_builder()

    summary = load_json("refresh_loop_readiness_summary.json")
    contract = load_json("refresh_loop_contract.json")
    dashboard = load_json("refreshed_mission_dashboard.json")

    disabled = [
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
    assert_false_flags(
        dashboard["live_readiness_state"],
        [
            "live_action_enabled",
            "external_action_enabled",
            "cieu_persistence_enabled",
            "brain_writeback_enabled",
            "memory_ingestion_enabled",
        ],
    )


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

