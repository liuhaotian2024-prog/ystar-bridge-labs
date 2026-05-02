from __future__ import annotations

from typing import Any, Dict, List

from .e10_shortest_revenue_path_scorer import E10RevenuePathScore
from .e10_target_candidate_registry import E10TargetCandidate
from .e10_validation_batch_builder import E10ValidationBatch


def build_e10_owner_decision_packet(
    scores: List[E10RevenuePathScore],
    batches: List[E10ValidationBatch],
    candidates: List[E10TargetCandidate],
    manifest_path: str,
    target_seeds_path: str,
) -> Dict[str, Any]:
    top_score = scores[0]
    top_batch = batches[0]
    candidate_by_id = {candidate.candidate_id: candidate for candidate in candidates}
    top_candidates = [candidate_by_id[candidate_id] for candidate_id in top_batch.target_candidate_ids if candidate_id in candidate_by_id]
    return {
        "recommended_next_decision": "approve_or_edit_E11_validation_batch",
        "top_offer": "48h AI Ops Operating Room Blueprint",
        "recommended_shortest_revenue_path": top_score.segment,
        "recommended_validation_batch": top_batch.batch_id,
        "top_candidate_ids": [candidate.candidate_id for candidate in top_candidates],
        "top_candidate_public_urls": [candidate.public_url for candidate in top_candidates],
        "evidence_supporting_target_selection": [
            "public implementation-burden signals",
            "public governance/safety signals",
            "pricing or budget proxy where visible",
            "public general-channel or owner-reviewable contactability",
        ],
        "risk_tier": "Tier 2 candidate only; owner approval required before any external contact",
        "owner_approval_required": True,
        "exact_approval_options": [
            "approve recommended batch",
            "edit targets",
            "edit channel",
            "edit draft",
            "request more target discovery",
            "choose owner-operated handoff",
            "provide safe execution provider",
            "hold",
        ],
        "what_approval_covers": "Only the exact targets, channel, draft hash, count, stop conditions, and execution mode the owner approves for E11.",
        "what_approval_does_not_cover": "No payment, form submission, account creation, publication, bulk outreach, scraped leads, core writeback, obligation registration, or COO invention.",
        "proposed_manifest_path": manifest_path,
        "proposed_target_seeds_path": target_seeds_path,
        "contact_executed": False,
        "publication_executed": False,
        "payment_form_account_action_executed": False,
        "validation_signal": "none_no_external_validation_or_feedback_in_e10",
        "paid_pilot_recommended": False,
        "exact_next_owner_action": "Review the proposed E10 manifest and target seeds, then approve or edit one E11 validation batch with exact targets, channel, draft hash, max count, stop conditions, and execution mode.",
    }


def render_e10_owner_decision_packet(packet: Dict[str, Any]) -> str:
    lines = ["# E10 Owner Decision Packet", ""]
    for key, value in packet.items():
        if key in {"exact_approval_options", "top_candidate_ids", "top_candidate_public_urls", "evidence_supporting_target_selection"}:
            continue
        lines.append(f"- {key}: {value}")
    lines.extend(["", "## Top Candidate IDs"])
    lines.extend(f"- {item}" for item in packet["top_candidate_ids"])
    lines.extend(["", "## Top Candidate Public URLs"])
    lines.extend(f"- {item}" for item in packet["top_candidate_public_urls"])
    lines.extend(["", "## Evidence Supporting Target Selection"])
    lines.extend(f"- {item}" for item in packet["evidence_supporting_target_selection"])
    lines.extend(["", "## Exact Approval Options"])
    lines.extend(f"- {item}" for item in packet["exact_approval_options"])
    lines.extend(
        [
            "",
            "## Boundary",
            "- no contact executed",
            "- no publication executed",
            "- no payment/form/account action executed",
            "- proposed target seeds are not owner-approved targets",
            "- paid pilot is not recommended without positive E11 feedback",
        ]
    )
    return "\n".join(lines)
