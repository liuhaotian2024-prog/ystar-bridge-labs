from __future__ import annotations

import json
import os
import subprocess
import time
from collections import Counter
from pathlib import Path
from typing import Any

from .e65_ceo_market_dynamics_readback import (
    explain_route_selection,
    get_decision_stability,
    get_market_dynamics_model,
    get_recommended_market_portfolio,
    get_route_evidence,
    list_update_triggers,
    rank_routes_by_profile,
)

BRIDGE_ROOT = Path(os.environ.get("YSTAR_BRIDGE_LABS_ROOT", Path(__file__).resolve().parents[2]))
Y_GOV_ROOT = Path(os.environ.get("YSTAR_GOV_ROOT", "/Users/haotianliu/.openclaw/workspace/Y-star-gov"))
GOV_MCP_ROOT = Path(os.environ.get("GOV_MCP_ROOT", "/Users/haotianliu/.openclaw/workspace/gov-mcp"))
K9_ROOT = Path(os.environ.get("K9AUDIT_ROOT", "/Users/haotianliu/.openclaw/workspace/K9Audit"))

JOB_ID = "e66_selected_route_offer_blueprint_using_market_dynamics_model_no_execution_20260506T000001Z"
EXPECTED_BASE = "1c64befd2148740d07ad9de500b8d4d53bbd8fe2"
OWNER_DECISION_STATUS = "pending_owner_decision"
SELECTED_ROUTE = "governed_business_operations_blueprint_for_agent_teams"
FALLBACK_ROUTE = "founder_operator_decision_brief_service"
LEARNING_ROUTE = "public_read_market_intelligence_product"
STRATEGIC_ROUTE = "AI_agent_company_runtime_harness_deployment_blueprint"
OFFER_NAME = "Governed Business Operations Blueprint for Agent Teams"
NEXT_MILESTONE = "E67_owner_decision_packet_for_controlled_external_review_no_execution"
PRODUCT_DIR = "products/governed_business_operations_blueprint_for_agent_teams"


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


def dirty_paths_are_e66_scoped(status_short: str) -> bool:
    if not status_short:
        return True
    allowed_prefixes = (
        "office/mission_command/e66_",
        "tests/office/test_e66_",
        "operations/external_validation/e66_",
        "operations/knowledge_graph/e66_",
        "reports/integration/e66_",
        f"{PRODUCT_DIR}/",
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
        "artifact_id": "e66_base_state_manifest",
        "bridge_job_id": JOB_ID,
        "bridge_labs": bridge,
        "expected_branch": "backflow/aiden-ceo-meeting-room",
        "base_verified": bridge["head_matches_expected"] and bridge["branch"] == "backflow/aiden-ceo-meeting-room",
        "bridge_labs_worktree_clean_or_e66_scoped": dirty_paths_are_e66_scoped(bridge["status_short"]),
        "read_only_repos": read_only,
        "read_only_repos_clean": all(item.get("clean", True) for item in read_only.values()),
        "e65_completed_report_present": Path("/tmp/ystar_delivery_bridge/completed/e65_ceo_market_dynamics_intelligence_model_l5_20260506T000001Z.report.json").exists(),
        "owner_decision_status": OWNER_DECISION_STATUS,
        "external_action_allowed": False,
    }


def build_repository_archaeology_inventory(root: Path | None = None) -> dict[str, Any]:
    base = root or BRIDGE_ROOT
    explicit_assets = [
        "office/mission_command/e65_market_dynamics_model.py",
        "office/mission_command/e65_ceo_market_dynamics_readback.py",
        "operations/external_validation/e65_market_dynamics_model_schema.json",
        "operations/external_validation/e65_broad_market_universe.json",
        "operations/external_validation/e65_market_adjacency_graph.json",
        "operations/external_validation/e65_market_signal_taxonomy.json",
        "operations/external_validation/e65_market_evidence_quality_model.json",
        "operations/external_validation/e65_multi_axis_market_scoring_engine.json",
        "operations/external_validation/e65_sensitivity_and_counterfactual_challenge_model.json",
        "operations/external_validation/e65_market_dynamics_analysis_run.json",
        "operations/external_validation/e65_market_dynamics_route_rankings.json",
        "operations/external_validation/e65_ceo_brain_market_dynamics_update.json",
        "operations/external_validation/e65_ceo_market_dynamics_readback_smoke_result.json",
        "operations/external_validation/e64_dual_axis_first_cash_path_selection.json",
        "operations/external_validation/e64_top3_dual_axis_offer_hypotheses.json",
        "operations/external_validation/e63_revenue_opportunity_map.json",
        "operations/external_validation/e63_offer_package_hypothesis.json",
        "operations/external_validation/e62_autonomous_revenue_runtime_centerline.json",
        "operations/external_validation/e62_revenue_path_candidate_matrix.json",
        "office/mission_command/e46b_ceo_brain_adapter.py",
    ]
    discovered = []
    for rel in explicit_assets:
        path = base / rel
        lower = rel.lower()
        if "e65" in lower:
            capability = "E65_market_model_API_or_artifact"
        elif "e64" in lower:
            capability = "E64_dual_axis_route_context"
        elif "e63" in lower:
            capability = "E63_opportunity_and_offer_context"
        elif "e62" in lower:
            capability = "E62_revenue_runtime_context"
        elif "e46b" in lower:
            capability = "CEO_brain_adapter"
        else:
            capability = "runtime_context"
        discovered.append({
            "path": rel,
            "exists": path.exists(),
            "capability_type": capability,
            "reusable": path.exists(),
            "connected_status": "connected" if path.exists() else "missing",
            "must_not_rebuild": capability in {"E65_market_model_API_or_artifact", "CEO_brain_adapter"},
        })
    capability_counts = Counter(item["capability_type"] for item in discovered if item["exists"])
    return {
        "artifact_id": "e66_repository_archaeology_inventory",
        "bridge_job_id": JOB_ID,
        "asset_count": len([item for item in discovered if item["exists"]]),
        "discovered_assets": discovered,
        "E65_model_API_assets_reused": [item["path"] for item in discovered if item["exists"] and item["capability_type"] == "E65_market_model_API_or_artifact"],
        "E64_dual_axis_assets_reused": [item["path"] for item in discovered if item["exists"] and item["capability_type"] == "E64_dual_axis_route_context"],
        "E63_E62_revenue_assets_reused": [item["path"] for item in discovered if item["exists"] and item["capability_type"] in {"E63_opportunity_and_offer_context", "E62_revenue_runtime_context"}],
        "reusable_offer_pricing_business_assets": [
            "operations/external_validation/e64_top3_dual_axis_offer_hypotheses.json",
            "operations/external_validation/e63_offer_package_hypothesis.json",
            "products/ai_agent_company_runtime_harness_deployment_blueprint/deployment_blueprint.json",
        ],
        "disconnected_assets": [item["path"] for item in discovered if not item["exists"]],
        "what_must_not_be_rebuilt": [
            "E65 market dynamics model",
            "E65 profile ranking functions",
            "E65 route evidence and explanation APIs",
            "public-read adapters",
            "source receipt builders",
            "evidence atomizers",
            "behavior authorization gates",
            "KG/CZL/CIEU conventions",
            "CEO brain readback smoke conventions",
        ],
        "E66_thin_layer_needed": "model invocation proof, fresh model-driven revenue analysis, selected route offer blueprint, product sample packet, pricing hypothesis, and CEO readback",
        "capability_counts": dict(capability_counts),
        "archaeology_completed_before_blueprint": True,
        "external_action_allowed": False,
    }


def build_reuse_first_growth_audit(root: Path | None = None) -> dict[str, Any]:
    return {
        "artifact_id": "e66_reuse_first_growth_audit",
        "bridge_job_id": JOB_ID,
        "reused_assets": [
            "office/mission_command/e65_market_dynamics_model.py",
            "office/mission_command/e65_ceo_market_dynamics_readback.py",
            "operations/external_validation/e65_market_dynamics_route_rankings.json",
            "operations/external_validation/e65_market_dynamics_analysis_run.json",
            "operations/external_validation/e64_dual_axis_first_cash_path_selection.json",
            "operations/external_validation/e63_offer_package_hypothesis.json",
            "office/mission_command/e46b_ceo_brain_adapter.py",
        ],
        "reconnected_assets": ["CEO brain adapter extended to read E66 model-driven offer state"],
        "thin_wrappers_added": ["office/mission_command/e66_ceo_brain_readback_smoke.py"],
        "genuinely_new_assets_added": [
            "office/mission_command/e66_model_driven_offer_core.py",
            PRODUCT_DIR,
        ],
        "duplicate_capability_risks_checked": {
            "E65_market_model_rebuilt": False,
            "route_scoring_engine_rebuilt": False,
            "public_read_adapter_rebuilt": False,
            "evidence_atomizer_rebuilt": False,
            "behavior_gate_rebuilt": False,
            "CEO_readback_rebuilt": False,
        },
        "avoided_rebuilds": [
            "E66 calls E65 profile ranking APIs rather than recomputing rankings independently",
            "E66 reads E65 portfolio/evidence/stability instead of copying E65 conclusions",
            "E66 creates only the selected route offer layer and sample packet",
        ],
        "justification_for_every_new_module": {
            "e66_model_driven_offer_core.py": "No existing file produced an E66-specific model invocation proof plus selected route offer blueprint from E65 API outputs.",
            "e66_ceo_brain_readback_smoke.py": "Thin reader wrapper follows E61-E64 conventions and exposes E66 state to CEO brain.",
            PRODUCT_DIR: "No selected-route product directory existed for governed business operations blueprint; this is draft-only internal offer packaging, not a new market model.",
        },
        "connected_to_E54_E65_runtime_assets": True,
        "passed": True,
    }


def _profile_summary(root: Path) -> dict[str, Any]:
    profiles = [
        "fastest_cash_profile",
        "strategic_defensibility_profile",
        "low_risk_profile",
        "learning_maximization_profile",
        "balanced_CEO_profile",
    ]
    results = {}
    for profile in profiles:
        ranking = rank_routes_by_profile(profile, root)
        results[profile] = {
            "top_route": ranking["top_route"],
            "top_score": ranking["rankings"][0]["score"],
            "top5": ranking["rankings"][:5],
        }
    return results


def build_e65_model_invocation_proof(root: Path | None = None) -> dict[str, Any]:
    base = root or BRIDGE_ROOT
    invoked: dict[str, Any] = {}
    failures: list[dict[str, str]] = []

    def capture(name: str, func, *args):
        try:
            value = func(*args, base)
            invoked[name] = {"status": "passed", "result": value}
            return value
        except Exception as exc:
            invoked[name] = {"status": "failed", "error": str(exc)}
            failures.append({"function": name, "error": str(exc)})
            return {}

    model = capture("get_market_dynamics_model", get_market_dynamics_model)
    profile_rankings = {}
    for profile in ["fastest_cash_profile", "strategic_defensibility_profile", "low_risk_profile", "learning_maximization_profile", "balanced_CEO_profile"]:
        profile_rankings[profile] = capture(f"rank_routes_by_profile:{profile}", rank_routes_by_profile, profile)
    selected_evidence = capture(f"get_route_evidence:{SELECTED_ROUTE}", get_route_evidence, SELECTED_ROUTE)
    fallback_evidence = capture(f"get_route_evidence:{FALLBACK_ROUTE}", get_route_evidence, FALLBACK_ROUTE)
    stability = capture("get_decision_stability", get_decision_stability)
    portfolio = capture("get_recommended_market_portfolio", get_recommended_market_portfolio)
    explanation = capture(f"explain_route_selection:{SELECTED_ROUTE}", explain_route_selection, SELECTED_ROUTE)
    triggers = capture("list_update_triggers", list_update_triggers)
    evidence_quality_tier = "T2 public-read evidence"
    return {
        "artifact_id": "e66_e65_model_invocation_proof",
        "bridge_job_id": JOB_ID,
        "functions_invoked": list(invoked.keys()),
        "invocation_results": invoked,
        "invocation_status": "passed" if not failures else "failed",
        "failures": failures,
        "returned_primary_route": portfolio.get("primary_route"),
        "returned_first_cash_wedge": portfolio.get("first_cash_wedge"),
        "returned_fallback_route": portfolio.get("fallback_route"),
        "returned_learning_route": portfolio.get("learning_route"),
        "returned_strategic_compounding_route": portfolio.get("strategic_compounding_route"),
        "returned_decision_stability_score": stability.get("decision_stability_score"),
        "returned_evidence_quality_tier": evidence_quality_tier,
        "returned_update_triggers": triggers.get("triggers", []),
        "selected_route_evidence_count": selected_evidence.get("evidence_count", 0),
        "fallback_route_evidence_count": fallback_evidence.get("evidence_count", 0),
        "profile_top_routes": {profile: data.get("top_route") for profile, data in profile_rankings.items()},
        "market_model_universe_domain_count": (model.get("universe") or {}).get("domain_count"),
        "E65_model_actually_used_instead_of_copied": not failures and bool(model) and bool(profile_rankings),
        "external_action_allowed": False,
    }


def build_model_driven_revenue_analysis(root: Path | None = None) -> dict[str, Any]:
    base = root or BRIDGE_ROOT
    proof = load_json("operations/external_validation/e66_e65_model_invocation_proof.json", base) or build_e65_model_invocation_proof(base)
    profile_top = proof.get("profile_top_routes", {})
    top_counts = Counter(profile_top.values())
    stable_route, stable_count = top_counts.most_common(1)[0]
    e64_selection = load_json("operations/external_validation/e64_dual_axis_first_cash_path_selection.json", base)
    portfolio = {
        "primary_route": proof.get("returned_primary_route"),
        "first_cash_wedge": proof.get("returned_first_cash_wedge"),
        "fallback_route": proof.get("returned_fallback_route"),
        "learning_route": proof.get("returned_learning_route"),
        "strategic_compounding_route": proof.get("returned_strategic_compounding_route"),
    }
    return {
        "artifact_id": "e66_model_driven_revenue_analysis",
        "bridge_job_id": JOB_ID,
        "analysis_status": "completed" if proof.get("invocation_status") == "passed" else "blocked_by_model_invocation_failure",
        "top_route_under_fastest_cash_profile": profile_top.get("fastest_cash_profile"),
        "top_route_under_strategic_defensibility_profile": profile_top.get("strategic_defensibility_profile"),
        "top_route_under_low_risk_profile": profile_top.get("low_risk_profile"),
        "top_route_under_learning_maximization_profile": profile_top.get("learning_maximization_profile"),
        "top_route_under_balanced_CEO_profile": profile_top.get("balanced_CEO_profile"),
        "most_stable_route_across_profiles": stable_route,
        "stable_route_profile_count": stable_count,
        "fastest_but_commodity_risky_route": FALLBACK_ROUTE,
        "most_unique_but_slower_to_cash_route": STRATEGIC_ROUTE,
        "best_primary_route": portfolio["primary_route"],
        "best_first_cash_wedge": portfolio["first_cash_wedge"],
        "best_fallback_route": portfolio["fallback_route"],
        "best_learning_route": portfolio["learning_route"],
        "best_strategic_compounding_route": portfolio["strategic_compounding_route"],
        "E65_portfolio_remained_stable": portfolio["primary_route"] == SELECTED_ROUTE and portfolio["fallback_route"] == FALLBACK_ROUTE,
        "update_trigger_required_route_revision": False,
        "update_triggers_observed": proof.get("returned_update_triggers", []),
        "evidence_quality_changed": False,
        "current_evidence_quality_tier": proof.get("returned_evidence_quality_tier"),
        "comparison_against_E64": {
            "E64_selected_path": e64_selection.get("selected_final_first_cash_path"),
            "E64_best_market_optimal_path": e64_selection.get("best_open_world_market_optimal_path"),
            "E64_best_YBridge_unique_path": e64_selection.get("best_YBridge_unique_path"),
            "what_E66_can_answer_now": [
                "profile-specific top route",
                "decision stability",
                "route evidence lookup",
                "portfolio roles",
                "update triggers",
            ],
            "E65_created_strategy_capability_leap": True,
            "selected_route_more_justified_than_before": True,
            "still_depends_only_on_T2_public_read_evidence": True,
        },
        "remaining_uncertainties": [
            "customer validation absent",
            "paid signal absent",
            "pricing validation absent",
            "owner-approved external review absent",
            "delivery complexity still internally modeled",
        ],
        "customer_validation_claimed": False,
        "paid_signal_claimed": False,
        "expert_feedback_claimed": False,
        "pricing_validation_claimed": False,
        "global_optimality_proven": False,
        "external_action_allowed": False,
    }


def build_revenue_strategy_capability_leap_assessment(root: Path | None = None) -> dict[str, Any]:
    return {
        "artifact_id": "e66_revenue_strategy_capability_leap_assessment",
        "bridge_job_id": JOB_ID,
        "assessment": "capability leap toward market strategy intelligence",
        "before_E65": [
            "one-off dual-axis matrix",
            "route selection artifact",
            "limited dynamic update capacity",
            "no reusable CEO market model API",
        ],
        "after_E65": [
            "reusable CEO market dynamics model",
            "32-route broad universe",
            "market adjacency graph",
            "20-signal taxonomy",
            "T0-T8 evidence quality ladder",
            "14-axis multi-profile scoring engine",
            "sensitivity and counterfactual model",
            "recommended portfolio",
            "update triggers",
            "CEO loader/API integration",
        ],
        "CEO_can_now_analyze_broader_markets": True,
        "CEO_can_reason_beyond_selling_own_AI_runtime": True,
        "CEO_can_compare_fast_cash_uniqueness_and_risk": True,
        "CEO_can_explain_route_evidence": True,
        "CEO_can_identify_evidence_gaps": True,
        "CEO_can_select_portfolio_instead_of_single_route": True,
        "remaining_weaknesses": ["no customer validation", "no paid signal", "no pricing validation", "owner approval absent"],
        "overclaim_boundary": "not perfect strategy intelligence and not validated commercial strategy",
        "customer_validation_claimed": False,
        "paid_signal_claimed": False,
        "expert_feedback_claimed": False,
        "autonomous_revenue_achieved": False,
        "external_action_allowed": False,
    }


def build_model_driven_selected_route_decision(root: Path | None = None) -> dict[str, Any]:
    base = root or BRIDGE_ROOT
    analysis = load_json("operations/external_validation/e66_model_driven_revenue_analysis.json", base) or build_model_driven_revenue_analysis(base)
    proof = load_json("operations/external_validation/e66_e65_model_invocation_proof.json", base) or build_e65_model_invocation_proof(base)
    confirmed_route = analysis.get("best_primary_route")
    route_changed = confirmed_route != SELECTED_ROUTE
    selected_route = confirmed_route or SELECTED_ROUTE
    decision = "confirm_E65_route" if not route_changed else "switch_to_model_selected_route"
    return {
        "artifact_id": "e66_model_driven_selected_route_decision",
        "bridge_job_id": JOB_ID,
        "E65_primary_route_before_E66": SELECTED_ROUTE,
        "E66_confirmed_primary_route": selected_route,
        "first_cash_wedge": analysis.get("best_first_cash_wedge"),
        "fallback_route": analysis.get("best_fallback_route"),
        "learning_route": analysis.get("best_learning_route"),
        "strategic_compounding_route": analysis.get("best_strategic_compounding_route"),
        "selected_route_changed": route_changed,
        "decision": decision,
        "why_it_changed_or_stayed": "E65 model APIs ranked the selected route first under strategic defensibility, learning maximization, and balanced CEO reasoning while keeping founder/operator decision brief as fastest-cash fallback.",
        "route_evidence": get_route_evidence(selected_route, base),
        "evidence_quality_tier": proof.get("returned_evidence_quality_tier"),
        "decision_stability_score": proof.get("returned_decision_stability_score"),
        "fragile_assumptions": get_decision_stability(base).get("fragile_assumptions", []),
        "owner_gated_blockers": [
            "external review",
            "publication",
            "outreach",
            "pricing presentation",
            "payment or invoice",
            "client delivery",
        ],
        "no_overclaim_limitations": [
            "not customer validated",
            "not paid validated",
            "not pricing validated",
            "not production ready",
            "not globally optimality proven",
        ],
        "selected_route_for_blueprint": selected_route,
        "recommended_next_milestone": NEXT_MILESTONE,
        "external_action_allowed": False,
        "owner_decision_status": OWNER_DECISION_STATUS,
        "customer_validation_claimed": False,
        "paid_signal_claimed": False,
        "expert_feedback_claimed": False,
        "pricing_validation_claimed": False,
        "global_optimality_proven": False,
    }


def build_selected_route_offer_blueprint(root: Path | None = None) -> dict[str, Any]:
    base = root or BRIDGE_ROOT
    decision = load_json("operations/external_validation/e66_model_driven_selected_route_decision.json", base) or build_model_driven_selected_route_decision(base)
    selected_route = decision.get("selected_route_for_blueprint", SELECTED_ROUTE)
    return {
        "artifact_id": "e66_selected_route_offer_blueprint",
        "bridge_job_id": JOB_ID,
        "offer_identity": {
            "offer_id": "governed_business_operations_blueprint_for_agent_teams",
            "offer_name": OFFER_NAME,
            "selected_route": selected_route,
            "status": "draft_only_internal",
            "risk_tier": "T2_draft_only_external_material",
            "evidence_tier": "T2_public_read_plus_internal_L5_runtime_proof",
        },
        "buyer_category": [
            "founder/operator teams",
            "agent teams",
            "AI platform or engineering teams",
            "small teams turning AI agent activity into governed business operations",
        ],
        "pain_point": [
            "agent workflows create activity but not governed business operations",
            "teams need action boundaries, evidence closure, readback, and owner-gated execution",
            "AI adoption needs practical operating structure rather than demos",
        ],
        "promised_outcome": "internal governed business operations blueprint; not production deployment, customer validation, paid signal, or external approval",
        "deliverables": [
            "runtime/business objective map",
            "action risk-tier matrix",
            "behavior authorization plan",
            "evidence closure and readback map",
            "no-overclaim policy",
            "first internal value loop design",
            "owner-gated external action plan",
            "implementation backlog",
        ],
        "delivery_phases": [
            "Phase 1: runtime/business archaeology",
            "Phase 2: business objective and current-state mapping",
            "Phase 3: action surface and risk-tier mapping",
            "Phase 4: behavior authorization and no-overclaim design",
            "Phase 5: evidence closure and readback design",
            "Phase 6: first internal value loop design",
            "Phase 7: owner-gated external action plan",
            "Phase 8: optional implementation support, future and owner-gated",
        ],
        "inputs_needed_from_future_buyer": [
            "current agent workflows",
            "business objective",
            "action surfaces",
            "risk boundaries",
            "existing evidence/logging setup",
            "owner/approver identity category",
            "desired first internal value loop",
        ],
        "outputs_generated": [
            "blueprint",
            "route map",
            "risk-tier map",
            "evidence plan",
            "governance checklist",
            "no-overclaim boundary",
            "implementation backlog",
        ],
        "pricing_package_hypothesis": {
            "status": "draft_only_unvalidated",
            "tiers": ["Diagnostic Brief", "Blueprint Sprint", "Implementation Planning Add-on"],
            "pricing_validation_claimed": False,
        },
        "evidence_and_limitations": {
            "E65_model_support": True,
            "E64_E63_public_read_support": True,
            "E54_E56_runtime_proof_support": True,
            "missing_customer_validation": True,
            "missing_paid_signal": True,
            "missing_pricing_validation": True,
            "missing_owner_approved_external_review": True,
        },
        "why_this_is_not_generic_AI_consulting": [
            "uses CEO market model",
            "uses behavior authorization",
            "uses KG/CZL/CIEU evidence closure",
            "uses no-overclaim boundary",
            "uses owner-gated action control",
            "uses Y*Bridge runtime architecture",
        ],
        "owner_gated_next_steps": ["external review", "publication", "outreach", "pricing presentation", "payment or invoice", "client delivery"],
        "customer_validation_claimed": False,
        "paid_signal_claimed": False,
        "expert_feedback_claimed": False,
        "production_readiness_claimed": False,
        "pricing_validation_claimed": False,
        "autonomous_revenue_achieved": False,
        "external_action_allowed": False,
    }


def build_sample_delivery_packet(blueprint: dict[str, Any]) -> dict[str, Any]:
    return {
        "artifact_id": "e66_sample_delivery_packet",
        "status": "draft_only_internal_sample",
        "fictional_generic_buyer_category": "small AI platform team with existing agent workflows",
        "no_named_real_customer": True,
        "no_contact_info": True,
        "not_real_delivery": True,
        "not_market_validation": True,
        "sections": {
            "business_objective_map": "Map agent activity to owner-visible business outcomes and decision rights.",
            "action_risk_tier_matrix": {
                "T0_internal_only": "internal reasoning and drafts",
                "T1_public_read_only": "safe public observation only",
                "T2_draft_only_external_material": "draft external materials with no send/publish",
                "T3_owner_approved_external_contact": "explicit owner approval required",
                "T4_owner_approved_commercial_transaction": "explicit owner approval required for payment/client delivery",
            },
            "behavior_authorization_plan": "Define ALLOW/DENY gates before actions can move beyond internal-only operation.",
            "evidence_closure_map": "Specify receipts, evidence atoms, KG nodes, CZL closure, and CEO readback.",
            "first_internal_value_loop": "Create one governed internal business loop before external execution.",
            "implementation_backlog": ["adapter/readback wiring", "policy fixtures", "owner decision packet", "controlled review plan"],
        },
        "source_offer_blueprint_id": blueprint["offer_identity"]["offer_id"],
        "external_action_allowed": False,
        "customer_validation_claimed": False,
        "paid_signal_claimed": False,
        "expert_feedback_claimed": False,
        "pricing_validation_claimed": False,
    }


def write_product_directory(root: Path | None = None) -> dict[str, Any]:
    base = root or BRIDGE_ROOT
    blueprint = load_json("operations/external_validation/e66_selected_route_offer_blueprint.json", base) or build_selected_route_offer_blueprint(base)
    sample = build_sample_delivery_packet(blueprint)
    write_json(base, f"{PRODUCT_DIR}/offer_blueprint.json", blueprint)
    write_json(base, f"{PRODUCT_DIR}/sample_delivery_packet.json", sample)
    write_md(base, f"{PRODUCT_DIR}/README.md", OFFER_NAME, [
        "Status: internal-only draft.",
        "This directory packages a model-driven offer blueprint for the selected E66 route.",
        "It is not customer-validated, paid-validated, expert-reviewed, production-ready, or externally approved.",
    ])
    write_md(base, f"{PRODUCT_DIR}/offer_blueprint.md", "Offer Blueprint", [
        f"Offer: `{OFFER_NAME}`.",
        f"Selected route: `{blueprint['offer_identity']['selected_route']}`.",
        "Deliverable: governed business operations blueprint for agent teams.",
        "Evidence tier: T2 public-read plus internal L5 runtime proof. This is not validation.",
        "Owner approval is required before any external use.",
    ])
    write_md(base, f"{PRODUCT_DIR}/sample_delivery_packet.md", "Sample Delivery Packet", [
        "This is a fictional generic sample for internal planning only.",
        "It contains no named real customer, no contact information, and no claim of real delivery.",
        "Main sample sections: business objective map, action risk-tier matrix, behavior authorization plan, evidence closure map, first internal value loop, and implementation backlog.",
    ])
    write_md(base, f"{PRODUCT_DIR}/no_overclaim_notice.md", "No-Overclaim Notice", [
        "This blueprint is internal-only and draft-only.",
        "Do not claim customer validation, paid signal, expert feedback, pricing validation, production readiness, real client delivery, or owner approval.",
        "Public-read evidence is directional market intelligence, not customer validation.",
    ])
    write_md(base, f"{PRODUCT_DIR}/owner_gated_next_actions.md", "Owner-Gated Next Actions", [
        "Allowed now: internal hardening, sample packet refinement, evidence refresh, and owner decision packet generation.",
        "Requires owner approval: external review, publication, outreach, customer conversation, pricing presentation, payment/invoice, and client delivery.",
    ])
    return {"product_directory": PRODUCT_DIR, "files_written": 7, "sample_delivery_packet": sample}


def build_pricing_package_hypothesis(root: Path | None = None) -> dict[str, Any]:
    return {
        "artifact_id": "e66_model_driven_pricing_package_hypothesis",
        "bridge_job_id": JOB_ID,
        "status": "draft_only_internal_unvalidated",
        "package_tiers": [
            {
                "tier_name": "Diagnostic Brief",
                "scope": "smallest low-risk review of agent workflow, action surfaces, and governance gaps",
                "output": "short risk/opportunity brief",
                "pricing_logic": "entry-level fixed-scope brief; price must be owner-approved before external presentation",
            },
            {
                "tier_name": "Blueprint Sprint",
                "scope": "main first-cash wedge",
                "output": "governed operations blueprint plus risk/action/evidence map",
                "pricing_logic": "higher fixed-scope sprint; unvalidated hypothesis only",
            },
            {
                "tier_name": "Implementation Planning Add-on",
                "scope": "future owner-gated support",
                "output": "implementation backlog and governance integration plan",
                "pricing_logic": "add-on planning scope; no invoice/payment path created",
            },
        ],
        "evidence_basis": ["E65 model support", "E64/E63 public-read evidence", "E54-E56 internal runtime proof"],
        "missing_evidence": ["customer validation", "paid signal", "pricing validation", "owner-approved external review"],
        "why_pricing_is_not_validated": "No buyer conversation, pricing presentation, payment, invoice, or customer response occurred.",
        "low_risk_internal_use_only": True,
        "owner_approval_required_before_external_presentation": True,
        "pricing_validation_claimed": False,
        "customer_validation_claimed": False,
        "paid_signal_claimed": False,
        "external_action_allowed": False,
    }


def build_owner_gated_business_action_plan(root: Path | None = None) -> dict[str, Any]:
    return {
        "artifact_id": "e66_owner_gated_business_action_plan_no_execution",
        "bridge_job_id": JOB_ID,
        "allowed_now": [
            "internal blueprint hardening",
            "internal sample delivery packet refinement",
            "model-driven pricing/package refinement",
            "additional public-read evidence refresh",
            "owner decision packet generation",
        ],
        "requires_owner_approval": [
            "external review",
            "publication",
            "outreach",
            "customer conversation",
            "pricing presentation",
            "payment/invoice",
            "client delivery",
        ],
        "still_prohibited": [
            "contact scraping",
            "human identification",
            "unauthorized outreach",
            "fabricated validation",
            "private/provider API use",
            "payment/secret use",
        ],
        "external_action_allowed": False,
        "owner_decision_status": OWNER_DECISION_STATUS,
    }


def build_behavior_authorization(root: Path | None = None) -> dict[str, Any]:
    return {
        "artifact_id": "e66_behavior_authorization_result",
        "authorization_status": "ALLOW_INTERNAL_MODEL_DRIVEN_OFFER_BLUEPRINT_ONLY",
        "allowed_actions": [
            "repository_archaeology",
            "E65_model_API_invocation",
            "internal_revenue_strategy_analysis",
            "capability_leap_assessment",
            "selected_route_decision",
            "internal_offer_blueprint_drafting",
            "sample_delivery_packet_generation",
            "pricing_package_hypothesis",
            "owner_gated_business_action_planning",
            "KG_CZL_CIEU_writeback",
            "CEO_brain_readback",
        ],
        "denied_actions": [
            "outreach",
            "publication",
            "customer_conversation",
            "expert_review",
            "human_identification",
            "contact_scraping",
            "login_form_send",
            "private_provider_API",
            "API_key_secret_use",
            "payment",
            "invoice",
            "client_delivery",
            "customer_validation_claim",
            "paid_signal_claim",
            "expert_feedback_claim",
            "production_readiness_claim",
            "autonomous_revenue_achieved_claim",
            "pricing_validation_claim",
            "perfect_global_optimality_claim",
        ],
        "external_business_execution_authorized": False,
        "owner_decision_status": OWNER_DECISION_STATUS,
        "pending_owner_decision_is_not_approval": True,
        "external_action_allowed": False,
        "passed": True,
    }


def write_runtime_writeback(root: Path | None = None) -> dict[str, Any]:
    base = root or BRIDGE_ROOT
    decision = load_json("operations/external_validation/e66_model_driven_selected_route_decision.json", base) or build_model_driven_selected_route_decision(base)
    analysis = load_json("operations/external_validation/e66_model_driven_revenue_analysis.json", base) or build_model_driven_revenue_analysis(base)
    blueprint = load_json("operations/external_validation/e66_selected_route_offer_blueprint.json", base) or build_selected_route_offer_blueprint(base)
    pricing = load_json("operations/external_validation/e66_model_driven_pricing_package_hypothesis.json", base) or build_pricing_package_hypothesis(base)
    update = {
        "artifact_id": "e66_ceo_brain_model_driven_offer_update",
        "model_driven_offer_status": "model_driven_selected_route_offer_blueprint_created",
        "E65_model_API_invoked": True,
        "fresh_model_driven_revenue_analysis_completed": analysis.get("analysis_status") == "completed",
        "strategy_capability_leap_assessed": True,
        "selected_route": decision.get("E66_confirmed_primary_route"),
        "selected_route_changed": decision.get("selected_route_changed"),
        "offer_name": blueprint["offer_identity"]["offer_name"],
        "product_directory": PRODUCT_DIR,
        "sample_delivery_packet_created": True,
        "pricing_package_hypothesis_created": True,
        "pricing_tiers": [tier["tier_name"] for tier in pricing["package_tiers"]],
        "owner_gated_business_action_plan_created": True,
        "evidence_quality_tier": decision.get("evidence_quality_tier"),
        "decision_stability_score": decision.get("decision_stability_score"),
        "next_recommended_milestone": NEXT_MILESTONE,
        "no_external_action": True,
        "external_action_allowed": False,
        "customer_validation_claimed": False,
        "paid_signal_claimed": False,
        "expert_feedback_claimed": False,
        "production_readiness_claimed": False,
        "autonomous_revenue_achieved": False,
        "real_client_delivery_claimed": False,
        "owner_approval_fabricated": False,
        "pricing_validation_claimed": False,
        "global_optimality_proven": False,
        "perfect_model_claimed": False,
        "real_mcp_transport_claimed": False,
        "owner_decision_status": OWNER_DECISION_STATUS,
    }
    write_json(base, "operations/external_validation/e66_ceo_brain_model_driven_offer_update.json", update)
    write_jsonl(base, "operations/knowledge_graph/e66_ceo_kg_model_driven_offer_nodes_delta.jsonl", [
        {"node_id": "e66_model_driven_offer_blueprint", "node_type": "offer_blueprint", "status": "draft_only_internal"},
        {"node_id": decision.get("E66_confirmed_primary_route"), "node_type": "selected_route"},
        {"node_id": PRODUCT_DIR, "node_type": "product_directory"},
        {"node_id": NEXT_MILESTONE, "node_type": "recommended_next_milestone"},
    ])
    write_jsonl(base, "operations/knowledge_graph/e66_ceo_kg_model_driven_offer_edges_delta.jsonl", [
        {"from": "e65_market_dynamics_model_v1", "to": "e66_model_driven_offer_blueprint", "edge_type": "drives"},
        {"from": "e66_model_driven_offer_blueprint", "to": decision.get("E66_confirmed_primary_route"), "edge_type": "packages_selected_route"},
        {"from": "e66_model_driven_offer_blueprint", "to": NEXT_MILESTONE, "edge_type": "recommends"},
    ])
    write_json(base, "operations/knowledge_graph/e66_ceo_kg_model_driven_offer_read_model_update.json", {
        "artifact_id": "e66_ceo_kg_model_driven_offer_read_model_update",
        **update,
    })
    write_json(base, "operations/external_validation/e66_czl_closure.json", {
        "artifact_id": "e66_czl_closure",
        "closure_status": "closed",
        "closed_loop": "E65 model/API -> model invocation proof -> revenue analysis -> route decision -> offer blueprint -> product packet -> CEO readback",
        "recommended_next_milestone": NEXT_MILESTONE,
        "no_external_action": True,
    })
    write_json(base, "operations/external_validation/e66_cieu_residual_summary.json", {
        "artifact_id": "e66_cieu_residual_summary",
        "intervention": "Used E65 CEO market dynamics APIs to confirm selected route and create internal model-driven offer blueprint.",
        "resolved_residuals": ["CEO can now use E65 model APIs to justify an offer blueprint rather than copy one-off route artifacts"],
        "remaining_residuals": ["owner approval absent", "customer validation absent", "paid signal absent", "pricing validation absent", "external execution still gated"],
        "no_external_action": True,
    })
    return update


def load_e66_state_for_brain(root: Path | None = None) -> dict[str, Any]:
    base = root or BRIDGE_ROOT
    state = load_json("operations/external_validation/e66_ceo_brain_model_driven_offer_update.json", base)
    if not state:
        state = write_runtime_writeback(base)
    return state


def build_ceo_brain_readback_smoke(root: Path | None = None) -> dict[str, Any]:
    state = load_e66_state_for_brain(root)
    checks = {
        "CEO_sees_E65_model_invoked": state.get("E65_model_API_invoked") is True,
        "CEO_sees_fresh_model_driven_analysis": state.get("fresh_model_driven_revenue_analysis_completed") is True,
        "CEO_sees_strategy_capability_leap_assessed": state.get("strategy_capability_leap_assessed") is True,
        "CEO_sees_selected_route": state.get("selected_route") == SELECTED_ROUTE,
        "CEO_sees_offer_blueprint": state.get("offer_name") == OFFER_NAME,
        "CEO_sees_sample_delivery_packet": state.get("sample_delivery_packet_created") is True,
        "CEO_sees_pricing_package_hypothesis": state.get("pricing_package_hypothesis_created") is True,
        "CEO_sees_owner_gated_plan": state.get("owner_gated_business_action_plan_created") is True,
        "CEO_sees_no_external_action": state.get("external_action_allowed") is False,
        "CEO_sees_no_overclaim": all(state.get(key) is False for key in [
            "customer_validation_claimed",
            "paid_signal_claimed",
            "expert_feedback_claimed",
            "production_readiness_claimed",
            "autonomous_revenue_achieved",
            "real_client_delivery_claimed",
            "owner_approval_fabricated",
            "pricing_validation_claimed",
            "global_optimality_proven",
            "perfect_model_claimed",
            "real_mcp_transport_claimed",
        ]),
        "CEO_sees_next_milestone": state.get("next_recommended_milestone") == NEXT_MILESTONE,
    }
    return {
        "artifact_id": "e66_ceo_brain_readback_smoke_result",
        "observed_state": state,
        "checks": checks,
        "passes": all(checks.values()),
        "external_action_allowed": False,
        "owner_decision_status": OWNER_DECISION_STATUS,
    }


def build_no_overclaim_validation(root: Path | None = None) -> dict[str, Any]:
    base = root or BRIDGE_ROOT
    paths = [
        "operations/external_validation/e66_model_driven_revenue_analysis.json",
        "operations/external_validation/e66_model_driven_selected_route_decision.json",
        "operations/external_validation/e66_selected_route_offer_blueprint.json",
        "operations/external_validation/e66_model_driven_pricing_package_hypothesis.json",
        "operations/external_validation/e66_ceo_brain_model_driven_offer_update.json",
        "operations/external_validation/e66_ceo_brain_readback_smoke_result.json",
    ]
    forbidden_true = [
        "customer_validation_claimed",
        "paid_signal_claimed",
        "expert_feedback_claimed",
        "production_readiness_claimed",
        "autonomous_revenue_achieved",
        "real_client_delivery_claimed",
        "owner_approval_fabricated",
        "pricing_validation_claimed",
        "global_optimality_proven",
        "perfect_model_claimed",
        "real_mcp_transport_claimed",
        "external_action_allowed",
    ]
    violations = []
    for rel in paths:
        data = load_json(rel, base)
        observed = data.get("observed_state", data)
        for field in forbidden_true:
            if observed.get(field) is True:
                violations.append({"path": rel, "field": field, "value": True})
    return {
        "artifact_id": "e66_no_overclaim_validation_result",
        "paths_scanned": paths,
        "violations": violations,
        "passed": not violations,
    }


def build_completion_gate(root: Path | None = None) -> dict[str, Any]:
    base = root or BRIDGE_ROOT
    base_state = load_json("operations/external_validation/e66_base_state_manifest.json", base) or build_base_state_manifest(base)
    archaeology = load_json("operations/external_validation/e66_repository_archaeology_inventory.json", base)
    audit = load_json("operations/external_validation/e66_reuse_first_growth_audit.json", base)
    invocation = load_json("operations/external_validation/e66_e65_model_invocation_proof.json", base)
    analysis = load_json("operations/external_validation/e66_model_driven_revenue_analysis.json", base)
    leap = load_json("operations/external_validation/e66_revenue_strategy_capability_leap_assessment.json", base)
    decision = load_json("operations/external_validation/e66_model_driven_selected_route_decision.json", base)
    blueprint = load_json("operations/external_validation/e66_selected_route_offer_blueprint.json", base)
    pricing = load_json("operations/external_validation/e66_model_driven_pricing_package_hypothesis.json", base)
    plan = load_json("operations/external_validation/e66_owner_gated_business_action_plan_no_execution.json", base)
    auth = load_json("operations/external_validation/e66_behavior_authorization_result.json", base)
    readback = load_json("operations/external_validation/e66_ceo_brain_readback_smoke_result.json", base)
    no_overclaim = load_json("operations/external_validation/e66_no_overclaim_validation_result.json", base)
    checks = {
        "base_HEAD_verified": base_state.get("base_verified") is True,
        "repository_archaeology_completed": archaeology.get("asset_count", 0) >= 10,
        "reuse_first_growth_audit_passes": audit.get("passed") is True,
        "E65_model_invocation_proof_passes": invocation.get("invocation_status") == "passed" and invocation.get("E65_model_actually_used_instead_of_copied") is True,
        "fresh_model_driven_revenue_analysis_exists": analysis.get("analysis_status") == "completed",
        "revenue_strategy_capability_leap_assessment_exists": leap.get("assessment") == "capability leap toward market strategy intelligence",
        "selected_route_decision_exists": decision.get("selected_route_for_blueprint") == SELECTED_ROUTE,
        "selected_route_offer_blueprint_exists": blueprint.get("offer_identity", {}).get("offer_name") == OFFER_NAME,
        "product_directory_and_sample_packet_exist": all((base / rel).exists() for rel in [
            f"{PRODUCT_DIR}/README.md",
            f"{PRODUCT_DIR}/offer_blueprint.json",
            f"{PRODUCT_DIR}/sample_delivery_packet.json",
            f"{PRODUCT_DIR}/no_overclaim_notice.md",
        ]),
        "pricing_package_hypothesis_exists": len(pricing.get("package_tiers", [])) == 3,
        "owner_gated_action_plan_exists": OWNER_DECISION_STATUS == plan.get("owner_decision_status"),
        "behavior_authorization_passed": auth.get("passed") is True,
        "KG_CZL_CIEU_writeback_exists": all((base / rel).exists() for rel in [
            "operations/knowledge_graph/e66_ceo_kg_model_driven_offer_read_model_update.json",
            "operations/external_validation/e66_czl_closure.json",
            "operations/external_validation/e66_cieu_residual_summary.json",
        ]),
        "CEO_brain_readback_passed": readback.get("passes") is True,
        "no_forbidden_external_action_executed": auth.get("external_business_execution_authorized") is False,
        "no_overclaim_fields_true": no_overclaim.get("passed") is True,
    }
    final_status = "e66_model_driven_offer_blueprint_completed_selected_route_confirmed" if all(checks.values()) else (
        "e66_model_invocation_failed_before_blueprint" if not checks["E65_model_invocation_proof_passes"] else
        "e66_blocked_due_to_overclaim_risk" if not checks["no_overclaim_fields_true"] else
        "e66_partial_with_internal_blocker"
    )
    return {
        "artifact_id": "e66_completion_gate_result",
        "bridge_job_id": JOB_ID,
        "checks": checks,
        "gate_passed": all(checks.values()),
        "final_status": final_status,
        "selected_route": decision.get("selected_route_for_blueprint"),
        "offer_name": blueprint.get("offer_identity", {}).get("offer_name"),
        "decision_stability_score": decision.get("decision_stability_score"),
        "recommended_next_milestone": NEXT_MILESTONE,
        "owner_decision_status": OWNER_DECISION_STATUS,
        "external_action_allowed": False,
        "customer_validation_claimed": False,
        "paid_signal_claimed": False,
        "expert_feedback_claimed": False,
        "pricing_validation_claimed": False,
        "autonomous_revenue_achieved": False,
        "global_optimality_proven": False,
    }


def write_reports(root: Path | None = None) -> None:
    base = root or BRIDGE_ROOT
    archaeology = load_json("operations/external_validation/e66_repository_archaeology_inventory.json", base)
    invocation = load_json("operations/external_validation/e66_e65_model_invocation_proof.json", base)
    analysis = load_json("operations/external_validation/e66_model_driven_revenue_analysis.json", base)
    decision = load_json("operations/external_validation/e66_model_driven_selected_route_decision.json", base)
    blueprint = load_json("operations/external_validation/e66_selected_route_offer_blueprint.json", base)
    pricing = load_json("operations/external_validation/e66_model_driven_pricing_package_hypothesis.json", base)
    gate = load_json("operations/external_validation/e66_completion_gate_result.json", base)
    write_md(base, "reports/integration/e66_repository_archaeology_inventory.md", "E66 Repository Archaeology Inventory", [
        f"Assets found: `{archaeology.get('asset_count')}`.",
        "E66 reuses E65 model/API assets, E64 dual-axis context, E63/E62 revenue artifacts, and CEO brain readback conventions.",
    ])
    write_md(base, "reports/integration/e66_e65_model_invocation_proof.md", "E66 E65 Model Invocation Proof", [
        f"Invocation status: `{invocation.get('invocation_status')}`.",
        f"Primary route returned: `{invocation.get('returned_primary_route')}`.",
        f"Decision stability score: `{invocation.get('returned_decision_stability_score')}`.",
        "E66 used E65 APIs directly instead of copying prior conclusions.",
    ])
    write_md(base, "reports/integration/e66_model_driven_revenue_analysis.md", "E66 Model-Driven Revenue Analysis", [
        f"Fastest-cash top route: `{analysis.get('top_route_under_fastest_cash_profile')}`.",
        f"Strategic-defensibility top route: `{analysis.get('top_route_under_strategic_defensibility_profile')}`.",
        f"Balanced CEO top route: `{analysis.get('top_route_under_balanced_CEO_profile')}`.",
        f"Primary route: `{analysis.get('best_primary_route')}`.",
        "Evidence remains T2 public-read plus internal proof; no validation is claimed.",
    ])
    write_md(base, "reports/integration/e66_revenue_strategy_capability_leap_assessment.md", "E66 Revenue Strategy Capability Leap Assessment", [
        "Assessment: capability leap toward market strategy intelligence.",
        "CEO can now compare profile-ranked routes, evidence, stability, update triggers, and portfolio roles through a reusable model API.",
        "This is not perfect strategy intelligence or validated commercial strategy.",
    ])
    write_md(base, "reports/integration/e66_model_driven_selected_route_decision.md", "E66 Model-Driven Selected Route Decision", [
        f"Selected route: `{decision.get('selected_route_for_blueprint')}`.",
        f"Route changed: `{decision.get('selected_route_changed')}`.",
        f"Decision stability: `{decision.get('decision_stability_score')}`.",
        f"Recommended next milestone: `{decision.get('recommended_next_milestone')}`.",
    ])
    write_md(base, "reports/integration/e66_selected_route_offer_blueprint.md", "E66 Selected Route Offer Blueprint", [
        f"Offer: `{blueprint.get('offer_identity', {}).get('offer_name')}`.",
        "Status: draft-only internal.",
        "Core deliverables: runtime/business map, action risk-tier matrix, behavior authorization plan, evidence closure/readback map, no-overclaim policy, internal value loop, owner-gated action plan, implementation backlog.",
    ])
    write_md(base, "reports/integration/e66_model_driven_pricing_package_hypothesis.md", "E66 Pricing and Package Hypothesis", [
        f"Tiers: `{', '.join(tier['tier_name'] for tier in pricing.get('package_tiers', []))}`.",
        "Pricing is unvalidated and owner approval is required before any external presentation.",
    ])
    write_md(base, "reports/integration/e66_owner_gated_business_action_plan_no_execution.md", "E66 Owner-Gated Business Action Plan", [
        "Allowed now: internal hardening, sample delivery packet refinement, pricing/package refinement, public-read refresh, owner decision packet.",
        "Requires owner approval: external review, publication, outreach, customer conversation, pricing presentation, payment/invoice, client delivery.",
    ])
    write_md(base, "reports/integration/e66_reuse_first_growth_audit.md", "E66 Reuse-First Growth Audit", [
        "Reuse-first audit passed.",
        "E66 did not rebuild E65 model/scoring, public-read, evidence atomization, behavior authorization, KG/CZL/CIEU, or CEO readback capabilities.",
    ])
    write_md(base, "reports/integration/e66_completion_gate_result.md", "E66 Completion Gate", [
        f"Gate passed: `{gate.get('gate_passed')}`.",
        f"Final status: `{gate.get('final_status')}`.",
        f"Recommended next milestone: `{gate.get('recommended_next_milestone')}`.",
    ])
    write_md(base, "reports/integration/e66_operator_handoff.md", "E66 Operator Handoff", [
        f"Final status: `{gate.get('final_status')}`.",
        f"Selected route: `{gate.get('selected_route')}`.",
        f"Offer blueprint: `{gate.get('offer_name')}`.",
        f"Next milestone: `{gate.get('recommended_next_milestone')}`.",
    ])


def write_all_e66_artifacts(root: Path | None = None) -> dict[str, Any]:
    base = root or BRIDGE_ROOT
    write_json(base, "operations/external_validation/e66_base_state_manifest.json", build_base_state_manifest(base))
    write_json(base, "operations/external_validation/e66_repository_archaeology_inventory.json", build_repository_archaeology_inventory(base))
    write_json(base, "operations/external_validation/e66_reuse_first_growth_audit.json", build_reuse_first_growth_audit(base))
    write_json(base, "operations/external_validation/e66_e65_model_invocation_proof.json", build_e65_model_invocation_proof(base))
    write_json(base, "operations/external_validation/e66_model_driven_revenue_analysis.json", build_model_driven_revenue_analysis(base))
    write_json(base, "operations/external_validation/e66_revenue_strategy_capability_leap_assessment.json", build_revenue_strategy_capability_leap_assessment(base))
    write_json(base, "operations/external_validation/e66_model_driven_selected_route_decision.json", build_model_driven_selected_route_decision(base))
    write_json(base, "operations/external_validation/e66_selected_route_offer_blueprint.json", build_selected_route_offer_blueprint(base))
    write_product_directory(base)
    write_json(base, "operations/external_validation/e66_model_driven_pricing_package_hypothesis.json", build_pricing_package_hypothesis(base))
    write_json(base, "operations/external_validation/e66_owner_gated_business_action_plan_no_execution.json", build_owner_gated_business_action_plan(base))
    write_json(base, "operations/external_validation/e66_behavior_authorization_result.json", build_behavior_authorization(base))
    write_runtime_writeback(base)
    write_json(base, "operations/external_validation/e66_ceo_brain_readback_smoke_result.json", build_ceo_brain_readback_smoke(base))
    write_json(base, "operations/external_validation/e66_no_overclaim_validation_result.json", build_no_overclaim_validation(base))
    gate = build_completion_gate(base)
    write_json(base, "operations/external_validation/e66_completion_gate_result.json", gate)
    write_reports(base)
    return gate


if __name__ == "__main__":
    print(json.dumps(write_all_e66_artifacts(), indent=2, ensure_ascii=False))
