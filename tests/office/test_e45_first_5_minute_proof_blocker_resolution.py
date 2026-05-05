import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]

def test_first_5_minute_blocker_resolution_records_gov_mcp_fix():
    artifact = json.loads((ROOT / "operations/external_validation/e45_first_5_minute_proof_blocker_resolution.json").read_text())
    assert artifact["blocker_status"] == "fixed_in_gov_mcp"
    assert artifact["gov_mcp_result_head"]
    assert artifact["patch_required"] is False
    assert artifact["no_external_action"] is True
