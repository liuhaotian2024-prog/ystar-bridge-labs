import json
from pathlib import Path
ROOT = Path(__file__).resolve().parents[2]
def test_conflict_map_documents_receipt_and_validator_boundaries():
    d = json.loads((ROOT / "operations/external_validation/e27_live_test_duplicate_conflict_map.json").read_text())
    assert d["cluster_count"] >= 10
    assert d["destructive_refactor_performed"] is False
    names = {row["capability"] for row in d["clusters"]}
    assert {"receipt generation", "live readiness validator", "canary planning"} <= names
