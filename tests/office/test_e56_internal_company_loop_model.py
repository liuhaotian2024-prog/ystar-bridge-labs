from office.mission_command.e56_internal_company_loop_model import build_internal_company_cycle_model


def test_internal_company_loop_model_has_all_required_stages():
    data = build_internal_company_cycle_model()
    assert data["model_status"] == "valid"
    assert len(data["stages"]) == 12
    assert "pending_owner_decision is not approval" in data["rules"]
    assert data["no_external_action"] is True

