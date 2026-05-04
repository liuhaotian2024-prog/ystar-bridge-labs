import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]


def test_e17_czl_closure_records_no_external_action_and_rt1_zero():
    data = json.loads((ROOT / "operations/external_validation/e17_czl_closure.json").read_text())
    assert data["Rt_plus_1"] == 0
    assert data["no_real_external_action_occurred"] is True
    assert data["no_fake_response_evidence_created"] is True
    assert data["no_provider_api_called"] is True
    assert data["no_send_receipt_generated"] is True
    assert data["feedback_runtime_ready"] is True


def test_e17_reports_exist():
    for rel in [
        "reports/integration/e17_first_commercial_signal_closed_loop.md",
        "reports/integration/e17_final_message_package.md",
        "reports/integration/e17_feedback_runtime.md",
        "reports/integration/e17_paid_signal_and_offer_revision.md",
        "reports/integration/e17_route_decision_packet.md",
        "reports/integration/e17_czl_closure.md",
    ]:
        assert (ROOT / rel).exists()
