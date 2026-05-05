import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]

def test_cross_repo_alignment_records_ownership_and_no_duplicates():
    artifact = json.loads((ROOT / "operations/external_validation/e45_cross_repo_alignment.json").read_text())
    assert artifact["Bridge_Labs_owns_CEO_runtime_and_demo_bundle"] is True
    assert artifact["gov_mcp_owns_execution_boundary_and_first_5_minute_docs"] is True
    assert artifact["Y_star_gov_owns_governance_kernel_and_demo_doctor"] is True
    assert artifact["no_duplicate_governance_kernel"] is True
    assert artifact["gov_mcp_modified_and_pushed"] is True
