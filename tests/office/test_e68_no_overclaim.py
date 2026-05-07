import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]


def test_e68_no_overclaim_validation_passes():
    data = json.loads((ROOT / "operations/external_validation/e68_no_overclaim_validation_result.json").read_text())
    assert data["passed"] is True
    assert data["violations"] == []

