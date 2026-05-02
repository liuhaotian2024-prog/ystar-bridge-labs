from __future__ import annotations

from dataclasses import asdict, dataclass
from enum import Enum
from typing import Any, Dict


class ClosureStatusFamily(str, Enum):
    DISCOVERY_COMPLETE = "discovery_complete"
    VALIDATION_COMPLETE = "validation_complete"
    PAID_SIGNAL_COMPLETE = "paid_signal_complete"
    REVENUE_LOOP_COMPLETE = "revenue_loop_complete"
    REPOSITORY_DELIVERY_COMPLETE = "repository_delivery_complete"
    BLOCKED = "blocked"
    RESIDUAL = "residual"


@dataclass(frozen=True)
class ClosureStatusDecision:
    requested_status: ClosureStatusFamily
    allowed: bool
    blocked_reason: str
    required_evidence: str
    status_boundary: str

    def to_dict(self) -> Dict[str, Any]:
        data = asdict(self)
        data["requested_status"] = self.requested_status.value
        return data


def route_closure_status(
    requested_status: ClosureStatusFamily | str,
    *,
    has_target_candidates: bool = False,
    has_action_ledger: bool = False,
    has_feedback_events: bool = False,
    has_paid_signal: bool = False,
    has_payment_authorization: bool = False,
    repository_committed: bool = False,
    blocked_reason: str = "",
) -> ClosureStatusDecision:
    status = ClosureStatusFamily(requested_status)
    if status == ClosureStatusFamily.DISCOVERY_COMPLETE:
        allowed = has_target_candidates
        return ClosureStatusDecision(status, allowed, "" if allowed else "discovery_complete_requires_target_candidates", "target_candidate_registry", "discovery_is_not_validation")
    if status == ClosureStatusFamily.VALIDATION_COMPLETE:
        allowed = has_action_ledger or has_feedback_events
        return ClosureStatusDecision(status, allowed, "" if allowed else "validation_complete_requires_action_ledger_or_feedback_events", "action_ledger_or_owner_entered_feedback", "validation_is_not_paid_signal")
    if status == ClosureStatusFamily.PAID_SIGNAL_COMPLETE:
        allowed = has_paid_signal
        return ClosureStatusDecision(status, allowed, "" if allowed else "paid_signal_complete_requires_paid_signal", "paid_signal", "paid_signal_is_not_payment_authorization")
    if status == ClosureStatusFamily.REVENUE_LOOP_COMPLETE:
        allowed = has_paid_signal and has_payment_authorization
        return ClosureStatusDecision(status, allowed, "" if allowed else "revenue_loop_requires_paid_signal_and_payment_authorization", "paid_signal_plus_payment_authorization", "revenue_loop_is_separate_from_validation")
    if status == ClosureStatusFamily.REPOSITORY_DELIVERY_COMPLETE:
        allowed = repository_committed
        return ClosureStatusDecision(status, allowed, "" if allowed else "repository_delivery_requires_commit_or_patch_bundle", "commit_hash_or_patch_bundle", "repository_delivery_is_not_capability_completion")
    if status == ClosureStatusFamily.BLOCKED:
        allowed = bool(blocked_reason)
        return ClosureStatusDecision(status, allowed, "" if allowed else "blocked_status_requires_blocked_reason", "blocked_reason_and_exact_unblock_action", "blocked_full_rt1_must_be_nonzero")
    return ClosureStatusDecision(status, False, "residual_requires_owner_review", "owner_review", "residual_is_not_complete")


def validation_complete_requires_ledger_or_feedback() -> bool:
    return not route_closure_status(ClosureStatusFamily.VALIDATION_COMPLETE).allowed

