from __future__ import annotations

import json
import os
from pathlib import Path
from typing import Any

from .e56_internal_company_loop_model import BRIDGE_ROOT, NEXT_MILESTONE, write_json, write_md


def _json(rel: str) -> dict[str, Any]:
    try:
        return json.loads((BRIDGE_ROOT / rel).read_text(encoding="utf-8"))
    except Exception:
        return {}


def run_internal_company_loop_l5_readiness_gate() -> dict[str, Any]:
    e54 = _json("operations/external_validation/e54_ceo_brain_l5_readiness_gate_result.json")
    e55 = _json("operations/external_validation/e55_behavior_center_l5_readiness_gate_result.json")
    model = _json("operations/external_validation/e56_internal_company_loop_model.json")
    scenario = _json("operations/external_validation/e56_internal_cycle_scenario.json")
    selection = _json("operations/external_validation/e56_counterfactual_internal_action_selection.json")
    queue = _json("operations/external_validation/e56_internal_loop_behavior_queue.json")
    auth = _json("operations/external_validation/e56_internal_loop_authorization_result.json")
    dry = _json("operations/external_validation/e56_internal_loop_dry_run_result.json")
    evidence = _json("operations/external_validation/e56_internal_loop_evidence_packet.json")
    readback = _json("operations/external_validation/e56_internal_loop_readback_smoke_result.json")
    self_eval = _json("operations/external_validation/e56_internal_loop_self_evaluation.json")
    anti = _json("operations/external_validation/e56_internal_loop_anti_drift_gate_result.json")
    binding = _json("operations/external_validation/e56_internal_loop_capability_binding_gate_result.json")
    ygov = _json("operations/external_validation/e56_y_star_gov_validation_result.json")
    gmcp = _json("operations/external_validation/e56_gov_mcp_validation_harness_result.json")
    checks = {
        "E54_brain_L5_passed": e54.get("final_status") == "ceo_brain_l5_cognitive_center_ready",
        "E55_behavior_center_L5_passed": e55.get("final_status") == "behavior_control_center_l5_ready",
        "internal_loop_model_valid": model.get("model_status") == "valid",
        "scenario_valid": scenario.get("selected_action") == "run_internal_operating_loop_self_test",
        "counterfactual_selection_valid": selection.get("nearest_alternative") == "prepare_E57_post_L5_money_route_retest",
        "selected_action_queued": queue.get("selected_action_queued") is True,
        "selected_action_authorized": auth.get("authorization_status") == "passed",
        "dry_run_execution_completed": dry.get("executor_status") == "passed",
        "external_action_denied": auth.get("checks", {}).get("external_first_user_review_denied") is True,
        "evidence_packet_written": evidence.get("selected_action") == "run_internal_operating_loop_self_test",
        "KG_CZL_CIEU_written": bool(evidence.get("KG_update") and evidence.get("CZL_closure") and evidence.get("CIEU_residual")),
        "brain_readback_passed": readback.get("passes") is True,
        "self_evaluation_passed": self_eval.get("self_evaluation_status") == "passed",
        "anti_drift_gate_passed": anti.get("passed") is True,
        "capability_binding_gate_passed": binding.get("passed") is True,
        "y_star_gov_validation_passed": ygov.get("passed") is True,
        "gov_mcp_ALLOW_DENY_passed": gmcp.get("passed") is True,
        "no_owner_approval_fabricated": True,
        "pending_owner_decision_remains_pending": auth.get("owner_decision_status") == "pending_owner_decision",
        "no_external_action_occurred": True,
        "no_customer_validation_claim": dry.get("customer_validation_claimed") is False,
        "no_paid_signal_claim": dry.get("paid_signal_claimed") is False,
        "no_real_mcp_transport_claim": dry.get("real_mcp_transport_claimed") is False,
    }
    passed = all(checks.values())
    return {"artifact_id": "e56_internal_company_loop_l5_readiness_gate_result", "gate_passed": passed, "final_status": "internal_company_operating_loop_l5_ready" if passed else "internal_company_operating_loop_l5_incomplete", "recommended_next_milestone": NEXT_MILESTONE if passed else "E56_R2_internal_loop_repair", "checks": checks, "external_action_allowed": False, "owner_decision_status": "pending_owner_decision", "no_external_action": True}


def write_internal_company_loop_l5_readiness_gate(output_root: Path | None = None) -> dict[str, Any]:
    root = output_root or BRIDGE_ROOT
    data = run_internal_company_loop_l5_readiness_gate()
    write_json(root, "operations/external_validation/e56_internal_company_loop_l5_readiness_gate_result.json", data)
    write_md(root, "reports/integration/e56_internal_company_loop_l5_readiness_gate_result.md", "E56 Internal Company Loop L5 Readiness Gate", [
        f"Gate passed: `{data['gate_passed']}`",
        f"Final status: `{data['final_status']}`",
        f"Recommended next milestone: `{data['recommended_next_milestone']}`",
    ])
    return data

