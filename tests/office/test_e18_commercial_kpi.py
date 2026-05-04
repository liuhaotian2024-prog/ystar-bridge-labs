import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]


def test_commercial_kpi_packet_uses_placeholders_not_fake_data():
    data = json.loads((ROOT / "operations/external_validation/e18_commercial_kpi_packet.json").read_text())
    assert data["target_count"] >= 5
    assert data["ready_target_count"] >= 3
    assert data["approved_count_placeholder"] == 0
    assert data["sent_count_placeholder"] == 0
    assert data["response_count_placeholder"] == 0
    assert data["paid_signal_count_placeholder"] == 0
    assert data["no_fake_data_policy"].startswith("All sent/response/paid-signal counts remain placeholders")
    assert data["external_action_executed"] is False
