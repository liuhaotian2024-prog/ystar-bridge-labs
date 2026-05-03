from __future__ import annotations

from dataclasses import asdict, dataclass, field
from typing import Dict, Iterable, List

from .e13r_buyer_pain_evidence import E13RBuyerPainEvidenceRecord, public_evidence_can_be_validation_feedback, public_readiness_can_be_revenue
from .e13r_offer_revision import E13R_REVISED_OFFER_IDS, generate_revised_offer_candidates


E13R_READINESS_CLASSIFICATIONS = [
    "paid_signal_ready",
    "evidence_promising_but_needs_validation",
    "needs_more_buyer_pain_evidence",
    "needs_offer_revision_again",
    "weak_or_unproven",
    "reject_for_now",
    "blocked_no_evidence",
]


@dataclass(frozen=True)
class E13ROfferReadiness:
    offer_id: str
    offer_name: str
    classification: str
    evidence_count: int
    direct_buyer_pain_count: int
    pricing_or_budget_count: int
    substitute_or_comparable_count: int
    feasible_48h_deliverable: bool
    clear_next_validation_question: bool
    acceptable_trust_gap_mitigation: bool
    owner_burden_low_enough: bool
    reason: str
    e14_entry_allowed: bool

    def to_dict(self) -> Dict[str, object]:
        return asdict(self)


@dataclass(frozen=True)
class E13RReadinessReport:
    classification: str
    top_revised_offer_id: str
    top_revised_offer: str
    second_best_offer_id: str
    second_best_offer: str
    offer_results: List[E13ROfferReadiness] = field(default_factory=list)
    evidence_count: int = 0
    paid_signal_readiness_rt1: int = 1
    buyer_pain_evidence_rt1: int = 1
    counterfactual_changed_default: bool = False
    e14_entry_allowed: bool = False
    limitations: List[str] = field(default_factory=list)

    def to_dict(self) -> Dict[str, object]:
        data = asdict(self)
        data["offer_results"] = [item.to_dict() for item in self.offer_results]
        return data


def _counts(records: Iterable[E13RBuyerPainEvidenceRecord]) -> Dict[str, int]:
    data = {"pain": 0, "pricing": 0, "substitute": 0, "invalid": 0}
    for record in records:
        if record.evidence_quality == "direct_buyer_pain":
            data["pain"] += 1
        elif record.evidence_quality == "pricing_or_budget":
            data["pricing"] += 1
        elif record.evidence_quality == "substitute_or_comparable":
            data["substitute"] += 1
        elif record.evidence_quality == "invalid_evidence":
            data["invalid"] += 1
    return data


def classify_offer_readiness(offer_id: str, records: List[E13RBuyerPainEvidenceRecord]) -> E13ROfferReadiness:
    offer_by_id = {item.offer_id: item for item in generate_revised_offer_candidates()}
    offer = offer_by_id[offer_id]
    valid = [record for record in records if record.evidence_quality != "invalid_evidence"]
    counts = _counts(valid)
    feasible = bool(offer.deliverable_48h)
    next_question = bool(offer.fastest_disconfirming_evidence)
    trust_ok = bool(offer.trust_gap_mitigation)
    owner_ok = offer.owner_burden.lower().startswith("low")
    if not valid:
        classification = "blocked_no_evidence"
        reason = "No valid public read-only evidence was collected for this revised offer."
    elif counts["pain"] == 0 and (counts["pricing"] > 0 or counts["substitute"] > 0):
        classification = "needs_more_buyer_pain_evidence"
        reason = "Budget or substitute evidence exists, but direct buyer-pain language is still missing."
    elif counts["pain"] > 0 and counts["pricing"] > 0 and counts["substitute"] > 0 and feasible and next_question and trust_ok and owner_ok:
        classification = "paid_signal_ready"
        reason = "The revised offer has direct pain, budget/pricing, substitute evidence, a feasible 48h deliverable, and a clear next validation question."
    elif counts["pain"] > 0 and (counts["pricing"] > 0 or counts["substitute"] > 0):
        classification = "evidence_promising_but_needs_validation"
        reason = "Buyer pain is present, but the evidence mix is not complete enough for paid-signal readiness."
    elif counts["pain"] > 0:
        classification = "needs_offer_revision_again"
        reason = "Pain exists, but budget and comparable-service evidence are still too thin."
    else:
        classification = "weak_or_unproven"
        reason = "Evidence remains too weak for E14 readiness."
    return E13ROfferReadiness(
        offer_id=offer_id,
        offer_name=offer.offer_name,
        classification=classification,
        evidence_count=len(valid),
        direct_buyer_pain_count=counts["pain"],
        pricing_or_budget_count=counts["pricing"],
        substitute_or_comparable_count=counts["substitute"],
        feasible_48h_deliverable=feasible,
        clear_next_validation_question=next_question,
        acceptable_trust_gap_mitigation=trust_ok,
        owner_burden_low_enough=owner_ok,
        reason=reason,
        e14_entry_allowed=classification == "paid_signal_ready",
    )


def build_e13r_readiness_report(records: List[E13RBuyerPainEvidenceRecord], default_offer_id: str = "ai_ops_operating_room_implementation_support") -> E13RReadinessReport:
    by_offer: Dict[str, List[E13RBuyerPainEvidenceRecord]] = {offer_id: [] for offer_id in E13R_REVISED_OFFER_IDS}
    for record in records:
        by_offer.setdefault(record.offer_id, []).append(record)
    results = [classify_offer_readiness(offer_id, by_offer.get(offer_id, [])) for offer_id in E13R_REVISED_OFFER_IDS]
    rank = {
        "paid_signal_ready": 0,
        "evidence_promising_but_needs_validation": 1,
        "needs_more_buyer_pain_evidence": 2,
        "needs_offer_revision_again": 3,
        "weak_or_unproven": 4,
        "reject_for_now": 5,
        "blocked_no_evidence": 6,
    }
    ranked = sorted(
        results,
        key=lambda item: (
            rank[item.classification],
            -item.direct_buyer_pain_count,
            -item.pricing_or_budget_count,
            -item.substitute_or_comparable_count,
            -item.evidence_count,
            item.offer_name,
        ),
    )
    top = ranked[0]
    second = ranked[1] if len(ranked) > 1 else ranked[0]
    total_pain = sum(item.direct_buyer_pain_count for item in results)
    readiness_rt1 = 0 if top.classification == "paid_signal_ready" else 1
    buyer_pain_rt1 = 0 if total_pain > 0 else 1
    limitations = [
        "Public evidence is not validation feedback.",
        "Paid-signal readiness is not revenue, outreach approval, payment approval, publication approval, or Aiden sending approval.",
    ]
    if not records:
        limitations.append("No valid E13R evidence was collected; host-side evidence execution or source access is still required.")
    if not public_evidence_can_be_validation_feedback():
        limitations.append("E11 evidence router blocks public market evidence from claiming validation feedback.")
    if not public_readiness_can_be_revenue():
        limitations.append("E11 evidence router blocks public readiness evidence from claiming paid signal or revenue.")
    return E13RReadinessReport(
        classification=top.classification,
        top_revised_offer_id=top.offer_id,
        top_revised_offer=top.offer_name,
        second_best_offer_id=second.offer_id,
        second_best_offer=second.offer_name,
        offer_results=results,
        evidence_count=len(records),
        paid_signal_readiness_rt1=readiness_rt1,
        buyer_pain_evidence_rt1=buyer_pain_rt1,
        counterfactual_changed_default=top.offer_id != default_offer_id,
        e14_entry_allowed=top.classification == "paid_signal_ready",
        limitations=limitations,
    )


def render_e13r_readiness_report(report: E13RReadinessReport) -> str:
    lines = [
        "# E13R Paid-Signal Readiness",
        "",
        f"- classification: {report.classification}",
        f"- top_revised_offer: {report.top_revised_offer}",
        f"- second_best_offer: {report.second_best_offer}",
        f"- evidence_count: {report.evidence_count}",
        f"- buyer_pain_evidence_rt1: {report.buyer_pain_evidence_rt1}",
        f"- paid_signal_readiness_rt1: {report.paid_signal_readiness_rt1}",
        f"- counterfactual_changed_default: {str(report.counterfactual_changed_default).lower()}",
        f"- e14_entry_allowed: {str(report.e14_entry_allowed).lower()}",
        "",
        "## Revised Offer Results",
    ]
    for item in report.offer_results:
        lines.extend(
            [
                f"### {item.offer_name}",
                f"- offer_id: {item.offer_id}",
                f"- classification: {item.classification}",
                f"- evidence_count: {item.evidence_count}",
                f"- direct_buyer_pain_count: {item.direct_buyer_pain_count}",
                f"- pricing_or_budget_count: {item.pricing_or_budget_count}",
                f"- substitute_or_comparable_count: {item.substitute_or_comparable_count}",
                f"- e14_entry_allowed: {str(item.e14_entry_allowed).lower()}",
                f"- reason: {item.reason}",
                "",
            ]
        )
    lines.extend(["## Limitations"])
    lines.extend(f"- {item}" for item in report.limitations)
    return "\n".join(lines).rstrip()
