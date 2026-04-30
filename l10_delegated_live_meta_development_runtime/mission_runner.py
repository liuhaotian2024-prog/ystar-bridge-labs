#!/usr/bin/env python3
"""Bounded delegated mission runner."""

from __future__ import annotations

from typing import Any

from .action_plan_builder import build_action_plan
from .autonomous_work_cycle_bridge import run_internal_mission_cycle
from .conflict_detector import build_conflict_report
from .controlled_research_executor import run_fixture_research_demo
from .controlled_research_planner import build_research_plan
from .escalation_packet_builder import build_escalation_packets
from .l8_action_loop_escalation_bridge import build_l8_action_loop_escalation_packet
from .l9_portfolio_update_bridge import build_l9_portfolio_update_packet
from .meta_strategy_brief_builder import build_meta_strategy_brief
from .mission_completion_report import build_mission_completion_report
from .mission_delegation_center import get_mission, update_mission_status
from .mission_model import FORBIDDEN_ACTION_CLASSES
from .mission_plan_builder import build_mission_plan
from .mission_progress_ledger import write_progress
from .opportunity_signal_extractor import extract_opportunity_signals
from .source_summary_builder import build_source_summary


def run_mission_cycle(mission_id: str | None = None, max_cycles: int = 1) -> dict[str, Any]:
    mission = get_mission(mission_id)
    if max_cycles < 1:
        return {"ok": False, "stopped_reason": "cycle_limit_reached", "mission_id": mission["mission_id"]}
    return run_internal_mission_cycle(mission["mission_id"], max_cycles=max_cycles)


def run_bounded_mission(mission_id: str | None = None, max_cycles: int = 2, fixture_research: bool = True) -> dict[str, Any]:
    mission = get_mission(mission_id)
    if _requests_forbidden_action(mission):
        progress = write_progress(mission["mission_id"], "blocked", blocked_tasks=["forbidden_action_requested"], current_summary="Mission requested a forbidden action class.")
        return {"ok": False, "stopped_reason": "forbidden_action_requested", "progress": progress}
    plan = build_mission_plan(mission["mission_id"])
    cycle = run_internal_mission_cycle(mission["mission_id"], max_cycles=max_cycles)
    research_plan = build_research_plan(mission["mission_id"])
    research = run_fixture_research_demo(mission["mission_id"]) if fixture_research else {"evidence_packets": []}
    summary = build_source_summary(mission["mission_id"])
    conflict = build_conflict_report(mission["mission_id"])
    signals = extract_opportunity_signals(mission["mission_id"])
    brief = build_meta_strategy_brief(mission["mission_id"])
    action_plan = build_action_plan(mission["mission_id"])
    escalations = build_escalation_packets(mission["mission_id"])
    l9_update = build_l9_portfolio_update_packet(mission["mission_id"])
    l8_escalation = build_l8_action_loop_escalation_packet(mission["mission_id"])
    report = build_mission_completion_report(mission["mission_id"])
    update_mission_status(mission["mission_id"], "completed_local_bounded_run")
    progress = write_progress(
        mission["mission_id"],
        "mission_complete",
        completed_tasks=[task for task in plan["workstreams"]],
        escalation_count=len(escalations),
        evidence_count=len(research.get("evidence_packets", [])),
        current_summary="Delegated mission completed locally with fixture-safe evidence and approval escalation packets.",
    )
    return {
        "ok": True,
        "mission": mission,
        "mission_plan": plan,
        "mission_cycle": cycle,
        "research_plan": research_plan,
        "research": research,
        "source_summary": summary,
        "conflict_report": conflict,
        "opportunity_signals": signals,
        "meta_strategy_brief": brief,
        "action_plan": action_plan,
        "escalation_packets": escalations,
        "l9_portfolio_update_packet": l9_update,
        "l8_action_loop_escalation_packet": l8_escalation,
        "mission_completion_report": report,
        "progress": progress,
        "stop_reason": "mission_complete",
    }


def _requests_forbidden_action(mission: dict[str, Any]) -> bool:
    text = f"{mission.get('title','')} {mission.get('owner_goal','')}".lower()
    return any(action.replace("_", " ") in text for action in FORBIDDEN_ACTION_CLASSES)

