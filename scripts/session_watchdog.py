#!/usr/bin/env python3
"""Session Watchdog — Lightweight in-session health monitor.

Checks 4 signals and returns a composite health score (0-100):
  1. Session age        (weight 25%)  — time since .session_booted created
  2. Context pressure   (weight 25%)  — context window usage percentage
  3. CIEU repetition    (weight 30%)  — repeated action fingerprints in recent events
  4. Obligation decay   (weight 20%)  — overdue obligations vs total

Usage:
    # Quick check (for hooks/statusline — <50ms target)
    python3 scripts/session_watchdog.py --quick

    # Full check with details
    python3 scripts/session_watchdog.py --full

    # Accept context_pct from stdin (hook mode)
    echo '{"context_pct": 72.5}' | python3 scripts/session_watchdog.py --quick

Output: JSON to stdout
    {"score": 78, "status": "OK", "signals": {...}, "recommendation": null}
    {"score": 42, "status": "WARNING", "signals": {...}, "recommendation": "Save state soon"}
    {"score": 28, "status": "RESTART_NOW", "signals": {...}, "recommendation": "Execute save-and-restart"}

Thresholds (aligned with gov_health):
    >= 70  OK
    40-69  WARNING
    < 40   RESTART_NOW
"""

from __future__ import annotations

import json
import os
import sys
import time
import sqlite3
import hashlib
from pathlib import Path
from typing import Optional

YSTAR_DIR = Path(__file__).resolve().parent.parent
CIEU_DB = YSTAR_DIR / ".ystar_cieu.db"
SESSION_MARKER = YSTAR_DIR / "scripts" / ".session_booted"
CALL_COUNT_FILE = YSTAR_DIR / "scripts" / ".session_call_count"

# Thresholds
SCORE_OK = 70
SCORE_WARNING = 40
SESSION_MAX_HOURS = 8  # after 8h, session age signal = 0
SESSION_WARN_HOURS = 3  # below this, full score
REPETITION_WINDOW = 30  # last N CIEU events to check
REPETITION_THRESHOLD = 0.30  # 30% repetition = score 0

# Weights
W_AGE = 0.25
W_CONTEXT = 0.25
W_REPETITION = 0.30
W_OBLIGATION = 0.20


def get_session_age_score() -> dict:
    """Score based on session age. Full marks if <3h, zero at 8h."""
    if not SESSION_MARKER.exists():
        return {"score": 100, "hours": 0, "detail": "no active session marker"}

    age_s = time.time() - SESSION_MARKER.stat().st_mtime
    hours = age_s / 3600

    if hours <= SESSION_WARN_HOURS:
        score = 100
    elif hours >= SESSION_MAX_HOURS:
        score = 0
    else:
        # Linear decay from 100 to 0 between WARN and MAX
        score = 100 * (1 - (hours - SESSION_WARN_HOURS) / (SESSION_MAX_HOURS - SESSION_WARN_HOURS))

    return {"score": round(score, 1), "hours": round(hours, 1), "detail": f"{hours:.1f}h elapsed"}


def get_context_score(context_pct: float | None) -> dict:
    """Score based on context window usage. Full marks if <50%, zero at 95%."""
    if context_pct is None:
        return {"score": 100, "pct": None, "detail": "no context data"}

    if context_pct <= 50:
        score = 100
    elif context_pct >= 95:
        score = 0
    else:
        score = 100 * (1 - (context_pct - 50) / 45)

    return {"score": round(score, 1), "pct": round(context_pct, 1), "detail": f"{context_pct:.0f}% used"}


def event_fingerprint(event_type: str, file_path: str | None, command: str | None,
                      agent_id: str | None = None, task_desc: str | None = None) -> str:
    """Stable semantic fingerprint for an action (matches gov_health algorithm).

    W14 fix: when file_path and command are both empty (common for
    external_observation / cmd_exec events), fall back to agent_id +
    task_description[:40] to distinguish actions. Without this fallback,
    8+ events with different semantic content collide to the same fingerprint,
    producing false-positive repetition signal.
    """
    parts = [event_type or "", file_path or "", command or ""]
    # Fallback: if primary params empty, distinguish by agent + task prefix
    if not (file_path or command):
        parts.append(agent_id or "")
        parts.append((task_desc or "")[:40])
    return hashlib.sha256("|".join(parts).encode()).hexdigest()[:16]


def get_repetition_score() -> dict:
    """Score based on action repetition in recent CIEU events."""
    if not CIEU_DB.exists():
        return {"score": 100, "repetition_rate": 0, "detail": "no CIEU DB"}

    try:
        conn = sqlite3.connect(CIEU_DB, timeout=2)
        conn.execute("PRAGMA journal_mode=WAL")
        # Exclude guard/watchdog infrastructure events — repetition among those
        # reflects active enforcement (healthy), not agent loop.
        rows = conn.execute(
            "SELECT event_type, file_path, command, agent_id, task_description FROM cieu_events "
            "WHERE agent_id NOT IN ('forget_guard', 'subagent_scan', 'reply_scan', 'cieu_watcher', 'orchestrator', 'intervention_engine') "
            "AND event_type NOT LIKE '%_DRIFT' "
            "AND event_type NOT LIKE 'CIEU_%' "
            "AND event_type NOT LIKE 'orchestration:%' "
            "AND event_type NOT IN ('HOOK_BOOT', 'circuit_breaker_armed', 'omission_setup_complete', 'governance_coverage_scan', 'handoff', 'intervention_gate:deny') "
            "ORDER BY created_at DESC LIMIT ?",
            (REPETITION_WINDOW,)
        ).fetchall()
        conn.close()
    except Exception:
        return {"score": 100, "repetition_rate": 0, "detail": "CIEU read error"}

    if len(rows) < 5:
        return {"score": 100, "repetition_rate": 0, "detail": f"only {len(rows)} events"}

    fps = [event_fingerprint(r[0], r[1], r[2], r[3] if len(r) > 3 else None, r[4] if len(r) > 4 else None) for r in rows]
    unique = len(set(fps))
    total = len(fps)
    repetition_rate = 1 - (unique / total) if total > 0 else 0

    if repetition_rate <= 0.05:
        score = 100
    elif repetition_rate >= REPETITION_THRESHOLD:
        score = 0
    else:
        score = 100 * (1 - repetition_rate / REPETITION_THRESHOLD)

    return {
        "score": round(score, 1),
        "repetition_rate": round(repetition_rate, 3),
        "unique": unique,
        "total": total,
        "detail": f"{repetition_rate:.0%} repetition in last {total} events"
    }


def get_obligation_score() -> dict:
    """Score based on overdue obligations ratio."""
    if not CIEU_DB.exists():
        return {"score": 100, "overdue": 0, "total": 0, "detail": "no CIEU DB"}

    try:
        conn = sqlite3.connect(CIEU_DB, timeout=2)
        now = time.time()

        # Count registered obligations
        registered = conn.execute(
            "SELECT COUNT(*) FROM cieu_events WHERE event_type = 'OBLIGATION_REGISTERED'"
        ).fetchone()[0]

        # Count fulfilled
        fulfilled = conn.execute(
            "SELECT COUNT(*) FROM cieu_events WHERE event_type = 'OBLIGATION_FULFILLED'"
        ).fetchone()[0]

        # Count cancelled (also closed state, not pending)
        cancelled = conn.execute(
            "SELECT COUNT(*) FROM cieu_events WHERE event_type = 'OBLIGATION_CANCELLED'"
        ).fetchone()[0]

        # Count overdue (registered but not fulfilled, with due_at in the past)
        # Simplified: just look at recent session obligations
        overdue_rows = conn.execute("""
            SELECT COUNT(*) FROM cieu_events
            WHERE event_type = 'OBLIGATION_REGISTERED'
            AND params_json LIKE '%due_at%'
            AND created_at > ?
        """, (now - 86400,)).fetchall()  # last 24h

        conn.close()

        pending = max(0, registered - fulfilled - cancelled)
        closed = fulfilled + cancelled
        if registered == 0:
            score = 100
        else:
            fulfillment_rate = closed / registered
            if fulfillment_rate >= 0.7:
                score = 100
            elif fulfillment_rate <= 0.3:
                score = 0
            else:
                score = 100 * (fulfillment_rate - 0.3) / 0.4

        return {
            "score": round(score, 1),
            "registered": registered,
            "fulfilled": fulfilled,
            "pending": pending,
            "detail": f"{fulfilled}/{registered} fulfilled"
        }
    except Exception:
        return {"score": 100, "overdue": 0, "total": 0, "detail": "query error"}


def get_call_count() -> int:
    """Read current tool call count from marker file."""
    try:
        return int(CALL_COUNT_FILE.read_text().strip())
    except Exception:
        return 0


def increment_call_count() -> int:
    """Increment and return new call count."""
    count = get_call_count() + 1
    CALL_COUNT_FILE.write_text(str(count))
    return count


def compute_health(context_pct: float | None = None) -> dict:
    """Compute composite health score and recommendation."""
    signals = {
        "session_age": get_session_age_score(),
        "context": get_context_score(context_pct),
        "repetition": get_repetition_score(),
        "obligation": get_obligation_score(),
    }

    composite = (
        W_AGE * signals["session_age"]["score"]
        + W_CONTEXT * signals["context"]["score"]
        + W_REPETITION * signals["repetition"]["score"]
        + W_OBLIGATION * signals["obligation"]["score"]
    )
    score = round(composite, 1)

    if score >= SCORE_OK:
        status = "OK"
        recommendation = None
    elif score >= SCORE_WARNING:
        status = "WARNING"
        recommendation = "Session degrading. Save state soon and prepare for restart."
    else:
        status = "RESTART_NOW"
        recommendation = (
            "SESSION HEALTH CRITICAL. Execute save-and-restart protocol NOW:\n"
            "1. Run: python3 scripts/session_close_yml.py ceo \"auto-restart: health score {}\"\n"
            "2. Run: bash scripts/session_auto_restart.sh save\n"
            "3. Tell Board: session needs restart"
        ).format(score)

    # Check for any single critical signal
    critical_signals = [
        name for name, sig in signals.items()
        if sig["score"] <= 10
    ]
    if critical_signals and status == "OK":
        status = "WARNING"
        recommendation = f"Critical signal(s): {', '.join(critical_signals)}"

    return {
        "score": score,
        "status": status,
        "signals": signals,
        "recommendation": recommendation,
        "call_count": get_call_count(),
        "timestamp": time.time(),
    }


def main():
    import argparse
    parser = argparse.ArgumentParser(description="Session health watchdog")
    parser.add_argument("--quick", action="store_true", help="Quick check (for statusline)")
    parser.add_argument("--full", action="store_true", help="Full check with details")
    parser.add_argument("--increment", action="store_true", help="Increment call count before check")
    parser.add_argument("--context-pct", type=float, default=None, help="Context window usage %")
    parser.add_argument("--statusline", action="store_true", help="Output for statusline (compact)")
    args = parser.parse_args()

    # Try reading context_pct from stdin if not provided
    context_pct = args.context_pct
    if context_pct is None and not sys.stdin.isatty():
        try:
            stdin_data = json.loads(sys.stdin.read())
            context_pct = stdin_data.get("context_pct") or stdin_data.get("context_window", {}).get("used_percentage")
        except Exception:
            pass

    if args.increment:
        increment_call_count()

    result = compute_health(context_pct)

    if args.statusline:
        # Compact output for statusline
        score = result["score"]
        status = result["status"]
        if status == "OK":
            color = "\033[0;32m"  # green
        elif status == "WARNING":
            color = "\033[1;33m"  # yellow
        else:
            color = "\033[1;31m"  # red
        reset = "\033[0m"
        print(f"{color}HP:{score:.0f}{reset}", end="")
    elif args.quick:
        # Minimal JSON
        print(json.dumps({
            "score": result["score"],
            "status": result["status"],
            "recommendation": result["recommendation"]
        }))
    else:
        # Full JSON
        print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
