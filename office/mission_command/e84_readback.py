from __future__ import annotations

import json
import os
import subprocess
from pathlib import Path
from typing import Any

from office.mission_command.e84_ystar_gov_ceo_cognitive_os_call_adapter import run_adapter_smoke


BRIDGE_ROOT = Path(os.environ.get("YSTAR_BRIDGE_LABS_ROOT", Path(__file__).resolve().parents[2]))
Y_GOV_ROOT = Path(os.environ.get("YSTAR_GOV_ROOT", "/Users/haotianliu/.openclaw/workspace/Y-star-gov"))
GOV_MCP_ROOT = Path(os.environ.get("GOV_MCP_ROOT", "/Users/haotianliu/.openclaw/workspace/gov-mcp"))
OUT_DIR = BRIDGE_ROOT / "operations" / "external_validation"

JOB_ID = "E84_YStarGov_GovMCP_BridgeLabs_Runtime_Interface_Audit_and_CEO_CognitiveOS_Hook_Wiring_R1"
EXPECTED_YSTAR_GOV_BASE = "e725b8721e348c4dd9834a265f73125f685a07a7"
EXPECTED_BRIDGE_BASE = "1680be9401b70a8701b15e83c04b8a8d642b2198"


REQUIRED_ARTIFACTS = [
    "operations/external_validation/e84_cieu_log_terminology_correction.json",
    "operations/external_validation/e84_cieu_log_terminology_correction.md",
    "operations/external_validation/e84_ystar_gov_runtime_topology_audit.json",
    "operations/external_validation/e84_ystar_gov_runtime_topology_audit.md",
    "operations/external_validation/e84_gov_mcp_runtime_topology_audit.json",
    "operations/external_validation/e84_gov_mcp_runtime_topology_audit.md",
    "operations/external_validation/e84_bridge_labs_ceo_packet_runtime_audit.json",
    "operations/external_validation/e84_bridge_labs_ceo_packet_runtime_audit.md",
    "operations/external_validation/e84_cross_repo_runtime_interface_map.json",
    "operations/external_validation/e84_cross_repo_runtime_interface_map.md",
    "operations/external_validation/e84_e83_implementation_correctness_audit.json",
    "operations/external_validation/e84_e83_implementation_correctness_audit.md",
    "operations/external_validation/e84_runtime_wiring_design.json",
    "operations/external_validation/e84_runtime_wiring_design.md",
    "operations/external_validation/e84_patch_result.json",
    "operations/external_validation/e84_patch_result.md",
    "operations/external_validation/e84_cieu_residual_for_runtime_interface_audit_and_wiring.json",
    "operations/external_validation/e84_cieu_residual_for_runtime_interface_audit_and_wiring.md",
    "operations/external_validation/e84_generated_next_milestone_proposal.json",
    "operations/external_validation/e84_generated_next_milestone_proposal.md",
    "operations/external_validation/e84_completion_report.json",
    "operations/external_validation/e84_completion_report.md",
]


def _git(args: list[str], cwd: Path) -> str:
    try:
        return subprocess.check_output(["git", *args], cwd=cwd, text=True, stderr=subprocess.DEVNULL).strip()
    except Exception:
        return "unavailable_nonfatal"


def _read(path: Path, limit: int = 160_000) -> str:
    try:
        if not path.exists() or path.is_dir():
            return ""
        return path.read_text(encoding="utf-8", errors="ignore")[:limit]
    except Exception:
        return ""


def _write_json(rel: str, data: Any) -> None:
    path = BRIDGE_ROOT / rel
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def _write_md(rel: str, title: str, lines: list[str]) -> None:
    path = BRIDGE_ROOT / rel
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("# " + title + "\n\n" + "\n".join(lines).rstrip() + "\n", encoding="utf-8")


def _repo_state() -> dict[str, Any]:
    return {
        "Y_star_gov_head": _git(["rev-parse", "HEAD"], Y_GOV_ROOT),
        "bridge_labs_head": _git(["rev-parse", "HEAD"], BRIDGE_ROOT),
        "gov_mcp_head": _git(["rev-parse", "HEAD"], GOV_MCP_ROOT) if (GOV_MCP_ROOT / ".git").exists() else "unavailable",
        "Y_star_gov_base_verified": _git(["rev-parse", "HEAD"], Y_GOV_ROOT) == EXPECTED_YSTAR_GOV_BASE,
        "bridge_labs_base_verified": _git(["rev-parse", "HEAD"], BRIDGE_ROOT) == EXPECTED_BRIDGE_BASE,
        "gov_mcp_available": (GOV_MCP_ROOT / ".git").exists(),
    }


def build_cieu_log_terminology_correction() -> dict[str, Any]:
    return {
        "artifact_id": "e84_cieu_log_terminology_correction",
        "job_id": JOB_ID,
        "forbidden_terms": ["CIEU-style trace"],
        "required_terms": ["CIEU log", "CIEU record", "CIEU validation record", "CIEU log candidate"],
        "E83_validator_output": "CIEU_validation_record_candidate",
        "formal_CIEU_log_write_status": "CIEU_log_write_deferred",
        "corrections": [
            "E83 validator creates a CIEU validation record candidate, not a formal CIEU log write.",
            "Formal CIEU log writing must use existing Y-star-gov CIEUStore or hook/OpenClaw auto-persist path, or K9Audit if ledger integration is separately approved.",
            "E84 may only claim CIEU log integration if actual code writes through that existing path.",
            "E84 does not make that claim; validator output remains a CIEU validation record candidate.",
        ],
    }


def build_ystar_gov_runtime_topology_audit() -> dict[str, Any]:
    nodes = [
        {
            "node_id": "ystar_public_api",
            "file_path": "ystar/__init__.py",
            "symbol": "check/enforce/IntentContract/CheckResult/EnforcementResult/check_hook exports",
            "layer": "public_api",
            "upstream_callers": ["package users", "gov-mcp"],
            "downstream_callees": ["ystar.kernel.engine", "ystar.adapters.hook", "ystar.governance"],
            "decision_vocabulary": ["passed", "violations", "enforcement modes"],
            "writes_CIEU_log": False,
            "builds_CIEU_validation_record_only": False,
            "runtime_path": True,
            "docs_tests_artifact_only": False,
            "CEO_Cognitive_OS_should_integrate_here": "no, export surface only",
            "evidence_path": "Y-star-gov:ystar/__init__.py",
            "confidence": "high",
        },
        {
            "node_id": "ystar_kernel_check_enforce",
            "file_path": "ystar/kernel/engine.py",
            "symbol": "check, enforce, CheckResult, EnforcementResult",
            "layer": "contract_check_enforce",
            "upstream_callers": ["gov-mcp gov_check/gov_enforce", "OpenClaw adapter"],
            "downstream_callees": ["IntentContract dimension checks"],
            "decision_vocabulary": ["ALLOW/DENY via passed", "LOG_ONLY", "HOLD_FOR_APPROVAL"],
            "writes_CIEU_log": False,
            "builds_CIEU_validation_record_only": False,
            "runtime_path": True,
            "docs_tests_artifact_only": False,
            "CEO_Cognitive_OS_should_integrate_here": "not directly; too low-level for CEO packet schema",
            "evidence_path": "Y-star-gov:ystar/kernel/engine.py",
            "confidence": "high",
        },
        {
            "node_id": "ystar_real_hook_runtime",
            "file_path": "ystar/adapters/hook.py",
            "symbol": "check_hook, _check_hook_full",
            "layer": "hook_runtime_path",
            "upstream_callers": ["Claude/OpenClaw PreToolUse hook"],
            "downstream_callees": ["ystar.domains.openclaw.adapter.enforce", "CIEUStore via cieu_writer", "auto_rewrite"],
            "decision_vocabulary": ["allow", "deny", "escalate", "redirect", "rewrite"],
            "writes_CIEU_log": True,
            "builds_CIEU_validation_record_only": False,
            "runtime_path": True,
            "docs_tests_artifact_only": False,
            "CEO_Cognitive_OS_should_integrate_here": "later hook runtime wiring, not patched in E84",
            "evidence_path": "Y-star-gov:ystar/adapters/hook.py",
            "confidence": "high",
        },
        {
            "node_id": "ystar_cieu_store",
            "file_path": "ystar/governance/cieu_store.py",
            "symbol": "CIEUStore.write, CIEUStore.write_dict",
            "layer": "CIEU_log_store",
            "upstream_callers": ["hook cieu_writer", "OpenClaw auto-persist", "other governance observers"],
            "downstream_callees": ["SQLite cieu_events table"],
            "decision_vocabulary": ["decision_canonical", "evidence_grade"],
            "writes_CIEU_log": True,
            "builds_CIEU_validation_record_only": False,
            "runtime_path": True,
            "docs_tests_artifact_only": False,
            "CEO_Cognitive_OS_should_integrate_here": "formal log write candidate for later E85, deferred now",
            "evidence_path": "Y-star-gov:ystar/governance/cieu_store.py",
            "confidence": "high",
        },
        {
            "node_id": "ystar_cieu_writer",
            "file_path": "ystar/adapters/cieu_writer.py",
            "symbol": "_write_cieu, _write_boot_record",
            "layer": "CIEU_log_writer_adapter",
            "upstream_callers": ["ystar.adapters.hook.check_hook"],
            "downstream_callees": ["CIEUStore.write_dict"],
            "decision_vocabulary": ["allow", "deny", "info"],
            "writes_CIEU_log": True,
            "builds_CIEU_validation_record_only": False,
            "runtime_path": True,
            "docs_tests_artifact_only": False,
            "CEO_Cognitive_OS_should_integrate_here": "not in E84; path is hook-specific",
            "evidence_path": "Y-star-gov:ystar/adapters/cieu_writer.py",
            "confidence": "high",
        },
        {
            "node_id": "ystar_hook_contract_dry_run",
            "file_path": "ystar/governance/hook_contract_adapter.py",
            "symbol": "run_hook_contract_dry_run",
            "layer": "hook_contract_dry_run",
            "upstream_callers": ["dry-run CLI", "tests"],
            "downstream_callees": ["run_governance_contract_dry_run"],
            "decision_vocabulary": ["allow", "warn", "require_revision", "deny", "escalate"],
            "writes_CIEU_log": False,
            "builds_CIEU_validation_record_only": False,
            "runtime_path": False,
            "docs_tests_artifact_only": False,
            "CEO_Cognitive_OS_should_integrate_here": "semantic interface precedent, not real hook",
            "evidence_path": "Y-star-gov:ystar/governance/hook_contract_adapter.py",
            "confidence": "high",
        },
        {
            "node_id": "ystar_ceo_cognitive_os_validator",
            "file_path": "ystar/governance/ceo_cognitive_os_contract.py",
            "symbol": "validate_ceo_pre_action_packet, validate_ceo_post_action_residual",
            "layer": "CEO_packet_governance_validation",
            "upstream_callers": ["bridge-labs E84 call adapter", "future hook/runtime wrapper"],
            "downstream_callees": ["deterministic validation rules"],
            "decision_vocabulary": ["ALLOW", "REQUIRE_REVISION", "DENY", "ESCALATE"],
            "writes_CIEU_log": False,
            "builds_CIEU_validation_record_only": True,
            "runtime_path": True,
            "docs_tests_artifact_only": False,
            "CEO_Cognitive_OS_should_integrate_here": "yes, bridge-labs should call this first",
            "evidence_path": "Y-star-gov:ystar/governance/ceo_cognitive_os_contract.py",
            "confidence": "high",
        },
    ]
    return {"artifact_id": "e84_ystar_gov_runtime_topology_audit", "job_id": JOB_ID, "nodes": nodes, "node_count": len(nodes)}


def build_gov_mcp_runtime_topology_audit() -> dict[str, Any]:
    available = (GOV_MCP_ROOT / ".git").exists()
    nodes = [
        {
            "node_id": "gov_mcp_server_registration",
            "file_path": "gov_mcp/server.py",
            "symbol": "create_server, gov_check, gov_enforce",
            "layer": "server_registration",
            "input_schema": "agent_id, tool_name, params",
            "output_schema": "JSON decision envelope",
            "decision_values": ["ALLOW", "DENY"],
            "can_consume_Y_star_gov_decision": True,
            "can_return_REQUIRE_REVISION_guidance": False,
            "writes_receipts": False,
            "executes_provider_action": "only deterministic Bash auto-exec; provider execution is separate outbound layer",
            "CEO_Cognitive_OS_should_integrate_here": "later, only after Y-star-gov allows/scopes provider/tool execution",
            "evidence_path": "gov-mcp:gov_mcp/server.py",
            "confidence": "high" if available else "unavailable",
        },
        {
            "node_id": "gov_mcp_company_preflight",
            "file_path": "gov_mcp/company_runtime_tools.py",
            "symbol": "gov_company_action_preflight, gov_company_mission_action_preflight",
            "layer": "governance_check",
            "input_schema": "company action dict and optional mission dict",
            "output_schema": "classification/preflight result with external_action_executed false",
            "decision_values": ["ok", "needs_budget", "escalation options"],
            "can_consume_Y_star_gov_decision": "planned",
            "can_return_REQUIRE_REVISION_guidance": "not directly",
            "writes_receipts": False,
            "executes_provider_action": False,
            "CEO_Cognitive_OS_should_integrate_here": "later L4/L5 company-action preflight",
            "evidence_path": "gov-mcp:gov_mcp/company_runtime_tools.py",
            "confidence": "high" if available else "unavailable",
        },
        {
            "node_id": "gov_mcp_outbound_policy",
            "file_path": "gov_mcp/outbound/policy.py",
            "symbol": "evaluate_outbound_policy",
            "layer": "provider_boundary",
            "input_schema": "OutboundActionIntent",
            "output_schema": "OutboundPreflightResult",
            "decision_values": ["deny", "send_gated_pending_authorization", "gov_mcp_execute_after_activation"],
            "can_consume_Y_star_gov_decision": "planned",
            "can_return_REQUIRE_REVISION_guidance": "no, policy returns reason codes",
            "writes_receipts": False,
            "executes_provider_action": False,
            "CEO_Cognitive_OS_should_integrate_here": "after CEO packet ALLOW and owner activation",
            "evidence_path": "gov-mcp:gov_mcp/outbound/policy.py",
            "confidence": "high" if available else "unavailable",
        },
        {
            "node_id": "gov_mcp_dry_run_adapter",
            "file_path": "gov_mcp/outbound/dry_run_adapter.py",
            "symbol": "dry_run_outbound_action",
            "layer": "dry_run",
            "input_schema": "OutboundActionIntent",
            "output_schema": "no-send receipt",
            "decision_values": ["dry_run_denied", "dry_run_completed"],
            "can_consume_Y_star_gov_decision": "planned",
            "can_return_REQUIRE_REVISION_guidance": "no, receipt reason codes only",
            "writes_receipts": True,
            "executes_provider_action": False,
            "CEO_Cognitive_OS_should_integrate_here": "L4/L5 no-send rehearsal after Y-star-gov ALLOW/ESCALATE closure",
            "evidence_path": "gov-mcp:gov_mcp/outbound/dry_run_adapter.py",
            "confidence": "high" if available else "unavailable",
        },
        {
            "node_id": "gov_mcp_provider_guard_stack",
            "file_path": "gov_mcp/outbound/provider_guard_stack.py",
            "symbol": "evaluate_provider_guard_stack",
            "layer": "provider_boundary",
            "input_schema": "ProviderExecutionRequest and provider manifest",
            "output_schema": "allowed_for_live_execution and reason_codes",
            "decision_values": ["allowed_for_live_execution true/false"],
            "can_consume_Y_star_gov_decision": "planned",
            "can_return_REQUIRE_REVISION_guidance": "no, guard reason codes only",
            "writes_receipts": False,
            "executes_provider_action": False,
            "CEO_Cognitive_OS_should_integrate_here": "only after future approved provider execution boundary",
            "evidence_path": "gov-mcp:gov_mcp/outbound/provider_guard_stack.py",
            "confidence": "high" if available else "unavailable",
        },
    ]
    return {
        "artifact_id": "e84_gov_mcp_runtime_topology_audit",
        "job_id": JOB_ID,
        "gov_mcp_available": available,
        "nodes": nodes if available else [],
        "node_count": len(nodes) if available else 0,
        "blocker": None if available else "gov_mcp_code_unavailable_for_required_E84_audit",
        "gov_mcp_mutated": False,
    }


def build_bridge_labs_ceo_packet_runtime_audit() -> dict[str, Any]:
    nodes = [
        {
            "node_id": "bridge_e81_pre_sync_validator",
            "file_path": "office/mission_command/e81_ceo_cognitive_os_preflight_validator.py",
            "symbol": "validate_pre_action_packet, validate_post_action_residual",
            "role": "packet_validator",
            "input_schema": "E81 pre-action packet and post-action residual",
            "output_schema": "bridge-labs ALLOW/DENY result",
            "does_call_Y_star_gov": False,
            "only_records_generated_artifacts": False,
            "can_route_REQUIRE_REVISION_guidance_back_to_CEO": "not before E84",
            "can_route_ESCALATE_to_owner_decision_packet": "limited local DENY only",
            "can_block_execution": True,
            "evidence_path": "bridge-labs:office/mission_command/e81_ceo_cognitive_os_preflight_validator.py",
            "confidence": "high",
        },
        {
            "node_id": "bridge_e84_call_adapter",
            "file_path": "office/mission_command/e84_ystar_gov_ceo_cognitive_os_call_adapter.py",
            "symbol": "validate_pre_action_with_ystar_gov, validate_post_action_with_ystar_gov",
            "role": "packet_validator_call_adapter",
            "input_schema": "CEO pre-action packet or post-action residual",
            "output_schema": "Y-star-gov decision plus bridge-labs route",
            "does_call_Y_star_gov": True,
            "only_records_generated_artifacts": False,
            "can_route_REQUIRE_REVISION_guidance_back_to_CEO": True,
            "can_route_ESCALATE_to_owner_decision_packet": True,
            "can_block_execution": True,
            "evidence_path": "bridge-labs:office/mission_command/e84_ystar_gov_ceo_cognitive_os_call_adapter.py",
            "confidence": "high",
        },
        {
            "node_id": "bridge_ceo_brain_adapter",
            "file_path": "office/mission_command/e46b_ceo_brain_adapter.py",
            "symbol": "load_ceo_brain_context",
            "role": "readback",
            "input_schema": "task dict",
            "output_schema": "CEO brain readback context",
            "does_call_Y_star_gov": False,
            "only_records_generated_artifacts": False,
            "can_route_REQUIRE_REVISION_guidance_back_to_CEO": "readback after E84",
            "can_route_ESCALATE_to_owner_decision_packet": "readback after E84",
            "can_block_execution": False,
            "evidence_path": "bridge-labs:office/mission_command/e46b_ceo_brain_adapter.py",
            "confidence": "high",
        },
        {
            "node_id": "bridge_e81_schemas",
            "file_path": "operations/external_validation/e81_ceo_mandatory_pre_action_packet_schema.json",
            "symbol": "mandatory pre-action packet schema",
            "role": "generated_artifact",
            "input_schema": "none",
            "output_schema": "minimum fields and CIEU prediction fields",
            "does_call_Y_star_gov": False,
            "only_records_generated_artifacts": True,
            "can_route_REQUIRE_REVISION_guidance_back_to_CEO": False,
            "can_route_ESCALATE_to_owner_decision_packet": False,
            "can_block_execution": False,
            "evidence_path": "bridge-labs:operations/external_validation/e81_ceo_mandatory_pre_action_packet_schema.json",
            "confidence": "high",
        },
    ]
    return {"artifact_id": "e84_bridge_labs_ceo_packet_runtime_audit", "job_id": JOB_ID, "nodes": nodes, "node_count": len(nodes)}


def build_cross_repo_runtime_interface_map() -> dict[str, Any]:
    edges = [
        {
            "edge_id": "bridge_packet_to_ystar_validator",
            "source_repo": "bridge-labs",
            "source_function_or_artifact": "office/mission_command/e84_ystar_gov_ceo_cognitive_os_call_adapter.py",
            "target_repo": "Y-star-gov",
            "target_function_or_artifact": "ystar.governance.validate_ceo_pre_action_packet",
            "data_passed": "CEO mandatory pre-action packet",
            "decision_semantics": ["ALLOW", "REQUIRE_REVISION", "DENY", "ESCALATE"],
            "current_status": "implemented",
            "correct_next_step": "use adapter for bridge-labs CEO major-action preflight",
        },
        {
            "edge_id": "bridge_residual_to_ystar_validator",
            "source_repo": "bridge-labs",
            "source_function_or_artifact": "office/mission_command/e84_ystar_gov_ceo_cognitive_os_call_adapter.py",
            "target_repo": "Y-star-gov",
            "target_function_or_artifact": "ystar.governance.validate_ceo_post_action_residual",
            "data_passed": "CEO post-action residual",
            "decision_semantics": ["ALLOW", "REQUIRE_REVISION", "DENY"],
            "current_status": "implemented",
            "correct_next_step": "require post-action residual validation after future action outputs",
        },
        {
            "edge_id": "ystar_validator_to_cieu_log",
            "source_repo": "Y-star-gov",
            "source_function_or_artifact": "ystar/governance/ceo_cognitive_os_contract.py",
            "target_repo": "Y-star-gov",
            "target_function_or_artifact": "ystar/governance/cieu_store.py",
            "data_passed": "CIEU validation record candidate",
            "decision_semantics": ["candidate only"],
            "current_status": "planned",
            "correct_next_step": "E85 targeted CIEU log write integration if owner approves and tests prove exact write path",
        },
        {
            "edge_id": "ystar_allow_to_gov_mcp_provider_envelope",
            "source_repo": "Y-star-gov",
            "source_function_or_artifact": "validate_ceo_pre_action_packet",
            "target_repo": "gov-mcp",
            "target_function_or_artifact": "gov_mcp.outbound.dry_run_adapter / provider_guard_stack",
            "data_passed": "approved and scoped provider/tool action envelope",
            "decision_semantics": ["gov-mcp deny/send_gated_pending_authorization/gov_mcp_execute_after_activation"],
            "current_status": "planned",
            "correct_next_step": "do not mutate gov-mcp until explicit base approval; use it only after Y-star-gov ALLOW and owner scope",
        },
    ]
    return {
        "artifact_id": "e84_cross_repo_runtime_interface_map",
        "job_id": JOB_ID,
        "responsibilities": {
            "bridge_labs": ["CEO packet producer", "business artifacts", "owner decision packet", "readback", "post-action residual producer"],
            "Y_star_gov": ["canonical CEO Cognitive OS validation", "owner approval governance", "CIEU log path when safely wired"],
            "gov_mcp": ["provider/tool execution envelope", "dry-run/provider promotion/receipt path"],
            "K9Audit": ["CIEU ledger/verifier owner if used directly"],
        },
        "edges": edges,
    }


def build_e83_correctness_audit() -> dict[str, Any]:
    return {
        "artifact_id": "e84_e83_implementation_correctness_audit",
        "job_id": JOB_ID,
        "decision": "correct_but_needs_bridge_labs_call_adapter",
        "answers": {
            "E83_validator_right_YstarGov_layer": True,
            "REQUIRE_REVISION_aligned_with_existing_YstarGov_semantics": True,
            "validator_only_builds_CIEU_validation_record_not_formal_log": True,
            "formal_CIEU_log_write_path_if_later_implemented": "Y-star-gov CIEUStore.write/write_dict or hook/OpenClaw auto-persist path; K9Audit only if separately approved",
            "bridge_labs_called_YstarGov_before_E84": False,
            "bridge_labs_calls_YstarGov_after_E84": True,
            "gov_mcp_needs_CEO_Cognitive_OS_now": False,
            "missing_interface_before_E84": "bridge-labs call adapter from CEO packet producer to Y-star-gov validator",
            "E84_patch": "implemented bridge-labs call adapter; no Y-star-gov hook rewrite; no formal CIEU log write",
        },
    }


def build_runtime_wiring_design() -> dict[str, Any]:
    return {
        "artifact_id": "e84_runtime_wiring_design",
        "job_id": JOB_ID,
        "flow": [
            {"step": 1, "description": "bridge-labs CEO proposes major action", "existing_module": "CEO milestone/runtime artifacts", "patch_required": False},
            {"step": 2, "description": "bridge-labs produces mandatory pre-action packet", "existing_module": "E81 schema/artifacts", "patch_required": False},
            {"step": 3, "description": "bridge-labs calls Y-star-gov validator", "existing_module": "e84_ystar_gov_ceo_cognitive_os_call_adapter.validate_pre_action_with_ystar_gov", "patch_required": True, "patch_status": "implemented"},
            {"step": 4, "description": "Y-star-gov returns ALLOW/REQUIRE_REVISION/DENY/ESCALATE", "existing_module": "ystar.governance.validate_ceo_pre_action_packet", "patch_required": False},
            {"step": 5, "description": "bridge-labs routes result", "existing_module": "E84 call adapter route map", "patch_required": True, "patch_status": "implemented"},
            {"step": 6, "description": "future provider/tool execution uses gov-mcp envelope after Y-star-gov allow/scope", "existing_module": "gov-mcp outbound/dry_run/provider_guard_stack", "patch_required": False, "status": "planned_read_only"},
            {"step": 7, "description": "bridge-labs produces post-action residual", "existing_module": "E81 post-action schema", "patch_required": False},
            {"step": 8, "description": "Y-star-gov validates post-action residual", "existing_module": "e84 adapter + validate_ceo_post_action_residual", "patch_required": True, "patch_status": "implemented"},
            {"step": 9, "description": "formal CIEU log write", "existing_module": "Y-star-gov CIEUStore / hook cieu_writer", "patch_required": True, "patch_status": "deferred"},
        ],
        "routing": {
            "ALLOW": "continue_to_approved_next_step_without_external_execution",
            "REQUIRE_REVISION": "return_correct_path_guidance_to_CEO",
            "ESCALATE": "generate_owner_decision_packet_no_execution",
            "DENY": "block_execution_and_record_residual",
        },
        "formal_CIEU_log_write_status": "CIEU_log_write_deferred",
    }


def build_patch_result() -> dict[str, Any]:
    smoke = run_adapter_smoke()
    return {
        "artifact_id": "e84_patch_result",
        "job_id": JOB_ID,
        "patch_made": True,
        "Y_star_gov_modified": False,
        "bridge_labs_modified": True,
        "gov_mcp_modified": False,
        "patch_type": "bridge_labs_call_adapter",
        "files_created": ["office/mission_command/e84_ystar_gov_ceo_cognitive_os_call_adapter.py", "office/mission_command/e84_readback.py", "tests/office/test_e84_runtime_interfaces.py"],
        "files_modified": ["office/mission_command/e46b_ceo_brain_adapter.py"],
        "formal_CIEU_log_write_implemented": False,
        "formal_CIEU_log_write_status": "CIEU_log_write_deferred",
        "validator_output_status": "CIEU_validation_record_candidate_only",
        "adapter_smoke": smoke,
    }


def build_cieu_residual() -> dict[str, Any]:
    return {
        "artifact_id": "e84_cieu_residual_for_runtime_interface_audit_and_wiring",
        "job_id": JOB_ID,
        "X_t": {
            "E83_corrected_auto_guidance_semantics": True,
            "owner_rejected_invented_CIEU_trace_terminology": True,
            "correct_interfaces_required_before_next_patch": True,
            "no_external_action_boundary": True,
        },
        "U_t": {
            "audited_Y_star_gov_runtime_topology": True,
            "audited_gov_mcp_runtime_topology": _repo_state()["gov_mcp_available"],
            "audited_bridge_labs_CEO_packet_runtime": True,
            "mapped_cross_repo_interfaces": True,
            "audited_E83_correctness": True,
            "implemented_patch": "bridge_labs_call_adapter_only",
        },
        "Y_star_t": {
            "intended_outcome": "use correct CIEU log terminology, attach CEO Cognitive OS through existing interfaces, avoid duplicate wheels, define correct L4/L5 path",
            "constraints": ["no external action", "no gov-mcp mutation", "no fake CIEU log write", "no L4/L5 claims"],
        },
        "Y_t_plus_1": {
            "topology_audits": "generated",
            "interface_map": "generated",
            "correctness_decision": "correct_but_needs_bridge_labs_call_adapter",
            "patch_result": "bridge_labs_call_adapter_implemented",
            "tests": "targeted E84 tests added",
        },
        "R_t_plus_1": {
            "residual_gaps": [
                "hook/runtime wiring remains",
                "formal CIEU log write deferred",
                "gov-mcp remains read-only and unwired",
                "L4 not executed",
                "L5 not ready",
                "customer/paid/pricing/compliance validation absent",
            ]
        },
    }


def build_next_milestone() -> dict[str, Any]:
    return {
        "artifact_id": "e84_generated_next_milestone_proposal",
        "job_id": JOB_ID,
        "next_recommended_milestone": "E85_YStarGov_CEO_Cognitive_OS_Hook_Runtime_Wiring_R1",
        "type": "targeted_hook_runtime_wiring",
        "why": "bridge-labs can now call the canonical Y-star-gov validator, while real hook/runtime wiring and formal CIEU log writes remain intentionally deferred.",
        "not_recommended": ["broad inventory", "generic construction", "generic L3 research", "mass outreach", "publication", "L5 revenue"],
    }


def build_completion_report() -> dict[str, Any]:
    state = _repo_state()
    patch = build_patch_result()
    return {
        "artifact_id": "e84_completion_report",
        "job_id": JOB_ID,
        "Y_star_gov_base_verified": state["Y_star_gov_base_verified"],
        "bridge_labs_base_verified": state["bridge_labs_base_verified"],
        "gov_mcp_availability": "available_read_only" if state["gov_mcp_available"] else "unavailable",
        "modified_repos": ["bridge-labs"],
        "verified_base_hashes": {"Y_star_gov": state["Y_star_gov_head"], "bridge_labs": state["bridge_labs_head"]},
        "final_hashes": {
            "Y_star_gov": state["Y_star_gov_head"],
            "bridge_labs": "reported_by_repository_delivery_bridge_after_commit",
        },
        "bridge_labs_final_hash_reporting": "owner_final_report_and_delivery_bridge_report",
        "Y_star_gov_runtime_topology_summary": "real hook runtime and CIEUStore write paths exist; CEO validator returns validation record candidate only",
        "gov_mcp_topology_summary": "gov_check/gov_enforce and outbound dry-run/provider guard/receipt paths exist; gov-mcp remains future execution envelope",
        "bridge_labs_packet_runtime_summary": "E84 call adapter now invokes Y-star-gov validator and routes decisions without executing external action",
        "cross_repo_interface_map_summary": "bridge-labs produces packets; Y-star-gov validates; gov-mcp executes only later after approval/scope; K9Audit remains ledger/verifier owner",
        "CIEU_terminology_correction": "validator output is CIEU validation record candidate, not formal CIEU log write",
        "formal_CIEU_log_write_status": "CIEU_log_write_deferred",
        "validator_output_remains_CIEU_validation_record_only": True,
        "E83_correctness_decision": "correct_but_needs_bridge_labs_call_adapter",
        "patch_result": patch,
        "next_recommended_milestone": build_next_milestone()["next_recommended_milestone"],
        "safety_statement": {
            "no_external_action": True,
            "no_outreach": True,
            "no_publication": True,
            "no_payment": True,
            "no_provider_live_execution": True,
            "no_live_MCP_execution": True,
            "no_customer_validation_claim": True,
            "no_expert_validation_claim": True,
            "no_paid_signal_claim": True,
            "no_pricing_validation_claim": True,
            "no_compliance_legal_claim": True,
            "no_production_deployment_claim": True,
            "no_L4_execution_claim": True,
            "no_L5_readiness_claim": True,
            "gov_mcp_mutated": False,
            "K9Audit_mutated": False,
            "ystar_company_mutated": False,
            "no_duplicate_governance_engine": True,
        },
    }


def load_e84_runtime_interface_state_for_brain() -> dict[str, Any]:
    report_path = OUT_DIR / "e84_completion_report.json"
    if report_path.exists():
        data = json.loads(report_path.read_text(encoding="utf-8"))
    else:
        data = build_completion_report()
    patch = data.get("patch_result", {})
    return {
        "E84_status": "runtime_interface_audited_bridge_labs_call_adapter_active",
        "gov_mcp_available": data.get("gov_mcp_availability") == "available_read_only",
        "formal_CIEU_log_write_status": data.get("formal_CIEU_log_write_status"),
        "validator_output_status": "CIEU_validation_record_candidate_only",
        "E83_correctness_decision": data.get("E83_correctness_decision"),
        "patch_type": patch.get("patch_type"),
        "bridge_labs_call_adapter_active": patch.get("patch_type") == "bridge_labs_call_adapter",
        "Y_star_gov_modified_in_E84": bool(patch.get("Y_star_gov_modified")),
        "gov_mcp_modified_in_E84": bool(patch.get("gov_mcp_modified")),
        "decision_routing": build_runtime_wiring_design()["routing"],
        "next_recommended_milestone": data.get("next_recommended_milestone"),
        "external_action_allowed": False,
        "L4_execution_authorized": False,
        "L5_ready": False,
    }


def generate_e84_artifacts() -> None:
    artifacts = {
        "e84_cieu_log_terminology_correction": build_cieu_log_terminology_correction(),
        "e84_ystar_gov_runtime_topology_audit": build_ystar_gov_runtime_topology_audit(),
        "e84_gov_mcp_runtime_topology_audit": build_gov_mcp_runtime_topology_audit(),
        "e84_bridge_labs_ceo_packet_runtime_audit": build_bridge_labs_ceo_packet_runtime_audit(),
        "e84_cross_repo_runtime_interface_map": build_cross_repo_runtime_interface_map(),
        "e84_e83_implementation_correctness_audit": build_e83_correctness_audit(),
        "e84_runtime_wiring_design": build_runtime_wiring_design(),
        "e84_patch_result": build_patch_result(),
        "e84_cieu_residual_for_runtime_interface_audit_and_wiring": build_cieu_residual(),
        "e84_generated_next_milestone_proposal": build_next_milestone(),
        "e84_completion_report": build_completion_report(),
    }
    for name, payload in artifacts.items():
        _write_json(f"operations/external_validation/{name}.json", payload)
        lines = [
            f"- artifact_id: `{payload.get('artifact_id', name)}`",
            f"- job_id: `{JOB_ID}`",
        ]
        if name == "e84_completion_report":
            lines.extend(
                [
                    f"- gov_mcp_availability: `{payload['gov_mcp_availability']}`",
                    f"- E83_correctness_decision: `{payload['E83_correctness_decision']}`",
                    f"- formal_CIEU_log_write_status: `{payload['formal_CIEU_log_write_status']}`",
                    f"- next_recommended_milestone: `{payload['next_recommended_milestone']}`",
                ]
            )
        if name == "e84_patch_result":
            lines.extend(
                [
                    f"- patch_type: `{payload['patch_type']}`",
                    f"- formal_CIEU_log_write_status: `{payload['formal_CIEU_log_write_status']}`",
                ]
            )
        _write_md(f"operations/external_validation/{name}.md", name.replace("_", " ").title(), lines)


if __name__ == "__main__":
    generate_e84_artifacts()
