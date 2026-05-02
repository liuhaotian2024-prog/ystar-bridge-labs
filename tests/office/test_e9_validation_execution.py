from pathlib import Path

from office.mission_command.e9_action_plan import build_e9_validation_action_plan
from office.mission_command.e9_draft_binding import E9DraftBinding
from office.mission_command.e9_external_action_preflight import E9PreflightResult
from office.mission_command.e9_validation_execution import E9DeterministicFakeProvider, E9ExternalValidationProvider, run_e9_validation_execution


def _plan():
    return build_e9_validation_action_plan(None, [], [E9DraftBinding("d1", "h1", "path", "email", True, True, False, [])])


def _preflight(allowed=True):
    return E9PreflightResult(allowed, not allowed, not allowed, "TIER_2", "valid", "valid", "valid", "valid", "clear", "valid", "" if allowed else "blocked")


def test_e9_execution_does_not_send_with_disabled_provider(tmp_path: Path):
    result = run_e9_validation_execution(tmp_path, _plan(), _preflight(True), E9ExternalValidationProvider(), "aiden_executes_if_provider_available")
    assert result.executed is False
    assert result.external_action_executed is False


def test_e9_execution_requires_action_ledger_if_sent(tmp_path: Path):
    result = run_e9_validation_execution(tmp_path, _plan(), _preflight(True), E9DeterministicFakeProvider(), "aiden_executes_if_provider_available")
    assert result.executed is True
    assert result.action_ledger_path
    assert Path(result.action_ledger_path).exists()


def test_e9_owner_operated_handoff_does_not_claim_aiden_sent(tmp_path: Path):
    result = run_e9_validation_execution(tmp_path, _plan(), _preflight(True), E9ExternalValidationProvider(), "owner_operated_handoff")
    assert result.owner_operated_handoff_ready is True
    assert result.external_action_executed is False
