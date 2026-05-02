from __future__ import annotations

import json
from dataclasses import asdict, dataclass, field
from pathlib import Path
from typing import Any, Dict, List


E12_APPROVAL_PATH = Path("operations/external_validation/e12_owner_approval.json")
E12_APPROVAL_REQUEST_PATH = Path("operations/external_validation/e12_owner_approval.request.json")
E10_PROPOSED_MANIFEST_PATH = Path("operations/external_validation/e10_external_validation_manifest.proposed.json")
E10_PROPOSED_TARGETS_PATH = Path("operations/external_validation/e10_target_seeds.proposed.json")

E12_ALLOWED_EXECUTION_MODES = {
    "owner_operated_handoff",
    "aiden_executes_if_provider_available",
    "dry_run_only",
}
E12_FORBIDDEN_TRUE_FLAGS = [
    "publication_authorized",
    "payment_authorized",
    "form_submission_authorized",
    "account_creation_authorized",
    "core_writeback_authorized",
]


@dataclass(frozen=True)
class E12ApprovalStatus:
    approval_present: bool
    approval_valid: bool
    approval_path: str
    request_path: str
    approval_state: str
    approved_batch_id: str
    approved_target_ids: List[str]
    approved_draft_id: str
    approved_draft_hash: str
    execution_mode: str
    max_external_messages: int
    errors: List[str] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


def _load_json(path: Path) -> Dict[str, Any]:
    if not path.exists():
        return {}
    return json.loads(path.read_text(encoding="utf-8"))


def _has_placeholder(value: Any) -> bool:
    if isinstance(value, str):
        return "OWNER_TO_FILL" in value or "OWNER_TO_REVIEW" in value or value.strip() == ""
    if isinstance(value, list):
        return any(_has_placeholder(item) for item in value)
    if isinstance(value, dict):
        return any(_has_placeholder(item) for item in value.values())
    return False


def build_e12_approval_request(repo_root: Path) -> Dict[str, Any]:
    proposal = _load_json(repo_root / E10_PROPOSED_MANIFEST_PATH)
    target_proposal = _load_json(repo_root / E10_PROPOSED_TARGETS_PATH)
    target_ids = proposal.get("approved_target_seed_ids") or [item.get("target_id") for item in target_proposal.get("targets", [])]
    draft_ids = proposal.get("approved_draft_ids") or ["e8_ai_disclosed_outreach_draft"]
    draft_id = draft_ids[0]
    draft_hash = (proposal.get("approved_draft_hashes") or {}).get(draft_id, "OWNER_TO_FILL_DRAFT_HASH")
    budget = proposal.get("autonomy_budget") or {}
    return {
        "request_type": "e12_router_gated_validation_approval_request",
        "approval_state": "proposed",
        "proposal_only": True,
        "this_is_not_approval": True,
        "approval_id": "OWNER_TO_FILL_E12_APPROVAL_ID",
        "approved_by": "OWNER_TO_FILL",
        "approved_at": "OWNER_TO_FILL",
        "top_offer": proposal.get("top_offer", "48h AI Ops Operating Room Blueprint"),
        "approved_batch_id": proposal.get("recommended_batch_id", "batch_ai_ops_agency_governance_layer"),
        "execution_mode": "owner_operated_handoff",
        "max_external_messages": min(int(budget.get("max_external_messages", len(target_ids) or 3)), 3),
        "max_targets": min(int(budget.get("max_targets", len(target_ids) or 3)), 3),
        "approved_target_ids": target_ids[:3],
        "approved_channels": proposal.get("approved_channels", ["owner_selected_email_or_public_general_channel_after_owner_review"]),
        "approved_draft_id": draft_id,
        "approved_draft_hash": draft_hash,
        "stop_conditions": budget.get("stop_conditions", []),
        "ai_disclosure_required": True,
        "opt_out_required": True,
        "no_scraped_leads": True,
        "no_bulk_outreach": True,
        "publication_authorized": False,
        "payment_authorized": False,
        "form_submission_authorized": False,
        "account_creation_authorized": False,
        "core_writeback_authorized": False,
        "owner_decision_options": ["owner_approved", "rejected", "needs_edit", "hold"],
        "owner_instructions": "Set approval_state to owner_approved and replace OWNER_TO_FILL fields only if this exact batch/channel/draft/target scope is approved.",
    }


def write_e12_approval_request(repo_root: Path) -> Path:
    path = repo_root / E12_APPROVAL_REQUEST_PATH
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(build_e12_approval_request(repo_root), indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    return path


def validate_e12_approval(approval: Dict[str, Any]) -> List[str]:
    errors: List[str] = []
    if not approval:
        return ["missing_e12_owner_approval"]
    if approval.get("proposal_only") is True or approval.get("this_is_not_approval") is True:
        errors.append("approval_request_or_proposal_is_not_approval")
    if approval.get("approval_state") != "owner_approved":
        errors.append("approval_state_must_be_owner_approved")
    for key in ["approval_id", "approved_by", "approved_at", "approved_batch_id", "execution_mode", "approved_draft_id", "approved_draft_hash"]:
        if _has_placeholder(approval.get(key)):
            errors.append(f"{key}_missing_or_placeholder")
    if approval.get("execution_mode") not in E12_ALLOWED_EXECUTION_MODES:
        errors.append("invalid_execution_mode")
    target_ids = approval.get("approved_target_ids") or []
    if not target_ids:
        errors.append("approved_target_ids_required")
    if len(target_ids) > 3:
        errors.append("e12_max_three_targets")
    if int(approval.get("max_external_messages") or 0) <= 0 or int(approval.get("max_external_messages") or 0) > 3:
        errors.append("max_external_messages_must_be_1_to_3")
    if not approval.get("approved_channels"):
        errors.append("approved_channels_required")
    if not approval.get("stop_conditions"):
        errors.append("stop_conditions_required")
    if approval.get("ai_disclosure_required") is not True:
        errors.append("ai_disclosure_required")
    if approval.get("opt_out_required") is not True:
        errors.append("opt_out_required")
    if approval.get("no_scraped_leads") is not True:
        errors.append("no_scraped_leads_required")
    for flag in E12_FORBIDDEN_TRUE_FLAGS:
        if approval.get(flag) is True:
            errors.append(f"{flag}_blocked_in_e12")
    return list(dict.fromkeys(errors))


def load_e12_approval_status(repo_root: Path) -> E12ApprovalStatus:
    approval_path = repo_root / E12_APPROVAL_PATH
    request_path = write_e12_approval_request(repo_root)
    approval = _load_json(approval_path)
    errors = validate_e12_approval(approval)
    return E12ApprovalStatus(
        approval_present=approval_path.exists(),
        approval_valid=not errors,
        approval_path=str(E12_APPROVAL_PATH),
        request_path=str(E12_APPROVAL_REQUEST_PATH),
        approval_state=str(approval.get("approval_state", "missing")),
        approved_batch_id=str(approval.get("approved_batch_id", "")),
        approved_target_ids=list(approval.get("approved_target_ids", []) or []),
        approved_draft_id=str(approval.get("approved_draft_id", "")),
        approved_draft_hash=str(approval.get("approved_draft_hash", "")),
        execution_mode=str(approval.get("execution_mode", "")),
        max_external_messages=int(approval.get("max_external_messages") or 0),
        errors=errors,
    )


def render_e12_approval_status(status: E12ApprovalStatus) -> str:
    lines = [
        "# E12 Approval Status",
        "",
        f"- approval_present: {str(status.approval_present).lower()}",
        f"- approval_valid: {str(status.approval_valid).lower()}",
        f"- approval_state: {status.approval_state}",
        f"- approval_path: {status.approval_path}",
        f"- approval_request_path: {status.request_path}",
        f"- approved_batch_id: {status.approved_batch_id or 'none'}",
        f"- approved_target_ids: {', '.join(status.approved_target_ids) or 'none'}",
        f"- approved_draft_id: {status.approved_draft_id or 'none'}",
        f"- approved_draft_hash: {status.approved_draft_hash or 'none'}",
        f"- execution_mode: {status.execution_mode or 'none'}",
        f"- max_external_messages: {status.max_external_messages}",
        "",
        "## Errors",
    ]
    lines.extend(f"- {error}" for error in status.errors or ["none"])
    lines.extend(
        [
            "",
            "## E12 Rule",
            "- E10 proposed files are not approval.",
            "- E12 requires explicit owner approval before contact, sending, provider execution, or owner-operated validation handoff is considered active.",
        ]
    )
    return "\n".join(lines)
