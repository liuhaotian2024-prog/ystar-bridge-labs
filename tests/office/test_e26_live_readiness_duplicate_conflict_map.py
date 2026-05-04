import json
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]
def test_e26_duplicate_conflict_map_routes_without_refactor():
    d=json.loads((ROOT/"operations/external_validation/e26_live_readiness_duplicate_conflict_map.json").read_text())
    assert d["cluster_count"]>=8
    assert d["destructive_refactor_performed"] is False
    assert any(c["capability"]=="receipt generation" for c in d["clusters"])
