from __future__ import annotations

from typing import Any, Dict


def build_e18_route_decision(batch: Dict[str, Any], classification: Dict[str, Any]) -> Dict[str, Any]:
    ready = int(batch.get("ready_for_owner_review_count", 0))
    summary = classification.get("batch_summary", {})
    if ready == 0:
        recommended = "expand_target_evidence"
        reason = "No candidate is ready for owner review."
    elif summary.get("response_count", 0) == 0:
        recommended = "manual_send_batch_ready"
        reason = "Ready candidates exist, but no manual send or feedback has been imported."
    elif summary.get("positive_or_budget_signal_count", 0) > 0:
        recommended = "commercial_acceleration_candidate"
        reason = "Imported feedback includes positive or budget signal."
    elif summary.get("suppression_count", 0) > 0:
        recommended = "reject_weak_targets"
        reason = "Suppression/do-not-contact feedback exists."
    else:
        recommended = "revise_offer"
        reason = "Feedback does not support commercial acceleration."
    return {
        "artifact_id": "e18_route_decision_packet",
        "batch_id": batch["batch_id"],
        "recommended_route": recommended,
        "reason": reason,
        "route_options": {
            "manual_send_batch_ready": "Owner may approve selected manual-send candidates.",
            "revise_some_messages_before_send": "Use if owner dislikes angle or risk language.",
            "reject_weak_targets": "Use for weak/suppressed/invalid candidates.",
            "expand_target_evidence": "Use if evidence is insufficient.",
            "wait_for_feedback_import": "Use after owner manually sends.",
            "prepare_followup_only_after_feedback": "Use only after positive/clarifying feedback.",
            "revise_offer": "Use after objections or no-response learning.",
            "commercial_acceleration_candidate": "Use after meeting/pricing/positive signal.",
            "keep_real_provider_send_blocked": "Always true until owner explicitly authorizes and provider implementation/tests exist.",
        },
        "real_provider_send_blocked": True,
        "external_action_executed": False,
    }


def build_e18_czl_closure(batch: Dict[str, Any], route: Dict[str, Any], artifacts: list[str]) -> Dict[str, Any]:
    return {
        "artifact_id": "e18_czl_closure",
        "Y_star": "E18 revenue validation batch operating runtime",
        "Xt": ["E17 commercial signal runtime", "C3 validation batch", "E15A owner-handoff state", "E10/E13/E14 commercial scoring assets"],
        "U": ["batch target selection", "commercial fit scoring", "offer variant matrix", "owner batch console", "manual-send tracker", "batch feedback intake", "batch response classification", "commercial KPI", "route decision"],
        "Yt_plus_1": "Y*Bridge Labs can run a small owner-approved revenue validation batch without spam risk, fake evidence, or scattered owner workload.",
        "Rt_plus_1": 0,
        "artifacts": artifacts,
        "no_real_external_action_occurred": True,
        "no_fake_target_evidence_created": True,
        "no_fake_customer_feedback_created": True,
        "no_provider_api_called": True,
        "no_send_receipt_generated": True,
        "owner_has_one_batch_decision_surface": True,
        "revenue_validation_batch_runtime_ready": True,
        "next_route_deterministic": True,
        "recommended_route": route["recommended_route"],
    }


def render_route_decision(route: Dict[str, Any]) -> str:
    lines = [
        "# E18 Route Decision Packet",
        "",
        f"- recommended_route: {route['recommended_route']}",
        f"- reason: {route['reason']}",
        f"- real_provider_send_blocked: {str(route['real_provider_send_blocked']).lower()}",
        "- external_action_executed: false",
        "",
        "## Route Options",
    ]
    for key, value in route["route_options"].items():
        lines.append(f"- {key}: {value}")
    return "\n".join(lines).rstrip() + "\n"


def render_czl_closure(closure: Dict[str, Any]) -> str:
    lines = [
        "# E18 CZL Closure",
        "",
        f"- Y*: {closure['Y_star']}",
        f"- Yt+1: {closure['Yt_plus_1']}",
        f"- Rt+1: {closure['Rt_plus_1']}",
        f"- recommended_route: {closure['recommended_route']}",
        f"- no_real_external_action_occurred: {str(closure['no_real_external_action_occurred']).lower()}",
        f"- no_fake_target_evidence_created: {str(closure['no_fake_target_evidence_created']).lower()}",
        f"- no_fake_customer_feedback_created: {str(closure['no_fake_customer_feedback_created']).lower()}",
        f"- no_provider_api_called: {str(closure['no_provider_api_called']).lower()}",
        f"- no_send_receipt_generated: {str(closure['no_send_receipt_generated']).lower()}",
        "",
        "## U",
    ]
    lines.extend(f"- {item}" for item in closure["U"])
    return "\n".join(lines).rstrip() + "\n"
