#!/usr/bin/env python3
"""Shared helpers for L7.1 parallel commercial autonomy lane builders.

The L7.1 builders are deterministic and offline-testable by default. They may
detect real controlled observation configuration from environment variables,
but they never print or serialize secret values.
"""

from __future__ import annotations

import json
import os
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[2]
SCHEMA_VERSION = "v0"
MILESTONE_ID = "L7.1"
MILESTONE_NAME = "Parallel Commercial Autonomy Sprint"
RUN_ID = "l7_1_parallel_commercial_autonomy_sprint_run_001"
GENERATED_AT = "2026-04-29T00:00:00Z"

POLICY_REFS = {
    "policy_ref": "policy/action_capability_registry.json",
    "action_capability_policy_ref": "policy/action_capability_registry.json",
    "approval_state_machine_ref": "policy/approval_state_machine.json",
    "revenue_policy_ref": "policy/revenue_action_policy.json",
    "discovery_policy_ref": "policy/discovery_policy.json",
    "writeback_policy_ref": "policy/writeback_policy.json",
    "runtime_access_policy_ref": "policy/runtime_access_policy.json",
    "owner_burden_reduction_policy_ref": "policy/owner_burden_reduction_policy.json",
    "secret_scanning_policy_ref": "policy/secret_scanning_policy.json",
}

FORBIDDEN_SIDE_EFFECTS = [
    "login",
    "account_creation",
    "payment",
    "checkout",
    "form_submission",
    "posting",
    "commenting",
    "messaging",
    "email_customer_outreach",
    "publication",
    "grant_rfp_bounty_submission",
    "customer_contact",
    "contract_signature",
    "revenue_execution",
    "mcp_execution",
    "live_behavior",
    "private_sensitive_data_collection",
    "private_local_internal_network_access",
    "high_volume_crawling",
    "unbounded_scraping",
    "browser_automation",
    "javascript_execution",
    "robots_access_control_bypass",
    "cieu_db_write",
    "brain_memory_writeback",
    "canonical_strategy_mutation",
    "direct_y_star_mutation",
    "y_star_gov_modification",
    "gov_mcp_modification",
    "db_wal_shm_log_active_agent_marker_content_read",
    "secret_commit",
    "ask_user_url",
]


def write_json(path: str, payload: dict[str, Any] | list[Any]) -> None:
    target = ROOT / path
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(json.dumps(payload, indent=2, sort_keys=False) + "\n", encoding="utf-8")


def write_text(path: str, payload: str) -> None:
    target = ROOT / path
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(payload, encoding="utf-8")


def load_json(path: str, default: Any) -> Any:
    target = ROOT / path
    if not target.exists():
        return default
    return json.loads(target.read_text(encoding="utf-8"))


def artifact_exists(path: str) -> bool:
    return (ROOT / path).exists()


def artifact_ref(path: str) -> str:
    return path if artifact_exists(path) else f"{path} (missing)"


def base_packet(packet_type: str) -> dict[str, Any]:
    return {
        "schema_version": SCHEMA_VERSION,
        "milestone_id": MILESTONE_ID,
        "milestone_name": MILESTONE_NAME,
        "run_id": RUN_ID,
        "packet_type": packet_type,
        "generated_at_utc": GENERATED_AT,
        **POLICY_REFS,
    }


def base_no_action_receipt(lane_id: str, lane_name: str) -> dict[str, Any]:
    receipt = {
        **base_packet("no_action_receipt"),
        "lane_id": lane_id,
        "lane_name": lane_name,
        "external_side_effects_occurred": False,
        "core_writeback_occurred": False,
        "secret_values_serialized": False,
        "ask_user_for_url_occurred": False,
        "manual_search_required": False,
        "manual_env_export_required": False,
    }
    for action in FORBIDDEN_SIDE_EFFECTS:
        receipt[f"{action}_occurred"] = False
    return receipt


def md_table(rows: list[dict[str, Any]], columns: list[str]) -> str:
    header = "| " + " | ".join(columns) + " |"
    sep = "| " + " | ".join(["---"] * len(columns)) + " |"
    body = []
    for row in rows:
        body.append("| " + " | ".join(str(row.get(col, "")) for col in columns) + " |")
    return "\n".join([header, sep] + body)


def simple_md(title: str, sections: list[tuple[str, str]]) -> str:
    chunks = [f"# {title}"]
    for heading, body in sections:
        chunks.append(f"\n## {heading}\n\n{body}")
    return "\n".join(chunks) + "\n"


def current_observation_config() -> dict[str, Any]:
    search_backend = os.environ.get("YSTAR_CONTROLLED_SEARCH_BACKEND", "disabled")
    page_read_backend = os.environ.get("YSTAR_CONTROLLED_PAGE_READ_BACKEND", "disabled")
    search_network_allowed = os.environ.get("YSTAR_CONTROLLED_SEARCH_ALLOW_NETWORK", "0") == "1"
    page_read_network_allowed = os.environ.get("YSTAR_CONTROLLED_PAGE_READ_ALLOW_NETWORK", "0") == "1"
    provider_keys = {
        "brave_search_api": bool(os.environ.get("BRAVE_SEARCH_API_KEY")),
        "tavily_search_api": bool(os.environ.get("TAVILY_API_KEY")),
        "serpapi": bool(os.environ.get("SERPAPI_API_KEY")),
    }
    provider_key_present = provider_keys.get(search_backend, False)
    configured = (
        search_backend in provider_keys
        and page_read_backend == "stdlib_public_http"
        and search_network_allowed
        and page_read_network_allowed
        and provider_key_present
    )
    missing = []
    if search_backend not in provider_keys:
        missing.append("configured_search_backend")
    if page_read_backend != "stdlib_public_http":
        missing.append("stdlib_public_http_page_reader")
    if not search_network_allowed:
        missing.append("YSTAR_CONTROLLED_SEARCH_ALLOW_NETWORK=1")
    if not page_read_network_allowed:
        missing.append("YSTAR_CONTROLLED_PAGE_READ_ALLOW_NETWORK=1")
    if search_backend in provider_keys and not provider_key_present:
        missing.append(f"{search_backend}_api_key_present")
    return {
        "search_backend": search_backend,
        "page_read_backend": page_read_backend,
        "search_network_allowed": search_network_allowed,
        "page_read_network_allowed": page_read_network_allowed,
        "provider_key_present": provider_key_present,
        "configured_for_real_read_only_scan": configured,
        "missing_requirements": missing,
        "secret_values_serialized": False,
    }


def lane_summary(lane_id: str, lane_name: str, output_dir: str, status: str, highlights: dict[str, Any]) -> dict[str, Any]:
    return {
        **base_packet("lane_summary"),
        "lane_id": lane_id,
        "lane_name": lane_name,
        "output_dir": output_dir,
        "status": status,
        "highlights": highlights,
        "external_side_effects_occurred": False,
        "core_writeback_occurred": False,
        "ask_user_for_url_occurred": False,
    }
