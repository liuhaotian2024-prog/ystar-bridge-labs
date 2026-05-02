from __future__ import annotations

from typing import Any, Dict


def build_e9_owner_decision_packet(context: Dict[str, Any]) -> Dict[str, Any]:
    signal = context.get("validation_signal", "blocked_no_feedback")
    validation_ran = bool(context.get("execution", {}).get("executed"))
    feedback_captured = bool(context.get("feedback_events"))
    if signal in {"strong_positive", "weak_positive"}:
        decision = "approve_E10_paid_pilot_prep"
    elif not context.get("manifest_present") or not context.get("targets_present"):
        decision = "provide_E9_manifest_targets_and_provider"
    elif context.get("execution", {}).get("owner_operated_handoff_ready"):
        decision = "run_owner_operated_validation"
    else:
        decision = "request_more_feedback"
    return {
        "e9_status": context.get("status", "unknown"),
        "pattern_mining_status": context.get("pattern_mining_status", "research_ran"),
        "top_patterns_adopted": context.get("top_patterns_adopted", []),
        "runtime_upgrades": context.get("runtime_upgrades", []),
        "external_validation_ran": validation_ran,
        "aiden_sent_anything": bool(context.get("execution", {}).get("external_action_executed")),
        "customer_contact_occurred": bool(context.get("execution", {}).get("customer_contact_occurred")),
        "publication_occurred": bool(context.get("execution", {}).get("publication_occurred")),
        "owner_operated_feedback_captured": feedback_captured,
        "validation_signal_classification": signal,
        "recommended_next_decision": decision,
        "recommend_paid_pilot_only_after_positive_signal": signal in {"strong_positive", "weak_positive"},
        "exact_owner_action": context.get("exact_owner_action", ""),
    }


def render_e9_owner_decision_packet(packet: Dict[str, Any]) -> str:
    lines = ["# E9 Owner Decision Packet", ""]
    for key, value in packet.items():
        if key in {"top_patterns_adopted", "runtime_upgrades"}:
            continue
        lines.append(f"- {key}: {value}")
    lines.extend(["", "## Top Borrowed Patterns"])
    lines.extend(f"- {item}" for item in packet.get("top_patterns_adopted", []))
    lines.extend(["", "## Runtime Upgrades"])
    lines.extend(f"- {item}" for item in packet.get("runtime_upgrades", []))
    lines.extend(
        [
            "",
            "## Boundary",
            "- no paid pilot is recommended without positive validation signal",
            "- payment collection remains blocked unless separately approved",
            "- templates are not approval",
            "- Aiden did not send, contact, publish, collect payment, create accounts, submit forms, write CIEU/core memory, register obligations, or invent COO",
        ]
    )
    return "\n".join(lines)
