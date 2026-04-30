#!/usr/bin/env python3
"""Local packet ledger for L7.6 scheduler runs and progress heartbeats."""

from __future__ import annotations

import sys
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
OFFICE_WEB_DIR = ROOT / "scripts/l7_labs_office_web"
if str(OFFICE_WEB_DIR) not in sys.path:
    sys.path.insert(0, str(OFFICE_WEB_DIR))

from whiteboard_store import PACKET_ROOT, append_timeline, atomic_write_json, ensure_dirs, now_id, now_iso, read_json  # noqa: E402


SCHEDULER_DIRS = [
    "autonomous_runs",
    "scheduler_ticks",
    "progress_heartbeats",
    "approval_interrupts",
]


def ensure_scheduler_dirs(packet_root: Path = PACKET_ROOT) -> None:
    ensure_dirs(packet_root)
    for relative in SCHEDULER_DIRS:
        path = packet_root / relative
        path.mkdir(parents=True, exist_ok=True)
        (path / ".gitkeep").write_text("local runtime packet directory\n", encoding="utf-8")


def base_packet(packet_type: str) -> dict[str, Any]:
    return {
        "schema_version": "v0",
        "milestone_id": "L7.6",
        "packet_type": packet_type,
        "created_at_utc": now_iso(),
        "external_side_effects": False,
        "core_writeback": False,
    }


def write_scheduler_tick(data: dict[str, Any], packet_root: Path = PACKET_ROOT) -> dict[str, Any]:
    ensure_scheduler_dirs(packet_root)
    tick_id = f"scheduler_tick_{now_id()}"
    packet = {**base_packet("scheduler_tick"), "scheduler_tick_id": tick_id, **data}
    atomic_write_json(packet_root / "scheduler_ticks" / f"{tick_id}.json", packet)
    append_timeline("scheduler tick", packet.get("summary", "Scheduler tick recorded."), {"scheduler_tick_id": tick_id}, packet_root)
    return packet


def write_progress_heartbeat(data: dict[str, Any], packet_root: Path = PACKET_ROOT) -> dict[str, Any]:
    ensure_scheduler_dirs(packet_root)
    heartbeat_id = f"heartbeat_{now_id()}"
    packet = {**base_packet("progress_heartbeat"), "heartbeat_id": heartbeat_id, **data}
    atomic_write_json(packet_root / "progress_heartbeats" / f"{heartbeat_id}.json", packet)
    append_timeline("progress heartbeat", packet.get("summary", "Progress heartbeat recorded."), {"heartbeat_id": heartbeat_id}, packet_root)
    return packet


def write_autonomous_run(data: dict[str, Any], packet_root: Path = PACKET_ROOT) -> dict[str, Any]:
    ensure_scheduler_dirs(packet_root)
    run_id = data.get("autonomous_run_id") or f"autonomous_run_{now_id()}"
    packet = {**base_packet("autonomous_run"), "autonomous_run_id": run_id, **data}
    atomic_write_json(packet_root / "autonomous_runs" / f"{run_id}.json", packet)
    append_timeline("autonomous run completed", packet.get("summary", "Autonomous run completed."), {"autonomous_run_id": run_id}, packet_root)
    return packet


def load_packets(kind: str, packet_root: Path = PACKET_ROOT) -> list[dict[str, Any]]:
    ensure_scheduler_dirs(packet_root)
    return [
        read_json(path, {})
        for path in sorted((packet_root / kind).glob("*.json"))
        if path.name != ".gitkeep"
    ]


def load_scheduler_ticks(packet_root: Path = PACKET_ROOT) -> list[dict[str, Any]]:
    return load_packets("scheduler_ticks", packet_root)


def load_progress_heartbeats(packet_root: Path = PACKET_ROOT) -> list[dict[str, Any]]:
    return load_packets("progress_heartbeats", packet_root)


def load_autonomous_runs(packet_root: Path = PACKET_ROOT) -> list[dict[str, Any]]:
    return load_packets("autonomous_runs", packet_root)


def load_approval_interrupts(packet_root: Path = PACKET_ROOT) -> list[dict[str, Any]]:
    return load_packets("approval_interrupts", packet_root)

