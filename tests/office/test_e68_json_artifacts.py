import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]


def test_e68_json_artifacts_parse_cleanly():
    paths = list((ROOT / "operations/external_validation").glob("e68_*.json"))
    paths += list((ROOT / "operations/knowledge_graph").glob("e68_*.json"))
    assert paths
    for path in paths:
        json.loads(path.read_text())
