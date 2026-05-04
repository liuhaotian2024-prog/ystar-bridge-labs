import json
from pathlib import Path
ROOT = Path(__file__).resolve().parents[2]
def test_closure_preserves_e28_and_proves_no_external_action():
    d = json.loads((ROOT / "operations/external_validation/e28r_czl_closure.json").read_text())
    assert d["Rt_plus_1"] == 0
    assert d["e28_not_undone"] is True
    assert d["history_rewritten"] is False
    assert d["e28_artifacts_deleted"] is False
    assert d["production_live_configuration_global_default"] is False
    assert d["no_real_external_action_occurred"] is True
    assert d["no_provider_api_called"] is True
    assert d["production_live_enabled"] is False
    assert d["production_live_receipt_count"] == 0
