#!/usr/bin/env python3
"""Run the deterministic L4.7 mission dashboard refresh loop."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[2]
PACK = ROOT / "mission_dashboard_refresh_loop"
GENERATED = PACK / "generated"
NEXT_MILESTONE = "L4.8 Governed Recurring Observation Loop Contract v0"
REFRESH_LOOP_ID = "mission_dashboard_refresh_loop_v0"

CONTRACT_REF = "mission_dashboard_refresh_loop/generated/refresh_loop_contract.json"
PREVIOUS_REF = "mission_dashboard_refresh_loop/generated/previous_dashboard_snapshot.json"
CURRENT_REF = "mission_dashboard_refresh_loop/generated/current_observation_input.json"
REFRESHED_DASHBOARD_REF = "mission_dashboard_refresh_loop/generated/refreshed_mission_dashboard.json"
DELTA_REF = "mission_dashboard_refresh_loop/generated/company_state_delta.json"
BACKLOG_REF = "mission_dashboard_refresh_loop/generated/refreshed_autonomous_backlog.json"
TRACE_REF = "mission_dashboard_refresh_loop/generated/refresh_loop_trace.json"
CIEU_EVENT_REF = "mission_dashboard_refresh_loop/generated/refresh_cieu_event.json"
RESIDUAL_DELTA_REF = "mission_dashboard_refresh_loop/generated/refresh_residual_delta.json"
NEXT_RECOMMENDATIONS_REF = "mission_dashboard_refresh_loop/generated/next_loop_recommendations.json"


class RefreshLoopError(Exception):
    """Raised when the refresh loop cannot run safely."""


def repo_path(relative_path: str) -> Path:
    candidate = Path(relative_path)
    if candidate.is_absolute():
        raise RefreshLoopError(f"absolute path rejected: {relative_path}")
    resolved = (ROOT / candidate).resolve()
    try:
        resolved.relative_to(ROOT)
    except ValueError as exc:
        raise RefreshLoopError(f"path escapes repository root: {relative_path}") from exc
    return resolved


def output_dir_path(relative_path: str) -> Path:
    path = repo_path(relative_path)
    try:
        path.relative_to(GENERATED.resolve())
    except ValueError as exc:
        raise RefreshLoopError("output directory must be mission_dashboard_refresh_loop/generated") from exc
    return path


def load_json(path: Path) -> dict[str, Any]:
    data = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(data, dict):
        raise RefreshLoopError(f"expected object JSON: {path}")
    return data


def write_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


def limited(items: Any, limit: int = 6) -> list[Any]:
    if isinstance(items, list):
        return items[:limit]
    return []


def build_refreshed_dashboard(
    contract: dict[str, Any],
    previous: dict[str, Any],
    current: dict[str, Any],
) -> dict[str, Any]:
    agent_status = current.get("latest_agent_team_work_status", {})
    bridge_status = current.get("latest_bridge_status", {})
    readonly_status = current.get("latest_readonly_tool_status", {})
    triage_status = current.get("latest_triage_status", {})
    observation_status = current.get("latest_observation_loop_status", {})
    return {
        "schema_name": "ystar.mission_dashboard_refresh_loop.generated.refreshed_mission_dashboard",
        "schema_version": "v0",
        "dashboard_id": "refreshed-mission-dashboard-001",
        "refresh_loop_id": contract.get("refresh_loop_id", REFRESH_LOOP_ID),
        "mission_id": previous.get("mission_id"),
        "mission_summary": previous.get("mission_summary"),
        "current_phase": "L4.7 deterministic mission dashboard refresh",
        "latest_committed_milestone": "L4.6 Agent Team Work Proposal to Governed Tool Invocation v0",
        "company_operating_state": "mission_bounded_local_readonly_dry_run",
        "mission_bounded_autonomy_state": {
            "supported": contract.get("mission_bounded_autonomy_supported"),
            "founder_sets_mission_agent_team_drives": contract.get(
                "founder_sets_mission_agent_team_drives"
            ),
            "step_by_step_human_prompting_required": contract.get(
                "step_by_step_human_prompting_required"
            ),
        },
        "observation_capability_state": {
            "governed_observation_loop_defined": observation_status.get(
                "read_only_observation_loop_defined"
            ),
            "current_observation_source": "agent_team_work_proposal/generated/bridged_tool_result_ref.json",
            "safe_findings": current.get("safe_new_findings", []),
        },
        "governed_tooling_state": {
            "first_governed_readonly_tool_exists": readonly_status.get(
                "first_governed_tool_wrapper_created"
            ),
            "local_readonly_dry_run_callable": readonly_status.get("local_readonly_dry_run_callable"),
            "pre_u_bridge_invocation_chain_exists": bridge_status.get(
                "first_governed_tool_invocation_chain_created"
            ),
            "tool_invoked_through_bridge": bridge_status.get("tool_invoked_through_bridge"),
        },
        "agent_team_work_state": {
            "agent_team_generated_work_proposal": agent_status.get("agent_team_generated_the_work"),
            "agent_team_selected_governed_tool": agent_status.get(
                "agent_team_selected_governed_tool"
            ),
            "work_proposal_routed_to_bridge": agent_status.get("work_proposal_routed_to_bridge"),
        },
        "legacy_asset_absorption_state": {
            "assets_scored": triage_status.get("assets_scored"),
            "blind_absorption_allowed": triage_status.get("blind_absorption_allowed"),
            "blanket_rewrite_allowed": triage_status.get("blanket_rewrite_allowed"),
        },
        "cieu_learning_state": {
            "dry_run_events_only": True,
            "persistence_enabled": False,
            "curation_required": True,
        },
        "live_readiness_state": {
            "live_action_enabled": False,
            "external_action_enabled": False,
            "cieu_persistence_enabled": False,
            "brain_writeback_enabled": False,
            "memory_ingestion_enabled": False,
        },
        "blocked_actions": current.get("blocked_risks", []),
        "top_risks": [
            "scheduler and daemon remain disabled",
            "live and external actions remain blocked",
            "CIEU persistence and writeback remain disabled",
        ],
        "top_opportunities": [
            "define a governed recurring observation loop contract",
            "turn refreshed dashboard evidence into a recurring loop fixture",
            "prepare dashboard refresh review before any scheduler exists",
        ],
        "next_recommended_milestone": NEXT_MILESTONE,
        "evidence_refs": previous.get("source_refs", []) + current.get("source_refs", []),
        "refreshed_at": "stable_refresh_001",
    }


def build_company_state_delta(
    previous: dict[str, Any],
    current: dict[str, Any],
    dashboard: dict[str, Any],
) -> dict[str, Any]:
    return {
        "schema_name": "ystar.mission_dashboard_refresh_loop.generated.company_state_delta",
        "schema_version": "v0",
        "delta_id": "company-state-delta-001",
        "previous_snapshot_ref": PREVIOUS_REF,
        "current_observation_ref": CURRENT_REF,
        "new_capabilities_detected": [
            "agent-team generated work proposal routed to governed tool bridge",
            "mission dashboard can now be refreshed from governed read-only observation evidence",
            "company state delta can be emitted as a dry-run CIEU-compatible fixture",
        ],
        "new_risks_detected": [
            "recurring operation needs a future scheduler-disabled contract before automation",
        ],
        "resolved_or_reduced_risks": [
            "manual tool request dependency reduced by agent-team generated proposal flow",
            "dashboard staleness reduced by deterministic refresh artifact",
        ],
        "new_work_candidates": current.get("candidate_next_work", []),
        "mission_progress_summary": (
            "The company now has a deterministic local refresh loop that converts L4.6 "
            "governed observation evidence into a refreshed mission dashboard and backlog."
        ),
        "state_change_level": "meaningful",
        "requires_review": True,
        "direct_brain_writeback_allowed": False,
        "direct_memory_ingestion_allowed": False,
        "evidence_refs": previous.get("source_refs", []) + dashboard.get("evidence_refs", []),
    }


def build_refreshed_backlog(dashboard: dict[str, Any], delta: dict[str, Any]) -> dict[str, Any]:
    items = [
        {
            "backlog_item_id": "refresh-backlog-001",
            "title": NEXT_MILESTONE,
            "description": "Define the contract for a governed recurring observation loop without enabling a scheduler.",
            "recommended_owner_agent": "Ryan-Platform",
            "supporting_agents": ["Samantha-Secretary", "Maya-Governance", "Leo-Kernel"],
            "mission_relevance": "Moves the company from manual refresh toward governed recurrence while preserving disabled live behavior.",
            "source_evidence_refs": [DELTA_REF, REFRESHED_DASHBOARD_REF],
            "risk_tier": "low",
            "requires_y_star_gov": True,
            "requires_operator_approval": False,
            "requires_cieu_event": True,
            "requires_live_action": False,
            "live_enabled": False,
            "external_action_enabled": False,
            "priority": 1,
            "selection_reason": "It is the smallest safe next step after a manual dashboard refresh loop.",
        },
        {
            "backlog_item_id": "refresh-backlog-002",
            "title": "Add dashboard refresh review packet fixture v0",
            "description": "Create a Pre-U review packet fixture for recurring dashboard refresh proposals.",
            "recommended_owner_agent": "Maya-Governance",
            "supporting_agents": ["Aiden-CEO"],
            "mission_relevance": "Keeps future recurring refresh decisions explainable and governed.",
            "source_evidence_refs": [TRACE_REF],
            "risk_tier": "low",
            "requires_y_star_gov": True,
            "requires_operator_approval": False,
            "requires_cieu_event": True,
            "requires_live_action": False,
            "live_enabled": False,
            "external_action_enabled": False,
            "priority": 2,
            "selection_reason": "Review packets can harden the next recurring-loop contract.",
        },
        {
            "backlog_item_id": "refresh-backlog-003",
            "title": "Create mission dashboard staleness indicator v0",
            "description": "Define a deterministic read-model field that marks whether generated dashboard evidence is stale.",
            "recommended_owner_agent": "Samantha-Secretary",
            "supporting_agents": ["Ryan-Platform"],
            "mission_relevance": "Improves autonomous situational awareness without external actions.",
            "source_evidence_refs": [REFRESHED_DASHBOARD_REF],
            "risk_tier": "low",
            "requires_y_star_gov": True,
            "requires_operator_approval": False,
            "requires_cieu_event": True,
            "requires_live_action": False,
            "live_enabled": False,
            "external_action_enabled": False,
            "priority": 3,
            "selection_reason": "A staleness indicator helps the team know when refresh is needed.",
        },
        {
            "backlog_item_id": "refresh-backlog-004",
            "title": "Plan governed wrapper for dashboard read-only refresh command",
            "description": "Design a future wrapper contract for invoking refresh through governance, not as an autonomous daemon.",
            "recommended_owner_agent": "Ethan-CTO",
            "supporting_agents": ["Leo-Kernel", "Maya-Governance"],
            "mission_relevance": "Moves toward tool-mediated company operation while preserving architecture boundaries.",
            "source_evidence_refs": [BACKLOG_REF],
            "risk_tier": "medium",
            "requires_y_star_gov": True,
            "requires_operator_approval": False,
            "requires_cieu_event": True,
            "requires_live_action": False,
            "live_enabled": False,
            "external_action_enabled": False,
            "priority": 4,
            "selection_reason": "Useful after the recurring-loop contract defines allowed invocation boundaries.",
        },
        {
            "backlog_item_id": "refresh-backlog-005",
            "title": "Prepare first operator-reviewed recurrence candidate",
            "description": "Draft a future candidate for operator-reviewed recurring refresh without scheduling or executing it.",
            "recommended_owner_agent": "Aiden-CEO",
            "supporting_agents": ["Maya-Governance", "Ryan-Platform"],
            "mission_relevance": "Reduces founder prompting while keeping human-controlled enablement explicit.",
            "source_evidence_refs": [DELTA_REF],
            "risk_tier": "medium",
            "requires_y_star_gov": True,
            "requires_operator_approval": True,
            "requires_cieu_event": True,
            "requires_live_action": False,
            "live_enabled": False,
            "external_action_enabled": False,
            "priority": 5,
            "selection_reason": "Operator review belongs after the contract exists, not in L4.7.",
        },
    ]
    return {
        "schema_name": "ystar.mission_dashboard_refresh_loop.generated.refreshed_autonomous_backlog",
        "schema_version": "v0",
        "dashboard_ref": REFRESHED_DASHBOARD_REF,
        "company_state_delta_ref": DELTA_REF,
        "backlog_count": len(items),
        "items": items,
        "top_item": items[0]["title"],
        "live_enabled": False,
        "external_action_enabled": False,
    }


def build_trace() -> dict[str, Any]:
    return {
        "schema_name": "ystar.mission_dashboard_refresh_loop.generated.refresh_loop_trace",
        "schema_version": "v0",
        "trace_id": "refresh-loop-trace-001",
        "refresh_loop_contract_ref": CONTRACT_REF,
        "previous_dashboard_snapshot_ref": PREVIOUS_REF,
        "current_observation_input_ref": CURRENT_REF,
        "refreshed_dashboard_ref": REFRESHED_DASHBOARD_REF,
        "company_state_delta_ref": DELTA_REF,
        "refreshed_backlog_ref": BACKLOG_REF,
        "runner_used": True,
        "scheduler_used": False,
        "daemon_used": False,
        "real_action_executed": False,
        "external_action_executed": False,
        "notes": "Manual local refresh transformed generated evidence into dashboard, delta, and backlog artifacts.",
    }


def build_refresh_event(
    dashboard: dict[str, Any],
    delta: dict[str, Any],
    backlog: dict[str, Any],
) -> dict[str, Any]:
    return {
        "schema_name": "ystar.mission_dashboard_refresh_loop.generated.refresh_cieu_event",
        "schema_version": "v0",
        "event_id": "refresh-cieu-event-001",
        "dry_run_only": True,
        "persistence_enabled": False,
        "refresh_loop_id": REFRESH_LOOP_ID,
        "Xt": {
            "previous_dashboard_snapshot_ref": PREVIOUS_REF,
            "current_observation_input_ref": CURRENT_REF,
            "latest_committed_milestone": dashboard.get("latest_committed_milestone"),
        },
        "U": "manual local deterministic mission dashboard refresh",
        "Y_star": "Refresh mission dashboard and backlog from governed read-only evidence without live execution.",
        "predicted_Y_t1": "Dashboard reflects L4.6 agent-team proposal bridge and recommends L4.8 recurring loop contract.",
        "predicted_R_t1": "Residual risk remains bounded by manual local execution and disabled scheduler, daemon, persistence, and writeback.",
        "actual_Y_t1": f"Refreshed dashboard produced with top backlog item: {backlog.get('top_item')}.",
        "actual_R_t1": "No real action, external action, scheduler, daemon, persistence, brain writeback, or memory ingestion occurred.",
        "residual_delta": {
            "status": "dry_run_refresh_delta_only",
            "state_change_level": delta.get("state_change_level"),
            "review_required": delta.get("requires_review"),
        },
        "evidence_refs": [
            CONTRACT_REF,
            PREVIOUS_REF,
            CURRENT_REF,
            REFRESHED_DASHBOARD_REF,
            DELTA_REF,
            BACKLOG_REF,
        ],
        "write_policy": {
            "persistence_allowed": False,
            "cieu_write_allowed": False,
            "brain_writeback_allowed": False,
            "memory_ingestion_allowed": False,
        },
        "learning_eligibility": False,
        "curation_required": True,
        "direct_brain_writeback_allowed": False,
        "direct_memory_ingestion_allowed": False,
        "raw_artifact_ingestion_allowed": False,
    }


def build_residual_delta(event: dict[str, Any]) -> dict[str, Any]:
    return {
        "schema_name": "ystar.mission_dashboard_refresh_loop.generated.refresh_residual_delta",
        "schema_version": "v0",
        "delta_id": "refresh-residual-delta-001",
        "event_id": event.get("event_id"),
        "predicted_vs_actual_summary": {
            "predicted": event.get("predicted_Y_t1"),
            "actual": event.get("actual_Y_t1"),
            "residual": event.get("actual_R_t1"),
        },
        "residual_delta": event.get("residual_delta"),
        "learning_eligibility": False,
        "curation_required": True,
        "direct_brain_writeback_allowed": False,
        "direct_memory_ingestion_allowed": False,
        "next_review_required": True,
        "notes": "Refresh delta is a dry-run fixture and requires curation before any future learning path.",
    }


def build_next_recommendations() -> dict[str, Any]:
    recommendations = [
        {
            "recommendation_id": "next-loop-001",
            "title": NEXT_MILESTONE,
            "recommended_owner_agent": "Ryan-Platform",
            "risk_tier": "low",
            "depends_on": [REFRESHED_DASHBOARD_REF, TRACE_REF],
            "requires_y_star_gov": True,
            "requires_operator_approval": False,
            "requires_cieu_event": True,
            "live_enabled": False,
            "external_action_enabled": False,
            "rationale": "Define recurrence boundaries before any scheduler or daemon can exist.",
        },
        {
            "recommendation_id": "next-loop-002",
            "title": "Dashboard refresh review packet fixture v0",
            "recommended_owner_agent": "Maya-Governance",
            "risk_tier": "low",
            "depends_on": [CIEU_EVENT_REF],
            "requires_y_star_gov": True,
            "requires_operator_approval": False,
            "requires_cieu_event": True,
            "live_enabled": False,
            "external_action_enabled": False,
            "rationale": "Prepares the governance review shape for future recurring refresh proposals.",
        },
        {
            "recommendation_id": "next-loop-003",
            "title": "Mission dashboard staleness indicator v0",
            "recommended_owner_agent": "Samantha-Secretary",
            "risk_tier": "low",
            "depends_on": [REFRESHED_DASHBOARD_REF],
            "requires_y_star_gov": True,
            "requires_operator_approval": False,
            "requires_cieu_event": True,
            "live_enabled": False,
            "external_action_enabled": False,
            "rationale": "Helps the agent team know when a future governed refresh is warranted.",
        },
    ]
    return {
        "schema_name": "ystar.mission_dashboard_refresh_loop.generated.next_loop_recommendations",
        "schema_version": "v0",
        "recommendation_count": len(recommendations),
        "recommendations": recommendations,
    }


def run_refresh_loop(output_dir: Path) -> dict[str, dict[str, Any]]:
    contract = load_json(ROOT / CONTRACT_REF)
    previous = load_json(ROOT / PREVIOUS_REF)
    current = load_json(ROOT / CURRENT_REF)

    dashboard = build_refreshed_dashboard(contract, previous, current)
    delta = build_company_state_delta(previous, current, dashboard)
    backlog = build_refreshed_backlog(dashboard, delta)
    trace = build_trace()
    event = build_refresh_event(dashboard, delta, backlog)
    residual = build_residual_delta(event)
    recommendations = build_next_recommendations()

    payloads = {
        "refreshed_mission_dashboard": dashboard,
        "company_state_delta": delta,
        "refreshed_autonomous_backlog": backlog,
        "refresh_loop_trace": trace,
        "refresh_cieu_event": event,
        "refresh_residual_delta": residual,
        "next_loop_recommendations": recommendations,
    }
    for name, payload in payloads.items():
        write_json(output_dir / f"{name}.json", payload)
    return payloads


def parse_args(argv: list[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Run L4.7 mission dashboard refresh loop.")
    parser.add_argument("--output-dir", required=True, help="Generated output directory")
    return parser.parse_args(argv)


def main(argv: list[str]) -> int:
    args = parse_args(argv)
    try:
        output_dir = output_dir_path(args.output_dir)
        output_dir.mkdir(parents=True, exist_ok=True)
        payloads = run_refresh_loop(output_dir)
        trace = payloads["refresh_loop_trace"]
        print("Mission dashboard refresh loop: PASS")
        print(f"runner_used: {trace.get('runner_used')}")
        print(f"scheduler_used: {trace.get('scheduler_used')}")
        print(f"daemon_used: {trace.get('daemon_used')}")
        return 0
    except Exception as exc:
        print(f"Mission dashboard refresh loop failed: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))

