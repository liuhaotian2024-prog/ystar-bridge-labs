import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]


def test_batch_feedback_intake_schema_supports_revenue_signal_responses():
    data = json.loads((ROOT / "operations/external_validation/e18_batch_feedback_intake_schema.json").read_text())
    for item in ["positive_interest", "meeting_request", "pricing_question", "technical_clarification", "objection", "referral", "bounce", "unsubscribe_or_do_not_contact"]:
        assert item in data["feedback_type_enum"]
    assert data["external_action_executed"] is False


def test_empty_batch_feedback_intake_claims_no_feedback():
    data = json.loads((ROOT / "operations/external_validation/e18_batch_feedback_intake_empty.json").read_text())
    assert data["response_count_placeholder"] == 0
    assert data["entries"]
    for entry in data["entries"]:
        assert entry["real_customer_response_claimed"] is False
        assert entry["external_action_executed_by_agent"] is False
