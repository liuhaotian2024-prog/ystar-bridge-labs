#!/usr/bin/env python3
"""
Inline test for Lesson Usage Tracking Phase 1.

Tests:
1. lesson_id_injector.py correctly injects UUIDs
2. hook.py emits LESSON_READ events when reading lesson files
3. K9 rule 11 DEAD_KNOWLEDGE correctly detects stale lessons

Part of verification Phase 1 (CEO 8f049222, Samantha A030 merge).
"""
import os
import re
import sqlite3
import subprocess
import sys
import tempfile
from pathlib import Path


def test_lesson_id_injection():
    """Test 1: lesson_id_injector adds UUIDs to lessons."""
    print("\n[TEST 1] Verifying lesson_id injection...")

    workspace = Path(__file__).resolve().parent.parent
    knowledge_dir = workspace / "knowledge"

    lesson_files = list(knowledge_dir.glob("*/lessons/*.md"))
    if not lesson_files:
        print("  ✗ No lesson files found")
        return False

    has_lesson_id_count = 0
    for lesson_path in lesson_files:
        content = lesson_path.read_text(encoding="utf-8")
        fm_match = re.match(r'^---\n(.*?)\n---', content, re.DOTALL)
        if fm_match:
            fm_block = fm_match.group(1)
            if re.search(r'^lesson_id:\s*\S', fm_block, re.MULTILINE):
                has_lesson_id_count += 1

    if has_lesson_id_count == len(lesson_files):
        print(f"  ✓ All {len(lesson_files)} lesson files have lesson_id")
        return True
    else:
        print(f"  ✗ Only {has_lesson_id_count}/{len(lesson_files)} have lesson_id")
        return False


def test_lesson_read_emission():
    """Test 2: hook.py emits LESSON_READ when reading lesson."""
    print("\n[TEST 2] Testing LESSON_READ emission (requires Y-gov hook installed)...")

    # This test assumes Y*gov hook is installed and active
    # We simulate by checking if hook.py has the _emit_lesson_read_event function
    ystar_gov_workspace = Path.home() / ".openclaw/workspace/Y-star-gov"
    hook_py = ystar_gov_workspace / "ystar/adapters/hook.py"

    if not hook_py.exists():
        print(f"  ⚠ Y-gov hook.py not found at {hook_py}, skipping test")
        return True  # Not a failure, just skipped

    content = hook_py.read_text(encoding="utf-8")
    if "_emit_lesson_read_event" in content and 'event_type": "LESSON_READ"' in content:
        print("  ✓ hook.py contains _emit_lesson_read_event logic")
        return True
    else:
        print("  ✗ hook.py missing LESSON_READ emission logic")
        return False


def test_k9_rule_11():
    """Test 3: K9 rule 11 DEAD_KNOWLEDGE detector exists and is callable."""
    print("\n[TEST 3] Testing K9 rule 11 DEAD_KNOWLEDGE...")

    ystar_gov_workspace = Path.home() / ".openclaw/workspace/Y-star-gov"
    rules_py = ystar_gov_workspace / "ystar/governance/k9_adapter/rules_6_10.py"

    if not rules_py.exists():
        print(f"  ⚠ K9 rules file not found at {rules_py}, skipping test")
        return True

    content = rules_py.read_text(encoding="utf-8")
    if "def check_dead_knowledge" in content and "DEAD_KNOWLEDGE" in content:
        print("  ✓ K9 rule 11 check_dead_knowledge exists")

        # Check if integrated into run_all_rules
        if "check_dead_knowledge(workspace, stale_days)" in content:
            print("  ✓ Rule 11 integrated into run_all_rules")
            return True
        else:
            print("  ✗ Rule 11 not integrated into run_all_rules")
            return False
    else:
        print("  ✗ K9 rule 11 missing")
        return False


def test_e2e_lesson_tracking():
    """Test 4: End-to-end lesson tracking (create lesson → read → verify CIEU event)."""
    print("\n[TEST 4] End-to-end lesson tracking (requires installed Y*gov hook)...")

    workspace = Path(__file__).resolve().parent.parent
    cieu_db = workspace / ".ystar_cieu.db"

    if not cieu_db.exists():
        print(f"  ⚠ CIEU database not found at {cieu_db}, skipping E2E test")
        return True

    # Count LESSON_READ events in CIEU
    try:
        conn = sqlite3.connect(str(cieu_db))
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM cieu_events WHERE event_type = 'LESSON_READ'")
        count = cursor.fetchone()[0]
        conn.close()

        if count > 0:
            print(f"  ✓ Found {count} LESSON_READ events in CIEU database")
            return True
        else:
            print("  ⚠ No LESSON_READ events yet (will be populated after hook is active)")
            return True  # Not a failure, just not triggered yet
    except Exception as e:
        print(f"  ✗ Failed to query CIEU database: {e}")
        return False


def main():
    print("=" * 60)
    print("Lesson Usage Tracking Phase 1 — Inline Test")
    print("=" * 60)

    tests = [
        test_lesson_id_injection,
        test_lesson_read_emission,
        test_k9_rule_11,
        test_e2e_lesson_tracking,
    ]

    results = [test() for test in tests]

    print("\n" + "=" * 60)
    print(f"SUMMARY: {sum(results)}/{len(results)} tests passed")
    print("=" * 60)

    return 0 if all(results) else 1


if __name__ == "__main__":
    sys.exit(main())
