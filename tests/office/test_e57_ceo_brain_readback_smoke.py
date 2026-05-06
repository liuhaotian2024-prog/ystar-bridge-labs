from office.mission_command.e57_ceo_brain_readback_smoke import run_ceo_brain_money_route_readback_smoke


def test_ceo_brain_reads_selected_money_route_back():
    data = run_ceo_brain_money_route_readback_smoke()
    assert data["passes"] is True
    assert data["checks"]["ceo_brain_sees_selected_route"] is True
    assert data["checks"]["ceo_brain_sees_external_action_blocked"] is True

