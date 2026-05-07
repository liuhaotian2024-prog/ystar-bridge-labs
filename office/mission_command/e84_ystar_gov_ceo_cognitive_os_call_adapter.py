from __future__ import annotations

import importlib
import json
import os
import sys
from pathlib import Path
from typing import Any, Mapping


BRIDGE_ROOT = Path(os.environ.get("YSTAR_BRIDGE_LABS_ROOT", Path(__file__).resolve().parents[2]))
Y_GOV_ROOT = Path(os.environ.get("YSTAR_GOV_ROOT", "/Users/haotianliu/.openclaw/workspace/Y-star-gov"))


def _load_ystar_governance_module(ystar_gov_root: Path | None = None) -> Any:
    root = ystar_gov_root or Y_GOV_ROOT
    if root.exists() and str(root) not in sys.path:
        sys.path.insert(0, str(root))
    return importlib.import_module("ystar.governance")


def _normalize_decision_result(result: Any) -> dict[str, Any]:
    if hasattr(result, "to_dict"):
        payload = result.to_dict()
    elif isinstance(result, Mapping):
        payload = dict(result)
    else:
        payload = {"decision": "DENY", "reason": f"unsupported Y-star-gov decision result: {type(result).__name__}"}

    payload.setdefault("passed", payload.get("decision") == "ALLOW")
    payload.setdefault("guidance", {})
    payload.setdefault("correct_path", [])
    payload.setdefault("requires_owner_decision", False)
    payload.setdefault("cieu_validation_record", payload.get("CIEU_validation_record", {}))
    return payload


def validate_pre_action_with_ystar_gov(
    packet: Mapping[str, Any],
    *,
    ystar_gov_root: Path | None = None,
) -> dict[str, Any]:
    """Call the canonical Y-star-gov CEO pre-action validator without executing work."""

    try:
        governance = _load_ystar_governance_module(ystar_gov_root)
        raw = governance.validate_ceo_pre_action_packet(packet)
        result = _normalize_decision_result(raw)
        import_status = "direct_YstarGov_import_used"
    except Exception as exc:
        result = {
            "decision": "DENY",
            "passed": False,
            "reason": f"Y-star-gov CEO Cognitive OS validator unavailable: {exc}",
            "failed_stage": "YstarGov_import",
            "violations": ["YstarGov_validator_unavailable"],
            "guidance": {},
            "correct_path": [],
            "requires_owner_decision": False,
            "cieu_validation_record": {},
        }
        import_status = "YstarGov_import_failed"

    return _route_decision(
        result,
        validator="validate_ceo_pre_action_packet",
        packet_kind="pre_action_packet",
        import_status=import_status,
    )


def validate_post_action_with_ystar_gov(
    residual: Mapping[str, Any],
    *,
    ystar_gov_root: Path | None = None,
) -> dict[str, Any]:
    """Call the canonical Y-star-gov CEO post-action validator without CIEU log writes."""

    try:
        governance = _load_ystar_governance_module(ystar_gov_root)
        raw = governance.validate_ceo_post_action_residual(residual)
        result = _normalize_decision_result(raw)
        import_status = "direct_YstarGov_import_used"
    except Exception as exc:
        result = {
            "decision": "DENY",
            "passed": False,
            "reason": f"Y-star-gov CEO Cognitive OS post-action validator unavailable: {exc}",
            "failed_stage": "YstarGov_import",
            "violations": ["YstarGov_validator_unavailable"],
            "guidance": {},
            "correct_path": [],
            "requires_owner_decision": False,
            "cieu_validation_record": {},
        }
        import_status = "YstarGov_import_failed"

    return _route_decision(
        result,
        validator="validate_ceo_post_action_residual",
        packet_kind="post_action_residual",
        import_status=import_status,
    )


def _route_decision(
    decision_result: Mapping[str, Any],
    *,
    validator: str,
    packet_kind: str,
    import_status: str,
) -> dict[str, Any]:
    decision = str(decision_result.get("decision", "DENY"))
    route_by_decision = {
        "ALLOW": {
            "route": "continue_to_approved_next_step_without_external_execution",
            "execution_allowed_by_adapter": False,
            "owner_decision_packet_required": False,
            "ceo_revision_required": False,
            "block_execution": False,
        },
        "REQUIRE_REVISION": {
            "route": "return_correct_path_guidance_to_ceo",
            "execution_allowed_by_adapter": False,
            "owner_decision_packet_required": False,
            "ceo_revision_required": True,
            "block_execution": True,
        },
        "ESCALATE": {
            "route": "generate_owner_decision_packet_no_execution",
            "execution_allowed_by_adapter": False,
            "owner_decision_packet_required": True,
            "ceo_revision_required": False,
            "block_execution": True,
        },
        "DENY": {
            "route": "block_execution_and_record_residual",
            "execution_allowed_by_adapter": False,
            "owner_decision_packet_required": False,
            "ceo_revision_required": False,
            "block_execution": True,
        },
    }
    route = dict(route_by_decision.get(decision, route_by_decision["DENY"]))
    return {
        "artifact_id": "e84_ystar_gov_ceo_cognitive_os_call_adapter_result",
        "validator": validator,
        "packet_kind": packet_kind,
        "YstarGov_import_status": import_status,
        "YstarGov_decision": decision,
        "YstarGov_reason": decision_result.get("reason", ""),
        "YstarGov_failed_stage": decision_result.get("failed_stage"),
        "YstarGov_guidance": dict(decision_result.get("guidance", {})),
        "YstarGov_correct_path": list(decision_result.get("correct_path", [])),
        "YstarGov_requires_owner_decision": bool(decision_result.get("requires_owner_decision", False)),
        "CIEU_validation_record_candidate": dict(decision_result.get("cieu_validation_record", {})),
        "formal_CIEU_log_written": False,
        "formal_CIEU_log_status": "CIEU_log_write_deferred",
        "external_action_executed": False,
        "provider_live_execution": False,
        "route": route,
    }


def build_sample_pre_action_packet(*, action_class: str = "owner_decision_preparation") -> dict[str, Any]:
    governance = _load_ystar_governance_module()
    contract = governance.build_ceo_cognitive_os_contract()
    return {
        "packet_id": "e84_sample_pre_action_packet",
        "job_id": "E84_YStarGov_GovMCP_BridgeLabs_Runtime_Interface_Audit",
        "proposed_action": "wire bridge-labs CEO packet through Y-star-gov validator",
        "action_class": action_class,
        "owner_intent": "validate CEO major actions through canonical Y-star-gov before execution",
        "current_mission_context": {"reasoning_scope": "runtime_interface_audited"},
        "discovered_capabilities_consulted": [
            {
                "capability_id": "ystar_gov_ceo_cognitive_os_validator",
                "evidence_paths": ["Y-star-gov:ystar/governance/ceo_cognitive_os_contract.py"],
                "claimed_runtime_active": True,
                "runtime_evidence_status": "runtime_active_verified",
            },
            {
                "capability_id": "bridge_labs_ceo_packet_artifacts",
                "evidence_paths": ["bridge-labs:operations/external_validation/e81_ceo_mandatory_pre_action_packet_schema.json"],
                "claimed_runtime_active": False,
            },
        ],
        "historical_assets_consulted": ["E81 schema", "E82 sync packet", "E83 autoguidance semantics"],
        "canonical_owner_map": {"Y-star-gov": "canonical governance validator", "bridge-labs": "packet producer"},
        "no_new_wheel_decision": {"decision": "call_existing_YstarGov_validator", "non_duplication_proof": "no bridge-labs governance clone"},
        "candidate_actions": ["bridge-labs call adapter", "Y-star-gov hook rewrite later"],
        "counterfactual_comparison": [
            {"candidate": "bridge-labs call adapter", "expected_gain": "immediate canonical validation"},
            {"candidate": "Y-star-gov hook rewrite later", "expected_gain": "runtime hook enforcement after scope closure"},
        ],
        "predicted_CIEU_records": [
            {
                "X_t": "Y-star-gov validator exists; bridge-labs packets exist",
                "U_t": "call validator before accepting CEO major action",
                "Y_star_t": "CEO work routes through canonical governance without external execution",
                "expected_Y_t_plus_1": "ALLOW/REQUIRE_REVISION/DENY/ESCALATE routing is returned to bridge-labs",
                "predicted_R_t_plus_1": "formal CIEU log write remains deferred",
                "residual_severity": "medium",
            }
        ],
        "adversarial_critique": "Adapter could become decorative if future CEO workflows do not call it.",
        "what_not_to_do": ["do not execute L4", "do not claim formal CIEU log write", "do not mutate gov-mcp"],
        "selected_action": "bridge-labs call adapter",
        "why_this_action": "It connects the existing packet producer to canonical Y-star-gov validation now.",
        "why_not_other_actions": "Hook rewriting and CIEU log writes need tighter insertion-point closure.",
        "safety_boundary": {"external_action_allowed": False},
        "overclaim_boundary": {
            "customer_validation_claim": False,
            "expert_validation_claim": False,
            "paid_signal_claim": False,
            "pricing_validation_claim": False,
            "compliance_legal_claim": False,
            "production_deployment_claim": False,
            "live_ledger_claim": False,
            "L4_execution_claim": False,
            "L5_readiness_claim": False,
        },
        "Y_star_contract_hash_input": "sha256:e84-runtime-interface",
        "required_YstarGov_check": "validate_ceo_pre_action_packet",
        "approval_required": action_class in {"L4_external_feedback_execution", "external_action"},
        "owner_approval_state": "approved" if action_class not in {"L4_external_feedback_execution", "external_action"} else "pending_owner_decision",
        "bypass_attempt": False,
        "loop_stage_results": [
            {"stage_id": stage_id, "status": "passed", "evidence_paths": ["repo://E84/evidence"]}
            for stage_id in contract.required_loop_stage_ids
        ],
    }


def build_sample_post_action_residual() -> dict[str, Any]:
    return {
        "packet_id": "e84_sample_post_action_residual",
        "linked_pre_action_packet_id": "e84_sample_pre_action_packet",
        "action_taken": "bridge-labs call adapter",
        "expected_outcome": "canonical Y-star-gov decision returned",
        "actual_output": "adapter result recorded; no external action executed",
        "CIEU_record": {
            "X_t": "Y-star-gov validator available",
            "U_t": "bridge-labs adapter invoked validator",
            "Y_star_t": "CEO major action is governance-checked before acceptance",
            "Y_t_plus_1": "decision route returned to bridge-labs",
            "R_t_plus_1": "formal CIEU log write remains deferred",
        },
        "residuals": ["hook runtime wiring pending", "formal CIEU log write deferred"],
        "unexpected_failures": [],
        "overclaim_check": {
            "customer_validation_claim": False,
            "expert_validation_claim": False,
            "paid_signal_claim": False,
            "pricing_validation_claim": False,
            "compliance_legal_claim": False,
            "production_deployment_claim": False,
            "live_ledger_claim": False,
            "L4_execution_claim": False,
            "L5_readiness_claim": False,
        },
        "no_new_wheel_check": {"passed": True},
        "owner_usefulness_check": {"passed": True},
        "intelligence_gate_result": {"passed": True},
        "capability_state_updates": ["bridge-labs can call Y-star-gov validator directly"],
        "learning_candidates": ["wire hook runtime after owner-approved closure"],
        "YstarGov_sync_status": "YstarGov_synced_call_adapter_active",
        "next_action_recommendation": "E85_YStarGov_CEO_Cognitive_OS_Hook_Runtime_Wiring_R1",
        "what_not_to_do_next": ["do not execute L4 without owner approval", "do not claim formal CIEU log write"],
    }


def run_adapter_smoke() -> dict[str, Any]:
    valid_packet = build_sample_pre_action_packet()
    revision_packet = json.loads(json.dumps(valid_packet))
    revision_packet["counterfactual_comparison"] = []
    escalation_packet = build_sample_pre_action_packet(action_class="L4_external_feedback_execution")
    denied_packet = json.loads(json.dumps(valid_packet))
    denied_packet["overclaim_boundary"]["customer_validation_claim"] = True

    return {
        "valid_packet": validate_pre_action_with_ystar_gov(valid_packet),
        "revision_packet": validate_pre_action_with_ystar_gov(revision_packet),
        "escalation_packet": validate_pre_action_with_ystar_gov(escalation_packet),
        "denied_packet": validate_pre_action_with_ystar_gov(denied_packet),
        "post_action_residual": validate_post_action_with_ystar_gov(build_sample_post_action_residual()),
    }
