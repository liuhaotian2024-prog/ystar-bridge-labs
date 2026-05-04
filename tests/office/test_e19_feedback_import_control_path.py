import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]


def test_feedback_import_control_path_does_not_claim_feedback_now():
    data = json.loads((ROOT / "operations/external_validation/e19_feedback_import_control_path.json").read_text())
    assert data["real_feedback_claimed_now"] is False
    assert "positive_interest" in data["followup_allowed_when"]
    assert "unsubscribe_or_do_not_contact" in data["followup_blocked_when"]
    assert data["external_action_executed"] is False
