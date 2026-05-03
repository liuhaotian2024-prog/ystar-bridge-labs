from __future__ import annotations

from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Dict

from .closure_status_router import ClosureStatusFamily, route_closure_status


@dataclass(frozen=True)
class E14CZLClosure:
    entry_rt1: int
    approval_packet_rt1: int
    manual_validation_readiness_rt1: int
    action_execution_rt1: int
    feedback_capture_rt1: int
    repository_delivery_rt1: str | int
    full_mission_rt1: int
    blocked_reason: str

    def to_dict(self) -> Dict[str, object]:
        return asdict(self)


def build_e14_czl_closure(
    *,
    entry_allowed: bool,
    approval_packet_valid: bool,
    manual_validation_ready: bool,
    action_executed: bool = False,
    feedback_captured: bool = False,
    repository_delivery_rt1: str | int = "pending_host_delivery_runner",
) -> E14CZLClosure:
    entry_rt1 = 0 if entry_allowed else 1
    approval_rt1 = 0 if approval_packet_valid else 1
    readiness_rt1 = 0 if manual_validation_ready else 1
    action_rt1 = 0 if action_executed else 1
    feedback_rt1 = 0 if feedback_captured else 1
    repo_closed = repository_delivery_rt1 == 0
    full = 0 if all([entry_rt1 == 0, approval_rt1 == 0, readiness_rt1 == 0, action_rt1 == 0, feedback_rt1 == 0, repo_closed]) else 1
    validation_boundary = route_closure_status(
        ClosureStatusFamily.VALIDATION_COMPLETE,
        has_action_ledger=action_executed,
        has_feedback_events=feedback_captured,
    )
    blocked = ""
    if action_rt1:
        blocked = "owner_manual_action_not_executed"
    if feedback_rt1:
        blocked = "valid_owner_entered_feedback_missing"
    if not validation_boundary.allowed:
        blocked = validation_boundary.blocked_reason
    return E14CZLClosure(
        entry_rt1=entry_rt1,
        approval_packet_rt1=approval_rt1,
        manual_validation_readiness_rt1=readiness_rt1,
        action_execution_rt1=action_rt1,
        feedback_capture_rt1=feedback_rt1,
        repository_delivery_rt1=repository_delivery_rt1,
        full_mission_rt1=full,
        blocked_reason=blocked or "none",
    )


def render_e14_czl_closure(closure: E14CZLClosure) -> str:
    return "\n".join(
        [
            "# E14 CZL Closure",
            "",
            f"- E14 entry_rt1: {closure.entry_rt1}",
            f"- E14 approval_packet_rt1: {closure.approval_packet_rt1}",
            f"- E14 manual_validation_readiness_rt1: {closure.manual_validation_readiness_rt1}",
            f"- E14 action_execution_rt1: {closure.action_execution_rt1}",
            f"- E14 feedback_capture_rt1: {closure.feedback_capture_rt1}",
            f"- E14 repository_delivery_rt1: {closure.repository_delivery_rt1}",
            f"- E14 full_mission_rt1: {closure.full_mission_rt1}",
            f"- blocked_reason: {closure.blocked_reason}",
            "",
            "## Interpretation",
            "- E14 prepares owner-operated validation but does not execute outreach.",
            "- Approval packet is not execution.",
            "- Public evidence is not validation feedback.",
            "- E15 remains blocked until valid action ledger and owner-entered feedback exist.",
            "",
            "## No External Side Effects",
            "- customer_contact: false",
            "- email_or_message_sent: false",
            "- publication: false",
            "- payment: false",
            "- account_creation: false",
            "- form_submission: false",
            "- login: false",
            "- core_brain_cieu_memory_writeback: false",
        ]
    )


def write_e14_czl_closure(repo_root: Path, closure: E14CZLClosure) -> Path:
    path = repo_root / "reports" / "integration" / "e14_czl_closure.md"
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(render_e14_czl_closure(closure) + "\n", encoding="utf-8")
    return path
