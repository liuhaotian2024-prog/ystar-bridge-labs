from __future__ import annotations

from dataclasses import asdict, dataclass
from typing import Any, Dict, List, Mapping

from office.mission_command.c2_gov_mcp_execution_control import build_c2_gov_mcp_execution_control
from office.mission_command.c2_ygov_action_decision import evaluate_c2_ygov_action


ALLOWED_C3_EXECUTION_MODES = {"owner_handoff", "dry_run_local", "prepare_only", "deny"}


@dataclass(frozen=True)
class C3DecisionReplayRecord:
    action_id: str
    role: str
    replay_decision_id: str
    replay_decision: str
    original_decision_id: str
    decision_matches_current_envelope: bool
    no_hard_gate_crossed: bool
    owner_handoff_only: bool
    gov_mcp_execution_mode: str
    prohibited_next_steps_explicit: bool
    deterministic_reason_codes: List[str]
    external_action_executed: bool = False

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


def replay_c3_decisions(batch: Mapping[str, Any], envelope: Mapping[str, Any]) -> Dict[str, Any]:
    records: List[C3DecisionReplayRecord] = []
    for action in batch.get("actions", []):
        if action.get("role") == "excluded":
            records.append(
                C3DecisionReplayRecord(
                    action_id=action["action_id"],
                    role="excluded",
                    replay_decision_id="excluded_no_replay",
                    replay_decision="deny",
                    original_decision_id=str(action.get("ygov_decision_id")),
                    decision_matches_current_envelope=True,
                    no_hard_gate_crossed=True,
                    owner_handoff_only=True,
                    gov_mcp_execution_mode="deny",
                    prohibited_next_steps_explicit=True,
                    deterministic_reason_codes=["excluded_agent_direct_execution"],
                )
            )
            continue
        packet = {
            "action_id": action["action_id"],
            "capability_domain": action["capability_domain"],
            "risk_tier": action["risk_tier"],
            "target_class": "ai_consultant_agency" if "consult" in str(action.get("target_name", "")).lower() or "consult" in str(action.get("selection_reason", "")).lower() else "ai_heavy_team_with_agent_workflow_bottleneck",
            "channel": "owner_handoff_or_governed_messaging_adapter",
            "proposed_u": "Prepare owner-handoff validation message only.",
            "evidence_refs": action.get("target_evidence_basis", []),
        }
        decision = evaluate_c2_ygov_action(packet, envelope)
        control = build_c2_gov_mcp_execution_control(decision.to_dict())
        records.append(
            C3DecisionReplayRecord(
                action_id=action["action_id"],
                role=str(action.get("role")),
                replay_decision_id=decision.decision_id,
                replay_decision=decision.decision,
                original_decision_id=str(action.get("ygov_decision_id")),
                decision_matches_current_envelope=decision.decision in {"owner_handoff_only", "blocked_by_missing_evidence", "blocked_by_invalid_target"},
                no_hard_gate_crossed=decision.decision != "blocked_by_hard_gate",
                owner_handoff_only=decision.decision != "mcp_execute_allowed",
                gov_mcp_execution_mode=control.execution_mode,
                prohibited_next_steps_explicit=bool(decision.prohibited_next_steps),
                deterministic_reason_codes=list(decision.reason_codes),
            )
        )
    return {
        "report_id": "c3_decision_replay_report",
        "all_consistent": all(validate_c3_decision_replay_record(record.to_dict()) == [] for record in records),
        "external_action_executed": False,
        "records": [record.to_dict() for record in records],
    }


def validate_c3_decision_replay_record(record: Mapping[str, Any]) -> List[str]:
    errors: List[str] = []
    if record.get("external_action_executed") is not False:
        errors.append("replay_must_not_execute_external_action")
    if record.get("no_hard_gate_crossed") is not True:
        errors.append("hard_gate_crossed")
    if record.get("owner_handoff_only") is not True:
        errors.append("agent_direct_execution_was_allowed")
    if record.get("gov_mcp_execution_mode") not in ALLOWED_C3_EXECUTION_MODES:
        errors.append("invalid_c3_gov_mcp_mode")
    if record.get("prohibited_next_steps_explicit") is not True:
        errors.append("missing_prohibited_next_steps")
    if not record.get("deterministic_reason_codes"):
        errors.append("missing_deterministic_reason_codes")
    return errors


def validate_c3_decision_replay_report(report: Mapping[str, Any]) -> List[str]:
    errors = [error for record in report.get("records", []) for error in validate_c3_decision_replay_record(record)]
    if report.get("external_action_executed") is not False:
        errors.append("replay_report_must_not_execute_external_action")
    if len(report.get("records", [])) < 7:
        errors.append("replay_report_must_cover_full_batch")
    return list(dict.fromkeys(errors))
