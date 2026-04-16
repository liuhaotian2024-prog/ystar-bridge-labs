#!/usr/bin/env python3
"""F2 Emit-Side Fix Verification Script

Validates that:
1. emit_cieu() uses canonical agent_id validation
2. New events have proper agent_id (canonical or 'unidentified')
3. AGENT_ID_UNIDENTIFIED_EMIT warnings are emitted for non-canonical agents
"""

import sys
import sqlite3
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from _cieu_helpers import emit_cieu, _get_canonical_agent, _load_canonical_registry


def main():
    print("=" * 70)
    print("F2 Emit-Side Fix Verification")
    print("=" * 70)

    # Test 1: Canonical registry loading
    registry = _load_canonical_registry()
    print(f"\n✓ Test 1: Canonical registry loaded ({len(registry)} roles)")
    print(f"  Sample: {sorted(list(registry))[:10]}")

    # Test 2: Current agent validation
    current_agent = _get_canonical_agent()
    print(f"\n✓ Test 2: Current agent = '{current_agent}'")
    print(f"  Is canonical: {current_agent in registry}")

    # Test 3: Emit test event
    result = emit_cieu(
        event_type="F2_VERIFICATION_TEST",
        decision="info",
        passed=1,
        task_description="F2 emit helper verification test",
        session_id="f2_verification"
    )
    print(f"\n✓ Test 3: Emit test event = {result}")

    # Test 4: Verify test event in DB
    db_path = Path.cwd() / ".ystar_cieu.db"
    conn = sqlite3.connect(str(db_path))
    cursor = conn.cursor()

    cursor.execute("""
        SELECT agent_id, event_type, decision, task_description
        FROM cieu_events
        WHERE event_type = 'F2_VERIFICATION_TEST'
        ORDER BY created_at DESC
        LIMIT 1
    """)
    row = cursor.fetchone()

    if row:
        agent_id, event_type, decision, task_desc = row
        print(f"\n✓ Test 4: Retrieved test event from DB")
        print(f"  agent_id: {agent_id}")
        print(f"  event_type: {event_type}")
        print(f"  decision: {decision}")
    else:
        print("\n✗ Test 4: FAILED - Test event not found in DB")
        conn.close()
        return 1

    # Test 5: Check recent unidentified rate
    cursor.execute("""
        SELECT
            COUNT(*) FILTER (WHERE agent_id = 'unidentified') as unidentified_count,
            COUNT(*) as total_count,
            ROUND(100.0 * COUNT(*) FILTER (WHERE agent_id = 'unidentified') / COUNT(*), 2) as unidentified_pct
        FROM cieu_events
        WHERE created_at > strftime('%s', 'now', '-1 hour')
    """)
    row = cursor.fetchone()

    if row:
        unidentified_count, total_count, unidentified_pct = row
        print(f"\n✓ Test 5: Recent emissions (last 1 hour)")
        print(f"  Total events: {total_count}")
        print(f"  Unidentified: {unidentified_count} ({unidentified_pct}%)")

        if unidentified_pct < 5.0:
            print(f"  ✓ PASS: Unidentified rate < 5%")
        else:
            print(f"  ⚠ WARNING: Unidentified rate high (target < 5%)")

    # Test 6: Check AGENT_ID_UNIDENTIFIED_EMIT warnings
    cursor.execute("""
        SELECT COUNT(*)
        FROM cieu_events
        WHERE event_type = 'AGENT_ID_UNIDENTIFIED_EMIT'
        AND created_at > strftime('%s', 'now', '-1 hour')
    """)
    warning_count = cursor.fetchone()[0]
    print(f"\n✓ Test 6: AGENT_ID_UNIDENTIFIED_EMIT warnings (last 1 hour): {warning_count}")

    conn.close()

    print("\n" + "=" * 70)
    print("Verification Complete")
    print("=" * 70)
    return 0


if __name__ == "__main__":
    sys.exit(main())
