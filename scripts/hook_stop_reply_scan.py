#!/usr/bin/env python3
"""
W10 — Stop Hook: Post-reply prose scan
Purpose: Scan CEO assistant reply after Claude finishes (Stop event), detect
  defer_language / choice_question / drift keywords, emit CIEU event.
  Warn-level only (does NOT block, reply already sent). Fail-open.

Wiring: .claude/settings.json `hooks.Stop` entry invokes this.
"""
import json
import os
import re
import sqlite3
import sys
import time
import uuid
from pathlib import Path

REPO_ROOT = Path("/Users/haotianliu/.openclaw/workspace/ystar-company")
CIEU_DB = REPO_ROOT / ".ystar_cieu.db"

DEFER_KEYWORDS = [
    "明日", "明天", "明早", "明晚", "下周", "稍后", "改天", "以后再", "晚些", "等会儿",
    "tomorrow", "tomorrow morning", "next week", "next session", "queued for",
    "wait for", "later",
]
CHOICE_PATTERNS = [
    r"请选择.*[方案]?\s*[12二]",
    r"Option [AB]",
    r"\b1[\)）]\s*.*2[\)）]",
    r"方案[12一二]",
]


def _read_last_assistant_reply(payload: dict) -> str:
    """Try to extract the latest assistant reply from hook payload."""
    # Claude Code Stop hook payload shape is evolving; best-effort extract
    txt = payload.get("assistant_message", "") or payload.get("reply_text", "")
    if txt:
        return txt
    # Fallback: read session transcript if path given
    tp = payload.get("transcript_path")
    if tp and Path(tp).exists():
        try:
            lines = Path(tp).read_text(encoding="utf-8").strip().split("\n")
            for line in reversed(lines[-20:]):
                try:
                    obj = json.loads(line)
                    if obj.get("role") == "assistant":
                        content = obj.get("content", "")
                        if isinstance(content, list):
                            for block in content:
                                if block.get("type") == "text":
                                    return block.get("text", "")
                        return str(content)
                except Exception:
                    continue
        except Exception:
            pass
    return ""


def _scan(text: str) -> dict:
    if not text:
        return {"triggered": False, "rules": []}
    rules_triggered = []
    text_lower = text.lower()
    for kw in DEFER_KEYWORDS:
        if kw in text or kw.lower() in text_lower:
            rules_triggered.append({"rule": "defer_in_reply", "keyword": kw})
            break  # one hit is enough for the warn
    for pat in CHOICE_PATTERNS:
        if re.search(pat, text):
            rules_triggered.append({"rule": "choice_question_in_reply", "pattern": pat})
            break
    return {"triggered": bool(rules_triggered), "rules": rules_triggered}


def _emit_cieu(event_type: str, metadata: dict) -> None:
    try:
        conn = sqlite3.connect(str(CIEU_DB), timeout=2.0)
        conn.execute(
            "INSERT INTO cieu_events (event_id, seq_global, created_at, session_id, agent_id, event_type, decision, passed, task_description) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)",
            (
                str(uuid.uuid4()),
                0,
                time.time(),
                "reply_scan",
                "ceo",
                event_type,
                "warn",
                1,
                json.dumps(metadata, ensure_ascii=False)[:500],
            ),
        )
        conn.commit()
        conn.close()
    except Exception:
        pass  # fail-open


def main():
    try:
        payload = json.loads(sys.stdin.read() or "{}")
    except Exception:
        payload = {}
    reply = _read_last_assistant_reply(payload)
    scan = _scan(reply)
    if scan["triggered"]:
        for r in scan["rules"]:
            _emit_cieu("DEFER_IN_REPLY_DRIFT" if r["rule"] == "defer_in_reply" else "CHOICE_IN_REPLY_DRIFT", r)
    # Stop hook: never block, always exit 0
    print(json.dumps({"action": "allow", "scanned": scan["triggered"]}))
    sys.exit(0)


if __name__ == "__main__":
    main()
