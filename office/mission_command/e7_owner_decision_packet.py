from __future__ import annotations

from typing import Any, Dict, List


def build_e7_owner_decision_packet(
    offer_packet: Dict[str, Any],
    quality_rows: List[Dict[str, Any]],
) -> Dict[str, Any]:
    usable_count = sum(1 for row in quality_rows if row.get("usable_for_customer_facing_packet"))
    noisy_count = sum(1 for row in quality_rows if row.get("noise_flags"))
    return {
        "recommended_next_decision": "approve_or_revise_E8_external_validation",
        "top_offer": offer_packet["offer_name"],
        "confidence_level": "medium evidence-backed, not customer-validated",
        "evidence_quality_summary": [
            f"{len(quality_rows)} E6 sources calibrated.",
            f"{usable_count} sources are clean enough for customer-facing packet use without raw snippet exposure.",
            f"{noisy_count} sources contain raw page noise and are internal evidence only unless manually cleaned.",
            "Pricing remains a hypothesis; vendor pricing is a budget proxy, not willingness-to-pay proof.",
        ],
        "remaining_uncertainties": offer_packet["remaining_uncertainties"],
        "exact_e8_options": [
            "approve 3-person qualitative validation",
            "approve 5-10 targeted outreach validation",
            "approve public landing/post draft publication",
            "request revision of offer packet",
            "request more public evidence",
            "hold",
        ],
        "approval_covers": [
            "only the exact validation mode/count/channel/message/stop condition selected by owner",
            "use of the E7 drafts after final owner review",
            "collection of validation feedback for residual learning",
        ],
        "approval_does_not_cover": [
            "customer contact by default",
            "publication by default",
            "payment collection",
            "form submission",
            "account creation",
            "production implementation",
            "legal/security certification",
            "core DB/brain/memory/CIEU writeback",
            "obligation registration",
        ],
        "preflight_requirements_before_e8_external_action": [
            "semantic action classification",
            "action-wide governance preflight",
            "owner-approved count, segment, channel, draft, and stop condition",
            "explicit no-autonomy boundary for any sending/publication",
        ],
        "stop_conditions": [
            "owner approval boundary unclear",
            "draft changes materially after approval",
            "requested contact count exceeded",
            "recipient asks to stop",
            "safety/preflight result is blocked or review-gated",
        ],
        "no_customer_contact_approved_by_default": True,
        "no_publication_approved_by_default": True,
        "no_payment_form_account_approved_by_default": True,
        "external_action_executed": False,
    }


def render_e7_owner_decision_packet(packet: Dict[str, Any]) -> str:
    lines = [
        "# E7 Owner Decision Packet",
        "",
        f"- recommended_next_decision: {packet['recommended_next_decision']}",
        f"- top_offer: {packet['top_offer']}",
        f"- confidence_level: {packet['confidence_level']}",
        f"- no_customer_contact_approved_by_default: {packet['no_customer_contact_approved_by_default']}",
        f"- no_publication_approved_by_default: {packet['no_publication_approved_by_default']}",
        f"- no_payment_form_account_approved_by_default: {packet['no_payment_form_account_approved_by_default']}",
        f"- external_action_executed: {packet['external_action_executed']}",
        "",
        "## Evidence Quality Summary",
    ]
    lines.extend(f"- {item}" for item in packet["evidence_quality_summary"])
    lines.extend(["", "## Remaining Uncertainties"])
    lines.extend(f"- {item}" for item in packet["remaining_uncertainties"])
    lines.extend(["", "## Exact E8 Approval Options"])
    lines.extend(f"- {item}" for item in packet["exact_e8_options"])
    lines.extend(["", "## What Approval Covers"])
    lines.extend(f"- {item}" for item in packet["approval_covers"])
    lines.extend(["", "## What Approval Does Not Cover"])
    lines.extend(f"- {item}" for item in packet["approval_does_not_cover"])
    lines.extend(["", "## Preflight Requirements Before External Action"])
    lines.extend(f"- {item}" for item in packet["preflight_requirements_before_e8_external_action"])
    lines.extend(["", "## Stop Conditions"])
    lines.extend(f"- {item}" for item in packet["stop_conditions"])
    return "\n".join(lines)
