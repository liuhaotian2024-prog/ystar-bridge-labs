#!/usr/bin/env python3
"""Shared helpers for the L7.4 first revenue readiness lane builders."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[2]
GENERATED_AT = "2026-04-30T00:00:00Z"
RUN_ID = "l7_4_parallel_first_revenue_readiness_run_001"

POLICY_REFS = {
    "policy_ref": "policy/action_capability_registry.json",
    "revenue_policy_ref": "policy/revenue_action_policy.json",
    "discovery_policy_ref": "policy/discovery_policy.json",
    "approval_state_machine_ref": "policy/approval_state_machine.json",
    "writeback_policy_ref": "policy/writeback_policy.json",
    "secret_scanning_policy_ref": "policy/secret_scanning_policy.json",
}


def packet(packet_type: str, lane_id: str | None = None) -> dict[str, Any]:
    data: dict[str, Any] = {
        "schema_version": "v0",
        "milestone_id": "L7.4",
        "milestone_name": "Parallel First Revenue Readiness Sprint",
        "run_id": RUN_ID,
        "packet_type": packet_type,
        "generated_at_utc": GENERATED_AT,
        **POLICY_REFS,
    }
    if lane_id:
        data["lane_id"] = lane_id
    return data


def load_json(relative_path: str, default: Any) -> Any:
    path = ROOT / relative_path
    if not path.exists():
        return default
    return json.loads(path.read_text(encoding="utf-8"))


def write_json(relative_path: str, data: Any) -> None:
    path = ROOT / relative_path
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


def write_md(relative_path: str, text: str) -> None:
    path = ROOT / relative_path
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text.strip() + "\n", encoding="utf-8")


def bullets(items: list[str]) -> str:
    return "\n".join(f"- {item}" for item in items)


def no_action_receipt(packet_type: str, lane_id: str) -> dict[str, Any]:
    return {
        **packet(packet_type, lane_id),
        "ask_user_url_occurred": False,
        "external_side_effects_occurred": False,
        "outreach_occurred": False,
        "email_sent_occurred": False,
        "form_submission_occurred": False,
        "publication_occurred": False,
        "payment_occurred": False,
        "account_creation_occurred": False,
        "customer_contact_occurred": False,
        "grant_rfp_submission_occurred": False,
        "mcp_live_behavior_occurred": False,
        "actual_memory_brain_canonical_cieu_db_writeback_occurred": False,
        "secret_printed_stored_in_repo_occurred": False,
        "y_star_gov_modification_occurred": False,
        "gov_mcp_modification_occurred": False,
        "db_log_wal_shm_active_agent_marker_content_read_occurred": False,
    }
