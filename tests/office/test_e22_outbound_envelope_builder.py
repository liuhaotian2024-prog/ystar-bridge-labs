import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]

def load(rel):
    return json.loads((ROOT / rel).read_text())


def test_outbound_envelopes_are_provider_compatible_and_live_disabled():
    data = load("operations/external_validation/e22_outbound_envelopes.json")
    assert data["envelope_count"] == 5
    for env in data["envelopes"]:
        assert env["provider_mode"] == "dry_run"
        assert env["live_execution_disabled"] is True
        assert env["idempotency_key"].startswith("idem_")
        assert env["message_hash"]
        assert env["suppression_status"] == "clear"
        assert env["external_action_executed"] is False
