import json
from pathlib import Path


def test_e62_json_artifacts_parse_cleanly():
    root = Path(__file__).resolve().parents[2]
    paths = sorted((root / "operations/external_validation").glob("e62_*.json"))
    assert paths
    for path in paths:
        json.loads(path.read_text(encoding="utf-8"))
    for path in sorted((root / "operations/knowledge_graph").glob("e62_*.json")):
        json.loads(path.read_text(encoding="utf-8"))
    for path in sorted((root / "operations/knowledge_graph").glob("e62_*.jsonl")):
        for line in path.read_text(encoding="utf-8").splitlines():
            json.loads(line)
