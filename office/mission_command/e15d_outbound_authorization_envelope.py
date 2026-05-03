from __future__ import annotations

from typing import Any, Dict, List, Mapping


E15D_AUTHORIZATION_MODES = ["draft_only", "owner_send_only", "send_gated"]


def build_e15d_outbound_authorization_envelope_request(
    console: Mapping[str, Any],
    domain: Mapping[str, Any],
) -> Dict[str, Any]:
    primary_actions = list(console.get("primary_actions", []))
    return {
        "envelope_id": "e15d_outbound_authorization_envelope_request",
        "status": "owner_review_required",
        "authorization_modes_requested": E15D_AUTHORIZATION_MODES,
        "default_authorization_mode": "draft_only",
        "requested_future_mode": "send_gated",
        "source_console_id": console.get("console_id"),
        "controlled_domain_id": domain.get("domain_id"),
        "owner_authorization_present": False,
        "send_allowed_now": False,
        "draft_only_allowed_now": True,
        "owner_send_only_allowed_now": True,
        "max_actions_per_batch": 3,
        "max_actions_per_day": 1,
        "allowed_target_categories": [
            "AI consultants/agencies needing governance layer",
            "AI-heavy teams with agent workflow bottlenecks",
            "organization-facing public business targets only",
        ],
        "prohibited_target_categories": [
            "scraped personal contacts",
            "private individuals without business context",
            "regulated/government/legal/financial targets requiring special approval",
            "suppressed or do-not-contact targets",
        ],
        "allowed_channels": ["owner-selected public/general channel", "approved low-risk email/message adapter after activation"],
        "prohibited_channels": ["scraped personal email", "unapproved social DM", "publication", "form submission", "login-required channel"],
        "allowed_action_ids": [action["action_id"] for action in primary_actions],
        "no_follow_up_unless_positive": True,
        "do_not_contact_suppression_required": True,
        "revocation": {"owner_can_revoke_anytime": True, "Y_gov_can_suspend_on_risk": True},
        "expiration": {"valid_days_after_activation": 7, "expires_if_owner_not_activated": True},
        "owner_override": {"hard_gate_override_required_for_payment_contract_legal_customer_system_core_writeback": True},
        "emergency_stop": {"global_kill_switch_supported": True, "batch_kill_switch_supported": True},
        "not_authorized": [
            "real email/message send before owner activation",
            "publication",
            "payment",
            "account creation",
            "form submission",
            "login",
            "external validation submission",
            "customer system access",
            "legal or financial commitment",
            "credential disclosure",
            "core brain/CIEU/memory writeback",
        ],
        "external_action_executed": False,
    }


def validate_e15d_outbound_authorization_envelope_request(envelope: Mapping[str, Any]) -> List[str]:
    errors: List[str] = []
    if envelope.get("status") != "owner_review_required":
        errors.append("envelope_must_remain_owner_review_required")
    if envelope.get("owner_authorization_present") is not False:
        errors.append("must_not_fake_owner_authorization")
    if envelope.get("send_allowed_now") is not False:
        errors.append("send_must_not_be_allowed_now")
    if envelope.get("draft_only_allowed_now") is not True:
        errors.append("draft_only_should_be_available")
    if envelope.get("max_actions_per_batch") != 3:
        errors.append("max_actions_per_batch_must_be_three")
    if len(envelope.get("allowed_action_ids", [])) != 3:
        errors.append("envelope_must_cover_three_primary_actions")
    for mode in E15D_AUTHORIZATION_MODES:
        if mode not in envelope.get("authorization_modes_requested", []):
            errors.append(f"missing_authorization_mode_{mode}")
    if envelope.get("external_action_executed") is not False:
        errors.append("envelope_must_not_execute_external_action")
    return list(dict.fromkeys(errors))
