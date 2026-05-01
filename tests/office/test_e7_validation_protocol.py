from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]


def _protocol() -> str:
    return (ROOT / "reports" / "integration" / "e7_validation_protocol.md").read_text(encoding="utf-8")


def test_validation_protocol_has_allowed_modes():
    text = _protocol()
    assert "Allowed Validation Modes" in text
    assert "owner-approved direct outreach" in text
    assert "owner-approved public post" in text


def test_validation_protocol_has_forbidden_modes():
    text = _protocol()
    assert "Forbidden Validation Modes" in text
    assert "automated bulk outreach" in text
    assert "payment collection" in text
    assert "account creation" in text


def test_validation_protocol_has_success_and_disconfirming_signals():
    text = _protocol()
    assert "Success Criteria" in text
    assert "buyer asks for price" in text
    assert "Disconfirming Signals" in text
    assert "buyer sees it as generic consulting" in text


def test_validation_protocol_has_stop_conditions():
    text = _protocol()
    assert "Stop Conditions" in text
    assert "any external action not explicitly approved" in text
