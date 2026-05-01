from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]


def test_method_learning_mentions_market_backed_not_validation_ready():
    text = (ROOT / "knowledge" / "ceo" / "wisdom" / "AIDEN_META_DEVELOPMENT_METHOD_KERNEL.md").read_text(encoding="utf-8")
    assert "Market-backed does not equal validation-ready" in text
    assert "calibrate evidence quality" in text
    assert "approval-gated validation protocols" in text
