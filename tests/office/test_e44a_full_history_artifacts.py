import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]

def test_full_history_artifacts_have_counts_and_quarantine():
    counts = json.loads((ROOT / "operations/external_validation/e44a_full_history_breakage_counts.json").read_text())
    assert counts["total_capability_looking_python_modules"] > 100
    assert counts["pure_get_artifact_accessors"] > 50
    assert counts["misleading_runtime_name_modules"] > 0
    assert counts["commercial_sales_first_user_revenue_assets_not_connected_to_task_loop"] > 0
    quarantine = json.loads((ROOT / "operations/external_validation/e44a_expert_route_quarantine_register.json").read_text())
    assert quarantine["default_status_for_E40_expert_artifacts"] == "historical_no_send_or_parked"
    assert quarantine["expert_contact_route_allowed_by_default"] is False
