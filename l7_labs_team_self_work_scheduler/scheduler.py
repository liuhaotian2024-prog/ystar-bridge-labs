#!/usr/bin/env python3
"""L7.6 local Labs team self-work scheduler."""

from __future__ import annotations

import sys
from pathlib import Path
from typing import Any

from .approval_interrupts import create_approval_interrupt
from .autonomous_cycle_engine import run_autonomous_internal_cycles
from .capability_classifier import classify_work_item
from .progress_ledger import (
    ensure_scheduler_dirs,
    load_approval_interrupts,
    load_autonomous_runs,
    load_progress_heartbeats,
    load_scheduler_ticks,
    write_scheduler_tick,
)
from .work_item_loader import classify_pending_items, pending_work_items, select_eligible_work_items


ROOT = Path(__file__).resolve().parents[1]
OFFICE_WEB_DIR = ROOT / "scripts/l7_labs_office_web"
if str(OFFICE_WEB_DIR) not in sys.path:
    sys.path.insert(0, str(OFFICE_WEB_DIR))

from whiteboard_store import PACKET_ROOT, create_work_item  # noqa: E402


DEMO_TITLE = "Improve first-cash-path offer package"
DEMO_DESCRIPTION = (
    "Team autonomously improves the first-cash-path Founder AI Workflow Audit & CEO Command Brief Sprint package. "
    "Refine the internal offer package, compare customer segments, improve delivery workflow, and produce an owner review packet. "
    "Do not send email, contact customers, publish, request payment, or perform writeback."
)


def scheduler_status(packet_root: Path = PACKET_ROOT) -> dict[str, Any]:
    ensure_scheduler_dirs(packet_root)
    classified = classify_pending_items(packet_root)
    eligible = [entry for entry in classified if entry["classification"]["classification"] == "autonomous_internal_allowed"]
    interrupts = load_approval_interrupts(packet_root)
    ticks = load_scheduler_ticks(packet_root)
    heartbeats = load_progress_heartbeats(packet_root)
    runs = load_autonomous_runs(packet_root)
    return {
        "schema_version": "v0",
        "milestone_id": "L7.6",
        "scheduler_ready": True,
        "pending_work_items": len(classified),
        "eligible_autonomous_work_items": len(eligible),
        "active_approval_interrupts": len([item for item in interrupts if item.get("status") == "waiting_for_owner"]),
        "autonomous_runs": len(runs),
        "progress_heartbeats": len(heartbeats),
        "scheduler_ticks": len(ticks),
        "last_scheduler_tick": ticks[-1] if ticks else None,
        "last_autonomous_run": runs[-1] if runs else None,
        "classified_pending_work": classified,
        "no_external_side_effects": True,
        "no_core_writeback": True,
        "coo_invented": False,
    }


def create_demo_work_item(packet_root: Path = PACKET_ROOT) -> dict[str, Any]:
    existing = [
        item
        for item in pending_work_items(packet_root)
        if item.get("title") == DEMO_TITLE or "first-cash-path" in item.get("title", "").lower()
    ]
    if existing:
        return existing[0]
    return create_work_item(DEMO_TITLE, DEMO_DESCRIPTION, None, assigned_agents=[], status="Inbox", packet_root=packet_root)


def run_once(
    packet_root: Path = PACKET_ROOT,
    max_cycles: int = 1,
    max_agent_replies_per_cycle: int = 8,
) -> dict[str, Any]:
    ensure_scheduler_dirs(packet_root)
    eligible = select_eligible_work_items(packet_root, limit=1)
    if eligible:
        return run_autonomous_internal_cycles(eligible[0], max_cycles=max_cycles, max_agent_replies_per_cycle=max_agent_replies_per_cycle, packet_root=packet_root)
    pending = pending_work_items(packet_root)
    if pending:
        item = pending[0]
        decision = classify_work_item(item)
        if decision["approval_required"] or decision["classification"] in {"approval_required_external_action", "approval_required_core_writeback", "blocked_unsafe"}:
            interrupt = create_approval_interrupt(item, decision, packet_root)
            tick = write_scheduler_tick(
                {
                    "work_item_id": item["work_item_id"],
                    "summary": f"Scheduler stopped for approval/security boundary: {item['title']}",
                    "policy_decision": decision,
                    "status": "interrupted",
                },
                packet_root,
            )
            return {"ok": True, "status": "interrupted", "scheduler_tick": tick, "approval_interrupt": interrupt, "policy_decision": decision}
    tick = write_scheduler_tick(
        {
            "summary": "No eligible autonomous internal work item exists.",
            "status": "no_eligible_action",
            "policy_decision": {"classification": "no_eligible_action"},
        },
        packet_root,
    )
    return {"ok": True, "status": "no_eligible_action", "scheduler_tick": tick}


def run_bounded(
    packet_root: Path = PACKET_ROOT,
    max_work_items: int = 3,
    max_cycles: int = 2,
    max_agent_replies_per_cycle: int = 8,
) -> dict[str, Any]:
    ensure_scheduler_dirs(packet_root)
    results = []
    items_processed = 0
    for item in select_eligible_work_items(packet_root, limit=max_work_items):
        results.append(
            run_autonomous_internal_cycles(
                item,
                max_cycles=max_cycles,
                max_agent_replies_per_cycle=max_agent_replies_per_cycle,
                packet_root=packet_root,
            )
        )
        items_processed += 1
    if results:
        return {
            "ok": True,
            "status": "completed",
            "items_processed": items_processed,
            "results": results,
            "cycle_limit": max_cycles,
            "max_work_items": max_work_items,
            "external_side_effects_occurred": False,
            "core_writeback_occurred": False,
        }
    return run_once(packet_root=packet_root, max_cycles=max_cycles, max_agent_replies_per_cycle=max_agent_replies_per_cycle)

