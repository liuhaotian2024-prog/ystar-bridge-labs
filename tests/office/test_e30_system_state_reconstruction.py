import json
from pathlib import Path
ROOT = Path(__file__).resolve().parents[2]
def test_system_state_reconstructs_without_memory_shortcuts():
    data = json.loads((ROOT / "operations/external_validation/e30_system_state_reconstruction.json").read_text())
    assert data["current_active_branch"] == "revenue_mode_shortest_cash_path"
    assert data["execution_capabilities"]["live_test_gate_ready"] is True
    assert data["execution_capabilities"]["production_live_enabled"] is False
    assert "buyer-facing paid readiness review package" in data["underbuilt_action_heavy_areas"]
    assert "provider/live readiness gates relative to buyer-facing package clarity" in data["overbuilt_readiness_heavy_areas"]
