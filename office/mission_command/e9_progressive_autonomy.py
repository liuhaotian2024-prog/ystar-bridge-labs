from __future__ import annotations

from dataclasses import asdict, dataclass
from typing import Any, Dict, List


class E9AutonomyLevel:
    L0_INTERNAL_ONLY = "L0_internal_only"
    L1_READ_ONLY = "L1_read_only"
    L2_OWNER_OPERATED_HANDOFF = "L2_owner_operated_handoff"
    L3_AIDEN_SENDS_WITH_EXACT_APPROVAL_PROVIDER = "L3_aiden_sends_with_exact_approval_provider"
    L4_PUBLIC_BROADCAST_WITH_EXPLICIT_APPROVAL = "L4_public_broadcast_with_explicit_approval"
    L5_COMMERCIAL_PRODUCTION_BLOCKED_IN_E9 = "L5_commercial_production_blocked_in_E9"


ORDERED_LEVELS = [
    E9AutonomyLevel.L0_INTERNAL_ONLY,
    E9AutonomyLevel.L1_READ_ONLY,
    E9AutonomyLevel.L2_OWNER_OPERATED_HANDOFF,
    E9AutonomyLevel.L3_AIDEN_SENDS_WITH_EXACT_APPROVAL_PROVIDER,
    E9AutonomyLevel.L4_PUBLIC_BROADCAST_WITH_EXPLICIT_APPROVAL,
    E9AutonomyLevel.L5_COMMERCIAL_PRODUCTION_BLOCKED_IN_E9,
]


@dataclass(frozen=True)
class E9ProgressiveAutonomyStep:
    level: str
    allowed: bool
    required_controls: List[str]
    description: str

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


def build_e9_progressive_autonomy_ladder() -> List[E9ProgressiveAutonomyStep]:
    return [
        E9ProgressiveAutonomyStep(E9AutonomyLevel.L0_INTERNAL_ONLY, True, ["no_external_side_effect"], "Prepare, analyze, draft."),
        E9ProgressiveAutonomyStep(E9AutonomyLevel.L1_READ_ONLY, True, ["public_read_only_budget"], "Read public no-login sources."),
        E9ProgressiveAutonomyStep(E9AutonomyLevel.L2_OWNER_OPERATED_HANDOFF, True, ["manifest", "targets", "draft_hash"], "Owner sends manually from handoff packet."),
        E9ProgressiveAutonomyStep(E9AutonomyLevel.L3_AIDEN_SENDS_WITH_EXACT_APPROVAL_PROVIDER, True, ["valid_manifest", "approved_targets", "safe_provider", "action_ledger"], "Aiden may send only within exact approved scope."),
        E9ProgressiveAutonomyStep(E9AutonomyLevel.L4_PUBLIC_BROADCAST_WITH_EXPLICIT_APPROVAL, True, ["tier3_publication_approval", "draft_hash", "ledger"], "Publish only with explicit Tier 3 approval."),
        E9ProgressiveAutonomyStep(E9AutonomyLevel.L5_COMMERCIAL_PRODUCTION_BLOCKED_IN_E9, False, ["separate_future_approval"], "Payment, contracts, account creation, production changes are blocked in E9."),
    ]


def autonomy_level_index(level: str) -> int:
    return ORDERED_LEVELS.index(level)


def autonomy_level_allowed_in_e9(level: str) -> bool:
    return level != E9AutonomyLevel.L5_COMMERCIAL_PRODUCTION_BLOCKED_IN_E9


def render_e9_progressive_autonomy_ladder(steps: List[E9ProgressiveAutonomyStep]) -> str:
    lines = ["# E9 Progressive Autonomy Ladder", ""]
    for step in steps:
        lines.extend(
            [
                f"## {step.level}",
                f"- allowed_in_E9: {step.allowed}",
                f"- required_controls: {', '.join(step.required_controls)}",
                f"- description: {step.description}",
                "",
            ]
        )
    return "\n".join(lines).rstrip()
