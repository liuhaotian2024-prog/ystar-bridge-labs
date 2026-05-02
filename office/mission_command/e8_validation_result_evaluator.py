from __future__ import annotations

from typing import Any, Dict


def evaluate_e8_validation_result(
    *,
    manifest_present: bool,
    targets_present: bool,
    provider_available: bool,
    preflight_allowed: bool,
    execution_gate: Dict[str, Any],
    feedback_signal: str,
) -> Dict[str, Any]:
    if feedback_signal in {"strong_positive", "weak_positive"}:
        status = "validation_signal_positive"
        recommendation = "approve_E9_paid_pilot_prep"
    elif feedback_signal in {"negative", "mixed"}:
        status = f"validation_signal_{feedback_signal}"
        recommendation = "revise_offer_and_rerun_validation"
    elif execution_gate.get("executed"):
        status = "external_validation_executed_waiting_for_feedback"
        recommendation = "request_more_feedback"
    elif not manifest_present:
        status = "blocked_missing_manifest"
        recommendation = "provide_external_validation_manifest"
    elif not targets_present:
        status = "blocked_missing_targets"
        recommendation = "provide_target_seeds"
    elif execution_gate.get("owner_operated_handoff_ready"):
        status = "owner_operated_handoff_ready"
        recommendation = "run_owner_operated_validation"
    elif not provider_available:
        status = "blocked_missing_execution_provider"
        recommendation = "provide_safe_execution_provider"
    elif not preflight_allowed:
        status = "validation_invalid_or_insufficient"
        recommendation = "revise_offer_and_rerun_validation"
    else:
        status = "dry_run_control_plane_ready"
        recommendation = "run_owner_operated_validation"
    return {
        "result_status": status,
        "recommended_next_decision": recommendation,
        "do_not_recommend_paid_pilot_without_positive_signal": feedback_signal not in {"strong_positive", "weak_positive"},
        "residual_learning_questions": [
            "buyer segment right?",
            "price hypothesis credible?",
            "blueprint enough or implementation required?",
            "trust gap too high?",
            "target channel viable?",
            "should opportunity ranking change?",
        ],
    }


def render_e8_validation_result_summary(result: Dict[str, Any]) -> str:
    lines = [
        "# E8 Validation Result Summary",
        "",
        f"- result_status: {result['result_status']}",
        f"- recommended_next_decision: {result['recommended_next_decision']}",
        f"- do_not_recommend_paid_pilot_without_positive_signal: {result['do_not_recommend_paid_pilot_without_positive_signal']}",
        "",
        "## Residual Learning Questions",
    ]
    lines.extend(f"- {item}" for item in result["residual_learning_questions"])
    return "\n".join(lines)


def render_e8_residual_learning_update(result: Dict[str, Any]) -> str:
    lines = [
        "# E8 Residual Learning Update",
        "",
        "- writeback_allowed: false",
        "- review_required: true",
        "- core_db_writeback: false",
        f"- validation_result_status: {result['result_status']}",
        "",
        "## Review-Gated Learning Questions",
    ]
    lines.extend(f"- {item}" for item in result["residual_learning_questions"])
    lines.extend(
        [
            "",
            "## Update Rule",
            "Do not write CIEU/core memory automatically. Owner or later governance approval is required before any persistent learning writeback.",
        ]
    )
    return "\n".join(lines)
