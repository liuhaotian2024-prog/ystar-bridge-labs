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


def wheel(name: str, repo: str, path: str, category: str, decision: str, supports: List[str], gap: str) -> Dict[str, Any]:
    return {
        "name": name,
        "repo": repo,
        "path": path,
        "capability_category": category,
        "reuse_decision": decision,
        "what_it_already_supports": supports,
        "gap_requiring_e28r": gap,
        "new_wheel_justification": "existing route is incomplete for branch-level revenue mode selection" if decision == "build_missing" else "reuse or wrap existing wheel",
    }


def build_existing_revenue_mode_wheel_inventory() -> Dict[str, Any]:
    wheels = [
        wheel("E24 CEO KG", "ystar-bridge-labs", "operations/knowledge_graph/e24_ceo_kg_nodes.jsonl", "CEO KG", "wrap_existing", ["source-bound revenue paths", "legacy assets", "innovation hypotheses"], "needs branch-mode delta"),
        wheel("E24 revenue portfolio selector", "ystar-bridge-labs", "operations/external_validation/e24_revenue_path_portfolio_selection.json", "portfolio selector", "wrap_existing", ["shortest cash path selection"], "does not express non-shortest-cash branch registry"),
        wheel("E24 commercial imagination paths", "ystar-bridge-labs", "operations/external_validation/e24_commercial_imagination_paths.json", "commercial imagination", "reuse_existing", ["alternative money-making hypotheses"], "not promoted into branch registry"),
        wheel("E24 innovation hypotheses", "ystar-bridge-labs", "operations/external_validation/e24_innovation_hypotheses.json", "innovation", "reuse_existing", ["productization/governance ideas"], "not selected as branch modes"),
        wheel("E28 production live decision gate", "ystar-bridge-labs", "operations/external_validation/e28_production_live_decision_gate.json", "production live decision", "wrap_existing", ["production config preparation recommendation"], "needs branch-scoped interpretation"),
        wheel("E28 evidence vs live tradeoff", "ystar-bridge-labs", "operations/external_validation/e28_evidence_vs_live_tradeoff.json", "route tradeoff", "wrap_existing", ["live config vs evidence/offer/target comparison"], "overweighted shortest cash path"),
        wheel("E28 CEO brain update", "ystar-bridge-labs", "operations/external_validation/e28_ceo_brain_portfolio_update.json", "CEO brain", "wrap_existing", ["selected path and next horizon"], "needs active/backup/deferred branch state"),
        wheel("E28 provider category comparison", "ystar-bridge-labs", "operations/external_validation/e28_provider_category_comparison.json", "provider category", "reuse_existing", ["email provider selected for outbound canary"], "branch dependency must be conditional"),
        wheel("E23 evidence tightening", "ystar-bridge-labs", "office/mission_command/e23_evidence_tightening_evaluator.py", "evidence expansion", "reuse_existing", ["evidence gap routing"], "alternative route input"),
        wheel("E13R offer revision", "ystar-bridge-labs", "office/mission_command/e13r_offer_revision.py", "offer revision", "reuse_existing", ["offer/pain revision"], "alternative route input"),
        wheel("E14 target scoring", "ystar-bridge-labs", "office/mission_command/e14_target_scoring.py", "target rebuild", "reuse_existing", ["target score/readiness"], "alternative route input"),
        wheel("gov-mcp provider boundary", "gov-mcp", "gov_mcp/outbound/live_test_gate.py", "provider boundary", "reuse_existing", ["live-test/production readiness split"], "should not determine business branch"),
        wheel("Y-star-gov governance semantics", "Y-star-gov", "README.md", "governance/CZL", "reuse_existing", ["closure and governance concepts"], "read-only alignment source"),
        wheel("ystar-company historical commercial assets", "ystar-company", "sales/customer_pipeline.md", "historical assets", "left_untouched", ["historical market context"], "not a branch selector"),
        wheel("Revenue Mode Branch Registry", "ystar-bridge-labs", "office/mission_command/e28r_revenue_mode_branch_registry.py", "revenue mode branch registry", "build_missing", ["branch-level revenue strategy modes"], "no existing branch registry wheel found"),
        wheel("Portfolio Re-selection Gate", "ystar-bridge-labs", "office/mission_command/e28r_portfolio_reselection_gate.py", "branch selection", "build_missing", ["select active branch before route"], "no existing branch re-selection gate found"),
        wheel("Anti-hardcoding route policy", "ystar-bridge-labs", "office/mission_command/e28r_route_decision.py", "route policy", "build_missing", ["production live config is conditional"], "no existing anti-hardcoding correction layer found"),
    ]
    counts: Dict[str, int] = {}
    for item in wheels:
        counts[item["reuse_decision"]] = counts.get(item["reuse_decision"], 0) + 1
    return {
        "artifact_id": "e28r_existing_revenue_mode_wheel_inventory",
        "audit_completed_before_new_e28r_modules": True,
        "repos_scanned": ["ystar-bridge-labs", "gov-mcp", "Y-star-gov", "ystar-company"],
        "repos_scanned_count": 4,
        "existing_revenue_mode_wheels_found": len(wheels),
        "reused_wheels_count": counts.get("reuse_existing", 0),
        "wrapped_wheels_count": counts.get("wrap_existing", 0),
        "extended_wheels_count": 0,
        "wrapped_or_extended_wheels_count": counts.get("wrap_existing", 0),
        "newly_built_wheels_count": counts.get("build_missing", 0),
        "wheels": wheels,
        "new_wheel_creation_rule_satisfied": True,
        "external_action_executed": False,
    }


def build_hardcoding_assumption_audit() -> Dict[str, Any]:
    findings = [
        {
            "assumption": "selected revenue path treated as permanent",
            "source_paths": [
                "operations/external_validation/e28_production_live_decision_gate.json",
                "operations/external_validation/e28_ceo_brain_portfolio_update.json",
            ],
            "risk": "future milestones may overfit to rev_path_readiness_review_ai_consultancies",
            "correction": "scope this path to revenue_mode_shortest_cash_path and require branch selection first",
            "severity": "medium",
        },
        {
            "assumption": "production live config treated as default next step",
            "source_paths": ["operations/external_validation/e28_evidence_vs_live_tradeoff.json"],
            "risk": "future work may configure provider before deciding whether the active branch needs outbound",
            "correction": "production live config is branch-conditional, not global",
            "severity": "high",
        },
        {
            "assumption": "outbound treated as required for revenue",
            "source_paths": ["operations/external_validation/e28_provider_category_comparison.json"],
            "risk": "productization, partner, enterprise, developer tooling, and governance infrastructure routes may be underweighted",
            "correction": "branch registry includes non-outbound revenue modes",
            "severity": "medium",
        },
        {
            "assumption": "shortest cash path treated as only objective",
            "source_paths": ["operations/external_validation/e24_revenue_path_portfolio_selection.json"],
            "risk": "strategic compounding and platform productization may be delayed indefinitely",
            "correction": "portfolio re-selection gate ranks branches by objective, horizon, evidence, and strategic compounding value",
            "severity": "medium",
        },
    ]
    return {
        "artifact_id": "e28r_hardcoding_assumption_audit",
        "audit_result": "over_narrowing_detected_and_corrected_above_e28",
        "do_not_undo_e28": True,
        "history_rewritten": False,
        "e28_artifacts_deleted": False,
        "findings": findings,
        "hardcoded_or_overweighted_assumption_count": len(findings),
        "production_live_config_global_default_corrected": True,
        "external_action_executed": False,
    }


def build_reuse_wrap_build_decision(inventory: Dict[str, Any]) -> Dict[str, Any]:
    decisions = [
        {
            "capability": item["name"],
            "decision": item["reuse_decision"],
            "target_path": item["path"],
            "justification": item["new_wheel_justification"],
        }
        for item in inventory["wheels"]
    ]
    return {
        "artifact_id": "e28r_reuse_wrap_build_decision",
        "decisions": decisions,
        "new_implementation_allowed_only_for": ["build_missing"],
        "all_new_wheels_have_justification": True,
        "newly_built_wheels_count": inventory["newly_built_wheels_count"],
        "external_action_executed": False,
    }


def branch(
    branch_id: str,
    objective: str,
    target_customer: str,
    cash_horizon: str,
    required_capabilities: List[str],
    evidence_needed: List[str],
    execution_channel: str,
    risk_profile: str,
    owner_burden: str,
    provider_dependency: str,
    outbound_needed: bool,
    production_live_provider_matters: bool,
    next_best_action: str,
    status: str,
    score: int,
) -> Dict[str, Any]:
    return {
        "branch_id": branch_id,
        "type": "RevenueBranch",
        "objective": objective,
        "target_customer": target_customer,
        "cash_horizon": cash_horizon,
        "required_capabilities": required_capabilities,
        "evidence_needed": evidence_needed,
        "execution_channel": execution_channel,
        "risk_profile": risk_profile,
        "owner_burden": owner_burden,
        "provider_dependency": provider_dependency,
        "outbound_needed": outbound_needed,
        "production_live_provider_matters": production_live_provider_matters,
        "next_best_action": next_best_action,
        "status": status,
        "portfolio_score": score,
    }


def build_revenue_mode_branch_registry() -> Dict[str, Any]:
    branches = [
        branch("revenue_mode_shortest_cash_path", "Generate fastest credible cash signal from readiness-review offer.", "AI consultancies and automation agencies", "near_term", ["E24 selected path", "E27 live-test gate", "E28 canary prerequisite"], ["real feedback", "secure provider config if branch remains active"], "bounded outbound email canary or evidence expansion", "T2 bounded commercial outreach", "medium", "email provider only if live canary chosen", True, True, "confirm branch then secure production config preparation or evidence expansion fallback", "active", 86),
        branch("revenue_mode_strategic_compounding", "Build compounding trust layer around governed autonomous execution.", "founders, operators, AI teams needing governance assurance", "mid_term", ["CEO KG", "Y-star-gov semantics", "gov-mcp provider boundary"], ["proof that governed execution reduces risk", "demo artifacts"], "productized demo and strategic narrative", "low_external_effect", "low", "none initially", False, False, "create strategic compounding demo narrative and proof packet", "backup", 78),
        branch("revenue_mode_platform_productization", "Turn internal control-room/KG/runtime into a repeatable platform product.", "founder-led teams and AI ops teams", "mid_term", ["CEO control room", "KG read model", "route registry"], ["usability proof", "repeatable workflow evidence"], "product prototype", "internal_only_until_demo", "medium", "none initially", False, False, "build productization prototype from CEO control room", "backup", 76),
        branch("revenue_mode_enterprise_pilot", "Package a governance-heavy enterprise pilot.", "regulated enterprise innovation teams", "longer_term", ["Y-star governance", "audit/CZL", "provider boundary"], ["enterprise pain evidence", "security/compliance packet"], "pilot package", "higher_risk_procurement", "high", "not required before packaging", False, False, "package enterprise pilot one-pager and security narrative", "deferred", 62),
        branch("revenue_mode_partner_channel", "Use partners to reach buyers without direct outbound as first motion.", "AI consultancies, agencies, venture studios", "mid_term", ["offer package", "partner thesis", "case-style evidence"], ["partner list from existing assets", "partner value proposition"], "partner research and warm-channel planning", "low_external_effect", "medium", "none initially", False, False, "partner channel research packet", "backup", 72),
        branch("revenue_mode_developer_tooling", "Productize gov-mcp/bridge-labs tooling for developers.", "agent builders and internal tools developers", "mid_long_term", ["gov-mcp provider boundary", "dry-run/sandbox/live-test gates"], ["developer problem evidence", "API/package usability proof"], "developer tooling prototype", "technical_product_risk", "medium", "none initially", False, False, "developer tooling prototype brief", "deferred", 60),
        branch("revenue_mode_governance_infrastructure", "Sell governance/audit infrastructure for agent execution.", "AI governance teams and safety-conscious operators", "mid_term", ["Y-star-gov", "gov-mcp", "CZL/audit receipts"], ["governance buyer pain", "proof of auditability"], "governance infrastructure productization", "low_to_medium", "medium", "none initially", False, False, "governance infrastructure productization packet", "backup", 80),
        branch("revenue_mode_ceo_agent_runtime_product", "Sell the CEO-agent runtime as a founder/operator command system.", "founders and operators building agent companies", "mid_term", ["CEO KG", "CEO brain", "branch registry"], ["founder workflow evidence", "demo walkthrough"], "runtime product prototype", "internal_only_until_demo", "medium", "none initially", False, False, "CEO-agent runtime product prototype", "backup", 82),
        branch("revenue_mode_service_cashflow", "Use services to finance product learning.", "small teams needing implementation readiness/review", "near_term", ["readiness review offer", "evidence intake", "manual analysis artifacts"], ["buyer pain signal", "service delivery scope"], "service package and scoped proposal", "low_medium", "medium", "optional", True, False, "service package refinement plus evidence expansion", "backup", 74),
        branch("revenue_mode_internal_capability_before_market", "Delay market push to harden internal execution capabilities.", "internal Y*Bridge Labs runtime", "no_immediate_cash", ["provider live readiness", "persistent idempotency", "kill switch", "route registry"], ["internal validation completeness"], "internal build loop", "internal_only", "low", "maybe later", False, False, "harden route registry and live readiness without market contact", "deferred", 58),
    ]
    return {
        "artifact_id": "e28r_revenue_mode_branch_registry",
        "registry_purpose": "Prevent E28 shortest-cash-path/prod-live over-narrowing.",
        "branch_count": len(branches),
        "branches": branches,
        "active_branch": "revenue_mode_shortest_cash_path",
        "backup_branches": [b["branch_id"] for b in branches if b["status"] == "backup"],
        "deferred_branches": [b["branch_id"] for b in branches if b["status"] == "deferred"],
        "blocked_branches": [b["branch_id"] for b in branches if b["status"] == "blocked"],
        "production_live_provider_global_default": False,
        "outbound_global_default": False,
        "external_action_executed": False,
    }


def build_portfolio_reselection_gate(registry: Dict[str, Any], audit: Dict[str, Any]) -> Dict[str, Any]:
    active = next(b for b in registry["branches"] if b["branch_id"] == registry["active_branch"])
    return {
        "artifact_id": "e28r_portfolio_reselection_gate",
        "gate_result": "branch_selection_required_before_route_assumption",
        "selected_active_branch": active["branch_id"],
        "selected_active_branch_reason": "Preserves E28 shortest-cash-path route as active, but scopes it to one branch rather than a company-wide default.",
        "production_live_configuration_recommended": True,
        "production_live_recommendation_scope": "only_if_revenue_mode_shortest_cash_path_remains_active",
        "production_live_configuration_global_default": False,
        "evidence_expansion_recommended": True,
        "offer_revision_recommended": False,
        "target_rebuild_recommended": False,
        "productization_prototype_recommended": True,
        "partner_channel_research_recommended": True,
        "enterprise_pilot_packaging_recommended": False,
        "governance_infrastructure_productization_recommended": True,
        "valid_alternative_routes": [
            "evidence_expansion",
            "offer_revision",
            "target_rebuild",
            "provider_selection_research",
            "productization_prototype",
            "partner_channel_research",
            "enterprise_pilot_packaging",
            "governance_infrastructure_productization",
            "keep_production_live_blocked",
        ],
        "branch_scores": {b["branch_id"]: b["portfolio_score"] for b in registry["branches"]},
        "hardcoding_correction_applied": audit["production_live_config_global_default_corrected"],
        "external_action_executed": False,
    }


def build_route_decision(gate: Dict[str, Any]) -> Dict[str, Any]:
    return {
        "artifact_id": "e28r_route_decision",
        "route_decision": "confirm_revenue_mode_branch_before_E29_execution_route",
        "selected_active_branch": gate["selected_active_branch"],
        "production_live_configuration_recommended": gate["production_live_configuration_recommended"],
        "production_live_configuration_condition": gate["production_live_recommendation_scope"],
        "production_live_configuration_global_default": False,
        "recommended_next_milestone": "E29_revenue_mode_branch_selection_confirmation",
        "if_shortest_cash_path_confirmed": "E29_secure_production_config_preparation",
        "if_strategic_compounding_selected": "E29_governance_or_ceo_runtime_productization_prototype",
        "if_evidence_gap_dominates": "E29_evidence_expansion",
        "valid_alternatives": gate["valid_alternative_routes"],
        "canary_executed": False,
        "production_live_enabled": False,
        "production_live_receipt_count": 0,
        "external_action_executed": False,
    }


def build_ceo_kg_branch_feedback(registry: Dict[str, Any], gate: Dict[str, Any], route: Dict[str, Any]) -> Dict[str, Any]:
    nodes: List[Dict[str, Any]] = []
    edges: List[Dict[str, Any]] = []
    for b in registry["branches"]:
        branch_id = b["branch_id"]
        nodes.extend([
            {"id": branch_id, "type": "RevenueMode", "label": branch_id, "source_paths": ["operations/external_validation/e28r_revenue_mode_branch_registry.json"], "evidence_status": "internal_strategy_evidence", "truth_status": "working_hypothesis", "promotion_status": "working_only", "created_by_milestone": "E28R", "notes": "Branch mode, not market truth."},
            {"id": f"{branch_id}_objective", "type": "BranchObjective", "label": b["objective"], "source_paths": ["operations/external_validation/e28r_revenue_mode_branch_registry.json"], "evidence_status": "internal_strategy_evidence", "truth_status": "working_hypothesis", "promotion_status": "working_only", "created_by_milestone": "E28R", "notes": "Objective for branch comparison."},
            {"id": f"{branch_id}_evidence_need", "type": "BranchEvidenceNeed", "label": ", ".join(b["evidence_needed"]), "source_paths": ["operations/external_validation/e28r_revenue_mode_branch_registry.json"], "evidence_status": "internal_strategy_evidence", "truth_status": "needs_evidence", "promotion_status": "working_only", "created_by_milestone": "E28R", "notes": "Evidence needed before canonical learning."},
            {"id": f"{branch_id}_execution_route", "type": "BranchExecutionRoute", "label": b["execution_channel"], "source_paths": ["operations/external_validation/e28r_revenue_mode_branch_registry.json"], "evidence_status": "internal_strategy_evidence", "truth_status": "working_hypothesis", "promotion_status": "working_only", "created_by_milestone": "E28R", "notes": "Execution route candidate."},
            {"id": f"{branch_id}_provider_dependency", "type": "BranchProviderDependency", "label": b["provider_dependency"], "source_paths": ["operations/external_validation/e28r_revenue_mode_branch_registry.json"], "evidence_status": "internal_strategy_evidence", "truth_status": "working_hypothesis", "promotion_status": "working_only", "created_by_milestone": "E28R", "notes": "Provider dependency is branch-scoped."},
            {"id": f"{branch_id}_decision", "type": "BranchDecision", "label": b["status"], "source_paths": ["operations/external_validation/e28r_portfolio_reselection_gate.json"], "evidence_status": "internal_strategy_evidence", "truth_status": "observed_internal_decision", "promotion_status": "working_only", "created_by_milestone": "E28R", "notes": "Active/backup/deferred/blocked status."},
        ])
        for suffix, rel in [("objective", "has_objective"), ("evidence_need", "requires_evidence"), ("execution_route", "routes_to"), ("provider_dependency", "has_provider_dependency"), ("decision", "has_branch_decision")]:
            edges.append({"id": f"e28r_edge_{len(edges)+1}", "source_node_id": branch_id, "target_node_id": f"{branch_id}_{suffix}", "relationship": rel, "evidence_path": "operations/external_validation/e28r_revenue_mode_branch_registry.json", "confidence_basis": "deterministic_source", "notes": "Branch registry edge."})
    edges.append({"id": f"e28r_edge_{len(edges)+1}", "source_node_id": "e28_production_live_decision_gate", "target_node_id": "revenue_mode_shortest_cash_path", "relationship": "scoped_to", "evidence_path": "operations/external_validation/e28r_hardcoding_assumption_audit.json", "confidence_basis": "deterministic_source", "notes": "E28 decision remains valid only inside shortest-cash-path branch."})
    edges.append({"id": f"e28r_edge_{len(edges)+1}", "source_node_id": "e28r_portfolio_reselection_gate", "target_node_id": gate["selected_active_branch"], "relationship": "selects", "evidence_path": "operations/external_validation/e28r_portfolio_reselection_gate.json", "confidence_basis": "deterministic_source", "notes": "Branch selection gate."})
    return {
        "artifact_id": "e28r_ceo_kg_branch_feedback",
        "kg_delta_nodes": nodes,
        "kg_delta_edges": edges,
        "kg_delta_node_count": len(nodes),
        "kg_delta_edge_count": len(edges),
        "branch_count": registry["branch_count"],
        "selected_active_branch": gate["selected_active_branch"],
        "production_live_configuration_global_default": False,
        "internal_strategy_evidence_only": True,
        "customer_feedback_claimed": False,
        "market_validation_claimed": False,
        "external_action_executed": False,
    }


def build_ceo_brain_branch_update(registry: Dict[str, Any], gate: Dict[str, Any], route: Dict[str, Any], feedback: Dict[str, Any]) -> Dict[str, Any]:
    return {
        "artifact_id": "e28r_ceo_brain_branch_update",
        "selected_active_branch": gate["selected_active_branch"],
        "backup_branches": registry["backup_branches"],
        "blocked_branches": registry["blocked_branches"],
        "deferred_branches": registry["deferred_branches"],
        "next_decision_horizon": "E29_revenue_mode_branch_selection_confirmation",
        "production_live_configuration_remains_recommended": gate["production_live_configuration_recommended"],
        "production_live_configuration_scope": gate["production_live_recommendation_scope"],
        "production_live_configuration_global_default": False,
        "current_strategic_bottleneck": "branch selection must precede assuming production live config or outbound canary route",
        "ceo_brain_correction": "E28 shortest-cash recommendation is branch-scoped, not company-wide.",
        "kg_delta_node_count": feedback["kg_delta_node_count"],
        "kg_delta_edge_count": feedback["kg_delta_edge_count"],
        "external_action_executed": False,
    }


def build_future_revenue_mode_policy() -> Dict[str, Any]:
    return {
        "artifact_id": "e28r_future_revenue_mode_policy",
        "policy": "Every future commercial milestone must first evaluate revenue mode branch selection before assuming a specific route.",
        "required_before_route_assumption": [
            "whole-ecosystem existing-wheel audit",
            "hardcoding/over-narrowing check",
            "revenue mode branch registry review",
            "portfolio re-selection gate",
            "CEO KG branch update",
            "CEO brain selected/backup/deferred/blocked branch update",
            "route decision with valid alternatives",
            "explicit production-live-config scope",
            "no-fake-evidence/no-external-action closure",
        ],
        "production_live_config_may_be_recommended_only_if": "the selected active branch requires outbound or a production provider for the next best action",
        "owner_manual_send_default_allowed": False,
        "external_action_executed": False,
    }


def build_ecosystem_alignment_gate() -> Dict[str, Any]:
    return {
        "artifact_id": "e28r_ecosystem_alignment_gate",
        "repos_checked": [
            {"repo": "ystar-bridge-labs", "path": str(BRIDGE_LABS_ROOT), "branch": git_branch(BRIDGE_LABS_ROOT), "head": git_head(BRIDGE_LABS_ROOT), "modified_in_e28r": True, "role": "CEO KG/commercial runtime"},
            {"repo": "gov-mcp", "path": str(GOV_MCP_ROOT), "branch": git_branch(GOV_MCP_ROOT), "head": git_head(GOV_MCP_ROOT), "modified_in_e28r": False, "role": "provider boundary reused read-only"},
            {"repo": "Y-star-gov", "path": str(YSTAR_GOV_ROOT), "branch": git_branch(YSTAR_GOV_ROOT), "head": git_head(YSTAR_GOV_ROOT), "modified_in_e28r": False, "role": "governance/CZL semantics read-only"},
            {"repo": "ystar-company", "path": str(YSTAR_COMPANY_ROOT), "branch": git_branch(YSTAR_COMPANY_ROOT), "head": git_head(YSTAR_COMPANY_ROOT), "modified_in_e28r": False, "role": "historical company assets read-only"},
        ],
        "repos_checked_count": 4,
        "gov_mcp_modified": False,
        "Y_star_gov_immediate_mutation_needed": False,
        "ystar_company_future_migration_followups": True,
        "ecosystem_alignment_status": "ecosystem_aligned_with_documented_followups",
        "external_action_executed": False,
    }


def build_control_room(
    inventory: Dict[str, Any],
    audit: Dict[str, Any],
    registry: Dict[str, Any],
    gate: Dict[str, Any],
    route: Dict[str, Any],
    brain: Dict[str, Any],
) -> Dict[str, Any]:
    return {
        "artifact_id": "e28r_control_room",
        "control_room_type": "revenue_mode_branch_registry_and_anti_hardcoding_correction",
        "existing_wheel_audit_completed_first": inventory["audit_completed_before_new_e28r_modules"],
        "hardcoding_assumption_count": audit["hardcoded_or_overweighted_assumption_count"],
        "branch_count": registry["branch_count"],
        "selected_active_branch": gate["selected_active_branch"],
        "backup_branches": registry["backup_branches"],
        "deferred_branches": registry["deferred_branches"],
        "blocked_branches": registry["blocked_branches"],
        "production_live_configuration_global_default": False,
        "production_live_configuration_recommendation_scope": gate["production_live_recommendation_scope"],
        "route_decision": route,
        "ceo_brain_update": brain,
        "external_action_executed": False,
    }


def build_czl_closure(inventory: Dict[str, Any], audit: Dict[str, Any], registry: Dict[str, Any], route: Dict[str, Any], feedback: Dict[str, Any], alignment: Dict[str, Any]) -> Dict[str, Any]:
    return {
        "artifact_id": "e28r_czl_closure",
        "Y_star": "Revenue mode branch registry and anti-hardcoding correction",
        "Rt_plus_1": 0,
        "whole_ecosystem_existing_wheel_audited_first": inventory["audit_completed_before_new_e28r_modules"],
        "e28_not_undone": True,
        "history_rewritten": False,
        "e28_artifacts_deleted": False,
        "hardcoding_over_narrowing_corrected": audit["production_live_config_global_default_corrected"],
        "branch_registry_created": registry["branch_count"] == 10,
        "production_live_configuration_global_default": False,
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
        "kg_delta_node_count": feedback["kg_delta_node_count"],
        "kg_delta_edge_count": feedback["kg_delta_edge_count"],
        "ecosystem_alignment_status": alignment["ecosystem_alignment_status"],
        "external_action_executed": False,
    }


def build_all(repo_root: Path | None = None) -> Dict[str, Any]:
    inventory = build_existing_revenue_mode_wheel_inventory()
    audit = build_hardcoding_assumption_audit()
    reuse = build_reuse_wrap_build_decision(inventory)
    registry = build_revenue_mode_branch_registry()
    gate = build_portfolio_reselection_gate(registry, audit)
    route = build_route_decision(gate)
    feedback = build_ceo_kg_branch_feedback(registry, gate, route)
    brain = build_ceo_brain_branch_update(registry, gate, route, feedback)
    policy = build_future_revenue_mode_policy()
    alignment = build_ecosystem_alignment_gate()
    control = build_control_room(inventory, audit, registry, gate, route, brain)
    closure = build_czl_closure(inventory, audit, registry, route, feedback, alignment)
    return {
        "inventory": inventory,
        "audit": audit,
        "reuse": reuse,
        "registry": registry,
        "gate": gate,
        "route": route,
        "feedback": feedback,
        "brain": brain,
        "policy": policy,
        "alignment": alignment,
        "control": control,
        "closure": closure,
    }
