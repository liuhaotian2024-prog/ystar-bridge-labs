#!/usr/bin/env python3
"""PreToolUse hook — OmissionEngine behavior-governance enforcement.

Reads .ystar_cieu_omission.db for OPEN obligations past hard_overdue_secs deadline
for the current active_agent. If any exist, DENY the tool call with specific
obligation ids + close-path hint.

Pure behavior-governance:
  - Checks: due_at + hard_overdue_secs < now (time arithmetic, not text scan)
  - Acts on: actual obligation table state (durable record, not agent utterance)
  - Blocks: Tool call (action, not language)

M-tag: M-2b (防漏做 — lazy agent no longer escapes silent). Board 2026-04-22 directive:
"OmissionEngine 必须完全起作用... 行为治理而不是言论钳制... 解决 agent 懒惰推诿".

Fail-open: If DB missing/corrupt, emit warning + allow (don't brick sessions).
Break-glass: If break-glass active (ceo_mode_state.json shows BREAK_GLASS), allow
             (emergency window must not be self-blocked).

Exit 0 = allow; exit 1 + stdout JSON = deny.
"""
from __future__ import annotations

import json
import os
import sqlite3
import sys
import time
from pathlib import Path

WORKSPACE = Path("/Users/haotianliu/.openclaw/workspace/ystar-company")
OMISSION_DB = WORKSPACE / ".ystar_cieu_omission.db"
CEO_MODE_STATE = WORKSPACE / "scripts" / ".ceo_mode_state.json"
ACTIVE_AGENT_FILE = WORKSPACE / "scripts" / ".ystar_active_agent"

# Agents we enforce against. path_a_agent excluded (synthetic meta-governance noise).
ENFORCED_AGENTS = {
    "ceo", "cto", "ethan", "leo", "maya", "ryan", "jordan",
    "sofia", "zara", "marco", "samantha",
}

# Don't enforce on these tools (breaks boot + debugging flows)
ALLOWLIST_TOOLS = {
    "Read", "Grep", "Glob",  # read-only, essential for debugging the block
}


def _is_break_glass_active() -> bool:
    """Don't self-block during break-glass emergency window."""
    if not CEO_MODE_STATE.exists():
        return False
    try:
        state = json.loads(CEO_MODE_STATE.read_text())
        if state.get("mode") == "BREAK_GLASS":
            expires = state.get("hard_cap_expires_at", 0)
            if expires > time.time():
                return True
    except Exception:
        pass
    return False


def _get_active_agent() -> str:
    """Read current active agent (fail-open if marker missing)."""
    if not ACTIVE_AGENT_FILE.exists():
        return ""
    try:
        return ACTIVE_AGENT_FILE.read_text().strip().lower()
    except Exception:
        return ""


def _query_overdue_open(agent_id: str, now: float) -> list[tuple]:
    """Return list of (obligation_id, due_at, violation_code, notes) for overdue open obligations.
    Overdue = pending + (due_at + hard_overdue_secs) < now."""
    if not OMISSION_DB.exists():
        return []
    try:
        conn = sqlite3.connect(str(OMISSION_DB), timeout=2)
        rows = conn.execute("""
            SELECT obligation_id, due_at, violation_code, notes, hard_overdue_secs
            FROM obligations
            WHERE actor_id = ?
              AND status = 'pending'
              AND (due_at + COALESCE(hard_overdue_secs, 0)) < ?
            ORDER BY due_at ASC
            LIMIT 10
        """, (agent_id, now)).fetchall()
        conn.close()
        return rows
    except Exception as e:
        print(f"[omission_enforce] DB query error (fail-open): {e}", file=sys.stderr)
        return []


def main() -> int:
    try:
        payload = json.loads(sys.stdin.read() or "{}")
    except Exception:
        payload = {}

    tool_name = payload.get("tool_name") or payload.get("tool") or ""
    if tool_name in ALLOWLIST_TOOLS:
        return 0

    # Break-glass override: don't self-block during emergency
    if _is_break_glass_active():
        return 0

    agent_id = _get_active_agent()
    if not agent_id or agent_id not in ENFORCED_AGENTS:
        return 0  # unknown agent, fail-open

    overdue = _query_overdue_open(agent_id, time.time())
    if not overdue:
        return 0

    # DENY with specific obligations
    ob_ids = [r[0] for r in overdue[:3]]
    first_due_ts = overdue[0][1]
    age_sec = time.time() - (first_due_ts + overdue[0][4] if overdue[0][4] else first_due_ts)
    age_min = int(age_sec / 60)

    message = (
        f"[OmissionEngine DENY] Agent '{agent_id}' has {len(overdue)} overdue open obligation(s).\n"
        f"Oldest overdue by {age_min} min.\n"
        f"Open obligation ids: {ob_ids}\n"
        f"Close required before new tool calls:\n"
        f"  python3.11 /Users/haotianliu/.openclaw/workspace/ystar-company/scripts/omission_status.py --agent {agent_id}\n"
        f"Or emit close event (acknowledgement/decline/blocker_report) for each.\n"
        f"Or break-glass T1 if emergency: python3 scripts/ceo_mode_manager.py force_break_glass --trigger T1"
    )

    print(json.dumps({
        "action": "block",
        "message": message,
        "agent": agent_id,
        "overdue_count": len(overdue),
        "oldest_obligation_id": overdue[0][0],
    }))
    return 1


if __name__ == "__main__":
    sys.exit(main())
