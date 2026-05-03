#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from office.mission_command.e14_action_ledger import write_e14_action_ledger_template
from office.mission_command.e14_czl_closure import build_e14_czl_closure, write_e14_czl_closure
from office.mission_command.e14_entry_gate import validate_e14_entry
from office.mission_command.e14_feedback_events import write_e14_feedback_events_template
from office.mission_command.e14_manual_validation_draft import build_e14_manual_validation_draft, validate_e14_manual_draft, write_e14_manual_draft
from office.mission_command.e14_owner_approval_packet import build_e14_owner_approval_packet, validate_e14_owner_approval_packet, write_e14_owner_approval_packet
from office.mission_command.e14_owner_decision_packet import build_e14_owner_decision_packet, render_e14_owner_decision_packet, write_e14_owner_decision_packet
from office.mission_command.e14_signal_evaluator import evaluate_e14_validation_signal, write_e14_validation_signal_report
from office.mission_command.e14_target_candidates import build_e14_target_candidates, validate_e14_target_candidate, write_e14_target_candidates
from office.mission_command.e14_target_scoring import build_e14_target_batch, write_e14_target_batch


def e14_entry_allowed(repo_root: Path) -> bool:
    return validate_e14_entry(repo_root).allowed


def render_prep_report(*, candidates_count: int, selected_count: int, approval_valid: bool, draft_errors: list[str]) -> str:
    return "\n".join(
        [
            "# E14 Owner-Operated Validation Prep",
            "",
            "- exact_offer: 48h AI Agent Implementation Readiness Review",
            f"- target_candidate_count: {candidates_count}",
            f"- selected_target_count: {selected_count}",
            f"- approval_packet_valid: {str(approval_valid).lower()}",
            f"- draft_errors: {', '.join(draft_errors) if draft_errors else 'none'}",
            "- aiden_sent_anything: false",
            "- customer_contact_occurred: false",
            "- publication_occurred: false",
            "",
            "## What This Prepares",
            "- owner approval packet",
            "- manual-send draft",
            "- target batch proposal",
            "- action ledger template",
            "- feedback event template",
            "- validation signal evaluator state",
            "",
            "## What This Does Not Do",
            "- does not approve contact",
            "- does not send email/message",
            "- does not publish",
            "- does not collect payment",
            "- does not enter E15",
        ]
    )


def render_manual_readiness_report(*, draft_hash: str, selected_ids: list[str], signal_classification: str) -> str:
    return "\n".join(
        [
            "# E14 Manual Validation Readiness",
            "",
            f"- draft_hash: {draft_hash}",
            f"- selected_target_ids: {', '.join(selected_ids) if selected_ids else 'none'}",
            f"- validation_signal_classification: {signal_classification}",
            "- action_ledger_template_exists: true",
            "- feedback_events_template_exists: true",
            "- e15_entry_allowed: false",
            "",
            "## Boundary",
            "- Manual validation is owner-operated only.",
            "- Aiden/Codex did not send anything.",
            "- No-response cannot be recorded until a valid owner action ledger exists.",
        ]
    )


def run(repo_root: Path) -> dict[str, object]:
    entry = e14_entry_allowed(repo_root)
    candidates = build_e14_target_candidates(repo_root)
    candidate_errors = [error for candidate in candidates for error in validate_e14_target_candidate(candidate)]
    write_e14_target_candidates(repo_root)
    write_e14_target_batch(repo_root, candidates)
    batch = build_e14_target_batch(candidates)
    selected_ids = list(batch.get("selected_target_ids", []))
    draft = build_e14_manual_validation_draft()
    draft_errors = validate_e14_manual_draft(draft)
    write_e14_manual_draft(repo_root)
    approval_packet = build_e14_owner_approval_packet(candidates, selected_ids, draft)
    approval_errors = validate_e14_owner_approval_packet(approval_packet)
    write_e14_owner_approval_packet(repo_root, approval_packet)
    write_e14_action_ledger_template(repo_root)
    write_e14_feedback_events_template(repo_root)
    signal = evaluate_e14_validation_signal()
    write_e14_validation_signal_report(repo_root)
    owner_packet = build_e14_owner_decision_packet(signal, approval_packet_valid=not approval_errors)
    write_e14_owner_decision_packet(repo_root, owner_packet)
    reports = repo_root / "reports" / "integration"
    reports.mkdir(parents=True, exist_ok=True)
    (reports / "e14_owner_operated_validation_prep.md").write_text(
        render_prep_report(candidates_count=len(candidates), selected_count=len(selected_ids), approval_valid=not approval_errors, draft_errors=draft_errors)
        + "\n",
        encoding="utf-8",
    )
    (reports / "e14_manual_validation_readiness.md").write_text(
        render_manual_readiness_report(draft_hash=draft.draft_hash, selected_ids=selected_ids, signal_classification=signal.classification) + "\n",
        encoding="utf-8",
    )
    (reports / "e14_owner_decision_packet.md").write_text(render_e14_owner_decision_packet(owner_packet) + "\n", encoding="utf-8")
    closure = build_e14_czl_closure(
        entry_allowed=entry,
        approval_packet_valid=not approval_errors,
        manual_validation_ready=not draft_errors and not candidate_errors and bool(selected_ids),
    )
    write_e14_czl_closure(repo_root, closure)
    return {
        "entry_allowed": entry,
        "target_candidate_count": len(candidates),
        "selected_target_count": len(selected_ids),
        "approval_errors": approval_errors,
        "draft_errors": draft_errors,
        "candidate_errors": candidate_errors,
        "signal_classification": signal.classification,
        "e15_entry_allowed": signal.e15_entry_allowed,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="Create E14 owner-operated validation prep packet.")
    parser.add_argument("--repo-root", default=".")
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()
    result = run(Path(args.repo_root).resolve())
    if args.json:
        print(json.dumps(result, indent=2))
    else:
        print(f"E14 target candidates: {result['target_candidate_count']}")
        print(f"E14 selected targets: {result['selected_target_count']}")
        print(f"E14 signal classification: {result['signal_classification']}")
    return 0 if result["entry_allowed"] else 2


if __name__ == "__main__":
    raise SystemExit(main())
