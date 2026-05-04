import json
from pathlib import Path

from office.mission_command.e18_batch_response_classifier import classify_entry

ROOT = Path(__file__).resolve().parents[2]


def test_batch_classifier_maps_meeting_to_paid_signal():
    result = classify_entry({"feedback_type": "meeting_request", "meeting_request_present": True})
    assert result["paid_signal_strength"] == 5
    assert result["next_action"] == "owner_schedule_meeting"
    assert result["followup_eligible_after_owner_review"] is True


def test_batch_classifier_suppresses_do_not_contact():
    result = classify_entry({"feedback_type": "unsubscribe_or_do_not_contact", "do_not_contact_requested": True})
    assert result["suppression_required"] is True
    assert result["next_action"] == "suppress_target"


def test_batch_response_classification_artifact_has_empty_summary():
    data = json.loads((ROOT / "operations/external_validation/e18_batch_response_classification_rules.json").read_text())
    assert data["classification_method"] == "deterministic_per_target_explicit_feedback_fields_no_llm_judge"
    assert data["batch_summary"]["response_count"] == 0
    assert data["batch_summary"]["batch_signal_quality"] == "no_feedback_imported_yet"
    assert data["external_action_executed"] is False
