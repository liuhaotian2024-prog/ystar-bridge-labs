from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]


def test_method_learning_mentions_risk_controlled_external_freedom():
    text = (ROOT / "knowledge" / "ceo" / "wisdom" / "AIDEN_META_DEVELOPMENT_METHOD_KERNEL.md").read_text(encoding="utf-8")
    assert "External freedom should be risk-controlled" in text
    assert "transparent AI identity" in text
    assert "action ledgers" in text
