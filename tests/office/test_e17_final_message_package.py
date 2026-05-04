import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]


def test_final_message_package_is_truthful_and_b2b_safe():
    data = json.loads((ROOT / "operations/external_validation/e17_final_message_package.json").read_text())
    text = data["email_message"].lower()
    assert "ai-assisted" in text
    assert "diagnostic-only" in text
    assert "production access" in text
    assert "paid diagnostic" in text
    assert "guaranteed" not in text
    assert "we already helped" not in text
    assert data["external_action_executed"] is False


def test_final_message_package_has_email_linkedin_subjects_and_blocked_followup():
    data = json.loads((ROOT / "operations/external_validation/e17_final_message_package.json").read_text())
    assert len(data["email_subject_options"]) >= 2
    assert data["linkedin_message"]
    assert data["softer_fallback_message"]
    assert data["one_follow_up_draft"]
    assert data["follow_up_status"].startswith("blocked_until")
