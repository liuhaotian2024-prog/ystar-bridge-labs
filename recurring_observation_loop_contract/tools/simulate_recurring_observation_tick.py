#!/usr/bin/env python3
"""Simulate one manual local L4.8 recurring observation tick."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[2]
PACK = ROOT / "recurring_observation_loop_contract"
GENERATED = PACK / "generated"
NEXT_MILESTONE = "L4.9 Manual Recurring Observation Tick Runner v0"
LOOP_ID = "governed_recurring_observation_loop_contract_v0"

CONTRACT_REF = "recurring_observation_loop_contract/generated/recurring_loop_contract.json"
SOURCES_REF = "recurring_observation_loop_contract/generated/allowed_observation_sources.json"
GATE_REF = "recurring_observation_loop_contract/generated/tick_governance_gate.json"
TICK_REF = "recurring_observation_loop_contract/generated/simulated_observation_tick_001.json"
DASHBOARD_DELTA_REF = "recurring_observation_loop_contract/generated/simulated_tick_dashboard_delta.json"
WORK_CANDIDATES_REF = "recurring_observation_loop_contract/generated/simulated_tick_work_candidates.json"
CIEU_EVENT_REF = "recurring_observation_loop_contract/generated/simulated_tick_cieu_event.json"
RESIDUAL_DELTA_REF = "recurring_observation_loop_contract/generated/simulated_tick_residual_delta.json"
STOP_ABORT_REF = "recurring_observation_loop_contract/generated/stop_abort_conditions.json"
ESCALATION_REF = "recurring_observation_loop_contract/generated/escalation_conditions.json"


class RecurringLoopError(Exception):
    """Raised when the manual simulation would violate the contract."""


def repo_path(relative_path: str) -> Path:
    candidate = Path(relative_path)
    if candidate.is_absolute():
        raise RecurringLoopError(f"absolute path rejected: {relative_path}")
    resolved = (ROOT / candidate).resolve()
    try:
        resolved.relative_to(ROOT)
    except ValueError as exc:
        raise RecurringLoopError(f"path escapes repository root: {relative_path}") from exc
    return resolved


def output_dir_path(relative_path: str) -> Path:
    path = repo_path(relative_path)
    try:
        path.relative_to(GENERATED.resolve())
    except ValueError as exc:
        raise RecurringLoopError(
            "output directory must be recurring_observation_loop_contract/generated"
        ) from exc
    return path


def load_json(path: Path) -> dict[str, Any]:
    data = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(data, dict):
        raise RecurringLoopError(f"expected object JSON: {path}")
    return data


def write_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


def source_path(source: dict[str, Any]) -> Path:
    if source.get("safe_to_read_now") is not True:
        raise RecurringLoopError(f"source not safe: {source.get('source_id')}")
    if source.get("raw_runtime_artifact") is not False:
        raise RecurringLoopError(f"source is raw runtime artifact: {source.get('source_id')}")
    if source.get("requires_network") is not False:
        raise RecurringLoopError(f"source requires network: {source.get('source_id')}")
    if source.get("requires_credentials") is not False:
        raise RecurringLoopError(f"source requires credentials: {source.get('source_id')}")
    path = repo_path(str(source["source_path"]))
    if path.suffix != ".json":
        raise RecurringLoopError(f"source must be generated JSON: {source.get('source_id')}")
    if not path.exists():
        raise RecurringLoopError(f"missing allowed source: {source.get('source_path')}")
    if path.stat().st_size > int(source.get("max_bytes", 0)):
        raise RecurringLoopError(f"source exceeds max_bytes: {source.get('source_id')}")
    return path


def require_disabled(contract: dict[str, Any], gate: dict[str, Any]) -> None:
    for payload_name, payload in [("contract", contract), ("gate", gate)]:
        for field in ["recurrence_enabled", "scheduler_enabled", "daemon_enabled"]:
            if payload.get(field) is not False:
                raise RecurringLoopError(f"{payload_name} must keep {field}=false")
    if contract.get("manual_local_simulation_only") is not True:
        raise RecurringLoopError("contract must be manual local simulation only")
    if gate.get("decision") != "allow_manual_local_simulated_tick":
        raise RecurringLoopError("tick governance gate must allow only manual local simulation")
    if gate.get("allowed_only_as_manual_local_simulation") is not True:
        raise RecurringLoopError("tick gate must be simulation-only")


def compact_source_observation(source: dict[str, Any], payload: dict[str, Any]) -> dict[str, Any]:
    interesting_keys = [
        "next_required_milestone",
        "state_change_level",
        "mission_bounded_autonomy_supported",
        "dashboard_refresh_loop_ran",
        "agent_team_generated_the_work",
        "tool_invoked_through_bridge",
        "first_governed_tool_wrapper_created",
        "read_only_observation_loop_defined",
        "assets_scored",
    ]
    observed = {key: payload.get(key) for key in interesting_keys if key in payload}
    return {
        "source_id": source["source_id"],
        "source_path": source["source_path"],
        "observed_fields": observed,
    }


def build_stop_abort_conditions() -> dict[str, Any]:
    labels = [
        ("stop-001", "unsafe source requested", "high"),
        ("stop-002", "database, sidecar, runtime, or text-run artifact requested", "high"),
        ("stop-003", "scheduler unexpectedly enabled", "critical"),
        ("stop-004", "daemon unexpectedly enabled", "critical"),
        ("stop-005", "external network requested", "critical"),
        ("stop-006", "live action requested", "critical"),
        ("stop-007", "CIEU persistence requested", "critical"),
        ("stop-008", "brain or memory writeback requested", "critical"),
        ("stop-009", "source registry validation failure", "high"),
        ("stop-010", "governance gate denies tick", "high"),
        ("stop-011", "repeated residual delta unresolved", "medium"),
        ("stop-012", "generated artifact size guard failure", "medium"),
    ]
    return {
        "schema_name": "ystar.recurring_observation_loop_contract.generated.stop_abort_conditions",
        "schema_version": "v0",
        "conditions": [
            {
                "condition_id": condition_id,
                "description": description,
                "severity": severity,
                "action": "stop_or_abort",
                "requires_operator_review": True,
            }
            for condition_id, description, severity in labels
        ],
        "condition_count": len(labels),
    }


def build_escalation_conditions() -> dict[str, Any]:
    labels = [
        ("escalate-001", "live enablement requested", "critical", "Maya-Governance"),
        ("escalate-002", "external action requested", "critical", "Aiden-CEO"),
        ("escalate-003", "asset absorption requested", "high", "Maya-Governance"),
        ("escalate-004", "brain or memory update requested", "critical", "Leo-Kernel"),
        ("escalate-005", "repeated failed ticks", "medium", "Ryan-Platform"),
        ("escalate-006", "major mission drift detected", "high", "Aiden-CEO"),
        ("escalate-007", "governance contract mismatch", "high", "Maya-Governance"),
        ("escalate-008", "unusual generated artifact growth", "medium", "Ryan-Platform"),
    ]
    return {
        "schema_name": "ystar.recurring_observation_loop_contract.generated.escalation_conditions",
        "schema_version": "v0",
        "conditions": [
            {
                "condition_id": condition_id,
                "description": description,
                "severity": severity,
                "escalation_target_agent": target,
                "requires_operator_review": True,
            }
            for condition_id, description, severity, target in labels
        ],
        "condition_count": len(labels),
    }


def build_tick(observations: list[dict[str, Any]]) -> dict[str, Any]:
    dashboard = next(
        (
            item
            for item in observations
            if item["source_path"].endswith("refreshed_mission_dashboard.json")
        ),
        {},
    )
    delta = next(
        (item for item in observations if item["source_path"].endswith("company_state_delta.json")),
        {},
    )
    backlog = next(
        (
            item
            for item in observations
            if item["source_path"].endswith("refreshed_autonomous_backlog.json")
        ),
        {},
    )
    return {
        "schema_name": "ystar.recurring_observation_loop_contract.generated.simulated_observation_tick",
        "schema_version": "v0",
        "tick_id": "simulated-observation-tick-001",
        "recurring_loop_id": LOOP_ID,
        "tick_number": 1,
        "manual_local_simulation_only": True,
        "recurrence_enabled": False,
        "scheduler_used": False,
        "daemon_used": False,
        "observation_sources_used": [item["source_path"] for item in observations],
        "observed_dashboard_state": dashboard.get("observed_fields", {}),
        "observed_state_delta": delta.get("observed_fields", {}),
        "observed_backlog_state": backlog.get("observed_fields", {}),
        "detected_findings": [
            "L4.7 manual dashboard refresh loop exists and remains non-recurring.",
            "L4.6 agent-team proposal bridge evidence is available in generated summaries.",
            "A recurring observation contract can be defined while scheduler and daemon remain disabled.",
        ],
        "safe_opportunities": [
            NEXT_MILESTONE,
            "Add manual tick runner validation before any recurring enablement.",
            "Strengthen source registry checks for every future tick.",
        ],
        "blocked_risks": [
            "recurrence is disabled",
            "scheduler is disabled",
            "daemon is disabled",
            "live action and external action remain disabled",
            "persistence and writeback remain disabled",
        ],
        "real_action_executed": False,
        "external_action_executed": False,
        "live_action_enabled": False,
    }


def build_dashboard_delta(tick: dict[str, Any]) -> dict[str, Any]:
    return {
        "schema_name": "ystar.recurring_observation_loop_contract.generated.simulated_tick_dashboard_delta",
        "schema_version": "v0",
        "delta_id": "simulated-tick-dashboard-delta-001",
        "tick_id": tick["tick_id"],
        "previous_dashboard_ref": "mission_dashboard_refresh_loop/generated/refreshed_mission_dashboard.json",
        "current_dashboard_ref": "mission_dashboard_refresh_loop/generated/refreshed_mission_dashboard.json",
        "detected_changes": [
            "recurring contract requirements are now represented as a disabled design artifact",
            "manual local tick governance is explicit",
            "future scheduler and daemon enablement require checklist review",
        ],
        "mission_progress_summary": (
            "The company can now describe how recurring observation should work while keeping "
            "the actual recurrence path disabled."
        ),
        "state_change_level": "meaningful",
        "requires_review": True,
        "direct_brain_writeback_allowed": False,
        "direct_memory_ingestion_allowed": False,
    }


def build_work_candidates(tick: dict[str, Any]) -> dict[str, Any]:
    candidates = [
        {
            "candidate_id": "tick-work-001",
            "title": NEXT_MILESTONE,
            "recommended_owner_agent": "Ryan-Platform",
            "supporting_agents": ["Samantha-Secretary", "Maya-Governance", "Leo-Kernel"],
            "risk_tier": "low",
            "source_evidence_refs": [TICK_REF, GATE_REF, SOURCES_REF],
            "requires_y_star_gov": True,
            "requires_operator_approval": False,
            "requires_cieu_event": True,
            "live_enabled": False,
            "external_action_enabled": False,
            "rationale": "A manual tick runner is the next safe step after defining the recurring contract.",
        },
        {
            "candidate_id": "tick-work-002",
            "title": "Add recurring tick source-registry validator fixture v0",
            "recommended_owner_agent": "Maya-Governance",
            "supporting_agents": ["Ryan-Platform"],
            "risk_tier": "low",
            "source_evidence_refs": [SOURCES_REF],
            "requires_y_star_gov": True,
            "requires_operator_approval": False,
            "requires_cieu_event": True,
            "live_enabled": False,
            "external_action_enabled": False,
            "rationale": "Every future tick needs a fail-closed source registry check.",
        },
        {
            "candidate_id": "tick-work-003",
            "title": "Draft operator-reviewed recurrence enablement packet v0",
            "recommended_owner_agent": "Aiden-CEO",
            "supporting_agents": ["Maya-Governance", "Ryan-Platform"],
            "risk_tier": "medium",
            "source_evidence_refs": [DASHBOARD_DELTA_REF],
            "requires_y_star_gov": True,
            "requires_operator_approval": True,
            "requires_cieu_event": True,
            "live_enabled": False,
            "external_action_enabled": False,
            "rationale": "Enablement should be designed as a reviewed packet, not as an active scheduler.",
        },
    ]
    return {
        "schema_name": "ystar.recurring_observation_loop_contract.generated.simulated_tick_work_candidates",
        "schema_version": "v0",
        "tick_id": tick["tick_id"],
        "candidate_count": len(candidates),
        "candidates": candidates,
        "top_candidate": NEXT_MILESTONE,
        "live_enabled": False,
        "external_action_enabled": False,
    }


def build_cieu_event(
    tick: dict[str, Any],
    dashboard_delta: dict[str, Any],
    work_candidates: dict[str, Any],
) -> dict[str, Any]:
    return {
        "schema_name": "ystar.recurring_observation_loop_contract.generated.simulated_tick_cieu_event",
        "schema_version": "v0",
        "event_id": "simulated-tick-cieu-event-001",
        "dry_run_only": True,
        "persistence_enabled": False,
        "recurring_loop_id": LOOP_ID,
        "tick_id": tick["tick_id"],
        "Xt": {
            "contract_ref": CONTRACT_REF,
            "allowed_sources_ref": SOURCES_REF,
            "tick_number": tick["tick_number"],
        },
        "U": "manual local simulated recurring observation tick",
        "Y_star": "mission-bounded autonomous company observes generated evidence under governance",
        "predicted_Y_t1": {
            "recurring_contract_defined": True,
            "manual_tick_simulated": True,
            "scheduler_enabled": False,
            "daemon_enabled": False,
        },
        "predicted_R_t1": {
            "risk_tier": "low",
            "requires_curation": True,
            "live_action_enabled": False,
        },
        "actual_Y_t1": {
            "simulated_tick_defined": True,
            "dashboard_delta_defined": True,
            "work_candidates_defined": work_candidates["candidate_count"] >= 3,
        },
        "actual_R_t1": {
            "real_action_executed": False,
            "external_action_executed": False,
            "persistence_enabled": False,
        },
        "residual_delta": {
            "summary": "Prediction matched simulated local-only contract behavior.",
            "state_change_level": dashboard_delta["state_change_level"],
            "unresolved_items": ["future manual tick runner remains to be built"],
        },
        "evidence_refs": [CONTRACT_REF, SOURCES_REF, GATE_REF, TICK_REF, DASHBOARD_DELTA_REF],
        "write_policy": {
            "generated_artifact_only": True,
            "persistent_store_write_allowed": False,
        },
        "learning_eligibility": False,
        "curation_required": True,
        "direct_brain_writeback_allowed": False,
        "direct_memory_ingestion_allowed": False,
        "raw_artifact_ingestion_allowed": False,
    }


def build_residual_delta(event: dict[str, Any]) -> dict[str, Any]:
    return {
        "schema_name": "ystar.recurring_observation_loop_contract.generated.simulated_tick_residual_delta",
        "schema_version": "v0",
        "delta_id": "simulated-tick-residual-delta-001",
        "event_id": event["event_id"],
        "predicted_vs_actual_summary": "Manual local simulated tick produced expected disabled-recurring artifacts.",
        "residual_delta": event["residual_delta"],
        "learning_eligibility": False,
        "curation_required": True,
        "direct_brain_writeback_allowed": False,
        "direct_memory_ingestion_allowed": False,
        "next_review_required": True,
        "notes": "Residual is review-only and cannot update memory or brain state directly.",
    }


def run(output_dir: Path) -> dict[str, dict[str, Any]]:
    output_dir.mkdir(parents=True, exist_ok=True)
    contract = load_json(GENERATED / "recurring_loop_contract.json")
    registry = load_json(GENERATED / "allowed_observation_sources.json")
    gate = load_json(GENERATED / "tick_governance_gate.json")
    require_disabled(contract, gate)

    source_entries = registry.get("sources", [])
    observations: list[dict[str, Any]] = []
    for source in source_entries:
        path = source_path(source)
        observations.append(compact_source_observation(source, load_json(path)))

    tick = build_tick(observations)
    dashboard_delta = build_dashboard_delta(tick)
    work_candidates = build_work_candidates(tick)
    cieu_event = build_cieu_event(tick, dashboard_delta, work_candidates)
    residual_delta = build_residual_delta(cieu_event)
    stop_abort = build_stop_abort_conditions()
    escalation = build_escalation_conditions()

    payloads = {
        "simulated_observation_tick_001": tick,
        "simulated_tick_dashboard_delta": dashboard_delta,
        "simulated_tick_work_candidates": work_candidates,
        "simulated_tick_cieu_event": cieu_event,
        "simulated_tick_residual_delta": residual_delta,
        "stop_abort_conditions": stop_abort,
        "escalation_conditions": escalation,
    }
    for name, payload in payloads.items():
        write_json(output_dir / f"{name}.json", payload)
    return payloads


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Simulate one manual recurring observation tick.")
    parser.add_argument(
        "--output-dir",
        default=str(GENERATED.relative_to(ROOT)),
        help="Output directory under recurring_observation_loop_contract/generated.",
    )
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv)
    output_dir = output_dir_path(args.output_dir)
    run(output_dir)
    print(f"Wrote simulated recurring observation tick artifacts to {output_dir.relative_to(ROOT)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

