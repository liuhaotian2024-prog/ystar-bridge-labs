from __future__ import annotations

from dataclasses import asdict, dataclass
from typing import Any, Dict, List


@dataclass(frozen=True)
class ResidualCandidate:
    source_mission_id: str
    opportunity_id: str
    expected_signal: str
    actual_signal_placeholder: str
    residual_type: str
    assumption_tested: str
    if_failed_interpretation: str
    if_succeeded_interpretation: str
    recommended_strategy_update: str
    writeback_allowed: bool
    review_required: bool

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


def build_residual_candidates_for_experiments(
    experiments: List[Dict[str, Any]],
    counterfactual_cases: List[Dict[str, Any]],
    source_mission_id: str = "mission",
) -> List[Dict[str, Any]]:
    by_title = {case["opportunity_title"]: case for case in counterfactual_cases}
    candidates: List[Dict[str, Any]] = []
    for experiment in experiments:
        title = experiment["opportunity"]
        case = by_title.get(title, {})
        candidates.append(
            ResidualCandidate(
                source_mission_id=source_mission_id,
                opportunity_id=str(case.get("opportunity_id") or title.lower().replace(" ", "_")),
                expected_signal=str(experiment.get("success_metric") or "strong paid-signal proxy"),
                actual_signal_placeholder="to_be_filled_after_experiment",
                residual_type="opportunity_assumption_test",
                assumption_tested=str(case.get("highest_risk_assumption") or "buyer urgency and delivery feasibility"),
                if_failed_interpretation=(
                    "Downgrade or reshape the opportunity; classify whether failure came from pain, buyer, budget, trust, channel, delivery, or owner burden."
                ),
                if_succeeded_interpretation=(
                    "Prepare owner-reviewed external validation packet; do not execute contact automatically."
                ),
                recommended_strategy_update=(
                    "Update opportunity ranking and next experiment after owner review; no core memory/CIEU writeback by default."
                ),
                writeback_allowed=False,
                review_required=True,
            ).to_dict()
        )
    return candidates


def render_residual_candidates_markdown(candidates: List[Dict[str, Any]]) -> str:
    lines = ["## Residual Learning Candidates"]
    for item in candidates:
        lines.extend(
            [
                f"### {item['opportunity_id']}",
                f"- expected_signal: {item['expected_signal']}",
                f"- actual_signal_placeholder: {item['actual_signal_placeholder']}",
                f"- residual_type: {item['residual_type']}",
                f"- assumption_tested: {item['assumption_tested']}",
                f"- if_failed_interpretation: {item['if_failed_interpretation']}",
                f"- if_succeeded_interpretation: {item['if_succeeded_interpretation']}",
                f"- recommended_strategy_update: {item['recommended_strategy_update']}",
                f"- writeback_allowed: {item['writeback_allowed']}",
                f"- review_required: {item['review_required']}",
            ]
        )
    return "\n".join(lines)
