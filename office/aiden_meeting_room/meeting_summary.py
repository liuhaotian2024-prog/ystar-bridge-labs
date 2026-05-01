from __future__ import annotations

from pathlib import Path

from .meeting_memory import MeetingMemory, default_memory_path


def build_summary(repo_root: Path) -> str:
    memory = MeetingMemory.load(default_memory_path(repo_root))
    if not memory.turns:
        return "No Aiden meeting turns recorded yet."
    latest = memory.turns[-5:]
    lines = ["# Aiden Meeting Summary", "", "Recent discussion:"]
    for turn in latest:
        lines.append(f"- Owner: {turn.get('owner_message', '')}")
        lines.append(f"  Aiden: {str(turn.get('aiden_response', '')).splitlines()[0]}")
    return "\n".join(lines)
