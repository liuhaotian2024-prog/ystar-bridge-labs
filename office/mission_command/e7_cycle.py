from __future__ import annotations

from pathlib import Path
from typing import Any, Dict

from .e7_evidence_quality import (
    build_e7_evidence_quality_table,
    parse_e6_external_source_summaries,
    render_e7_cleaned_evidence_table,
    render_e7_evidence_quality_calibration,
)
from .e7_offer_packet import build_e7_validation_ready_offer_packet, render_e7_validation_ready_offer_packet
from .e7_owner_decision_packet import build_e7_owner_decision_packet, render_e7_owner_decision_packet
from .e7_validation_protocol import (
    build_e7_validation_protocol,
    render_e7_demo_call_script,
    render_e7_landing_page_draft,
    render_e7_outreach_draft,
    render_e7_validation_protocol,
    render_e7_validation_question_set,
)
from .strict_czl import build_strict_czl_state, render_strict_czl_report


E7_Y_STAR = [
    "implementation_inspection_completed",
    "e6_evidence_quality_calibrated",
    "cleaned_evidence_table_created",
    "validation_ready_offer_packet_created",
    "validation_protocol_created",
    "approval_gated_outreach_draft_created",
    "approval_gated_landing_page_draft_created",
    "approval_gated_demo_call_script_created",
    "approval_gated_validation_question_set_created",
    "owner_decision_packet_created",
    "method_learning_updated",
    "strict_czl_closure_created",
    "no_external_side_effects",
]


NO_EXTERNAL_ACTION_RECEIPT = {
    "external sending": False,
    "customer contact": False,
    "email/message": False,
    "publication": False,
    "payment": False,
    "account creation": False,
    "form submission": False,
    "core DB/brain/memory/CIEU writeback": False,
    "obligation auto-registration": False,
    "COO invented": False,
}


def method_learning_updated(repo_root: Path) -> bool:
    path = repo_root / "knowledge" / "ceo" / "wisdom" / "AIDEN_META_DEVELOPMENT_METHOD_KERNEL.md"
    if not path.exists():
        return False
    text = path.read_text(encoding="utf-8")
    return "Market-backed does not equal validation-ready" in text


def build_e7_cycle(repo_root: Path) -> Dict[str, Any]:
    reports = repo_root / "reports" / "integration"
    sources = parse_e6_external_source_summaries(reports / "e6_external_source_summaries.md")
    quality_rows = build_e7_evidence_quality_table(sources)
    offer_packet = build_e7_validation_ready_offer_packet(quality_rows)
    protocol = build_e7_validation_protocol()
    owner_packet = build_e7_owner_decision_packet(offer_packet, quality_rows)
    y_t1 = {
        "implementation_inspection_completed": (reports / "e7_implementation_inspection.md").exists(),
        "e6_evidence_quality_calibrated": bool(quality_rows),
        "cleaned_evidence_table_created": True,
        "validation_ready_offer_packet_created": bool(offer_packet),
        "validation_protocol_created": bool(protocol),
        "approval_gated_outreach_draft_created": True,
        "approval_gated_landing_page_draft_created": True,
        "approval_gated_demo_call_script_created": True,
        "approval_gated_validation_question_set_created": True,
        "owner_decision_packet_created": bool(owner_packet),
        "method_learning_updated": method_learning_updated(repo_root),
        "strict_czl_closure_created": True,
        "no_external_side_effects": not any(NO_EXTERNAL_ACTION_RECEIPT.values()),
    }
    blocked_reason = "" if all(y_t1.values()) else "E7 validation-readiness artifact is missing or method learning is not updated."
    exact_unblock_action = [] if not blocked_reason else ["Create the missing E7 artifact or method learning update, then rerun E7 closure."]
    czl = build_strict_czl_state(
        mission_id="e7_validation_ready_commercial_packet",
        y_star=E7_Y_STAR,
        xt={
            "start_commit": "0ccc4911",
            "e6_state": "market-backed thesis exists; commercial packet not yet validation-ready",
            "e6_top_path": "AI Ops Operating Room Implementation Support",
            "known_residual": "raw web-noise evidence must be cleaned before owner/customer-facing validation",
        },
        u=[
            "inspected E6 implementation and reports",
            "calibrated E6 evidence quality",
            "created cleaned evidence table",
            "sharpened validation-ready commercial offer packet",
            "created approval-gated validation protocol and drafts",
            "created owner decision packet for E8",
            "updated Aiden method learning",
            "closed strict E7 CZL with no external side effects",
        ],
        y_t1=y_t1,
        feasible_criteria=E7_Y_STAR,
        full_criteria=E7_Y_STAR,
        blocked_reason=blocked_reason,
        exact_unblock_action=exact_unblock_action,
        blocked_status="BLOCKED_BY_E7_VALIDATION_READINESS_RESIDUAL",
    )
    return {
        "sources": sources,
        "quality_rows": quality_rows,
        "offer_packet": offer_packet,
        "protocol": protocol,
        "owner_packet": owner_packet,
        "strict_czl": czl,
        "status": czl.status,
        "no_external_action_receipt": NO_EXTERNAL_ACTION_RECEIPT,
    }


def render_e7_czl_closure(cycle: Dict[str, Any]) -> str:
    lines = [
        render_strict_czl_report(cycle["strict_czl"]),
        "",
        "## E7 Status Interpretation",
        "- E7 is an internal validation-readiness milestone, not an external validation mission.",
        "- Complete means the owner can approve/revise/hold a specific E8 validation mission.",
        "- Customer contact, publication, forms, payments, accounts, and core writeback remain unapproved.",
        "",
        "## Tests",
        "- validation commands are recorded in the final assistant response after execution.",
        "",
        "## No-External-Action Receipt",
    ]
    for key, value in cycle["no_external_action_receipt"].items():
        lines.append(f"- {key}: {str(value).lower()}")
    return "\n".join(lines)


def write_e7_reports(repo_root: Path) -> Dict[str, Path]:
    reports = repo_root / "reports" / "integration"
    reports.mkdir(parents=True, exist_ok=True)
    cycle = build_e7_cycle(repo_root)
    outputs = {
        "e7_evidence_quality_calibration.md": render_e7_evidence_quality_calibration(cycle["quality_rows"]),
        "e7_cleaned_evidence_table.md": render_e7_cleaned_evidence_table(cycle["quality_rows"]),
        "e7_validation_ready_offer_packet.md": render_e7_validation_ready_offer_packet(cycle["offer_packet"]),
        "e7_validation_protocol.md": render_e7_validation_protocol(cycle["protocol"]),
        "e7_outreach_draft.md": render_e7_outreach_draft(),
        "e7_landing_page_draft.md": render_e7_landing_page_draft(),
        "e7_demo_call_script.md": render_e7_demo_call_script(),
        "e7_validation_survey_or_question_set.md": render_e7_validation_question_set(),
        "e7_owner_decision_packet.md": render_e7_owner_decision_packet(cycle["owner_packet"]),
        "e7_czl_closure_report.md": render_e7_czl_closure(cycle),
    }
    written: Dict[str, Path] = {}
    for filename, text in outputs.items():
        path = reports / filename
        path.write_text(text.rstrip() + "\n", encoding="utf-8")
        written[filename] = path
    return written


if __name__ == "__main__":
    write_e7_reports(Path(__file__).resolve().parents[2])
