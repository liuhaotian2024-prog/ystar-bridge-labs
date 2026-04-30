"""Small local meeting memory for the Aiden CEO chat."""

from __future__ import annotations

import re
from typing import Any

from .aiden_context_model import PACKET_DIRS, ensure_dirs, now_iso, read_json, timestamp_id, write_json


MEMORY_PATH = PACKET_DIRS["memory"] / "aiden_meeting_memory.json"


def normalize_message(text: str) -> str:
    return re.sub(r"\s+", "", text.strip().lower())


def load_meeting_memory() -> dict[str, Any]:
    ensure_dirs()
    return read_json(
        MEMORY_PATH,
        {
            "schema_version": "v0",
            "milestone_id": "L10.2",
            "packet_type": "aiden_meeting_memory",
            "created_at_utc": now_iso(),
            "recent_turns": [],
            "current_meeting_goal": "",
            "open_questions": [],
            "decisions_discussed": [],
            "follow_up_tasks": [],
            "external_side_effects": False,
            "core_writeback": False,
        },
    )


def save_meeting_memory(memory: dict[str, Any]) -> dict[str, Any]:
    memory["updated_at_utc"] = now_iso()
    memory["recent_turns"] = memory.get("recent_turns", [])[-80:]
    write_json(MEMORY_PATH, memory)
    return memory


def repeated_owner_question(message: str, memory: dict[str, Any]) -> bool:
    normalized = normalize_message(message)
    seen = [
        normalize_message(turn.get("text", ""))
        for turn in memory.get("recent_turns", [])
        if turn.get("speaker") == "owner"
    ]
    return normalized in seen


def record_turn(message: str, response: dict[str, Any]) -> dict[str, Any]:
    memory = load_meeting_memory()
    now = now_iso()
    memory.setdefault("recent_turns", []).extend(
        [
            {"speaker": "owner", "text": message, "created_at_utc": now, "intent": response.get("intent")},
            {"speaker": "aiden_ceo", "text": response.get("text", ""), "created_at_utc": now, "intent": response.get("intent")},
        ]
    )
    if response.get("intent") in {"fastest_cash_question", "meta_development_question", "general_strategy_question"}:
        memory["current_meeting_goal"] = "clarify Labs first-revenue and meta-development strategy"
    if response.get("next_concrete_step"):
        tasks = memory.setdefault("follow_up_tasks", [])
        if response["next_concrete_step"] not in tasks:
            tasks.append(response["next_concrete_step"])
    return save_meeting_memory(memory)


def build_meeting_summary() -> dict[str, Any]:
    memory = load_meeting_memory()
    owner_messages = [turn["text"] for turn in memory.get("recent_turns", []) if turn.get("speaker") == "owner"][-6:]
    aiden_messages = [turn["text"] for turn in memory.get("recent_turns", []) if turn.get("speaker") == "aiden_ceo"][-6:]
    summary = {
        "summary_id": timestamp_id("aiden_meeting_summary"),
        "created_at_utc": now_iso(),
        "current_meeting_goal": memory.get("current_meeting_goal") or "Aiden CEO discussion",
        "owner_questions": owner_messages,
        "aiden_positions": aiden_messages,
        "open_questions": memory.get("open_questions", []),
        "decisions_discussed": memory.get("decisions_discussed", []),
        "follow_up_tasks": memory.get("follow_up_tasks", []),
        "external_side_effects": False,
        "core_writeback": False,
    }
    write_json(PACKET_DIRS["memory"] / "aiden_meeting_summary_latest.json", summary)
    return summary


def create_l10_mission_from_discussion() -> dict[str, Any]:
    summary = build_meeting_summary()
    mission = {
        "mission_packet_id": timestamp_id("aiden_l10_mission_candidate"),
        "created_at_utc": now_iso(),
        "mission_title": "Aiden CEO discussion follow-up mission",
        "owner_goal": summary["current_meeting_goal"],
        "suggested_permission_tier": "Tier 0 internal work, optionally Tier 1 read-only research if owner enables it",
        "expected_deliverables": [
            "CEO decision brief",
            "7-day action plan",
            "top money-path comparison",
            "approval escalation packet if external action is proposed",
        ],
        "status": "candidate_only_not_executed",
        "external_side_effects": False,
        "core_writeback": False,
    }
    write_json(PACKET_DIRS["memory"] / "aiden_l10_mission_candidate_latest.json", mission)
    return mission
