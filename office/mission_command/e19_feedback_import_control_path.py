from __future__ import annotations

from typing import Any, Dict


def build_feedback_import_control_path(e18_schema: Dict[str, Any], e18_empty: Dict[str, Any]) -> Dict[str, Any]:
    return {
        "artifact_id": "e19_feedback_import_control_path",
        "batch_id": e18_schema["batch_id"],
        "owner_import_location": "operations/external_validation/e18_batch_feedback_intake_empty.json or a future owner-supplied e20 feedback import file",
        "schema_validation_rules": e18_schema["required_per_target_fields"],
        "response_classifier_input": "office/mission_command/e18_batch_response_classifier.py consumes per-target explicit fields",
        "paid_signal_evaluator_input": "e18_batch_response_classification_rules -> commercial KPI and route decision",
        "kpi_update_path": "E20 real feedback import loop updates placeholders only after owner-imported evidence exists",
        "followup_allowed_when": [
            "positive_interest",
            "meeting_request",
            "pricing_question",
            "technical_clarification",
            "referral",
        ],
        "followup_blocked_when": [
            "no_response",
            "unsubscribe_or_do_not_contact",
            "negative_response",
            "bounce",
            "missing feedback provenance",
        ],
        "real_feedback_claimed_now": False,
        "external_action_executed": False,
    }


def render_feedback_import_control_path(path: Dict[str, Any]) -> str:
    lines = [
        "# E19 Feedback Import Control Path",
        "",
        f"- batch_id: {path['batch_id']}",
        f"- owner_import_location: {path['owner_import_location']}",
        f"- real_feedback_claimed_now: {str(path['real_feedback_claimed_now']).lower()}",
        "- external_action_executed: false",
        "",
        "## Follow-Up Allowed When",
    ]
    lines.extend(f"- {item}" for item in path["followup_allowed_when"])
    lines.extend(["", "## Follow-Up Blocked When"])
    lines.extend(f"- {item}" for item in path["followup_blocked_when"])
    return "\n".join(lines).rstrip() + "\n"
