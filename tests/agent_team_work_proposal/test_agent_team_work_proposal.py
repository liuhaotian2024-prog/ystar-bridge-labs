from __future__ import annotations

import json
import subprocess
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
PACK = ROOT / "agent_team_work_proposal"
GENERATED = PACK / "generated"
BUILDER = PACK / "tools" / "build_agent_team_work_proposal.py"
RUNNER = PACK / "tools" / "run_work_proposal_to_bridge.py"

JSON_OUTPUTS = [
    "mission_context_snapshot.json",
    "agent_team_observation_input.json",
    "autonomous_work_proposals.json",
    "selected_agent_work_proposal.json",
    "role_review_board.json",
    "tool_need_analysis.json",
    "generated_tool_request.json",
    "work_proposal_to_bridge_trace.json",
    "bridged_tool_result_ref.json",
    "work_proposal_cieu_event.json",
    "work_proposal_residual_delta.json",
    "next_agent_work_recommendations.json",
    "agent_team_work_proposal_summary.json",
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


def test_mission_context_and_observation_input_are_mission_bounded() -> None:
    run_builder()

    mission = load_json("mission_context_snapshot.json")
    observation = load_json("agent_team_observation_input.json")

    assert mission["mission_id"]
    assert mission["mission_bounded_autonomy"] is True
    assert mission["founder_sets_mission_agent_team_drives"] is True
    assert mission["step_by_step_human_prompting_required"] is False
    assert mission["current_safe_observation_sources"]
    assert mission["current_governed_tools"][0]["bridge_required"] is True
    assert observation["input_policy"] == "generated_read_model_only"
    assert observation["existing_governed_readonly_tool"]["callable"] is True
    assert observation["existing_tool_bridge"]["tool_invoked_through_bridge"] is True


def test_agent_team_generates_and_selects_safe_work_proposal() -> None:
    run_builder()

    proposals = load_json("autonomous_work_proposals.json")
    selected = load_json("selected_agent_work_proposal.json")

    assert proposals["proposal_count"] >= 5
    assert len(proposals["proposals"]) >= 5
    assert any("governed_readonly_observation_tool_v0" in proposal["tool_need"] for proposal in proposals["proposals"])
    for proposal in proposals["proposals"]:
        assert proposal["live_enabled"] is False
        assert proposal["external_action_enabled"] is False
    assert selected["selected_by_agent"] == "Aiden-CEO"
    assert selected["requires_tool_invocation"] is True
    assert selected["selected_tool_id"] == "governed_readonly_observation_tool_v0"
    assert selected["selected_bridge_id"] == "governed_tool_invocation_bridge_v0"
    assert selected["live_enabled"] is False
    assert selected["external_action_enabled"] is False


def test_role_review_board_includes_all_roles_and_governance_constraints() -> None:
    run_builder()

    board = load_json("role_review_board.json")
    reviews = {review["agent_id"]: review for review in board["reviews"]}
    assert set(reviews) == {
        "Aiden-CEO",
        "Ethan-CTO",
        "Maya-Governance",
        "Ryan-Platform",
        "Samantha-Secretary",
        "Leo-Kernel",
    }
    for review in reviews.values():
        assert review["approved_for_local_readonly_dry_run"] is True
    maya = reviews["Maya-Governance"]
    assert any("Pre-U bridge" in item for item in maya["required_constraints"])
    assert "direct tool invocation" in maya["forbidden_actions"]
    assert "governed_tool_invocation_bridge_v0 exists" in reviews["Ryan-Platform"]["support_or_concern"]
    assert "read-model observation" in reviews["Samantha-Secretary"]["support_or_concern"]
    assert "no runtime or kernel mutation" in reviews["Leo-Kernel"]["support_or_concern"]
    assert "deterministic builders/runners" in reviews["Ethan-CTO"]["support_or_concern"]


def test_tool_need_analysis_and_generated_request_are_bridge_compatible() -> None:
    run_builder()

    analysis = load_json("tool_need_analysis.json")
    request = load_json("generated_tool_request.json")

    assert analysis["tool_needed"] is True
    assert analysis["bridge_required"] is True
    assert analysis["tool_id"] == "governed_readonly_observation_tool_v0"
    assert analysis["bridge_id"] == "governed_tool_invocation_bridge_v0"
    assert analysis["risk_tier"] == "low"
    assert analysis["requires_y_star_gov"] is True
    assert analysis["requires_cieu_event"] is True
    assert analysis["operator_approval_required"] is False
    assert analysis["live_enabled"] is False
    assert analysis["external_action_enabled"] is False

    assert request["requesting_agent"] == "Aiden-CEO"
    assert request["supporting_agent"] == "Samantha-Secretary"
    assert request["tool_id"] == analysis["tool_id"]
    assert request["request_type"] == "company_state_observation"
    assert request["requested_summary_level"] == "executive"
    assert request["risk_tier"] == "low"
    assert request["requested_sources"]
    assert request["source_work_proposal_ref"].endswith("selected_agent_work_proposal.json")
    assert request["role_review_ref"].endswith("role_review_board.json")
    assert request["tool_need_analysis_ref"].endswith("tool_need_analysis.json")
    assert_false_flags(
        request,
        [
            "live_action_requested",
            "external_action_requested",
            "brain_writeback_requested",
            "memory_ingestion_requested",
            "cieu_persistence_requested",
        ],
    )


def test_runner_routes_generated_request_to_bridge() -> None:
    run_builder()
    run_script(
        str(RUNNER.relative_to(ROOT)),
        "--request",
        "agent_team_work_proposal/generated/generated_tool_request.json",
        "--output-dir",
        "agent_team_work_proposal/generated",
    )

    trace = load_json("work_proposal_to_bridge_trace.json")
    bridged = load_json("bridged_tool_result_ref.json")

    assert trace["bridge_runner_used"] is True
    assert trace["direct_tool_invocation_used"] is False
    assert trace["pre_u_bridge_required"] is True
    assert trace["pre_u_bridge_satisfied"] is True
    assert trace["real_action_executed"] is False
    assert trace["external_action_executed"] is False
    assert bridged["result_status"] == "success"
    assert bridged["read_source_count"] > 0
    assert bridged["real_action_executed"] is False
    assert bridged["external_action_executed"] is False
    assert bridged["live_action_enabled"] is False


def test_cieu_event_residual_delta_and_recommendations_are_dry_run_only() -> None:
    run_builder()

    event = load_json("work_proposal_cieu_event.json")
    delta = load_json("work_proposal_residual_delta.json")
    recommendations = load_json("next_agent_work_recommendations.json")

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
    assert recommendations["recommendation_count"] >= 3
    assert recommendations["recommendations"][0]["title"] == "L4.7 First Mission Dashboard Refresh Loop v0"
    for recommendation in recommendations["recommendations"]:
        assert recommendation["live_enabled"] is False
        assert recommendation["external_action_enabled"] is False


def test_readiness_summary_records_agent_team_work_and_disabled_flags() -> None:
    run_builder()

    summary = load_json("agent_team_work_proposal_summary.json")
    for field in [
        "agent_team_work_proposal_defined",
        "mission_context_snapshot_defined",
        "agent_team_observation_input_defined",
        "autonomous_work_proposals_defined",
        "selected_work_proposal_defined",
        "role_review_board_defined",
        "tool_need_analysis_defined",
        "generated_tool_request_defined",
        "work_proposal_routed_to_bridge",
        "bridge_runner_used",
        "bridged_tool_result_ref_defined",
        "work_proposal_cieu_event_defined",
        "work_proposal_residual_delta_defined",
        "next_agent_work_recommendations_defined",
        "mission_bounded_autonomy_supported",
        "founder_sets_mission_agent_team_drives",
        "agent_team_generated_the_work",
        "agent_team_selected_governed_tool",
        "pre_u_bridge_required",
        "pre_u_bridge_satisfied",
    ]:
        assert summary[field] is True

    assert summary["step_by_step_human_prompting_required"] is False
    assert_false_flags(
        summary,
        [
            "direct_tool_invocation_used",
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
        ],
    )
    assert summary["next_required_milestone"] == "L4.7 First Mission Dashboard Refresh Loop v0"


def test_generated_outputs_do_not_depend_on_forbidden_runtime_paths() -> None:
    run_builder()

    forbidden = [
        ".db-wal",
        ".db-shm",
        ".sqlite",
        ".sqlite3",
        "scripts/.logs/",
    ]
    for path in GENERATED.iterdir():
        if path.suffix not in {".json", ".md"}:
            continue
        text = path.read_text(encoding="utf-8").lower()
        for marker in forbidden:
            assert marker not in text, f"{marker} appeared in {path.name}"


def test_builder_and_runner_sources_are_non_runtime() -> None:
    for path in [BUILDER, RUNNER]:
        source = path.read_text(encoding="utf-8")
        assert "shell=True" not in source
        assert "import sqlite3" not in source
        assert "requests." not in source
        assert "urllib.request" not in source
