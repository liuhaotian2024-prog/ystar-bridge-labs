from __future__ import annotations

from dataclasses import asdict, dataclass
from typing import Any, Dict, List, Mapping


HARD_OWNER_GATE_DOMAINS = {"payment_or_contract_gate", "core_writeback_gate"}
FINANCIAL_LEGAL_FORM_CATEGORIES = {
    "financial_submit",
    "legal_commitment_submit",
    "regulated_submit",
    "government_form",
    "tax_form",
    "immigration_form",
    "identity_form",
}


@dataclass(frozen=True)
class CapabilityDomain:
    domain_id: str
    level: int
    allowed_actions: List[str]
    denied_actions: List[str]
    required_envelope_fields: List[str]
    pre_u_action_packet_fields: List[str]
    y_gov_validation_expectation: str
    gov_mcp_execution_contract: str
    action_ledger_requirement: str
    cieu_residual_semantics: str
    rollback_or_takedown_requirement: str
    escalation_triggers: List[str]
    owner_role: str

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


@dataclass(frozen=True)
class CapabilityDecision:
    domain_id: str
    level: int
    allowed: bool
    denied: bool
    escalated: bool
    decision: str
    reason_codes: List[str]
    owner_hard_approval_required: bool
    y_gov_validation_required: bool
    gov_mcp_execution_required: bool
    action_ledger_required: bool
    cieu_residual_required: bool
    no_live_action_executed: bool = True

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


def build_capability_domains() -> List[CapabilityDomain]:
    return [
        CapabilityDomain(
            "public_readonly_observation",
            1,
            ["read_public_page", "read_public_doc", "read_public_pricing", "read_public_forum"],
            ["login", "submit", "message", "publish", "payment"],
            ["source_url", "access_mode", "no_login", "read_only_budget"],
            ["intent_id", "y_star", "domain_id", "source_policy", "residual_hypothesis"],
            "Y*gov verifies public-only, no-login, no-contact, no-submit boundaries.",
            "gov-mcp may fetch/read only allowlisted public sources and returns receipts.",
            "receipt ledger required for collected evidence; no action ledger because no external action is executed.",
            "Residual compares evidence found vs evidence needed; public evidence cannot become validation feedback.",
            "Not applicable except source removal from report if invalid.",
            ["login_required", "paywall", "robots_or_access_restriction", "private_data_detected"],
            "owner sets research boundary, not per-page operation.",
        ),
        CapabilityDomain(
            "authenticated_readonly_observation",
            2,
            ["login_readonly", "view_dashboard", "view_authorized_inbox_state"],
            ["modify", "draft_submit", "send", "publish", "payment"],
            ["credential_vault_ref", "account_identity", "allowed_accounts", "session_scope", "session_duration_minutes"],
            ["intent_id", "y_star", "domain_id", "account_ref", "read_scope", "privacy_boundary"],
            "Y*gov validates authenticated session capability and read-only scope.",
            "gov-mcp opens or denies session through credential-safe adapter; no secret printing.",
            "session action ledger required.",
            "Residual records whether authorized read-only state answered the mission question.",
            "Logout/session cleanup required where applicable.",
            ["credential_missing", "mfa_required", "scope_requests_write", "private_unapproved_data"],
            "owner approves constitutional account envelope, not each readonly view.",
        ),
        CapabilityDomain(
            "authenticated_draft_creation",
            3,
            ["create_draft", "edit_draft", "fill_without_submit"],
            ["submit", "send", "publish_public", "payment"],
            ["credential_vault_ref", "account_identity", "draft_mode", "no_submit", "draft_storage_ref"],
            ["intent_id", "y_star", "domain_id", "draft_hash", "no_submit_assertion"],
            "Y*gov validates draft-only mode and claim boundaries.",
            "gov-mcp may create/edit drafts but must not submit or publish.",
            "draft ledger required with hash and storage ref.",
            "Residual tracks draft readiness vs intended external action.",
            "Draft delete/revert plan required.",
            ["submit_button_required", "claim_boundary_failure", "unexpected_public_visibility"],
            "owner approves account/channel envelope and high-claim exceptions.",
        ),
        CapabilityDomain(
            "form_fill_draft",
            3,
            ["fill_form_draft", "save_form_draft"],
            ["submit_form", "regulated_submit", "payment"],
            ["form_url", "form_category", "draft_only", "no_submit", "field_manifest"],
            ["intent_id", "y_star", "domain_id", "form_category", "field_manifest_hash"],
            "Y*gov classifies form category and verifies draft-only status.",
            "gov-mcp may fill/save draft fields where adapter supports no-submit.",
            "form draft ledger required.",
            "Residual records completion of draft vs safe submit readiness.",
            "Clear/reset draft plan required.",
            ["submit_required_to_save", "regulated_field_detected", "identity_or_payment_field_detected"],
            "owner handles regulated/financial/legal exceptions only.",
        ),
        CapabilityDomain(
            "low_risk_form_submission",
            4,
            ["submit_low_risk_interest_form", "submit_commercial_contact_form_under_envelope"],
            ["financial_submit", "legal_commitment_submit", "regulated_submit", "government_form"],
            ["form_url", "form_category", "approved_envelope_id", "y_gov_validation_ref", "gov_mcp_contract_ref", "message_hash"],
            ["intent_id", "y_star", "domain_id", "form_category", "submit_rationale", "stop_conditions"],
            "Y*gov validates low-risk form category, envelope, message hash, and stop conditions.",
            "gov-mcp executes submit or denies with normalized receipt.",
            "external action ledger required.",
            "Residual tracks submitted action outcome and follow-up feedback requirement.",
            "Withdrawal/correction path required where available.",
            ["regulated_form", "financial_or_legal_field", "identity_field", "budget_exceeded", "out_of_envelope"],
            "owner is not required for low-risk envelope-compliant submit; hard gate for legal/financial/regulated.",
        ),
        CapabilityDomain(
            "publication_draft",
            3,
            ["create_publication_draft", "private_preview"],
            ["public_publish", "high_claim_publication", "legal_claim_publication"],
            ["channel_ref", "draft_hash", "publication_mode", "claim_boundary_check"],
            ["intent_id", "y_star", "domain_id", "draft_hash", "claim_boundary"],
            "Y*gov validates draft/private-preview status and claim boundary.",
            "gov-mcp may create private draft/preview only.",
            "draft ledger required.",
            "Residual tracks draft clarity and risk reduction.",
            "Delete/revert draft plan required.",
            ["public_visibility", "high_claim_detected", "unapproved_channel"],
            "owner approves brand constitution and high-claim exceptions.",
        ),
        CapabilityDomain(
            "governed_publication",
            4,
            ["publish_to_approved_channel", "update_approved_public_content"],
            ["high_claim_publication", "legal_claim_publication", "financial_claim_publication"],
            ["channel_allowlist", "message_hash", "claim_boundary_passed", "frequency_cap", "takedown_plan", "approved_envelope_id"],
            ["intent_id", "y_star", "domain_id", "publication_claims", "rollback_plan", "frequency_state"],
            "Y*gov validates channel, claims, frequency, transparency, and takedown plan.",
            "gov-mcp publishes or denies and returns publication receipt.",
            "external action ledger required.",
            "Residual tracks response, correction needs, and claim risk.",
            "Takedown/update plan required before publish.",
            ["high_claim", "frequency_cap_exceeded", "missing_takedown_plan", "negative_feedback"],
            "owner sets brand/claim constitution; not every approved-channel post.",
        ),
        CapabilityDomain(
            "low_risk_account_creation",
            4,
            ["create_internal_test_account", "create_vendor_trial_account"],
            ["payment_account", "contract_account", "kyc_account", "customer_identity_account"],
            ["account_category", "identity_binding", "no_payment", "no_contract", "no_kyc", "approved_vendor_envelope"],
            ["intent_id", "y_star", "domain_id", "account_category", "identity_binding"],
            "Y*gov validates identity binding, cost/legal/KYC absence, and vendor envelope.",
            "gov-mcp creates or denies account and returns receipt; no credential disclosure.",
            "account action ledger required.",
            "Residual tracks account utility vs lifecycle cleanup burden.",
            "Close/delete account plan required.",
            ["payment_required", "contract_required", "kyc_required", "customer_representation_required"],
            "owner approves identity/vendor constitution and all payment/legal/KYC cases.",
        ),
        CapabilityDomain(
            "external_validation_message",
            5,
            ["send_ai_transparent_validation_message"],
            ["bulk_outreach", "nontransparent_message", "automated_followup", "tracking_link_without_approval"],
            ["approved_envelope_id", "approved_target_class", "draft_family", "max_sends", "ai_transparency", "opt_out_language", "suppression_check"],
            ["intent_id", "y_star", "domain_id", "target_class", "draft_hash", "stop_conditions"],
            "Y*gov validates envelope, target class, draft family, max sends, transparency, opt-out, and suppression.",
            "gov-mcp sends or denies through approved messaging adapter and returns action receipt.",
            "external action ledger required before feedback/no-response can be counted.",
            "Residual tracks feedback vs validation question; feedback may become CIEU delta candidate.",
            "Stop/suppress/takedown where applicable; no automated follow-up unless envelope allows.",
            ["opt_out", "negative_feedback", "complaint", "budget_exceeded", "target_class_mismatch"],
            "owner sets validation constitution; Y*gov governs low-volume envelope-compliant sends.",
        ),
        CapabilityDomain(
            "feedback_capture",
            5,
            ["record_feedback_event", "classify_feedback_signal"],
            ["invent_feedback", "public_evidence_as_feedback", "core_writeback"],
            ["action_id", "feedback_source", "recorded_by", "feedback_summary", "limitations"],
            ["intent_id", "y_star", "domain_id", "action_id", "feedback_classification"],
            "Y*gov validates feedback provenance and learning eligibility.",
            "gov-mcp normalizes capture receipt; persistent writes remain gated.",
            "feedback ledger required.",
            "Residual compares expected feedback signal with actual feedback.",
            "Correction/deletion path for invalid feedback required.",
            ["missing_action_id", "invented_feedback", "public_evidence_source", "core_writeback_requested"],
            "owner only handles disputed/high-risk feedback interpretation.",
        ),
        CapabilityDomain(
            "payment_or_contract_gate",
            6,
            ["request_owner_payment_or_contract_approval"],
            ["auto_pay", "auto_collect_payment", "auto_sign_contract", "financial_commitment"],
            ["owner_explicit_approval_id", "legal_or_financial_review_ref"],
            ["intent_id", "y_star", "domain_id", "hard_gate_reason"],
            "Y*gov must deny automatic execution and escalate owner.",
            "gov-mcp must refuse execution without explicit owner approval.",
            "escalation ledger required; no execution ledger without owner action.",
            "Residual remains open until owner decision.",
            "Not applicable; no autonomous execution.",
            ["payment", "contract", "legal_obligation", "financial_commitment"],
            "owner hard approval required.",
        ),
        CapabilityDomain(
            "core_writeback_gate",
            6,
            ["request_cieu_or_brain_writeback_review"],
            ["auto_core_writeback", "uncurated_brain_writeback", "direct_memory_mutation"],
            ["cieu_delta_ref", "learning_eligibility", "owner_or_governance_promotion_ref"],
            ["intent_id", "y_star", "domain_id", "learning_candidate_ref"],
            "Y*gov must validate CIEU delta and learning eligibility before any persistent promotion.",
            "gov-mcp must not write core brain/CIEU/memory directly.",
            "learning review ledger required.",
            "Residual tracks learning candidate vs approved canonical update.",
            "Rollback requires canonical memory governance.",
            ["uncurated_writeback", "missing_cieu_delta", "raw_artifact_learning_source"],
            "owner or constitutional governance approval required for canonical writeback.",
        ),
    ]


def domain_by_id(domain_id: str) -> CapabilityDomain:
    for domain in build_capability_domains():
        if domain.domain_id == domain_id:
            return domain
    raise KeyError(domain_id)


def evaluate_capability_action(domain_id: str, envelope: Mapping[str, Any] | None = None) -> CapabilityDecision:
    envelope = dict(envelope or {})
    domain = domain_by_id(domain_id)
    reasons: List[str] = []
    escalated = False
    owner_required = False

    missing = [field for field in domain.required_envelope_fields if not envelope.get(field)]
    if missing:
        reasons.extend(f"missing_{field}" for field in missing)

    if domain_id in HARD_OWNER_GATE_DOMAINS:
        reasons.append("owner_hard_gate")
        escalated = True
        owner_required = True

    if domain_id == "public_readonly_observation":
        if envelope.get("requires_login") or envelope.get("external_side_effect"):
            reasons.append("not_public_readonly")

    if domain_id == "authenticated_readonly_observation":
        if not envelope.get("credential_vault_ref"):
            reasons.append("credential_missing")
        if envelope.get("session_scope") != "read_only":
            reasons.append("scope_not_read_only")

    if domain_id == "authenticated_draft_creation":
        if envelope.get("no_submit") is not True or envelope.get("draft_mode") is not True:
            reasons.append("draft_only_boundary_missing")

    if domain_id == "form_fill_draft":
        if envelope.get("no_submit") is not True or envelope.get("draft_only") is not True:
            reasons.append("form_draft_only_boundary_missing")

    if domain_id == "low_risk_form_submission":
        category = str(envelope.get("form_category", ""))
        if category in FINANCIAL_LEGAL_FORM_CATEGORIES:
            reasons.append("financial_legal_or_regulated_form_hard_gate")
            escalated = True
            owner_required = True
        if category not in {"low_risk_submit", "commercial_contact_submit"}:
            reasons.append("form_category_not_low_risk")

    if domain_id == "publication_draft":
        if envelope.get("publication_mode") not in {"draft_only", "private_preview"}:
            reasons.append("publication_not_draft_or_private_preview")

    if domain_id == "governed_publication":
        if envelope.get("high_claim") is True:
            reasons.append("high_claim_publication_escalates")
            escalated = True
        if envelope.get("frequency_ok") is not True:
            reasons.append("frequency_cap_missing_or_exceeded")
        if envelope.get("claim_boundary_passed") is not True:
            reasons.append("claim_boundary_not_passed")

    if domain_id == "low_risk_account_creation":
        category = str(envelope.get("account_category", ""))
        if category in {"payment_account", "contract_account", "kyc_account", "regulated_identity_account"}:
            reasons.append("payment_contract_or_kyc_account_hard_gate")
            escalated = True
            owner_required = True
        if envelope.get("no_payment") is not True or envelope.get("no_contract") is not True or envelope.get("no_kyc") is not True:
            reasons.append("cost_legal_or_kyc_boundary_missing")

    if domain_id == "external_validation_message":
        if envelope.get("ai_transparency") is not True:
            reasons.append("ai_transparency_required")
        if envelope.get("opt_out_language") is not True:
            reasons.append("opt_out_language_required")
        if envelope.get("suppression_check") is not True:
            reasons.append("suppression_check_required")
        if int(envelope.get("max_sends", 0) or 0) > int(envelope.get("approved_max_sends", 0) or 0):
            reasons.append("budget_exceeded")
        if envelope.get("target_class") != envelope.get("approved_target_class"):
            reasons.append("target_class_mismatch")

    if domain_id == "feedback_capture":
        if envelope.get("feedback_source") == "public_evidence":
            reasons.append("public_evidence_is_not_validation_feedback")
        if not envelope.get("action_id"):
            reasons.append("missing_action_id")

    denied = bool(reasons) and not (domain_id == "governed_publication" and reasons == ["high_claim_publication_escalates"])
    if escalated:
        decision = "escalate"
        allowed = False
    elif denied:
        decision = "deny"
        allowed = False
    else:
        decision = "allow"
        allowed = True

    return CapabilityDecision(
        domain_id=domain_id,
        level=domain.level,
        allowed=allowed,
        denied=denied,
        escalated=escalated,
        decision=decision,
        reason_codes=list(dict.fromkeys(reasons)),
        owner_hard_approval_required=owner_required,
        y_gov_validation_required=True,
        gov_mcp_execution_required=domain.level >= 2,
        action_ledger_required=domain.level >= 3,
        cieu_residual_required=True,
    )


def public_evidence_is_validation_feedback() -> bool:
    return False


def stop_required_for_event(event_type: str) -> bool:
    return event_type in {"opt_out", "negative_feedback", "complaint", "budget_exceeded", "target_class_mismatch"}
