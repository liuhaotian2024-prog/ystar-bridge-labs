"""Diagnostics and manifest for L10.2 Aiden CEO brain rescue."""

from __future__ import annotations

from .aiden_context_loader import load_aiden_context
from .aiden_context_model import PACKET_DIRS, ensure_dirs, now_iso, read_json, write_json
from .aiden_meeting_memory import load_meeting_memory


def build_aiden_diagnostics() -> dict[str, object]:
    ensure_dirs()
    context = load_aiden_context(write_snapshot=True)
    memory = load_meeting_memory()
    latest = read_json(PACKET_DIRS["diagnostics"] / "aiden_diagnostics_latest.json", {})
    diagnostics = {
        "schema_version": "v0",
        "milestone_id": "L10.2",
        "packet_type": "aiden_brain_diagnostics",
        "generated_at_utc": now_iso(),
        "aiden_context_loaded": True,
        "milestones_known": context["completed_milestones"],
        "limitations_known": context["current_limitations"],
        "meeting_memory_count": len(memory.get("recent_turns", [])),
        "last_intent": latest.get("intent", "none"),
        "meeting_memory_used": latest.get("meeting_memory_used", False),
        "generic_fallback_disabled_for_known_owner_questions": True,
        "raw_template_fallback_occurred": latest.get("raw_template_fallback_occurred", False),
        "external_side_effects": False,
        "customer_contact": False,
        "email_sent": False,
        "publication": False,
        "payment_processed": False,
        "core_writeback": False,
        "coo_invented": False,
    }
    write_json(PACKET_DIRS["manifests"] / "l10_2_aiden_brain_rescue_manifest.json", diagnostics)
    return diagnostics
