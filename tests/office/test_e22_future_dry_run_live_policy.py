import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]

def load(rel):
    return json.loads((ROOT / rel).read_text())


def test_future_policy_requires_dry_run_and_live_proofs():
    data = load("operations/external_validation/e22_future_dry_run_live_policy.json")
    required = data["future_autonomous_outbound_milestone_must_include"]
    assert "dry-run receipt ledger" in required
    assert "idempotency proof" in required
    assert "suppression proof" in required
    assert "live promotion blocker report" in required
    assert data["live_mode_default_enabled"] is False
