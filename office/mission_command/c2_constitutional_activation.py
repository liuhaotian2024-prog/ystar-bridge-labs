from __future__ import annotations

import json
from dataclasses import asdict, dataclass, field
from pathlib import Path
from typing import Any, Dict, List, Mapping

from office.mission_command.c1_constitutional_envelope import HARD_GATES, build_c1_constitutional_envelope_request


ACTIVATION_STATUSES = [
    "proposed_envelope",
    "owner_review_required",
    "activated_envelope",
    "expired_envelope",
    "revoked_envelope",
    "scope_limited_envelope",
    "action_domain_specific_envelope",
]

PROGRESSIVE_ACTION_DOMAINS = [
    "low_risk_validation_messaging",
    "public_readonly_research",
    "low_risk_publication_draft_preparation",
    "account_creation_proposal",
    "login_proposal",
    "form_preparation_proposal",
    "non_binding_customer_discovery",
    "owner_approved_manual_send_owner_handoff",
]


@dataclass(frozen=True)
class C2ConstitutionalActivationPacket:
    activation_id: str
    source_envelope_id: str
    status: str
    activation_state: str
    owner_approval_present: bool
    live_external_execution_approved: bool
    scope: Dict[str, Any]
    owner_hard_gates: List[str] = field(default_factory=lambda: list(HARD_GATES))
    progressive_action_domains: List[str] = field(default_factory=lambda: list(PROGRESSIVE_ACTION_DOMAINS))
    allowed_without_activation: List[str] = field(
        default_factory=lambda: [
            "decision_simulation",
            "owner_handoff_capsule_generation",
            "governed_action_queue_preparation",
            "feedback_schema_preparation",
            "dry_run_local_receipt_generation",
        ]
    )
    external_action_executed: bool = False

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


def _load_json(path: Path) -> Dict[str, Any]:
    if not path.exists():
        return {}
    return json.loads(path.read_text(encoding="utf-8"))


def build_c2_activation_packet(repo_root: Path | None = None) -> C2ConstitutionalActivationPacket:
    root = repo_root or Path(__file__).resolve().parents[2]
    envelope_path = root / "operations" / "external_validation" / "c1_owner_constitutional_envelope.request.json"
    source = _load_json(envelope_path) or build_c1_constitutional_envelope_request().to_dict()
    owner_approved = source.get("status") in {"owner_approved", "activated_envelope"} and source.get("live_execution_approved") is True
    status = "activated_envelope" if owner_approved else "owner_review_required"
    return C2ConstitutionalActivationPacket(
        activation_id="c2_pending_constitutional_activation",
        source_envelope_id=str(source.get("envelope_id", "c1_owner_constitutional_envelope_request")),
        status=status,
        activation_state="active_scope_limited" if owner_approved else "pending_owner_activation",
        owner_approval_present=owner_approved,
        live_external_execution_approved=owner_approved,
        scope={
            "validity_days": source.get("validity_days", 7),
            "max_total_actions": source.get("max_total_actions", 3),
            "max_actions_per_day": source.get("max_actions_per_day", 1),
            "approved_target_classes": source.get("approved_target_classes", []),
            "approved_offer_families": source.get("approved_offer_families", []),
            "approved_capability_domains": source.get("approved_capability_domains", []),
            "stop_conditions": source.get("stop_conditions", []),
            "ai_transparency_required": source.get("ai_transparency_required") is True,
            "opt_out_required": source.get("opt_out_required") is True,
            "action_ledger_required": source.get("action_ledger_required") is True,
            "feedback_event_required": source.get("feedback_event_required") is True,
        },
        owner_hard_gates=list(source.get("hard_owner_gates") or HARD_GATES),
    )


def validate_c2_activation_packet(packet: Mapping[str, Any] | C2ConstitutionalActivationPacket) -> List[str]:
    data = packet.to_dict() if isinstance(packet, C2ConstitutionalActivationPacket) else dict(packet)
    errors: List[str] = []
    if data.get("status") not in ACTIVATION_STATUSES:
        errors.append("invalid_activation_status")
    if data.get("owner_approval_present") is True and data.get("live_external_execution_approved") is not True:
        errors.append("activated_envelope_requires_live_execution_approval")
    if data.get("owner_approval_present") is False and data.get("external_action_executed") is not False:
        errors.append("pending_activation_must_not_execute_external_action")
    hard_gates = set(data.get("owner_hard_gates", []))
    for gate in HARD_GATES:
        if gate not in hard_gates:
            errors.append(f"missing_owner_hard_gate_{gate}")
    allowed_without_activation = set(data.get("allowed_without_activation", []))
    for allowed in ["decision_simulation", "owner_handoff_capsule_generation", "governed_action_queue_preparation"]:
        if allowed not in allowed_without_activation:
            errors.append(f"missing_pending_allowed_{allowed}")
    return errors
