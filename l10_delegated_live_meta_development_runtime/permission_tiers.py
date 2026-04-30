#!/usr/bin/env python3
"""Permission tier policy for delegated Labs missions."""

from __future__ import annotations

from typing import Any

from .mission_model import FORBIDDEN_ACTION_CLASSES, base_packet


def permission_tier_registry() -> dict[str, Any]:
    tiers = [
        {
            "tier_id": "tier_0",
            "tier_name": "autonomous_internal_work",
            "allowed_action_classes": ["internal_analysis", "local_packet_creation", "strategy_drafting", "scheduler_cycle"],
            "requires_budget": False,
            "requires_owner_approval": False,
            "forbidden_action_classes": FORBIDDEN_ACTION_CLASSES,
            "escalation_required_for": ["external_research", *FORBIDDEN_ACTION_CLASSES],
            "explanation": "Safe local work only.",
        },
        {
            "tier_id": "tier_1",
            "tier_name": "autonomous_read_only_external_research",
            "allowed_action_classes": ["internal_analysis", "local_packet_creation", "budgeted_read_only_research", "evidence_packet_generation"],
            "requires_budget": True,
            "requires_owner_approval": False,
            "forbidden_action_classes": FORBIDDEN_ACTION_CLASSES,
            "escalation_required_for": FORBIDDEN_ACTION_CLASSES,
            "explanation": "Budgeted read-only research with no login/contact/submit/payment/publication.",
        },
        {
            "tier_id": "tier_2",
            "tier_name": "autonomous_preparation_owner_approved_execution",
            "allowed_action_classes": ["draft_outreach", "proposal_draft", "landing_page_draft", "public_post_draft", "service_package_draft"],
            "requires_budget": False,
            "requires_owner_approval": True,
            "forbidden_action_classes": FORBIDDEN_ACTION_CLASSES,
            "escalation_required_for": FORBIDDEN_ACTION_CLASSES,
            "explanation": "Labs can prepare external-action drafts; owner approval is required to execute.",
        },
        {
            "tier_id": "tier_3",
            "tier_name": "pre_approved_constrained_external_action_future_slot",
            "allowed_action_classes": ["future_owner_approved_message", "future_owner_approved_publication", "future_owner_approved_form_submission"],
            "requires_budget": True,
            "requires_owner_approval": True,
            "forbidden_action_classes": FORBIDDEN_ACTION_CLASSES,
            "escalation_required_for": FORBIDDEN_ACTION_CLASSES,
            "explanation": "Future slot only in L10; no execution is implemented.",
        },
        {
            "tier_id": "tier_4",
            "tier_name": "high_risk_blocked_or_review_gated",
            "allowed_action_classes": [],
            "requires_budget": True,
            "requires_owner_approval": True,
            "forbidden_action_classes": FORBIDDEN_ACTION_CLASSES,
            "escalation_required_for": FORBIDDEN_ACTION_CLASSES,
            "explanation": "High-risk actions remain blocked/review-gated.",
        },
    ]
    return {**base_packet("permission_tier_policy_registry"), "tiers": tiers, "tier_count": len(tiers)}


def get_tier(tier_id: str) -> dict[str, Any]:
    for tier in permission_tier_registry()["tiers"]:
        if tier["tier_id"] == tier_id:
            return tier
    raise ValueError(f"unknown permission tier: {tier_id}")


def is_action_allowed(tier_id: str, action_class: str, budget_attached: bool = False) -> dict[str, Any]:
    tier = get_tier(tier_id)
    if action_class in tier["forbidden_action_classes"]:
        return {"allowed": False, "requires_escalation": True, "reason": f"{action_class} is forbidden at {tier_id}"}
    if tier["requires_budget"] and not budget_attached:
        return {"allowed": False, "requires_escalation": False, "reason": "budget required"}
    return {
        "allowed": action_class in tier["allowed_action_classes"],
        "requires_escalation": action_class in tier["escalation_required_for"],
        "reason": tier["explanation"],
    }

