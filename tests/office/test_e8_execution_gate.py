from pathlib import Path

from office.mission_command.e8_execution_gate import DeterministicFakeExternalValidationProvider, DisabledExternalValidationProvider, run_e8_execution_gate
from office.mission_command.e8_external_action_preflight import E8ExternalValidationAction, E8PreflightResult
from office.mission_command.e8_risk_controlled_action_model import ActionType, RiskTier


ROOT = Path(__file__).resolve().parents[2]


def _action():
    return E8ExternalValidationAction("a1", ActionType.SEND_VALIDATION_MESSAGE, RiskTier.TIER_2_TRANSPARENT_LOW_RISK_EXTERNAL_VALIDATION, "t1", "email", "d1", "h1", "m1", True, "I’m Aiden, an AI-assisted CEO/runtime agent.", ["opt-out"], "owner_operated_handoff")


def _preflight(allowed=True):
    return E8PreflightResult("a1", allowed, False, not allowed, RiskTier.TIER_2_TRANSPARENT_LOW_RISK_EXTERNAL_VALIDATION, "valid", "valid", "valid", "valid", "valid", "allowed" if allowed else "blocked", "" if allowed else "no")


def test_execution_gate_does_not_send_without_provider():
    result = run_e8_execution_gate(_action(), _preflight(True), ROOT, DisabledExternalValidationProvider(), "aiden_executes_if_provider_available")
    assert result.executed is False
    assert result.external_action_executed is False


def test_execution_gate_does_not_send_when_owner_operated_handoff():
    result = run_e8_execution_gate(_action(), _preflight(True), ROOT, DisabledExternalValidationProvider(), "owner_operated_handoff")
    assert result.executed is False
    assert result.owner_operated_handoff_ready is True


def test_execution_gate_writes_handoff_packet_when_owner_operated():
    result = run_e8_execution_gate(_action(), _preflight(True), ROOT, DisabledExternalValidationProvider(), "owner_operated_handoff")
    assert result.handoff_packet_path
    assert Path(result.handoff_packet_path).exists()


def test_execution_gate_requires_action_ledger_if_executed():
    result = run_e8_execution_gate(_action(), _preflight(True), ROOT, DeterministicFakeExternalValidationProvider(), "aiden_executes_if_provider_available")
    assert result.executed is True
    assert result.action_ledger_path
    assert Path(result.action_ledger_path).exists()
