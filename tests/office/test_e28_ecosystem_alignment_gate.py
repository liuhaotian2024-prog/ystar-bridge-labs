import json
from pathlib import Path
ROOT = Path(__file__).resolve().parents[2]
def test_alignment_checks_four_repos_without_gov_mutation():
    d = json.loads((ROOT / "operations/external_validation/e28_ecosystem_alignment_gate.json").read_text())
    assert d["repos_checked_count"] == 4
    assert d["gov_mcp_modified"] is False
    assert d["gov_mcp_delivery_required"] is False
    assert d["Y_star_gov_immediate_mutation_needed"] is False
    assert d["ecosystem_alignment_status"] == "ecosystem_aligned_with_documented_followups"
