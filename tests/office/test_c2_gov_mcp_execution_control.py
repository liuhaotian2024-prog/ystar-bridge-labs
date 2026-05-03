from __future__ import annotations

from pathlib import Path

from office.mission_command.c2_action_queue import build_c2_action_queue
from office.mission_command.c2_constitutional_activation import build_c2_activation_packet
from office.mission_command.c2_gov_mcp_execution_control import (
    build_c2_gov_mcp_execution_control,
    mode_for_ygov_decision,
    validate_c2_execution_control,
)


ROOT = Path(__file__).resolve().parents[2]


def test_c2_execution_control_owner_handoff_for_pending_activation() -> None:
    activation = build_c2_activation_packet(ROOT).to_dict()
    decision = build_c2_action_queue(ROOT, activation)["candidates"][0]["ygov_decision"]
    control = build_c2_gov_mcp_execution_control(decision)
    assert control.execution_mode == "owner_handoff"
    assert control.external_action_executed is False
    assert validate_c2_execution_control(control) == []


def test_c2_execution_control_maps_denials() -> None:
    assert mode_for_ygov_decision({"decision": "blocked_by_hard_gate"}) == "deny"
    assert mode_for_ygov_decision({"decision": "blocked_by_scope_mismatch"}) == "deny"


def test_c2_execution_control_never_runs_live_execute_mode() -> None:
    control = build_c2_gov_mcp_execution_control({"action_id": "a1", "decision": "mcp_execute_allowed"})
    assert control.execution_mode == "dry_run_local"
    assert "c2_must_not_run_live_mcp_execute_mode" not in validate_c2_execution_control(control)


def test_c2_execution_contract_declares_future_interface() -> None:
    control = build_c2_gov_mcp_execution_control({"action_id": "a1", "decision": "owner_handoff_only"})
    assert "action_intent_packet" in control.input_packet_schema
    assert "ygov_decision_envelope" in control.input_packet_schema
    assert "mcp_execution_contract" in control.input_packet_schema
    assert control.no_secret_printing is True
    assert control.no_credential_disclosure is True
