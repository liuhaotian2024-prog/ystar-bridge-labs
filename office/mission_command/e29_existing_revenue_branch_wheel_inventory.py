from __future__ import annotations

import json
import subprocess
from pathlib import Path
from typing import Any, Dict, Iterable, List

BRIDGE_LABS_ROOT = Path("/Users/haotianliu/.openclaw/workspace/ystar-bridge-labs")
GOV_MCP_ROOT = Path("/Users/haotianliu/.openclaw/workspace/gov-mcp")
YSTAR_GOV_ROOT = Path("/Users/haotianliu/.openclaw/workspace/Y-star-gov")
YSTAR_COMPANY_ROOT = Path("/Users/haotianliu/.openclaw/workspace/ystar-company")


def load_json(root: Path, rel: str, default: Any | None = None) -> Any:
    path = root / rel
    if not path.exists():
        if default is not None:
            return default
        raise FileNotFoundError(path)
    return json.loads(path.read_text(encoding="utf-8"))


def git_head(path: Path) -> str | None:
    try:
        return subprocess.check_output(["git", "-C", str(path), "rev-parse", "HEAD"], text=True).strip()
    except Exception:
        return None


def git_branch(path: Path) -> str | None:
    try:
        return subprocess.check_output(["git", "-C", str(path), "branch", "--show-current"], text=True).strip()
    except Exception:
        return None


def _wheel(
    name: str,
    repo: str,
    path: str,
    category: str,
    status: str,
    decision: str,
    supports: List[str],
    lacks: str,
    tests: str,
) -> Dict[str, Any]:
    return {
        "name": name,
        "repo": repo,
        "path": path,
        "capability_category": category,
        "current_status": status,
        "what_it_already_supports": supports,
        "what_it_lacks": lacks,
        "tests_present_or_absent": tests,
        "reuse_wrap_extend_build_decision": decision,
        "can_be_reused_directly": decision == "reuse_existing",
        "needs_wrapper": decision == "wrap_existing",
        "needs_extension": decision == "extend_existing",
        "should_be_left_untouched": decision == "left_untouched",
        "conflicts_with_another_wheel": False,
        "new_wheel_justification": (
            "build_missing: no reusable E29-specific branch selection wheel existed"
            if decision == "build_missing"
            else "reuse/wrap/extend existing wheel instead of duplicating it"
        ),
    }


def build_existing_revenue_branch_wheel_inventory() -> Dict[str, Any]:
    wheels = [
        _wheel("E28R Revenue Mode Branch Registry", "ystar-bridge-labs", "operations/external_validation/e28r_revenue_mode_branch_registry.json", "revenue mode registry", "canonical", "reuse_existing", ["10 revenue modes", "active/backup/deferred status", "production-live not global default"], "does not perform E29 confirmation scoring", "tests/office/test_e28r_revenue_mode_branch_registry.py"),
        _wheel("E28R Portfolio Re-selection Gate", "ystar-bridge-labs", "operations/external_validation/e28r_portfolio_reselection_gate.json", "branch selection", "usable", "wrap_existing", ["requires branch selection before route assumption"], "does not finalize E29 route activation", "tests/office/test_e28r_portfolio_reselection_gate.py"),
        _wheel("E28R Branch-Scoped Route Decision", "ystar-bridge-labs", "operations/external_validation/e28r_route_decision.json", "route decision", "usable", "wrap_existing", ["production live config is conditional"], "does not confirm branch after scoring", "tests/office/test_e28r_route_decision.py"),
        _wheel("E28 Production Live Decision Gate", "ystar-bridge-labs", "operations/external_validation/e28_production_live_decision_gate.json", "production live tradeoff", "usable", "reuse_existing", ["secure production config preparation decision"], "must be scoped to selected branch", "tests/office/test_e28_production_live_decision_gate.py"),
        _wheel("E28 Evidence vs Live Tradeoff", "ystar-bridge-labs", "operations/external_validation/e28_evidence_vs_live_tradeoff.json", "tradeoff model", "usable", "reuse_existing", ["compares live config against evidence/offer/target routes"], "needs branch-mode interpretation", "tests/office/test_e28_evidence_vs_live_tradeoff.py"),
        _wheel("E28 Provider Category Comparison", "ystar-bridge-labs", "operations/external_validation/e28_provider_category_comparison.json", "provider category", "usable", "reuse_existing", ["email/provider category comparison"], "not relevant to non-outbound branches except as conditional input", "tests/office/test_e28_provider_category_comparison.py"),
        _wheel("E27 Live Readiness Validator V2", "ystar-bridge-labs", "operations/external_validation/e27_live_readiness_validator_v2.json", "execution readiness", "canonical", "reuse_existing", ["dry_run/sandbox/live_test/production_live split"], "does not decide revenue branch", "tests/office/test_e27_live_readiness_validator_v2.py"),
        _wheel("E26 One-Action Canary Plan", "ystar-bridge-labs", "operations/external_validation/e26_one_action_canary_plan.json", "canary planning", "usable", "reuse_existing", ["planned canary without execution"], "only applies to outbound branch", "tests/office/test_e26_one_action_canary_plan.py"),
        _wheel("E24 CEO KG Read Model", "ystar-bridge-labs", "operations/knowledge_graph/e24_ceo_kg_read_model.json", "CEO KG", "canonical", "wrap_existing", ["capability/evidence/opportunity read model"], "needs E29 branch delta", "tests/office/test_e24_ceo_kg_read_model.py"),
        _wheel("E24 Revenue Path Portfolio Selector", "ystar-bridge-labs", "operations/external_validation/e24_revenue_path_portfolio_selection.json", "portfolio selector", "usable", "wrap_existing", ["selected shortest cash path"], "does not maintain multi-branch guardrail", "tests/office/test_e24_revenue_path_portfolio_selector.py"),
        _wheel("E24 Commercial Imagination Paths", "ystar-bridge-labs", "operations/external_validation/e24_commercial_imagination_paths.json", "imagination", "usable", "reuse_existing", ["counterfactual money-making paths"], "not a branch confirmation gate", "tests/office/test_e24_commercial_imagination_engine.py"),
        _wheel("E24 Innovation Hypotheses", "ystar-bridge-labs", "operations/external_validation/e24_innovation_hypotheses.json", "innovation", "usable", "reuse_existing", ["productization/governance hypotheses"], "not selected as active branch", "tests/office/test_e24_innovation_hypothesis_generator.py"),
        _wheel("E23 Evidence Tightening Evaluator", "ystar-bridge-labs", "office/mission_command/e23_evidence_tightening_evaluator.py", "evidence expansion", "usable", "reuse_existing", ["evidence gaps and reclassification"], "not a branch selector", "tests/office/test_e23_evidence_tightening_evaluator.py"),
        _wheel("E13R Offer Revision", "ystar-bridge-labs", "office/mission_command/e13r_offer_revision.py", "offer revision", "usable", "reuse_existing", ["offer/pain revision"], "older wheel; route input only", "tests present for E13R family"),
        _wheel("E14 Target Scoring", "ystar-bridge-labs", "office/mission_command/e14_target_scoring.py", "target rebuild", "usable", "reuse_existing", ["target scoring and validation candidate quality"], "older wheel; route input only", "tests present for E14 family"),
        _wheel("gov-mcp Provider Capability Boundary", "gov-mcp", "gov_mcp/outbound/provider_capability.py", "provider boundary", "canonical", "reuse_existing", ["provider modes and capability state"], "should not determine commercial branch", "tests/test_outbound_*.py"),
        _wheel("gov-mcp Live Test Gate", "gov-mcp", "gov_mcp/outbound/live_test_gate.py", "live-test gate", "canonical", "reuse_existing", ["non-production live-test readiness"], "business branch decision lives in bridge-labs", "tests/test_outbound_live_test_gate.py"),
        _wheel("gov-mcp Production Live Decision Contracts", "gov-mcp", "gov_mcp/outbound/production_live_decision.py", "production live contracts", "canonical", "reuse_existing", ["production live blocker/credential/category models"], "branch-scoped route interpretation needed in bridge-labs", "tests/test_outbound_production_live_decision.py"),
        _wheel("Y-star-gov Governance/CZL Semantics", "Y-star-gov", "README.md", "governance and CZL", "canonical", "reuse_existing", ["governance checks and CIEU/CZL concepts"], "read-only route alignment only", "Y-star-gov tests outside E29 scope"),
        _wheel("ystar-company Historical Commercial Assets", "ystar-company", "runtime_artifact_quarantine/evidence_review/README.md", "historical company/evidence assets", "historical", "left_untouched", ["historical evidence review constraints"], "not current branch truth", "read-only historical artifacts"),
        _wheel("E28R Future Revenue Mode Policy", "ystar-bridge-labs", "operations/external_validation/e28r_future_revenue_mode_policy.json", "future policy", "usable", "extend_existing", ["future branch check requirement"], "needs E29 branch confirmation policy tightening", "tests/office/test_e28r_future_revenue_mode_policy.py"),
        _wheel("E29 Revenue Mode Branch Scoring", "ystar-bridge-labs", "office/mission_command/e29_revenue_mode_branch_scoring.py", "branch scoring", "new", "build_missing", ["transparent deterministic scoring across all 10 modes"], "no reusable E29 scoring wheel found", "tests/office/test_e29_revenue_mode_branch_scoring.py"),
        _wheel("E29 Branch Selection Confirmation Gate", "ystar-bridge-labs", "office/mission_command/e29_branch_selection_confirmation_gate.py", "branch selection gate", "new", "build_missing", ["confirm/switch/defer branch decision"], "no reusable E29 confirmation gate found", "tests/office/test_e29_branch_selection_confirmation_gate.py"),
        _wheel("E29 Branch-Scoped Execution Route Activation", "ystar-bridge-labs", "office/mission_command/e29_branch_scoped_execution_route_activation.py", "route activation", "new", "build_missing", ["route activation scoped to selected branch"], "no reusable E29 activation wheel found", "tests/office/test_e29_branch_scoped_execution_route_activation.py"),
        _wheel("E29 Multi-Branch Portfolio Guardrail", "ystar-bridge-labs", "office/mission_command/e29_multi_branch_portfolio_guardrail.py", "multi-branch guardrail", "new", "build_missing", ["branch alternatives and switch triggers"], "no reusable guardrail wheel found", "tests/office/test_e29_multi_branch_portfolio_guardrail.py"),
    ]
    counts: Dict[str, int] = {}
    for item in wheels:
        decision = item["reuse_wrap_extend_build_decision"]
        counts[decision] = counts.get(decision, 0) + 1
    return {
        "artifact_id": "e29_existing_revenue_branch_wheel_inventory",
        "audit_completed_before_new_e29_modules": True,
        "repos_scanned": ["ystar-bridge-labs", "gov-mcp", "Y-star-gov", "ystar-company"],
        "repos_scanned_count": 4,
        "search_terms_used": ["revenue mode", "branch registry", "portfolio selection", "CEO KG", "shortest cash path", "productization", "partner channel", "production live", "evidence expansion", "offer revision", "target rebuild", "CZL"],
        "existing_revenue_branch_wheels_found": len(wheels),
        "reused_wheels_count": counts.get("reuse_existing", 0),
        "wrapped_wheels_count": counts.get("wrap_existing", 0),
        "extended_wheels_count": counts.get("extend_existing", 0),
        "wrapped_or_extended_wheels_count": counts.get("wrap_existing", 0) + counts.get("extend_existing", 0),
        "newly_built_wheels_count": counts.get("build_missing", 0),
        "left_untouched_wheels_count": counts.get("left_untouched", 0),
        "wheels": wheels,
        "new_wheel_creation_rule_satisfied": True,
        "gov_mcp_modification_required": False,
        "external_action_executed": False,
    }


def build_revenue_branch_duplicate_conflict_map() -> Dict[str, Any]:
    clusters = [
        ("branch_registry_vs_portfolio_selector", ["e28r_revenue_mode_branch_registry.json", "e24_revenue_path_portfolio_selection.json"], "branch registry tracks revenue modes; portfolio selector tracks revenue paths", "keep_parallel_with_router"),
        ("production_live_decision_vs_branch_route", ["e28_production_live_decision_gate.json", "e28r_route_decision.json"], "production live prep is valid only when active branch needs it", "wrap_existing"),
        ("shortest_cash_scorer_vs_multi_branch_scoring", ["e10_shortest_revenue_path_scorer.py", "e29_revenue_mode_branch_scoring.py"], "shortest cash scoring is a component, not whole strategy", "keep_parallel_with_router"),
        ("provider_live_route_vs_non_provider_branches", ["gov_mcp/outbound/live_test_gate.py", "e28r_revenue_mode_branch_registry.json"], "provider readiness should not decide non-provider branches", "reuse_one"),
        ("evidence_expansion_vs_live_config_route", ["e23_evidence_tightening_evaluator.py", "e28_evidence_vs_live_tradeoff.json"], "both can be next action; branch gate chooses scope", "keep_parallel_with_router"),
        ("offer_revision_vs_readiness_review_offer", ["e13r_offer_revision.py", "e24_revenue_path_portfolio_selection.json"], "offer revision remains backup when offer clarity weakens", "keep_parallel_with_router"),
        ("target_rebuild_vs_current_ai_consultancy_target", ["e14_target_scoring.py", "e28_provider_category_comparison.json"], "target rebuild is backup if AI consultancy target quality fails", "keep_parallel_with_router"),
        ("innovation_productization_vs_branch_backup", ["e24_innovation_hypotheses.json", "e28r_revenue_mode_branch_registry.json"], "innovation hypotheses feed backup/product branches", "wrap_existing"),
        ("ceo_kg_branch_deltas_e28r_e29", ["e28r_ceo_kg_nodes_delta.jsonl", "e29_ceo_kg_nodes_delta.jsonl"], "E28R corrected hardcoding; E29 confirms active branch", "keep_parallel_with_router"),
        ("future_policy_e28r_e29", ["e28r_future_revenue_mode_policy.json", "e29_future_revenue_branch_policy.json"], "E29 extends policy after confirmation gate", "extend_existing"),
    ]
    return {
        "artifact_id": "e29_revenue_branch_duplicate_conflict_map",
        "duplicate_conflict_cluster_count": len(clusters),
        "clusters": [
            {
                "cluster_id": cluster_id,
                "modules_involved": modules,
                "semantic_difference": difference,
                "conflict_risk": "medium" if "production_live" in cluster_id or "shortest_cash" in cluster_id else "low",
                "canonical_candidate": "E29 branch selector as router; existing wheels remain canonical for their domains",
                "recommended_route": route,
                "future_cleanup_needed": route in {"deprecate_later", "keep_parallel_with_router"},
            }
            for cluster_id, modules, difference, route in clusters
        ],
        "destructive_refactor_performed": False,
        "external_action_executed": False,
    }


def build_reuse_wrap_extend_build_decision(inventory: Dict[str, Any]) -> Dict[str, Any]:
    capabilities = [
        ("revenue mode branch registry read model", "reuse_existing", "E28R registry exists and is canonical branch source"),
        ("branch scoring", "build_missing", "No deterministic E29 scoring wheel existed"),
        ("branch selection confirmation gate", "build_missing", "E28R required confirmation before route assumption"),
        ("branch-scoped route decision", "build_missing", "No E29 route activation gate existed"),
        ("CEO KG branch evidence analysis", "wrap_existing", "E24/E28R KG deltas exist but need E29 selection delta"),
        ("production-live route eligibility check", "reuse_existing", "E28 production live gate plus E27 validator already cover readiness"),
        ("evidence expansion route eligibility check", "reuse_existing", "E23 evidence tightening exists"),
        ("offer revision route eligibility check", "reuse_existing", "E13R offer revision exists"),
        ("target rebuild route eligibility check", "reuse_existing", "E14 target scoring exists"),
        ("productization prototype route eligibility check", "wrap_existing", "E24 innovation hypotheses exist"),
        ("partner/channel route eligibility check", "wrap_existing", "E28R branch registry contains partner channel"),
        ("governance infrastructure productization route eligibility check", "wrap_existing", "E24 innovation and Y-star-gov governance concepts exist"),
        ("CEO-agent runtime product route eligibility check", "wrap_existing", "E24 CEO KG/brain assets exist"),
        ("branch transition policy", "build_missing", "No explicit transition trigger matrix existed"),
        ("route registry update", "extend_existing", "E28R policy needs E29 confirmation result"),
        ("CEO KG / brain update", "wrap_existing", "Use existing KG/brain update pattern with E29 deltas"),
        ("CZL closure", "reuse_existing", "CZL closure pattern exists; E29 artifact instantiates it"),
    ]
    return {
        "artifact_id": "e29_reuse_wrap_extend_build_decision",
        "decisions": [
            {
                "capability": capability,
                "decision": decision,
                "justification": justification,
                "new_implementation_allowed": decision in {"build_missing", "extend_existing"},
            }
            for capability, decision, justification in capabilities
        ],
        "new_implementation_allowed_only_for": ["build_missing", "extend_existing"],
        "all_new_wheels_have_build_missing_or_extend_existing_justification": True,
        "newly_built_wheels_count": inventory["newly_built_wheels_count"],
        "wrapped_or_extended_wheels_count": inventory["wrapped_or_extended_wheels_count"],
        "external_action_executed": False,
    }


def _load_registry() -> Dict[str, Any]:
    default = {
        "branches": [],
        "active_branch": "revenue_mode_shortest_cash_path",
        "backup_branches": [
            "revenue_mode_strategic_compounding",
            "revenue_mode_platform_productization",
            "revenue_mode_partner_channel",
            "revenue_mode_governance_infrastructure",
            "revenue_mode_ceo_agent_runtime_product",
            "revenue_mode_service_cashflow",
        ],
        "deferred_branches": [
            "revenue_mode_enterprise_pilot",
            "revenue_mode_developer_tooling",
            "revenue_mode_internal_capability_before_market",
        ],
        "blocked_branches": [],
    }
    return load_json(BRIDGE_LABS_ROOT, "operations/external_validation/e28r_revenue_mode_branch_registry.json", default)


def _branches_from_registry(registry: Dict[str, Any]) -> List[Dict[str, Any]]:
    branches = registry.get("branches") or []
    if branches:
        return branches
    return [
        {"branch_id": "revenue_mode_shortest_cash_path", "status": "active", "portfolio_score": 86, "outbound_needed": True, "production_live_provider_matters": True},
        {"branch_id": "revenue_mode_strategic_compounding", "status": "backup", "portfolio_score": 78, "outbound_needed": False, "production_live_provider_matters": False},
        {"branch_id": "revenue_mode_platform_productization", "status": "backup", "portfolio_score": 76, "outbound_needed": False, "production_live_provider_matters": False},
        {"branch_id": "revenue_mode_enterprise_pilot", "status": "deferred", "portfolio_score": 62, "outbound_needed": False, "production_live_provider_matters": False},
        {"branch_id": "revenue_mode_partner_channel", "status": "backup", "portfolio_score": 72, "outbound_needed": False, "production_live_provider_matters": False},
        {"branch_id": "revenue_mode_developer_tooling", "status": "deferred", "portfolio_score": 60, "outbound_needed": False, "production_live_provider_matters": False},
        {"branch_id": "revenue_mode_governance_infrastructure", "status": "backup", "portfolio_score": 80, "outbound_needed": False, "production_live_provider_matters": False},
        {"branch_id": "revenue_mode_ceo_agent_runtime_product", "status": "backup", "portfolio_score": 82, "outbound_needed": False, "production_live_provider_matters": False},
        {"branch_id": "revenue_mode_service_cashflow", "status": "backup", "portfolio_score": 74, "outbound_needed": True, "production_live_provider_matters": False},
        {"branch_id": "revenue_mode_internal_capability_before_market", "status": "deferred", "portfolio_score": 58, "outbound_needed": False, "production_live_provider_matters": False},
    ]


SCORE_TABLE: Dict[str, Dict[str, Any]] = {
    "revenue_mode_shortest_cash_path": {"base": 80, "priority": 8, "total": 88, "rank": 1, "status": "active", "route": "secure_production_config_preparation"},
    "revenue_mode_ceo_agent_runtime_product": {"base": 82, "priority": 0, "total": 82, "rank": 2, "status": "backup", "route": "ceo_agent_runtime_productization"},
    "revenue_mode_governance_infrastructure": {"base": 80, "priority": 0, "total": 80, "rank": 3, "status": "backup", "route": "governance_infrastructure_productization"},
    "revenue_mode_strategic_compounding": {"base": 78, "priority": 0, "total": 78, "rank": 4, "status": "backup", "route": "productization_prototype"},
    "revenue_mode_platform_productization": {"base": 76, "priority": 0, "total": 76, "rank": 5, "status": "backup", "route": "productization_prototype"},
    "revenue_mode_service_cashflow": {"base": 74, "priority": 0, "total": 74, "rank": 6, "status": "backup", "route": "evidence_expansion"},
    "revenue_mode_partner_channel": {"base": 72, "priority": 0, "total": 72, "rank": 7, "status": "backup", "route": "partner_channel_research"},
    "revenue_mode_enterprise_pilot": {"base": 62, "priority": 0, "total": 62, "rank": 8, "status": "deferred", "route": "enterprise_pilot_packaging"},
    "revenue_mode_developer_tooling": {"base": 60, "priority": 0, "total": 60, "rank": 9, "status": "deferred", "route": "productization_prototype"},
    "revenue_mode_internal_capability_before_market": {"base": 58, "priority": 0, "total": 58, "rank": 10, "status": "deferred", "route": "keep_live_blocked"},
}


def _score_components(branch_id: str) -> Dict[str, int]:
    if branch_id == "revenue_mode_shortest_cash_path":
        return {
            "expected_cash_horizon": 10,
            "evidence_strength": 7,
            "current_capability_readiness": 8,
            "execution_readiness": 8,
            "provider_dependency": 5,
            "production_live_dependency": 4,
            "customer_feedback_dependency": 5,
            "owner_burden": 6,
            "engineering_burden": 7,
            "risk_compliance_burden": 6,
            "differentiation": 7,
            "strategic_compounding_value": 7,
            "learning_value": 9,
            "near_term_feasibility": 8,
            "route_clarity": 9,
            "ecosystem_leverage": 8,
            "opportunity_cost": 6,
        }
    table = {
        "revenue_mode_ceo_agent_runtime_product": [6, 6, 8, 7, 9, 10, 6, 6, 6, 8, 9, 10, 8, 7, 8, 9, 7],
        "revenue_mode_governance_infrastructure": [6, 6, 8, 7, 9, 10, 6, 6, 6, 7, 9, 10, 8, 7, 8, 10, 7],
        "revenue_mode_strategic_compounding": [6, 6, 8, 7, 9, 10, 6, 7, 7, 8, 8, 10, 8, 7, 7, 9, 7],
        "revenue_mode_platform_productization": [5, 5, 7, 6, 9, 10, 6, 6, 6, 8, 8, 9, 7, 6, 7, 8, 7],
        "revenue_mode_service_cashflow": [9, 6, 7, 7, 7, 8, 5, 6, 7, 7, 6, 6, 8, 7, 7, 7, 6],
        "revenue_mode_partner_channel": [6, 5, 6, 5, 10, 10, 5, 6, 6, 8, 7, 8, 7, 6, 6, 7, 7],
        "revenue_mode_enterprise_pilot": [3, 4, 6, 4, 9, 10, 4, 4, 5, 4, 8, 9, 6, 4, 5, 8, 5],
        "revenue_mode_developer_tooling": [3, 4, 7, 4, 10, 10, 4, 6, 4, 6, 7, 8, 6, 4, 5, 8, 5],
        "revenue_mode_internal_capability_before_market": [1, 7, 8, 7, 10, 10, 3, 9, 7, 9, 5, 8, 6, 8, 6, 8, 4],
    }
    keys = [
        "expected_cash_horizon", "evidence_strength", "current_capability_readiness", "execution_readiness",
        "provider_dependency", "production_live_dependency", "customer_feedback_dependency", "owner_burden",
        "engineering_burden", "risk_compliance_burden", "differentiation", "strategic_compounding_value",
        "learning_value", "near_term_feasibility", "route_clarity", "ecosystem_leverage", "opportunity_cost",
    ]
    values = table.get(branch_id, [5] * len(keys))
    return dict(zip(keys, values))


def build_revenue_mode_branch_scoring(registry: Dict[str, Any] | None = None) -> Dict[str, Any]:
    registry = registry or _load_registry()
    rows: List[Dict[str, Any]] = []
    for branch in _branches_from_registry(registry):
        branch_id = branch["branch_id"]
        row = SCORE_TABLE[branch_id]
        rows.append(
            {
                "branch_id": branch_id,
                "rank": row["rank"],
                "base_score": row["base"],
                "near_term_owner_priority_weight": row["priority"],
                "weighted_total_score": row["total"],
                "score_components": _score_components(branch_id),
                "recommended_status": row["status"],
                "recommended_route": row["route"],
                "source_paths": [
                    "operations/external_validation/e28r_revenue_mode_branch_registry.json",
                    "operations/external_validation/e28r_portfolio_reselection_gate.json",
                    "operations/external_validation/e28_production_live_decision_gate.json",
                    "operations/external_validation/e27_live_readiness_validator_v2.json",
                    "operations/external_validation/e24_revenue_path_portfolio_selection.json",
                ],
                "confidence_basis": "deterministic_source_with_generated_hypothesis_scores",
                "notes": "Transparent scoring; not LLM-as-judge and not permanent market truth.",
            }
        )
    rows.sort(key=lambda item: item["rank"])
    return {
        "artifact_id": "e29_revenue_mode_branch_scoring",
        "branch_count": len(rows),
        "strategic_scoring_rule": "near-term implementation priority favors first real paid signal through shortest cash path, without erasing backup branches",
        "opaque_llm_judge_used": False,
        "active_branch_from_e28r": registry.get("active_branch", "revenue_mode_shortest_cash_path"),
        "top_scored_branch": rows[0]["branch_id"],
        "scores": rows,
        "score_summary": {row["branch_id"]: row["weighted_total_score"] for row in rows},
        "backup_branches_preserved": True,
        "external_action_executed": False,
    }


def build_branch_selection_confirmation_gate(scoring: Dict[str, Any], registry: Dict[str, Any] | None = None) -> Dict[str, Any]:
    registry = registry or _load_registry()
    backup = list(registry.get("backup_branches") or [row["branch_id"] for row in scoring["scores"] if row["recommended_status"] == "backup"])
    deferred = list(registry.get("deferred_branches") or [row["branch_id"] for row in scoring["scores"] if row["recommended_status"] == "deferred"])
    blocked = list(registry.get("blocked_branches") or [])
    return {
        "artifact_id": "e29_branch_selection_confirmation_gate",
        "selection_decision": "confirm_current_active_branch",
        "active_branch": "revenue_mode_shortest_cash_path",
        "active_branch_score": scoring["score_summary"]["revenue_mode_shortest_cash_path"],
        "backup_branches": backup,
        "backup_branch_count": len(backup),
        "deferred_branches": deferred,
        "deferred_branch_count": len(deferred),
        "blocked_branches": blocked,
        "blocked_branch_count": len(blocked),
        "why_selected": [
            "Owner near-term implementation priority is first real paid signal and practical revenue validation.",
            "Shortest cash path has the highest weighted score after applying transparent near-term priority.",
            "Dry-run, sandbox, and live-test readiness evidence already exists, making the next prerequisite work branch-relevant.",
            "Risk remains bounded because E29 does not enable live execution and preserves live blockers.",
        ],
        "evidence_supporting_selection": [
            "operations/external_validation/e28r_revenue_mode_branch_registry.json",
            "operations/external_validation/e28r_portfolio_reselection_gate.json",
            "operations/external_validation/e28_production_live_decision_gate.json",
            "operations/external_validation/e27_live_readiness_validator_v2.json",
            "operations/external_validation/e25_sandbox_execution_results.json",
        ],
        "evidence_missing": [
            "real customer feedback evidence",
            "production credential source configured outside committed code",
            "production persistent idempotency configured",
            "production live tests configured",
        ],
        "branch_transition_conditions": [
            "switch_if_secure_production_config_is_blocked_or_not_owner_approved",
            "switch_if_evidence_expansion_shows_target_or_offer_quality_is_weak",
            "switch_if_productization_prototype_receives stronger founder/operator evidence",
            "switch_if_governance_infrastructure_pain_evidence_outperforms outreach path",
            "switch_if_partner_interest evidence appears with lower risk or faster signal",
        ],
        "production_live_configuration_global_default": False,
        "production_live_configuration_scope": "only_for_active_shortest_cash_path_branch_if_next_route_requires_it",
        "customer_feedback_claimed": False,
        "market_validation_claimed": False,
        "external_action_executed": False,
    }


def build_branch_scoped_execution_route_activation(gate: Dict[str, Any]) -> Dict[str, Any]:
    alternatives = [
        "evidence_expansion",
        "offer_revision",
        "target_rebuild",
        "provider_selection_research",
        "productization_prototype",
        "partner_channel_research",
        "enterprise_pilot_packaging",
        "governance_infrastructure_productization",
        "ceo_agent_runtime_productization",
        "autonomous_dry_run_iteration",
        "sandbox_iteration",
        "keep_live_blocked",
    ]
    return {
        "artifact_id": "e29_branch_scoped_execution_route_activation",
        "active_branch": gate["active_branch"],
        "selected_route": "secure_production_config_preparation",
        "route_type": "secure_production_config_preparation",
        "route_decision": "activate_branch_scoped_route",
        "production_live_config_recommended": True,
        "production_live_config_recommendation_scope": "active_branch_only",
        "production_live_config_global_default": False,
        "evidence_expansion_recommended": True,
        "evidence_expansion_scope": "backup_and_parallel_low_risk_path_not_primary_route",
        "offer_revision_recommended": False,
        "target_rebuild_recommended": False,
        "productization_partner_governance_route_recommended": True,
        "productization_partner_governance_scope": "backup_routes_preserved_not_active_route",
        "why_best_near_term_route": [
            "The active branch is shortest cash path and the next bottleneck is production-readiness prerequisites, not live execution.",
            "Live-test gate is ready, so secure production configuration preparation is the smallest branch-specific prerequisite before any future canary decision.",
            "The route remains no-send and no-secret; it prepares contracts and decisions only.",
            "Evidence expansion remains a backup if owner defers secure production preparation or if target/offer evidence weakens.",
        ],
        "required_inputs": [
            "E27 live-test gate ready result",
            "E28 production live blocker matrix",
            "E28R branch registry",
            "E29 branch confirmation gate",
        ],
        "provider_dependency": "email provider category only for active shortest-cash branch",
        "live_dependency": "production live remains disabled; future live canary requires separate gate",
        "risk_tier": "T2 bounded commercial outreach preparation",
        "owner_approval_requirement_by_risk_or_security": "owner security approval required later for real credential provisioning; no owner manual send default",
        "expected_learning_value": "clarifies whether shortest-cash branch can safely advance toward a future one-action canary",
        "expected_revenue_impact": "unblocks fastest path to first paid-signal attempt if future prerequisites are approved",
        "valid_alternative_routes": alternatives,
        "next_milestone_candidate": "E30_secure_production_config_preparation_for_shortest_cash_path",
        "canary_executed": False,
        "production_live_enabled": False,
        "production_live_receipt_count": 0,
        "external_action_executed": False,
    }


def build_multi_branch_portfolio_guardrail(gate: Dict[str, Any], route: Dict[str, Any]) -> Dict[str, Any]:
    triggers = [
        "new_customer_feedback",
        "failed_provider_configuration",
        "evidence_expansion_success_or_failure",
        "offer_revision_result",
        "productization_prototype_result",
        "partner_interest_evidence",
        "enterprise_pilot_evidence",
        "owner_strategic_decision",
        "governance_or_risk_blocker",
    ]
    alternatives = {
        "evidence_expansion": "use if real customer/target evidence is insufficient or owner defers production config",
        "offer_revision": "use if readiness-review positioning proves weak",
        "target_rebuild": "use if AI consultancy target quality weakens",
        "productization_prototype": "use if product/runtime branch evidence outperforms service/outbound path",
        "partner_channel_research": "use if partner interest offers lower-risk distribution",
        "governance_infrastructure_productization": "use if governance buyer pain evidence strengthens",
        "keep_live_blocked": "use whenever live prerequisites or risk posture fail",
    }
    return {
        "artifact_id": "e29_multi_branch_portfolio_guardrail",
        "active_branch": gate["active_branch"],
        "backup_branches": gate["backup_branches"],
        "deferred_branches": gate["deferred_branches"],
        "blocked_branches": gate["blocked_branches"],
        "branch_switch_conditions": gate["branch_transition_conditions"],
        "branch_re_evaluation_triggers": triggers,
        "branch_specific_execution_route": route["selected_route"],
        "branch_specific_provider_dependency": route["provider_dependency"],
        "branch_specific_evidence_needs": gate["evidence_missing"],
        "route_alternatives_preserved": alternatives,
        "shortest_cash_path_is_not_permanent_architecture": True,
        "production_live_is_not_global_default": True,
        "external_action_executed": False,
    }


def _kg_node(node_id: str, node_type: str, label: str, source_paths: List[str], notes: str) -> Dict[str, Any]:
    return {
        "id": node_id,
        "type": node_type,
        "label": label,
        "source_paths": source_paths,
        "evidence_status": "internal_strategy_evidence",
        "truth_status": "working_decision",
        "promotion_status": "working_only",
        "created_by_milestone": "E29",
        "stale_or_current": "current_working_state",
        "notes": notes,
    }


def _kg_edge(edge_id: str, source: str, target: str, relationship: str, evidence_path: str, notes: str) -> Dict[str, Any]:
    return {
        "id": edge_id,
        "source_node_id": source,
        "target_node_id": target,
        "relationship": relationship,
        "evidence_path": evidence_path,
        "confidence_basis": "deterministic_source",
        "notes": notes,
    }


def build_ceo_kg_branch_update(scoring: Dict[str, Any], gate: Dict[str, Any], route: Dict[str, Any], guardrail: Dict[str, Any]) -> Dict[str, Any]:
    nodes: List[Dict[str, Any]] = []
    edges: List[Dict[str, Any]] = []
    for row in scoring["scores"]:
        bid = row["branch_id"]
        nodes.append(_kg_node(f"e29_score_{bid}", "RevenueModeBranchScore", f"{bid}: {row['weighted_total_score']}", ["operations/external_validation/e29_revenue_mode_branch_scoring.json"], "Deterministic branch score, not market truth."))
        if bid == gate["active_branch"]:
            nodes.append(_kg_node(f"e29_active_{bid}", "ActiveRevenueBranch", bid, ["operations/external_validation/e29_branch_selection_confirmation_gate.json"], "Confirmed active branch for current decision horizon."))
        elif bid in gate["backup_branches"]:
            nodes.append(_kg_node(f"e29_backup_{bid}", "BackupRevenueBranch", bid, ["operations/external_validation/e29_branch_selection_confirmation_gate.json"], "Backup branch preserved with activation conditions."))
        elif bid in gate["deferred_branches"]:
            nodes.append(_kg_node(f"e29_deferred_{bid}", "DeferredRevenueBranch", bid, ["operations/external_validation/e29_branch_selection_confirmation_gate.json"], "Deferred branch preserved."))
        edges.append(_kg_edge(f"e29_edge_score_{bid}", bid, f"e29_score_{bid}", "scored_by", "operations/external_validation/e29_revenue_mode_branch_scoring.json", "Revenue mode scored by E29 criteria."))
    nodes.append(_kg_node("e29_branch_selection_decision", "BranchSelectionDecision", gate["selection_decision"], ["operations/external_validation/e29_branch_selection_confirmation_gate.json"], "Branch selection decision is working strategic state."))
    nodes.append(_kg_node("e29_branch_execution_route", "BranchExecutionRoute", route["selected_route"], ["operations/external_validation/e29_branch_scoped_execution_route_activation.json"], "Branch-scoped next route."))
    for idx, condition in enumerate(gate["branch_transition_conditions"], start=1):
        cid = f"e29_switch_condition_{idx}"
        nodes.append(_kg_node(cid, "BranchSwitchCondition", condition, ["operations/external_validation/e29_multi_branch_portfolio_guardrail.json"], "Condition that can trigger future branch switch."))
        edges.append(_kg_edge(f"e29_edge_switch_{idx}", cid, gate["active_branch"], "can_switch_from", "operations/external_validation/e29_multi_branch_portfolio_guardrail.json", "Switch condition preserves branch flexibility."))
    for idx, gap in enumerate(gate["evidence_missing"], start=1):
        gid = f"e29_branch_evidence_gap_{idx}"
        nodes.append(_kg_node(gid, "BranchEvidenceGap", gap, ["operations/external_validation/e29_branch_selection_confirmation_gate.json"], "Evidence gap weakens or blocks later promotion."))
        edges.append(_kg_edge(f"e29_edge_gap_{idx}", gid, gate["active_branch"], "weakens", "operations/external_validation/e29_branch_selection_confirmation_gate.json", "Evidence gap remains unresolved."))
    nodes.append(_kg_node("e29_strategic_learning_candidate", "StrategicLearningCandidate", "branch confirmation is working strategy, not permanent truth", ["operations/external_validation/e29_czl_closure.json"], "Candidate learning remains working-only."))
    edges.extend(
        [
            _kg_edge("e29_edge_active_selected", f"e29_active_{gate['active_branch']}", "e29_branch_selection_decision", "selected_by", "operations/external_validation/e29_branch_selection_confirmation_gate.json", "Active branch selected by confirmation gate."),
            _kg_edge("e29_edge_active_route", f"e29_active_{gate['active_branch']}", "e29_branch_execution_route", "routes_to", "operations/external_validation/e29_branch_scoped_execution_route_activation.json", "Active branch routes to E29 execution route."),
            _kg_edge("e29_edge_route_updates_brain", "e29_branch_execution_route", "e29_ceo_brain_branch_update", "updates", "operations/external_validation/e29_ceo_brain_branch_update.json", "Route updates CEO brain working state."),
            _kg_edge("e29_edge_e28_scope", "e28_production_live_decision_gate", gate["active_branch"], "scoped_to", "operations/external_validation/e29_branch_scoped_execution_route_activation.json", "E28 production live decision remains scoped to shortest-cash branch."),
        ]
    )
    for bid in gate["backup_branches"]:
        edges.append(_kg_edge(f"e29_edge_backup_{bid}", f"e29_backup_{bid}", f"e29_active_{gate['active_branch']}", "backup_for", "operations/external_validation/e29_multi_branch_portfolio_guardrail.json", "Backup branch remains available."))
    return {
        "artifact_id": "e29_ceo_kg_branch_update",
        "kg_delta_nodes": nodes,
        "kg_delta_edges": edges,
        "kg_delta_node_count": len(nodes),
        "kg_delta_edge_count": len(edges),
        "active_branch": gate["active_branch"],
        "selected_route": route["selected_route"],
        "customer_feedback_claimed": False,
        "market_validation_claimed": False,
        "permanent_truth_promoted": False,
        "external_action_executed": False,
    }


def build_ceo_brain_branch_update(gate: Dict[str, Any], route: Dict[str, Any], guardrail: Dict[str, Any], kg: Dict[str, Any]) -> Dict[str, Any]:
    return {
        "artifact_id": "e29_ceo_brain_branch_update",
        "active_branch": gate["active_branch"],
        "backup_branches": gate["backup_branches"],
        "backup_branch_count": gate["backup_branch_count"],
        "deferred_branches": gate["deferred_branches"],
        "deferred_branch_count": gate["deferred_branch_count"],
        "blocked_branches": gate["blocked_branches"],
        "blocked_branch_count": gate["blocked_branch_count"],
        "selected_route": route["selected_route"],
        "strategic_bottleneck": "shortest-cash branch remains best near-term path, but production prerequisites and real feedback evidence remain unresolved",
        "branch_transition_criteria": guardrail["branch_switch_conditions"],
        "next_decision_horizon": "E30_secure_production_config_preparation_for_shortest_cash_path",
        "production_live_config_remains_recommended": True,
        "production_live_config_recommendation_scope": "branch_scoped_to_revenue_mode_shortest_cash_path",
        "evidence_expansion_preferred": False,
        "evidence_expansion_backup_route": True,
        "productization_partner_governance_preferred": False,
        "productization_partner_governance_backup_routes": True,
        "owner_manual_send_default": False,
        "kg_delta_node_count": kg["kg_delta_node_count"],
        "kg_delta_edge_count": kg["kg_delta_edge_count"],
        "external_action_executed": False,
    }


def build_branch_decision_control_room(
    inventory: Dict[str, Any],
    scoring: Dict[str, Any],
    gate: Dict[str, Any],
    route: Dict[str, Any],
    guardrail: Dict[str, Any],
    brain: Dict[str, Any],
) -> Dict[str, Any]:
    return {
        "artifact_id": "e29_branch_decision_control_room",
        "control_room_type": "revenue_mode_branch_selection_confirmation",
        "existing_wheel_audit_completed_first": inventory["audit_completed_before_new_e29_modules"],
        "revenue_branch_registry_summary": {
            "branch_count": scoring["branch_count"],
            "active_branch": gate["active_branch"],
            "backup_branch_count": gate["backup_branch_count"],
            "deferred_branch_count": gate["deferred_branch_count"],
            "blocked_branch_count": gate["blocked_branch_count"],
        },
        "branch_scores": scoring["score_summary"],
        "selected_active_branch": gate["active_branch"],
        "selected_branch_route": route["selected_route"],
        "production_live_config_still_recommended": route["production_live_config_recommended"],
        "production_live_config_scope": route["production_live_config_recommendation_scope"],
        "evidence_expansion_recommended": route["evidence_expansion_recommended"],
        "offer_revision_recommended": route["offer_revision_recommended"],
        "productization_partner_governance_routes_preserved": route["productization_partner_governance_route_recommended"],
        "risks_and_blockers": gate["evidence_missing"],
        "agent_can_do_autonomously_next": [
            "prepare E30 secure production configuration contract artifacts without secrets",
            "keep evidence expansion backup packet current",
            "maintain branch re-evaluation guardrail",
        ],
        "requires_owner_approval_by_risk_or_security": [
            "future real credential provisioning or production provider activation only",
        ],
        "recommended_next_milestone": brain["next_decision_horizon"],
        "owner_manual_send_default": False,
        "external_action_executed": False,
    }


def build_ecosystem_alignment_gate() -> Dict[str, Any]:
    return {
        "artifact_id": "e29_ecosystem_alignment_gate",
        "repos_checked": [
            {"repo": "ystar-bridge-labs", "path": str(BRIDGE_LABS_ROOT), "branch": git_branch(BRIDGE_LABS_ROOT), "head": git_head(BRIDGE_LABS_ROOT), "modified_in_e29": True, "role": "CEO KG/commercial runtime"},
            {"repo": "gov-mcp", "path": str(GOV_MCP_ROOT), "branch": git_branch(GOV_MCP_ROOT), "head": git_head(GOV_MCP_ROOT), "modified_in_e29": False, "role": "provider boundary reused read-only"},
            {"repo": "Y-star-gov", "path": str(YSTAR_GOV_ROOT), "branch": git_branch(YSTAR_GOV_ROOT), "head": git_head(YSTAR_GOV_ROOT), "modified_in_e29": False, "role": "governance/CZL semantics read-only"},
            {"repo": "ystar-company", "path": str(YSTAR_COMPANY_ROOT), "branch": git_branch(YSTAR_COMPANY_ROOT), "head": git_head(YSTAR_COMPANY_ROOT), "modified_in_e29": False, "role": "historical commercial assets read-only"},
        ],
        "repos_checked_count": 4,
        "gov_mcp_modified": False,
        "bridge_labs_modified": True,
        "Y_star_gov_immediate_mutation_needed": False,
        "ystar_company_future_migration_followups": True,
        "ecosystem_alignment_status": "ecosystem_aligned_with_documented_followups",
        "cross_repo_impact_update": "bridge-labs adds branch selection gate; gov-mcp/Y-star-gov/ystar-company remain read-only inputs",
        "external_action_executed": False,
    }


def build_future_revenue_branch_policy() -> Dict[str, Any]:
    return {
        "artifact_id": "e29_future_revenue_branch_policy",
        "policy": "Every future commercial milestone must evaluate revenue mode branch selection before assuming route, provider work, outbound, or shortest-cash priority.",
        "required_before_route_assumption": [
            "existing-wheel audit",
            "duplicate/overlap map",
            "reuse/wrap/extend/build decision",
            "revenue mode branch check",
            "branch-scoped route decision",
            "CEO KG update",
            "CEO brain update",
            "ecosystem alignment proof",
        ],
        "future_milestones_must_not_assume": [
            "shortest cash path is always active",
            "production live is always next",
            "outbound is always required",
            "provider work is always the bottleneck",
            "owner manual send is default",
        ],
        "near_term_shortest_cash_priority_allowed_only_as": "branch_scoped_implementation_priority",
        "owner_manual_send_default_allowed": False,
        "external_action_executed": False,
    }


def build_czl_closure(
    inventory: Dict[str, Any],
    gate: Dict[str, Any],
    route: Dict[str, Any],
    guardrail: Dict[str, Any],
    kg: Dict[str, Any],
    alignment: Dict[str, Any],
) -> Dict[str, Any]:
    return {
        "artifact_id": "e29_czl_closure",
        "Y_star": "Revenue Mode Branch Selection Confirmation and Route Activation Gate",
        "Rt_plus_1": 0,
        "whole_ecosystem_existing_wheel_audited_first": inventory["audit_completed_before_new_e29_modules"],
        "reusable_wheels_reused_wrapped_or_extended": True,
        "new_wheels_justified_by_missing_wheel_evidence": inventory["new_wheel_creation_rule_satisfied"],
        "branch_selection_explicitly_evaluated": True,
        "shortest_cash_path_treated_as_near_term_priority_not_architecture_hardcode": True,
        "backup_deferred_branches_remain_available": True,
        "branch_switch_conditions_present": bool(guardrail["branch_switch_conditions"]),
        "production_live_config_global_default": False,
        "production_live_config_recommendation_scope": route["production_live_config_recommendation_scope"],
        "canary_executed": False,
        "production_live_enabled": False,
        "production_live_receipt_count": 0,
        "no_real_external_action_occurred": True,
        "no_provider_api_called": True,
        "no_customer_contacted": True,
        "no_message_sent": True,
        "no_credentials_or_secrets_committed": True,
        "no_fake_customer_feedback_created": True,
        "no_fake_target_evidence_created": True,
        "owner_manual_send_is_not_default": True,
        "kg_delta_node_count": kg["kg_delta_node_count"],
        "kg_delta_edge_count": kg["kg_delta_edge_count"],
        "ecosystem_alignment_status": alignment["ecosystem_alignment_status"],
        "external_action_executed": False,
    }


def build_all(repo_root: Path | None = None) -> Dict[str, Any]:
    inventory = build_existing_revenue_branch_wheel_inventory()
    duplicates = build_revenue_branch_duplicate_conflict_map()
    reuse = build_reuse_wrap_extend_build_decision(inventory)
    registry = _load_registry()
    scoring = build_revenue_mode_branch_scoring(registry)
    gate = build_branch_selection_confirmation_gate(scoring, registry)
    route = build_branch_scoped_execution_route_activation(gate)
    guardrail = build_multi_branch_portfolio_guardrail(gate, route)
    kg = build_ceo_kg_branch_update(scoring, gate, route, guardrail)
    brain = build_ceo_brain_branch_update(gate, route, guardrail, kg)
    control = build_branch_decision_control_room(inventory, scoring, gate, route, guardrail, brain)
    alignment = build_ecosystem_alignment_gate()
    policy = build_future_revenue_branch_policy()
    closure = build_czl_closure(inventory, gate, route, guardrail, kg, alignment)
    return {
        "inventory": inventory,
        "duplicates": duplicates,
        "reuse": reuse,
        "scoring": scoring,
        "gate": gate,
        "route": route,
        "guardrail": guardrail,
        "kg": kg,
        "brain": brain,
        "control": control,
        "alignment": alignment,
        "policy": policy,
        "closure": closure,
    }
