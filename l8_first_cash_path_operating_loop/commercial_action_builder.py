#!/usr/bin/env python3
"""Build approval-gated commercial action variants for the first cash path."""

from __future__ import annotations

from typing import Any

from .commercial_action_queue import list_commercial_actions, save_action
from .first_cash_path_loader import initialize_first_cash_path
from .first_cash_path_model import base_packet, now_iso


ACTION_VARIANTS = [
    {
        "action_type": "warm_intro_request",
        "title": "Warm intro request for founder workflow audit pilot",
        "target_profile": "Trusted peer or founder-adjacent contact who can introduce an AI startup founder/operator.",
        "draft_content": (
            "I am testing a small, paid Founder AI Workflow Audit & CEO Command Brief Sprint for AI founders/operators. "
            "The goal is to identify execution bottlenecks, agent workflow risks, and the next concrete action plan. "
            "Do you know one founder who might value a tightly scoped $1,500 diagnostic pilot? No pressure if not."
        ),
        "risk_boundary": "Do not claim proven customer outcomes yet; this is a paid pilot hypothesis for manual owner review.",
    },
    {
        "action_type": "direct_founder_outreach",
        "title": "Direct founder outreach draft for workflow bottleneck diagnostic",
        "target_profile": "AI startup founder or technical operator with urgent workflow, strategy, or execution bottleneck.",
        "draft_content": (
            "I am preparing a done-for-you AI workflow audit and CEO command brief sprint for founders using agent/coding workflows. "
            "The deliverable is an internal decision brief: bottlenecks, evidence/risk notes, and next action options. "
            "Would a scoped $1,500 diagnostic be worth reviewing if the fit is right?"
        ),
        "risk_boundary": "Manual send only after owner approval; no scraping, no mass outreach, no unsupported promise of revenue results.",
    },
    {
        "action_type": "founder_operator_diagnostic_offer",
        "title": "Founder/operator diagnostic offer packet",
        "target_profile": "Small AI/product team deciding what to automate, delegate, or govern next.",
        "draft_content": (
            "Offer: Founder AI Workflow Audit & CEO Command Brief Sprint. Included: intake, governed observation plan, workflow audit, "
            "decision-risk notes, and an owner-facing command brief. Not included: external execution, legal/compliance advice, or guaranteed revenue."
        ),
        "risk_boundary": "Use as an owner-reviewed offer packet, not a published marketing page or automated checkout flow.",
    },
]


def build_commercial_actions(force: bool = False) -> dict[str, Any]:
    cash_path = initialize_first_cash_path()
    existing = list_commercial_actions()
    if existing and not force:
        return {"ok": True, "cash_path": cash_path, "actions": existing, "created": 0}
    actions = []
    for variant in ACTION_VARIANTS:
        action_id = f"commercial_action_{variant['action_type']}"
        action = {
            **base_packet("commercial_action"),
            "action_id": action_id,
            "cash_path_id": cash_path["cash_path_id"],
            "action_type": variant["action_type"],
            "title": variant["title"],
            "target_profile": variant["target_profile"],
            "draft_content": variant["draft_content"],
            "risk_boundary": variant["risk_boundary"],
            "approval_required": True,
            "execution_mode": "manual_send_packet",
            "disabled_tool_send_email_future_slot": {
                "available": False,
                "enabled": False,
                "reason": "L8.0 only supports owner manual-send packets. No email tool execution is allowed.",
            },
            "status": "pending_owner_approval",
            "created_at": now_iso(),
            "updated_at": now_iso(),
            "price_hypothesis_usd": 1500,
            "what_is_offered": "Governed observation + workflow audit + CEO command brief style deliverable.",
            "what_is_not_promised": [
                "guaranteed revenue",
                "legal/compliance advice",
                "automatic execution",
                "publication",
                "grant/RFP application",
            ],
        }
        actions.append(save_action(action))
    return {"ok": True, "cash_path": cash_path, "actions": actions, "created": len(actions)}

