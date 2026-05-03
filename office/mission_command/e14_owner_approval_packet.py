from __future__ import annotations

import json
from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List

from .e14_manual_validation_draft import E14ManualValidationDraft
from .e14_target_candidates import E14_PRIMARY_OFFER, E14TargetCandidate


@dataclass(frozen=True)
class E14OwnerApprovalPacket:
    approval_packet_id: str
    status: str
    exact_offer: str
    target_batch_id: str
    target_ids: List[str]
    target_rationale: List[str]
    draft_id: str
    draft_hash: str
    draft_text: str
    allowed_channel: str
    max_sends: int
    stop_conditions: List[str]
    ai_transparency_language: str
    opt_out_ignore_language: str
    what_is_approved_if_owner_accepts: List[str]
    what_is_not_approved: List[str]
    expiration: str
    revocation_rule: str
    feedback_capture_requirement: str
    action_ledger_requirement: str
    owner_choices: List[str] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


def build_e14_owner_approval_packet(candidates: List[E14TargetCandidate], selected_target_ids: List[str], draft: E14ManualValidationDraft) -> E14OwnerApprovalPacket:
    by_id = {item.target_id: item for item in candidates}
    target_rationale = [f"{target_id}: {by_id[target_id].relevance_to_offer}" for target_id in selected_target_ids if target_id in by_id]
    return E14OwnerApprovalPacket(
        approval_packet_id="e14_owner_operated_manual_validation_request",
        status="request_only_not_approval",
        exact_offer=E14_PRIMARY_OFFER,
        target_batch_id="e14_owner_operated_readiness_review_batch",
        target_ids=selected_target_ids,
        target_rationale=target_rationale,
        draft_id=draft.draft_id,
        draft_hash=draft.draft_hash,
        draft_text=draft.draft_text,
        allowed_channel="owner_selected_manual_email_or_public_general_channel_only_after_owner_approval",
        max_sends=len(selected_target_ids),
        stop_conditions=[
            "any opt-out or stop request",
            "any negative response requesting no follow-up",
            "owner uncertainty about target fit or channel",
            "any request requiring payment, account creation, form submission, login, legal commitment, or production access",
        ],
        ai_transparency_language="I am Aiden, an AI-assisted CEO/runtime agent for Y*Bridge Labs, working with Haotian.",
        opt_out_ignore_language="No pressure, no automated follow-up, and it is completely fine to ignore this.",
        what_is_approved_if_owner_accepts=[
            "owner-operated manual validation only",
            "up to the approved max sends",
            "exact draft hash unless owner edits and re-approves",
            "recording action ledger and owner-entered feedback events",
        ],
        what_is_not_approved=[
            "Aiden autonomous sending",
            "customer contact by Codex/Aiden",
            "publication",
            "payment collection",
            "account creation",
            "form submission",
            "login",
            "tracking links or attachments",
            "core brain/CIEU/memory writeback",
        ],
        expiration="7 days after owner approval or sooner if revoked",
        revocation_rule="Owner may revoke approval at any time; any opt-out suppresses that target immediately.",
        feedback_capture_requirement="Owner must record feedback in e14_feedback_events.template.json format before E15 can evaluate validation signal.",
        action_ledger_requirement="Owner must record each manual send in e14_action_ledger.template.json format; no_response is invalid without a valid action ledger entry.",
        owner_choices=[
            "approve_owner_operated_manual_validation",
            "request_revision",
            "reject",
            "hold",
        ],
    )


def validate_e14_owner_approval_packet(packet: E14OwnerApprovalPacket | Dict[str, Any]) -> List[str]:
    data = packet.to_dict() if isinstance(packet, E14OwnerApprovalPacket) else dict(packet)
    errors: List[str] = []
    if data.get("status") != "request_only_not_approval":
        errors.append("packet_must_be_request_only_not_approval")
    if not data.get("target_ids"):
        errors.append("target_ids_required")
    if int(data.get("max_sends", 0) or 0) > 3:
        errors.append("max_sends_must_be_at_most_three")
    draft_text = str(data.get("draft_text", "")).lower()
    if "ai-assisted" not in draft_text or "aiden" not in draft_text:
        errors.append("draft_requires_ai_transparency")
    if "ignore" not in draft_text or "no automated follow-up" not in draft_text:
        errors.append("draft_requires_opt_out_ignore_language")
    forbidden = " ".join(data.get("what_is_not_approved", [])).lower()
    for item in ["aiden autonomous sending", "payment", "account creation", "form submission", "login"]:
        if item not in forbidden:
            errors.append(f"missing_not_approved_{item.replace(' ', '_')}")
    return list(dict.fromkeys(errors))


def write_e14_owner_approval_packet(repo_root: Path, packet: E14OwnerApprovalPacket) -> Path:
    path = repo_root / "operations" / "external_validation" / "e14_owner_approval_packet.request.json"
    path.parent.mkdir(parents=True, exist_ok=True)
    payload = packet.to_dict()
    payload["created_at"] = datetime.now(timezone.utc).isoformat()
    path.write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    return path
