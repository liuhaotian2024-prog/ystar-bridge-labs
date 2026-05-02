from __future__ import annotations

from dataclasses import asdict, dataclass, field
from typing import Any, Dict, List

from .e8_risk_controlled_action_model import ActionType, RiskTier
from .e9_draft_binding import E9DraftBinding
from .e9_scope_minimization import E9ActionScope, build_standard_e9_action_scope


@dataclass(frozen=True)
class E9ValidationActionPlan:
    plan_id: str
    top_offer: str
    planned_action_type: str
    risk_tier: str
    execution_mode: str
    target_ids: List[str]
    channel: str
    draft_id: str
    draft_hash: str
    max_count: int
    stop_conditions: List[str]
    scope: E9ActionScope
    plan_status: str
    blocker_reasons: List[str] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        item = asdict(self)
        item["scope"] = self.scope.to_dict()
        return item


def build_e9_validation_action_plan(manifest: Any | None, targets: List[Any], bindings: List[E9DraftBinding]) -> E9ValidationActionPlan:
    binding = bindings[0] if bindings else E9DraftBinding("", "", "", "", False, False, False, ["missing_draft_binding"])
    target_ids = [target.target_id for target in targets]
    blockers: List[str] = []
    if manifest is None:
        blockers.append("missing_manifest")
    if not targets:
        blockers.append("missing_targets")
    if not binding.draft_hash:
        blockers.append("missing_draft_hash")
    channel = getattr(manifest, "approved_channels", ["owner_selected_email"])[0] if manifest and getattr(manifest, "approved_channels", []) else "owner_selected_email"
    return E9ValidationActionPlan(
        plan_id="e9_validation_action_plan_001",
        top_offer=getattr(manifest, "top_offer", "48h AI Ops Operating Room Blueprint") if manifest else "48h AI Ops Operating Room Blueprint",
        planned_action_type=ActionType.SEND_VALIDATION_MESSAGE,
        risk_tier=RiskTier.TIER_2_TRANSPARENT_LOW_RISK_EXTERNAL_VALIDATION,
        execution_mode=getattr(manifest, "progressive_autonomy_level", "L2_owner_operated_handoff") if manifest else "L2_owner_operated_handoff",
        target_ids=target_ids or ["owner_to_provide_targets"],
        channel=channel,
        draft_id=binding.draft_id or "e8_ai_disclosed_outreach_draft",
        draft_hash=binding.draft_hash,
        max_count=min(3, len(targets)) if targets else 0,
        stop_conditions=["opt-out", "recipient asks to stop", "budget exhausted", "scope mismatch", "owner revokes approval"],
        scope=build_standard_e9_action_scope("e9_action_001"),
        plan_status="ready" if not blockers else "blocked_missing_inputs",
        blocker_reasons=blockers,
    )


def action_plan_respects_budget(plan: E9ValidationActionPlan, max_count: int) -> bool:
    return plan.max_count <= max_count and "budget exhausted" in plan.stop_conditions


def render_e9_validation_action_plan(plan: E9ValidationActionPlan) -> str:
    lines = ["# E9 Validation Action Plan", ""]
    for key, value in plan.to_dict().items():
        lines.append(f"- {key}: {value}")
    return "\n".join(lines)
