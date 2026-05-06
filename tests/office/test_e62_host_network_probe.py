import json
from pathlib import Path

from office.mission_command.e62_host_network_probe import run_host_network_probe
from office.mission_command.e62_revenue_runtime_core import write_all_e62_artifacts


def test_e62_host_network_probe_regenerates_truthful_environment_result():
    root = Path(__file__).resolve().parents[2]
    gate = write_all_e62_artifacts(root)
    data = run_host_network_probe(root)
    blocker = data["blocker_classification"]
    assert gate["gate_passed"] is True
    assert blocker["blocker_status"] in {
        "host_public_read_available",
        "host_dns_unavailable",
        "sandbox_dns_unavailable_but_host_bridge_unknown",
        "unknown_network_blocker",
    }
    assert blocker["fixture_or_blocker_not_live_market_freshness"] is True
    assert data["delivery_bridge_probe_result"]["live_receipt_count"] >= 0
    assert json.loads((root / "operations/external_validation/e62_completion_gate_result.json").read_text())["gate_passed"] is True
