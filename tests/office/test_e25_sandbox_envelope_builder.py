import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]

def test_e25_sandbox_envelopes_are_provider_compatible_and_not_live():
    data = json.loads((ROOT / "operations/external_validation/e25_sandbox_envelopes.json").read_text())
    assert data["selected_count"] == 1
    envelope = data["envelopes"][0]
    assert envelope["provider_mode"] == "sandbox_ready"
    assert envelope["live_disabled"] is True
    assert envelope["idempotency_key"]
    assert envelope["owner_approval_required_by_risk"] is False
