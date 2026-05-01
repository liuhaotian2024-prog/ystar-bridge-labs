from __future__ import annotations

from dataclasses import asdict, dataclass
from datetime import datetime, timezone
import hashlib
from typing import Any, Dict, List


@dataclass(frozen=True)
class OwnerDecisionPacket:
    packet_id: str
    mission_id: str
    recommended_next_action: str
    reason: str
    evidence_status: Dict[str, Any]
    czl_status: Dict[str, Any]
    counterfactual_gate_result: Dict[str, Any]
    action_wide_preflight_summary: Dict[str, Any]
    requested_owner_decision: str
    options: List[str]
    exact_boundary_of_approval: str
    external_action_executed: bool

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


def _packet_id(mission_id: str) -> str:
    stamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    digest = hashlib.sha1(mission_id.encode("utf-8")).hexdigest()[:8]
    return f"owner_decision_{stamp}_m_{digest}"


def build_owner_decision_packet(
    mission_id: str,
    evidence_status: Dict[str, Any],
    czl_status: Dict[str, Any],
    counterfactual_gate_result: Dict[str, Any],
    action_wide_preflight_summary: Dict[str, Any],
) -> Dict[str, Any]:
    packet = OwnerDecisionPacket(
        packet_id=_packet_id(mission_id),
        mission_id=mission_id,
        recommended_next_action="Approve or revise a Tier 1 live read-only evidence mission.",
        reason=(
            "The current plan is internally grounded but still lacks live external market evidence. "
            "The next owner decision should enable bounded read-only research, not customer contact."
        ),
        evidence_status=evidence_status,
        czl_status=czl_status,
        counterfactual_gate_result=counterfactual_gate_result,
        action_wide_preflight_summary=action_wide_preflight_summary,
        requested_owner_decision="approve_or_revise_tier1_read_only_research",
        options=["approve", "reject", "request_revision", "hold"],
        exact_boundary_of_approval=(
            "Approval covers only bounded Tier 1 read-only research planning/execution if separately configured and budgeted; "
            "it does not approve customer contact, email, publication, payment, account creation, form submission, obligation registration, or core writeback."
        ),
        external_action_executed=False,
    )
    return packet.to_dict()


def render_owner_decision_packet_markdown(packet: Dict[str, Any]) -> str:
    lines = [
        "## Owner Decision Packet",
        f"- packet_id: {packet['packet_id']}",
        f"- mission_id: {packet['mission_id']}",
        f"- recommended_next_action: {packet['recommended_next_action']}",
        f"- reason: {packet['reason']}",
        f"- requested_owner_decision: {packet['requested_owner_decision']}",
        f"- options: {', '.join(packet['options'])}",
        f"- exact_boundary_of_approval: {packet['exact_boundary_of_approval']}",
        f"- external_action_executed: {packet['external_action_executed']}",
    ]
    return "\n".join(lines)
