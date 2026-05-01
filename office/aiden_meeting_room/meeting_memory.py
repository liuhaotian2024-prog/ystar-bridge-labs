from __future__ import annotations

import json
from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List


def now_utc() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


@dataclass
class MeetingMemory:
    path: Path
    turns: List[Dict[str, Any]] = field(default_factory=list)

    @classmethod
    def load(cls, path: Path) -> "MeetingMemory":
        if path.exists():
            try:
                data = json.loads(path.read_text(encoding="utf-8"))
                return cls(path=path, turns=list(data.get("turns", []))[-30:])
            except (OSError, json.JSONDecodeError):
                return cls(path=path)
        return cls(path=path)

    def record(self, owner_message: str, aiden_response: str, intent: str) -> None:
        self.turns.append(
            {
                "created_at": now_utc(),
                "owner_message": owner_message,
                "aiden_response": aiden_response,
                "intent": intent,
            }
        )
        self.turns = self.turns[-30:]
        self.path.parent.mkdir(parents=True, exist_ok=True)
        self.path.write_text(
            json.dumps({"turns": self.turns}, ensure_ascii=False, indent=2),
            encoding="utf-8",
        )

    def repeated(self, owner_message: str) -> bool:
        return any(t.get("owner_message") == owner_message for t in self.turns[-5:])


def default_memory_path(repo_root: Path) -> Path:
    return repo_root / "office" / "aiden_meeting_room" / ".meeting_memory.json"
