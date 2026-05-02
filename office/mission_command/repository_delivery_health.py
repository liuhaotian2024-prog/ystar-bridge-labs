from __future__ import annotations

from pathlib import Path
from typing import Dict

from .repository_delivery_czl import build_repository_delivery_czl, render_repository_delivery_czl
from .repository_delivery_status import RepositoryDeliveryAssessment, assess_repository_delivery


def render_repository_delivery_health(assessment: RepositoryDeliveryAssessment) -> str:
    lines = [
        "# Repository Delivery Health",
        "",
        "## Summary",
        f"- branch: {assessment.branch}",
        f"- expected_branch: {assessment.expected_branch}",
        f"- local_head: {assessment.local_head}",
        f"- expected_head: {assessment.expected_head or 'not_specified'}",
        f"- remote_head: {assessment.remote_head or 'unavailable'}",
        f"- worktree_clean: {str(assessment.preflight.worktree_clean).lower()}",
        f"- remote_url_present: {str(assessment.preflight.remote_url_present).lower()}",
        f"- connectivity_ok: {str(assessment.connectivity.ok).lower()}",
        f"- push_attempted: {str(assessment.push_attempt.attempted).lower()}",
        f"- push_succeeded: {str(assessment.push_attempt.succeeded).lower()}",
        f"- remote_confirmation_confirmed: {str(assessment.remote_confirmation.confirmed).lower()}",
        f"- repository_delivery_rt1: {assessment.repository_delivery_rt1}",
        f"- next_milestone_allowed: {str(assessment.next_milestone_allowed).lower()}",
        f"- failure_code: {assessment.failure_code or 'none'}",
        "",
        "## Preflight",
        f"- branch_ok: {str(assessment.preflight.branch_ok).lower()}",
        f"- head_ok: {str(assessment.preflight.head_ok).lower()}",
        f"- push_allowed: {str(assessment.preflight.push_allowed).lower()}",
        f"- remote_url: {assessment.preflight.remote_url_redacted or 'missing'}",
        f"- dirty_paths: {', '.join(assessment.preflight.dirty_paths) or 'none'}",
        f"- unsafe_dirty_paths: {', '.join(assessment.preflight.unsafe_dirty_paths) or 'none'}",
        "",
        "## Connectivity",
        f"- attempted: {str(assessment.connectivity.attempted).lower()}",
        f"- ok: {str(assessment.connectivity.ok).lower()}",
        f"- failure_code: {assessment.connectivity.failure_code or 'none'}",
        f"- raw_error_summary: {assessment.connectivity.raw_error_summary or 'none'}",
        "",
        "## Remote Confirmation",
        f"- attempted: {str(assessment.remote_confirmation.attempted).lower()}",
        f"- confirmed: {str(assessment.remote_confirmation.confirmed).lower()}",
        f"- failure_code: {assessment.remote_confirmation.failure_code or 'none'}",
        f"- residual_reason: {assessment.remote_confirmation.residual_reason or 'none'}",
        "",
        "## E13 Entry Gate",
        "- E13 is allowed only when repository_delivery_rt1 is 0.",
        f"- e13_entry_allowed: {str(assessment.next_milestone_allowed).lower()}",
    ]
    if assessment.owner_handoff:
        lines.extend(["", assessment.owner_handoff])
    return "\n".join(lines)


def write_repository_delivery_reports(
    repo_root: Path,
    expected_branch: str,
    expected_head: str = "",
    remote_name: str = "origin",
    attempt_push: bool = False,
) -> Dict[str, Path]:
    assessment = assess_repository_delivery(
        repo_root=repo_root,
        expected_branch=expected_branch,
        expected_head=expected_head,
        remote_name=remote_name,
        attempt_push=attempt_push,
    )
    czl = build_repository_delivery_czl(assessment)
    reports = repo_root / "reports" / "integration"
    reports.mkdir(parents=True, exist_ok=True)
    outputs = {
        "repository_delivery_health.md": render_repository_delivery_health(assessment),
        "e12r_repository_delivery_reliability.md": "\n\n".join(
            [
                "# E12R Repository Delivery Reliability Closure",
                "",
                "E12R separates local commit existence from true remote repository closure. Local tests and commits are not enough; the remote branch SHA must match local HEAD.",
                render_repository_delivery_health(assessment),
                render_repository_delivery_czl(czl),
                "",
                "## No External Side Effects",
                "- customer_contact: false",
                "- email_or_message_sent: false",
                "- publication: false",
                "- payment: false",
                "- account_creation: false",
                "- form_submission: false",
                "- core_brain_cieu_memory_writeback: false",
            ]
        ),
    }
    written: Dict[str, Path] = {}
    for filename, text in outputs.items():
        path = reports / filename
        path.write_text(text.rstrip() + "\n", encoding="utf-8")
        written[filename] = path
    return written
