"""Context-grounded deterministic Aiden response engine."""

from __future__ import annotations

from typing import Any

from . import aiden_answer_templates as templates
from .aiden_context_loader import load_aiden_context
from .aiden_context_model import PACKET_DIRS, ensure_dirs, now_iso, timestamp_id, write_json
from .aiden_intent_classifier import classify_intent
from .aiden_meeting_memory import load_meeting_memory, record_turn, repeated_owner_question


def _select_answer(intent: str, context: dict[str, Any], message: str, repeated: bool) -> tuple[str, str, bool]:
    if intent == "fastest_cash_question":
        text, step = templates.fastest_cash(context, repeated)
    elif intent == "rationale_question":
        text, step = templates.rationale(context, repeated)
    elif intent == "meta_development_question":
        text, step = templates.meta_development(context, repeated)
    elif intent == "self_state_question":
        text, step = templates.self_state(context, repeated)
    elif intent == "team_delegation_request":
        text, step = templates.team_plan(context, repeated)
    elif intent == "approval_question":
        text, step = templates.approval(context, repeated)
    elif intent == "runtime_status_question":
        text, step = templates.runtime_status(context, repeated)
    elif intent == "general_strategy_question":
        text, step = templates.strategy(context, repeated)
    elif intent == "critique_or_frustration":
        text, step = templates.frustration(context, repeated)
    elif intent == "next_action_question":
        text, step = templates.team_plan(context, repeated)
    else:
        text, step = templates.unknown(context, message, repeated)
        return text, step, True
    return text, step, False


def create_aiden_response(message: str, write_packets: bool = True) -> dict[str, Any]:
    ensure_dirs()
    text = message.strip()
    if not text:
        raise ValueError("message is required")
    context = load_aiden_context(write_snapshot=write_packets)
    memory = load_meeting_memory()
    repeated = repeated_owner_question(text, memory)
    classification = classify_intent(text)
    response_text, next_step, used_fallback = _select_answer(str(classification["intent"]), context, text, repeated)
    response = {
        "schema_version": "v0",
        "milestone_id": "L10.2",
        "packet_type": "aiden_response",
        "response_id": timestamp_id("aiden_response"),
        "created_at_utc": now_iso(),
        "agent_id": "aiden_ceo",
        "display_name": "Aiden Liu",
        "speaker": "aiden_ceo",
        "owner_message": text,
        "intent": classification["intent"],
        "intent_confidence": classification["confidence"],
        "matched_reason": classification["matched_reason"],
        "text": response_text,
        "next_concrete_step": next_step,
        "context_used": True,
        "meeting_memory_used": bool(memory.get("recent_turns")),
        "repeated_question_detected": repeated,
        "used_fallback": used_fallback,
        "raw_template_fallback_used": False,
        "external_side_effects": False,
        "customer_contact": False,
        "email_sent": False,
        "publication": False,
        "payment_processed": False,
        "core_writeback": False,
        "coo_invented": False,
    }
    if write_packets:
        write_json(PACKET_DIRS["responses"] / f"{response['response_id']}.json", response)
        record_turn(text, response)
        diagnostics = {
            "diagnostic_id": timestamp_id("aiden_diagnostics"),
            "created_at_utc": now_iso(),
            "context_loaded": True,
            "known_milestones": context["completed_milestones"],
            "known_limitations": context["current_limitations"],
            "intent": response["intent"],
            "meeting_memory_used": response["meeting_memory_used"],
            "response_used_fallback": used_fallback,
            "raw_template_fallback_occurred": False,
            "external_side_effects": False,
            "core_writeback": False,
        }
        write_json(PACKET_DIRS["diagnostics"] / "aiden_diagnostics_latest.json", diagnostics)
    return response
