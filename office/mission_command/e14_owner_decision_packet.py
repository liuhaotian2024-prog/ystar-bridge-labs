from __future__ import annotations

import json
from dataclasses import asdict, dataclass, field
from pathlib import Path
from typing import Any, Dict, List

from .e14_signal_evaluator import E14ValidationSignalReport


@dataclass(frozen=True)
class E14OwnerDecisionPacket:
    recommended_next_step: str
    exact_offer: str
    proposed_validation_batch: str
    draft_status: str
    approval_packet_status: str
    action_execution_status: str
    feedback_capture_status: str
    e15_entry_allowed: bool
    exact_owner_action: str
    not_approved: List[str] = field(default_factory=list)
    conditions_for_e15: List[str] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


def choose_e14_next_step(signal: E14ValidationSignalReport, approval_packet_valid: bool) -> str:
    if signal.e15_entry_allowed:
        return "proceed_to_E15_only_after_feedback"
    if approval_packet_valid and signal.classification == "no_approval":
        return "owner_approve_manual_validation_batch"
    if not approval_packet_valid:
        return "request_offer_or_target_revision"
    return "hold_until_more_evidence"


def build_e14_owner_decision_packet(signal: E14ValidationSignalReport, approval_packet_valid: bool = True) -> E14OwnerDecisionPacket:
    return E14OwnerDecisionPacket(
        recommended_next_step=choose_e14_next_step(signal, approval_packet_valid),
        exact_offer="48h AI Agent Implementation Readiness Review",
        proposed_validation_batch="e14_owner_operated_readiness_review_batch",
        draft_status="ready_request_only_not_sent",
        approval_packet_status="request_only_not_approval" if approval_packet_valid else "invalid_request_revision_needed",
        action_execution_status="not_executed_by_aiden_or_codex",
        feedback_capture_status="not_captured_until_owner_records_real_feedback",
        e15_entry_allowed=signal.e15_entry_allowed,
        exact_owner_action="Review e14_owner_approval_packet.request.json; if acceptable, owner may manually approve and execute the batch, then record action ledger and feedback events.",
        not_approved=[
            "Aiden sending",
            "customer contact by Codex/Aiden",
            "publication",
            "payment",
            "account creation",
            "form submission",
            "login",
            "core brain/CIEU/memory writeback",
        ],
        conditions_for_e15=[
            "valid owner approval",
            "valid action ledger event",
            "valid owner-entered feedback event",
            "signal evaluator returns weak_positive, strong_positive, or paid_signal_candidate as appropriate",
        ],
    )


def write_e14_owner_decision_packet(repo_root: Path, packet: E14OwnerDecisionPacket) -> Path:
    path = repo_root / "operations" / "external_validation" / "e14_owner_decision_packet.json"
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(packet.to_dict(), indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    return path


def render_e14_owner_decision_packet(packet: E14OwnerDecisionPacket) -> str:
    lines = [
        "# E14 Owner Decision Packet",
        "",
        f"- recommended_next_step: {packet.recommended_next_step}",
        f"- exact_offer: {packet.exact_offer}",
        f"- proposed_validation_batch: {packet.proposed_validation_batch}",
        f"- draft_status: {packet.draft_status}",
        f"- approval_packet_status: {packet.approval_packet_status}",
        f"- action_execution_status: {packet.action_execution_status}",
        f"- feedback_capture_status: {packet.feedback_capture_status}",
        f"- e15_entry_allowed: {str(packet.e15_entry_allowed).lower()}",
        f"- exact_owner_action: {packet.exact_owner_action}",
        "",
        "## Conditions For E15",
    ]
    lines.extend(f"- {item}" for item in packet.conditions_for_e15)
    lines.extend(["", "## Not Approved"])
    lines.extend(f"- {item}" for item in packet.not_approved)
    return "\n".join(lines)
