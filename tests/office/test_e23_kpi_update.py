import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]

def load(rel):
    return json.loads((ROOT / rel).read_text())


def test_kpi_update_has_no_live_or_real_response_metrics():
    data=load("operations/external_validation/e23_kpi_update.json")
    assert data["total_candidates"] == 7
    assert data["previous_dry_run_executed"] == 5
    assert data["newly_dry_run_eligible"] == 0
    assert data["still_evidence_required"] == 1
    assert data["suppressed"] == 1
    assert data["live_ready"] == 0
    assert data["live_send_count"] == 0
    assert data["real_response_count"] == 0
    assert data["paid_signal_count"] == 0
