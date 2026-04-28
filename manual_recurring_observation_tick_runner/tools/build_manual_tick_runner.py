#!/usr/bin/env python3
"""Build L4.9 manual recurring observation tick runner artifacts."""

from __future__ import annotations

import json
import sys
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from manual_recurring_observation_tick_runner.tools import run_manual_observation_tick as runner


PACK = ROOT / "manual_recurring_observation_tick_runner"
GENERATED = PACK / "generated"
NEXT_MILESTONE = runner.NEXT_MILESTONE

REQUIRED_OUTPUTS = [
    "manual_tick_runner_contract.json",
    "manual_tick_request.json",
    "manual_tick_preflight.json",
    "manual_tick_source_validation.json",
    "manual_tick_governance_decision.json",
    "manual_tick_result.json",
    "manual_tick_dashboard_delta.json",
    "manual_tick_work_candidates.json",
    "manual_tick_cieu_event.json",
    "manual_tick_residual_delta.json",
    "manual_tick_run_receipt.json",
    "manual_tick_history_index.json",
    "manual_tick_next_recommendations.json",
]


def write_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


def write_text(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def load_json(path: Path) -> dict[str, Any]:
    data = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(data, dict):
        raise ValueError(f"Expected object JSON: {path}")
    return data


def build_manual_tick_runner_contract() -> dict[str, Any]:
    return {
        "schema_name": "ystar.manual_recurring_observation_tick_runner.generated.manual_tick_runner_contract",
        "schema_version": "v0",
        "manual_tick_runner_id": runner.RUNNER_ID,
        "manual_tick_runner_name": "Manual Recurring Observation Tick Runner",
        "manual_tick_runner_version": "v0",
        "uses_recurring_loop_contract": True,
        "recurring_loop_contract_ref": runner.L48_CONTRACT_REF,
        "uses_allowed_observation_sources": True,
        "uses_tick_governance_gate": True,
        "uses_stop_abort_conditions": True,
        "uses_escalation_conditions": True,
        "manual_trigger_required": True,
        "recurrence_enabled": False,
        "scheduler_enabled": False,
        "daemon_enabled": False,
        "auto_run_enabled": False,
        "manual_local_run_only": True,
        "one_tick_per_invocation": True,
        "tick_run_receipt_required": True,
        "tick_history_index_required": True,
        "cieu_event_required": True,
        "residual_delta_required": True,
        "dashboard_delta_required": True,
        "work_candidates_required": True,
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


def build_manual_tick_request() -> dict[str, Any]:
    return {
        "schema_name": "ystar.manual_recurring_observation_tick_runner.generated.manual_tick_request",
        "schema_version": "v0",
        "request_id": "manual-tick-request-001",
        "requested_by": "operator_or_founder",
        "request_type": "manual_recurring_observation_tick",
        "mission_id": "company-autonomy-runtime-mission",
        "reason": (
            "Run one governed local observation tick under the L4.8 contract and capture "
            "a reviewable receipt trail."
        ),
        "requested_tick_number": 1,
        "manual_trigger": True,
        "recurrence_requested": False,
        "scheduler_requested": False,
        "daemon_requested": False,
        "auto_run_requested": False,
        "live_action_requested": False,
        "external_action_requested": False,
        "brain_writeback_requested": False,
        "memory_ingestion_requested": False,
        "cieu_persistence_requested": False,
    }


def validate_generated_outputs() -> None:
    for name in REQUIRED_OUTPUTS:
        load_json(GENERATED / name)


def build_readiness_summary(payloads: dict[str, dict[str, Any]]) -> dict[str, Any]:
    history = payloads["manual_tick_history_index"]
    return {
        "schema_name": "ystar.manual_recurring_observation_tick_runner.generated.manual_tick_runner_readiness_summary",
        "schema_version": "v0",
        "manual_recurring_observation_tick_runner_defined": True,
        "manual_tick_runner_contract_defined": True,
        "manual_tick_request_defined": True,
        "manual_tick_preflight_defined": True,
        "manual_tick_source_validation_defined": True,
        "manual_tick_governance_decision_defined": True,
        "manual_tick_result_defined": True,
        "manual_tick_dashboard_delta_defined": True,
        "manual_tick_work_candidates_defined": True,
        "manual_tick_cieu_event_defined": True,
        "manual_tick_residual_delta_defined": True,
        "manual_tick_run_receipt_defined": True,
        "manual_tick_history_index_defined": True,
        "manual_tick_next_recommendations_defined": True,
        "manual_trigger_required": True,
        "one_tick_per_invocation": True,
        "total_recorded_ticks": history.get("total_recorded_ticks"),
        "mission_bounded_autonomy_supported": True,
        "founder_sets_mission_agent_team_drives": True,
        "step_by_step_human_prompting_required": False,
        "recurrence_enabled": False,
        "scheduler_enabled": False,
        "daemon_enabled": False,
        "auto_run_enabled": False,
        "manual_local_run_only": True,
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
        "generated_contract": runner.CONTRACT_REF,
        "generated_request": runner.REQUEST_REF,
        "generated_result": runner.RESULT_REF,
        "generated_receipt": runner.RECEIPT_REF,
        "generated_history": runner.HISTORY_REF,
        "generated_cieu_event": runner.CIEU_EVENT_REF,
        "generated_residual_delta": runner.RESIDUAL_DELTA_REF,
        "warning": "Manual tick runner executes exactly one local dry-run tick and does not enable recurrence.",
    }


def render_report(payloads: dict[str, dict[str, Any]], readiness: dict[str, Any]) -> str:
    contract = load_json(GENERATED / "manual_tick_runner_contract.json")
    request = load_json(GENERATED / "manual_tick_request.json")
    preflight = payloads["manual_tick_preflight"]
    source_validation = payloads["manual_tick_source_validation"]
    decision = payloads["manual_tick_governance_decision"]
    result = payloads["manual_tick_result"]
    delta = payloads["manual_tick_dashboard_delta"]
    candidates = payloads["manual_tick_work_candidates"]
    event = payloads["manual_tick_cieu_event"]
    residual = payloads["manual_tick_residual_delta"]
    receipt = payloads["manual_tick_run_receipt"]
    history = payloads["manual_tick_history_index"]
    recommendations = payloads["manual_tick_next_recommendations"]
    return "\n".join(
        [
            "# Manual Recurring Observation Tick Runner Report",
            "",
            "## Manual Tick Runner Contract",
            f"- runner: {contract['manual_tick_runner_id']}",
            f"- one tick per invocation: {contract['one_tick_per_invocation']}",
            f"- scheduler enabled: {contract['scheduler_enabled']}",
            f"- daemon enabled: {contract['daemon_enabled']}",
            "",
            "## Manual Tick Request",
            f"- request id: {request['request_id']}",
            f"- manual trigger: {request['manual_trigger']}",
            f"- requested tick number: {request['requested_tick_number']}",
            "",
            "## Preflight",
            f"- decision: {preflight['preflight_decision']}",
            f"- unsafe request detected: {preflight['unsafe_request_detected']}",
            "",
            "## Source Validation",
            f"- sources checked: {source_validation['sources_checked']}",
            f"- all sources safe: {source_validation['all_sources_safe']}",
            "",
            "## Governance Decision",
            f"- decision: {decision['decision']}",
            f"- local read-only only: {decision['allowed_only_as_manual_local_readonly_tick']}",
            "",
            "## Manual Tick Result",
            f"- status: {result['status']}",
            f"- tick id: {result['tick_id']}",
            f"- sources read: {len(result['sources_read'])}",
            "",
            "## Dashboard Delta",
            f"- state change: {delta['state_change_level']}",
            f"- requires review: {delta['requires_review']}",
            "",
            "## Work Candidates",
            f"- candidate count: {candidates['candidate_count']}",
            f"- top candidate: {candidates['top_candidate']}",
            "",
            "## CIEU Event",
            f"- dry run only: {event['dry_run_only']}",
            f"- persistence enabled: {event['persistence_enabled']}",
            "",
            "## Residual Delta",
            f"- curation required: {residual['curation_required']}",
            f"- next review required: {residual['next_review_required']}",
            "",
            "## Tick Run Receipt",
            f"- receipt id: {receipt['receipt_id']}",
            f"- status: {receipt['status']}",
            "",
            "## Tick History Index",
            f"- total recorded ticks: {history['total_recorded_ticks']}",
            f"- latest tick id: {history['latest_tick_id']}",
            "",
            "## Next Recommendations",
            f"- recommendation count: {recommendations['recommendation_count']}",
            f"- top recommendation: {recommendations['top_recommendation']}",
            "",
            "## Why Scheduler/Daemon/Auto-Run Remain Disabled",
            "This milestone proves one manual local tick only. Recurrence, scheduler, daemon, auto-run, live action, persistence, and writeback stay disabled.",
            "",
            "## Readiness",
            f"- next required milestone: {readiness['next_required_milestone']}",
            "",
        ]
    )


def build() -> None:
    GENERATED.mkdir(parents=True, exist_ok=True)
    contract = build_manual_tick_runner_contract()
    request = build_manual_tick_request()
    write_json(GENERATED / "manual_tick_runner_contract.json", contract)
    write_json(GENERATED / "manual_tick_request.json", request)

    payloads = runner.run(GENERATED / "manual_tick_request.json", GENERATED)
    validate_generated_outputs()
    readiness = build_readiness_summary(payloads)
    write_json(GENERATED / "manual_tick_runner_readiness_summary.json", readiness)
    write_text(GENERATED / "manual_tick_runner_report.md", render_report(payloads, readiness))


def main() -> int:
    build()
    print(f"Wrote manual recurring observation tick runner artifacts to {GENERATED.relative_to(ROOT)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

