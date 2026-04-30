#!/usr/bin/env python3
"""Progress records for delegated mission runs."""

from __future__ import annotations

from typing import Any

from .mission_model import base_packet, load_packets, now_id, now_iso, write_packet


def write_progress(
    mission_id: str,
    status: str,
    completed_tasks: list[str] | None = None,
    pending_tasks: list[str] | None = None,
    blocked_tasks: list[str] | None = None,
    escalation_count: int = 0,
    evidence_count: int = 0,
    current_summary: str = "",
) -> dict[str, Any]:
    progress_id = f"progress_{now_id()}"
    packet = {
        **base_packet("mission_progress_record"),
        "progress_id": progress_id,
        "mission_id": mission_id,
        "cycle_id": f"cycle_{now_id()}",
        "status": status,
        "completed_tasks": completed_tasks or [],
        "pending_tasks": pending_tasks or [],
        "blocked_tasks": blocked_tasks or [],
        "escalation_count": escalation_count,
        "evidence_count": evidence_count,
        "current_summary": current_summary,
        "created_at": now_iso(),
    }
    return write_packet("mission_progress", progress_id, packet)


def list_progress() -> list[dict[str, Any]]:
    return load_packets("mission_progress")

