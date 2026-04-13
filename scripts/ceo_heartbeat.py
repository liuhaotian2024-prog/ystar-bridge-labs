#!/usr/bin/env python3
"""CEO self-heartbeat loop — proactive autonomy driver.

Problem: ADE idle-pull sends next-U to OTHER agents, but CEO still reactive.
Solution: CEO checks own alignment every N minutes, auto-pulls when off-target or idle.

Triggers:
1. OFF_TARGET: CEO active action misaligned with priority_brief.today_targets
2. IDLE: No CIEU events from CEO in last 5min (sleeping)
3. TODAY_DONE: All today_targets completed, prompt to update priority_brief

Usage:
    python3 scripts/ceo_heartbeat.py
    python3 scripts/ceo_heartbeat.py --interval 300  # 5min (default)
    python3 scripts/ceo_heartbeat.py --dry-run       # test without emitting CIEU

Cron:
    */5 * * * * /usr/bin/python3 /Users/haotianliu/.openclaw/workspace/ystar-company/scripts/ceo_heartbeat.py >> /tmp/ceo_heartbeat.log 2>&1
"""

import argparse
import json
import sqlite3
import sys
import time
from datetime import datetime, timedelta
from pathlib import Path
from typing import Optional

REPO_ROOT = Path(__file__).resolve().parent.parent
ACTIVE_AGENT_PATH = REPO_ROOT / ".ystar_active_agent"
PRIORITY_BRIEF_PATH = REPO_ROOT / "reports" / "priority_brief.md"
CIEU_DB_PATH = REPO_ROOT / ".ystar_memory.db"

# Idle threshold: if last CEO CIEU event > 5min ago, considered idle
IDLE_THRESHOLD_SECONDS = 300


def get_active_agent() -> str:
    """Read current active agent from .ystar_active_agent."""
    if not ACTIVE_AGENT_PATH.exists():
        return "unknown"
    return ACTIVE_AGENT_PATH.read_text().strip()


def parse_priority_brief_targets() -> dict:
    """Parse priority_brief.md YAML frontmatter for today_targets."""
    if not PRIORITY_BRIEF_PATH.exists():
        return {"today_targets": []}

    content = PRIORITY_BRIEF_PATH.read_text()

    # Extract YAML frontmatter between first two "---"
    lines = content.split("\n")
    if not lines or lines[0] != "---":
        return {"today_targets": []}

    yaml_end = -1
    for i in range(1, len(lines)):
        if lines[i] == "---":
            yaml_end = i
            break

    if yaml_end == -1:
        return {"today_targets": []}

    yaml_content = "\n".join(lines[1:yaml_end])

    # Simple YAML parsing for today_targets list
    targets = []
    in_today_section = False
    current_indent = 0

    for line in yaml_content.split("\n"):
        if line.strip().startswith("today_targets:"):
            in_today_section = True
            continue

        if in_today_section:
            # Check if we've moved to a different section
            if line and not line.startswith(" ") and not line.startswith("-"):
                in_today_section = False
                continue

            # Parse target entry
            if line.strip().startswith("- target:"):
                target_text = line.split("- target:", 1)[1].strip().strip('"')
                targets.append(target_text)

    return {"today_targets": targets}


def get_last_ceo_cieu_timestamp() -> Optional[datetime]:
    """Query CIEU db for most recent CEO event timestamp."""
    if not CIEU_DB_PATH.exists():
        return None

    try:
        conn = sqlite3.connect(str(CIEU_DB_PATH))
        cursor = conn.cursor()

        # Query last CEO event
        cursor.execute("""
            SELECT timestamp
            FROM cieu_events
            WHERE actor = 'ceo'
            ORDER BY timestamp DESC
            LIMIT 1
        """)

        row = cursor.fetchone()
        conn.close()

        if not row:
            return None

        # Parse timestamp (format: 2026-04-13T08:49:15.123456)
        return datetime.fromisoformat(row[0])

    except Exception as e:
        print(f"[ERROR] Failed to query CIEU db: {e}", file=sys.stderr)
        return None


def emit_cieu_event(event_type: str, description: str, metadata: dict = None, dry_run: bool = False):
    """Emit CIEU event to .ystar_memory.db."""
    if dry_run:
        print(f"[DRY-RUN] Would emit CIEU: {event_type} — {description}")
        return

    try:
        conn = sqlite3.connect(str(CIEU_DB_PATH))
        cursor = conn.cursor()

        # Ensure table exists
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS cieu_events (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp TEXT NOT NULL,
                actor TEXT NOT NULL,
                event_type TEXT NOT NULL,
                description TEXT,
                metadata TEXT
            )
        """)

        now = datetime.now().isoformat()
        metadata_json = json.dumps(metadata or {})

        cursor.execute("""
            INSERT INTO cieu_events (timestamp, actor, event_type, description, metadata)
            VALUES (?, ?, ?, ?, ?)
        """, (now, "ceo", event_type, description, metadata_json))

        conn.commit()
        conn.close()

        print(f"[CIEU] {event_type} — {description}")

    except Exception as e:
        print(f"[ERROR] Failed to emit CIEU event: {e}", file=sys.stderr)


def check_off_target(targets: list) -> bool:
    """
    Detect if CEO is off-target.

    For MVP: return False (always assume on-target).
    Future: integrate with ADE detect_off_target(agent_id, current_action).
    """
    # TODO: Integrate with actual ADE when it's implemented
    return False


def check_idle() -> bool:
    """Check if CEO has been idle (no CIEU events in last 5min)."""
    last_event = get_last_ceo_cieu_timestamp()

    if last_event is None:
        # No events ever recorded — consider idle
        return True

    now = datetime.now()
    elapsed = (now - last_event).total_seconds()

    return elapsed > IDLE_THRESHOLD_SECONDS


def check_today_done(targets: list) -> bool:
    """
    Check if all today_targets are completed.

    For MVP: return False (assume not done).
    Future: query omission_store for completion status.
    """
    # TODO: Integrate with omission_store obligation completion tracking
    return False


def main():
    parser = argparse.ArgumentParser(description="CEO self-heartbeat loop")
    parser.add_argument("--interval", type=int, default=300, help="Heartbeat interval in seconds (default: 300)")
    parser.add_argument("--dry-run", action="store_true", help="Test mode: don't emit CIEU events")
    parser.add_argument("--once", action="store_true", help="Run once and exit (for cron)")
    args = parser.parse_args()

    # Run heartbeat check
    def heartbeat_check():
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        print(f"\n[{timestamp}] CEO Heartbeat Check")

        # 1. Check if current agent is CEO
        active_agent = get_active_agent()
        if active_agent != "ceo":
            print(f"[SKIP] Active agent is {active_agent}, not ceo")
            return

        # 2. Parse priority_brief targets
        brief = parse_priority_brief_targets()
        targets = brief.get("today_targets", [])
        print(f"[INFO] Today's targets: {len(targets)} items")

        # 3. Check off-target
        if check_off_target(targets):
            emit_cieu_event(
                "CEO_HEARTBEAT_OFF_TARGET",
                "CEO current action misaligned with priority_brief.today_targets",
                {"targets": targets},
                dry_run=args.dry_run
            )
            return

        # 4. Check idle
        if check_idle():
            emit_cieu_event(
                "CEO_HEARTBEAT_IDLE",
                "CEO idle for >5min, pulling next action from priority_brief",
                {"targets": targets},
                dry_run=args.dry_run
            )
            return

        # 5. Check today done
        if check_today_done(targets):
            emit_cieu_event(
                "CEO_TODAY_DONE_PULL_TOMORROW",
                "All today_targets completed, prompt to update priority_brief",
                {"completed_targets": targets},
                dry_run=args.dry_run
            )
            return

        print("[OK] CEO on-target and active")

    # Run once or loop
    if args.once:
        heartbeat_check()
    else:
        print(f"[START] CEO heartbeat loop (interval: {args.interval}s)")
        while True:
            heartbeat_check()
            time.sleep(args.interval)


if __name__ == "__main__":
    main()
