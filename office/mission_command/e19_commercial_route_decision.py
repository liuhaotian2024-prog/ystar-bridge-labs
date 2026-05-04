from __future__ import annotations

from typing import Any, Dict


def build_commercial_route_decision(control_room: Dict[str, Any], drift_register: Dict[str, Any]) -> Dict[str, Any]:
    ready_count = int(control_room["kpi_state"]["ready_target_count"])
    if ready_count > 0:
        recommended = "E19_owner_manual_batch_ready"
        reason = "Ready owner-reviewed candidates exist and no feedback has been imported yet."
    else:
        recommended = "E19_target_evidence_expansion_first"
        reason = "No ready candidates exist."
    return {
        "artifact_id": "e19_commercial_route_decision_packet",
        "recommended_route": recommended,
        "reason": reason,
        "route_options": {
            "E19_owner_manual_batch_ready": "Owner may approve selected manual-send candidates.",
            "E19_message_revision_first": "Use if owner wants softer or more specific message variants.",
            "E19_target_evidence_expansion_first": "Use if target quality feels weak.",
            "E19_feedback_import_after_manual_send": "Use after owner manually sends and has response/no-response evidence.",
            "E20_real_feedback_import_loop": "Recommended after any owner manual send.",
            "E20_provider_adapter_preparation": "No-send engineering only unless owner explicitly chooses real-send path later.",
            "E20_ecosystem_drift_resolution": "Use if cross-repo ownership drift becomes blocking.",
            "keep_real_provider_send_blocked": "Current default for real provider send.",
        },
        "real_provider_send_blocked": True,
        "blocking_register_ids": [item["blocker_id"] for item in drift_register["blockers"]],
        "external_action_executed": False,
    }


def render_commercial_route_decision(packet: Dict[str, Any]) -> str:
    lines = [
        "# E19 Commercial Route Decision Packet",
        "",
        f"- recommended_route: {packet['recommended_route']}",
        f"- reason: {packet['reason']}",
        f"- real_provider_send_blocked: {str(packet['real_provider_send_blocked']).lower()}",
        "- external_action_executed: false",
        "",
        "## Route Options",
    ]
    for route, description in packet["route_options"].items():
        lines.append(f"- {route}: {description}")
    return "\n".join(lines).rstrip() + "\n"
