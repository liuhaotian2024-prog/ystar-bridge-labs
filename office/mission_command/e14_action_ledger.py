from __future__ import annotations

import json
from dataclasses import asdict, dataclass, field
from pathlib import Path
from typing import Any, Dict, List


@dataclass(frozen=True)
class E14ActionLedgerTemplate:
    action_id: str
    approval_id: str
    target_id: str
    owner_executor: str
    executed_by: str
    execution_time: str
    channel: str
    message_hash: str
    draft_version: str
    external_action_type: str
    result_status: str
    no_response_allowed_after_date: str
    notes: str
    evidence_refs: List[str] = field(default_factory=list)
    safety_receipt: Dict[str, bool] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


def build_e14_action_ledger_template() -> Dict[str, Any]:
    template = E14ActionLedgerTemplate(
        action_id="OWNER_TO_FILL_AFTER_MANUAL_EXECUTION",
        approval_id="OWNER_APPROVAL_ID_REQUIRED",
        target_id="OWNER_APPROVED_TARGET_ID_REQUIRED",
        owner_executor="OWNER_TO_FILL",
        executed_by="owner_manual_execution_only",
        execution_time="OWNER_TO_FILL_ISO8601",
        channel="OWNER_APPROVED_CHANNEL_REQUIRED",
        message_hash="APPROVED_DRAFT_HASH_REQUIRED",
        draft_version="e14_manual_owner_operated_ai_agent_readiness_review_v1",
        external_action_type="owner_operated_manual_validation",
        result_status="sent|not_sent|blocked|owner_cancelled",
        no_response_allowed_after_date="OWNER_TO_FILL_ONLY_AFTER_VALID_SEND",
        notes="Do not create an executed ledger entry unless owner actually sends or explicitly records the manual action.",
        evidence_refs=[],
        safety_receipt={
            "customer_contact_by_aiden": False,
            "email_or_message_sent_by_aiden": False,
            "publication": False,
            "payment": False,
            "account_creation": False,
            "form_submission": False,
            "login": False,
            "core_brain_cieu_memory_writeback": False,
        },
    )
    return {"ledger_events": [], "template": template.to_dict(), "executed_action_exists": False}


def validate_e14_action_ledger_event(event: Dict[str, Any], owner_executed: bool = False) -> List[str]:
    errors: List[str] = []
    if event.get("result_status") in {"sent", "no_response"} and not owner_executed:
        errors.append("executed_action_requires_owner_execution")
    if not event.get("approval_id") or "OWNER" in str(event.get("approval_id")):
        errors.append("valid_approval_id_required")
    if not event.get("target_id") or "OWNER" in str(event.get("target_id")):
        errors.append("valid_target_id_required")
    if event.get("executed_by") not in {"owner_manual_execution_only", "owner"}:
        errors.append("executed_by_must_be_owner_manual")
    return list(dict.fromkeys(errors))


def write_e14_action_ledger_template(repo_root: Path) -> Path:
    path = repo_root / "operations" / "external_validation" / "e14_action_ledger.template.json"
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(build_e14_action_ledger_template(), indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    return path
