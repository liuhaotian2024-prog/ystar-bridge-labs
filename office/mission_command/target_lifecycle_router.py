from __future__ import annotations

from dataclasses import asdict, dataclass
from enum import Enum
from typing import Any, Dict


class TargetLifecycleState(str, Enum):
    DISCOVERED_CANDIDATE = "discovered_candidate"
    PROPOSED_TARGET_SEED = "proposed_target_seed"
    OWNER_APPROVED_TARGET = "owner_approved_target"
    PREFLIGHTED_ACTION_TARGET = "preflighted_action_target"
    EXECUTED_ACTION_TARGET = "executed_action_target"
    FEEDBACK_SOURCE = "feedback_source"
    SUPPRESSED_TARGET = "suppressed_target"


@dataclass(frozen=True)
class TargetLifecycleDecision:
    target_id: str
    state: TargetLifecycleState
    contact_allowed: bool
    preflight_allowed: bool
    execution_allowed: bool
    feedback_allowed: bool
    blocked_reason: str
    exact_next_state: str

    def to_dict(self) -> Dict[str, Any]:
        data = asdict(self)
        data["state"] = self.state.value
        return data


def classify_target_lifecycle(target: Dict[str, Any]) -> TargetLifecycleState:
    if target.get("opt_out_state") in {"opted_out", "stop_requested"} or target.get("suppressed"):
        return TargetLifecycleState.SUPPRESSED_TARGET
    if target.get("feedback_event_exists") or target.get("feedback_source"):
        return TargetLifecycleState.FEEDBACK_SOURCE
    if target.get("contact_executed") or target.get("action_ledger_reference"):
        return TargetLifecycleState.EXECUTED_ACTION_TARGET
    if target.get("preflight_allowed") or target.get("preflighted"):
        return TargetLifecycleState.PREFLIGHTED_ACTION_TARGET
    if target.get("owner_approved_for_contact") is True and not target.get("proposal_only"):
        return TargetLifecycleState.OWNER_APPROVED_TARGET
    if target.get("proposal_only") or target.get("target_seed_proposal") or target.get("proposed"):
        return TargetLifecycleState.PROPOSED_TARGET_SEED
    return TargetLifecycleState.DISCOVERED_CANDIDATE


def route_target_lifecycle(target: Dict[str, Any], requested_action: str = "contact") -> TargetLifecycleDecision:
    state = classify_target_lifecycle(target)
    target_id = str(target.get("target_id") or target.get("candidate_id") or "unknown_target")
    if state == TargetLifecycleState.SUPPRESSED_TARGET:
        return TargetLifecycleDecision(target_id, state, False, False, False, False, "target_suppressed_or_opted_out", "do_not_contact")
    if state == TargetLifecycleState.DISCOVERED_CANDIDATE:
        return TargetLifecycleDecision(target_id, state, False, False, False, False, "discovered_candidate_is_not_contact_approval", "owner_review_target_seed")
    if state == TargetLifecycleState.PROPOSED_TARGET_SEED:
        return TargetLifecycleDecision(target_id, state, False, False, False, False, "proposed_target_seed_is_not_approval", "owner_materialize_approved_target_seed")
    if state == TargetLifecycleState.OWNER_APPROVED_TARGET:
        return TargetLifecycleDecision(target_id, state, False, True, False, False, "", "run_governance_preflight")
    if state == TargetLifecycleState.PREFLIGHTED_ACTION_TARGET:
        allowed = requested_action == "execute" and bool(target.get("preflight_allowed"))
        return TargetLifecycleDecision(target_id, state, allowed, True, allowed, False, "" if allowed else "execution_requires_allowed_preflight", "execution_gate")
    if state == TargetLifecycleState.EXECUTED_ACTION_TARGET:
        return TargetLifecycleDecision(target_id, state, False, False, False, True, "", "await_or_record_feedback_event")
    return TargetLifecycleDecision(target_id, state, False, False, False, True, "", "evaluate_feedback_signal")


def target_contact_is_blocked(target: Dict[str, Any]) -> bool:
    return not route_target_lifecycle(target, requested_action="contact").contact_allowed

