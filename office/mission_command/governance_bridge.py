from __future__ import annotations

import sys
from pathlib import Path
from typing import Any, Dict, List


def _add_sibling_repos(repo_root: Path) -> None:
    workspace = repo_root.parent
    for name in ("Y-star-gov", "gov-mcp"):
        candidate = workspace / name
        if candidate.exists():
            path = str(candidate)
            if path not in sys.path:
                sys.path.insert(0, path)


def _unavailable(kind: str, exc: Exception | str) -> Dict[str, Any]:
    return {
        "bridge": kind,
        "available": False,
        "error": str(exc),
        "external_action_executed": False,
        "core_db_write": False,
    }


def preflight_mission_action(
    action: Dict[str, Any],
    mission: Dict[str, Any],
    repo_root: Path | None = None,
    force_unavailable: bool = False,
) -> Dict[str, Any]:
    if force_unavailable:
        return _unavailable("mission_action", "forced unavailable for graceful-degradation test")
    root = (repo_root or Path(__file__).resolve().parents[2]).resolve()
    _add_sibling_repos(root)
    try:
        from gov_mcp.company_runtime_tools import gov_company_action_preflight

        result = gov_company_action_preflight(action, mission)
        result["bridge"] = "gov_mcp_company_action_preflight"
        result["external_action_executed"] = False
        return result
    except Exception as mcp_exc:
        try:
            from ystar.domains.company_runtime import mission_permission_check

            result = mission_permission_check(mission, action)
            result["bridge"] = "ystar_company_runtime_mission_permission_check"
            result["external_action_executed"] = False
            return result
        except Exception as gov_exc:
            return _unavailable("mission_action", f"gov-mcp: {mcp_exc}; Y-star-gov: {gov_exc}")


def preflight_admin_rule(
    rule: Dict[str, Any],
    mission: Dict[str, Any] | None = None,
    repo_root: Path | None = None,
    force_unavailable: bool = False,
) -> Dict[str, Any]:
    if force_unavailable:
        return _unavailable("admin_rule", "forced unavailable for graceful-degradation test")
    root = (repo_root or Path(__file__).resolve().parents[2]).resolve()
    _add_sibling_repos(root)
    try:
        from gov_mcp.company_runtime_tools import gov_company_admin_rule_check

        result = gov_company_admin_rule_check(rule)
        result["bridge"] = "gov_mcp_company_admin_rule_check"
        result["external_action_executed"] = False
        return result
    except Exception as mcp_exc:
        try:
            from ystar.domains.company_runtime import classify_admin_rule

            result = classify_admin_rule(rule)
            result["bridge"] = "ystar_company_runtime_classify_admin_rule"
            result["external_action_executed"] = False
            return result
        except Exception as gov_exc:
            return _unavailable("admin_rule", f"gov-mcp: {mcp_exc}; Y-star-gov: {gov_exc}")


def preflight_value_alignment(
    item: Dict[str, Any],
    repo_root: Path | None = None,
    force_unavailable: bool = False,
) -> Dict[str, Any]:
    if force_unavailable:
        return _unavailable("value_alignment", "forced unavailable for graceful-degradation test")
    root = (repo_root or Path(__file__).resolve().parents[2]).resolve()
    _add_sibling_repos(root)
    try:
        from gov_mcp.company_runtime_tools import gov_company_value_alignment_check

        result = gov_company_value_alignment_check(item)
        result["bridge"] = "gov_mcp_company_value_alignment_check"
        result["external_action_executed"] = False
        return result
    except Exception as mcp_exc:
        try:
            from ystar.domains.company_runtime import value_production_relevance

            result = value_production_relevance(item)
            result["bridge"] = "ystar_company_runtime_value_production_relevance"
            result["external_action_executed"] = False
            return result
        except Exception as gov_exc:
            return _unavailable("value_alignment", f"gov-mcp: {mcp_exc}; Y-star-gov: {gov_exc}")


def summarize_preflight_results(results: List[Dict[str, Any]]) -> Dict[str, Any]:
    decisions = [result.get("decision") for result in results if result.get("decision")]
    return {
        "available_count": sum(1 for result in results if result.get("available", True)),
        "approval_needed": any(decision == "NEEDS_OWNER_APPROVAL" for decision in decisions),
        "blocked_or_review_gated": any(decision in {"BLOCKED", "REVIEW_GATED"} for decision in decisions),
        "external_action_executed": False,
        "core_db_write": False,
        "results": results,
    }
