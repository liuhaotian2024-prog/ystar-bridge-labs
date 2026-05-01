from __future__ import annotations

from typing import Any, Dict, Iterable, List

from .action_semantics import (
    action_class_from_structured_action,
    classify_structured_action,
    decision_from_structured_action,
    explain_action_semantics,
)
from .governance_bridge import preflight_mission_action
from .mission_model import MissionCommandResult


def _action(action_id: str, title: str, source: str) -> Dict[str, Any]:
    structured = classify_structured_action(
        {
            "action_id": action_id,
            "action_title": title,
            "action_source": source,
        }
    )
    return {
        "action_id": action_id,
        "action_title": title,
        "action_source": source,
        "action_class": action_class_from_structured_action(structured),
        "structured_action": structured.to_dict(),
    }


def build_action_inventory(
    mission_result: MissionCommandResult,
    method_trace: Dict[str, Any],
    obligation_drafts: Iterable[Dict[str, Any]],
    residual_candidates: Iterable[Dict[str, Any]],
) -> List[Dict[str, Any]]:
    actions: List[Dict[str, Any]] = []
    index = 1
    for title in mission_result.autonomous_internal_actions:
        actions.append(_action(f"action_{index:03d}", title, "autonomous_internal_actions"))
        index += 1
    for title in mission_result.approval_needed_actions:
        actions.append(_action(f"action_{index:03d}", title, "approval_needed_actions"))
        index += 1
    for task in mission_result.team_tasks:
        actions.append(_action(f"action_{index:03d}", f"{task.agent}: {task.task} Output: {task.output}", "team_task"))
        index += 1
    for experiment in method_trace.get("experiments", []):
        actions.append(_action(f"action_{index:03d}", experiment["48h_internal_experiment"], "experiment_48h_internal"))
        index += 1
        actions.append(_action(f"action_{index:03d}", experiment["tier1_read_only_research_experiment"], "experiment_tier1_research"))
        index += 1
        actions.append(_action(f"action_{index:03d}", experiment["approval_needed_external_validation_experiment"], "experiment_external_validation"))
        index += 1
    for draft in obligation_drafts:
        actions.append(_action(f"action_{index:03d}", f"Obligation dry-run draft: {draft['rule_name']}", "obligation_draft"))
        index += 1
    for candidate in residual_candidates:
        actions.append(_action(f"action_{index:03d}", f"Residual review candidate: {candidate['opportunity_id']}", "residual_candidate"))
        index += 1
    actions.append(_action(f"action_{index:03d}", method_trace.get("next_executable_u", ""), "next_executable_u"))
    return actions


def preflight_action_inventory(
    actions: List[Dict[str, Any]],
    mission_dict: Dict[str, Any],
    repo_root: Any,
) -> List[Dict[str, Any]]:
    rows: List[Dict[str, Any]] = []
    for action in actions:
        preflight = preflight_mission_action({"action": action["action_title"]}, mission_dict, repo_root)
        structured = classify_structured_action(action)
        decision = decision_from_structured_action(structured)
        rows.append(
            {
                **action,
                "action_class": action_class_from_structured_action(structured),
                "structured_action": structured.to_dict(),
                "preflight_decision": decision,
                "reason": explain_action_semantics(structured)
                or preflight.get("owner_visible_explanation")
                or preflight.get("reason")
                or preflight.get("error")
                or "",
                "external_action_executed": False,
                "preflight": preflight,
            }
        )
    return rows


def summarize_action_preflight(rows: List[Dict[str, Any]]) -> Dict[str, Any]:
    counts: Dict[str, int] = {}
    for row in rows:
        counts[row["preflight_decision"]] = counts.get(row["preflight_decision"], 0) + 1
    return {
        "total_actions": len(rows),
        "decision_counts": counts,
        "all_actions_preflighted": all(row.get("preflight_decision") for row in rows),
        "external_action_executed": False,
        "rows": rows,
    }


def render_action_preflight_markdown(rows: List[Dict[str, Any]]) -> str:
    lines = [
        "## Action-Wide Governance Preflight Table",
        "| action_id | source | class | decision | title | external_action_executed |",
        "| --- | --- | --- | --- | --- | --- |",
    ]
    for row in rows:
        title = str(row["action_title"]).replace("|", "/")
        lines.append(
            f"| {row['action_id']} | {row['action_source']} | {row['action_class']} | {row['preflight_decision']} | {title} | {row['external_action_executed']} |"
        )
    return "\n".join(lines)
