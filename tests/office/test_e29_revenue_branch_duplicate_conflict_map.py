import json
from pathlib import Path
ROOT = Path(__file__).resolve().parents[2]
def test_duplicate_conflict_map_routes_without_deleting_legacy_wheels():
    data = json.loads((ROOT / "operations/external_validation/e29_revenue_branch_duplicate_conflict_map.json").read_text())
    assert data["duplicate_conflict_cluster_count"] == 10
    assert data["destructive_refactor_performed"] is False
    assert any(c["recommended_route"] == "keep_parallel_with_router" for c in data["clusters"])
