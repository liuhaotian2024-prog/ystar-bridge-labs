from __future__ import annotations

from typing import Any

from .e35_one_brain_integration_guard import get_artifact


def build_recent_line_runtime_connection_audit() -> dict[str, Any]:
    """Return the E41 artifact and keep a stable code-level entry point."""
    artifact = get_artifact("e41_recent_line_runtime_connection_audit")
    return artifact


def forbidden_action_flags(artifact: dict[str, Any] | None = None) -> dict[str, bool]:
    artifact = artifact or build_recent_line_runtime_connection_audit()
    keys = [
        "customer_contact_occurred",
        "expert_contact_occurred",
        "real_human_target_identification_occurred",
        "personal_contact_info_scraped",
        "message_send_occurred",
        "publication_occurred",
        "form_submission_occurred",
        "login_occurred",
        "provider_api_or_tool_execution_occurred",
        "external_integration_occurred",
        "payment_occurred",
        "secret_used",
        "customer_validation_claimed",
        "expert_feedback_claimed",
        "paid_signal_claimed",
        "final_product_selected",
    ]
    return {key: bool(artifact.get(key, False)) for key in keys}


def milestones_needing_reconciliation(artifact: dict[str, Any] | None = None) -> list[str]:
    artifact = artifact or build_recent_line_runtime_connection_audit()
    return [item["milestone"] for item in artifact.get("milestones", []) if item.get("status") != "connected"]

