#!/usr/bin/env python3
"""Build artifacts for governed tool invocation through the Pre-U bridge."""

from __future__ import annotations

import json
import sys
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from governed_tool_invocation_bridge.tools import run_governed_tool_bridge as bridge


GENERATED = ROOT / "governed_tool_invocation_bridge" / "generated"
READINESS_PATH = GENERATED / "tool_bridge_readiness_summary.json"
REPORT_PATH = GENERATED / "tool_bridge_report.md"


def write_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


def build_readiness_summary(payloads: dict[str, dict[str, Any]]) -> dict[str, Any]:
    result = payloads["bridged_tool_result"]
    trace = payloads["bridge_invocation_trace"]
    return {
        "schema_name": "ystar.governed_tool_invocation_bridge.generated.tool_bridge_readiness_summary",
        "schema_version": "v0",
        "governed_tool_invocation_bridge_defined": True,
        "bridge_contract_defined": True,
        "agent_tool_request_defined": True,
        "pre_u_tool_packet_defined": True,
        "governance_decision_defined": True,
        "bridge_authorization_defined": True,
        "tool_invoked_through_bridge": result.get("status") == "success",
        "direct_tool_invocation_rejected": trace.get("direct_tool_invocation_rejected") is True,
        "unsafe_bridge_request_rejected": trace.get("unsafe_bridge_request_rejected") is True,
        "bridge_cieu_event_defined": True,
        "bridge_residual_delta_defined": True,
        "mission_bounded_autonomy_supported": True,
        "step_by_step_human_prompting_reduced": True,
        "first_governed_tool_invocation_chain_created": True,
        "real_action_executed": False,
        "external_action_executed": False,
        "live_action_enabled": False,
        "network_enabled": False,
        "git_push_enabled": False,
        "daemon_control_enabled": False,
        "cieu_persistence_enabled": False,
        "brain_writeback_enabled": False,
        "memory_ingestion_enabled": False,
        "email_or_external_communication_enabled": False,
        "next_required_milestone": bridge.NEXT_MILESTONE,
        "generated_contract": bridge.BRIDGE_CONTRACT_REF,
        "generated_agent_request": bridge.REQUEST_REF,
        "generated_pre_u_packet": bridge.PRE_U_REF,
        "generated_decision": bridge.DECISION_REF,
        "generated_authorization": bridge.AUTHORIZATION_REF,
        "generated_bridged_result": bridge.BRIDGED_RESULT_REF,
        "generated_cieu_event": bridge.CIEU_EVENT_REF,
        "generated_residual_delta": bridge.RESIDUAL_DELTA_REF,
        "warning": (
            "Tool invocation is routed through a Pre-U bridge for local read-only dry-run only. "
            "Live execution and persistence remain disabled."
        ),
    }


def render_report(summary: dict[str, Any], payloads: dict[str, dict[str, Any]]) -> str:
    contract = payloads["bridge_contract"]
    request = payloads["agent_tool_request"]
    packet = payloads["pre_u_tool_packet"]
    decision = payloads["governance_decision_envelope"]
    authorization = payloads["bridge_authorization"]
    result = payloads["bridged_tool_result"]
    lines = [
        "# Governed Tool Invocation Bridge Report",
        "",
        f"bridge_id: {contract['bridge_id']}",
        f"supported_tool_id: {contract['supported_tool_id']}",
        f"agent_direct_tool_invocation_allowed: {contract['agent_direct_tool_invocation_allowed']}",
        f"pre_u_packet_required: {contract['pre_u_packet_required']}",
        f"governance_decision_required: {contract['governance_decision_required']}",
        "",
        "## Agent Tool Request",
        "",
        f"- request_id: {request['request_id']}",
        f"- requesting_agent: {request['requesting_agent']}",
        f"- supporting_agent: {request['supporting_agent']}",
        f"- request_type: {request['request_type']}",
        "",
        "## Pre-U Packet",
        "",
        f"- packet_id: {packet['packet_id']}",
        f"- candidate_U_count: {len(packet['candidate_U'])}",
        f"- selected_U: {packet['selected_U']['u_id']}",
        "",
        "## Governance Decision",
        "",
        f"- decision_id: {decision['decision_id']}",
        f"- decision: {decision['decision']}",
        f"- allowed_only_as_local_readonly_dry_run: {decision['allowed_only_as_local_readonly_dry_run']}",
        "",
        "## Bridge Authorization",
        "",
        f"- authorization_id: {authorization['authorization_id']}",
        f"- authorized: {authorization['authorized']}",
        f"- allowed_sources: {len(authorization['allowed_sources'])}",
        "",
        "## Bridged Tool Result",
        "",
        f"- status: {result['status']}",
        f"- read_sources: {len(result['read_sources'])}",
        f"- real_action_executed: {result['real_action_executed']}",
        f"- external_action_executed: {result['external_action_executed']}",
        f"- live_action_enabled: {result['live_action_enabled']}",
        f"- cieu_persistence_enabled: {result['cieu_persistence_enabled']}",
        f"- brain_writeback_enabled: {result['brain_writeback_enabled']}",
        f"- memory_ingestion_enabled: {result['memory_ingestion_enabled']}",
        "",
        "## Rejections",
        "",
        f"- direct_tool_invocation_rejected: {summary['direct_tool_invocation_rejected']}",
        f"- unsafe_bridge_request_rejected: {summary['unsafe_bridge_request_rejected']}",
        "",
        f"Next required milestone: {summary['next_required_milestone']}",
        "",
        f"Warning: {summary['warning']}",
        "",
    ]
    return "\n".join(lines)


def main() -> int:
    GENERATED.mkdir(parents=True, exist_ok=True)
    request = bridge.build_agent_tool_request()
    payloads = bridge.run_bridge(request, GENERATED)
    readiness = build_readiness_summary(payloads)
    write_json(READINESS_PATH, readiness)
    REPORT_PATH.write_text(render_report(readiness, payloads), encoding="utf-8")

    print("Governed tool invocation bridge artifacts generated.")
    print(f"tool_invoked_through_bridge: {readiness['tool_invoked_through_bridge']}")
    print(f"direct_tool_invocation_rejected: {readiness['direct_tool_invocation_rejected']}")
    print(f"unsafe_bridge_request_rejected: {readiness['unsafe_bridge_request_rejected']}")
    return 0


if __name__ == "__main__":
    sys.exit(main())

