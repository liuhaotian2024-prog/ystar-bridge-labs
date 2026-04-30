#!/usr/bin/env python3
"""Manual-send-only execution plans for selected L9 opportunities."""

from __future__ import annotations

from typing import Any

from .money_path_model import get_money_path
from .opportunity_model import base_packet, load_packets, now_iso, write_packet
from .opportunity_portfolio import get_opportunity


def build_execution_plan(money_path_id: str | None = None) -> dict[str, Any]:
    path = _selected_path(money_path_id)
    opportunity = get_opportunity(path["opportunity_id"])
    plan_id = f"execution_plan_{path['money_path_id']}"
    plan = {
        **base_packet("execution_plan"),
        "execution_plan_id": plan_id,
        "opportunity_id": opportunity["opportunity_id"],
        "money_path_id": path["money_path_id"],
        "selected_offer": path["offer_hypothesis"],
        "target_customer_profile": path["target_customer"],
        "first_action": path["first_action"],
        "commercial_action_variants": _action_variants(opportunity, path),
        "required_owner_approval": [
            "approve any external contact",
            "approve target recipient/channel",
            "approve claims and price before use",
            "approve any payment or contract step separately",
        ],
        "manual_execution_mode": "manual_send_only",
        "tool_send_email_enabled": False,
        "feedback_intake_plan": path["feedback_plan"],
        "residual_plan": "Compare expected signal to owner-entered feedback and create a portfolio residual.",
        "learning_candidate_plan": "Create review-gated learning candidate only; no core memory writeback.",
        "status": "execution_plan_ready_for_owner_review",
        "created_at": now_iso(),
        "external_side_effects": False,
        "email_sent": False,
        "customer_contact": False,
        "payment_processed": False,
    }
    return write_packet("execution_plans", plan_id, plan)


def list_execution_plans() -> list[dict[str, Any]]:
    return load_packets("execution_plans")


def _selected_path(money_path_id: str | None) -> dict[str, Any]:
    if money_path_id:
        path = get_money_path(money_path_id)
        if not path:
            raise ValueError(f"unknown money path: {money_path_id}")
        if path.get("status") != "selected_for_execution":
            raise ValueError(f"money path is not selected for execution: {money_path_id}")
        return path
    selected = [path for path in load_packets("money_path_candidates") if path.get("status") == "selected_for_execution"]
    if not selected:
        raise ValueError("no selected opportunity is ready for execution planning")
    return selected[0]


def _action_variants(opportunity: dict[str, Any], path: dict[str, Any]) -> list[dict[str, Any]]:
    profile = path["target_customer"]
    return [
        {
            "variant_id": f"{path['money_path_id']}_warm_intro_request",
            "action_type": "warm_intro_request",
            "target_profile": profile,
            "draft_angle": f"Ask a trusted connector whether this {opportunity['category']} problem is active for a founder/operator.",
            "approval_required": True,
            "execution_mode": "manual_send_only",
        },
        {
            "variant_id": f"{path['money_path_id']}_direct_founder_outreach",
            "action_type": "direct_founder_outreach",
            "target_profile": profile,
            "draft_angle": f"Offer a scoped diagnostic conversation around: {opportunity['problem_statement']}",
            "approval_required": True,
            "execution_mode": "manual_send_only",
        },
        {
            "variant_id": f"{path['money_path_id']}_diagnostic_offer",
            "action_type": "diagnostic_offer",
            "target_profile": profile,
            "draft_angle": f"Present the first paid diagnostic hypothesis: {path['offer_hypothesis']}",
            "approval_required": True,
            "execution_mode": "manual_send_only",
        },
    ]
