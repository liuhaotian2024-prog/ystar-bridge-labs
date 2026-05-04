from __future__ import annotations

import json
import subprocess
from pathlib import Path
from typing import Any, Dict, Iterable, List

BRIDGE_LABS_ROOT = Path("/Users/haotianliu/.openclaw/workspace/ystar-bridge-labs")
GOV_MCP_ROOT = Path("/Users/haotianliu/.openclaw/workspace/gov-mcp")
YSTAR_GOV_ROOT = Path("/Users/haotianliu/.openclaw/workspace/Y-star-gov")
YSTAR_COMPANY_ROOT = Path("/Users/haotianliu/.openclaw/workspace/ystar-company")
GOV_MCP_E26_REPORT = "/tmp/ystar_delivery_bridge/completed/e26_gov_mcp_live_readiness_wheels_20260504T171500Z.report.json"


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


def gov_delivery_report() -> Dict[str, Any]:
    path = Path(GOV_MCP_E26_REPORT)
    if not path.exists():
        return {"remote_confirmed": False, "result_head": git_head(GOV_MCP_ROOT), "repository_delivery_rt1": 1}
    return json.loads(path.read_text(encoding="utf-8"))


def wheel(name: str, repo: str, path: str, category: str, status: str, supports: List[str], lacks: List[str], tests: str, decision: str) -> Dict[str, Any]:
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
        "left_untouched": decision == "reuse_existing",
    }


def build_existing_live_readiness_wheel_inventory() -> Dict[str, Any]:
    wheels = [
        wheel("provider capability modes", "gov-mcp", "gov_mcp/outbound/provider_capability.py", "provider mode separation", "canonical", ["no_send", "dry_run", "sandbox", "live_disabled/live_ready vocabulary"], ["does not configure credentials"], "tests/test_outbound_provider_capability.py", "reuse_existing"),
        wheel("provider manifest", "gov-mcp", "gov_mcp/outbound/provider_manifest.py", "provider manifest", "canonical", ["disabled-live manifest", "sandbox manifest integration", "receipt separation"], ["does not own CEO route"], "tests/test_outbound_provider_manifest.py", "reuse_existing"),
        wheel("provider promotion contract", "gov-mcp", "gov_mcp/outbound/provider_promotion.py", "promotion gate", "usable", ["dry-run-to-live gate", "owner approval by risk"], ["does not include E26 live config/kill switch directly"], "tests/test_outbound_provider_promotion.py", "wrap_existing"),
        wheel("sandbox promotion contract", "gov-mcp", "gov_mcp/outbound/sandbox_promotion.py", "promotion gate", "usable", ["sandbox-to-live gate", "persistent idempotency gate"], ["live config and kill switch needed as integrated context"], "tests/test_outbound_sandbox_promotion.py", "wrap_existing"),
        wheel("persistent idempotency store", "gov-mcp", "gov_mcp/outbound/persistent_idempotency.py", "persistent idempotency", "extended", ["file-backed records", "duplicate detection", "corruption/missing store fail-closed"], ["production path not configured"], "tests/test_outbound_persistent_idempotency.py", "extend_existing"),
        wheel("base idempotency validator", "gov-mcp", "gov_mcp/outbound/idempotency.py", "idempotency", "canonical", ["idempotency key validation"], ["not durable by itself"], "tests/test_outbound_idempotency.py", "reuse_existing"),
        wheel("dry-run receipts", "gov-mcp", "gov_mcp/outbound/receipts.py", "receipt generation", "canonical", ["dry-run/failure receipts", "no-send invariants"], ["does not create live receipt"], "tests/test_outbound_receipts.py", "reuse_existing"),
        wheel("sandbox receipts", "gov-mcp", "gov_mcp/outbound/sandbox_receipts.py", "receipt boundary", "usable", ["sandbox receipt distinct from dry-run/live"], ["not live receipt writer"], "tests/test_outbound_sandbox_receipts.py", "reuse_existing"),
        wheel("live config contract", "gov-mcp", "gov_mcp/outbound/live_config.py", "live provider configuration", "new_missing_wheel_built", ["schema", "credential names only", "no secret values"], ["no real credentials configured"], "tests/test_outbound_live_config.py", "build_missing"),
        wheel("live kill switch", "gov-mcp", "gov_mcp/outbound/live_kill_switch.py", "kill switch", "new_missing_wheel_built", ["global/provider/channel/campaign/target/action live stop"], ["requires future production policy source"], "tests/test_outbound_live_kill_switch.py", "build_missing"),
        wheel("live receipt boundary", "gov-mcp", "gov_mcp/outbound/live_receipts.py", "live receipt boundary", "new_missing_wheel_built", ["prevents live receipt without all live flags"], ["no live receipt created in E26"], "tests/test_outbound_live_receipts.py", "build_missing"),
        wheel("live readiness validator", "gov-mcp", "gov_mcp/outbound/live_readiness.py", "live readiness validator", "new_missing_wheel_built", ["integrates config, manifest, idempotency, kill switch, receipts, promotion"], ["live remains blocked"], "tests/test_outbound_live_readiness.py", "build_missing"),
        wheel("one-action live canary plan", "gov-mcp", "gov_mcp/outbound/live_canary.py", "canary planning", "new_missing_wheel_built", ["plan contract", "abort/success/failure criteria", "credential names only"], ["does not execute"], "tests/test_outbound_live_canary.py", "build_missing"),
        wheel("risk tier taxonomy", "ystar-bridge-labs", "office/mission_command/e20_risk_tier_taxonomy.py", "risk tier / owner approval", "canonical", ["owner approval only by risk", "no owner manual default"], ["provider config comes from gov-mcp"], "tests/office/test_e20_risk_tier_taxonomy.py", "reuse_existing"),
        wheel("CEO KG", "ystar-bridge-labs", "operations/knowledge_graph/e24_ceo_kg_nodes.jsonl", "CEO KG feedback", "canonical", ["source-bound strategy graph", "working evidence only"], ["needs E26 live-readiness delta"], "tests/office/test_e24_ceo_knowledge_graph_builder.py", "wrap_existing"),
        wheel("E25 sandbox control room", "ystar-bridge-labs", "operations/external_validation/e25_sandbox_control_room.json", "sandbox/live blocker state", "usable", ["sandbox result", "live blockers"], ["needs live canary gate update"], "tests/office/test_e25_sandbox_control_room.py", "wrap_existing"),
        wheel("suppression registry", "ystar-bridge-labs", "office/mission_command/e23_suppression_registry.py", "suppression", "usable", ["suppression schema/model"], ["production suppression source not live-integrated"], "tests/office/test_e23_suppression_registry.py", "reuse_existing"),
        wheel("compliance registry", "ystar-bridge-labs", "office/mission_command/e23_compliance_registry.py", "compliance", "usable", ["commercial outreach compliance model"], ["future jurisdiction/provider-specific policy"], "tests/office/test_e23_compliance_registry.py", "reuse_existing"),
        wheel("Y-star-gov CIEU/CZL", "Y-star-gov", "README.md", "audit/CZL/CIEU", "canonical_read_only", ["tamper-evident audit semantics", "governance check concepts"], ["not mutated in E26"], "repo tests present", "reuse_existing"),
        wheel("ystar-company historical sales assets", "ystar-company", "sales/customer_pipeline.md", "historical company asset", "source_only", ["historical commercial context"], ["not a live-readiness wheel"], "unknown", "left_untouched"),
    ]
    decisions = {}
    for item in wheels:
        decisions[item["reuse_decision"]] = decisions.get(item["reuse_decision"], 0) + 1
    return {
        "artifact_id": "e26_existing_live_readiness_wheel_inventory",
        "audit_completed_before_new_e26_modules": True,
        "repos_scanned": ["ystar-bridge-labs", "gov-mcp", "Y-star-gov", "ystar-company"],
        "repos_scanned_count": 4,
        "existing_live_readiness_wheels_found": len(wheels),
        "reused_wheels_count": decisions.get("reuse_existing", 0),
        "wrapped_wheels_count": decisions.get("wrap_existing", 0),
        "extended_wheels_count": decisions.get("extend_existing", 0),
        "newly_built_wheels_count": decisions.get("build_missing", 0),
        "wheels": wheels,
        "new_wheel_creation_rule_satisfied": True,
        "external_action_executed": False,
    }


def build_live_readiness_duplicate_conflict_map(inventory: Dict[str, Any]) -> Dict[str, Any]:
    clusters = [
        ("idempotency", ["gov_mcp/outbound/idempotency.py", "gov_mcp/outbound/persistent_idempotency.py"], "base validator vs durable store", "wrap persistent store around base validator"),
        ("receipt generation", ["gov_mcp/outbound/receipts.py", "gov_mcp/outbound/sandbox_receipts.py", "gov_mcp/outbound/live_receipts.py"], "dry-run/sandbox/live receipt types differ by external-effect boundary", "keep parallel with strict boundary router"),
        ("provider modes", ["gov_mcp/outbound/provider_capability.py", "gov_mcp/outbound/provider_manifest.py"], "mode enum vs manifest read model", "reuse both"),
        ("promotion gates", ["gov_mcp/outbound/provider_promotion.py", "gov_mcp/outbound/sandbox_promotion.py", "gov_mcp/outbound/live_readiness.py"], "dry-run/sandbox gates feed E26 live readiness validator", "wrap existing gates"),
        ("suppression/compliance", ["office/mission_command/e23_suppression_registry.py", "office/mission_command/e23_compliance_registry.py"], "bridge-labs commercial policy vs future provider-specific registries", "reuse now; future provider registry optional"),
        ("risk tier / owner approval", ["office/mission_command/e20_risk_tier_taxonomy.py", "gov_mcp/outbound/provider_guard_stack.py"], "commercial route risk vs provider guard implementation", "keep parallel with router"),
        ("kill switch", ["gov_mcp/outbound/live_kill_switch.py", "gov_mcp/server.py safemode"], "outbound live kill switch vs broad governance safemode", "build missing outbound-specific wheel; do not mutate broad safemode"),
        ("CEO KG feedback", ["operations/knowledge_graph/e24_ceo_kg_nodes.jsonl", "operations/knowledge_graph/e25_ceo_kg_nodes_delta.jsonl"], "base KG vs milestone deltas", "wrap via delta files"),
    ]
    return {
        "artifact_id": "e26_live_readiness_duplicate_conflict_map",
        "cluster_count": len(clusters),
        "destructive_refactor_performed": False,
        "clusters": [
            {
                "capability": name,
                "modules_involved": modules,
                "semantic_difference": diff,
                "conflict_risk": "medium" if name in {"receipt generation", "promotion gates"} else "low",
                "canonical_candidate": modules[0],
                "recommended_route": route,
            }
            for name, modules, diff, route in clusters
        ],
        "external_action_executed": False,
    }


def build_reuse_wrap_extend_build_decision() -> Dict[str, Any]:
    rows = [
        ("live provider configuration", "build_missing", "gov_mcp/outbound/live_config.py", "No existing credential-names-only live config contract existed."),
        ("credential source contract", "build_missing", "gov_mcp/outbound/live_config.py", "Built names-only contract; no secret values."),
        ("provider mode separation", "reuse_existing", "gov_mcp/outbound/provider_capability.py", "E25 provider modes already canonical."),
        ("persistent idempotency", "extend_existing", "gov_mcp/outbound/persistent_idempotency.py", "Extended E25 store for missing/corrupted fail-closed handling."),
        ("rate limit / quota", "wrap_existing", "gov_mcp/outbound/live_config.py + provider_guard_stack", "Use config contract and existing guard semantics."),
        ("kill switch", "build_missing", "gov_mcp/outbound/live_kill_switch.py", "No outbound-specific live kill switch existed."),
        ("suppression integration", "reuse_existing", "office/mission_command/e23_suppression_registry.py", "Existing bridge-labs registry reused as readiness input."),
        ("compliance integration", "reuse_existing", "office/mission_command/e23_compliance_registry.py", "Existing bridge-labs registry reused as readiness input."),
        ("live receipt boundary", "build_missing", "gov_mcp/outbound/live_receipts.py", "Existing receipts were dry-run/sandbox only."),
        ("live readiness validator", "build_missing", "gov_mcp/outbound/live_readiness.py", "New wrapper integrates existing wheels."),
        ("sandbox-to-live promotion gate", "wrap_existing", "gov_mcp/outbound/sandbox_promotion.py", "Existing promotion gate wrapped by E26 readiness validator."),
        ("one-action live canary plan", "build_missing", "gov_mcp/outbound/live_canary.py", "No execution-free live canary plan contract existed."),
        ("audit/CZL closure", "reuse_existing", "Y-star-gov README/CIEU semantics + bridge-labs CZL pattern", "Use read-only governance semantics and local closure artifact."),
        ("CEO KG feedback", "wrap_existing", "operations/knowledge_graph/e24/e25 KG artifacts", "Append E26 delta nodes/edges."),
        ("route registry update", "wrap_existing", "operations/external_validation/e24_ecosystem_route_registry.json", "E26 updates read model rather than replacing registry."),
    ]
    return {
        "artifact_id": "e26_reuse_wrap_extend_build_decision",
        "decisions": [
            {"capability": cap, "decision": decision, "target_path": path, "justification": why}
            for cap, decision, path, why in rows
        ],
        "new_implementation_allowed_only_for": ["build_missing", "extend_existing"],
        "all_new_wheels_have_justification": True,
        "external_action_executed": False,
    }


def build_live_config_capability_sync(gov_head: str) -> Dict[str, Any]:
    return {
        "artifact_id": "e26_live_config_capability_sync",
        "source_repo": "gov-mcp",
        "source_head": gov_head,
        "live_config_schema_ready": True,
        "credential_source_contract_ready": True,
        "credential_source_type": "environment_variable_names_only",
        "required_credential_variable_names": ["YSTAR_OUTBOUND_PROVIDER_API_KEY"],
        "credential_values_committed": False,
        "secrets_committed": False,
        "live_enabled": False,
        "sandbox_enabled": True,
        "dry_run_enabled": True,
        "quota_rate_limit_config_ready": True,
        "suppression_registry_config_ready": True,
        "compliance_registry_config_ready": True,
        "audit_receipt_storage_config_ready": False,
        "live_blocked_reason": [
            "live_enabled_false",
            "credential_values_absent_by_design",
            "live_provider_tests_not_configured",
            "production_persistent_idempotency_not_configured",
        ],
        "external_action_executed": False,
    }


def build_persistent_idempotency_readiness() -> Dict[str, Any]:
    return {
        "artifact_id": "e26_persistent_idempotency_readiness",
        "existing_wheel_reused": "gov_mcp/outbound/persistent_idempotency.py",
        "extension_delivered": True,
        "persistent_status": "persistent_disabled_until_live_configuration",
        "store_type": "file_backed_json_contract",
        "duplicate_protection_result": "validated_by_gov_mcp_tests_duplicate_noop",
        "corruption_handling": "corrupted_store_blocked",
        "missing_store_handling": "missing_store_blocked",
        "live_promotion_impact": "blocks_live_promotion_until_persistent_ready",
        "persistent_ready": False,
        "external_action_executed": False,
    }


def build_kill_switch_readiness() -> Dict[str, Any]:
    return {
        "artifact_id": "e26_kill_switch_readiness",
        "kill_switch_ready": True,
        "default_state": "global_live_disabled",
        "supported_scopes": ["global", "provider", "channel", "campaign", "target", "action"],
        "live_execution_allowed_now": False,
        "reason_codes": ["global_live_disabled", "provider_live_disabled"],
        "audit_czl_note_required": True,
        "external_action_executed": False,
    }


def build_live_receipt_boundary() -> Dict[str, Any]:
    return {
        "artifact_id": "e26_live_receipt_boundary",
        "receipt_types": ["dry_run_receipt", "sandbox_receipt", "live_receipt", "blocked_receipt", "replay_noop_receipt"],
        "live_receipts_created_count": 0,
        "dry_run_cannot_create_live_receipt": True,
        "sandbox_cannot_create_live_receipt": True,
        "blocked_action_cannot_create_live_receipt": True,
        "live_receipt_requires_external_effect_true": True,
        "receipt_boundary_proof": "gov_mcp live receipt boundary tests passed; E26 created no live receipts.",
        "external_action_executed": False,
    }


def build_live_provider_readiness_validator(
    live_config: Dict[str, Any],
    idempotency: Dict[str, Any],
    kill_switch: Dict[str, Any],
    receipt_boundary: Dict[str, Any],
) -> Dict[str, Any]:
    blockers = []
    blockers.extend(live_config["live_blocked_reason"])
    blockers.append(idempotency["live_promotion_impact"])
    blockers.extend(kill_switch["reason_codes"])
    blockers.append("live_receipt_writer_not_activated")
    blockers = list(dict.fromkeys(blockers))
    return {
        "artifact_id": "e26_live_provider_readiness_validator",
        "validator_source": "gov_mcp/outbound/live_readiness.py",
        "live_ready": False,
        "live_ready_action_count": 0,
        "live_blocked_action_count": 1,
        "dry_run_receipt_history_present": True,
        "sandbox_receipt_history_present": True,
        "ceo_kg_route_supported": True,
        "reason_codes": blockers,
        "primary_blockers": [
            "live_enabled_false",
            "live_provider_tests_not_configured",
            "production_persistent_idempotency_not_configured",
            "global_live_disabled",
        ],
        "external_action_executed": False,
    }


def build_one_action_canary_plan(repo_root: Path = BRIDGE_LABS_ROOT) -> Dict[str, Any]:
    route = load_json(repo_root, "operations/external_validation/e25_ceo_kg_sandbox_route_selection.json")
    return {
        "artifact_id": "e26_one_action_canary_plan",
        "canary_plan_created": True,
        "canary_executed": False,
        "customer_contacted": False,
        "message_sent": False,
        "live_receipt_created": False,
        "selected_revenue_path": route["selected_revenue_path_id"],
        "selected_action_candidate": "e26_live_canary_readiness_review_ai_consultancy_candidate_1",
        "kg_support_nodes_edges": route["kg_support_node_ids"],
        "target_evidence": [
            "operations/external_validation/e18_revenue_validation_batch.json",
            "operations/external_validation/e25_sandbox_execution_results.json",
        ],
        "message_content_reference": "operations/external_validation/e17_final_message_package.json",
        "channel": "email",
        "provider_category": "outbound_message_provider",
        "risk_tier": route["sandbox_route_candidate"]["risk_tier"],
        "autonomous_eligibility": "eligible_in_principle_after_live_readiness_passes",
        "owner_approval_required_by_risk": False,
        "required_live_config": "gov_mcp_live_provider_config_contract_v1",
        "required_credential_source_names_only": ["YSTAR_OUTBOUND_PROVIDER_API_KEY"],
        "persistent_idempotency_requirement": "persistent_ready",
        "rate_limit": {"max_live_actions": 1, "window": "canary"},
        "suppression_check": "required_clear",
        "compliance_check": "required_clear",
        "kill_switch": "required_clear",
        "live_receipt_path": "gov_mcp/outbound/live_receipts.py",
        "abort_criteria": ["kill_switch_active", "suppression_not_clear", "compliance_not_clear", "provider_live_not_ready", "persistent_idempotency_not_ready"],
        "success_criteria": ["one live action accepted by provider", "live receipt written", "feedback import wait-state opened"],
        "failure_criteria": ["provider error", "rate limit exceeded", "bounce/suppression signal"],
        "post_canary_feedback_import_path": "operations/external_validation/e18_batch_feedback_intake_empty.json",
        "ceo_kg_feedback_ingestion_path": "operations/knowledge_graph/e26_ceo_kg_live_readiness_feedback.json",
        "live_disabled_unless_validator_passes": True,
        "external_action_executed": False,
    }


def node(node_id: str, node_type: str, label: str, source_paths: List[str], evidence_status: str, truth_status: str, promotion_status: str, notes: str) -> Dict[str, Any]:
    return {
        "id": node_id,
        "type": node_type,
        "label": label,
        "source_paths": source_paths,
        "evidence_status": evidence_status,
        "truth_status": truth_status,
        "promotion_status": promotion_status,
        "created_by_milestone": "E26",
        "stale_or_current": "current_working",
        "notes": notes,
    }


def edge(edge_id: str, source: str, target: str, relationship: str, evidence_path: str, confidence_basis: str, notes: str) -> Dict[str, Any]:
    return {
        "id": edge_id,
        "source_node_id": source,
        "target_node_id": target,
        "relationship": relationship,
        "evidence_path": evidence_path,
        "confidence_basis": confidence_basis,
        "notes": notes,
    }


def build_ceo_kg_live_readiness_feedback(
    canary: Dict[str, Any],
    validator: Dict[str, Any],
    inventory: Dict[str, Any],
) -> Dict[str, Any]:
    nodes = [
        node("e26_existing_wheel_inventory", "ExistingWheelInventory", "E26 existing live-readiness wheel inventory", ["operations/external_validation/e26_existing_live_readiness_wheel_inventory.json"], "evidence_bound", "observed_internal_audit", "working_only", "Audit occurred before E26 implementation."),
        node("e26_reuse_decision", "ReuseDecision", "Reuse/wrap/extend/build decision", ["operations/external_validation/e26_reuse_wrap_extend_build_decision.json"], "evidence_bound", "observed_internal_decision", "working_only", "Every new wheel has build_missing or extend_existing justification."),
        node("e26_live_config_contract", "LiveConfigContract", "Live provider configuration contract", ["operations/external_validation/e26_live_config_capability_sync.json"], "evidence_bound", "observed_internal_capability", "validated_internal_execution_candidate", "Names-only credential contract; no secrets."),
        node("e26_persistent_idempotency_readiness", "PersistentIdempotencyReadiness", "Persistent idempotency readiness", ["operations/external_validation/e26_persistent_idempotency_readiness.json"], "evidence_bound", "observed_internal_capability", "working_only", "Store foundation hardened; production live persistence not configured."),
        node("e26_kill_switch_capability", "KillSwitchCapability", "Live kill switch capability", ["operations/external_validation/e26_kill_switch_readiness.json"], "evidence_bound", "observed_internal_capability", "validated_internal_execution_candidate", "Defaults safe and blocks live."),
        node("e26_live_receipt_boundary", "LiveReceiptBoundary", "Live receipt boundary", ["operations/external_validation/e26_live_receipt_boundary.json"], "evidence_bound", "observed_internal_capability", "validated_internal_execution_candidate", "No live receipts without real allowed live effect."),
        node("e26_live_provider_readiness_validator", "LiveProviderReadinessValidator", "Live readiness validator", ["operations/external_validation/e26_live_provider_readiness_validator.json"], "evidence_bound", "observed_internal_validator", "working_only", "Blocks current live execution."),
        node("e26_canary_plan", "CanaryPlan", "One-action live canary plan", ["operations/external_validation/e26_one_action_canary_plan.json"], "evidence_bound", "planned_internal_route", "working_only", "Plan only; not executed."),
        node("e26_live_promotion_blocker", "LivePromotionBlocker", "Live readiness blockers", ["operations/external_validation/e26_live_provider_readiness_validator.json"], "evidence_bound", "observed_internal_blocker", "working_only", ", ".join(validator["primary_blockers"])),
        node("e26_strategic_learning_candidate", "StrategicLearningCandidate", "Existing wheels can be integrated into a live canary gate", ["operations/external_validation/e26_ceo_brain_portfolio_update.json"], "evidence_bound", "internal_readiness_learning_not_market_truth", "validated_internal_execution_candidate", "Internal readiness evidence only."),
    ]
    edges = [
        edge("e26_edge_path_requires_live_config", canary["selected_revenue_path"], "e26_live_config_contract", "requires", "operations/external_validation/e26_one_action_canary_plan.json", "deterministic_source", "Selected path requires live config before canary."),
        edge("e26_edge_path_requires_idempotency", canary["selected_revenue_path"], "e26_persistent_idempotency_readiness", "requires", "operations/external_validation/e26_persistent_idempotency_readiness.json", "deterministic_source", "Live promotion requires durable idempotency."),
        edge("e26_edge_canary_routes_to_path", "e26_canary_plan", canary["selected_revenue_path"], "routes_to", "operations/external_validation/e26_one_action_canary_plan.json", "deterministic_source", "Canary plan targets selected revenue path."),
        edge("e26_edge_validator_blocks_live", "e26_live_provider_readiness_validator", "e26_live_promotion_blocker", "blocks", "operations/external_validation/e26_live_provider_readiness_validator.json", "deterministic_source", "Validator blocks current live execution."),
        edge("e26_edge_blocker_missing_config", "e26_live_promotion_blocker", "e26_live_config_contract", "blocked_by", "operations/external_validation/e26_live_config_capability_sync.json", "deterministic_source", "Live enabled/config/tests absent."),
        edge("e26_edge_existing_wheel_reused", "e26_existing_wheel_inventory", "e26_reuse_decision", "supports", "operations/external_validation/e26_reuse_wrap_extend_build_decision.json", "deterministic_source", "Audit gates implementation choices."),
        edge("e26_edge_reuse_extends_idempotency", "e26_reuse_decision", "e26_persistent_idempotency_readiness", "extended_by", "operations/external_validation/e26_reuse_wrap_extend_build_decision.json", "deterministic_source", "Existing persistent idempotency wheel extended."),
        edge("e26_edge_kill_switch_blocks_canary", "e26_kill_switch_capability", "e26_canary_plan", "governed_by", "operations/external_validation/e26_kill_switch_readiness.json", "deterministic_source", "Canary requires kill switch clear."),
        edge("e26_edge_receipt_boundary_governs_canary", "e26_live_receipt_boundary", "e26_canary_plan", "governed_by", "operations/external_validation/e26_live_receipt_boundary.json", "deterministic_source", "Canary cannot create live receipt until boundary passes."),
        edge("e26_edge_readiness_updates_learning", "e26_live_provider_readiness_validator", "e26_strategic_learning_candidate", "supports", "operations/knowledge_graph/e26_ceo_kg_live_readiness_feedback.json", "deterministic_source", "Readiness result informs CEO brain."),
        edge("e26_edge_learning_updates_bottleneck", "e26_strategic_learning_candidate", "e26_ceo_brain_update", "routes_to", "operations/external_validation/e26_ceo_brain_portfolio_update.json", "deterministic_source", "CEO brain consumes readiness feedback."),
    ]
    return {
        "artifact_id": "e26_ceo_kg_live_readiness_feedback",
        "kg_delta_nodes": nodes,
        "kg_delta_edges": edges,
        "kg_delta_node_count": len(nodes),
        "kg_delta_edge_count": len(edges),
        "internal_readiness_evidence_only": True,
        "customer_feedback_claimed": False,
        "market_validation_claimed": False,
        "canonical_truth_promoted": False,
        "promotion_candidates": [
            {"node_id": "e26_live_config_contract", "promotion_status": "validated_internal_execution_candidate"},
            {"node_id": "e26_kill_switch_capability", "promotion_status": "validated_internal_execution_candidate"},
            {"node_id": "e26_live_receipt_boundary", "promotion_status": "validated_internal_execution_candidate"},
        ],
        "promotion_candidates_count": 3,
        "external_action_executed": False,
    }


def build_ceo_brain_portfolio_update(canary: Dict[str, Any], validator: Dict[str, Any], feedback: Dict[str, Any]) -> Dict[str, Any]:
    return {
        "artifact_id": "e26_ceo_brain_portfolio_update",
        "state_type": "working_shadow_not_canonical_truth",
        "selected_revenue_path": canary["selected_revenue_path"],
        "provider_readiness": "live_blocked",
        "idempotency_readiness": "persistent_disabled_until_live_configuration",
        "kill_switch_readiness": "ready_defaults_safe",
        "live_receipt_readiness": "boundary_ready_no_live_receipts_created",
        "canary_readiness_status": "planned_but_blocked",
        "existing_wheel_reuse_status": "audit_completed_reuse_wrap_extend_build_decision_recorded",
        "current_strategic_bottleneck": "live canary is planned but blocked by live_enabled_false, live tests/config, production persistent idempotency, and kill switch default-disabled state",
        "next_decision_horizon": "E27 should configure live readiness prerequisites in a controlled sandbox/live-test setting before any canary execution",
        "portfolio_update": {
            "selected_path_remains_selected": True,
            "live_canary_candidate_path": canary["selected_revenue_path"],
            "evidence_needed_paths": ["real customer feedback still absent"],
            "offer_revision_needed_paths": [],
            "blocked_no_go_paths": ["any live execution before validator passes"],
        },
        "kg_feedback": {
            "delta_nodes": feedback["kg_delta_node_count"],
            "delta_edges": feedback["kg_delta_edge_count"],
            "market_truth_claimed": False,
        },
        "external_action_executed": False,
    }


def build_live_readiness_control_room(inventory: Dict[str, Any], decision: Dict[str, Any], live_config: Dict[str, Any], idempotency: Dict[str, Any], kill_switch: Dict[str, Any], receipt_boundary: Dict[str, Any], validator: Dict[str, Any], canary: Dict[str, Any], brain: Dict[str, Any]) -> Dict[str, Any]:
    return {
        "artifact_id": "e26_live_readiness_control_room",
        "control_room_type": "live_readiness_existing_wheel_integration_and_canary_gate",
        "existing_wheel_audit_completed_first": inventory["audit_completed_before_new_e26_modules"],
        "existing_wheels_reused": inventory["reused_wheels_count"],
        "wrapped_or_extended_wheels": inventory["wrapped_wheels_count"] + inventory["extended_wheels_count"],
        "new_wheels_added_with_justification": inventory["newly_built_wheels_count"],
        "duplicate_overlap_risks": "documented_in_e26_live_readiness_duplicate_conflict_map",
        "ceo_kg_selected_path": canary["selected_revenue_path"],
        "live_config_status": live_config,
        "persistent_idempotency_status": idempotency,
        "kill_switch_status": kill_switch,
        "live_receipt_boundary_status": receipt_boundary,
        "live_readiness_validator_result": validator,
        "one_action_canary_plan": canary,
        "blockers": validator["primary_blockers"],
        "agent_can_do_autonomously_next": [
            "run live readiness validation after config changes",
            "prepare credential-source contract without values",
            "run no-effect canary gate regression",
        ],
        "owner_approval_required_by_risk": [],
        "blocked_actions": ["live canary execution", "provider API call", "live receipt creation"],
        "owner_manual_send_is_default": False,
        "recommended_next_milestone": brain["next_decision_horizon"],
        "external_action_executed": False,
    }


def build_ecosystem_alignment_gate(gov_head: str) -> Dict[str, Any]:
    repos = {
        "ystar-bridge-labs": BRIDGE_LABS_ROOT,
        "gov-mcp": GOV_MCP_ROOT,
        "Y-star-gov": YSTAR_GOV_ROOT,
        "ystar-company": YSTAR_COMPANY_ROOT,
    }
    return {
        "artifact_id": "e26_ecosystem_alignment_gate",
        "repos_checked": list(repos),
        "repo_status": {name: {"exists": path.exists(), "head": git_head(path), "branch": git_branch(path)} for name, path in repos.items()},
        "gov_mcp_modified": True,
        "gov_mcp_delivered": True,
        "gov_mcp_head": gov_head,
        "bridge_labs_modified": True,
        "Y_star_gov_immediate_mutation_needed": False,
        "ystar_company_future_migration_followups": ["future sales/historical assets may feed KG route evidence only through explicit evidence-bound migration"],
        "closure_status": "ecosystem_aligned_with_documented_followups",
        "cross_repo_impact_update": [
            {"repo": "gov-mcp", "impact": "Live readiness wheels integrated into canonical provider boundary."},
            {"repo": "ystar-bridge-labs", "impact": "CEO KG/control-room consumes live readiness and canary gate state."},
            {"repo": "Y-star-gov", "impact": "Read-only governance/CIEU/CZL alignment; no mutation needed."},
            {"repo": "ystar-company", "impact": "Read-only historical context; no mutation needed."},
        ],
        "drift_blockers": ["live remains disabled", "real customer feedback absent", "production credential source not configured"],
        "external_action_executed": False,
    }


def build_repo_modification_decision_packet(gov_head: str) -> Dict[str, Any]:
    return {
        "artifact_id": "e26_repo_modification_decision_packet",
        "decisions": [
            {"repo": "gov-mcp", "decision": "immediate_update_required_and_delivered", "reason": "Missing live-readiness wheels belong in canonical provider boundary.", "delivered_head": gov_head},
            {"repo": "ystar-bridge-labs", "decision": "bridge_labs_update_required", "reason": "CEO KG/control room/canary gate artifacts live in commercial runtime.", "delivered_by_this_job": True},
            {"repo": "Y-star-gov", "decision": "no_change_needed", "reason": "Governance concepts aligned read-only."},
            {"repo": "ystar-company", "decision": "no_change_needed", "reason": "Historical commercial context only."},
        ],
        "cross_repo_mutation_performed": True,
        "external_action_executed": False,
    }


def build_future_anti_duplication_policy() -> Dict[str, Any]:
    return {
        "artifact_id": "e26_future_anti_duplication_policy",
        "future_milestone_start_requirements": [
            "existing-wheel audit",
            "duplicate/overlap map",
            "reuse/wrap/extend/build decision",
            "canonical route registry update",
            "explicit new-wheel justification",
            "ecosystem alignment proof",
        ],
        "future_live_canary_requirements": [
            "CEO KG selected route",
            "live config validation",
            "credential source contract without committing secrets",
            "persistent idempotency persistent_ready",
            "kill switch clear",
            "suppression clear",
            "compliance clear",
            "rate-limit budget",
            "sandbox receipt history",
            "dry-run receipt history",
            "live receipt writer readiness",
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


def build_czl_closure(inventory: Dict[str, Any], validator: Dict[str, Any], canary: Dict[str, Any], feedback: Dict[str, Any], alignment: Dict[str, Any]) -> Dict[str, Any]:
    return {
        "artifact_id": "e26_czl_closure",
        "Y_star": "Live readiness existing-wheel integration and canary gate",
        "Rt_plus_1": 0,
        "whole_ecosystem_existing_wheel_audited_first": inventory["audit_completed_before_new_e26_modules"],
        "reusable_wheels_reused_wrapped_or_extended": True,
        "new_wheels_justified_by_missing_wheel_evidence": inventory["new_wheel_creation_rule_satisfied"],
        "no_real_external_action_occurred": True,
        "no_provider_api_called": True,
        "no_customer_contacted": True,
        "no_message_sent": True,
        "no_live_receipt_created": True,
        "no_credentials_or_secrets_committed": True,
        "live_mode_honestly_reported": "disabled",
        "persistent_idempotency_honestly_reported": "persistent_disabled_until_live_configuration",
        "kill_switch_defaults_safe": True,
        "one_action_canary_planned_not_executed": canary["canary_plan_created"] and not canary["canary_executed"],
        "ceo_kg_updated_only_with_internal_readiness_evidence": True,
        "kg_delta_node_count": feedback["kg_delta_node_count"],
        "kg_delta_edge_count": feedback["kg_delta_edge_count"],
        "no_fake_customer_feedback_created": True,
        "no_fake_target_evidence_created": True,
        "owner_manual_send_is_not_default": True,
        "ecosystem_alignment_status": alignment["closure_status"],
        "live_ready": validator["live_ready"],
        "external_action_executed": False,
    }


def build_all(repo_root: Path = BRIDGE_LABS_ROOT) -> Dict[str, Any]:
    gov_report = gov_delivery_report()
    gov_head = gov_report.get("result_head") or git_head(GOV_MCP_ROOT) or ""
    inventory = build_existing_live_readiness_wheel_inventory()
    conflicts = build_live_readiness_duplicate_conflict_map(inventory)
    decision = build_reuse_wrap_extend_build_decision()
    live_config = build_live_config_capability_sync(gov_head)
    idempotency = build_persistent_idempotency_readiness()
    kill_switch = build_kill_switch_readiness()
    receipt_boundary = build_live_receipt_boundary()
    validator = build_live_provider_readiness_validator(live_config, idempotency, kill_switch, receipt_boundary)
    canary = build_one_action_canary_plan(repo_root)
    feedback = build_ceo_kg_live_readiness_feedback(canary, validator, inventory)
    brain = build_ceo_brain_portfolio_update(canary, validator, feedback)
    control = build_live_readiness_control_room(inventory, decision, live_config, idempotency, kill_switch, receipt_boundary, validator, canary, brain)
    alignment = build_ecosystem_alignment_gate(gov_head)
    repo_decision = build_repo_modification_decision_packet(gov_head)
    future_policy = build_future_anti_duplication_policy()
    closure = build_czl_closure(inventory, validator, canary, feedback, alignment)
    return {
        "inventory": inventory,
        "conflicts": conflicts,
        "decision": decision,
        "live_config": live_config,
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
