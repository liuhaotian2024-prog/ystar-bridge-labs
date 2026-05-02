import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
REPORTS = ROOT / "reports" / "integration"


def test_fingerprint_index_contains_multiple_artifact_types():
    payload = json.loads((REPORTS / "e11_capability_fingerprint_index.json").read_text(encoding="utf-8"))
    artifact_types = {item["artifact_type"] for item in payload["fingerprints"]}
    assert payload["fingerprint_count"] > 100
    assert {"function", "report_section", "operation_template", "test_assertion"} <= artifact_types
    assert {"brain_schema", "dream_cycle", "cieu_schema", "gateway_tool"} & artifact_types

