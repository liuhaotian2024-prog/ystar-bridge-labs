import json
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]
def test_e26_ecosystem_alignment_tracks_gov_mcp_delivery():
    d=json.loads((ROOT/"operations/external_validation/e26_ecosystem_alignment_gate.json").read_text())
    assert set(d["repos_checked"])=={"ystar-bridge-labs","gov-mcp","Y-star-gov","ystar-company"}
    assert d["gov_mcp_modified"] is True
    assert d["gov_mcp_delivered"] is True
    assert d["Y_star_gov_immediate_mutation_needed"] is False
    assert d["closure_status"]=="ecosystem_aligned_with_documented_followups"
