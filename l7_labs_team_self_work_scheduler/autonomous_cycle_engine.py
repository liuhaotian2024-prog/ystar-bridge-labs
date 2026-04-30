#!/usr/bin/env python3
"""Bounded autonomous internal cycle engine for L7.6."""

from __future__ import annotations

import sys
from pathlib import Path
from typing import Any

from .capability_classifier import classify_work_item
from .completion_aggregator import aggregate_completion
from .progress_ledger import write_autonomous_run, write_progress_heartbeat, write_scheduler_tick


ROOT = Path(__file__).resolve().parents[1]
OFFICE_WEB_DIR = ROOT / "scripts/l7_labs_office_web"
if str(OFFICE_WEB_DIR) not in sys.path:
    sys.path.insert(0, str(OFFICE_WEB_DIR))

from agent_worker_runtime import auditor_boundary_reply, generate_agent_reply  # noqa: E402
from team_router import route_owner_goal  # noqa: E402
from whiteboard_store import PACKET_ROOT, create_agent_reply, save_work_item  # noqa: E402


def _assigned_agents_for(item: dict[str, Any]) -> list[str]:
    existing = [agent for agent in item.get("assigned_agents", []) if agent]
    if existing:
        return existing
    routing = route_owner_goal(item.get("description") or item.get("title", ""), "whole_team")
    assigned = [routing["primary_agent"], *routing.get("supporting_agents", [])]
    return list(dict.fromkeys(assigned))


def run_autonomous_internal_cycles(
    work_item: dict[str, Any],
    max_cycles: int = 2,
    max_agent_replies_per_cycle: int = 8,
    packet_root: Path = PACKET_ROOT,
) -> dict[str, Any]:
    decision = classify_work_item(work_item)
    if decision["classification"] != "autonomous_internal_allowed":
        raise ValueError(f"Work item is not autonomous-internal eligible: {decision['classification']}")

    assigned_agents = _assigned_agents_for(work_item)
    work_item["assigned_agents"] = assigned_agents
    work_item["status"] = "In Progress"
    work_item.setdefault("progress_notes", []).append("L7.6 autonomous scheduler started bounded internal work.")
    save_work_item(work_item, packet_root)

    ticks: list[dict[str, Any]] = []
    heartbeats: list[dict[str, Any]] = []
    replies: list[dict[str, Any]] = []
    cycles_run = 0
    for cycle_index in range(1, max_cycles + 1):
        cycles_run += 1
        ticks.append(
            write_scheduler_tick(
                {
                    "work_item_id": work_item["work_item_id"],
                    "cycle_index": cycle_index,
                    "summary": f"Running bounded internal cycle {cycle_index} for {work_item['title']}",
                    "policy_decision": decision,
                    "status": "running",
                },
                packet_root,
            )
        )
        heartbeats.append(
            write_progress_heartbeat(
                {
                    "work_item_id": work_item["work_item_id"],
                    "cycle_index": cycle_index,
                    "summary": "Agents are producing local role-specific replies.",
                    "assigned_agents": assigned_agents,
                    "status": "running",
                },
                packet_root,
            )
        )
        reply_agents = assigned_agents[: max(1, max_agent_replies_per_cycle - 1)]
        if "samantha_secretary" not in reply_agents and len(reply_agents) < max_agent_replies_per_cycle:
            reply_agents.append("samantha_secretary")
        for agent_id in list(dict.fromkeys(reply_agents))[:max_agent_replies_per_cycle]:
            replies.append(create_agent_reply(generate_agent_reply(agent_id, work_item), packet_root))
        if len(replies) < max_agent_replies_per_cycle:
            replies.append(create_agent_reply(auditor_boundary_reply(work_item), packet_root))
        work_item.setdefault("progress_notes", []).append(
            f"L7.6 cycle {cycle_index}: generated {len(reply_agents)} agent replies and one safety review if capacity allowed."
        )
        save_work_item(work_item, packet_root)

    work_item["status"] = "Done"
    work_item.setdefault("progress_notes", []).append("L7.6 autonomous scheduler finished within bounded cycle limit.")
    save_work_item(work_item, packet_root)
    completion = aggregate_completion(work_item, packet_root)
    autonomous_run = write_autonomous_run(
        {
            "work_item_id": work_item["work_item_id"],
            "cycles_run": cycles_run,
            "cycle_limit": max_cycles,
            "agent_replies_created": [reply["reply_id"] for reply in replies],
            "progress_heartbeats_created": [heartbeat["heartbeat_id"] for heartbeat in heartbeats],
            "scheduler_ticks_created": [tick["scheduler_tick_id"] for tick in ticks],
            "completion_report_id": completion["completion_report_id"],
            "summary": f"Completed bounded local self-work for {work_item['title']}",
            "stop_reason": "cycle_limit_reached_or_work_completed",
            "external_side_effects_occurred": False,
            "core_writeback_occurred": False,
        },
        packet_root,
    )
    return {
        "ok": True,
        "work_item": work_item,
        "policy_decision": decision,
        "cycles_run": cycles_run,
        "scheduler_ticks": ticks,
        "progress_heartbeats": heartbeats,
        "agent_replies": replies,
        "completion_report": completion,
        "autonomous_run": autonomous_run,
        "approval_interrupt": None,
    }

