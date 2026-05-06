import json
from pathlib import Path


def test_e53_json_artifacts_are_valid():
    root = Path(__file__).resolve().parents[2]
    paths = list((root / "operations/external_validation").glob("e53*.json"))
    paths += list((root / "products/governed_agent_action_proof_packet").glob("e53*.json"))
    assert paths
    for path in paths:
        json.loads(path.read_text(encoding="utf-8"))
