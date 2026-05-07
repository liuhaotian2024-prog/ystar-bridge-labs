import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]


def _load(rel: str) -> dict:
    return json.loads((ROOT / rel).read_text())


def test_e78_source_receipts_exist_and_stay_in_owner_scope():
    receipts = _load("operations/external_validation/e78_l3_source_receipts.json")

    assert receipts["source_count"] >= 20
    assert 4 <= len(receipts["source_categories_used"]) <= 6
    for receipt in receipts["receipts"]:
        assert receipt["access_mode"] == "public_read_only"
        assert receipt["public_read_only_confirmed"] is True
        assert receipt["login_required"] is False
        assert receipt["interaction_required"] is False
        assert receipt["allowed_by_owner_scope"] is True
        assert receipt["included_in_synthesis"] is True
        assert receipt["no_contact_confirmed"] is True
        assert receipt["no_publication_confirmed"] is True
        assert receipt["no_payment_confirmed"] is True


def test_e78_excluded_source_log_exists():
    excluded = _load("operations/external_validation/e78_l3_excluded_sources_log.json")

    assert excluded["excluded_source_count"] >= 1
    assert excluded["no_contact_confirmed"] is True
    assert excluded["no_login_gated_source_used"] is True
    assert excluded["no_payment_source_used"] is True

