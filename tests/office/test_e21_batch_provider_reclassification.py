import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]


def test_e21_batch_reclassification_moves_provider_missing_to_live_disabled_scaffold():
    data = json.loads((ROOT / "operations/external_validation/e21_batch_provider_reclassification.json").read_text())
    counts = data["summary_counts"]
    assert counts["dry_run_available"] == 5
    assert counts["live_scaffolded_but_disabled"] == 5
    assert counts["provider_capability_missing"] == 0
    assert counts["evidence_required"] == 2
    assert counts["owner_approval_required_by_risk_tier"] == 0
    assert data["external_action_executed"] is False
