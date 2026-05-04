import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]


def test_e21_future_policy_requires_provider_manifest_and_promotion_proof():
    data = json.loads((ROOT / "operations/external_validation/e21_future_provider_policy.json").read_text())
    required = data["future_real_send_milestone_must_include"]
    assert "provider capability manifest" in required
    assert "promotion contract result" in required
    assert "suppression check" in required
    assert data["owner_manual_send_is_default"] is False
    assert data["live_send_allowed_without_live_ready_provider"] is False
