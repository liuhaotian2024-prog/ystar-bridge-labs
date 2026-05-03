from __future__ import annotations

from dataclasses import asdict, dataclass, field
from typing import Any, Dict, List, Mapping

from office.mission_command.b2r_capability_domains import domain_by_id


@dataclass(frozen=True)
class B2RActionPacket:
    intent_id: str
    y_star: str
    domain_id: str
    capability_level: int
    action_summary: str
    envelope_id: str
    y_gov_validation_ref: str
    gov_mcp_contract_ref: str
    action_ledger_schema_ref: str
    cieu_residual_semantics: str
    stop_conditions: List[str] = field(default_factory=list)
    no_live_action_in_this_milestone: bool = True

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


def build_action_packet(domain_id: str, overrides: Mapping[str, Any] | None = None) -> B2RActionPacket:
    overrides = dict(overrides or {})
    domain = domain_by_id(domain_id)
    return B2RActionPacket(
        intent_id=str(overrides.get("intent_id") or f"b2r_intent_{domain_id}"),
        y_star=str(overrides.get("y_star") or "governed_progressive_external_action_with_minimum_residual"),
        domain_id=domain_id,
        capability_level=domain.level,
        action_summary=str(overrides.get("action_summary") or f"Preflight governed capability domain {domain_id}."),
        envelope_id=str(overrides.get("envelope_id") or "b2r_owner_constitutional_envelope_request"),
        y_gov_validation_ref=str(overrides.get("y_gov_validation_ref") or "Y-star-gov::Pre-U/action_packet_validator_profile_required"),
        gov_mcp_contract_ref=str(overrides.get("gov_mcp_contract_ref") or "gov-mcp::execute_or_deny_contract_required"),
        action_ledger_schema_ref=str(overrides.get("action_ledger_schema_ref") or "b2r_action_ledger_schema"),
        cieu_residual_semantics=domain.cieu_residual_semantics,
        stop_conditions=list(overrides.get("stop_conditions") or domain.escalation_triggers),
    )


def validate_action_packet(packet: Mapping[str, Any] | B2RActionPacket) -> List[str]:
    data = packet.to_dict() if isinstance(packet, B2RActionPacket) else dict(packet)
    required = [
        "intent_id",
        "y_star",
        "domain_id",
        "capability_level",
        "action_summary",
        "envelope_id",
        "y_gov_validation_ref",
        "gov_mcp_contract_ref",
        "action_ledger_schema_ref",
        "cieu_residual_semantics",
    ]
    errors = [f"missing_{key}" for key in required if not data.get(key)]
    if not str(data.get("y_gov_validation_ref", "")).startswith("Y-star-gov::"):
        errors.append("action_packet_requires_y_star_gov_validation_reference")
    if "gov-mcp" not in str(data.get("gov_mcp_contract_ref", "")):
        errors.append("action_packet_requires_gov_mcp_contract_reference")
    if data.get("no_live_action_in_this_milestone") is not True:
        errors.append("b2r_milestone_must_not_execute_live_action")
    try:
        domain = domain_by_id(str(data.get("domain_id")))
        if int(data.get("capability_level")) != domain.level:
            errors.append("capability_level_mismatch")
    except Exception:
        errors.append("unknown_domain_id")
    return list(dict.fromkeys(errors))
