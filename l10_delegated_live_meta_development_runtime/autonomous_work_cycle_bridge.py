#!/usr/bin/env python3
"""Bridge L10 missions to bounded local work-cycle records."""

from __future__ import annotations

from typing import Any

from .mission_model import base_packet, now_id, now_iso, write_packet
from .mission_progress_ledger import write_progress


def run_internal_mission_cycle(mission_id: str, max_cycles: int = 1) -> dict[str, Any]:
    cycle_id = f"mission_cycle_{now_id()}"
    packet = {
        **base_packet("mission_cycle"),
        "cycle_id": cycle_id,
        "mission_id": mission_id,
        "max_cycles": max_cycles,
        "cycles_executed": min(max_cycles, 1),
        "actions_taken": ["review mission plan", "update progress ledger", "prepare research/evidence step"],
        "stop_reason": "cycle_limit_reached" if max_cycles <= 1 else "ready_for_next_step",
        "created_at": now_iso(),
    }
    write_packet("mission_cycles", cycle_id, packet)
    progress = write_progress(mission_id, "cycle_completed", current_summary="Bounded internal mission cycle completed.")
    return {"ok": True, "mission_cycle": packet, "progress": progress}

