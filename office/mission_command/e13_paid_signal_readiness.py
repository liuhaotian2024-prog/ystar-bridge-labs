from __future__ import annotations

from dataclasses import asdict, dataclass, field
from typing import Any, Dict, Iterable, List

from .e13_evidence_records import E13EvidenceQuality, E13EvidenceRecord, E13_OPPORTUNITY_PATHS
from .evidence_signal_router import EvidenceClaimType, EvidenceSignalType, route_evidence_signal


READINESS_CLASSIFICATIONS = [
    "paid_signal_ready",
    "evidence_promising_but_needs_validation",
    "needs_offer_revision",
    "needs_more_read_only_evidence",
    "weak_or_unproven",
    "reject_for_now",
    "blocked_no_evidence",
]


@dataclass(frozen=True)
class E13PathReadiness:
    opportunity_path: str
    classification: str
    evidence_count: int
    direct_buyer_pain_count: int
    pricing_or_budget_count: int
    substitute_count: int
    trust_gap_count: int
    owner_burden_low_enough: bool
    next_validation_question: str
    reason: str
    evidence_router_allows_validation_feedback_claim: bool
    evidence_router_allows_paid_signal_claim: bool

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


@dataclass(frozen=True)
class E13PaidSignalReadinessReport:
    top_path: str
    second_best_path: str
    classification: str
    path_results: List[E13PathReadiness] = field(default_factory=list)
    counterfactual_changed_default: bool = False
    paid_signal_readiness_rt1: int = 1
    evidence_count: int = 0
    limitations: List[str] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        data = asdict(self)
        data["path_results"] = [item.to_dict() for item in self.path_results]
        return data


def _quality_counts(records: Iterable[E13EvidenceRecord]) -> Dict[str, int]:
    counts = {
        "direct": 0,
        "pricing": 0,
        "substitute": 0,
        "trust": 0,
        "invalid": 0,
    }
    for record in records:
        quality = record.evidence_quality
        if quality == E13EvidenceQuality.DIRECT_BUYER_PAIN.value:
            counts["direct"] += 1
        if quality == E13EvidenceQuality.PRICING_REFERENCE.value:
            counts["pricing"] += 1
        if quality == E13EvidenceQuality.COMPETITOR_OR_SUBSTITUTE.value:
            counts["substitute"] += 1
        if record.trust_gap_signal:
            counts["trust"] += 1
        if quality == E13EvidenceQuality.INVALID_EVIDENCE.value:
            counts["invalid"] += 1
    return counts


def classify_path_readiness(opportunity_path: str, records: List[E13EvidenceRecord]) -> E13PathReadiness:
    valid = [record for record in records if record.evidence_quality != E13EvidenceQuality.INVALID_EVIDENCE.value]
    counts = _quality_counts(valid)
    if not valid:
        classification = "blocked_no_evidence"
        reason = "No valid public read-only evidence was collected for this path."
    elif counts["direct"] >= 1 and (counts["pricing"] >= 1 or counts["substitute"] >= 1) and len(valid) >= 3:
        classification = "paid_signal_ready"
        reason = "Public evidence supports pain, budget/substitute spend, segment plausibility, and a next validation question."
    elif counts["direct"] >= 1 and (counts["pricing"] >= 1 or counts["substitute"] >= 1):
        classification = "evidence_promising_but_needs_validation"
        reason = "Evidence is promising but not dense enough for readiness closure."
    elif counts["direct"] == 0 and len(valid) >= 2:
        classification = "needs_offer_revision"
        reason = "Market evidence exists, but direct buyer pain is weak or missing."
    elif len(valid) == 1:
        classification = "needs_more_read_only_evidence"
        reason = "Only one valid source supports this path."
    else:
        classification = "weak_or_unproven"
        reason = "Evidence remains too weak for E14 approval."
    validation_route = route_evidence_signal(EvidenceSignalType.PUBLIC_MARKET_EVIDENCE, EvidenceClaimType.VALIDATION_RESULT)
    paid_route = route_evidence_signal(EvidenceSignalType.PUBLIC_MARKET_EVIDENCE, EvidenceClaimType.PAID_SIGNAL_CLAIM)
    return E13PathReadiness(
        opportunity_path=opportunity_path,
        classification=classification,
        evidence_count=len(valid),
        direct_buyer_pain_count=counts["direct"],
        pricing_or_budget_count=counts["pricing"],
        substitute_count=counts["substitute"],
        trust_gap_count=counts["trust"],
        owner_burden_low_enough=True,
        next_validation_question=f"Would a 48h {opportunity_path} diagnostic produce enough value to justify a paid next step?",
        reason=reason,
        evidence_router_allows_validation_feedback_claim=validation_route.allowed,
        evidence_router_allows_paid_signal_claim=paid_route.allowed,
    )


def build_paid_signal_readiness_report(records: List[E13EvidenceRecord], default_path: str = "Agent Workflow Bottleneck Diagnosis") -> E13PaidSignalReadinessReport:
    by_path: Dict[str, List[E13EvidenceRecord]] = {path: [] for path in E13_OPPORTUNITY_PATHS}
    for record in records:
        by_path.setdefault(record.opportunity_path, []).append(record)
    results = [classify_path_readiness(path, by_path.get(path, [])) for path in E13_OPPORTUNITY_PATHS]
    rank_order = {
        "paid_signal_ready": 0,
        "evidence_promising_but_needs_validation": 1,
        "needs_more_read_only_evidence": 2,
        "needs_offer_revision": 3,
        "weak_or_unproven": 4,
        "reject_for_now": 5,
        "blocked_no_evidence": 6,
    }
    ranked = sorted(results, key=lambda item: (rank_order[item.classification], -item.evidence_count, item.opportunity_path))
    top = ranked[0]
    second = ranked[1] if len(ranked) > 1 else ranked[0]
    readiness_rt1 = 0 if top.classification == "paid_signal_ready" else 1
    limitations = [
        "Public evidence is not E12 validation feedback.",
        "Readiness is not revenue and does not approve outreach, payment, publication, account creation, or form submission.",
    ]
    if not records:
        limitations.append("No evidence was collected; host-side source/provider configuration is still required.")
    return E13PaidSignalReadinessReport(
        top_path=top.opportunity_path,
        second_best_path=second.opportunity_path,
        classification=top.classification,
        path_results=results,
        counterfactual_changed_default=top.opportunity_path != default_path,
        paid_signal_readiness_rt1=readiness_rt1,
        evidence_count=len(records),
        limitations=limitations,
    )
