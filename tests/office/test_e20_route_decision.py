import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]


def test_route_decision_recommends_e21_provider_plan():
    data = json.loads((ROOT / "operations/external_validation/e20_route_decision_packet.json").read_text())
    assert data["recommended_route"] == "prepare_E21_autonomous_provider_adapter_plan"
    assert "resolve_gov_mcp_provider_gap" in data["route_options"]
    assert data["summary_counts"]["provider_capability_missing"] >= 1
    assert data["real_external_action_executed"] is False
