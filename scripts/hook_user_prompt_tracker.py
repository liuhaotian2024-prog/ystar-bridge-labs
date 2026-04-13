#!/usr/bin/env python3
"""
[L3] UserPromptSubmit Hook — Proactive Context Injection + Board tracking

On every user message:
1. Update scripts/.ystar_last_board_msg with current timestamp
2. Revoke CEO mode (Board presence → back to standard)
3. INJECT system context into user prompt (L2→L3 AMENDMENT-021)

Registered in .claude/settings.json as UserPromptSubmit hook
"""

import sys
import time
import json
import subprocess
from pathlib import Path
from datetime import datetime

WORKSPACE_ROOT = Path("/Users/haotianliu/.openclaw/workspace/ystar-company")
YGOV_ROOT = Path("/Users/haotianliu/.openclaw/workspace/Y-star-gov")
LAST_BOARD_MSG_FILE = WORKSPACE_ROOT / "scripts/.ystar_last_board_msg"
MODE_MANAGER_SCRIPT = WORKSPACE_ROOT / "scripts/ceo_mode_manager.py"
ACTIVE_AGENT_FILE = WORKSPACE_ROOT / ".ystar_active_agent"
SESSION_JSON = WORKSPACE_ROOT / ".ystar_session.json"
CIEU_DB = WORKSPACE_ROOT / ".ystar_cieu.db"
WHITELIST_MATCHER = WORKSPACE_ROOT / "scripts/whitelist_matcher.py"
INJECT_LOG = Path("/tmp/ystar_user_prompt_hook.log")
DIALOGUE_CONTRACT_LOG = WORKSPACE_ROOT / "scripts/.logs/dialogue_contract.log"
DIALOGUE_CONTRACT_SCRIPT = WORKSPACE_ROOT / "scripts/dialogue_to_contract_worker.py"


def get_active_agent():
    """Read current active agent"""
    try:
        return ACTIVE_AGENT_FILE.read_text().strip()
    except Exception:
        return "unknown"


def get_ceo_mode():
    """Read CEO mode from session.json"""
    try:
        with open(SESSION_JSON) as f:
            data = json.load(f)
            return data.get("ceo_mode", "standard")
    except Exception:
        return "unknown"


def get_session_age():
    """Calculate session age in minutes"""
    try:
        import sqlite3
        conn = sqlite3.connect(CIEU_DB)
        cursor = conn.cursor()
        cursor.execute("""
            SELECT timestamp FROM cieu_events
            WHERE event_type = 'session_start'
            ORDER BY id DESC LIMIT 1
        """)
        row = cursor.fetchone()
        conn.close()
        if row:
            start_time = datetime.fromisoformat(row[0])
            age_seconds = (datetime.now() - start_time).total_seconds()
            return int(age_seconds / 60)
    except Exception:
        pass
    return 0


def get_top_obligations():
    """Get top 3 pending obligations from CIEU"""
    try:
        import sqlite3
        conn = sqlite3.connect(CIEU_DB)
        cursor = conn.cursor()
        cursor.execute("""
            SELECT details FROM cieu_events
            WHERE event_type = 'obligation_created'
            AND details NOT LIKE '%completed%'
            ORDER BY id DESC LIMIT 3
        """)
        rows = cursor.fetchall()
        conn.close()
        return [r[0][:80] for r in rows] if rows else []
    except Exception:
        return []


def get_recent_drift():
    """Get last 5 FORGET_GUARD events from CIEU (last 1h)"""
    try:
        import sqlite3
        conn = sqlite3.connect(CIEU_DB)
        cursor = conn.cursor()
        one_hour_ago = (datetime.now().timestamp() - 3600)
        cursor.execute("""
            SELECT rule_id, details FROM cieu_events
            WHERE event_type = 'FORGET_GUARD'
            AND timestamp > datetime(?, 'unixepoch')
            ORDER BY id DESC LIMIT 5
        """, (one_hour_ago,))
        rows = cursor.fetchall()
        conn.close()
        return [f"{r[0]}: {r[1][:50]}" for r in rows] if rows else []
    except Exception:
        return []


def get_whitelist_hints(user_msg):
    """Get top 3 whitelist entries matching user message"""
    try:
        result = subprocess.run(
            ["python3", str(WHITELIST_MATCHER), user_msg],
            capture_output=True,
            timeout=2,
            text=True
        )
        if result.returncode == 0:
            lines = result.stdout.strip().split('\n')
            return lines[:3] if lines else []
    except Exception:
        pass
    return []


def inject_context(user_msg_preview=""):
    """Generate system context injection block"""
    active_agent = get_active_agent()
    ceo_mode = get_ceo_mode()
    session_age = get_session_age()
    obligations = get_top_obligations()
    recent_drift = get_recent_drift()
    whitelist_hints = get_whitelist_hints(user_msg_preview)

    context = f"""<system-context auto-injected="UserPromptSubmit">
[STATE] active_agent={active_agent} | ceo_mode={ceo_mode} | session_age={session_age}min
[OBLIGATIONS] {len(obligations)} pending
"""
    for i, obl in enumerate(obligations, 1):
        context += f"  {i}. {obl}\n"

    if recent_drift:
        context += f"[RECENT_DRIFT] {len(recent_drift)} events (last 1h)\n"
        for drift in recent_drift:
            context += f"  - {drift}\n"

    if whitelist_hints:
        context += "[WHITELIST_HINT] Matching patterns:\n"
        for hint in whitelist_hints:
            context += f"  - {hint}\n"

    context += "[L_TAG_REMINDER] All status reports must include [LX] tag (Iron Rule 1.5)\n"
    context += "[BREAK_GLASS_AVAILABLE] python3 scripts/ceo_mode_manager.py force_break_glass --trigger T1\n"
    context += "</system-context>\n"

    return context


def trigger_dialogue_contract_translation(user_msg: str):
    """
    AMENDMENT-022: Fork dialogue text to async nl_to_contract pipeline.
    Fire-and-forget background subprocess, emits DIALOGUE_CONTRACT_DRAFT CIEU event.
    """
    if not user_msg or len(user_msg.strip()) < 10:
        return  # Skip empty/trivial messages

    try:
        # Launch background worker (fire-and-forget)
        subprocess.Popen(
            ["python3", str(DIALOGUE_CONTRACT_SCRIPT), user_msg[:1000]],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
            start_new_session=True  # Detach from parent
        )
    except Exception as e:
        # Log error but never fail the hook
        with open(DIALOGUE_CONTRACT_LOG, "a") as f:
            f.write(f"{datetime.now().isoformat()} | spawn_error: {e}\n")


def main():
    """Hook entry point (fail-open, max 500ms)"""
    start_time = time.time()

    try:
        # Update last Board message timestamp
        now = time.time()
        LAST_BOARD_MSG_FILE.write_text(str(now))

        # Revoke CEO mode (Board is back → exit autonomous/break_glass)
        try:
            subprocess.run(
                ["python3", str(MODE_MANAGER_SCRIPT), "revoke"],
                capture_output=True,
                timeout=3
            )
        except subprocess.SubprocessError:
            pass  # Non-critical if mode manager fails

        # Inject context to stdout (Claude Code prepends to user prompt)
        # Read stdin for user message preview (if available)
        user_msg_preview = ""
        if not sys.stdin.isatty():
            try:
                user_msg_preview = sys.stdin.read(1000)  # Read full message for contract analysis
            except Exception:
                pass

        context = inject_context(user_msg_preview[:200])  # Inject uses first 200 chars
        print(context, file=sys.stdout)

        # AMENDMENT-022: Async dialogue→contract translation (non-blocking)
        if user_msg_preview:
            trigger_dialogue_contract_translation(user_msg_preview)

        # Log injection for audit trail
        elapsed_ms = int((time.time() - start_time) * 1000)
        log_entry = f"{datetime.now().isoformat()} | {elapsed_ms}ms | injected {len(context)} chars\n"
        with open(INJECT_LOG, "a") as f:
            f.write(log_entry)
            f.write(context)
            f.write("\n---\n")

    except Exception as e:
        # Fail-open: log error but don't block user message
        with open(INJECT_LOG, "a") as f:
            f.write(f"{datetime.now().isoformat()} | ERROR: {e}\n")


if __name__ == "__main__":
    main()
