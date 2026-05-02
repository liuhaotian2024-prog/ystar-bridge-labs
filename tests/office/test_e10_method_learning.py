from pathlib import Path


def test_method_kernel_mentions_autonomous_buyer_discovery():
    root = Path(__file__).resolve().parents[2]
    text = (root / "knowledge" / "ceo" / "wisdom" / "AIDEN_META_DEVELOPMENT_METHOD_KERNEL.md").read_text(encoding="utf-8")
    assert "Autonomous Buyer Discovery and Shortest Revenue Path" in text
    assert "rank segments by shortest path to a paid signal" in text
