from office.mission_command.e41_recent_line_runtime_connection_audit import build_recent_line_runtime_connection_audit


def test_e41_recent_line_runtime_connection_audit_contract():
    artifact = build_recent_line_runtime_connection_audit()
    milestones = {item["milestone"] for item in artifact["milestones"]}
    assert {"E31", "E38", "E40"}.issubset(milestones)
    e40 = next(item for item in artifact["milestones"] if item["milestone"] == "E40")
    assert any("route drift" in risk for risk in e40["conflict_risks"])
    assert artifact["summary"]["needs_reconciliation"] is True

