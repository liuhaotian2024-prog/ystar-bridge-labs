import json
from pathlib import Path
ROOT = Path(__file__).resolve().parents[2]

def test_full_ecosystem_archaeology_reuses_existing_wheels_first():
    data = json.loads((ROOT / "operations/external_validation/e32_full_ecosystem_runtime_archaeology.json").read_text())
    assert data["repos_scanned_count"] == 4
    assert data["capability_clusters_found"] >= 9
    assert data["reused_wheels_count"] >= 10
    assert data["newly_required_wheels_count"] == 6
    assert "safe public page reader" in data["do_not_rebuild"]
    assert data["gov_mcp_modified"] is False
