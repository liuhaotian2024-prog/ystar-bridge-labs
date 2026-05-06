from __future__ import annotations

import os
from pathlib import Path
from typing import Any

from .e55_action_authorization_gate import authorize_action
from .e56_internal_company_loop_model import BRIDGE_ROOT, SELECTED_ACTION, write_json, write_md
from .e56_internal_loop_behavior_queue import build_internal_loop_behavior_queue, selected_action_proposal


def run_internal_loop_authorization() -> dict[str, Any]:
    queue = build_internal_loop_behavior_queue()
    selected_auth = authorize_action(selected_action_proposal())
    external_proposal = {**selected_action_proposal(), "action_id": "execute_external_first_user_review_now", "action_type": "external_contact", "externality_level": "external_human", "owner_approval_required": True}
    external_auth = authorize_action(external_proposal)
    checks = {
        "selected_internal_action_queued": queue["selected_action_queued"],
        "selected_action_authorized_dry_run": selected_auth["authorization_status"] in {"dry_run_only", "allow"},
        "external_first_user_review_denied": external_auth["authorization_status"] == "deny",
        "pending_owner_decision_remains_pending": selected_auth["owner_approval_status"] == "pending_owner_decision",
        "no_external_action_allowed": selected_auth["external_action_allowed"] is False and external_auth["external_action_allowed"] is False,
        "action_has_evidence_path": bool(selected_action_proposal()["evidence_path"]),
        "requires_KG_CZL_CIEU_writeback": True,
        "ceo_brain_is_source_not_executor": selected_action_proposal()["source"] != "CEO_brain",
    }
    return {
        "artifact_id": "e56_internal_loop_authorization_result",
        "authorization_status": "passed" if all(checks.values()) else "failed",
        "selected_action": SELECTED_ACTION,
        "selected_action_authorization": selected_auth,
        "external_action_authorization": external_auth,
        "checks": checks,
        "external_action_allowed": False,
        "owner_decision_status": "pending_owner_decision",
        "no_external_action": True,
    }


def write_internal_loop_authorization(output_root: Path | None = None) -> dict[str, Any]:
    root = output_root or BRIDGE_ROOT
    data = run_internal_loop_authorization()
    write_json(root, "operations/external_validation/e56_internal_loop_authorization_result.json", data)
    write_md(root, "reports/integration/e56_internal_loop_authorization_result.md", "E56 Internal Loop Authorization", [
        f"Authorization status: `{data['authorization_status']}`",
        "External first-user review: `denied`",
    ])
    return data

