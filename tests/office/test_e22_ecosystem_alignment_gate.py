import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]

def load(rel):
    return json.loads((ROOT / rel).read_text())


def test_e22_ecosystem_alignment_gate_is_cross_repo_and_no_gov_mcp_mutation():
    data = load("operations/external_validation/e22_ecosystem_alignment_gate.json")
    assert data["closure_status"] == "ecosystem_aligned_no_cross_repo_changes_needed"
    assert data["gov_mcp_read_only"] is True
    assert data["gov_mcp_modified"] is False
    assert len(data["repos_checked"]) == 4
    assert data["external_action_executed"] is False
