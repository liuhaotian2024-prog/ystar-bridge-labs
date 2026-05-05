import json
from pathlib import Path
ROOT = Path(__file__).resolve().parents[2]

def test_base_reconciliation_accepts_current_remote_confirmed_head():
    data = json.loads((ROOT / "operations/external_validation/e32_base_reconciliation.json").read_text())
    assert data["previous_requested_base_head"] == "4ccf3ec7d60ec0f96183b42fb2dbc0888d36d95a"
    assert data["actual_current_local_head"] == "31f0a7125a10bf058dbc0b356f4425e0a6aaa361"
    assert data["actual_current_remote_head"] == data["actual_current_local_head"]
    assert data["ancestor_check"]["previous_base_is_ancestor_of_current_head"] is True
    assert data["risk_classification"] == "safe_to_continue_from_current_head"
    assert data["rollback_reset_rewrite_performed"] is False
    assert data["files_modified_before_reconciliation"] is False
