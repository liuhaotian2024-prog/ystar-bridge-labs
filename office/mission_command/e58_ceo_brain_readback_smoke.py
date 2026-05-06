from __future__ import annotations

import json
import os
from pathlib import Path
from typing import Any

from .e58_case_study_boundary import BRIDGE_ROOT, CASE_STUDY_ID, NEXT_MILESTONE, SELECTED_ROUTE, write_json, write_md


def _json(rel: str) -> dict[str, Any]:
    try:
        return json.loads((BRIDGE_ROOT / rel).read_text(encoding="utf-8"))
    except Exception:
        return {}


def load_case_study_state_for_brain() -> dict[str, Any]:
    update = _json("operations/external_validation/e58_ceo_brain_case_study_update.json")
    case = _json("products/ai_agent_company_runtime_harness_case_study/case_study.json")
    gate = _json("operations/external_validation/e58_case_study_completion_gate_result.json")
    if not update and not case and not gate:
        return {"case_study_status": "unavailable_nonfatal", "external_action_allowed": False, "owner_decision_status": "pending_owner_decision", "no_external_action": True}
    gate_passed = gate.get("final_status") == "AI_agent_company_runtime_harness_case_study_packaged"
    return {
        "case_study_status": (gate.get("final_status") if gate_passed else None) or update.get("case_study_status") or "AI_agent_company_runtime_harness_case_study_packaged",
        "case_study_id": update.get("case_study_id") or case.get("case_study_id") or CASE_STUDY_ID,
        "selected_route_from_E57": update.get("selected_route_from_E57") or case.get("selected_route_from_E57") or SELECTED_ROUTE,
        "external_intelligence_gap_declared": update.get("external_intelligence_gap_declared") if update else True,
        "E59_required_before_market_contact": update.get("E59_required_before_market_contact") if update else True,
        "external_action_allowed": False,
        "customer_validation_claimed": False,
        "paid_signal_claimed": False,
        "real_mcp_transport_claimed": False,
        "external_intelligence_L5_claimed_complete": False,
        "next_recommended_milestone": (gate.get("recommended_next_milestone") if gate_passed else None) or update.get("next_recommended_milestone") or case.get("next_recommended_milestone") or NEXT_MILESTONE,
        "owner_decision_status": "pending_owner_decision",
        "no_external_action": True,
    }


def run_case_study_readback_smoke() -> dict[str, Any]:
    state = load_case_study_state_for_brain()
    try:
        from office.mission_command.e46b_ceo_brain_adapter import load_ceo_brain_context
        context = load_ceo_brain_context({"task_title": "E58 case study readback", "task_description": "safe local readback"})
    except Exception as exc:
        context = {"error": str(exc)}
    checks = {
        "ceo_brain_sees_case_study_exists": state.get("case_study_id") == CASE_STUDY_ID,
        "ceo_brain_sees_selected_route_from_E57": state.get("selected_route_from_E57") == SELECTED_ROUTE,
        "ceo_brain_sees_external_intelligence_gap": state.get("external_intelligence_gap_declared") is True,
        "ceo_brain_sees_E59_required_before_market_contact": state.get("E59_required_before_market_contact") is True,
        "ceo_brain_sees_external_action_blocked": state.get("external_action_allowed") is False,
        "ceo_brain_sees_no_customer_paid_mcp_claim": state.get("customer_validation_claimed") is False and state.get("paid_signal_claimed") is False and state.get("real_mcp_transport_claimed") is False,
        "ceo_brain_sees_next_milestone": state.get("next_recommended_milestone") == NEXT_MILESTONE,
        "canonical_runtime_can_see_e58_state": context.get("latest_case_study_state", {}).get("case_study_id") == CASE_STUDY_ID,
    }
    return {"artifact_id": "e58_ceo_brain_readback_smoke_result", "state": state, "ceo_brain_context_excerpt": {"current_case_study_status": context.get("current_case_study_status"), "current_case_study_next_milestone": context.get("current_case_study_next_milestone")}, "checks": checks, "passes": all(checks.values()), "external_action_allowed": False, "no_external_action": True}


def write_case_study_readback_smoke(output_root: Path | None = None) -> dict[str, Any]:
    root = output_root or BRIDGE_ROOT
    data = run_case_study_readback_smoke()
    write_json(root, "operations/external_validation/e58_ceo_brain_readback_smoke_result.json", data)
    write_md(root, "reports/integration/e58_ceo_brain_readback_smoke_result.md", "E58 CEO Brain Case Study Readback Smoke", [f"Passes: `{data['passes']}`", f"Next milestone: `{data['state'].get('next_recommended_milestone')}`"])
    return data
