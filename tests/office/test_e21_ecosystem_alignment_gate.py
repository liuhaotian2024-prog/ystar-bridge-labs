import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]


def test_e21_ecosystem_gate_records_cross_repo_delivery_and_followups():
    data = json.loads((ROOT / "operations/external_validation/e21_ecosystem_alignment_gate.json").read_text())
    assert data["closure_status"] == "ecosystem_aligned_with_documented_followups"
    assert data["gov_mcp_modified_and_delivered"] is True
    assert data["bridge_labs_modified_and_delivered"] is True
    assert data["Y_star_gov_immediate_update_needed"] is False
    assert len(data["repos_checked"]) == 4
    assert data["external_action_executed"] is False
