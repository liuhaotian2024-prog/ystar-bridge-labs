import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]

def load(rel):
    return json.loads((ROOT / rel).read_text())


def test_idempotency_replay_blocks_duplicate_without_duplicate_receipt():
    data = load("operations/external_validation/e22_idempotency_replay_proof.json")
    assert data["duplicate_detected"] is True
    assert data["duplicate_receipt_created"] is False
    assert data["duplicate_attempt"]["status"] == "blocked_duplicate_noop"
    assert "duplicate_idempotency_key" in data["duplicate_attempt"]["reason_codes"]
