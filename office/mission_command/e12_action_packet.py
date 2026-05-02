from __future__ import annotations

from dataclasses import asdict, dataclass, field
from pathlib import Path
from typing import Any, Dict, List

from .action_authorization_router import ActionAuthorizationRequest, authorize_external_action
from .e8_draft_freeze import freeze_validation_drafts, validate_frozen_draft_transparency
from .e12_target_preflight import E12TargetPreflightResult


AI_DISCLOSURE = "I'm Aiden, an AI-assisted CEO/runtime agent for Y*Bridge Labs. I'm testing whether this 48h offer is useful before asking anyone to buy it."
OPT_OUT_LANGUAGE = "If this is not useful, please ignore this message; no automated follow-up will happen unless you reply or opt in."


@dataclass(frozen=True)
class E12DraftBinding:
    draft_id: str
    draft_hash: str
    draft_path: str
    hash_matches_approval: bool
    ai_disclosure_present: bool
    opt_out_present: bool
    errors: List[str] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


@dataclass(frozen=True)
class E12ValidationActionPacket:
    action_id: str
    target_id: str
    target_label: str
    channel: str
    draft_id: str
    draft_hash: str
    ai_transparency_statement: str
    opt_out_language: str
    max_count: int
    stop_conditions: List[str]
    owner_approval_reference: str
    target_router_state: str
    action_authorization_allowed: bool
    action_authorization_blocked_reason: str
    external_action_expected: bool
    packet_errors: List[str] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


def bind_e12_draft(repo_root: Path, approved_draft_id: str, approved_draft_hash: str) -> E12DraftBinding:
    drafts = freeze_validation_drafts(repo_root)
    selected = next((draft for draft in drafts if draft["draft_id"] == (approved_draft_id or "e8_ai_disclosed_outreach_draft")), None)
    if not selected:
        return E12DraftBinding(approved_draft_id, "", "", False, False, False, ["approved_draft_not_found"])
    errors = validate_frozen_draft_transparency(selected)
    hash_matches = bool(approved_draft_hash and approved_draft_hash == selected.get("content_hash"))
    if approved_draft_hash and not hash_matches:
        errors.append("approved_draft_hash_mismatch")
    return E12DraftBinding(
        draft_id=selected["draft_id"],
        draft_hash=selected["content_hash"],
        draft_path=selected["source_path"],
        hash_matches_approval=hash_matches,
        ai_disclosure_present=bool(selected["ai_disclosure_present"]),
        opt_out_present=bool(selected["opt_out_present"]),
        errors=list(dict.fromkeys(errors)),
    )


def build_e12_action_packets(
    approval_status: Any,
    target_results: List[E12TargetPreflightResult],
    draft_binding: E12DraftBinding,
) -> List[E12ValidationActionPacket]:
    packets: List[E12ValidationActionPacket] = []
    for index, target in enumerate(target_results, start=1):
        lifecycle_state = "preflighted_action_target" if target.preflight_allowed else target.lifecycle_state
        auth_request = ActionAuthorizationRequest(
            action_id=f"e12_validation_action_{index:03d}",
            action_type="send_validation_message",
            risk_tier="Tier 2",
            target_lifecycle_state=lifecycle_state,
            owner_approval_present=bool(approval_status.approval_valid),
            manifest_valid=bool(approval_status.approval_valid),
            channel_approved=bool(approval_status.approval_valid),
            draft_hash_valid=bool(draft_binding.hash_matches_approval or not approval_status.approval_present),
            y_star_gov_decision="owner_approval_required_and_present" if approval_status.approval_valid else "owner_approval_missing",
            gov_mcp_gateway_available=True,
            gov_mcp_preflight_passed=bool(approval_status.approval_valid and target.preflight_allowed),
            execution_provider_available=False,
            no_forbidden_side_effects=True,
        )
        auth = authorize_external_action(auth_request)
        errors = list(target.errors) + list(draft_binding.errors)
        if not approval_status.approval_valid:
            errors.extend(approval_status.errors)
        packets.append(
            E12ValidationActionPacket(
                action_id=auth_request.action_id,
                target_id=target.target_id,
                target_label=target.target_label,
                channel="owner_selected_email_or_public_general_channel_after_owner_review",
                draft_id=draft_binding.draft_id,
                draft_hash=draft_binding.draft_hash,
                ai_transparency_statement=AI_DISCLOSURE,
                opt_out_language=OPT_OUT_LANGUAGE,
                max_count=max(int(approval_status.max_external_messages or 0), 0),
                stop_conditions=[],
                owner_approval_reference=approval_status.approval_path if approval_status.approval_present else approval_status.request_path,
                target_router_state=target.lifecycle_state,
                action_authorization_allowed=auth.allowed,
                action_authorization_blocked_reason=auth.blocked_reason,
                external_action_expected=False,
                packet_errors=list(dict.fromkeys(error for error in errors if error)),
            )
        )
    return packets


def render_e12_validation_action_packet(packets: List[E12ValidationActionPacket], draft_binding: E12DraftBinding) -> str:
    lines = [
        "# E12 Validation Action Packet",
        "",
        "## Draft Binding",
        f"- draft_id: {draft_binding.draft_id}",
        f"- draft_hash: {draft_binding.draft_hash}",
        f"- draft_path: {draft_binding.draft_path}",
        f"- hash_matches_approval: {str(draft_binding.hash_matches_approval).lower()}",
        f"- ai_disclosure_present: {str(draft_binding.ai_disclosure_present).lower()}",
        f"- opt_out_present: {str(draft_binding.opt_out_present).lower()}",
        f"- errors: {', '.join(draft_binding.errors) or 'none'}",
        "",
        "## Action Packets",
    ]
    for packet in packets:
        lines.extend(
            [
                f"### {packet.action_id}",
                f"- target_id: {packet.target_id}",
                f"- target_label: {packet.target_label}",
                f"- channel: {packet.channel}",
                f"- draft_id: {packet.draft_id}",
                f"- draft_hash: {packet.draft_hash}",
                f"- target_router_state: {packet.target_router_state}",
                f"- action_authorization_allowed: {str(packet.action_authorization_allowed).lower()}",
                f"- action_authorization_blocked_reason: {packet.action_authorization_blocked_reason or 'none'}",
                f"- external_action_expected: {str(packet.external_action_expected).lower()}",
                f"- packet_errors: {', '.join(packet.packet_errors) or 'none'}",
                f"- ai_transparency_statement: {packet.ai_transparency_statement}",
                f"- opt_out_language: {packet.opt_out_language}",
                "",
            ]
        )
    return "\n".join(lines).rstrip()

