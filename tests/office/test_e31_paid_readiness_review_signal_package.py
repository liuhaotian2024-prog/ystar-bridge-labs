import json
from pathlib import Path
ROOT = Path(__file__).resolve().parents[2]
def test_paid_readiness_signal_package_is_ready_but_no_send():
    data = json.loads((ROOT / "operations/external_validation/e31_paid_readiness_review_signal_package.json").read_text())
    assert data["package_created"] is True
    assert data["one_page_offer_ready"] is True
    assert data["diagnostic_outline_ready"] is True
    assert data["price_commitment_hypothesis_ready"] is True
    assert data["no_send_validation_status"]["sent"] is False
    assert data["no_send_validation_status"]["production_live_receipt_count"] == 0
