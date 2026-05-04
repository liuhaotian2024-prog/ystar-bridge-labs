import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]


def test_batch_owner_console_is_one_decision_surface():
    data = json.loads((ROOT / "operations/external_validation/e18_batch_owner_console.json").read_text())
    assert data["owner_console_type"] == "single_batch_decision_surface"
    assert data["candidates"]
    first = data["candidates"][0]
    assert "approve_manual_send" in first["approval_choices"]
    assert "feedback_fields_to_capture" in first
    assert "agent send" in data["blocked_actions"]
    assert data["external_action_executed"] is False


def test_batch_owner_console_markdown_exists():
    text = (ROOT / "operations/external_validation/e18_batch_owner_console.md").read_text()
    assert "E18 Batch Owner Console" in text
    assert "manual_send_readiness" in text
