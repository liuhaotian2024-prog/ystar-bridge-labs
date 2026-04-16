#!/usr/bin/env python3
"""
W13 — Layer 7 Gap Fix: Sub-agent output prose scan
Purpose: After Agent tool returns (PostToolUse), scan the sub-agent's returned text
  for defer/choice/backlog-disguise patterns. Emit CIEU warn-level event if drift.
  Fail-open (does NOT block, since output already happened).

Wiring: .claude/settings.json hooks.PostToolUse (matcher applied via tool_name check inside).
"""
import json
import re
import sqlite3
import sys
import time
import uuid
from pathlib import Path

REPO_ROOT = Path("/Users/haotianliu/.openclaw/workspace/ystar-company")
CIEU_DB = REPO_ROOT / ".ystar_cieu.db"

DRIFT_KEYWORDS = [
    # defer disguise
    "稍后", "以后再", "改天", "queued for", "wait for", "later",
    "next session", "tomorrow morning",
    # backlog disguise
    "入 backlog", "入 Backlog", "入 Campaign", "下次 session",
    "下 session", "defer to", "推到下",
]
CHOICE_PATTERNS = [
    r"请选择.*[12二]",
    r"Option [AB]",
    r"方案[12一二]",
    r"[选]\s*[一二]",
    r"三选一",
    r"A\)\s.*B\)\s.*C\)",
    r"❕.*选项",
]
# Request-board-shell pattern (Board shell marker violation)
SHELL_REQUEST_PATTERNS = [
    r"Board 请跑",
    r"Board 手动跑",
    r"Board 手动写",
    r"Board 执行",
    r"需要 Board.*手动",
    r"Board 请在 terminal",
]


def _scan(text: str) -> list:
    if not text:
        return []
    hits = []
    text_lower = text.lower()
    for kw in DRIFT_KEYWORDS:
        if kw in text or kw.lower() in text_lower:
            hits.append(("SUBAGENT_DEFER_DRIFT", f"keyword={kw}"))
            break
    for pat in CHOICE_PATTERNS:
        if re.search(pat, text):
            hits.append(("SUBAGENT_CHOICE_DRIFT", f"pattern={pat}"))
            break
    for pat in SHELL_REQUEST_PATTERNS:
        if re.search(pat, text):
            hits.append(("SUBAGENT_BOARD_SHELL_REQUEST", f"pattern={pat}"))
            break
    return hits


def _emit_cieu(event_type: str, metadata: str) -> None:
    try:
        conn = sqlite3.connect(str(CIEU_DB), timeout=2.0)
        conn.execute(
            "INSERT INTO cieu_events (event_id, seq_global, created_at, session_id, agent_id, event_type, decision, passed, task_description) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)",
            (str(uuid.uuid4()), 0, time.time(), "subagent_scan", "ceo", event_type, "warn", 1, metadata[:500]),
        )
        conn.commit()
        conn.close()
    except Exception:
        pass


def main():
    try:
        payload = json.loads(sys.stdin.read() or "{}")
    except Exception:
        payload = {}

    # Only scan Agent tool outputs
    tool_name = payload.get("tool_name", "")
    if tool_name != "Agent":
        print(json.dumps({"action": "allow", "scanned": False, "reason": "not Agent tool"}))
        sys.exit(0)

    # Extract sub-agent text — multiple possible locations
    result_text = ""
    for key in ("tool_result", "result", "output"):
        v = payload.get(key)
        if isinstance(v, str):
            result_text = v
            break
        if isinstance(v, dict):
            result_text = v.get("content", v.get("text", "")) or ""
            break

    hits = _scan(result_text)
    for event_type, meta in hits:
        _emit_cieu(event_type, meta)

    print(json.dumps({"action": "allow", "scanned": True, "hits": len(hits)}))
    sys.exit(0)


if __name__ == "__main__":
    main()
