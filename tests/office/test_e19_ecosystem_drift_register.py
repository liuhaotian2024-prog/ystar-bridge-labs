import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]


def test_drift_register_captures_provider_feedback_and_cieu_blockers():
    data = json.loads((ROOT / "operations/external_validation/e19_ecosystem_drift_register.json").read_text())
    ids = {item["blocker_id"] for item in data["blockers"]}
    assert "real_provider_send_blocked" in ids
    assert "missing_feedback_evidence" in ids
    assert "canonical_cieu_writeback_blocked" in ids
    assert data["repo_modification_required_now"] is False
    assert data["external_action_executed"] is False
