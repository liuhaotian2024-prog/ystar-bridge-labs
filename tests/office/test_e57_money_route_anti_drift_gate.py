from office.mission_command.e57_money_route_anti_drift_gate import run_money_route_anti_drift_gate


def test_money_route_anti_drift_gate_has_readback_and_no_report_only_p0():
    data = run_money_route_anti_drift_gate()
    assert data["passed"] is True
    assert data["checks"]["decision_packet_has_writer_reader_readback"] is True
    assert data["checks"]["no_report_only_p0_closure"] is True

