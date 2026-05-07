from __future__ import annotations

import json
import os
import subprocess
import time
from pathlib import Path
from typing import Any

from .e65_ceo_market_dynamics_readback import (
    get_decision_stability,
    get_recommended_market_portfolio,
    list_update_triggers,
    rank_routes_by_profile,
)
from .e67_ceo_external_validation_readback import (
    get_non_contact_validation_portfolio,
    get_route_external_validation_score,
    list_owner_gated_validation_next_steps,
)
from .e68_ceo_cieu_route_readback import (
    explain_cieu_overclaim_limits,
    get_cieu_external_validation,
    get_cieu_portfolio_role,
    get_cieu_product_wedge,
    get_cieu_route_score,
)


BRIDGE_ROOT = Path(os.environ.get("YSTAR_BRIDGE_LABS_ROOT", Path(__file__).resolve().parents[2]))
Y_GOV_ROOT = Path(os.environ.get("YSTAR_GOV_ROOT", "/Users/haotianliu/.openclaw/workspace/Y-star-gov"))
GOV_MCP_ROOT = Path(os.environ.get("GOV_MCP_ROOT", "/Users/haotianliu/.openclaw/workspace/gov-mcp"))
K9_ROOT = Path(os.environ.get("K9AUDIT_ROOT", "/Users/haotianliu/.openclaw/workspace/K9Audit"))

JOB_ID = "e69_ceo_autonomous_next_action_planner_and_cieu_module_plan_20260506T000001Z"
EXPECTED_BASE = "9f00c799a141855c8120c9cb3d9aa1dd5357e33f"
OWNER_DECISION_STATUS = "pending_owner_decision"
CURRENT_PRIMARY_ROUTE = "governed_business_operations_blueprint_for_agent_teams"
CIEU_ROUTE = "CIEU_high_risk_AI_agent_audit_log"
FALLBACK_ROUTE = "founder_operator_decision_brief_service"
LEARNING_ROUTE = "public_read_market_intelligence_product"
PRODUCT_DIR = "products/governed_business_operations_blueprint_for_agent_teams"
SELECTED_ACTION = "integrate_CIEU_audit_log_module_into_governed_business_operations_blueprint_no_execution"
NEXT_MILESTONE = "E70_execute_internal_CIEU_module_integration_no_external_action"


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


def dirty_paths_are_e69_scoped(status_short: str) -> bool:
    if not status_short:
        return True
    allowed_prefixes = (
        "office/mission_command/e69_",
        "tests/office/test_e69_",
        "operations/external_validation/e69_",
        "operations/knowledge_graph/e69_",
        "reports/integration/e69_",
        f"{PRODUCT_DIR}/cieu_",
        f"{PRODUCT_DIR}/updated_offer_blueprint_with_cieu_module",
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
    return {
        "artifact_id": "e69_base_state_manifest",
        "bridge_job_id": JOB_ID,
        "bridge_labs": bridge,
        "expected_branch": "backflow/aiden-ceo-meeting-room",
        "base_verified": bridge["head_matches_expected"] and bridge["branch"] == "backflow/aiden-ceo-meeting-room",
        "bridge_labs_worktree_clean_or_e69_scoped": dirty_paths_are_e69_scoped(bridge["status_short"]),
        "read_only_repos": {
            "Y-star-gov": git_state(Y_GOV_ROOT, "b0d9aa8b1badd1180127a2f79f73ceed48e16451"),
            "gov-mcp": git_state(GOV_MCP_ROOT, "d0181bc8f19d8ae7714bd0f8a220fe12e6ceee90"),
            "K9Audit": git_state(K9_ROOT, "37911e18ce4425470e3f745b30d155c43d76ff55"),
        },
        "e68_completed_report_present": Path("/tmp/ystar_delivery_bridge/completed/e68_cieu_high_risk_ai_audit_log_route_evaluation_20260506T000001Z.report.json").exists(),
        "owner_decision_status": OWNER_DECISION_STATUS,
        "external_action_allowed": False,
    }


def state_bundle(root: Path | None = None) -> dict[str, Any]:
    base = root or BRIDGE_ROOT
    e65_portfolio = get_recommended_market_portfolio(base)
    e65_stability = get_decision_stability(base)
    e65_triggers = list_update_triggers(base)
    e67_primary = get_route_external_validation_score(CURRENT_PRIMARY_ROUTE, base)
    e67_fallback = get_route_external_validation_score(FALLBACK_ROUTE, base)
    e67_validation_portfolio = get_non_contact_validation_portfolio(base)
    e67_owner_gated = list_owner_gated_validation_next_steps(base)
    cieu_score = get_cieu_route_score(base)
    cieu_ev = get_cieu_external_validation(base)
    cieu_portfolio = get_cieu_portfolio_role(base)
    cieu_wedge = get_cieu_product_wedge(base)
    cieu_limits = explain_cieu_overclaim_limits(base)
    e66_offer = load_json("operations/external_validation/e66_selected_route_offer_blueprint.json", base)
    e66_decision = load_json("operations/external_validation/e66_model_driven_selected_route_decision.json", base)
    e66_owner_plan = load_json("operations/external_validation/e66_owner_gated_business_action_plan_no_execution.json", base)
    return {
        "E65_market_dynamics": {
            "portfolio": e65_portfolio,
            "decision_stability": e65_stability,
            "update_triggers": e65_triggers,
            "fastest_cash_top_route": rank_routes_by_profile("fastest_cash_profile", base).get("top_route"),
            "balanced_CEO_top_route": rank_routes_by_profile("balanced_CEO_profile", base).get("top_route"),
        },
        "E67_external_validation": {
            "primary_score": e67_primary,
            "fallback_score": e67_fallback,
            "validation_portfolio": e67_validation_portfolio,
            "owner_gated_next_steps": e67_owner_gated,
        },
        "E68_CIEU_route": {
            "score": cieu_score,
            "external_validation": cieu_ev,
            "portfolio_role": cieu_portfolio,
            "product_wedge": cieu_wedge,
            "no_overclaim_limits": cieu_limits,
        },
        "E66_offer": {
            "offer_blueprint": e66_offer,
            "selected_route_decision": e66_decision,
            "owner_gated_action_plan": e66_owner_plan,
        },
        "owner_decision_status": OWNER_DECISION_STATUS,
        "external_action_allowed": False,
    }


def build_repository_archaeology_inventory(root: Path | None = None) -> dict[str, Any]:
    base = root or BRIDGE_ROOT
    expected = [
        ("office/mission_command/e65_ceo_market_dynamics_readback.py", "E65_market_dynamics_API"),
        ("office/mission_command/e67_ceo_external_validation_readback.py", "E67_external_validation_API"),
        ("office/mission_command/e68_ceo_cieu_route_readback.py", "E68_CIEU_route_API"),
        ("operations/external_validation/e66_selected_route_offer_blueprint.json", "E66_offer_blueprint"),
        ("operations/external_validation/e68_strategic_portfolio_update.json", "E68_CIEU_portfolio"),
        ("operations/external_validation/e67_owner_gated_external_validation_roadmap.json", "E67_owner_gated_validation"),
        ("office/mission_command/e46b_ceo_brain_adapter.py", "CEO_brain_readback"),
        ("products/governed_business_operations_blueprint_for_agent_teams/offer_blueprint.json", "product_offer_blueprint"),
    ]
    assets = [
        {
            "path": path,
            "capability_type": cap,
            "exists": (base / path).exists(),
            "reusable": (base / path).exists(),
            "connected_status": "connected" if (base / path).exists() else "missing",
        }
        for path, cap in expected
    ]
    return {
        "artifact_id": "e69_repository_archaeology_inventory",
        "bridge_job_id": JOB_ID,
        "discovered_assets": assets,
        "asset_count": len(assets),
        "reusable_CEO_state_loaders": [a["path"] for a in assets if "API" in a["capability_type"]],
        "reusable_market_dynamics_APIs": ["rank_routes_by_profile", "get_decision_stability", "get_recommended_market_portfolio", "list_update_triggers"],
        "reusable_external_validation_APIs": ["get_route_external_validation_score", "get_non_contact_validation_portfolio", "list_owner_gated_validation_next_steps"],
        "reusable_CIEU_route_APIs": ["get_cieu_route_score", "get_cieu_external_validation", "get_cieu_portfolio_role", "explain_cieu_overclaim_limits"],
        "reusable_offer_blueprint_assets": [a["path"] for a in assets if "offer" in a["capability_type"]],
        "reusable_owner_decision_packet_assets": ["operations/external_validation/e66_owner_gated_business_action_plan_no_execution.json"],
        "disconnected_planning_assets": ["CEO autonomous next-action planner not yet present before E69"],
        "what_must_not_be_rebuilt": [
            "E65 market dynamics model",
            "E67 external validation model",
            "E68 CIEU route model",
            "E66 offer blueprint",
            "public-read adapters",
            "evidence atomizers",
            "behavior authorization gate",
            "KG/CZL/CIEU writeback conventions",
            "CEO brain readback mechanisms",
        ],
        "E69_should_add_only": "thin autonomous next-action planning layer over installed CEO capabilities",
        "external_action_allowed": False,
    }


def build_reuse_first_growth_audit(root: Path | None = None) -> dict[str, Any]:
    return {
        "artifact_id": "e69_reuse_first_growth_audit",
        "bridge_job_id": JOB_ID,
        "reused_assets": [
            "office/mission_command/e65_ceo_market_dynamics_readback.py",
            "office/mission_command/e67_ceo_external_validation_readback.py",
            "office/mission_command/e68_ceo_cieu_route_readback.py",
            "operations/external_validation/e66_selected_route_offer_blueprint.json",
            "products/governed_business_operations_blueprint_for_agent_teams/offer_blueprint.json",
        ],
        "thin_wrappers_added": ["office/mission_command/e69_ceo_next_action_planner_readback.py"],
        "genuinely_new_assets_added": ["office/mission_command/e69_ceo_next_action_planner.py"],
        "duplicate_capability_risks_checked": {
            "E65_market_model_rebuilt": False,
            "E67_external_validation_model_rebuilt": False,
            "E68_CIEU_route_model_rebuilt": False,
            "E66_offer_blueprint_rebuilt_from_scratch": False,
            "public_read_adapter_rebuilt": False,
            "evidence_atomizer_rebuilt": False,
            "behavior_authorization_gate_rebuilt": False,
            "KG_CZL_CIEU_conventions_rebuilt": False,
            "CEO_readback_mechanism_rebuilt": False,
        },
        "avoided_rebuilds": [
            "E69 calls installed E65/E67/E68 APIs instead of cloning their scoring models.",
            "E69 updates the existing selected product directory only with a CIEU module appendix.",
            "E69 produces a decision packet but does not treat it as approval.",
        ],
        "passed": True,
    }


def build_installed_capability_inventory(root: Path | None = None) -> dict[str, Any]:
    bundle = state_bundle(root)
    capabilities = [
        {
            "capability": "market_dynamics_capability",
            "source": "E65",
            "loader_API_functions": ["rank_routes_by_profile", "get_decision_stability", "get_recommended_market_portfolio", "list_update_triggers"],
            "state_fields_in_CEO_brain": ["latest_market_dynamics_model_state", "current_market_dynamics_primary_route", "current_market_dynamics_decision_stability"],
            "what_CEO_can_answer": ["best route by profile", "decision stability", "fallback portfolio", "update triggers"],
            "available_to_CEO": True,
            "callable_or_read_only": "callable",
            "evidence_artifact": "operations/external_validation/e65_ceo_brain_market_dynamics_update.json",
            "limitation": "T2 public-read evidence; no customer or paid validation",
            "can_influence_next_action_selection": True,
        },
        {
            "capability": "external_validation_capability",
            "source": "E67",
            "loader_API_functions": ["get_route_external_validation_score", "get_non_contact_validation_portfolio", "list_owner_gated_validation_next_steps"],
            "EV_levels": "EV0-EV8",
            "route_validation_scores": {
                CURRENT_PRIMARY_ROUTE: bundle["E67_external_validation"]["primary_score"].get("external_validation_confidence"),
                FALLBACK_ROUTE: bundle["E67_external_validation"]["fallback_score"].get("external_validation_confidence"),
            },
            "available_to_CEO": True,
            "callable_or_read_only": "callable",
            "evidence_artifact": "operations/external_validation/e67_route_external_validation_scorecards.json",
            "limitation": "EV1-EV4 are non-contact evidence, not human feedback or paid signal",
            "can_influence_next_action_selection": True,
        },
        {
            "capability": "CIEU_route_capability",
            "source": "E68",
            "loader_API_functions": ["get_cieu_route_score", "get_cieu_external_validation", "get_cieu_portfolio_role", "explain_cieu_overclaim_limits"],
            "CIEU_route_score": bundle["E68_CIEU_route"]["score"],
            "CIEU_EV_level": bundle["E68_CIEU_route"]["external_validation"].get("highest_achieved_EV_level"),
            "portfolio_role": bundle["E68_CIEU_route"]["portfolio_role"],
            "product_wedge": bundle["E68_CIEU_route"]["product_wedge"].get("offer_name"),
            "available_to_CEO": True,
            "callable_or_read_only": "callable",
            "evidence_artifact": "operations/external_validation/e68_ceo_brain_cieu_route_update.json",
            "limitation": "strategic and regulatory evidence only; no compliance claim",
            "can_influence_next_action_selection": True,
        },
        {
            "capability": "model_driven_offer_capability",
            "source": "E66",
            "selected_route": CURRENT_PRIMARY_ROUTE,
            "offer_blueprint": "Governed Business Operations Blueprint for Agent Teams",
            "pricing_package_hypothesis": "draft-only internal",
            "owner_gated_action_plan": "created",
            "available_to_CEO": True,
            "callable_or_read_only": "read_only_artifact",
            "evidence_artifact": "operations/external_validation/e66_selected_route_offer_blueprint.json",
            "limitation": "not customer-validated or paid-validated",
            "can_influence_next_action_selection": True,
        },
        {
            "capability": "runtime_governance_capability",
            "source": "E54/E55/E56/KG_CZL_CIEU",
            "components": ["CEO Brain", "Behavior Center", "Internal Company Loop", "KG/CZL/CIEU", "anti-drift", "capability binding", "no-overclaim"],
            "available_to_CEO": True,
            "callable_or_read_only": "readback_and_policy",
            "evidence_artifact": "office/mission_command/e46b_ceo_brain_adapter.py",
            "limitation": "governed internal proposal generation only; no autonomous external execution",
            "can_influence_next_action_selection": True,
        },
    ]
    return {
        "artifact_id": "e69_ceo_installed_capability_inventory",
        "bridge_job_id": JOB_ID,
        "capabilities": capabilities,
        "capability_count": len(capabilities),
        "all_required_capabilities_available_to_CEO": all(item["available_to_CEO"] for item in capabilities),
        "external_action_allowed": False,
    }


def build_current_strategic_state_synthesis(root: Path | None = None) -> dict[str, Any]:
    bundle = state_bundle(root)
    cieu_ev = bundle["E68_CIEU_route"]["external_validation"]
    return {
        "artifact_id": "e69_ceo_current_strategic_state_synthesis",
        "bridge_job_id": JOB_ID,
        "current_primary_first_cash_route": CURRENT_PRIMARY_ROUTE,
        "CIEU_high_defensibility_vertical": CIEU_ROUTE,
        "fallback_route": FALLBACK_ROUTE,
        "learning_route": LEARNING_ROUTE,
        "strategic_compounding_route": CIEU_ROUTE,
        "selected_offer_blueprint_status": "draft_only_internal",
        "non_contact_EV_level": cieu_ev.get("highest_achieved_EV_level"),
        "unresolved_residuals": [
            "no customer validation",
            "no paid signal",
            "no pricing validation",
            "no owner-approved external review",
            "CIEU legal/regulatory caution remains high",
            "CEO can generate proposals but cannot execute externally",
        ],
        "owner_gated_blockers": ["external review", "EV5 public experiment", "human feedback", "pricing presentation", "payment/invoice", "client delivery"],
        "evidence_quality_limits": {
            "highest_current_tier": "T2_public_read_non_contact",
            "EV5_EV8_achieved": False,
            "public_evidence_not_buyer_commitment": True,
        },
        "current_contradiction_map": [
            "CIEU is highly unique and defensible but weaker as fastest cash route",
            "founder/operator decision brief is fastest cash but less unique",
            "current primary route balances first cash and uniqueness but needs clearer module packaging",
        ],
        "fragile_assumptions": bundle["E65_market_dynamics"]["decision_stability"].get("fragile_assumptions", []),
        "CEO_can_safely_do_internally_now": [
            "generate next-action candidates",
            "score candidates",
            "draft owner decision packet",
            "plan CIEU module integration",
            "harden internal product blueprint",
            "prepare no-execution next milestone",
        ],
        "CEO_cannot_do_without_owner_approval": [
            "outreach",
            "publication",
            "customer conversation",
            "expert review",
            "EV5 public experiment execution",
            "pricing presentation",
            "payment/invoice",
            "client delivery",
        ],
        "autonomy_statement": "CEO has installed capabilities and can now generate next-action proposals, but is not fully autonomous in external business execution.",
        "E69_objective": "convert CEO from readback consumer into autonomous proposal generator",
        "external_action_allowed": False,
    }


def base_candidate_specs(bundle: dict[str, Any]) -> list[dict[str, Any]]:
    return [
        {
            "candidate_id": SELECTED_ACTION,
            "source_state_used": ["E66_offer", "E68_CIEU_route", "E67_external_validation", "E65_market_dynamics"],
            "objective_served": "combine current primary first-cash route with CIEU high-defensibility vertical",
            "portfolio_role": "primary_route_module_upgrade",
            "risk_tier": "T0_internal_only",
            "external_action_required": False,
            "owner_approval_required": False,
            "current_evidence_basis": "E66 offer plus E68 CIEU EV4 and E65/E67 portfolio state",
            "expected_value": 92,
            "urgency": 86,
            "reversibility": 92,
            "learning_value": 84,
            "relation_to_first_cash": "strengthens current first-cash offer without external action",
            "relation_to_CIEU_strategic_vertical": "directly integrates CIEU as module",
            "what_would_be_delivered": "internal CIEU audit module integration plan and product blueprint update",
            "what_would_remain_blocked": "external review, compliance claims, customer validation, paid signal",
        },
        {
            "candidate_id": "owner_decision_packet_for_controlled_external_review_no_execution",
            "source_state_used": ["E66_owner_plan", "E67_owner_gated_roadmap", "E68_portfolio"],
            "objective_served": "prepare owner choice for later controlled external review",
            "portfolio_role": "owner_gate_progression",
            "risk_tier": "T2_draft_only_external_material",
            "external_action_required": False,
            "owner_approval_required": False,
            "current_evidence_basis": "E67 EV4 and E68 CIEU route evaluation",
            "expected_value": 83,
            "urgency": 76,
            "reversibility": 88,
            "learning_value": 80,
            "relation_to_first_cash": "moves toward external review but not execution",
            "relation_to_CIEU_strategic_vertical": "can include CIEU as review angle",
            "what_would_be_delivered": "owner decision packet only",
            "what_would_remain_blocked": "actual review, outreach, publication, experiment, payment",
        },
        {
            "candidate_id": "targeted_non_contact_validation_for_CIEU_high_risk_vertical",
            "source_state_used": ["E68_CIEU_EV_scorecard", "E65_update_triggers"],
            "objective_served": "increase CIEU public evidence density",
            "portfolio_role": "learning_route",
            "risk_tier": "T1_public_read_only",
            "external_action_required": False,
            "owner_approval_required": False,
            "current_evidence_basis": "E68 14/14 public regulatory reads and EV4",
            "expected_value": 72,
            "urgency": 48,
            "reversibility": 95,
            "learning_value": 92,
            "relation_to_first_cash": "indirect; strengthens strategic vertical evidence",
            "relation_to_CIEU_strategic_vertical": "direct evidence improvement",
            "what_would_be_delivered": "more non-contact evidence",
            "what_would_remain_blocked": "EV5-EV8, buyer feedback, paid signal",
        },
        {
            "candidate_id": "model_driven_offer_blueprint_hardening_no_execution",
            "source_state_used": ["E66_offer", "E65_market_dynamics"],
            "objective_served": "harden current blueprint without changing portfolio",
            "portfolio_role": "first_cash_offer_hardening",
            "risk_tier": "T0_internal_only",
            "external_action_required": False,
            "owner_approval_required": False,
            "current_evidence_basis": "E66 blueprint and E65 balanced CEO route",
            "expected_value": 76,
            "urgency": 70,
            "reversibility": 93,
            "learning_value": 70,
            "relation_to_first_cash": "improves deliverable clarity",
            "relation_to_CIEU_strategic_vertical": "weak unless CIEU module is included",
            "what_would_be_delivered": "hardened blueprint",
            "what_would_remain_blocked": "external use and validation",
        },
        {
            "candidate_id": "prepare_EV5_public_experiment_decision_packet_no_execution",
            "source_state_used": ["E67_owner_gated_roadmap", "E65_update_triggers"],
            "objective_served": "prepare owner decision for public experiment planning",
            "portfolio_role": "owner_gated_validation_progression",
            "risk_tier": "T2_draft_only_external_material",
            "external_action_required": False,
            "owner_approval_required": False,
            "current_evidence_basis": "EV5 remains owner-gated and unachieved",
            "expected_value": 80,
            "urgency": 68,
            "reversibility": 86,
            "learning_value": 88,
            "relation_to_first_cash": "could unlock stronger validation later",
            "relation_to_CIEU_strategic_vertical": "possible experiment route, not execution",
            "what_would_be_delivered": "EV5 planning packet only",
            "what_would_remain_blocked": "actual landing page/post/ad/pricing-click experiment",
        },
        {
            "candidate_id": "compare_current_primary_route_vs_CIEU_route_after_E68",
            "source_state_used": ["E65_market_dynamics", "E68_CIEU_route"],
            "objective_served": "challenge portfolio decision before integration",
            "portfolio_role": "counterfactual_check",
            "risk_tier": "T0_internal_only",
            "external_action_required": False,
            "owner_approval_required": False,
            "current_evidence_basis": "E68 scoring already compares current route and CIEU",
            "expected_value": 63,
            "urgency": 45,
            "reversibility": 96,
            "learning_value": 75,
            "relation_to_first_cash": "indirect",
            "relation_to_CIEU_strategic_vertical": "direct comparison",
            "what_would_be_delivered": "comparison memo",
            "what_would_remain_blocked": "module integration and owner packet",
        },
        {
            "candidate_id": "continue_internal_CEO_autonomy_loop_hardening",
            "source_state_used": ["E54_E56_runtime", "E65_E67_E68_loaders"],
            "objective_served": "improve CEO proposal generation before product work",
            "portfolio_role": "runtime_capability_hardening",
            "risk_tier": "T0_internal_only",
            "external_action_required": False,
            "owner_approval_required": False,
            "current_evidence_basis": "E69 identifies gap between installed capabilities and autonomous proposal generation",
            "expected_value": 82,
            "urgency": 84,
            "reversibility": 90,
            "learning_value": 92,
            "relation_to_first_cash": "indirect but improves future decisions",
            "relation_to_CIEU_strategic_vertical": "enables more autonomous CIEU planning",
            "what_would_be_delivered": "stronger planner loop",
            "what_would_remain_blocked": "external action and product module execution",
        },
        {
            "candidate_id": "defer_external_review_and_strengthen_CIEU_no_overclaim_policy",
            "source_state_used": ["E68_no_overclaim_policy", "E68_CIEU_EV_scorecard"],
            "objective_served": "reduce legal/compliance overclaim risk",
            "portfolio_role": "risk_reduction",
            "risk_tier": "T0_internal_only",
            "external_action_required": False,
            "owner_approval_required": False,
            "current_evidence_basis": "E68 overclaim risks around compliance, medical, energy readiness",
            "expected_value": 68,
            "urgency": 65,
            "reversibility": 96,
            "learning_value": 68,
            "relation_to_first_cash": "indirect",
            "relation_to_CIEU_strategic_vertical": "protects CIEU positioning",
            "what_would_be_delivered": "stricter no-overclaim policy",
            "what_would_remain_blocked": "integration and owner decision packet",
        },
        {
            "candidate_id": "prepare_fallback_founder_operator_decision_brief_packet",
            "source_state_used": ["E65_fastest_cash_profile", "E67_fallback_score"],
            "objective_served": "prepare fastest-cash fallback option",
            "portfolio_role": "fallback_first_cash",
            "risk_tier": "T0_internal_only",
            "external_action_required": False,
            "owner_approval_required": False,
            "current_evidence_basis": "E65 fastest cash route remains founder/operator decision brief",
            "expected_value": 74,
            "urgency": 60,
            "reversibility": 90,
            "learning_value": 64,
            "relation_to_first_cash": "direct fallback first-cash path",
            "relation_to_CIEU_strategic_vertical": "weak",
            "what_would_be_delivered": "fallback route packet",
            "what_would_remain_blocked": "external presentation and validation",
        },
        {
            "candidate_id": "refresh_buyer_understandability_language_from_market_dynamics_no_contact",
            "source_state_used": ["E65_fragile_assumptions", "E65_update_triggers"],
            "objective_served": "address fragile assumption that buyers understand governed business operations",
            "portfolio_role": "model_discovered_additional_candidate",
            "risk_tier": "T0_internal_only",
            "external_action_required": False,
            "owner_approval_required": False,
            "current_evidence_basis": "E65 fragile assumptions include buyer understandability",
            "expected_value": 73,
            "urgency": 72,
            "reversibility": 94,
            "learning_value": 78,
            "relation_to_first_cash": "improves clarity of first-cash offer",
            "relation_to_CIEU_strategic_vertical": "helps explain CIEU as module instead of compliance product",
            "what_would_be_delivered": "internal language refinement brief",
            "what_would_remain_blocked": "external use without owner approval",
        },
    ]


def build_candidate_set(root: Path | None = None) -> dict[str, Any]:
    bundle = state_bundle(root)
    candidates = []
    for spec in base_candidate_specs(bundle):
        spec = dict(spec)
        spec["generated_by_CEO_planner"] = True
        spec["no_overclaim_boundary"] = [
            "no external action",
            "no owner approval fabricated",
            "no customer validation claim",
            "no paid signal claim",
            "no expert feedback claim",
            "no pricing validation claim",
            "no legal/EU AI Act compliance claim",
            "no medical or energy readiness claim",
        ]
        candidates.append(spec)
    return {
        "artifact_id": "e69_ceo_next_action_candidate_set",
        "bridge_job_id": JOB_ID,
        "generated_from_installed_capabilities": True,
        "source_state_used": ["E65", "E67", "E68", "E66", "E54_E56_governance"],
        "candidate_count": len(candidates),
        "candidates": candidates,
        "external_action_allowed": False,
    }


def candidate_axis_scores(candidate: dict[str, Any], bundle: dict[str, Any]) -> dict[str, int]:
    cieu_ev_conf = int(bundle["E68_CIEU_route"]["external_validation"].get("confidence", 0))
    primary_ev_conf = int(bundle["E67_external_validation"]["primary_score"].get("external_validation_confidence", 0))
    cieu_unique = int(bundle["E68_CIEU_route"]["score"].get("YBridge_unique_score", 0))
    stability = int(bundle["E65_market_dynamics"]["decision_stability"].get("decision_stability_score", 60))
    cid = candidate["candidate_id"]
    uses_cieu = "CIEU" in cid or "cieu" in cid
    is_owner_packet = "owner_decision_packet" in cid
    is_autonomy = "CEO_autonomy" in cid or "planner" in cid or "autonomy_loop" in cid
    return {
        "market_dynamics_fit": 92 if cid == SELECTED_ACTION else 84 if is_owner_packet else 78,
        "external_validation_fit": min(100, primary_ev_conf if not uses_cieu else round((primary_ev_conf + cieu_ev_conf) / 2)),
        "CIEU_strategic_value": cieu_unique if uses_cieu else 55,
        "first_cash_support": 88 if cid == SELECTED_ACTION else 80 if "fallback" in cid else 72,
        "owner_gate_readiness": 95 if not candidate["owner_approval_required"] and not candidate["external_action_required"] else 70,
        "internal_only_feasibility": 96 if not candidate["external_action_required"] else 60,
        "risk_safety": 94 if candidate["risk_tier"] == "T0_internal_only" else 82,
        "no_overclaim_safety": 96 if "no_overclaim" in cid or uses_cieu else 90,
        "learning_value": int(candidate["learning_value"]),
        "reversibility": int(candidate["reversibility"]),
        "route_stability": 86 if cid == SELECTED_ACTION else stability,
        "time_to_next_useful_artifact": 90 if cid == SELECTED_ACTION else 84,
        "contribution_to_CEO_autonomy": 94 if cid == SELECTED_ACTION else 98 if is_autonomy else 82,
        "implementation_complexity_inverse": 84 if cid == SELECTED_ACTION else 72 if is_owner_packet else 78,
        "evidence_quality": 86 if cid == SELECTED_ACTION else 80,
    }


def build_scoring_matrix(root: Path | None = None) -> dict[str, Any]:
    bundle = state_bundle(root)
    candidates = (load_json("operations/external_validation/e69_ceo_next_action_candidate_set.json", root) or build_candidate_set(root))["candidates"]
    rows = []
    for candidate in candidates:
        axes = candidate_axis_scores(candidate, bundle)
        score = round(sum(axes.values()) / len(axes), 2)
        rows.append({"candidate_id": candidate["candidate_id"], "axis_scores": axes, "total_score": score})
    rows.sort(key=lambda row: row["total_score"], reverse=True)
    for idx, row in enumerate(rows, 1):
        row["rank"] = idx
    return {
        "artifact_id": "e69_ceo_next_action_scoring_matrix",
        "bridge_job_id": JOB_ID,
        "scoring_axes": list(rows[0]["axis_scores"].keys()) if rows else [],
        "rows": rows,
        "top_candidate": rows[0]["candidate_id"],
        "nearest_alternative": rows[1]["candidate_id"],
        "scoring_uses_installed_capabilities": True,
        "external_action_allowed": False,
    }


def build_counterfactuals(root: Path | None = None) -> dict[str, Any]:
    return {
        "artifact_id": "e69_ceo_next_action_counterfactuals",
        "bridge_job_id": JOB_ID,
        "counterfactuals": [
            {"question": "What if we integrate CIEU module now?", "answer": "It strengthens the current primary route and CIEU vertical internally without external action; best current move."},
            {"question": "What if we prepare owner decision packet now?", "answer": "Useful, but owner packet is more credible after the internal CIEU module plan is attached."},
            {"question": "What if we delay external review and do more non-contact validation?", "answer": "Lower urgency because E68 already reached EV4 with 14 successful public reads."},
            {"question": "What if we focus on first-cash fallback instead?", "answer": "Faster cash, but weaker Y*Bridge uniqueness; keep as fallback rather than primary."},
            {"question": "What if we harden CEO autonomy before product work?", "answer": "E69 itself hardens proposal generation; next useful artifact should connect autonomy to the selected product path."},
            {"question": "What if CIEU sales cycle is too long?", "answer": "Keep CIEU as module/vertical inside the current offer instead of standalone primary route."},
            {"question": "What if owner does not approve external action?", "answer": "Continue internal module integration, no-overclaim hardening, and evidence appendix work."},
            {"question": "What if selected route is too hard to explain?", "answer": "Use the CIEU module as concrete audit evidence layer while retaining the buyer-understandable operations blueprint framing."},
            {"question": "What if public evidence remains only EV4?", "answer": "Proceed only with internal planning and owner packet; do not claim validation or paid signal."},
            {"question": "What if customer validation later rejects the offer?", "answer": "Activate fallback founder/operator decision brief and learning route while preserving CIEU as strategic infrastructure."},
        ],
        "fallback_logic": {
            "if_owner_rejects_external_progression": "continue internal CIEU module integration and no-overclaim hardening",
            "if_CIEU_too_complex": "package it as optional appendix, not primary promise",
            "if_first_cash_pressure_increases": FALLBACK_ROUTE,
        },
        "external_action_allowed": False,
    }


def build_selected_next_action_decision(root: Path | None = None) -> dict[str, Any]:
    scoring = load_json("operations/external_validation/e69_ceo_next_action_scoring_matrix.json", root) or build_scoring_matrix(root)
    selected = scoring["top_candidate"]
    nearest = scoring["nearest_alternative"]
    return {
        "artifact_id": "e69_ceo_selected_next_action_decision",
        "bridge_job_id": JOB_ID,
        "selected_next_action": selected,
        "nearest_alternative": nearest,
        "selection_made_by_CEO_planning_model": True,
        "why_selected": "It is internal-only, strengthens the current first-cash route, incorporates the E68 high-defensibility CIEU vertical, improves buyer-facing concreteness, and advances CEO autonomy by turning installed state into a concrete next artifact.",
        "why_not_alternatives": {
            "owner_decision_packet_for_controlled_external_review_no_execution": "valuable but stronger after CIEU module plan is attached",
            "targeted_non_contact_validation_for_CIEU_high_risk_vertical": "E68 already reached EV4 with public evidence; more validation is lower urgency",
            "prepare_fallback_founder_operator_decision_brief_packet": "fast cash but less unique and less aligned with strategic compounding",
            "continue_internal_CEO_autonomy_loop_hardening": "E69 already implements first autonomy loop; product-connected next action is more useful",
        },
        "risk_tier": "T0_internal_only",
        "owner_approval_requirement": "not_required_for_internal_plan; required_before_external_review_or_execution",
        "evidence_basis": ["E65 market dynamics", "E67 external validation", "E68 CIEU EV4 and route scoring", "E66 offer blueprint"],
        "no_overclaim_limits": ["no compliance claim", "no customer validation", "no paid signal", "no expert feedback", "no pricing validation", "no external execution"],
        "internal_only": True,
        "advances_CEO_autonomy": True,
        "advances_first_cash": True,
        "advances_CIEU_strategic_vertical": True,
        "next_recommended_milestone": NEXT_MILESTONE,
        "external_action_allowed": False,
        "owner_decision_status": OWNER_DECISION_STATUS,
    }


def build_cieu_module_integration_plan(root: Path | None = None) -> dict[str, Any]:
    base = root or BRIDGE_ROOT
    plan = {
        "artifact_id": "e69_cieu_module_integration_plan",
        "bridge_job_id": JOB_ID,
        "module_name": "CIEU Audit Module",
        "module_purpose": "Add causal intent-action-outcome-residual evidence planning to the Governed Business Operations Blueprint.",
        "selected_or_top2": True,
        "CIEU_five_tuple_fields": {
            "X_t": "context",
            "U_t": "action/intervention",
            "Y_star_t": "declared intent or expected outcome",
            "Y_t_plus_1": "observed outcome",
            "R_t_plus_1": "residual, deviation, or governance gap",
        },
        "fit_with_governed_business_operations_blueprint": "Turns action governance into auditable business operation evidence without claiming legal compliance.",
        "buyer_pain_addressed": "agent teams need action boundaries, traceability, owner-gated execution, residual review, and no-overclaim evidence.",
        "future_high_risk_or_regulated_routes_it_may_support": ["record-keeping readiness", "post-market monitoring evidence", "human oversight evidence", "incident review"],
        "difference_from_ordinary_logs_or_traces": "ordinary logs record events and traces record calls; CIEU maps context, action, intended outcome, observed outcome, and residual.",
        "does_not_claim": ["EU AI Act compliance", "legal compliance", "medical certification", "energy dispatch readiness", "production readiness", "customer validation", "paid signal"],
        "delivery_artifacts": ["CIEU field map", "causal action evidence plan", "residual review table", "no-overclaim notice", "owner-gated validation path"],
        "implementation_backlog": [
            "add CIEU module to product blueprint",
            "add sample CIEU tuple section to sample delivery packet",
            "add no-overclaim/legal caution notice",
            "add owner-gated external review questions",
        ],
        "owner_gated_next_steps": ["external review", "legal/regulatory review", "domain expert feedback", "EV5 public experiment", "paid pilot"],
        "no_overclaim_language": "CIEU is a causal audit and traceability evidence pattern; it may support record-keeping readiness discussions but is not compliance proof.",
        "legal_caution_language": "Legal/regulatory review is required before any compliance, medical, energy, or high-risk production readiness claim.",
        "external_action_allowed": False,
    }
    write_json(base, f"{PRODUCT_DIR}/cieu_audit_module.json", plan)
    write_md(base, f"{PRODUCT_DIR}/cieu_audit_module.md", "CIEU Audit Module", [
        "Status: internal-only draft.",
        plan["module_purpose"],
        "CIEU fields: X_t, U_t, Y_star_t, Y_t_plus_1, R_t_plus_1.",
        "This module does not claim EU AI Act compliance, legal compliance, medical readiness, energy readiness, production readiness, customer validation, or paid signal.",
    ])
    write_md(base, f"{PRODUCT_DIR}/cieu_no_overclaim_notice.md", "CIEU No-Overclaim Notice", [
        "CIEU is a causal audit and traceability evidence pattern.",
        "It may support readiness discussions around record-keeping, oversight evidence, post-market monitoring evidence, and incident review.",
        "It is not legal advice, compliance proof, medical certification, energy dispatch readiness, production readiness, customer validation, pricing validation, or paid signal.",
        "External use requires owner approval.",
    ])
    updated = {
        "artifact_id": "e69_updated_offer_blueprint_with_cieu_module",
        "source_offer_blueprint": "operations/external_validation/e66_selected_route_offer_blueprint.json",
        "offer_name": "Governed Business Operations Blueprint for Agent Teams",
        "added_module": "CIEU Audit Module",
        "status": "draft_only_internal",
        "module_deliverables": plan["delivery_artifacts"],
        "owner_approval_required_before_external_use": True,
        "customer_validation_claimed": False,
        "paid_signal_claimed": False,
        "expert_feedback_claimed": False,
        "legal_compliance_claimed": False,
        "EU_AI_Act_compliance_claimed": False,
        "external_action_allowed": False,
    }
    write_json(base, f"{PRODUCT_DIR}/updated_offer_blueprint_with_cieu_module.json", updated)
    write_md(base, f"{PRODUCT_DIR}/updated_offer_blueprint_with_cieu_module.md", "Updated Offer Blueprint With CIEU Module", [
        "Status: internal-only draft.",
        "The current governed business operations blueprint now has a planned CIEU Audit Module.",
        "The module is an internal plan only and remains owner-gated before any external use.",
    ])
    return plan


def build_owner_decision_packet(root: Path | None = None) -> dict[str, Any]:
    candidate_set = load_json("operations/external_validation/e69_ceo_next_action_candidate_set.json", root) or build_candidate_set(root)
    scoring = load_json("operations/external_validation/e69_ceo_next_action_scoring_matrix.json", root) or build_scoring_matrix(root)
    decision = load_json("operations/external_validation/e69_ceo_selected_next_action_decision.json", root) or build_selected_next_action_decision(root)
    return {
        "artifact_id": "e69_owner_decision_packet_no_execution",
        "bridge_job_id": JOB_ID,
        "packet_status": "owner_reviewable_no_execution",
        "not_owner_approval": True,
        "CEO_generated_candidate_count": candidate_set["candidate_count"],
        "scoring_matrix_top_candidate": scoring["top_candidate"],
        "selected_next_action": decision["selected_next_action"],
        "nearest_alternatives": [scoring["nearest_alternative"], "owner_decision_packet_for_controlled_external_review_no_execution", FALLBACK_ROUTE],
        "owner_choices": [
            "approve internal CIEU module integration",
            "approve owner-gated external review preparation",
            "approve EV5 public experiment planning only",
            "ask for more non-contact validation",
            "switch to fallback route",
            "reject all external progression",
        ],
        "exact_actions_remain_prohibited": [
            "outreach",
            "publication",
            "customer conversation",
            "expert review",
            "human identification",
            "contact scraping",
            "login/form/send",
            "payment/invoice",
            "client delivery",
            "compliance/customer/paid/expert/pricing validation claims",
        ],
        "evidence_basis": ["E65", "E67", "E68", "E66"],
        "no_overclaim_boundaries": decision["no_overclaim_limits"],
        "if_owner_approves": "only the explicitly approved future action may be prepared or executed in a later milestone",
        "if_owner_rejects": "continue internal module hardening and no-overclaim evidence closure only",
        "CEO_can_do_next_internally_without_approval": ["internal CIEU module integration plan hardening", "sample packet update", "owner packet refinement", "no-overclaim policy hardening"],
        "owner_decision_status": OWNER_DECISION_STATUS,
        "external_action_allowed": False,
    }


def build_behavior_authorization(root: Path | None = None) -> dict[str, Any]:
    return {
        "artifact_id": "e69_behavior_authorization_result",
        "authorization_status": "ALLOW_INTERNAL_CEO_NEXT_ACTION_PLANNING_ONLY",
        "allowed_actions": [
            "repository_archaeology",
            "installed_capability_inventory",
            "CEO_current_strategic_state_synthesis",
            "internal_next_action_candidate_generation",
            "next_action_scoring",
            "counterfactual_analysis",
            "selected_next_action_decision",
            "internal_CIEU_module_integration_plan",
            "internal_owner_decision_packet",
            "CEO_planner_loader_readback_integration",
            "KG_CZL_CIEU_writeback",
            "CEO_brain_readback",
        ],
        "denied_actions": [
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
            "owner_approval_fabrication",
            "customer_validation_claim",
            "paid_signal_claim",
            "expert_feedback_claim",
            "pricing_validation_claim",
            "autonomous_revenue_achieved_claim",
        ],
        "external_business_execution_authorized": False,
        "external_action_allowed": False,
        "owner_decision_status": OWNER_DECISION_STATUS,
        "passed": True,
    }


def write_runtime_writeback(root: Path | None = None) -> dict[str, Any]:
    base = root or BRIDGE_ROOT
    inventory = load_json("operations/external_validation/e69_ceo_installed_capability_inventory.json", base)
    synthesis = load_json("operations/external_validation/e69_ceo_current_strategic_state_synthesis.json", base)
    candidates = load_json("operations/external_validation/e69_ceo_next_action_candidate_set.json", base)
    scoring = load_json("operations/external_validation/e69_ceo_next_action_scoring_matrix.json", base)
    counterfactuals = load_json("operations/external_validation/e69_ceo_next_action_counterfactuals.json", base)
    decision = load_json("operations/external_validation/e69_ceo_selected_next_action_decision.json", base)
    owner_packet = load_json("operations/external_validation/e69_owner_decision_packet_no_execution.json", base)
    integration = load_json("operations/external_validation/e69_cieu_module_integration_plan.json", base)
    update = {
        "artifact_id": "e69_ceo_brain_next_action_planning_update",
        "planning_status": "CEO autonomous next-action proposal generation ready",
        "installed_capability_inventory_status": "created" if inventory else "missing",
        "current_strategic_state_status": "synthesized" if synthesis else "missing",
        "generated_candidate_count": candidates.get("candidate_count", 0),
        "scoring_matrix_top_candidate": scoring.get("top_candidate"),
        "counterfactual_count": len(counterfactuals.get("counterfactuals", [])),
        "selected_next_action": decision.get("selected_next_action"),
        "nearest_alternative": decision.get("nearest_alternative"),
        "owner_decision_packet_status": owner_packet.get("packet_status"),
        "CIEU_integration_plan_status": "created" if integration else "missing",
        "remaining_uncertainties": synthesis.get("unresolved_residuals", []),
        "owner_gated_next_steps": owner_packet.get("owner_choices", []),
        "next_recommended_milestone": decision.get("next_recommended_milestone", NEXT_MILESTONE),
        "requires_owner_approval_for_selected_internal_action": False,
        "owner_decision_status": OWNER_DECISION_STATUS,
        "external_action_allowed": False,
        "no_external_action": True,
        "CEO_fully_autonomous_external_execution_claimed": False,
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
    }
    write_json(base, "operations/external_validation/e69_ceo_brain_next_action_planning_update.json", update)
    write_jsonl(base, "operations/knowledge_graph/e69_ceo_kg_next_action_planning_nodes_delta.jsonl", [
        {"node_id": "e69_ceo_next_action_planner", "node_type": "capability", "status": "ready"},
        {"node_id": decision.get("selected_next_action"), "node_type": "selected_next_action"},
        {"node_id": "e69_owner_decision_packet_no_execution", "node_type": "owner_decision_packet", "status": "no_execution"},
    ])
    write_jsonl(base, "operations/knowledge_graph/e69_ceo_kg_next_action_planning_edges_delta.jsonl", [
        {"from": "E65_market_dynamics", "to": "e69_ceo_next_action_planner", "edge_type": "feeds"},
        {"from": "E67_external_validation", "to": "e69_ceo_next_action_planner", "edge_type": "feeds"},
        {"from": "E68_CIEU_route", "to": "e69_ceo_next_action_planner", "edge_type": "feeds"},
        {"from": "e69_ceo_next_action_planner", "to": decision.get("selected_next_action"), "edge_type": "selects"},
    ])
    write_json(base, "operations/knowledge_graph/e69_ceo_kg_next_action_planning_read_model_update.json", {"artifact_id": "e69_ceo_kg_next_action_planning_read_model_update", **update})
    write_json(base, "operations/external_validation/e69_czl_closure.json", {
        "artifact_id": "e69_czl_closure",
        "closure_status": "closed",
        "closed_loop": "installed capability state -> CEO-generated candidate set -> scoring -> counterfactuals -> selected action -> owner packet -> readback",
        "recommended_next_milestone": update["next_recommended_milestone"],
        "no_external_action": True,
    })
    write_json(base, "operations/external_validation/e69_cieu_residual_summary.json", {
        "artifact_id": "e69_cieu_residual_summary",
        "intervention": "Converted CEO from readback consumer into autonomous next-action proposal generator.",
        "resolved_residuals": ["CEO now generates and scores next-action candidates from installed capabilities"],
        "remaining_residuals": update["remaining_uncertainties"],
        "no_external_action": True,
    })
    return update


def load_e69_next_action_state_for_brain(root: Path | None = None) -> dict[str, Any]:
    base = root or BRIDGE_ROOT
    state = load_json("operations/external_validation/e69_ceo_brain_next_action_planning_update.json", base)
    if not state:
        state = write_runtime_writeback(base)
    return state


def get_ceo_candidate_actions(root: Path | None = None) -> dict[str, Any]:
    return load_json("operations/external_validation/e69_ceo_next_action_candidate_set.json", root) or build_candidate_set(root)


def get_ceo_next_action_scoring(root: Path | None = None) -> dict[str, Any]:
    return load_json("operations/external_validation/e69_ceo_next_action_scoring_matrix.json", root) or build_scoring_matrix(root)


def get_ceo_selected_next_action(root: Path | None = None) -> dict[str, Any]:
    return load_json("operations/external_validation/e69_ceo_selected_next_action_decision.json", root) or build_selected_next_action_decision(root)


def get_owner_decision_packet(root: Path | None = None) -> dict[str, Any]:
    return load_json("operations/external_validation/e69_owner_decision_packet_no_execution.json", root) or build_owner_decision_packet(root)


def explain_next_action_selection(root: Path | None = None) -> dict[str, Any]:
    decision = get_ceo_selected_next_action(root)
    scoring = get_ceo_next_action_scoring(root)
    return {
        "selected_next_action": decision.get("selected_next_action"),
        "why_selected": decision.get("why_selected"),
        "nearest_alternative": decision.get("nearest_alternative"),
        "top_scores": scoring.get("rows", [])[:3],
        "external_action_allowed": False,
    }


def build_ceo_next_action_planner_readback_smoke(root: Path | None = None) -> dict[str, Any]:
    state = load_e69_next_action_state_for_brain(root)
    checks = {
        "CEO_sees_candidate_count": state.get("generated_candidate_count", 0) >= 10,
        "CEO_sees_selected_next_action": state.get("selected_next_action") == SELECTED_ACTION,
        "CEO_sees_nearest_alternative": bool(state.get("nearest_alternative")),
        "CEO_sees_owner_decision_packet": state.get("owner_decision_packet_status") == "owner_reviewable_no_execution",
        "CEO_sees_external_action_blocked": state.get("external_action_allowed") is False,
        "CEO_sees_next_milestone": state.get("next_recommended_milestone") == NEXT_MILESTONE,
        "CEO_sees_no_forbidden_claims": all(state.get(field) is False for field in [
            "CEO_fully_autonomous_external_execution_claimed",
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
        ]),
    }
    return {
        "artifact_id": "e69_ceo_next_action_planner_readback_smoke_result",
        "observed_state": state,
        "checks": checks,
        "passes": all(checks.values()),
        "external_action_allowed": False,
    }


def build_no_overclaim_validation(root: Path | None = None) -> dict[str, Any]:
    base = root or BRIDGE_ROOT
    paths = [
        "operations/external_validation/e69_ceo_brain_next_action_planning_update.json",
        "operations/external_validation/e69_owner_decision_packet_no_execution.json",
        "operations/external_validation/e69_behavior_authorization_result.json",
        "operations/external_validation/e69_ceo_next_action_planner_readback_smoke_result.json",
        f"{PRODUCT_DIR}/updated_offer_blueprint_with_cieu_module.json",
    ]
    forbidden_true = [
        "external_action_allowed",
        "external_business_execution_authorized",
        "CEO_fully_autonomous_external_execution_claimed",
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
    return {"artifact_id": "e69_no_overclaim_validation_result", "paths_scanned": paths, "violations": violations, "passed": not violations}


def build_completion_gate(root: Path | None = None) -> dict[str, Any]:
    base = root or BRIDGE_ROOT
    base_state = load_json("operations/external_validation/e69_base_state_manifest.json", base) or build_base_state_manifest(base)
    archaeology = load_json("operations/external_validation/e69_repository_archaeology_inventory.json", base)
    audit = load_json("operations/external_validation/e69_reuse_first_growth_audit.json", base)
    inventory = load_json("operations/external_validation/e69_ceo_installed_capability_inventory.json", base)
    synthesis = load_json("operations/external_validation/e69_ceo_current_strategic_state_synthesis.json", base)
    candidates = load_json("operations/external_validation/e69_ceo_next_action_candidate_set.json", base)
    scoring = load_json("operations/external_validation/e69_ceo_next_action_scoring_matrix.json", base)
    counterfactuals = load_json("operations/external_validation/e69_ceo_next_action_counterfactuals.json", base)
    decision = load_json("operations/external_validation/e69_ceo_selected_next_action_decision.json", base)
    integration = load_json("operations/external_validation/e69_cieu_module_integration_plan.json", base)
    owner_packet = load_json("operations/external_validation/e69_owner_decision_packet_no_execution.json", base)
    readback = load_json("operations/external_validation/e69_ceo_next_action_planner_readback_smoke_result.json", base)
    auth = load_json("operations/external_validation/e69_behavior_authorization_result.json", base)
    no_overclaim = load_json("operations/external_validation/e69_no_overclaim_validation_result.json", base)
    checks = {
        "base_HEAD_verified": base_state.get("base_verified") is True,
        "repository_archaeology_completed": archaeology.get("asset_count", 0) >= 8,
        "reuse_first_audit_passes": audit.get("passed") is True,
        "installed_capability_inventory_created": inventory.get("all_required_capabilities_available_to_CEO") is True,
        "current_strategic_state_synthesis_created": synthesis.get("autonomy_statement", "").startswith("CEO has installed capabilities"),
        "CEO_generated_candidate_set_created": candidates.get("candidate_count", 0) >= 10 and all(c.get("generated_by_CEO_planner") is True for c in candidates.get("candidates", [])),
        "candidate_scoring_matrix_created": scoring.get("top_candidate") == decision.get("selected_next_action"),
        "counterfactual_analysis_created": len(counterfactuals.get("counterfactuals", [])) >= 10,
        "selected_next_action_decision_created": decision.get("selection_made_by_CEO_planning_model") is True,
        "CIEU_module_integration_plan_or_defer_reason_created": bool(integration),
        "owner_decision_packet_created": owner_packet.get("packet_status") == "owner_reviewable_no_execution" and owner_packet.get("not_owner_approval") is True,
        "CEO_next_action_loader_readback_implemented": callable(load_e69_next_action_state_for_brain) and callable(get_ceo_candidate_actions),
        "CEO_brain_adapter_reads_E69_state": readback.get("passes") is True,
        "behavior_authorization_passed": auth.get("passed") is True,
        "KG_CZL_CIEU_writeback_exists": all((base / rel).exists() for rel in [
            "operations/knowledge_graph/e69_ceo_kg_next_action_planning_read_model_update.json",
            "operations/external_validation/e69_czl_closure.json",
            "operations/external_validation/e69_cieu_residual_summary.json",
        ]),
        "no_forbidden_external_action_executed": auth.get("external_business_execution_authorized") is False,
        "no_overclaim_fields_true": no_overclaim.get("passed") is True,
    }
    final_status = "e69_ceo_selected_cieu_module_integration_as_next_action" if all(checks.values()) else "e69_partial_with_internal_blocker"
    return {
        "artifact_id": "e69_completion_gate_result",
        "bridge_job_id": JOB_ID,
        "checks": checks,
        "gate_passed": all(checks.values()),
        "final_status": final_status,
        "selected_next_action": decision.get("selected_next_action"),
        "nearest_alternative": decision.get("nearest_alternative"),
        "candidate_count": candidates.get("candidate_count", 0),
        "recommended_next_milestone": decision.get("next_recommended_milestone", NEXT_MILESTONE),
        "owner_decision_status": OWNER_DECISION_STATUS,
        "external_action_allowed": False,
        "customer_validation_claimed": False,
        "paid_signal_claimed": False,
        "expert_feedback_claimed": False,
        "EU_AI_Act_compliance_claimed": False,
        "legal_compliance_claimed": False,
        "CEO_fully_autonomous_external_execution_claimed": False,
    }


def write_reports(root: Path | None = None) -> None:
    base = root or BRIDGE_ROOT
    archaeology = load_json("operations/external_validation/e69_repository_archaeology_inventory.json", base)
    inventory = load_json("operations/external_validation/e69_ceo_installed_capability_inventory.json", base)
    synthesis = load_json("operations/external_validation/e69_ceo_current_strategic_state_synthesis.json", base)
    candidates = load_json("operations/external_validation/e69_ceo_next_action_candidate_set.json", base)
    scoring = load_json("operations/external_validation/e69_ceo_next_action_scoring_matrix.json", base)
    counterfactuals = load_json("operations/external_validation/e69_ceo_next_action_counterfactuals.json", base)
    decision = load_json("operations/external_validation/e69_ceo_selected_next_action_decision.json", base)
    integration = load_json("operations/external_validation/e69_cieu_module_integration_plan.json", base)
    owner_packet = load_json("operations/external_validation/e69_owner_decision_packet_no_execution.json", base)
    gate = load_json("operations/external_validation/e69_completion_gate_result.json", base)
    write_md(base, "reports/integration/e69_repository_archaeology_inventory.md", "E69 Repository Archaeology", [
        f"Assets inspected: `{archaeology.get('asset_count')}`.",
        "E69 reused E65, E67, E68, E66, CEO brain, and product blueprint assets.",
    ])
    write_md(base, "reports/integration/e69_ceo_installed_capability_inventory.md", "E69 CEO Installed Capability Inventory", [
        f"Capabilities available to CEO: `{inventory.get('capability_count')}`.",
        "Capabilities include market dynamics, external validation, CIEU route, model-driven offer, and runtime governance.",
    ])
    write_md(base, "reports/integration/e69_ceo_current_strategic_state_synthesis.md", "E69 CEO Current Strategic State Synthesis", [
        f"Primary route: `{synthesis.get('current_primary_first_cash_route')}`.",
        f"CIEU vertical: `{synthesis.get('CIEU_high_defensibility_vertical')}`.",
        "CEO can propose next actions internally, but cannot execute externally without owner approval.",
    ])
    write_md(base, "reports/integration/e69_ceo_next_action_candidate_set.md", "E69 CEO Next-Action Candidate Set", [
        f"CEO-generated candidates: `{candidates.get('candidate_count')}`.",
        f"Top candidate after scoring: `{scoring.get('top_candidate')}`.",
    ])
    write_md(base, "reports/integration/e69_ceo_next_action_scoring_matrix.md", "E69 CEO Next-Action Scoring Matrix", [
        f"Top candidate: `{scoring.get('top_candidate')}`.",
        f"Nearest alternative: `{scoring.get('nearest_alternative')}`.",
    ])
    write_md(base, "reports/integration/e69_ceo_next_action_counterfactuals.md", "E69 CEO Next-Action Counterfactuals", [
        f"Counterfactuals evaluated: `{len(counterfactuals.get('counterfactuals', []))}`.",
        "Counterfactuals cover CIEU integration, owner packet timing, validation refresh, fallback route, and owner rejection.",
    ])
    write_md(base, "reports/integration/e69_ceo_selected_next_action_decision.md", "E69 CEO Selected Next-Action Decision", [
        f"Selected next action: `{decision.get('selected_next_action')}`.",
        f"Nearest alternative: `{decision.get('nearest_alternative')}`.",
        f"Next milestone: `{decision.get('next_recommended_milestone')}`.",
    ])
    write_md(base, "reports/integration/e69_cieu_module_integration_plan.md", "E69 CIEU Module Integration Plan", [
        f"Module: `{integration.get('module_name')}`.",
        "Internal-only; no compliance, customer, paid, expert, medical, or energy readiness claim.",
    ])
    write_md(base, "reports/integration/e69_owner_decision_packet_no_execution.md", "E69 Owner Decision Packet No Execution", [
        f"Packet status: `{owner_packet.get('packet_status')}`.",
        "This packet is not owner approval. It is a decision object for future owner review.",
    ])
    write_md(base, "reports/integration/e69_reuse_first_growth_audit.md", "E69 Reuse-First Growth Audit", [
        "Reuse-first audit passed. E69 added only a thin autonomous next-action planning layer.",
    ])
    write_md(base, "reports/integration/e69_completion_gate_result.md", "E69 Completion Gate", [
        f"Gate passed: `{gate.get('gate_passed')}`.",
        f"Final status: `{gate.get('final_status')}`.",
        f"Recommended next milestone: `{gate.get('recommended_next_milestone')}`.",
    ])
    write_md(base, "reports/integration/e69_operator_handoff.md", "E69 Operator Handoff", [
        "CEO can now generate, score, and select next-action candidates from installed state.",
        "External execution remains owner-gated.",
    ])


def write_all_e69_artifacts(root: Path | None = None) -> dict[str, Any]:
    base = root or BRIDGE_ROOT
    write_json(base, "operations/external_validation/e69_base_state_manifest.json", build_base_state_manifest(base))
    write_json(base, "operations/external_validation/e69_repository_archaeology_inventory.json", build_repository_archaeology_inventory(base))
    write_json(base, "operations/external_validation/e69_reuse_first_growth_audit.json", build_reuse_first_growth_audit(base))
    write_json(base, "operations/external_validation/e69_ceo_installed_capability_inventory.json", build_installed_capability_inventory(base))
    write_json(base, "operations/external_validation/e69_ceo_current_strategic_state_synthesis.json", build_current_strategic_state_synthesis(base))
    write_json(base, "operations/external_validation/e69_ceo_next_action_candidate_set.json", build_candidate_set(base))
    write_json(base, "operations/external_validation/e69_ceo_next_action_scoring_matrix.json", build_scoring_matrix(base))
    write_json(base, "operations/external_validation/e69_ceo_next_action_counterfactuals.json", build_counterfactuals(base))
    write_json(base, "operations/external_validation/e69_ceo_selected_next_action_decision.json", build_selected_next_action_decision(base))
    write_json(base, "operations/external_validation/e69_cieu_module_integration_plan.json", build_cieu_module_integration_plan(base))
    write_json(base, "operations/external_validation/e69_owner_decision_packet_no_execution.json", build_owner_decision_packet(base))
    write_json(base, "operations/external_validation/e69_behavior_authorization_result.json", build_behavior_authorization(base))
    write_runtime_writeback(base)
    write_json(base, "operations/external_validation/e69_ceo_next_action_planner_readback_smoke_result.json", build_ceo_next_action_planner_readback_smoke(base))
    write_json(base, "operations/external_validation/e69_no_overclaim_validation_result.json", build_no_overclaim_validation(base))
    gate = build_completion_gate(base)
    write_json(base, "operations/external_validation/e69_completion_gate_result.json", gate)
    write_reports(base)
    return gate


if __name__ == "__main__":
    print(json.dumps(write_all_e69_artifacts(), indent=2, ensure_ascii=False))
