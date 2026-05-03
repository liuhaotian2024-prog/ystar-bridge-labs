from __future__ import annotations

from dataclasses import asdict, dataclass, field
from typing import Any, Dict, List, Mapping


HARD_GATES = [
    "payment",
    "contract",
    "legal_obligation",
    "financial_commitment",
    "customer_system_access",
    "regulated_government_tax_immigration_identity_forms",
    "credential_disclosure",
    "core_brain_cieu_memory_writeback",
    "out_of_envelope_action",
]


@dataclass(frozen=True)
class C1ConstitutionalEnvelope:
    envelope_id: str
    status: str
    validity_days: int
    max_total_actions: int
    max_actions_per_day: int
    approved_target_classes: List[str]
    approved_offer_families: List[str]
    approved_capability_domains: List[str]
    ai_transparency_required: bool
    opt_out_required: bool
    no_follow_up_unless_approved: bool
    no_attachment_unless_approved: bool
    no_tracking_link_unless_approved: bool
    action_ledger_required: bool
    feedback_event_required: bool
    stop_conditions: List[str]
    hard_owner_gates: List[str] = field(default_factory=lambda: list(HARD_GATES))
    owner_role: str = "constitutional_boundary_setter_not_operator"
    live_execution_approved: bool = False

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


def build_c1_constitutional_envelope_request() -> C1ConstitutionalEnvelope:
    return C1ConstitutionalEnvelope(
        envelope_id="c1_owner_constitutional_envelope_request",
        status="request_only_not_approval",
        validity_days=7,
        max_total_actions=3,
        max_actions_per_day=1,
        approved_target_classes=["ai_consultant_agency", "ai_heavy_team_with_agent_workflow_bottleneck"],
        approved_offer_families=["48h AI Agent Implementation Readiness Review"],
        approved_capability_domains=[
            "external_validation_message",
            "low_risk_form_submission",
            "publication_draft",
            "authenticated_draft_creation",
        ],
        ai_transparency_required=True,
        opt_out_required=True,
        no_follow_up_unless_approved=True,
        no_attachment_unless_approved=True,
        no_tracking_link_unless_approved=True,
        action_ledger_required=True,
        feedback_event_required=True,
        stop_conditions=["opt_out", "negative_feedback", "complaint", "budget_exceeded", "target_class_mismatch"],
    )


def validate_c1_constitutional_envelope(envelope: Mapping[str, Any] | C1ConstitutionalEnvelope) -> List[str]:
    data = envelope.to_dict() if isinstance(envelope, C1ConstitutionalEnvelope) else dict(envelope)
    errors: List[str] = []
    if data.get("status") != "request_only_not_approval":
        errors.append("envelope_must_be_request_only_until_owner_approves")
    if data.get("validity_days") != 7:
        errors.append("validity_days_must_be_7")
    if data.get("max_total_actions") != 3:
        errors.append("max_total_actions_must_be_3")
    if data.get("max_actions_per_day") != 1:
        errors.append("max_actions_per_day_must_be_1")
    for flag in [
        "ai_transparency_required",
        "opt_out_required",
        "no_follow_up_unless_approved",
        "no_attachment_unless_approved",
        "no_tracking_link_unless_approved",
        "action_ledger_required",
        "feedback_event_required",
    ]:
        if data.get(flag) is not True:
            errors.append(f"{flag}_must_be_true")
    if data.get("live_execution_approved") is not False:
        errors.append("c1_request_must_not_approve_live_execution")
    for gate in HARD_GATES:
        if gate not in data.get("hard_owner_gates", []):
            errors.append(f"missing_hard_gate_{gate}")
    return errors
