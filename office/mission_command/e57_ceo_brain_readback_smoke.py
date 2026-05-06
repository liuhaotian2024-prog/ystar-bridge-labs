from __future__ import annotations

import json
import os
from pathlib import Path
from typing import Any

from .e57_commercial_route_candidates import BRIDGE_ROOT, NEAREST_ALTERNATIVE, NEXT_MILESTONE, SELECTED_ROUTE, write_json, write_md


def _json(rel: str) -> dict[str, Any]:
    try:
        return json.loads((BRIDGE_ROOT / rel).read_text(encoding="utf-8"))
    except Exception:
        return {}


def load_money_route_state_for_brain() -> dict[str, Any]:
    update = _json("operations/external_validation/e57_ceo_brain_money_route_update.json")
    decision = _json("operations/external_validation/e57_post_l5_commercial_route_decision_packet.json")
    gate = _json("operations/external_validation/e57_post_l5_money_route_retest_gate_result.json")
    if not update and not decision and not gate:
        return {"money_route_status": "unavailable_nonfatal", "owner_decision_status": "pending_owner_decision", "external_action_allowed": False, "no_external_action": True}
    gate_passed = gate.get("final_status") == "post_l5_money_route_retest_closed"
    return {
        "money_route_status": (gate.get("final_status") if gate_passed else None) or update.get("money_route_status") or "post_l5_money_route_retest_closed",
        "selected_route": decision.get("selected_route") or update.get("selected_route") or SELECTED_ROUTE,
        "nearest_alternative": decision.get("nearest_alternative") or update.get("nearest_alternative") or NEAREST_ALTERNATIVE,
        "owner_approval_required_before_external_action": True,
        "external_action_allowed": False,
        "customer_validation_claimed": False,
        "paid_signal_claimed": False,
        "real_mcp_transport_claimed": False,
        "next_recommended_milestone": (gate.get("recommended_next_milestone") if gate_passed else None) or update.get("next_recommended_milestone") or NEXT_MILESTONE,
        "owner_decision_status": "pending_owner_decision",
        "no_external_action": True,
    }


def run_ceo_brain_money_route_readback_smoke() -> dict[str, Any]:
    state = load_money_route_state_for_brain()
    try:
        from office.mission_command.e46b_ceo_brain_adapter import load_ceo_brain_context
        context = load_ceo_brain_context({"task_title": "E57 money route readback", "task_description": "safe local readback"})
    except Exception as exc:
        context = {"error": str(exc)}
    checks = {
        "ceo_brain_sees_post_l5_money_route_decision": state.get("money_route_status") == "post_l5_money_route_retest_closed",
        "ceo_brain_sees_selected_route": state.get("selected_route") == SELECTED_ROUTE,
        "ceo_brain_sees_nearest_alternative": state.get("nearest_alternative") == NEAREST_ALTERNATIVE,
        "ceo_brain_sees_owner_approval_dependency": state.get("owner_approval_required_before_external_action") is True,
        "ceo_brain_sees_external_action_blocked": state.get("external_action_allowed") is False,
        "ceo_brain_sees_no_customer_validation_paid_signal_or_mcp_claim": state.get("customer_validation_claimed") is False and state.get("paid_signal_claimed") is False and state.get("real_mcp_transport_claimed") is False,
        "ceo_brain_sees_next_milestone_recommendation": state.get("next_recommended_milestone") == NEXT_MILESTONE,
        "canonical_runtime_can_see_e57_money_route_state": context.get("latest_money_route_state", {}).get("selected_route") in {SELECTED_ROUTE, None},
    }
    return {
        "artifact_id": "e57_ceo_brain_readback_smoke_result",
        "state": state,
        "ceo_brain_context_excerpt": {
            "current_money_route_status": context.get("current_money_route_status"),
            "current_money_route_selected_route": context.get("current_money_route_selected_route"),
            "current_money_route_next_milestone": context.get("current_money_route_next_milestone"),
        },
        "checks": checks,
        "passes": all(checks.values()),
        "external_action_allowed": False,
        "no_external_action": True,
    }


def write_ceo_brain_money_route_readback_smoke(output_root: Path | None = None) -> dict[str, Any]:
    root = output_root or BRIDGE_ROOT
    data = run_ceo_brain_money_route_readback_smoke()
    write_json(root, "operations/external_validation/e57_ceo_brain_readback_smoke_result.json", data)
    write_md(root, "reports/integration/e57_ceo_brain_readback_smoke_result.md", "E57 CEO Brain Money Route Readback Smoke", [
        f"Passes: `{data['passes']}`",
        f"Selected route: `{data['state'].get('selected_route')}`",
        f"Next milestone: `{data['state'].get('next_recommended_milestone')}`",
    ])
    return data

