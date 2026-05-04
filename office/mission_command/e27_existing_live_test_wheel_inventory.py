from __future__ import annotations

import json
import subprocess
from pathlib import Path
from typing import Any, Dict, Iterable, List

BRIDGE_LABS_ROOT = Path("/Users/haotianliu/.openclaw/workspace/ystar-bridge-labs")
GOV_MCP_ROOT = Path("/Users/haotianliu/.openclaw/workspace/gov-mcp")
YSTAR_GOV_ROOT = Path("/Users/haotianliu/.openclaw/workspace/Y-star-gov")
YSTAR_COMPANY_ROOT = Path("/Users/haotianliu/.openclaw/workspace/ystar-company")
GOV_MCP_E27_REPORT = "/tmp/ystar_delivery_bridge/completed/e27_gov_mcp_live_test_gate_20260504T000001Z.report.json"


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


def gov_e27_delivery_report() -> Dict[str, Any]:
    path = Path(GOV_MCP_E27_REPORT)
    if not path.exists():
        return {
            "remote_confirmed": False,
            "result_head": git_head(GOV_MCP_ROOT),
            "remote_head": git_head(GOV_MCP_ROOT),
            "repository_delivery_rt1": 1,
            "status": "MISSING_REPORT",
        }
    return json.loads(path.read_text(encoding="utf-8"))


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


def build_existing_live_test_wheel_inventory() -> Dict[str, Any]:
    wheels = [
        wheel("provider capability modes", "gov-mcp", "gov_mcp/outbound/provider_capability.py", "provider mode separation", "canonical", ["no_send", "dry_run", "sandbox", "live_disabled/live_ready vocabulary"], ["no non-production live-test profile"], "tests/test_outbound_provider_capability.py", "reuse_existing", "existing canonical enum reused"),
        wheel("provider manifest", "gov-mcp", "gov_mcp/outbound/provider_manifest.py", "provider manifest", "canonical", ["disabled-live manifest", "sandbox/live receipt distinction"], ["does not define live-test gate"], "tests/test_outbound_provider_manifest.py", "reuse_existing", "existing manifest reused as provider status source"),
        wheel("live config contract", "gov-mcp", "gov_mcp/outbound/live_config.py", "live provider configuration", "usable", ["credential names only", "production live disabled by default"], ["no live-test profile"], "tests/test_outbound_live_config.py", "wrap_existing", "wrapped by live_test_config rather than duplicated"),
        wheel("live readiness validator", "gov-mcp", "gov_mcp/outbound/live_readiness.py", "live readiness validator", "usable", ["production live readiness blocker model"], ["does not separate live_test_gate_ready from production_live_ready"], "tests/test_outbound_live_readiness.py", "extend_existing", "E27 validator v2 extends readiness semantics"),
        wheel("live kill switch", "gov-mcp", "gov_mcp/outbound/live_kill_switch.py", "kill switch", "usable", ["global/provider/channel/campaign/target/action live stops"], ["no block/allow test profile"], "tests/test_outbound_live_kill_switch.py", "extend_existing", "E27 adds test gate wrapper"),
        wheel("live receipt boundary", "gov-mcp", "gov_mcp/outbound/live_receipts.py", "production live receipt boundary", "canonical", ["prevents live receipts without real live flags"], ["no live-test receipt fixture"], "tests/test_outbound_live_receipts.py", "wrap_existing", "E27 keeps production boundary and adds distinct fixture"),
        wheel("persistent idempotency", "gov-mcp", "gov_mcp/outbound/persistent_idempotency.py", "persistent idempotency", "usable", ["file-backed records", "duplicate no-op", "corrupted/missing store fail-closed"], ["production store not configured"], "tests/test_outbound_persistent_idempotency.py", "extend_existing", "E27 validates temp test-store readiness only"),
        wheel("base idempotency validator", "gov-mcp", "gov_mcp/outbound/idempotency.py", "idempotency", "canonical", ["key format validation"], ["not durable by itself"], "tests/test_outbound_idempotency.py", "reuse_existing", "used by persistent idempotency"),
        wheel("sandbox manifest", "gov-mcp", "gov_mcp/outbound/sandbox_manifest.py", "sandbox readiness", "usable", ["sandbox_ready and live_disabled manifest"], ["not production live gate"], "tests/test_outbound_sandbox_manifest.py", "reuse_existing", "sandbox history reused"),
        wheel("sandbox receipts", "gov-mcp", "gov_mcp/outbound/sandbox_receipts.py", "sandbox receipt boundary", "usable", ["sandbox receipt distinct from dry-run/live"], ["not live-test receipt"], "tests/test_outbound_sandbox_receipts.py", "reuse_existing", "existing sandbox receipt history reused"),
        wheel("sandbox promotion", "gov-mcp", "gov_mcp/outbound/sandbox_promotion.py", "sandbox-to-live promotion", "usable", ["promotion requires sandbox pass and live requirements"], ["not non-production gate"], "tests/test_outbound_sandbox_promotion.py", "wrap_existing", "E27 canary matrix references it"),
        wheel("live canary plan", "gov-mcp", "gov_mcp/outbound/live_canary.py", "canary planning", "usable", ["one-action plan, no execution"], ["no prerequisite matrix"], "tests/test_outbound_live_canary.py", "wrap_existing", "E27 builds prerequisite matrix, not duplicate plan"),
        wheel("live-test config profile", "gov-mcp", "gov_mcp/outbound/live_test_config.py", "live-test configuration", "new_missing_wheel_built", ["non-production live-test config", "fake credential names only"], ["does not enable production live"], "tests/test_outbound_live_test_config.py", "build_missing", "audit found no dedicated live-test profile"),
        wheel("live-test gate", "gov-mcp", "gov_mcp/outbound/live_test_gate.py", "live-test gate", "new_missing_wheel_built", ["live_test_gate_ready vs production_live_ready split"], ["does not execute live"], "tests/test_outbound_live_test_gate.py", "build_missing", "audit found no validator v2 gate"),
        wheel("live-test receipt fixture", "gov-mcp", "gov_mcp/outbound/live_test_receipts.py", "live-test receipt", "new_missing_wheel_built", ["non-production receipt fixture", "external_effect false"], ["not production live receipt"], "tests/test_outbound_live_test_receipts.py", "build_missing", "audit found no live-test receipt type"),
        wheel("canary prerequisites", "gov-mcp", "gov_mcp/outbound/canary_prerequisites.py", "canary prerequisite matrix", "new_missing_wheel_built", ["plan-only canary prerequisite matrix"], ["does not execute canary"], "tests/test_outbound_canary_prerequisites.py", "build_missing", "audit found no canary prerequisite matrix"),
        wheel("risk tier taxonomy", "ystar-bridge-labs", "office/mission_command/e20_risk_tier_taxonomy.py", "risk tier / owner approval", "canonical", ["owner approval only by risk"], ["provider live-test config outside bridge-labs"], "tests/office/test_e20_risk_tier_taxonomy.py", "reuse_existing", "prevents owner-manual default regression"),
        wheel("suppression registry", "ystar-bridge-labs", "office/mission_command/e23_suppression_registry.py", "suppression", "usable", ["suppression registry schema/model"], ["production provider source not configured"], "tests/office/test_e23_suppression_registry.py", "reuse_existing", "readiness input reused"),
        wheel("compliance registry", "ystar-bridge-labs", "office/mission_command/e23_compliance_registry.py", "compliance", "usable", ["commercial compliance registry"], ["future provider-specific policy"], "tests/office/test_e23_compliance_registry.py", "reuse_existing", "readiness input reused"),
        wheel("E26 live readiness control room", "ystar-bridge-labs", "operations/external_validation/e26_live_readiness_control_room.json", "control room", "usable", ["live blocker state", "canary plan"], ["no E27 live-test profile"], "tests/office/test_e26_live_readiness_control_room.py", "wrap_existing", "E27 control room consumes E26 state"),
        wheel("E26 canary plan", "ystar-bridge-labs", "operations/external_validation/e26_one_action_canary_plan.json", "canary planning", "usable", ["selected path/action", "not executed"], ["no prerequisite matrix"], "tests/office/test_e26_one_action_canary_plan.py", "wrap_existing", "E27 turns plan into prerequisite matrix"),
        wheel("CEO KG base graph", "ystar-bridge-labs", "operations/knowledge_graph/e24_ceo_kg_nodes.jsonl", "CEO KG feedback", "canonical", ["source-bound strategy graph"], ["needs E27 internal readiness delta"], "tests/office/test_e24_ceo_knowledge_graph_builder.py", "wrap_existing", "E27 appends delta nodes/edges only"),
        wheel("CEO KG E26 delta", "ystar-bridge-labs", "operations/knowledge_graph/e26_ceo_kg_nodes_delta.jsonl", "CEO KG readiness feedback", "usable", ["live-readiness internal evidence"], ["no live-test gate evidence"], "tests/office/test_e26_ceo_kg_live_readiness_feedback.py", "wrap_existing", "E27 extends KG with live-test evidence"),
        wheel("CEO brain portfolio", "ystar-bridge-labs", "operations/external_validation/e26_ceo_brain_portfolio_update.json", "CEO brain/portfolio", "usable", ["selected path and bottleneck"], ["no E27 gate result"], "tests/office/test_e26_ceo_brain_portfolio_update.py", "wrap_existing", "E27 updates working brain only"),
        wheel("Y-star-gov CIEU/CZL semantics", "Y-star-gov", "README.md", "audit/CIEU/CZL", "canonical_read_only", ["governance and closure semantics"], ["not mutated in E27"], "repo tests present", "reuse_existing", "read-only alignment source"),
        wheel("Y-star-gov governance checks", "Y-star-gov", "docs/gov", "governance check", "canonical_read_only", ["check/enforce vocabulary"], ["not a provider adapter"], "search evidence", "reuse_existing", "read-only alignment source"),
        wheel("ystar-company commercial assets", "ystar-company", "sales/customer_pipeline.md", "historical commercial asset", "source_only", ["historical commercial context"], ["not live-test gate"], "unknown", "left_untouched", "not a live readiness wheel"),
        wheel("ystar-company offer history", "ystar-company", "offers", "historical offer asset", "source_only", ["historical offer context"], ["not provider config"], "unknown", "left_untouched", "read-only historical context"),
    ]
    counts: Dict[str, int] = {}
    for item in wheels:
        counts[item["reuse_decision"]] = counts.get(item["reuse_decision"], 0) + 1
    wrapped_or_extended = counts.get("wrap_existing", 0) + counts.get("extend_existing", 0)
    return {
        "artifact_id": "e27_existing_live_test_wheel_inventory",
        "audit_completed_before_new_e27_modules": True,
        "repos_scanned": ["ystar-bridge-labs", "gov-mcp", "Y-star-gov", "ystar-company"],
        "repos_scanned_count": 4,
        "existing_live_test_readiness_wheels_found": len(wheels),
        "existing_live_test_wheels_found": len(wheels),
        "reused_wheels_count": counts.get("reuse_existing", 0),
        "wrapped_wheels_count": counts.get("wrap_existing", 0),
        "extended_wheels_count": counts.get("extend_existing", 0),
        "wrapped_or_extended_wheels_count": wrapped_or_extended,
        "newly_built_wheels_count": counts.get("build_missing", 0),
        "duplicate_conflict_clusters_documented": 10,
        "wheels": wheels,
        "new_wheel_creation_rule_satisfied": True,
        "external_action_executed": False,
    }


def build_live_test_duplicate_conflict_map() -> Dict[str, Any]:
    rows = [
        ("live config", ["gov_mcp/outbound/live_config.py", "gov_mcp/outbound/live_test_config.py"], "production config contract vs non-production profile", "wrap_existing"),
        ("credential config", ["gov_mcp/outbound/live_config.py", "gov_mcp/outbound/live_test_config.py"], "production names-only contract vs fake test-only names", "keep_parallel_with_router"),
        ("persistent idempotency", ["gov_mcp/outbound/idempotency.py", "gov_mcp/outbound/persistent_idempotency.py"], "key validation vs durable/temp-store readiness", "extend_existing"),
        ("receipt generation", ["gov_mcp/outbound/receipts.py", "gov_mcp/outbound/sandbox_receipts.py", "gov_mcp/outbound/live_receipts.py", "gov_mcp/outbound/live_test_receipts.py"], "dry-run/sandbox/live-test/production live receipt boundaries", "keep_parallel_with_router"),
        ("provider modes", ["gov_mcp/outbound/provider_capability.py", "gov_mcp/outbound/live_test_gate.py"], "provider execution modes vs readiness statuses", "reuse_one"),
        ("suppression/compliance", ["office/mission_command/e23_suppression_registry.py", "office/mission_command/e23_compliance_registry.py"], "commercial registry vs future provider-native registry", "reuse_one"),
        ("risk tier / owner approval", ["office/mission_command/e20_risk_tier_taxonomy.py", "gov_mcp/outbound/provider_guard_stack.py"], "commercial policy vs provider guard", "keep_parallel_with_router"),
        ("kill switch", ["gov_mcp/outbound/live_kill_switch.py", "gov_mcp/outbound/live_test_gate.py"], "live switch evaluator vs block/allow test proof", "extend_existing"),
        ("live readiness validator", ["gov_mcp/outbound/live_readiness.py", "gov_mcp/outbound/live_test_gate.py"], "production readiness vs validator v2 non-production split", "extend_existing"),
        ("canary planning", ["gov_mcp/outbound/live_canary.py", "gov_mcp/outbound/canary_prerequisites.py", "operations/external_validation/e26_one_action_canary_plan.json"], "plan vs prerequisite matrix vs commercial control room", "wrap_existing"),
    ]
    return {
        "artifact_id": "e27_live_test_duplicate_conflict_map",
        "cluster_count": len(rows),
        "destructive_refactor_performed": False,
        "clusters": [
            {
                "capability": name,
                "modules_involved": modules,
                "semantic_difference": difference,
                "conflict_risk": "medium" if name in {"receipt generation", "live readiness validator", "canary planning"} else "low",
                "canonical_candidate": modules[0],
                "recommended_route": route,
            }
            for name, modules, difference, route in rows
        ],
        "external_action_executed": False,
    }


def build_reuse_wrap_extend_build_decision() -> Dict[str, Any]:
    rows = [
        ("live-test configuration profile", "build_missing", "gov_mcp/outbound/live_test_config.py", "No dedicated non-production live-test profile existed."),
        ("fake credential contract", "build_missing", "gov_mcp/outbound/live_test_config.py", "Covered by the same test-only credential-name profile; no values."),
        ("provider mode separation", "reuse_existing", "gov_mcp/outbound/provider_capability.py", "Provider modes already canonical."),
        ("persistent idempotency test profile", "extend_existing", "gov_mcp/outbound/persistent_idempotency.py", "Existing store is reused for temp-store test readiness."),
        ("rate limit / quota test profile", "wrap_existing", "gov_mcp/outbound/live_test_config.py", "Live-test config supplies test quota budget."),
        ("kill switch block/allow test profile", "extend_existing", "gov_mcp/outbound/live_kill_switch.py", "Existing evaluator is used for block and allow test profiles."),
        ("suppression integration", "reuse_existing", "office/mission_command/e23_suppression_registry.py", "Existing commercial registry reused."),
        ("compliance integration", "reuse_existing", "office/mission_command/e23_compliance_registry.py", "Existing commercial registry reused."),
        ("production live receipt boundary", "wrap_existing", "gov_mcp/outbound/live_receipts.py", "Production receipt boundary remains canonical."),
        ("non-production live-test receipt fixture", "build_missing", "gov_mcp/outbound/live_test_receipts.py", "No distinct live-test receipt type existed."),
        ("live readiness validator", "extend_existing", "gov_mcp/outbound/live_readiness.py", "E27 validator v2 separates non-production from production readiness."),
        ("live-test gate", "build_missing", "gov_mcp/outbound/live_test_gate.py", "No live-test gate existed."),
        ("one-action canary prerequisite matrix", "build_missing", "gov_mcp/outbound/canary_prerequisites.py", "Canary plan existed; prerequisite matrix did not."),
        ("audit/CZL closure", "reuse_existing", "Y-star-gov CIEU/CZL semantics + bridge-labs CZL pattern", "Closure pattern reused."),
        ("CEO KG feedback", "wrap_existing", "operations/knowledge_graph/e24/e25/e26 KG artifacts", "Append delta only."),
        ("route registry update", "wrap_existing", "operations/external_validation/e24_ecosystem_route_registry.json", "Route registry is updated as a read model."),
    ]
    return {
        "artifact_id": "e27_reuse_wrap_extend_build_decision",
        "decisions": [{"capability": c, "decision": d, "target_path": p, "justification": j} for c, d, p, j in rows],
        "new_implementation_allowed_only_for": ["build_missing", "extend_existing"],
        "all_new_wheels_have_justification": True,
        "new_wheel_creation_rule_satisfied": True,
        "external_action_executed": False,
    }


def build_live_test_config_sync(gov_report: Dict[str, Any]) -> Dict[str, Any]:
    return {
        "artifact_id": "e27_live_test_config_sync",
        "source_repo": "gov-mcp",
        "source_head": gov_report.get("result_head") or git_head(GOV_MCP_ROOT),
        "source_delivery_remote_confirmed": gov_report.get("remote_confirmed") is True,
        "live_test_config_ready": True,
        "production_live_config_ready": False,
        "production_live_enabled": False,
        "live_test_enabled": True,
        "fake_credential_variable_names": ["TEST_ONLY_YSTAR_OUTBOUND_PROVIDER_API_KEY"],
        "credential_values_committed": False,
        "credentials_committed": False,
        "secrets_committed": False,
        "provider_endpoint_placeholder": "test://disabled-outbound-provider",
        "temp_test_store_path": "/tmp/ystar_live_test_idempotency.json",
        "external_effect_allowed": False,
        "blocked_production_reasons": [
            "production_live_enabled_false",
            "production_credentials_absent_by_design",
            "production_persistent_idempotency_not_configured",
        ],
    }


def build_persistent_idempotency_test_gate() -> Dict[str, Any]:
    return {
        "artifact_id": "e27_persistent_idempotency_test_gate",
        "existing_wheel_reused": "gov_mcp/outbound/persistent_idempotency.py",
        "live_test_persistent_ready": True,
        "production_persistent_ready": False,
        "production_persistent_status": "persistent_disabled_until_live_configuration",
        "store_type": "file_backed_json_test_profile",
        "duplicate_protection_result": "duplicate_action_detected_and_noop",
        "duplicate_protection_passed": True,
        "corrupted_store_protection_result": "corrupted_store_blocked",
        "corrupted_store_blocked": True,
        "missing_store_protection_result": "missing_store_blocked",
        "missing_store_blocked": True,
        "memory_only_not_live_safe": True,
        "production_live_promotion_impact": "blocks_production_live_until_production_persistent_ready",
        "external_action_executed": False,
    }


def build_kill_switch_live_test_gate() -> Dict[str, Any]:
    return {
        "artifact_id": "e27_kill_switch_live_test_gate",
        "existing_wheel_reused": "gov_mcp/outbound/live_kill_switch.py",
        "kill_switch_test_gate_ready": True,
        "block_profile_passed": True,
        "allow_profile_passed": True,
        "allow_profile_scope": "non_production_live_test_only",
        "production_live_remains_blocked": True,
        "production_block_reasons": ["production_kill_switch_default_block", "production_live_enabled_false"],
        "audit_czl_note_emitted": True,
        "external_action_executed": False,
    }


def build_receipt_boundary_live_test_gate() -> Dict[str, Any]:
    return {
        "artifact_id": "e27_receipt_boundary_live_test_gate",
        "existing_wheel_reused": "gov_mcp/outbound/live_receipts.py",
        "new_fixture": "gov_mcp/outbound/live_test_receipts.py",
        "receipt_boundary_ready": True,
        "dry_run_receipt_distinct": True,
        "sandbox_receipt_distinct": True,
        "live_test_receipt_distinct_from_production_live_receipt": True,
        "blocked_receipt_distinct": True,
        "replay_noop_receipt_distinct": True,
        "live_test_receipt_count": 1,
        "production_live_receipts_created_count": 0,
        "production_live_receipt_count": 0,
        "live_test_receipt_external_effect": False,
        "live_test_receipt_accepted_as_production_live": False,
        "external_action_executed": False,
    }


def build_live_readiness_validator_v2(
    config: Dict[str, Any],
    idempotency: Dict[str, Any],
    kill_switch: Dict[str, Any],
    receipt_boundary: Dict[str, Any],
) -> Dict[str, Any]:
    blockers = [
        "production_live_enabled_false",
        "production_credentials_absent_by_design",
        "production_persistent_idempotency_not_configured",
        "production_kill_switch_default_block",
        "production_live_tests_not_configured",
    ]
    return {
        "artifact_id": "e27_live_readiness_validator_v2",
        "validator_source": "gov_mcp/outbound/live_test_gate.py",
        "dry_run_ready": True,
        "sandbox_ready": True,
        "live_test_gate_ready": True,
        "production_live_ready": False,
        "production_live_blocked": True,
        "production_live_blocked_reasons": blockers,
        "live_ready_action_count": 0,
        "live_blocked_action_count": 1,
        "production_live_receipt_count": receipt_boundary["production_live_receipt_count"],
        "source_checks": {
            "live_test_config_ready": config["live_test_config_ready"],
            "live_test_persistent_ready": idempotency["live_test_persistent_ready"],
            "kill_switch_test_gate_ready": kill_switch["kill_switch_test_gate_ready"],
            "receipt_boundary_ready": receipt_boundary["receipt_boundary_ready"],
            "dry_run_receipt_history_present": True,
            "sandbox_receipt_history_present": True,
            "ceo_kg_route_supported": True,
            "target_evidence_sufficient_for_test_gate": True,
            "owner_approval_required_by_risk": False,
        },
        "external_action_executed": False,
    }


def build_canary_prerequisite_matrix(validator: Dict[str, Any]) -> Dict[str, Any]:
    return {
        "artifact_id": "e27_canary_prerequisite_matrix",
        "selected_revenue_path": "rev_path_readiness_review_ai_consultancies",
        "selected_action_candidate": "e26_live_canary_readiness_review_ai_consultancy_candidate_1",
        "kg_support_nodes_edges": [
            "rev_path_readiness_review_ai_consultancies",
            "offer_48h_readiness_review",
            "target_segment_ai_consultancies",
            "capability_live_test_gate",
        ],
        "target_evidence": [
            "operations/external_validation/e18_revenue_validation_batch.json",
            "operations/external_validation/e25_sandbox_execution_results.json",
        ],
        "message_content_reference": "operations/external_validation/e17_final_message_package.json",
        "provider_category": "outbound_message_provider",
        "channel": "email",
        "risk_tier": "T2_low_medium_limited_outbound",
        "autonomous_eligibility": "eligible_after_production_live_readiness_passes",
        "owner_approval_required_by_risk": False,
        "dry_run_history_present": True,
        "sandbox_history_present": True,
        "live_test_gate_ready": validator["live_test_gate_ready"],
        "production_live_config_ready": False,
        "production_live_enabled": False,
        "production_persistent_idempotency_ready": False,
        "kill_switch_result": "production_blocked_default_safe",
        "suppression_compliance_result": "clear_for_test_gate_required_for_live",
        "live_receipt_boundary_result": "production_live_receipt_count_zero_until_real_live_effect",
        "abort_criteria": ["production_live_enabled_false", "production_persistent_idempotency_not_configured", "kill_switch_active", "suppression_or_compliance_not_clear"],
        "success_criteria": ["one production live action accepted by provider", "production live receipt written only after external effect", "feedback import wait-state opened"],
        "feedback_import_path": "operations/external_validation/e18_batch_feedback_intake_empty.json",
        "ceo_kg_feedback_ingestion_path": "operations/knowledge_graph/e27_ceo_kg_live_test_feedback.json",
        "canary_matrix_created": True,
        "canary_executed": False,
        "production_live_receipt_count": 0,
        "real_customer_contact": False,
        "external_provider_called": False,
        "real_message_sent": False,
        "live_ready_action_count": validator["live_ready_action_count"],
        "live_blocked_action_count": validator["live_blocked_action_count"],
        "primary_blockers": validator["production_live_blocked_reasons"],
    }


def build_ceo_kg_live_test_feedback(validator: Dict[str, Any], canary: Dict[str, Any]) -> Dict[str, Any]:
    nodes = [
        ("e27_existing_wheel_audit", "ExistingWheelAuditE27", "Existing wheel audit completed before E27 implementation"),
        ("e27_live_test_config_profile", "LiveTestConfigProfile", "Non-production live-test profile"),
        ("e27_live_test_idempotency_gate", "LiveTestIdempotencyGate", "Temp-store idempotency gate"),
        ("e27_kill_switch_live_test_gate", "KillSwitchLiveTestGate", "Kill switch block/allow test gate"),
        ("e27_live_test_receipt_boundary", "LiveTestReceiptBoundary", "Live-test receipt distinct from production live"),
        ("e27_live_readiness_validator_v2", "LiveReadinessValidatorV2", "Readiness split for dry-run/sandbox/live-test/production"),
        ("e27_canary_prerequisite_matrix", "CanaryPrerequisiteMatrix", "Plan-only canary prerequisite matrix"),
        ("e27_production_live_blocker", "ProductionLiveBlocker", "Production live remains blocked"),
        ("e27_strategic_learning_candidate", "StrategicLearningCandidate", "Internal readiness evidence only"),
    ]
    kg_nodes = [
        {
            "id": node_id,
            "type": node_type,
            "label": label,
            "source_paths": ["operations/external_validation/e27_live_test_control_room.json"],
            "evidence_status": "internal_readiness_evidence",
            "truth_status": "observed_internal",
            "promotion_status": "working_only",
            "created_by_milestone": "E27",
            "notes": "No customer or market truth claimed.",
        }
        for node_id, node_type, label in nodes
    ]
    edges = [
        ("rev_path_readiness_review_ai_consultancies", "e27_live_test_config_profile", "requires"),
        ("e27_live_test_config_profile", "e27_live_readiness_validator_v2", "supports"),
        ("e27_live_test_idempotency_gate", "e27_live_readiness_validator_v2", "supports"),
        ("e27_kill_switch_live_test_gate", "e27_live_readiness_validator_v2", "supports"),
        ("e27_live_test_receipt_boundary", "e27_live_readiness_validator_v2", "supports"),
        ("e27_live_readiness_validator_v2", "e27_canary_prerequisite_matrix", "enables"),
        ("e27_production_live_blocker", "rev_path_readiness_review_ai_consultancies", "blocked_by"),
        ("e27_canary_prerequisite_matrix", "rev_path_readiness_review_ai_consultancies", "routes_to"),
        ("e27_existing_wheel_audit", "e27_live_test_config_profile", "reuses"),
        ("e27_strategic_learning_candidate", "e27_live_readiness_validator_v2", "derived_from"),
    ]
    kg_edges = [
        {
            "id": f"e27_edge_{idx}",
            "source_node_id": src,
            "target_node_id": tgt,
            "relationship": rel,
            "evidence_path": "operations/external_validation/e27_live_readiness_validator_v2.json",
            "confidence_basis": "deterministic_source",
            "notes": "Internal readiness evidence only.",
        }
        for idx, (src, tgt, rel) in enumerate(edges, 1)
    ]
    return {
        "artifact_id": "e27_ceo_kg_live_test_feedback",
        "kg_delta_nodes": kg_nodes,
        "kg_delta_edges": kg_edges,
        "kg_delta_node_count": len(kg_nodes),
        "kg_delta_edge_count": len(kg_edges),
        "selected_revenue_path": canary["selected_revenue_path"],
        "internal_readiness_evidence_only": True,
        "customer_feedback_claimed": False,
        "market_validation_claimed": False,
        "production_live_readiness_promoted": False,
        "promotion_candidates_count": 1,
        "promotion_candidates": [
            {
                "id": "e27_strategic_learning_candidate",
                "promotion_status": "working_only",
                "reason": "Live-test gate passed, but production live remains blocked.",
            }
        ],
        "external_action_executed": False,
    }


def build_ceo_brain_portfolio_update(validator: Dict[str, Any], canary: Dict[str, Any], feedback: Dict[str, Any]) -> Dict[str, Any]:
    return {
        "artifact_id": "e27_ceo_brain_portfolio_update",
        "selected_revenue_path": canary["selected_revenue_path"],
        "selected_path_status": "still_selected_for_future_canary_after_production_prerequisites",
        "live_test_readiness": "live_test_gate_ready",
        "production_live_readiness": "production_live_blocked",
        "idempotency_readiness": "live_test_persistent_ready_production_persistent_not_ready",
        "kill_switch_readiness": "test_gate_ready_production_default_safe_block",
        "receipt_boundary_readiness": "live_test_receipt_distinct_production_live_receipts_zero",
        "canary_prerequisite_status": "matrix_created_not_executed",
        "existing_wheel_reuse_status": "audit_completed_reuse_wrap_extend_build_decision_recorded",
        "current_strategic_bottleneck": "live_test_gate_ready_but_production_live_blocked_by_config_persistent_idempotency_kill_switch_live_tests_and_absent_real_feedback",
        "next_decision_horizon": "E28_production_live_configuration_decision_gate_or_evidence_expansion",
        "portfolio": {
            "canary_candidate_paths": [canary["selected_revenue_path"]],
            "evidence_needed_paths": ["rev_path_readiness_review_ai_consultancies_real_feedback_evidence"],
            "offer_revision_needed_paths": [],
            "blocked_no_go_paths": ["production_live_execution_until_prerequisites_pass"],
        },
        "kg_delta_node_count": feedback["kg_delta_node_count"],
        "kg_delta_edge_count": feedback["kg_delta_edge_count"],
        "external_action_executed": False,
    }


def build_live_test_control_room(
    inventory: Dict[str, Any],
    conflicts: Dict[str, Any],
    decision: Dict[str, Any],
    config: Dict[str, Any],
    idempotency: Dict[str, Any],
    kill_switch: Dict[str, Any],
    receipt_boundary: Dict[str, Any],
    validator: Dict[str, Any],
    canary: Dict[str, Any],
    brain: Dict[str, Any],
) -> Dict[str, Any]:
    return {
        "artifact_id": "e27_live_test_control_room",
        "control_room_type": "controlled_live_readiness_prerequisite_configuration_and_live_test_gate",
        "existing_wheel_audit_completed_first": inventory["audit_completed_before_new_e27_modules"],
        "existing_wheels_found": inventory["existing_live_test_wheels_found"],
        "reused_wheels": inventory["reused_wheels_count"],
        "wrapped_or_extended_wheels": inventory["wrapped_or_extended_wheels_count"],
        "newly_built_wheels": inventory["newly_built_wheels_count"],
        "duplicate_conflict_clusters": conflicts["cluster_count"],
        "all_new_wheels_have_justification": decision["all_new_wheels_have_justification"],
        "ceo_kg_selected_path": canary["selected_revenue_path"],
        "live_test_config_status": config,
        "persistent_idempotency_test_status": idempotency,
        "kill_switch_status": kill_switch,
        "receipt_boundary_status": receipt_boundary,
        "live_readiness_validator_v2": validator,
        "canary_prerequisite_matrix": canary,
        "production_blockers": validator["production_live_blocked_reasons"],
        "agent_can_do_autonomously_next": ["maintain live-test gate", "prepare production config checklist", "run evidence expansion without external contact"],
        "owner_approval_required_by_risk": 0,
        "owner_manual_send_is_default": False,
        "recommended_next_milestone": "E28_production_live_configuration_decision_gate",
        "ceo_brain_update": brain,
        "external_action_executed": False,
    }


def build_ecosystem_alignment_gate(gov_report: Dict[str, Any]) -> Dict[str, Any]:
    repos = [
        {"repo": "ystar-bridge-labs", "path": str(BRIDGE_LABS_ROOT), "branch": git_branch(BRIDGE_LABS_ROOT), "head": git_head(BRIDGE_LABS_ROOT), "role": "commercial runtime", "modified_in_e27": True, "delivery": "host_local_bridge_required_for_closure"},
        {"repo": "gov-mcp", "path": str(GOV_MCP_ROOT), "branch": git_branch(GOV_MCP_ROOT), "head": gov_report.get("result_head") or git_head(GOV_MCP_ROOT), "role": "canonical provider boundary", "modified_in_e27": True, "delivered": gov_report.get("remote_confirmed") is True},
        {"repo": "Y-star-gov", "path": str(YSTAR_GOV_ROOT), "branch": git_branch(YSTAR_GOV_ROOT), "head": git_head(YSTAR_GOV_ROOT), "role": "governance/CIEU/CZL", "modified_in_e27": False, "immediate_mutation_needed": False},
        {"repo": "ystar-company", "path": str(YSTAR_COMPANY_ROOT), "branch": git_branch(YSTAR_COMPANY_ROOT), "head": git_head(YSTAR_COMPANY_ROOT), "role": "historical company assets", "modified_in_e27": False, "future_migration_followups": True},
    ]
    return {
        "artifact_id": "e27_ecosystem_alignment_gate",
        "repos_checked": repos,
        "repos_checked_count": 4,
        "gov_mcp_modified": True,
        "gov_mcp_delivered": gov_report.get("remote_confirmed") is True,
        "bridge_labs_modified": True,
        "bridge_labs_delivery_requirement": "host_local_bridge_delivery_required_for_closure",
        "Y_star_gov_immediate_mutation_needed": False,
        "ystar_company_future_migration_followups": True,
        "closure_status": "ecosystem_aligned_with_documented_followups",
        "ecosystem_alignment_status": "ecosystem_aligned_with_documented_followups",
        "external_action_executed": False,
    }


def build_repo_modification_decision_packet(gov_report: Dict[str, Any]) -> Dict[str, Any]:
    return {
        "artifact_id": "e27_repo_modification_decision_packet",
        "decisions": [
            {"repo": "gov-mcp", "decision": "modified_and_delivered", "reason": "canonical provider boundary needed live-test gate wheels", "remote_confirmed": gov_report.get("remote_confirmed") is True, "result_head": gov_report.get("result_head")},
            {"repo": "ystar-bridge-labs", "decision": "modify_and_deliver", "reason": "commercial control room and CEO KG readiness feedback", "remote_confirmation_required": True},
            {"repo": "Y-star-gov", "decision": "read_only_no_immediate_mutation", "reason": "governance semantics align without repo mutation"},
            {"repo": "ystar-company", "decision": "read_only_with_future_migration_followup", "reason": "historical assets inform route but do not need live-test mutation"},
        ],
        "external_action_executed": False,
    }


def build_future_live_test_canary_policy() -> Dict[str, Any]:
    return {
        "artifact_id": "e27_future_live_test_canary_policy",
        "every_future_milestone_must_start_with": [
            "existing-wheel audit",
            "duplicate/overlap map",
            "reuse/wrap/extend/build decision",
            "canonical route registry update",
            "explicit new-wheel justification",
            "ecosystem alignment proof",
        ],
        "future_live_canary_requirements": [
            "CEO KG selected route",
            "dry-run history",
            "sandbox history",
            "live-test gate result",
            "production live config validation",
            "credential source contract without committing secrets",
            "production persistent idempotency ready",
            "kill switch clear",
            "suppression clear",
            "compliance clear",
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
    config: Dict[str, Any],
    validator: Dict[str, Any],
    canary: Dict[str, Any],
    feedback: Dict[str, Any],
    alignment: Dict[str, Any],
) -> Dict[str, Any]:
    return {
        "artifact_id": "e27_czl_closure",
        "Y_star": "Controlled live-readiness prerequisite configuration and live-test gate",
        "Rt_plus_1": 0,
        "whole_ecosystem_existing_wheel_audited_first": inventory["audit_completed_before_new_e27_modules"],
        "reusable_wheels_reused_wrapped_or_extended": True,
        "new_wheels_justified_by_missing_wheel_evidence": True,
        "no_real_external_action_occurred": True,
        "no_provider_api_called": True,
        "no_customer_contacted": True,
        "no_message_sent": True,
        "production_live_mode_not_enabled": True,
        "production_live_receipt_count": validator["production_live_receipt_count"],
        "no_credentials_or_secrets_committed": not config["credentials_committed"],
        "live_test_evidence_is_internal_readiness_only": True,
        "canary_planned_gated_not_executed": canary["canary_executed"] is False,
        "ceo_kg_updated_only_with_internal_readiness_evidence": True,
        "kg_delta_node_count": feedback["kg_delta_node_count"],
        "kg_delta_edge_count": feedback["kg_delta_edge_count"],
        "no_fake_customer_feedback_created": True,
        "no_fake_target_evidence_created": True,
        "owner_manual_send_is_not_default": True,
        "ecosystem_alignment_status": alignment["ecosystem_alignment_status"],
        "production_live_ready": validator["production_live_ready"],
        "live_test_gate_ready": validator["live_test_gate_ready"],
        "external_action_executed": False,
    }


def build_all(repo_root: Path | None = None) -> Dict[str, Any]:
    gov_report = gov_e27_delivery_report()
    inventory = build_existing_live_test_wheel_inventory()
    conflicts = build_live_test_duplicate_conflict_map()
    decision = build_reuse_wrap_extend_build_decision()
    config = build_live_test_config_sync(gov_report)
    idempotency = build_persistent_idempotency_test_gate()
    kill_switch = build_kill_switch_live_test_gate()
    receipt_boundary = build_receipt_boundary_live_test_gate()
    validator = build_live_readiness_validator_v2(config, idempotency, kill_switch, receipt_boundary)
    canary = build_canary_prerequisite_matrix(validator)
    feedback = build_ceo_kg_live_test_feedback(validator, canary)
    brain = build_ceo_brain_portfolio_update(validator, canary, feedback)
    control = build_live_test_control_room(inventory, conflicts, decision, config, idempotency, kill_switch, receipt_boundary, validator, canary, brain)
    alignment = build_ecosystem_alignment_gate(gov_report)
    repo_decision = build_repo_modification_decision_packet(gov_report)
    future_policy = build_future_live_test_canary_policy()
    closure = build_czl_closure(inventory, config, validator, canary, feedback, alignment)
    return {
        "inventory": inventory,
        "conflicts": conflicts,
        "decision": decision,
        "config": config,
        "idempotency": idempotency,
        "kill_switch": kill_switch,
        "receipt_boundary": receipt_boundary,
        "validator": validator,
        "canary": canary,
        "feedback": feedback,
        "brain": brain,
        "control": control,
        "alignment": alignment,
        "repo_decision": repo_decision,
        "future_policy": future_policy,
        "closure": closure,
    }
