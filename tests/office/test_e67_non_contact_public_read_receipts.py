import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]


def test_e67_receipts_exist_or_classify_public_read_blocker_truthfully():
    data = json.loads((ROOT / "operations/external_validation/e67_non_contact_public_read_receipts.json").read_text())
    assert data["receipt_count"] >= 24
    assert data["public_read_blocker_classification"]
    for receipt in data["receipts"]:
        assert receipt["no_contact_info_extracted"] is True
        assert receipt["no_login"] is True
        assert receipt["no_form_submission"] is True
        assert receipt["no_human_identification"] is True
        assert receipt["not_customer_validation"] is True
        assert receipt["not_paid_signal"] is True
        assert receipt["not_pricing_validation"] is True

