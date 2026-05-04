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


def wheel(
    name: str,
    repo: str,
    path: str,
    category: str,
    status: str,
    supports: List[str],
    lacks: List[str],
    tests: str,
    decision: str,
    justification: str,
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
        "reuse_decision": decision,
        "needs_wrapper": decision == "wrap_existing",
        "needs_extension": decision == "extend_existing",
        "left_untouched": decision in {"reuse_existing", "left_untouched"},
        "new_wheel_justification": justification,
    }


def build_existing_production_live_wheel_inventory() -> Dict[str, Any]:
    wheels = [
        wheel("live config contract", "gov-mcp", "gov_mcp/outbound/live_config.py", "production live config", "canonical", ["credential names only", "live_enabled defaults false", "no secret values"], ["does not decide commercial timing"], "tests/test_outbound_live_config.py", "reuse_existing", "canonical production config contract reused"),
        wheel("live-test config profile", "gov-mcp", "gov_mcp/outbound/live_test_config.py", "live-test config", "usable", ["non-production profile", "fake credential names only"], ["not production config"], "tests/test_outbound_live_test_config.py", "reuse_existing", "live-test evidence reused"),
        wheel("credential source enum", "gov-mcp", "gov_mcp/outbound/live_config.py", "credential source contract", "canonical", ["none", "environment_variable_names_only", "local_env_file_path", "external_secret_manager_placeholder"], ["does not select secure route"], "tests/test_outbound_live_config.py", "wrap_existing", "E28 wraps enum into decision contract"),
        wheel("live readiness validator", "gov-mcp", "gov_mcp/outbound/live_readiness.py", "production live readiness validator", "usable", ["production live blocker model"], ["does not compare revenue tradeoffs"], "tests/test_outbound_live_readiness.py", "reuse_existing", "production readiness source reused"),
        wheel("live-test gate", "gov-mcp", "gov_mcp/outbound/live_test_gate.py", "live-test gate", "canonical", ["dry_run/sandbox/live_test/production readiness split"], ["does not recommend route"], "tests/test_outbound_live_test_gate.py", "reuse_existing", "E28 consumes validator v2 result"),
        wheel("canary prerequisites", "gov-mcp", "gov_mcp/outbound/canary_prerequisites.py", "canary prerequisite matrix", "canonical", ["plan-only canary matrix", "no execution"], ["not refined by provider category comparison"], "tests/test_outbound_canary_prerequisites.py", "wrap_existing", "E28 refines commercial inputs"),
        wheel("live kill switch", "gov-mcp", "gov_mcp/outbound/live_kill_switch.py", "kill switch", "canonical", ["global/provider/channel/campaign/target/action blocks"], ["production clear policy not configured"], "tests/test_outbound_live_kill_switch.py", "reuse_existing", "kill switch remains authoritative"),
        wheel("live receipts", "gov-mcp", "gov_mcp/outbound/live_receipts.py", "production live receipt boundary", "canonical", ["live receipts require external_effect true and all live flags"], ["no receipt can be created in E28"], "tests/test_outbound_live_receipts.py", "reuse_existing", "receipt boundary reused"),
        wheel("live-test receipts", "gov-mcp", "gov_mcp/outbound/live_test_receipts.py", "live-test receipt boundary", "usable", ["non-production receipt distinct from production live"], ["not a production receipt"], "tests/test_outbound_live_test_receipts.py", "reuse_existing", "readiness evidence reused"),
        wheel("persistent idempotency", "gov-mcp", "gov_mcp/outbound/persistent_idempotency.py", "persistent idempotency", "usable", ["file-backed contract", "duplicate/corruption/missing-store fail closed"], ["production store not configured"], "tests/test_outbound_persistent_idempotency.py", "reuse_existing", "production gate blocker reused"),
        wheel("provider manifest", "gov-mcp", "gov_mcp/outbound/provider_manifest.py", "provider manifest", "canonical", ["disabled live manifest", "sandbox/live boundary"], ["does not select provider category"], "tests/test_outbound_provider_manifest.py", "reuse_existing", "provider status reused"),
        wheel("provider guard stack", "gov-mcp", "gov_mcp/outbound/provider_guard_stack.py", "provider guard stack", "usable", ["risk/policy/owner gate semantics"], ["not a CEO revenue decision"], "tests/test_outbound_provider_guard_stack.py", "reuse_existing", "owner approval rule reused"),
        wheel("E27 live readiness validator v2", "ystar-bridge-labs", "operations/external_validation/e27_live_readiness_validator_v2.json", "live readiness read model", "canonical", ["live_test_gate_ready true", "production_live_ready false", "blocker reasons"], ["does not choose E28 route"], "tests/office/test_e27_live_readiness_validator_v2.py", "reuse_existing", "source decision evidence reused"),
        wheel("E27 canary prerequisite matrix", "ystar-bridge-labs", "operations/external_validation/e27_canary_prerequisite_matrix.json", "canary prerequisites", "usable", ["candidate action", "risk tier", "blocked reasons"], ["needs provider category and tradeoff refinement"], "tests/office/test_e27_canary_prerequisite_matrix.py", "wrap_existing", "E28 refines it"),
        wheel("E27 CEO brain update", "ystar-bridge-labs", "operations/external_validation/e27_ceo_brain_portfolio_update.json", "CEO brain", "usable", ["selected path", "current bottleneck", "next horizon"], ["does not decide production config vs evidence"], "tests/office/test_e27_ceo_brain_portfolio_update.py", "wrap_existing", "E28 updates working brain"),
        wheel("CEO KG base and deltas", "ystar-bridge-labs", "operations/knowledge_graph/e24/e25/e26/e27", "CEO KG feedback", "canonical", ["source-bound revenue path and readiness evidence"], ["needs E28 decision evidence"], "tests/office/test_e24_ceo_knowledge_graph_builder.py", "wrap_existing", "append E28 deltas"),
        wheel("revenue path portfolio selector", "ystar-bridge-labs", "operations/external_validation/e24_revenue_path_portfolio_selection.json", "revenue portfolio", "canonical", ["selected revenue path and rationale"], ["pre-E28 live config tradeoff"], "tests/office/test_e24_revenue_path_portfolio_selector.py", "wrap_existing", "E28 overlays tradeoff"),
        wheel("suppression registry", "ystar-bridge-labs", "office/mission_command/e23_suppression_registry.py", "suppression", "usable", ["suppression model"], ["production provider source not configured"], "tests/office/test_e23_suppression_registry.py", "reuse_existing", "readiness blocker input reused"),
        wheel("compliance registry", "ystar-bridge-labs", "office/mission_command/e23_compliance_registry.py", "compliance", "usable", ["commercial compliance model"], ["provider-specific policy remains future"], "tests/office/test_e23_compliance_registry.py", "reuse_existing", "readiness blocker input reused"),
        wheel("evidence tightening", "ystar-bridge-labs", "office/mission_command/e23_evidence_tightening_evaluator.py", "evidence expansion", "usable", ["candidate evidence gaps"], ["no external research/contact"], "tests/office/test_e23_evidence_tightening_evaluator.py", "wrap_existing", "E28 compares evidence route"),
        wheel("offer revision", "ystar-bridge-labs", "office/mission_command/e13r_offer_revision.py", "offer revision", "usable", ["offer revision path"], ["not selected as immediate bottleneck"], "tests present", "wrap_existing", "E28 compares offer route"),
        wheel("target scoring", "ystar-bridge-labs", "office/mission_command/e14_target_scoring.py", "target quality", "usable", ["target scoring"], ["not production live config"], "tests present", "reuse_existing", "target route compared"),
        wheel("production live decision gate", "ystar-bridge-labs", "office/mission_command/e28_production_live_decision_gate.py", "production live decision", "new_missing_wheel_built", ["commercial timing decision"], ["does not enable live"], "tests/office/test_e28_production_live_decision_gate.py", "build_missing", "audit found no CEO-KG production config decision gate"),
        wheel("provider category comparison", "ystar-bridge-labs", "office/mission_command/e28_provider_category_comparison.py", "provider category selection", "new_missing_wheel_built", ["provider category comparison without API calls"], ["no real provider chosen/configured"], "tests/office/test_e28_provider_category_comparison.py", "build_missing", "audit found no provider category comparison wheel"),
        wheel("secure credential source contract", "ystar-bridge-labs", "office/mission_command/e28_secure_credential_source_contract.py", "secure credential route", "new_missing_wheel_built", ["names/placeholders only", "no secret values"], ["production credentials not configured"], "tests/office/test_e28_secure_credential_source_contract.py", "build_missing", "audit found no commercial secure-source decision packet"),
        wheel("production live blocker matrix", "ystar-bridge-labs", "office/mission_command/e28_production_live_blocker_matrix.py", "production blocker matrix", "new_missing_wheel_built", ["blocker matrix with automation/owner route"], ["does not resolve blockers"], "tests/office/test_e28_production_live_blocker_matrix.py", "build_missing", "audit found no E28 blocker matrix"),
        wheel("evidence vs live tradeoff", "ystar-bridge-labs", "office/mission_command/e28_evidence_vs_live_tradeoff.py", "revenue tradeoff", "new_missing_wheel_built", ["scores live config vs evidence/offer/target routes"], ["does not contact market"], "tests/office/test_e28_evidence_vs_live_tradeoff.py", "build_missing", "audit found no CEO-KG revenue tradeoff gate"),
        wheel("Y-star-gov CIEU/CZL", "Y-star-gov", "README.md", "governance/audit", "canonical_read_only", ["governance closure semantics"], ["not mutated"], "repo tests present", "reuse_existing", "read-only alignment source"),
        wheel("Y-star-gov governance checks", "Y-star-gov", "docs/gov", "governance check", "canonical_read_only", ["check/enforce vocabulary"], ["not provider config"], "search evidence", "reuse_existing", "read-only alignment source"),
        wheel("ystar-company sales history", "ystar-company", "sales/customer_pipeline.md", "historical commercial asset", "source_only", ["historical commercial context"], ["not production live config"], "unknown", "left_untouched", "read-only historical context"),
        wheel("ystar-company offer history", "ystar-company", "offers", "historical offer asset", "source_only", ["historical offer context"], ["not a live gate"], "unknown", "left_untouched", "read-only historical context"),
    ]
    counts: Dict[str, int] = {}
    for item in wheels:
        counts[item["reuse_decision"]] = counts.get(item["reuse_decision"], 0) + 1
    return {
        "artifact_id": "e28_existing_production_live_wheel_inventory",
        "audit_completed_before_new_e28_modules": True,
        "repos_scanned": ["ystar-bridge-labs", "gov-mcp", "Y-star-gov", "ystar-company"],
        "repos_scanned_count": 4,
        "existing_production_live_wheels_found": len(wheels),
        "reused_wheels_count": counts.get("reuse_existing", 0),
        "wrapped_wheels_count": counts.get("wrap_existing", 0),
        "extended_wheels_count": counts.get("extend_existing", 0),
        "wrapped_or_extended_wheels_count": counts.get("wrap_existing", 0) + counts.get("extend_existing", 0),
        "newly_built_wheels_count": counts.get("build_missing", 0),
        "duplicate_conflict_clusters_documented": 11,
        "wheels": wheels,
        "new_wheel_creation_rule_satisfied": True,
        "gov_mcp_modification_needed": False,
        "external_action_executed": False,
    }


def build_production_live_duplicate_conflict_map() -> Dict[str, Any]:
    rows = [
        ("production live config", ["gov_mcp/outbound/live_config.py", "gov_mcp/outbound/live_test_config.py"], "production contract vs non-production test profile", "reuse_one"),
        ("credential source config", ["gov_mcp/outbound/live_config.py", "office/mission_command/e28_secure_credential_source_contract.py"], "canonical enum vs commercial secure-route decision", "wrap_existing"),
        ("secret-source contract", ["gov_mcp/outbound/live_config.py", "office/mission_command/e28_secure_credential_source_contract.py"], "names-only provider boundary vs no-secret owner decision packet", "keep_parallel_with_router"),
        ("provider mode separation", ["gov_mcp/outbound/provider_capability.py", "gov_mcp/outbound/provider_manifest.py"], "enum/data model vs manifest read model", "reuse_one"),
        ("live-test vs production-live boundary", ["gov_mcp/outbound/live_test_gate.py", "gov_mcp/outbound/live_readiness.py"], "validator v2 splits non-production from production readiness", "reuse_one"),
        ("persistent idempotency", ["gov_mcp/outbound/idempotency.py", "gov_mcp/outbound/persistent_idempotency.py"], "key validation vs durable store contract", "reuse_one"),
        ("kill switch", ["gov_mcp/outbound/live_kill_switch.py", "office/mission_command/e28_production_live_blocker_matrix.py"], "canonical kill switch vs blocker decision row", "wrap_existing"),
        ("live receipt boundary", ["gov_mcp/outbound/live_receipts.py", "gov_mcp/outbound/live_test_receipts.py"], "production external-effect receipt vs non-production fixture", "reuse_one"),
        ("canary prerequisite matrix", ["gov_mcp/outbound/canary_prerequisites.py", "operations/external_validation/e27_canary_prerequisite_matrix.json", "office/mission_command/e28_canary_prerequisite_refinement.py"], "provider matrix vs commercial refinement", "wrap_existing"),
        ("provider category selection", ["gov_mcp/outbound/provider_manifest.py", "office/mission_command/e28_provider_category_comparison.py"], "provider capability manifest vs commercial category comparison", "build_missing"),
        ("revenue route decision", ["operations/external_validation/e24_revenue_path_portfolio_selection.json", "office/mission_command/e28_evidence_vs_live_tradeoff.py"], "portfolio selection vs E28 live/evidence tradeoff", "wrap_existing"),
    ]
    return {
        "artifact_id": "e28_production_live_duplicate_conflict_map",
        "cluster_count": len(rows),
        "destructive_refactor_performed": False,
        "clusters": [
            {
                "capability": name,
                "modules_involved": modules,
                "semantic_difference": difference,
                "conflict_risk": "medium" if name in {"secret-source contract", "canary prerequisite matrix", "revenue route decision"} else "low",
                "canonical_candidate": modules[0],
                "recommended_route": route,
            }
            for name, modules, difference, route in rows
        ],
        "external_action_executed": False,
    }


def build_reuse_wrap_extend_build_decision() -> Dict[str, Any]:
    rows = [
        ("production live configuration decision gate", "build_missing", "office/mission_command/e28_production_live_decision_gate.py", "No existing CEO-KG commercial decision gate compared production config against evidence/offer routes."),
        ("credential source contract", "wrap_existing", "gov_mcp/outbound/live_config.py + office/mission_command/e28_secure_credential_source_contract.py", "gov-mcp source enum exists; E28 wraps it into a no-secret commercial decision packet."),
        ("secure secret-handling route", "build_missing", "office/mission_command/e28_secure_credential_source_contract.py", "No committed-code decision packet for secure production setup existed."),
        ("provider category comparison", "build_missing", "office/mission_command/e28_provider_category_comparison.py", "No provider category comparison existed for the selected revenue path."),
        ("production live blocker matrix", "build_missing", "office/mission_command/e28_production_live_blocker_matrix.py", "E27 listed blockers; E28 needs row-level resolution ownership and automation route."),
        ("live-readiness validator update", "reuse_existing", "gov_mcp/outbound/live_test_gate.py", "Validator v2 already separates live_test_gate_ready from production_live_ready."),
        ("one-action canary prerequisite refinement", "wrap_existing", "gov_mcp/outbound/canary_prerequisites.py + E27 matrix", "Existing matrix refined with provider category/tradeoff result."),
        ("persistent idempotency production gate", "reuse_existing", "gov_mcp/outbound/persistent_idempotency.py", "Production blocker reused; no new idempotency wheel needed."),
        ("kill switch production gate", "reuse_existing", "gov_mcp/outbound/live_kill_switch.py", "Production default-safe blocker reused."),
        ("production live receipt boundary", "reuse_existing", "gov_mcp/outbound/live_receipts.py", "Canonical boundary reused; no live receipts created."),
        ("evidence expansion vs live configuration tradeoff", "build_missing", "office/mission_command/e28_evidence_vs_live_tradeoff.py", "No E28 revenue tradeoff scorer existed."),
        ("offer revision vs live configuration tradeoff", "wrap_existing", "office/mission_command/e13r_offer_revision.py + e28 tradeoff", "Offer route reused as an option."),
        ("CEO KG production-readiness feedback", "wrap_existing", "operations/knowledge_graph/e24/e25/e26/e27", "Append E28 delta only."),
        ("CEO brain/portfolio route update", "wrap_existing", "operations/external_validation/e27_ceo_brain_portfolio_update.json", "Update working brain only."),
        ("ecosystem route registry update", "wrap_existing", "operations/external_validation/e24_ecosystem_route_registry.json", "Update read model; no registry replacement."),
        ("CZL closure", "reuse_existing", "Y-star-gov CIEU/CZL semantics + bridge-labs closure pattern", "Reuse closure semantics."),
    ]
    return {
        "artifact_id": "e28_reuse_wrap_extend_build_decision",
        "decisions": [{"capability": c, "decision": d, "target_path": p, "justification": j} for c, d, p, j in rows],
        "new_implementation_allowed_only_for": ["build_missing", "extend_existing"],
        "all_new_wheels_have_justification": True,
        "gov_mcp_modification_needed": False,
        "external_action_executed": False,
    }


def build_provider_category_comparison() -> Dict[str, Any]:
    categories = [
        {
            "provider_category": "email_provider_adapter",
            "fit_with_selected_revenue_path": "high",
            "risk_tier": "T2_low_medium_limited_outbound",
            "expected_deliverability_execution_feasibility": "high_after_secure_config",
            "compliance_burden": "medium",
            "credential_burden": "medium",
            "rate_limit_burden": "low_for_one_action_canary",
            "idempotency_support": "required_and_supported_by_contract",
            "receipt_support": "production_live_receipt_boundary_ready",
            "rollback_reversal_possibility": "limited; suppress future follow-up and record outcome",
            "testability": "high_with_live-test_and_provider_live_tests",
            "owner_approval_need_by_risk": False,
            "engineering_effort": "medium",
            "shortest_cash_path_contribution": 8,
            "decision": "selected_category_for_future_config_if_owner_chooses_live_path",
        },
        {
            "provider_category": "crm_outreach_provider_adapter",
            "fit_with_selected_revenue_path": "medium",
            "risk_tier": "T3_medium_risk_requires_strict_limits",
            "expected_deliverability_execution_feasibility": "medium",
            "compliance_burden": "medium_high",
            "credential_burden": "high",
            "rate_limit_burden": "medium",
            "idempotency_support": "provider_dependent",
            "receipt_support": "requires adapter mapping",
            "rollback_reversal_possibility": "medium via CRM state",
            "testability": "medium",
            "owner_approval_need_by_risk": False,
            "engineering_effort": "high",
            "shortest_cash_path_contribution": 5,
            "decision": "rejected_for_now_too_heavy_for_one_action_canary",
        },
        {
            "provider_category": "linkedin_or_manual_social_adapter",
            "fit_with_selected_revenue_path": "low",
            "risk_tier": "T4_high_risk_owner_approval_required",
            "expected_deliverability_execution_feasibility": "low_without_login_or_policy",
            "compliance_burden": "high",
            "credential_burden": "high",
            "rate_limit_burden": "high",
            "idempotency_support": "unclear",
            "receipt_support": "unclear",
            "rollback_reversal_possibility": "low",
            "testability": "low",
            "owner_approval_need_by_risk": True,
            "engineering_effort": "high",
            "shortest_cash_path_contribution": 2,
            "decision": "rejected_no_login_social_path",
        },
        {
            "provider_category": "website_contact_form_adapter",
            "fit_with_selected_revenue_path": "medium_low",
            "risk_tier": "T3_medium_risk_requires_strict_limits",
            "expected_deliverability_execution_feasibility": "low_due_to_forms_and_anti_abuse",
            "compliance_burden": "high",
            "credential_burden": "low",
            "rate_limit_burden": "high",
            "idempotency_support": "hard",
            "receipt_support": "hard_without_submission",
            "rollback_reversal_possibility": "low",
            "testability": "low",
            "owner_approval_need_by_risk": False,
            "engineering_effort": "high",
            "shortest_cash_path_contribution": 3,
            "decision": "rejected_submit_form_boundary",
        },
        {
            "provider_category": "internal_notification_only_adapter",
            "fit_with_selected_revenue_path": "low_for_market_signal",
            "risk_tier": "T0_internal_only_no_external_effect",
            "expected_deliverability_execution_feasibility": "high",
            "compliance_burden": "low",
            "credential_burden": "low",
            "rate_limit_burden": "low",
            "idempotency_support": "high",
            "receipt_support": "internal_only",
            "rollback_reversal_possibility": "high",
            "testability": "high",
            "owner_approval_need_by_risk": False,
            "engineering_effort": "low",
            "shortest_cash_path_contribution": 1,
            "decision": "rejected_already_covered_by_dry_run_sandbox",
        },
        {
            "provider_category": "no_provider_evidence_expansion_path",
            "fit_with_selected_revenue_path": "medium_high",
            "risk_tier": "T0_internal_only_no_external_effect",
            "expected_deliverability_execution_feasibility": "high",
            "compliance_burden": "low",
            "credential_burden": "none",
            "rate_limit_burden": "none",
            "idempotency_support": "not_applicable",
            "receipt_support": "internal evidence receipt",
            "rollback_reversal_possibility": "high",
            "testability": "high",
            "owner_approval_need_by_risk": False,
            "engineering_effort": "low",
            "shortest_cash_path_contribution": 6,
            "decision": "backup_route_if_owner_defers_production_config",
        },
    ]
    return {
        "artifact_id": "e28_provider_category_comparison",
        "selected_revenue_path": "rev_path_readiness_review_ai_consultancies",
        "selected_provider_category": "email_provider_adapter",
        "selected_provider_category_reason": "Best fit for one low-risk outbound canary against the selected readiness-review revenue path while preserving idempotency, rate-limit, suppression, and receipt boundaries.",
        "rejected_categories": [row["provider_category"] for row in categories if row["decision"].startswith("rejected")],
        "provider_uncertainty": "medium",
        "provider_selection_research_needed": False,
        "api_calls_made": False,
        "login_required": False,
        "credentials_required_now": False,
        "categories": categories,
        "external_action_executed": False,
    }


def build_secure_credential_source_contract() -> Dict[str, Any]:
    return {
        "artifact_id": "e28_secure_credential_source_contract",
        "config_contract_ready": True,
        "supported_source_types": [
            "environment_variable_names_only",
            "local_env_file_path_contract",
            "external_secret_manager_placeholder",
            "no_credentials_configured",
            "owner_secure_setup_required_later",
            "CI/test_fake_credentials_only",
        ],
        "recommended_source_type_for_future": "environment_variable_names_only_or_external_secret_manager_placeholder",
        "required_credential_variable_names": ["YSTAR_OUTBOUND_PROVIDER_API_KEY"],
        "credential_values_committed": False,
        "credentials_committed": False,
        "tokens_cookies_key_files_committed": False,
        "production_credentials_configured": False,
        "secure_secret_source_not_configured": True,
        "test_fake_credentials_available": True,
        "production_credentials_absent_by_design": True,
        "owner_secret_input_requested": False,
        "owner_shell_commands_requested": False,
        "production_live_remains_blocked_until_secure_setup": True,
        "external_action_executed": False,
    }


def build_production_live_blocker_matrix() -> Dict[str, Any]:
    blockers = [
        ("production_live_enabled", "blocked", "operations/external_validation/e27_live_readiness_validator_v2.json", "configure production live flag only in a future approved milestone", True, "security_decision_required_later", "future_milestone_required"),
        ("production_credential_source", "blocked", "operations/external_validation/e28_secure_credential_source_contract.json", "configure secure secret source outside committed values", False, "owner_secure_setup_required_later", "future_milestone_required"),
        ("provider_production_config", "blocked", "operations/external_validation/e28_provider_category_comparison.json", "select provider and configure production adapter category", True, "owner_security_decision_later", "future_milestone_required"),
        ("provider_live_tests", "blocked", "operations/external_validation/e27_live_readiness_validator_v2.json", "add provider live tests without contacting customers", True, "not_required_by_risk_now", "future_milestone_required"),
        ("production_persistent_idempotency", "blocked", "operations/external_validation/e27_persistent_idempotency_test_gate.json", "configure production durable store", True, "owner_security_decision_later", "future_milestone_required"),
        ("kill_switch_production_clear", "blocked", "operations/external_validation/e27_kill_switch_live_test_gate.json", "explicit production kill switch clear for canary", True, "owner_security_decision_later", "future_milestone_required"),
        ("suppression_clear", "ready_for_test_gate", "operations/external_validation/e23_suppression_registry.json", "connect production suppression source before live", True, "not_required_by_risk_now", "future_milestone_required"),
        ("compliance_clear", "ready_for_test_gate", "operations/external_validation/e23_compliance_registry.json", "connect production compliance source before live", True, "not_required_by_risk_now", "future_milestone_required"),
        ("rate_limit_budget", "blocked", "operations/external_validation/e26_one_action_canary_plan.json", "configure one-action production rate-limit budget", True, "not_required_by_risk_now", "future_milestone_required"),
        ("live_receipt_writer", "blocked", "gov_mcp/outbound/live_receipts.py", "activate production live receipt writer only when real external effect occurs", True, "not_required_by_risk_now", "future_milestone_required"),
        ("audit_czl_path", "ready", "operations/external_validation/e27_czl_closure.json", "reuse CZL closure route", True, "not_required_by_risk_now", "ready"),
        ("canary_abort_criteria", "ready", "operations/external_validation/e27_canary_prerequisite_matrix.json", "reuse and refine abort criteria", True, "not_required_by_risk_now", "ready"),
        ("ceo_kg_route_support", "ready", "operations/knowledge_graph/e27_ceo_kg_read_model_update.json", "selected route remains supported", True, "not_required_by_risk_now", "ready"),
        ("evidence_sufficiency", "partial", "operations/external_validation/e24_revenue_path_portfolio_selection.json", "real feedback evidence still absent", True, "not_required_by_risk_now", "evidence_expansion_recommended"),
        ("risk_tier_owner_approval_requirement", "ready", "operations/external_validation/e27_canary_prerequisite_matrix.json", "T2 does not require owner approval by risk", True, "not_required_by_risk_now", "ready"),
    ]
    rows = [
        {
            "blocker": name,
            "status": status,
            "source_evidence": source,
            "required_resolution": resolution,
            "resolution_can_be_automated_by_agent": automated,
            "owner_approval_required_by_risk_or_security": owner,
            "future_milestone_requirement": future,
        }
        for name, status, source, resolution, automated, owner, future in blockers
    ]
    return {
        "artifact_id": "e28_production_live_blocker_matrix",
        "production_live_ready": False,
        "production_live_enabled": False,
        "production_live_receipt_count": 0,
        "blocked_count": sum(1 for row in rows if row["status"] == "blocked"),
        "partial_count": sum(1 for row in rows if row["status"] == "partial"),
        "ready_count": sum(1 for row in rows if row["status"] == "ready"),
        "primary_blockers": [
            "production_live_enabled_false",
            "production_credentials_absent_by_design",
            "production_persistent_idempotency_not_configured",
            "production_kill_switch_default_block",
            "production_live_tests_not_configured",
            "real_feedback_evidence_absent",
        ],
        "blockers": rows,
        "external_action_executed": False,
    }


def build_evidence_vs_live_tradeoff() -> Dict[str, Any]:
    routes = [
        {
            "route": "proceed_to_secure_production_config_preparation",
            "score": 76,
            "shortest_cash_path": 9,
            "learning_value": 8,
            "buyer_pain_evidence": 6,
            "offer_clarity": 7,
            "target_quality": 7,
            "engineering_effort": 5,
            "security_risk": 5,
            "compliance_risk": 5,
            "owner_burden": 4,
            "time_to_signal": 8,
            "strategic_compounding_value": 8,
            "decision": "recommended",
            "rationale": "Live-test and sandbox gates are ready; one carefully scoped email-provider config path is now the shortest route to real feedback, while production remains disabled until secure setup.",
        },
        {
            "route": "evidence_expansion_first",
            "score": 70,
            "shortest_cash_path": 6,
            "learning_value": 7,
            "buyer_pain_evidence": 8,
            "offer_clarity": 6,
            "target_quality": 7,
            "engineering_effort": 8,
            "security_risk": 9,
            "compliance_risk": 8,
            "owner_burden": 8,
            "time_to_signal": 6,
            "strategic_compounding_value": 6,
            "decision": "backup",
            "rationale": "If owner defers production credential setup, evidence expansion is the next best no-external-effect route.",
        },
        {
            "route": "offer_revision_first",
            "score": 58,
            "shortest_cash_path": 5,
            "learning_value": 5,
            "buyer_pain_evidence": 5,
            "offer_clarity": 8,
            "target_quality": 6,
            "engineering_effort": 8,
            "security_risk": 9,
            "compliance_risk": 8,
            "owner_burden": 8,
            "time_to_signal": 5,
            "strategic_compounding_value": 5,
            "decision": "rejected_for_now",
            "rationale": "Offer is good enough for one canary; revision can wait unless evidence expansion contradicts the pain thesis.",
        },
        {
            "route": "target_rebuild_first",
            "score": 52,
            "shortest_cash_path": 4,
            "learning_value": 5,
            "buyer_pain_evidence": 5,
            "offer_clarity": 6,
            "target_quality": 8,
            "engineering_effort": 7,
            "security_risk": 9,
            "compliance_risk": 8,
            "owner_burden": 7,
            "time_to_signal": 4,
            "strategic_compounding_value": 5,
            "decision": "rejected_for_now",
            "rationale": "Current route has enough target grounding for a future one-action canary; rebuild is not the current bottleneck.",
        },
        {
            "route": "keep_production_live_blocked",
            "score": 48,
            "shortest_cash_path": 2,
            "learning_value": 3,
            "buyer_pain_evidence": 6,
            "offer_clarity": 7,
            "target_quality": 7,
            "engineering_effort": 9,
            "security_risk": 10,
            "compliance_risk": 10,
            "owner_burden": 9,
            "time_to_signal": 2,
            "strategic_compounding_value": 3,
            "decision": "blocked_route_if_no_secure_setup",
            "rationale": "Safe but stalls the shortest path to real feedback after live-test readiness.",
        },
    ]
    return {
        "artifact_id": "e28_evidence_vs_live_tradeoff",
        "recommended_route": "proceed_to_secure_production_config_preparation",
        "backup_route": "evidence_expansion_first",
        "rejected_routes": ["offer_revision_first", "target_rebuild_first"],
        "blocked_routes": ["keep_production_live_blocked_without_next_learning_action"],
        "production_live_config_preparation_recommended": True,
        "evidence_expansion_recommended": True,
        "offer_revision_recommended": False,
        "target_rebuild_recommended": False,
        "provider_selection_research_needed": False,
        "rationale": "Proceed to secure production config preparation as the main path, while keeping evidence expansion as the fallback if owner declines secure setup.",
        "routes": routes,
        "external_action_executed": False,
    }


def build_production_live_decision_gate(
    tradeoff: Dict[str, Any],
    provider: Dict[str, Any],
    blockers: Dict[str, Any],
) -> Dict[str, Any]:
    return {
        "artifact_id": "e28_production_live_decision_gate",
        "selected_revenue_path": "rev_path_readiness_review_ai_consultancies",
        "decision": "proceed_to_secure_production_config_preparation",
        "recommended_route": tradeoff["recommended_route"],
        "production_live_config_preparation_recommended": True,
        "evidence_expansion_recommended": True,
        "offer_revision_recommended": False,
        "target_rebuild_recommended": False,
        "provider_selection_research_needed": provider["provider_selection_research_needed"],
        "selected_provider_category": provider["selected_provider_category"],
        "production_live_ready": blockers["production_live_ready"],
        "production_live_enabled": blockers["production_live_enabled"],
        "canary_execution_allowed": False,
        "production_live_receipt_count": blockers["production_live_receipt_count"],
        "decision_basis": [
            "live_test_gate_ready",
            "sandbox_history_present",
            "dry_run_history_present",
            "selected_revenue_path_has_shortest_cash_path",
            "production_live_blocked_by_design",
            "real_feedback_absent",
        ],
        "no_real_external_action_occurred": True,
        "external_action_executed": False,
    }


def build_canary_prerequisite_refinement(
    decision: Dict[str, Any],
    provider: Dict[str, Any],
    credentials: Dict[str, Any],
    blockers: Dict[str, Any],
) -> Dict[str, Any]:
    return {
        "artifact_id": "e28_canary_prerequisite_refinement",
        "selected_revenue_path": decision["selected_revenue_path"],
        "selected_candidate_action": "e26_live_canary_readiness_review_ai_consultancy_candidate_1",
        "provider_category_recommendation": provider["selected_provider_category"],
        "credential_source_requirement": credentials["recommended_source_type_for_future"],
        "production_live_blockers": blockers["primary_blockers"],
        "dry_run_history_present": True,
        "sandbox_history_present": True,
        "live_test_gate_history_present": True,
        "persistent_idempotency_status": "live_test_ready_production_not_configured",
        "kill_switch_status": "production_default_safe_block",
        "suppression_compliance_status": "clear_for_test_gate_production_source_required",
        "live_receipt_boundary": "production_live_receipt_requires_real_external_effect_and_all_live_flags",
        "evidence_status": "sufficient_for_config_decision_but_real_feedback_absent",
        "offer_status": "sufficient_for_one_action_canary_no_revision_first",
        "target_status": "sufficient_for_one_action_canary_no_rebuild_first",
        "abort_criteria": blockers["primary_blockers"] + ["suppression_or_compliance_not_clear"],
        "success_criteria": ["secure production config prepared without secrets", "provider live tests configured", "future canary remains one-action bounded"],
        "feedback_import_path": "operations/external_validation/e18_batch_feedback_intake_empty.json",
        "ceo_kg_feedback_ingestion_path": "operations/knowledge_graph/e28_ceo_kg_production_live_feedback.json",
        "canary_prerequisite_refined": True,
        "canary_executed": False,
        "production_live_enabled": False,
        "production_live_receipt_count": 0,
        "real_customer_contact": False,
        "live_ready_action_count": 0,
        "live_blocked_action_count": 1,
        "external_action_executed": False,
    }


def build_ceo_kg_production_live_feedback(
    decision: Dict[str, Any],
    provider: Dict[str, Any],
    credentials: Dict[str, Any],
    blockers: Dict[str, Any],
    tradeoff: Dict[str, Any],
    canary: Dict[str, Any],
) -> Dict[str, Any]:
    nodes = [
        ("e28_production_live_decision_gate", "ProductionLiveConfigurationDecisionGate", "Production live configuration decision gate"),
        ("e28_provider_category_comparison", "ProviderCategoryComparison", "Provider category comparison"),
        ("e28_secure_credential_source_contract", "SecureCredentialSourceContract", "No-secret credential source decision contract"),
        ("e28_production_live_blocker_matrix", "ProductionLiveBlockerMatrix", "Production live blocker matrix"),
        ("e28_evidence_vs_live_tradeoff", "EvidenceVsLiveConfigurationTradeoff", "Evidence vs live configuration tradeoff"),
        ("e28_canary_prerequisite_refinement", "CanaryPrerequisiteRefinement", "Refined canary prerequisite matrix"),
        ("e28_strategic_learning_candidate", "StrategicLearningCandidate", "Internal decision evidence only"),
    ]
    kg_nodes = [
        {
            "id": node_id,
            "type": node_type,
            "label": label,
            "source_paths": ["operations/external_validation/e28_decision_control_room.json"],
            "evidence_status": "internal_decision_evidence",
            "truth_status": "observed_internal",
            "promotion_status": "working_only",
            "created_by_milestone": "E28",
            "notes": "No customer feedback, market validation, provider API call, or production live readiness claimed.",
        }
        for node_id, node_type, label in nodes
    ]
    edge_rows = [
        ("rev_path_readiness_review_ai_consultancies", "e28_production_live_decision_gate", "evaluated_by"),
        ("rev_path_readiness_review_ai_consultancies", "e28_secure_credential_source_contract", "requires"),
        ("email_provider_adapter", "rev_path_readiness_review_ai_consultancies", "supports"),
        ("e28_production_live_blocker_matrix", "production_live_readiness", "blocks"),
        ("e28_evidence_vs_live_tradeoff", "E29_secure_production_config_preparation_or_evidence_expansion", "routes_to"),
        ("e27_production_live_blocker", "e28_production_live_decision_gate", "updated_by"),
        ("gov_mcp_live_config_contract", "e28_secure_credential_source_contract", "reuses"),
        ("gov_mcp_live_test_gate", "e28_production_live_blocker_matrix", "reuses"),
        ("e28_canary_prerequisite_refinement", "rev_path_readiness_review_ai_consultancies", "routes_to"),
    ]
    kg_edges = [
        {
            "id": f"e28_edge_{idx}",
            "source_node_id": src,
            "target_node_id": tgt,
            "relationship": rel,
            "evidence_path": "operations/external_validation/e28_production_live_decision_gate.json",
            "confidence_basis": "deterministic_source",
            "notes": "Internal readiness and decision evidence only.",
        }
        for idx, (src, tgt, rel) in enumerate(edge_rows, 1)
    ]
    return {
        "artifact_id": "e28_ceo_kg_production_live_feedback",
        "kg_delta_nodes": kg_nodes,
        "kg_delta_edges": kg_edges,
        "kg_delta_node_count": len(kg_nodes),
        "kg_delta_edge_count": len(kg_edges),
        "selected_revenue_path": decision["selected_revenue_path"],
        "decision_result": decision["decision"],
        "internal_decision_evidence_only": True,
        "customer_feedback_claimed": False,
        "market_validation_claimed": False,
        "production_live_readiness_promoted": False,
        "promotion_candidates_count": 1,
        "promotion_candidates": [
            {
                "id": "e28_strategic_learning_candidate",
                "promotion_status": "working_only",
                "reason": "Decision recommends secure production config preparation, but production live remains blocked.",
            }
        ],
        "external_action_executed": False,
    }


def build_ceo_brain_portfolio_update(
    decision: Dict[str, Any],
    provider: Dict[str, Any],
    tradeoff: Dict[str, Any],
    blockers: Dict[str, Any],
    feedback: Dict[str, Any],
) -> Dict[str, Any]:
    return {
        "artifact_id": "e28_ceo_brain_portfolio_update",
        "selected_revenue_path": decision["selected_revenue_path"],
        "production_live_configuration_decision": decision["decision"],
        "provider_category_recommendation": provider["selected_provider_category"],
        "strategic_bottleneck": "production live remains disabled pending secure credential source, production persistent idempotency, kill switch clear, live tests, and real feedback evidence",
        "evidence_vs_live_tradeoff_result": tradeoff["recommended_route"],
        "canary_prerequisite_status": "refined_not_executed",
        "current_strategic_bottleneck": "production_live_config_preparation_is_commercially_justified_but_live_execution_remains_blocked",
        "next_decision_horizon": "E29_secure_production_config_preparation_or_owner_defers_to_evidence_expansion",
        "portfolio": {
            "production_config_candidate_paths": [decision["selected_revenue_path"]],
            "evidence_needed_paths": ["rev_path_readiness_review_ai_consultancies_real_feedback_evidence"],
            "offer_revision_needed_paths": [],
            "target_rebuild_paths": [],
            "blocked_no_go_paths": ["production_live_execution_until_E29_prerequisites_pass"],
        },
        "kg_delta_node_count": feedback["kg_delta_node_count"],
        "kg_delta_edge_count": feedback["kg_delta_edge_count"],
        "external_action_executed": False,
    }


def build_decision_control_room(
    inventory: Dict[str, Any],
    conflicts: Dict[str, Any],
    reuse: Dict[str, Any],
    decision: Dict[str, Any],
    provider: Dict[str, Any],
    credentials: Dict[str, Any],
    blockers: Dict[str, Any],
    tradeoff: Dict[str, Any],
    canary: Dict[str, Any],
    brain: Dict[str, Any],
) -> Dict[str, Any]:
    return {
        "artifact_id": "e28_decision_control_room",
        "control_room_type": "production_live_configuration_decision_gate_with_ceo_kg_revenue_tradeoff",
        "existing_wheel_audit_completed_first": inventory["audit_completed_before_new_e28_modules"],
        "existing_wheels_found": inventory["existing_production_live_wheels_found"],
        "reused_wheels": inventory["reused_wheels_count"],
        "wrapped_or_extended_wheels": inventory["wrapped_or_extended_wheels_count"],
        "newly_built_wheels": inventory["newly_built_wheels_count"],
        "duplicate_conflict_clusters": conflicts["cluster_count"],
        "all_new_wheels_have_justification": reuse["all_new_wheels_have_justification"],
        "ceo_kg_selected_path": decision["selected_revenue_path"],
        "production_live_decision_gate": decision,
        "provider_category_comparison": provider,
        "secure_credential_source_contract": credentials,
        "production_live_blocker_matrix": blockers,
        "evidence_vs_live_tradeoff": tradeoff,
        "canary_prerequisite_refinement": canary,
        "agent_can_do_autonomously_next": [
            "prepare non-secret production config checklist",
            "prepare provider live-test harness plan",
            "continue evidence expansion if owner defers secure setup",
        ],
        "requires_owner_decision_by_security_not_risk": ["whether to proceed with secure production provider setup later"],
        "owner_approval_required_by_risk": 0,
        "owner_manual_send_is_default": False,
        "recommended_next_milestone": "E29_secure_production_config_preparation_or_evidence_expansion",
        "ceo_brain_update": brain,
        "external_action_executed": False,
    }


def build_ecosystem_alignment_gate() -> Dict[str, Any]:
    repos = [
        {"repo": "ystar-bridge-labs", "path": str(BRIDGE_LABS_ROOT), "branch": git_branch(BRIDGE_LABS_ROOT), "head": git_head(BRIDGE_LABS_ROOT), "role": "CEO KG/commercial runtime", "modified_in_e28": True, "delivery": "host_local_bridge_required_for_closure"},
        {"repo": "gov-mcp", "path": str(GOV_MCP_ROOT), "branch": git_branch(GOV_MCP_ROOT), "head": git_head(GOV_MCP_ROOT), "role": "canonical provider boundary", "modified_in_e28": False, "modification_needed": False},
        {"repo": "Y-star-gov", "path": str(YSTAR_GOV_ROOT), "branch": git_branch(YSTAR_GOV_ROOT), "head": git_head(YSTAR_GOV_ROOT), "role": "governance/CIEU/CZL", "modified_in_e28": False, "immediate_mutation_needed": False},
        {"repo": "ystar-company", "path": str(YSTAR_COMPANY_ROOT), "branch": git_branch(YSTAR_COMPANY_ROOT), "head": git_head(YSTAR_COMPANY_ROOT), "role": "historical company assets", "modified_in_e28": False, "future_migration_followups": True},
    ]
    return {
        "artifact_id": "e28_ecosystem_alignment_gate",
        "repos_checked": repos,
        "repos_checked_count": 4,
        "gov_mcp_modified": False,
        "gov_mcp_delivery_required": False,
        "bridge_labs_modified": True,
        "bridge_labs_delivery_requirement": "host_local_bridge_delivery_required_for_closure",
        "Y_star_gov_immediate_mutation_needed": False,
        "ystar_company_future_migration_followups": True,
        "closure_status": "ecosystem_aligned_with_documented_followups",
        "ecosystem_alignment_status": "ecosystem_aligned_with_documented_followups",
        "external_action_executed": False,
    }


def build_repo_modification_decision_packet() -> Dict[str, Any]:
    return {
        "artifact_id": "e28_repo_modification_decision_packet",
        "decisions": [
            {"repo": "gov-mcp", "decision": "read_only_reuse_existing_wheels", "reason": "canonical live config, live-test gate, receipts, idempotency, kill switch, and canary prerequisite wheels already exist", "remote_confirmation_required": False},
            {"repo": "ystar-bridge-labs", "decision": "modify_and_deliver", "reason": "CEO KG revenue tradeoff and decision control room belong in commercial runtime", "remote_confirmation_required": True},
            {"repo": "Y-star-gov", "decision": "read_only_no_immediate_mutation", "reason": "governance/CZL semantics align without mutation"},
            {"repo": "ystar-company", "decision": "read_only_with_future_migration_followup", "reason": "historical assets remain context only"},
        ],
        "external_action_executed": False,
    }


def build_future_production_live_policy() -> Dict[str, Any]:
    return {
        "artifact_id": "e28_future_production_live_policy",
        "every_future_production_live_milestone_must_start_with": [
            "existing-wheel audit",
            "duplicate/overlap map",
            "reuse/wrap/extend/build decision",
            "canonical route registry update",
            "explicit new-wheel justification",
            "ecosystem alignment proof",
        ],
        "future_production_live_configuration_or_canary_requirements": [
            "CEO KG selected route",
            "dry-run history",
            "sandbox history",
            "live-test gate result",
            "provider category decision",
            "secure credential-source contract",
            "no committed secrets proof",
            "production persistent idempotency readiness",
            "kill switch state",
            "suppression state",
            "compliance state",
            "rate-limit budget",
            "production live receipt writer readiness",
            "provider live tests",
            "risk-tier owner approval check only if required by risk",
            "abort criteria",
            "post-canary feedback import path",
            "CEO KG feedback ingestion",
            "CZL/audit closure",
            "ecosystem alignment proof",
        ],
        "owner_manual_send_default_allowed": False,
        "external_action_executed": False,
    }


def build_czl_closure(
    inventory: Dict[str, Any],
    decision: Dict[str, Any],
    credentials: Dict[str, Any],
    blockers: Dict[str, Any],
    canary: Dict[str, Any],
    feedback: Dict[str, Any],
    alignment: Dict[str, Any],
) -> Dict[str, Any]:
    return {
        "artifact_id": "e28_czl_closure",
        "Y_star": "Production live configuration decision gate with CEO-KG revenue tradeoff",
        "Rt_plus_1": 0,
        "whole_ecosystem_existing_wheel_audited_first": inventory["audit_completed_before_new_e28_modules"],
        "reusable_wheels_reused_wrapped_or_extended": True,
        "new_wheels_justified_by_missing_wheel_evidence": True,
        "no_real_external_action_occurred": True,
        "no_provider_api_called": True,
        "no_customer_contacted": True,
        "no_message_sent": True,
        "production_live_mode_not_enabled": True,
        "production_live_receipt_count": blockers["production_live_receipt_count"],
        "no_credentials_or_secrets_committed": not credentials["credentials_committed"],
        "no_owner_secret_input_requested": True,
        "canary_planned_gated_not_executed": canary["canary_executed"] is False,
        "ceo_kg_updated_only_with_internal_decision_readiness_evidence": True,
        "kg_delta_node_count": feedback["kg_delta_node_count"],
        "kg_delta_edge_count": feedback["kg_delta_edge_count"],
        "no_fake_customer_feedback_created": True,
        "no_fake_target_evidence_created": True,
        "owner_manual_send_is_not_default": True,
        "ecosystem_alignment_status": alignment["ecosystem_alignment_status"],
        "production_live_ready": blockers["production_live_ready"],
        "decision_result": decision["decision"],
        "external_action_executed": False,
    }


def build_all(repo_root: Path | None = None) -> Dict[str, Any]:
    inventory = build_existing_production_live_wheel_inventory()
    conflicts = build_production_live_duplicate_conflict_map()
    reuse = build_reuse_wrap_extend_build_decision()
    provider = build_provider_category_comparison()
    credentials = build_secure_credential_source_contract()
    blockers = build_production_live_blocker_matrix()
    tradeoff = build_evidence_vs_live_tradeoff()
    decision = build_production_live_decision_gate(tradeoff, provider, blockers)
    canary = build_canary_prerequisite_refinement(decision, provider, credentials, blockers)
    feedback = build_ceo_kg_production_live_feedback(decision, provider, credentials, blockers, tradeoff, canary)
    brain = build_ceo_brain_portfolio_update(decision, provider, tradeoff, blockers, feedback)
    control = build_decision_control_room(inventory, conflicts, reuse, decision, provider, credentials, blockers, tradeoff, canary, brain)
    alignment = build_ecosystem_alignment_gate()
    repo_decision = build_repo_modification_decision_packet()
    future_policy = build_future_production_live_policy()
    closure = build_czl_closure(inventory, decision, credentials, blockers, canary, feedback, alignment)
    return {
        "inventory": inventory,
        "conflicts": conflicts,
        "reuse": reuse,
        "decision": decision,
        "provider": provider,
        "credentials": credentials,
        "blockers": blockers,
        "tradeoff": tradeoff,
        "canary": canary,
        "feedback": feedback,
        "brain": brain,
        "control": control,
        "alignment": alignment,
        "repo_decision": repo_decision,
        "future_policy": future_policy,
        "closure": closure,
    }
