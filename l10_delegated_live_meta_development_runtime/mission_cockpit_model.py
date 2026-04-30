#!/usr/bin/env python3
"""Cockpit snapshots for the L10 delegated mission runtime."""

from __future__ import annotations

from typing import Any

from .action_plan_builder import list_action_plans
from .conflict_detector import list_conflict_reports
from .controlled_research_planner import list_research_plans
from .escalation_packet_builder import list_escalation_packets
from .escalation_review_center import list_escalation_review_decisions
from .evidence_packet_builder import list_evidence_packets
from .l8_action_loop_escalation_bridge import list_l8_action_loop_escalation_packets
from .l9_portfolio_update_bridge import list_l9_portfolio_update_packets
from .meta_strategy_brief_builder import list_meta_strategy_briefs
from .mission_completion_report import list_mission_completion_reports
from .mission_delegation_center import list_missions
from .mission_model import base_packet, latest_packet, load_packets, now_iso, write_packet
from .mission_plan_builder import list_mission_plans
from .mission_progress_ledger import list_progress
from .opportunity_signal_extractor import list_opportunity_signals
from .source_summary_builder import list_source_summaries


def build_mission_cockpit(snapshot_id: str = "l10_mission_cockpit_latest") -> dict[str, Any]:
    missions = list_missions()
    progress = list_progress()
    evidence = list_evidence_packets()
    signals = list_opportunity_signals()
    briefs = list_meta_strategy_briefs()
    escalations = list_escalation_packets()
    reports = list_mission_completion_reports()
    snapshot = {
        **base_packet("mission_cockpit_snapshot"),
        "snapshot_id": snapshot_id,
        "active_missions": [mission for mission in missions if mission.get("status") not in {"completed_local_bounded_run"}],
        "missions": missions,
        "mission_plans": list_mission_plans(),
        "mission_team_tasks": load_packets("mission_team_tasks"),
        "mission_progress": progress,
        "research_plans": list_research_plans(),
        "research_budget_status": load_packets("research_budget_receipts"),
        "evidence_count": len(evidence),
        "evidence_packets": evidence,
        "source_summaries": list_source_summaries(),
        "conflict_reports": list_conflict_reports(),
        "opportunity_signal_count": len(signals),
        "opportunity_signals": signals,
        "strategy_brief_status": "ready" if briefs else "not_ready",
        "meta_strategy_briefs": briefs,
        "action_plans": list_action_plans(),
        "escalation_queue": [item for item in escalations if item.get("status") == "waiting_for_owner_review"],
        "escalation_packets": escalations,
        "escalation_review_decisions": list_escalation_review_decisions(),
        "l9_portfolio_update_packets": list_l9_portfolio_update_packets(),
        "l8_action_loop_escalation_packets": list_l8_action_loop_escalation_packets(),
        "mission_completion_reports": reports,
        "next_owner_decision": _next_decision(missions, escalations, reports),
        "configured_live_read_only_research_available": False,
        "fixture_demo_available": True,
        "created_at": now_iso(),
    }
    return write_packet("cockpit_snapshots", snapshot_id, snapshot)


def current_mission_cockpit() -> dict[str, Any]:
    return latest_packet("cockpit_snapshots") or build_mission_cockpit()


def _next_decision(missions: list[dict[str, Any]], escalations: list[dict[str, Any]], reports: list[dict[str, Any]]) -> str:
    if not missions:
        return "create default meta-development mission"
    waiting = [item for item in escalations if item.get("status") == "waiting_for_owner_review"]
    if waiting:
        return "review escalation packet"
    if not reports:
        return "run bounded delegated mission"
    return "choose next mission or approve/revise a commercial escalation"

