from __future__ import annotations

from dataclasses import asdict, dataclass, field
from typing import Any, Dict, List

from .e8_risk_controlled_action_model import RiskTier


@dataclass(frozen=True)
class E8AutonomyBudget:
    budget_id: str = ""
    max_external_messages: int = 0
    max_public_posts: int = 0
    max_landing_pages: int = 0
    max_followups_per_target: int = 0
    max_targets: int = 0
    allowed_risk_tiers: List[str] = field(default_factory=list)
    allowed_channels: List[str] = field(default_factory=list)
    expires_at: str = ""
    stop_conditions: List[str] = field(default_factory=list)
    require_human_review_before_send: bool = True
    allow_aiden_execution: bool = False
    allow_owner_operated_handoff: bool = True

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


def autonomy_budget_from_dict(data: Dict[str, Any] | None) -> E8AutonomyBudget:
    data = data or {}
    return E8AutonomyBudget(
        budget_id=str(data.get("budget_id", "")),
        max_external_messages=int(data.get("max_external_messages", 0) or 0),
        max_public_posts=int(data.get("max_public_posts", 0) or 0),
        max_landing_pages=int(data.get("max_landing_pages", 0) or 0),
        max_followups_per_target=int(data.get("max_followups_per_target", 0) or 0),
        max_targets=int(data.get("max_targets", 0) or 0),
        allowed_risk_tiers=list(data.get("allowed_risk_tiers", [])),
        allowed_channels=list(data.get("allowed_channels", [])),
        expires_at=str(data.get("expires_at", "")),
        stop_conditions=list(data.get("stop_conditions", [])),
        require_human_review_before_send=bool(data.get("require_human_review_before_send", True)),
        allow_aiden_execution=bool(data.get("allow_aiden_execution", False)),
        allow_owner_operated_handoff=bool(data.get("allow_owner_operated_handoff", True)),
    )


def validate_e8_autonomy_budget(budget: E8AutonomyBudget | Dict[str, Any], requested_tier: str | None = None) -> List[str]:
    item = budget if isinstance(budget, E8AutonomyBudget) else autonomy_budget_from_dict(budget)
    errors: List[str] = []
    if item.max_external_messages <= 0 and item.max_public_posts <= 0 and item.max_landing_pages <= 0:
        errors.append("missing_external_action_count")
    if item.max_targets <= 0:
        errors.append("missing_max_targets")
    if not item.stop_conditions:
        errors.append("missing_stop_conditions")
    if not item.allowed_risk_tiers:
        errors.append("missing_allowed_risk_tiers")
    if requested_tier and requested_tier not in item.allowed_risk_tiers:
        errors.append("risk_tier_not_in_budget")
    if RiskTier.TIER_4_COMMERCIAL_LEGAL_PRODUCTION_HIGH_RISK in item.allowed_risk_tiers:
        errors.append("tier4_not_allowed_in_e8")
    return list(dict.fromkeys(errors))


def render_e8_autonomy_budget_template() -> Dict[str, Any]:
    return E8AutonomyBudget(
        budget_id="e8_standard_3_person_validation",
        max_external_messages=3,
        max_public_posts=0,
        max_landing_pages=0,
        max_followups_per_target=0,
        max_targets=3,
        allowed_risk_tiers=[RiskTier.TIER_2_TRANSPARENT_LOW_RISK_EXTERNAL_VALIDATION],
        allowed_channels=["owner_selected_email", "owner_selected_dm"],
        expires_at="2026-05-08T23:59:59Z",
        stop_conditions=[
            "any target opts out",
            "message count reaches budget",
            "draft hash changes",
            "recipient asks for no further contact",
            "owner pauses validation",
        ],
        require_human_review_before_send=True,
        allow_aiden_execution=False,
        allow_owner_operated_handoff=True,
    ).to_dict()
