from __future__ import annotations

from dataclasses import asdict, dataclass
from typing import Any, Dict, List

from .e17_response_classifier import E17ResponseClassification


@dataclass(frozen=True)
class E17PaidSignalReadinessPacket:
    artifact_id: str
    action_id: str
    selected_target: str
    offer: str
    current_feedback_state: str
    paid_signal_strength: int
    paid_signal_label: str
    manual_follow_up_allowed: bool
    meeting_scheduling_allowed: bool
    offer_revision_required: bool
    target_revision_required: bool
    target_expansion_allowed: bool
    provider_adapter_preparation_allowed: bool
    broader_commercial_acceleration_allowed: bool
    cieU_writeback_allowed: bool
    next_allowed_commercial_action: str
    limitations: List[str]
    external_action_executed: bool = False

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


def build_paid_signal_readiness_packet(selected_action: Dict[str, Any], classification: E17ResponseClassification) -> E17PaidSignalReadinessPacket:
    strength = classification.paid_signal_strength
    return E17PaidSignalReadinessPacket(
        artifact_id="e17_paid_signal_readiness_packet",
        action_id=str(selected_action.get("action_id", "unknown_action")),
        selected_target=str(selected_action.get("target_name", "selected target")),
        offer="48h AI Agent Implementation Readiness Review",
        current_feedback_state=classification.feedback_type,
        paid_signal_strength=strength,
        paid_signal_label=classification.paid_signal_label,
        manual_follow_up_allowed=strength >= 3 and not classification.suppression_required,
        meeting_scheduling_allowed=strength >= 5 and not classification.suppression_required,
        offer_revision_required=classification.offer_revision_required,
        target_revision_required=classification.target_revision_required,
        target_expansion_allowed=strength <= 1,
        provider_adapter_preparation_allowed=True,
        broader_commercial_acceleration_allowed=strength >= 4,
        cieU_writeback_allowed=False,
        next_allowed_commercial_action=(
            "owner_manual_send_first" if classification.feedback_type == "no_response_yet" else classification.next_action_allowed
        ),
        limitations=[
            "No real customer signal is claimed until owner imports response evidence.",
            "Provider adapter preparation remains no-send unless owner explicitly activates E16C1 later.",
            "CIEU/core writeback remains hard-gated.",
        ],
    )


def build_next_target_expansion_queue(c3_batch: Dict[str, Any], selected_action_id: str) -> Dict[str, Any]:
    entries: List[Dict[str, Any]] = []
    for action in c3_batch.get("actions", []):
        action_id = str(action.get("action_id", ""))
        role = str(action.get("role", "candidate"))
        missing = list(action.get("missing_fields", []))
        suppression_reason = str(action.get("exclusion_or_suppression_reason", ""))
        if action_id == selected_action_id:
            status = "current_selected_action"
        elif role in {"primary", "fallback"} and not missing:
            status = "ready_candidate_from_existing_repo_evidence"
        elif role in {"suppression_candidate", "suppressed"} or "suppress" in suppression_reason.lower():
            status = "suppress_or_do_not_contact"
        elif missing:
            status = "needs_evidence_expansion"
        else:
            status = "blocked_due_to_missing_source"
        entries.append(
            {
                "action_id": action_id,
                "target_id": action.get("target_id"),
                "target_name": action.get("target_name"),
                "role": role,
                "status": status,
                "missing_fields": missing,
                "selection_basis": action.get("selection_reason"),
                "offer_thesis": action.get("offer_thesis"),
                "external_action_executed": False,
            }
        )
    return {
        "artifact_id": "e17_next_target_expansion_queue",
        "source_batch_id": c3_batch.get("batch_id"),
        "selection_policy": "reuse_existing_repo_evidence_only_no_web_scrape_no_fake_targets",
        "selected_action_id": selected_action_id,
        "entries": entries,
        "external_action_executed": False,
    }


def render_paid_signal_and_offer_report(packet: Dict[str, Any], offer_revision: Dict[str, Any]) -> str:
    lines = [
        "# E17 Paid Signal and Offer Revision",
        "",
        f"- current_feedback_state: {packet['current_feedback_state']}",
        f"- paid_signal_strength: {packet['paid_signal_strength']}",
        f"- paid_signal_label: {packet['paid_signal_label']}",
        f"- next_allowed_commercial_action: {packet['next_allowed_commercial_action']}",
        f"- offer_revision_required: {str(packet['offer_revision_required']).lower()}",
        "",
        "## Offer Revision Path",
        f"- lead_offer_should_remain: {str(offer_revision['lead_offer_should_remain']).lower()}",
        f"- revision_priority: {offer_revision['revision_priority']}",
    ]
    lines.extend(f"- {item}" for item in offer_revision.get("recommended_revisions", []))
    return "\n".join(lines).rstrip() + "\n"
