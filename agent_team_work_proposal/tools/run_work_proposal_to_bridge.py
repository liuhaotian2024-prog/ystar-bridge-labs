#!/usr/bin/env python3
"""Route an agent-team generated work proposal into the governed tool bridge."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from governed_tool_invocation_bridge.tools import run_governed_tool_bridge as bridge


PACK = ROOT / "agent_team_work_proposal"
GENERATED = PACK / "generated"
TOOL_ID = "governed_readonly_observation_tool_v0"
BRIDGE_ID = "governed_tool_invocation_bridge_v0"
NEXT_MILESTONE = "L4.7 First Mission Dashboard Refresh Loop v0"

SELECTED_REF = "agent_team_work_proposal/generated/selected_agent_work_proposal.json"
ROLE_REVIEW_REF = "agent_team_work_proposal/generated/role_review_board.json"
TOOL_NEED_REF = "agent_team_work_proposal/generated/tool_need_analysis.json"
REQUEST_REF = "agent_team_work_proposal/generated/generated_tool_request.json"
TRACE_REF = "agent_team_work_proposal/generated/work_proposal_to_bridge_trace.json"
BRIDGED_RESULT_REF = "agent_team_work_proposal/generated/bridged_tool_result_ref.json"
CIEU_EVENT_REF = "agent_team_work_proposal/generated/work_proposal_cieu_event.json"
RESIDUAL_DELTA_REF = "agent_team_work_proposal/generated/work_proposal_residual_delta.json"
NEXT_RECOMMENDATIONS_REF = "agent_team_work_proposal/generated/next_agent_work_recommendations.json"


class WorkProposalBridgeError(Exception):
    """Raised when the proposal-to-bridge policy rejects the request."""


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
        raise WorkProposalBridgeError(f"absolute path rejected: {relative_path}")
    resolved = (ROOT / candidate).resolve()
    try:
        resolved.relative_to(ROOT)
    except ValueError as exc:
        raise WorkProposalBridgeError(f"path escapes repository root: {relative_path}") from exc
    return resolved


def output_dir_path(relative_path: str) -> Path:
    path = repo_path(relative_path)
    expected = GENERATED.resolve()
    try:
        path.relative_to(expected)
    except ValueError as exc:
        raise WorkProposalBridgeError("output directory must be agent_team_work_proposal/generated") from exc
    return path


def load_context() -> tuple[dict[str, Any], dict[str, Any], dict[str, Any]]:
    selected = load_json(ROOT / SELECTED_REF)
    role_review = load_json(ROOT / ROLE_REVIEW_REF)
    tool_need = load_json(ROOT / TOOL_NEED_REF)
    return selected, role_review, tool_need


def validate_request_context(
    request: dict[str, Any],
    selected: dict[str, Any],
    role_review: dict[str, Any],
    tool_need: dict[str, Any],
) -> list[str]:
    failures: list[str] = []
    if request.get("source_work_proposal_ref") != SELECTED_REF:
        failures.append("request_source_work_proposal_ref_mismatch")
    if request.get("role_review_ref") != ROLE_REVIEW_REF:
        failures.append("request_role_review_ref_mismatch")
    if request.get("tool_need_analysis_ref") != TOOL_NEED_REF:
        failures.append("request_tool_need_analysis_ref_mismatch")
    if selected.get("requires_tool_invocation") is not True:
        failures.append("selected_proposal_must_require_tool_invocation")
    if selected.get("selected_tool_id") != TOOL_ID:
        failures.append("selected_tool_id_mismatch")
    if selected.get("selected_bridge_id") != BRIDGE_ID:
        failures.append("selected_bridge_id_mismatch")
    if tool_need.get("tool_needed") is not True:
        failures.append("tool_need_must_be_true")
    if tool_need.get("bridge_required") is not True:
        failures.append("bridge_required_must_be_true")
    if tool_need.get("bridge_id") != BRIDGE_ID:
        failures.append("tool_need_bridge_id_mismatch")
    if tool_need.get("tool_id") != TOOL_ID:
        failures.append("tool_need_tool_id_mismatch")

    reviews = role_review.get("reviews", [])
    if {review.get("agent_id") for review in reviews} != {
        "Aiden-CEO",
        "Ethan-CTO",
        "Maya-Governance",
        "Ryan-Platform",
        "Samantha-Secretary",
        "Leo-Kernel",
    }:
        failures.append("role_review_must_include_all_six_roles")
    for review in reviews:
        if review.get("approved_for_local_readonly_dry_run") is not True:
            failures.append(f"role_review_not_approved:{review.get('agent_id')}")
        if review.get("agent_id") == "Maya-Governance":
            constraints = " ".join(str(item) for item in review.get("required_constraints", [])).lower()
            forbidden = " ".join(str(item) for item in review.get("forbidden_actions", [])).lower()
            if "pre-u bridge" not in constraints and "pre_u bridge" not in constraints:
                failures.append("maya_must_require_pre_u_bridge")
            if "direct tool invocation" not in forbidden:
                failures.append("maya_must_forbid_direct_tool_invocation")

    for field in [
        "live_action_requested",
        "external_action_requested",
        "brain_writeback_requested",
        "memory_ingestion_requested",
        "cieu_persistence_requested",
    ]:
        if request.get(field) is not False:
            failures.append(f"{field}_must_be_false")
    return failures


def build_trace(
    selected: dict[str, Any],
    request: dict[str, Any],
    bridge_payloads: dict[str, dict[str, Any]],
) -> dict[str, Any]:
    bridge_trace = bridge_payloads["bridge_invocation_trace"]
    return {
        "schema_name": "ystar.agent_team_work_proposal.generated.work_proposal_to_bridge_trace",
        "schema_version": "v0",
        "trace_id": "work-proposal-to-bridge-trace-001",
        "selected_proposal_ref": SELECTED_REF,
        "selected_proposal_id": selected.get("selected_proposal_id"),
        "role_review_ref": ROLE_REVIEW_REF,
        "tool_need_analysis_ref": TOOL_NEED_REF,
        "generated_tool_request_ref": REQUEST_REF,
        "bridge_runner_used": True,
        "bridge_invocation_ref": "governed_tool_invocation_bridge/tools/run_governed_tool_bridge.py::run_bridge_payloads",
        "bridged_tool_result_ref": BRIDGED_RESULT_REF,
        "bridge_trace_summary": {
            "tool_invoked_through_bridge": bridge_trace.get("tool_invoked_through_bridge"),
            "direct_tool_invocation_rejected": bridge_trace.get("direct_tool_invocation_rejected"),
            "unsafe_bridge_request_rejected": bridge_trace.get("unsafe_bridge_request_rejected"),
        },
        "direct_tool_invocation_used": False,
        "pre_u_bridge_required": True,
        "pre_u_bridge_satisfied": True,
        "real_action_executed": False,
        "external_action_executed": False,
        "notes": "Agent-team generated request was routed through the L4.5 bridge in memory.",
    }


def build_bridged_tool_result_ref(bridge_payloads: dict[str, dict[str, Any]]) -> dict[str, Any]:
    result = bridge_payloads["bridged_tool_result"]
    return {
        "schema_name": "ystar.agent_team_work_proposal.generated.bridged_tool_result_ref",
        "schema_version": "v0",
        "bridge_id": BRIDGE_ID,
        "tool_id": TOOL_ID,
        "result_status": result.get("status"),
        "bridged_tool_result_source": "in_memory_l4_5_bridge_payload",
        "pre_u_packet_ref": "governed_tool_invocation_bridge/generated/pre_u_tool_packet.json",
        "governance_decision_ref": "governed_tool_invocation_bridge/generated/governance_decision_envelope.json",
        "read_source_count": len(result.get("read_sources", [])),
        "read_sources": result.get("read_sources", []),
        "normalized_observation": result.get("normalized_observation", {}),
        "next_work_candidates": result.get("next_work_candidates", []),
        "real_action_executed": False,
        "external_action_executed": False,
        "live_action_enabled": False,
        "cieu_persistence_enabled": False,
        "brain_writeback_enabled": False,
        "memory_ingestion_enabled": False,
    }


def build_work_proposal_event(
    selected: dict[str, Any],
    request: dict[str, Any],
    bridge_payloads: dict[str, dict[str, Any]],
) -> dict[str, Any]:
    bridge_event = bridge_payloads["bridge_cieu_event"]
    result = bridge_payloads["bridged_tool_result"]
    return {
        "schema_name": "ystar.agent_team_work_proposal.generated.work_proposal_cieu_event",
        "schema_version": "v0",
        "event_id": "work-proposal-cieu-event-001",
        "dry_run_only": True,
        "persistence_enabled": False,
        "proposal_id": selected.get("selected_proposal_id"),
        "tool_id": TOOL_ID,
        "bridge_id": BRIDGE_ID,
        "request_id": request.get("request_id"),
        "Xt": {
            "selected_proposal_ref": SELECTED_REF,
            "role_review_ref": ROLE_REVIEW_REF,
            "tool_need_analysis_ref": TOOL_NEED_REF,
            "request_type": request.get("request_type"),
        },
        "U": "route agent-team generated tool request through governed Pre-U bridge",
        "Y_star": "Agent team converts mission observation into governed read-only tool invocation without live action.",
        "predicted_Y_t1": "Bridge returns normalized company-state observation for next work recommendation.",
        "predicted_R_t1": "Residual risk remains bounded by Pre-U bridge, read-only tool contract, and disabled persistence.",
        "actual_Y_t1": f"Bridge result status: {result.get('status')}; read sources: {len(result.get('read_sources', []))}.",
        "actual_R_t1": bridge_event.get("actual_R_t1"),
        "residual_delta": {
            "status": "dry_run_work_proposal_delta_only",
            "bridge_delta_ref": "governed_tool_invocation_bridge/generated/bridge_residual_delta.json",
            "delta_summary": "Agent-team work proposal successfully reached governed read-only tool result.",
        },
        "evidence_refs": [
            SELECTED_REF,
            ROLE_REVIEW_REF,
            TOOL_NEED_REF,
            REQUEST_REF,
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
        "schema_name": "ystar.agent_team_work_proposal.generated.work_proposal_residual_delta",
        "schema_version": "v0",
        "delta_id": "work-proposal-residual-delta-001",
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
        "notes": "Residual delta is dry-run only and must not be written to brain or memory.",
    }


def build_next_recommendations(selected: dict[str, Any]) -> dict[str, Any]:
    recommendations = [
        {
            "recommendation_id": "next-agent-work-001",
            "title": NEXT_MILESTONE,
            "recommended_owner_agent": "Samantha-Secretary",
            "risk_tier": "low",
            "depends_on": [selected.get("selected_proposal_id"), TRACE_REF],
            "requires_y_star_gov": True,
            "requires_operator_approval": False,
            "requires_cieu_event": True,
            "live_enabled": False,
            "external_action_enabled": False,
            "rationale": "Refresh the mission dashboard from the first agent-team generated governed observation path.",
        },
        {
            "recommendation_id": "next-agent-work-002",
            "title": "Define governed proposal scoring review fixture v0",
            "recommended_owner_agent": "Maya-Governance",
            "risk_tier": "low",
            "depends_on": [ROLE_REVIEW_REF],
            "requires_y_star_gov": True,
            "requires_operator_approval": False,
            "requires_cieu_event": True,
            "live_enabled": False,
            "external_action_enabled": False,
            "rationale": "Keep future agent-selected work explainable before any tool request is generated.",
        },
        {
            "recommendation_id": "next-agent-work-003",
            "title": "Prepare wrapper plan for the top legacy triage candidate",
            "recommended_owner_agent": "Ethan-CTO",
            "risk_tier": "medium",
            "depends_on": ["legacy_asset_triage/generated/top_absorption_candidates.json"],
            "requires_y_star_gov": True,
            "requires_operator_approval": False,
            "requires_cieu_event": True,
            "live_enabled": False,
            "external_action_enabled": False,
            "rationale": "Turn triage evidence into a governed wrapper plan without absorbing or executing legacy code.",
        },
    ]
    return {
        "schema_name": "ystar.agent_team_work_proposal.generated.next_agent_work_recommendations",
        "schema_version": "v0",
        "recommendation_count": len(recommendations),
        "recommendations": recommendations,
    }


def run_proposal_to_bridge(request: dict[str, Any], output_dir: Path) -> dict[str, dict[str, Any]]:
    selected, role_review, tool_need = load_context()
    failures = validate_request_context(request, selected, role_review, tool_need)
    if failures:
        raise WorkProposalBridgeError(f"work proposal bridge rejected: {failures}")

    bridge_payloads = bridge.run_bridge_payloads(request)
    trace = build_trace(selected, request, bridge_payloads)
    bridged_ref = build_bridged_tool_result_ref(bridge_payloads)
    event = build_work_proposal_event(selected, request, bridge_payloads)
    delta = build_residual_delta(event)
    recommendations = build_next_recommendations(selected)

    payloads = {
        "work_proposal_to_bridge_trace": trace,
        "bridged_tool_result_ref": bridged_ref,
        "work_proposal_cieu_event": event,
        "work_proposal_residual_delta": delta,
        "next_agent_work_recommendations": recommendations,
    }
    for key, payload in payloads.items():
        write_json(output_dir / f"{key}.json", payload)
    return payloads


def parse_args(argv: list[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Route agent-team work proposal to governed bridge.")
    parser.add_argument("--request", required=True, help="Generated tool request JSON")
    parser.add_argument("--output-dir", required=True, help="Generated output directory")
    return parser.parse_args(argv)


def main(argv: list[str]) -> int:
    args = parse_args(argv)
    try:
        request = load_json(repo_path(args.request))
        output_dir = output_dir_path(args.output_dir)
        output_dir.mkdir(parents=True, exist_ok=True)
        payloads = run_proposal_to_bridge(request, output_dir)
        trace = payloads["work_proposal_to_bridge_trace"]
        print("Agent team work proposal to bridge: PASS")
        print(f"bridge_runner_used: {trace.get('bridge_runner_used')}")
        print(f"direct_tool_invocation_used: {trace.get('direct_tool_invocation_used')}")
        print(f"pre_u_bridge_satisfied: {trace.get('pre_u_bridge_satisfied')}")
        return 0
    except Exception as exc:
        print(f"Agent team work proposal to bridge failed: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
