import json
from pathlib import Path


def test_e61_json_artifacts_parse_cleanly():
    root = Path(__file__).resolve().parents[2]
    paths = sorted((root / "operations/external_validation").glob("e61_*.json")) + sorted((root / "operations/knowledge_graph").glob("e61_*.json"))
    assert paths
    for path in paths:
        json.loads(path.read_text(encoding="utf-8"))
