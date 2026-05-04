from __future__ import annotations

from typing import Any, Dict, List


OWNER_ACTIONS = [
    "approve_manual_send_for_candidate",
    "revise_message",
    "reject_candidate",
    "request_more_evidence",
    "import_feedback",
    "suppress_candidate",
    "defer_batch",
    "prepare_provider_adapter_plan",
    "keep_real_provider_send_blocked",
]


def build_owner_action_model() -> Dict[str, Any]:
    actions: List[Dict[str, Any]] = []
    base_required = ["candidate exists in E18 batch", "owner decision recorded in control room"]
    for action in OWNER_ACTIONS:
        if action == "approve_manual_send_for_candidate":
            allowed = ["candidate status is ready_for_owner_review", "message variant accepted by owner"]
            forbidden = ["candidate suppressed", "missing evidence", "owner has not reviewed message"]
            next_state = "approved_not_sent"
        elif action == "import_feedback":
            allowed = ["owner manually sent outside repo", "feedback evidence provided by owner"]
            forbidden = ["agent claims feedback", "feedback lacks action_id/ledger_id/feedback_event_id"]
            next_state = "response_imported"
        elif action == "prepare_provider_adapter_plan":
            allowed = ["planning only", "no-send provider boundary remains intact"]
            forbidden = ["real send", "provider API call", "credential use"]
            next_state = "provider_plan_prepared_no_send"
        elif action == "keep_real_provider_send_blocked":
            allowed = ["always allowed as safe default"]
            forbidden = []
            next_state = "real_provider_send_blocked"
        else:
            allowed = base_required
            forbidden = ["real external action by agent"]
            next_state = action.replace("_", "-")
        actions.append(
            {
                "action": action,
                "allowed_preconditions": allowed,
                "forbidden_preconditions": forbidden,
                "required_evidence": base_required if action != "keep_real_provider_send_blocked" else ["no further evidence required"],
                "next_state": next_state,
                "audit_czl_note": "Owner action is modeled locally; no external action is performed by E19.",
            }
        )
    return {
        "artifact_id": "e19_owner_action_model",
        "actions": actions,
        "external_action_executed": False,
    }
