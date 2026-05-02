from __future__ import annotations

from typing import Any, Dict


def build_e8_owner_decision_packet(cycle: Dict[str, Any]) -> Dict[str, Any]:
    result = cycle["validation_result"]
    execution = cycle["execution_gate"]
    return {
        "e8_result_status": result["result_status"],
        "external_validation_ran": bool(execution.get("executed")),
        "customer_contact_occurred": bool(execution.get("customer_contact_occurred")),
        "publication_occurred": bool(execution.get("publication_occurred")),
        "ai_disclosure_policy_status": "created",
        "manifest_status": "present" if cycle["manifest_present"] else "missing_request_written",
        "target_seed_status": "present" if cycle["targets_present"] else "missing_request_written",
        "provider_status": "available" if execution.get("provider_available") else "disabled_or_missing",
        "preflight_status": cycle["preflight"]["governance_status"],
        "action_ledger_path": execution.get("action_ledger_path") or "",
        "feedback_captured": bool(cycle["feedback_events"]),
        "validation_signal_classification": cycle["feedback_signal"],
        "top_offer": "48h AI Ops Operating Room Blueprint",
        "what_changed_from_e7": [
            "E8 adds risk tiers, transparency requirements, autonomy budgets, target constraints, frozen draft hashes, execution gate, and feedback ledger.",
            "E7 drafts become governed external-action candidates, not merely internal review docs.",
        ],
        "remaining_uncertainties": [
            "owner has not supplied a final validation manifest",
            "owner has not supplied approved targets",
            "no safe external sending provider is configured",
            "no real market feedback exists yet",
        ],
        "recommended_next_decision": result["recommended_next_decision"],
        "exact_owner_action": (
            "Create the manifest and target seed files from templates, then choose owner-operated handoff or provide a safe execution provider."
            if result["result_status"] in {"blocked_missing_manifest", "blocked_missing_targets", "blocked_missing_execution_provider", "owner_operated_handoff_ready"}
            else "Review validation signal and decide whether to revise or prepare E9."
        ),
        "no_unapproved_external_action": True,
    }


def render_e8_owner_decision_packet(packet: Dict[str, Any]) -> str:
    lines = ["# E8 Owner Decision Packet", ""]
    for key in [
        "e8_result_status",
        "external_validation_ran",
        "customer_contact_occurred",
        "publication_occurred",
        "ai_disclosure_policy_status",
        "manifest_status",
        "target_seed_status",
        "provider_status",
        "preflight_status",
        "action_ledger_path",
        "feedback_captured",
        "validation_signal_classification",
        "top_offer",
        "recommended_next_decision",
        "exact_owner_action",
        "no_unapproved_external_action",
    ]:
        value = packet.get(key)
        lines.append(f"- {key}: {'none' if value == '' or value is None else value}")
    lines.extend(["", "## What Changed From E7"])
    lines.extend(f"- {item}" for item in packet["what_changed_from_e7"])
    lines.extend(["", "## Remaining Uncertainties"])
    lines.extend(f"- {item}" for item in packet["remaining_uncertainties"])
    return "\n".join(lines)
