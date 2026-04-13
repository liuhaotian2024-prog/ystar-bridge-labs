#!/usr/bin/env python3
"""Test semantic matcher against recent CEO events to measure OFF_TARGET false-positive rate."""

import json
import sqlite3
import sys
from pathlib import Path

# Import from ceo_heartbeat
sys.path.insert(0, str(Path(__file__).resolve().parent))
from ceo_heartbeat import (
    CIEU_DB_PATH,
    PRIORITY_BRIEF_PATH,
    parse_priority_brief_targets,
    _semantic_match,
)


def get_recent_ceo_events(limit: int = 200):
    """Get recent CEO work events (filtered for governance noise)."""
    if not CIEU_DB_PATH.exists():
        return []

    # Governance noise event types to ignore
    NOISE_EVENT_TYPES = {
        "omission_violation:task_completion_report",
        "omission_violation:progress_update",
        "omission_violation:directive_acknowledgement",
        "omission_violation:intent_declaration",
        "omission_violation:required_acknowledgement_omission",
        "intervention_pulse:soft_pulse",
        "intervention_pulse:interrupt_gate",
        "BEHAVIOR_RULE_VIOLATION",
        "DRIFT_DETECTED",
        "CEO_SELF_LOCK_WARNING",
        "CEO_HEARTBEAT_IDLE",
        "CEO_HEARTBEAT_OFF_TARGET",
        "OFF_TARGET_WARNING",
        "TWIN_EVOLUTION",
        "INTENT_ADJUSTED",
    }

    conn = sqlite3.connect(str(CIEU_DB_PATH))
    cursor = conn.cursor()

    # Get more events to allow for filtering
    cursor.execute("""
        SELECT event_type, task_description, command, file_path, created_at
        FROM cieu_events
        WHERE agent_id = 'ceo'
        ORDER BY created_at DESC
        LIMIT ?
    """, (limit * 10,))  # Get 10x to account for heavy filtering

    all_events = cursor.fetchall()
    conn.close()

    # Filter out governance noise
    work_events = []
    for event_type, task_desc, command, file_path, created_at in all_events:
        # Skip pure governance noise events
        if event_type in NOISE_EVENT_TYPES:
            continue

        # Require either a meaningful task_description, command, or file_path
        if not task_desc and not command and not file_path:
            continue

        work_events.append((event_type, task_desc, command, file_path, created_at))

        # Stop after collecting desired limit
        if len(work_events) >= limit:
            break

    return work_events


def test_matcher(dry_run: bool = True):
    """Test semantic matcher against recent CEO events."""
    print("Testing semantic matcher against recent CEO events...")
    print("=" * 80)

    # Parse current targets
    brief = parse_priority_brief_targets()
    targets = [t for t in brief.get("today_targets", [])]

    if not targets:
        print("ERROR: No targets found in priority_brief.md")
        return

    print(f"\nTargets from priority_brief.md ({len(targets)}):")
    for i, target in enumerate(targets, 1):
        print(f"  {i}. {target[:100]}")

    # Get recent CEO events
    events = get_recent_ceo_events(200)
    if not events:
        print("\nERROR: No CEO events found in CIEU database")
        return

    print(f"\nTesting against {len(events)} recent CEO events...")
    print("-" * 80)

    # Test each event
    on_target_count = 0
    off_target_count = 0

    for event_type, task_desc, command, file_path, created_at in events:
        # Build action text from available fields (same logic as heartbeat.py)
        parts = []
        if event_type:
            parts.append(event_type)
        if task_desc:
            parts.append(task_desc)
        if command:
            # Filter out pure inspection commands
            if command and not any(cmd in command for cmd in ["ls ", "cat ", "head ", "tail ", "grep "]):
                parts.append(command)
        if file_path:
            from pathlib import Path
            parts.append(Path(file_path).name)

        if not parts:
            continue

        action_text = " | ".join(parts)

        # Use threshold=0.4 to match heartbeat.py
        matches = _semantic_match(action_text, targets, threshold=0.4, dry_run=False)

        if matches:
            on_target_count += 1
            status = "✓ ON-TARGET"
        else:
            off_target_count += 1
            status = "✗ OFF-TARGET"

        if dry_run:
            print(f"\n{status} | {created_at}")
            print(f"  Action: {action_text[:120]}")
            # Re-run with dry_run=True to show scores
            _semantic_match(action_text, targets, threshold=0.4, dry_run=True)

    # Summary
    total = len(events)
    off_target_rate = (off_target_count / total * 100) if total > 0 else 0

    print("\n" + "=" * 80)
    print("SUMMARY")
    print("=" * 80)
    print(f"Total events tested:  {total}")
    print(f"ON-TARGET:            {on_target_count} ({on_target_count/total*100:.1f}%)")
    print(f"OFF-TARGET:           {off_target_count} ({off_target_rate:.1f}%)")
    print("")

    if off_target_rate < 10:
        print("✓ PASS: OFF_TARGET rate < 10%")
    elif off_target_rate < 20:
        print("⚠ MARGINAL: OFF_TARGET rate 10-20%, consider tuning threshold")
    else:
        print("✗ FAIL: OFF_TARGET rate > 20%, matcher needs improvement")

    return {
        "total": total,
        "on_target": on_target_count,
        "off_target": off_target_count,
        "off_target_rate": off_target_rate,
    }


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="Test heartbeat semantic matcher")
    parser.add_argument("--verbose", action="store_true", help="Show detailed scores per event")
    args = parser.parse_args()

    result = test_matcher(dry_run=args.verbose)
    sys.exit(0 if result and result["off_target_rate"] < 20 else 1)
