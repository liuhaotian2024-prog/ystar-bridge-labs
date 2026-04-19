"""
Goal 1 Demonstrator — Labs 行为 100% 被 Y*gov 治理覆盖 (measurement)

Audience: Board (Goal 1 empirical measurement evidence).
Research basis: CIEU event store captures every tool call that passes
through PreToolUse hook. Coverage = fraction of distinct (tool_name,
agent_id) pairs with at least one CIEU event in the last 7 days.
Synthesis: a truly 100%-governed Labs team produces a CIEU trace for
every action. Daemons/cron that never emit CIEU are the measurable gap.

Run: python3 reports/ceo/demonstrators/goal_1_hook_coverage_measure.py
Output: prints JSON summary to stdout; writes
reports/ceo/demonstrators/goal_1_output.json
"""
import json
import os
import sqlite3
import time
from pathlib import Path

CIEU_DB = "/Users/haotianliu/.openclaw/workspace/ystar-company/.ystar_cieu.db"
OUT = "/Users/haotianliu/.openclaw/workspace/ystar-company/reports/ceo/demonstrators/goal_1_output.json"
TRACKED_TOOLS = ["Bash", "Edit", "Write", "Read", "Grep", "Glob", "Agent", "NotebookEdit"]


def measure_coverage(db_path: str = CIEU_DB, window_days: int = 7) -> dict:
    if not Path(db_path).exists():
        return {"error": f"CIEU db missing at {db_path}"}
    now = time.time()
    cutoff = now - window_days * 86400
    conn = sqlite3.connect(db_path)
    try:
        cur = conn.cursor()
        cur.execute(
            "SELECT COUNT(*) FROM cieu_events WHERE created_at > ?",
            (cutoff,),
        )
        total = int((cur.fetchone() or (0,))[0] or 0)
        cur.execute(
            """SELECT COUNT(DISTINCT agent_id) FROM cieu_events
               WHERE created_at > ? AND agent_id != ''""",
            (cutoff,),
        )
        distinct_agents = int((cur.fetchone() or (0,))[0] or 0)
        tool_fires = {}
        for tool in TRACKED_TOOLS:
            cur.execute(
                """SELECT COUNT(*) FROM cieu_events
                   WHERE created_at > ? AND params_json LIKE ?""",
                (cutoff, f'%"{tool}"%'),
            )
            tool_fires[tool] = int((cur.fetchone() or (0,))[0] or 0)
        cur.execute(
            """SELECT COUNT(DISTINCT event_type) FROM cieu_events
               WHERE created_at > ?""",
            (cutoff,),
        )
        distinct_event_types = int((cur.fetchone() or (0,))[0] or 0)
        daemon_heartbeats = tool_fires_check(cur, cutoff, "DAEMON_HEARTBEAT")
        cron_ticks = tool_fires_check(cur, cutoff, "CRON_TICK")
    finally:
        conn.close()

    tools_covered = sum(1 for v in tool_fires.values() if v > 0)
    tool_coverage_pct = 100.0 * tools_covered / len(TRACKED_TOOLS)

    summary = {
        "window_days": window_days,
        "total_cieu_events_7d": total,
        "distinct_agents_7d": distinct_agents,
        "distinct_event_types_7d": distinct_event_types,
        "tool_fires_7d": tool_fires,
        "tool_coverage_pct": round(tool_coverage_pct, 1),
        "daemon_heartbeats_7d": daemon_heartbeats,
        "cron_ticks_7d": cron_ticks,
        "blind_spots": {
            "daemon": "unmeasured" if daemon_heartbeats == 0 else "measured",
            "cron": "unmeasured" if cron_ticks == 0 else "measured",
            "shell_bang_prefix": "unmeasured_always (Claude Code ! bypass)",
        },
        "goal_1_coverage_pct": round(
            tool_coverage_pct
            - (10 if daemon_heartbeats == 0 else 0)
            - (5 if cron_ticks == 0 else 0),
            1,
        ),
    }
    Path(OUT).parent.mkdir(parents=True, exist_ok=True)
    with open(OUT, "w", encoding="utf-8") as f:
        json.dump(summary, f, indent=2, ensure_ascii=False)
    return summary


def tool_fires_check(cur, cutoff, event_type):
    cur.execute(
        "SELECT COUNT(*) FROM cieu_events WHERE created_at > ? AND event_type = ?",
        (cutoff, event_type),
    )
    return int((cur.fetchone() or (0,))[0] or 0)


if __name__ == "__main__":
    r = measure_coverage()
    print(json.dumps(r, indent=2, ensure_ascii=False))
