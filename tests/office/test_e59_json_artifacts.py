import json
from pathlib import Path


def test_e59_json_artifacts_parse_cleanly():
    root = Path(__file__).resolve().parents[2]
    paths = list((root / "operations/external_validation").glob("e59_*.json"))
    paths += list((root / "operations/knowledge_graph").glob("e59_*.json"))
    assert paths
    for path in paths:
        json.loads(path.read_text(encoding="utf-8"))

