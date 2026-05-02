from __future__ import annotations

from dataclasses import asdict, dataclass
from typing import Any, Dict, List


class E9ApprovalDecisionType:
    APPROVE = "approve"
    EDIT = "edit"
    REJECT = "reject"
    HOLD = "hold"
    ESCALATE = "escalate"


VALID_DECISIONS = {
    E9ApprovalDecisionType.APPROVE,
    E9ApprovalDecisionType.EDIT,
    E9ApprovalDecisionType.REJECT,
    E9ApprovalDecisionType.HOLD,
    E9ApprovalDecisionType.ESCALATE,
}


@dataclass(frozen=True)
class E9ApprovalDecision:
    decision_id: str
    action_id: str
    decision: str
    reviewer: str
    edited_draft_id: str = ""
    edited_target_id: str = ""
    edited_channel: str = ""
    edited_count: int = 0
    reason: str = ""
    escalate_to: str = ""

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


def validate_e9_approval_decision(decision: E9ApprovalDecision | Dict[str, Any]) -> List[str]:
    item = decision if isinstance(decision, E9ApprovalDecision) else E9ApprovalDecision(**decision)
    errors: List[str] = []
    if item.decision not in VALID_DECISIONS:
        errors.append("invalid_decision")
    if not item.action_id:
        errors.append("missing_action_id")
    if item.decision in {E9ApprovalDecisionType.REJECT, E9ApprovalDecisionType.HOLD} and not item.reason:
        errors.append("missing_reason")
    if item.decision == E9ApprovalDecisionType.EDIT and not any([item.edited_draft_id, item.edited_target_id, item.edited_channel, item.edited_count]):
        errors.append("edit_requires_changed_field")
    if item.decision == E9ApprovalDecisionType.ESCALATE and not item.escalate_to:
        errors.append("missing_escalation_target")
    return errors


def render_e9_approval_decision_model() -> str:
    return "\n".join(
        [
            "# E9 Approval Decision Model",
            "",
            "- supported_decisions: approve, edit, reject, hold, escalate",
            "- approve: run exactly as scoped only if preflight passes",
            "- edit: change draft, target, channel, or count before rerunning preflight",
            "- reject: do not execute; record reason and learning",
            "- hold: wait for more evidence, targets, or owner review",
            "- escalate: send to owner or governance reviewer for higher-risk decision",
        ]
    )
