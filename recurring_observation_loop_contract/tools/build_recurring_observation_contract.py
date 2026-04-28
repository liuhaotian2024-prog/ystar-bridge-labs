#!/usr/bin/env python3
"""Build L4.8 governed recurring observation loop contract artifacts."""

from __future__ import annotations

import json
import sys
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from recurring_observation_loop_contract.tools import simulate_recurring_observation_tick as simulator


PACK = ROOT / "recurring_observation_loop_contract"
GENERATED = PACK / "generated"
NEXT_MILESTONE = simulator.NEXT_MILESTONE

ALLOWED_SOURCE_SPECS = [
    (
        "mission-dashboard-refresh",
        "mission_dashboard_refresh_loop/generated/refreshed_mission_dashboard.json",
        "mission_dashboard",
        "Refreshed L4.7 mission dashboard summary.",
    ),
    (
        "mission-dashboard-delta",
        "mission_dashboard_refresh_loop/generated/company_state_delta.json",
        "company_state_delta",
        "L4.7 generated company state delta.",
    ),
    (
        "mission-dashboard-backlog",
        "mission_dashboard_refresh_loop/generated/refreshed_autonomous_backlog.json",
        "autonomous_backlog",
        "L4.7 refreshed autonomous backlog.",
    ),
    (
        "agent-team-work-proposal-summary",
        "agent_team_work_proposal/generated/agent_team_work_proposal_summary.json",
        "agent_team_summary",
        "L4.6 agent-team generated work proposal summary.",
    ),
    (
        "tool-bridge-readiness-summary",
        "governed_tool_invocation_bridge/generated/tool_bridge_readiness_summary.json",
        "tool_bridge_summary",
        "L4.5 governed bridge readiness summary.",
    ),
    (
        "readonly-tool-readiness-summary",
        "governed_readonly_observation_tool/generated/tool_readiness_summary.json",
        "readonly_tool_summary",
        "L4.4 governed read-only tool readiness summary.",
    ),
    (
        "governed-observation-loop-summary",
        "governed_observation_loop/generated/governed_observation_loop_summary.json",
        "observation_loop_summary",
        "L4.3 governed observation loop summary.",
    ),
    (
        "legacy-triage-summary",
        "legacy_asset_triage/generated/legacy_asset_triage_summary.json",
        "legacy_triage_summary",
        "L4.3 legacy asset triage summary.",
    ),
    (
        "team-console-snapshot",
        "console_read_model/generated/team_console_snapshot.json",
        "console_read_model",
        "Generated team console snapshot.",
    ),
]


def write_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


def write_text(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def repo_path(relative_path: str) -> Path:
    path = (ROOT / relative_path).resolve()
    try:
        path.relative_to(ROOT)
    except ValueError as exc:
        raise ValueError(f"source outside repository: {relative_path}") from exc
    return path


def build_recurring_loop_contract() -> dict[str, Any]:
    return {
        "schema_name": "ystar.recurring_observation_loop_contract.generated.recurring_loop_contract",
        "schema_version": "v0",
        "recurring_loop_id": simulator.LOOP_ID,
        "recurring_loop_name": "Governed Recurring Observation Loop Contract",
        "recurring_loop_version": "v0",
        "mission_bounded_autonomy_supported": True,
        "founder_sets_mission_agent_team_drives": True,
        "step_by_step_human_prompting_required": False,
        "recurrence_defined": True,
        "recurrence_enabled": False,
        "scheduler_enabled": False,
        "daemon_enabled": False,
        "auto_run_enabled": False,
        "manual_local_simulation_only": True,
        "tick_requires_governance_gate": True,
        "tick_requires_cieu_event": True,
        "tick_requires_residual_delta": True,
        "tick_requires_dashboard_refresh": True,
        "tick_requires_work_candidate_generation": True,
        "tick_requires_stop_abort_check": True,
        "tick_requires_escalation_check": True,
        "allowed_source_registry_required": True,
        "raw_runtime_artifacts_allowed": False,
        "external_network_allowed": False,
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
    }


def build_recurrence_schedule_draft() -> dict[str, Any]:
    return {
        "schema_name": "ystar.recurring_observation_loop_contract.generated.recurrence_schedule_draft",
        "schema_version": "v0",
        "schedule_id": "recurrence-schedule-draft-001",
        "schedule_type": "draft_only",
        "recurrence_enabled": False,
        "scheduler_enabled": False,
        "daemon_enabled": False,
        "manual_local_simulation_only": True,
        "proposed_frequency": "manual_or_hourly_when_enabled_later",
        "minimum_interval_seconds": 3600,
        "jitter_policy": "none_until_scheduler_contract_exists",
        "max_ticks_per_day": 0,
        "quiet_hours_policy": "not_applicable_until_manual_enablement",
        "operator_enablement_required": True,
        "governance_precondition": (
            "Each tick requires a governance gate, allowed source registry validation, "
            "CIEU dry-run event, residual delta, stop/abort check, and escalation check."
        ),
        "notes": "Draft schedule only; no recurrence, scheduler, daemon, or auto-run is enabled.",
    }


def build_allowed_observation_sources() -> dict[str, Any]:
    sources = []
    for source_id, relative_path, source_type, notes in ALLOWED_SOURCE_SPECS:
        path = repo_path(relative_path)
        size = path.stat().st_size if path.exists() else 0
        sources.append(
            {
                "source_id": source_id,
                "source_path": relative_path,
                "source_type": source_type,
                "safe_to_read_now": True,
                "raw_runtime_artifact": False,
                "requires_network": False,
                "requires_credentials": False,
                "max_bytes": max(size + 4096, 32768),
                "governance_notes": notes,
            }
        )
    return {
        "schema_name": "ystar.recurring_observation_loop_contract.generated.allowed_observation_sources",
        "schema_version": "v0",
        "allowed_source_registry_defined": True,
        "source_count": len(sources),
        "sources": sources,
        "raw_runtime_artifacts_allowed": False,
        "external_network_allowed": False,
    }


def build_tick_governance_gate() -> dict[str, Any]:
    return {
        "schema_name": "ystar.recurring_observation_loop_contract.generated.tick_governance_gate",
        "schema_version": "v0",
        "gate_id": "tick-governance-gate-001",
        "tick_type": "recurring_observation_tick",
        "decision": "allow_manual_local_simulated_tick",
        "decision_reason": (
            "The tick is local, deterministic, read-only, generated-source only, and all "
            "recurrence/live/writeback/persistence flags are disabled."
        ),
        "allowed_only_as_manual_local_simulation": True,
        "recurrence_enabled": False,
        "scheduler_enabled": False,
        "daemon_enabled": False,
        "live_action_allowed": False,
        "external_action_allowed": False,
        "cieu_persistence_allowed": False,
        "brain_writeback_allowed": False,
        "memory_ingestion_allowed": False,
        "operator_approval_required_for_enablement": True,
        "notes": "This gate does not authorize recurring execution.",
    }


def build_manual_enablement_checklist() -> dict[str, Any]:
    raw_items = [
        ("enablement-001", "recurring loop contract reviewed", "defined_disabled"),
        ("enablement-002", "allowed source registry reviewed", "defined_disabled"),
        ("enablement-003", "tick governance gate reviewed", "defined_disabled"),
        ("enablement-004", "CIEU tick event policy reviewed", "defined_disabled"),
        ("enablement-005", "residual delta review policy reviewed", "defined_disabled"),
        ("enablement-006", "stop/abort policy reviewed", "defined_disabled"),
        ("enablement-007", "escalation policy reviewed", "defined_disabled"),
        ("enablement-008", "scheduler sandbox designed", "not_started"),
        ("enablement-009", "daemon lifecycle policy designed", "not_started"),
        ("enablement-010", "operator approval gate implemented", "not_started"),
        ("enablement-011", "generated artifact size guard implemented", "defined_disabled"),
        ("enablement-012", "live disable flags verified", "defined_disabled"),
        ("enablement-013", "rollback plan defined", "not_started"),
    ]
    return {
        "schema_name": "ystar.recurring_observation_loop_contract.generated.manual_enablement_checklist",
        "schema_version": "v0",
        "checklist_items": [
            {
                "item_id": item_id,
                "description": description,
                "status": status,
            }
            for item_id, description, status in raw_items
        ],
        "allowed_statuses": ["not_started", "defined_disabled"],
        "disallowed_statuses": ["enabled", "approved", "complete", "live", "active"],
        "manual_enablement_required": True,
    }


def build_readiness_summary(
    payloads: dict[str, dict[str, Any]],
    checklist: dict[str, Any],
) -> dict[str, Any]:
    return {
        "schema_name": "ystar.recurring_observation_loop_contract.generated.recurring_loop_readiness_summary",
        "schema_version": "v0",
        "recurring_observation_loop_contract_defined": True,
        "recurrence_policy_defined": True,
        "recurrence_enabled": False,
        "scheduler_enabled": False,
        "daemon_enabled": False,
        "auto_run_enabled": False,
        "manual_local_simulation_only": True,
        "allowed_observation_sources_defined": True,
        "tick_governance_gate_defined": True,
        "simulated_observation_tick_defined": True,
        "simulated_tick_dashboard_delta_defined": True,
        "simulated_tick_work_candidates_defined": True,
        "simulated_tick_cieu_event_defined": True,
        "simulated_tick_residual_delta_defined": True,
        "stop_abort_conditions_defined": True,
        "escalation_conditions_defined": True,
        "manual_enablement_checklist_defined": True,
        "manual_enablement_item_count": len(checklist.get("checklist_items", [])),
        "mission_bounded_autonomy_supported": True,
        "founder_sets_mission_agent_team_drives": True,
        "step_by_step_human_prompting_required": False,
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
        "generated_contract": simulator.CONTRACT_REF,
        "generated_allowed_sources": simulator.SOURCES_REF,
        "generated_tick": simulator.TICK_REF,
        "generated_cieu_event": simulator.CIEU_EVENT_REF,
        "generated_residual_delta": simulator.RESIDUAL_DELTA_REF,
        "generated_stop_abort_conditions": simulator.STOP_ABORT_REF,
        "generated_escalation_conditions": simulator.ESCALATION_REF,
        "tick_candidate_count": payloads["simulated_tick_work_candidates"].get("candidate_count"),
        "warning": "Recurring observation is contract-only; scheduler, daemon, auto-run, live action, and persistence remain disabled.",
    }


def render_report(
    contract: dict[str, Any],
    schedule: dict[str, Any],
    sources: dict[str, Any],
    gate: dict[str, Any],
    payloads: dict[str, dict[str, Any]],
    checklist: dict[str, Any],
) -> str:
    tick = payloads["simulated_observation_tick_001"]
    delta = payloads["simulated_tick_dashboard_delta"]
    candidates = payloads["simulated_tick_work_candidates"]
    event = payloads["simulated_tick_cieu_event"]
    residual = payloads["simulated_tick_residual_delta"]
    stop_abort = payloads["stop_abort_conditions"]
    escalation = payloads["escalation_conditions"]
    top_candidate = candidates["candidates"][0]["title"]
    return "\n".join(
        [
            "# Governed Recurring Observation Loop Contract Report",
            "",
            "## Recurring Contract",
            f"- contract: {contract['recurring_loop_id']}",
            f"- recurrence enabled: {contract['recurrence_enabled']}",
            f"- scheduler enabled: {contract['scheduler_enabled']}",
            f"- daemon enabled: {contract['daemon_enabled']}",
            f"- manual local simulation only: {contract['manual_local_simulation_only']}",
            "",
            "## Recurrence Schedule Draft",
            f"- proposed frequency: {schedule['proposed_frequency']}",
            f"- max ticks per day while disabled: {schedule['max_ticks_per_day']}",
            f"- operator enablement required: {schedule['operator_enablement_required']}",
            "",
            "## Allowed Sources",
            f"- sources: {sources['source_count']}",
            "- all sources are generated/read-model JSON with no network or credential requirement",
            "",
            "## Tick Governance Gate",
            f"- decision: {gate['decision']}",
            f"- simulation only: {gate['allowed_only_as_manual_local_simulation']}",
            "",
            "## Simulated Observation Tick",
            f"- tick id: {tick['tick_id']}",
            f"- sources used: {len(tick['observation_sources_used'])}",
            f"- scheduler used: {tick['scheduler_used']}",
            f"- daemon used: {tick['daemon_used']}",
            "",
            "## Dashboard Delta",
            f"- state change: {delta['state_change_level']}",
            f"- requires review: {delta['requires_review']}",
            "",
            "## Work Candidates",
            f"- candidate count: {candidates['candidate_count']}",
            f"- top candidate: {top_candidate}",
            "",
            "## CIEU Event",
            f"- dry run only: {event['dry_run_only']}",
            f"- persistence enabled: {event['persistence_enabled']}",
            f"- curation required: {event['curation_required']}",
            "",
            "## Residual Delta",
            f"- review required: {residual['next_review_required']}",
            f"- learning eligibility: {residual['learning_eligibility']}",
            "",
            "## Stop/Abort Conditions",
            f"- count: {stop_abort['condition_count']}",
            "- unsafe, external, live, persistence, writeback, gate, and size failures stop the loop",
            "",
            "## Escalation Conditions",
            f"- count: {escalation['condition_count']}",
            "- escalations route to the role best able to preserve mission and boundaries",
            "",
            "## Manual Enablement Checklist",
            f"- item count: {len(checklist['checklist_items'])}",
            "- no item is enabled, approved, complete, live, or active",
            "",
            "## Why Scheduler/Daemon/Auto-Run Remain Disabled",
            "L4.8 defines the contract and simulates one manual tick only. Recurrence requires future operator-reviewed enablement, a scheduler sandbox, a daemon lifecycle policy, governance gates, and stop/abort handling.",
            "",
        ]
    )


def build() -> None:
    GENERATED.mkdir(parents=True, exist_ok=True)
    contract = build_recurring_loop_contract()
    schedule = build_recurrence_schedule_draft()
    sources = build_allowed_observation_sources()
    gate = build_tick_governance_gate()

    write_json(GENERATED / "recurring_loop_contract.json", contract)
    write_json(GENERATED / "recurrence_schedule_draft.json", schedule)
    write_json(GENERATED / "allowed_observation_sources.json", sources)
    write_json(GENERATED / "tick_governance_gate.json", gate)

    payloads = simulator.run(GENERATED)
    checklist = build_manual_enablement_checklist()
    readiness = build_readiness_summary(payloads, checklist)

    write_json(GENERATED / "manual_enablement_checklist.json", checklist)
    write_json(GENERATED / "recurring_loop_readiness_summary.json", readiness)
    write_text(
        GENERATED / "recurring_loop_report.md",
        render_report(contract, schedule, sources, gate, payloads, checklist),
    )


def main() -> int:
    build()
    print(f"Wrote recurring observation loop contract artifacts to {GENERATED.relative_to(ROOT)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

