import json
from pathlib import Path


def test_e58_json_artifacts_parse_cleanly():
    root = Path(__file__).resolve().parents[2]
    paths = list((root / "operations/external_validation").glob("e58_*.json"))
    paths += list((root / "products/ai_agent_company_runtime_harness_case_study").glob("*.json"))
    assert paths
    for path in paths:
        json.loads(path.read_text(encoding="utf-8"))

