import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]


def test_e18_czl_closure_proves_no_external_action_and_runtime_ready():
    data = json.loads((ROOT / "operations/external_validation/e18_czl_closure.json").read_text())
    assert data["Rt_plus_1"] == 0
    assert data["no_real_external_action_occurred"] is True
    assert data["no_fake_target_evidence_created"] is True
    assert data["no_fake_customer_feedback_created"] is True
    assert data["no_provider_api_called"] is True
    assert data["no_send_receipt_generated"] is True
    assert data["owner_has_one_batch_decision_surface"] is True
    assert data["revenue_validation_batch_runtime_ready"] is True


def test_e18_required_reports_exist():
    for rel in [
        "reports/integration/e18_revenue_validation_batch_runtime.md",
        "reports/integration/e18_offer_variant_matrix.md",
        "reports/integration/e18_manual_send_tracker.md",
        "reports/integration/e18_batch_feedback_runtime.md",
        "reports/integration/e18_route_decision_packet.md",
        "reports/integration/e18_commercial_kpi_packet.md",
        "reports/integration/e18_czl_closure.md",
    ]:
        assert (ROOT / rel).exists()
