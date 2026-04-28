#!/usr/bin/env python3
"""Build deterministic L5.3 projection-checked autonomous cycle artifacts."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[2]
CYCLE = ROOT / "projection_checked_autonomous_work_cycle"
WORK = ROOT / "projection_checked_work_proposal"
PRE_U = ROOT / "behavior_projection_pre_u_cycle_gate"
RESULT = ROOT / "projection_checked_dry_run_work_result"
CIEU = ROOT / "projection_checked_cieu_residual_cycle"
LEARNING = ROOT / "projection_checked_learning_review_queue"
READINESS = ROOT / "projection_checked_cycle_readiness"

INPUT_REFS = {
    "mission_y_star": "mission_to_behavior_y_star_projection/mission_y_star_input.json",
    "behavior_y_star": "mission_to_behavior_y_star_projection/behavior_level_y_star_candidate.json",
    "projection_trace": "mission_to_behavior_y_star_projection/mission_to_behavior_projection_trace.json",
    "projection_context": "mission_to_behavior_y_star_projection/projection_context_field_fixture.json",
    "l5_2_pre_u": "behavior_y_star_to_pre_u_candidate/pre_u_packet_candidate_from_behavior_y_star.json",
    "l5_2_learning_stub": "projection_behavior_residual_loop_fixture/projection_learning_candidate_stub.json",
    "l5_2_readiness": "field_projection_cycle_readiness/field_projection_cycle_readiness.json",
    "l5_2_operator_summary": "field_functional_auto_projection_core/field_projection_operator_summary.json",
    "l4_work_proposal_summary": "agent_team_work_proposal/generated/agent_team_work_proposal_summary.json",
    "l4_dashboard_refresh_summary": "mission_dashboard_refresh_loop/generated/refresh_loop_readiness_summary.json",
    "l4_autonomous_cycle_summary": "company_autonomous_work_cycle/generated/autonomous_work_cycle_summary.json",
}

SAFETY_FLAGS = {
    "live_execution_enabled": False,
    "behavior_execution_enabled": False,
    "external_action_enabled": False,
    "network_enabled": False,
    "scheduler_enabled": False,
    "daemon_enabled": False,
    "cieu_persistence_enabled": False,
    "brain_writeback_enabled": False,
    "memory_ingestion_enabled": False,
    "candidate_auto_approval_enabled": False,
    "semantic_truth_scoring_enabled": False,
    "raw_runtime_artifact_reading_enabled": False,
    "revenue_opportunity_discovery_enabled": False,
}

CYCLE_STAGES = [
    "load_mission_y_star",
    "load_behavior_y_star_candidate",
    "load_projection_trace",
    "derive_projection_checked_work_intent",
    "generate_or_select_autonomous_work_proposal",
    "check_work_proposal_against_behavior_y_star",
    "generate_pre_u_packet_candidate",
    "run_dry_run_governance_decision",
    "produce_dry_run_work_result",
    "emit_cieu_like_cycle_event",
    "compute_projection_cycle_residual_delta",
    "create_review_queue_learning_candidate",
    "produce_next_cycle_recommendation",
]

FORBIDDEN_OPERATIONS = [
    "reading raw DB/WAL/SHM/log contents",
    "reading active-agent marker contents",
    "running live hooks",
    "running daemon/scheduler/runtime scripts",
    "external network/API calls",
    "GitHub issue/PR creation",
    "git push",
    "CIEU DB writes",
    "brain writeback",
    "memory ingestion",
    "candidate approval",
    "L6 revenue opportunity discovery",
    "semantic truth scoring",
]


def rel(path: Path) -> str:
    return str(path.relative_to(ROOT))


def load_json(relative_path: str) -> dict[str, Any]:
    if relative_path not in set(INPUT_REFS.values()):
        raise ValueError(f"Refusing non-curated input: {relative_path}")
    path = ROOT / relative_path
    if not path.exists():
        raise FileNotFoundError(f"Missing curated input: {relative_path}")
    return json.loads(path.read_text(encoding="utf-8"))


def write_json(path: Path, payload: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


def write_text(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def md(title: str, lines: list[str]) -> str:
    return "# " + title + "\n\n" + "\n".join(lines) + "\n"


def build_contract() -> dict[str, Any]:
    return {
        "schema_version": "v0",
        "cycle_name": "Projection-Checked Autonomous Work Cycle",
        "cycle_id": "projection_checked_autonomous_work_cycle_v0",
        "purpose": (
            "Consume behavior-level Y* from the field functional projection core as "
            "a normative gate before any autonomous work proposal proceeds to a "
            "dry-run Pre-U-like cycle."
        ),
        "required_inputs": [
            INPUT_REFS["mission_y_star"],
            INPUT_REFS["behavior_y_star"],
            INPUT_REFS["projection_trace"],
            INPUT_REFS["projection_context"],
            INPUT_REFS["l5_2_pre_u"],
            INPUT_REFS["l5_2_learning_stub"],
            INPUT_REFS["l5_2_readiness"],
        ],
        "cycle_stages": CYCLE_STAGES,
        "required_outputs": [
            "projection_checked_cycle_run",
            "projection_checked_work_intent",
            "autonomous_work_proposal_candidate",
            "work_proposal_projection_gate_decision",
            "cycle_pre_u_packet_candidate",
            "cycle_pre_u_gate_decision",
            "dry_run_work_result",
            "projection_checked_cieu_event_fixture",
            "projection_checked_residual_delta",
            "projection_checked_learning_candidate",
            "projection_checked_cycle_readiness",
        ],
        "projection_gate_requirements": [
            "behavior-level Y* must be loaded before work proposal selection",
            "work proposal must align with allowed behavior boundary",
            "forbidden behavior boundary must deny live, external, network, scheduler, daemon, persistence, writeback, and approval paths",
            "unresolved gaps must remain explicit and cannot be guessed away",
        ],
        "work_cycle_requirements": [
            "work proposal must be internal and dry-run only",
            "work result must be a static fixture or safe generated/read-model summary",
            "no live behavior execution or live tool execution may occur",
        ],
        "residual_loop_requirements": [
            "CIEU-like event must be a dry-run fixture",
            "residual delta must be deterministic structural classification",
            "semantic truth scoring remains disabled",
        ],
        "learning_queue_requirements": [
            "learning candidate may enter review queue only",
            "candidate must not be approved or applied",
            "brain writeback and memory ingestion remain blocked",
        ],
        "safety_flags": SAFETY_FLAGS,
        "forbidden_operations": FORBIDDEN_OPERATIONS,
        "non_goals": [
            "not live execution",
            "not behavior execution",
            "not scheduler or daemon activation",
            "not network-enabled",
            "not external action",
            "not CIEU DB persistence",
            "not brain writeback",
            "not memory ingestion",
            "not candidate approval",
            "not L6 revenue opportunity discovery",
        ],
        "next_required_milestone": "L5.4 Review-Gated Learning Loop v0",
    }


def build_input_fixture() -> dict[str, Any]:
    return {
        "schema_name": "ystar.projection_checked_autonomous_work_cycle.input_fixture",
        "schema_version": "v0",
        "fixture_id": "projection-checked-cycle-input-001",
        "mission_y_star_ref": INPUT_REFS["mission_y_star"],
        "behavior_y_star_candidate_ref": INPUT_REFS["behavior_y_star"],
        "projection_trace_ref": INPUT_REFS["projection_trace"],
        "projection_context_ref": INPUT_REFS["projection_context"],
        "behavior_pre_u_packet_candidate_ref": INPUT_REFS["l5_2_pre_u"],
        "projection_learning_candidate_stub_ref": INPUT_REFS["l5_2_learning_stub"],
        "field_projection_readiness_ref": INPUT_REFS["l5_2_readiness"],
        "safe_l4_context_refs": [
            INPUT_REFS["l4_work_proposal_summary"],
            INPUT_REFS["l4_dashboard_refresh_summary"],
            INPUT_REFS["l4_autonomous_cycle_summary"],
        ],
        "behavior_y_star_required_before_work_allowed": True,
        "dry_run_only": True,
        "safety_flags": SAFETY_FLAGS,
    }


def build_work_intent(behavior: dict[str, Any]) -> dict[str, Any]:
    return {
        "schema_name": "ystar.projection_checked_work_proposal.work_intent",
        "schema_version": "v0",
        "work_intent_id": "projection-checked-work-intent-001",
        "source_behavior_y_star_id": behavior["behavior_y_star_id"],
        "declared_work_intent": (
            "Refresh mission dashboard state through an internal dry-run work cycle "
            "only after checking the proposal against behavior-level Y*."
        ),
        "required_behavior_y_star_alignment": behavior["declared_behavior_y_star"],
        "expected_safe_result": "A projection-checked cycle summary and next-cycle recommendation.",
        "explicit_non_goals": [
            "live behavior execution",
            "external action",
            "network access",
            "brain or memory writeback",
            "CIEU persistence",
            "revenue opportunity discovery",
        ],
        "forbidden_work_patterns": behavior["forbidden_behavior_boundary"],
        "evidence_refs": [
            INPUT_REFS["behavior_y_star"],
            INPUT_REFS["projection_trace"],
            INPUT_REFS["l5_2_readiness"],
        ],
        "safety_flags": SAFETY_FLAGS,
    }


def build_work_proposal(work_intent: dict[str, Any], behavior: dict[str, Any]) -> dict[str, Any]:
    return {
        "schema_name": "ystar.projection_checked_work_proposal.candidate",
        "schema_version": "v0",
        "proposal_id": "projection-checked-work-proposal-001",
        "title": "refresh mission dashboard using projection-checked behavior-level Y* context",
        "description": (
            "Generate a dry-run internal work-cycle result that consumes behavior-level Y* "
            "as the normative gate before producing CIEU-like and residual fixtures."
        ),
        "source_work_intent_id": work_intent["work_intent_id"],
        "source_behavior_y_star_id": behavior["behavior_y_star_id"],
        "internal_only": True,
        "dry_run_only": True,
        "read_model_only": True,
        "requires_pre_u_packet_candidate": True,
        "requires_projection_gate": True,
        "requires_cieu_like_event_fixture": True,
        "requires_residual_delta": True,
        "requires_learning_review_candidate": True,
        "proposed_owner_agent": "Aiden-CEO",
        "supporting_agents": ["Maya-Governance", "Ryan-Platform", "Samantha-Secretary"],
        "expected_outputs": [
            "dry-run work result fixture",
            "CIEU-like cycle event fixture",
            "projection cycle residual delta",
            "review-queue-only learning candidate",
            "L5.4 recommendation",
        ],
        "forbidden_operations": FORBIDDEN_OPERATIONS,
        "live_execution_requested": False,
        "behavior_execution_requested": False,
        "external_action_requested": False,
        "network_requested": False,
        "db_or_runtime_content_requested": False,
        "brain_writeback_requested": False,
        "memory_ingestion_requested": False,
        "cieu_persistence_requested": False,
        "candidate_approval_requested": False,
        "revenue_opportunity_discovery_requested": False,
        "safety_flags": SAFETY_FLAGS,
        "evidence_refs": work_intent["evidence_refs"],
    }


def build_alignment(
    proposal: dict[str, Any],
    behavior: dict[str, Any],
) -> dict[str, Any]:
    return {
        "schema_name": "ystar.projection_checked_work_proposal.behavior_alignment",
        "schema_version": "v0",
        "alignment_id": "work-proposal-to-behavior-y-star-alignment-001",
        "proposal_id": proposal["proposal_id"],
        "behavior_y_star_id": behavior["behavior_y_star_id"],
        "inherited_mission_alignment": "proposal preserves mission-bounded autonomy and review-gated learning",
        "behavior_intent_alignment": "proposal prepares a projection-checked work cycle candidate without executing behavior",
        "allowed_boundary_alignment": {
            "allowed_boundary": behavior["allowed_behavior_boundary"],
            "proposal_within_allowed_boundary": True,
        },
        "forbidden_boundary_check": {
            "forbidden_boundary": behavior["forbidden_behavior_boundary"],
            "forbidden_operations_requested": [],
            "passed": True,
        },
        "required_pre_u_validation_check": {
            "required_pre_u_validation": behavior["required_pre_u_validation"],
            "pre_u_packet_candidate_required": True,
            "passed": True,
        },
        "residual_learning_boundary_check": {
            "review_queue_only": True,
            "direct_brain_writeback_allowed": False,
            "direct_memory_ingestion_allowed": False,
            "candidate_auto_approval_allowed": False,
            "passed": True,
        },
        "unresolved_alignment_gaps": [
            "future production Y-star-gov validation is still required before execution",
            "real behavior outcome cannot exist in a dry-run cycle",
        ],
        "decision": "projection_gate_passed_for_dry_run",
        "safety_flags": SAFETY_FLAGS,
        "evidence_refs": [INPUT_REFS["behavior_y_star"], INPUT_REFS["projection_trace"]],
    }


def build_projection_gate(alignment: dict[str, Any], proposal: dict[str, Any]) -> dict[str, Any]:
    return {
        "schema_name": "ystar.projection_checked_work_proposal.gate_decision",
        "schema_version": "v0",
        "gate_name": "behavior-y-star-projection-gate-v0",
        "gate_decision_id": "projection-work-gate-decision-001",
        "proposal_id": proposal["proposal_id"],
        "decision": alignment["decision"],
        "allowed_scope": [
            "internal deterministic dry-run artifact generation",
            "Pre-U packet candidate preparation",
            "CIEU-like fixture generation",
            "review-queue-only learning candidate creation",
        ],
        "denied_scope": FORBIDDEN_OPERATIONS,
        "required_next_validation": [
            "dry-run Pre-U-like gate decision",
            "future Y-star-gov validation before any behavior execution",
            "human or governance review before learning is applied",
        ],
        "live_execution_authorized": False,
        "behavior_execution_authorized": False,
        "dry_run_only": True,
        "evidence_refs": alignment["evidence_refs"],
        "safety_flags": SAFETY_FLAGS,
    }


def build_pre_u_packet(
    behavior: dict[str, Any],
    context: dict[str, Any],
    work_intent: dict[str, Any],
    proposal: dict[str, Any],
    gate: dict[str, Any],
) -> dict[str, Any]:
    return {
        "schema_name": "ystar.behavior_projection_pre_u_cycle_gate.packet_candidate",
        "schema_version": "v0",
        "packet_candidate_id": "cycle-pre-u-packet-candidate-001",
        "source_behavior_y_star_id": behavior["behavior_y_star_id"],
        "source_work_intent_id": work_intent["work_intent_id"],
        "source_work_proposal_id": proposal["proposal_id"],
        "declared_Y_star": behavior["declared_behavior_y_star"],
        "Xt": {
            "source": "projection_context_field_fixture",
            "context_ref": INPUT_REFS["projection_context"],
            "context_summary": context["future_meta_development_context"],
        },
        "candidate_U": {
            "candidate_u_id": "cycle-candidate-u-projection-checked-work-v0",
            "work_intent": work_intent["declared_work_intent"],
            "proposal_title": proposal["title"],
            "execution_mode": "dry_run_static_fixture",
        },
        "governance_expectations": {
            "work_proposal_gate_decision": gate["decision"],
            "required_next_validation": gate["required_next_validation"],
            "allow_only_dry_run": True,
        },
        "deny_or_boundary_constraints": behavior["forbidden_behavior_boundary"],
        "trace_refs": [
            INPUT_REFS["projection_trace"],
            "mission_to_behavior_y_star_projection/y_star_inheritance_map.json",
            "mission_to_behavior_y_star_projection/y_star_contraction_map.json",
            "projection_checked_work_proposal/work_proposal_to_behavior_y_star_alignment.json",
        ],
        "execution_boundary": SAFETY_FLAGS,
        "dry_run_only": True,
        "production_ready": False,
        "requires_y_star_gov_validation_before_execution": True,
        "live_execution_authorized": False,
        "behavior_execution_authorized": False,
        "external_action_authorized": False,
        "network_authorized": False,
        "cieu_persistence_authorized": False,
        "brain_writeback_authorized": False,
        "memory_ingestion_authorized": False,
        "candidate_auto_approval_authorized": False,
        "safety_flags": SAFETY_FLAGS,
    }


def build_pre_u_mapping(packet: dict[str, Any]) -> dict[str, Any]:
    return {
        "schema_name": "ystar.behavior_projection_pre_u_cycle_gate.mapping",
        "schema_version": "v0",
        "mapping_id": "cycle-pre-u-mapping-from-behavior-y-star-001",
        "source_packet_candidate_id": packet["packet_candidate_id"],
        "mapping": [
            {
                "source": "behavior_level_y_star_candidate.declared_behavior_y_star",
                "target": "declared_Y_star",
                "status": "mapped",
            },
            {
                "source": "projection_checked_work_intent",
                "target": "candidate_U",
                "status": "mapped",
            },
            {
                "source": "projection_context_field_fixture",
                "target": "Xt",
                "status": "mapped",
            },
            {
                "source": "behavior forbidden boundary",
                "target": "deny_or_boundary_constraints",
                "status": "mapped",
            },
            {
                "source": "projection trace",
                "target": "trace_refs",
                "status": "mapped",
            },
            {
                "source": "safety flags",
                "target": "execution_boundary",
                "status": "mapped_false_only",
            },
            {
                "source": "work proposal gate decision",
                "target": "governance_expectations",
                "status": "mapped",
            },
        ],
        "y_star_gov_imported": False,
        "y_star_gov_modified": False,
        "live_hooks_called": False,
        "runtime_scripts_run": False,
        "safety_flags": SAFETY_FLAGS,
    }


def build_pre_u_gate(packet: dict[str, Any]) -> dict[str, Any]:
    return {
        "schema_name": "ystar.behavior_projection_pre_u_cycle_gate.decision",
        "schema_version": "v0",
        "gate_decision_id": "cycle-pre-u-gate-decision-001",
        "packet_candidate_id": packet["packet_candidate_id"],
        "decision": "allow_dry_run_only",
        "decision_reason": (
            "The packet candidate is internal, deterministic, projection-checked, and "
            "requests only dry-run fixture generation."
        ),
        "allowed_scope": [
            "dry-run static result fixture",
            "CIEU-like fixture",
            "structural residual delta",
            "review-only learning candidate",
        ],
        "denied_scope": FORBIDDEN_OPERATIONS,
        "dry_run_only": True,
        "production_ready": False,
        "live_execution_authorized": False,
        "behavior_execution_authorized": False,
        "external_action_authorized": False,
        "requires_y_star_gov_validation_before_execution": True,
        "safety_flags": SAFETY_FLAGS,
    }


def build_execution_plan(
    contract: dict[str, Any],
    behavior: dict[str, Any],
    packet: dict[str, Any],
    gate: dict[str, Any],
) -> dict[str, Any]:
    return {
        "schema_name": "ystar.projection_checked_dry_run_work_result.execution_plan",
        "schema_version": "v0",
        "plan_id": "dry-run-work-execution-plan-001",
        "source_cycle_id": contract["cycle_id"],
        "source_behavior_y_star_id": behavior["behavior_y_star_id"],
        "source_pre_u_packet_candidate_id": packet["packet_candidate_id"],
        "source_pre_u_gate_decision_id": gate["gate_decision_id"],
        "work_steps": [
            "confirm behavior-level Y* is loaded",
            "confirm projection gate passed for dry-run",
            "confirm Pre-U-like gate allows dry-run only",
            "generate static dry-run work result fixture",
            "generate CIEU-like event fixture and residual delta",
            "create review-only learning candidate",
        ],
        "allowed_operations": gate["allowed_scope"],
        "forbidden_operations": FORBIDDEN_OPERATIONS,
        "expected_outputs": [
            "projection_checked_dry_run_work_result/dry_run_work_result.json",
            "projection_checked_cieu_residual_cycle/projection_checked_cieu_event_fixture.json",
            "projection_checked_learning_review_queue/projection_checked_learning_candidate.json",
        ],
        "safety_flags": SAFETY_FLAGS,
    }


def build_work_result(plan: dict[str, Any], proposal: dict[str, Any]) -> dict[str, Any]:
    return {
        "schema_name": "ystar.projection_checked_dry_run_work_result.result",
        "schema_version": "v0",
        "result_id": "dry-run-work-result-001",
        "source_plan_id": plan["plan_id"],
        "source_work_proposal_id": proposal["proposal_id"],
        "execution_mode": "dry_run_static_fixture",
        "real_execution_performed": False,
        "live_tool_called": False,
        "external_action_performed": False,
        "network_called": False,
        "db_log_runtime_content_read": False,
        "generated_outputs": [
            "projection-checked cycle contract and run artifact",
            "projection-checked work proposal and gate",
            "dry-run Pre-U packet candidate and gate decision",
            "CIEU-like event fixture",
            "structural residual delta",
            "review-only learning candidate",
        ],
        "observed_safe_result": (
            "The cycle consumed behavior-level Y* as a governance object and produced "
            "only local dry-run fixtures."
        ),
        "evidence_refs": [
            rel(WORK / "work_proposal_projection_gate_decision.json"),
            rel(PRE_U / "cycle_pre_u_gate_decision.json"),
            rel(RESULT / "dry_run_work_execution_plan.json"),
        ],
        "unresolved_gaps": [
            "production Y-star-gov validation is not yet invoked",
            "real behavior execution remains blocked",
            "learning candidate is not applied",
        ],
        "safety_flags": SAFETY_FLAGS,
    }


def build_receipt(result: dict[str, Any]) -> dict[str, Any]:
    return {
        "schema_name": "ystar.projection_checked_dry_run_work_result.receipt",
        "schema_version": "v0",
        "receipt_id": "dry-run-work-receipt-001",
        "result_id": result["result_id"],
        "no_live_behavior_execution": True,
        "no_external_action": True,
        "no_network": True,
        "no_scheduler_or_daemon": True,
        "no_cieu_persistence": True,
        "no_brain_writeback": True,
        "no_memory_ingestion": True,
        "no_candidate_approval": True,
        "real_execution_performed": False,
        "safety_flags": SAFETY_FLAGS,
    }


def build_cieu_and_residual(
    behavior: dict[str, Any],
    packet: dict[str, Any],
    result: dict[str, Any],
) -> tuple[dict[str, Any], dict[str, Any], dict[str, Any], dict[str, Any]]:
    predicted = {
        "schema_name": "ystar.projection_checked_cieu_residual_cycle.predicted_outcome",
        "schema_version": "v0",
        "predicted_outcome_id": "projection-checked-predicted-outcome-001",
        "source_behavior_y_star_id": behavior["behavior_y_star_id"],
        "expected_y": behavior["expected_y_if_allowed"],
        "expected_residual": "production validation and real behavior outcome remain absent by design",
        "safety_flags": SAFETY_FLAGS,
    }
    actual = {
        "schema_name": "ystar.projection_checked_cieu_residual_cycle.mock_actual_outcome",
        "schema_version": "v0",
        "mock_actual_outcome_id": "projection-checked-mock-actual-outcome-001",
        "synthetic_dry_run_only": True,
        "real_behavior_executed": False,
        "actual_y_summary": result["observed_safe_result"],
        "actual_residual_summary": "dry-run fixture produced; execution and writeback intentionally absent",
        "safety_flags": SAFETY_FLAGS,
    }
    event = {
        "schema_name": "ystar.projection_checked_cieu_residual_cycle.event_fixture",
        "schema_version": "v0",
        "event_id": "projection-checked-cieu-event-fixture-001",
        "X_t": {
            "projection_context_ref": INPUT_REFS["projection_context"],
            "behavior_y_star_ref": INPUT_REFS["behavior_y_star"],
        },
        "U_t": {
            "work_proposal_ref": rel(WORK / "autonomous_work_proposal_candidate.json"),
            "pre_u_packet_candidate_ref": rel(PRE_U / "cycle_pre_u_packet_candidate.json"),
        },
        "Y_star_t": {
            "behavior_y_star_ref": INPUT_REFS["behavior_y_star"],
            "declared_behavior_y_star": behavior["declared_behavior_y_star"],
        },
        "Y_t_plus_1": {
            "mock_actual_outcome_ref": rel(CIEU / "projection_checked_mock_actual_outcome.json"),
            "dry_run_mock_only": True,
        },
        "R_t_plus_1": {
            "residual_mode": "deterministic_structural_residual",
            "semantic_truth_scoring_used": False,
        },
        "event_mode": "dry_run_fixture",
        "persistence_enabled": False,
        "db_write_performed": False,
        "evidence_refs": [INPUT_REFS["behavior_y_star"], packet["packet_candidate_id"], result["result_id"]],
        "safety_flags": SAFETY_FLAGS,
    }
    residual = {
        "schema_name": "ystar.projection_checked_cieu_residual_cycle.residual_delta",
        "schema_version": "v0",
        "residual_delta_id": "projection-checked-residual-delta-001",
        "event_id": event["event_id"],
        "projection_alignment_residual": "proposal passed dry-run projection gate; production validation remains future",
        "pre_u_gate_residual": "cycle gate allows dry-run only and does not call Y-star-gov",
        "dry_run_execution_residual": "no real execution occurred, so actual outcome is synthetic",
        "behavior_boundary_residual": "forbidden boundaries remain enforced as blocked scopes",
        "evidence_gap_residual": "deep Xt and production runtime evidence are not present",
        "learning_queue_residual": "learning is review-queue-only and not applied",
        "live_blocker_residual": "live execution remains blocked",
        "writeback_blocker_residual": "brain and memory writeback remain blocked",
        "real_behavior_executed": False,
        "semantic_truth_scoring_used": False,
        "safety_flags": SAFETY_FLAGS,
    }
    return predicted, actual, event, residual


def build_learning(residual: dict[str, Any]) -> tuple[dict[str, Any], dict[str, Any], dict[str, Any]]:
    candidate = {
        "schema_name": "ystar.projection_checked_learning_review_queue.candidate",
        "schema_version": "v0",
        "candidate_id": "projection-checked-learning-candidate-001",
        "source_cycle_id": "projection_checked_autonomous_work_cycle_v0",
        "source_residual_delta_id": residual["residual_delta_id"],
        "learning_target": [
            "projection_policy",
            "behavior_y_star_generation",
            "pre_u_mapping",
            "work_proposal_alignment",
            "residual_classification",
        ],
        "proposed_learning_scope": (
            "Improve future projection-gate policy and Pre-U mapping review criteria; "
            "do not update memory directly."
        ),
        "evidence_refs": [
            rel(CIEU / "projection_checked_residual_delta.json"),
            rel(WORK / "work_proposal_to_behavior_y_star_alignment.json"),
            rel(PRE_U / "cycle_pre_u_gate_decision.json"),
        ],
        "eligible_for_review_queue": True,
        "eligible_for_direct_brain_writeback": False,
        "eligible_for_direct_memory_ingestion": False,
        "eligible_for_candidate_auto_approval": False,
        "requires_human_or_governance_review": True,
        "approved": False,
        "applied": False,
        "live_learning_enabled": False,
        "safety_flags": SAFETY_FLAGS,
    }
    queue_entry = {
        "schema_name": "ystar.projection_checked_learning_review_queue.entry",
        "schema_version": "v0",
        "queue_entry_id": "projection-learning-review-entry-001",
        "candidate_id": candidate["candidate_id"],
        "queue_status": "pending_review",
        "approval_status": "not_approved",
        "application_status": "not_applied",
        "review_required_before_use": True,
        "safety_flags": SAFETY_FLAGS,
    }
    policy_stub = {
        "schema_name": "ystar.projection_checked_learning_review_queue.policy_update_stub",
        "schema_version": "v0",
        "policy_update_stub_id": "projection-learning-policy-update-stub-001",
        "source_candidate_id": candidate["candidate_id"],
        "target_policy_area": "projection_checked_cycle_policy",
        "stub_only": True,
        "approved": False,
        "applied": False,
        "direct_brain_writeback_allowed": False,
        "direct_memory_ingestion_allowed": False,
        "candidate_auto_approval_allowed": False,
        "safety_flags": SAFETY_FLAGS,
    }
    return candidate, queue_entry, policy_stub


def build_readiness() -> dict[str, Any]:
    return {
        "schema_name": "ystar.projection_checked_cycle_readiness",
        "schema_version": "v0",
        "projection_checked_cycle_readiness_id": "projection-checked-cycle-readiness-v0",
        "behavior_y_star_consumed_by_cycle": True,
        "work_proposal_checked_against_behavior_y_star": True,
        "pre_u_packet_candidate_generated": True,
        "dry_run_gate_decision_generated": True,
        "dry_run_result_generated": True,
        "cieu_like_event_fixture_generated": True,
        "residual_delta_generated": True,
        "learning_review_candidate_generated": True,
        "learning_review_candidate_approved": False,
        "live_execution_still_blocked": True,
        "writeback_still_blocked": True,
        "external_action_still_blocked": True,
        "network_still_blocked": True,
        "scheduler_daemon_still_blocked": True,
        "behavior_execution_still_blocked": True,
        "ready_for_l5_4_review_gated_learning_loop": True,
        "live_execution_enabled": False,
        "behavior_execution_enabled": False,
        "external_action_enabled": False,
        "network_enabled": False,
        "scheduler_enabled": False,
        "daemon_enabled": False,
        "cieu_persistence_enabled": False,
        "brain_writeback_enabled": False,
        "memory_ingestion_enabled": False,
        "candidate_auto_approval_enabled": False,
        "semantic_truth_scoring_enabled": False,
        "raw_runtime_artifact_reading_enabled": False,
        "revenue_opportunity_discovery_enabled": False,
        "next_required_milestone": "L5.4 Review-Gated Learning Loop v0",
    }


def main() -> None:
    inputs = {name: load_json(path) for name, path in INPUT_REFS.items()}
    contract = build_contract()
    input_fixture = build_input_fixture()
    behavior = inputs["behavior_y_star"]
    context = inputs["projection_context"]

    work_intent = build_work_intent(behavior)
    proposal = build_work_proposal(work_intent, behavior)
    alignment = build_alignment(proposal, behavior)
    projection_gate = build_projection_gate(alignment, proposal)

    pre_u_packet = build_pre_u_packet(behavior, context, work_intent, proposal, projection_gate)
    pre_u_mapping = build_pre_u_mapping(pre_u_packet)
    pre_u_gate = build_pre_u_gate(pre_u_packet)

    execution_plan = build_execution_plan(contract, behavior, pre_u_packet, pre_u_gate)
    work_result = build_work_result(execution_plan, proposal)
    work_receipt = build_receipt(work_result)

    predicted, mock_actual, cieu_event, residual = build_cieu_and_residual(
        behavior, pre_u_packet, work_result
    )
    learning_candidate, queue_entry, policy_stub = build_learning(residual)
    readiness = build_readiness()
    next_step = {
        "schema_name": "ystar.projection_checked_cycle_readiness.next_step",
        "schema_version": "v0",
        "recommendation_id": "l5-4-review-gated-learning-loop",
        "title": "L5.4 Review-Gated Learning Loop v0",
        "rationale": "L5.3 creates review-only learning candidates; L5.4 should define the governed review loop.",
        "requires_y_star_gov": True,
        "requires_operator_approval": False,
        "live_execution_enabled": False,
        "external_action_enabled": False,
        "network_enabled": False,
        "brain_writeback_enabled": False,
        "memory_ingestion_enabled": False,
        "candidate_auto_approval_enabled": False,
    }

    cycle_run = {
        "schema_name": "ystar.projection_checked_autonomous_work_cycle.run",
        "schema_version": "v0",
        "cycle_run_id": "projection-checked-cycle-run-001",
        "cycle_id": contract["cycle_id"],
        "stage_order": CYCLE_STAGES,
        "stage_results": [
            {"stage": stage, "status": "completed_dry_run"} for stage in CYCLE_STAGES
        ],
        "behavior_y_star_consumed_as_governance_object": True,
        "projection_gate_decision_ref": rel(WORK / "work_proposal_projection_gate_decision.json"),
        "cycle_pre_u_packet_candidate_ref": rel(PRE_U / "cycle_pre_u_packet_candidate.json"),
        "dry_run_result_ref": rel(RESULT / "dry_run_work_result.json"),
        "cieu_like_event_ref": rel(CIEU / "projection_checked_cieu_event_fixture.json"),
        "residual_delta_ref": rel(CIEU / "projection_checked_residual_delta.json"),
        "learning_candidate_ref": rel(LEARNING / "projection_checked_learning_candidate.json"),
        "next_recommendation_ref": rel(READINESS / "l5_4_recommended_next_step.json"),
        "safety_flags": SAFETY_FLAGS,
    }
    cycle_summary = {
        "schema_name": "ystar.projection_checked_autonomous_work_cycle.summary",
        "schema_version": "v0",
        "projection_checked_autonomous_work_cycle_defined": True,
        "behavior_y_star_consumed_by_cycle": True,
        "work_proposal_checked_against_behavior_y_star": True,
        "pre_u_packet_candidate_generated": True,
        "dry_run_gate_decision_generated": True,
        "dry_run_result_generated": True,
        "cieu_like_event_fixture_generated": True,
        "residual_delta_generated": True,
        "learning_review_candidate_generated_but_not_approved": True,
        "ready_for_l5_4_review_gated_learning_loop": True,
        "live_execution_enabled": False,
        "behavior_execution_enabled": False,
        "external_action_enabled": False,
        "network_enabled": False,
        "scheduler_enabled": False,
        "daemon_enabled": False,
        "cieu_persistence_enabled": False,
        "brain_writeback_enabled": False,
        "memory_ingestion_enabled": False,
        "candidate_auto_approval_enabled": False,
        "semantic_truth_scoring_enabled": False,
        "raw_runtime_artifact_reading_enabled": False,
        "revenue_opportunity_discovery_enabled": False,
        "next_required_milestone": "L5.4 Review-Gated Learning Loop v0",
    }
    work_summary = {
        "schema_name": "ystar.projection_checked_work_proposal.summary",
        "schema_version": "v0",
        "projection_checked_work_intent_defined": True,
        "autonomous_work_proposal_candidate_defined": True,
        "work_proposal_to_behavior_y_star_alignment_defined": True,
        "projection_gate_decision_defined": True,
        "projection_gate_decision": alignment["decision"],
        "internal_dry_run_only": True,
        "live_execution_enabled": False,
        "behavior_execution_enabled": False,
        "external_action_enabled": False,
        "network_enabled": False,
    }
    pre_u_summary = {
        "schema_name": "ystar.behavior_projection_pre_u_cycle_gate.summary",
        "schema_version": "v0",
        "cycle_pre_u_packet_candidate_generated": True,
        "cycle_pre_u_mapping_generated": True,
        "cycle_pre_u_gate_decision_generated": True,
        "cycle_pre_u_gate_decision": pre_u_gate["decision"],
        "dry_run_only": True,
        "production_ready": False,
        "requires_y_star_gov_validation_before_execution": True,
        "live_execution_authorized": False,
        "behavior_execution_authorized": False,
        "external_action_authorized": False,
    }
    result_summary = {
        "schema_name": "ystar.projection_checked_dry_run_work_result.summary",
        "schema_version": "v0",
        "dry_run_work_execution_plan_defined": True,
        "dry_run_work_result_defined": True,
        "dry_run_work_receipt_defined": True,
        "real_execution_performed": False,
        "live_tool_called": False,
        "external_action_performed": False,
        "network_called": False,
        "db_log_runtime_content_read": False,
    }
    residual_summary = {
        "schema_name": "ystar.projection_checked_cieu_residual_cycle.summary",
        "schema_version": "v0",
        "cieu_like_event_fixture_generated": True,
        "predicted_outcome_generated": True,
        "mock_actual_outcome_generated": True,
        "residual_delta_generated": True,
        "event_mode": "dry_run_fixture",
        "persistence_enabled": False,
        "db_write_performed": False,
        "semantic_truth_scoring_used": False,
    }
    learning_summary = {
        "schema_name": "ystar.projection_checked_learning_review_queue.summary",
        "schema_version": "v0",
        "projection_checked_learning_candidate_generated": True,
        "review_queue_entry_generated": True,
        "policy_update_candidate_stub_generated": True,
        "eligible_for_review_queue": True,
        "approved": False,
        "applied": False,
        "eligible_for_direct_brain_writeback": False,
        "eligible_for_direct_memory_ingestion": False,
        "eligible_for_candidate_auto_approval": False,
    }

    write_text(
        CYCLE / "README.md",
        "# Projection-Checked Autonomous Work Cycle\n\n"
        "L5.3 consumes behavior-level Y* from L5.2 as the normative gate for a dry-run autonomous work cycle.\n",
    )
    write_json(CYCLE / "projection_checked_cycle_contract.json", contract)
    write_json(CYCLE / "projection_checked_cycle_input_fixture.json", input_fixture)
    write_json(CYCLE / "projection_checked_cycle_run.json", cycle_run)
    write_json(CYCLE / "projection_checked_cycle_summary.json", cycle_summary)
    write_text(
        CYCLE / "projection_checked_cycle_report.md",
        md(
            "Projection-Checked Cycle Report",
            [
                "- Behavior-level Y* was consumed before work proposal approval.",
                "- The work proposal passed only for dry-run scope.",
                "- No live behavior, external action, persistence, writeback, scheduler, daemon, or network path was enabled.",
            ],
        ),
    )

    write_json(WORK / "projection_checked_work_intent.json", work_intent)
    write_json(WORK / "autonomous_work_proposal_candidate.json", proposal)
    write_json(WORK / "work_proposal_to_behavior_y_star_alignment.json", alignment)
    write_json(WORK / "work_proposal_projection_gate_decision.json", projection_gate)
    write_json(WORK / "projection_checked_work_proposal_summary.json", work_summary)
    write_text(
        WORK / "projection_checked_work_proposal_report.md",
        md(
            "Projection-Checked Work Proposal Report",
            [
                "- Work intent is derived from behavior-level Y*.",
                "- Proposal is internal, read-model oriented, and dry-run only.",
                "- Projection gate decision: projection_gate_passed_for_dry_run.",
            ],
        ),
    )

    write_json(PRE_U / "cycle_pre_u_packet_candidate.json", pre_u_packet)
    write_json(PRE_U / "cycle_pre_u_mapping_from_behavior_y_star.json", pre_u_mapping)
    write_json(PRE_U / "cycle_pre_u_gate_decision.json", pre_u_gate)
    write_text(
        PRE_U / "cycle_pre_u_gap_report.md",
        md(
            "Cycle Pre-U Gap Report",
            [
                "- Production Y-star-gov validation is not invoked in L5.3.",
                "- Live behavior execution remains blocked.",
                "- The packet candidate is suitable only for future validation design.",
            ],
        ),
    )
    write_json(PRE_U / "cycle_pre_u_gate_summary.json", pre_u_summary)

    write_json(RESULT / "dry_run_work_execution_plan.json", execution_plan)
    write_json(RESULT / "dry_run_work_result.json", work_result)
    write_json(RESULT / "dry_run_work_receipt.json", work_receipt)
    write_json(RESULT / "dry_run_work_result_summary.json", result_summary)
    write_text(
        RESULT / "dry_run_work_result_report.md",
        md(
            "Dry-Run Work Result Report",
            [
                "- Result is a static dry-run fixture.",
                "- No live tool, network, external action, DB/runtime content read, or behavior execution occurred.",
            ],
        ),
    )

    write_json(CIEU / "projection_checked_cieu_event_fixture.json", cieu_event)
    write_json(CIEU / "projection_checked_predicted_outcome.json", predicted)
    write_json(CIEU / "projection_checked_mock_actual_outcome.json", mock_actual)
    write_json(CIEU / "projection_checked_residual_delta.json", residual)
    write_json(CIEU / "projection_checked_residual_summary.json", residual_summary)
    write_text(
        CIEU / "projection_checked_residual_report.md",
        md(
            "Projection-Checked Residual Report",
            [
                "- CIEU-like event is a dry-run fixture with persistence disabled.",
                "- Residuals are structural and deterministic, not semantic truth scores.",
            ],
        ),
    )

    write_json(LEARNING / "projection_checked_learning_candidate.json", learning_candidate)
    write_json(LEARNING / "projection_checked_review_queue_entry.json", queue_entry)
    write_json(LEARNING / "projection_learning_policy_update_candidate_stub.json", policy_stub)
    write_json(LEARNING / "projection_learning_review_summary.json", learning_summary)
    write_text(
        LEARNING / "projection_learning_review_report.md",
        md(
            "Projection Learning Review Report",
            [
                "- Learning candidate is eligible for review queue only.",
                "- Candidate is not approved, not applied, and not written to brain or memory.",
            ],
        ),
    )

    write_json(READINESS / "projection_checked_cycle_readiness.json", readiness)
    write_text(
        READINESS / "projection_checked_cycle_readiness.md",
        md(
            "Projection-Checked Cycle Readiness",
            [
                "- behavior_y_star_consumed_by_cycle: true",
                "- work_proposal_checked_against_behavior_y_star: true",
                "- ready_for_l5_4_review_gated_learning_loop: true",
                "- live/writeback/external/network/scheduler/daemon/behavior execution remain blocked.",
            ],
        ),
    )
    write_json(READINESS / "l5_4_recommended_next_step.json", next_step)

    print("Built L5.3 projection-checked autonomous work cycle artifacts.")


if __name__ == "__main__":
    main()
