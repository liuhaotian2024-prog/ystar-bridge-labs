from __future__ import annotations

from dataclasses import asdict, dataclass, field
from typing import Any, Dict, List

from .e13_paid_signal_readiness import E13PaidSignalReadinessReport


@dataclass(frozen=True)
class E13OwnerDecisionPacket:
    recommended_next_step: str
    recommended_path: str
    second_best_path: str
    proposed_target_segment: str
    proposed_manual_validation_question: str
    proposed_offer_wording: str
    proposed_price_hypothesis: str
    exact_approval_boundary: str
    not_approved: List[str] = field(default_factory=list)
    evidence_support: List[str] = field(default_factory=list)
    evidence_limitations: List[str] = field(default_factory=list)
    paths_downgraded: List[str] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


def choose_next_step(readiness: E13PaidSignalReadinessReport) -> str:
    if readiness.classification == "paid_signal_ready":
        return "approve_E14_owner_operated_validation_batch"
    if readiness.classification == "evidence_promising_but_needs_validation":
        return "approve_E14_Aiden_assisted_manual_outreach_packet"
    if readiness.classification in {"needs_more_read_only_evidence", "blocked_no_evidence"}:
        return "approve_more_Tier1_read_only_evidence"
    if readiness.classification == "needs_offer_revision":
        return "revise_offer_and_rerun_E13"
    if readiness.classification == "reject_for_now":
        return "reject_path_for_now"
    return "hold"


def build_owner_decision_packet(readiness: E13PaidSignalReadinessReport) -> E13OwnerDecisionPacket:
    next_step = choose_next_step(readiness)
    downgraded = [
        item.opportunity_path
        for item in readiness.path_results
        if item.opportunity_path not in {readiness.top_path, readiness.second_best_path}
        and item.classification in {"weak_or_unproven", "blocked_no_evidence", "needs_offer_revision"}
    ]
    return E13OwnerDecisionPacket(
        recommended_next_step=next_step,
        recommended_path=readiness.top_path,
        second_best_path=readiness.second_best_path,
        proposed_target_segment="AI consultants/agencies needing governance layer, plus AI-heavy teams with agent workflow bottlenecks.",
        proposed_manual_validation_question=f"Would a 48h {readiness.top_path} be useful enough to justify a paid diagnostic or pilot-prep conversation?",
        proposed_offer_wording=f"48h {readiness.top_path}: a focused, AI-transparent diagnostic that maps bottlenecks, governance risks, and the fastest safe next step.",
        proposed_price_hypothesis="$500-$2,500 diagnostic range remains a hypothesis until E14 owner-approved validation or buyer feedback exists.",
        exact_approval_boundary="Approves only E14 planning/owner-operated validation preparation; does not approve outreach, publication, payment, account creation, form submission, or Aiden sending.",
        not_approved=[
            "customer contact",
            "email/message sending",
            "publication",
            "payment collection",
            "account creation",
            "form submission",
            "login",
            "core brain/CIEU/memory writeback",
        ],
        evidence_support=[
            f"classification: {readiness.classification}",
            f"evidence_count: {readiness.evidence_count}",
            f"default_changed_by_counterfactual_gate: {str(readiness.counterfactual_changed_default).lower()}",
        ],
        evidence_limitations=readiness.limitations,
        paths_downgraded=downgraded,
    )


def render_owner_decision_packet(packet: E13OwnerDecisionPacket) -> str:
    lines = [
        "# E13 Owner Decision Packet",
        "",
        f"- recommended_next_step: {packet.recommended_next_step}",
        f"- recommended_path: {packet.recommended_path}",
        f"- second_best_path: {packet.second_best_path}",
        f"- proposed_target_segment: {packet.proposed_target_segment}",
        f"- proposed_manual_validation_question: {packet.proposed_manual_validation_question}",
        f"- proposed_offer_wording: {packet.proposed_offer_wording}",
        f"- proposed_price_hypothesis: {packet.proposed_price_hypothesis}",
        f"- exact_approval_boundary: {packet.exact_approval_boundary}",
        "",
        "## Evidence Support",
    ]
    lines.extend(f"- {item}" for item in packet.evidence_support or ["none"])
    lines.extend(["", "## Evidence Limitations"])
    lines.extend(f"- {item}" for item in packet.evidence_limitations or ["none"])
    lines.extend(["", "## Paths Rejected Or Downgraded"])
    lines.extend(f"- {item}" for item in packet.paths_downgraded or ["none"])
    lines.extend(["", "## Not Approved"])
    lines.extend(f"- {item}" for item in packet.not_approved)
    return "\n".join(lines)
