#!/usr/bin/env python3
"""
Evidence Aggregator — Automated CZL Enforcement Evidence Extraction
AMENDMENT-026, 2026-04-15

Queries .ystar_cieu.db for CZL (Canonical-Zero-Level) enforcement events,
generates classical structure report for whitepaper/sales demo.

Event types covered:
- FORGETGUARD_DENY: ForgetGuard blocked action
- CANONICAL_HASH_DRIFT: Canonical hash mismatch
- DEFER_IN_REPLY_DRIFT: Defer language in reply
- BACKLOG_DISGUISE_DRIFT: Backlog as defer disguise
- PROMPT_SUBGOAL_CHECK: Narrative coherence check
- SUBGOAL_COMPRESSED: Sub-goal compression event
- CAMPAIGN_STUB_REJECTED: Campaign stub rejected

Output format (classical structure):
1. Summary: high-level overview
2. Counts: event counts by type
3. Timeline: chronological event list
4. Sample: 2-3 representative events with full context
5. Reproducibility: how to re-run the query
"""

import sqlite3
import json
import sys
from pathlib import Path
from datetime import datetime
from typing import List, Dict, Any
from collections import Counter


# CZL enforcement event types
CZL_EVENT_TYPES = [
    "FORGETGUARD_DENY",
    "CANONICAL_HASH_DRIFT",
    "DEFER_IN_REPLY_DRIFT",
    "BACKLOG_DISGUISE_DRIFT",
    "PROMPT_SUBGOAL_CHECK",
    "SUBGOAL_COMPRESSED",
    "CAMPAIGN_STUB_REJECTED",
    "DEFER_LANGUAGE_DRIFT",
    "BOARD_CHOICE_QUESTION_DRIFT",
    "IMMUTABLE_FORGOT_BREAK_GLASS",
    "CEO_CODE_WRITE_DRIFT",
]


def connect_cieu_db() -> sqlite3.Connection:
    """Connect to .ystar_cieu.db"""
    db_path = Path.cwd() / ".ystar_cieu.db"
    if not db_path.exists():
        print(f"ERROR: CIEU DB not found at {db_path}", file=sys.stderr)
        sys.exit(1)
    return sqlite3.connect(str(db_path))


def query_czl_events(conn: sqlite3.Connection, event_types: List[str]) -> List[Dict[str, Any]]:
    """Query all CZL enforcement events"""
    placeholders = ", ".join("?" * len(event_types))
    query = f"""
        SELECT
            event_id, seq_global, created_at, session_id, agent_id, event_type,
            decision, passed, drift_detected, drift_details, drift_category,
            file_path, command, evidence_grade
        FROM cieu_events
        WHERE event_type IN ({placeholders})
        ORDER BY created_at DESC
    """

    cursor = conn.cursor()
    cursor.execute(query, event_types)

    events = []
    for row in cursor.fetchall():
        events.append({
            "event_id": row[0],
            "seq_global": row[1],
            "created_at": row[2],
            "session_id": row[3],
            "agent_id": row[4],
            "event_type": row[5],
            "decision": row[6],
            "passed": row[7],
            "drift_detected": row[8],
            "drift_details": row[9],
            "drift_category": row[10],
            "file_path": row[11],
            "command": row[12],
            "evidence_grade": row[13],
        })

    return events


def format_timestamp(ts: float) -> str:
    """Format UNIX timestamp to readable datetime"""
    return datetime.fromtimestamp(ts).strftime("%Y-%m-%d %H:%M:%S")


def generate_classical_report(events: List[Dict[str, Any]]) -> str:
    """Generate classical structure report"""
    if not events:
        return "No CZL enforcement events found in CIEU database.\n"

    # 1. Summary
    total_count = len(events)
    event_type_counts = Counter(e["event_type"] for e in events)
    session_count = len(set(e["session_id"] for e in events))

    summary = f"""# CZL Enforcement Evidence Report
Generated: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}

## Summary

Total CZL enforcement events: {total_count}
Unique sessions: {session_count}
Date range: {format_timestamp(events[-1]['created_at'])} to {format_timestamp(events[0]['created_at'])}

This report aggregates governance enforcement events from Y*gov's CIEU database,
demonstrating real-world runtime governance in action.

"""

    # 2. Counts
    counts = "## Event Counts by Type\n\n"
    counts += "| Event Type | Count | Description |\n"
    counts += "|------------|-------|-------------|\n"

    event_descriptions = {
        "FORGETGUARD_DENY": "ForgetGuard blocked action",
        "CANONICAL_HASH_DRIFT": "Canonical hash mismatch",
        "DEFER_IN_REPLY_DRIFT": "Defer language in reply",
        "BACKLOG_DISGUISE_DRIFT": "Backlog as defer disguise",
        "PROMPT_SUBGOAL_CHECK": "Narrative coherence check",
        "SUBGOAL_COMPRESSED": "Sub-goal compression",
        "CAMPAIGN_STUB_REJECTED": "Campaign stub rejected",
        "DEFER_LANGUAGE_DRIFT": "Defer language drift",
        "BOARD_CHOICE_QUESTION_DRIFT": "Choice question to Board",
        "IMMUTABLE_FORGOT_BREAK_GLASS": "Immutable file edit without break-glass",
        "CEO_CODE_WRITE_DRIFT": "CEO writing code",
    }

    for event_type, count in event_type_counts.most_common():
        desc = event_descriptions.get(event_type, "Unknown")
        counts += f"| `{event_type}` | {count} | {desc} |\n"

    counts += "\n"

    # 3. Timeline
    timeline = "## Timeline (Latest 20 Events)\n\n"
    timeline += "| Timestamp | Event Type | Agent | Session ID (last 8) |\n"
    timeline += "|-----------|------------|-------|---------------------|\n"

    for event in events[:20]:
        ts = format_timestamp(event["created_at"])
        event_type = event["event_type"]
        agent = event["agent_id"]
        session_id = event["session_id"][-8:] if event["session_id"] else "unknown"
        timeline += f"| {ts} | `{event_type}` | {agent} | {session_id} |\n"

    timeline += "\n"

    # 4. Sample
    sample = "## Representative Samples\n\n"
    sample += "### Sample 1: ForgetGuard Deny\n\n"

    forgetguard_events = [e for e in events if "FORGETGUARD" in e["event_type"] or "DRIFT" in e["event_type"]]
    if forgetguard_events:
        e = forgetguard_events[0]
        sample += f"**Event ID**: `{e['event_id']}`\n"
        sample += f"**Timestamp**: {format_timestamp(e['created_at'])}\n"
        sample += f"**Agent**: {e['agent_id']}\n"
        sample += f"**Event Type**: `{e['event_type']}`\n"
        sample += f"**Decision**: {e['decision']}\n"
        sample += f"**Drift Detected**: {bool(e['drift_detected'])}\n\n"

        if e["drift_details"]:
            try:
                details = json.loads(e["drift_details"])
                sample += "**Drift Details**:\n```json\n"
                sample += json.dumps(details, indent=2)
                sample += "\n```\n\n"
            except json.JSONDecodeError:
                sample += f"**Drift Details**: {e['drift_details']}\n\n"

        if e["file_path"]:
            sample += f"**File Path**: `{e['file_path']}`\n\n"
        if e["command"]:
            sample += f"**Command**: `{e['command']}`\n\n"

    # 5. Reproducibility
    repro = "## Reproducibility\n\n"
    repro += "To re-run this query:\n\n"
    repro += "```bash\n"
    repro += "python3 scripts/evidence_aggregator.py > reports/whitepaper/evidence_auto_$(date +%Y%m%d).md\n"
    repro += "```\n\n"
    repro += "Direct SQL query:\n\n"
    repro += "```sql\n"
    repro += "SELECT event_id, created_at, agent_id, event_type, decision\n"
    repro += "FROM cieu_events\n"
    repro += "WHERE event_type IN (\n"
    for i, et in enumerate(CZL_EVENT_TYPES):
        comma = "," if i < len(CZL_EVENT_TYPES) - 1 else ""
        repro += f"  '{et}'{comma}\n"
    repro += ")\n"
    repro += "ORDER BY created_at DESC;\n"
    repro += "```\n\n"

    return summary + counts + timeline + sample + repro


def main():
    """Main entry point"""
    conn = connect_cieu_db()
    events = query_czl_events(conn, CZL_EVENT_TYPES)
    conn.close()

    report = generate_classical_report(events)
    print(report)


if __name__ == "__main__":
    main()
