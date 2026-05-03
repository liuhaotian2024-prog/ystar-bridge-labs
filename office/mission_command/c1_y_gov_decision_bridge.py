from __future__ import annotations

from dataclasses import asdict, dataclass
from typing import Any, Dict, Mapping

from office.mission_command.c1_action_intent_packet import validate_c1_action_intent_packet
from office.mission_command.c1_constitutional_envelope import HARD_GATES, validate_c1_constitutional_envelope


@dataclass(frozen=True)
class C1YGovDecision:
    decision_id: str
    decision: str
    allowed: bool
    denied: bool
    escalated: bool
    reason_code: str
    executes_action: bool = False

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


def evaluate_y_gov_decision(packet: Mapping[str, Any], envelope: Mapping[str, Any] | None) -> C1YGovDecision:
    if envelope is None:
        return C1YGovDecision("c1_y_gov_decision_missing_envelope", "deny", False, True, False, "blocked_no_envelope")
    envelope_errors = validate_c1_constitutional_envelope(envelope)
    packet_errors = validate_c1_action_intent_packet(packet)
    if envelope_errors:
        return C1YGovDecision("c1_y_gov_decision_invalid_envelope", "deny", False, True, False, "invalid_envelope")
    if packet_errors:
        return C1YGovDecision("c1_y_gov_decision_invalid_packet", "deny", False, True, False, "invalid_action_packet")
    text = " ".join(
        str(packet.get(key, "")).lower()
        for key in ["proposed_u", "capability_domain", "channel", "risk_tier", "target_class"]
    )
    if any(gate.replace("_", " ") in text or gate in text for gate in HARD_GATES):
        return C1YGovDecision("c1_y_gov_decision_hard_gate", "escalate", False, False, True, "owner_hard_gate")
    if packet.get("capability_domain") not in envelope.get("approved_capability_domains", []):
        return C1YGovDecision("c1_y_gov_decision_domain_mismatch", "deny", False, True, False, "capability_domain_not_in_envelope")
    if packet.get("target_class") not in envelope.get("approved_target_classes", []) and packet.get("capability_domain") != "publication_draft":
        return C1YGovDecision("c1_y_gov_decision_target_mismatch", "deny", False, True, False, "target_class_not_in_envelope")
    return C1YGovDecision("c1_y_gov_decision_allow_readiness", "allow_readiness_only", True, False, False, "ready_for_gov_mcp_preflight")
