from __future__ import annotations

import sys
from pathlib import Path
from typing import Any, Dict

from .mission_model import Mission


def _add_sibling_repos(repo_root: Path) -> None:
    workspace = repo_root.parent
    for name in ("Y-star-gov", "gov-mcp"):
        candidate = workspace / name
        if candidate.exists():
            path = str(candidate)
            if path not in sys.path:
                sys.path.insert(0, path)


def run_ystar_gov_preflight(mission: Mission, repo_root: Path) -> Dict[str, Any]:
    _add_sibling_repos(repo_root)
    try:
        from ystar.domains.company_runtime import (
            classify_admin_rule,
            mission_action_preflight,
            value_production_relevance,
        )
    except Exception as exc:
        return {"available": False, "error": str(exc), "external_action_executed": False}

    mission_dict = {
        "mission_id": mission.mission_id,
        "owner_goal": mission.goal,
        "allowed_permission_tier": mission.allowed_permission_tier,
        "research_budget": mission.research_budget,
    }
    return {
        "available": True,
        "mission_action_preflight": mission_action_preflight(
            mission_dict,
            {"action": "read-only research for first paid customer interview"},
        ),
        "admin_rule_check": classify_admin_rule({"title": "old LinkedIn calendar"}),
        "value_alignment": value_production_relevance({"title": "first paid customer interview"}),
        "external_action_executed": False,
    }


def run_gov_mcp_preflight(mission: Mission, repo_root: Path) -> Dict[str, Any]:
    _add_sibling_repos(repo_root)
    try:
        from gov_mcp.company_runtime_tools import (
            gov_company_action_preflight,
            gov_company_admin_rule_check,
            gov_company_value_alignment_check,
        )
    except Exception as exc:
        return {"available": False, "error": str(exc), "external_action_executed": False}

    mission_dict = {
        "mission_id": mission.mission_id,
        "owner_goal": mission.goal,
        "allowed_permission_tier": mission.allowed_permission_tier,
        "research_budget": mission.research_budget,
    }
    return {
        "available": True,
        "internal_research": gov_company_action_preflight(
            {"action": "read-only research public page search"},
            mission_dict,
        ),
        "external_contact": gov_company_action_preflight(
            {"action": "send email to selected customer"},
            mission_dict,
        ),
        "admin_rule": gov_company_admin_rule_check({"title": "old daily report"}),
        "value_alignment": gov_company_value_alignment_check({"title": "first paid customer interview"}),
        "external_action_executed": False,
    }

