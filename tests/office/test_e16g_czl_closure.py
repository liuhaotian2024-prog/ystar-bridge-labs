from __future__ import annotations

from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]


def test_e16g_czl_records_no_real_external_action() -> None:
    text = (ROOT / "reports/integration/e16g_czl_closure.md").read_text()
    assert "Rt+1: 0" in text
    assert "real_external_action_executed=false" in text
    assert "no customer contact" in text
    assert "real provider API call" in text


def test_e16g_reports_exist() -> None:
    for rel in [
        "reports/integration/e16g_gov_mcp_adapter_promotion_result.md",
        "reports/integration/e16g_bridge_labs_router_alignment.md",
        "reports/integration/e16g_risk_capability_execution_mapping.md",
        "reports/integration/e16g_e16_route_update_packet.md",
    ]:
        assert (ROOT / rel).exists()
