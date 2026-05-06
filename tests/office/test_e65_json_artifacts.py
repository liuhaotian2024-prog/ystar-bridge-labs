import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]


def test_e65_json_and_jsonl_artifacts_parse_cleanly():
    paths = list((ROOT / "operations/external_validation").glob("e65_*.json"))
    paths += list((ROOT / "operations/knowledge_graph").glob("e65_*.json"))
    assert paths
    for path in paths:
        json.loads(path.read_text())
    for path in (ROOT / "operations/knowledge_graph").glob("e65_*.jsonl"):
        for line in path.read_text().splitlines():
            assert json.loads(line)
