import json
from pathlib import Path

from office.mission_command.e17_feedback_intake import validate_feedback_intake_event

ROOT = Path(__file__).resolve().parents[2]


def test_feedback_schema_supports_required_feedback_types():
    schema = json.loads((ROOT / "operations/external_validation/e17_feedback_intake_schema.json").read_text())
    for value in ["no_response_yet", "positive_interest", "pricing_question", "meeting_request", "referral", "unsubscribe_or_do_not_contact", "bounced_or_invalid_target"]:
        assert value in schema["feedback_type_enum"]
    assert schema["external_action_executed_by_agent"] is False


def test_empty_feedback_intake_claims_no_real_response():
    event = json.loads((ROOT / "operations/external_validation/e17_feedback_intake_empty.json").read_text())
    assert event["feedback_type"] == "no_response_yet"
    assert event["response_evidence_present"] is False
    assert event["real_customer_response_claimed"] is False
    assert validate_feedback_intake_event(event) == []
