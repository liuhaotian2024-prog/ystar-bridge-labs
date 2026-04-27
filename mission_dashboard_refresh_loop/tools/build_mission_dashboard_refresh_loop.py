#!/usr/bin/env python3
"""Build L4.7 mission dashboard refresh loop artifacts."""

from __future__ import annotations

import json
import sys
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from mission_dashboard_refresh_loop.tools import run_dashboard_refresh_loop as runner


PACK = ROOT / "mission_dashboard_refresh_loop"
GENERATED = PACK / "generated"
NEXT_MILESTONE = runner.NEXT_MILESTONE

MISSION_CONTEXT = "agent_team_work_proposal/generated/mission_context_snapshot.json"
MISSION_DASHBOARD = "governed_observation_loop/generated/mission_dashboard_snapshot.json"
COMPANY_DIGEST = "governed_observation_loop/generated/company_state_digest.json"
WORK_SUMMARY = "agent_team_work_proposal/generated/agent_team_work_proposal_summary.json"
WORK_RECOMMENDATIONS = "agent_team_work_proposal/generated/next_agent_work_recommendations.json"
BRIDGED_RESULT = "agent_team_work_proposal/generated/bridged_tool_result_ref.json"
BRIDGE_SUMMARY = "governed_tool_invocation_bridge/generated/tool_bridge_readiness_summary.json"
READONLY_TOOL_SUMMARY = "governed_readonly_observation_tool/generated/tool_readiness_summary.json"
TRIAGE_SUMMARY = "legacy_asset_triage/generated/legacy_asset_triage_summary.json"
OBSERVATION_LOOP_SUMMARY = "governed_observation_loop/generated/governed_observation_loop_summary.json"
CONSOLE_SNAPSHOT = "console_read_model/generated/team_console_snapshot.json"


def write_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


def load_json(relative_path: str) -> dict[str, Any]:
    path = ROOT / relative_path
    data = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(data, dict):
        raise ValueError(f"Expected object JSON: {relative_path}")
    return data


def first_list(*values: Any, limit: int = 8) -> list[Any]:
    for value in values:
        if isinstance(value, list) and value:
            return value[:limit]
    return []


def build_refresh_loop_contract() -> dict[str, Any]:
    return {
        "schema_name": "ystar.mission_dashboard_refresh_loop.generated.refresh_loop_contract",
        "schema_version": "v0",
        "refresh_loop_id": "mission_dashboard_refresh_loop_v0",
        "refresh_loop_name": "First Mission Dashboard Refresh Loop",
        "refresh_loop_version": "v0",
        "mission_bounded_autonomy_supported": True,
        "founder_sets_mission_agent_team_drives": True,
        "step_by_step_human_prompting_required": False,
        "uses_agent_team_work_proposal": True,
        "uses_governed_tool_invocation_bridge": True,
        "uses_governed_readonly_observation_tool": True,
        "uses_generated_read_model_only": True,
        "scheduler_enabled": False,
        "daemon_enabled": False,
        "recurring_auto_run_enabled": False,
        "manual_local_run_only": True,
        "real_action_executed": False,
        "external_action_executed": False,
        "live_action_enabled": False,
        "network_enabled": False,
        "git_push_enabled": False,
        "daemon_control_enabled": False,
        "cieu_persistence_enabled": False,
        "brain_writeback_enabled": False,
        "memory_ingestion_enabled": False,
        "email_or_external_communication_enabled": False,
        "next_required_milestone": NEXT_MILESTONE,
    }


def build_previous_dashboard_snapshot(inputs: dict[str, dict[str, Any]]) -> dict[str, Any]:
    dashboard = inputs["dashboard"]
    digest = inputs["digest"]
    mission = inputs["mission_context"]
    console = inputs["console"]
    work = inputs["work_summary"]
    readiness = console.get("readiness_summary", {})
    return {
        "schema_name": "ystar.mission_dashboard_refresh_loop.generated.previous_dashboard_snapshot",
        "schema_version": "v0",
        "snapshot_id": "previous-dashboard-snapshot-001",
        "source_refs": [
            MISSION_DASHBOARD,
            COMPANY_DIGEST,
            MISSION_CONTEXT,
            WORK_SUMMARY,
            CONSOLE_SNAPSHOT,
        ],
        "mission_id": mission.get("mission_id"),
        "mission_summary": mission.get("founder_defined_mission") or dashboard.get("mission"),
        "milestone_chain": first_list(
            dashboard.get("current_milestone_chain"),
            readiness.get("ready_now"),
            limit=12,
        ),
        "known_capabilities": first_list(
            digest.get("what_it_can_safely_do_now"),
            readiness.get("ready_now"),
            limit=8,
        ),
        "known_blocked_actions": first_list(
            digest.get("what_remains_blocked"),
            mission.get("current_blocked_actions"),
            limit=8,
        ),
        "known_risks": first_list(dashboard.get("top_risks"), mission.get("current_top_risks"), limit=8),
        "known_opportunities": first_list(
            dashboard.get("top_opportunities"),
            mission.get("current_top_opportunities"),
            limit=8,
        ),
        "known_next_recommendations": [
            work.get("next_required_milestone", "L4.7 First Mission Dashboard Refresh Loop v0"),
            dashboard.get("next_recommended_work", "L4.4 First Governed Read-Only Observation Tool Wrapper v0"),
        ],
    }


def build_current_observation_input(inputs: dict[str, dict[str, Any]]) -> dict[str, Any]:
    work = inputs["work_summary"]
    bridge = inputs["bridge_summary"]
    readonly_tool = inputs["readonly_tool_summary"]
    triage = inputs["triage_summary"]
    observation = inputs["observation_loop_summary"]
    bridged = inputs["bridged_result"]
    recommendations = inputs["work_recommendations"]
    normalized = bridged.get("normalized_observation", {})
    return {
        "schema_name": "ystar.mission_dashboard_refresh_loop.generated.current_observation_input",
        "schema_version": "v0",
        "observation_input_id": "current-observation-input-001",
        "source_refs": [
            WORK_SUMMARY,
            WORK_RECOMMENDATIONS,
            BRIDGED_RESULT,
            BRIDGE_SUMMARY,
            READONLY_TOOL_SUMMARY,
            TRIAGE_SUMMARY,
            OBSERVATION_LOOP_SUMMARY,
            CONSOLE_SNAPSHOT,
        ],
        "latest_agent_team_work_status": {
            "agent_team_generated_the_work": work.get("agent_team_generated_the_work"),
            "agent_team_selected_governed_tool": work.get("agent_team_selected_governed_tool"),
            "work_proposal_routed_to_bridge": work.get("work_proposal_routed_to_bridge"),
            "direct_tool_invocation_used": work.get("direct_tool_invocation_used"),
        },
        "latest_bridge_status": {
            "tool_invoked_through_bridge": bridge.get("tool_invoked_through_bridge"),
            "first_governed_tool_invocation_chain_created": bridge.get(
                "first_governed_tool_invocation_chain_created"
            ),
            "direct_tool_invocation_rejected": bridge.get("direct_tool_invocation_rejected"),
        },
        "latest_readonly_tool_status": {
            "first_governed_tool_wrapper_created": readonly_tool.get(
                "first_governed_tool_wrapper_created"
            ),
            "local_readonly_dry_run_callable": readonly_tool.get("local_readonly_dry_run_callable"),
            "unsafe_invocation_rejected": readonly_tool.get("unsafe_invocation_rejected"),
        },
        "latest_triage_status": {
            "assets_scored": triage.get("assets_scored"),
            "top_absorption_candidate_count": triage.get("top_absorption_candidate_count"),
            "blind_absorption_allowed": triage.get("blind_absorption_allowed"),
            "blanket_rewrite_allowed": triage.get("blanket_rewrite_allowed"),
        },
        "latest_observation_loop_status": {
            "read_only_observation_loop_defined": observation.get("read_only_observation_loop_defined"),
            "observation_tick_generated": observation.get("observation_tick_generated"),
            "mission_dashboard_snapshot_defined": observation.get("mission_dashboard_snapshot_defined"),
        },
        "safe_new_findings": [
            "L4.6 generated an agent-team work proposal from mission and observation context.",
            "The selected proposal used the governed read-only observation tool through the L4.5 bridge.",
            f"The bridged tool result read {bridged.get('read_source_count', 0)} curated generated sources.",
        ],
        "blocked_risks": [
            "scheduler remains disabled",
            "daemon remains disabled",
            "live and external actions remain disabled",
            "CIEU persistence, brain writeback, and memory ingestion remain disabled",
        ],
        "candidate_next_work": [
            item.get("title")
            for item in recommendations.get("recommendations", [])
            if isinstance(item, dict)
        ],
        "current_governed_observation": {
            "result_status": bridged.get("result_status"),
            "read_source_count": bridged.get("read_source_count"),
            "next_work_candidates": bridged.get("next_work_candidates", []),
            "normalized_observation_keys": sorted(normalized.keys()),
        },
        "real_action_executed": False,
        "external_action_executed": False,
    }


def build_readiness_summary(payloads: dict[str, dict[str, Any]]) -> dict[str, Any]:
    trace = payloads["refresh_loop_trace"]
    return {
        "schema_name": "ystar.mission_dashboard_refresh_loop.generated.refresh_loop_readiness_summary",
        "schema_version": "v0",
        "mission_dashboard_refresh_loop_defined": True,
        "refresh_loop_contract_defined": True,
        "previous_dashboard_snapshot_defined": True,
        "current_observation_input_defined": True,
        "refreshed_mission_dashboard_defined": True,
        "company_state_delta_defined": True,
        "refreshed_autonomous_backlog_defined": True,
        "refresh_loop_trace_defined": True,
        "refresh_cieu_event_defined": True,
        "refresh_residual_delta_defined": True,
        "next_loop_recommendations_defined": True,
        "mission_bounded_autonomy_supported": True,
        "founder_sets_mission_agent_team_drives": True,
        "step_by_step_human_prompting_required": False,
        "dashboard_refresh_loop_ran": trace.get("runner_used") is True,
        "scheduler_used": False,
        "daemon_used": False,
        "manual_local_run_only": True,
        "real_action_executed": False,
        "external_action_executed": False,
        "live_action_enabled": False,
        "network_enabled": False,
        "git_push_enabled": False,
        "daemon_control_enabled": False,
        "cieu_persistence_enabled": False,
        "brain_writeback_enabled": False,
        "memory_ingestion_enabled": False,
        "email_or_external_communication_enabled": False,
        "next_required_milestone": NEXT_MILESTONE,
        "generated_contract": runner.CONTRACT_REF,
        "generated_previous_dashboard": runner.PREVIOUS_REF,
        "generated_current_observation": runner.CURRENT_REF,
        "generated_refreshed_dashboard": runner.REFRESHED_DASHBOARD_REF,
        "generated_company_state_delta": runner.DELTA_REF,
        "generated_refreshed_backlog": runner.BACKLOG_REF,
        "generated_cieu_event": runner.CIEU_EVENT_REF,
        "warning": (
            "Mission dashboard refresh loop is manual, local, read-only, and dry-run only. "
            "Scheduler and daemon use remain disabled."
        ),
    }


def render_report(
    previous: dict[str, Any],
    current: dict[str, Any],
    dashboard: dict[str, Any],
    delta: dict[str, Any],
    backlog: dict[str, Any],
    trace: dict[str, Any],
    event: dict[str, Any],
    residual: dict[str, Any],
    recommendations: dict[str, Any],
    summary: dict[str, Any],
) -> str:
    lines = [
        "# Mission Dashboard Refresh Loop Report",
        "",
        "## Previous Dashboard State",
        "",
        f"- mission_id: {previous.get('mission_id')}",
        f"- known_capabilities: {len(previous.get('known_capabilities', []))}",
        f"- known_blocked_actions: {len(previous.get('known_blocked_actions', []))}",
        "",
        "## Current Observation Input",
        "",
        f"- safe_new_findings: {len(current.get('safe_new_findings', []))}",
        f"- candidate_next_work: {len(current.get('candidate_next_work', []))}",
        f"- real_action_executed: {current.get('real_action_executed')}",
        f"- external_action_executed: {current.get('external_action_executed')}",
        "",
        "## Refreshed Mission Dashboard",
        "",
        f"- dashboard_id: {dashboard.get('dashboard_id')}",
        f"- company_operating_state: {dashboard.get('company_operating_state')}",
        f"- next_recommended_milestone: {dashboard.get('next_recommended_milestone')}",
        "",
        "## Company State Delta",
        "",
        f"- state_change_level: {delta.get('state_change_level')}",
        f"- requires_review: {delta.get('requires_review')}",
        f"- new_capabilities_detected: {len(delta.get('new_capabilities_detected', []))}",
        "",
        "## Refreshed Backlog",
        "",
        f"- backlog_count: {backlog.get('backlog_count')}",
        f"- top_item: {backlog.get('top_item')}",
        "",
        "## Refresh Loop Trace",
        "",
        f"- runner_used: {trace.get('runner_used')}",
        f"- scheduler_used: {trace.get('scheduler_used')}",
        f"- daemon_used: {trace.get('daemon_used')}",
        "",
        "## CIEU Event",
        "",
        f"- dry_run_only: {event.get('dry_run_only')}",
        f"- persistence_enabled: {event.get('persistence_enabled')}",
        f"- curation_required: {event.get('curation_required')}",
        "",
        "## Residual Delta",
        "",
        f"- delta_id: {residual.get('delta_id')}",
        f"- next_review_required: {residual.get('next_review_required')}",
        "",
        "## Next Recommendations",
        "",
        f"- recommendation_count: {recommendations.get('recommendation_count')}",
        f"- top_recommendation: {recommendations.get('recommendations', [{}])[0].get('title')}",
        "",
        "## Why No Scheduler Or Live Action Was Enabled",
        "",
        "The loop proves a deterministic manual refresh only. Scheduler, daemon, live action, external action, CIEU persistence, brain writeback, and memory ingestion remain disabled by policy.",
        "",
        f"Next required milestone: {summary.get('next_required_milestone')}",
        "",
    ]
    return "\n".join(lines)


def main() -> int:
    GENERATED.mkdir(parents=True, exist_ok=True)
    inputs = {
        "mission_context": load_json(MISSION_CONTEXT),
        "dashboard": load_json(MISSION_DASHBOARD),
        "digest": load_json(COMPANY_DIGEST),
        "work_summary": load_json(WORK_SUMMARY),
        "work_recommendations": load_json(WORK_RECOMMENDATIONS),
        "bridged_result": load_json(BRIDGED_RESULT),
        "bridge_summary": load_json(BRIDGE_SUMMARY),
        "readonly_tool_summary": load_json(READONLY_TOOL_SUMMARY),
        "triage_summary": load_json(TRIAGE_SUMMARY),
        "observation_loop_summary": load_json(OBSERVATION_LOOP_SUMMARY),
        "console": load_json(CONSOLE_SNAPSHOT),
    }

    contract = build_refresh_loop_contract()
    previous = build_previous_dashboard_snapshot(inputs)
    current = build_current_observation_input(inputs)
    write_json(GENERATED / "refresh_loop_contract.json", contract)
    write_json(GENERATED / "previous_dashboard_snapshot.json", previous)
    write_json(GENERATED / "current_observation_input.json", current)

    payloads = runner.run_refresh_loop(GENERATED)
    summary = build_readiness_summary(payloads)
    write_json(GENERATED / "refresh_loop_readiness_summary.json", summary)
    report = render_report(
        previous,
        current,
        payloads["refreshed_mission_dashboard"],
        payloads["company_state_delta"],
        payloads["refreshed_autonomous_backlog"],
        payloads["refresh_loop_trace"],
        payloads["refresh_cieu_event"],
        payloads["refresh_residual_delta"],
        payloads["next_loop_recommendations"],
        summary,
    )
    (GENERATED / "refresh_loop_report.md").write_text(report, encoding="utf-8")

    print("Mission dashboard refresh loop artifacts generated.")
    print(f"dashboard_refresh_loop_ran: {summary['dashboard_refresh_loop_ran']}")
    print(f"scheduler_used: {summary['scheduler_used']}")
    print(f"daemon_used: {summary['daemon_used']}")
    return 0


if __name__ == "__main__":
    sys.exit(main())

