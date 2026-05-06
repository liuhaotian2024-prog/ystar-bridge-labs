import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]


def test_e64_json_artifacts_parse_cleanly():
    paths = list((ROOT / "operations/external_validation").glob("e64_*.json"))
    paths += list((ROOT / "operations/knowledge_graph").glob("e64_*.json"))
    paths += list((ROOT / "products/ai_agent_company_runtime_harness_deployment_blueprint").glob("*.json"))
    assert paths
    for path in paths:
        json.loads(path.read_text())


def test_e64_jsonl_artifacts_parse_cleanly():
    paths = list((ROOT / "operations/knowledge_graph").glob("e64_*.jsonl"))
    assert paths
    for path in paths:
        for line in path.read_text().splitlines():
            assert json.loads(line)
