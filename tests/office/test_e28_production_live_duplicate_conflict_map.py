import json
from pathlib import Path
ROOT = Path(__file__).resolve().parents[2]
def test_duplicate_map_documents_production_live_boundaries():
    d = json.loads((ROOT / "operations/external_validation/e28_production_live_duplicate_conflict_map.json").read_text())
    assert d["cluster_count"] >= 11
    assert d["destructive_refactor_performed"] is False
    names = {row["capability"] for row in d["clusters"]}
    assert {"production live config", "secret-source contract", "revenue route decision"} <= names
