from __future__ import annotations

import os
from pathlib import Path
from typing import Any

from .e56_internal_company_loop_model import (
    BRIDGE_ROOT, NEAREST_ALTERNATIVE, NEXT_MILESTONE, OWNER_STATUS, SELECTED_ACTION, current_state_summary, write_json, write_md,
)


def _candidate(action_id: str, action_type: str, disposition: str, reason: str, external: bool = False) -> dict[str, Any]:
    return {
        "action_id": action_id,
        "action_type": action_type,
        "intent": reason,
        "disposition": disposition,
        "owner_approval_required": external,
        "external_action_allowed": False,
        "pending_owner_decision_not_approval": True,
        "evidence_required": True,
    }


def build_internal_cycle_scenario() -> dict[str, Any]:
    candidates = [
        _candidate(SELECTED_ACTION, "internal_validation", "select", "prove the internal company loop before any money-route retest"),
        _candidate(NEAREST_ALTERNATIVE, "internal_analysis", "defer", "prepare the post-L5 money route retest after E56 proof passes"),
        _candidate("wait_for_owner_decision", "internal_analysis", "defer", "safe but passive; does not prove operating loop readiness"),
        _candidate("close_real_mcp_transport_gate", "internal_validation", "defer", "important but not required to prove internal company loop L5"),
        _candidate("execute_external_first_user_review_now", "external_contact", "deny", "owner decision remains pending; external action blocked", True),
    ]
    return {
        "artifact_id": "e56_internal_cycle_scenario",
        "cycle_id": "e56_internal_company_operating_cycle_20260506T000001Z",
        "current_state": current_state_summary(),
        "candidate_actions": candidates,
        "selected_action": SELECTED_ACTION,
        "nearest_alternative": NEAREST_ALTERNATIVE,
        "external_first_user_review_action": "denied",
        "owner_decision_status": OWNER_STATUS,
        "external_action_allowed": False,
        "next_milestone_if_cycle_passes": NEXT_MILESTONE,
        "no_external_action": True,
    }


def write_internal_cycle_scenario(output_root: Path | None = None) -> dict[str, Any]:
    root = output_root or BRIDGE_ROOT
    data = build_internal_cycle_scenario()
    write_json(root, "operations/external_validation/e56_internal_cycle_scenario.json", data)
    write_md(root, "reports/integration/e56_internal_cycle_scenario.md", "E56 Internal Cycle Scenario", [
        f"Selected action: `{data['selected_action']}`",
        f"Nearest alternative: `{data['nearest_alternative']}`",
        "External first-user review action: `denied`",
    ])
    return data

