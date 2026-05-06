import json
from pathlib import Path


def test_e57_json_artifacts_parse_and_do_not_overclaim():
    root = Path(__file__).resolve().parents[2]
    files = list((root / "operations/external_validation").glob("e57_*.json"))
    files += list((root / "operations/knowledge_graph").glob("e57_*.json"))
    assert files
    for path in files:
        data = json.loads(path.read_text(encoding="utf-8"))
        assert data.get("external_action_allowed") is not True
        assert data.get("customer_validation_claimed") is not True
        assert data.get("paid_signal_claimed") is not True
        assert data.get("real_mcp_transport_claimed") is not True

