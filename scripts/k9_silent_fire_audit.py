#!/usr/bin/env python3
"""
K9 Silent Fire Audit — Detect K9 events emitted during atomic execution

**Authority**: Platform Engineer Ryan Park per CEO directive CZL-136
**Spec**: governance/action_model_v2.md Phase C step 13
**Purpose**: Audit K9 scope/secret/syntax violations emitted between atomic start-end

Called by: action_model_validator.py register_reply() at Phase C completion
Emits CIEU: K9_SILENT_FIRE_DETECTED if ≥1 K9 violation found in atomic time window

Usage:
    python3 k9_silent_fire_audit.py --start "2026-04-16T12:00:00Z" --end "2026-04-16T12:05:00Z"
    # OR called as function from register_reply()
"""

import sys
import json
import sqlite3
from pathlib import Path
from datetime import datetime
from typing import List, Dict, Optional


# K9 event types that indicate violations (not informational events)
K9_VIOLATION_EVENTS = [
    "K9_SCOPE_VIOLATION",
    "K9_SECRET_DETECTED",
    "K9_SYNTAX_ERROR",
    "K9_UNAUTHORIZED_ACCESS",
    "K9_RESOURCE_LEAK"
]


def audit_during_atomic(start_ts: str, end_ts: str, atomic_id: Optional[str] = None) -> Dict:
    """
    Query CIEU database for K9 violation events in [start_ts, end_ts] window.

    Returns:
        {
            "violation_count": int,
            "violations": List[Dict],  # List of K9 events found
            "silent_fire": bool,  # True if ≥1 violation detected
            "audit_timestamp": str
        }
    """
    db_path = Path.home() / ".openclaw/workspace/ystar-company/.ystar_cieu.db"

    try:
        conn = sqlite3.connect(str(db_path), timeout=5.0)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()

        # Query K9 violation events in time window
        cursor.execute("""
            SELECT event_id, event_type, timestamp, agent_id, data
            FROM cieu_events
            WHERE event_type IN ({})
              AND timestamp BETWEEN ? AND ?
            ORDER BY timestamp ASC
        """.format(','.join('?' * len(K9_VIOLATION_EVENTS))),
            (*K9_VIOLATION_EVENTS, start_ts, end_ts)
        )

        rows = cursor.fetchall()
        violations = [dict(row) for row in rows]
        conn.close()

        silent_fire = len(violations) > 0

        result = {
            "violation_count": len(violations),
            "violations": violations,
            "silent_fire": silent_fire,
            "audit_timestamp": datetime.utcnow().isoformat() + "Z",
            "atomic_id": atomic_id
        }

        # Emit CIEU event if silent fire detected
        if silent_fire:
            emit_cieu_silent_fire(result)

        return result

    except sqlite3.Error as e:
        sys.stderr.write(f"K9 audit DB error: {e}\n")
        return {
            "violation_count": 0,
            "violations": [],
            "silent_fire": False,
            "audit_timestamp": datetime.utcnow().isoformat() + "Z",
            "error": str(e)
        }


def emit_cieu_silent_fire(audit_result: Dict):
    """Emit K9_SILENT_FIRE_DETECTED CIEU event."""
    try:
        import uuid as uuid_lib
        import time

        db_path = Path.home() / ".openclaw/workspace/ystar-company/.ystar_cieu.db"
        conn = sqlite3.connect(str(db_path), timeout=5.0)
        cursor = conn.cursor()

        # Generate event fields per schema
        event_id = str(uuid_lib.uuid4())
        now = time.time()
        seq_global = int(now * 1_000_000)  # microsecond timestamp

        cursor.execute("""
            INSERT INTO cieu_events (
                event_id, seq_global, created_at, session_id, agent_id, event_type,
                decision, passed, violations, drift_detected
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            event_id,
            seq_global,
            now,
            "current",  # session_id placeholder
            "k9_silent_fire_audit",
            "K9_SILENT_FIRE_DETECTED",
            "escalate",  # K9 violations require escalation
            0,  # Not passed (violation detected)
            json.dumps([v["event_type"] for v in audit_result["violations"]]),
            1  # Drift detected (K9 violations are drift)
        ))

        conn.commit()
        conn.close()
    except Exception as e:
        sys.stderr.write(f"K9_SILENT_FIRE emit error: {e}\n")


def main():
    """CLI entry point for standalone audit runs."""
    import argparse

    parser = argparse.ArgumentParser(description="Audit K9 events in time window")
    parser.add_argument("--start", required=True, help="Start timestamp ISO8601")
    parser.add_argument("--end", required=True, help="End timestamp ISO8601")
    parser.add_argument("--atomic-id", help="Optional atomic ID for tracking")
    args = parser.parse_args()

    result = audit_during_atomic(args.start, args.end, args.atomic_id)
    print(json.dumps(result, indent=2))

    return 0 if not result["silent_fire"] else 1


if __name__ == "__main__":
    sys.exit(main())
