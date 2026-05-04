import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]

def load(rel):
    return json.loads((ROOT / rel).read_text())


def test_kpi_delta_updates_only_dry_run_metrics():
    data = load("operations/external_validation/e22_kpi_dry_run_delta.json")
    assert data["dry_run_selected_count"] == 5
    assert data["dry_run_executed_count"] == 5
    assert data["guard_pass_count"] == 5
    assert data["idempotency_block_count"] == 1
    assert data["suppression_block_count"] == 1
    assert data["live_send_count"] == 0
    assert data["real_response_count"] == 0
    assert data["paid_signal_count"] == 0
