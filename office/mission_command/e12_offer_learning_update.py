from __future__ import annotations

from dataclasses import asdict, dataclass
from typing import Any, Dict

from .evidence_signal_router import EvidenceClaimType, EvidenceSignalType, route_evidence_signal
from .learning_writeback_router import LearningDestination, LearningSource, route_learning_writeback
from .e12_signal_evaluator import E12SignalEvaluation


@dataclass(frozen=True)
class E12OfferLearningUpdate:
    top_offer: str
    top_segment: str
    signal_classification: str
    supports_48h_blueprint: str
    supports_agency_segment: str
    supports_pricing_hypothesis: str
    blueprint_vs_implementation_learning: str
    trust_gap_learning: str
    recommended_next_step: str
    evidence_router_allows_validation_claim: bool
    learning_writeback_allowed: bool

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


def build_e12_offer_learning_update(evaluation: E12SignalEvaluation) -> E12OfferLearningUpdate:
    validation_evidence = route_evidence_signal(EvidenceSignalType.VALIDATION_FEEDBACK, EvidenceClaimType.VALIDATION_RESULT)
    writeback = route_learning_writeback(LearningSource.REPORT_ONLY_LEARNING, LearningDestination.BRAIN_GRAPH)
    if evaluation.classification == "strong_positive":
        next_step = "approve_E13_paid_signal_or_pilot_prep"
        supports = "supported_by_valid_feedback"
        pricing = "credible_if_price_or_would_pay_signal_present"
    elif evaluation.classification == "weak_positive":
        next_step = "approve_second_validation_batch"
        supports = "partially_supported_more_signal_needed"
        pricing = "not_yet_supported"
    elif evaluation.classification in {"negative", "mixed"}:
        next_step = "revise_offer_and_rerun_validation"
        supports = "not_supported_or_mixed"
        pricing = "not_supported"
    elif evaluation.classification in {"blocked_no_execution", "no_feedback_yet", "invalid_feedback"}:
        next_step = "provide_valid_E12_approval_and_feedback"
        supports = "no_real_feedback_yet"
        pricing = "no_real_feedback_yet"
    else:
        next_step = "hold_or_request_more_feedback"
        supports = "insufficient_signal"
        pricing = "insufficient_signal"
    return E12OfferLearningUpdate(
        top_offer="48h AI Ops Operating Room Blueprint",
        top_segment="AI consultants/agencies needing governance layer",
        signal_classification=evaluation.classification,
        supports_48h_blueprint=supports,
        supports_agency_segment=supports,
        supports_pricing_hypothesis=pricing,
        blueprint_vs_implementation_learning="do_not_change_without_feedback" if "feedback" in supports or "no_real" in supports else "inspect_feedback_for_blueprint_vs_implementation_preference",
        trust_gap_learning="unmeasured_without_valid_feedback" if evaluation.classification in {"blocked_no_execution", "no_feedback_yet", "invalid_feedback"} else "classify_from_feedback_summary",
        recommended_next_step=next_step,
        evidence_router_allows_validation_claim=validation_evidence.allowed and evaluation.classification not in {"blocked_no_execution", "no_feedback_yet", "invalid_feedback"},
        learning_writeback_allowed=writeback.allowed,
    )


def render_e12_offer_learning_update(update: E12OfferLearningUpdate) -> str:
    return "\n".join(
        [
            "# E12 Offer Learning Update",
            "",
            f"- top_offer: {update.top_offer}",
            f"- top_segment: {update.top_segment}",
            f"- signal_classification: {update.signal_classification}",
            f"- supports_48h_blueprint: {update.supports_48h_blueprint}",
            f"- supports_agency_segment: {update.supports_agency_segment}",
            f"- supports_pricing_hypothesis: {update.supports_pricing_hypothesis}",
            f"- blueprint_vs_implementation_learning: {update.blueprint_vs_implementation_learning}",
            f"- trust_gap_learning: {update.trust_gap_learning}",
            f"- recommended_next_step: {update.recommended_next_step}",
            f"- evidence_router_allows_validation_claim: {str(update.evidence_router_allows_validation_claim).lower()}",
            f"- learning_writeback_allowed: {str(update.learning_writeback_allowed).lower()}",
            "",
            "## Learning Boundary",
            "- This report proposes learning only.",
            "- It does not write brain, memory, CIEU, or core DB state.",
            "- Paid pilot prep is not recommended unless valid positive feedback supports it.",
        ]
    )

