from pathlib import Path

from office.mission_command.e8_feedback_capture import E8FeedbackEvent, load_e8_feedback_events, validate_feedback_event


ROOT = Path(__file__).resolve().parents[2]


def test_feedback_capture_does_not_invent_feedback():
    assert load_e8_feedback_events(ROOT) == []
    text = (ROOT / "reports" / "integration" / "e8_feedback_capture_report.md").read_text(encoding="utf-8")
    assert "feedback_captured: False" in text


def test_feedback_capture_respects_opt_out():
    event = E8FeedbackEvent("f1", "t1", "2026-05-01T00:00:00Z", "email", "opt_out", "stop", "", "", "", "", "follow up", True, "a1")
    assert "opt_out_must_not_have_next_step" in validate_feedback_event(event)
