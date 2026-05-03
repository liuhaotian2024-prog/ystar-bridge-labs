from __future__ import annotations

from dataclasses import asdict, dataclass, field
from typing import Dict, List

from .e13r_readiness_gate import E13RReadinessReport


@dataclass(frozen=True)
class E13ROwnerDecisionPacket:
    recommended_next_step: str
    recommended_revised_offer: str
    second_best_offer: str
    proposed_target_segment: str
    proposed_manual_validation_question: str
    proposed_offer_wording: str
    proposed_price_hypothesis: str
    exact_approval_boundary: str
    not_approved: List[str] = field(default_factory=list)
    evidence_support: List[str] = field(default_factory=list)
    evidence_limitations: List[str] = field(default_factory=list)
    rejected_or_downgraded_offers: List[str] = field(default_factory=list)

    def to_dict(self) -> Dict[str, object]:
        return asdict(self)


def choose_e13r_next_step(report: E13RReadinessReport) -> str:
    if report.classification == "paid_signal_ready":
        return "prepare_E14_owner_operated_validation"
    if report.classification == "evidence_promising_but_needs_validation":
        return "approve_E14_owner_operated_validation_prep_only"
    if report.classification == "needs_more_buyer_pain_evidence":
        return "approve_more_Tier1_buyer_pain_evidence"
    if report.classification == "needs_offer_revision_again":
        return "revise_offer_and_rerun_E13R"
    if report.classification == "blocked_no_evidence":
        return "run_host_side_E13R_evidence_collection"
    if report.classification == "reject_for_now":
        return "reject_path_for_now"
    return "hold"


def build_e13r_owner_decision_packet(report: E13RReadinessReport) -> E13ROwnerDecisionPacket:
    downgraded = [
        item.offer_name
        for item in report.offer_results
        if item.offer_name not in {report.top_revised_offer, report.second_best_offer}
        and item.classification in {"weak_or_unproven", "blocked_no_evidence", "needs_offer_revision_again", "needs_more_buyer_pain_evidence"}
    ]
    return E13ROwnerDecisionPacket(
        recommended_next_step=choose_e13r_next_step(report),
        recommended_revised_offer=report.top_revised_offer,
        second_best_offer=report.second_best_offer,
        proposed_target_segment="AI consultants/agencies needing governance layer, plus AI-heavy teams with agent workflow bottlenecks.",
        proposed_manual_validation_question=f"Would {report.top_revised_offer} be useful enough to justify a paid diagnostic or pilot-prep conversation?",
        proposed_offer_wording=f"{report.top_revised_offer}: a 48h AI-transparent diagnostic focused on buyer-visible pain, bottlenecks, governance risk, and the smallest safe next step.",
        proposed_price_hypothesis="$500-$2,500 diagnostic remains a hypothesis until E14 owner-approved validation or buyer feedback exists.",
        exact_approval_boundary="Approves only the next decision packet and E14 preparation if readiness supports it; does not approve outreach, Aiden sending, publication, payment, account creation, form submission, login, or core memory/CIEU/brain writeback.",
        not_approved=[
            "customer contact",
            "email/message sending",
            "publication",
            "payment collection",
            "account creation",
            "form submission",
            "login",
            "Aiden autonomous sending",
            "core brain/CIEU/memory writeback",
        ],
        evidence_support=[
            f"classification: {report.classification}",
            f"evidence_count: {report.evidence_count}",
            f"buyer_pain_evidence_rt1: {report.buyer_pain_evidence_rt1}",
            f"paid_signal_readiness_rt1: {report.paid_signal_readiness_rt1}",
            f"counterfactual_changed_default: {str(report.counterfactual_changed_default).lower()}",
        ],
        evidence_limitations=report.limitations,
        rejected_or_downgraded_offers=downgraded,
    )


def render_e13r_owner_decision_packet(packet: E13ROwnerDecisionPacket) -> str:
    lines = [
        "# E13R Owner Decision Packet",
        "",
        f"- recommended_next_step: {packet.recommended_next_step}",
        f"- recommended_revised_offer: {packet.recommended_revised_offer}",
        f"- second_best_offer: {packet.second_best_offer}",
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
    lines.extend(["", "## Rejected Or Downgraded Offers"])
    lines.extend(f"- {item}" for item in packet.rejected_or_downgraded_offers or ["none"])
    lines.extend(["", "## Not Approved"])
    lines.extend(f"- {item}" for item in packet.not_approved)
    return "\n".join(lines).rstrip()
