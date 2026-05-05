from office.mission_command.e38_public_source_collector import build_public_source_collection_run
from office.mission_command.e35_one_brain_integration_guard import get_artifact


def test_public_source_collection_executed_with_real_receipts():
    run = build_public_source_collection_run()
    receipts = get_artifact("e38_public_evidence_receipts")
    assert run["execution_status"] == "executed_public_read_only"
    assert run["source_count"] >= 20
    assert run["minimum_target_met"] is True
    assert receipts["receipt_count"] == run["source_count"]
    for receipt in receipts["receipts"]:
        assert receipt["source_url"].startswith("https://")
        assert receipt["public_observation_only"] is True
        assert receipt["not_customer_validation"] is True
        assert receipt["not_paid_signal"] is True
        assert receipt["no_login"] is True
        assert receipt["no_form"] is True
        assert receipt["no_contact"] is True
