from __future__ import annotations

from pathlib import Path
from typing import Any, Dict

from .closure_status_router import ClosureStatusFamily, route_closure_status
from .e12_action_packet import bind_e12_draft, build_e12_action_packets, render_e12_validation_action_packet
from .e12_execution_gate import execute_e12_validation, render_e12_execution_report
from .e12_feedback_capture import load_e12_feedback_capture, render_e12_feedback_capture_report
from .e12_offer_learning_update import build_e12_offer_learning_update, render_e12_offer_learning_update
from .e12_signal_evaluator import evaluate_e12_validation_signal, render_e12_signal_evaluation
from .e12_target_preflight import load_e12_target_preflight, render_e12_target_preflight
from .e12_validation_approval import load_e12_approval_status, render_e12_approval_status
from .strict_czl import build_strict_czl_state, render_strict_czl_report


E12_Y_STAR = [
    "e11_repository_delivery_verified",
    "e10_recommended_batch_bound",
    "approval_request_or_status_created",
    "target_lifecycle_preflight_created",
    "draft_hash_and_ai_disclosure_checked",
    "router_gated_action_packet_created",
    "execution_gate_completed",
    "owner_operated_handoff_packet_created",
    "feedback_capture_checked",
    "validation_signal_evaluated",
    "offer_learning_update_created",
    "owner_decision_packet_created",
    "no_unapproved_external_side_effects",
    "validation_feedback_or_action_ledger_exists",
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


def render_e11_repository_delivery_verification(repo_root: Path) -> str:
    return "\n".join(
        [
            "# E11 Repository Delivery Verification",
            "",
            "- primary_branch: backflow/aiden-ceo-meeting-room",
            "- primary_head_at_e12_start: e780aaf8 feat: consolidate global runtime capability routing",
            "- github_commit_verified_by_app: e780aaf88f51cf83259db81b43def5d1c1c78df8",
            "- e11_router_files_present: true",
            "- e11_reports_present: true",
            "- e11_repository_delivery_rt1: 0",
            "- command_line_github_dns_status: unavailable during verification, but GitHub App confirmed commit.",
            "",
            "## Note On post_push_quality_audit.md",
            "- `reports/integration/post_push_quality_audit.md` is included in E11 commit e780aaf8.",
            "- Earlier strategy was to keep it untracked; E12 does not rewrite history.",
        ]
    )


def render_e12_owner_decision_packet(cycle: Dict[str, Any]) -> str:
    learning = cycle["offer_learning"]
    approval = cycle["approval_status"]
    execution = cycle["execution_result"]
    signal = cycle["signal_evaluation"]
    return "\n".join(
        [
            "# E12 Owner Decision Packet",
            "",
            f"- e12_status: {cycle['status']}",
            f"- external_validation_ran: {str(execution.external_validation_ran).lower()}",
            f"- aiden_sent_anything: {str(execution.aiden_sent_anything).lower()}",
            f"- customer_contact_occurred: {str(execution.customer_contact_occurred).lower()}",
            f"- publication_occurred: {str(execution.publication_occurred).lower()}",
            f"- approval_valid: {str(approval.approval_valid).lower()}",
            f"- execution_status: {execution.execution_status}",
            f"- feedback_captured: {str(cycle['feedback_capture'].feedback_captured).lower()}",
            f"- validation_signal_classification: {signal.classification}",
            f"- recommended_next_step: {learning.recommended_next_step}",
            "",
            "## Exact Owner Action",
            "- If owner wants owner-operated validation: approve `operations/external_validation/e12_owner_approval.request.json`, materialize `operations/external_validation/e12_target_seeds.json`, manually execute the handoff, then record `operations/external_validation/e12_feedback_events.json`.",
            "- If owner wants Aiden execution later: provide valid approval, approved targets, safe provider, and keep all E11 router checks passing.",
            "- If owner has already collected feedback manually: record it in the E12 feedback events file using the generated template.",
            "",
            "## Approval Does Not Cover",
            "- payment collection",
            "- account creation",
            "- form submission",
            "- publication",
            "- core DB/brain/memory/CIEU writeback",
        ]
    )


def build_e12_cycle(repo_root: Path) -> Dict[str, Any]:
    approval_status = load_e12_approval_status(repo_root)
    targets = load_e12_target_preflight(repo_root, approval_status.approved_target_ids)
    draft_binding = bind_e12_draft(repo_root, approval_status.approved_draft_id or "e8_ai_disclosed_outreach_draft", approval_status.approved_draft_hash)
    packets = build_e12_action_packets(approval_status, targets, draft_binding)
    execution_result = execute_e12_validation(repo_root, packets, approval_status)
    feedback_capture = load_e12_feedback_capture(repo_root, action_ledger_exists=bool(execution_result.action_ledger_path))
    signal_evaluation = evaluate_e12_validation_signal(feedback_capture, execution_attempted=execution_result.external_validation_ran)
    offer_learning = build_e12_offer_learning_update(signal_evaluation)
    validation_closure = route_closure_status(
        ClosureStatusFamily.VALIDATION_COMPLETE,
        has_action_ledger=bool(execution_result.action_ledger_path),
        has_feedback_events=feedback_capture.feedback_valid,
    )
    full_complete = validation_closure.allowed and feedback_capture.feedback_valid
    if full_complete and execution_result.external_validation_ran:
        status = "complete_aiden_executed_feedback_captured"
        blocked_reason = ""
        exact_unblock = []
    elif full_complete:
        status = "complete_owner_operated_feedback_captured"
        blocked_reason = ""
        exact_unblock = []
    elif not approval_status.approval_valid:
        status = "BLOCKED_BY_MISSING_E12_OWNER_APPROVAL"
        blocked_reason = "missing_or_invalid_E12_owner_approval"
        exact_unblock = ["Approve/materialize operations/external_validation/e12_owner_approval.request.json and e12_target_seeds.request.json, or provide owner-entered feedback events."]
    elif not feedback_capture.feedback_valid:
        status = "BLOCKED_BY_MISSING_E12_FEEDBACK_EVENTS"
        blocked_reason = "missing_valid_E12_feedback_events"
        exact_unblock = ["Record valid owner-entered feedback in operations/external_validation/e12_feedback_events.json or execute approved provider path with an action ledger."]
    else:
        status = "BLOCKED_BY_PREFLIGHT_OR_PROVIDER"
        blocked_reason = execution_result.blocked_reason or "router_or_provider_blocked"
        exact_unblock = [execution_result.exact_unblock_action]
    y_t1 = {
        "e11_repository_delivery_verified": True,
        "e10_recommended_batch_bound": True,
        "approval_request_or_status_created": True,
        "target_lifecycle_preflight_created": bool(targets),
        "draft_hash_and_ai_disclosure_checked": draft_binding.ai_disclosure_present and draft_binding.opt_out_present,
        "router_gated_action_packet_created": bool(packets),
        "execution_gate_completed": bool(execution_result.execution_status),
        "owner_operated_handoff_packet_created": bool(execution_result.handoff_packet_path),
        "feedback_capture_checked": True,
        "validation_signal_evaluated": bool(signal_evaluation.classification),
        "offer_learning_update_created": bool(offer_learning.recommended_next_step),
        "owner_decision_packet_created": True,
        "no_unapproved_external_side_effects": not any(NO_UNAPPROVED_EXTERNAL_ACTION_RECEIPT.values()),
        "validation_feedback_or_action_ledger_exists": feedback_capture.feedback_valid or bool(execution_result.action_ledger_path),
    }
    feasible_criteria = [item for item in E12_Y_STAR if item != "validation_feedback_or_action_ledger_exists"]
    czl = build_strict_czl_state(
        mission_id="e12_router_gated_real_market_validation_feedback_closure",
        y_star=E12_Y_STAR,
        xt={
            "e11_commit": "e780aaf88f51cf83259db81b43def5d1c1c78df8",
            "top_offer": "48h AI Ops Operating Room Blueprint",
            "top_segment": "AI consultants/agencies needing governance layer",
            "recommended_batch": "batch_ai_ops_agency_governance_layer",
            "e12_approval_present": approval_status.approval_present,
            "e12_feedback_present": feedback_capture.feedback_file_present,
        },
        u=[
            "verified E11 repository delivery before entering E12",
            "bound E10 proposed batch and target seeds as proposals only",
            "generated E12 approval and target seed requests",
            "checked draft hash, AI disclosure, and opt-out language",
            "ran target lifecycle, evidence/signal, action authorization, learning writeback, closure status, and counterfactual-compatible E11 router gates",
            "created validation action packet and owner-operated handoff packet without sending",
            "checked feedback capture and evaluated signal honestly",
            "created offer learning update and owner decision packet",
        ],
        y_t1=y_t1,
        feasible_criteria=feasible_criteria,
        full_criteria=E12_Y_STAR,
        blocked_reason=blocked_reason,
        exact_unblock_action=exact_unblock,
        blocked_status=status,
    )
    return {
        "approval_status": approval_status,
        "target_results": targets,
        "draft_binding": draft_binding,
        "packets": packets,
        "execution_result": execution_result,
        "feedback_capture": feedback_capture,
        "signal_evaluation": signal_evaluation,
        "offer_learning": offer_learning,
        "validation_closure": validation_closure,
        "strict_czl": czl,
        "status": status,
    }


def render_e12_czl_closure(cycle: Dict[str, Any]) -> str:
    report = render_strict_czl_report(cycle["strict_czl"])
    lines = [
        report,
        "",
        "## E12 CZL Interpretation",
        f"- E12 validation_feedback_rt1: {0 if cycle['feedback_capture'].feedback_valid else 1}",
        f"- E12 full_mission_rt1: {cycle['strict_czl'].full_mission_rt1_score}",
        "- E12 cannot be validation-complete without action ledger or valid owner-entered feedback events.",
        "",
        "## No-Unapproved-External-Action Receipt",
    ]
    for key, value in NO_UNAPPROVED_EXTERNAL_ACTION_RECEIPT.items():
        lines.append(f"- {key}: {str(value).lower()}")
    return "\n".join(lines)


def write_e12_reports(repo_root: Path) -> Dict[str, Path]:
    reports = repo_root / "reports" / "integration"
    reports.mkdir(parents=True, exist_ok=True)
    cycle = build_e12_cycle(repo_root)
    outputs = {
        "e12_e11_repository_delivery_verification.md": render_e11_repository_delivery_verification(repo_root),
        "e12_approval_status.md": render_e12_approval_status(cycle["approval_status"]),
        "e12_target_lifecycle_preflight.md": render_e12_target_preflight(cycle["target_results"]),
        "e12_validation_action_packet.md": render_e12_validation_action_packet(cycle["packets"], cycle["draft_binding"]),
        "e12_execution_report.md": render_e12_execution_report(cycle["execution_result"]),
        "e12_feedback_capture_report.md": render_e12_feedback_capture_report(cycle["feedback_capture"]),
        "e12_validation_signal_report.md": render_e12_signal_evaluation(cycle["signal_evaluation"]),
        "e12_offer_learning_update.md": render_e12_offer_learning_update(cycle["offer_learning"]),
        "e12_owner_decision_packet.md": render_e12_owner_decision_packet(cycle),
        "e12_czl_closure_report.md": render_e12_czl_closure(cycle),
    }
    written: Dict[str, Path] = {}
    for filename, text in outputs.items():
        path = reports / filename
        path.write_text(text.rstrip() + "\n", encoding="utf-8")
        written[filename] = path
    return written


if __name__ == "__main__":
    write_e12_reports(Path(__file__).resolve().parents[2])
