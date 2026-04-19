"""
Audience: Experiment 3 B2 axis — lock-death recurrence tracker.
Research basis: identity lock-death plagued today pre-fix (10+ occurrences per memory project_active_agent_drift); sibling bug #4 + P1-d break-glass + payload override shipped.
Synthesis: detect pattern = agent_id='agent' + restricted write deny + no recovery event within N seconds.
Purpose: 2h rolling window count; 0 target.

Exit: 0 pass / 1 fail (any lock-death) / 2 harness error.
"""
import json
import sqlite3
import sys
import time
from pathlib import Path

CIEU_DB = Path("/Users/haotianliu/.openclaw/workspace/ystar-company/.ystar_cieu.db")
REPORT_DIR = Path("/Users/haotianliu/.openclaw/workspace/ystar-company/reports/ceo/experiments/exp3_b2")
REPORT_DIR.mkdir(parents=True, exist_ok=True)

WINDOW_SECONDS = 2 * 60 * 60
RECOVERY_WINDOW_SECONDS = 120

LOCK_DEATH_MARKERS = [
    "Restricted write path violation",
    "can only be written by roles",
    "boundary violation",
]

RECOVERY_MARKERS = [
    "break_glass",
    "self_heal",
    "A025",
    "active_agent restore",
]


def fetch_events(conn, window_seconds: int):
    cutoff = time.time() - window_seconds
    rows = conn.execute(
        "SELECT event_id, event_type, agent_id, decision, violations, "
        "drift_details, file_path, command, created_at "
        "FROM cieu_events WHERE created_at >= ? ORDER BY created_at ASC",
        (cutoff,),
    ).fetchall()
    return rows


def detect_lock_deaths(rows):
    candidates = []
    for row in rows:
        (event_id, event_type, agent_id, decision, violations,
         drift_details, file_path, command, created_at) = row
        if (decision or "").lower() != "deny":
            continue
        if (agent_id or "").lower() != "agent":
            continue
        probe = " ".join(filter(None, [event_type, violations, drift_details, file_path, command]))
        if any(m.lower() in probe.lower() for m in LOCK_DEATH_MARKERS):
            candidates.append({
                "event_id": event_id,
                "ts": created_at,
                "event_type": event_type,
                "file_path": file_path,
                "violations": violations,
            })
    return candidates


def detect_recovery(rows, lock_ts):
    recovery_cutoff = lock_ts + RECOVERY_WINDOW_SECONDS
    for row in rows:
        (event_id, event_type, agent_id, decision, violations,
         drift_details, file_path, command, created_at) = row
        if created_at < lock_ts or created_at > recovery_cutoff:
            continue
        probe = " ".join(filter(None, [event_type, violations, drift_details, command]))
        if any(m.lower() in probe.lower() for m in RECOVERY_MARKERS):
            return {"event_id": event_id, "ts": created_at, "event_type": event_type}
    return None


def main():
    if not CIEU_DB.exists():
        return {"error": f"CIEU DB missing at {CIEU_DB}"}, 2
    conn = sqlite3.connect(f"file:{CIEU_DB}?mode=ro", uri=True)
    rows = fetch_events(conn, WINDOW_SECONDS)
    candidates = detect_lock_deaths(rows)
    resolved = []
    unresolved = []
    for cand in candidates:
        rec = detect_recovery(rows, cand["ts"])
        entry = {**cand, "recovery": rec}
        (resolved if rec else unresolved).append(entry)
    verdict = "pass" if not unresolved else "fail"
    result = {
        "axis": "B2_lockdeath",
        "timestamp": int(time.time()),
        "window_seconds": WINDOW_SECONDS,
        "recovery_window_seconds": RECOVERY_WINDOW_SECONDS,
        "total_events_scanned": len(rows),
        "lock_death_candidates": len(candidates),
        "resolved_by_recovery": len(resolved),
        "unresolved_lockdeaths": len(unresolved),
        "unresolved_detail": unresolved[:5],
        "verdict": verdict,
    }
    out_path = REPORT_DIR / f"{int(time.time())}.json"
    out_path.write_text(json.dumps(result, indent=2, ensure_ascii=False))
    return result, (1 if verdict == "fail" else 0)


if __name__ == "__main__":
    result, rc = main()
    print(json.dumps(result, indent=2, ensure_ascii=False))
    sys.exit(rc)
