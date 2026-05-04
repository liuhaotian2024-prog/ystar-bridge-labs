import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]


def test_autonomous_outbound_envelope_schema_blocks_live_execution_in_e20():
    data = json.loads((ROOT / "operations/external_validation/e20_autonomous_outbound_envelope_schema.json").read_text())
    assert "idempotency_key" in data["required_fields"]
    assert "provider_capability_status" in data["required_fields"]
    assert data["live_execution_forbidden_in_e20"] is True
    assert data["external_action_executed"] is False


def test_reclassification_rows_have_envelopes_and_no_send_receipts():
    data = json.loads((ROOT / "operations/external_validation/e20_batch_autonomous_reclassification.json").read_text())
    assert data["autonomous_outbound_envelopes"]
    first = data["autonomous_outbound_envelopes"][0]
    assert first["dry_run_receipt"]["external_action_executed"] is False
    assert first["dry_run_receipt"]["provider_called"] is False
