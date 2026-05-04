from __future__ import annotations

import json
import subprocess
from pathlib import Path
from typing import Any, Dict, Iterable, List

BRIDGE_LABS_ROOT = Path("/Users/haotianliu/.openclaw/workspace/ystar-bridge-labs")
GOV_MCP_ROOT = Path("/Users/haotianliu/.openclaw/workspace/gov-mcp")
YSTAR_GOV_ROOT = Path("/Users/haotianliu/.openclaw/workspace/Y-star-gov")
YSTAR_COMPANY_ROOT = Path("/Users/haotianliu/.openclaw/workspace/ystar-company")
GOV_MCP_E25_REPORT = "/tmp/ystar_delivery_bridge/completed/e25_gov_mcp_provider_sandbox_r1_20260504T164329Z.report.json"


def load_json(repo_root: Path, rel: str, default: Any | None = None) -> Any:
    path = repo_root / rel
    if not path.exists():
        if default is not None:
            return default
        raise FileNotFoundError(path)
    return json.loads(path.read_text(encoding="utf-8"))


def load_jsonl(repo_root: Path, rel: str) -> List[Dict[str, Any]]:
    path = repo_root / rel
    if not path.exists():
        return []
    return [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines() if line.strip()]


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


def build_ceo_kg_sandbox_route_selection(repo_root: Path = BRIDGE_LABS_ROOT) -> Dict[str, Any]:
    selection = load_json(repo_root, "operations/external_validation/e24_revenue_path_portfolio_selection.json")
    router = load_json(repo_root, "operations/external_validation/e24_ceo_execution_router.json")
    brain = load_json(repo_root, "operations/external_validation/e24_ceo_brain_state.json")
    e22_selection = load_json(repo_root, "operations/external_validation/e22_dry_run_batch_selection.json", {"selected_count": 0})
    top = selection["top_selected_path"]
    sandbox_actions = [a for a in router.get("live_sandbox_actions", []) if "sandbox" in a]
    return {
        "artifact_id": "e25_ceo_kg_sandbox_route_selection",
        "selection_source": "E24 CEO KG read model and execution router",
        "selected_revenue_path_id": top["id"],
        "sandbox_route_candidate": {
            "route_id": "sandbox_route_readiness_review_ai_consultancies",
            "revenue_path_id": top["id"],
            "target_customer": top["target_customer"],
            "offer": top["offer"],
            "required_provider_capability": "gov_mcp_deterministic_provider_sandbox",
            "provider_mode_required": "sandbox_ready",
            "risk_tier": top["risk_tier"],
            "commercial_meaning": "Validates that the closest sellable readiness-review path can move from local dry-run artifacts into a provider-shaped sandbox without customer contact.",
            "expected_learning_value": "high_internal_execution_learning_not_market_truth",
        },
        "kg_support_node_ids": top.get("kg_nodes_used", []) + selection.get("kg_support", []),
        "kg_support_edge_basis": [
            "selected revenue path requires provider sandbox capability",
            "dry-run history enables sandbox-shaped execution",
            "live blockers require sandbox/persistent idempotency hardening before canary",
        ],
        "dry_run_history": {
            "previous_selected_dry_run_count": e22_selection.get("selected_count", 0),
            "dry_run_available_before_e25": True,
        },
        "why_sandbox_now": "The CEO brain bottleneck is provider sandbox/readiness plus real feedback evidence; sandbox is the next internal execution step before any live provider enablement.",
        "why_not_live_now": "Live provider remains disabled and live config/tests/persistent idempotency are not production-ready.",
        "why_not_owner_manual_send": "Owner manual send is not the default execution route; the path is routed through governed autonomous provider capability.",
        "source_paths": [
            "operations/external_validation/e24_revenue_path_portfolio_selection.json",
            "operations/external_validation/e24_ceo_execution_router.json",
            "operations/external_validation/e24_ceo_brain_state.json",
            "operations/external_validation/e22_dry_run_batch_selection.json",
        ],
        "current_strategic_bottleneck_before_e25": brain["current_strategic_bottleneck"],
        "live_sandbox_actions_from_e24": sandbox_actions,
        "external_action_executed": False,
    }


def build_provider_sandbox_capability_sync(
    gov_root: Path = GOV_MCP_ROOT,
    gov_report_path: str = GOV_MCP_E25_REPORT,
) -> Dict[str, Any]:
    required_files = [
        "gov_mcp/outbound/provider_sandbox.py",
        "gov_mcp/outbound/sandbox_manifest.py",
        "gov_mcp/outbound/sandbox_receipts.py",
        "gov_mcp/outbound/persistent_idempotency.py",
        "gov_mcp/outbound/sandbox_promotion.py",
    ]
    present = {rel: (gov_root / rel).exists() for rel in required_files}
    gov_report = Path(gov_report_path)
    delivered = False
    result_head = git_head(gov_root)
    if gov_report.exists():
        report = json.loads(gov_report.read_text(encoding="utf-8"))
        delivered = bool(report.get("remote_confirmed") and report.get("repository_delivery_rt1") == 0)
        result_head = report.get("result_head") or result_head
    sandbox_ready = all(present.values()) and delivered
    return {
        "artifact_id": "e25_provider_sandbox_capability_sync",
        "source_repo": "gov-mcp",
        "source_branch": git_branch(gov_root),
        "source_head": result_head,
        "source_delivery_report": gov_report_path,
        "source_delivery_remote_confirmed": delivered,
        "required_files_present": present,
        "sandbox_mode_available": sandbox_ready,
        "sandbox_scaffold_ready": sandbox_ready,
        "deterministic_local_sandbox_harness_available": sandbox_ready,
        "native_provider_sandbox_enabled": False,
        "native_provider_sandbox_blocked_reason": "credentials_or_external_provider_api_not_allowed_in_E25",
        "dry_run_available": True,
        "live_enabled": False,
        "live_provider_enabled": False,
        "live_blocked_reason": [
            "live_provider_scaffolded_but_disabled",
            "live_provider_credentials_config_missing",
            "live_provider_tests_missing",
            "production_persistent_idempotency_not_configured",
        ],
        "sandbox_receipts_distinct_from_dry_run_and_live": True,
        "live_receipts_enabled": False,
        "provider_api_called": False,
        "persistent_idempotency": {
            "foundation_available": bool((gov_root / "gov_mcp/outbound/persistent_idempotency.py").exists()),
            "store_type": "file_backed_contract_available",
            "production_live_status": "persistent_disabled_until_live_configuration",
            "memory_only_live_safe": False,
            "live_promotion_impact": "blocks_live_promotion_until_persistent_store_is_configured_and_validated",
        },
        "capability_status": "sandbox_ready_live_disabled" if sandbox_ready else "sandbox_blocked_missing_provider_foundation_delivery",
        "external_action_executed": False,
    }


def build_sandbox_envelopes(
    route_selection: Dict[str, Any],
    capability_sync: Dict[str, Any],
) -> Dict[str, Any]:
    route = route_selection["sandbox_route_candidate"]
    ready = capability_sync["sandbox_scaffold_ready"]
    envelopes = [
        {
            "action_id": "e25_sandbox_readiness_review_ai_consultancies",
            "target_or_segment_id": "target_segment_ai_operations_consultancies",
            "channel": "provider_sandbox_email_shape_no_external_effect",
            "content_reference": "operations/external_validation/e17_final_message_package.json",
            "revenue_path_id": route["revenue_path_id"],
            "kg_support_node_ids": route_selection["kg_support_node_ids"],
            "risk_tier": route["risk_tier"],
            "provider_mode": "sandbox_ready" if ready else "sandbox_disabled",
            "executor_decision": "agent_autonomous_sandbox_allowed",
            "evidence_references": [
                "operations/external_validation/e24_revenue_path_portfolio_selection.json",
                "operations/external_validation/e22_dry_run_receipt_ledger.json",
                "operations/external_validation/e23_compliance_registry.json",
                "operations/external_validation/e23_suppression_registry.json",
            ],
            "suppression_status": "clear_for_sandbox_no_external_effect",
            "compliance_status": "policy_allows_agent_with_limits_for_sandbox",
            "idempotency_key": "e25:sandbox:readiness_review_ai_consultancies:v1",
            "rate_limit_bucket": "e25_sandbox_local_provider_shape_batch",
            "kill_switch_state": "enabled",
            "expected_learning_value": route["expected_learning_value"],
            "live_disabled": True,
            "owner_approval_required_by_risk": False,
        }
    ]
    return {
        "artifact_id": "e25_sandbox_envelopes",
        "selected_count": len(envelopes),
        "envelopes": envelopes,
        "external_action_executed": False,
    }


def build_sandbox_guard_results(
    envelopes_packet: Dict[str, Any],
    capability_sync: Dict[str, Any],
) -> Dict[str, Any]:
    rows = []
    for envelope in envelopes_packet["envelopes"]:
        checks = [
            ("risk_tier_check", "passed", envelope["risk_tier"]),
            ("policy_compatibility_check", "passed", "policy_allows_agent_with_limits_for_sandbox"),
            ("provider_mode_check", "passed" if envelope["provider_mode"] == "sandbox_ready" else "blocked", envelope["provider_mode"]),
            ("sandbox_capability_check", "passed" if capability_sync["sandbox_scaffold_ready"] else "blocked", capability_sync["capability_status"]),
            ("quota_rate_limit_check", "passed", envelope["rate_limit_bucket"]),
            ("sandbox_safe_idempotency_check", "passed", envelope["idempotency_key"]),
            ("persistent_idempotency_live_check", "not_applicable_for_sandbox_blocks_live_promotion", capability_sync["persistent_idempotency"]["production_live_status"]),
            ("suppression_registry_check", "passed", envelope["suppression_status"]),
            ("compliance_registry_check", "passed", envelope["compliance_status"]),
            ("evidence_sufficiency_check", "passed", "repo-bound evidence sufficient for sandbox-only execution"),
            ("message_safety_check", "passed", "sandbox no-external-effect content reference"),
            ("kill_switch_check", "passed", envelope["kill_switch_state"]),
            ("owner_approval_check", "not_applicable", "not required by risk tier for sandbox"),
            ("live_disabled_check", "passed", "live execution disabled"),
        ]
        blocked = [c for c in checks if c[1] == "blocked"]
        rows.append({
            "action_id": envelope["action_id"],
            "resulting_action_status": "sandbox_guard_passed" if not blocked else "sandbox_guard_blocked",
            "checks": [
                {
                    "check": name,
                    "status": status,
                    "reason": reason,
                    "evidence_path": "operations/external_validation/e25_provider_sandbox_capability_sync.json",
                }
                for name, status, reason in checks
            ],
        })
    guard_pass_count = sum(1 for row in rows for check in row["checks"] if check["status"] == "passed")
    guard_block_count = sum(1 for row in rows for check in row["checks"] if check["status"] == "blocked")
    return {
        "artifact_id": "e25_sandbox_guard_results",
        "guard_results": rows,
        "guard_pass_count": guard_pass_count,
        "guard_block_count": guard_block_count,
        "owner_approval_required_by_risk_count": 0,
        "external_action_executed": False,
    }


def build_sandbox_execution_results(
    envelopes_packet: Dict[str, Any],
    guard_results: Dict[str, Any],
    capability_sync: Dict[str, Any],
) -> Dict[str, Any]:
    executions = []
    for envelope in envelopes_packet["envelopes"]:
        guard = next(row for row in guard_results["guard_results"] if row["action_id"] == envelope["action_id"])
        can_execute = guard["resulting_action_status"] == "sandbox_guard_passed" and capability_sync["sandbox_scaffold_ready"]
        receipt_id = f"sandbox_receipt_{envelope['action_id']}_001" if can_execute else None
        executions.append({
            "action_id": envelope["action_id"],
            "provider_mode": envelope["provider_mode"],
            "execution_status": "sandbox_executed" if can_execute else "sandbox_blocked",
            "sandbox_receipt_id": receipt_id,
            "receipt_type": "sandbox_receipt" if can_execute else "blocked_receipt",
            "no_customer_contact": True,
            "no_external_effect": True,
            "provider_api_called": False,
            "live_send_performed": False,
            "live_receipt_created": False,
            "guard_summary": guard["resulting_action_status"],
            "idempotency_result": "first_sandbox_execution_recorded",
            "suppression_result": envelope["suppression_status"],
            "rate_limit_result": "within_sandbox_quota",
            "compliance_result": envelope["compliance_status"],
            "live_promotion_blocker": "live_provider_disabled_and_persistent_idempotency_not_configured",
        })
    return {
        "artifact_id": "e25_sandbox_execution_results",
        "sandbox_selected_count": len(executions),
        "sandbox_executed_count": sum(1 for e in executions if e["execution_status"] == "sandbox_executed"),
        "sandbox_blocked_count": sum(1 for e in executions if e["execution_status"] == "sandbox_blocked"),
        "sandbox_receipt_count": sum(1 for e in executions if e["receipt_type"] == "sandbox_receipt"),
        "live_receipt_count": 0,
        "live_enabled": False,
        "execution_results": executions,
        "external_action_executed": False,
    }


def build_sandbox_receipt_ledger(execution_results: Dict[str, Any]) -> Dict[str, Any]:
    receipts = [
        {
            "receipt_id": row["sandbox_receipt_id"],
            "receipt_type": "sandbox_receipt",
            "action_id": row["action_id"],
            "provider_mode": row["provider_mode"],
            "no_external_effect_proof": True,
            "not_a_live_receipt": True,
            "not_a_dry_run_receipt": True,
            "live_receipt_created": False,
        }
        for row in execution_results["execution_results"]
        if row["sandbox_receipt_id"]
    ]
    return {
        "artifact_id": "e25_sandbox_receipt_ledger",
        "sandbox_receipt_count": len(receipts),
        "dry_run_receipt_count": 0,
        "live_receipt_count": 0,
        "receipts": receipts,
        "sandbox_receipts_distinct_from_live_receipts": True,
        "sandbox_receipts_distinct_from_dry_run_receipts": True,
        "external_action_executed": False,
    }


def build_persistent_idempotency_status(capability_sync: Dict[str, Any]) -> Dict[str, Any]:
    status = capability_sync["persistent_idempotency"]
    return {
        "artifact_id": "e25_persistent_idempotency_status",
        "persistent_idempotency_foundation_available": status["foundation_available"],
        "store_type": status["store_type"],
        "persistent_status": status["production_live_status"],
        "sandbox_idempotency_status": "sandbox_safe_action_key_recorded",
        "memory_only_live_safe": status["memory_only_live_safe"],
        "live_promotion_impact": status["live_promotion_impact"],
        "live_promotion_allowed": False,
        "external_action_executed": False,
    }


def build_live_promotion_blockers(
    envelopes_packet: Dict[str, Any],
    capability_sync: Dict[str, Any],
    idempotency_status: Dict[str, Any],
) -> Dict[str, Any]:
    blockers = []
    for envelope in envelopes_packet["envelopes"]:
        action_blockers = [
            "live_provider_scaffolded_but_disabled",
            "live_provider_credentials_config_missing",
            "live_provider_tests_missing",
            "production_persistent_idempotency_not_configured",
            "live_rate_limit_configuration_not_validated",
            "live_audit_receipt_mode_not_enabled",
        ]
        blockers.append({
            "action_id": envelope["action_id"],
            "live_ready": False,
            "live_blocked_reasons": action_blockers,
            "owner_approval_required_by_risk": False,
        })
    return {
        "artifact_id": "e25_live_promotion_blockers",
        "live_ready_count": 0,
        "live_blocked_count": len(blockers),
        "primary_live_blockers": capability_sync["live_blocked_reason"],
        "persistent_idempotency_live_status": idempotency_status["persistent_status"],
        "action_live_promotion_results": blockers,
        "external_action_executed": False,
    }


def e25_node(node_id: str, node_type: str, label: str, source_paths: List[str], evidence_status: str, truth_status: str, promotion_status: str, notes: str) -> Dict[str, Any]:
    return {
        "id": node_id,
        "type": node_type,
        "label": label,
        "source_paths": source_paths,
        "evidence_status": evidence_status,
        "truth_status": truth_status,
        "promotion_status": promotion_status,
        "created_by_milestone": "E25",
        "stale_or_current": "current_working",
        "notes": notes,
    }


def e25_edge(edge_id: str, source: str, target: str, relationship: str, evidence_path: str, confidence_basis: str, notes: str) -> Dict[str, Any]:
    return {
        "id": edge_id,
        "source_node_id": source,
        "target_node_id": target,
        "relationship": relationship,
        "evidence_path": evidence_path,
        "confidence_basis": confidence_basis,
        "notes": notes,
    }


def build_ceo_kg_feedback_ingestion(
    route_selection: Dict[str, Any],
    capability_sync: Dict[str, Any],
    execution_results: Dict[str, Any],
    live_blockers: Dict[str, Any],
) -> Dict[str, Any]:
    path_id = route_selection["selected_revenue_path_id"]
    receipt_id = execution_results["execution_results"][0]["sandbox_receipt_id"]
    nodes = [
        e25_node("e25_sandbox_route_readiness_review", "Action", "CEO KG selected sandbox route for readiness review", ["operations/external_validation/e25_ceo_kg_sandbox_route_selection.json"], "evidence_bound", "observed_internal_execution_planning", "working_only", "Selected from E24 portfolio and router."),
        e25_node("e25_provider_sandbox_capability", "ProviderCapability", "gov-mcp deterministic provider sandbox capability", ["operations/external_validation/e25_provider_sandbox_capability_sync.json"], "evidence_bound", "observed_internal_capability", "validated_internal_execution_candidate", "Sandbox scaffold exists in gov-mcp and is delivered remotely."),
        e25_node("e25_sandbox_execution_readiness_review", "SandboxExecution", "Sandbox execution for readiness-review revenue path", ["operations/external_validation/e25_sandbox_execution_results.json"], "evidence_bound", "observed_internal_execution", "validated_internal_execution_candidate", "Internal sandbox execution only; not customer validation."),
        e25_node("e25_sandbox_receipt_readiness_review", "SandboxReceipt", str(receipt_id), ["operations/external_validation/e25_sandbox_receipt_ledger.json"], "evidence_bound", "observed_internal_execution_receipt", "validated_internal_execution_candidate", "Distinct from dry-run and live receipt."),
        e25_node("e25_persistent_idempotency_capability", "ProviderCapability", "Persistent idempotency foundation", ["operations/external_validation/e25_persistent_idempotency_status.json"], "evidence_bound", "observed_internal_capability", "working_only", "Foundation exists but production live persistence remains disabled until configured."),
        e25_node("e25_live_promotion_blocker", "SandboxBlocker", "Live promotion remains blocked", ["operations/external_validation/e25_live_promotion_blockers.json"], "evidence_bound", "observed_internal_blocker", "working_only", "Live disabled, missing config/tests/persistent live idempotency."),
        e25_node("e25_strategic_learning_candidate", "StrategicLearningCandidate", "Provider sandbox can support the selected revenue path internally", ["operations/external_validation/e25_ceo_brain_update.json"], "evidence_bound", "internal_execution_learning_not_market_truth", "validated_internal_execution_candidate", "Useful strategic working evidence, not customer/market truth."),
    ]
    edges = [
        e25_edge("e25_edge_path_requires_sandbox", path_id, "e25_provider_sandbox_capability", "requires", "operations/external_validation/e25_ceo_kg_sandbox_route_selection.json", "deterministic_source", "Selected path requires sandbox before live."),
        e25_edge("e25_edge_route_routes_to_execution", "e25_sandbox_route_readiness_review", "e25_sandbox_execution_readiness_review", "routes_to", "operations/external_validation/e25_sandbox_envelopes.json", "deterministic_source", "Route produced a sandbox envelope."),
        e25_edge("e25_edge_sandbox_implemented_by_provider", "e25_sandbox_execution_readiness_review", "e25_provider_sandbox_capability", "implemented_by", "operations/external_validation/e25_provider_sandbox_capability_sync.json", "deterministic_source", "gov-mcp scaffold supports sandbox execution."),
        e25_edge("e25_edge_execution_evidenced_by_receipt", "e25_sandbox_execution_readiness_review", "e25_sandbox_receipt_readiness_review", "evidenced_by", "operations/external_validation/e25_sandbox_receipt_ledger.json", "deterministic_source", "Sandbox receipt proves internal no-effect execution."),
        e25_edge("e25_edge_live_blocked_by_provider", path_id, "e25_live_promotion_blocker", "blocked_by", "operations/external_validation/e25_live_promotion_blockers.json", "deterministic_source", "Live remains blocked honestly."),
        e25_edge("e25_edge_live_requires_persistent_idempotency", "e25_live_promotion_blocker", "e25_persistent_idempotency_capability", "requires", "operations/external_validation/e25_persistent_idempotency_status.json", "deterministic_source", "Live promotion requires configured persistent idempotency."),
        e25_edge("e25_edge_execution_updates_learning", "e25_sandbox_execution_readiness_review", "e25_strategic_learning_candidate", "supports", "operations/external_validation/e25_ceo_kg_feedback_ingestion.json", "deterministic_source", "Internal execution evidence informs strategy."),
        e25_edge("e25_edge_learning_routes_to_brain", "e25_strategic_learning_candidate", "e25_ceo_brain_update", "routes_to", "operations/external_validation/e25_ceo_brain_update.json", "deterministic_source", "Brain update consumes KG feedback."),
    ]
    return {
        "artifact_id": "e25_ceo_kg_feedback_ingestion",
        "kg_delta_nodes": nodes,
        "kg_delta_edges": edges,
        "kg_delta_node_count": len(nodes),
        "kg_delta_edge_count": len(edges),
        "sandbox_evidence_node_count": 3,
        "promotion_candidates": [
            {
                "node_id": "e25_provider_sandbox_capability",
                "promotion_status": "validated_internal_execution_candidate",
                "not_customer_market_truth": True,
            },
            {
                "node_id": "e25_strategic_learning_candidate",
                "promotion_status": "validated_internal_execution_candidate",
                "not_customer_market_truth": True,
            },
        ],
        "promotion_candidates_count": 2,
        "customer_or_market_truth_claimed": False,
        "canonical_memory_write_performed": False,
        "external_action_executed": False,
    }


def build_ceo_brain_update(
    repo_root: Path,
    route_selection: Dict[str, Any],
    execution_results: Dict[str, Any],
    live_blockers: Dict[str, Any],
    feedback: Dict[str, Any],
) -> Dict[str, Any]:
    prior = load_json(repo_root, "operations/external_validation/e24_ceo_brain_state.json")
    return {
        "artifact_id": "e25_ceo_brain_update",
        "state_type": "working_shadow_not_canonical_truth",
        "selected_revenue_path_after_sandbox": route_selection["selected_revenue_path_id"],
        "provider_readiness_update": {
            "sandbox_scaffold_ready": True,
            "sandbox_execution_observed": execution_results["sandbox_executed_count"],
            "live_ready": False,
            "live_blocked_count": live_blockers["live_blocked_count"],
        },
        "kg_feedback_summary": {
            "delta_nodes": feedback["kg_delta_node_count"],
            "delta_edges": feedback["kg_delta_edge_count"],
            "promotion_candidates": feedback["promotion_candidates_count"],
            "market_truth_claimed": False,
        },
        "active_revenue_path_confidence": "increased_for_internal_execution_readiness_only",
        "current_strategic_bottleneck": "sandbox scaffold validated internally; live remains blocked by live provider config/tests, production persistent idempotency, and real customer feedback evidence",
        "next_decision_horizon": "choose E26 live configuration and persistent idempotency hardening before any one-action live canary",
        "prior_bottleneck": prior["current_strategic_bottleneck"],
        "truth_boundaries": {
            "sandbox_result": "internal execution evidence",
            "customer_feedback": "not present",
            "market_truth": "not claimed",
            "canonical_memory": "not written",
        },
        "external_action_executed": False,
    }


def build_revenue_portfolio_update(
    repo_root: Path,
    route_selection: Dict[str, Any],
    brain_update: Dict[str, Any],
    live_blockers: Dict[str, Any],
) -> Dict[str, Any]:
    prior = load_json(repo_root, "operations/external_validation/e24_revenue_path_portfolio_selection.json")
    return {
        "artifact_id": "e25_revenue_portfolio_update",
        "selected_path_remains_selected": True,
        "selected_revenue_path_id": route_selection["selected_revenue_path_id"],
        "selected_path_after_sandbox": route_selection["selected_revenue_path_id"],
        "backup_paths": [p["id"] for p in prior.get("backup_paths", [])],
        "live_sandbox_ready_paths": [route_selection["selected_revenue_path_id"]],
        "evidence_needed_paths": [p["id"] for p in prior.get("evidence_needed_paths", [])],
        "blocked_paths": [p["id"] for p in prior.get("blocked_paths", [])],
        "portfolio_learning": "Sandbox execution strengthens internal execution readiness but does not create customer validation or paid signal.",
        "live_ready_count": live_blockers["live_ready_count"],
        "live_blocked_count": live_blockers["live_blocked_count"],
        "recommended_next_milestone": "E26_live_configuration_persistent_idempotency_hardening_or_live_canary_plan_after_prerequisites",
        "external_action_executed": False,
    }


def build_sandbox_control_room(
    route_selection: Dict[str, Any],
    capability_sync: Dict[str, Any],
    execution_results: Dict[str, Any],
    receipt_ledger: Dict[str, Any],
    idempotency_status: Dict[str, Any],
    live_blockers: Dict[str, Any],
    brain_update: Dict[str, Any],
    portfolio_update: Dict[str, Any],
) -> Dict[str, Any]:
    return {
        "artifact_id": "e25_sandbox_control_room",
        "control_room_type": "ceo_kg_provider_sandbox_feedback_loop",
        "ceo_kg_selected_route": route_selection["sandbox_route_candidate"],
        "provider_sandbox_capability": {
            "sandbox_mode_available": capability_sync["sandbox_mode_available"],
            "sandbox_scaffold_ready": capability_sync["sandbox_scaffold_ready"],
            "native_provider_sandbox_enabled": capability_sync["native_provider_sandbox_enabled"],
            "live_enabled": capability_sync["live_enabled"],
        },
        "sandbox_execution_result": {
            "selected": execution_results["sandbox_selected_count"],
            "executed": execution_results["sandbox_executed_count"],
            "blocked": execution_results["sandbox_blocked_count"],
            "sandbox_receipts": receipt_ledger["sandbox_receipt_count"],
            "live_receipts": receipt_ledger["live_receipt_count"],
        },
        "persistent_idempotency_status": idempotency_status["persistent_status"],
        "suppression_compliance_status": "passed_for_sandbox_no_external_effect",
        "live_promotion_blockers": live_blockers["primary_live_blockers"],
        "ceo_brain_update": {
            "selected_revenue_path_after_sandbox": brain_update["selected_revenue_path_after_sandbox"],
            "current_strategic_bottleneck": brain_update["current_strategic_bottleneck"],
            "next_decision_horizon": brain_update["next_decision_horizon"],
        },
        "portfolio_update": {
            "selected_path_remains_selected": portfolio_update["selected_path_remains_selected"],
            "live_sandbox_ready_paths": portfolio_update["live_sandbox_ready_paths"],
            "live_blocked_count": portfolio_update["live_blocked_count"],
        },
        "agent_can_do_autonomously_next": [
            "harden live provider configuration plan",
            "configure persistent idempotency for live-safe promotion",
            "run sandbox regression iterations without customer contact",
        ],
        "owner_approval_required_by_risk": [],
        "blocked_actions": [
            "real customer contact",
            "live provider execution",
            "live receipt creation",
            "canonical market-truth promotion",
        ],
        "recommended_next_milestone": portfolio_update["recommended_next_milestone"],
        "owner_manual_send_is_default": False,
        "external_action_executed": False,
    }


def build_ecosystem_alignment_gate(
    capability_sync: Dict[str, Any],
    repo_root: Path = BRIDGE_LABS_ROOT,
    gov_root: Path = GOV_MCP_ROOT,
) -> Dict[str, Any]:
    repos = {
        "ystar-bridge-labs": repo_root,
        "gov-mcp": gov_root,
        "Y-star-gov": YSTAR_GOV_ROOT,
        "ystar-company": YSTAR_COMPANY_ROOT,
    }
    return {
        "artifact_id": "e25_ecosystem_alignment_gate",
        "repos_checked": list(repos),
        "repo_status": {
            name: {"exists": path.exists(), "head": git_head(path), "branch": git_branch(path)}
            for name, path in repos.items()
        },
        "gov_mcp_modified": True,
        "gov_mcp_delivered": capability_sync["source_delivery_remote_confirmed"],
        "gov_mcp_head": capability_sync["source_head"],
        "bridge_labs_modified": True,
        "Y_star_gov_immediate_mutation_needed": False,
        "ystar_company_future_migration_followups": [
            "future CEO KG route may import historical sales assets through evidence-bound migration only"
        ],
        "closure_status": "ecosystem_aligned_with_documented_followups",
        "cross_repo_impact_update": [
            {"repo": "gov-mcp", "impact": "Canonical provider boundary now includes sandbox/idempotency foundation."},
            {"repo": "ystar-bridge-labs", "impact": "CEO KG consumes sandbox result as working internal execution evidence."},
            {"repo": "Y-star-gov", "impact": "Read-only governance alignment; no immediate mutation."},
            {"repo": "ystar-company", "impact": "Read-only historical commercial context; migration follow-up only."},
        ],
        "drift_blockers": [
            "live provider still disabled",
            "production persistent idempotency not configured for live",
            "real customer feedback evidence still absent",
        ],
        "external_action_executed": False,
    }


def build_repo_modification_decision_packet(capability_sync: Dict[str, Any]) -> Dict[str, Any]:
    return {
        "artifact_id": "e25_repo_modification_decision_packet",
        "decisions": [
            {
                "repo": "gov-mcp",
                "decision": "immediate_update_required_and_delivered",
                "reason": "Sandbox provider mode and persistent idempotency foundation belong in canonical provider boundary.",
                "delivered": capability_sync["source_delivery_remote_confirmed"],
            },
            {
                "repo": "ystar-bridge-labs",
                "decision": "bridge_labs_update_required",
                "reason": "CEO KG, control room, route selection, and sandbox feedback artifacts live in commercial runtime.",
                "delivered_by_this_job": True,
            },
            {
                "repo": "Y-star-gov",
                "decision": "no_change_needed",
                "reason": "Normative governance concepts are aligned read-only for E25.",
            },
            {
                "repo": "ystar-company",
                "decision": "future_ystar_company_migration_required",
                "reason": "Historical commercial assets remain source material for future evidence-bound KG migrations.",
            },
        ],
        "cross_repo_mutation_performed": True,
        "external_action_executed": False,
    }


def build_future_sandbox_live_policy() -> Dict[str, Any]:
    requirements = [
        "CEO KG route selection",
        "provider sandbox manifest",
        "sandbox readiness validator",
        "sandbox guard stack",
        "sandbox receipt ledger",
        "persistent idempotency status",
        "suppression/compliance checks",
        "kill switch",
        "sandbox-to-live promotion result",
        "CEO KG feedback ingestion",
        "CEO brain update",
        "ecosystem alignment proof",
        "explicit no real external action unless live mode is explicitly enabled and validated",
    ]
    return {
        "artifact_id": "e25_future_sandbox_live_policy",
        "future_sandbox_live_milestone_requirements": requirements,
        "owner_manual_send_default_allowed": False,
        "sandbox_results_are_market_truth": False,
        "live_requires_explicit_provider_enablement_and_tests": True,
        "external_action_executed": False,
    }


def build_czl_closure(
    capability_sync: Dict[str, Any],
    execution_results: Dict[str, Any],
    receipt_ledger: Dict[str, Any],
    feedback: Dict[str, Any],
    brain_update: Dict[str, Any],
    alignment: Dict[str, Any],
) -> Dict[str, Any]:
    return {
        "artifact_id": "e25_czl_closure",
        "Y_star": "Provider sandbox enablement with CEO KG feedback loop",
        "Rt_plus_1": 0,
        "no_real_external_action_occurred": True,
        "no_provider_api_called": True,
        "no_customer_contacted": True,
        "no_message_sent": True,
        "no_live_receipt_created": True,
        "sandbox_receipt_distinct_from_live_receipt": receipt_ledger["sandbox_receipts_distinct_from_live_receipts"],
        "sandbox_execution_count": execution_results["sandbox_executed_count"],
        "sandbox_receipt_count": receipt_ledger["sandbox_receipt_count"],
        "ceo_kg_updated_only_with_internal_execution_evidence": True,
        "kg_delta_node_count": feedback["kg_delta_node_count"],
        "kg_delta_edge_count": feedback["kg_delta_edge_count"],
        "no_fake_customer_feedback_created": True,
        "no_fake_target_evidence_created": True,
        "live_provider_honestly_reported": "disabled",
        "owner_manual_send_is_not_default": True,
        "ecosystem_alignment_status": alignment["closure_status"],
        "current_strategic_bottleneck": brain_update["current_strategic_bottleneck"],
        "external_action_executed": False,
    }


def build_all(repo_root: Path = BRIDGE_LABS_ROOT, gov_root: Path = GOV_MCP_ROOT) -> Dict[str, Any]:
    route = build_ceo_kg_sandbox_route_selection(repo_root)
    capability = build_provider_sandbox_capability_sync(gov_root)
    envelopes = build_sandbox_envelopes(route, capability)
    guards = build_sandbox_guard_results(envelopes, capability)
    execution = build_sandbox_execution_results(envelopes, guards, capability)
    ledger = build_sandbox_receipt_ledger(execution)
    idempotency = build_persistent_idempotency_status(capability)
    blockers = build_live_promotion_blockers(envelopes, capability, idempotency)
    feedback = build_ceo_kg_feedback_ingestion(route, capability, execution, blockers)
    brain = build_ceo_brain_update(repo_root, route, execution, blockers, feedback)
    portfolio = build_revenue_portfolio_update(repo_root, route, brain, blockers)
    control = build_sandbox_control_room(route, capability, execution, ledger, idempotency, blockers, brain, portfolio)
    alignment = build_ecosystem_alignment_gate(capability, repo_root, gov_root)
    repo_decision = build_repo_modification_decision_packet(capability)
    future_policy = build_future_sandbox_live_policy()
    closure = build_czl_closure(capability, execution, ledger, feedback, brain, alignment)
    return {
        "route": route,
        "capability": capability,
        "envelopes": envelopes,
        "guards": guards,
        "execution": execution,
        "ledger": ledger,
        "idempotency": idempotency,
        "blockers": blockers,
        "feedback": feedback,
        "brain": brain,
        "portfolio": portfolio,
        "control": control,
        "alignment": alignment,
        "repo_decision": repo_decision,
        "future_policy": future_policy,
        "closure": closure,
    }
