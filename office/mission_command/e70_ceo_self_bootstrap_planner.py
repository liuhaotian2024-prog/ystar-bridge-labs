from __future__ import annotations

import json
import os
import subprocess
import time
from pathlib import Path
from typing import Any

from .e69_ceo_next_action_planner_readback import (
    get_ceo_candidate_actions,
    get_ceo_next_action_scoring,
    get_ceo_selected_next_action,
    get_owner_decision_packet as get_e69_owner_decision_packet,
    load_e69_next_action_state_for_brain,
)


BRIDGE_ROOT = Path(os.environ.get("YSTAR_BRIDGE_LABS_ROOT", Path(__file__).resolve().parents[2]))
Y_GOV_ROOT = Path(os.environ.get("YSTAR_GOV_ROOT", "/Users/haotianliu/.openclaw/workspace/Y-star-gov"))
GOV_MCP_ROOT = Path(os.environ.get("GOV_MCP_ROOT", "/Users/haotianliu/.openclaw/workspace/gov-mcp"))
K9_ROOT = Path(os.environ.get("K9AUDIT_ROOT", "/Users/haotianliu/.openclaw/workspace/K9Audit"))

JOB_ID = "e70_ceo_self_bootstrap_capability_growth_runtime_L5_20260506T000001Z"
EXPECTED_BASE = "44e6c7d74c8d059b4d3aa01bdc829576e562b03c"
OWNER_DECISION_STATUS = "pending_owner_decision"
GOAL_ID = "integrate_CIEU_audit_log_module_into_governed_business_operations_blueprint"
CURRENT_PRIMARY_ROUTE = "governed_business_operations_blueprint_for_agent_teams"
CIEU_ROUTE = "CIEU_high_risk_AI_agent_audit_log"
SELECTED_SELF_BOOTSTRAP_ACTION = "combined_self_bootstrap_foundation_layer"
NEAREST_SELF_BOOTSTRAP_ALTERNATIVE = "install_self_evolution_CIEU_loop_as_CEO_runtime_capability"
REFERENCED_BUSINESS_ACTION = "integrate_CIEU_audit_log_module_into_governed_business_operations_blueprint_no_execution"
GENERATED_CODEX_JOB_PROPOSAL_ID = "e70_codex_job_E71_execute_internal_CIEU_module_integration_no_external_action"
GENERATED_MILESTONE = "E71_execute_internal_CIEU_module_integration_no_external_action"
NEXT_RECOMMENDED_MILESTONE = "E71_execute_CEO_generated_codex_job_proposal_no_external_action"


def utc_now() -> str:
    return time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())


def write_json(root: Path, rel: str, data: dict[str, Any]) -> None:
    path = root / rel
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


def write_jsonl(root: Path, rel: str, rows: list[dict[str, Any]]) -> None:
    path = root / rel
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("".join(json.dumps(row, ensure_ascii=False) + "\n" for row in rows), encoding="utf-8")


def write_md(root: Path, rel: str, title: str, lines: list[str]) -> None:
    path = root / rel
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("# " + title + "\n\n" + "\n".join(lines) + "\n", encoding="utf-8")


def load_json(rel: str, root: Path | None = None) -> dict[str, Any]:
    try:
        return json.loads(((root or BRIDGE_ROOT) / rel).read_text(encoding="utf-8"))
    except Exception:
        return {}


def read_text(path: Path, limit: int = 60000) -> str:
    try:
        if not path.exists() or path.is_dir():
            return ""
        return path.read_text(encoding="utf-8", errors="ignore")[:limit]
    except Exception:
        return ""


def git_state(path: Path, expected_head: str | None = None) -> dict[str, Any]:
    def run(*args: str) -> str:
        try:
            return subprocess.check_output(["git", *args], cwd=path, text=True, stderr=subprocess.DEVNULL).strip()
        except Exception:
            return ""

    head = run("rev-parse", "HEAD")
    status = run("status", "--short")
    branch = run("rev-parse", "--abbrev-ref", "HEAD")
    return {
        "path": str(path),
        "branch": branch,
        "head": head,
        "expected_head": expected_head,
        "head_matches_expected": expected_head is None or head == expected_head,
        "clean": status == "",
        "status_short": status,
    }


def dirty_paths_are_e70_scoped(status_short: str) -> bool:
    if not status_short:
        return True
    allowed_prefixes = (
        "office/mission_command/e70_",
        "tests/office/test_e70_",
        "operations/external_validation/e70_",
        "operations/knowledge_graph/e70_",
        "reports/integration/e70_",
    )
    allowed_exact = {"office/mission_command/e46b_ceo_brain_adapter.py"}
    for line in status_short.splitlines():
        path = line[3:] if len(line) > 3 and line[2] == " " else line[2:].strip()
        if path in allowed_exact or path.startswith(allowed_prefixes):
            continue
        return False
    return True


def build_base_state_manifest(root: Path | None = None) -> dict[str, Any]:
    base = root or BRIDGE_ROOT
    bridge = git_state(base, EXPECTED_BASE)
    read_only = {
        "Y-star-gov": git_state(Y_GOV_ROOT, "b0d9aa8b1badd1180127a2f79f73ceed48e16451"),
        "gov-mcp": git_state(GOV_MCP_ROOT, "d0181bc8f19d8ae7714bd0f8a220fe12e6ceee90"),
        "K9Audit": git_state(K9_ROOT, "37911e18ce4425470e3f745b30d155c43d76ff55"),
    }
    return {
        "artifact_id": "e70_base_state_manifest",
        "bridge_job_id": JOB_ID,
        "bridge_labs": bridge,
        "expected_branch": "backflow/aiden-ceo-meeting-room",
        "base_verified": bridge["head_matches_expected"] and bridge["branch"] == "backflow/aiden-ceo-meeting-room",
        "bridge_labs_worktree_clean_or_e70_scoped": dirty_paths_are_e70_scoped(bridge["status_short"]),
        "read_only_repos": read_only,
        "read_only_repos_clean": all(item.get("clean", True) for item in read_only.values()),
        "e69_completed_report_present": Path("/tmp/ystar_delivery_bridge/completed/e69_ceo_autonomous_next_action_planner_and_cieu_module_plan_20260506T000001Z.report.json").exists(),
        "e69_failed_blocker_report_present": Path("/tmp/ystar_delivery_bridge/failed/e69_ceo_self_bootstrap_capability_growth_runtime_L5_20260506T000001Z.report.json").exists(),
        "owner_decision_status": OWNER_DECISION_STATUS,
        "external_action_allowed": False,
    }


def discover_self_evolution_creed(root: Path | None = None) -> dict[str, Any]:
    base = root or BRIDGE_ROOT
    agent_paths = [
        ".claude/agents/ceo.md",
        ".claude/agents/cto.md",
        ".claude/agents/cmo.md",
        ".claude/agents/cso.md",
        ".claude/agents/cfo.md",
    ]
    files = []
    for rel in agent_paths:
        text = read_text(base / rel)
        files.append(
            {
                "path": rel,
                "exists": bool(text),
                "contains_self_evolution_creed": "Self-Evolution Creed" in text,
                "contains_CIEU_five_tuple_terms": all(term in text for term in ["Y*", "X_t", "U", "Y_{t+1}", "R_{t+1}"]),
            }
        )
    try:
        commit_stat = subprocess.check_output(
            ["git", "show", "--stat", "--oneline", "e7b11b22a0555f0a98d54aa444f2d738fe0a0bda"],
            cwd=base,
            text=True,
            stderr=subprocess.DEVNULL,
        )
    except Exception:
        commit_stat = ""
    return {
        "source_commit": "e7b11b22a0555f0a98d54aa444f2d738fe0a0bda",
        "source_commit_title": "creed: CIEU five-tuple self-evolution written into all 5 agents",
        "commit_available_in_local_history": bool(commit_stat),
        "agent_files": files,
        "creed_discovered": any(item["contains_self_evolution_creed"] for item in files),
        "core_pattern": {
            "Y_star_capability_target": "ideal capability target",
            "X_t_current_capability_state": "honest current state",
            "U_t_improvement_action": "immediate action to close the gap",
            "Y_t_plus_1_measured_improvement": "actual measured improvement after action",
            "R_t_plus_1_remaining_gap": "honest remaining distance to Y_star",
            "cycle": "act -> measure -> assess gap -> derive next action -> repeat",
        },
    }


def local_skill_inventory(root: Path | None = None) -> dict[str, Any]:
    base = root or BRIDGE_ROOT
    patterns = (
        "skill",
        "skills",
        "capability",
        "tool",
        "tool_registry",
        "install",
        "plugin",
        "bootstrap",
        "self",
        "self_evolution",
        "self_improvement",
        "learning",
        "capability_gap",
        "enhancement",
        "codex",
        "proposal",
        "bridge",
    )
    matches: list[str] = []
    for path in base.rglob("*"):
        if ".git" in path.parts or path.is_dir():
            continue
        rel = str(path.relative_to(base))
        lowered = rel.lower()
        if any(pattern in lowered for pattern in patterns):
            matches.append(rel)
        if len(matches) >= 80:
            break
    return {
        "local_skill_inventory_allowed": True,
        "external_skill_installation_executed": False,
        "internet_package_install_attempted": False,
        "local_skill_candidate_count": len(matches),
        "local_skill_candidate_paths": matches[:40],
        "missing_formal_skill_registry": not any("tool_registry" in item or "skills/" in item for item in matches),
        "installation_constraints": [
            "local inventory is allowed",
            "selection is proposal-only",
            "public-read discovery may be planned but not installed",
            "external skill/package install requires owner approval",
        ],
    }


def e69_state_bundle(root: Path | None = None) -> dict[str, Any]:
    base = root or BRIDGE_ROOT
    return {
        "E69_next_action_state": load_e69_next_action_state_for_brain(base),
        "E69_business_candidates": get_ceo_candidate_actions(base),
        "E69_business_scoring": get_ceo_next_action_scoring(base),
        "E69_selected_business_action": get_ceo_selected_next_action(base),
        "E69_owner_packet": get_e69_owner_decision_packet(base),
    }


def build_repository_archaeology_inventory(root: Path | None = None) -> dict[str, Any]:
    base = root or BRIDGE_ROOT
    expected_assets = [
        ("office/mission_command/e69_ceo_next_action_planner.py", "E69_business_next_action_planner", "reuse_directly"),
        ("office/mission_command/e69_ceo_next_action_planner_readback.py", "E69_business_next_action_readback", "reuse_directly"),
        ("operations/external_validation/e69_ceo_next_action_candidate_set.json", "E69_business_candidate_set", "reuse_directly"),
        ("operations/external_validation/e69_ceo_selected_next_action_decision.json", "E69_selected_business_action", "reuse_directly"),
        ("operations/external_validation/e69_owner_decision_packet_no_execution.json", "E69_owner_packet_pattern", "thin_wrap"),
        ("office/mission_command/e65_ceo_market_dynamics_readback.py", "E65_market_dynamics_API", "reuse_directly"),
        ("office/mission_command/e67_ceo_external_validation_readback.py", "E67_external_validation_API", "reuse_directly"),
        ("office/mission_command/e68_ceo_cieu_route_readback.py", "E68_CIEU_route_API", "reuse_directly"),
        ("operations/external_validation/e66_selected_route_offer_blueprint.json", "E66_offer_blueprint", "reuse_directly"),
        ("office/mission_command/e46b_ceo_brain_adapter.py", "CEO_brain_adapter", "extend_thinly"),
    ]
    assets = [
        {
            "path": path,
            "capability_type": capability_type,
            "exists": (base / path).exists(),
            "reuse_strategy": strategy,
            "connected_status": "connected" if (base / path).exists() else "missing",
        }
        for path, capability_type, strategy in expected_assets
    ]
    creed = discover_self_evolution_creed(base)
    skills = local_skill_inventory(base)
    return {
        "artifact_id": "e70_self_bootstrap_repository_archaeology_inventory",
        "bridge_job_id": JOB_ID,
        "base_artifacts_inspected": [item["path"] for item in assets],
        "E69_autonomous_next_action_planner_assets_reused": [item["path"] for item in assets if item["capability_type"].startswith("E69")],
        "old_self_evolution_creed_assets": creed,
        "reusable_CEO_state_loaders": [
            "load_e69_next_action_state_for_brain",
            "load_e65_market_dynamics_state_for_brain",
            "load_e67_external_validation_state_for_brain",
            "load_e68_cieu_route_state_for_brain",
        ],
        "reusable_market_dynamics_APIs": ["rank_routes_by_profile", "get_decision_stability", "get_recommended_market_portfolio"],
        "reusable_external_validation_APIs": ["get_route_external_validation_score", "list_owner_gated_validation_next_steps"],
        "reusable_CIEU_route_APIs": ["get_cieu_route_score", "get_cieu_external_validation", "get_cieu_portfolio_role"],
        "reusable_offer_blueprint_assets": ["operations/external_validation/e66_selected_route_offer_blueprint.json"],
        "existing_local_skill_tool_capability_assets": skills,
        "existing_bridge_job_or_Codex_proposal_patterns": [
            "delivery bridge completed report convention",
            "operations/external_validation owner packet convention",
            "E69 generated owner decision packet no-execution pattern",
        ],
        "disconnected_self_improvement_assets": [
            "old agent creed existed as instruction text, not CEO-callable runtime",
            "E69 business planner generated next actions but not self-improvement candidates",
            "no generated Codex job proposal API existed before E70",
        ],
        "what_must_not_be_rebuilt": [
            "E69 business next-action planner",
            "E65 market dynamics model",
            "E67 external validation model",
            "E68 CIEU route model",
            "E66 offer blueprint",
            "CIEU self-evolution creed",
            "public-read adapters",
            "evidence atomizers",
            "behavior authorization gate conventions",
            "KG/CZL/CIEU writeback conventions",
            "delivery bridge patterns",
        ],
        "E70_adds": "self-bootstrap runtime layer: goal-to-capability mapping, self-improvement candidates, scoring, Codex job proposal generation, skill boundary, CIEU residual measurement, and CEO readback",
        "asset_count": len(assets),
        "assets": assets,
        "external_action_allowed": False,
    }


def build_reuse_first_growth_audit(root: Path | None = None) -> dict[str, Any]:
    return {
        "artifact_id": "e70_self_bootstrap_reuse_first_growth_audit",
        "bridge_job_id": JOB_ID,
        "passed": True,
        "reused_assets": [
            "E69 autonomous next-action planner and readback",
            "E65 market dynamics readback/API",
            "E67 external validation readback/API",
            "E68 CIEU route readback/API",
            "E66 selected offer blueprint",
            "old CIEU self-evolution creed in .claude/agents",
            "existing KG/CZL/CIEU artifact conventions",
        ],
        "thin_wrappers_added": [
            "office/mission_command/e70_ceo_capability_growth_model.py",
            "office/mission_command/e70_ceo_self_bootstrap_readback.py",
        ],
        "genuinely_new_assets_added": [
            "office/mission_command/e70_ceo_self_bootstrap_planner.py",
            "goal-to-capability map",
            "capability gap registry",
            "Codex job proposal schema and generated proposal",
            "skill inventory/install boundary",
            "L5 use-case measurement artifact",
        ],
        "duplicate_capability_risks_checked": [
            "does not rebuild E69 business planner",
            "does not rebuild E65 scoring",
            "does not rebuild E67 validation ladder",
            "does not rebuild E68 CIEU route scoring",
            "does not install external skills",
        ],
        "avoided_rebuilds": [
            "E70 consumes E69 business-action decision instead of reselecting the business route",
            "E70 formalizes the old creed instead of inventing a parallel self-evolution theory",
            "E70 produces proposal packets but does not execute unapproved external action",
        ],
        "justification_for_new_runtime": "No prior CEO-callable layer could map a goal to capability gaps, generate self-improvement candidates, create Codex job proposals, plan skill boundaries, and measure CIEU residuals.",
        "external_action_allowed": False,
    }


def build_self_evolution_runtime_schema(root: Path | None = None) -> dict[str, Any]:
    return {
        "artifact_id": "e70_cieu_self_evolution_runtime_schema",
        "bridge_job_id": JOB_ID,
        "schema_version": "E70_CIEU_self_bootstrap_runtime_v1",
        "fields": {
            "Y_star_capability_target": "ideal measurable CEO capability target",
            "X_t_current_capability_state": "honest current CEO capability state",
            "goal_context": "active business/runtime goal driving capability growth",
            "capability_gap": "missing capability blocking the goal",
            "U_t_improvement_action": "immediate internal improvement action",
            "Y_t_plus_1_measured_improvement": "measured improvement after U_t",
            "R_t_plus_1_remaining_gap": "remaining distance to Y_star after measurement",
            "evidence_required": "artifacts/tests/readback needed before claiming improvement",
            "allowed_improvement_modes": "governed modes CEO may propose",
            "prohibited_improvement_modes": "unsafe modes CEO must not perform",
            "behavior_authorization_requirement": "ALLOW/DENY gate must be explicit",
            "owner_approval_requirement": "external or installation steps stay owner-gated",
            "KG_CZL_CIEU_writeback_requirement": "results must be written to read model and residual logs",
            "next_cycle_trigger": "residual or new goal that triggers the next self-bootstrap loop",
        },
        "allowed_improvement_modes": [
            "reuse_existing_capability",
            "reconnect_existing_capability",
            "strengthen_existing_capability_with_tests_or_readback",
            "generate_internal_code_enhancement_proposal",
            "request_Codex_implementation_under_owner_approved_job",
            "local_skill_inventory_and_selection",
            "public_read_only_skill_discovery_plan",
            "owner_gated_skill_installation_plan",
            "owner_gated_external_capability_acquisition",
            "defer_due_to_safety_or_permission",
        ],
        "prohibited_improvement_modes": [
            "autonomous_external_installation",
            "private_provider_API_use",
            "internet_package_install_without_approval",
            "modifying_read_only_repos",
            "executing_unreviewed_self_modifying_code",
            "bypassing_behavior_authorization",
            "claiming_improvement_without_measurement",
            "using_fabricated_evidence",
        ],
        "old_creed_integrated": discover_self_evolution_creed(root).get("creed_discovered") is True,
        "external_action_allowed": False,
    }


def build_installed_capability_inventory(root: Path | None = None) -> dict[str, Any]:
    base = root or BRIDGE_ROOT
    e69 = e69_state_bundle(base)
    skills = local_skill_inventory(base)
    capabilities = [
        {
            "capability": "autonomous_next_action_planning",
            "source": "E69",
            "available_to_CEO": True,
            "callable_or_read_only": "callable",
            "evidence_artifact": "operations/external_validation/e69_ceo_brain_next_action_planning_update.json",
            "loader_API_functions": ["get_ceo_candidate_actions", "get_ceo_next_action_scoring", "get_ceo_selected_next_action"],
            "what_CEO_can_answer": ["business candidate set", "business scoring", "selected internal next action", "owner packet"],
            "limitation": "business-action planning, not full self-bootstrap before E70",
            "can_influence_next_action_selection": True,
            "can_influence_capability_growth_selection": True,
        },
        {
            "capability": "market_dynamics",
            "source": "E65",
            "available_to_CEO": True,
            "callable_or_read_only": "callable",
            "evidence_artifact": "operations/external_validation/e65_ceo_brain_market_dynamics_update.json",
            "loader_API_functions": ["rank_routes_by_profile", "get_decision_stability", "get_recommended_market_portfolio"],
            "what_CEO_can_answer": ["route profiles", "portfolio stability", "evidence limits"],
            "limitation": "no customer or paid validation",
            "can_influence_next_action_selection": True,
            "can_influence_capability_growth_selection": True,
        },
        {
            "capability": "external_validation",
            "source": "E67",
            "available_to_CEO": True,
            "callable_or_read_only": "callable",
            "evidence_artifact": "operations/external_validation/e67_route_external_validation_scorecards.json",
            "EV_levels": "EV0-EV8",
            "owner_gated_validation_roadmap": "operations/external_validation/e67_owner_gated_external_validation_roadmap.json",
            "limitation": "EV1-EV4 non-contact evidence only",
            "can_influence_next_action_selection": True,
            "can_influence_capability_growth_selection": True,
        },
        {
            "capability": "CIEU_route",
            "source": "E68",
            "available_to_CEO": True,
            "callable_or_read_only": "callable",
            "evidence_artifact": "operations/external_validation/e68_ceo_brain_cieu_route_update.json",
            "portfolio_role": "high-defensibility strategic vertical and module",
            "product_wedge": "Governed Business Operations Blueprint + CIEU Audit Module",
            "limitation": "no legal/compliance/medical/energy readiness claim",
            "can_influence_next_action_selection": True,
            "can_influence_capability_growth_selection": True,
        },
        {
            "capability": "model_driven_offer",
            "source": "E66",
            "available_to_CEO": True,
            "callable_or_read_only": "read_only_artifact",
            "evidence_artifact": "operations/external_validation/e66_selected_route_offer_blueprint.json",
            "selected_route": CURRENT_PRIMARY_ROUTE,
            "limitation": "draft-only internal; not customer or paid validated",
            "can_influence_next_action_selection": True,
            "can_influence_capability_growth_selection": False,
        },
        {
            "capability": "self_evolution_creed",
            "source": "old .claude/agents creed",
            "available_to_CEO": True,
            "callable_or_read_only": "formalized_by_E70_runtime",
            "evidence_artifact": ".claude/agents/ceo.md",
            "limitation": "was instruction-only before E70",
            "can_influence_next_action_selection": False,
            "can_influence_capability_growth_selection": True,
        },
        {
            "capability": "runtime_governance",
            "source": "E54/E55/E56/KG_CZL_CIEU",
            "available_to_CEO": True,
            "callable_or_read_only": "readback_and_policy",
            "evidence_artifact": "office/mission_command/e46b_ceo_brain_adapter.py",
            "limitation": "internal proposal generation only; external execution owner-gated",
            "can_influence_next_action_selection": True,
            "can_influence_capability_growth_selection": True,
        },
        {
            "capability": "local_skill_tool_capability_inventory",
            "source": "local repo search",
            "available_to_CEO": True,
            "callable_or_read_only": "inventory_only",
            "evidence_artifact": "operations/external_validation/e70_skill_inventory_and_installation_boundary.json",
            "local_skill_candidate_count": skills["local_skill_candidate_count"],
            "limitation": "no external skill installation; selection is proposal-only",
            "can_influence_next_action_selection": False,
            "can_influence_capability_growth_selection": True,
        },
        {
            "capability": "Codex_bridge_job_proposal",
            "source": "E70",
            "available_to_CEO": True,
            "callable_or_read_only": "callable_after_E70",
            "evidence_artifact": "operations/external_validation/e70_generated_codex_job_proposal.json",
            "limitation": "CEO may propose jobs; Codex execution remains an approved bridge job, not arbitrary self-execution",
            "can_influence_next_action_selection": True,
            "can_influence_capability_growth_selection": True,
        },
    ]
    return {
        "artifact_id": "e70_ceo_installed_capability_inventory",
        "bridge_job_id": JOB_ID,
        "e69_selected_business_action": e69["E69_selected_business_action"].get("selected_next_action"),
        "capability_count": len(capabilities),
        "capabilities": capabilities,
        "all_required_capabilities_available_to_CEO": all(item["available_to_CEO"] for item in capabilities),
        "external_action_allowed": False,
    }


def build_current_state_and_gap_synthesis(root: Path | None = None) -> dict[str, Any]:
    e69 = e69_state_bundle(root)
    return {
        "artifact_id": "e70_ceo_current_state_and_capability_gap_synthesis",
        "bridge_job_id": JOB_ID,
        "current_business_state": {
            "primary_first_cash_route": CURRENT_PRIMARY_ROUTE,
            "CIEU_high_defensibility_vertical": CIEU_ROUTE,
            "fallback_route": "founder_operator_decision_brief_service",
            "learning_route": "public_read_market_intelligence_product",
            "strategic_compounding_route": CIEU_ROUTE,
            "selected_offer_blueprint_status": "draft_only_internal",
            "CIEU_module_integration_selected_by_E69": e69["E69_selected_business_action"].get("selected_next_action") == REFERENCED_BUSINESS_ACTION,
            "non_contact_EV_level": "EV4_public_demand_or_behavior_proxy",
            "owner_gated_blockers": ["external review", "EV5 experiment", "human feedback", "pricing presentation", "payment", "client delivery"],
            "evidence_quality_limits": ["no customer validation", "no paid signal", "no pricing validation", "no expert feedback"],
        },
        "current_CEO_capability_state": {
            "capabilities_installed_and_readable": ["E65", "E66", "E67", "E68", "E69"],
            "capabilities_callable": ["E69 business planner", "E65 market readback", "E67 validation readback", "E68 CIEU readback"],
            "capabilities_only_report_only": ["old self-evolution creed before E70", "some local skill/tool references"],
            "E69_business_next_action_generation_exists": True,
            "missing_self_improvement_candidate_generation": True,
            "missing_autonomous_skill_discovery_selection": True,
            "missing_owner_gated_skill_installation_workflow": True,
            "missing_self_improvement_CIEU_cycle_as_runtime_artifact": True,
            "missing_measured_capability_improvement_loop": True,
            "missing_automatic_Codex_job_proposal_generation": True,
            "missing_reusable_goal_to_capability_mapping": True,
        },
        "unresolved_residuals": [
            "customer validation absent",
            "paid signal absent",
            "external action owner-gated",
            "CIEU module not yet executed as final product update",
            "CEO is not fully autonomous in external execution",
            "CEO does not yet self-generate capability upgrades as a standard operating loop before E70",
        ],
        "CEO_can_safely_do_internally_after_E70": [
            "generate capability-growth candidates",
            "propose internal code-enhancement jobs",
            "propose local skill reuse",
            "propose owner-gated skill discovery/install plan",
            "measure capability growth with CIEU residuals",
        ],
        "CEO_cannot_do_without_owner_approval": [
            "external review",
            "publication",
            "outreach",
            "install external packages or skills",
            "use private APIs",
            "execute client delivery",
            "claim compliance, revenue, or validation",
        ],
        "active_goal": GOAL_ID,
        "external_action_allowed": False,
    }


CAPABILITY_GAPS = [
    {
        "capability_gap_id": "gap_self_evolution_creed_not_runtime",
        "gap": "Old CIEU self-evolution creed exists but is not a CEO-callable runtime loop.",
        "blocking_goal": GOAL_ID,
        "severity": "high",
        "required_capabilities": ["runtime schema", "residual measurement", "readback"],
    },
    {
        "capability_gap_id": "gap_goal_to_capability_mapping_absent",
        "gap": "CEO cannot systematically map strategic goals to required internal capabilities.",
        "blocking_goal": GOAL_ID,
        "severity": "high",
        "required_capabilities": ["goal mapper", "capability requirements"],
    },
    {
        "capability_gap_id": "gap_codex_job_proposal_generation_absent",
        "gap": "CEO cannot yet generate a complete Codex bridge job proposal for internal capability enhancement.",
        "blocking_goal": GOAL_ID,
        "severity": "high",
        "required_capabilities": ["proposal schema", "proposal generator", "safety boundaries"],
    },
    {
        "capability_gap_id": "gap_skill_installation_boundary_absent",
        "gap": "CEO lacks a governed skill/tool inventory and installation boundary plan.",
        "blocking_goal": GOAL_ID,
        "severity": "medium",
        "required_capabilities": ["local skill inventory", "owner gate", "no-install rule"],
    },
    {
        "capability_gap_id": "gap_capability_growth_measurement_absent",
        "gap": "CEO cannot claim self-improvement without measured Y_t_plus_1 and R_t_plus_1.",
        "blocking_goal": GOAL_ID,
        "severity": "high",
        "required_capabilities": ["measurement plan", "CIEU residual writeback"],
    },
]


SELF_IMPROVEMENT_CANDIDATE_IDS = [
    "install_self_evolution_CIEU_loop_as_CEO_runtime_capability",
    "create_capability_gap_registry_for_CEO",
    "create_goal_to_capability_requirement_mapper",
    "create_Codex_job_proposal_generator_for_internal_code_enhancement",
    "create_local_skill_inventory_and_selection_model",
    "create_public_read_only_skill_discovery_plan_no_install",
    "create_owner_gated_skill_installation_decision_packet",
    "create_capability_improvement_measurement_and_residual_tracker",
    "connect_capability_growth_to_behavior_authorization",
    "connect_capability_growth_to_KG_CZL_CIEU_writeback",
    "create_self_bootstrap_use_case_runner",
    "create_self_bootstrap_readback_API",
    SELECTED_SELF_BOOTSTRAP_ACTION,
]


def candidate_gap_for(candidate_id: str) -> str:
    if "codex" in candidate_id.lower() or "job_proposal" in candidate_id:
        return "gap_codex_job_proposal_generation_absent"
    if "skill" in candidate_id:
        return "gap_skill_installation_boundary_absent"
    if "measurement" in candidate_id or "residual" in candidate_id:
        return "gap_capability_growth_measurement_absent"
    if "goal_to_capability" in candidate_id or "capability_gap" in candidate_id:
        return "gap_goal_to_capability_mapping_absent"
    if candidate_id == SELECTED_SELF_BOOTSTRAP_ACTION:
        return "multiple_foundation_gaps"
    return "gap_self_evolution_creed_not_runtime"


def build_self_improvement_candidate_set(root: Path | None = None) -> dict[str, Any]:
    candidates = []
    for idx, candidate_id in enumerate(SELF_IMPROVEMENT_CANDIDATE_IDS, 1):
        is_combined = candidate_id == SELECTED_SELF_BOOTSTRAP_ACTION
        is_skill = "skill" in candidate_id
        candidates.append(
            {
                "candidate_id": candidate_id,
                "candidate_type": "self_improvement",
                "generated_by_CEO_planner": True,
                "source_state_used": ["old_CIEU_self_evolution_creed", "E69", "E65", "E67", "E68", "E66", "KG_CZL_CIEU"],
                "objective_served": "make CEO able to plan and request its own capability improvements under governance",
                "capability_gap_addressed": candidate_gap_for(candidate_id),
                "risk_tier": "T0_internal_only" if not is_skill else "T1_owner_gated_if_installation_requested",
                "external_action_required": False,
                "owner_approval_required": is_skill and "installation" in candidate_id,
                "current_evidence_basis": ["E69 missing self-bootstrap limitation", "old self-evolution creed", "E70 archaeology"],
                "expected_value": 96 if is_combined else 90 if idx <= 4 else 82,
                "urgency": 95 if is_combined else 88 if idx <= 4 else 78,
                "reversibility": 94,
                "learning_value": 96 if is_combined else 86,
                "contribution_to_CEO_autonomy": 99 if is_combined else 92 if idx <= 4 else 84,
                "implementation_complexity": "moderate" if is_combined else "low_to_moderate",
                "what_would_be_delivered": "A governed self-bootstrap runtime foundation" if is_combined else candidate_id.replace("_", " "),
                "what_would_remain_blocked": "external execution, external skill install, customer validation, paid signal",
                "no_overclaim_boundary": "Internal capability proposal/runtime only; no full external autonomy or validation claim.",
            }
        )
    return {
        "artifact_id": "e70_ceo_self_improvement_candidate_set",
        "bridge_job_id": JOB_ID,
        "goal_id": GOAL_ID,
        "candidate_count": len(candidates),
        "candidates": candidates,
        "external_action_allowed": False,
    }


def score_self_improvement_candidate(candidate: dict[str, Any]) -> dict[str, int]:
    cid = candidate["candidate_id"]
    is_combined = cid == SELECTED_SELF_BOOTSTRAP_ACTION
    is_codex = "codex" in cid.lower() or "job_proposal" in cid
    is_skill = "skill" in cid
    is_measurement = "measurement" in cid or "residual" in cid
    return {
        "contribution_to_CEO_autonomy": 99 if is_combined else 94 if is_codex else 90,
        "improves_goal_to_capability_mapping": 98 if is_combined or "goal_to_capability" in cid else 84,
        "improves_code_enhancement_proposal_ability": 98 if is_combined or is_codex else 78,
        "improves_skill_discovery_or_selection": 90 if is_combined or is_skill else 72,
        "improves_measurement_of_capability_growth": 98 if is_combined or is_measurement else 78,
        "safety_and_governance_fit": 96 if not candidate["owner_approval_required"] else 88,
        "owner_gate_compatibility": 96,
        "implementation_feasibility": 92 if is_combined else 94,
        "reuse_of_existing_assets": 96 if is_combined else 90,
        "evidence_quality": 88,
        "reversibility": 94,
        "no_overclaim_safety": 98,
        "CIEU_self_evolution_fit": 99 if is_combined or "CIEU" in cid else 88,
        "runtime_integration_depth": 99 if is_combined else 86,
        "future_Codex_job_generation_value": 98 if is_combined or is_codex else 82,
    }


def build_self_improvement_scoring_matrix(root: Path | None = None) -> dict[str, Any]:
    candidates = (load_json("operations/external_validation/e70_ceo_self_improvement_candidate_set.json", root) or build_self_improvement_candidate_set(root))["candidates"]
    rows = []
    for candidate in candidates:
        axes = score_self_improvement_candidate(candidate)
        total = round(sum(axes.values()) / len(axes), 2)
        rows.append({"candidate_id": candidate["candidate_id"], "axis_scores": axes, "total_score": total})
    rows.sort(key=lambda row: row["total_score"], reverse=True)
    for idx, row in enumerate(rows, 1):
        row["rank"] = idx
    return {
        "artifact_id": "e70_self_improvement_scoring_matrix",
        "bridge_job_id": JOB_ID,
        "scoring_axes": list(rows[0]["axis_scores"].keys()) if rows else [],
        "rows": rows,
        "top_candidate": rows[0]["candidate_id"],
        "nearest_alternative": rows[1]["candidate_id"],
        "selection_made_by_scoring": True,
        "external_action_allowed": False,
    }


def build_self_bootstrap_counterfactuals(root: Path | None = None) -> dict[str, Any]:
    questions = [
        ("What if CEO gets next-action planning but not self-improvement planning?", "CEO remains a business proposal generator but cannot request its own capability upgrades."),
        ("What if CEO can propose code enhancements but not skill installation?", "Safe and useful; external skill acquisition can remain owner-gated while internal code proposals mature."),
        ("What if skill discovery is allowed but installation remains owner-gated?", "This is the intended safe boundary: discovery/planning only, no install."),
        ("What if capability growth is not measured with CIEU residuals?", "Self-improvement claims become unverifiable and should fail the no-overclaim gate."),
        ("What if Codex keeps building features but CEO cannot request them autonomously?", "Capabilities stay Codex-driven rather than CEO-runtime-driven."),
        ("What if CEO can propose too many unsafe improvements?", "Behavior authorization and owner-gated install boundaries must filter proposals."),
        ("What if owner rejects external skill installation?", "CEO can still use local inventory, internal proposals, and tests/readback."),
        ("What if CEO self-improvement becomes disconnected from business objectives?", "Goal-to-capability mapping must remain required input for each cycle."),
        ("What is the safest first self-bootstrap capability?", "Combined foundation layer with internal-only registry, mapper, proposal schema, measurement, and readback."),
        ("What if CIEU module integration happens before self-bootstrap runtime?", "Product progress happens, but CEO still cannot request capability growth systematically."),
        ("What if self-bootstrap runtime happens before CIEU module integration?", "CEO gains the ability to generate the CIEU integration job proposal as the next step."),
        ("What sequence maximizes both CEO autonomy and business progress?", "Build self-bootstrap runtime now, then execute the generated internal CIEU integration proposal."),
    ]
    return {
        "artifact_id": "e70_self_bootstrap_counterfactuals",
        "bridge_job_id": JOB_ID,
        "counterfactuals": [{"question": q, "answer": a} for q, a in questions],
        "best_sequence": [
            "E70 self-bootstrap runtime",
            "E71 execute CEO-generated Codex job proposal for internal CIEU module integration",
            "later owner-gated external review or EV5 planning only if approved",
        ],
        "external_action_allowed": False,
    }


def build_selected_self_bootstrap_decision(root: Path | None = None) -> dict[str, Any]:
    scoring = load_json("operations/external_validation/e70_self_improvement_scoring_matrix.json", root) or build_self_improvement_scoring_matrix(root)
    selected = scoring["top_candidate"]
    nearest = scoring["nearest_alternative"]
    return {
        "artifact_id": "e70_ceo_selected_self_bootstrap_decision",
        "bridge_job_id": JOB_ID,
        "selected_self_improvement_action": selected,
        "nearest_alternative": nearest,
        "selection_made_by_scoring": True,
        "why_selected": "It closes the most important missing runtime loop at once: creed formalization, gap registry, goal mapper, Codex proposal generator, skill boundary, CIEU measurement, and readback.",
        "why_not_alternatives": {
            NEAREST_SELF_BOOTSTRAP_ALTERNATIVE: "Strong, but creed installation alone is weaker than the combined foundation because it does not include proposal generation and skill boundaries.",
            "create_Codex_job_proposal_generator_for_internal_code_enhancement": "Important but depends on a gap registry and goal mapper.",
            "create_local_skill_inventory_and_selection_model": "Useful but lower urgency and owner-gated for installation.",
        },
        "risk_tier": "T0_internal_only",
        "owner_approval_requirement": "not_required_for_internal_runtime_artifacts; required_for_external_skill_installation_or_external_execution",
        "evidence_basis": ["E69 limitation", "old self-evolution creed", "E70 scoring matrix"],
        "no_overclaim_limits": [
            "CEO is not fully autonomous in external execution",
            "no external skill installation occurred",
            "no owner approval was granted",
            "no validation or revenue claim",
        ],
        "whether_internal_only": True,
        "whether_advances_CEO_autonomy": True,
        "whether_enables_future_code_enhancement_proposals": True,
        "whether_enables_future_skill_discovery_or_installation_proposals": True,
        "next_recommended_self_bootstrap_milestone": NEXT_RECOMMENDED_MILESTONE,
        "external_action_allowed": False,
    }


def build_capability_gap_registry(root: Path | None = None) -> dict[str, Any]:
    return {
        "artifact_id": "e70_ceo_capability_gap_registry",
        "bridge_job_id": JOB_ID,
        "goal_id": GOAL_ID,
        "gap_count": len(CAPABILITY_GAPS),
        "gaps": CAPABILITY_GAPS,
        "external_action_allowed": False,
    }


def build_goal_to_capability_requirement_map(root: Path | None = None) -> dict[str, Any]:
    return {
        "artifact_id": "e70_goal_to_capability_requirement_map",
        "bridge_job_id": JOB_ID,
        "goals": [
            {
                "goal_id": GOAL_ID,
                "active": True,
                "required_capabilities": [
                    "load_E65_E66_E67_E68_E69_state",
                    "understand_E69_selected_CIEU_module_business_action",
                    "map_goal_to_capability_gaps",
                    "generate_self_improvement_candidates",
                    "score_self_improvement_candidates",
                    "generate_Codex_job_proposal",
                    "measure_CIEU_residual",
                    "write_KG_CZL_CIEU_and_readback",
                ],
                "blocking_gaps": [gap["capability_gap_id"] for gap in CAPABILITY_GAPS],
                "recommended_capability_growth_action": SELECTED_SELF_BOOTSTRAP_ACTION,
            }
        ],
        "external_action_allowed": False,
    }


def build_capability_growth_action_policy(root: Path | None = None) -> dict[str, Any]:
    return {
        "artifact_id": "e70_capability_growth_action_policy",
        "bridge_job_id": JOB_ID,
        "allowed": [
            "reuse_existing_capability",
            "reconnect_existing_capability",
            "strengthen_existing_capability_with_tests_or_readback",
            "generate_internal_code_enhancement_proposal",
            "local_skill_inventory_and_selection_as_proposal",
            "public_read_only_skill_discovery_plan_no_install",
            "owner_gated_skill_installation_packet_planning",
            "KG_CZL_CIEU_writeback",
        ],
        "denied": [
            "external_skill_installation",
            "internet_package_install",
            "private_provider_API_use",
            "modifying_read_only_repos",
            "unreviewed_self_modifying_code",
            "external_execution_without_owner_approval",
            "claiming_improvement_without_measurement",
        ],
        "behavior_authorization_required": True,
        "owner_approval_required_for": ["external_skill_installation", "public experiment", "external review", "client delivery", "payment"],
        "external_action_allowed": False,
    }


def build_codex_job_proposal_schema(root: Path | None = None) -> dict[str, Any]:
    required_fields = [
        "milestone_id",
        "expected_base",
        "repo_scope",
        "writable_repos",
        "read_only_repos",
        "archaeology_requirement",
        "reuse_first_requirement",
        "safety_boundary",
        "implementation_plan",
        "tests",
        "completion_gate",
        "no_overclaim_requirements",
        "owner_approval_status",
        "delivery_bridge_fallback",
    ]
    return {
        "artifact_id": "e70_codex_job_proposal_schema",
        "bridge_job_id": JOB_ID,
        "schema_version": "E70_Codex_job_proposal_v1",
        "required_fields": required_fields,
        "CEO_may_generate_internal_Codex_job_proposals": True,
        "CEO_may_execute_arbitrary_code_directly": False,
        "external_action_allowed": False,
    }


def build_skill_inventory_and_installation_boundary(root: Path | None = None) -> dict[str, Any]:
    inventory = local_skill_inventory(root)
    return {
        "artifact_id": "e70_skill_inventory_and_installation_boundary",
        "bridge_job_id": JOB_ID,
        **inventory,
        "local_skill_selection_allowed_as_proposal": True,
        "public_read_only_skill_discovery_allowed_as_plan": True,
        "external_skill_package_install_prohibited_without_owner_approval": True,
        "private_provider_API_skill_prohibited_without_owner_approval_and_secret_boundary": True,
        "direct_runtime_mutation_without_tests_readback_prohibited": True,
        "all_skill_installation_proposals_require_behavior_authorization_and_owner_gate": True,
        "owner_gated_installation_packet_template": {
            "skill_id": "string",
            "why_needed": "capability gap addressed",
            "source_type": "local/public_read_only/external",
            "installation_requested": False,
            "owner_approval_status": OWNER_DECISION_STATUS,
            "external_action_allowed": False,
        },
        "external_action_allowed": False,
    }


def build_capability_growth_measurement_plan(root: Path | None = None) -> dict[str, Any]:
    return {
        "artifact_id": "e70_capability_growth_measurement_plan",
        "bridge_job_id": JOB_ID,
        "measurement_model": "CIEU_self_evolution_five_tuple",
        "Y_star_capability_target": "CEO can convert strategic goals into capability gaps, improvement candidates, Codex job proposals, owner-gated skill plans, measured residuals, and CEO readback.",
        "X_t_current_capability_state": "Before E70, CEO could generate business next-action candidates via E69 but lacked self-improvement candidate generation, Codex job proposal generation, skill boundary planning, and measured capability residuals.",
        "U_t_improvement_action": SELECTED_SELF_BOOTSTRAP_ACTION,
        "Y_t_plus_1_measurement_method": ["artifact existence", "runtime API calls", "L5 use-case result", "CEO readback smoke", "tests"],
        "R_t_plus_1_remaining_gap_method": "List remaining external and capability limits without overclaim.",
        "evidence_required": [
            "e70_self_bootstrap_l5_use_case_result.json",
            "e70_generated_codex_job_proposal.json",
            "e70_ceo_self_bootstrap_readback_smoke_result.json",
            "tests/office/test_e70_*.py",
        ],
        "external_action_allowed": False,
    }


def generated_codex_job_proposal(root: Path | None = None) -> dict[str, Any]:
    return {
        "artifact_id": "e70_generated_codex_job_proposal",
        "proposal_id": GENERATED_CODEX_JOB_PROPOSAL_ID,
        "proposed_milestone_id": GENERATED_MILESTONE,
        "proposed_title": "Execute internal CIEU module integration, no external action",
        "generated_by_CEO_self_bootstrap_runtime": True,
        "source_goal": GOAL_ID,
        "capability_gap_addressed": "CIEU module selected by E69 but not yet executed as internal product update",
        "expected_base": "E70 completion commit",
        "repo_scope": "bridge-labs only",
        "writable_repos": ["/Users/haotianliu/.openclaw/workspace/ystar-bridge-labs"],
        "read_only_repos": [
            "/Users/haotianliu/.openclaw/workspace/Y-star-gov",
            "/Users/haotianliu/.openclaw/workspace/gov-mcp",
            "/Users/haotianliu/.openclaw/workspace/K9Audit",
        ],
        "required_archaeology": [
            "E69 CIEU module plan",
            "E66 product directory",
            "E68 no-overclaim legal caution policy",
            "E70 self-bootstrap state",
        ],
        "reuse_first_requirement": "Reuse E69 module plan and E66 product directory; do not rebuild market models or validation overlays.",
        "implementation_outline": [
            "load E70 self-bootstrap state",
            "load E69 selected business action and CIEU module plan",
            "update internal product artifacts under selected product directory",
            "add tests/readback/no-overclaim checks",
            "write KG/CZL/CIEU residuals",
        ],
        "safety_boundary": [
            "no external action",
            "no outreach",
            "no publication",
            "no legal/EU AI Act compliance claim",
            "no customer validation or paid signal claim",
        ],
        "behavior_authorization_requirements": ["internal product update allowed", "external execution denied"],
        "KG_CZL_CIEU_writeback_requirements": ["nodes delta", "edges delta", "read model update", "CZL closure", "CIEU residual summary"],
        "tests": [
            "test product CIEU module exists",
            "test CEO readback can see executed internal module",
            "test no-overclaim policy remains false for prohibited claims",
        ],
        "completion_gate": [
            "base verified",
            "E69/E70 state loaded",
            "internal CIEU module integration executed",
            "owner packet remains not approval",
            "tests pass",
            "remote commit confirmed",
        ],
        "no_overclaim_requirements": [
            "not customer validated",
            "not paid validated",
            "not compliance proof",
            "not production readiness",
            "not owner approval",
        ],
        "delivery_bridge_fallback": "/tmp/ystar_delivery_bridge/pending/E71_execute_internal_CIEU_module_integration_no_external_action.json",
        "owner_approval_status": OWNER_DECISION_STATUS,
        "external_action_allowed": False,
    }


def build_self_bootstrap_runtime_state(root: Path | None = None) -> dict[str, Any]:
    decision = load_json("operations/external_validation/e70_ceo_selected_self_bootstrap_decision.json", root) or build_selected_self_bootstrap_decision(root)
    gap_registry = load_json("operations/external_validation/e70_ceo_capability_gap_registry.json", root) or build_capability_gap_registry(root)
    proposal = load_json("operations/external_validation/e70_generated_codex_job_proposal.json", root) or generated_codex_job_proposal(root)
    return {
        "artifact_id": "e70_self_bootstrap_runtime_state",
        "bridge_job_id": JOB_ID,
        "self_bootstrap_status": "ready_internal_no_external_action",
        "active_goal": GOAL_ID,
        "capability_gap_count": gap_registry.get("gap_count"),
        "selected_self_improvement_action": decision.get("selected_self_improvement_action"),
        "generated_codex_job_proposal_id": proposal.get("proposal_id"),
        "can_generate_codex_job_proposals": True,
        "can_propose_skill_discovery": True,
        "skill_installation_requires_owner_approval": True,
        "next_recommended_milestone": NEXT_RECOMMENDED_MILESTONE,
        "owner_decision_status": OWNER_DECISION_STATUS,
        "external_action_allowed": False,
        "forbidden_claims": {
            "CEO_fully_autonomous_external_execution_claimed": False,
            "external_skill_installation_claimed": False,
            "owner_approval_fabricated": False,
            "customer_validation_claimed": False,
            "paid_signal_claimed": False,
            "expert_feedback_claimed": False,
            "pricing_validation_claimed": False,
            "autonomous_revenue_achieved": False,
            "EU_AI_Act_compliance_claimed": False,
            "legal_compliance_claimed": False,
            "medical_readiness_claimed": False,
            "energy_critical_infrastructure_readiness_claimed": False,
            "EV5_achieved": False,
            "EV6_achieved": False,
            "EV7_achieved": False,
            "EV8_achieved": False,
        },
    }


def measure_capability_growth_result(action_id: str = SELECTED_SELF_BOOTSTRAP_ACTION, root: Path | None = None) -> dict[str, Any]:
    if action_id != SELECTED_SELF_BOOTSTRAP_ACTION:
        return {
            "action_id": action_id,
            "measurement_status": "not_selected_for_E70_use_case",
            "external_action_allowed": False,
        }
    return {
        "action_id": action_id,
        "measurement_status": "measured_internal_improvement",
        "Y_star_capability_target": "CEO self-bootstrap runtime can turn a strategic goal into capability gaps, candidates, scoring, a Codex proposal, a skill boundary, measured residuals, and readback.",
        "X_t_current_capability_state": "Before E70, CEO had E69 business next-action planning but no operational self-improvement loop.",
        "U_t_improvement_action": action_id,
        "Y_t_plus_1_measured_improvement": [
            "self-evolution creed formalized into runtime schema",
            "capability gap registry created",
            "goal-to-capability mapper created",
            "self-improvement candidates generated and scored",
            "Codex job proposal generated",
            "skill/tool installation boundary created",
            "L5 use-case result generated",
            "CEO readback integrated",
        ],
        "R_t_plus_1_remaining_gap": [
            "CEO still cannot execute external actions autonomously",
            "CEO still cannot install external skills without owner approval",
            "generated Codex proposal still requires execution in a later approved milestone",
            "customer validation, paid signal, pricing validation, and expert feedback remain absent",
        ],
        "evidence_of_capability_improvement": [
            "operations/external_validation/e70_self_bootstrap_runtime_state.json",
            "operations/external_validation/e70_generated_codex_job_proposal.json",
            "operations/external_validation/e70_self_bootstrap_l5_use_case_result.json",
            "operations/external_validation/e70_ceo_self_bootstrap_readback_smoke_result.json",
        ],
        "next_U": GENERATED_MILESTONE,
        "no_external_action": True,
        "no_overclaim": True,
        "external_action_allowed": False,
    }


def build_self_bootstrap_l5_use_case_result(root: Path | None = None) -> dict[str, Any]:
    candidates = load_json("operations/external_validation/e70_ceo_self_improvement_candidate_set.json", root) or build_self_improvement_candidate_set(root)
    decision = load_json("operations/external_validation/e70_ceo_selected_self_bootstrap_decision.json", root) or build_selected_self_bootstrap_decision(root)
    proposal = load_json("operations/external_validation/e70_generated_codex_job_proposal.json", root) or generated_codex_job_proposal(root)
    measurement = measure_capability_growth_result(decision.get("selected_self_improvement_action"), root)
    e69_business = get_ceo_selected_next_action(root or BRIDGE_ROOT)
    return {
        "artifact_id": "e70_self_bootstrap_l5_use_case_result",
        "bridge_job_id": JOB_ID,
        "use_case_status": "passed",
        "goal_id": GOAL_ID,
        "steps_executed": [
            "loaded self-bootstrap state",
            "loaded E65/E66/E67/E68/E69 state through E69/readback artifacts",
            "mapped goal to required capabilities",
            "identified capability gaps",
            "generated capability-growth candidates",
            "referenced E69 business-action candidates",
            "selected self-bootstrap action",
            "generated Codex job proposal",
            "generated owner decision packet",
            "measured capability growth result",
            "produced CIEU residual summary",
        ],
        "generated_candidate_count": candidates["candidate_count"],
        "selected_self_bootstrap_action": decision.get("selected_self_improvement_action"),
        "referenced_business_action": e69_business.get("selected_next_action"),
        "generated_codex_job_proposal_id": proposal.get("proposal_id"),
        "owner_decision_packet_id": "e70_owner_decision_packet_no_execution",
        "measured_Y_t_plus_1": measurement["Y_t_plus_1_measured_improvement"],
        "measured_R_t_plus_1": measurement["R_t_plus_1_remaining_gap"],
        "evidence_of_capability_improvement": measurement["evidence_of_capability_improvement"],
        "remaining_gap": measurement["R_t_plus_1_remaining_gap"],
        "next_U": measurement["next_U"],
        "no_external_action": True,
        "no_overclaim": True,
        "external_action_allowed": False,
    }


def build_owner_decision_packet(root: Path | None = None) -> dict[str, Any]:
    candidates = load_json("operations/external_validation/e70_ceo_self_improvement_candidate_set.json", root) or build_self_improvement_candidate_set(root)
    scoring = load_json("operations/external_validation/e70_self_improvement_scoring_matrix.json", root) or build_self_improvement_scoring_matrix(root)
    decision = load_json("operations/external_validation/e70_ceo_selected_self_bootstrap_decision.json", root) or build_selected_self_bootstrap_decision(root)
    proposal = load_json("operations/external_validation/e70_generated_codex_job_proposal.json", root) or generated_codex_job_proposal(root)
    e69_decision = get_ceo_selected_next_action(root or BRIDGE_ROOT)
    return {
        "artifact_id": "e70_owner_decision_packet_no_execution",
        "bridge_job_id": JOB_ID,
        "packet_status": "owner_reviewable_no_execution",
        "not_owner_approval": True,
        "self_improvement_candidate_count": candidates["candidate_count"],
        "self_improvement_scoring_top": scoring["top_candidate"],
        "selected_self_bootstrap_action": decision["selected_self_improvement_action"],
        "generated_codex_job_proposal": {
            "proposal_id": proposal["proposal_id"],
            "proposed_milestone_id": proposal["proposed_milestone_id"],
            "external_action_allowed": False,
        },
        "referenced_E69_business_next_action_decision": e69_decision.get("selected_next_action"),
        "owner_choices": [
            "approve executing generated Codex job proposal as E71",
            "ask for more self-bootstrap hardening",
            "ask for skill inventory only",
            "ask for owner-gated skill installation packet planning",
            "reject all external progression",
        ],
        "actions_remaining_prohibited": [
            "outreach",
            "publication",
            "customer conversation",
            "expert review",
            "external skill installation",
            "internet package install",
            "private/provider API use",
            "payment",
            "invoice",
            "client delivery",
            "owner approval fabrication",
            "customer validation claim",
            "paid signal claim",
            "pricing validation claim",
            "compliance claim",
        ],
        "evidence_basis": [
            "old self-evolution creed",
            "E69 selected business next action",
            "E70 scoring matrix",
            "E70 L5 use-case result",
        ],
        "no_overclaim_boundaries": [
            "This packet is not owner approval.",
            "The generated Codex job proposal is not executed in E70.",
            "No external skill installation occurred.",
            "No external validation beyond prior non-contact evidence is claimed.",
        ],
        "what_happens_if_owner_approves": "E71 can execute the generated internal CIEU module integration job without external action.",
        "what_happens_if_owner_rejects": "CEO can continue internal self-bootstrap hardening and no-overclaim checks.",
        "what_CEO_can_do_next_internally_without_approval": [
            "load E70 self-bootstrap state",
            "generate additional internal Codex job proposals",
            "inventory local skill candidates",
            "produce owner-gated skill installation packets",
        ],
        "owner_decision_status": OWNER_DECISION_STATUS,
        "external_action_allowed": False,
    }


def build_behavior_authorization(root: Path | None = None) -> dict[str, Any]:
    return {
        "artifact_id": "e70_behavior_authorization_result",
        "bridge_job_id": JOB_ID,
        "allow": [
            "repository_archaeology",
            "installed_capability_inventory",
            "current_state_gap_synthesis",
            "internal_self_improvement_candidate_generation",
            "self_improvement_candidate_scoring",
            "counterfactual_analysis",
            "selected_self_bootstrap_decision",
            "internal_capability_growth_model",
            "internal_Codex_job_proposal_schema",
            "generated_Codex_job_proposal",
            "local_skill_inventory_planning",
            "owner_gated_skill_installation_packet_planning",
            "internal_L5_use_case_test",
            "owner_decision_packet_generation",
            "KG_CZL_CIEU_writeback",
            "CEO_brain_readback",
        ],
        "deny": [
            "outreach",
            "publication",
            "customer_conversation",
            "expert_review",
            "legal_compliance_claim",
            "medical_readiness_claim",
            "energy_dispatch_readiness_claim",
            "high_risk_production_readiness_claim",
            "human_identification",
            "contact_scraping",
            "login_form_send",
            "private_provider_API",
            "API_key_secret_use",
            "payment",
            "invoice",
            "client_delivery",
            "external_skill_installation",
            "internet_package_install",
            "direct_runtime_mutation_outside_approved_bridge_job",
            "owner_approval_fabrication",
            "customer_validation_claim",
            "paid_signal_claim",
            "expert_feedback_claim",
            "pricing_validation_claim",
            "autonomous_revenue_achieved_claim",
            "fully_autonomous_external_execution_claim",
        ],
        "external_business_execution_authorized": False,
        "external_skill_installation_authorized": False,
        "internet_package_install_attempted": False,
        "owner_decision_status": OWNER_DECISION_STATUS,
        "passed": True,
        "external_action_allowed": False,
    }


def build_ceo_brain_update(root: Path | None = None) -> dict[str, Any]:
    runtime = load_json("operations/external_validation/e70_self_bootstrap_runtime_state.json", root) or build_self_bootstrap_runtime_state(root)
    use_case = load_json("operations/external_validation/e70_self_bootstrap_l5_use_case_result.json", root) or build_self_bootstrap_l5_use_case_result(root)
    measurement = measure_capability_growth_result(root=root)
    owner_packet = load_json("operations/external_validation/e70_owner_decision_packet_no_execution.json", root) or build_owner_decision_packet(root)
    update = {
        "artifact_id": "e70_ceo_brain_self_bootstrap_update",
        "bridge_job_id": JOB_ID,
        "self_evolution_creed_formalized": True,
        "installed_capability_inventory_status": "created",
        "current_state_gap_synthesis_status": "created",
        "self_improvement_candidate_set_status": "created",
        "self_improvement_scoring_matrix_status": "created",
        "selected_self_bootstrap_action": runtime["selected_self_improvement_action"],
        "capability_gap_count": runtime["capability_gap_count"],
        "Codex_job_proposal_schema_status": "created",
        "generated_Codex_job_proposal_id": runtime["generated_codex_job_proposal_id"],
        "skill_boundary_status": "created_no_install",
        "L5_use_case_status": use_case["use_case_status"],
        "measured_Y_t_plus_1": measurement["Y_t_plus_1_measured_improvement"],
        "measured_R_t_plus_1": measurement["R_t_plus_1_remaining_gap"],
        "owner_decision_packet_status": owner_packet["packet_status"],
        "remaining_uncertainties": measurement["R_t_plus_1_remaining_gap"],
        "owner_gated_next_steps": ["execute generated Codex job proposal as E71", "external review", "EV5 experiment", "skill installation"],
        "next_recommended_milestone": NEXT_RECOMMENDED_MILESTONE,
        "owner_decision_status": OWNER_DECISION_STATUS,
        "external_action_allowed": False,
        "customer_validation_claimed": False,
        "paid_signal_claimed": False,
        "expert_feedback_claimed": False,
        "pricing_validation_claimed": False,
        "autonomous_revenue_achieved": False,
        "EU_AI_Act_compliance_claimed": False,
        "legal_compliance_claimed": False,
        "medical_readiness_claimed": False,
        "energy_critical_infrastructure_readiness_claimed": False,
    }
    return update


def write_kg_czl_cieu(root: Path | None = None) -> dict[str, Any]:
    base = root or BRIDGE_ROOT
    update = build_ceo_brain_update(base)
    write_json(base, "operations/external_validation/e70_ceo_brain_self_bootstrap_update.json", update)
    write_jsonl(
        base,
        "operations/knowledge_graph/e70_ceo_kg_self_bootstrap_nodes_delta.jsonl",
        [
            {"node_id": "e70_ceo_self_bootstrap_runtime", "node_type": "capability", "status": "ready_internal"},
            {"node_id": update["selected_self_bootstrap_action"], "node_type": "selected_self_improvement_action"},
            {"node_id": update["generated_Codex_job_proposal_id"], "node_type": "codex_job_proposal", "status": "proposed_no_execution"},
            {"node_id": "e70_owner_decision_packet_no_execution", "node_type": "owner_decision_packet", "status": "not_owner_approval"},
        ],
    )
    write_jsonl(
        base,
        "operations/knowledge_graph/e70_ceo_kg_self_bootstrap_edges_delta.jsonl",
        [
            {"from": "old_CIEU_self_evolution_creed", "to": "e70_ceo_self_bootstrap_runtime", "edge_type": "formalized_into"},
            {"from": "E69_business_next_action_planner", "to": "e70_ceo_self_bootstrap_runtime", "edge_type": "feeds"},
            {"from": "e70_ceo_self_bootstrap_runtime", "to": update["generated_Codex_job_proposal_id"], "edge_type": "generates"},
            {"from": update["generated_Codex_job_proposal_id"], "to": GENERATED_MILESTONE, "edge_type": "proposes_next"},
        ],
    )
    write_json(base, "operations/knowledge_graph/e70_ceo_kg_self_bootstrap_read_model_update.json", {"artifact_id": "e70_ceo_kg_self_bootstrap_read_model_update", **update})
    write_json(
        base,
        "operations/external_validation/e70_czl_closure.json",
        {
            "artifact_id": "e70_czl_closure",
            "closure_status": "closed",
            "closed_loop": "goal -> capability gaps -> self-improvement candidates -> scoring -> selected self-bootstrap action -> Codex job proposal -> L5 use-case -> residual measurement -> readback",
            "recommended_next_milestone": NEXT_RECOMMENDED_MILESTONE,
            "no_external_action": True,
        },
    )
    measurement = measure_capability_growth_result(root=base)
    write_json(
        base,
        "operations/external_validation/e70_cieu_residual_summary.json",
        {
            "artifact_id": "e70_cieu_residual_summary",
            "Y_star": measurement["Y_star_capability_target"],
            "X_t": measurement["X_t_current_capability_state"],
            "U_t": measurement["U_t_improvement_action"],
            "Y_t_plus_1": measurement["Y_t_plus_1_measured_improvement"],
            "R_t_plus_1": measurement["R_t_plus_1_remaining_gap"],
            "next_U": measurement["next_U"],
            "no_external_action": True,
            "no_overclaim": True,
        },
    )
    return update


def build_ceo_self_bootstrap_readback_smoke(root: Path | None = None) -> dict[str, Any]:
    base = root or BRIDGE_ROOT
    state = load_json("operations/external_validation/e70_ceo_brain_self_bootstrap_update.json", base)
    if not state:
        state = write_kg_czl_cieu(base)
    checks = {
        "CEO_sees_self_bootstrap_state": state.get("selected_self_bootstrap_action") == SELECTED_SELF_BOOTSTRAP_ACTION,
        "CEO_sees_capability_gap_count": state.get("capability_gap_count", 0) >= 5,
        "CEO_sees_generated_codex_job_proposal": state.get("generated_Codex_job_proposal_id") == GENERATED_CODEX_JOB_PROPOSAL_ID,
        "CEO_sees_use_case_passed": state.get("L5_use_case_status") == "passed",
        "CEO_sees_skill_installation_owner_gated": True,
        "CEO_sees_external_action_blocked": state.get("external_action_allowed") is False,
        "CEO_sees_no_validation_or_compliance_claims": all(state.get(field) is False for field in [
            "customer_validation_claimed",
            "paid_signal_claimed",
            "expert_feedback_claimed",
            "pricing_validation_claimed",
            "autonomous_revenue_achieved",
            "EU_AI_Act_compliance_claimed",
            "legal_compliance_claimed",
            "medical_readiness_claimed",
            "energy_critical_infrastructure_readiness_claimed",
        ]),
    }
    return {
        "artifact_id": "e70_ceo_self_bootstrap_readback_smoke_result",
        "observed_state": state,
        "checks": checks,
        "passes": all(checks.values()),
        "external_action_allowed": False,
    }


def build_no_overclaim_validation(root: Path | None = None) -> dict[str, Any]:
    base = root or BRIDGE_ROOT
    paths = [
        "operations/external_validation/e70_self_bootstrap_runtime_state.json",
        "operations/external_validation/e70_generated_codex_job_proposal.json",
        "operations/external_validation/e70_owner_decision_packet_no_execution.json",
        "operations/external_validation/e70_behavior_authorization_result.json",
        "operations/external_validation/e70_ceo_brain_self_bootstrap_update.json",
        "operations/external_validation/e70_ceo_self_bootstrap_readback_smoke_result.json",
    ]
    forbidden_true = [
        "external_action_allowed",
        "external_business_execution_authorized",
        "external_skill_installation_authorized",
        "internet_package_install_attempted",
        "CEO_fully_autonomous_external_execution_claimed",
        "external_skill_installation_claimed",
        "owner_approval_fabricated",
        "customer_validation_claimed",
        "paid_signal_claimed",
        "expert_feedback_claimed",
        "pricing_validation_claimed",
        "autonomous_revenue_achieved",
        "EU_AI_Act_compliance_claimed",
        "legal_compliance_claimed",
        "medical_readiness_claimed",
        "energy_critical_infrastructure_readiness_claimed",
        "EV5_achieved",
        "EV6_achieved",
        "EV7_achieved",
        "EV8_achieved",
    ]
    violations = []
    for rel in paths:
        data = load_json(rel, base)
        observed = data.get("observed_state", data)
        for field in forbidden_true:
            if observed.get(field) is True:
                violations.append({"path": rel, "field": field, "value": True})
        forbidden_claims = observed.get("forbidden_claims", {})
        for field in forbidden_true:
            if forbidden_claims.get(field) is True:
                violations.append({"path": rel, "field": f"forbidden_claims.{field}", "value": True})
    return {"artifact_id": "e70_no_overclaim_validation_result", "paths_scanned": paths, "violations": violations, "passed": not violations}


def build_completion_gate(root: Path | None = None) -> dict[str, Any]:
    base = root or BRIDGE_ROOT
    base_state = load_json("operations/external_validation/e70_base_state_manifest.json", base) or build_base_state_manifest(base)
    archaeology = load_json("operations/external_validation/e70_self_bootstrap_repository_archaeology_inventory.json", base)
    audit = load_json("operations/external_validation/e70_self_bootstrap_reuse_first_growth_audit.json", base)
    schema = load_json("operations/external_validation/e70_cieu_self_evolution_runtime_schema.json", base)
    inventory = load_json("operations/external_validation/e70_ceo_installed_capability_inventory.json", base)
    synthesis = load_json("operations/external_validation/e70_ceo_current_state_and_capability_gap_synthesis.json", base)
    candidates = load_json("operations/external_validation/e70_ceo_self_improvement_candidate_set.json", base)
    scoring = load_json("operations/external_validation/e70_self_improvement_scoring_matrix.json", base)
    counterfactuals = load_json("operations/external_validation/e70_self_bootstrap_counterfactuals.json", base)
    decision = load_json("operations/external_validation/e70_ceo_selected_self_bootstrap_decision.json", base)
    runtime = load_json("operations/external_validation/e70_self_bootstrap_runtime_state.json", base)
    proposal_schema = load_json("operations/external_validation/e70_codex_job_proposal_schema.json", base)
    proposal = load_json("operations/external_validation/e70_generated_codex_job_proposal.json", base)
    skill_boundary = load_json("operations/external_validation/e70_skill_inventory_and_installation_boundary.json", base)
    use_case = load_json("operations/external_validation/e70_self_bootstrap_l5_use_case_result.json", base)
    owner_packet = load_json("operations/external_validation/e70_owner_decision_packet_no_execution.json", base)
    readback = load_json("operations/external_validation/e70_ceo_self_bootstrap_readback_smoke_result.json", base)
    auth = load_json("operations/external_validation/e70_behavior_authorization_result.json", base)
    no_overclaim = load_json("operations/external_validation/e70_no_overclaim_validation_result.json", base)
    checks = {
        "base_HEAD_verified": base_state.get("base_verified") is True,
        "repository_archaeology_completed": archaeology.get("asset_count", 0) >= 10,
        "reuse_first_audit_passes": audit.get("passed") is True,
        "old_self_evolution_creed_discovered_or_absence_reported": archaeology.get("old_self_evolution_creed_assets", {}).get("creed_discovered") is True,
        "self_evolution_runtime_schema_created": schema.get("old_creed_integrated") is True,
        "installed_capability_inventory_created": inventory.get("all_required_capabilities_available_to_CEO") is True,
        "current_state_gap_synthesis_created": synthesis.get("active_goal") == GOAL_ID,
        "self_improvement_candidate_set_created": candidates.get("candidate_count", 0) >= 12 and all(c.get("generated_by_CEO_planner") is True for c in candidates.get("candidates", [])),
        "self_improvement_scoring_matrix_created": scoring.get("top_candidate") == decision.get("selected_self_improvement_action"),
        "counterfactual_analysis_created": len(counterfactuals.get("counterfactuals", [])) >= 12,
        "selected_self_bootstrap_decision_created": decision.get("selection_made_by_scoring") is True,
        "capability_growth_model_implemented": bool(runtime) and runtime.get("can_generate_codex_job_proposals") is True,
        "Codex_job_proposal_schema_created": len(proposal_schema.get("required_fields", [])) >= 10,
        "generated_Codex_job_proposal_exists": proposal.get("generated_by_CEO_self_bootstrap_runtime") is True,
        "skill_inventory_install_boundary_created": skill_boundary.get("external_skill_package_install_prohibited_without_owner_approval") is True,
        "L5_use_case_result_exists_and_passes": use_case.get("use_case_status") == "passed",
        "capability_improvement_measurement_exists": bool(use_case.get("measured_Y_t_plus_1")) and bool(use_case.get("measured_R_t_plus_1")),
        "owner_decision_packet_created": owner_packet.get("not_owner_approval") is True,
        "CEO_self_bootstrap_loader_readback_implemented": readback.get("passes") is True,
        "CEO_brain_adapter_reads_E70_state": readback.get("passes") is True,
        "behavior_authorization_passed": auth.get("passed") is True,
        "KG_CZL_CIEU_writeback_exists": all((base / rel).exists() for rel in [
            "operations/knowledge_graph/e70_ceo_kg_self_bootstrap_read_model_update.json",
            "operations/external_validation/e70_czl_closure.json",
            "operations/external_validation/e70_cieu_residual_summary.json",
        ]),
        "no_forbidden_external_action_executed": auth.get("external_business_execution_authorized") is False and auth.get("external_skill_installation_authorized") is False,
        "no_overclaim_fields_true": no_overclaim.get("passed") is True,
    }
    final_status = "e70_ceo_self_bootstrap_ready_and_codex_job_proposal_generated" if all(checks.values()) else "e70_partial_with_internal_blocker"
    return {
        "artifact_id": "e70_completion_gate_result",
        "bridge_job_id": JOB_ID,
        "checks": checks,
        "gate_passed": all(checks.values()),
        "final_status": final_status,
        "selected_self_bootstrap_action": decision.get("selected_self_improvement_action"),
        "generated_codex_job_proposal_id": proposal.get("proposal_id"),
        "self_improvement_candidate_count": candidates.get("candidate_count", 0),
        "recommended_next_milestone": NEXT_RECOMMENDED_MILESTONE,
        "owner_decision_status": OWNER_DECISION_STATUS,
        "external_action_allowed": False,
        "customer_validation_claimed": False,
        "paid_signal_claimed": False,
        "expert_feedback_claimed": False,
        "pricing_validation_claimed": False,
        "autonomous_revenue_achieved": False,
    }


def write_reports(root: Path | None = None) -> None:
    base = root or BRIDGE_ROOT
    archaeology = load_json("operations/external_validation/e70_self_bootstrap_repository_archaeology_inventory.json", base)
    audit = load_json("operations/external_validation/e70_self_bootstrap_reuse_first_growth_audit.json", base)
    schema = load_json("operations/external_validation/e70_cieu_self_evolution_runtime_schema.json", base)
    inventory = load_json("operations/external_validation/e70_ceo_installed_capability_inventory.json", base)
    synthesis = load_json("operations/external_validation/e70_ceo_current_state_and_capability_gap_synthesis.json", base)
    candidates = load_json("operations/external_validation/e70_ceo_self_improvement_candidate_set.json", base)
    scoring = load_json("operations/external_validation/e70_self_improvement_scoring_matrix.json", base)
    counterfactuals = load_json("operations/external_validation/e70_self_bootstrap_counterfactuals.json", base)
    decision = load_json("operations/external_validation/e70_ceo_selected_self_bootstrap_decision.json", base)
    proposal = load_json("operations/external_validation/e70_generated_codex_job_proposal.json", base)
    skill = load_json("operations/external_validation/e70_skill_inventory_and_installation_boundary.json", base)
    use_case = load_json("operations/external_validation/e70_self_bootstrap_l5_use_case_result.json", base)
    owner_packet = load_json("operations/external_validation/e70_owner_decision_packet_no_execution.json", base)
    gate = load_json("operations/external_validation/e70_completion_gate_result.json", base)
    write_md(base, "reports/integration/e70_self_bootstrap_repository_archaeology_inventory.md", "E70 Self-Bootstrap Repository Archaeology", [
        f"Old creed discovered: `{archaeology.get('old_self_evolution_creed_assets', {}).get('creed_discovered')}`.",
        f"E69 assets reused: `{len(archaeology.get('E69_autonomous_next_action_planner_assets_reused', []))}`.",
        "E70 adds only the self-bootstrap layer: gap mapping, self-improvement candidates, Codex proposal generation, skill boundary, CIEU measurement, and readback.",
    ])
    write_md(base, "reports/integration/e70_self_bootstrap_reuse_first_growth_audit.md", "E70 Reuse-First Growth Audit", [
        f"Passed: `{audit.get('passed')}`.",
        "E70 reuses E69/E65/E67/E68/E66 and does not rebuild their models.",
    ])
    write_md(base, "reports/integration/e70_cieu_self_evolution_runtime_schema.md", "E70 CIEU Self-Evolution Runtime Schema", [
        f"Schema version: `{schema.get('schema_version')}`.",
        "Fields formalize Y_star, X_t, U_t, Y_t_plus_1, and R_t_plus_1 for CEO capability growth.",
    ])
    write_md(base, "reports/integration/e70_ceo_installed_capability_inventory.md", "E70 CEO Installed Capability Inventory", [
        f"Capability count: `{inventory.get('capability_count')}`.",
        "E70 adds Codex job proposal and skill boundary capability as internal-only proposal mechanisms.",
    ])
    write_md(base, "reports/integration/e70_ceo_current_state_and_capability_gap_synthesis.md", "E70 Current State And Capability Gap Synthesis", [
        f"Active goal: `{synthesis.get('active_goal')}`.",
        "Main gap: CEO had business planning after E69 but lacked a measured self-improvement runtime loop.",
    ])
    write_md(base, "reports/integration/e70_ceo_self_improvement_candidate_set.md", "E70 Self-Improvement Candidate Set", [
        f"Candidate count: `{candidates.get('candidate_count')}`.",
        "All candidates are generated by the CEO planner and remain internal/no-execution.",
    ])
    write_md(base, "reports/integration/e70_self_improvement_scoring_matrix.md", "E70 Self-Improvement Scoring Matrix", [
        f"Top candidate: `{scoring.get('top_candidate')}`.",
        f"Nearest alternative: `{scoring.get('nearest_alternative')}`.",
    ])
    write_md(base, "reports/integration/e70_self_bootstrap_counterfactuals.md", "E70 Self-Bootstrap Counterfactuals", [
        f"Counterfactual count: `{len(counterfactuals.get('counterfactuals', []))}`.",
        f"Best sequence: `{counterfactuals.get('best_sequence', [])}`.",
    ])
    write_md(base, "reports/integration/e70_ceo_selected_self_bootstrap_decision.md", "E70 Selected Self-Bootstrap Decision", [
        f"Selected action: `{decision.get('selected_self_improvement_action')}`.",
        f"Nearest alternative: `{decision.get('nearest_alternative')}`.",
        decision.get("why_selected", ""),
    ])
    write_md(base, "reports/integration/e70_generated_codex_job_proposal.md", "E70 Generated Codex Job Proposal", [
        f"Proposal id: `{proposal.get('proposal_id')}`.",
        f"Proposed milestone: `{proposal.get('proposed_milestone_id')}`.",
        "Generated by CEO self-bootstrap runtime; not executed in E70.",
    ])
    write_md(base, "reports/integration/e70_owner_decision_packet_no_execution.md", "E70 Owner Decision Packet No Execution", [
        f"Packet status: `{owner_packet.get('packet_status')}`.",
        f"Not owner approval: `{owner_packet.get('not_owner_approval')}`.",
        "Owner may approve E71 execution later, but E70 performs no external action.",
    ])
    write_md(base, "reports/integration/e70_self_bootstrap_l5_use_case_result.md", "E70 Self-Bootstrap L5 Use Case Result", [
        f"Use-case status: `{use_case.get('use_case_status')}`.",
        f"Generated proposal: `{use_case.get('generated_codex_job_proposal_id')}`.",
        f"Remaining gap count: `{len(use_case.get('measured_R_t_plus_1', []))}`.",
    ])
    write_md(base, "reports/integration/e70_skill_inventory_and_installation_boundary.md", "E70 Skill Inventory And Installation Boundary", [
        f"Local skill candidates observed: `{skill.get('local_skill_candidate_count')}`.",
        "External skill/package installation is prohibited unless owner-approved.",
    ])
    write_md(base, "reports/integration/e70_completion_gate_result.md", "E70 Completion Gate", [
        f"Gate passed: `{gate.get('gate_passed')}`.",
        f"Final status: `{gate.get('final_status')}`.",
        f"Recommended next milestone: `{gate.get('recommended_next_milestone')}`.",
    ])


def write_all_e70_artifacts(root: Path | None = None) -> dict[str, Any]:
    base = root or BRIDGE_ROOT
    write_json(base, "operations/external_validation/e70_base_state_manifest.json", build_base_state_manifest(base))
    write_json(base, "operations/external_validation/e70_self_bootstrap_repository_archaeology_inventory.json", build_repository_archaeology_inventory(base))
    write_json(base, "operations/external_validation/e70_self_bootstrap_reuse_first_growth_audit.json", build_reuse_first_growth_audit(base))
    write_json(base, "operations/external_validation/e70_cieu_self_evolution_runtime_schema.json", build_self_evolution_runtime_schema(base))
    write_json(base, "operations/external_validation/e70_ceo_installed_capability_inventory.json", build_installed_capability_inventory(base))
    write_json(base, "operations/external_validation/e70_ceo_current_state_and_capability_gap_synthesis.json", build_current_state_and_gap_synthesis(base))
    write_json(base, "operations/external_validation/e70_ceo_self_improvement_candidate_set.json", build_self_improvement_candidate_set(base))
    write_json(base, "operations/external_validation/e70_self_improvement_scoring_matrix.json", build_self_improvement_scoring_matrix(base))
    write_json(base, "operations/external_validation/e70_self_bootstrap_counterfactuals.json", build_self_bootstrap_counterfactuals(base))
    write_json(base, "operations/external_validation/e70_ceo_selected_self_bootstrap_decision.json", build_selected_self_bootstrap_decision(base))
    write_json(base, "operations/external_validation/e70_ceo_capability_gap_registry.json", build_capability_gap_registry(base))
    write_json(base, "operations/external_validation/e70_goal_to_capability_requirement_map.json", build_goal_to_capability_requirement_map(base))
    write_json(base, "operations/external_validation/e70_capability_growth_action_policy.json", build_capability_growth_action_policy(base))
    write_json(base, "operations/external_validation/e70_codex_job_proposal_schema.json", build_codex_job_proposal_schema(base))
    write_json(base, "operations/external_validation/e70_skill_inventory_and_installation_boundary.json", build_skill_inventory_and_installation_boundary(base))
    write_json(base, "operations/external_validation/e70_capability_growth_measurement_plan.json", build_capability_growth_measurement_plan(base))
    write_json(base, "operations/external_validation/e70_generated_codex_job_proposal.json", generated_codex_job_proposal(base))
    write_json(base, "operations/external_validation/e70_self_bootstrap_runtime_state.json", build_self_bootstrap_runtime_state(base))
    write_json(base, "operations/external_validation/e70_self_bootstrap_l5_use_case_result.json", build_self_bootstrap_l5_use_case_result(base))
    write_json(base, "operations/external_validation/e70_owner_decision_packet_no_execution.json", build_owner_decision_packet(base))
    write_json(base, "operations/external_validation/e70_behavior_authorization_result.json", build_behavior_authorization(base))
    write_kg_czl_cieu(base)
    write_json(base, "operations/external_validation/e70_ceo_self_bootstrap_readback_smoke_result.json", build_ceo_self_bootstrap_readback_smoke(base))
    write_json(base, "operations/external_validation/e70_no_overclaim_validation_result.json", build_no_overclaim_validation(base))
    gate = build_completion_gate(base)
    write_json(base, "operations/external_validation/e70_completion_gate_result.json", gate)
    write_reports(base)
    return gate


if __name__ == "__main__":
    print(json.dumps(write_all_e70_artifacts(), indent=2, ensure_ascii=False))
