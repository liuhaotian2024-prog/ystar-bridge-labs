import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]


def test_batch_reclassification_distinguishes_policy_allowed_from_provider_gap():
    data = json.loads((ROOT / "operations/external_validation/e20_batch_autonomous_reclassification.json").read_text())
    assert data["summary_counts"]["provider_capability_missing"] >= 1
    assert data["summary_counts"]["owner_approval_required"] == 0
    assert any(row["classification"] == "policy_allows_autonomous_but_provider_missing" for row in data["rows"])
    assert data["external_action_executed"] is False
