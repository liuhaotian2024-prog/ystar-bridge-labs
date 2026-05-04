import json
from pathlib import Path
ROOT = Path(__file__).resolve().parents[2]
def test_ecosystem_alignment_checks_four_repos_and_gov_delivery():
    d = json.loads((ROOT / "operations/external_validation/e27_ecosystem_alignment_gate.json").read_text())
    assert d["repos_checked_count"] == 4
    assert d["gov_mcp_modified"] is True
    assert d["gov_mcp_delivered"] is True
    assert d["Y_star_gov_immediate_mutation_needed"] is False
    assert d["ecosystem_alignment_status"] == "ecosystem_aligned_with_documented_followups"
