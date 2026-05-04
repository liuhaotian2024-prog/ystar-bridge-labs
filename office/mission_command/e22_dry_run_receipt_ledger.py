from __future__ import annotations

from typing import Any, Dict, List


def build_dry_run_receipt_ledger(dry_run_results: Dict[str, Any], idempotency: Dict[str, Any]) -> Dict[str, Any]:
    entries: List[Dict[str, Any]] = []
    for row in dry_run_results["dry_run_results"]:
        entries.append({
            "ledger_entry_id": "ledger_" + row["action_id"],
            "action_id": row["action_id"],
            "target_name": row["target_name"],
            "receipt_type": "dry_run_receipt" if row.get("dry_run_executed") else "blocked_receipt",
            "dry_run_receipt_id": row.get("dry_run_receipt_id"),
            "live_receipt_id": None,
            "external_provider_called": False,
            "real_message_sent": False,
            "live_receipt_created": False,
            "no_external_effect_proof": row.get("no_external_effect_proof", {"provider_called": False, "real_message_sent": False, "live_receipt_created": False}),
        })
    entries.append({
        "ledger_entry_id": "ledger_replay_" + idempotency["replayed_action_id"],
        "action_id": idempotency["replayed_action_id"],
        "receipt_type": "replay_receipt",
        "dry_run_receipt_id": None,
        "live_receipt_id": None,
        "duplicate_receipt_created": idempotency["duplicate_receipt_created"],
        "external_provider_called": False,
        "real_message_sent": False,
        "live_receipt_created": False,
    })
    return {"artifact_id": "e22_dry_run_receipt_ledger", "ledger_entries": entries, "dry_run_receipt_count": sum(1 for e in entries if e["receipt_type"] == "dry_run_receipt"), "live_receipt_count": 0, "replay_receipt_count": 1, "blocked_receipt_count": sum(1 for e in entries if e["receipt_type"] == "blocked_receipt"), "external_action_executed": False}


def render_dry_run_receipt_ledger(ledger: Dict[str, Any]) -> str:
    return "\n".join(["# E22 Dry-Run Receipt Ledger", "", f"- dry_run_receipt_count: {ledger['dry_run_receipt_count']}", f"- live_receipt_count: {ledger['live_receipt_count']}", f"- replay_receipt_count: {ledger['replay_receipt_count']}", f"- blocked_receipt_count: {ledger['blocked_receipt_count']}", "- external_action_executed: false"]).rstrip()+"\n"
