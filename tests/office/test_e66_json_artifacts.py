import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]


def test_e66_json_artifacts_parse_cleanly():
    paths = list((ROOT / "operations/external_validation").glob("e66_*.json"))
    paths += list((ROOT / "operations/knowledge_graph").glob("e66_*.json"))
    paths += list((ROOT / "products/governed_business_operations_blueprint_for_agent_teams").glob("*.json"))
    assert paths
    for path in paths:
        json.loads(path.read_text())
