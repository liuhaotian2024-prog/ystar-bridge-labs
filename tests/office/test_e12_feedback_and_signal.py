import json
from pathlib import Path

from office.mission_command.e12_feedback_capture import load_e12_feedback_capture, validate_e12_feedback_event
from office.mission_command.e12_signal_evaluator import evaluate_e12_validation_signal


def _event(response_type="asks_price"):
    return {
        "feedback_id": "fb_1",
        "target_id": "cand_alicelabs_alicelabs",
        "received_at": "2026-05-02T00:00:00Z",
        "source_channel": "owner_operated_handoff",
        "response_type": response_type,
        "verbatim_or_summary": "Asked whether there is a price and described a workflow.",
        "price_signal": "asked_price",
        "workflow_signal": "has_workflow",
        "urgency_signal": "",
        "trust_gap_signal": "",
        "next_step_requested": "send_example",
        "owner_entered": True,
        "external_action_reference": "owner_operated_handoff",
    }


def test_no_fake_feedback_accepted():
    fake = _event()
    fake["owner_entered"] = False
    fake["external_action_reference"] = ""
    assert "feedback_must_be_owner_entered_or_reference_action_ledger" in validate_e12_feedback_event(fake, action_ledger_exists=False)


def test_no_response_requires_action_ledger_or_owner_entered_event():
    no_response = _event("no_response")
    no_response["owner_entered"] = False
    no_response["external_action_reference"] = ""
    errors = validate_e12_feedback_event(no_response, action_ledger_exists=False)
    assert "no_response_requires_action_ledger_or_owner_entered_event" in errors


def test_owner_entered_feedback_path_works(tmp_path: Path):
    path = tmp_path / "operations/external_validation/e12_feedback_events.json"
    path.parent.mkdir(parents=True)
    path.write_text(json.dumps({"events": [_event()]}, indent=2), encoding="utf-8")
    capture = load_e12_feedback_capture(tmp_path)
    evaluation = evaluate_e12_validation_signal(capture)
    assert capture.feedback_valid is True
    assert evaluation.classification == "strong_positive"


def test_negative_feedback_recommends_negative_signal(tmp_path: Path):
    path = tmp_path / "operations/external_validation/e12_feedback_events.json"
    path.parent.mkdir(parents=True)
    path.write_text(json.dumps({"events": [_event("says_tools_solve_it")]}, indent=2), encoding="utf-8")
    capture = load_e12_feedback_capture(tmp_path)
    assert evaluate_e12_validation_signal(capture).classification == "negative"

