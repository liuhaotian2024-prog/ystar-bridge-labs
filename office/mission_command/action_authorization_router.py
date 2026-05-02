from __future__ import annotations

from dataclasses import asdict, dataclass
from enum import Enum
from typing import Any, Dict


class AuthorizationStatus(str, Enum):
    ALLOWED = "allowed"
    REVIEW_GATED = "review_gated"
    BLOCKED = "blocked"


@dataclass(frozen=True)
class ActionAuthorizationRequest:
    action_id: str
    action_type: str
    risk_tier: str
    target_lifecycle_state: str
    owner_approval_present: bool
    manifest_valid: bool
    channel_approved: bool
    draft_hash_valid: bool
    y_star_gov_decision: str
    gov_mcp_gateway_available: bool
    gov_mcp_preflight_passed: bool
    execution_provider_available: bool
    no_forbidden_side_effects: bool

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


@dataclass(frozen=True)
class ActionAuthorizationDecision:
    action_id: str
    status: AuthorizationStatus
    allowed: bool
    blocked_reason: str
    y_star_gov_reference_required: bool
    gov_mcp_gateway_reference_required: bool
    exact_unblock_action: str

    def to_dict(self) -> Dict[str, Any]:
        data = asdict(self)
        data["status"] = self.status.value
        return data


def authorize_external_action(request: ActionAuthorizationRequest) -> ActionAuthorizationDecision:
    required = {
        "owner_approval_present": request.owner_approval_present,
        "manifest_valid": request.manifest_valid,
        "channel_approved": request.channel_approved,
        "draft_hash_valid": request.draft_hash_valid,
        "gov_mcp_gateway_available": request.gov_mcp_gateway_available,
        "gov_mcp_preflight_passed": request.gov_mcp_preflight_passed,
        "execution_provider_available": request.execution_provider_available,
        "no_forbidden_side_effects": request.no_forbidden_side_effects,
    }
    if request.risk_tier not in {"Tier 2", "TIER_2_TRANSPARENT_LOW_RISK_EXTERNAL_VALIDATION"}:
        return ActionAuthorizationDecision(request.action_id, AuthorizationStatus.BLOCKED, False, "E11_allows_only_tier2_transparent_validation", True, True, "reduce_action_to_approved_Tier_2_validation")
    if request.target_lifecycle_state != "preflighted_action_target":
        return ActionAuthorizationDecision(request.action_id, AuthorizationStatus.BLOCKED, False, "target_must_pass_canonical_lifecycle_preflight", True, True, "route_target_through_target_lifecycle_router")
    if request.y_star_gov_decision not in {"owner_approval_required_and_present", "allowed_with_owner_approval"}:
        return ActionAuthorizationDecision(request.action_id, AuthorizationStatus.BLOCKED, False, "Y_star_gov_permission_decision_not_satisfied", True, True, "obtain_or_reference_Y_star_gov_owner_approval_decision")
    missing = [name for name, ok in required.items() if not ok]
    if missing:
        return ActionAuthorizationDecision(request.action_id, AuthorizationStatus.BLOCKED, False, "missing_" + "_and_".join(missing), True, True, "satisfy_full_authorization_chain_before_execution")
    return ActionAuthorizationDecision(request.action_id, AuthorizationStatus.ALLOWED, True, "", True, True, "write_action_ledger_and_execute_with_provider")


def action_authorization_blocks_without_governance(request: ActionAuthorizationRequest) -> bool:
    return not authorize_external_action(request).allowed

