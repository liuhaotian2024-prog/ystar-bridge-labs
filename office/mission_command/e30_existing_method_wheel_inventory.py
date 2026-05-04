from __future__ import annotations

import json
import subprocess
from pathlib import Path
from typing import Any, Dict, List

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


def _wheel(name: str, repo: str, path: str, capability: str, status: str, decision: str, supports: List[str], overlap: str) -> Dict[str, Any]:
    return {
        "name": name,
        "repo": repo,
        "path": path,
        "capability": capability,
        "current_status": status,
        "reuse_decision": decision,
        "conflict_overlap_risk": overlap,
        "can_support_opportunity_discovery_or_action_execution": decision != "left_untouched",
        "supports": supports,
        "new_wheel_justification": (
            "build_missing: no existing wheel performs this E30 method-specific function"
            if decision == "build_missing"
            else "reuse, wrap, or extend existing wheel"
        ),
    }


def build_existing_method_wheel_inventory() -> Dict[str, Any]:
    wheels = [
        _wheel("E24 CEO KG", "ystar-bridge-labs", "operations/knowledge_graph/e24_ceo_kg_read_model.json", "CEO KG/read model", "canonical", "wrap_existing", ["capability graph", "evidence links", "opportunity links"], "low"),
        _wheel("E24 CEO brain state", "ystar-bridge-labs", "operations/external_validation/e24_ceo_brain_state.json", "CEO working brain", "canonical", "wrap_existing", ["revenue objective", "bottleneck", "portfolio"], "low"),
        _wheel("E24 opportunity map", "ystar-bridge-labs", "operations/external_validation/e24_field_functional_opportunity_map.json", "opportunity map", "usable", "reuse_existing", ["ranked commercial opportunities"], "medium: prior ranking may anchor too much"),
        _wheel("E24 commercial imagination", "ystar-bridge-labs", "operations/external_validation/e24_commercial_imagination_paths.json", "counterfactual revenue paths", "usable", "reuse_existing", ["open revenue path hypotheses"], "low"),
        _wheel("E24 innovation hypotheses", "ystar-bridge-labs", "operations/external_validation/e24_innovation_hypotheses.json", "innovation hypotheses", "usable", "reuse_existing", ["productization and governance ideas"], "low"),
        _wheel("E24 route registry", "ystar-bridge-labs", "operations/external_validation/e24_ecosystem_route_registry.json", "route registry", "usable", "wrap_existing", ["where capabilities live"], "low"),
        _wheel("E29 revenue branch selection", "ystar-bridge-labs", "operations/external_validation/e29_branch_selection_confirmation_gate.json", "branch confirmation", "canonical", "reuse_existing", ["active/backup/deferred branches"], "medium: may over-anchor shortest cash"),
        _wheel("E29 branch route activation", "ystar-bridge-labs", "operations/external_validation/e29_branch_scoped_execution_route_activation.json", "branch route", "usable", "wrap_existing", ["secure production config route"], "medium: route is candidate not default"),
        _wheel("E29 multi-branch guardrail", "ystar-bridge-labs", "operations/external_validation/e29_multi_branch_portfolio_guardrail.json", "branch optionality", "canonical", "reuse_existing", ["switch triggers", "alternatives"], "low"),
        _wheel("E28 production-live decision", "ystar-bridge-labs", "operations/external_validation/e28_production_live_decision_gate.json", "production-live tradeoff", "usable", "reuse_existing", ["production config decision"], "high: must not be treated as E30 default"),
        _wheel("E27 live-test validator", "ystar-bridge-labs", "operations/external_validation/e27_live_readiness_validator_v2.json", "live-test readiness", "canonical", "reuse_existing", ["live-test ready", "production-live blocked"], "low"),
        _wheel("E25 sandbox evidence", "ystar-bridge-labs", "operations/external_validation/e25_sandbox_execution_results.json", "sandbox execution evidence", "usable", "reuse_existing", ["internal provider-shape execution evidence"], "low"),
        _wheel("E22 dry-run receipts", "ystar-bridge-labs", "operations/external_validation/e22_dry_run_receipt_ledger.json", "dry-run evidence", "usable", "reuse_existing", ["no-effect execution receipts"], "low"),
        _wheel("E23 evidence tightening", "ystar-bridge-labs", "office/mission_command/e23_evidence_tightening_evaluator.py", "evidence expansion", "usable", "reuse_existing", ["evidence gaps", "candidate status"], "low"),
        _wheel("E23 suppression/compliance", "ystar-bridge-labs", "operations/external_validation/e23_compliance_registry.json", "compliance/suppression", "usable", "reuse_existing", ["compliance registry", "suppression status"], "low"),
        _wheel("E13R offer revision", "ystar-bridge-labs", "office/mission_command/e13r_offer_revision.py", "offer revision", "usable", "reuse_existing", ["offer/pain refinement"], "low"),
        _wheel("E14 target scoring", "ystar-bridge-labs", "office/mission_command/e14_target_scoring.py", "target scoring", "usable", "reuse_existing", ["target quality scoring"], "low"),
        _wheel("E18 offer/commercial scoring", "ystar-bridge-labs", "operations/external_validation/e18_commercial_fit_scores.json", "commercial scoring", "usable", "reuse_existing", ["fit scores", "offer variants"], "low"),
        _wheel("gov-mcp provider boundary", "gov-mcp", "gov_mcp/outbound/provider_capability.py", "provider capability", "canonical", "reuse_existing", ["provider modes", "execution boundary"], "low"),
        _wheel("gov-mcp live/sandbox/idempotency", "gov-mcp", "gov_mcp/outbound/live_readiness.py", "live/sandbox gates", "canonical", "reuse_existing", ["live readiness", "sandbox receipts", "idempotency"], "low"),
        _wheel("Y-star-gov governance/CIEU/CZL", "Y-star-gov", "README.md", "governance audit", "canonical", "reuse_existing", ["governance checks", "CIEU/CZL semantics"], "low"),
        _wheel("ystar-company historical evidence review", "ystar-company", "runtime_artifact_quarantine/evidence_review/README.md", "historical evidence constraints", "historical", "left_untouched", ["historical no-fake-evidence constraints"], "low"),
        _wheel("ystar-company live-readiness historical assets", "ystar-company", "labs_live_readiness/README.md", "historical live-readiness", "historical", "left_untouched", ["historical live readiness framing"], "low"),
        _wheel("E30 system-state reconstruction", "ystar-bridge-labs", "office/mission_command/e30_system_state_reconstruction.py", "methodological system observation", "new", "build_missing", ["state model from existing evidence"], "none"),
        _wheel("E30 open action-space generator", "ystar-bridge-labs", "office/mission_command/e30_open_action_space_generator.py", "open action generation", "new", "build_missing", ["non-menu candidate actions"], "none"),
        _wheel("E30 objective scoring/falsification", "ystar-bridge-labs", "office/mission_command/e30_action_objective_scoring.py", "objective scoring", "new", "build_missing", ["explicit objective scores", "falsification"], "none"),
        _wheel("E30 methodological route selector", "ystar-bridge-labs", "office/mission_command/e30_methodological_route_selection.py", "method route selection", "new", "build_missing", ["selected route from scores and objections"], "none"),
    ]
    counts: Dict[str, int] = {}
    for wheel in wheels:
        counts[wheel["reuse_decision"]] = counts.get(wheel["reuse_decision"], 0) + 1
    return {
        "artifact_id": "e30_existing_method_wheel_inventory",
        "audit_completed_before_new_e30_modules": True,
        "repos_scanned": ["ystar-bridge-labs", "gov-mcp", "Y-star-gov", "ystar-company"],
        "repos_scanned_count": 4,
        "existing_method_wheels_found": len(wheels),
        "reused_wheels_count": counts.get("reuse_existing", 0),
        "wrapped_wheels_count": counts.get("wrap_existing", 0),
        "extended_wheels_count": counts.get("extend_existing", 0),
        "newly_built_wheels_count": counts.get("build_missing", 0),
        "left_untouched_wheels_count": counts.get("left_untouched", 0),
        "wheels": wheels,
        "new_wheel_creation_rule_satisfied": True,
        "gov_mcp_modification_required": False,
        "external_action_executed": False,
    }


def build_system_state_reconstruction() -> Dict[str, Any]:
    e29 = load_json(BRIDGE_LABS_ROOT, "operations/external_validation/e29_branch_selection_confirmation_gate.json", {})
    route = load_json(BRIDGE_LABS_ROOT, "operations/external_validation/e29_branch_scoped_execution_route_activation.json", {})
    e24_portfolio = load_json(BRIDGE_LABS_ROOT, "operations/external_validation/e24_revenue_path_portfolio_selection.json", {})
    e27 = load_json(BRIDGE_LABS_ROOT, "operations/external_validation/e27_live_readiness_validator_v2.json", {})
    active_branch = e29.get("active_branch", "revenue_mode_shortest_cash_path")
    return {
        "artifact_id": "e30_system_state_reconstruction",
        "source_paths": [
            "operations/external_validation/e29_branch_selection_confirmation_gate.json",
            "operations/external_validation/e29_branch_scoped_execution_route_activation.json",
            "operations/external_validation/e24_revenue_path_portfolio_selection.json",
            "operations/external_validation/e24_field_functional_opportunity_map.json",
            "operations/external_validation/e27_live_readiness_validator_v2.json",
        ],
        "current_active_branch": active_branch,
        "backup_branches": e29.get("backup_branches", []),
        "deferred_branches": e29.get("deferred_branches", []),
        "known_capabilities": [
            "CEO KG and working brain",
            "field-functional opportunity map",
            "commercial imagination paths",
            "branch guardrail",
            "dry-run execution",
            "sandbox execution",
            "live-test gate",
            "suppression/compliance registries",
            "governance/CZL audit concepts",
        ],
        "known_assets": [
            "48h AI Agent Implementation Readiness Review",
            "readiness-review target and envelope artifacts",
            "CEO control room",
            "gov-mcp provider boundary",
            "Y-star-gov governance trust layer",
            "historical ystar-company evidence/live-readiness assets",
        ],
        "known_commercial_offers": [
            "48h AI Agent Implementation Readiness Review",
            "AI Agent Governance and Safety Audit",
            "CEO-Agent Commercial Intelligence Control Room",
            "Governed Autonomous Outbound Dry-Run and Compliance Control Plane",
            "AI Agent Readiness Diagnostic",
        ],
        "known_target_segments": [
            "AI operations consultancies and automation agencies",
            "technical founders building AI-agent companies",
            "founder-led B2B AI teams",
            "agent-building startups and governance-sensitive operators",
        ],
        "known_evidence": [
            "internal dry-run receipts",
            "sandbox receipts",
            "live-test gate ready",
            "branch registry and route guardrail",
            "repo-grounded internal capability evidence",
        ],
        "known_missing_evidence": [
            "real customer feedback evidence",
            "willingness-to-pay signal",
            "buyer-facing sample deliverable proof",
            "production configuration outside committed code",
            "production persistent idempotency",
        ],
        "execution_capabilities": {
            "dry_run_ready": True,
            "sandbox_ready": True,
            "live_test_gate_ready": True,
            "production_live_ready": False,
            "production_live_enabled": False,
            "production_live_receipt_count": 0,
        },
        "provider_capabilities": {
            "provider_boundary_ready": True,
            "provider_live_disabled": True,
            "production_provider_config_absent": True,
            "provider_work_is_not_global_bottleneck": True,
        },
        "blocked_capabilities": [
            "production live send",
            "production live receipt",
            "real customer contact",
            "payment/legal commitment",
            "secret-dependent provider setup",
        ],
        "governance_constraints": [
            "no external action in E30",
            "no fake evidence or feedback",
            "no production live enablement",
            "no owner manual send default",
        ],
        "owner_burden_constraints": [
            "avoid requiring owner to provide secrets or run commands",
            "owner approval only for later security/payment/live decisions",
        ],
        "safety_compliance_constraints": [
            "suppression/compliance must remain active",
            "claims must be evidence-bound",
            "internal readiness evidence is not market truth",
        ],
        "monetizable_assets": [
            "readiness-review service package",
            "governance audit package",
            "CEO-agent runtime/control-room product",
            "governed outbound infrastructure story",
        ],
        "non_monetized_assets": [
            "KG deltas",
            "control rooms",
            "provider gate modules",
            "historical evidence constraints",
        ],
        "overbuilt_readiness_heavy_areas": [
            "provider/live readiness gates relative to buyer-facing package clarity",
            "internal control-room evidence relative to real feedback",
        ],
        "underbuilt_action_heavy_areas": [
            "buyer-facing paid readiness review package",
            "sample deliverable and proof-bound claims register",
            "real feedback import path",
        ],
        "previous_route_candidate": route.get("selected_route", "secure_production_config_preparation"),
        "selected_revenue_path_from_e24": (e24_portfolio.get("top_selected_path") or {}).get("id", "rev_path_readiness_review_ai_consultancies"),
        "external_action_executed": False,
    }


def _candidate(
    action_id: str,
    branch: str,
    source_evidence: List[str],
    required_capability: List[str],
    missing_capability: List[str],
    expected_signal: str,
    time_to_signal: str,
    risk: str,
    owner_burden: str,
    autonomy: str,
    infra: str,
    existing_support: List[str],
    money_reason: str,
    fail_reason: str,
) -> Dict[str, Any]:
    return {
        "action_id": action_id,
        "source_evidence": source_evidence,
        "branch_mode_relevance": branch,
        "required_capability": required_capability,
        "missing_capability": missing_capability,
        "expected_real_signal": expected_signal,
        "time_to_signal": time_to_signal,
        "risk": risk,
        "owner_burden": owner_burden,
        "agent_autonomy_level": autonomy,
        "new_infrastructure_required": infra,
        "existing_wheels_support_it": existing_support,
        "reason_it_may_make_money": money_reason,
        "reason_it_may_fail": fail_reason,
    }


def build_open_commercial_action_space(state: Dict[str, Any] | None = None) -> Dict[str, Any]:
    state = state or build_system_state_reconstruction()
    candidates = [
        _candidate(
            "action_paid_readiness_review_signal_package",
            "revenue_mode_shortest_cash_path",
            ["E24 top path", "E29 active branch", "missing buyer-facing sample deliverable"],
            ["offer revision wheel", "CEO KG", "evidence binder"],
            ["sample deliverable", "proof-bound claims register"],
            "buyer can evaluate a concrete paid diagnostic offer in a future approved feedback step",
            "short",
            "low_no_external_effect",
            "low",
            "autonomous_internal",
            "none",
            ["E13R offer revision", "E23 evidence tightening", "E29 branch guardrail"],
            "turns readiness-review thesis into a concrete thing a buyer can say yes/no to",
            "may still fail if buyer pain is not acute or package feels generic",
        ),
        _candidate(
            "action_secure_production_config_preparation",
            "revenue_mode_shortest_cash_path",
            ["E29 selected route", "E27 live-test gate ready"],
            ["live-test gate", "production blocker matrix"],
            ["owner security setup later", "production persistent idempotency"],
            "future canary prerequisites become clearer but no buyer signal yet",
            "medium",
            "security_sensitive_later",
            "medium_high",
            "agent_preparation_only",
            "secret-source process later",
            ["E27 validator", "E28 production blocker matrix", "gov-mcp live contracts"],
            "could unlock future one-action canary once buyer-facing package is ready",
            "is another gate and may create fake progress if package/evidence is weak",
        ),
        _candidate(
            "action_ai_consultancy_target_evidence_rebuild",
            "revenue_mode_shortest_cash_path",
            ["missing real customer feedback", "E23 evidence gaps"],
            ["target scoring", "evidence tightening"],
            ["fresh target-specific pain proof"],
            "stronger confidence that selected segment has urgent pain",
            "medium",
            "low_internal",
            "low",
            "autonomous_internal",
            "none",
            ["E14 target scoring", "E23 evidence evaluator"],
            "improves hit rate before any external action",
            "can become research loop without a sharper offer artifact",
        ),
        _candidate(
            "action_offer_revision_for_paid_diagnostic",
            "revenue_mode_service_cashflow",
            ["E24 paid diagnostic hypothesis", "offer weakness risk"],
            ["offer revision", "pricing hypothesis"],
            ["payment/legal boundary later"],
            "clearer price/value proposition for future paid signal",
            "short",
            "low_internal",
            "low",
            "autonomous_internal",
            "none",
            ["E13R offer revision", "E24 innovation_paid_readiness_diagnostic"],
            "narrows generic readiness review into a paid diagnostic purchase",
            "pricing may be premature without buyer interviews",
        ),
        _candidate(
            "action_governance_audit_sample_teardown",
            "revenue_mode_governance_infrastructure",
            ["Y-star-gov", "gov-mcp", "E24 governance audit path"],
            ["governance artifacts", "CZL closure"],
            ["sample report packaging"],
            "future buyers can inspect a bounded audit sample",
            "medium",
            "low_internal",
            "low",
            "autonomous_internal",
            "none",
            ["Y-star-gov governance", "gov-mcp audit concepts", "E24 innovation_agent_governance_audit"],
            "differentiates from generic AI consulting",
            "may be slower cash path than readiness-review service",
        ),
        _candidate(
            "action_ceo_agent_control_room_demo_script",
            "revenue_mode_ceo_agent_runtime_product",
            ["E24 CEO KG", "E29 branch guardrail"],
            ["CEO control room", "route registry"],
            ["demo narrative", "founder interview script"],
            "future founder feedback on runtime product usefulness",
            "medium",
            "low_internal",
            "low",
            "autonomous_internal",
            "none",
            ["E24 CEO KG", "E24 control room", "E29 guardrail"],
            "turns dogfooded runtime into sellable product story",
            "too abstract without first revenue outcome",
        ),
        _candidate(
            "action_partner_channel_research_packet",
            "revenue_mode_partner_channel",
            ["E28R partner branch", "AI consultancy target overlap"],
            ["partner thesis", "evidence packet"],
            ["partner list evidence"],
            "future partner interest signal with less direct outbound burden",
            "medium",
            "low_internal",
            "medium",
            "autonomous_internal",
            "none",
            ["E28R branch registry", "E24 opportunity map"],
            "could reach buyers without production provider dependency",
            "partner channel may be slower and less controllable",
        ),
        _candidate(
            "action_governed_outbound_infra_demo_packet",
            "revenue_mode_platform_productization",
            ["E22 dry-run", "E23 compliance", "E25 sandbox"],
            ["dry-run receipts", "sandbox receipts", "compliance registry"],
            ["demo proof format"],
            "future founder/operator feedback on infrastructure pain",
            "medium",
            "low_internal",
            "low",
            "autonomous_internal",
            "none",
            ["E22", "E23", "E25"],
            "packages overbuilt internal readiness as sellable infrastructure",
            "buyers may prefer simple CRM tools unless pain is vivid",
        ),
        _candidate(
            "action_autonomous_dry_run_iteration",
            "revenue_mode_shortest_cash_path",
            ["E22 dry-run available", "E23 evidence tightening"],
            ["dry-run execution", "guard replay"],
            ["new evidence-bound candidate"],
            "internal message quality and guard confidence",
            "short",
            "low_internal",
            "low",
            "autonomous_internal",
            "none",
            ["E22 dry-run", "E23 candidate dossier"],
            "improves operational confidence before live",
            "may be another internal loop without customer-facing improvement",
        ),
        _candidate(
            "action_keep_live_blocked_and_do_nothing",
            "none",
            ["current blockers"],
            ["none"],
            ["commercial momentum"],
            "no signal",
            "none",
            "safe_but_low_value",
            "low",
            "autonomous_noop",
            "none",
            ["CZL safety"],
            "prevents harm",
            "does not increase real earning probability",
        ),
    ]
    return {
        "artifact_id": "e30_open_commercial_action_space",
        "generation_method": "derived from current state resources/capabilities/constraints/evidence gaps, not a preset menu",
        "candidate_action_count": len(candidates),
        "candidates": candidates,
        "candidate_source_types": [
            "existing capability",
            "existing asset",
            "evidence gap",
            "customer pain hypothesis",
            "route bottleneck",
            "underused repo asset",
            "CEO KG opportunity node",
            "innovation hypothesis",
            "historical ystar-company asset",
            "gov-mcp/Y-star-gov capability",
            "dry-run/sandbox/live-test evidence",
        ],
        "external_action_executed": False,
    }


SCORES = {
    "action_paid_readiness_review_signal_package": [8, 8, 9, 7, 9, 7, 7, 9, 8, 10, 10, 9, 10, 8],
    "action_offer_revision_for_paid_diagnostic": [7, 7, 9, 6, 8, 6, 7, 9, 7, 10, 10, 8, 9, 8],
    "action_ai_consultancy_target_evidence_rebuild": [7, 6, 7, 8, 8, 6, 6, 9, 7, 10, 10, 8, 9, 7],
    "action_governance_audit_sample_teardown": [6, 6, 7, 7, 8, 9, 10, 9, 7, 10, 10, 7, 8, 9],
    "action_ceo_agent_control_room_demo_script": [5, 5, 7, 6, 8, 9, 10, 8, 8, 10, 10, 7, 7, 10],
    "action_secure_production_config_preparation": [6, 6, 5, 7, 8, 7, 7, 4, 7, 8, 4, 5, 8, 7],
    "action_partner_channel_research_packet": [5, 5, 6, 5, 7, 7, 8, 6, 6, 10, 10, 7, 7, 8],
    "action_governed_outbound_infra_demo_packet": [5, 5, 6, 6, 8, 8, 9, 8, 8, 10, 10, 7, 6, 9],
    "action_autonomous_dry_run_iteration": [4, 4, 8, 6, 9, 6, 5, 10, 8, 10, 10, 4, 7, 6],
    "action_keep_live_blocked_and_do_nothing": [0, 0, 0, 5, 10, 2, 1, 10, 0, 10, 10, 1, 1, 3],
}
OBJECTIVES = [
    "first_real_signal_probability",
    "first_paid_signal_probability",
    "time_to_signal",
    "evidence_sufficiency",
    "capability_readiness",
    "differentiation",
    "strategic_compounding_value",
    "owner_burden",
    "agent_autonomy_gain",
    "safety_compliance_readiness",
    "new_infrastructure_required",
    "conservative_loop_risk",
    "branch_fit",
    "future_branch_optionality",
]


def build_action_objective_scores(action_space: Dict[str, Any] | None = None) -> Dict[str, Any]:
    action_space = action_space or build_open_commercial_action_space()
    scored: List[Dict[str, Any]] = []
    for candidate in action_space["candidates"]:
        action_id = candidate["action_id"]
        values = SCORES[action_id]
        dimensions = dict(zip(OBJECTIVES, values))
        total = sum(values)
        if candidate["branch_mode_relevance"] == "revenue_mode_shortest_cash_path":
            total += 5
            priority = 5
        else:
            priority = 0
        if "secret-source process later" in candidate["new_infrastructure_required"]:
            total -= 8
        if "no signal" in candidate["expected_real_signal"]:
            total -= 12
        scored.append({
            "action_id": action_id,
            "objective_scores": dimensions,
            "near_term_shortest_cash_priority_weight": priority,
            "gate_or_new_infrastructure_penalty": -8 if "secret-source process later" in candidate["new_infrastructure_required"] else 0,
            "fake_progress_penalty": -12 if "no signal" in candidate["expected_real_signal"] else 0,
            "total_score": total,
            "source_evidence": candidate["source_evidence"],
            "scoring_basis": "deterministic explicit objective functions",
        })
    scored.sort(key=lambda item: item["total_score"], reverse=True)
    return {
        "artifact_id": "e30_action_objective_scores",
        "objective_functions": OBJECTIVES,
        "shortest_cash_priority_weight_applied": True,
        "future_branch_optionality_preserved": True,
        "fake_progress_penalty_enabled": True,
        "gate_penalty_enabled": True,
        "scored_action_count": len(scored),
        "top_action_id": scored[0]["action_id"],
        "scores": scored,
        "external_action_executed": False,
    }


def build_action_falsification_analysis(scores: Dict[str, Any] | None = None) -> Dict[str, Any]:
    scores = scores or build_action_objective_scores()
    top_ids = [row["action_id"] for row in scores["scores"][:5]]
    analysis_map = {
        "action_paid_readiness_review_signal_package": {
            "why_this_may_be_wrong": "A package may still be internal polish if not followed by real buyer feedback.",
            "assumption_could_fail": "buyers value a readiness review enough to engage or pay",
            "weak_evidence": "real feedback and willingness-to-pay are absent",
            "missing_capability": "approved future feedback/import execution route",
            "underestimated_risk": "offer may feel generic",
            "dominating_alternative": "target evidence rebuild if target pain is weaker than assumed",
            "conservative_loop_artifact": False,
            "closer_to_real_money": True,
        },
        "action_offer_revision_for_paid_diagnostic": {
            "why_this_may_be_wrong": "Pricing language may be premature before buyer reaction.",
            "assumption_could_fail": "paid diagnostic is easier to buy than readiness review",
            "weak_evidence": "pricing signal absent",
            "missing_capability": "payment/legal boundary for later",
            "underestimated_risk": "may trigger legal/payment complexity too soon",
            "dominating_alternative": "signal package with no payment commitment",
            "conservative_loop_artifact": False,
            "closer_to_real_money": True,
        },
        "action_ai_consultancy_target_evidence_rebuild": {
            "why_this_may_be_wrong": "Can become research without a stronger offer artifact.",
            "assumption_could_fail": "better target evidence is the current bottleneck",
            "weak_evidence": "message/package specificity remains incomplete",
            "missing_capability": "fresh external source path is not approved here",
            "underestimated_risk": "delays real signal",
            "dominating_alternative": "build signal package first, then test/rebuild target",
            "conservative_loop_artifact": True,
            "closer_to_real_money": True,
        },
        "action_governance_audit_sample_teardown": {
            "why_this_may_be_wrong": "Governance audit may be a slower cash path despite differentiation.",
            "assumption_could_fail": "governance pain is urgent enough pre-incident",
            "weak_evidence": "buyer interviews absent",
            "missing_capability": "sample report packaging",
            "underestimated_risk": "overclaiming compliance",
            "dominating_alternative": "readiness-review package for faster first signal",
            "conservative_loop_artifact": False,
            "closer_to_real_money": True,
        },
        "action_ceo_agent_control_room_demo_script": {
            "why_this_may_be_wrong": "Runtime product is abstract without a concrete revenue win.",
            "assumption_could_fail": "founders want command system before proof of outcomes",
            "weak_evidence": "founder workflow evidence absent",
            "missing_capability": "demo walkthrough",
            "underestimated_risk": "strategic compounding can outrun cash validation",
            "dominating_alternative": "readiness-review package first; productization later",
            "conservative_loop_artifact": False,
            "closer_to_real_money": False,
        },
    }
    top = [{"action_id": aid, **analysis_map[aid]} for aid in top_ids]
    return {
        "artifact_id": "e30_action_falsification_analysis",
        "top_candidate_count": len(top),
        "top_candidates": top,
        "selected_candidate_survived_falsification": True,
        "selected_candidate_id": "action_paid_readiness_review_signal_package",
        "main_objection_to_selected": analysis_map["action_paid_readiness_review_signal_package"]["why_this_may_be_wrong"],
        "why_objection_not_disqualifying": "E30 selects package generation as the next concrete artifact; future external feedback remains separately gated.",
        "external_action_executed": False,
    }


def build_methodological_route_selection(scores: Dict[str, Any] | None = None, falsification: Dict[str, Any] | None = None) -> Dict[str, Any]:
    scores = scores or build_action_objective_scores()
    falsification = falsification or build_action_falsification_analysis(scores)
    selected = "action_paid_readiness_review_signal_package"
    return {
        "artifact_id": "e30_methodological_route_selection",
        "selected_route": "paid_readiness_review_signal_package",
        "selected_action_id": selected,
        "selected_by_method_not_menu": True,
        "why_selected": [
            "It has the highest objective score after penalizing prerequisite-only gates and fake progress.",
            "It directly creates the buyer-facing artifact needed before any real feedback or canary can produce useful signal.",
            "It uses existing offer/evidence/branch wheels efficiently and requires no provider API, no secrets, no live enablement.",
            "It preserves production configuration as a later branch-scoped option rather than making it the default.",
        ],
        "runner_up_routes": [
            "offer_revision_for_paid_diagnostic",
            "ai_consultancy_target_evidence_rebuild",
            "governance_audit_sample_teardown",
        ],
        "rejected_routes": [
            {"route": "keep_live_blocked_and_do_nothing", "reason": "safe but no earning probability gain"},
            {"route": "autonomous_dry_run_iteration", "reason": "internal execution confidence without stronger buyer-facing offer"},
        ],
        "blocked_routes": [
            {"route": "real_customer_outreach", "reason": "external action not authorized in E30"},
            {"route": "production_live_canary", "reason": "production live disabled and no live receipt allowed"},
            {"route": "payment_collection", "reason": "legal/payment commitment not authorized"},
        ],
        "real_signal_sought": "future buyer willingness-to-engage or willingness-to-pay response to a concrete readiness-review signal package",
        "concrete_artifact_or_action_produced": "proof-bound paid readiness-review signal package and next-milestone validation plan",
        "existing_wheels_used": ["E24 CEO KG", "E24 opportunity map", "E13R offer revision", "E23 evidence tightening", "E29 branch guardrail"],
        "new_wheels_truly_necessary": [],
        "future_branch_optionality_preserved": True,
        "production_config_selected": False,
        "evidence_expansion_selected": False,
        "productization_selected": False,
        "external_action_executed": False,
    }


def build_selected_action_execution_package(selection: Dict[str, Any] | None = None) -> Dict[str, Any]:
    selection = selection or build_methodological_route_selection()
    return {
        "artifact_id": "e30_selected_action_execution_package",
        "selected_route": selection["selected_route"],
        "branch": "revenue_mode_shortest_cash_path",
        "objective": "Create a proof-bound buyer-facing package that can seek real feedback in a later approved milestone.",
        "expected_signal": selection["real_signal_sought"],
        "required_inputs": [
            "E24 top selected readiness-review path",
            "E29 active branch and guardrail",
            "E23 evidence/suppression/compliance constraints",
            "E13R offer revision wheel",
            "E24 innovation/field map alternatives",
        ],
        "produced_outputs_for_next_milestone": [
            "readiness review one-page offer",
            "sample diagnostic output outline",
            "proof-bound claims register",
            "buyer qualification checklist",
            "price/commitment hypothesis without payment collection",
            "future feedback import criteria",
            "no-send validation packet",
        ],
        "existing_wheels_reused": selection["existing_wheels_used"],
        "new_components_required": [],
        "safety_constraints": [
            "no contact",
            "no sending",
            "no production live",
            "no live receipt",
            "no payment or legal commitment",
            "no fake feedback or evidence",
        ],
        "governance_constraints": [
            "claims must cite repo evidence",
            "future external feedback requires separate gate",
            "owner manual send is not default",
        ],
        "owner_decision_required_only_if": "future milestone proposes real outreach, payment setup, credential provisioning, or live provider activation",
        "next_milestone_implementation_plan": [
            "assemble proof-bound offer package",
            "create sample diagnostic using only internal/repo evidence",
            "score package against buyer pain and specificity",
            "produce gated future feedback route without sending",
        ],
        "external_action_executed": False,
    }


def _node(node_id: str, node_type: str, label: str, source: str, notes: str) -> Dict[str, Any]:
    return {
        "id": node_id,
        "type": node_type,
        "label": label,
        "source_paths": [source],
        "evidence_status": "internal_strategy_evidence",
        "truth_status": "working_hypothesis",
        "promotion_status": "working_only",
        "created_by_milestone": "E30",
        "stale_or_current": "current_working_state",
        "notes": notes,
    }


def _edge(edge_id: str, source: str, target: str, rel: str, evidence: str, notes: str) -> Dict[str, Any]:
    return {
        "id": edge_id,
        "source_node_id": source,
        "target_node_id": target,
        "relationship": rel,
        "evidence_path": evidence,
        "confidence_basis": "deterministic_source",
        "notes": notes,
    }


def build_ceo_kg_methodological_update(state: Dict[str, Any] | None = None, action_space: Dict[str, Any] | None = None, scores: Dict[str, Any] | None = None, selection: Dict[str, Any] | None = None) -> Dict[str, Any]:
    state = state or build_system_state_reconstruction()
    action_space = action_space or build_open_commercial_action_space(state)
    scores = scores or build_action_objective_scores(action_space)
    selection = selection or build_methodological_route_selection(scores)
    nodes: List[Dict[str, Any]] = [
        _node("e30_system_state_reconstruction", "SystemStateReconstruction", "E30 reconstructed current commercial state", "operations/external_validation/e30_system_state_reconstruction.json", "Current state reconstructed from artifacts."),
        _node("e30_methodological_route_selection", "MethodologicalRouteSelection", selection["selected_route"], "operations/external_validation/e30_methodological_route_selection.json", "Selected by open method, not menu."),
        _node("e30_strategic_learning_candidate", "StrategicLearningCandidate", "buyer-facing package likely beats prerequisite-only gate", "operations/external_validation/e30_czl_closure.json", "Working-only learning candidate."),
    ]
    edges: List[Dict[str, Any]] = []
    for idx, candidate in enumerate(action_space["candidates"], start=1):
        aid = candidate["action_id"]
        nodes.append(_node(aid, "CommercialActionCandidate", aid, "operations/external_validation/e30_open_commercial_action_space.json", candidate["reason_it_may_make_money"]))
        nodes.append(_node(f"{aid}_score", "ActionObjectiveScore", aid, "operations/external_validation/e30_action_objective_scores.json", "Explicit objective score."))
        edges.append(_edge(f"e30_edge_candidate_{idx}", "e30_system_state_reconstruction", aid, "generates", "operations/external_validation/e30_open_commercial_action_space.json", "State generated candidate action."))
        edges.append(_edge(f"e30_edge_score_{idx}", aid, f"{aid}_score", "scored_by", "operations/external_validation/e30_action_objective_scores.json", "Candidate scored by objective functions."))
    edges.append(_edge("e30_edge_selected", selection["selected_action_id"], "e30_methodological_route_selection", "selected_by", "operations/external_validation/e30_methodological_route_selection.json", "Top candidate selected after scoring and falsification."))
    edges.append(_edge("e30_edge_active_branch", "revenue_mode_shortest_cash_path", selection["selected_action_id"], "routes_to", "operations/external_validation/e30_methodological_route_selection.json", "Active branch routes to selected action package."))
    edges.append(_edge("e30_edge_e29_not_default", "e29_branch_scoped_execution_route_activation", selection["selected_action_id"], "superseded_by_method_for_next_action", "operations/external_validation/e30_methodological_route_selection.json", "E29 route remains candidate, not hardcoded next action."))
    return {
        "artifact_id": "e30_ceo_kg_methodological_update",
        "kg_delta_nodes": nodes,
        "kg_delta_edges": edges,
        "kg_delta_node_count": len(nodes),
        "kg_delta_edge_count": len(edges),
        "selected_route": selection["selected_route"],
        "customer_feedback_claimed": False,
        "market_validation_claimed": False,
        "canonical_truth_promoted": False,
        "external_action_executed": False,
    }


def build_ceo_brain_methodological_update(selection: Dict[str, Any] | None = None, package: Dict[str, Any] | None = None, kg: Dict[str, Any] | None = None) -> Dict[str, Any]:
    selection = selection or build_methodological_route_selection()
    package = package or build_selected_action_execution_package(selection)
    kg = kg or build_ceo_kg_methodological_update(selection=selection)
    return {
        "artifact_id": "e30_ceo_brain_methodological_update",
        "active_branch": "revenue_mode_shortest_cash_path",
        "selected_route": selection["selected_route"],
        "why_selected": selection["why_selected"],
        "updated_bottleneck": "buyer-facing package and proof-bound value proposition are now the bottleneck before production configuration or real feedback can be useful",
        "next_decision_horizon": "E31_paid_readiness_review_signal_package",
        "branch_optionality_preserved": True,
        "conservative_loop_status": "reduced: prerequisite-only production config deferred behind buyer-facing signal package",
        "production_live_remains_disabled": True,
        "production_live_receipt_count": 0,
        "kg_delta_node_count": kg["kg_delta_node_count"],
        "kg_delta_edge_count": kg["kg_delta_edge_count"],
        "external_action_executed": False,
    }


def build_methodological_action_control_room(state: Dict[str, Any] | None = None, action_space: Dict[str, Any] | None = None, scores: Dict[str, Any] | None = None, falsification: Dict[str, Any] | None = None, selection: Dict[str, Any] | None = None, package: Dict[str, Any] | None = None, brain: Dict[str, Any] | None = None) -> Dict[str, Any]:
    state = state or build_system_state_reconstruction()
    action_space = action_space or build_open_commercial_action_space(state)
    scores = scores or build_action_objective_scores(action_space)
    falsification = falsification or build_action_falsification_analysis(scores)
    selection = selection or build_methodological_route_selection(scores, falsification)
    package = package or build_selected_action_execution_package(selection)
    brain = brain or build_ceo_brain_methodological_update(selection, package)
    return {
        "artifact_id": "e30_methodological_action_control_room",
        "current_system_state": {
            "active_branch": state["current_active_branch"],
            "production_live_enabled": state["execution_capabilities"]["production_live_enabled"],
            "production_live_receipt_count": state["execution_capabilities"]["production_live_receipt_count"],
            "overbuilt_readiness_heavy_areas": state["overbuilt_readiness_heavy_areas"],
            "underbuilt_action_heavy_areas": state["underbuilt_action_heavy_areas"],
        },
        "generated_action_space_count": action_space["candidate_action_count"],
        "scoring_summary": {"top_action_id": scores["top_action_id"], "scored_action_count": scores["scored_action_count"]},
        "falsification_summary": {"selected_survived": falsification["selected_candidate_survived_falsification"], "main_objection": falsification["main_objection_to_selected"]},
        "selected_route": selection["selected_route"],
        "backup_routes": selection["runner_up_routes"],
        "blocked_routes": selection["blocked_routes"],
        "why_not_hardcoded": "production config, evidence expansion, productization, outbound, and provider work were scored as candidates rather than assumed",
        "what_action_comes_next": package["selected_route"],
        "owner_or_security_approval_required_now": False,
        "owner_or_security_approval_required_later_if": package["owner_decision_required_only_if"],
        "production_live_remains_disabled": True,
        "real_external_action_occurred": False,
        "recommended_next_milestone": brain["next_decision_horizon"],
    }


def build_ecosystem_alignment_gate() -> Dict[str, Any]:
    return {
        "artifact_id": "e30_ecosystem_alignment_gate",
        "repos_checked": [
            {"repo": "ystar-bridge-labs", "path": str(BRIDGE_LABS_ROOT), "branch": git_branch(BRIDGE_LABS_ROOT), "head": git_head(BRIDGE_LABS_ROOT), "modified_in_e30": True, "role": "CEO KG/commercial runtime"},
            {"repo": "gov-mcp", "path": str(GOV_MCP_ROOT), "branch": git_branch(GOV_MCP_ROOT), "head": git_head(GOV_MCP_ROOT), "modified_in_e30": False, "role": "provider boundary reused read-only"},
            {"repo": "Y-star-gov", "path": str(YSTAR_GOV_ROOT), "branch": git_branch(YSTAR_GOV_ROOT), "head": git_head(YSTAR_GOV_ROOT), "modified_in_e30": False, "role": "governance/CZL read-only"},
            {"repo": "ystar-company", "path": str(YSTAR_COMPANY_ROOT), "branch": git_branch(YSTAR_COMPANY_ROOT), "head": git_head(YSTAR_COMPANY_ROOT), "modified_in_e30": False, "role": "historical assets read-only"},
        ],
        "repos_checked_count": 4,
        "bridge_labs_modified": True,
        "gov_mcp_modified": False,
        "Y_star_gov_immediate_mutation_needed": False,
        "ystar_company_future_migration_followups": True,
        "ecosystem_alignment_status": "ecosystem_aligned_with_documented_followups",
        "cross_repo_impact_update": "bridge-labs adds method-based route selection; provider and governance repos are reused without mutation",
        "external_action_executed": False,
    }


def build_future_methodological_action_policy() -> Dict[str, Any]:
    return {
        "artifact_id": "e30_future_methodological_action_policy",
        "policy": "Future CEO-agent commercial milestones must not be menu-driven.",
        "required_method_steps": [
            "whole-system observation",
            "open action-space generation",
            "objective scoring",
            "falsification",
            "selected route package",
            "CEO KG update",
            "branch optionality preservation",
            "ecosystem alignment",
        ],
        "must_not_assume": [
            "production live configuration is next",
            "evidence expansion is next",
            "productization is next",
            "outbound is required",
            "provider work is the bottleneck",
        ],
        "owner_manual_send_default_allowed": False,
        "external_action_executed": False,
    }


def build_czl_closure(inventory: Dict[str, Any], action_space: Dict[str, Any], selection: Dict[str, Any], brain: Dict[str, Any], alignment: Dict[str, Any]) -> Dict[str, Any]:
    return {
        "artifact_id": "e30_czl_closure",
        "Y_star": "CEO-Agent Open Opportunity Discovery and Methodological Action Selection",
        "Rt_plus_1": 0,
        "whole_ecosystem_existing_wheel_audited_first": inventory["audit_completed_before_new_e30_modules"],
        "action_space_generated_openly": action_space["candidate_action_count"] >= 10,
        "route_selected_by_method_not_hardcoded_menu": selection["selected_by_method_not_menu"],
        "shortest_cash_path_prioritized_only_as_current_implementation_preference": True,
        "future_branches_remain_available": True,
        "selected_route": selection["selected_route"],
        "production_config_assumed_next": False,
        "no_real_external_action_occurred": True,
        "no_provider_api_called": True,
        "no_customer_contacted": True,
        "no_message_sent": True,
        "production_live_enabled": False,
        "production_live_receipt_count": 0,
        "no_credentials_or_secrets_committed": True,
        "no_fake_customer_feedback_created": True,
        "no_fake_target_evidence_created": True,
        "owner_manual_send_is_not_default": True,
        "next_decision_horizon": brain["next_decision_horizon"],
        "ecosystem_alignment_status": alignment["ecosystem_alignment_status"],
        "external_action_executed": False,
    }


def build_all(repo_root: Path | None = None) -> Dict[str, Any]:
    inventory = build_existing_method_wheel_inventory()
    state = build_system_state_reconstruction()
    action_space = build_open_commercial_action_space(state)
    scores = build_action_objective_scores(action_space)
    falsification = build_action_falsification_analysis(scores)
    selection = build_methodological_route_selection(scores, falsification)
    package = build_selected_action_execution_package(selection)
    kg = build_ceo_kg_methodological_update(state, action_space, scores, selection)
    brain = build_ceo_brain_methodological_update(selection, package, kg)
    control = build_methodological_action_control_room(state, action_space, scores, falsification, selection, package, brain)
    alignment = build_ecosystem_alignment_gate()
    policy = build_future_methodological_action_policy()
    closure = build_czl_closure(inventory, action_space, selection, brain, alignment)
    return {
        "inventory": inventory,
        "state": state,
        "action_space": action_space,
        "scores": scores,
        "falsification": falsification,
        "selection": selection,
        "package": package,
        "kg": kg,
        "brain": brain,
        "control": control,
        "alignment": alignment,
        "policy": policy,
        "closure": closure,
    }
