from __future__ import annotations

from dataclasses import asdict, dataclass
from typing import Dict, List


class RiskTier:
    TIER_0_INTERNAL = "TIER_0_INTERNAL"
    TIER_1_PUBLIC_READ_ONLY = "TIER_1_PUBLIC_READ_ONLY"
    TIER_2_TRANSPARENT_LOW_RISK_EXTERNAL_VALIDATION = "TIER_2_TRANSPARENT_LOW_RISK_EXTERNAL_VALIDATION"
    TIER_3_PUBLIC_BROADCAST_OR_LANDING = "TIER_3_PUBLIC_BROADCAST_OR_LANDING"
    TIER_4_COMMERCIAL_LEGAL_PRODUCTION_HIGH_RISK = "TIER_4_COMMERCIAL_LEGAL_PRODUCTION_HIGH_RISK"


class ActionType:
    INTERNAL_PREPARE = "internal_prepare"
    PUBLIC_READ = "public_read"
    SEND_VALIDATION_MESSAGE = "send_validation_message"
    REQUEST_FEEDBACK = "request_feedback"
    PUBLISH_POST = "publish_post"
    PUBLISH_LANDING_PAGE = "publish_landing_page"
    COLLECT_SURVEY_RESPONSE = "collect_survey_response"
    COLLECT_PAYMENT = "collect_payment"
    CREATE_ACCOUNT = "create_account"
    SUBMIT_FORM = "submit_form"
    EXECUTE_CONTRACT = "execute_contract"
    PRODUCTION_IMPLEMENTATION = "production_implementation"
    CORE_WRITEBACK = "core_writeback"


class RiskControlRequirement:
    AI_DISCLOSURE_REQUIRED = "ai_disclosure_required"
    OWNER_APPROVAL_REQUIRED = "owner_approval_required"
    TARGET_SEED_REQUIRED = "target_seed_required"
    CHANNEL_REQUIRED = "channel_required"
    DRAFT_HASH_REQUIRED = "draft_hash_required"
    MAX_COUNT_REQUIRED = "max_count_required"
    STOP_CONDITIONS_REQUIRED = "stop_conditions_required"
    OPT_OUT_REQUIRED = "opt_out_required"
    ACTION_LEDGER_REQUIRED = "action_ledger_required"
    FEEDBACK_LEDGER_REQUIRED = "feedback_ledger_required"
    NO_DECEPTION_REQUIRED = "no_deception_required"
    NO_SCRAPED_LEADS_REQUIRED = "no_scraped_leads_required"
    NO_PAYMENT_REQUIRED = "no_payment_required"
    NO_ACCOUNT_CREATION_REQUIRED = "no_account_creation_required"
    NO_CORE_WRITEBACK_REQUIRED = "no_core_writeback_required"


@dataclass(frozen=True)
class RiskTierPolicy:
    tier: str
    allowed_actions: List[str]
    prohibited_actions: List[str]
    required_controls: List[str]
    escalation_rule: str
    stop_conditions: List[str]
    audit_ledger_required: bool

    def to_dict(self) -> Dict[str, object]:
        return asdict(self)


TIER_POLICIES = {
    RiskTier.TIER_0_INTERNAL: RiskTierPolicy(
        tier=RiskTier.TIER_0_INTERNAL,
        allowed_actions=[ActionType.INTERNAL_PREPARE],
        prohibited_actions=[],
        required_controls=[],
        escalation_rule="No external side effect is allowed.",
        stop_conditions=["stop if action becomes external-facing"],
        audit_ledger_required=False,
    ),
    RiskTier.TIER_1_PUBLIC_READ_ONLY: RiskTierPolicy(
        tier=RiskTier.TIER_1_PUBLIC_READ_ONLY,
        allowed_actions=[ActionType.PUBLIC_READ],
        prohibited_actions=[ActionType.SEND_VALIDATION_MESSAGE, ActionType.PUBLISH_POST, ActionType.COLLECT_PAYMENT],
        required_controls=[
            RiskControlRequirement.STOP_CONDITIONS_REQUIRED,
            RiskControlRequirement.NO_PAYMENT_REQUIRED,
            RiskControlRequirement.NO_ACCOUNT_CREATION_REQUIRED,
        ],
        escalation_rule="Escalate if login, form submission, contact, payment, or private data appears.",
        stop_conditions=["login required", "form/payment/contact flow", "private or sensitive page"],
        audit_ledger_required=True,
    ),
    RiskTier.TIER_2_TRANSPARENT_LOW_RISK_EXTERNAL_VALIDATION: RiskTierPolicy(
        tier=RiskTier.TIER_2_TRANSPARENT_LOW_RISK_EXTERNAL_VALIDATION,
        allowed_actions=[ActionType.SEND_VALIDATION_MESSAGE, ActionType.REQUEST_FEEDBACK, ActionType.COLLECT_SURVEY_RESPONSE],
        prohibited_actions=[ActionType.COLLECT_PAYMENT, ActionType.CREATE_ACCOUNT, ActionType.SUBMIT_FORM, ActionType.CORE_WRITEBACK],
        required_controls=[
            RiskControlRequirement.AI_DISCLOSURE_REQUIRED,
            RiskControlRequirement.OWNER_APPROVAL_REQUIRED,
            RiskControlRequirement.TARGET_SEED_REQUIRED,
            RiskControlRequirement.CHANNEL_REQUIRED,
            RiskControlRequirement.DRAFT_HASH_REQUIRED,
            RiskControlRequirement.MAX_COUNT_REQUIRED,
            RiskControlRequirement.STOP_CONDITIONS_REQUIRED,
            RiskControlRequirement.OPT_OUT_REQUIRED,
            RiskControlRequirement.ACTION_LEDGER_REQUIRED,
            RiskControlRequirement.FEEDBACK_LEDGER_REQUIRED,
            RiskControlRequirement.NO_DECEPTION_REQUIRED,
            RiskControlRequirement.NO_SCRAPED_LEADS_REQUIRED,
        ],
        escalation_rule="Allow only with exact manifest, target, channel, draft hash, count, stop conditions, and disclosure.",
        stop_conditions=["opt-out", "recipient asks to stop", "budget exhausted", "draft hash changes", "unapproved channel"],
        audit_ledger_required=True,
    ),
    RiskTier.TIER_3_PUBLIC_BROADCAST_OR_LANDING: RiskTierPolicy(
        tier=RiskTier.TIER_3_PUBLIC_BROADCAST_OR_LANDING,
        allowed_actions=[ActionType.PUBLISH_POST, ActionType.PUBLISH_LANDING_PAGE],
        prohibited_actions=[ActionType.COLLECT_PAYMENT, ActionType.CREATE_ACCOUNT, ActionType.EXECUTE_CONTRACT],
        required_controls=[
            RiskControlRequirement.AI_DISCLOSURE_REQUIRED,
            RiskControlRequirement.OWNER_APPROVAL_REQUIRED,
            RiskControlRequirement.DRAFT_HASH_REQUIRED,
            RiskControlRequirement.STOP_CONDITIONS_REQUIRED,
            RiskControlRequirement.ACTION_LEDGER_REQUIRED,
            RiskControlRequirement.NO_DECEPTION_REQUIRED,
        ],
        escalation_rule="Requires explicit Tier 3 publication approval.",
        stop_conditions=["publication content changes", "form/payment/account flow appears", "owner approval missing"],
        audit_ledger_required=True,
    ),
    RiskTier.TIER_4_COMMERCIAL_LEGAL_PRODUCTION_HIGH_RISK: RiskTierPolicy(
        tier=RiskTier.TIER_4_COMMERCIAL_LEGAL_PRODUCTION_HIGH_RISK,
        allowed_actions=[],
        prohibited_actions=[
            ActionType.COLLECT_PAYMENT,
            ActionType.CREATE_ACCOUNT,
            ActionType.SUBMIT_FORM,
            ActionType.EXECUTE_CONTRACT,
            ActionType.PRODUCTION_IMPLEMENTATION,
            ActionType.CORE_WRITEBACK,
        ],
        required_controls=[
            RiskControlRequirement.NO_PAYMENT_REQUIRED,
            RiskControlRequirement.NO_ACCOUNT_CREATION_REQUIRED,
            RiskControlRequirement.NO_CORE_WRITEBACK_REQUIRED,
        ],
        escalation_rule="Always blocked in E8.",
        stop_conditions=["any Tier 4 action requested"],
        audit_ledger_required=True,
    ),
}


def classify_external_action(action_type: str) -> str:
    if action_type == ActionType.INTERNAL_PREPARE:
        return RiskTier.TIER_0_INTERNAL
    if action_type == ActionType.PUBLIC_READ:
        return RiskTier.TIER_1_PUBLIC_READ_ONLY
    if action_type in {ActionType.SEND_VALIDATION_MESSAGE, ActionType.REQUEST_FEEDBACK, ActionType.COLLECT_SURVEY_RESPONSE}:
        return RiskTier.TIER_2_TRANSPARENT_LOW_RISK_EXTERNAL_VALIDATION
    if action_type in {ActionType.PUBLISH_POST, ActionType.PUBLISH_LANDING_PAGE}:
        return RiskTier.TIER_3_PUBLIC_BROADCAST_OR_LANDING
    return RiskTier.TIER_4_COMMERCIAL_LEGAL_PRODUCTION_HIGH_RISK


def required_controls_for_tier(tier: str) -> List[str]:
    policy = TIER_POLICIES.get(tier)
    return list(policy.required_controls) if policy else []


def action_type_is_allowed_in_e8(action_type: str) -> bool:
    tier = classify_external_action(action_type)
    return tier != RiskTier.TIER_4_COMMERCIAL_LEGAL_PRODUCTION_HIGH_RISK


def render_e8_risk_model_report() -> str:
    lines = [
        "# E8 Risk-Controlled External Action Model",
        "",
        "E8 asks what external action is allowed under which risk controls, not whether all external action is permanently forbidden.",
        "",
    ]
    for policy in TIER_POLICIES.values():
        lines.extend(
            [
                f"## {policy.tier}",
                f"- allowed_actions: {', '.join(policy.allowed_actions) or 'none'}",
                f"- prohibited_actions: {', '.join(policy.prohibited_actions) or 'none'}",
                f"- required_controls: {', '.join(policy.required_controls) or 'none'}",
                f"- escalation_rule: {policy.escalation_rule}",
                f"- audit_ledger_required: {policy.audit_ledger_required}",
                "### Stop Conditions",
            ]
        )
        lines.extend(f"- {item}" for item in policy.stop_conditions)
        lines.append("")
    return "\n".join(lines).rstrip()
