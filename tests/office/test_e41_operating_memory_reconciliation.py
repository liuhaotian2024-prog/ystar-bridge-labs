from office.mission_command.e41_operating_memory_reconciliation import build_operating_memory_reconciliation


def test_e41_operating_memory_reconciliation_contract():
    artifact = build_operating_memory_reconciliation()
    surfaces = {item["memory_surface"] for item in artifact["maps_recent_artifacts_to"]}
    assert "CEO KG / brain" in surfaces
    assert "directive tracker" in surfaces
    assert artifact["no_daily_brief_written"] is True
    assert artifact["no_directive_tracker_written"] is True

