#!/usr/bin/env python3
"""
Y* Bridge Labs — CIEU event watcher (Secretary-owned, AMENDMENT / Board
2026-04-15 directive).

Purpose
-------
Close the auto-trigger gap for telegram_notify.send_event. Before this watcher,
CRITICAL_INSIGHT / MAJOR_INCIDENT rows could only reach the Board channel via
manual CLI (`python3 scripts/telegram_notify.py event ...`). Any agent writing
to CIEU directly (not going through the CLI) got swallowed.

Design (Iron Rule 1.6 CIEU 5-tuple)
-----------------------------------
- Y   : watcher polls `.ystar_cieu.db` every cron tick.
- Xt  : reads state file for last-polled rowid, queries
        `WHERE rowid > ? AND event_type IN (...)` (index-backed, no full scan).
- U   : for each new matching row, calls
        `telegram_notify.send_event(event_type, ctx)`; advances state file
        atomically; self-emits CIEU `CIEU_WATCHER_TICK` row so this loop is
        itself auditable (prevents silent failure).
- Yt+1: Telegram push delivered (or dry-run stdout in test mode).
- Rt+1=0: no push attempted iff zero matching rows advanced.

Poll target event_types
-----------------------
- CRITICAL_INSIGHT  — agent surfaces a non-obvious truth worth Board attention
                       (see docs/cieu_event_schema.md for emit contract).
- MAJOR_INCIDENT    — system failure, data loss risk, governance breach.

MILESTONE_SHIPPED is NOT watched here because it already has a dedicated
trigger path (3a905495). We intentionally keep this watcher's scope narrow.

Anti-duplication
----------------
State file `scripts/.state/cieu_watcher_last_rowid` stores the last rowid we
handled. Rowid is monotonic (AUTOINCREMENT). On crash mid-batch, worst case is
the last un-advanced row is sent twice on the next tick — acceptable since
Telegram messages are idempotent at the human-reader layer.

Usage
-----
    python3 scripts/cieu_event_watcher.py            # one tick, live push
    python3 scripts/cieu_event_watcher.py --dry-run  # stdout only
    python3 scripts/cieu_event_watcher.py --reset    # reset cursor to MAX(rowid)

Cron
----
    */1 * * * * cd /Users/haotianliu/.openclaw/workspace/ystar-company && \\
        /usr/bin/python3 scripts/cieu_event_watcher.py \\
        >> scripts/.logs/cieu_event_watcher.log 2>&1
"""
from __future__ import annotations

import argparse
import json
import os
import sqlite3
import sys
import time
from pathlib import Path

WORKSPACE = Path("/Users/haotianliu/.openclaw/workspace/ystar-company")
CIEU_DB = WORKSPACE / ".ystar_cieu.db"
STATE_DIR = WORKSPACE / "scripts" / ".state"
STATE_FILE = STATE_DIR / "cieu_watcher_last_rowid"
LOG_DIR = WORKSPACE / "scripts" / ".logs"

WATCHED_EVENT_TYPES = ("CRITICAL_INSIGHT", "MAJOR_INCIDENT")

# Import the Secretary-owned notifier. Keep import-time side effects minimal.
sys.path.insert(0, str(WORKSPACE / "scripts"))
from telegram_notify import send_event  # noqa: E402


def _read_cursor() -> int:
    if not STATE_FILE.exists():
        return 0
    try:
        return int(STATE_FILE.read_text().strip() or 0)
    except Exception:
        return 0


def _write_cursor(rowid: int) -> None:
    STATE_DIR.mkdir(parents=True, exist_ok=True)
    tmp = STATE_FILE.with_suffix(".tmp")
    tmp.write_text(str(rowid))
    tmp.replace(STATE_FILE)


def _emit_tick(processed: int, pushed: int, last_rowid: int) -> None:
    """Self-audit row so the watcher itself is traceable in CIEU."""
    if not CIEU_DB.exists():
        return
    try:
        now = time.time()
        event_id = f"cieu_watcher_{int(now * 1_000_000)}"
        conn = sqlite3.connect(str(CIEU_DB), timeout=2.0)
        try:
            conn.execute(
                """INSERT OR IGNORE INTO cieu_events
                   (event_id, seq_global, created_at, session_id, agent_id,
                    event_type, decision, passed, violations, drift_detected)
                   VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, 0)""",
                (
                    event_id,
                    int(now * 1_000_000),
                    now,
                    os.environ.get("CLAUDE_SESSION_ID", "cieu_event_watcher"),
                    "samantha-secretary",
                    "CIEU_WATCHER_TICK",
                    "allow",
                    1,
                    json.dumps(
                        {"processed": processed, "pushed": pushed, "last_rowid": last_rowid}
                    ),
                ),
            )
            conn.commit()
        finally:
            conn.close()
    except Exception:
        pass


def tick(dry_run: bool = False) -> int:
    if not CIEU_DB.exists():
        print(f"[watcher] DB missing: {CIEU_DB}")
        return 2

    cursor = _read_cursor()
    conn = sqlite3.connect(str(CIEU_DB), timeout=5.0)
    conn.row_factory = sqlite3.Row
    try:
        placeholders = ",".join("?" for _ in WATCHED_EVENT_TYPES)
        # Index-backed: idx_event_type on event_type + rowid filter.
        rows = conn.execute(
            f"""SELECT rowid, event_id, event_type, agent_id, task_description,
                       file_path, command, violations, created_at
                FROM cieu_events
                WHERE rowid > ?
                  AND event_type IN ({placeholders})
                ORDER BY rowid ASC
                LIMIT 50""",
            (cursor, *WATCHED_EVENT_TYPES),
        ).fetchall()
    finally:
        conn.close()

    if not rows:
        _emit_tick(0, 0, cursor)
        return 0

    pushed = 0
    last_rowid = cursor
    for row in rows:
        ctx = {
            "title": (row["task_description"] or row["event_id"])[:140],
            "detail": (
                f"agent: `{row['agent_id']}`\n"
                f"file: `{row['file_path'] or '—'}`\n"
                f"cmd: `{(row['command'] or '—')[:120]}`\n"
                f"violations: {row['violations'] or '—'}"
            ),
            "source": f"cieu_watcher · rowid={row['rowid']}",
        }
        ok = send_event(row["event_type"], ctx, dry_run=dry_run)
        if ok:
            pushed += 1
        last_rowid = row["rowid"]
        # Advance cursor per row so a mid-batch crash doesn't replay the whole batch.
        _write_cursor(last_rowid)

    _emit_tick(len(rows), pushed, last_rowid)
    print(
        f"[watcher] processed={len(rows)} pushed={pushed} "
        f"cursor {cursor} -> {last_rowid} dry={dry_run}"
    )
    return 0


def reset_cursor() -> int:
    if not CIEU_DB.exists():
        print(f"[watcher] DB missing: {CIEU_DB}")
        return 2
    conn = sqlite3.connect(str(CIEU_DB))
    try:
        mx = conn.execute("SELECT COALESCE(MAX(rowid), 0) FROM cieu_events").fetchone()[0]
    finally:
        conn.close()
    _write_cursor(mx)
    print(f"[watcher] cursor reset to MAX(rowid)={mx}")
    return 0


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--dry-run", action="store_true", help="stdout push, no telegram HTTP")
    ap.add_argument("--reset", action="store_true", help="set cursor to MAX(rowid) and exit")
    args = ap.parse_args()

    LOG_DIR.mkdir(parents=True, exist_ok=True)

    if args.reset:
        return reset_cursor()
    return tick(dry_run=args.dry_run)


if __name__ == "__main__":
    sys.exit(main())
