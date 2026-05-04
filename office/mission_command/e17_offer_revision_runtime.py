from __future__ import annotations

from typing import Any, Dict, List

from .e17_response_classifier import E17ResponseClassification


def build_offer_revision_packet(commercial_assessment: Dict[str, Any], classification: E17ResponseClassification) -> Dict[str, Any]:
    lead_offer = str(commercial_assessment.get("top_revised_offer", "48h AI Agent Implementation Readiness Review"))
    revisions: List[str] = []
    revision_priority = "none_before_first_manual_send"
    if classification.feedback_type == "no_response_yet":
        revisions = [
            "Do not revise before the first manual send unless owner dislikes the tone.",
            "Keep the 48h review concrete: scorecard, blockers, governance/eval checklist, one safe next step.",
            "Use the softer fallback if owner wants lower-pressure language.",
        ]
    elif classification.offer_revision_required:
        revision_priority = "revise_after_feedback"
        revisions = [
            "Improve pain framing around implementation readiness and governance/evaluation gaps.",
            "Clarify what the buyer gets in 48 hours.",
            "Tighten CTA to either paid diagnostic fit check or explicit disqualification.",
            "Add credibility evidence only if it is already repo-backed.",
            "Evaluate pricing/packaging if pricing questions appear.",
        ]
    elif classification.paid_signal_strength >= 4:
        revision_priority = "preserve_offer_prepare_follow_up"
        revisions = [
            "Preserve the 48h review as lead offer.",
            "Prepare a concise owner-reviewed follow-up that answers the exact buyer signal.",
            "Do not automate follow-up without owner review and feedback provenance.",
        ]
    else:
        revision_priority = "monitor_before_revision"
        revisions = ["Wait for clearer feedback before changing the lead offer."]
    return {
        "artifact_id": "e17_offer_revision_packet",
        "lead_offer": lead_offer,
        "lead_offer_should_remain": True,
        "revision_priority": revision_priority,
        "recommended_revisions": revisions,
        "pain_framing_improvement": "Anchor the review in readiness blockers, governance/evaluation gaps, and safe next operational step.",
        "cta_improvement": "Ask whether a paid diagnostic or short pilot-prep conversation is worth considering.",
        "target_segmentation_improvement": "Prioritize AI consultants/agencies and AI-heavy teams with governance or implementation burden evidence.",
        "credibility_evidence_rule": "Use only repo-backed evidence; do not invent customer proof.",
        "pricing_packaging_rule": "Pricing remains hypothesis until imported response evidence confirms budget or objection.",
        "external_action_executed": False,
    }
