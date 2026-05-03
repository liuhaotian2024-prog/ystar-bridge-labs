from __future__ import annotations

from typing import Any, Dict, List, Mapping


def build_c1_action_ledger_template() -> Dict[str, Any]:
    return {
        "template": {
            "action_id": "OWNER_OR_GOV_MCP_TO_FILL_AFTER_EXECUTION",
            "envelope_id": "c1_owner_constitutional_envelope_request",
            "y_gov_decision_id": "REQUIRED",
            "gov_mcp_receipt_id": "REQUIRED",
            "target_id_or_class": "REQUIRED",
            "action_type": "external_validation_message|low_risk_contact_form_submission|publication_draft_or_private_preview",
            "channel": "REQUIRED",
            "draft_hash": "REQUIRED_IF_MESSAGE_OR_PUBLICATION",
            "executed_by": "gov-mcp governed adapter or owner if explicitly chosen",
            "executed_at": "REQUIRED_AFTER_EXECUTION",
            "result": "sent|submitted|draft_created|denied|escalated|blocked",
            "stop_condition_triggered": "",
            "evidence_refs": [],
            "residual_candidate": "expected_vs_actual_outcome_summary",
        },
        "no_placeholder_execution": True,
    }


def validate_c1_action_ledger_event(event: Mapping[str, Any]) -> List[str]:
    required = ["action_id", "envelope_id", "y_gov_decision_id", "gov_mcp_receipt_id", "target_id_or_class", "action_type", "channel", "executed_by", "executed_at", "result"]
    errors = [f"missing_{key}" for key in required if not event.get(key) or str(event.get(key)).startswith("REQUIRED")]
    if str(event.get("action_id", "")).startswith("OWNER_OR_GOV_MCP_TO_FILL"):
        errors.append("placeholder_action_id_is_not_execution")
    return list(dict.fromkeys(errors))
