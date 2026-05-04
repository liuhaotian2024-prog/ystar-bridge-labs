import json
from pathlib import Path
ROOT = Path(__file__).resolve().parents[2]
def test_ecosystem_alignment_is_bridge_labs_only_with_followups():
    data = json.loads((ROOT / "operations/external_validation/e29_ecosystem_alignment_gate.json").read_text())
    assert data["repos_checked_count"] == 4
    assert data["bridge_labs_modified"] is True
    assert data["gov_mcp_modified"] is False
    assert data["ecosystem_alignment_status"] == "ecosystem_aligned_with_documented_followups"
