from __future__ import annotations

from dataclasses import asdict, dataclass
from typing import Any, Dict, List, Mapping


@dataclass(frozen=True)
class C1ActionIntentPacket:
    intent_id: str
    y_star: str
    x_t: str
    proposed_u: str
    target_class: str
    channel: str
    risk_tier: str
    capability_domain: str
    required_envelope: str
    y_gov_validation_expectation: str
    gov_mcp_execution_expectation: str
    action_ledger_schema_ref: str
    cieu_residual_semantics: str
    feedback_capture_requirement: str
    stop_conditions: List[str]
    live_execution_in_this_milestone: bool = False

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


def build_c1_action_intent_examples() -> List[C1ActionIntentPacket]:
    common = {
        "y_star": "first_governed_low_risk_external_action_cycle_ready_without_owner_as_operator",
        "x_t": "AB2 runtime contracts exist; no live external action has been approved or executed.",
        "required_envelope": "c1_owner_constitutional_envelope_request",
        "y_gov_validation_expectation": "Y*gov validates Pre-U/action packet, target class, capability domain, envelope limits, residual semantics, and hard gates.",
        "gov_mcp_execution_expectation": "gov-mcp returns allow/deny/escalate and execution receipt; no secret printing or credential disclosure.",
        "action_ledger_schema_ref": "operations/external_validation/c1_action_ledger.template.json",
        "cieu_residual_semantics": "CIEU residual compares intended governed action with actual gov-mcp receipt and feedback/no-feedback state.",
        "feedback_capture_requirement": "Feedback event is required before validation learning or E15/C2 paid-signal evaluation.",
        "stop_conditions": ["opt_out", "negative_feedback", "complaint", "budget_exceeded", "target_class_mismatch"],
    }
    return [
        C1ActionIntentPacket(
            intent_id="c1_intent_external_validation_message_001",
            proposed_u="Send one AI-transparent validation message within envelope after approval.",
            target_class="ai_consultant_agency",
            channel="approved_manual_or_governed_messaging_adapter",
            risk_tier="Tier 4/5 governed low-volume external validation",
            capability_domain="external_validation_message",
            **common,
        ),
        C1ActionIntentPacket(
            intent_id="c1_intent_low_risk_contact_form_001",
            proposed_u="Submit one low-risk commercial contact form under envelope after approval.",
            target_class="ai_heavy_team_with_agent_workflow_bottleneck",
            channel="approved_public_contact_form",
            risk_tier="Tier 4 low-risk form submission",
            capability_domain="low_risk_form_submission",
            **common,
        ),
        C1ActionIntentPacket(
            intent_id="c1_intent_publication_private_preview_001",
            proposed_u="Create governed publication draft/private preview; no public publish in this milestone.",
            target_class="public_audience_preview",
            channel="approved_private_preview_channel",
            risk_tier="Tier 3 draft/private preview",
            capability_domain="publication_draft",
            **common,
        ),
    ]


def validate_c1_action_intent_packet(packet: Mapping[str, Any] | C1ActionIntentPacket) -> List[str]:
    data = packet.to_dict() if isinstance(packet, C1ActionIntentPacket) else dict(packet)
    required = [
        "intent_id",
        "y_star",
        "x_t",
        "proposed_u",
        "target_class",
        "channel",
        "risk_tier",
        "capability_domain",
        "required_envelope",
        "y_gov_validation_expectation",
        "gov_mcp_execution_expectation",
        "action_ledger_schema_ref",
        "cieu_residual_semantics",
        "feedback_capture_requirement",
        "stop_conditions",
    ]
    errors = [f"missing_{key}" for key in required if not data.get(key)]
    if "Y*gov" not in str(data.get("y_gov_validation_expectation", "")):
        errors.append("missing_y_gov_expectation")
    if "gov-mcp" not in str(data.get("gov_mcp_execution_expectation", "")):
        errors.append("missing_gov_mcp_expectation")
    if data.get("live_execution_in_this_milestone") is not False:
        errors.append("c1_must_not_execute_live_action")
    return errors
