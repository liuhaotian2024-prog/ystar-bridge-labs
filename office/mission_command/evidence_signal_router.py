from __future__ import annotations

from dataclasses import asdict, dataclass
from enum import Enum
from typing import Any, Dict


class EvidenceSignalType(str, Enum):
    INTERNAL_HYPOTHESIS = "internal_hypothesis"
    PUBLIC_MARKET_EVIDENCE = "public_market_evidence"
    EXTERNAL_PATTERN_EVIDENCE = "external_pattern_evidence"
    PUBLIC_TARGET_DISCOVERY_EVIDENCE = "public_target_discovery_evidence"
    VALIDATION_FEEDBACK = "validation_feedback"
    PAID_SIGNAL = "paid_signal"
    GOVERNANCE_EVIDENCE = "governance_evidence"
    BRAIN_LEARNING_CANDIDATE = "brain_learning_candidate"


class EvidenceClaimType(str, Enum):
    MARKET_THESIS = "market_thesis"
    VALIDATION_RESULT = "validation_result"
    PAID_PILOT_PREP = "paid_pilot_prep"
    PAID_SIGNAL_CLAIM = "paid_signal_claim"
    BRAIN_WRITEBACK = "brain_writeback"


@dataclass(frozen=True)
class EvidenceRoutingDecision:
    evidence_type: EvidenceSignalType
    claim_type: EvidenceClaimType
    allowed: bool
    blocked_reason: str
    required_upgrade: str

    def to_dict(self) -> Dict[str, Any]:
        data = asdict(self)
        data["evidence_type"] = self.evidence_type.value
        data["claim_type"] = self.claim_type.value
        return data


def route_evidence_signal(evidence_type: EvidenceSignalType | str, claim_type: EvidenceClaimType | str) -> EvidenceRoutingDecision:
    evidence = EvidenceSignalType(evidence_type)
    claim = EvidenceClaimType(claim_type)
    if claim == EvidenceClaimType.MARKET_THESIS:
        allowed = evidence in {
            EvidenceSignalType.PUBLIC_MARKET_EVIDENCE,
            EvidenceSignalType.PUBLIC_TARGET_DISCOVERY_EVIDENCE,
            EvidenceSignalType.EXTERNAL_PATTERN_EVIDENCE,
            EvidenceSignalType.VALIDATION_FEEDBACK,
            EvidenceSignalType.PAID_SIGNAL,
        }
        return EvidenceRoutingDecision(evidence, claim, allowed, "" if allowed else "market_thesis_requires_external_or_feedback_evidence", "public evidence")
    if claim == EvidenceClaimType.VALIDATION_RESULT:
        allowed = evidence in {EvidenceSignalType.VALIDATION_FEEDBACK, EvidenceSignalType.PAID_SIGNAL}
        return EvidenceRoutingDecision(evidence, claim, allowed, "" if allowed else "validation_result_requires_feedback_or_paid_signal", "validation_feedback")
    if claim in {EvidenceClaimType.PAID_PILOT_PREP, EvidenceClaimType.PAID_SIGNAL_CLAIM}:
        allowed = evidence == EvidenceSignalType.PAID_SIGNAL
        return EvidenceRoutingDecision(evidence, claim, allowed, "" if allowed else "paid_pilot_or_paid_signal_requires_paid_signal_evidence", "paid_signal")
    if claim == EvidenceClaimType.BRAIN_WRITEBACK:
        allowed = evidence == EvidenceSignalType.BRAIN_LEARNING_CANDIDATE
        return EvidenceRoutingDecision(evidence, claim, allowed, "" if allowed else "brain_writeback_requires_brain_learning_candidate_then_CIEU_gate", "CIEU_prediction_delta")
    return EvidenceRoutingDecision(evidence, claim, False, "unknown_claim_type", "owner_review")


def evidence_supports_claim(evidence_type: EvidenceSignalType | str, claim_type: EvidenceClaimType | str) -> bool:
    return route_evidence_signal(evidence_type, claim_type).allowed

