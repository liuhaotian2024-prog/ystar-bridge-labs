#!/usr/bin/env python3
"""Run a governed read-only tool invocation through the Pre-U bridge."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from governed_readonly_observation_tool.tools import run_readonly_observation_tool as readonly_tool


PACK = ROOT / "governed_tool_invocation_bridge"
GENERATED = PACK / "generated"
BRIDGE_ID = "governed_tool_invocation_bridge_v0"
TOOL_ID = "governed_readonly_observation_tool_v0"
NEXT_MILESTONE = "L4.6 Agent Team Work Proposal to Governed Tool Invocation v0"

BRIDGE_CONTRACT_REF = "governed_tool_invocation_bridge/generated/bridge_contract.json"
REQUEST_REF = "governed_tool_invocation_bridge/generated/agent_tool_request.json"
PRE_U_REF = "governed_tool_invocation_bridge/generated/pre_u_tool_packet.json"
DECISION_REF = "governed_tool_invocation_bridge/generated/governance_decision_envelope.json"
AUTHORIZATION_REF = "governed_tool_invocation_bridge/generated/bridge_authorization.json"
BRIDGED_RESULT_REF = "governed_tool_invocation_bridge/generated/bridged_tool_result.json"
TRACE_REF = "governed_tool_invocation_bridge/generated/bridge_invocation_trace.json"
CIEU_EVENT_REF = "governed_tool_invocation_bridge/generated/bridge_cieu_event.json"
RESIDUAL_DELTA_REF = "governed_tool_invocation_bridge/generated/bridge_residual_delta.json"
DIRECT_REJECTION_REF = "governed_tool_invocation_bridge/generated/rejected_direct_tool_invocation.json"
UNSAFE_REJECTION_REF = "governed_tool_invocation_bridge/generated/rejected_unsafe_bridge_request.json"

LOCAL_READONLY_DECISION = "allow_local_readonly_tool_invocation"


class BridgePolicyError(Exception):
    """Raised when the bridge policy rejects a request before tool invocation."""


def write_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


def load_json(path: Path) -> dict[str, Any]:
    data = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(data, dict):
        raise ValueError(f"Expected object JSON: {path}")
    return data


def repo_path(relative_path: str) -> Path:
    candidate = Path(relative_path)
    if candidate.is_absolute():
        raise BridgePolicyError(f"absolute path rejected: {relative_path}")
    resolved = (ROOT / candidate).resolve()
    try:
        resolved.relative_to(ROOT)
    except ValueError as exc:
        raise BridgePolicyError(f"path escapes repository root: {relative_path}") from exc
    return resolved


def output_dir_path(relative_path: str) -> Path:
    path = repo_path(relative_path)
    expected = (ROOT / "governed_tool_invocation_bridge" / "generated").resolve()
    try:
        path.relative_to(expected)
    except ValueError as exc:
        raise BridgePolicyError("output directory must be governed_tool_invocation_bridge/generated") from exc
    return path


def build_bridge_contract() -> dict[str, Any]:
    return {
        "schema_name": "ystar.governed_tool_invocation_bridge.generated.bridge_contract",
        "schema_version": "v0",
        "bridge_id": BRIDGE_ID,
        "bridge_name": "Governed Tool Invocation Through Pre-U Bridge",
        "bridge_version": "v0",
        "supported_tool_id": TOOL_ID,
        "agent_direct_tool_invocation_allowed": False,
        "pre_u_packet_required": True,
        "governance_decision_required": True,
        "bridge_authorization_required": True,
        "cieu_event_required": True,
        "residual_delta_required": True,
        "requires_y_star_gov": True,
        "requires_operator_approval_for_local_readonly": False,
        "requires_operator_approval_for_live": True,
        "live_enabled": False,
        "external_action_enabled": False,
        "network_enabled": False,
        "git_push_enabled": False,
        "daemon_control_enabled": False,
        "cieu_persistence_enabled": False,
        "brain_writeback_enabled": False,
        "memory_ingestion_enabled": False,
        "email_or_external_communication_enabled": False,
        "allowed_decisions": [
            "allow_local_readonly_tool_invocation",
            "require_revision",
            "deny",
        ],
        "denied_paths_policy": [
            "no DB/WAL/SHM",
            "no logs",
            "no active-agent markers",
            "no raw runtime artifacts",
            "no memory/WORLD_STATE.md",
            "no BOARD_PENDING.md",
            "no external network",
            "no external communication",
        ],
        "status": "defined_disabled_for_live_but_callable_for_local_readonly_dry_run",
    }


def build_agent_tool_request() -> dict[str, Any]:
    return {
        "schema_name": "ystar.governed_tool_invocation_bridge.generated.agent_tool_request",
        "schema_version": "v0",
        "request_id": "agent-tool-request-001",
        "requesting_agent": "Aiden-CEO",
        "supporting_agent": "Samantha-Secretary",
        "mission_id": "mission-commercial-agent-company-v0",
        "tool_id": TOOL_ID,
        "request_type": "company_state_observation",
        "business_reason": "Produce a governed company-state observation before selecting the next autonomy work item.",
        "declared_intent": "Observe safe generated summaries through the governed read-only tool via Pre-U bridge.",
        "requested_summary_level": "executive",
        "requested_sources": [
            "mission-dashboard",
            "company-state-digest",
            "observation-loop-summary",
            "legacy-triage-summary",
            "autonomous-cycle-summary",
            "autonomy-inventory-summary",
            "live-boundary-summary",
            "cieu-boundary-summary",
        ],
        "risk_tier": "low",
        "live_action_requested": False,
        "external_action_requested": False,
        "brain_writeback_requested": False,
        "memory_ingestion_requested": False,
        "cieu_persistence_requested": False,
    }


def build_pre_u_tool_packet(request: dict[str, Any]) -> dict[str, Any]:
    safe_request = (
        request.get("risk_tier") == "low"
        and request.get("tool_id") == TOOL_ID
        and not any(
            request.get(field) is True
            for field in [
                "live_action_requested",
                "external_action_requested",
                "brain_writeback_requested",
                "memory_ingestion_requested",
                "cieu_persistence_requested",
            ]
        )
    )
    candidate_u = [
        {
            "u_id": "U1",
            "summary": "invoke governed read-only observation tool through bridge",
            "local_readonly": True,
            "live_enabled": False,
            "expected_residual": "lowest_when_request_is_safe",
        },
        {
            "u_id": "U2",
            "summary": "defer invocation and request revision",
            "local_readonly": True,
            "live_enabled": False,
            "expected_residual": "medium_when_more_context_is_needed",
        },
        {
            "u_id": "U3",
            "summary": "deny invocation due to unsafe request",
            "local_readonly": False,
            "live_enabled": False,
            "expected_residual": "lowest_when_request_is_unsafe",
        },
    ]
    selected = candidate_u[0] if safe_request else candidate_u[2]
    return {
        "schema_name": "ystar.governed_tool_invocation_bridge.generated.pre_u_tool_packet",
        "schema_version": "v0",
        "packet_id": "pre-u-tool-packet-001",
        "agent_id": request.get("requesting_agent"),
        "tool_id": request.get("tool_id"),
        "request_id": request.get("request_id"),
        "Xt": {
            "request_type": request.get("request_type"),
            "supporting_agent": request.get("supporting_agent"),
            "requested_summary_level": request.get("requested_summary_level"),
            "requested_sources": request.get("requested_sources", []),
        },
        "Y_star": "Use governed local read-only observation to reduce uncertainty without live or external action.",
        "candidate_U": candidate_u,
        "predicted_Y_t1": "A normalized company-state observation is available for next work selection.",
        "predicted_R_t1": "Residual risk remains bounded because all live and writeback paths are disabled.",
        "selected_U": selected,
        "why_min_residual": (
            "Selected local read-only invocation because request is low-risk and forbids live/external/writeback behavior."
            if safe_request
            else "Selected denial because request was unsafe for local read-only invocation."
        ),
        "risk_tier": request.get("risk_tier"),
        "governance_expectations": {
            "requires_y_star_gov": True,
            "requires_bridge_authorization": True,
            "agent_direct_tool_invocation_allowed": False,
        },
        "cieu_link_policy": {
            "cieu_event_required": True,
            "persistence_enabled": False,
            "curation_required": True,
        },
        "tool_contract_ref": "governed_readonly_observation_tool/generated/tool_contract.json",
        "allowed_source_registry_ref": "governed_readonly_observation_tool/generated/allowed_source_registry.json",
    }


def build_governance_decision_envelope(packet: dict[str, Any]) -> dict[str, Any]:
    selected_id = packet.get("selected_U", {}).get("u_id")
    decision = LOCAL_READONLY_DECISION if selected_id == "U1" else "deny"
    return {
        "schema_name": "ystar.governed_tool_invocation_bridge.generated.governance_decision_envelope",
        "schema_version": "v0",
        "decision_id": "governance-decision-tool-bridge-001",
        "packet_id": packet.get("packet_id"),
        "decision": decision,
        "decision_reason": "Local deterministic bridge decision allows only the safe read-only tool path.",
        "allowed_only_as_local_readonly_dry_run": decision == LOCAL_READONLY_DECISION,
        "agent_direct_tool_invocation_allowed": False,
        "live_action_allowed": False,
        "external_action_allowed": False,
        "cieu_persistence_allowed": False,
        "brain_writeback_allowed": False,
        "memory_ingestion_allowed": False,
        "operator_approval_required_for_live": True,
        "notes": (
            "This L4.5 decision envelope is deterministic and local. It references existing dry-run "
            "governance posture but does not edit or invoke external repositories."
        ),
    }


def build_bridge_authorization(
    request: dict[str, Any],
    packet: dict[str, Any],
    decision: dict[str, Any],
    registry: dict[str, dict[str, Any]],
) -> dict[str, Any]:
    requested = request.get("requested_sources", [])
    allowed_sources = [source_id for source_id in requested if source_id in registry]
    denied_sources = [
        {"source_id": source_id, "reason": "source_not_in_allowed_registry"}
        for source_id in requested
        if source_id not in registry
    ]
    authorized = (
        decision.get("decision") == LOCAL_READONLY_DECISION
        and decision.get("allowed_only_as_local_readonly_dry_run") is True
        and not denied_sources
    )
    return {
        "schema_name": "ystar.governed_tool_invocation_bridge.generated.bridge_authorization",
        "schema_version": "v0",
        "authorization_id": "bridge-authorization-001",
        "packet_id": packet.get("packet_id"),
        "decision_id": decision.get("decision_id"),
        "tool_id": request.get("tool_id"),
        "authorized": authorized,
        "authorized_only_for_local_readonly_dry_run": authorized,
        "agent_direct_tool_invocation_allowed": False,
        "allowed_sources": allowed_sources,
        "denied_sources": denied_sources,
        "live_action_allowed": False,
        "external_action_allowed": False,
        "cieu_persistence_allowed": False,
        "brain_writeback_allowed": False,
        "memory_ingestion_allowed": False,
        "notes": "Authorization is scoped to local read-only dry-run invocation through the bridge only.",
    }


def build_direct_invocation_rejection() -> dict[str, Any]:
    return {
        "schema_name": "ystar.governed_tool_invocation_bridge.generated.rejected_direct_tool_invocation",
        "schema_version": "v0",
        "rejection_id": "rejected-direct-tool-invocation-001",
        "status": "rejected",
        "reason": "agent_direct_tool_invocation_disallowed_pre_u_bridge_required",
        "agent_direct_tool_invocation_allowed": False,
        "pre_u_packet_required": True,
        "governance_decision_required": True,
        "tool_invoked": False,
        "real_action_executed": False,
        "external_action_executed": False,
        "live_action_enabled": False,
        "cieu_persistence_enabled": False,
        "brain_writeback_enabled": False,
        "memory_ingestion_enabled": False,
    }


def build_unsafe_bridge_request_rejection() -> dict[str, Any]:
    return {
        "schema_name": "ystar.governed_tool_invocation_bridge.generated.rejected_unsafe_bridge_request",
        "schema_version": "v0",
        "rejection_id": "rejected-unsafe-bridge-request-001",
        "status": "rejected",
        "reason": "unsafe_requested_source_or_operation_rejected_before_tool_invocation",
        "request": {
            "request_id": "unsafe-agent-tool-request-001",
            "tool_id": TOOL_ID,
            "requested_sources": ["unsafe-unregistered-source"],
            "live_action_requested": True,
            "external_action_requested": False,
            "brain_writeback_requested": False,
            "memory_ingestion_requested": False,
            "cieu_persistence_requested": False,
        },
        "blocked_reasons": [
            "source_not_in_allowed_registry",
            "live_action_requested_forbidden",
        ],
        "tool_invoked": False,
        "read_sources": [],
        "real_action_executed": False,
        "external_action_executed": False,
        "live_action_enabled": False,
        "cieu_persistence_enabled": False,
        "brain_writeback_enabled": False,
        "memory_ingestion_enabled": False,
    }


def validate_request_for_bridge(request: dict[str, Any], registry: dict[str, dict[str, Any]]) -> list[dict[str, Any]]:
    blocked: list[dict[str, Any]] = []
    if request.get("tool_id") != TOOL_ID:
        blocked.append({"reason": "unsupported_tool_id", "value": request.get("tool_id")})
    if request.get("attempted_direct_tool_invocation") is True:
        blocked.append({"reason": "direct_tool_invocation_disallowed"})
    for field in [
        "live_action_requested",
        "external_action_requested",
        "brain_writeback_requested",
        "memory_ingestion_requested",
        "cieu_persistence_requested",
    ]:
        if request.get(field) is True:
            blocked.append({"reason": f"{field}_forbidden"})
    for source_id in request.get("requested_sources", []):
        if source_id not in registry:
            blocked.append({"reason": "source_not_in_allowed_registry", "source_id": source_id})
    return blocked


def validate_bridge_authorization(
    contract: dict[str, Any],
    decision: dict[str, Any],
    authorization: dict[str, Any],
) -> list[dict[str, Any]]:
    blocked: list[dict[str, Any]] = []
    if contract.get("agent_direct_tool_invocation_allowed") is not False:
        blocked.append({"reason": "contract_must_disallow_direct_tool_invocation"})
    if decision.get("decision") != LOCAL_READONLY_DECISION:
        blocked.append({"reason": "decision_does_not_allow_local_readonly_invocation"})
    if decision.get("allowed_only_as_local_readonly_dry_run") is not True:
        blocked.append({"reason": "decision_not_scoped_to_local_readonly_dry_run"})
    for field in [
        "live_action_allowed",
        "external_action_allowed",
        "cieu_persistence_allowed",
        "brain_writeback_allowed",
        "memory_ingestion_allowed",
    ]:
        if decision.get(field) is not False:
            blocked.append({"reason": f"decision_must_keep_{field}_false"})
    if authorization.get("authorized") is not True:
        blocked.append({"reason": "bridge_authorization_not_granted"})
    if authorization.get("authorized_only_for_local_readonly_dry_run") is not True:
        blocked.append({"reason": "authorization_not_scoped_to_local_readonly_dry_run"})
    if authorization.get("agent_direct_tool_invocation_allowed") is not False:
        blocked.append({"reason": "authorization_must_disallow_direct_tool_invocation"})
    for field in [
        "live_action_allowed",
        "external_action_allowed",
        "cieu_persistence_allowed",
        "brain_writeback_allowed",
        "memory_ingestion_allowed",
    ]:
        if authorization.get(field) is not False:
            blocked.append({"reason": f"authorization_must_keep_{field}_false"})
    return blocked


def build_tool_invocation(request: dict[str, Any], authorization: dict[str, Any]) -> dict[str, Any]:
    return {
        "schema_name": "ystar.governed_tool_invocation_bridge.generated.bridged_tool_invocation",
        "schema_version": "v0",
        "invocation_id": "bridge-readonly-observation-invocation-001",
        "tool_id": TOOL_ID,
        "requesting_agent": request.get("requesting_agent"),
        "mission_id": request.get("mission_id"),
        "request_type": request.get("request_type"),
        "requested_sources": authorization.get("allowed_sources", []),
        "requested_summary_level": request.get("requested_summary_level"),
        "declared_Y_star": request.get("declared_intent"),
        "risk_tier": request.get("risk_tier"),
        "requires_y_star_gov": True,
        "requires_cieu_event": True,
        "live_action_requested": False,
        "external_action_requested": False,
        "brain_writeback_requested": False,
        "memory_ingestion_requested": False,
        "cieu_persistence_requested": False,
    }


def build_bridged_tool_result(
    tool_result: dict[str, Any],
    packet: dict[str, Any],
    decision: dict[str, Any],
    authorization: dict[str, Any],
) -> dict[str, Any]:
    return {
        "schema_name": "ystar.governed_tool_invocation_bridge.generated.bridged_tool_result",
        "schema_version": "v0",
        "result_id": "bridged-tool-result-001",
        "bridge_id": BRIDGE_ID,
        "invocation_id": tool_result.get("invocation_id"),
        "tool_id": TOOL_ID,
        "status": tool_result.get("status"),
        "pre_u_packet_ref": PRE_U_REF,
        "governance_decision_ref": DECISION_REF,
        "bridge_authorization_ref": AUTHORIZATION_REF,
        "tool_result_ref": BRIDGED_RESULT_REF,
        "read_sources": tool_result.get("read_sources", []),
        "normalized_observation": tool_result.get("normalized_observation", {}),
        "next_work_candidates": tool_result.get("next_work_candidates", []),
        "packet_id": packet.get("packet_id"),
        "decision_id": decision.get("decision_id"),
        "authorization_id": authorization.get("authorization_id"),
        "agent_direct_tool_invocation_allowed": False,
        "real_action_executed": False,
        "external_action_executed": False,
        "live_action_enabled": False,
        "cieu_persistence_enabled": False,
        "brain_writeback_enabled": False,
        "memory_ingestion_enabled": False,
    }


def build_bridge_cieu_event(
    request: dict[str, Any],
    packet: dict[str, Any],
    decision: dict[str, Any],
    bridged_result: dict[str, Any],
) -> dict[str, Any]:
    return {
        "schema_name": "ystar.governed_tool_invocation_bridge.generated.bridge_cieu_event",
        "schema_version": "v0",
        "event_id": "bridge-cieu-event-001",
        "dry_run_only": True,
        "persistence_enabled": False,
        "bridge_id": BRIDGE_ID,
        "tool_id": TOOL_ID,
        "request_id": request.get("request_id"),
        "packet_id": packet.get("packet_id"),
        "decision_id": decision.get("decision_id"),
        "Xt": packet.get("Xt", {}),
        "U": packet.get("selected_U", {}),
        "Y_star": packet.get("Y_star"),
        "predicted_Y_t1": packet.get("predicted_Y_t1"),
        "predicted_R_t1": packet.get("predicted_R_t1"),
        "actual_Y_t1": f"Bridge invoked tool with status {bridged_result.get('status')}.",
        "actual_R_t1": "Invocation remained local read-only with no live, external, CIEU persistence, brain, or memory action.",
        "residual_delta": {
            "status": "dry_run_bridge_delta_only",
            "semantic_truth_status": "not_evaluated",
            "delta_summary": "Pre-U bridge successfully constrained and invoked the read-only tool.",
        },
        "evidence_refs": [
            BRIDGE_CONTRACT_REF,
            PRE_U_REF,
            DECISION_REF,
            AUTHORIZATION_REF,
            BRIDGED_RESULT_REF,
        ],
        "write_policy": {
            "persistence_allowed": False,
            "cieu_write_allowed": False,
            "brain_writeback_allowed": False,
            "memory_ingestion_allowed": False,
        },
        "learning_eligibility": False,
        "curation_required": True,
        "direct_brain_writeback_allowed": False,
        "direct_memory_ingestion_allowed": False,
        "raw_artifact_ingestion_allowed": False,
    }


def build_residual_delta(event: dict[str, Any]) -> dict[str, Any]:
    return {
        "schema_name": "ystar.governed_tool_invocation_bridge.generated.bridge_residual_delta",
        "schema_version": "v0",
        "delta_id": "bridge-residual-delta-001",
        "event_id": event.get("event_id"),
        "predicted_vs_actual_summary": {
            "predicted": event.get("predicted_Y_t1"),
            "actual": event.get("actual_Y_t1"),
            "residual": event.get("actual_R_t1"),
        },
        "residual_delta": event.get("residual_delta"),
        "learning_eligibility": False,
        "curation_required": True,
        "direct_brain_writeback_allowed": False,
        "direct_memory_ingestion_allowed": False,
        "next_review_required": True,
        "notes": "Residual delta is a dry-run simulation only and is not eligible for direct writeback.",
    }


def build_trace(
    request: dict[str, Any],
    packet: dict[str, Any],
    decision: dict[str, Any],
    authorization: dict[str, Any],
    bridged_result: dict[str, Any],
    direct_rejection: dict[str, Any],
    unsafe_rejection: dict[str, Any],
) -> dict[str, Any]:
    return {
        "schema_name": "ystar.governed_tool_invocation_bridge.generated.bridge_invocation_trace",
        "schema_version": "v0",
        "trace_id": "bridge-invocation-trace-001",
        "bridge_id": BRIDGE_ID,
        "steps": [
            {"step": "agent_tool_request", "status": "accepted_for_pre_u", "ref": REQUEST_REF},
            {"step": "pre_u_tool_packet", "status": "built", "packet_id": packet.get("packet_id")},
            {"step": "governance_decision", "status": decision.get("decision"), "decision_id": decision.get("decision_id")},
            {"step": "bridge_authorization", "status": "authorized" if authorization.get("authorized") else "rejected"},
            {"step": "tool_invocation", "status": bridged_result.get("status"), "tool_id": TOOL_ID},
            {"step": "direct_invocation_rejection", "status": direct_rejection.get("status")},
            {"step": "unsafe_request_rejection", "status": unsafe_rejection.get("status")},
        ],
        "request_id": request.get("request_id"),
        "tool_invoked_through_bridge": bridged_result.get("status") == "success",
        "direct_tool_invocation_rejected": direct_rejection.get("status") == "rejected",
        "unsafe_bridge_request_rejected": unsafe_rejection.get("status") == "rejected",
        "real_action_executed": False,
        "external_action_executed": False,
        "live_action_enabled": False,
    }


def run_bridge(request: dict[str, Any], output_dir: Path) -> dict[str, dict[str, Any]]:
    contract = build_bridge_contract()
    readonly_contract = readonly_tool.load_contract()
    registry = readonly_tool.load_registry()
    if readonly_contract.get("tool_id") != TOOL_ID:
        raise BridgePolicyError("L4.4 tool contract does not match bridge supported tool")

    request_blocked = validate_request_for_bridge(request, registry)
    packet = build_pre_u_tool_packet(request)
    decision = build_governance_decision_envelope(packet)
    authorization = build_bridge_authorization(request, packet, decision, registry)
    authorization_blocked = validate_bridge_authorization(contract, decision, authorization)
    if request_blocked or authorization_blocked:
        raise BridgePolicyError(f"bridge request rejected: {request_blocked + authorization_blocked}")

    tool_invocation = build_tool_invocation(request, authorization)
    tool_result = readonly_tool.run_invocation(tool_invocation)
    if tool_result.get("status") != "success":
        raise BridgePolicyError("read-only observation tool did not return success through bridge")

    bridged_result = build_bridged_tool_result(tool_result, packet, decision, authorization)
    event = build_bridge_cieu_event(request, packet, decision, bridged_result)
    delta = build_residual_delta(event)
    direct_rejection = build_direct_invocation_rejection()
    unsafe_rejection = build_unsafe_bridge_request_rejection()
    trace = build_trace(request, packet, decision, authorization, bridged_result, direct_rejection, unsafe_rejection)

    payloads = {
        "bridge_contract": contract,
        "agent_tool_request": request,
        "pre_u_tool_packet": packet,
        "governance_decision_envelope": decision,
        "bridge_authorization": authorization,
        "bridged_tool_result": bridged_result,
        "bridge_cieu_event": event,
        "bridge_residual_delta": delta,
        "rejected_direct_tool_invocation": direct_rejection,
        "rejected_unsafe_bridge_request": unsafe_rejection,
        "bridge_invocation_trace": trace,
    }
    file_names = {
        "bridge_contract": "bridge_contract.json",
        "agent_tool_request": "agent_tool_request.json",
        "pre_u_tool_packet": "pre_u_tool_packet.json",
        "governance_decision_envelope": "governance_decision_envelope.json",
        "bridge_authorization": "bridge_authorization.json",
        "bridged_tool_result": "bridged_tool_result.json",
        "bridge_cieu_event": "bridge_cieu_event.json",
        "bridge_residual_delta": "bridge_residual_delta.json",
        "rejected_direct_tool_invocation": "rejected_direct_tool_invocation.json",
        "rejected_unsafe_bridge_request": "rejected_unsafe_bridge_request.json",
        "bridge_invocation_trace": "bridge_invocation_trace.json",
    }
    for key, filename in file_names.items():
        write_json(output_dir / filename, payloads[key])
    return payloads


def parse_args(argv: list[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Run governed tool invocation through Pre-U bridge.")
    parser.add_argument("--request", required=True, help="Agent tool request JSON")
    parser.add_argument("--output-dir", required=True, help="Generated output directory")
    return parser.parse_args(argv)


def main(argv: list[str]) -> int:
    args = parse_args(argv)
    try:
        request = load_json(repo_path(args.request))
        output_dir = output_dir_path(args.output_dir)
        output_dir.mkdir(parents=True, exist_ok=True)
        payloads = run_bridge(request, output_dir)
        result = payloads["bridged_tool_result"]
        print("Governed tool invocation bridge: PASS")
        print(f"tool_invoked_through_bridge: {result.get('status') == 'success'}")
        print("direct_tool_invocation_allowed: False")
        print("live_action_enabled: False")
        return 0
    except Exception as exc:
        print(f"Governed tool invocation bridge failed: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))

