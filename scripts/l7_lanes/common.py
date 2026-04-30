#!/usr/bin/env python3
"""Shared helpers for L7 parallel commercial lane builders.

The L7.0P builders are deterministic/offline. They generate scoped JSON and
Markdown artifacts only; no external network, external action, or core
writeback is performed.
"""

from __future__ import annotations

from datetime import datetime, timezone
import json
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[2]
SCHEMA_VERSION = "v0"
MILESTONE_ID = "L7.0P"
MILESTONE_NAME = "Parallel Commercial Agent Team Execution Orchestrator"
RUN_ID = "l7_0p_parallel_commercial_agent_team_orchestrator_run_001"

FORBIDDEN_ACTIONS = [
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

L7_0Q_POLICY_MIGRATION_DIRS = {
    "l7_agent_team_runtime",
    "l7_revenue_opportunity_radar",
    "l7_human_approved_external_action_gate",
    "l7_review_gated_memory_writeback",
    "l7_owner_runtime_cockpit",
    "l7_parallel_commercial_agent_team_orchestrator",
}

LANES = [
    {
        "lane_id": "L7A",
        "name": "Agent Team Runtime",
        "short": "team",
        "branch": "l7/team-runtime",
        "worktree": "../ystar-company-l7-team",
        "prompt": "l7_parallel_lane_specs/l7a_agent_team_runtime.prompt.md",
        "builder": "scripts/l7_lanes/build_l7a_agent_team_runtime.py",
        "output_dir": "l7_agent_team_runtime",
        "summary": "l7_agent_team_runtime/l7a_agent_team_runtime_summary.json",
    },
    {
        "lane_id": "L7B",
        "name": "Revenue Opportunity Radar",
        "short": "revenue",
        "branch": "l7/revenue-opportunity-radar",
        "worktree": "../ystar-company-l7-revenue",
        "prompt": "l7_parallel_lane_specs/l7b_revenue_opportunity_radar.prompt.md",
        "builder": "scripts/l7_lanes/build_l7b_revenue_opportunity_radar.py",
        "output_dir": "l7_revenue_opportunity_radar",
        "summary": "l7_revenue_opportunity_radar/l7b_revenue_opportunity_radar_summary.json",
    },
    {
        "lane_id": "L7C",
        "name": "Human-Approved External Action Gate",
        "short": "action",
        "branch": "l7/human-approved-action-gate",
        "worktree": "../ystar-company-l7-action",
        "prompt": "l7_parallel_lane_specs/l7c_human_approved_external_action_gate.prompt.md",
        "builder": "scripts/l7_lanes/build_l7c_human_approved_external_action_gate.py",
        "output_dir": "l7_human_approved_external_action_gate",
        "summary": "l7_human_approved_external_action_gate/l7c_human_approved_external_action_gate_summary.json",
    },
    {
        "lane_id": "L7D",
        "name": "Review-Gated Memory / Brain Writeback Protocol",
        "short": "memory",
        "branch": "l7/review-gated-memory-writeback",
        "worktree": "../ystar-company-l7-memory",
        "prompt": "l7_parallel_lane_specs/l7d_review_gated_memory_writeback.prompt.md",
        "builder": "scripts/l7_lanes/build_l7d_review_gated_memory_writeback.py",
        "output_dir": "l7_review_gated_memory_writeback",
        "summary": "l7_review_gated_memory_writeback/l7d_review_gated_memory_writeback_summary.json",
    },
    {
        "lane_id": "L7E",
        "name": "Owner Runtime Cockpit",
        "short": "cockpit",
        "branch": "l7/runtime-cockpit",
        "worktree": "../ystar-company-l7-cockpit",
        "prompt": "l7_parallel_lane_specs/l7e_owner_runtime_cockpit.prompt.md",
        "builder": "scripts/l7_lanes/build_l7e_owner_runtime_cockpit.py",
        "output_dir": "l7_owner_runtime_cockpit",
        "summary": "l7_owner_runtime_cockpit/l7e_owner_runtime_cockpit_summary.json",
    },
]


def utc_now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def l7_0q_policy_migration_for_path(path: str) -> dict[str, Any] | None:
    top_level = path.split("/", 1)[0]
    if top_level not in L7_0Q_POLICY_MIGRATION_DIRS:
        return None
    if "human_approved_external_action_gate" in path:
        category = "external_action_gate"
        stage = "draft"
        requires_approval = True
    elif "review_gated_memory_writeback" in path:
        category = "writeback"
        stage = "writeback_candidate"
        requires_approval = True
    elif "revenue_opportunity_radar" in path:
        category = "revenue_discovery"
        stage = "analyze"
        requires_approval = False
    elif "owner_runtime_cockpit" in path:
        category = "owner_cockpit"
        stage = "plan"
        requires_approval = False
    elif "parallel_commercial_agent_team_orchestrator" in path:
        category = "parallel_orchestration"
        stage = "plan"
        requires_approval = False
    else:
        category = "agent_team_runtime"
        stage = "plan"
        requires_approval = False

    block: dict[str, Any] = {
        "policy_ref": "policy/action_capability_registry.json",
        "action_capability_policy_ref": "policy/action_capability_registry.json",
        "approval_state_machine_ref": "policy/approval_state_machine.json",
        "revenue_policy_ref": "policy/revenue_action_policy.json",
        "discovery_policy_ref": "policy/discovery_policy.json",
        "runtime_access_policy_ref": "policy/runtime_access_policy.json",
        "writeback_policy_ref": "policy/writeback_policy.json",
        "owner_burden_reduction_policy_ref": "policy/owner_burden_reduction_policy.json",
        "allowed_capability_stage": stage,
        "capability_category": category,
        "execution_requires_human_approval": requires_approval,
        "migration_note": "L7.0Q first migration adds staged policy references while preserving explicit safety text.",
    }
    if category == "revenue_discovery":
        block["revenue_execution_requires_human_approval"] = True
    if category == "writeback":
        block["allowed_writeback_stage"] = "dry_run_writeback"
    return block


def l7_0r_staged_policy_for_path(path: str) -> dict[str, Any] | None:
    top_level = path.split("/", 1)[0]
    if top_level not in L7_0Q_POLICY_MIGRATION_DIRS:
        return None
    if "revenue_opportunity_radar" in path:
        principle = "Do not block revenue work. Block unapproved revenue side effects."
        stages = ["observe", "search", "read", "extract", "analyze", "draft", "plan", "request_approval"]
    elif "human_approved_external_action_gate" in path:
        principle = "External execution is staged: draft allowed, execution blocked until human approval."
        stages = ["draft", "request_approval", "execute_after_approval"]
    elif "review_gated_memory_writeback" in path:
        principle = "Do not block learning. Block unreviewed permanent writeback."
        stages = ["writeback_candidate", "dry_run_writeback", "actual_writeback_after_approval"]
    else:
        principle = "Use staged capability policy instead of blanket blocking."
        stages = ["observe", "analyze", "draft", "plan", "request_approval"]
    return {
        "policy_decision_helper": "policy/policy_decision.py",
        "principle": principle,
        "allowed_capability_stages": stages,
        "read_only_discovery_allowed": True,
        "draft_allowed": True,
        "actual_execution_blocked_until_approval": True,
        "actual_core_writeback_blocked_until_approval": True,
        "owner_manual_burden_replacement": "Prefer one-command launchers, resolvers, and orchestrators over manual URLs, manual env exports, manual worktrees, or manual merges.",
    }


def write_json(path: str, payload: dict[str, Any] | list[Any]) -> None:
    target = ROOT / path
    target.parent.mkdir(parents=True, exist_ok=True)
    if isinstance(payload, dict):
        migration = l7_0q_policy_migration_for_path(path)
        if migration:
            payload.setdefault("l7_0q_policy_migration", migration)
        remediation = l7_0r_staged_policy_for_path(path)
        if remediation:
            payload.setdefault("l7_0r_staged_policy_remediation", remediation)
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


def artifact_ref(path: str) -> str:
    return path if (ROOT / path).exists() else f"{path} (missing)"


def base_no_action_receipt(lane_id: str, lane_name: str) -> dict[str, Any]:
    receipt = {
        "schema_version": SCHEMA_VERSION,
        "milestone_id": MILESTONE_ID,
        "lane_id": lane_id,
        "lane_name": lane_name,
        "generated_at_utc": utc_now(),
        "external_network_performed": False,
        "external_side_effects_occurred": False,
        "core_writeback_occurred": False,
        "ask_user_for_url_occurred": False,
        "secret_values_serialized": False,
    }
    for action in FORBIDDEN_ACTIONS:
        receipt[f"{action}_occurred"] = False
    return receipt


def simple_md(title: str, payload: dict[str, Any]) -> str:
    return f"# {title}\n\n```json\n{json.dumps(payload, indent=2, sort_keys=False)}\n```\n"


def lane_summary(
    lane_id: str,
    lane_name: str,
    output_dir: str,
    artifacts: list[str],
    next_safe_step: str,
    extra: dict[str, Any] | None = None,
) -> dict[str, Any]:
    payload = {
        "schema_version": SCHEMA_VERSION,
        "milestone_id": MILESTONE_ID,
        "lane_id": lane_id,
        "lane_name": lane_name,
        "output_dir": output_dir,
        "status": "complete",
        "artifacts": artifacts,
        "next_safe_step": next_safe_step,
        "external_actions_blocked": True,
        "core_writebacks_blocked": True,
        "ask_user_for_url_occurred": False,
        "external_side_effects_occurred": False,
        "core_writeback_occurred": False,
        "secret_values_serialized": False,
    }
    if extra:
        payload.update(extra)
    return payload


def lane_status() -> dict[str, Any]:
    lanes = []
    for lane in LANES:
        output_dir = ROOT / lane["output_dir"]
        summary = ROOT / lane["summary"]
        status = "complete" if output_dir.is_dir() and summary.is_file() else "missing"
        lanes.append(
            {
                "lane_id": lane["lane_id"],
                "lane_name": lane["name"],
                "branch": lane["branch"],
                "worktree": lane["worktree"],
                "prompt": lane["prompt"],
                "builder": lane["builder"],
                "output_dir": lane["output_dir"],
                "summary": lane["summary"],
                "status": status,
            }
        )
    return {
        "schema_version": SCHEMA_VERSION,
        "milestone_id": MILESTONE_ID,
        "run_id": RUN_ID,
        "lanes": lanes,
        "all_lanes_complete": all(lane["status"] == "complete" for lane in lanes),
    }
