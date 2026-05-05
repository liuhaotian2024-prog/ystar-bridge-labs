from __future__ import annotations

from typing import Any

from .e35_one_brain_integration_guard import get_artifact


def build_frontier_capability_import_loop() -> dict[str, Any]:
    """Return the E41 artifact and keep a stable code-level entry point."""
    artifact = get_artifact("e41_frontier_capability_import_loop")
    return artifact


def forbidden_action_flags(artifact: dict[str, Any] | None = None) -> dict[str, bool]:
    artifact = artifact or build_frontier_capability_import_loop()
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


def choose_import_pattern(candidate: dict[str, Any]) -> str:
    if candidate.get("external_side_effect"):
        return "owner approval required"
    pattern = str(candidate.get("proposed_implementation_type", "method-only"))
    if pattern in {"method-only", "schema", "evaluator", "artifact builder"}:
        return pattern
    return "reject"

