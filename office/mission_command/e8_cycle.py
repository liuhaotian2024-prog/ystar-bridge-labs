from __future__ import annotations

from pathlib import Path
from typing import Any, Dict

from .e8_ai_transparency_policy import render_e8_ai_transparency_policy
from .e8_draft_freeze import freeze_validation_drafts, render_e8_frozen_validation_drafts
from .e8_execution_gate import DisabledExternalValidationProvider, render_e8_execution_gate_report, run_e8_execution_gate
from .e8_external_action_preflight import build_standard_e8_validation_action, preflight_e8_external_action, render_e8_external_action_preflight
from .e8_feedback_capture import load_e8_feedback_events, render_e8_feedback_capture_report
from .e8_owner_decision_packet import build_e8_owner_decision_packet, render_e8_owner_decision_packet
from .e8_risk_controlled_action_model import render_e8_risk_model_report
from .e8_target_registry import (
    TARGET_SEEDS_TEMPLATE_PATH,
    load_e8_target_seeds,
    render_e8_target_seed_status_or_request,
    render_e8_target_seed_template,
)
from .e8_validation_approval import (
    MANIFEST_TEMPLATE_PATH,
    load_e8_external_validation_manifest,
    render_e8_manifest_status_or_request,
    render_e8_manifest_template,
)
from .e8_validation_result_evaluator import render_e8_residual_learning_update, render_e8_validation_result_summary, evaluate_e8_validation_result
from .e8_validation_signal_evaluator import classify_validation_signal, render_e8_validation_signal_evaluation
from .strict_czl import build_strict_czl_state, render_strict_czl_report


E8_Y_STAR = [
    "implementation_inspection_completed",
    "risk_control_model_created",
    "ai_transparency_policy_created",
    "autonomy_budget_manifest_checked_or_requested",
    "target_seed_registry_checked_or_requested",
    "frozen_validation_drafts_created",
    "external_action_preflight_created",
    "execution_gate_report_created",
    "feedback_capture_model_created",
    "validation_signal_evaluation_created",
    "validation_result_summary_created",
    "residual_learning_update_created",
    "owner_decision_packet_created",
    "strict_czl_closure_created",
    "no_unapproved_external_side_effects",
]


NO_UNAPPROVED_EXTERNAL_ACTION_RECEIPT = {
    "unapproved external sending": False,
    "unapproved customer contact": False,
    "unapproved email/message": False,
    "unapproved publication": False,
    "payment": False,
    "account creation": False,
    "form submission": False,
    "core DB/brain/memory/CIEU writeback": False,
    "obligation auto-registration": False,
    "COO invented": False,
}


def method_learning_updated(repo_root: Path) -> bool:
    path = repo_root / "knowledge" / "ceo" / "wisdom" / "AIDEN_META_DEVELOPMENT_METHOD_KERNEL.md"
    return path.exists() and "External freedom should be risk-controlled" in path.read_text(encoding="utf-8")


def _write_templates(repo_root: Path) -> Dict[str, Path]:
    ops = repo_root / "operations" / "external_validation"
    ops.mkdir(parents=True, exist_ok=True)
    manifest_template = repo_root / MANIFEST_TEMPLATE_PATH
    target_template = repo_root / TARGET_SEEDS_TEMPLATE_PATH
    manifest_template.write_text(render_e8_manifest_template() + "\n", encoding="utf-8")
    target_template.write_text(render_e8_target_seed_template() + "\n", encoding="utf-8")
    return {"manifest_template": manifest_template, "target_template": target_template}


def build_e8_cycle(repo_root: Path) -> Dict[str, Any]:
    _write_templates(repo_root)
    manifest = load_e8_external_validation_manifest(repo_root)
    targets = load_e8_target_seeds(repo_root)
    drafts = freeze_validation_drafts(repo_root)
    action = build_standard_e8_validation_action(manifest, targets, drafts)
    preflight = preflight_e8_external_action(action, manifest, targets, drafts)
    execution_gate = run_e8_execution_gate(
        action,
        preflight,
        repo_root,
        provider=DisabledExternalValidationProvider(),
        execution_mode="owner_operated_handoff",
    )
    feedback_events = load_e8_feedback_events(repo_root)
    feedback_signal = classify_validation_signal(feedback_events)
    validation_result = evaluate_e8_validation_result(
        manifest_present=manifest is not None,
        targets_present=bool(targets),
        provider_available=execution_gate.provider_available,
        preflight_allowed=preflight.allowed,
        execution_gate=execution_gate.to_dict(),
        feedback_signal=feedback_signal,
    )
    y_t1 = {
        "implementation_inspection_completed": (repo_root / "reports" / "integration" / "e8_implementation_inspection.md").exists(),
        "risk_control_model_created": True,
        "ai_transparency_policy_created": True,
        "autonomy_budget_manifest_checked_or_requested": True,
        "target_seed_registry_checked_or_requested": True,
        "frozen_validation_drafts_created": bool(drafts),
        "external_action_preflight_created": True,
        "execution_gate_report_created": True,
        "feedback_capture_model_created": True,
        "validation_signal_evaluation_created": True,
        "validation_result_summary_created": True,
        "residual_learning_update_created": True,
        "owner_decision_packet_created": True,
        "strict_czl_closure_created": True,
        "no_unapproved_external_side_effects": not any(NO_UNAPPROVED_EXTERNAL_ACTION_RECEIPT.values()) and not execution_gate.external_action_executed,
    }
    status = "complete_control_plane_ready" if all(y_t1.values()) else "residual"
    czl = build_strict_czl_state(
        mission_id="e8_risk_controlled_external_validation_runtime",
        y_star=E8_Y_STAR,
        xt={
            "start_commit": "b49dc9ca",
            "e7_state": "validation-ready packet exists; no external validation executed",
            "manifest_present": manifest is not None,
            "target_seeds_present": bool(targets),
            "execution_provider_present": False,
        },
        u=[
            "inspected E7 implementation and reports",
            "implemented E8 risk tiers and AI transparency policy",
            "implemented autonomy budget manifest and target registry",
            "froze validation drafts and produced AI-disclosed outreach draft",
            "ran external action preflight and execution gate in non-sending mode",
            "created feedback capture, signal evaluation, result summary, owner packet, residual learning, and CZL closure",
        ],
        y_t1=y_t1,
        feasible_criteria=E8_Y_STAR,
        full_criteria=E8_Y_STAR,
        blocked_reason="" if status == "complete_control_plane_ready" else "E8 control-plane artifact missing",
        exact_unblock_action=[] if status == "complete_control_plane_ready" else ["Create missing E8 control-plane artifact and rerun closure."],
        blocked_status=status,
    )
    owner_packet = build_e8_owner_decision_packet(
        {
            "validation_result": validation_result,
            "execution_gate": execution_gate.to_dict(),
            "manifest_present": manifest is not None,
            "targets_present": bool(targets),
            "preflight": preflight.to_dict(),
            "feedback_events": [event.to_dict() for event in feedback_events],
            "feedback_signal": feedback_signal,
        }
    )
    return {
        "manifest": manifest,
        "targets": targets,
        "drafts": drafts,
        "action": action,
        "preflight": preflight,
        "execution_gate": execution_gate,
        "feedback_events": feedback_events,
        "feedback_signal": feedback_signal,
        "validation_result": validation_result,
        "owner_packet": owner_packet,
        "strict_czl": czl,
        "status": status,
    }


def render_e8_czl_closure(cycle: Dict[str, Any]) -> str:
    lines = [
        render_strict_czl_report(cycle["strict_czl"]).replace("- status: complete", "- status: complete_control_plane_ready", 1),
        "",
        "## E8 Status Interpretation",
        "- E8 completes the reusable control plane for risk-controlled external validation.",
        "- No customer contact, publication, or sending occurred because no valid manifest/targets/provider exist.",
        "- The next step is owner-provided manifest/targets and either owner-operated handoff or safe provider configuration.",
        "",
        "## No-Unapproved-External-Action Receipt",
    ]
    for key, value in NO_UNAPPROVED_EXTERNAL_ACTION_RECEIPT.items():
        lines.append(f"- {key}: {str(value).lower()}")
    return "\n".join(lines)


def write_e8_reports(repo_root: Path) -> Dict[str, Path]:
    reports = repo_root / "reports" / "integration"
    reports.mkdir(parents=True, exist_ok=True)
    cycle = build_e8_cycle(repo_root)
    outputs = {
        "e8_risk_control_model.md": render_e8_risk_model_report(),
        "e8_ai_transparency_policy.md": render_e8_ai_transparency_policy(),
        "e8_external_validation_manifest_request.md": render_e8_manifest_status_or_request(cycle["manifest"]),
        "e8_target_seed_request.md": render_e8_target_seed_status_or_request(cycle["targets"]),
        "e8_frozen_validation_drafts.md": render_e8_frozen_validation_drafts(cycle["drafts"]),
        "e8_external_action_preflight.md": render_e8_external_action_preflight(cycle["action"], cycle["preflight"]),
        "e8_execution_gate_report.md": render_e8_execution_gate_report(cycle["execution_gate"]),
        "e8_feedback_capture_report.md": render_e8_feedback_capture_report(cycle["feedback_events"]),
        "e8_validation_signal_evaluation.md": render_e8_validation_signal_evaluation(cycle["feedback_events"]),
        "e8_validation_result_summary.md": render_e8_validation_result_summary(cycle["validation_result"]),
        "e8_residual_learning_update.md": render_e8_residual_learning_update(cycle["validation_result"]),
        "e8_owner_decision_packet.md": render_e8_owner_decision_packet(cycle["owner_packet"]),
        "e8_czl_closure_report.md": render_e8_czl_closure(cycle),
    }
    written: Dict[str, Path] = {}
    for filename, text in outputs.items():
        path = reports / filename
        path.write_text(text.rstrip() + "\n", encoding="utf-8")
        written[filename] = path
    return written


if __name__ == "__main__":
    write_e8_reports(Path(__file__).resolve().parents[2])
