from __future__ import annotations

import json
from dataclasses import asdict, dataclass, field
from pathlib import Path
from typing import Any, Dict, List, Mapping


C3_NARROW_STATUS = [
    "proposed",
    "owner_review_required",
    "locally_activated_for_owner_handoff_only",
    "expired",
    "revoked",
    "rejected",
]

C3_ALLOWED_SCOPE = [
    "low_risk_validation_messaging",
    "owner_handoff_execution",
    "local_dry_run_receipt",
    "feedback_intake",
    "signal_evaluation",
    "next_action_recommendation",
]

C3_EXCLUDED_SCOPE = [
    "payment",
    "contract",
    "legal_obligation",
    "financial_commitment",
    "customer_system_access",
    "regulated_government_tax_immigration_identity_forms",
    "credential_disclosure",
    "direct_email_message_sending_by_agent",
    "publication",
    "account_creation",
    "login",
    "form_submission",
    "external_validation_submission",
    "core_brain_cieu_memory_canonical_writeback",
]


@dataclass(frozen=True)
class C3NarrowConstitutionalEnvelope:
    envelope_id: str
    source_c2_activation_id: str
    status: str
    owner_approval_evidence_present: bool
    local_activation_mode: str
    allowed_scope: List[str] = field(default_factory=lambda: list(C3_ALLOWED_SCOPE))
    excluded_scope: List[str] = field(default_factory=lambda: list(C3_EXCLUDED_SCOPE))
    scope: Dict[str, Any] = field(default_factory=dict)
    allowed_execution_modes: List[str] = field(default_factory=lambda: ["owner_handoff", "dry_run_local"])
    agent_direct_execution_allowed: bool = False
    external_action_executed: bool = False
    max_actions: int = 3
    offer_thesis: str = "48h AI Agent Implementation Readiness Review"
    required_owner_step: str = "Owner may later activate the envelope; C3 itself does not approve sending."

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


def _load_json(path: Path) -> Dict[str, Any]:
    if not path.exists():
        return {}
    return json.loads(path.read_text(encoding="utf-8"))


def build_c3_narrow_envelope(repo_root: Path) -> C3NarrowConstitutionalEnvelope:
    c2 = _load_json(repo_root / "operations" / "external_validation" / "c2_constitutional_activation_packet.json")
    owner_approved = c2.get("owner_approval_present") is True and c2.get("live_external_execution_approved") is True
    c2_scope = dict(c2.get("scope", {}))
    return C3NarrowConstitutionalEnvelope(
        envelope_id="c3_narrow_owner_handoff_only_envelope",
        source_c2_activation_id=str(c2.get("activation_id", "c2_pending_constitutional_activation")),
        status="locally_activated_for_owner_handoff_only" if not owner_approved else "owner_review_required",
        owner_approval_evidence_present=owner_approved,
        local_activation_mode="owner_handoff_only_no_agent_execute",
        max_actions=int(c2.get("scope", {}).get("max_total_actions", 3) or 3),
        scope={
            "approved_target_classes": c2_scope.get("approved_target_classes", []),
            "approved_offer_families": ["48h AI Agent Implementation Readiness Review"],
            "approved_capability_domains": ["external_validation_message"],
            "max_total_actions": min(int(c2_scope.get("max_total_actions", 3) or 3), 3),
            "stop_conditions": c2_scope.get("stop_conditions", []),
        },
    )


def validate_c3_narrow_envelope(envelope: Mapping[str, Any] | C3NarrowConstitutionalEnvelope) -> List[str]:
    data = envelope.to_dict() if isinstance(envelope, C3NarrowConstitutionalEnvelope) else dict(envelope)
    errors: List[str] = []
    if data.get("status") not in C3_NARROW_STATUS:
        errors.append("invalid_c3_envelope_status")
    if data.get("owner_approval_evidence_present") is not False:
        errors.append("c3_must_not_fake_owner_approval")
    if data.get("agent_direct_execution_allowed") is not False:
        errors.append("agent_direct_execution_must_remain_blocked")
    if data.get("external_action_executed") is not False:
        errors.append("c3_envelope_must_not_execute_external_action")
    for item in ["owner_handoff_execution", "local_dry_run_receipt", "feedback_intake", "signal_evaluation"]:
        if item not in data.get("allowed_scope", []):
            errors.append(f"missing_allowed_scope_{item}")
    for item in C3_EXCLUDED_SCOPE:
        if item not in data.get("excluded_scope", []):
            errors.append(f"missing_excluded_scope_{item}")
    if set(data.get("allowed_execution_modes", [])) - {"owner_handoff", "dry_run_local"}:
        errors.append("c3_allows_only_owner_handoff_or_dry_run_local")
    scope = dict(data.get("scope", {}))
    if scope.get("approved_capability_domains") != ["external_validation_message"]:
        errors.append("c3_scope_must_be_narrow_validation_messaging_only")
    return errors
