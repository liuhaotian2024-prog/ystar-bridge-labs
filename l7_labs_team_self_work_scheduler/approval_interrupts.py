#!/usr/bin/env python3
"""Approval interruption packets for scheduler-stopped work items."""

from __future__ import annotations

import sys
from pathlib import Path
from typing import Any

from .progress_ledger import base_packet, ensure_scheduler_dirs


ROOT = Path(__file__).resolve().parents[1]
OFFICE_WEB_DIR = ROOT / "scripts/l7_labs_office_web"
if str(OFFICE_WEB_DIR) not in sys.path:
    sys.path.insert(0, str(OFFICE_WEB_DIR))

from whiteboard_store import PACKET_ROOT, append_timeline, atomic_write_json, create_approval_request, now_id, save_work_item  # noqa: E402


def create_approval_interrupt(
    work_item: dict[str, Any],
    policy_decision: dict[str, Any],
    packet_root: Path = PACKET_ROOT,
) -> dict[str, Any]:
    ensure_scheduler_dirs(packet_root)
    interrupt_id = f"approval_interrupt_{now_id()}"
    reason = policy_decision.get("owner_visible_explanation", "Owner approval is required before this action.")
    work_item["status"] = "Waiting for Approval"
    work_item.setdefault("blockers", []).append(reason)
    save_work_item(work_item, packet_root)
    approval_request = create_approval_request(work_item, reason, packet_root)
    interrupt = {
        **base_packet("approval_interrupt"),
        "approval_interrupt_id": interrupt_id,
        "work_item_id": work_item["work_item_id"],
        "classification": policy_decision.get("classification"),
        "reason_codes": policy_decision.get("reason_codes", []),
        "owner_visible_explanation": reason,
        "approval_request_id": approval_request["approval_request_id"],
        "status": "waiting_for_owner",
        "scheduler_stopped": True,
        "external_side_effects_executed": False,
        "core_writeback_executed": False,
    }
    atomic_write_json(packet_root / "approval_interrupts" / f"{interrupt_id}.json", interrupt)
    append_timeline("approval interruption", reason, {"approval_interrupt_id": interrupt_id, "work_item_id": work_item["work_item_id"]}, packet_root)
    return interrupt

