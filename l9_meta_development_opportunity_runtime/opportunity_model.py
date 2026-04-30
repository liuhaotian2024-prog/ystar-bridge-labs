#!/usr/bin/env python3
"""Storage and shared model helpers for the L9 meta-development runtime."""

from __future__ import annotations

import json
import os
import time
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "l9_meta_development_opportunity_runtime"
PACKET_ROOT = OUT / "runtime_packets"
GENERATED_AT = "2026-04-30T00:00:00Z"
LOCAL_URL = "http://127.0.0.1:8765"

PACKET_DIRS = {
    "internal_asset_inventory": PACKET_ROOT / "internal_asset_inventory",
    "opportunity_candidates": PACKET_ROOT / "opportunity_candidates",
    "money_path_candidates": PACKET_ROOT / "money_path_candidates",
    "opportunity_rankings": PACKET_ROOT / "opportunity_rankings",
    "evidence_basis": PACKET_ROOT / "evidence_basis",
    "owner_decision_packets": PACKET_ROOT / "owner_decision_packets",
    "opportunity_review_decisions": PACKET_ROOT / "opportunity_review_decisions",
    "execution_plans": PACKET_ROOT / "execution_plans",
    "l8_bridge_packets": PACKET_ROOT / "l8_bridge_packets",
    "portfolio_feedback": PACKET_ROOT / "portfolio_feedback",
    "portfolio_residuals": PACKET_ROOT / "portfolio_residuals",
    "portfolio_learning_candidates": PACKET_ROOT / "portfolio_learning_candidates",
    "cockpit_snapshots": PACKET_ROOT / "cockpit_snapshots",
    "manifests": PACKET_ROOT / "manifests",
}

LENSES = [
    "shortest_cash",
    "strategic_long_term",
    "low_effort",
    "fastest_feedback",
    "productizable",
    "demo_value",
    "owner_leverage",
    "balanced",
]

FORBIDDEN_ACTIONS = [
    "automatic customer contact",
    "automatic email sending",
    "publication",
    "social posting",
    "form submission",
    "payment processing",
    "payment link creation",
    "account creation",
    "lead scraping",
    "mass outreach",
    "uncontrolled web search/crawl",
    "MCP/live behavior execution",
    "real memory/brain/canonical/CIEU DB writeback",
]

OWNER_GOAL = (
    "Build an AI agent company runtime that can discover opportunities, prepare commercial actions, "
    "collect feedback, learn safely, and make money."
)


def now_iso() -> str:
    return time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())


def now_id() -> str:
    return f"{time.strftime('%Y%m%dT%H%M%SZ', time.gmtime())}_{time.time_ns() % 1_000_000:06d}"


def safe_id(value: str) -> str:
    cleaned = "".join(ch if ch.isalnum() or ch in "-_" else "_" for ch in value.strip())[:110].strip("_")
    return cleaned or "packet"


def ensure_dirs() -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    for path in PACKET_DIRS.values():
        path.mkdir(parents=True, exist_ok=True)
        (path / ".gitkeep").write_text("local L9 runtime packet directory\n", encoding="utf-8")


def atomic_write_json(path: Path, data: Any) -> None:
    if not str(path.resolve()).startswith(str(OUT.resolve())):
        raise ValueError(f"Refusing L9 write outside package root: {path}")
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
    return [
        read_json(path, {})
        for path in sorted(PACKET_DIRS[kind].glob("*.json"))
        if path.name != ".gitkeep"
    ]


def get_packet(kind: str, packet_id: str) -> dict[str, Any] | None:
    path = PACKET_DIRS[kind] / f"{packet_id}.json"
    return read_json(path, None) if path.exists() else None


def latest_packet(kind: str) -> dict[str, Any] | None:
    packets = load_packets(kind)
    return packets[-1] if packets else None


def base_packet(packet_type: str) -> dict[str, Any]:
    return {
        "schema_version": "v0",
        "milestone_id": "L9.0",
        "packet_type": packet_type,
        "created_at": now_iso(),
        "external_side_effects": False,
        "customer_contact": False,
        "email_sent": False,
        "payment_processed": False,
        "publication": False,
        "core_writeback": False,
        "grant_rfp_path_created_by_default": False,
        "coo_invented": False,
    }


def no_action_receipt() -> dict[str, Any]:
    return {
        **base_packet("l9_no_action_receipt"),
        "automatic_customer_contact": False,
        "automatic_email_sending": False,
        "publication_occurred": False,
        "payment_processed": False,
        "account_creation_occurred": False,
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

