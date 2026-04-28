#!/usr/bin/env python3
"""Run one manual local recurring observation tick under the L4.8 contract."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[2]
PACK = ROOT / "manual_recurring_observation_tick_runner"
GENERATED = PACK / "generated"
RUNNER_ID = "manual_recurring_observation_tick_runner_v0"
NEXT_MILESTONE = "L5.0 Review-Gated Learning Candidate Queue v0"

CONTRACT_REF = "manual_recurring_observation_tick_runner/generated/manual_tick_runner_contract.json"
REQUEST_REF = "manual_recurring_observation_tick_runner/generated/manual_tick_request.json"
PREFLIGHT_REF = "manual_recurring_observation_tick_runner/generated/manual_tick_preflight.json"
SOURCE_VALIDATION_REF = "manual_recurring_observation_tick_runner/generated/manual_tick_source_validation.json"
GOVERNANCE_DECISION_REF = "manual_recurring_observation_tick_runner/generated/manual_tick_governance_decision.json"
RESULT_REF = "manual_recurring_observation_tick_runner/generated/manual_tick_result.json"
DASHBOARD_DELTA_REF = "manual_recurring_observation_tick_runner/generated/manual_tick_dashboard_delta.json"
WORK_CANDIDATES_REF = "manual_recurring_observation_tick_runner/generated/manual_tick_work_candidates.json"
CIEU_EVENT_REF = "manual_recurring_observation_tick_runner/generated/manual_tick_cieu_event.json"
RESIDUAL_DELTA_REF = "manual_recurring_observation_tick_runner/generated/manual_tick_residual_delta.json"
RECEIPT_REF = "manual_recurring_observation_tick_runner/generated/manual_tick_run_receipt.json"
HISTORY_REF = "manual_recurring_observation_tick_runner/generated/manual_tick_history_index.json"
NEXT_RECOMMENDATIONS_REF = "manual_recurring_observation_tick_runner/generated/manual_tick_next_recommendations.json"

L48_CONTRACT_REF = "recurring_observation_loop_contract/generated/recurring_loop_contract.json"
L48_SOURCES_REF = "recurring_observation_loop_contract/generated/allowed_observation_sources.json"
L48_GATE_REF = "recurring_observation_loop_contract/generated/tick_governance_gate.json"
L48_STOP_ABORT_REF = "recurring_observation_loop_contract/generated/stop_abort_conditions.json"
L48_ESCALATION_REF = "recurring_observation_loop_contract/generated/escalation_conditions.json"
L48_DASHBOARD_REF = "mission_dashboard_refresh_loop/generated/refreshed_mission_dashboard.json"


class ManualTickError(Exception):
    """Raised when the manual tick cannot run safely."""


def repo_path(relative_path: str) -> Path:
    candidate = Path(relative_path)
    if candidate.is_absolute():
        raise ManualTickError(f"absolute path rejected: {relative_path}")
    resolved = (ROOT / candidate).resolve()
    try:
        resolved.relative_to(ROOT)
    except ValueError as exc:
        raise ManualTickError(f"path escapes repository root: {relative_path}") from exc
    return resolved


def output_dir_path(relative_path: str) -> Path:
    path = repo_path(relative_path)
    try:
        path.relative_to(GENERATED.resolve())
    except ValueError as exc:
        raise ManualTickError(
            "output directory must be manual_recurring_observation_tick_runner/generated"
        ) from exc
    return path


def load_json(path: Path) -> dict[str, Any]:
    data = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(data, dict):
        raise ManualTickError(f"expected object JSON: {path}")
    return data


def write_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


def disabled_request_fields(request: dict[str, Any]) -> list[str]:
    fields = [
        "recurrence_requested",
        "scheduler_requested",
        "daemon_requested",
        "auto_run_requested",
        "live_action_requested",
        "external_action_requested",
        "brain_writeback_requested",
        "memory_ingestion_requested",
        "cieu_persistence_requested",
    ]
    return [field for field in fields if request.get(field) is not False]


def require_contracts_disabled(contract: dict[str, Any], recurring_contract: dict[str, Any]) -> None:
    for payload_name, payload in [
        ("manual_tick_runner_contract", contract),
        ("recurring_loop_contract", recurring_contract),
    ]:
        for field in ["recurrence_enabled", "scheduler_enabled", "daemon_enabled", "auto_run_enabled"]:
            if payload.get(field) is not False:
                raise ManualTickError(f"{payload_name} must keep {field}=false")
    if contract.get("one_tick_per_invocation") is not True:
        raise ManualTickError("manual tick runner must allow exactly one tick per invocation")
    if contract.get("manual_trigger_required") is not True:
        raise ManualTickError("manual trigger must be required")


def build_preflight(
    request: dict[str, Any],
    contract: dict[str, Any],
    recurring_contract: dict[str, Any],
    source_registry: dict[str, Any],
    gate: dict[str, Any],
    stop_abort: dict[str, Any],
    escalation: dict[str, Any],
) -> dict[str, Any]:
    unsafe_fields = disabled_request_fields(request)
    unsafe_detected = bool(unsafe_fields) or request.get("manual_trigger") is not True
    return {
        "schema_name": "ystar.manual_recurring_observation_tick_runner.generated.manual_tick_preflight",
        "schema_version": "v0",
        "preflight_id": "manual-tick-preflight-001",
        "request_id": request["request_id"],
        "contract_loaded": bool(contract),
        "allowed_sources_loaded": bool(source_registry.get("sources")),
        "governance_gate_loaded": bool(gate),
        "stop_abort_conditions_loaded": bool(stop_abort.get("conditions")),
        "escalation_conditions_loaded": bool(escalation.get("conditions")),
        "scheduler_enabled": False,
        "daemon_enabled": False,
        "recurrence_enabled": False,
        "auto_run_enabled": False,
        "unsafe_request_detected": unsafe_detected,
        "preflight_decision": "allow_manual_local_tick" if not unsafe_detected else "deny",
        "notes": {
            "manual_trigger": request.get("manual_trigger"),
            "unsafe_requested_fields": unsafe_fields,
            "recurring_loop_contract_ref": L48_CONTRACT_REF,
            "source_registry_ref": L48_SOURCES_REF,
        },
    }


def validate_sources(source_registry: dict[str, Any], request_id: str) -> tuple[dict[str, Any], list[dict[str, Any]]]:
    allowed: list[dict[str, Any]] = []
    rejected: list[dict[str, Any]] = []
    for source in source_registry.get("sources", []):
        reason = None
        if source.get("safe_to_read_now") is not True:
            reason = "source not marked safe"
        elif source.get("raw_runtime_artifact") is not False:
            reason = "raw runtime source not allowed"
        elif source.get("requires_network") is not False:
            reason = "network source not allowed"
        elif source.get("requires_credentials") is not False:
            reason = "credentialed source not allowed"
        else:
            path = repo_path(str(source["source_path"]))
            if not path.exists():
                reason = "source missing"
            elif path.suffix != ".json":
                reason = "source is not generated JSON"
            elif path.stat().st_size > int(source.get("max_bytes", 0)):
                reason = "source exceeds declared size bound"
        if reason:
            rejected.append({"source_id": source.get("source_id"), "reason": reason})
        else:
            allowed.append(source)

    validation = {
        "schema_name": "ystar.manual_recurring_observation_tick_runner.generated.manual_tick_source_validation",
        "schema_version": "v0",
        "validation_id": "manual-tick-source-validation-001",
        "request_id": request_id,
        "sources_checked": len(source_registry.get("sources", [])),
        "sources_allowed": [
            {"source_id": source["source_id"], "source_path": source["source_path"]}
            for source in allowed
        ],
        "sources_rejected": rejected,
        "all_sources_safe": not rejected,
        "raw_runtime_artifacts_requested": False,
        "db_or_log_sources_requested": False,
        "network_sources_requested": False,
        "credentials_required": False,
        "validation_decision": "allow" if not rejected else "deny",
    }
    return validation, allowed


def build_governance_decision(request: dict[str, Any], preflight: dict[str, Any], validation: dict[str, Any]) -> dict[str, Any]:
    allowed = (
        preflight.get("preflight_decision") == "allow_manual_local_tick"
        and validation.get("validation_decision") == "allow"
    )
    return {
        "schema_name": "ystar.manual_recurring_observation_tick_runner.generated.manual_tick_governance_decision",
        "schema_version": "v0",
        "decision_id": "manual-tick-governance-decision-001",
        "request_id": request["request_id"],
        "decision": "allow_manual_local_tick" if allowed else "deny",
        "decision_reason": (
            "Request is manual, local, read-only, generated-source only, and all recurring/live/writeback flags are disabled."
            if allowed
            else "Request failed preflight or source validation."
        ),
        "allowed_only_as_manual_local_readonly_tick": allowed,
        "recurrence_enabled": False,
        "scheduler_enabled": False,
        "daemon_enabled": False,
        "live_action_allowed": False,
        "external_action_allowed": False,
        "cieu_persistence_allowed": False,
        "brain_writeback_allowed": False,
        "memory_ingestion_allowed": False,
        "operator_approval_required_for_scheduler_enablement": True,
        "notes": "Decision is deterministic local dry-run gating, not Y-star-gov runtime mutation.",
    }


def compact_source_observation(source: dict[str, Any], payload: dict[str, Any]) -> dict[str, Any]:
    keys = [
        "next_required_milestone",
        "state_change_level",
        "mission_bounded_autonomy_supported",
        "dashboard_refresh_loop_ran",
        "agent_team_generated_the_work",
        "tool_invoked_through_bridge",
        "first_governed_tool_wrapper_created",
        "read_only_observation_loop_defined",
        "assets_scored",
        "recurring_observation_loop_contract_defined",
    ]
    observed = {key: payload.get(key) for key in keys if key in payload}
    return {
        "source_id": source["source_id"],
        "source_path": source["source_path"],
        "observed_fields": observed,
    }


def read_allowed_sources(sources: list[dict[str, Any]]) -> list[dict[str, Any]]:
    observations: list[dict[str, Any]] = []
    for source in sources:
        payload = load_json(repo_path(str(source["source_path"])))
        observations.append(compact_source_observation(source, payload))
    return observations


def build_result(request: dict[str, Any], observations: list[dict[str, Any]]) -> dict[str, Any]:
    return {
        "schema_name": "ystar.manual_recurring_observation_tick_runner.generated.manual_tick_result",
        "schema_version": "v0",
        "result_id": "manual-tick-result-001",
        "request_id": request["request_id"],
        "tick_id": "manual-recurring-observation-tick-001",
        "tick_number": 1,
        "status": "success",
        "manual_trigger": True,
        "one_tick_per_invocation": True,
        "recurrence_enabled": False,
        "scheduler_used": False,
        "daemon_used": False,
        "sources_read": [item["source_path"] for item in observations],
        "observed_state_summary": {
            "source_count": len(observations),
            "observed_sources": observations,
            "recurring_contract_loaded": True,
            "manual_tick_executed": True,
        },
        "detected_findings": [
            "Manual one-shot tick completed under the L4.8 recurring observation contract.",
            "Allowed generated/read-model sources were validated before observation.",
            "The tick created a receipt and history index while keeping recurrence disabled.",
        ],
        "safe_opportunities": [
            NEXT_MILESTONE,
            "Use the receipt and residual delta to seed a review-gated learning candidate queue.",
            "Prepare curated learning review without enabling brain or memory writeback.",
        ],
        "blocked_risks": [
            "recurrence remains disabled",
            "scheduler remains disabled",
            "daemon remains disabled",
            "live and external actions remain disabled",
            "CIEU persistence and writeback remain disabled",
        ],
        "real_action_executed": False,
        "external_action_executed": False,
        "live_action_enabled": False,
    }


def build_dashboard_delta(result: dict[str, Any]) -> dict[str, Any]:
    return {
        "schema_name": "ystar.manual_recurring_observation_tick_runner.generated.manual_tick_dashboard_delta",
        "schema_version": "v0",
        "delta_id": "manual-tick-dashboard-delta-001",
        "tick_id": result["tick_id"],
        "previous_dashboard_ref": L48_DASHBOARD_REF,
        "current_dashboard_ref": L48_DASHBOARD_REF,
        "detected_changes": [
            "manual one-shot tick runner now executes under the L4.8 contract",
            "tick run receipt and history index are generated",
            "next step shifts from observation execution to review-gated learning candidate queue",
        ],
        "mission_progress_summary": (
            "The company can now manually run one governed recurring observation tick and capture "
            "a reviewable dry-run evidence trail without enabling recurrence."
        ),
        "state_change_level": "meaningful",
        "requires_review": True,
        "direct_brain_writeback_allowed": False,
        "direct_memory_ingestion_allowed": False,
    }


def build_work_candidates(result: dict[str, Any]) -> dict[str, Any]:
    candidates = [
        {
            "candidate_id": "manual-tick-work-001",
            "title": NEXT_MILESTONE,
            "recommended_owner_agent": "Maya-Governance",
            "supporting_agents": ["Samantha-Secretary", "Leo-Kernel", "Aiden-CEO"],
            "risk_tier": "medium",
            "source_evidence_refs": [RESULT_REF, DASHBOARD_DELTA_REF, CIEU_EVENT_REF, RESIDUAL_DELTA_REF],
            "requires_y_star_gov": True,
            "requires_operator_approval": True,
            "requires_cieu_event": True,
            "live_enabled": False,
            "external_action_enabled": False,
            "rationale": "Manual tick evidence should next become a review-gated learning candidate, not direct memory.",
        },
        {
            "candidate_id": "manual-tick-work-002",
            "title": "Define tick receipt review rubric v0",
            "recommended_owner_agent": "Samantha-Secretary",
            "supporting_agents": ["Maya-Governance"],
            "risk_tier": "low",
            "source_evidence_refs": [RECEIPT_REF],
            "requires_y_star_gov": True,
            "requires_operator_approval": False,
            "requires_cieu_event": True,
            "live_enabled": False,
            "external_action_enabled": False,
            "rationale": "Receipts need deterministic review fields before learning candidates can be queued.",
        },
        {
            "candidate_id": "manual-tick-work-003",
            "title": "Add manual tick regression fixture v0",
            "recommended_owner_agent": "Ryan-Platform",
            "supporting_agents": ["Ethan-CTO"],
            "risk_tier": "low",
            "source_evidence_refs": [HISTORY_REF],
            "requires_y_star_gov": True,
            "requires_operator_approval": False,
            "requires_cieu_event": True,
            "live_enabled": False,
            "external_action_enabled": False,
            "rationale": "A stable manual tick fixture protects future recurring-loop changes.",
        },
    ]
    return {
        "schema_name": "ystar.manual_recurring_observation_tick_runner.generated.manual_tick_work_candidates",
        "schema_version": "v0",
        "tick_id": result["tick_id"],
        "candidate_count": len(candidates),
        "candidates": candidates,
        "top_candidate": NEXT_MILESTONE,
        "live_enabled": False,
        "external_action_enabled": False,
    }


def build_cieu_event(
    request: dict[str, Any],
    result: dict[str, Any],
    dashboard_delta: dict[str, Any],
    work_candidates: dict[str, Any],
) -> dict[str, Any]:
    return {
        "schema_name": "ystar.manual_recurring_observation_tick_runner.generated.manual_tick_cieu_event",
        "schema_version": "v0",
        "event_id": "manual-tick-cieu-event-001",
        "dry_run_only": True,
        "persistence_enabled": False,
        "manual_tick_runner_id": RUNNER_ID,
        "request_id": request["request_id"],
        "tick_id": result["tick_id"],
        "Xt": {
            "manual_tick_request_ref": REQUEST_REF,
            "runner_contract_ref": CONTRACT_REF,
            "recurring_loop_contract_ref": L48_CONTRACT_REF,
        },
        "U": "manual local one-shot recurring observation tick",
        "Y_star": "mission-bounded company observes generated evidence and prepares review-gated learning candidates",
        "predicted_Y_t1": {
            "manual_tick_result_defined": True,
            "tick_run_receipt_defined": True,
            "review_gated_learning_next": True,
            "scheduler_enabled": False,
        },
        "predicted_R_t1": {
            "risk_tier": "low",
            "requires_curation": True,
            "persistence_enabled": False,
        },
        "actual_Y_t1": {
            "manual_tick_result_defined": result["status"] == "success",
            "dashboard_delta_defined": True,
            "work_candidates_defined": work_candidates["candidate_count"] >= 3,
        },
        "actual_R_t1": {
            "real_action_executed": False,
            "external_action_executed": False,
            "persistence_enabled": False,
        },
        "residual_delta": {
            "summary": "Manual tick matched expected local read-only behavior.",
            "state_change_level": dashboard_delta["state_change_level"],
            "unresolved_items": ["review-gated learning candidate queue remains to be built"],
        },
        "evidence_refs": [REQUEST_REF, PREFLIGHT_REF, SOURCE_VALIDATION_REF, GOVERNANCE_DECISION_REF, RESULT_REF],
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
        "schema_name": "ystar.manual_recurring_observation_tick_runner.generated.manual_tick_residual_delta",
        "schema_version": "v0",
        "delta_id": "manual-tick-residual-delta-001",
        "event_id": event["event_id"],
        "predicted_vs_actual_summary": "Manual one-shot tick produced the expected dry-run observation trail.",
        "residual_delta": event["residual_delta"],
        "learning_eligibility": False,
        "curation_required": True,
        "direct_brain_writeback_allowed": False,
        "direct_memory_ingestion_allowed": False,
        "next_review_required": True,
        "notes": "Residual may inform a future review-gated queue but cannot write memory directly.",
    }


def build_receipt(request: dict[str, Any], result: dict[str, Any]) -> dict[str, Any]:
    created_artifacts = [
        PREFLIGHT_REF,
        SOURCE_VALIDATION_REF,
        GOVERNANCE_DECISION_REF,
        RESULT_REF,
        DASHBOARD_DELTA_REF,
        WORK_CANDIDATES_REF,
        CIEU_EVENT_REF,
        RESIDUAL_DELTA_REF,
    ]
    return {
        "schema_name": "ystar.manual_recurring_observation_tick_runner.generated.manual_tick_run_receipt",
        "schema_version": "v0",
        "receipt_id": "manual-tick-run-receipt-001",
        "request_id": request["request_id"],
        "tick_id": result["tick_id"],
        "status": "success",
        "preflight_ref": PREFLIGHT_REF,
        "source_validation_ref": SOURCE_VALIDATION_REF,
        "governance_decision_ref": GOVERNANCE_DECISION_REF,
        "manual_tick_result_ref": RESULT_REF,
        "dashboard_delta_ref": DASHBOARD_DELTA_REF,
        "work_candidates_ref": WORK_CANDIDATES_REF,
        "cieu_event_ref": CIEU_EVENT_REF,
        "residual_delta_ref": RESIDUAL_DELTA_REF,
        "created_artifacts": created_artifacts,
        "manual_trigger": True,
        "scheduler_used": False,
        "daemon_used": False,
        "real_action_executed": False,
        "external_action_executed": False,
    }


def build_history(receipt: dict[str, Any]) -> dict[str, Any]:
    return {
        "schema_name": "ystar.manual_recurring_observation_tick_runner.generated.manual_tick_history_index",
        "schema_version": "v0",
        "history_id": "manual-tick-history-index-001",
        "manual_tick_runner_id": RUNNER_ID,
        "total_recorded_ticks": 1,
        "latest_tick_id": receipt["tick_id"],
        "tick_receipts": [
            {
                "tick_id": receipt["tick_id"],
                "receipt_ref": RECEIPT_REF,
                "status": receipt["status"],
            }
        ],
        "scheduler_enabled": False,
        "daemon_enabled": False,
        "recurrence_enabled": False,
        "notes": "Generated history index records the single manual dry-run tick only.",
    }


def build_next_recommendations() -> dict[str, Any]:
    recommendations = [
        {
            "recommendation_id": "manual-tick-next-001",
            "title": NEXT_MILESTONE,
            "recommended_owner_agent": "Maya-Governance",
            "risk_tier": "medium",
            "depends_on": [RECEIPT_REF, CIEU_EVENT_REF, RESIDUAL_DELTA_REF],
            "requires_y_star_gov": True,
            "requires_operator_approval": True,
            "requires_cieu_event": True,
            "live_enabled": False,
            "external_action_enabled": False,
            "rationale": "Manual tick evidence must be reviewed before it can inform learning.",
        },
        {
            "recommendation_id": "manual-tick-next-002",
            "title": "Create tick evidence curation checklist v0",
            "recommended_owner_agent": "Samantha-Secretary",
            "risk_tier": "low",
            "depends_on": [RESIDUAL_DELTA_REF],
            "requires_y_star_gov": True,
            "requires_operator_approval": False,
            "requires_cieu_event": True,
            "live_enabled": False,
            "external_action_enabled": False,
            "rationale": "A checklist helps distinguish evidence from learning candidates.",
        },
        {
            "recommendation_id": "manual-tick-next-003",
            "title": "Define learning candidate rejection reasons v0",
            "recommended_owner_agent": "Leo-Kernel",
            "risk_tier": "low",
            "depends_on": [WORK_CANDIDATES_REF],
            "requires_y_star_gov": True,
            "requires_operator_approval": False,
            "requires_cieu_event": True,
            "live_enabled": False,
            "external_action_enabled": False,
            "rationale": "Fail-closed rejection reasons are needed before any future candidate queue.",
        },
    ]
    return {
        "schema_name": "ystar.manual_recurring_observation_tick_runner.generated.manual_tick_next_recommendations",
        "schema_version": "v0",
        "recommendation_count": len(recommendations),
        "recommendations": recommendations,
        "top_recommendation": NEXT_MILESTONE,
    }


def run(request_path: Path, output_dir: Path) -> dict[str, dict[str, Any]]:
    output_dir.mkdir(parents=True, exist_ok=True)
    request = load_json(request_path)
    contract = load_json(GENERATED / "manual_tick_runner_contract.json")
    recurring_contract = load_json(repo_path(L48_CONTRACT_REF))
    source_registry = load_json(repo_path(L48_SOURCES_REF))
    gate = load_json(repo_path(L48_GATE_REF))
    stop_abort = load_json(repo_path(L48_STOP_ABORT_REF))
    escalation = load_json(repo_path(L48_ESCALATION_REF))

    require_contracts_disabled(contract, recurring_contract)
    preflight = build_preflight(
        request,
        contract,
        recurring_contract,
        source_registry,
        gate,
        stop_abort,
        escalation,
    )
    source_validation, allowed_sources = validate_sources(source_registry, request["request_id"])
    decision = build_governance_decision(request, preflight, source_validation)
    if preflight["preflight_decision"] != "allow_manual_local_tick":
        raise ManualTickError("manual tick request failed preflight")
    if source_validation["validation_decision"] != "allow":
        raise ManualTickError("manual tick source validation failed")
    if decision["decision"] != "allow_manual_local_tick":
        raise ManualTickError("manual tick governance decision denied")

    observations = read_allowed_sources(allowed_sources)
    result = build_result(request, observations)
    dashboard_delta = build_dashboard_delta(result)
    work_candidates = build_work_candidates(result)
    cieu_event = build_cieu_event(request, result, dashboard_delta, work_candidates)
    residual_delta = build_residual_delta(cieu_event)
    receipt = build_receipt(request, result)
    history = build_history(receipt)
    next_recommendations = build_next_recommendations()

    payloads = {
        "manual_tick_preflight": preflight,
        "manual_tick_source_validation": source_validation,
        "manual_tick_governance_decision": decision,
        "manual_tick_result": result,
        "manual_tick_dashboard_delta": dashboard_delta,
        "manual_tick_work_candidates": work_candidates,
        "manual_tick_cieu_event": cieu_event,
        "manual_tick_residual_delta": residual_delta,
        "manual_tick_run_receipt": receipt,
        "manual_tick_history_index": history,
        "manual_tick_next_recommendations": next_recommendations,
    }
    for name, payload in payloads.items():
        write_json(output_dir / f"{name}.json", payload)
    return payloads


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Run one manual local observation tick.")
    parser.add_argument("--request", required=True, help="Generated manual tick request JSON.")
    parser.add_argument(
        "--output-dir",
        default=str(GENERATED.relative_to(ROOT)),
        help="Output directory under manual_recurring_observation_tick_runner/generated.",
    )
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv)
    request_path = repo_path(args.request)
    output_dir = output_dir_path(args.output_dir)
    run(request_path, output_dir)
    print(f"Wrote manual recurring observation tick artifacts to {output_dir.relative_to(ROOT)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

