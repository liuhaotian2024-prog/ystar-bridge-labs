import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]


def test_czl_closure_records_no_external_action_and_direction_change():
    data = json.loads((ROOT / "operations/external_validation/e20_czl_closure.json").read_text())
    assert data["Rt_plus_1"] == 0
    assert data["owner_manual_send_no_longer_default"] is True
    assert data["low_risk_autonomous_execution_path_defined"] is True
    assert data["high_risk_human_intervention_boundary_defined"] is True
    assert data["no_real_external_action_occurred"] is True
    assert data["no_customer_contact_occurred"] is True
    assert data["no_provider_api_called"] is True


def test_e20_reports_exist():
    for rel in [
        "reports/integration/e20_risk_tiered_autonomous_outbound_control_plane.md",
        "reports/integration/e20_human_intervention_boundary.md",
        "reports/integration/e20_batch_autonomous_reclassification.md",
        "reports/integration/e20_provider_capability_detection.md",
        "reports/integration/e20_ecosystem_alignment_gate.md",
        "reports/integration/e20_route_decision_packet.md",
        "reports/integration/e20_future_outbound_policy.md",
        "reports/integration/e20_czl_closure.md",
    ]:
        assert (ROOT / rel).exists()
