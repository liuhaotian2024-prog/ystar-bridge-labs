from __future__ import annotations

import json
from pathlib import Path

from .ecosystem_preflight import run_gov_mcp_preflight, run_ystar_gov_preflight
from .mission_alignment import align_mission_to_m_triangle
from .mission_from_owner_message import build_mission_from_owner_message
from .mission_model import MissionCommandResult
from .mission_router import route_mission
from .research_capability import audit_research_capability
from .team_task_builder import build_team_tasks


def build_mission_result(owner_message: str, repo_root: Path | None = None) -> MissionCommandResult:
    root = (repo_root or Path(__file__).resolve().parents[2]).resolve()
    mission = build_mission_from_owner_message(owner_message, root)
    routing = route_mission(mission)
    return MissionCommandResult(
        mission=mission,
        m_triangle_alignment=align_mission_to_m_triangle(mission),
        team_tasks=build_team_tasks(mission),
        autonomous_internal_actions=routing["autonomous_internal_actions"],
        approval_needed_actions=routing["approval_needed_actions"],
        admin_burden_avoided=routing["admin_burden_avoided"],
        ystar_gov_preflight=run_ystar_gov_preflight(mission, root),
        gov_mcp_preflight=run_gov_mcp_preflight(mission, root),
        next_owner_decision=routing["next_owner_decision"],
    )


def build_mission_summary(owner_message: str, repo_root: Path | None = None) -> str:
    result = build_mission_result(owner_message, repo_root)
    mission = result.mission
    root = (repo_root or Path(__file__).resolve().parents[2]).resolve()
    research_audit = audit_research_capability(root)
    evidence_mode = (
        "live-read-only evidence-backed plan"
        if research_audit.plan_confidence_allowed == "evidence_backed_live_read_only"
        else "internal-evidence preliminary plan"
    )
    lines = [
        "# Mission Command Summary",
        "",
        f"Mission goal: {mission.goal}",
        f"Mission type: {mission.mission_type}",
        f"Default priority: {mission.default_priority}",
        f"Evidence mode: {evidence_mode}",
        f"External research verdict: {research_audit.external_research_verdict}",
        f"Plan confidence allowed: {research_audit.plan_confidence_allowed}",
        "",
        "## Aiden Recommended Path",
        mission.recommended_path,
        "",
        "## M Triangle Alignment",
        f"Primary: {result.m_triangle_alignment['primary']}",
        result.m_triangle_alignment["explanation"],
        "",
        "## Evidence Basis",
        *mission.evidence_basis,
        "",
        "## Team Task Split",
    ]
    for task in result.team_tasks:
        lines.append(f"- {task.agent} ({task.function}, Tier {task.permission_tier}): {task.task} Output: {task.output}.")
    lines.extend(
        [
            "",
            "## Autonomous Internal Actions",
            *[f"- {action}" for action in result.autonomous_internal_actions],
            "",
            "## Approval-Needed Actions",
            *[f"- {action}" for action in result.approval_needed_actions],
            "",
            "## Admin Burden Avoided",
            *[f"- {item}" for item in result.admin_burden_avoided],
            "",
            "## Y-star-gov Preflight",
            "```json",
            json.dumps(result.ystar_gov_preflight, ensure_ascii=False, indent=2, sort_keys=True),
            "```",
            "",
            "## gov-mcp Preflight",
            "```json",
            json.dumps(result.gov_mcp_preflight, ensure_ascii=False, indent=2, sort_keys=True),
            "```",
            "",
            "## Next Owner Decision",
            result.next_owner_decision,
            "",
            "Safety: no external sending, customer contact, email, payment, publication, form submission, account creation, or core DB writeback executed.",
        ]
    )
    return "\n".join(lines)
