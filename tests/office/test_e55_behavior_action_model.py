from office.mission_command.e55_behavior_action_model import build_action_model_contract, build_broken_action_fixtures, validate_action_proposal

def test_action_model_valid_and_brain_cannot_execute_directly():
    data = build_action_model_contract()
    assert data["validation"]["seed_valid"] is True
    fixture = next(f for f in build_broken_action_fixtures() if f["action_id"] == "fixture_ceo_brain_direct_execution")
    assert "ceo_brain_direct_execution_not_allowed" in validate_action_proposal(fixture)["failures"]
    assert data["external_action_allowed"] is False
