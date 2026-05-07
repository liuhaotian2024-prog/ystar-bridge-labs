import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]


def test_e69_scoring_matrix_selects_cieu_module_by_model_axes():
    data = json.loads((ROOT / "operations/external_validation/e69_ceo_next_action_scoring_matrix.json").read_text())
    assert data["scoring_uses_installed_capabilities"] is True
    assert data["top_candidate"] == "integrate_CIEU_audit_log_module_into_governed_business_operations_blueprint_no_execution"
    assert "CIEU_strategic_value" in data["scoring_axes"]
    assert data["rows"][0]["total_score"] >= data["rows"][1]["total_score"]

