#!/usr/bin/env python3
"""
E2E test for W10.1: defer_language multi-keyword AND logic
AMENDMENT-026, 2026-04-15

Tests that schedule expressions (time_word only) are allowed,
but time_word + defer_verb co-occurrence is denied.
"""

import json
import subprocess
import sys
from pathlib import Path

# Test cases: 3 allow + 3 deny
TEST_CASES = [
    # Allow: schedule expressions (time_word without defer_verb)
    {
        "name": "allow_schedule_morning_report",
        "tool": "Write",
        "file_path": "reports/test.md",
        "content": "明天 6:00 晨报",
        "expected_action": "allow",
    },
    {
        "name": "allow_schedule_launch_deadline",
        "tool": "Write",
        "file_path": "reports/test.md",
        "content": "下周一 launch",
        "expected_action": "allow",
    },
    {
        "name": "allow_schedule_date_eod",
        "tool": "Write",
        "file_path": "reports/test.md",
        "content": "2026-04-20 EOD 交付",
        "expected_action": "allow",
    },
    # Deny: defer expressions (time_word + defer_verb co-occurrence)
    {
        "name": "deny_defer_tomorrow_continue",
        "tool": "Write",
        "file_path": "reports/test.md",
        "content": "明日继续",
        "expected_action": "deny",
    },
    {
        "name": "deny_defer_next_week_later",
        "tool": "Write",
        "file_path": "reports/test.md",
        "content": "下周再说",
        "expected_action": "deny",
    },
    {
        "name": "deny_defer_tomorrow_fix",
        "tool": "Write",
        "file_path": "reports/test.md",
        "content": "明天再补这个 bug",
        "expected_action": "deny",
    },
]


def run_forget_guard(payload: dict) -> dict:
    """Run forget_guard.py with payload, return JSON result"""
    script_path = Path.cwd() / "scripts" / "forget_guard.py"
    payload_json = json.dumps(payload)

    result = subprocess.run(
        ["python3", str(script_path)],
        input=payload_json,
        capture_output=True,
        text=True,
    )

    # Parse stdout (JSON result)
    try:
        return json.loads(result.stdout)
    except json.JSONDecodeError:
        print(f"[ERROR] Failed to parse forget_guard output: {result.stdout}", file=sys.stderr)
        print(f"[ERROR] stderr: {result.stderr}", file=sys.stderr)
        return {"action": "unknown", "rules_triggered": []}


def main():
    """Run all test cases and report results"""
    passed = 0
    failed = 0

    print("=" * 70)
    print("W10.1 Multi-Keyword AND Logic E2E Test")
    print("=" * 70)

    for case in TEST_CASES:
        payload = {
            "tool": case["tool"],
            "file_path": case.get("file_path", ""),
            "content": case.get("content", ""),
        }

        result = run_forget_guard(payload)
        actual_action = result.get("action", "unknown")
        expected_action = case["expected_action"]

        if actual_action == expected_action:
            print(f"✅ PASS: {case['name']}")
            print(f"   Content: {case['content']}")
            print(f"   Action: {actual_action}")
            passed += 1
        else:
            print(f"❌ FAIL: {case['name']}")
            print(f"   Content: {case['content']}")
            print(f"   Expected: {expected_action}, Got: {actual_action}")
            print(f"   Rules triggered: {result.get('rules_triggered', [])}")
            failed += 1
        print()

    print("=" * 70)
    print(f"Results: {passed} passed, {failed} failed")
    print("=" * 70)

    sys.exit(0 if failed == 0 else 1)


if __name__ == "__main__":
    main()
