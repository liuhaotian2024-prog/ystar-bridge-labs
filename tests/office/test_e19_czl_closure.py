import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]


def test_czl_closure_records_ecosystem_alignment_and_no_external_action():
    data = json.loads((ROOT / "operations/external_validation/e19_czl_closure.json").read_text())
    assert data["Rt_plus_1"] == 0
    assert set(data["repos_checked"]) == {"ystar-bridge-labs", "gov-mcp", "Y-star-gov", "ystar-company"}
    assert data["no_real_external_action_occurred"] is True
    assert data["no_fake_target_evidence_created"] is True
    assert data["no_fake_feedback_created"] is True
    assert data["no_provider_api_called"] is True
    assert data["no_send_receipt_generated"] is True


def test_e19_reports_exist():
    for rel in [
        "reports/integration/e19_ecosystem_alignment_scan.md",
        "reports/integration/e19_cross_repo_impact_matrix.md",
        "reports/integration/e19_revenue_validation_control_room.md",
        "reports/integration/e19_feedback_import_control_path.md",
        "reports/integration/e19_ecosystem_drift_register.md",
        "reports/integration/e19_repo_modification_decision_packet.md",
        "reports/integration/e19_commercial_route_decision_packet.md",
        "reports/integration/e19_future_milestone_alignment_gate.md",
        "reports/integration/e19_czl_closure.md",
    ]:
        assert (ROOT / rel).exists()
