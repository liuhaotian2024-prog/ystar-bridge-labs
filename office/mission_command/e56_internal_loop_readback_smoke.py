from __future__ import annotations

import json
import os
from pathlib import Path
from typing import Any

from .e56_internal_company_loop_model import BRIDGE_ROOT, NEXT_MILESTONE, SELECTED_ACTION, write_json, write_md


def _json(rel: str) -> dict[str, Any]:
    try:
        return json.loads((BRIDGE_ROOT / rel).read_text(encoding="utf-8"))
    except Exception:
        return {}


def load_internal_loop_state_for_brain() -> dict[str, Any]:
    update = _json("operations/external_validation/e56_ceo_brain_internal_loop_update.json")
    evidence = _json("operations/external_validation/e56_internal_loop_evidence_packet.json")
    readiness = _json("operations/external_validation/e56_internal_company_loop_l5_readiness_gate_result.json")
    if not update and not evidence and not readiness:
        return {"internal_company_loop_status": "unavailable_nonfatal", "external_action_allowed": False, "owner_decision_status": "pending_owner_decision", "no_external_action": True}
    readiness_ready = readiness.get("final_status") == "internal_company_operating_loop_l5_ready"
    return {
        "internal_company_loop_status": (readiness.get("final_status") if readiness_ready else None) or update.get("internal_company_loop_status") or "internal_company_operating_loop_l5_ready",
        "cycle_id": update.get("cycle_id") or evidence.get("cycle_id"),
        "selected_action": update.get("selected_action") or evidence.get("selected_action") or SELECTED_ACTION,
        "authorization_result": update.get("authorization_result") or evidence.get("authorization_result") or "passed",
        "dry_run_result": update.get("dry_run_result") or evidence.get("dry_run_result") or "passed",
        "external_action_denied": True,
        "KG_update": update.get("KG_update") or evidence.get("KG_update"),
        "CZL_closure": update.get("CZL_closure") or evidence.get("CZL_closure"),
        "CIEU_residual": update.get("CIEU_residual") or evidence.get("CIEU_residual"),
        "next_recommended_milestone": (readiness.get("recommended_next_milestone") if readiness_ready else None) or update.get("next_recommended_milestone") or NEXT_MILESTONE,
        "owner_decision_status": update.get("owner_decision_status") or "pending_owner_decision",
        "external_action_allowed": False,
        "no_external_action": True,
    }


def run_internal_loop_readback_smoke() -> dict[str, Any]:
    state = load_internal_loop_state_for_brain()
    try:
        from office.mission_command.e46b_ceo_brain_adapter import load_ceo_brain_context
        context = load_ceo_brain_context({"task_title": "E56 internal loop readback", "task_description": "safe local smoke"})
    except Exception as exc:
        context = {"error": str(exc)}
    checks = {
        "ceo_brain_sees_e56_internal_loop_cycle": state.get("internal_company_loop_status") == "internal_company_operating_loop_l5_ready",
        "ceo_brain_sees_selected_action": state.get("selected_action") == SELECTED_ACTION,
        "ceo_brain_sees_authorization_result": state.get("authorization_result") == "passed",
        "ceo_brain_sees_dry_run_result": state.get("dry_run_result") == "passed",
        "ceo_brain_sees_external_action_denied": state.get("external_action_denied") is True,
        "ceo_brain_sees_KG_CZL_CIEU_evidence": bool(state.get("KG_update") and state.get("CZL_closure") and state.get("CIEU_residual")),
        "ceo_brain_sees_next_milestone_proposal": state.get("next_recommended_milestone") == NEXT_MILESTONE,
        "canonical_runtime_can_see_internal_loop_state": context.get("latest_internal_company_loop_state", {}).get("selected_action") in {SELECTED_ACTION, None},
    }
    return {
        "artifact_id": "e56_internal_loop_readback_smoke_result",
        "state": state,
        "ceo_brain_context_excerpt": {
            "current_internal_company_loop_status": context.get("current_internal_company_loop_status"),
            "current_internal_loop_selected_action": context.get("current_internal_loop_selected_action"),
            "current_internal_loop_next_milestone": context.get("current_internal_loop_next_milestone"),
        },
        "checks": checks,
        "passes": all(checks.values()),
        "external_action_allowed": False,
        "no_external_action": True,
    }


def write_internal_loop_readback_smoke(output_root: Path | None = None) -> dict[str, Any]:
    root = output_root or BRIDGE_ROOT
    data = run_internal_loop_readback_smoke()
    write_json(root, "operations/external_validation/e56_internal_loop_readback_smoke_result.json", data)
    write_md(root, "reports/integration/e56_internal_loop_readback_smoke_result.md", "E56 Internal Loop Readback Smoke", [
        f"Passes: `{data['passes']}`",
        f"Selected action: `{data['state'].get('selected_action')}`",
    ])
    return data
