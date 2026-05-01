from __future__ import annotations

from dataclasses import asdict, dataclass, replace
from pathlib import Path
from typing import Any, Dict, List

from .mission_model import MissionCommandResult


E1_5_Y_STAR = [
    "Aiden Mission Command explicitly defines Y*, Xt, U, Yt+1, and Rt+1 for a mission.",
    "Counterfactual reasoning is a decision gate, not just a report section.",
    "Counterfactual gate can confirm or change the default recommendation.",
    "All proposed mission actions are inventoried and passed through governance preflight.",
    "Obligation drafts use dynamic, collision-safe identifiers and remain dry-run only.",
    "Residual candidates can be updated with actual signal placeholders and remain review-gated.",
    "A clear owner decision packet is generated.",
    "Mission output distinguishes plan, executable U, observed Yt+1, and remaining Rt+1.",
    "No external side effects occur.",
    "Tests and unseen smoke checks verify behavior.",
]


@dataclass(frozen=True)
class CZLState:
    mission_id: str
    y_star: List[str]
    xt_snapshot: Dict[str, Any]
    u_actions: List[Dict[str, Any]]
    y_t1_observed: Dict[str, Any]
    rt1_residuals: List[str]
    rt1_score: int
    status: str

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


def build_czl_plan(mission_result: MissionCommandResult, repo_root: Path) -> CZLState:
    return CZLState(
        mission_id=mission_result.mission.mission_id,
        y_star=E1_5_Y_STAR,
        xt_snapshot={
            "repo_root": str(repo_root),
            "mission_type": mission_result.mission.mission_type,
            "current_default_recommendation": mission_result.mission.recommended_path,
            "known_gap_czl_tuple_missing": True,
            "known_gap_action_wide_preflight_missing": True,
            "known_gap_owner_decision_packet_missing": True,
            "external_research_executed": False,
        },
        u_actions=[],
        y_t1_observed={},
        rt1_residuals=list(E1_5_Y_STAR),
        rt1_score=len(E1_5_Y_STAR),
        status="planned",
    )


def record_u_action(czl_state: CZLState, action: Dict[str, Any]) -> CZLState:
    return replace(czl_state, u_actions=[*czl_state.u_actions, action], status="running")


def observe_y_t1(czl_state: CZLState, evidence: Dict[str, Any]) -> CZLState:
    observed = dict(czl_state.y_t1_observed)
    observed.update(evidence)
    return replace(czl_state, y_t1_observed=observed)


def compute_rt1(czl_state: CZLState, y_star_criteria: List[str] | None = None) -> CZLState:
    evidence = czl_state.y_t1_observed
    checks = [
        ("czl_tuple_present", "Aiden Mission Command explicitly defines Y*, Xt, U, Yt+1, and Rt+1 for a mission."),
        ("counterfactual_gate_present", "Counterfactual reasoning is a decision gate, not just a report section."),
        ("counterfactual_gate_can_change_or_confirm", "Counterfactual gate can confirm or change the default recommendation."),
        ("action_wide_preflight_complete", "All proposed mission actions are inventoried and passed through governance preflight."),
        ("dynamic_obligation_ids_dry_run", "Obligation drafts use dynamic, collision-safe identifiers and remain dry-run only."),
        ("residual_update_review_gated", "Residual candidates can be updated with actual signal placeholders and remain review-gated."),
        ("owner_decision_packet_present", "A clear owner decision packet is generated."),
        ("plan_u_yt1_rt1_distinguished", "Mission output distinguishes plan, executable U, observed Yt+1, and remaining Rt+1."),
        ("no_external_side_effects", "No external side effects occur."),
        ("tests_and_unseen_smoke_passed", "Tests and unseen smoke checks verify behavior."),
    ]
    residuals = [criterion for key, criterion in checks if not evidence.get(key)]
    if evidence.get("external_research_executed") and not evidence.get("live_research_explicitly_enabled_and_budgeted"):
        residuals.append("External research was run without explicit enablement and budget.")
    if not evidence.get("action_wide_preflight_complete"):
        residuals.append("Action-wide preflight missing, so Rt+1 cannot be zero.")
    residuals = list(dict.fromkeys(residuals))
    return replace(
        czl_state,
        rt1_residuals=residuals,
        rt1_score=len(residuals),
        status="complete" if not residuals else "residual",
    )


def is_czl_complete(czl_state: CZLState) -> bool:
    return czl_state.rt1_score == 0 and not czl_state.rt1_residuals and czl_state.status == "complete"


def render_czl_markdown(czl_state: CZLState) -> str:
    lines = [
        "## CZL Mission Loop",
        f"- mission_id: {czl_state.mission_id}",
        f"- status: {czl_state.status}",
        f"- rt1_score: {czl_state.rt1_score}",
        "",
        "### Y*",
    ]
    lines.extend(f"- {item}" for item in czl_state.y_star)
    lines.extend(["", "### Xt"])
    lines.extend(f"- {key}: {value}" for key, value in czl_state.xt_snapshot.items())
    lines.extend(["", "### U"])
    for action in czl_state.u_actions:
        lines.append(f"- {action.get('action_id', 'u')}: {action.get('description') or action}")
    lines.extend(["", "### Yt+1"])
    lines.extend(f"- {key}: {value}" for key, value in czl_state.y_t1_observed.items())
    lines.extend(["", "### Rt+1"])
    if czl_state.rt1_residuals:
        lines.extend(f"- {item}" for item in czl_state.rt1_residuals)
    else:
        lines.append("- Rt+1 = 0")
    return "\n".join(lines)
