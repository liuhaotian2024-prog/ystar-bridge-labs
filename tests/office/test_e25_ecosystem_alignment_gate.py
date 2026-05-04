import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]

def test_e25_ecosystem_alignment_gate_records_cross_repo_delivery():
    data = json.loads((ROOT / "operations/external_validation/e25_ecosystem_alignment_gate.json").read_text())
    assert set(data["repos_checked"]) == {"ystar-bridge-labs", "gov-mcp", "Y-star-gov", "ystar-company"}
    assert data["gov_mcp_modified"] is True
    assert data["gov_mcp_delivered"] is True
    assert data["Y_star_gov_immediate_mutation_needed"] is False
    assert data["closure_status"] == "ecosystem_aligned_with_documented_followups"
