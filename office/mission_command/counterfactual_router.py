from __future__ import annotations

from dataclasses import asdict, dataclass
from enum import Enum
from pathlib import Path
from typing import Any, Dict


class CounterfactualRoute(str, Enum):
    OPPORTUNITY = "opportunity_counterfactual"
    MARKET = "market_counterfactual"
    EXECUTION = "execution_counterfactual"
    REVENUE = "revenue_counterfactual"
    GOVERNANCE = "governance_counterfactual"
    BRAIN_LEARNING = "brain_learning_counterfactual"


@dataclass(frozen=True)
class CounterfactualRoutingDecision:
    route: CounterfactualRoute
    method_kernel_source: str
    required_fields: list[str]
    allowed: bool
    blocked_reason: str

    def to_dict(self) -> Dict[str, Any]:
        data = asdict(self)
        data["route"] = self.route.value
        return data


def method_kernel_has_counterfactual_protocol(repo_root: Path) -> bool:
    path = repo_root / "knowledge" / "ceo" / "wisdom" / "AIDEN_META_DEVELOPMENT_METHOD_KERNEL.md"
    if not path.exists():
        return False
    text = path.read_text(encoding="utf-8")
    return "Counterfactual" in text or "counterfactual" in text or "disconfirm" in text


def route_counterfactual(repo_root: Path, route: CounterfactualRoute | str) -> CounterfactualRoutingDecision:
    counterfactual_route = CounterfactualRoute(route)
    has_protocol = method_kernel_has_counterfactual_protocol(repo_root)
    return CounterfactualRoutingDecision(
        route=counterfactual_route,
        method_kernel_source="knowledge/ceo/wisdom/AIDEN_META_DEVELOPMENT_METHOD_KERNEL.md",
        required_fields=["claim", "what_would_invalidate", "disconfirming_signal", "kill_or_revision_condition"],
        allowed=has_protocol,
        blocked_reason="" if has_protocol else "method_kernel_counterfactual_protocol_missing",
    )

