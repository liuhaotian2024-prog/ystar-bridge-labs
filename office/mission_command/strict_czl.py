from __future__ import annotations

from dataclasses import asdict, dataclass, field
from typing import Any, Dict, List


@dataclass(frozen=True)
class StrictCZLState:
    mission_id: str
    y_star: List[str]
    xt: Dict[str, Any]
    u: List[str]
    y_t1: Dict[str, Any]
    feasible_internal_residuals: List[str] = field(default_factory=list)
    full_mission_residuals: List[str] = field(default_factory=list)
    feasible_internal_rt1_score: int = 0
    full_mission_rt1_score: int = 0
    status: str = "planned"
    blocked_reason: str = ""
    exact_unblock_action: List[str] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


def _missing(criteria: List[str], observed: Dict[str, Any]) -> List[str]:
    return [criterion for criterion in criteria if not observed.get(criterion)]


def compute_feasible_internal_rt1(
    y_t1: Dict[str, Any],
    feasible_criteria: List[str],
) -> Dict[str, Any]:
    residuals = _missing(feasible_criteria, y_t1)
    return {
        "residuals": residuals,
        "score": len(residuals),
        "complete": len(residuals) == 0,
    }


def compute_full_mission_rt1(
    y_t1: Dict[str, Any],
    full_criteria: List[str],
    blocked_reason: str = "",
) -> Dict[str, Any]:
    residuals = _missing(full_criteria, y_t1)
    if blocked_reason and "live_external_evidence_available" in full_criteria and not y_t1.get("live_external_evidence_available"):
        residuals.append(f"blocked: {blocked_reason}")
    residuals = list(dict.fromkeys(residuals))
    return {
        "residuals": residuals,
        "score": len(residuals),
        "complete": len(residuals) == 0,
    }


def build_strict_czl_state(
    mission_id: str,
    y_star: List[str],
    xt: Dict[str, Any],
    u: List[str],
    y_t1: Dict[str, Any],
    feasible_criteria: List[str],
    full_criteria: List[str],
    blocked_reason: str = "",
    exact_unblock_action: List[str] | None = None,
) -> StrictCZLState:
    feasible = compute_feasible_internal_rt1(y_t1, feasible_criteria)
    full = compute_full_mission_rt1(y_t1, full_criteria, blocked_reason)
    if full["complete"]:
        status = "complete"
    elif blocked_reason:
        status = "BLOCKED_BY_MISSING_LIVE_RESEARCH_CONFIG"
    else:
        status = "residual"
    return StrictCZLState(
        mission_id=mission_id,
        y_star=y_star,
        xt=xt,
        u=u,
        y_t1=y_t1,
        feasible_internal_residuals=list(feasible["residuals"]),
        full_mission_residuals=list(full["residuals"]),
        feasible_internal_rt1_score=int(feasible["score"]),
        full_mission_rt1_score=int(full["score"]),
        status=status,
        blocked_reason=blocked_reason,
        exact_unblock_action=exact_unblock_action or [],
    )


def strict_czl_is_complete(state: StrictCZLState) -> bool:
    return state.status == "complete" and state.full_mission_rt1_score == 0 and not state.full_mission_residuals


def strict_czl_is_blocked(state: StrictCZLState) -> bool:
    return state.status.startswith("BLOCKED") and state.full_mission_rt1_score > 0


def render_strict_czl_report(state: StrictCZLState) -> str:
    lines = [
        "# Strict CZL Report",
        "",
        f"- mission_id: {state.mission_id}",
        f"- status: {state.status}",
        f"- feasible_internal_rt1: {state.feasible_internal_rt1_score}",
        f"- full_mission_rt1: {state.full_mission_rt1_score}",
        f"- blocked_reason: {state.blocked_reason or 'none'}",
        "",
        "## Y*",
    ]
    lines.extend(f"- {item}" for item in state.y_star)
    lines.extend(["", "## Xt"])
    lines.extend(f"- {key}: {value}" for key, value in state.xt.items())
    lines.extend(["", "## U"])
    lines.extend(f"- {item}" for item in state.u)
    lines.extend(["", "## Yt+1"])
    lines.extend(f"- {key}: {value}" for key, value in state.y_t1.items())
    lines.extend(["", "## Feasible Internal Rt+1"])
    if state.feasible_internal_residuals:
        lines.extend(f"- {item}" for item in state.feasible_internal_residuals)
    else:
        lines.append("- feasible_internal_rt1 = 0")
    lines.extend(["", "## Full Mission Rt+1"])
    if state.full_mission_residuals:
        lines.extend(f"- {item}" for item in state.full_mission_residuals)
    else:
        lines.append("- full_mission_rt1 = 0")
    if state.exact_unblock_action:
        lines.extend(["", "## Exact Unblock Action"])
        lines.extend(f"- {item}" for item in state.exact_unblock_action)
    return "\n".join(lines)
