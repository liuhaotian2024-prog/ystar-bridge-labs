from __future__ import annotations

from typing import Any, Dict, List


OWNER_CHOICES = ["approve_manual_send", "revise_message", "reject_target", "defer", "expand_evidence"]


def build_batch_owner_console(batch: Dict[str, Any], scores: Dict[str, Any], variants: Dict[str, Any]) -> Dict[str, Any]:
    score_by_action = {item["action_id"]: item for item in scores.get("scores", [])}
    variant_by_id = {item["variant_id"]: item for item in variants.get("variants", [])}
    candidates: List[Dict[str, Any]] = []
    for candidate in batch.get("candidates", []):
        score = score_by_action.get(candidate["action_id"], {})
        variant_id = score.get("recommended_message_variant_id", "direct_readiness_review")
        variant = variant_by_id.get(variant_id, {})
        ready = candidate.get("status") == "ready_for_owner_review"
        candidates.append(
            {
                "action_id": candidate["action_id"],
                "target_name": candidate["target_name"],
                "status": candidate["status"],
                "why_included": candidate["selection_reason"],
                "evidence_status": "evidence_present" if candidate.get("evidence_basis") else "missing_evidence",
                "commercial_score": score.get("total_score", 0),
                "recommended_message_variant_id": variant_id,
                "message_angle": variant.get("message_angle", ""),
                "cta": variant.get("cta", ""),
                "risk_tier": candidate["risk_tier"],
                "approval_choices": OWNER_CHOICES,
                "manual_send_readiness": "ready_if_owner_approves" if ready else "not_ready",
                "feedback_fields_to_capture": [
                    "owner_sent_status",
                    "feedback_type",
                    "raw_feedback_summary",
                    "pricing_question_present",
                    "meeting_request_present",
                    "positive_interest_present",
                    "do_not_contact_requested",
                    "owner_notes",
                ],
            }
        )
    return {
        "artifact_id": "e18_batch_owner_console",
        "batch_id": batch["batch_id"],
        "owner_console_type": "single_batch_decision_surface",
        "owner_burden_policy": "review_one_console_choose_candidate_decisions_send_only_if_owner_approves",
        "lead_offer": batch["lead_offer"],
        "recommended_batch_action": "approve ready candidates only if owner wants first small revenue validation batch; otherwise revise/reject/defer.",
        "candidates": candidates,
        "blocked_actions": [
            "agent send",
            "provider API call",
            "real send receipt",
            "fake feedback",
            "scraped private contact data",
            "core brain/CIEU/memory canonical writeback",
        ],
        "external_action_executed": False,
    }


def render_batch_owner_console(console: Dict[str, Any]) -> str:
    lines = [
        "# E18 Batch Owner Console",
        "",
        "This is the single owner-facing batch surface. It does not send anything.",
        "",
        f"- batch_id: {console['batch_id']}",
        f"- lead_offer: {console['lead_offer']}",
        f"- recommended_batch_action: {console['recommended_batch_action']}",
        "- external_action_executed: false",
        "",
        "## Candidates",
    ]
    for item in console["candidates"]:
        lines.extend(
            [
                f"### {item['target_name']}",
                f"- action_id: {item['action_id']}",
                f"- status: {item['status']}",
                f"- manual_send_readiness: {item['manual_send_readiness']}",
                f"- commercial_score: {item['commercial_score']}",
                f"- evidence_status: {item['evidence_status']}",
                f"- message_variant: {item['recommended_message_variant_id']}",
                f"- message_angle: {item['message_angle']}",
                f"- CTA: {item['cta']}",
                f"- owner_choices: {', '.join(item['approval_choices'])}",
                "",
            ]
        )
    lines.append("## Blocked Actions")
    lines.extend(f"- {item}" for item in console["blocked_actions"])
    return "\n".join(lines).rstrip() + "\n"
