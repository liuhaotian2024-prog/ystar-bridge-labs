from office.mission_command.e58_external_intelligence_gap import build_external_intelligence_gap


def test_external_intelligence_gap_declares_e59_baseline_reuse_first():
    data = build_external_intelligence_gap()
    assert data["external_world_intelligence_L5_complete"] is False
    assert data["E59_required_before_market_contact"] is True
    baseline = " ".join(data["E59_baseline_inspection_required"])
    assert "E50B public-read-only observation artifacts" in baseline
    assert "E57 skipped evidence refresh blocker" in baseline
    assert "reuse_existing_capabilities_first" in data["E59_instruction"]

