import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]


def test_e70_json_artifacts_are_parseable():
    paths = list((ROOT / "operations/external_validation").glob("e70_*.json"))
    assert len(paths) >= 20
    for path in paths:
        json.loads(path.read_text())
