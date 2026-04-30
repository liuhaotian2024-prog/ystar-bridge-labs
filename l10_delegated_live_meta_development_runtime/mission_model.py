#!/usr/bin/env python3
"""Shared storage/model helpers for the L10 delegated mission runtime."""

from __future__ import annotations

import json
import os
import time
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "l10_delegated_live_meta_development_runtime"
PACKET_ROOT = OUT / "runtime_packets"
GENERATED_AT = "2026-04-30T00:00:00Z"

PACKET_DIRS = {
    "missions": PACKET_ROOT / "missions",
    "mission_plans": PACKET_ROOT / "mission_plans",
    "mission_team_tasks": PACKET_ROOT / "mission_team_tasks",
    "mission_cycles": PACKET_ROOT / "mission_cycles",
    "research_plans": PACKET_ROOT / "research_plans",
    "research_budget_receipts": PACKET_ROOT / "research_budget_receipts",
    "research_evidence_packets": PACKET_ROOT / "research_evidence_packets",
    "source_summaries": PACKET_ROOT / "source_summaries",
    "conflict_reports": PACKET_ROOT / "conflict_reports",
    "opportunity_signals": PACKET_ROOT / "opportunity_signals",
    "meta_strategy_briefs": PACKET_ROOT / "meta_strategy_briefs",
    "action_plans": PACKET_ROOT / "action_plans",
    "escalation_packets": PACKET_ROOT / "escalation_packets",
    "escalation_review_decisions": PACKET_ROOT / "escalation_review_decisions",
    "l9_portfolio_update_packets": PACKET_ROOT / "l9_portfolio_update_packets",
    "l8_action_loop_escalation_packets": PACKET_ROOT / "l8_action_loop_escalation_packets",
    "mission_progress": PACKET_ROOT / "mission_progress",
    "mission_completion_reports": PACKET_ROOT / "mission_completion_reports",
    "cockpit_snapshots": PACKET_ROOT / "cockpit_snapshots",
    "manifests": PACKET_ROOT / "manifests",
}

LEGACY_AGENT_IDS = {
    "haotian_board_founder",
    "aiden_ceo",
    "ethan_cto",
    "sofia_cmo",
    "marco_cfo",
    "zara_cso",
    "samantha_secretary",
    "leo_engineer",
    "maya_engineer",
    "ryan_engineer",
    "jordan_engineer",
    "jinjin_k9_scout",
}

DEFAULT_MISSION_TITLE = "Research and formulate the next 30-day meta-development plan for Y*Bridge Labs"
DEFAULT_OWNER_GOAL = (
    "Research and formulate the next 30-day meta-development plan for Y*Bridge Labs "
    "to maximize the chance of first revenue without locking the company to one offer."
)

FORBIDDEN_ACTION_CLASSES = [
    "customer_contact",
    "email_send",
    "publication",
    "form_submission",
    "payment",
    "account_creation",
    "grant_rfp_submission",
    "mcp_live_behavior",
    "core_writeback",
    "external_repo_modification",
    "secret_or_env_read",
    "db_wal_shm_log_active_agent_content_read",
]


def now_iso() -> str:
    return time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())


def now_id() -> str:
    return f"{time.strftime('%Y%m%dT%H%M%SZ', time.gmtime())}_{time.time_ns() % 1_000_000:06d}"


def safe_id(value: str) -> str:
    cleaned = "".join(ch if ch.isalnum() or ch in "-_" else "_" for ch in value.strip())[:120].strip("_")
    return cleaned or "packet"


def ensure_dirs() -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    for path in PACKET_DIRS.values():
        path.mkdir(parents=True, exist_ok=True)
        (path / ".gitkeep").write_text("local L10 runtime packet directory\n", encoding="utf-8")


def atomic_write_json(path: Path, data: Any) -> None:
    if not str(path.resolve()).startswith(str(OUT.resolve())):
        raise ValueError(f"Refusing L10 write outside package root: {path}")
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_suffix(path.suffix + ".tmp")
    tmp.write_text(json.dumps(data, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    os.replace(tmp, path)


def read_json(path: Path, default: Any) -> Any:
    if not path.exists():
        return default
    return json.loads(path.read_text(encoding="utf-8"))


def write_packet(kind: str, packet_id: str, packet: dict[str, Any]) -> dict[str, Any]:
    ensure_dirs()
    atomic_write_json(PACKET_DIRS[kind] / f"{packet_id}.json", packet)
    return packet


def load_packets(kind: str) -> list[dict[str, Any]]:
    ensure_dirs()
    return [read_json(path, {}) for path in sorted(PACKET_DIRS[kind].glob("*.json")) if path.name != ".gitkeep"]


def get_packet(kind: str, packet_id: str) -> dict[str, Any] | None:
    path = PACKET_DIRS[kind] / f"{packet_id}.json"
    return read_json(path, None) if path.exists() else None


def latest_packet(kind: str) -> dict[str, Any] | None:
    packets = load_packets(kind)
    return packets[-1] if packets else None


def base_packet(packet_type: str) -> dict[str, Any]:
    return {
        "schema_version": "v0",
        "milestone_id": "L10.0",
        "packet_type": packet_type,
        "created_at": now_iso(),
        "external_side_effects": False,
        "customer_contact": False,
        "email_sent": False,
        "payment_processed": False,
        "publication": False,
        "uncontrolled_web_research": False,
        "grant_rfp_path_created_by_default": False,
        "core_writeback": False,
        "coo_invented": False,
    }


def no_action_receipt() -> dict[str, Any]:
    return {
        **base_packet("l10_no_action_receipt"),
        "automatic_customer_contact": False,
        "automatic_email_sending": False,
        "form_submission_occurred": False,
        "publication_occurred": False,
        "payment_processed": False,
        "account_creation_occurred": False,
        "grant_rfp_workflow_created_by_default": False,
        "lead_scraping_occurred": False,
        "mass_outreach_occurred": False,
        "uncontrolled_web_search_crawl_occurred": False,
        "mcp_live_behavior_occurred": False,
        "real_memory_brain_canonical_cieu_db_writeback": False,
        "y_star_gov_modified": False,
        "gov_mcp_modified": False,
        "ystar_bridge_labs_modified": False,
        "secret_env_file_read": False,
        "db_wal_shm_log_active_agent_marker_content_read": False,
    }

