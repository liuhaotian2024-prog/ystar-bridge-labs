from __future__ import annotations

from dataclasses import asdict, dataclass, field
from typing import Any, Dict, List

from .e8_ai_transparency_policy import validate_ai_disclosure
from .e8_risk_controlled_action_model import ActionType, RiskTier
from .e9_action_plan import E9ValidationActionPlan
from .e9_draft_binding import E9DraftBinding, validate_e9_draft_binding
from .e9_scope_minimization import validate_e9_action_scope
from .e9_suppression_registry import E9SuppressionRegistry, suppression_blocks_target
from .e9_target_registry import E9ValidationTarget, e9_target_allows_action
from .e9_validation_manifest import E9ExternalValidationManifest, e9_manifest_allows_action, validate_e9_validation_manifest


@dataclass(frozen=True)
class E9PreflightResult:
    allowed: bool
    review_gated: bool
    blocked: bool
    risk_tier: str
    manifest_status: str
    target_status: str
    draft_status: str
    scope_status: str
    suppression_status: str
    transparency_status: str
    blocked_reason: str
    exact_unblock_action: List[str] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


def _target_for_plan(targets: List[E9ValidationTarget], plan: E9ValidationActionPlan) -> E9ValidationTarget | None:
    for target in targets:
        if target.target_id in plan.target_ids:
            return target
    return None


def _binding_for_plan(bindings: List[E9DraftBinding], plan: E9ValidationActionPlan) -> E9DraftBinding | None:
    for binding in bindings:
        if binding.draft_id == plan.draft_id:
            return binding
    return None


def preflight_e9_external_action(
    plan: E9ValidationActionPlan,
    manifest: E9ExternalValidationManifest | None,
    targets: List[E9ValidationTarget],
    bindings: List[E9DraftBinding],
    suppression_registry: E9SuppressionRegistry,
) -> E9PreflightResult:
    errors: List[str] = []
    manifest_errors = validate_e9_validation_manifest(manifest)
    target = _target_for_plan(targets, plan)
    binding = _binding_for_plan(bindings, plan)
    if manifest_errors:
        errors.append("manifest_invalid_or_missing")
    if target is None or not e9_target_allows_action(target, {"target_id": getattr(target, "target_id", ""), "channel": plan.channel}):
        errors.append("target_invalid_or_missing")
    if binding is None or validate_e9_draft_binding(binding):
        errors.append("draft_invalid_or_missing")
    if validate_e9_action_scope(plan.scope):
        errors.append("scope_invalid")
    if target and suppression_blocks_target(suppression_registry, target.target_id):
        errors.append("suppression_blocks_target")
    if validate_ai_disclosure("I am Aiden, an AI-assisted CEO/runtime agent for Y*Bridge Labs. You can ignore this message and no automated follow-up will happen."):
        errors.append("ai_disclosure_invalid")
    if plan.planned_action_type in {ActionType.PUBLISH_POST, ActionType.PUBLISH_LANDING_PAGE}:
        errors.append("tier3_publication_blocked_without_explicit_approval")
    if plan.planned_action_type in {ActionType.COLLECT_PAYMENT, ActionType.CREATE_ACCOUNT, ActionType.SUBMIT_FORM, ActionType.CORE_WRITEBACK}:
        errors.append("tier4_action_blocked")
    action = {
        "action_type": plan.planned_action_type,
        "target_id": target.target_id if target else "",
        "channel": plan.channel,
        "draft_id": plan.draft_id,
        "draft_hash": plan.draft_hash,
    }
    if manifest and not e9_manifest_allows_action(manifest, action):
        errors.append("manifest_does_not_allow_action")
    errors = list(dict.fromkeys(errors))
    allowed = not errors
    return E9PreflightResult(
        allowed=allowed,
        review_gated=bool(errors and "tier4_action_blocked" not in errors),
        blocked=bool(errors),
        risk_tier=RiskTier.TIER_2_TRANSPARENT_LOW_RISK_EXTERNAL_VALIDATION,
        manifest_status="valid" if not manifest_errors else "invalid_or_missing",
        target_status="valid" if target and e9_target_allows_action(target, {"target_id": target.target_id, "channel": plan.channel}) else "invalid_or_missing",
        draft_status="valid" if binding and not validate_e9_draft_binding(binding) else "invalid_or_missing",
        scope_status="valid" if not validate_e9_action_scope(plan.scope) else "invalid",
        suppression_status="clear" if not (target and suppression_blocks_target(suppression_registry, target.target_id)) else "blocked",
        transparency_status="valid",
        blocked_reason=", ".join(errors),
        exact_unblock_action=[] if allowed else ["Provide valid E9 manifest, owner-provided targets, exact draft hash approval, clear suppression state, and safe provider or owner-operated handoff before execution."],
    )


def render_e9_action_preflight(plan: E9ValidationActionPlan, result: E9PreflightResult) -> str:
    lines = ["# E9 Action Preflight", "", f"- plan_id: {plan.plan_id}"]
    for key, value in result.to_dict().items():
        lines.append(f"- {key}: {value}")
    return "\n".join(lines)
