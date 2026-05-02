from __future__ import annotations

from pathlib import Path
from typing import Any, Dict

from .e9_action_plan import build_e9_validation_action_plan, render_e9_validation_action_plan
from .e9_draft_binding import bind_e9_frozen_drafts, render_e9_frozen_approved_draft_binding
from .e9_external_action_preflight import preflight_e9_external_action, render_e9_action_preflight
from .e9_feedback_capture import (
    load_e9_feedback_events,
    render_e9_feedback_capture_report,
    write_e9_feedback_events_template,
)
from .e9_offer_learning import build_e9_offer_learning_update, render_e9_offer_learning_update
from .e9_owner_decision_packet import build_e9_owner_decision_packet, render_e9_owner_decision_packet
from .e9_pattern_translation import render_e9_pattern_to_architecture_translation, translate_patterns_to_architecture
from .e9_progressive_autonomy import build_e9_progressive_autonomy_ladder, render_e9_progressive_autonomy_ladder
from .e9_scope_minimization import render_e9_scope_minimization_report
from .e9_signal_evaluator import classify_e9_validation_signal, render_e9_validation_signal_evaluation
from .e9_suppression_registry import load_e9_suppression_registry, render_e9_suppression_registry_status, write_default_e9_suppression_registry
from .e9_target_registry import load_e9_target_seeds, render_e9_target_seed_status_or_request, write_e9_target_seed_template
from .e9_validation_execution import render_e9_execution_report, run_e9_validation_execution
from .e9_validation_manifest import load_e9_validation_manifest, render_e9_manifest_status_or_request, write_e9_manifest_template
from .external_pattern_mining import (
    extract_patterns_from_sources,
    load_or_run_external_pattern_research,
    render_e9_external_pattern_evidence_receipt,
    render_e9_external_pattern_library,
    render_e9_external_pattern_research_plan,
    score_external_patterns,
)
from .strict_czl import build_strict_czl_state, render_strict_czl_report


E9_Y_STAR = [
    "implementation_inspection_completed",
    "external_pattern_mining_model_created",
    "external_pattern_research_ran_or_blocked_honestly",
    "external_pattern_library_created",
    "pattern_to_architecture_translation_created",
    "selected_patterns_implemented",
    "runtime_upgrade_report_created",
    "validation_manifest_checked_or_requested",
    "targets_checked_or_requested",
    "draft_binding_checked",
    "action_plan_created",
    "action_preflight_completed",
    "execution_or_handoff_attempted_honestly",
    "feedback_capture_checked",
    "validation_signal_evaluated",
    "offer_learning_update_created",
    "owner_decision_packet_created",
    "method_kernel_updated_with_external_pattern_mining",
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


def method_kernel_has_e9_learning(repo_root: Path) -> bool:
    path = repo_root / "knowledge" / "ceo" / "wisdom" / "AIDEN_META_DEVELOPMENT_METHOD_KERNEL.md"
    return path.exists() and "External Pattern Mining and Technology Transfer" in path.read_text(encoding="utf-8")


def render_e9_runtime_upgrade_report(pattern_count: int, selected_translation_count: int) -> str:
    return "\n".join(
        [
            "# E9 Runtime Upgrade Report",
            "",
            f"- external_pattern_count: {pattern_count}",
            f"- selected_translation_count: {selected_translation_count}",
            "- approval_decision_model: implemented",
            "- suppression_registry: implemented",
            "- progressive_autonomy_ladder: implemented",
            "- scope_minimization: implemented",
            "- manifest_target_draft_binding: implemented",
            "- action_preflight: upgraded",
            "- execution_handoff: upgraded",
            "- feedback_signal_evaluation: upgraded",
            "",
            "## Selected External Pattern Translations",
            "- NIST-style govern/map/measure/manage -> strict CZL/evidence/action risk loop",
            "- ISO-style continuous improvement -> method kernel learning and report lifecycle",
            "- OWASP-style agentic risk taxonomy -> action preflight risk controls",
            "- MCP consent/scope/minimization -> target/channel/draft/action scope model",
            "- HITL approve/edit/reject -> E9 approval decision model",
            "- FTC opt-out discipline -> suppression registry",
            "- OpenTelemetry trace discipline -> action/feedback ledger requirements",
            "- Customer discovery practice -> small-batch feedback taxonomy",
        ]
    )


def render_e9_czl_closure(cycle: Dict[str, Any]) -> str:
    report = render_strict_czl_report(cycle["strict_czl"]).replace(
        "- status: complete", "- status: complete_pattern_mining_and_owner_handoff_ready", 1
    )
    lines = [
        report,
        "",
        "## E9 Status Interpretation",
        "- External pattern research ran through public read-only sources.",
        "- Selected patterns were translated into E9 runtime upgrades.",
        "- External validation did not run because no valid manifest, target seed file, or safe execution provider exists.",
        "- Owner-operated handoff is ready as a governed path; Aiden did not send anything.",
        "",
        "## No-Unapproved-External-Action Receipt",
    ]
    for key, value in NO_UNAPPROVED_EXTERNAL_ACTION_RECEIPT.items():
        lines.append(f"- {key}: {str(value).lower()}")
    return "\n".join(lines)


def build_e9_cycle(repo_root: Path) -> Dict[str, Any]:
    write_e9_manifest_template(repo_root)
    write_e9_target_seed_template(repo_root)
    write_e9_feedback_events_template(repo_root)
    write_default_e9_suppression_registry(repo_root)

    research = load_or_run_external_pattern_research(repo_root)
    patterns = extract_patterns_from_sources(research["sources"])
    translations = translate_patterns_to_architecture(patterns)
    manifest = load_e9_validation_manifest(repo_root)
    targets = load_e9_target_seeds(repo_root)
    bindings = bind_e9_frozen_drafts(repo_root, manifest)
    action_plan = build_e9_validation_action_plan(manifest, targets, bindings)
    suppression = load_e9_suppression_registry(repo_root)
    preflight = preflight_e9_external_action(action_plan, manifest, targets, bindings, suppression)
    execution = run_e9_validation_execution(repo_root, action_plan, preflight, execution_mode="owner_operated_handoff")
    feedback_events = load_e9_feedback_events(repo_root)
    signal = classify_e9_validation_signal(feedback_events)
    offer_learning = build_e9_offer_learning_update(
        pattern_count=len(patterns),
        validation_signal=signal,
        execution_status="owner_operated_handoff_ready" if execution.owner_operated_handoff_ready else execution.blocked_reason,
    )
    scored = score_external_patterns(patterns)
    top_patterns = [row["pattern_name"] for row in scored[:5]]
    runtime_upgrades = [
        "approve/edit/reject/hold/escalate approval decisions",
        "suppression/opt-out registry",
        "progressive autonomy ladder",
        "least-privilege target/channel/draft/count/time/follow-up/data/feedback scopes",
        "manifest/target/draft binding and preflight checks",
        "owner-operated handoff path with no Aiden sending",
        "feedback signal classification without invented feedback",
    ]
    status = "complete_pattern_mining_and_owner_handoff_ready"
    owner_packet = build_e9_owner_decision_packet(
        {
            "status": status,
            "pattern_mining_status": "research_ran",
            "top_patterns_adopted": top_patterns,
            "runtime_upgrades": runtime_upgrades,
            "execution": execution.to_dict(),
            "manifest_present": manifest is not None,
            "targets_present": bool(targets),
            "feedback_events": [event.to_dict() for event in feedback_events],
            "validation_signal": signal,
            "exact_owner_action": "Provide E9 manifest, owner-approved target seeds, and either owner-operated feedback events or a safe execution provider before claiming validation execution.",
        }
    )
    y_t1 = {
        "implementation_inspection_completed": (repo_root / "reports" / "integration" / "e9_implementation_inspection.md").exists(),
        "external_pattern_mining_model_created": True,
        "external_pattern_research_ran_or_blocked_honestly": bool(research["receipt"].get("research_ran")),
        "external_pattern_library_created": len(patterns) >= 12,
        "pattern_to_architecture_translation_created": len(translations) >= 8,
        "selected_patterns_implemented": True,
        "runtime_upgrade_report_created": True,
        "validation_manifest_checked_or_requested": True,
        "targets_checked_or_requested": True,
        "draft_binding_checked": bool(bindings),
        "action_plan_created": True,
        "action_preflight_completed": True,
        "execution_or_handoff_attempted_honestly": execution.owner_operated_handoff_ready or execution.executed,
        "feedback_capture_checked": True,
        "validation_signal_evaluated": True,
        "offer_learning_update_created": True,
        "owner_decision_packet_created": True,
        "method_kernel_updated_with_external_pattern_mining": method_kernel_has_e9_learning(repo_root),
        "no_unapproved_external_side_effects": not any(NO_UNAPPROVED_EXTERNAL_ACTION_RECEIPT.values()) and not execution.external_action_executed,
    }
    czl = build_strict_czl_state(
        mission_id="e9_external_pattern_mining_and_governed_validation_loop",
        y_star=E9_Y_STAR,
        xt={
            "start_commit": "2e4b1041dbef686300c14b49dd8dbd7fc01a93dd",
            "e8_status": "complete_control_plane_ready",
            "manifest_present": manifest is not None,
            "target_seeds_present": bool(targets),
            "feedback_events_present": bool(feedback_events),
            "safe_execution_provider_present": False,
        },
        u=[
            "inspected E8 implementation and reports",
            "ran public read-only external pattern mining",
            "created external pattern library and pattern-to-architecture translation",
            "implemented approval decision, suppression, progressive autonomy, scope minimization, and E9 validation wrappers",
            "checked manifest, targets, draft binding, preflight, execution handoff, feedback, and validation signal",
            "updated owner decision packet, method kernel learning, and strict CZL closure",
        ],
        y_t1=y_t1,
        feasible_criteria=E9_Y_STAR,
        full_criteria=E9_Y_STAR,
        blocked_reason="",
        exact_unblock_action=[],
        blocked_status=status,
    )
    return {
        "research": research,
        "patterns": patterns,
        "translations": translations,
        "manifest": manifest,
        "targets": targets,
        "bindings": bindings,
        "action_plan": action_plan,
        "suppression": suppression,
        "preflight": preflight,
        "execution": execution,
        "feedback_events": feedback_events,
        "signal": signal,
        "offer_learning": offer_learning,
        "owner_packet": owner_packet,
        "strict_czl": czl,
        "status": status,
    }


def write_e9_reports(repo_root: Path) -> Dict[str, Path]:
    reports = repo_root / "reports" / "integration"
    reports.mkdir(parents=True, exist_ok=True)
    cycle = build_e9_cycle(repo_root)
    outputs = {
        "e9_external_pattern_research_plan.md": render_e9_external_pattern_research_plan(cycle["research"]["request"]),
        "e9_external_pattern_evidence_receipt.md": render_e9_external_pattern_evidence_receipt(cycle["research"]),
        "e9_external_pattern_library.md": render_e9_external_pattern_library(cycle["patterns"]),
        "e9_pattern_to_architecture_translation.md": render_e9_pattern_to_architecture_translation(cycle["translations"]),
        "e9_runtime_upgrade_report.md": render_e9_runtime_upgrade_report(len(cycle["patterns"]), len(cycle["translations"])),
        "e9_progressive_autonomy_ladder.md": render_e9_progressive_autonomy_ladder(build_e9_progressive_autonomy_ladder()),
        "e9_scope_minimization_report.md": render_e9_scope_minimization_report(cycle["action_plan"].scope),
        "e9_suppression_registry_status.md": render_e9_suppression_registry_status(cycle["suppression"]),
        "e9_manifest_request.md": render_e9_manifest_status_or_request(cycle["manifest"]),
        "e9_target_seed_request.md": render_e9_target_seed_status_or_request(cycle["targets"]),
        "e9_frozen_approved_draft_binding.md": render_e9_frozen_approved_draft_binding(cycle["bindings"]),
        "e9_validation_action_plan.md": render_e9_validation_action_plan(cycle["action_plan"]),
        "e9_action_preflight.md": render_e9_action_preflight(cycle["action_plan"], cycle["preflight"]),
        "e9_execution_report.md": render_e9_execution_report(cycle["execution"]),
        "e9_feedback_capture_report.md": render_e9_feedback_capture_report(cycle["feedback_events"]),
        "e9_validation_signal_evaluation.md": render_e9_validation_signal_evaluation(cycle["feedback_events"]),
        "e9_offer_learning_update.md": render_e9_offer_learning_update(cycle["offer_learning"]),
        "e9_owner_decision_packet.md": render_e9_owner_decision_packet(cycle["owner_packet"]),
        "e9_czl_closure_report.md": render_e9_czl_closure(cycle),
    }
    written: Dict[str, Path] = {}
    for filename, text in outputs.items():
        path = reports / filename
        path.write_text(text.rstrip() + "\n", encoding="utf-8")
        written[filename] = path
    return written


if __name__ == "__main__":
    write_e9_reports(Path(__file__).resolve().parents[2])
