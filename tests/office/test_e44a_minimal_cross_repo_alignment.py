import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]

def test_minimal_cross_repo_alignment_boundaries():
    artifact = json.loads((ROOT / "operations/external_validation/e44a_minimal_cross_repo_alignment.json").read_text())
    assert artifact["Y_star_gov_remains_governance_kernel"] is True
    assert artifact["gov_mcp_remains_execution_boundary"] is True
    assert artifact["Bridge_Labs_owns_ceo_cognition_runtime"] is True
    assert artifact["no_duplicate_governance_kernel_created"] is True
    assert artifact["no_duplicate_MCP_execution_layer_created"] is True
