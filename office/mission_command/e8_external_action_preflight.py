from __future__ import annotations

from dataclasses import asdict, dataclass, field
from typing import Any, Dict, List

from .e8_ai_transparency_policy import validate_ai_disclosure
from .e8_autonomy_budget import autonomy_budget_from_dict, validate_e8_autonomy_budget
from .e8_draft_freeze import verify_draft_hash
from .e8_risk_controlled_action_model import (
    ActionType,
    RiskTier,
    action_type_is_allowed_in_e8,
    classify_external_action,
)
from .e8_target_registry import E8ValidationTarget, target_allows_action
from .e8_validation_approval import E8ExternalValidationManifest, manifest_allows_action, validate_e8_external_validation_manifest


@dataclass(frozen=True)
class E8ExternalValidationAction:
    action_id: str
    action_type: str
    risk_tier: str
    target_id: str
    channel: str
    draft_id: str
    draft_hash: str
    manifest_id: str
    expected_external_side_effect: bool
    ai_disclosure_text: str
    stop_conditions: List[str]
    execution_mode: str

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


@dataclass(frozen=True)
class E8PreflightResult:
    action_id: str
    allowed: bool
    review_gated: bool
    blocked: bool
    risk_tier: str
    manifest_status: str
    target_status: str
    draft_status: str
    transparency_status: str
    autonomy_budget_status: str
    governance_status: str
    blocked_reason: str
    exact_unblock_action: List[str] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


def _find_target(targets: List[E8ValidationTarget], target_id: str) -> E8ValidationTarget | None:
    for target in targets:
        if target.target_id == target_id:
            return target
    return None


def _find_draft(drafts: List[Dict[str, Any]], draft_id: str) -> Dict[str, Any] | None:
    for draft in drafts:
        if draft.get("draft_id") == draft_id:
            return draft
    return None


def build_standard_e8_validation_action(
    manifest: E8ExternalValidationManifest | None,
    targets: List[E8ValidationTarget],
    drafts: List[Dict[str, Any]],
) -> E8ExternalValidationAction:
    draft = drafts[0] if drafts else {}
    target = targets[0] if targets else None
    return E8ExternalValidationAction(
        action_id="e8_action_001",
        action_type=ActionType.SEND_VALIDATION_MESSAGE,
        risk_tier=RiskTier.TIER_2_TRANSPARENT_LOW_RISK_EXTERNAL_VALIDATION,
        target_id=target.target_id if target else "missing_target",
        channel=target.channel if target else "missing_channel",
        draft_id=str(draft.get("draft_id", "missing_draft")),
        draft_hash=str(draft.get("content_hash", "")),
        manifest_id=manifest.manifest_id if manifest else "missing_manifest",
        expected_external_side_effect=True,
        ai_disclosure_text="I’m Aiden, an AI-assisted CEO/runtime agent for Y*Bridge Labs.",
        stop_conditions=["opt-out", "budget exhausted", "recipient asks to stop"],
        execution_mode="owner_operated_handoff",
    )


def preflight_e8_external_action(
    action: E8ExternalValidationAction | Dict[str, Any],
    manifest: E8ExternalValidationManifest | None,
    targets: List[E8ValidationTarget],
    drafts: List[Dict[str, Any]],
) -> E8PreflightResult:
    item = action if isinstance(action, E8ExternalValidationAction) else E8ExternalValidationAction(**action)
    tier = item.risk_tier or classify_external_action(item.action_type)
    errors: List[str] = []
    manifest_errors = validate_e8_external_validation_manifest(manifest)
    target = _find_target(targets, item.target_id)
    draft = _find_draft(drafts, item.draft_id)
    transparency_errors = validate_ai_disclosure(item.ai_disclosure_text)
    if tier == RiskTier.TIER_4_COMMERCIAL_LEGAL_PRODUCTION_HIGH_RISK or not action_type_is_allowed_in_e8(item.action_type):
        errors.append("tier4_or_forbidden_action")
    if manifest_errors:
        errors.append("manifest_invalid_or_missing")
    if target is None or not target_allows_action(target, item.to_dict()):
        errors.append("target_invalid_or_missing")
    if draft is None or not verify_draft_hash(draft, item.draft_hash):
        errors.append("draft_invalid_or_hash_mismatch")
    if draft and not draft.get("ai_disclosure_present"):
        errors.append("draft_missing_ai_disclosure")
    if transparency_errors:
        errors.extend(transparency_errors)
    if not item.stop_conditions:
        errors.append("missing_stop_conditions")
    if manifest and validate_e8_autonomy_budget(autonomy_budget_from_dict(manifest.autonomy_budget), requested_tier=tier):
        errors.append("autonomy_budget_invalid")
    if manifest and not manifest_allows_action(manifest, item.to_dict()):
        errors.append("manifest_does_not_allow_action")
    if item.action_type in {ActionType.PUBLISH_POST, ActionType.PUBLISH_LANDING_PAGE} and tier != RiskTier.TIER_3_PUBLIC_BROADCAST_OR_LANDING:
        errors.append("publication_requires_tier3")

    allowed = not errors
    blocked_reason = ", ".join(list(dict.fromkeys(errors)))
    return E8PreflightResult(
        action_id=item.action_id,
        allowed=allowed,
        review_gated=bool(errors and "manifest_invalid_or_missing" not in errors),
        blocked=bool(errors),
        risk_tier=tier,
        manifest_status="valid" if not manifest_errors else "invalid_or_missing",
        target_status="valid" if target and target_allows_action(target, item.to_dict()) else "invalid_or_missing",
        draft_status="valid" if draft and verify_draft_hash(draft, item.draft_hash) else "invalid_or_missing",
        transparency_status="valid" if not transparency_errors else "invalid",
        autonomy_budget_status="valid" if manifest and not validate_e8_autonomy_budget(autonomy_budget_from_dict(manifest.autonomy_budget), requested_tier=tier) else "invalid_or_missing",
        governance_status="allowed" if allowed else "blocked_or_review_gated",
        blocked_reason=blocked_reason,
        exact_unblock_action=[] if allowed else ["Provide a valid manifest, target seed, frozen draft hash, AI disclosure, and stop conditions before any E8 external action."],
    )


def render_e8_external_action_preflight(action: E8ExternalValidationAction, result: E8PreflightResult) -> str:
    lines = [
        "# E8 External Action Preflight",
        "",
        f"- action_id: {action.action_id}",
        f"- action_type: {action.action_type}",
        f"- risk_tier: {result.risk_tier}",
        f"- allowed: {result.allowed}",
        f"- review_gated: {result.review_gated}",
        f"- blocked: {result.blocked}",
        f"- manifest_status: {result.manifest_status}",
        f"- target_status: {result.target_status}",
        f"- draft_status: {result.draft_status}",
        f"- transparency_status: {result.transparency_status}",
        f"- autonomy_budget_status: {result.autonomy_budget_status}",
        f"- governance_status: {result.governance_status}",
        f"- blocked_reason: {result.blocked_reason or 'none'}",
        "",
        "## Exact Unblock Action",
    ]
    if result.exact_unblock_action:
        lines.extend(f"- {item}" for item in result.exact_unblock_action)
    else:
        lines.append("- none")
    return "\n".join(lines)
