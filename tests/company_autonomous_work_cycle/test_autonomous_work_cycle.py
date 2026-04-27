from __future__ import annotations

import json
import subprocess
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
INVENTORY_BUILDER = ROOT / "company_autonomy_inventory" / "tools" / "build_company_autonomy_inventory.py"
CYCLE_BUILDER = ROOT / "company_autonomous_work_cycle" / "tools" / "build_autonomous_work_cycle.py"
GENERATED = ROOT / "company_autonomous_work_cycle" / "generated"
INVENTORY_GENERATED = ROOT / "company_autonomy_inventory" / "generated"

JSON_OUTPUTS = [
    "mission_profile.json",
    "company_observation_snapshot.json",
    "autonomous_work_backlog.json",
    "selected_work_item.json",
    "role_delegation_plan.json",
    "governed_tool_selection.json",
    "pre_u_packet_simulation.json",
    "governance_decision_simulation.json",
    "simulated_action_plan.json",
    "simulated_cieu_event.json",
    "residual_delta_simulation.json",
    "next_task_recommendations.json",
    "autonomous_work_cycle_summary.json",
]

REQUIRED_ROLES = {
    "Aiden-CEO",
    "Ethan-CTO",
    "Maya-Governance",
    "Ryan-Platform",
    "Samantha-Secretary",
    "Leo-Kernel",
}


def run_script(path: Path) -> None:
    result = subprocess.run(
        ["python3", str(path.relative_to(ROOT))],
        cwd=ROOT,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        check=False,
    )
    assert result.returncode == 0, result.stdout + result.stderr


def run_builders() -> None:
    run_script(INVENTORY_BUILDER)
    run_script(CYCLE_BUILDER)


def load_cycle_json(name: str) -> dict:
    path = GENERATED / name
    assert path.exists(), f"missing generated file: {name}"
    return json.loads(path.read_text(encoding="utf-8"))


def load_inventory_json(name: str) -> dict:
    return json.loads((INVENTORY_GENERATED / name).read_text(encoding="utf-8"))


def test_autonomous_work_cycle_outputs_and_summary_flags() -> None:
    run_builders()

    for name in JSON_OUTPUTS:
        load_cycle_json(name)

    summary = load_cycle_json("autonomous_work_cycle_summary.json")
    for field in [
        "autonomous_work_cycle_defined",
        "mission_bounded_autonomy_defined",
        "founder_sets_mission_agent_team_drives",
        "observation_snapshot_defined",
        "autonomous_work_backlog_defined",
        "selected_work_item_defined",
        "role_delegation_defined",
        "governed_tool_selection_defined",
        "pre_u_packet_simulated",
        "governance_decision_simulated",
        "action_plan_simulated",
        "cieu_event_simulated",
        "residual_delta_simulated",
        "next_task_recommendations_defined",
        "requires_manual_enablement_for_live",
    ]:
        assert summary[field] is True

    for field in [
        "step_by_step_human_prompting_required",
        "real_action_executed",
        "external_action_executed",
        "live_action_enabled",
        "git_push_enabled",
        "daemon_control_enabled",
        "cieu_persistence_enabled",
        "brain_writeback_enabled",
        "memory_ingestion_enabled",
        "email_or_external_communication_enabled",
    ]:
        assert summary[field] is False

    assert summary["next_required_milestone"] == "L4.3 Governed Read-Only Observation Loop v0"


def test_mission_backlog_delegation_and_tool_selection() -> None:
    run_builders()

    mission = load_cycle_json("mission_profile.json")
    backlog = load_cycle_json("autonomous_work_backlog.json")
    selected = load_cycle_json("selected_work_item.json")
    delegation = load_cycle_json("role_delegation_plan.json")
    tool_selection = load_cycle_json("governed_tool_selection.json")
    registry = load_inventory_json("governed_tool_registry_candidates.json")

    assert mission["mission_bounded_autonomy"] is True
    assert mission["step_by_step_human_prompting_required"] is False
    assert mission["human_sets_mission_agent_team_drives_execution"] is True

    work_items = backlog["work_items"]
    assert len(work_items) >= 5
    assert selected["selected_work_item"]["work_item_id"] in {item["work_item_id"] for item in work_items}
    assert selected["selected_work_item"]["live_enabled"] is False

    roles = {item["agent_id"] for item in delegation["delegations"]}
    assert roles == REQUIRED_ROLES

    candidate_ids = {candidate["tool_id"] for candidate in registry["candidates"]}
    selected_tool_ids = {tool["tool_id"] for tool in tool_selection["selected_tool_candidates"]}
    assert selected_tool_ids
    assert selected_tool_ids <= candidate_ids
    assert tool_selection["live_enabled"] is False
    assert tool_selection["external_action_enabled"] is False


def test_pre_u_governance_action_cieu_and_residual_are_simulated_only() -> None:
    run_builders()

    pre_u = load_cycle_json("pre_u_packet_simulation.json")
    decision = load_cycle_json("governance_decision_simulation.json")
    action_plan = load_cycle_json("simulated_action_plan.json")
    event = load_cycle_json("simulated_cieu_event.json")
    delta = load_cycle_json("residual_delta_simulation.json")
    next_tasks = load_cycle_json("next_task_recommendations.json")

    assert len(pre_u["candidate_U"]) >= 3
    assert all(candidate["live_enabled"] is False for candidate in pre_u["candidate_U"])

    assert decision["decision"] == "allow_simulation"
    assert decision["allowed_only_as_simulation"] is True
    assert decision["live_action_allowed"] is False
    assert decision["external_action_allowed"] is False
    assert decision["cieu_persistence_allowed"] is False
    assert decision["brain_writeback_allowed"] is False
    assert decision["memory_ingestion_allowed"] is False

    assert action_plan["real_execution_performed"] is False
    assert action_plan["external_effects"] == []

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

    assert len(next_tasks["recommendations"]) >= 3
    assert next_tasks["recommendations"][0]["title"] == "L4.3 Governed Read-Only Observation Loop v0"
    assert all(task["live_enabled"] is False for task in next_tasks["recommendations"])


def test_builder_source_remains_local_and_non_runtime() -> None:
    source = CYCLE_BUILDER.read_text(encoding="utf-8")
    assert "shell=True" not in source
    assert "import subprocess" not in source
    assert "import sqlite3" not in source
    assert "scripts/.logs" not in source
    assert ".db-wal" not in source
    assert ".db-shm" not in source
