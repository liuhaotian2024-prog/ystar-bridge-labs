from office.mission_command.e59_external_intelligence_maturity_diagnosis import run_external_intelligence_maturity_diagnosis


def test_external_intelligence_maturity_diagnosis_targets_l5_and_reuse():
    data = run_external_intelligence_maturity_diagnosis()
    assert data["target_level"] == "L5"
    assert "external_page_read_adapter_unavailable" in data["L5_blockers"]
    assert "reuse" in data["reuse_first_findings"].lower()
    assert len(data["dimensions"]) == 18

