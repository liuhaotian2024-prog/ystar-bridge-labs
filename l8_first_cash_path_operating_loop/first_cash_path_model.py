#!/usr/bin/env python3
"""Core local models and packet storage for the L8 first cash path loop."""

from __future__ import annotations

import json
import os
import time
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "l8_first_cash_path_operating_loop"
PACKET_ROOT = OUT / "runtime_packets"
GENERATED_AT = "2026-04-30T00:00:00Z"
LOCAL_URL = "http://127.0.0.1:8765"

PACKET_DIRS = {
    "first_cash_paths": PACKET_ROOT / "first_cash_paths",
    "commercial_action_queue": PACKET_ROOT / "commercial_action_queue",
    "owner_approval_decisions": PACKET_ROOT / "owner_approval_decisions",
    "manual_send_packets": PACKET_ROOT / "manual_send_packets",
    "manual_action_receipts": PACKET_ROOT / "manual_action_receipts",
    "customer_feedback": PACKET_ROOT / "customer_feedback",
    "commercial_residuals": PACKET_ROOT / "commercial_residuals",
    "learning_candidates": PACKET_ROOT / "learning_candidates",
    "cockpit_snapshots": PACKET_ROOT / "cockpit_snapshots",
    "manifests": PACKET_ROOT / "manifests",
}

FORBIDDEN_ACTIONS = [
    "automatic customer contact",
    "automatic email sending",
    "publication",
    "social posting",
    "form submission",
    "payment",
    "account creation",
    "lead scraping",
    "mass outreach",
    "grant/RFP application",
    "MCP/live behavior execution",
    "real memory/brain/canonical/CIEU DB writeback",
]

SELECTED_CASH_PATH_ID = "first_cash_path_founder_ai_workflow_audit_ceo_brief"
SELECTED_OFFER = "Founder AI Workflow Audit & CEO Command Brief Sprint"
TARGET_CUSTOMER_PROFILE = (
    "AI startup founder, technical operator, or small AI/product team with an urgent workflow, strategy, "
    "agent-runtime, research, governance, or execution bottleneck."
)


def now_iso() -> str:
    return time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())


def now_id() -> str:
    return f"{time.strftime('%Y%m%dT%H%M%SZ', time.gmtime())}_{time.time_ns() % 1_000_000:06d}"


def safe_id(value: str) -> str:
    cleaned = "".join(ch if ch.isalnum() or ch in "-_" else "_" for ch in value.strip())[:96].strip("_")
    return cleaned or "packet"


def ensure_dirs() -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    for path in PACKET_DIRS.values():
        path.mkdir(parents=True, exist_ok=True)
        (path / ".gitkeep").write_text("local L8 runtime packet directory\n", encoding="utf-8")


def atomic_write_json(path: Path, data: Any) -> None:
    if not str(path.resolve()).startswith(str(OUT.resolve())):
        raise ValueError(f"Refusing L8 write outside package root: {path}")
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
    path = PACKET_DIRS[kind] / f"{packet_id}.json"
    atomic_write_json(path, packet)
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
        "milestone_id": "L8.0",
        "packet_type": packet_type,
        "created_at": now_iso(),
        "external_side_effects": False,
        "core_writeback": False,
        "grant_rfp_path_created_by_default": False,
        "coo_invented": False,
    }


def default_first_cash_path() -> dict[str, Any]:
    return {
        **base_packet("first_cash_path"),
        "cash_path_id": SELECTED_CASH_PATH_ID,
        "title": "First Cash Path: Founder AI Workflow Audit & CEO Command Brief Sprint",
        "selected_offer": SELECTED_OFFER,
        "target_customer_profile": TARGET_CUSTOMER_PROFILE,
        "current_stage": "commercial_package_prepared_for_owner_approval",
        "pricing_hypothesis": {
            "low_test_price_usd": 750,
            "mid_test_price_usd": 1500,
            "high_test_price_usd": 3000,
            "recommended_first_test_usd": 1500,
        },
        "delivery_promise": (
            "A done-for-you governed observation, workflow audit, and CEO command brief that helps an AI "
            "founder/operator understand execution bottlenecks, decision risk, agent workflow weakness, and next actions."
        ),
        "evidence_basis": [
            "L7.2 selected path_001 as the primary shortest cash path.",
            "L7.3 produced approval-ready offer validation and delivery workflow artifacts.",
            "L7.4/L7.5/L7.6 created the local office, whiteboard, and bounded self-work scheduler.",
        ],
        "owner_decision_needed": "Choose whether to approve one manual-send commercial action packet.",
        "next_recommended_action": "Build commercial action queue, review owner approval center, and approve/reject/hold one action.",
        "status": "initialized",
        "forbidden_current_routes": ["grant/RFP default route", "automatic lead scraping", "automatic outreach send"],
    }


def no_action_receipt() -> dict[str, Any]:
    return {
        **base_packet("l8_no_action_receipt"),
        "customer_contacted": False,
        "email_sent": False,
        "publication_occurred": False,
        "payment_occurred": False,
        "form_submission_occurred": False,
        "account_creation_occurred": False,
        "grant_rfp_path_created_by_default": False,
        "grant_rfp_application_occurred": False,
        "mcp_live_behavior_occurred": False,
        "core_writeback_occurred": False,
        "y_star_gov_modified": False,
        "gov_mcp_modified": False,
        "ystar_bridge_labs_modified": False,
        "secret_env_file_read": False,
        "db_wal_shm_log_active_agent_marker_content_read": False,
    }

