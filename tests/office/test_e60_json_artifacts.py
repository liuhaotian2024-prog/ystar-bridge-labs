import json
from pathlib import Path


def test_e60_json_artifacts_parse_cleanly():
    root = Path(__file__).resolve().parents[2]
    paths = sorted((root / "operations/external_validation").glob("e60_*.json")) + sorted((root / "operations/knowledge_graph").glob("e60_*.json"))
    assert paths, "E60 JSON artifacts should exist"
    for path in paths:
        json.loads(path.read_text(encoding="utf-8"))
