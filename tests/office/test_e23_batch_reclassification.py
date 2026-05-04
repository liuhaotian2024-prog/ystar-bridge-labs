import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]

def load(rel):
    return json.loads((ROOT / rel).read_text())


def test_batch_reclassification_counts_live_readiness_states():
    data=load("operations/external_validation/e23_batch_reclassification.json")
    counts=data["counts"]
    assert counts["dry_run_available"] == 5
    assert counts["dry_run_executed_previously"] == 5
    assert counts["newly_promoted_to_dry_run_available"] == 0
    assert counts["still_evidence_required"] == 1
    assert counts["suppressed"] == 1
    assert counts["compliance_blocked"] == 0
    assert counts["live_ready"] == 0
    assert counts["live_blocked_provider_disabled"] == 7
