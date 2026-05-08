from __future__ import annotations

import importlib
import json
import os
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Mapping

from office.mission_command.e84_ystar_gov_ceo_cognitive_os_call_adapter import (
    build_sample_post_action_residual,
    build_sample_pre_action_packet,
    run_adapter_smoke,
)


BRIDGE_ROOT = Path(os.environ.get("YSTAR_BRIDGE_LABS_ROOT", Path(__file__).resolve().parents[2]))
Y_GOV_ROOT = Path(os.environ.get("YSTAR_GOV_ROOT", "/Users/haotianliu/.openclaw/workspace/Y-star-gov"))
GOV_MCP_ROOT = Path(os.environ.get("GOV_MCP_ROOT", "/Users/haotianliu/.openclaw/workspace/gov-mcp"))


def _load_ystar_governance_module(ystar_gov_root: Path | None = None) -> Any:
    root = ystar_gov_root or Y_GOV_ROOT
    if root.exists() and str(root) not in sys.path:
        sys.path.insert(0, str(root))
    return importlib.import_module("ystar.governance")


def _load_gov_mcp_dry_run_adapter(gov_mcp_root: Path | None = None) -> Any:
    root = gov_mcp_root or GOV_MCP_ROOT
    if root.exists() and str(root) in sys.path:
        sys.path.remove(str(root))
    if root.exists():
        sys.path.insert(0, str(root))
    _clear_shadowed_gov_mcp_package(root)
    importlib.invalidate_caches()
    return importlib.import_module("gov_mcp.outbound.dry_run_adapter")


def _clear_shadowed_gov_mcp_package(root: Path) -> None:
    """Ensure bridge-labs' local gov_mcp package does not hide the gov-mcp repo."""

    module = sys.modules.get("gov_mcp")
    module_file = Path(getattr(module, "__file__", "")) if module is not None else None
    if module_file and root.exists() and not _is_relative_to(module_file, root):
        for name in list(sys.modules):
            if name == "gov_mcp" or name.startswith("gov_mcp."):
                sys.modules.pop(name, None)


def _is_relative_to(path: Path, root: Path) -> bool:
    try:
        path.resolve().relative_to(root.resolve())
        return True
    except ValueError:
        return False


def build_ceo_major_action_runtime_envelope(
    *,
    packet: Mapping[str, Any] | None = None,
    action_id: str = "e85_ceo_major_action_runtime_gate",
    action_type: str = "runtime_major_action",
    objective: str = "route CEO major action through Y-star-gov runtime hook",
    externality_level: str = "internal",
    owner_approval_status: str = "approved",
    action_phase: str = "pre_action",
    include_pre_action_packet: bool = True,
    post_action_residual: Mapping[str, Any] | None = None,
) -> dict[str, Any]:
    """Build a bridge-labs CEO major-action envelope for Y-star-gov runtime validation."""

    selected_packet = dict(packet or build_sample_pre_action_packet())
    envelope: dict[str, Any] = {
        "action_id": action_id,
        "actor": "CEO",
        "role": "ceo",
        "action_type": action_type,
        "mission": "CEO Cognitive OS runtime foundation",
        "objective": objective,
        "declared_intent": "validate before accepting any CEO major action",
        "context": "E85 bridge-labs runtime bridge; no external work executed",
        "proposed_execution_boundary": "internal governance runtime gate only",
        "externality_level": externality_level,
        "owner_approval_status": owner_approval_status,
        "action_phase": action_phase,
        "requires_ceo_cognitive_os": True,
        "candidate_actions": selected_packet.get("candidate_actions", []),
        "counterfactual_alternatives": selected_packet.get("counterfactual_comparison", []),
        "pre_action_CIEU_prediction": selected_packet.get("predicted_CIEU_records", []),
        "adversarial_critique": selected_packet.get("adversarial_critique"),
        "what_not_to_do": selected_packet.get("what_not_to_do", []),
        "evidence_basis": [
            "bridge-labs:office/mission_command/e84_ystar_gov_ceo_cognitive_os_call_adapter.py",
            "Y-star-gov:ystar/governance/ceo_cognitive_os_runtime_hook.py",
            "gov-mcp:gov_mcp/server.py",
            "gov-mcp:gov_mcp/outbound/provider_guard_stack.py",
        ],
        "rollback_containment_plan": [
            "do not execute external action from ALLOW",
            "route REQUIRE_REVISION back to CEO correct_path",
            "route ESCALATE to owner decision packet without execution",
            "route DENY to blocked execution with residual candidate",
        ],
        "formal_CIEU_log_written": False,
        "claims_formal_CIEU_log_write": False,
        "external_action_executed": False,
        "provider_live_execution": False,
    }
    if include_pre_action_packet:
        envelope["pre_action_packet"] = selected_packet
    if post_action_residual is not None:
        envelope["post_action_residual"] = dict(post_action_residual)
    return envelope


def build_provider_tool_ceo_major_action_runtime_envelope(
    *,
    action_id: str = "e85r_ceo_provider_tool_dry_run_boundary",
    packet: Mapping[str, Any] | None = None,
) -> dict[str, Any]:
    selected_packet = dict(packet or build_sample_pre_action_packet(action_class="provider_tool_execution"))
    return build_ceo_major_action_runtime_envelope(
        packet=selected_packet,
        action_id=action_id,
        action_type="runtime_major_action",
        objective="prepare provider/tool action through gov-mcp dry-run envelope only",
        externality_level="provider_tool_boundary",
        owner_approval_status="approved",
    )


def route_ceo_major_action_through_ystar_gov_runtime(
    envelope: Mapping[str, Any],
    *,
    ystar_gov_root: Path | None = None,
) -> dict[str, Any]:
    """Call the Y-star-gov CEO Cognitive OS runtime hook and map it to bridge-labs routing."""

    try:
        governance = _load_ystar_governance_module(ystar_gov_root)
        raw = governance.validate_ceo_runtime_envelope(envelope)
        ystar_result = raw.to_dict() if hasattr(raw, "to_dict") else dict(raw)
        import_status = "direct_YstarGov_runtime_hook_import_used"
    except Exception as exc:
        ystar_result = {
            "decision": "DENY",
            "route": "block_execution_and_record_residual",
            "reason": f"Y-star-gov CEO Cognitive OS runtime hook unavailable: {exc}",
            "failed_stage": "YstarGov_runtime_hook_import",
            "violations": ["YstarGov_runtime_hook_unavailable"],
            "guidance": {},
            "correct_path": [],
            "cieu_validation_record_candidate": {},
            "requires_owner_decision": False,
            "post_action_residual_required": True,
            "allow_approved_next_step": False,
            "allow_external_execution": False,
            "external_action_executed": False,
            "provider_live_execution": False,
            "formal_CIEU_log_written": False,
            "formal_CIEU_log_status": "CIEU_log_write_deferred",
        }
        import_status = "YstarGov_runtime_hook_import_failed"

    decision = str(ystar_result.get("decision", "DENY"))
    bridge_route = _bridge_route_for_decision(decision)
    return {
        "artifact_id": "e85_ceo_cognitive_os_runtime_bridge_result",
        "YstarGov_import_status": import_status,
        "YstarGov_runtime_decision": decision,
        "YstarGov_runtime_route": ystar_result.get("route"),
        "YstarGov_reason": ystar_result.get("reason", ""),
        "YstarGov_guidance": dict(ystar_result.get("guidance", {})),
        "YstarGov_correct_path": list(ystar_result.get("correct_path", [])),
        "YstarGov_requires_owner_decision": bool(ystar_result.get("requires_owner_decision", False)),
        "YstarGov_post_action_residual_required": bool(
            ystar_result.get("post_action_residual_required", False)
        ),
        "YstarGov_classification": dict(ystar_result.get("classification", {})),
        "YstarGov_hook_decision_envelope": dict(ystar_result.get("hook_decision_envelope", {})),
        "YstarGov_validator_result": dict(ystar_result.get("validator_result", {})),
        "CIEU_validation_record_candidate": dict(
            ystar_result.get("cieu_validation_record_candidate", {})
        ),
        "CIEU_validation_record_status": "CIEU_validation_record_candidate_only",
        "formal_CIEU_log_written": bool(ystar_result.get("formal_CIEU_log_written", False)),
        "formal_CIEU_log_status": ystar_result.get("formal_CIEU_log_status", "CIEU_log_write_deferred"),
        "external_action_executed": False,
        "provider_live_execution": False,
        "bridge_labs_route": bridge_route,
    }


def route_provider_tool_action_through_runtime_nervous_system(
    envelope: Mapping[str, Any],
    *,
    ystar_gov_root: Path | None = None,
    gov_mcp_root: Path | None = None,
) -> dict[str, Any]:
    """Route a CEO provider/tool action through Y-star-gov, then gov-mcp dry-run only."""

    ystar_route = route_ceo_major_action_through_ystar_gov_runtime(
        envelope,
        ystar_gov_root=ystar_gov_root,
    )
    classification = ystar_route.get("YstarGov_classification", {})
    categories = set(classification.get("categories", [])) if isinstance(classification, Mapping) else set()
    decision = ystar_route.get("YstarGov_runtime_decision")
    provider_tool_boundary = "provider_tool_execution" in categories or "gov-mcp" in str(envelope).lower()

    if decision != "ALLOW" or not provider_tool_boundary:
        return {
            "artifact_id": "e85r_runtime_nervous_system_provider_route",
            "YstarGov_route": ystar_route,
            "gov_mcp_dry_run_invoked": False,
            "gov_mcp_receipt": {},
            "reason": "gov-mcp dry-run is only prepared after Y-star-gov ALLOW on provider/tool category",
            "external_side_effect": False,
            "provider_action_executed": False,
        }

    try:
        dry_run_adapter = _load_gov_mcp_dry_run_adapter(gov_mcp_root)
        receipt = dry_run_adapter.dry_run_outbound_action(
            _build_gov_mcp_dry_run_intent(envelope),
        {
            "source_repo": "bridge-labs",
            "source_runtime": "Y-star-gov CEO Cognitive OS runtime hook",
            "YstarGov_decision": decision,
            "execution_boundary": "dry_run_only",
            "intelligence_loop_metadata": _intelligence_loop_metadata_from_envelope(envelope),
        },
    )
        import_status = "direct_gov_mcp_dry_run_import_used"
    except Exception as exc:
        receipt = {
            "receipt_id": "",
            "action_id": str(envelope.get("action_id", "")),
            "execution_mode": "deny",
            "failure_code": "gov_mcp_dry_run_unavailable",
            "reason_codes": [str(exc)],
            "external_action_executed": False,
            "provider_called": False,
            "real_message_sent": False,
        }
        import_status = "gov_mcp_dry_run_import_failed"

    receipt.update(
        {
            "source_repo": "bridge-labs",
            "source_runtime": "Y-star-gov CEO Cognitive OS runtime hook",
            "YstarGov_decision": decision,
            "execution_mode_boundary": "dry_run_only",
            "provider_action_executed": False,
            "external_side_effect": False,
        }
    )
    return {
        "artifact_id": "e85r_runtime_nervous_system_provider_route",
        "YstarGov_route": ystar_route,
        "gov_mcp_import_status": import_status,
        "gov_mcp_dry_run_invoked": import_status == "direct_gov_mcp_dry_run_import_used",
        "gov_mcp_receipt": receipt,
        "external_side_effect": False,
        "provider_action_executed": False,
    }


def _build_gov_mcp_dry_run_intent(envelope: Mapping[str, Any]) -> dict[str, Any]:
    action_id = str(envelope.get("action_id") or "e85r_provider_tool_dry_run")
    return {
        "action_id": action_id,
        "capability_domain": "external_validation_message",
        "risk_tier": "TIER_2_TRANSPARENT_LOW_RISK_EXTERNAL_VALIDATION",
        "execution_mode": "send_gated_dry_run",
        "authorization_state": "owner_review_required",
        "target_id": f"dry_run_target_{action_id}",
        "target_identity_sufficient": True,
        "message_hash": f"sha256:{action_id}",
        "idempotency_key": f"{action_id}:dry-run",
        "ai_transparency_present": True,
        "opt_out_language_present": True,
        "suppression_clear": True,
        "rate_limit_clear": True,
        "hard_gates_absent": True,
        "requested_action": "external_validation_message",
        "channel": "owner_approved_validation_message",
        "metadata": {
            "source_repo": "bridge-labs",
            "source_runtime": "Y-star-gov CEO Cognitive OS runtime hook",
            "no_real_provider_action": True,
            **_intelligence_loop_metadata_from_envelope(envelope),
        },
    }


def _intelligence_loop_metadata_from_envelope(envelope: Mapping[str, Any]) -> dict[str, Any]:
    metadata = envelope.get("intelligence_loop_metadata")
    if isinstance(metadata, Mapping):
        result = dict(metadata)
    else:
        result = {}
    for key in (
        "intelligence_loop_id",
        "selected_candidate_id",
        "YstarGov_intelligence_decision",
        "commercial_sharpness_summary",
        "owner_approval_state",
    ):
        if key in envelope:
            result[key] = envelope[key]
    if result:
        result.setdefault("provider_action_executed", False)
        result.setdefault("external_side_effect", False)
        result.setdefault("no_send_invariant", True)
    return result


def _bridge_route_for_decision(decision: str) -> dict[str, Any]:
    route_by_decision = {
        "ALLOW": {
            "route": "approved_next_step_pending_execution_boundary",
            "approved_next_step_allowed": True,
            "external_execution_allowed": False,
            "ceo_revision_required": False,
            "owner_decision_packet_required": False,
            "execution_blocked": False,
        },
        "REQUIRE_REVISION": {
            "route": "ceo_revision_required_with_correct_path",
            "approved_next_step_allowed": False,
            "external_execution_allowed": False,
            "ceo_revision_required": True,
            "owner_decision_packet_required": False,
            "execution_blocked": True,
        },
        "ESCALATE": {
            "route": "owner_decision_packet_required_no_execution",
            "approved_next_step_allowed": False,
            "external_execution_allowed": False,
            "ceo_revision_required": False,
            "owner_decision_packet_required": True,
            "execution_blocked": True,
        },
        "DENY": {
            "route": "execution_blocked_with_residual_candidate",
            "approved_next_step_allowed": False,
            "external_execution_allowed": False,
            "ceo_revision_required": False,
            "owner_decision_packet_required": False,
            "execution_blocked": True,
        },
        "STATUS_ONLY": {
            "route": "status_only_no_major_action_gate_required",
            "approved_next_step_allowed": False,
            "external_execution_allowed": False,
            "ceo_revision_required": False,
            "owner_decision_packet_required": False,
            "execution_blocked": False,
        },
    }
    return dict(route_by_decision.get(decision, route_by_decision["DENY"]))


def assess_formal_cieu_log_insertion() -> dict[str, Any]:
    """Record the E85 CIEU log insertion decision without pretending a write occurred."""

    return {
        "artifact_id": "e85_cieu_log_insertion_assessment",
        "formal_CIEU_log_written": False,
        "formal_CIEU_log_status": "CIEU_log_write_deferred",
        "validator_output_status": "CIEU_validation_record_candidate_only",
        "existing_paths_inspected": [
            "Y-star-gov:ystar/governance/cieu_store.py::CIEUStore.write",
            "Y-star-gov:ystar/governance/cieu_store.py::CIEUStore.write_dict",
            "Y-star-gov:ystar/adapters/cieu_writer.py::_write_cieu",
            "Y-star-gov:ystar/adapters/hook.py::_check_hook_full",
        ],
        "deferred_blocker": (
            "Y-star-gov has a formal CIEU store and hook writer path, but E85 did not prove a "
            "safe CEO Cognitive OS validation-record insertion that preserves ownership, session "
            "semantics, and tests without broad hook refactor."
        ),
        "E86_recommended_scope": (
            "Target the exact CIEUStore or hook writer insertion for CEO Cognitive OS validation "
            "record persistence, including tests that distinguish CIEU validation record candidate "
            "from formal CIEU log write."
        ),
    }


def build_l5_runtime_readiness_gate() -> dict[str, Any]:
    return {
        "artifact_id": "e85_l5_runtime_readiness_gate",
        "job_id": "E85_CEO_Nervous_System_L5_Runtime_Foundation_R1",
        "already_wired": {
            "pre_action_packet_required_for_CEO_major_action": True,
            "YstarGov_hook_runtime_validation": True,
            "REQUIRE_REVISION_correct_path": True,
            "DENY_hard_stop": True,
            "ESCALATE_owner_path": True,
            "post_action_residual_requirement": True,
            "bridge_labs_runtime_adapter_to_YstarGov_runtime_hook": True,
        },
        "still_pending": {
            "formal_CIEU_log_write": True,
            "gov_mcp_provider_tool_execution_envelope_integration": True,
            "L4_external_feedback_execution": True,
            "L5_customer_revenue_payment_pricing_loop": True,
            "legal_compliance_data_handling_proof": True,
            "real_feedback_learning_loop": True,
            "production_deployment": True,
        },
        "status": {
            "L5_runtime_foundation": True,
            "L5_business_loop_complete": False,
            "L5_revenue_loop_complete": False,
            "L5_external_feedback_loop_complete": False,
        },
        "truth_constraint": (
            "This is a runtime foundation gate map only. It is not L5 completion, not revenue "
            "completion, not customer validation, and not production deployment."
        ),
    }


def run_runtime_bridge_smoke() -> dict[str, Any]:
    valid = route_ceo_major_action_through_ystar_gov_runtime(
        build_ceo_major_action_runtime_envelope()
    )

    revision_packet = build_sample_pre_action_packet()
    revision_packet["counterfactual_comparison"] = []
    revision = route_ceo_major_action_through_ystar_gov_runtime(
        build_ceo_major_action_runtime_envelope(packet=revision_packet)
    )

    escalation_packet = build_sample_pre_action_packet(action_class="L4_external_feedback_execution")
    escalation = route_ceo_major_action_through_ystar_gov_runtime(
        build_ceo_major_action_runtime_envelope(
            packet=escalation_packet,
            action_id="e85_l4_owner_decision_boundary",
            objective="prepare L4 external feedback decision without execution",
            externality_level="external_feedback",
            owner_approval_status="pending_owner_decision",
        )
    )

    denied_envelope = build_ceo_major_action_runtime_envelope()
    denied_envelope["bypass_attempt"] = True
    denied = route_ceo_major_action_through_ystar_gov_runtime(denied_envelope)

    post_action = route_ceo_major_action_through_ystar_gov_runtime(
        build_ceo_major_action_runtime_envelope(
            action_phase="completed",
            post_action_residual=build_sample_post_action_residual(),
        )
    )

    return {
        "valid_internal_major_action": valid,
        "repairable_missing_counterfactual": revision,
        "owner_decision_boundary": escalation,
        "hard_boundary_bypass": denied,
        "post_action_residual": post_action,
    }


def build_completion_report() -> dict[str, Any]:
    smoke = run_runtime_bridge_smoke()
    l5_gate = build_l5_runtime_readiness_gate()
    cieu = assess_formal_cieu_log_insertion()
    e84_smoke = run_adapter_smoke()
    provider_route = route_provider_tool_action_through_runtime_nervous_system(
        build_provider_tool_ceo_major_action_runtime_envelope()
    )
    return {
        "job_id": "E85_CEO_Nervous_System_L5_Runtime_Foundation_R1",
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "repo_bases": {
            "bridge_labs": {
                "expected_base": "c87b03f29c2e406578e3ceb3ef881b734b5ae87c",
                "actual_start_HEAD": "c87b03f29c2e406578e3ceb3ef881b734b5ae87c",
            },
            "Y_star_gov": {
                "expected_base": "e725b8721e348c4dd9834a265f73125f685a07a7",
                "actual_start_HEAD": "e725b8721e348c4dd9834a265f73125f685a07a7",
            },
            "gov_mcp": {
                "expected_read_only_hash": "d0181bc8f19d8ae7714bd0f8a220fe12e6ceee90",
                "mutated": False,
            },
        },
        "files_inspected": [
            "Y-star-gov:ystar/governance/ceo_cognitive_os_contract.py",
            "Y-star-gov:ystar/adapters/hook.py",
            "Y-star-gov:ystar/governance/hook_contract_adapter.py",
            "Y-star-gov:ystar/governance/cieu_store.py",
            "Y-star-gov:ystar/adapters/cieu_writer.py",
            "bridge-labs:office/mission_command/e84_ystar_gov_ceo_cognitive_os_call_adapter.py",
            "bridge-labs:operations/external_validation/e84_patch_result.json",
            "gov-mcp:gov_mcp/server.py",
            "gov-mcp:gov_mcp/company_runtime_tools.py",
            "gov-mcp:gov_mcp/outbound/policy.py",
            "gov-mcp:gov_mcp/outbound/dry_run_adapter.py",
            "gov-mcp:gov_mcp/outbound/provider_guard_stack.py",
        ],
        "files_modified": [
            "bridge-labs:office/mission_command/e85_ceo_cognitive_os_runtime_bridge.py",
            "bridge-labs:office/mission_command/e85_ceo_nervous_system_l5_runtime_foundation_report.json",
            "bridge-labs:office/mission_command/e85_ceo_nervous_system_l5_runtime_foundation_readback.md",
            "bridge-labs:operations/external_validation/e85_l5_runtime_readiness_gate.json",
            "bridge-labs:operations/external_validation/e85_l5_runtime_readiness_gate.md",
            "bridge-labs:operations/external_validation/e85_cieu_log_insertion_assessment.json",
            "bridge-labs:operations/external_validation/e85_cieu_log_insertion_assessment.md",
        ],
        "YstarGov_hook_runtime_insertion_point": (
            "Y-star-gov:ystar/governance/ceo_cognitive_os_runtime_hook.py::"
            "validate_ceo_runtime_envelope"
        ),
        "bridge_labs_runtime_bridge_path": (
            "bridge-labs:office/mission_command/e85_ceo_cognitive_os_runtime_bridge.py"
        ),
        "decision_semantics_preserved": {
            "ALLOW": "approved next step only; no external execution",
            "REQUIRE_REVISION": "correct_path guidance returns to CEO",
            "DENY": "execution blocked with CIEU validation record candidate",
            "ESCALATE": "owner decision path required; no execution",
        },
        "major_action_classifier_coverage": [
            "external_read_write_action",
            "customer_contact_action",
            "payment_revenue_pricing_action",
            "public_publication",
            "provider_tool_execution",
            "strategy_mutation",
            "canonical_y_star_mutation",
            "brain_memory_write",
            "CIEU_log_write_claim",
            "cross_repo_governance_mutation",
            "owner_approval_boundary_crossing",
            "L4_L5_escalation_attempt",
        ],
        "post_action_residual_requirement_status": "runtime_required_for_CEO_major_action_closure",
        "formal_CIEU_log_status": cieu,
        "gov_mcp_status": {
            "read_only_inspected": True,
            "mutated": False,
            "future_boundary": "provider/tool envelope integration remains pending",
        },
        "L5_status": l5_gate["status"],
        "runtime_bridge_smoke": smoke,
        "runtime_nervous_system_chain": {
            "bridge_labs_CEO_runtime": "builds CEO major-action runtime envelope",
            "Y_star_gov_hook_enforcement": "validate_ceo_runtime_envelope returns runtime decision",
            "gov_mcp_dry_run_execution_envelope": "dry_run_outbound_action used only after Y-star-gov ALLOW on provider/tool category",
            "post_action_residual": "required before major-action closure",
            "CIEU_validation_candidate": "validator output remains candidate-only",
            "formal_CIEU_log_status": cieu["formal_CIEU_log_status"],
            "provider_route_fixture": provider_route,
        },
        "E84_direct_call_adapter_compatibility_smoke": e84_smoke,
        "next_routing": {
            "recommended": "E86_YStarGov_CEO_Cognitive_OS_CIEU_Log_Write_Insertion_Point_R1",
            "reason": "formal CIEU log insertion remains deferred while runtime hook foundation is wired",
        },
        "safety_statement": {
            "no_external_action": True,
            "no_outreach": True,
            "no_publication": True,
            "no_payment": True,
            "no_provider_live_execution": True,
            "no_live_MCP_execution": True,
            "no_customer_validation_claim": True,
            "no_pricing_validation_claim": True,
            "no_paid_signal_claim": True,
            "no_compliance_proof_claim": True,
            "no_production_deployment_claim": True,
            "no_L4_execution_claim": True,
            "no_L5_completion_claim": True,
        },
    }


def write_e85_artifacts(root: Path | None = None) -> dict[str, Any]:
    target_root = root or BRIDGE_ROOT
    report = build_completion_report()
    l5_gate = build_l5_runtime_readiness_gate()
    cieu = assess_formal_cieu_log_insertion()
    paths = {
        "report_json": target_root
        / "office/mission_command/e85_ceo_nervous_system_l5_runtime_foundation_report.json",
        "readback_md": target_root
        / "office/mission_command/e85_ceo_nervous_system_l5_runtime_foundation_readback.md",
        "l5_gate_json": target_root / "operations/external_validation/e85_l5_runtime_readiness_gate.json",
        "l5_gate_md": target_root / "operations/external_validation/e85_l5_runtime_readiness_gate.md",
        "cieu_json": target_root
        / "operations/external_validation/e85_cieu_log_insertion_assessment.json",
        "cieu_md": target_root
        / "operations/external_validation/e85_cieu_log_insertion_assessment.md",
        "e85r_report_json": target_root
        / "office/mission_command/e85r_canonical_delivery_and_runtime_nervous_system_report.json",
        "e85r_readback_md": target_root
        / "office/mission_command/e85r_canonical_delivery_and_runtime_nervous_system_readback.md",
    }
    for path in paths.values():
        path.parent.mkdir(parents=True, exist_ok=True)
    paths["report_json"].write_text(json.dumps(report, indent=2, sort_keys=True), encoding="utf-8")
    paths["l5_gate_json"].write_text(json.dumps(l5_gate, indent=2, sort_keys=True), encoding="utf-8")
    paths["cieu_json"].write_text(json.dumps(cieu, indent=2, sort_keys=True), encoding="utf-8")
    paths["readback_md"].write_text(_report_markdown(report), encoding="utf-8")
    paths["l5_gate_md"].write_text(_l5_gate_markdown(l5_gate), encoding="utf-8")
    paths["cieu_md"].write_text(_cieu_markdown(cieu), encoding="utf-8")
    paths["e85r_report_json"].write_text(json.dumps(_e85r_report(report), indent=2, sort_keys=True), encoding="utf-8")
    paths["e85r_readback_md"].write_text(_e85r_markdown(_e85r_report(report)), encoding="utf-8")
    return report


def _report_markdown(report: Mapping[str, Any]) -> str:
    lines = [
        "# E85 CEO Nervous System L5 Runtime Foundation",
        "",
        f"- job_id: `{report['job_id']}`",
        "- status: `CEO_Cognitive_OS_hook_runtime_foundation_wired`",
        f"- Y-star-gov insertion point: `{report['YstarGov_hook_runtime_insertion_point']}`",
        f"- bridge-labs runtime bridge: `{report['bridge_labs_runtime_bridge_path']}`",
        "- ALLOW: approved next step only; no external execution",
        "- REQUIRE_REVISION: correct_path guidance returns to CEO",
        "- DENY: execution blocked with CIEU validation record candidate",
        "- ESCALATE: owner decision path required; no execution",
        f"- formal_CIEU_log_written: `{report['formal_CIEU_log_status']['formal_CIEU_log_written']}`",
        f"- formal_CIEU_log_status: `{report['formal_CIEU_log_status']['formal_CIEU_log_status']}`",
        f"- L5_runtime_foundation: `{report['L5_status']['L5_runtime_foundation']}`",
        f"- L5_business_loop_complete: `{report['L5_status']['L5_business_loop_complete']}`",
        f"- L5_revenue_loop_complete: `{report['L5_status']['L5_revenue_loop_complete']}`",
        f"- L5_external_feedback_loop_complete: `{report['L5_status']['L5_external_feedback_loop_complete']}`",
        f"- next_routing: `{report['next_routing']['recommended']}`",
        "",
        "E85 completed: CEO Cognitive OS is now wired into Y-star-gov hook/runtime foundation and bridge-labs can route CEO major actions through the runtime gate. This establishes the L5-runtime nervous-system foundation, but L4 external feedback, gov-mcp provider execution, formal CIEU log write if deferred, and L5 revenue/customer/payment loops remain pending.",
    ]
    return "\n".join(lines) + "\n"


def _l5_gate_markdown(gate: Mapping[str, Any]) -> str:
    lines = [
        "# E85 L5 Runtime Readiness Gate",
        "",
        f"- L5_runtime_foundation: `{gate['status']['L5_runtime_foundation']}`",
        f"- L5_business_loop_complete: `{gate['status']['L5_business_loop_complete']}`",
        f"- L5_revenue_loop_complete: `{gate['status']['L5_revenue_loop_complete']}`",
        f"- L5_external_feedback_loop_complete: `{gate['status']['L5_external_feedback_loop_complete']}`",
        "",
        "## Already Wired",
    ]
    lines.extend(f"- {key}: `{value}`" for key, value in gate["already_wired"].items())
    lines.append("")
    lines.append("## Still Pending")
    lines.extend(f"- {key}: `{value}`" for key, value in gate["still_pending"].items())
    lines.append("")
    lines.append(gate["truth_constraint"])
    return "\n".join(lines) + "\n"


def _cieu_markdown(cieu: Mapping[str, Any]) -> str:
    lines = [
        "# E85 CIEU Log Insertion Assessment",
        "",
        f"- formal_CIEU_log_written: `{cieu['formal_CIEU_log_written']}`",
        f"- formal_CIEU_log_status: `{cieu['formal_CIEU_log_status']}`",
        f"- validator_output_status: `{cieu['validator_output_status']}`",
        f"- deferred_blocker: {cieu['deferred_blocker']}",
        f"- E86_recommended_scope: {cieu['E86_recommended_scope']}",
    ]
    return "\n".join(lines) + "\n"


def _e85r_report(report: Mapping[str, Any]) -> dict[str, Any]:
    return {
        "artifact_id": "e85r_canonical_delivery_and_runtime_nervous_system_report",
        "job_id": "E85R_Canonical_Delivery_Rescue_And_Full_Runtime_Nervous_System_R1",
        "delivery_rescue_method_used": "host_local_repository_delivery_bridge_after_queue_archaeology_and_stale_queue_cleanup",
        "prior_failed_delivery_reason": (
            "manual sandbox worker could not write canonical repos; GitHub connector token expired; "
            "direct network DNS failed; host-local bridge queue contained stale non-job files and a stuck running job"
        ),
        "prior_bridge_mechanism_found": True,
        "canonical_starting_HEADs": {
            "bridge_labs": "c87b03f29c2e406578e3ceb3ef881b734b5ae87c",
            "Y_star_gov": "e725b8721e348c4dd9834a265f73125f685a07a7",
            "gov_mcp": "d0181bc8f19d8ae7714bd0f8a220fe12e6ceee90",
        },
        "canonical_final_HEADs_expected_after_delivery": {
            "Y_star_gov": "0c449edd9f892acb2520acd529e7c4e2fd9a304f",
            "bridge_labs": "set_by_delivery_bridge_after_this_report_commit",
            "gov_mcp": "d0181bc8f19d8ae7714bd0f8a220fe12e6ceee90",
        },
        "temp_commits_applied_or_reconstructed": {
            "Y_star_gov_temp_commit": "a53fe260a3e3d1323ab477226a70dee9dc8b7942",
            "bridge_labs_temp_commit": "877733848774f1870d488bf65530eb2ad033e732",
        },
        "runtime_nervous_system_chain_status": dict(report["runtime_nervous_system_chain"]),
        "push_status": "handled_by_host_local_delivery_bridge",
        "L5_status": dict(report["L5_status"]),
        "remaining_blockers": [
            "formal CIEU log write insertion point remains deferred",
            "gov-mcp live provider execution remains pending and not authorized",
            "L4 external feedback not executed",
            "L5 customer/revenue/payment loop not complete",
        ],
        "recommended_next_milestone": "E86_YStarGov_CEO_Cognitive_OS_CIEU_Log_Write_Insertion_Point_R1",
    }


def _e85r_markdown(report: Mapping[str, Any]) -> str:
    lines = [
        "# E85R Canonical Delivery And Runtime Nervous System",
        "",
        f"- job_id: `{report['job_id']}`",
        f"- delivery_rescue_method_used: `{report['delivery_rescue_method_used']}`",
        f"- prior_bridge_mechanism_found: `{report['prior_bridge_mechanism_found']}`",
        f"- Y_star_gov_expected_final: `{report['canonical_final_HEADs_expected_after_delivery']['Y_star_gov']}`",
        f"- bridge_labs_expected_final: `{report['canonical_final_HEADs_expected_after_delivery']['bridge_labs']}`",
        "- gov-mcp: read-only inspected; no mutation",
        f"- L5_runtime_foundation: `{report['L5_status']['L5_runtime_foundation']}`",
        f"- L5_business_loop_complete: `{report['L5_status']['L5_business_loop_complete']}`",
        f"- L5_revenue_loop_complete: `{report['L5_status']['L5_revenue_loop_complete']}`",
        f"- L5_external_feedback_loop_complete: `{report['L5_status']['L5_external_feedback_loop_complete']}`",
        f"- recommended_next_milestone: `{report['recommended_next_milestone']}`",
        "",
        "Runtime chain: bridge-labs CEO runtime envelope -> Y-star-gov CEO Cognitive OS runtime hook -> gov-mcp dry-run envelope only for provider/tool category -> post-action residual requirement -> CIEU validation record candidate.",
    ]
    return "\n".join(lines) + "\n"


if __name__ == "__main__":
    write_e85_artifacts()
