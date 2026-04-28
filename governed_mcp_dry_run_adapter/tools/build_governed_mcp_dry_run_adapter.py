#!/usr/bin/env python3
"""Build deterministic L5.6 governed MCP dry-run adapter proof artifacts."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[2]

ADAPTER = ROOT / "governed_mcp_dry_run_adapter"
INTENT = ROOT / "mcp_request_intent_projection"
PRE_U = ROOT / "mcp_pre_u_packet_candidate"
DECISION = ROOT / "mcp_governance_decision_envelope"
BRIDGE = ROOT / "mcp_bridge_authorization_receipt"
CALL = ROOT / "governed_mcp_call_candidate"
RECEIPT = ROOT / "mcp_dry_run_receipt_and_cieu"
RESIDUAL = ROOT / "mcp_residual_and_learning_candidate"
READINESS = ROOT / "governed_mcp_adapter_readiness"

SCHEMA_VERSION = "v0"

INPUT_REFS = {
    "behavior_y_star": "mission_to_behavior_y_star_projection/behavior_level_y_star_candidate.json",
    "behavior_pre_u": (
        "behavior_y_star_to_pre_u_candidate/pre_u_packet_candidate_from_behavior_y_star.json"
    ),
    "projection_cycle_run": (
        "projection_checked_autonomous_work_cycle/projection_checked_cycle_run.json"
    ),
    "governed_mcp_interface_contract": (
        "governed_mcp_interface_contract/governed_mcp_interface_contract.json"
    ),
    "mcp_call_pre_u_boundary_contract": (
        "governed_mcp_interface_contract/mcp_call_pre_u_boundary_contract.json"
    ),
    "mcp_call_cieu_receipt_contract": (
        "governed_mcp_interface_contract/mcp_call_cieu_receipt_contract.json"
    ),
    "required_gate_sequence": "cross_repo_non_bypass_proof/required_gate_sequence.json",
    "forbidden_bypass_path_matrix": "cross_repo_non_bypass_proof/forbidden_bypass_path_matrix.json",
    "cross_repo_governance_readiness": (
        "cross_repo_gap_and_readiness/cross_repo_governance_readiness.json"
    ),
    "pre_u_to_y_star_gov_expectation_map": (
        "ystar_company_to_y_star_gov_alignment/pre_u_candidate_to_validator_expectation_map.json"
    ),
    "gov_mcp_bypass_risk_inventory": "gov_mcp_boundary_inventory/gov_mcp_bypass_risk_inventory.json",
}

SAFETY_FLAGS = {
    "live_execution_enabled": False,
    "behavior_execution_enabled": False,
    "external_action_enabled": False,
    "network_enabled": False,
    "scheduler_enabled": False,
    "daemon_enabled": False,
    "mcp_server_execution_enabled": False,
    "mcp_tool_execution_enabled": False,
    "mcp_resource_mutation_enabled": False,
    "cieu_persistence_enabled": False,
    "brain_writeback_enabled": False,
    "memory_ingestion_enabled": False,
    "candidate_auto_approval_enabled": False,
    "canonical_policy_mutation_enabled": False,
    "y_star_gov_modification_enabled": False,
    "gov_mcp_modification_enabled": False,
    "semantic_truth_scoring_enabled": False,
    "raw_runtime_artifact_reading_enabled": False,
    "revenue_opportunity_discovery_enabled": False,
}

ADAPTER_STAGES = [
    "load_behavior_level_y_star",
    "load_cross_repo_non_bypass_contract",
    "derive_mcp_request_intent",
    "generate_mcp_call_pre_u_packet_candidate",
    "map_pre_u_candidate_to_y_star_gov_expectations",
    "generate_dry_run_governance_decision_envelope",
    "generate_bridge_authorization_receipt",
    "generate_governed_mcp_call_candidate",
    "block_real_mcp_execution",
    "generate_mcp_dry_run_receipt",
    "emit_mcp_cieu_like_event_fixture",
    "compute_mcp_residual_delta",
    "create_review_only_mcp_learning_candidate",
    "produce_l5_7_recommendation",
]

FORBIDDEN_OPERATIONS = [
    "modifying Y-star-gov",
    "modifying gov-mcp",
    "starting gov-mcp server",
    "executing MCP tools",
    "mutating MCP resources",
    "running Y-star-gov live hooks",
    "reading raw DB/WAL/SHM/log contents",
    "reading active-agent marker contents",
    "running daemon/scheduler/runtime scripts",
    "external network/API calls",
    "GitHub issue/PR creation",
    "git push",
    "CIEU DB writes",
    "brain writeback",
    "memory ingestion",
    "candidate approval",
    "canonical policy mutation",
    "L6 revenue opportunity discovery",
    "semantic truth scoring",
    "direct behavior execution",
]

DENIED_SCOPE = [
    "real MCP server startup",
    "MCP tool execution",
    "MCP resource mutation",
    "external action",
    "network/API call",
    "DB/log/raw runtime artifact read",
    "brain writeback",
    "memory ingestion",
    "canonical policy mutation",
    "candidate approval",
    "L6 revenue opportunity discovery",
]

ALLOWED_SCOPE = [
    "local dry-run adapter fixture generation",
    "safe generated/read-model summary reference",
    "governance expectation mapping",
    "bridge receipt fixture generation",
    "CIEU-like fixture generation without persistence",
    "review-only learning candidate generation",
]


def rel(path: Path) -> str:
    return str(path.relative_to(ROOT))


def load_json(relative_path: str) -> dict[str, Any]:
    if relative_path not in set(INPUT_REFS.values()):
        raise ValueError(f"Refusing non-curated L5.6 input: {relative_path}")
    path = ROOT / relative_path
    if not path.exists():
        raise FileNotFoundError(f"Missing curated L5.6 input: {relative_path}")
    return json.loads(path.read_text(encoding="utf-8"))


def write_json(path: Path, payload: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


def write_text(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def md(title: str, lines: list[str]) -> str:
    return "# " + title + "\n\n" + "\n".join(lines) + "\n"


def common_false_status() -> dict[str, Any]:
    return {
        **SAFETY_FLAGS,
        "y_star_gov_unmodified": True,
        "gov_mcp_unmodified": True,
        "mcp_server_not_started": True,
        "mcp_tool_not_executed": True,
        "mcp_resource_not_mutated": True,
        "db_log_wal_shm_active_marker_content_read": False,
        "candidate_approved": False,
        "candidate_applied": False,
        "l6_revenue_opportunity_discovery_implemented": False,
    }


def evidence_refs(*refs: str) -> list[str]:
    return [ref for ref in refs if ref]


def build_contract() -> dict[str, Any]:
    return {
        "schema_name": "ystar.governed_mcp_dry_run_adapter.contract",
        "schema_version": SCHEMA_VERSION,
        "adapter_name": "Governed MCP Dry-Run Adapter",
        "purpose": (
            "Prove future MCP/tool/resource calls are downstream of behavior-level Y*, Pre-U, "
            "governance expectation, bridge receipt, CIEU-like receipt, residual delta, and "
            "review-only learning gates without executing MCP."
        ),
        "required_inputs": list(INPUT_REFS.values()),
        "adapter_stages": ADAPTER_STAGES,
        "required_outputs": [
            "MCP request intent",
            "MCP Pre-U packet candidate",
            "Y-star-gov expectation map",
            "dry-run governance decision envelope",
            "bridge authorization receipt",
            "governed MCP call candidate",
            "real execution blocker",
            "MCP dry-run receipt",
            "MCP CIEU-like event fixture",
            "MCP residual delta",
            "review-only MCP learning candidate",
            "L5.7 readiness",
        ],
        "mcp_non_bypass_requirements": [
            "no_mcp_call_without_behavior_y_star",
            "no_mcp_call_without_pre_u_candidate",
            "no_mcp_call_without_governance_decision",
            "no_mcp_call_without_bridge_receipt",
            "no_mcp_call_without_cieu_receipt",
            "no_mcp_call_without_residual_delta",
        ],
        "governance_boundary_requirements": [
            "Y-star-gov remains canonical validator",
            "ystar-company generates dry-run candidates only",
            "gov-mcp is interface boundary only",
            "live validation requires future approved adapter",
        ],
        "bridge_receipt_requirements": [
            "authorized operation",
            "authorized dry-run scope",
            "denied live/MCP/external scope",
            "CIEU receipt required",
            "residual delta required",
        ],
        "cieu_receipt_requirements": [
            "X_t",
            "U_t",
            "Y_star_t",
            "Y_t_plus_1",
            "R_t_plus_1",
            "persistence disabled",
        ],
        "residual_requirements": [
            "projection alignment residual",
            "Pre-U mapping residual",
            "governance decision residual",
            "bridge receipt residual",
            "MCP execution blocker residual",
            "CIEU receipt residual",
            "review queue residual",
        ],
        "safety_flags": SAFETY_FLAGS,
        "forbidden_operations": FORBIDDEN_OPERATIONS,
        "non_goals": [
            "run gov-mcp",
            "execute MCP tools",
            "modify gov-mcp",
            "modify Y-star-gov",
            "perform live validation",
            "persist CIEU",
            "write brain or memory",
            "approve learning candidates",
            "discover revenue opportunities",
        ],
    }


def build_input_fixture(loaded: dict[str, Any]) -> dict[str, Any]:
    return {
        "schema_name": "ystar.governed_mcp_dry_run_adapter.input_fixture",
        "schema_version": SCHEMA_VERSION,
        "fixture_id": "governed-mcp-dry-run-input-fixture-v0",
        "input_refs": INPUT_REFS,
        "loaded_inputs": {
            key: {
                "source_path": path,
                "loaded": True,
                "schema_name": loaded[key].get("schema_name"),
                "safe_generated_or_contract_source": True,
            }
            for key, path in INPUT_REFS.items()
        },
        "read_only_reference_repos": [
            "/Users/haotianliu/.openclaw/workspace/Y-star-gov",
            "/Users/haotianliu/.openclaw/workspace/gov-mcp",
        ],
        "reference_repo_modification_performed": False,
        "mcp_server_or_tool_executed": False,
        "safety_flags": SAFETY_FLAGS,
    }


def build_request_intent(behavior: dict[str, Any]) -> tuple[dict[str, Any], dict[str, Any], dict[str, Any]]:
    behavior_id = behavior.get("behavior_y_star_id")
    candidate_u = {
        "candidate_u_id": "candidate-u-governed-mcp-read-summary-dry-run-v0",
        "candidate_u": "request a safe generated console/read-model summary through a future governed MCP resource boundary",
        "execution_mode": "dry_run_adapter_fixture",
        "real_mcp_execution": False,
    }
    intent = {
        "schema_name": "ystar.mcp_request_intent_projection.intent",
        "schema_version": SCHEMA_VERSION,
        "request_intent_id": "mcp-request-intent-read-safe-summary-v0",
        "source_behavior_y_star_id": behavior_id,
        "declared_request_intent": (
            "retrieve a safe console/read-model summary through a future governed MCP resource adapter"
        ),
        "requested_mcp_surface_type": "resource",
        "requested_operation_class": "read_safe_generated_summary_dry_run",
        "candidate_U_summary": candidate_u,
        "candidate_u_summary": candidate_u,
        "expected_safe_result": (
            "A dry-run receipt summarizing what a future governed MCP resource read would return "
            "without starting a server or reading raw runtime artifacts."
        ),
        "explicit_non_goals": [
            "do not execute MCP",
            "do not start gov-mcp",
            "do not mutate files or resources",
            "do not call network",
            "do not read DB/log/raw runtime artifacts",
            "do not write brain or memory",
        ],
        "forbidden_request_patterns": DENIED_SCOPE,
        "internal_only": True,
        "dry_run_only": True,
        "evidence_refs": evidence_refs(
            INPUT_REFS["behavior_y_star"],
            INPUT_REFS["governed_mcp_interface_contract"],
            INPUT_REFS["required_gate_sequence"],
        ),
        "safety_flags": SAFETY_FLAGS,
    }
    context = {
        "schema_name": "ystar.mcp_request_intent_projection.context_fixture",
        "schema_version": SCHEMA_VERSION,
        "context_fixture_id": "mcp-request-context-safe-summary-v0",
        "internal_only": True,
        "dry_run_only": True,
        "safe_resource_class": "tracked_generated_console_read_model_summary",
        "requested_safe_resource_ref": "console_read_model/generated/cross_repo_governance_summary.json",
        "no_real_mcp_server": True,
        "no_real_tool_execution": True,
        "no_external_action": True,
        "no_resource_mutation": True,
        "no_network": True,
        "no_db_log_runtime_content_read": True,
        "safety_flags": SAFETY_FLAGS,
    }
    boundary = {
        "schema_name": "ystar.mcp_request_intent_projection.operation_boundary",
        "schema_version": SCHEMA_VERSION,
        "operation_boundary_id": "mcp-requested-operation-boundary-v0",
        "requested_operation": "read_safe_generated_summary_resource_dry_run",
        "allowed_operations": ALLOWED_SCOPE,
        "forbidden_operations": DENIED_SCOPE,
        "external_network_forbidden": True,
        "raw_runtime_artifact_reads_forbidden": True,
        "brain_memory_writeback_forbidden": True,
        "revenue_discovery_forbidden": True,
        "mcp_execution_forbidden_now": True,
        "safety_flags": SAFETY_FLAGS,
    }
    return intent, context, boundary


def build_pre_u(
    behavior: dict[str, Any],
    intent: dict[str, Any],
    context: dict[str, Any],
    expectation_source: dict[str, Any],
) -> tuple[dict[str, Any], dict[str, Any], str, dict[str, Any]]:
    packet_id = "mcp-pre-u-packet-candidate-read-safe-summary-v0"
    candidate_u = intent["candidate_U_summary"]
    packet = {
        "schema_name": "ystar.mcp_pre_u_packet_candidate.packet",
        "schema_version": SCHEMA_VERSION,
        "pre_u_packet_id": packet_id,
        "source_behavior_y_star_id": behavior.get("behavior_y_star_id"),
        "declared_Y_star": behavior.get("declared_behavior_y_star"),
        "X_t": context,
        "Xt": context,
        "candidate_U": candidate_u,
        "mcp_tool_or_resource_id": "future-gov-mcp-resource:console-read-model-summary",
        "requested_operation": "read_safe_generated_summary_resource_dry_run",
        "allowed_scope": ALLOWED_SCOPE,
        "denied_scope": DENIED_SCOPE,
        "governance_expectations": {
            "requires_y_star_gov_validation_before_execution": True,
            "versioned_governance_adapter_allowed_for_future_dry_run": True,
            "canonical_live_validation_performed_now": False,
            "source_expectation_map": INPUT_REFS["pre_u_to_y_star_gov_expectation_map"],
        },
        "trace_refs": [
            INPUT_REFS["behavior_y_star"],
            INPUT_REFS["required_gate_sequence"],
            "mcp_request_intent_projection/mcp_request_intent.json",
        ],
        "execution_boundary": SAFETY_FLAGS,
        "safety_flags": SAFETY_FLAGS,
        "unresolved_gaps": [
            "Y-star-gov live validation not invoked",
            "gov-mcp resource adapter not implemented",
            "real MCP receipt schema requires future versioned adapter test",
        ],
        "dry_run_only": True,
        "production_ready": False,
        "requires_y_star_gov_validation_before_execution": True,
        "live_execution_authorized": False,
        "behavior_execution_authorized": False,
        "external_action_authorized": False,
        "mcp_tool_execution_authorized": False,
    }
    expectation_map = {
        "schema_name": "ystar.mcp_pre_u_packet_candidate.y_star_gov_expectation_map",
        "schema_version": SCHEMA_VERSION,
        "map_id": "mcp-pre-u-to-y-star-gov-expectation-map-v0",
        "source_pre_u_packet_id": packet_id,
        "source_expectation_map_ref": INPUT_REFS["pre_u_to_y_star_gov_expectation_map"],
        "mapped_fields": [
            {"mcp_pre_u_field": "declared_Y_star", "y_star_gov_expectation": "declared_Y_star"},
            {"mcp_pre_u_field": "X_t / Xt", "y_star_gov_expectation": "X_t / Xt"},
            {"mcp_pre_u_field": "candidate_U", "y_star_gov_expectation": "candidate_U"},
            {
                "mcp_pre_u_field": "execution_boundary",
                "y_star_gov_expectation": "safety and denied-scope validation",
            },
            {"mcp_pre_u_field": "trace_refs", "y_star_gov_expectation": "audit trace references"},
        ],
        "expectation_source_status": expectation_source.get("validator_status"),
        "canonical_y_star_gov_validation_performed": False,
        "y_star_gov_validation_required_before_live": True,
        "safety_flags": SAFETY_FLAGS,
    }
    gap_report = md(
        "MCP Pre-U Gap Report",
        [
            "- Y-star-gov validation is required before live execution but was not invoked in L5.6.",
            "- gov-mcp was not started and no MCP tool/resource was executed.",
            "- Production-ready adapter semantics remain future L5.7+ work.",
        ],
    )
    summary = {
        "schema_name": "ystar.mcp_pre_u_packet_candidate.summary",
        "schema_version": SCHEMA_VERSION,
        "mcp_pre_u_packet_candidate_generated": True,
        "source_behavior_y_star_id": behavior.get("behavior_y_star_id"),
        "requires_y_star_gov_validation_before_execution": True,
        "dry_run_only": True,
        "production_ready": False,
        "live_execution_authorized": False,
        "behavior_execution_authorized": False,
        "external_action_authorized": False,
        "mcp_tool_execution_authorized": False,
        "canonical_y_star_gov_validation_performed": False,
        "safety_flags": SAFETY_FLAGS,
    }
    return packet, expectation_map, gap_report, summary


def build_decision(packet: dict[str, Any]) -> tuple[dict[str, Any], dict[str, Any], str, dict[str, Any]]:
    decision_id = "mcp-governance-decision-envelope-dry-run-v0"
    envelope = {
        "schema_name": "ystar.mcp_governance_decision_envelope.envelope",
        "schema_version": SCHEMA_VERSION,
        "decision_id": decision_id,
        "source_pre_u_packet_id": packet["pre_u_packet_id"],
        "decision": "allow_mcp_dry_run_only",
        "decision_scope": "internal deterministic adapter fixture only",
        "allowed_scope": ALLOWED_SCOPE,
        "denied_scope": DENIED_SCOPE,
        "required_next_gate": "bridge_authorization_receipt",
        "reason_codes": [
            "behavior_y_star_present",
            "pre_u_candidate_present",
            "operation_internal_dry_run_only",
            "real_mcp_execution_blocked",
            "no_external_network_or_writeback_requested",
        ],
        "evidence_refs": evidence_refs(
            "mcp_pre_u_packet_candidate/mcp_call_pre_u_packet_candidate.json",
            INPUT_REFS["required_gate_sequence"],
            INPUT_REFS["forbidden_bypass_path_matrix"],
        ),
        "dry_run_only": True,
        "canonical_y_star_gov_validation_performed": False,
        "y_star_gov_validation_required_before_live": True,
        "live_execution_authorized": False,
        "mcp_tool_execution_authorized": False,
        "external_action_authorized": False,
        "safety_flags": SAFETY_FLAGS,
    }
    reason_trace = {
        "schema_name": "ystar.mcp_governance_decision_envelope.reason_trace",
        "schema_version": SCHEMA_VERSION,
        "trace_id": "mcp-decision-reason-trace-v0",
        "source_decision_id": decision_id,
        "structural_checks": [
            {"check": "behavior Y* loaded", "result": "pass"},
            {"check": "Pre-U candidate generated", "result": "pass"},
            {"check": "future MCP operation is internal dry-run", "result": "pass"},
            {"check": "real MCP execution requested", "result": "blocked_false"},
            {"check": "Y-star-gov live validation performed", "result": "not_performed_required_before_live"},
        ],
        "semantic_truth_scoring_performed": False,
        "safety_flags": SAFETY_FLAGS,
    }
    gap_report = md(
        "MCP Governance Decision Gap Report",
        [
            "- Decision envelope is dry-run only and does not claim canonical Y-star-gov validation.",
            "- Live authorization remains blocked until a future approved governance adapter exists.",
        ],
    )
    summary = {
        "schema_name": "ystar.mcp_governance_decision_envelope.summary",
        "schema_version": SCHEMA_VERSION,
        "governance_decision_envelope_generated": True,
        "decision": "allow_mcp_dry_run_only",
        "canonical_y_star_gov_validation_performed": False,
        "y_star_gov_validation_required_before_live": True,
        "live_execution_authorized": False,
        "mcp_tool_execution_authorized": False,
        "external_action_authorized": False,
        "safety_flags": SAFETY_FLAGS,
    }
    return envelope, reason_trace, gap_report, summary


def build_bridge(decision: dict[str, Any]) -> tuple[dict[str, Any], dict[str, Any], dict[str, Any], str]:
    receipt_id = "mcp-bridge-authorization-receipt-dry-run-v0"
    receipt = {
        "schema_name": "ystar.mcp_bridge_authorization_receipt.receipt",
        "schema_version": SCHEMA_VERSION,
        "bridge_receipt_id": receipt_id,
        "source_decision_id": decision["decision_id"],
        "authorized_operation": "continue_to_governed_mcp_call_candidate_fixture",
        "authorized_scope": ALLOWED_SCOPE,
        "denied_scope": DENIED_SCOPE,
        "authorization_mode": "dry_run_adapter_only",
        "real_mcp_execution_authorized": False,
        "live_execution_authorized": False,
        "external_action_authorized": False,
        "cieu_receipt_required": True,
        "residual_delta_required": True,
        "evidence_refs": evidence_refs(
            "mcp_governance_decision_envelope/mcp_governance_decision_envelope.json"
        ),
        "safety_flags": SAFETY_FLAGS,
    }
    denied = {
        "schema_name": "ystar.mcp_bridge_authorization_receipt.denied_scope",
        "schema_version": SCHEMA_VERSION,
        "denied_scope_id": "mcp-bridge-denied-scope-v0",
        "source_bridge_receipt_id": receipt_id,
        "denied_operations": DENIED_SCOPE,
        "real_mcp_execution_denied": True,
        "external_action_denied": True,
        "network_api_call_denied": True,
        "db_log_raw_runtime_artifact_read_denied": True,
        "brain_writeback_denied": True,
        "memory_ingestion_denied": True,
        "canonical_policy_mutation_denied": True,
        "candidate_approval_denied": True,
        "safety_flags": SAFETY_FLAGS,
    }
    summary = {
        "schema_name": "ystar.mcp_bridge_authorization_receipt.summary",
        "schema_version": SCHEMA_VERSION,
        "bridge_receipt_generated": True,
        "authorization_mode": "dry_run_adapter_only",
        "real_mcp_execution_authorized": False,
        "live_execution_authorized": False,
        "external_action_authorized": False,
        "cieu_receipt_required": True,
        "residual_delta_required": True,
        "safety_flags": SAFETY_FLAGS,
    }
    report = md(
        "MCP Bridge Receipt Report",
        [
            "- Bridge receipt authorizes dry-run adapter continuation only.",
            "- Real MCP server startup, tool calls, resource mutation, network, and writeback are denied.",
        ],
    )
    return receipt, denied, summary, report


def build_call_candidate(
    bridge: dict[str, Any],
    packet: dict[str, Any],
) -> tuple[dict[str, Any], dict[str, Any], dict[str, Any], dict[str, Any], str]:
    call_id = "governed-mcp-call-candidate-read-safe-summary-v0"
    candidate = {
        "schema_name": "ystar.governed_mcp_call_candidate.candidate",
        "schema_version": SCHEMA_VERSION,
        "mcp_call_candidate_id": call_id,
        "source_bridge_receipt_id": bridge["bridge_receipt_id"],
        "source_pre_u_packet_id": packet["pre_u_packet_id"],
        "mcp_tool_or_resource_id": packet["mcp_tool_or_resource_id"],
        "requested_operation": packet["requested_operation"],
        "requested_U": packet["candidate_U"],
        "allowed_U": "produce dry-run adapter receipt for safe generated summary request",
        "denied_U": DENIED_SCOPE,
        "dry_run_only": True,
        "real_execution_performed": False,
        "mcp_server_started": False,
        "mcp_tool_called": False,
        "mcp_resource_mutated": False,
        "network_called": False,
        "evidence_refs": evidence_refs(
            "mcp_bridge_authorization_receipt/mcp_bridge_authorization_receipt.json",
            "mcp_pre_u_packet_candidate/mcp_call_pre_u_packet_candidate.json",
        ),
        "safety_flags": SAFETY_FLAGS,
    }
    plan = {
        "schema_name": "ystar.governed_mcp_call_candidate.execution_plan",
        "schema_version": SCHEMA_VERSION,
        "execution_plan_id": "governed-mcp-call-execution-plan-dry-run-v0",
        "source_mcp_call_candidate_id": call_id,
        "plan_mode": "dry_run_plan_only",
        "planned_steps": [
            "confirm bridge receipt",
            "confirm real MCP execution is blocked",
            "construct dry-run receipt fixture",
            "construct CIEU-like fixture",
            "construct residual delta",
        ],
        "allowed_operations": ALLOWED_SCOPE,
        "forbidden_operations": DENIED_SCOPE,
        "real_execution_performed": False,
        "safety_flags": SAFETY_FLAGS,
    }
    blocker = {
        "schema_name": "ystar.governed_mcp_call_candidate.real_execution_blocker",
        "schema_version": SCHEMA_VERSION,
        "blocker_id": "mcp-real-execution-blocker-v0",
        "source_mcp_call_candidate_id": call_id,
        "real_mcp_execution_blocked": True,
        "block_reason": (
            "L5.6 is an adapter proof only. Live MCP execution requires future approved mode, "
            "Y-star-gov validation or versioned adapter validation, operator controls, and receipt persistence policy."
        ),
        "blocked_operations": DENIED_SCOPE,
        "future_unblock_requirements": [
            "controlled canonical learning design",
            "versioned governed MCP adapter",
            "operator approval mode",
            "Y-star-gov validation integration",
            "CIEU persistence boundary review",
        ],
        "safety_flags": SAFETY_FLAGS,
    }
    summary = {
        "schema_name": "ystar.governed_mcp_call_candidate.summary",
        "schema_version": SCHEMA_VERSION,
        "governed_mcp_call_candidate_generated": True,
        "real_mcp_execution_blocked": True,
        "real_execution_performed": False,
        "mcp_server_started": False,
        "mcp_tool_called": False,
        "mcp_resource_mutated": False,
        "network_called": False,
        "safety_flags": SAFETY_FLAGS,
    }
    report = md(
        "Governed MCP Call Report",
        [
            "- A governed MCP call candidate was generated as a fixture.",
            "- Real MCP execution is explicitly blocked and no server/tool/resource was used.",
        ],
    )
    return candidate, plan, blocker, summary, report


def build_receipt_and_cieu(
    call: dict[str, Any],
    packet: dict[str, Any],
    decision: dict[str, Any],
    bridge: dict[str, Any],
) -> tuple[dict[str, Any], dict[str, Any], dict[str, Any], dict[str, Any], dict[str, Any], str]:
    receipt_id = "mcp-dry-run-receipt-read-safe-summary-v0"
    actual_summary = {
        "result_mode": "mock_dry_run_summary",
        "safe_resource_ref": "console_read_model/generated/cross_repo_governance_summary.json",
        "observed_effect": "No MCP server was started; receipt records only the intended safe resource boundary.",
    }
    receipt = {
        "schema_name": "ystar.mcp_dry_run_receipt_and_cieu.receipt",
        "schema_version": SCHEMA_VERSION,
        "mcp_call_id": receipt_id,
        "source_pre_u_packet_id": packet["pre_u_packet_id"],
        "source_decision_envelope_id": decision["decision_id"],
        "source_bridge_receipt_id": bridge["bridge_receipt_id"],
        "tool_or_resource_id": call["mcp_tool_or_resource_id"],
        "requested_U": call["requested_U"],
        "allowed_U": call["allowed_U"],
        "actual_result_summary": actual_summary,
        "execution_mode": "dry_run_adapter_fixture",
        "real_execution_performed": False,
        "mcp_server_started": False,
        "mcp_tool_called": False,
        "mcp_resource_mutated": False,
        "network_called": False,
        "persistence_mode": "none",
        "evidence_refs": evidence_refs(
            "governed_mcp_call_candidate/governed_mcp_call_candidate.json",
            "mcp_bridge_authorization_receipt/mcp_bridge_authorization_receipt.json",
        ),
        "safety_flags": SAFETY_FLAGS,
    }
    predicted = {
        "schema_name": "ystar.mcp_dry_run_receipt_and_cieu.predicted_outcome",
        "schema_version": SCHEMA_VERSION,
        "predicted_outcome_id": "mcp-predicted-outcome-v0",
        "source_pre_u_packet_id": packet["pre_u_packet_id"],
        "predicted_Y_t_plus_1": "Dry-run receipt exists and real MCP execution remains blocked.",
        "predicted_R_t_plus_1": "Residual should record missing live validation and execution blocker only.",
        "safety_flags": SAFETY_FLAGS,
    }
    mock_actual = {
        "schema_name": "ystar.mcp_dry_run_receipt_and_cieu.mock_actual_outcome",
        "schema_version": SCHEMA_VERSION,
        "mock_actual_outcome_id": "mcp-mock-actual-outcome-v0",
        "synthetic_dry_run_only": True,
        "Y_t_plus_1": actual_summary,
        "real_execution_performed": False,
        "mcp_server_started": False,
        "mcp_tool_called": False,
        "mcp_resource_mutated": False,
        "network_called": False,
        "safety_flags": SAFETY_FLAGS,
    }
    cieu = {
        "schema_name": "ystar.mcp_dry_run_receipt_and_cieu.cieu_event_fixture",
        "schema_version": SCHEMA_VERSION,
        "event_id": "mcp-cieu-like-event-fixture-v0",
        "X_t": packet["X_t"],
        "U_t": {
            "source_mcp_call_candidate_id": call["mcp_call_candidate_id"],
            "requested_U": call["requested_U"],
            "allowed_U": call["allowed_U"],
        },
        "Y_star_t": {
            "source_behavior_y_star_id": packet["source_behavior_y_star_id"],
            "declared_Y_star": packet["declared_Y_star"],
            "source_pre_u_packet_id": packet["pre_u_packet_id"],
        },
        "Y_t_plus_1": actual_summary,
        "R_t_plus_1": {
            "residual_mode": "deterministic_structural_residual",
            "real_execution_absent": True,
            "missing_live_validation": True,
            "mcp_execution_blocked": True,
        },
        "event_mode": "mcp_dry_run_fixture",
        "persistence_enabled": False,
        "db_write_performed": False,
        "safety_flags": SAFETY_FLAGS,
    }
    summary = {
        "schema_name": "ystar.mcp_dry_run_receipt_and_cieu.summary",
        "schema_version": SCHEMA_VERSION,
        "mcp_dry_run_receipt_generated": True,
        "mcp_cieu_event_fixture_generated": True,
        "execution_mode": "dry_run_adapter_fixture",
        "real_execution_performed": False,
        "mcp_server_started": False,
        "mcp_tool_called": False,
        "mcp_resource_mutated": False,
        "network_called": False,
        "persistence_enabled": False,
        "db_write_performed": False,
        "safety_flags": SAFETY_FLAGS,
    }
    report = md(
        "MCP Receipt and CIEU Report",
        [
            "- Dry-run receipt and CIEU-like fixture were generated.",
            "- Y_t_plus_1 is synthetic; R_t_plus_1 is structural and not semantic truth scoring.",
        ],
    )
    return receipt, cieu, predicted, mock_actual, summary, report


def build_residual_learning(
    cieu: dict[str, Any],
) -> tuple[dict[str, Any], dict[str, Any], dict[str, Any], dict[str, Any], dict[str, Any], str]:
    delta_id = "mcp-residual-delta-v0"
    classes = {
        "mcp_projection_alignment_residual": "behavior Y* mapped to MCP request intent; no live validation",
        "mcp_pre_u_mapping_residual": "MCP-specific Pre-U candidate is structurally complete but unvalidated",
        "governance_decision_residual": "dry-run envelope allows only fixture continuation",
        "bridge_receipt_residual": "bridge receipt authorizes dry-run adapter only",
        "mcp_execution_blocker_residual": "real MCP execution intentionally blocked",
        "cieu_receipt_residual": "CIEU-like fixture emitted without persistence",
        "evidence_gap_residual": "future adapter needs production schema and validator integration evidence",
        "learning_queue_residual": "learning candidate is review-only",
        "live_blocker_residual": "live execution remains blocked",
        "writeback_blocker_residual": "brain/memory writeback remains blocked",
    }
    delta = {
        "schema_name": "ystar.mcp_residual_and_learning_candidate.residual_delta",
        "schema_version": SCHEMA_VERSION,
        "residual_delta_id": delta_id,
        "source_cieu_event_id": cieu["event_id"],
        **classes,
        "residual_classes": classes,
        "semantic_truth_scoring_performed": False,
        "learning_eligibility": "review_queue_only",
        "direct_writeback_allowed": False,
        "safety_flags": SAFETY_FLAGS,
    }
    classification = {
        "schema_name": "ystar.mcp_residual_and_learning_candidate.classification",
        "schema_version": SCHEMA_VERSION,
        "classification_id": "mcp-residual-classification-v0",
        "source_mcp_residual_delta_id": delta_id,
        "residual_class_names": list(classes),
        "allowed_learning_targets": [
            "governed_mcp_interface_contract",
            "mcp_pre_u_mapping",
            "bridge_receipt_requirements",
            "cieu_receipt_requirements",
            "non_bypass_invariants",
            "residual_classification",
        ],
        "denied_learning_effects": [
            "direct brain writeback",
            "direct memory ingestion",
            "candidate auto-approval",
            "canonical policy mutation",
            "live MCP execution",
        ],
        "safety_flags": SAFETY_FLAGS,
    }
    candidate = {
        "schema_name": "ystar.mcp_residual_and_learning_candidate.learning_candidate",
        "schema_version": SCHEMA_VERSION,
        "candidate_id": "mcp-review-only-learning-candidate-v0",
        "source_mcp_residual_delta_id": delta_id,
        "learning_target": [
            "governed_mcp_interface_contract",
            "mcp_pre_u_mapping",
            "bridge_receipt_requirements",
            "cieu_receipt_requirements",
            "non_bypass_invariants",
            "residual_classification",
        ],
        "proposed_learning_scope": (
            "tighten dry-run MCP adapter requirements and residual labels before any future governed MCP adapter"
        ),
        "evidence_refs": evidence_refs(
            "mcp_residual_and_learning_candidate/mcp_residual_delta.json",
            "mcp_dry_run_receipt_and_cieu/mcp_cieu_event_fixture.json",
        ),
        "eligible_for_review_queue": True,
        "eligible_for_direct_brain_writeback": False,
        "eligible_for_direct_memory_ingestion": False,
        "eligible_for_candidate_auto_approval": False,
        "eligible_for_canonical_policy_mutation": False,
        "requires_human_or_governance_review": True,
        "approved": False,
        "applied": False,
        "live_learning_enabled": False,
        "safety_flags": SAFETY_FLAGS,
    }
    queue = {
        "schema_name": "ystar.mcp_residual_and_learning_candidate.review_queue_entry",
        "schema_version": SCHEMA_VERSION,
        "review_queue_entry_id": "mcp-learning-review-queue-entry-v0",
        "source_candidate_id": candidate["candidate_id"],
        "status": "pending_review",
        "approved": False,
        "applied": False,
        "direct_brain_writeback_allowed": False,
        "direct_memory_ingestion_allowed": False,
        "candidate_auto_approval_allowed": False,
        "safety_flags": SAFETY_FLAGS,
    }
    summary = {
        "schema_name": "ystar.mcp_residual_and_learning_candidate.summary",
        "schema_version": SCHEMA_VERSION,
        "mcp_residual_delta_generated": True,
        "mcp_learning_candidate_generated": True,
        "eligible_for_review_queue": True,
        "approved": False,
        "applied": False,
        "eligible_for_direct_brain_writeback": False,
        "eligible_for_direct_memory_ingestion": False,
        "eligible_for_candidate_auto_approval": False,
        "eligible_for_canonical_policy_mutation": False,
        "safety_flags": SAFETY_FLAGS,
    }
    report = md(
        "MCP Residual Learning Report",
        [
            "- MCP residual classes were generated structurally.",
            "- Learning candidate is review-only, not approved, not applied, and not writeback eligible.",
        ],
    )
    return delta, classification, candidate, queue, summary, report


def build_readiness() -> tuple[dict[str, Any], str, dict[str, Any]]:
    readiness = {
        "schema_name": "ystar.governed_mcp_adapter_readiness.readiness",
        "schema_version": SCHEMA_VERSION,
        "readiness_id": "governed-mcp-adapter-readiness-v0",
        "behavior_y_star_loaded": True,
        "cross_repo_non_bypass_contract_loaded": True,
        "mcp_request_intent_generated": True,
        "mcp_pre_u_packet_candidate_generated": True,
        "governance_decision_envelope_generated": True,
        "bridge_receipt_generated": True,
        "governed_mcp_call_candidate_generated": True,
        "real_mcp_execution_blocked": True,
        "mcp_dry_run_receipt_generated": True,
        "mcp_cieu_event_fixture_generated": True,
        "mcp_residual_delta_generated": True,
        "mcp_learning_candidate_generated": True,
        "y_star_gov_unmodified": True,
        "gov_mcp_unmodified": True,
        "mcp_server_not_started": True,
        "mcp_tool_not_executed": True,
        "mcp_resource_not_mutated": True,
        "live_execution_still_blocked": True,
        "writeback_still_blocked": True,
        "external_action_still_blocked": True,
        "ready_for_l5_7_controlled_canonical_learning_design": True,
        "ready_for_l6_revenue_opportunity_discovery": False,
        **common_false_status(),
        "safety_flags": SAFETY_FLAGS,
        "next_required_milestone": "L5.7 Controlled Canonical Learning Design v0",
    }
    readiness_md = md(
        "Governed MCP Adapter Readiness",
        [
            "- L5.6 dry-run adapter proof is complete.",
            "- Real MCP execution is blocked; Y-star-gov and gov-mcp remain unmodified.",
            "- Ready for L5.7 controlled canonical learning design: true.",
            "- Ready for L6 revenue opportunity discovery: false.",
        ],
    )
    recommendation = {
        "schema_name": "ystar.governed_mcp_adapter_readiness.next_step",
        "schema_version": SCHEMA_VERSION,
        "recommendation_id": "l5-7-recommended-next-step-v0",
        "recommended_next_milestone": "L5.7 Controlled Canonical Learning Design v0",
        "reason": (
            "MCP dry-run adapter non-bypass path exists, but canonical learning controls must be designed "
            "before any live adapter, policy mutation, or revenue discovery work."
        ),
        "ready_for_l6_revenue_opportunity_discovery": False,
        "safety_flags": SAFETY_FLAGS,
    }
    return readiness, readiness_md, recommendation


def build_run(
    contract: dict[str, Any],
    readiness: dict[str, Any],
) -> dict[str, Any]:
    return {
        "schema_name": "ystar.governed_mcp_dry_run_adapter.run",
        "schema_version": SCHEMA_VERSION,
        "run_id": "governed-mcp-dry-run-adapter-run-v0",
        "adapter_name": contract["adapter_name"],
        "adapter_stages_completed": ADAPTER_STAGES,
        "required_gate_sequence_preserved": True,
        "real_mcp_execution_blocked": True,
        "mcp_server_or_tool_executed": False,
        "y_star_gov_modified": False,
        "gov_mcp_modified": False,
        "ready_for_l5_7_controlled_canonical_learning_design": readiness[
            "ready_for_l5_7_controlled_canonical_learning_design"
        ],
        "ready_for_l6_revenue_opportunity_discovery": False,
        "safety_flags": SAFETY_FLAGS,
    }


def build_adapter_summary(readiness: dict[str, Any]) -> dict[str, Any]:
    return {
        "schema_name": "ystar.governed_mcp_dry_run_adapter.summary",
        "schema_version": SCHEMA_VERSION,
        "l5_6_governed_mcp_dry_run_adapter_defined": True,
        "behavior_y_star_loaded": True,
        "mcp_request_intent_generated": True,
        "mcp_pre_u_packet_candidate_generated": True,
        "dry_run_governance_decision_envelope_generated": True,
        "bridge_authorization_receipt_generated": True,
        "governed_mcp_call_candidate_generated": True,
        "real_mcp_execution_blocked": True,
        "mcp_dry_run_receipt_generated": True,
        "mcp_cieu_like_event_generated": True,
        "mcp_residual_delta_generated": True,
        "review_only_mcp_learning_candidate_generated": True,
        "y_star_gov_unmodified": True,
        "gov_mcp_unmodified": True,
        "mcp_server_not_started": True,
        "mcp_tool_not_executed": True,
        "mcp_resource_not_mutated": True,
        "ready_for_l5_7_controlled_canonical_learning_design": readiness[
            "ready_for_l5_7_controlled_canonical_learning_design"
        ],
        "ready_for_l6_revenue_opportunity_discovery": False,
        **SAFETY_FLAGS,
        "next_required_milestone": readiness["next_required_milestone"],
        "generated_adapter_summary": "governed_mcp_dry_run_adapter/governed_mcp_dry_run_adapter_summary.json",
        "generated_readiness": "governed_mcp_adapter_readiness/governed_mcp_adapter_readiness.json",
        "warning": (
            "L5.6 is an adapter proof only. No gov-mcp server/tool/resource was executed or mutated, "
            "and Y-star-gov/gov-mcp remain unmodified."
        ),
    }


def build() -> None:
    loaded = {key: load_json(path) for key, path in INPUT_REFS.items()}
    behavior = loaded["behavior_y_star"]

    contract = build_contract()
    input_fixture = build_input_fixture(loaded)
    intent, context, boundary = build_request_intent(behavior)
    pre_u_packet, pre_u_map, pre_u_gap, pre_u_summary = build_pre_u(
        behavior,
        intent,
        context,
        loaded["pre_u_to_y_star_gov_expectation_map"],
    )
    decision, reason_trace, decision_gap, decision_summary = build_decision(pre_u_packet)
    bridge_receipt, bridge_denied, bridge_summary, bridge_report = build_bridge(decision)
    call_candidate, call_plan, blocker, call_summary, call_report = build_call_candidate(
        bridge_receipt,
        pre_u_packet,
    )
    receipt, cieu, predicted, mock_actual, receipt_summary, receipt_report = build_receipt_and_cieu(
        call_candidate,
        pre_u_packet,
        decision,
        bridge_receipt,
    )
    residual_delta, residual_classification, learning_candidate, review_queue, residual_summary, residual_report = (
        build_residual_learning(cieu)
    )
    readiness, readiness_md, recommendation = build_readiness()
    adapter_run = build_run(contract, readiness)
    adapter_summary = build_adapter_summary(readiness)

    write_json(ADAPTER / "governed_mcp_dry_run_adapter_contract.json", contract)
    write_json(ADAPTER / "governed_mcp_dry_run_input_fixture.json", input_fixture)
    write_json(ADAPTER / "governed_mcp_dry_run_adapter_run.json", adapter_run)
    write_json(ADAPTER / "governed_mcp_dry_run_adapter_summary.json", adapter_summary)
    write_text(
        ADAPTER / "governed_mcp_dry_run_adapter_report.md",
        md(
            "Governed MCP Dry-Run Adapter Report",
            [
                "- Behavior-level Y* was loaded and converted into a safe MCP request intent.",
                "- MCP Pre-U packet, dry-run governance decision, bridge receipt, call candidate, receipt, CIEU-like fixture, residual, and review-only learning candidate were generated.",
                "- No MCP server/tool/resource was executed or mutated.",
                "- Y-star-gov and gov-mcp were not modified.",
            ],
        ),
    )

    write_json(INTENT / "mcp_request_intent.json", intent)
    write_json(INTENT / "mcp_request_context_fixture.json", context)
    write_json(INTENT / "mcp_requested_operation_boundary.json", boundary)
    write_json(
        INTENT / "mcp_request_intent_summary.json",
        {
            "schema_name": "ystar.mcp_request_intent_projection.summary",
            "schema_version": SCHEMA_VERSION,
            "mcp_request_intent_generated": True,
            "source_behavior_y_star_id": behavior.get("behavior_y_star_id"),
            "internal_only": True,
            "dry_run_only": True,
            "no_real_mcp_server": True,
            "no_real_tool_execution": True,
            "no_external_action": True,
            "safety_flags": SAFETY_FLAGS,
        },
    )
    write_text(
        INTENT / "mcp_request_intent_report.md",
        md(
            "MCP Request Intent Report",
            [
                "- Intent requests only a safe generated/read-model summary through a future governed MCP boundary.",
                "- External, network, raw runtime, writeback, and revenue operations are forbidden.",
            ],
        ),
    )

    write_json(PRE_U / "mcp_call_pre_u_packet_candidate.json", pre_u_packet)
    write_json(PRE_U / "mcp_pre_u_to_y_star_gov_expectation_map.json", pre_u_map)
    write_text(PRE_U / "mcp_pre_u_gap_report.md", pre_u_gap)
    write_json(PRE_U / "mcp_pre_u_summary.json", pre_u_summary)

    write_json(DECISION / "mcp_governance_decision_envelope.json", decision)
    write_json(DECISION / "mcp_decision_reason_trace.json", reason_trace)
    write_text(DECISION / "mcp_governance_decision_gap_report.md", decision_gap)
    write_json(DECISION / "mcp_governance_decision_summary.json", decision_summary)

    write_json(BRIDGE / "mcp_bridge_authorization_receipt.json", bridge_receipt)
    write_json(BRIDGE / "mcp_bridge_denied_scope.json", bridge_denied)
    write_json(BRIDGE / "mcp_bridge_receipt_summary.json", bridge_summary)
    write_text(BRIDGE / "mcp_bridge_receipt_report.md", bridge_report)

    write_json(CALL / "governed_mcp_call_candidate.json", call_candidate)
    write_json(CALL / "governed_mcp_call_execution_plan.json", call_plan)
    write_json(CALL / "mcp_real_execution_blocker.json", blocker)
    write_json(CALL / "governed_mcp_call_summary.json", call_summary)
    write_text(CALL / "governed_mcp_call_report.md", call_report)

    write_json(RECEIPT / "mcp_dry_run_receipt.json", receipt)
    write_json(RECEIPT / "mcp_cieu_event_fixture.json", cieu)
    write_json(RECEIPT / "mcp_predicted_outcome.json", predicted)
    write_json(RECEIPT / "mcp_mock_actual_outcome.json", mock_actual)
    write_json(RECEIPT / "mcp_receipt_cieu_summary.json", receipt_summary)
    write_text(RECEIPT / "mcp_receipt_cieu_report.md", receipt_report)

    write_json(RESIDUAL / "mcp_residual_delta.json", residual_delta)
    write_json(RESIDUAL / "mcp_residual_classification.json", residual_classification)
    write_json(RESIDUAL / "mcp_learning_candidate.json", learning_candidate)
    write_json(RESIDUAL / "mcp_review_queue_entry.json", review_queue)
    write_json(RESIDUAL / "mcp_residual_learning_summary.json", residual_summary)
    write_text(RESIDUAL / "mcp_residual_learning_report.md", residual_report)

    write_json(READINESS / "governed_mcp_adapter_readiness.json", readiness)
    write_text(READINESS / "governed_mcp_adapter_readiness.md", readiness_md)
    write_json(READINESS / "l5_7_recommended_next_step.json", recommendation)

    print("Governed MCP dry-run adapter artifacts generated.")
    print(f"- {rel(ADAPTER / 'governed_mcp_dry_run_adapter_summary.json')}")
    print(f"- {rel(READINESS / 'governed_mcp_adapter_readiness.json')}")


if __name__ == "__main__":
    build()
