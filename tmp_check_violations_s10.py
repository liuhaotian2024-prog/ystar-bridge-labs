#!/usr/bin/env python3
"""Quick violations analysis for Session 10."""
import sqlite3
from datetime import datetime, timedelta

db_path = '.ystar_cieu_omission.db'
conn = sqlite3.connect(db_path)
c = conn.cursor()

print("=" * 60)
print("VIOLATIONS ANALYSIS — Session 10")
print("=" * 60)

# Total violations
total = c.execute("SELECT COUNT(*) FROM cieu_events").fetchone()[0]
print(f"\nTotal violations in DB: {total}")

# Check acknowledgement events
ack_count = c.execute(
    "SELECT COUNT(*) FROM governance_events WHERE event_type='acknowledgement'"
).fetchone()[0]
print(f"Acknowledgement events: {ack_count}")

# Time range
earliest = c.execute("SELECT MIN(timestamp) FROM cieu_events").fetchone()[0]
latest = c.execute("SELECT MAX(timestamp) FROM cieu_events").fetchone()[0]
print(f"Time range: {earliest} → {latest}")

# Violations by type (all time)
print("\n" + "=" * 60)
print("TOP VIOLATION TYPES (all time)")
print("=" * 60)
violations = c.execute("""
    SELECT violation_type, COUNT(*) as cnt
    FROM cieu_events
    GROUP BY violation_type
    ORDER BY cnt DESC
    LIMIT 10
""").fetchall()
for vtype, cnt in violations:
    print(f"  {cnt:5d}  {vtype}")

# Violations by agent (all time)
print("\n" + "=" * 60)
print("TOP VIOLATORS (all time)")
print("=" * 60)
agents = c.execute("""
    SELECT agent_id, COUNT(*) as cnt
    FROM cieu_events
    GROUP BY agent_id
    ORDER BY cnt DESC
    LIMIT 10
""").fetchall()
for agent, cnt in agents:
    print(f"  {cnt:5d}  {agent}")

# Recent violations (last 4 hours)
print("\n" + "=" * 60)
print("RECENT VIOLATIONS (last 4 hours)")
print("=" * 60)
recent = c.execute("""
    SELECT COUNT(*) FROM cieu_events
    WHERE timestamp > datetime('now', '-4 hours')
""").fetchone()[0]
print(f"Total: {recent}")

recent_types = c.execute("""
    SELECT violation_type, COUNT(*) as cnt
    FROM cieu_events
    WHERE timestamp > datetime('now', '-4 hours')
    GROUP BY violation_type
    ORDER BY cnt DESC
    LIMIT 5
""").fetchall()
print("\nBy type:")
for vtype, cnt in recent_types:
    print(f"  {cnt:5d}  {vtype}")

# Check if generic 'agent' ID still being used
generic_count = c.execute("""
    SELECT COUNT(*) FROM cieu_events WHERE agent_id = 'agent'
""").fetchone()[0]
print(f"\n⚠️  Generic 'agent' ID violations: {generic_count}")

# Sample recent violations
print("\n" + "=" * 60)
print("SAMPLE RECENT VIOLATIONS (last 10)")
print("=" * 60)
samples = c.execute("""
    SELECT timestamp, agent_id, violation_type
    FROM cieu_events
    ORDER BY timestamp DESC
    LIMIT 10
""").fetchall()
for ts, agent, vtype in samples:
    print(f"  {ts}  [{agent:20s}]  {vtype}")

conn.close()
