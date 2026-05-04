from __future__ import annotations

from typing import Any, Dict, List

from .e17_paid_signal_runtime import E17PaidSignalReadinessPacket


def build_route_decision_packet(
    selected_action: Dict[str, Any],
    paid_signal: E17PaidSignalReadinessPacket,
    offer_revision: Dict[str, Any],
) -> Dict[str, Any]:
    if paid_signal.current_feedback_state == "no_response_yet":
        recommended = "E17_manual_send_ready"
        reason = "The selected action is commercially prepared, owner-facing, and still no-send; the shortest cash path is owner manual send followed by feedback import."
    elif paid_signal.paid_signal_strength >= 4:
        recommended = "E18_commercial_acceleration_candidate"
        reason = "Imported feedback shows strong positive or budget/meeting signal."
    elif paid_signal.offer_revision_required:
        recommended = "E17_offer_revision_required"
        reason = "Feedback weakened message/offer fit or no response after wait window."
    elif paid_signal.target_revision_required:
        recommended = "E17_target_evidence_expansion_required"
        reason = "Target/channel quality needs repair."
    else:
        recommended = "E17_wait_for_owner_feedback_import"
        reason = "The system is waiting for owner-imported response evidence."
    return {
        "artifact_id": "e17_route_decision_packet",
        "selected_action_id": selected_action.get("action_id"),
        "recommended_route": recommended,
        "reason": reason,
        "route_options": {
            "E17_manual_send_ready": {
                "status": "recommended_if_no_response_yet",
                "allowed_actions": ["owner reviews one page", "owner manually sends if approved", "owner later imports feedback"],
                "blocked_actions": ["agent send", "provider API call", "real send receipt"],
            },
            "E17_wait_for_owner_feedback_import": {
                "status": "after_owner_manual_send",
                "allowed_actions": ["owner imports response summary", "deterministic classification"],
                "blocked_actions": ["claim paid signal without evidence"],
            },
            "E17_offer_revision_required": {
                "status": "if weak/no-response/objection evidence appears",
                "allowed_actions": ["revise pain framing", "revise CTA", "revise packaging"],
                "blocked_actions": ["keep repeating weak message"],
            },
            "E17_target_evidence_expansion_required": {
                "status": "if target/channel evidence is weak",
                "allowed_actions": ["public read-only evidence expansion", "replace from existing queue"],
                "blocked_actions": ["scrape private contact data"],
            },
            "E17_provider_adapter_preparation_allowed": {
                "status": "allowed_as_no_send_engineering_only",
                "allowed_actions": ["provider-safe tests", "no-send adapter preparation"],
                "blocked_actions": ["real send before explicit activation"],
            },
            "E16C1_real_send_still_blocked": {
                "status": "blocked",
                "required_before_unblock": ["explicit owner activation", "real provider adapter implementation", "provider tests", "safety tests", "bridge delivery closure"],
                "allowed_actions": [],
                "blocked_actions": ["real email/message send"],
            },
            "E18_commercial_acceleration_candidate": {
                "status": "only_if_imported_response_is_positive_or_budget_signal",
                "allowed_actions": ["owner-reviewed paid diagnostic follow-up", "meeting scheduling if requested"],
                "blocked_actions": ["automated follow-up without owner review"],
            },
        },
        "e16c1_real_send_blocked": True,
        "external_action_executed": False,
        "next_owner_decision_surface": ["approve_manual_send", "revise_message", "reject_target", "defer", "import_feedback_if_already_sent_manually"],
    }


def build_czl_closure(route_packet: Dict[str, Any], artifacts: List[str]) -> Dict[str, Any]:
    return {
        "artifact_id": "e17_czl_closure",
        "Y_star": "E17 first commercial signal closed loop runtime",
        "Xt": ["E16C0 selected action", "E16C0 no-send dry-run receipt", "E13/E13R/E14 commercial readiness assets", "host-local bridge delivery"],
        "U": ["owner activation console", "final message package", "feedback intake", "response classifier", "paid-signal evaluator", "offer revision planner", "target expansion queue", "route decision"],
        "Yt_plus_1": "Y*Bridge Labs is owner-manual-send ready for the first commercial signal and ready to classify imported feedback without fake evidence.",
        "Rt_plus_1": 0,
        "artifacts": artifacts,
        "no_real_external_action_occurred": True,
        "no_fake_response_evidence_created": True,
        "no_provider_api_called": True,
        "no_send_receipt_generated": True,
        "owner_activation_console_ready": True,
        "feedback_runtime_ready": True,
        "route_decision_deterministic": True,
        "commercial_path_advanced": "from no-send dry-run preparation to owner-gated customer signal loop readiness",
    }


def render_route_decision_packet(packet: Dict[str, Any]) -> str:
    lines = [
        "# E17 Route Decision Packet",
        "",
        f"- recommended_route: {packet['recommended_route']}",
        f"- reason: {packet['reason']}",
        f"- e16c1_real_send_blocked: {str(packet['e16c1_real_send_blocked']).lower()}",
        "",
        "## Route Options",
    ]
    for route, details in packet["route_options"].items():
        lines.extend([f"### {route}", f"- status: {details['status']}"])
        for action in details.get("allowed_actions", []):
            lines.append(f"- allowed: {action}")
        for action in details.get("blocked_actions", []):
            lines.append(f"- blocked: {action}")
        for item in details.get("required_before_unblock", []):
            lines.append(f"- required_before_unblock: {item}")
        lines.append("")
    return "\n".join(lines).rstrip() + "\n"


def render_czl_closure(closure: Dict[str, Any]) -> str:
    lines = [
        "# E17 CZL Closure",
        "",
        f"- Y*: {closure['Y_star']}",
        f"- Yt+1: {closure['Yt_plus_1']}",
        f"- Rt+1: {closure['Rt_plus_1']}",
        f"- no_real_external_action_occurred: {str(closure['no_real_external_action_occurred']).lower()}",
        f"- no_fake_response_evidence_created: {str(closure['no_fake_response_evidence_created']).lower()}",
        f"- no_provider_api_called: {str(closure['no_provider_api_called']).lower()}",
        f"- no_send_receipt_generated: {str(closure['no_send_receipt_generated']).lower()}",
        f"- commercial_path_advanced: {closure['commercial_path_advanced']}",
        "",
        "## U",
    ]
    lines.extend(f"- {item}" for item in closure["U"])
    lines.extend(["", "## Artifacts"])
    lines.extend(f"- {item}" for item in closure["artifacts"])
    return "\n".join(lines).rstrip() + "\n"
