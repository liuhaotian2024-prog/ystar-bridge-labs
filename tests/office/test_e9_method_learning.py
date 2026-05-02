from pathlib import Path


def test_method_kernel_mentions_external_pattern_mining():
    root = Path(__file__).resolve().parents[2]
    text = (root / "knowledge" / "ceo" / "wisdom" / "AIDEN_META_DEVELOPMENT_METHOD_KERNEL.md").read_text(encoding="utf-8")
    assert "External Pattern Mining and Technology Transfer" in text
    assert "translate the strongest ideas into Y*Bridge runtime modules" in text
