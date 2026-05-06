from office.mission_command.e53_y_star_gov_validation_runner import run_e53_y_star_gov_validation

def test_y_star_gov_validation_passes_pending_owner_manifest():
    data = run_e53_y_star_gov_validation()
    assert data["passed"] is True
    assert data["approval_pending_validation"]["status"] == "pending_owner_decision"
