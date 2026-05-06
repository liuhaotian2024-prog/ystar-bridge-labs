from office.mission_command.e63_offer_package_hypothesis import run_offer_package_hypothesis


def test_e63_offer_package_is_draft_only_internal():
    data = run_offer_package_hypothesis()
    assert data["offer_status"] == "draft_only_internal"
    assert data["required_owner_approval_before_external_use"] is True
    assert data["risk_tier"] == "T2_draft_only_external_material"
    assert "not customer validated" in data["no_overclaim_language"]
    assert data["external_action_allowed"] is False
