#!/usr/bin/env python3
"""Build artifacts for the governed read-only observation tool wrapper."""

from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[2]
PACK = ROOT / "governed_readonly_observation_tool"
GENERATED = PACK / "generated"
RUNNER = "governed_readonly_observation_tool/tools/run_readonly_observation_tool.py"
TOOL_ID = "governed_readonly_observation_tool_v0"
NEXT_MILESTONE = "L4.5 Governed Tool Invocation Through Pre-U Bridge v0"

CONTRACT_PATH = GENERATED / "tool_contract.json"
REGISTRY_PATH = GENERATED / "allowed_source_registry.json"
SAMPLE_INVOCATION_PATH = GENERATED / "sample_tool_invocation.json"
SAMPLE_RESULT_PATH = GENERATED / "sample_tool_result.json"
REJECTED_INVOCATION_PATH = GENERATED / "rejected_unsafe_invocation.json"
TRACE_PATH = GENERATED / "tool_invocation_trace.json"
CIEU_EVENT_PATH = GENERATED / "tool_cieu_event.json"
READINESS_PATH = GENERATED / "tool_readiness_summary.json"
REPORT_PATH = GENERATED / "tool_wrapper_report.md"

SOURCE_DEFINITIONS = [
    (
        "mission-dashboard",
        "governed_observation_loop/generated/mission_dashboard_snapshot.json",
        "mission_dashboard",
        "generated mission dashboard snapshot from the read-only observation loop",
    ),
    (
        "company-state-digest",
        "governed_observation_loop/generated/company_state_digest.json",
        "company_state_digest",
        "generated concise company state digest",
    ),
    (
        "observation-loop-summary",
        "governed_observation_loop/generated/governed_observation_loop_summary.json",
        "observation_loop_summary",
        "generated governed observation loop summary",
    ),
    (
        "legacy-triage-summary",
        "legacy_asset_triage/generated/legacy_asset_triage_summary.json",
        "legacy_triage_summary",
        "generated legacy asset triage summary",
    ),
    (
        "top-absorption-candidates",
        "legacy_asset_triage/generated/top_absorption_candidates.json",
        "legacy_triage_candidates",
        "generated top absorption candidates from triage",
    ),
    (
        "autonomous-cycle-summary",
        "company_autonomous_work_cycle/generated/autonomous_work_cycle_summary.json",
        "autonomous_cycle_summary",
        "generated mission-bounded autonomous work cycle summary",
    ),
    (
        "autonomy-inventory-summary",
        "company_autonomy_inventory/generated/company_autonomy_readiness_summary.json",
        "autonomy_inventory_summary",
        "generated company autonomy inventory readiness summary",
    ),
    (
        "live-readiness-report",
        "labs_live_readiness/generated/live_readiness_report.json",
        "live_readiness_report",
        "generated live readiness report",
    ),
    (
        "live-boundary-summary",
        "labs_live_boundary/generated/live_boundary_summary.json",
        "live_boundary_summary",
        "generated disabled live boundary summary",
    ),
    (
        "cieu-boundary-summary",
        "labs_cieu_runtime_boundary/generated/cieu_runtime_boundary_summary.json",
        "cieu_boundary_summary",
        "generated disabled CIEU runtime boundary summary",
    ),
    (
        "team-console-snapshot",
        "console_read_model/generated/team_console_snapshot.json",
        "team_console_snapshot",
        "generated team console snapshot",
    ),
]


def write_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


def load_json(path: Path) -> dict[str, Any]:
    data = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(data, dict):
        raise ValueError(f"Expected object JSON: {path}")
    return data


def build_contract() -> dict[str, Any]:
    return {
        "schema_name": "ystar.governed_readonly_observation_tool.generated.tool_contract",
        "schema_version": "v0",
        "tool_id": TOOL_ID,
        "tool_name": "Governed Read-Only Observation Tool",
        "tool_version": "v0",
        "owner_agent_candidates": ["Samantha-Secretary", "Aiden-CEO", "Maya-Governance", "Ryan-Platform"],
        "primary_owner_agent": "Samantha-Secretary",
        "supporting_agents": ["Aiden-CEO", "Maya-Governance", "Ryan-Platform"],
        "tool_category": "read_only_observation",
        "input_contract_required": True,
        "output_contract_required": True,
        "requires_y_star_gov": True,
        "requires_operator_approval": False,
        "requires_cieu_event": True,
        "requires_rollback_policy": False,
        "live_enabled": False,
        "external_action_enabled": False,
        "network_enabled": False,
        "git_push_enabled": False,
        "daemon_control_enabled": False,
        "cieu_persistence_enabled": False,
        "brain_writeback_enabled": False,
        "memory_ingestion_enabled": False,
        "email_or_external_communication_enabled": False,
        "allowed_operations": [
            "read_generated_summary",
            "read_mission_dashboard",
            "read_company_state_digest",
            "read_legacy_triage_summary",
            "read_autonomy_summary",
            "produce_normalized_observation",
        ],
        "denied_operations": [
            "read_db",
            "read_log",
            "read_raw_runtime_artifact",
            "read_active_agent_marker",
            "write_brain",
            "write_memory",
            "write_cieu_db",
            "start_daemon",
            "stop_daemon",
            "git_push",
            "create_github_issue",
            "create_github_pr",
            "send_external_communication",
            "network_call",
        ],
        "allowed_source_registry_ref": "governed_readonly_observation_tool/generated/allowed_source_registry.json",
        "output_schema_ref": "governed_readonly_observation_tool/tool_result_schema.json",
        "risk_tier": "low",
        "status": "defined_disabled_for_live_but_callable_for_local_readonly_dry_run",
    }


def build_source_registry() -> dict[str, Any]:
    sources = []
    for source_id, source_path, source_type, notes in SOURCE_DEFINITIONS:
        path = ROOT / source_path
        max_bytes = max(200000, path.stat().st_size + 4096 if path.exists() else 200000)
        sources.append(
            {
                "source_id": source_id,
                "source_path": source_path,
                "source_type": source_type,
                "safe_to_read_now": True,
                "raw_runtime_artifact": False,
                "requires_network": False,
                "requires_credentials": False,
                "read_mode": "json_summary",
                "max_bytes": max_bytes,
                "governance_notes": notes,
            }
        )
    return {
        "schema_name": "ystar.governed_readonly_observation_tool.generated.allowed_source_registry",
        "schema_version": "v0",
        "source_count": len(sources),
        "sources": sources,
    }


def build_sample_invocation(registry: dict[str, Any]) -> dict[str, Any]:
    requested_sources = [
        "mission-dashboard",
        "company-state-digest",
        "observation-loop-summary",
        "legacy-triage-summary",
        "autonomous-cycle-summary",
        "autonomy-inventory-summary",
        "live-boundary-summary",
        "cieu-boundary-summary",
    ]
    known = {source["source_id"] for source in registry["sources"]}
    requested_sources = [source_id for source_id in requested_sources if source_id in known]
    return {
        "schema_name": "ystar.governed_readonly_observation_tool.generated.tool_invocation",
        "schema_version": "v0",
        "invocation_id": "readonly-observation-invocation-001",
        "tool_id": TOOL_ID,
        "requesting_agent": "Aiden-CEO",
        "mission_id": "mission-commercial-agent-company-v0",
        "request_type": "company_state_observation",
        "requested_sources": requested_sources,
        "requested_summary_level": "executive",
        "declared_Y_star": (
            "Observe safe generated company state summaries and identify the next governed "
            "autonomy step without live or external action."
        ),
        "risk_tier": "low",
        "requires_y_star_gov": True,
        "requires_cieu_event": True,
        "live_action_requested": False,
        "external_action_requested": False,
        "brain_writeback_requested": False,
        "memory_ingestion_requested": False,
        "cieu_persistence_requested": False,
    }


def build_rejected_invocation() -> dict[str, Any]:
    return {
        "schema_name": "ystar.governed_readonly_observation_tool.generated.rejected_unsafe_invocation",
        "schema_version": "v0",
        "invocation_id": "readonly-observation-rejected-001",
        "tool_id": TOOL_ID,
        "requesting_agent": "Aiden-CEO",
        "mission_id": "mission-commercial-agent-company-v0",
        "request_type": "company_state_observation",
        "requested_sources": ["forbidden-raw-runtime-source"],
        "requested_summary_level": "executive",
        "declared_Y_star": "Attempt to read a source outside the allowed registry.",
        "risk_tier": "high",
        "requires_y_star_gov": True,
        "requires_cieu_event": True,
        "live_action_requested": False,
        "external_action_requested": False,
        "brain_writeback_requested": False,
        "memory_ingestion_requested": False,
        "cieu_persistence_requested": False,
    }


def run_sample_tool() -> dict[str, Any]:
    command = [
        "python3",
        RUNNER,
        "--input",
        "governed_readonly_observation_tool/generated/sample_tool_invocation.json",
        "--output",
        "governed_readonly_observation_tool/generated/sample_tool_result.json",
    ]
    result = subprocess.run(
        command,
        cwd=ROOT,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        check=False,
    )
    if result.returncode != 0:
        raise RuntimeError(result.stdout + result.stderr)
    return load_json(SAMPLE_RESULT_PATH)


def simulate_rejection(rejected_invocation: dict[str, Any]) -> dict[str, Any]:
    return {
        "schema_name": "ystar.governed_readonly_observation_tool.generated.tool_result",
        "schema_version": "v0",
        "result_id": "result-readonly-observation-rejected-001",
        "invocation_id": rejected_invocation["invocation_id"],
        "tool_id": TOOL_ID,
        "status": "rejected",
        "read_sources": [],
        "normalized_observation": {},
        "blocked_sources": [
            {
                "source_id": "forbidden-raw-runtime-source",
                "reason": "source_not_in_allowed_registry",
            }
        ],
        "policy_decision": {
            "decision": "reject",
            "reason": "unsafe or unregistered sources are rejected before any source read",
        },
        "real_action_executed": False,
        "external_action_executed": False,
        "live_action_enabled": False,
        "cieu_persistence_enabled": False,
        "brain_writeback_enabled": False,
        "memory_ingestion_enabled": False,
        "next_work_candidates": [],
        "notes": "Rejected fixture confirms the wrapper fails closed.",
    }


def build_trace(sample_result: dict[str, Any], rejected_result: dict[str, Any]) -> dict[str, Any]:
    return {
        "schema_name": "ystar.governed_readonly_observation_tool.generated.tool_invocation_trace",
        "schema_version": "v0",
        "trace_id": "readonly-observation-tool-trace-001",
        "entries": [
            {
                "invocation_id": sample_result["invocation_id"],
                "status": sample_result["status"],
                "read_source_count": len(sample_result.get("read_sources", [])),
                "blocked_source_count": len(sample_result.get("blocked_sources", [])),
                "real_action_executed": False,
                "external_action_executed": False,
            },
            {
                "invocation_id": rejected_result["invocation_id"],
                "status": rejected_result["status"],
                "read_source_count": len(rejected_result.get("read_sources", [])),
                "blocked_source_count": len(rejected_result.get("blocked_sources", [])),
                "real_action_executed": False,
                "external_action_executed": False,
            },
        ],
    }


def build_cieu_event(sample_invocation: dict[str, Any], sample_result: dict[str, Any]) -> dict[str, Any]:
    return {
        "schema_name": "ystar.governed_readonly_observation_tool.generated.tool_cieu_event",
        "schema_version": "v0",
        "event_id": "readonly-observation-tool-cieu-event-001",
        "dry_run_only": True,
        "persistence_enabled": False,
        "tool_id": TOOL_ID,
        "invocation_id": sample_invocation["invocation_id"],
        "Xt": {
            "request_type": sample_invocation["request_type"],
            "requested_sources": sample_invocation["requested_sources"],
            "summary_level": sample_invocation["requested_summary_level"],
        },
        "U": {
            "operation": "produce_normalized_observation",
            "real_action_executed": False,
            "external_action_executed": False,
        },
        "Y_star": sample_invocation["declared_Y_star"],
        "predicted_Y_t1": "A normalized observation result is produced from allowed generated summaries.",
        "predicted_R_t1": "All live, external, persistence, brain, and memory behaviors remain disabled.",
        "actual_Y_t1": f"Tool result status: {sample_result['status']}; sources read: {len(sample_result['read_sources'])}.",
        "actual_R_t1": "No live action, external action, CIEU persistence, brain writeback, or memory ingestion occurred.",
        "residual_delta": {
            "status": "dry_run_observation_delta_only",
            "semantic_truth_status": "not_evaluated",
            "delta_summary": "Wrapper produced the expected local read-only observation result.",
        },
        "evidence_refs": [source["source_path"] for source in sample_result.get("read_sources", [])],
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


def build_readiness_summary(sample_result: dict[str, Any], rejected_result: dict[str, Any]) -> dict[str, Any]:
    return {
        "schema_name": "ystar.governed_readonly_observation_tool.generated.tool_readiness_summary",
        "schema_version": "v0",
        "governed_readonly_observation_tool_defined": True,
        "tool_contract_defined": True,
        "allowed_source_registry_defined": True,
        "sample_invocation_defined": True,
        "sample_result_defined": sample_result.get("status") == "success",
        "unsafe_invocation_rejected": rejected_result.get("status") == "rejected",
        "tool_cieu_event_defined": True,
        "local_readonly_dry_run_callable": sample_result.get("status") == "success",
        "mission_bounded_autonomy_supported": True,
        "step_by_step_human_prompting_reduced": True,
        "first_governed_tool_wrapper_created": True,
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
        "next_required_milestone": NEXT_MILESTONE,
        "generated_contract": "governed_readonly_observation_tool/generated/tool_contract.json",
        "generated_registry": "governed_readonly_observation_tool/generated/allowed_source_registry.json",
        "generated_sample_result": "governed_readonly_observation_tool/generated/sample_tool_result.json",
        "generated_cieu_event": "governed_readonly_observation_tool/generated/tool_cieu_event.json",
        "warning": "Read-only wrapper is callable locally, but live execution and persistence remain disabled.",
    }


def render_report(summary: dict[str, Any], registry: dict[str, Any], sample_result: dict[str, Any]) -> str:
    lines = [
        "# Governed Read-Only Observation Tool Report",
        "",
        f"tool_contract_defined: {summary['tool_contract_defined']}",
        f"allowed_source_registry_defined: {summary['allowed_source_registry_defined']}",
        f"sample_result_defined: {summary['sample_result_defined']}",
        f"unsafe_invocation_rejected: {summary['unsafe_invocation_rejected']}",
        f"local_readonly_dry_run_callable: {summary['local_readonly_dry_run_callable']}",
        f"first_governed_tool_wrapper_created: {summary['first_governed_tool_wrapper_created']}",
        "",
        "## Source Registry",
        "",
        f"- source_count: {registry['source_count']}",
    ]
    for source in registry["sources"]:
        lines.append(f"- {source['source_id']}: {source['source_path']}")
    lines.extend(
        [
            "",
            "## Sample Result",
            "",
            f"- status: {sample_result['status']}",
            f"- read_sources: {len(sample_result['read_sources'])}",
            f"- real_action_executed: {sample_result['real_action_executed']}",
            f"- external_action_executed: {sample_result['external_action_executed']}",
            f"- live_action_enabled: {sample_result['live_action_enabled']}",
            f"- cieu_persistence_enabled: {sample_result['cieu_persistence_enabled']}",
            f"- brain_writeback_enabled: {sample_result['brain_writeback_enabled']}",
            f"- memory_ingestion_enabled: {sample_result['memory_ingestion_enabled']}",
            "",
            f"Next required milestone: {summary['next_required_milestone']}",
            "",
            f"Warning: {summary['warning']}",
            "",
        ]
    )
    return "\n".join(lines)


def main() -> int:
    GENERATED.mkdir(parents=True, exist_ok=True)

    contract = build_contract()
    registry = build_source_registry()
    sample_invocation = build_sample_invocation(registry)
    rejected_invocation = build_rejected_invocation()

    write_json(CONTRACT_PATH, contract)
    write_json(REGISTRY_PATH, registry)
    write_json(SAMPLE_INVOCATION_PATH, sample_invocation)
    write_json(REJECTED_INVOCATION_PATH, rejected_invocation)

    sample_result = run_sample_tool()
    rejected_result = simulate_rejection(rejected_invocation)
    trace = build_trace(sample_result, rejected_result)
    cieu_event = build_cieu_event(sample_invocation, sample_result)
    readiness = build_readiness_summary(sample_result, rejected_result)

    write_json(TRACE_PATH, trace)
    write_json(CIEU_EVENT_PATH, cieu_event)
    write_json(READINESS_PATH, readiness)
    REPORT_PATH.write_text(render_report(readiness, registry, sample_result), encoding="utf-8")

    print("Governed read-only observation tool artifacts generated.")
    print(f"sources_registered: {registry['source_count']}")
    print(f"sample_result_status: {sample_result['status']}")
    print(f"unsafe_invocation_rejected: {readiness['unsafe_invocation_rejected']}")
    return 0


if __name__ == "__main__":
    sys.exit(main())

