#!/usr/bin/env python3
"""
idle_pulse.py — ADE IDLE_PULL Trigger

Detects idle sessions (< 3 CIEU events in last 5min) and emits IDLE_PULL reminder.
Designed for cron execution: */5 * * * *
"""
import sys
import sqlite3
import json
import time
from datetime import datetime
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))
from _cieu_helpers import _get_current_agent

COMPANY_ROOT = Path("/Users/haotianliu/.openclaw/workspace/ystar-company")
CIEU_DB = COMPANY_ROOT / ".ystar_cieu.db"
ACTIVE_AGENT_FILE = COMPANY_ROOT / ".ystar_active_agent"
BOOT_PACKAGES_DIR = COMPANY_ROOT / "boot_packages"

DRY_RUN = "--dry-run" in sys.argv
IDLE_THRESHOLD = 3  # events
WINDOW_SECS = 300   # 5 minutes


def main():
    if not CIEU_DB.exists():
        # No CIEU DB yet — silent exit (no pollution)
        if DRY_RUN:
            print("[DRY_RUN] No CIEU DB found, would exit silently")
        sys.exit(0)

    # Check recent CIEU events
    try:
        conn = sqlite3.connect(str(CIEU_DB))
        cursor = conn.cursor()

        # Get events in last 5 minutes
        cutoff_ts = time.time() - WINDOW_SECS
        cursor.execute(
            "SELECT COUNT(*) FROM cieu_events WHERE created_at > ?",
            (cutoff_ts,)
        )
        recent_count = cursor.fetchone()[0]

        # Get last event timestamp
        cursor.execute("SELECT MAX(created_at) FROM cieu_events")
        last_ts = cursor.fetchone()[0]
        last_age = int(time.time() - float(last_ts)) if last_ts else -1

        conn.close()
    except sqlite3.Error as e:
        if DRY_RUN:
            print(f"[DRY_RUN] DB error (would exit): {e}")
        sys.exit(1)

    is_idle = recent_count < IDLE_THRESHOLD

    if DRY_RUN:
        print(f"[DRY_RUN] Recent events: {recent_count}, Threshold: {IDLE_THRESHOLD}")
        print(f"[DRY_RUN] Last event age: {last_age}s")
        print(f"[DRY_RUN] Idle: {is_idle}")

    if not is_idle:
        # Not idle, silent exit
        if DRY_RUN:
            print("[DRY_RUN] Not idle, would exit silently")
        sys.exit(0)

    # Read active agent
    active_agent = "unknown"
    if ACTIVE_AGENT_FILE.exists():
        active_agent = ACTIVE_AGENT_FILE.read_text().strip()

    # Get next action hint from boot package
    next_action_hint = None
    boot_pkg_path = BOOT_PACKAGES_DIR / f"{active_agent}.json"
    if boot_pkg_path.exists():
        try:
            boot_pkg = json.loads(boot_pkg_path.read_text())
            actions = boot_pkg.get("category_11_action_queue", {}).get("actions", [])
            if actions:
                next_action_hint = actions[0].get("action")
        except (json.JSONDecodeError, KeyError):
            pass

    # Build IDLE_PULL event payload
    payload = {
        "last_cieu_age_secs": last_age,
        "recent_event_count": recent_count,
        "current_active_agent": active_agent,
        "next_action_hint": next_action_hint,
        "trigger_time": datetime.now().isoformat()
    }

    if DRY_RUN:
        print("[DRY_RUN] Would emit IDLE_PULL event:")
        print(json.dumps(payload, indent=2))
        sys.exit(0)

    # Emit CIEU event (using actual schema)
    try:
        conn = sqlite3.connect(str(CIEU_DB))
        cursor = conn.cursor()

        # Get next seq_global
        cursor.execute("SELECT MAX(seq_global) FROM cieu_events")
        max_seq = cursor.fetchone()[0] or 0
        next_seq = max_seq + 1

        cursor.execute(
            """INSERT INTO cieu_events
               (event_id, seq_global, created_at, session_id, agent_id, event_type, decision, passed, violations)
               VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)""",
            (
                f"idle_pulse_{int(time.time())}",
                next_seq,
                time.time(),
                "cron",
                active_agent,
                "IDLE_PULL",
                json.dumps(payload),
                1,
                json.dumps([])
            )
        )
        conn.commit()
        conn.close()
        print(f"[IDLE_PULSE] Emitted IDLE_PULL for {active_agent} (last event {last_age}s ago)")
    except sqlite3.Error as e:
        print(f"[ERROR] Failed to emit CIEU: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
