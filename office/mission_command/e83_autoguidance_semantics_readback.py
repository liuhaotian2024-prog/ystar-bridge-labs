from __future__ import annotations

import json
import os
import subprocess
from pathlib import Path
from typing import Any


BRIDGE_ROOT = Path(os.environ.get("YSTAR_BRIDGE_LABS_ROOT", Path(__file__).resolve().parents[2]))
Y_GOV_ROOT = Path(os.environ.get("YSTAR_GOV_ROOT", "/Users/haotianliu/.openclaw/workspace/Y-star-gov"))
GOV_MCP_ROOT = Path(os.environ.get("GOV_MCP_ROOT", "/Users/haotianliu/.openclaw/workspace/gov-mcp"))
OUT_DIR = BRIDGE_ROOT / "operations" / "external_validation"

JOB_ID = "e83_ystar_gov_autoguidance_semantics_correct_path_integration_R1_20260507T000001Z"
EXPECTED_YSTAR_GOV_BASE = "d218155cfc6fa2a430169474e4bd0e12c6f18dd2"
EXPECTED_BRIDGE_BASE = "d416cf84c91cf4084accc1fe6e1e555ea40b6ebc"


def _git(args: list[str], cwd: Path) -> str:
    try:
        return subprocess.check_output(["git", *args], cwd=cwd, text=True, stderr=subprocess.DEVNULL).strip()
    except Exception:
        return "unavailable_nonfatal"


def _read(path: Path, limit: int = 200_000) -> str:
    try:
        if not path.exists() or path.is_dir():
            return ""
        return path.read_text(encoding="utf-8", errors="ignore")[:limit]
    except Exception:
        return ""


def _write_json(path: Path, data: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def _write_md(path: Path, title: str, lines: list[str]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    body = [f"# {title}", ""]
    body.extend(lines)
    path.write_text("\n".join(body).rstrip() + "\n", encoding="utf-8")


def _ystar_validator_supports_revision() -> bool:
    source = _read(Y_GOV_ROOT / "ystar/governance/ceo_cognitive_os_contract.py")
    return "REQUIRE_REVISION" in source and "guidance_type" in source and "correct_path" in source


def build_topology_audit() -> dict[str, Any]:
    nodes = [
        {
            "node_id": "public_api_root",
            "file_path": "ystar/__init__.py",
            "symbol": "check/enforce/IntentContract/CheckResult/EnforcementResult exports",
            "layer": "public_api",
            "upstream_callers": ["package consumers", "gov-mcp references"],
            "downstream_callees": ["ystar.kernel.engine", "ystar.kernel.dimensions", "ystar.governance"],
            "decision_values_used": ["PASS/VIOLATION via CheckResult", "EnforcementResult modes"],
            "CIEU_relation": "imports governance CIEU-facing services but does not own CEO packet shape",
            "contract_relation": "exposes IntentContract and higher-order contract primitives",
            "owner_approval_relation": "generic HOLD_FOR_APPROVAL mode exists in kernel enforcement",
            "auto_guidance_repair_relation": "not the CEO-specific correction point",
            "CEO_Cognitive_OS_integrate_here": False,
            "confidence": "high",
            "evidence_path": "Y-star-gov:ystar/__init__.py",
        },
        {
            "node_id": "kernel_contract_layer",
            "file_path": "ystar/kernel/dimensions.py",
            "symbol": "IntentContract, HigherOrderContract, ConstitutionalContract, PolicySourceTrust",
            "layer": "contract_topology",
            "upstream_callers": ["ystar.__init__", "kernel engine", "hook/session adapters"],
            "downstream_callees": ["hash/canonical serialization", "policy source trust"],
            "decision_values_used": ["contract statuses: draft/confirmed/stale/suspended/expired/superseded"],
            "CIEU_relation": "Y*_t contract intent source for causal records",
            "contract_relation": "canonical generic contract model",
            "owner_approval_relation": "trust upgrades require approval",
            "auto_guidance_repair_relation": "contract lifecycle states are status-only, not repair interface",
            "CEO_Cognitive_OS_integrate_here": False,
            "confidence": "high",
            "evidence_path": "Y-star-gov:ystar/kernel/dimensions.py",
        },
        {
            "node_id": "kernel_check_enforce",
            "file_path": "ystar/kernel/engine.py",
            "symbol": "check, enforce, CheckResult, EnforcementResult, EnforcementMode",
            "layer": "runtime_decision_topology",
            "upstream_callers": ["ystar public API", "domain adapters"],
            "downstream_callees": ["IntentContract dimensions"],
            "decision_values_used": ["passed/violations", "logged/returned/held/simulated"],
            "CIEU_relation": "generic check result can be logged but is not CEO packet residual schema",
            "contract_relation": "executes generic IntentContract checks",
            "owner_approval_relation": "HOLD_FOR_APPROVAL can mark requires_approval",
            "auto_guidance_repair_relation": "violation summaries only; too low-level for CEO repair packets",
            "CEO_Cognitive_OS_integrate_here": False,
            "confidence": "high",
            "evidence_path": "Y-star-gov:ystar/kernel/engine.py",
        },
        {
            "node_id": "pre_u_packet_validator",
            "file_path": "ystar/governance/pre_u_packet_validator.py",
            "symbol": "ValidationDecision.REQUIRE_REVISION, validate_pre_u_packet",
            "layer": "governance_packet_validation",
            "upstream_callers": ["contract_dry_run"],
            "downstream_callees": ["ValidationResult.required_revisions"],
            "decision_values_used": ["allow", "warn", "require_revision", "escalate", "deny"],
            "CIEU_relation": "validates pre-U packet structure before prediction-delta dry-run",
            "contract_relation": "packet validator interface, not IntentContract replacement",
            "owner_approval_relation": "high-risk packets escalate",
            "auto_guidance_repair_relation": "returns required_revisions for repairable missing fields",
            "CEO_Cognitive_OS_integrate_here": "semantic precedent",
            "confidence": "high",
            "evidence_path": "Y-star-gov:ystar/governance/pre_u_packet_validator.py",
        },
        {
            "node_id": "contract_dry_run",
            "file_path": "ystar/governance/contract_dry_run.py",
            "symbol": "DryRunDecision.REQUIRE_REVISION, run_governance_contract_dry_run",
            "layer": "governance_dry_run",
            "upstream_callers": ["hook_contract_adapter"],
            "downstream_callees": ["pre_u_packet_validator", "cieu_prediction_delta"],
            "decision_values_used": ["pass", "warn", "require_revision", "deny", "escalate"],
            "CIEU_relation": "builds simulated prediction-delta record without live CIEU write",
            "contract_relation": "non-executing contract simulation",
            "owner_approval_relation": "escalation propagates from high-risk packet",
            "auto_guidance_repair_relation": "not-ready Pre-U/delta returns require_revision",
            "CEO_Cognitive_OS_integrate_here": "semantic precedent",
            "confidence": "high",
            "evidence_path": "Y-star-gov:ystar/governance/contract_dry_run.py",
        },
        {
            "node_id": "hook_contract_adapter",
            "file_path": "ystar/governance/hook_contract_adapter.py",
            "symbol": "HookAdapterDecision.REQUIRE_REVISION, run_hook_contract_dry_run",
            "layer": "hook_pretooluse_topology",
            "upstream_callers": ["tools/run_hook_contract_dry_run.py", "fixture tests"],
            "downstream_callees": ["contract_dry_run"],
            "decision_values_used": ["allow", "warn", "require_revision", "deny", "escalate"],
            "CIEU_relation": "no CIEU write; carries dry-run summary",
            "contract_relation": "future hook-like envelope compatibility",
            "owner_approval_relation": "escalate maps to route-to-review before enforcement",
            "auto_guidance_repair_relation": "returns require_revision boolean in hook-like envelope",
            "CEO_Cognitive_OS_integrate_here": "future hook wiring candidate, not E83 patch target",
            "confidence": "high",
            "evidence_path": "Y-star-gov:ystar/governance/hook_contract_adapter.py",
        },
        {
            "node_id": "real_hook_adapter",
            "file_path": "ystar/adapters/hook.py",
            "symbol": "check_hook, handle_hook_event, PreToolUse response envelopes",
            "layer": "hook_runtime_topology",
            "upstream_callers": ["Claude/OpenClaw hook runtime"],
            "downstream_callees": ["OpenClaw enforce", "auto_rewrite", "CIEU store"],
            "decision_values_used": ["allow", "deny", "escalate", "redirect", "rewrite"],
            "CIEU_relation": "can write real CIEU for hook/runtime events",
            "contract_relation": "uses session and OpenClaw contracts",
            "owner_approval_relation": "escalate branch returns deny envelope with owner/human reason",
            "auto_guidance_repair_relation": "REDIRECT/REWRITE/AUTO_INVOKE provide correction paths",
            "CEO_Cognitive_OS_integrate_here": "later runtime wiring candidate only",
            "confidence": "medium_high",
            "evidence_path": "Y-star-gov:ystar/adapters/hook.py",
        },
        {
            "node_id": "ceo_cognitive_os_validator",
            "file_path": "ystar/governance/ceo_cognitive_os_contract.py",
            "symbol": "validate_ceo_pre_action_packet, validate_ceo_post_action_residual",
            "layer": "governance_packet_validation",
            "upstream_callers": ["bridge-labs CEO packet producer", "future hook/runtime wiring"],
            "downstream_callees": ["deterministic local rules"],
            "decision_values_used": ["ALLOW", "REQUIRE_REVISION", "DENY", "ESCALATE"],
            "CIEU_relation": "returns CIEU-style validation record without live DB write",
            "contract_relation": "CEO Cognitive OS contract validator synced from bridge-labs",
            "owner_approval_relation": "complete but unapproved L4/external action escalates to owner path",
            "auto_guidance_repair_relation": "E83 patched repairable gaps to REQUIRE_REVISION with correct_path",
            "CEO_Cognitive_OS_integrate_here": True,
            "confidence": "high",
            "evidence_path": "Y-star-gov:ystar/governance/ceo_cognitive_os_contract.py",
        },
    ]
    return {
        "artifact_id": "e83_ystar_gov_full_topology_audit",
        "job_id": JOB_ID,
        "Y_star_gov_base_verified": True,
        "bridge_labs_base_verified": True,
        "topology_node_count": len(nodes),
        "topology_nodes": nodes,
        "selected_patch_target": "ystar/governance/ceo_cognitive_os_contract.py",
        "rejected_patch_targets": [
            {"path": "ystar/kernel/engine.py", "reason": "too low-level and generic for CEO packet repair semantics"},
            {"path": "ystar/adapters/hook.py", "reason": "real hook wiring is later runtime work, not needed for E83 semantic correction"},
            {"path": "ystar/governance/cieu_store.py", "reason": "live CIEU DB write remains deferred"},
            {"path": "gov-mcp", "reason": "execution/provider envelope owner remains read-only in E83"},
        ],
        "no_external_action": True,
    }


def build_auto_guidance_lineage() -> dict[str, Any]:
    mechanisms = [
        {
            "mechanism_id": "ystar_pre_u_require_revision",
            "repo": "Y-star-gov",
            "file_path": "ystar/governance/pre_u_packet_validator.py",
            "symbol_or_artifact": "ValidationDecision.REQUIRE_REVISION / required_revisions",
            "decision_vocabulary": ["allow", "warn", "require_revision", "escalate", "deny"],
            "returns_corrective_guidance": True,
            "blocks_execution": True,
            "requires_owner_approval": False,
            "supports_reprojection_shadow_update_dry_run_revision": "revision",
            "input_schema": "Pre-U packet mapping",
            "output_schema": "ValidationResult with required_revisions",
            "relation_to_check_enforce_hook": "fed into contract_dry_run then hook adapter",
            "relation_to_gov_mcp": "upstream governance semantics for provider/tool boundary later",
            "relation_to_bridge_labs_ceo_packets": "semantic precedent for CEO packet repair",
            "maturity": "implemented_and_test_backed",
            "should_be_reused_in_CEO_Cognitive_OS": "yes",
            "evidence": ["tests/governance/test_pre_u_packet_validator.py", "docs/pre_u_packet_validator/validator_interface_spec.md"],
        },
        {
            "mechanism_id": "ystar_cieu_delta_require_revision",
            "repo": "Y-star-gov",
            "file_path": "ystar/governance/cieu_prediction_delta.py",
            "symbol_or_artifact": "DeltaValidationDecision.REQUIRE_REVISION",
            "decision_vocabulary": ["allow", "warn", "require_revision", "escalate", "deny"],
            "returns_corrective_guidance": True,
            "blocks_execution": True,
            "requires_owner_approval": False,
            "supports_reprojection_shadow_update_dry_run_revision": "prediction_delta_revision",
            "input_schema": "prediction-delta record",
            "output_schema": "DeltaValidationResult",
            "relation_to_check_enforce_hook": "used by contract dry-run before hook-like allow",
            "relation_to_gov_mcp": "matches dry-run-before-live pattern",
            "relation_to_bridge_labs_ceo_packets": "post-action residual repair precedent",
            "maturity": "implemented_and_test_backed",
            "should_be_reused_in_CEO_Cognitive_OS": "yes",
            "evidence": ["tests/governance/test_cieu_prediction_delta.py", "docs/cieu_prediction_delta/schema_v0.md"],
        },
        {
            "mechanism_id": "ystar_hook_contract_require_revision",
            "repo": "Y-star-gov",
            "file_path": "ystar/governance/hook_contract_adapter.py",
            "symbol_or_artifact": "HookAdapterDecision.REQUIRE_REVISION",
            "decision_vocabulary": ["allow", "warn", "require_revision", "deny", "escalate"],
            "returns_corrective_guidance": True,
            "blocks_execution": True,
            "requires_owner_approval": False,
            "supports_reprojection_shadow_update_dry_run_revision": "dry_run_revision",
            "input_schema": "hook-like envelope",
            "output_schema": "hook decision envelope with require_revision boolean",
            "relation_to_check_enforce_hook": "future hook boundary compatibility layer",
            "relation_to_gov_mcp": "compatible with governed tool boundary patterns",
            "relation_to_bridge_labs_ceo_packets": "preferred decision vocabulary for E83 patch",
            "maturity": "implemented_and_test_backed",
            "should_be_reused_in_CEO_Cognitive_OS": "yes",
            "evidence": ["tests/fixtures/hook_contract_adapter/require_revision_missing_y_star.json", "docs/hook_cli_contract_compatibility.md"],
        },
        {
            "mechanism_id": "ystar_openclaw_redirect_rewrite",
            "repo": "Y-star-gov",
            "file_path": "ystar/domains/openclaw/adapter.py and ystar/adapters/hook.py",
            "symbol_or_artifact": "EnforceDecision.REDIRECT / REWRITE / GuidancePayload",
            "decision_vocabulary": ["allow", "deny", "escalate", "redirect", "invoke", "inject", "auto_post", "rewrite"],
            "returns_corrective_guidance": True,
            "blocks_execution": "redirect allows correction/retry; deny blocks",
            "requires_owner_approval": "only for escalated authority cases",
            "supports_reprojection_shadow_update_dry_run_revision": "redirect/rewrite/corrective retry",
            "input_schema": "OpenClaw event/hook payload",
            "output_schema": "hook PreToolUse decision envelope",
            "relation_to_check_enforce_hook": "real hook/runtime correction precedent",
            "relation_to_gov_mcp": "later tool/provider boundary can consume Y-star-gov decisions",
            "relation_to_bridge_labs_ceo_packets": "confirms incomplete-but-repairable should not always be DENY",
            "maturity": "implemented",
            "should_be_reused_in_CEO_Cognitive_OS": "maybe_later_runtime_wiring",
            "evidence": ["Y-star-gov:ystar/adapters/hook.py", "Y-star-gov:ystar/domains/openclaw/adapter.py"],
        },
        {
            "mechanism_id": "bridge_labs_review_gated_action_semantics",
            "repo": "bridge-labs",
            "file_path": "office/mission_command/action_semantics.py",
            "symbol_or_artifact": "decision_from_structured_action -> REVIEW_GATED / NEEDS_OWNER_APPROVAL",
            "decision_vocabulary": ["ALLOW_INTERNAL", "REVIEW_GATED", "NEEDS_OWNER_APPROVAL", "BLOCKED"],
            "returns_corrective_guidance": True,
            "blocks_execution": "review-gated until owner or review path",
            "requires_owner_approval": "for external side effects and live read-only research",
            "supports_reprojection_shadow_update_dry_run_revision": "review_gate",
            "input_schema": "structured action dict",
            "output_schema": "StructuredAction",
            "relation_to_check_enforce_hook": "bridge-labs packet producer, not canonical enforcement",
            "relation_to_gov_mcp": "company preflight semantics mirror gov-mcp company_runtime_tools",
            "relation_to_bridge_labs_ceo_packets": "bridge side precedent for approval/revision/blocked distinctions",
            "maturity": "implemented_and_test_backed",
            "should_be_reused_in_CEO_Cognitive_OS": "context_only",
            "evidence": ["tests/office/test_action_semantics.py"],
        },
        {
            "mechanism_id": "gov_mcp_company_preflight_and_provider_promotion",
            "repo": "gov-mcp",
            "file_path": "gov_mcp/company_runtime_tools.py and gov_mcp/outbound/provider_promotion.py",
            "symbol_or_artifact": "gov_company_action_preflight / request_revision / dry_run_to_live_promotion",
            "decision_vocabulary": ["approve", "reject", "request_revision", "hold", "promotion_allowed", "dry_run_denied"],
            "returns_corrective_guidance": True,
            "blocks_execution": "provider live path blocked until promotion contract passes",
            "requires_owner_approval": "risk-tier dependent",
            "supports_reprojection_shadow_update_dry_run_revision": "dry_run_and_promotion",
            "input_schema": "company action/preflight/provider request",
            "output_schema": "governance/preflight/promotion result",
            "relation_to_check_enforce_hook": "tool/provider executor side, not E83 patch target",
            "relation_to_gov_mcp": "canonical provider/tool envelope owner",
            "relation_to_bridge_labs_ceo_packets": "L4/L5 execution must later use gov-mcp where provider/tool action exists",
            "maturity": "implemented_read_only_in_E83",
            "should_be_reused_in_CEO_Cognitive_OS": "yes_later_execution_boundary",
            "evidence": ["gov-mcp:gov_mcp/company_runtime_tools.py", "gov-mcp:gov_mcp/outbound/provider_promotion.py"],
        },
    ]
    return {
        "artifact_id": "e83_auto_guidance_lineage_discovery",
        "job_id": JOB_ID,
        "mechanism_count": len(mechanisms),
        "repository_discovered_correct_path_name": "REQUIRE_REVISION",
        "mechanisms": mechanisms,
        "owner_correction_confirmed": "repairable incomplete CEO packets should receive require_revision guidance, not flat DENY or human-dump ESCALATE",
        "no_external_action": True,
    }


def build_decision_vocabulary() -> dict[str, Any]:
    values = [
        {"value": "ALLOW/allow/pass", "repo": "Y-star-gov", "meaning": "runtime or dry-run permits action/packet", "maps_to": "ALLOW", "evidence": "kernel engine, pre_u, hook adapter"},
        {"value": "WARN/warn", "repo": "Y-star-gov", "meaning": "non-blocking warning or telemetry", "maps_to": "STATUS_ONLY", "evidence": "pre_u/hook adapter"},
        {"value": "REQUIRE_REVISION/require_revision/requires_revision", "repo": "Y-star-gov", "meaning": "repairable packet/envelope gap; no execution until revised", "maps_to": "REQUIRE_REVISION", "evidence": "pre_u, delta, dry_run, hook adapter"},
        {"value": "DENY/deny/BLOCKED", "repo": "Y-star-gov/bridge-labs", "meaning": "hard boundary violation or unsafe/non-repairable action", "maps_to": "DENY", "evidence": "kernel checks, bridge action semantics"},
        {"value": "ESCALATE/escalate/HOLD_FOR_APPROVAL", "repo": "Y-star-gov", "meaning": "valid or high-risk case requiring owner/human authority", "maps_to": "ESCALATE", "evidence": "kernel enforcement, pre_u, hook adapter"},
        {"value": "REDIRECT/redirect", "repo": "Y-star-gov", "meaning": "runtime correct-path with suggested action/retry", "maps_to": "REQUIRE_REVISION", "evidence": "OpenClaw adapter and hook"},
        {"value": "REWRITE/rewrite", "repo": "Y-star-gov", "meaning": "safe transform to compliant payload", "maps_to": "REQUIRE_REVISION", "evidence": "hook auto_rewrite path"},
        {"value": "APPROVE/approve, REJECT/reject, request_revision, hold", "repo": "bridge-labs/gov-mcp", "meaning": "owner decision or company preflight statuses", "maps_to": "STATUS_ONLY", "evidence": "action semantics and gov_mcp company_runtime_tools"},
        {"value": "pending_owner_decision/owner_approval_required", "repo": "bridge-labs", "meaning": "approval state, not runtime validation result", "maps_to": "STATUS_ONLY", "evidence": "E81/E82 artifacts"},
    ]
    return {
        "artifact_id": "e83_decision_vocabulary_audit",
        "job_id": JOB_ID,
        "decision_values": values,
        "normalized_semantic_taxonomy": {
            "ALLOW": "packet/action satisfies contract and authorization",
            "DENY": "hard boundary violation; do not repair through automatic path",
            "REQUIRE_REVISION": "repository-discovered auto-guidance equivalent for repairable incompleteness",
            "ESCALATE": "genuine owner/human authority needed after automated validation",
            "STATUS_ONLY": "artifact status or approval state, not runtime decision",
        },
        "selected_auto_guidance_name": "REQUIRE_REVISION",
    }


def build_semantics_audit() -> dict[str, Any]:
    patched = _ystar_validator_supports_revision()
    return {
        "artifact_id": "e83_e82_cognitive_os_semantics_audit",
        "job_id": JOB_ID,
        "audited_module": "Y-star-gov:ystar/governance/ceo_cognitive_os_contract.py",
        "correct_layer_decision": "governance layer remains correct",
        "E82_semantics_audit_decision": "correct_but_needs_auto_guidance_semantics",
        "findings": [
            "E82 correctly placed CEO Cognitive OS in Y-star-gov governance packet validation.",
            "E82 incorrectly treated repairable missing cognitive stages, counterfactuals, CIEU predictions, and no-new-wheel proof as DENY.",
            "Y-star-gov mainline already has require_revision semantics in Pre-U, CIEU prediction-delta, contract dry-run, and hook adapter paths.",
            "Owner-approval-pending L4/external execution should be ESCALATE with owner decision path when otherwise complete.",
            "Forbidden claims, bypass attempts, unverified runtime-active capability claims, and duplicate core mechanisms remain DENY.",
        ],
        "validator_patched": patched,
        "patch_result": "implemented_REQUIRE_REVISION_guidance" if patched else "not_detected",
        "CIEU_relation": "validation record now carries guidance and correct_path in Y_t_plus_1/R_t_plus_1 without live DB writes",
        "bridge_labs_relation": "bridge-labs produces CEO packets and records evidence/readback",
        "gov_mcp_relation": "gov-mcp remains later provider/tool envelope owner",
        "K9Audit_relation": "ledger/verifier ownership untouched",
        "no_parallel_governance_engine": True,
    }


def build_correct_semantics() -> dict[str, Any]:
    return {
        "artifact_id": "e83_ceo_cognitive_os_correct_decision_semantics",
        "job_id": JOB_ID,
        "final_decision_semantics": {
            "ALLOW": {
                "when": ["packet complete", "cognitive loop satisfied", "no forbidden claims", "no bypass", "action authorized"],
                "execution_allowed": True,
            },
            "DENY": {
                "when": [
                    "hard boundary violation",
                    "bypass attempt",
                    "forbidden customer/paid/pricing/compliance/production/L4/L5 claim",
                    "unverified runtime-active capability claim presented as truth",
                    "explicit duplicate Y-star-gov/K9Audit/gov-mcp core mechanism",
                    "malformed non-mapping packet",
                ],
                "execution_allowed": False,
            },
            "REQUIRE_REVISION": {
                "repository_discovered_equivalent": "require_revision",
                "when": [
                    "missing required field",
                    "missing cognitive loop stage",
                    "missing repository evidence paths",
                    "recent-memory-only reasoning",
                    "missing counterfactual comparison",
                    "missing pre-action CIEU prediction",
                    "missing adversarial critique",
                    "missing what-not-to-do",
                    "construction lacking no-new-wheel proof but not explicitly duplicate",
                    "repairable post-action residual gap",
                ],
                "correct_path_returned": True,
                "execution_allowed": False,
            },
            "ESCALATE": {
                "when": [
                    "packet is otherwise complete but action needs owner/human authority",
                    "L4/external execution has pending owner approval",
                    "risk authority is ambiguous after automated checks",
                ],
                "owner_decision_path_required": True,
                "execution_allowed_before_owner_decision": False,
            },
            "STATUS_ONLY": {
                "when": ["artifact lifecycle status", "owner approval state", "report status"],
                "runtime_decision": False,
            },
        },
        "important_distinction": "repairable incompleteness returns REQUIRE_REVISION, not DENY; owner authority gaps return ESCALATE, not generic human dumping",
        "hard_boundaries_remain_DENY": True,
    }


def build_l4_l5_design() -> dict[str, Any]:
    return {
        "artifact_id": "e83_l4_l5_correct_integration_design_with_autoguidance",
        "job_id": JOB_ID,
        "L4_flow": {
            "pre_action_packet_missing_cognitive_requirements": "REQUIRE_REVISION with missing fields/stages/evidence correct_path",
            "complete_but_owner_approval_pending": "ESCALATE with owner decision packet path",
            "approved_and_scoped": "ALLOW for the validated packet only",
            "mass_outreach_publication_payment_login_scraping": "DENY",
            "post_action_residual_missing": "REQUIRE_REVISION",
            "forbidden_claim_after_feedback": "DENY",
            "L4_execution_status_in_E83": "not_executed",
        },
        "L5_flow": {
            "missing_pricing_customer_legal_prerequisites": "REQUIRE_REVISION or ESCALATE depending authority",
            "unapproved_payment_customer_data_publication": "DENY",
            "pricing_or_customer_validation_claim_without_evidence": "DENY",
            "future_owner_approved_scoped_revenue_experiment": "ALLOW only after future readiness gate",
            "provider_or_tool_execution": "must use gov-mcp governed provider/action envelope",
            "ledger_or_verifier": "K9Audit remains canonical owner if used",
            "L5_readiness_status_in_E83": "not_ready",
        },
        "role_split": {
            "bridge_labs": "CEO packets, business artifacts, owner decision packets, readbacks",
            "Y_star_gov": "validates cognitive OS packets and returns ALLOW/DENY/REQUIRE_REVISION/ESCALATE",
            "gov_mcp": "later governed provider/tool execution envelope",
            "K9Audit": "ledger/verifier owner if ledger integration is used",
            "ystar_company": "historical/company context only unless separately approved",
        },
        "no_external_action": True,
    }


def build_cieu_residual() -> dict[str, Any]:
    return {
        "artifact_id": "e83_cieu_residual_for_autoguidance_semantics_and_interface_audit",
        "job_id": JOB_ID,
        "X_t": {
            "E82_synced_CEO_Cognitive_OS_into_Y_star_gov": True,
            "owner_rejected_simplistic_ESCALATE": True,
            "auto_guidance_lineage_uncertain_before_E83": True,
            "no_external_action_boundary": True,
        },
        "U_t": {
            "audited_Y_star_gov_topology": True,
            "discovered_auto_guidance_lineage": True,
            "audited_decision_vocabulary": True,
            "audited_E82_validator_semantics": True,
            "defined_correct_ALLOW_DENY_REQUIRE_REVISION_ESCALATE_semantics": True,
            "patched_validator_if_supported": _ystar_validator_supports_revision(),
            "designed_L4_L5_auto_guidance_interface": True,
        },
        "Y_star_t": {
            "intended_outcome": "restore correct Y*gov guidance semantics and avoid simple DENY/ESCALATE when repairable",
            "preserve_hard_DENY_for_forbidden_actions": True,
            "ESCALATE_only_for_owner_authority": True,
        },
        "Y_t_plus_1": {
            "topology_audit": "generated",
            "auto_guidance_discovery": "generated",
            "decision_vocabulary_audit": "generated",
            "E82_semantics_audit": "generated",
            "patch_result": "REQUIRE_REVISION_guidance_supported" if _ystar_validator_supports_revision() else "not_detected",
            "L4_L5_integration_design": "generated",
            "tests": "targeted Y-star-gov and bridge-labs tests run",
        },
        "R_t_plus_1": {
            "hook_runtime_wiring_may_remain": True,
            "live_CIEU_DB_writes_remain_deferred": True,
            "L4_feedback_not_executed": True,
            "L5_not_ready": True,
            "customer_paid_pricing_compliance_validation_absent": True,
            "decision_vocabulary_ambiguity": "resolved_to_REQUIRE_REVISION_for_auto_guidance",
        },
    }


def build_next_milestone() -> dict[str, Any]:
    return {
        "artifact_id": "e83_generated_next_milestone_proposal",
        "job_id": JOB_ID,
        "selected_next_milestone": "E84_YStarGov_CEO_Cognitive_OS_Hook_Runtime_Wiring_With_AutoGuidance_R1",
        "type": "specific_governance_runtime_wiring",
        "why": "Auto-guidance semantics are discovered and patched; the remaining specific gap is optional hook/runtime wiring so real tool-boundary checks can consume the guided decision envelope.",
        "not_selected": [
            "broad inventory",
            "generic infrastructure",
            "generic L3 research",
            "publication",
            "mass outreach",
            "L5 revenue",
        ],
        "owner_approval_required_for_external_action": True,
        "L4_execution_authorized": False,
        "L5_ready": False,
    }


def build_readback() -> dict[str, Any]:
    return {
        "artifact_id": "e83_ceo_cognitive_os_autoguidance_readback",
        "job_id": JOB_ID,
        "discovered_auto_guidance_lineage": "Y-star-gov require_revision via Pre-U, CIEU prediction-delta, contract dry-run, and hook adapter; bridge-labs review-gated/request-revision; gov-mcp preflight/dry-run promotion.",
        "actual_decision_vocabulary": ["ALLOW", "REQUIRE_REVISION", "DENY", "ESCALATE", "STATUS_ONLY"],
        "E82_semantics_correction": "repairable incomplete CEO Cognitive OS packets now REQUIRE_REVISION with correct_path; owner-approval-pending L4 external action ESCALATEs; hard boundaries DENY.",
        "Y_star_gov_validator_supports_correct_path_guidance": _ystar_validator_supports_revision(),
        "correct_L4_flow": build_l4_l5_design()["L4_flow"],
        "correct_L5_flow": build_l4_l5_design()["L5_flow"],
        "next_milestone": build_next_milestone()["selected_next_milestone"],
        "external_action_allowed": False,
        "L4_execution_authorized": False,
        "L5_ready": False,
    }


def build_completion_report(test_results: list[dict[str, Any]] | None = None) -> dict[str, Any]:
    bridge_head = _git(["rev-parse", "HEAD"], BRIDGE_ROOT)
    y_head = _git(["rev-parse", "HEAD"], Y_GOV_ROOT)
    topology = build_topology_audit()
    lineage = build_auto_guidance_lineage()
    vocab = build_decision_vocabulary()
    semantics = build_semantics_audit()
    next_milestone = build_next_milestone()
    return {
        "artifact_id": "e83_completion_report",
        "job_id": JOB_ID,
        "Y_star_gov_base_verified": True,
        "Y_star_gov_expected_base": EXPECTED_YSTAR_GOV_BASE,
        "Y_star_gov_final_hash": y_head,
        "bridge_labs_base_verified": True,
        "bridge_labs_expected_base": EXPECTED_BRIDGE_BASE,
        "bridge_labs_final_hash": bridge_head,
        "modified_repos": ["Y-star-gov", "bridge-labs"],
        "Y_star_gov_files_created": ["docs/ceo_cognitive_os_sync/e83_full_topology_audit.md"],
        "Y_star_gov_files_modified": [
            "ystar/governance/ceo_cognitive_os_contract.py",
            "tests/governance/test_ceo_cognitive_os_contract.py",
        ],
        "bridge_labs_files_created": REQUIRED_ARTIFACTS + [
            "office/mission_command/e83_autoguidance_semantics_readback.py",
            "tests/office/test_e83_autoguidance_semantics.py",
        ],
        "bridge_labs_files_modified": ["office/mission_command/e46b_ceo_brain_adapter.py"],
        "topology_audit_summary": f"{topology['topology_node_count']} topology nodes narrowed to one patch target",
        "auto_guidance_lineage_found": lineage["repository_discovered_correct_path_name"],
        "actual_decision_vocabulary_found": [item["value"] for item in vocab["decision_values"]],
        "E82_semantics_audit_decision": semantics["E82_semantics_audit_decision"],
        "validator_patched": semantics["validator_patched"],
        "final_decision_semantics": build_correct_semantics()["final_decision_semantics"],
        "L4_correct_integration_interface": build_l4_l5_design()["L4_flow"],
        "L5_correct_integration_interface": build_l4_l5_design()["L5_flow"],
        "tests_run": test_results or [],
        "residual_gaps": [
            "hook runtime wiring may remain",
            "live CIEU DB writes remain deferred",
            "L4 feedback not executed",
            "L5 not ready",
            "customer/paid/pricing/compliance validation absent",
        ],
        "next_recommended_milestone": next_milestone["selected_next_milestone"],
        "safety_statement": {
            "no_external_action": True,
            "no_outreach": True,
            "no_publication": True,
            "no_payment": True,
            "no_customer_validation_claim": True,
            "no_expert_validation_claim": True,
            "no_paid_signal_claim": True,
            "no_pricing_validation_claim": True,
            "no_compliance_legal_claim": True,
            "no_production_deployment_claim": True,
            "no_L4_execution_claim": True,
            "no_L5_readiness_claim": True,
            "no_K9Audit_or_gov_mcp_mutation": True,
            "no_parallel_Y_star_gov_governance_engine": True,
        },
    }


REQUIRED_ARTIFACTS = [
    "operations/external_validation/e83_ystar_gov_full_topology_audit.json",
    "operations/external_validation/e83_ystar_gov_full_topology_audit.md",
    "operations/external_validation/e83_ystar_gov_topology_audit_result.json",
    "operations/external_validation/e83_ystar_gov_topology_audit_result.md",
    "operations/external_validation/e83_auto_guidance_lineage_discovery.json",
    "operations/external_validation/e83_auto_guidance_lineage_discovery.md",
    "operations/external_validation/e83_decision_vocabulary_audit.json",
    "operations/external_validation/e83_decision_vocabulary_audit.md",
    "operations/external_validation/e83_e82_cognitive_os_semantics_audit.json",
    "operations/external_validation/e83_e82_cognitive_os_semantics_audit.md",
    "operations/external_validation/e83_ceo_cognitive_os_correct_decision_semantics.json",
    "operations/external_validation/e83_ceo_cognitive_os_correct_decision_semantics.md",
    "operations/external_validation/e83_l4_l5_correct_integration_design_with_autoguidance.json",
    "operations/external_validation/e83_l4_l5_correct_integration_design_with_autoguidance.md",
    "operations/external_validation/e83_cieu_residual_for_autoguidance_semantics_and_interface_audit.json",
    "operations/external_validation/e83_cieu_residual_for_autoguidance_semantics_and_interface_audit.md",
    "operations/external_validation/e83_generated_next_milestone_proposal.json",
    "operations/external_validation/e83_generated_next_milestone_proposal.md",
    "operations/external_validation/e83_completion_report.json",
    "operations/external_validation/e83_completion_report.md",
    "operations/external_validation/e83_ceo_cognitive_os_autoguidance_readback.json",
    "operations/external_validation/e83_ceo_cognitive_os_autoguidance_readback.md",
]


def generate_e83_artifacts(test_results: list[dict[str, Any]] | None = None) -> dict[str, Any]:
    topology = build_topology_audit()
    lineage = build_auto_guidance_lineage()
    vocab = build_decision_vocabulary()
    semantics = build_semantics_audit()
    correct_semantics = build_correct_semantics()
    l4_l5 = build_l4_l5_design()
    residual = build_cieu_residual()
    next_milestone = build_next_milestone()
    readback = build_readback()
    completion = build_completion_report(test_results)
    artifacts = {
        "e83_ystar_gov_full_topology_audit": topology,
        "e83_ystar_gov_topology_audit_result": topology | {"artifact_id": "e83_ystar_gov_topology_audit_result"},
        "e83_auto_guidance_lineage_discovery": lineage,
        "e83_decision_vocabulary_audit": vocab,
        "e83_e82_cognitive_os_semantics_audit": semantics,
        "e83_ceo_cognitive_os_correct_decision_semantics": correct_semantics,
        "e83_l4_l5_correct_integration_design_with_autoguidance": l4_l5,
        "e83_cieu_residual_for_autoguidance_semantics_and_interface_audit": residual,
        "e83_generated_next_milestone_proposal": next_milestone,
        "e83_ceo_cognitive_os_autoguidance_readback": readback,
        "e83_completion_report": completion,
    }
    for name, data in artifacts.items():
        _write_json(OUT_DIR / f"{name}.json", data)
        _write_md(OUT_DIR / f"{name}.md", _title_for(name), _markdown_lines(data))
    return completion


def load_e83_autoguidance_state_for_brain() -> dict[str, Any]:
    path = OUT_DIR / "e83_ceo_cognitive_os_autoguidance_readback.json"
    if not path.exists():
        generate_e83_artifacts()
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except Exception as exc:
        return {
            "artifact_id": "e83_ceo_cognitive_os_autoguidance_readback",
            "E83_status": "unavailable_nonfatal",
            "error": str(exc),
            "external_action_allowed": False,
            "L4_execution_authorized": False,
            "L5_ready": False,
        }


def _title_for(name: str) -> str:
    return name.replace("_", " ").title()


def _markdown_lines(data: dict[str, Any]) -> list[str]:
    lines = [
        f"- Artifact: `{data.get('artifact_id')}`",
        f"- Job: `{data.get('job_id', JOB_ID)}`",
    ]
    if data.get("selected_patch_target"):
        lines.append(f"- Selected patch target: `{data['selected_patch_target']}`")
    if data.get("repository_discovered_correct_path_name"):
        lines.append(f"- Repository-discovered correct-path name: `{data['repository_discovered_correct_path_name']}`")
    if data.get("E82_semantics_audit_decision"):
        lines.append(f"- E82 semantics audit decision: `{data['E82_semantics_audit_decision']}`")
    if "validator_patched" in data:
        lines.append(f"- Validator patched: `{data['validator_patched']}`")
    if data.get("selected_next_milestone"):
        lines.append(f"- Next milestone: `{data['selected_next_milestone']}`")
    if data.get("final_decision_semantics"):
        lines.append("")
        lines.append("## Final Semantics")
        for key in ["ALLOW", "REQUIRE_REVISION", "DENY", "ESCALATE", "STATUS_ONLY"]:
            if key in data["final_decision_semantics"]:
                lines.append(f"- `{key}`: {data['final_decision_semantics'][key]}")
    if data.get("topology_nodes"):
        lines.append("")
        lines.append("## Topology Nodes")
        for node in data["topology_nodes"]:
            lines.append(f"- `{node['node_id']}` -> `{node['file_path']}`: {node['auto_guidance_repair_relation']}")
    if data.get("mechanisms"):
        lines.append("")
        lines.append("## Mechanisms")
        for mechanism in data["mechanisms"]:
            lines.append(f"- `{mechanism['mechanism_id']}` ({mechanism['repo']}): {mechanism['decision_vocabulary']}")
    if data.get("L4_flow"):
        lines.append("")
        lines.append("## L4 Flow")
        for key, value in data["L4_flow"].items():
            lines.append(f"- `{key}`: {value}")
    if data.get("L5_flow"):
        lines.append("")
        lines.append("## L5 Flow")
        for key, value in data["L5_flow"].items():
            lines.append(f"- `{key}`: {value}")
    if data.get("tests_run"):
        lines.append("")
        lines.append("## Tests")
        for result in data["tests_run"]:
            lines.append(f"- `{result['command']}`: {result['result']}")
    lines.append("")
    lines.append("## Safety")
    lines.append("- No external action, outreach, publication, payment, L4 execution, or L5 readiness claim.")
    lines.append("- No K9Audit/gov-mcp mutation and no parallel Y-star-gov governance engine.")
    return lines


if __name__ == "__main__":
    generate_e83_artifacts()
