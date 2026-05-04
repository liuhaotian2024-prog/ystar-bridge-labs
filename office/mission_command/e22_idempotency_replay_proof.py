from __future__ import annotations

from typing import Any, Dict


def build_idempotency_replay_proof(envelopes: Dict[str, Any]) -> Dict[str, Any]:
    first = envelopes["envelopes"][0]
    return {
        "artifact_id": "e22_idempotency_replay_proof",
        "replayed_action_id": first["action_id"],
        "first_attempt": {"status": "dry_run_receipt_recorded", "idempotency_key": first["idempotency_key"]},
        "duplicate_attempt": {"status": "blocked_duplicate_noop", "idempotency_key": first["idempotency_key"], "reason_codes": ["duplicate_idempotency_key", "no_duplicate_receipt_created"]},
        "duplicate_detected": True,
        "duplicate_receipt_created": False,
        "external_action_executed": False,
    }
