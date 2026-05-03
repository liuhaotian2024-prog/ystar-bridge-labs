from __future__ import annotations

from dataclasses import asdict, dataclass
from typing import Any, Dict, List

from office.mission_command.b2r_capability_domains import build_capability_domains, domain_by_id


@dataclass(frozen=True)
class ProgressiveUnlockLevel:
    level: int
    name: str
    capability_domains: List[str]
    eligibility_criteria: List[str]
    required_evidence: List[str]
    required_envelope: str
    y_gov_validation_requirement: str
    gov_mcp_execution_requirement: str
    audit_requirement: str
    rollback_requirement: str
    stop_conditions: List[str]
    owner_role: str

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


def build_progressive_unlock_levels() -> List[ProgressiveUnlockLevel]:
    return [
        ProgressiveUnlockLevel(0, "internal_only", [], ["repo/test/report only"], ["local evidence"], "none", "standard CZL", "none", "git/test audit", "git revert via normal review", ["dirty repo", "test failure"], "not a micro-operator"),
        ProgressiveUnlockLevel(1, "public_read_only", ["public_readonly_observation"], ["public source", "no login", "no side effect"], ["source receipts"], "public source policy", "public-only preflight", "optional read adapter", "evidence receipts", "remove invalid evidence", ["login required", "private data"], "sets research boundary"),
        ProgressiveUnlockLevel(2, "authenticated_read_only", ["authenticated_readonly_observation"], ["valid credential vault ref", "readonly scope"], ["session ledger"], "authenticated session envelope", "session capability validation", "session open/read/deny contract", "session action ledger", "logout/session cleanup", ["credential missing", "MFA required", "write scope"], "approves account constitution"),
        ProgressiveUnlockLevel(3, "authenticated_draft_or_form_fill", ["authenticated_draft_creation", "form_fill_draft", "publication_draft"], ["draft-only", "no submit", "claim boundary"], ["draft hash"], "draft/action envelope", "draft-only validation", "draft create/edit contract", "draft ledger", "delete/revert draft", ["submit required", "public visibility"], "approves channel constitution"),
        ProgressiveUnlockLevel(4, "low_risk_submit_or_publication", ["low_risk_form_submission", "governed_publication", "low_risk_account_creation"], ["approved envelope", "low-risk category", "rollback plan"], ["action receipts"], "low-risk action envelope", "action packet validation", "execute/deny contract", "action ledger", "withdraw/takedown/close", ["high claim", "regulated form", "payment required"], "hard exceptions only"),
        ProgressiveUnlockLevel(5, "external_validation_messaging", ["external_validation_message", "feedback_capture"], ["AI transparency", "max sends", "suppression", "feedback capture"], ["message/action/feedback ledger"], "validation messaging envelope", "target/draft/stop validation", "send-or-deny contract", "action and feedback ledger", "suppression/stop", ["opt-out", "negative feedback", "complaint"], "sets validation constitution"),
        ProgressiveUnlockLevel(6, "financial_legal_customer_system_core_writeback_hard_gate", ["payment_or_contract_gate", "core_writeback_gate"], ["explicit owner approval"], ["approval and review refs"], "hard-gate envelope", "deny/escalate", "deny without owner approval", "escalation ledger", "no autonomous rollback because no action", ["payment", "contract", "legal", "customer system", "core writeback"], "explicit hard approval required"),
    ]


def build_progressive_unlock_matrix() -> Dict[str, Any]:
    return {
        "levels": [level.to_dict() for level in build_progressive_unlock_levels()],
        "domains": [domain.to_dict() for domain in build_capability_domains()],
    }


def level_for_domain(domain_id: str) -> int:
    return domain_by_id(domain_id).level


def owner_required_for_every_micro_action(domain_id: str) -> bool:
    return domain_by_id(domain_id).level >= 6
