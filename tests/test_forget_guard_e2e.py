#!/usr/bin/env python3
"""
[L3 TESTED] E2E tests for ForgetGuard engine
Tests all 4 bugs fixed in A021 EXP 4 deep test
"""

import json
import subprocess
import sys
from pathlib import Path

WORKSPACE_ROOT = Path(__file__).parent.parent


def test_forget_guard_summary_no_sql_error():
    """Bug 1: forget_guard_summary.py should not crash on missing rule_id column"""
    result = subprocess.run(
        ["python3", str(WORKSPACE_ROOT / "scripts/forget_guard_summary.py")],
        capture_output=True,
        text=True,
        timeout=5
    )

    # Should not have SQL error in stderr
    assert "no such column: rule_id" not in result.stderr.lower(), \
        f"SQL error still present: {result.stderr}"

    # Should exit 0 (fail-open)
    assert result.returncode == 0, f"Non-zero exit code: {result.returncode}"

    print("✓ Bug 1 PASS: forget_guard_summary.py SQL query fixed")


def test_forget_guard_flat_schema():
    """Bug 2: forget_guard.py should accept flat PreToolUse payload schema"""
    payload_flat = {
        "tool": "Bash",
        "command": "git commit -m 'fix明日'"
    }

    result = subprocess.run(
        ["python3", str(WORKSPACE_ROOT / "scripts/forget_guard.py")],
        input=json.dumps(payload_flat),
        capture_output=True,
        text=True,
        timeout=5
    )

    # Should emit defer warning
    assert "defer_language_in_commit_msg" in result.stderr, \
        f"Did not detect defer language in flat schema: {result.stderr}"

    print("✓ Bug 2a PASS: forget_guard.py accepts flat schema")


def test_forget_guard_nested_schema():
    """Bug 2: forget_guard.py should accept nested tool_input schema"""
    payload_nested = {
        "tool_name": "Bash",
        "tool_input": {
            "command": "git commit -m 'queued for tomorrow'"
        }
    }

    result = subprocess.run(
        ["python3", str(WORKSPACE_ROOT / "scripts/forget_guard.py")],
        input=json.dumps(payload_nested),
        capture_output=True,
        text=True,
        timeout=5
    )

    # Should emit defer warning
    assert "defer_language_in_commit_msg" in result.stderr, \
        f"Did not detect defer language in nested schema: {result.stderr}"

    print("✓ Bug 2b PASS: forget_guard.py accepts nested schema")


def test_forget_guard_defer_in_echo():
    """Bug 3: New rule should detect defer language in echo commands"""
    payload = {
        "tool": "Bash",
        "command": "echo '明早fix'"
    }

    result = subprocess.run(
        ["python3", str(WORKSPACE_ROOT / "scripts/forget_guard.py")],
        input=json.dumps(payload),
        capture_output=True,
        text=True,
        timeout=5
    )

    # Should emit defer warning
    assert "defer_language_in_echo" in result.stderr or "DEFER_IN_BASH_DRIFT" in result.stderr, \
        f"Did not detect defer language in echo: {result.stderr}"

    print("✓ Bug 3 PASS: forget_guard_rules.yaml extended with defer detection")


def test_wire_integrity_no_false_positive():
    """Bug 4: wire_integrity_check should not report false positives for registered hooks"""
    result = subprocess.run(
        ["python3", str(WORKSPACE_ROOT / "scripts/wire_integrity_check.py")],
        capture_output=True,
        text=True,
        timeout=5
    )

    # Should NOT report hook_user_prompt_tracker.py as missing (it's registered)
    assert "hook_user_prompt_tracker.py not registered" not in result.stderr, \
        f"False positive for hook_user_prompt_tracker.py: {result.stderr}"

    # Should exit 0 (fail-open)
    assert result.returncode == 0, f"Non-zero exit code: {result.returncode}"

    print("✓ Bug 4 PASS: wire_integrity_check.py uses precise basename matching")


if __name__ == "__main__":
    try:
        test_forget_guard_summary_no_sql_error()
        test_forget_guard_flat_schema()
        test_forget_guard_nested_schema()
        test_forget_guard_defer_in_echo()
        test_wire_integrity_no_false_positive()

        print("\n" + "=" * 70)
        print("ALL 4 BUGS FIXED — E2E TEST PASS")
        print("=" * 70)
        sys.exit(0)

    except AssertionError as e:
        print(f"\n✗ TEST FAILED: {e}", file=sys.stderr)
        sys.exit(1)
    except Exception as e:
        print(f"\n✗ UNEXPECTED ERROR: {e}", file=sys.stderr)
        sys.exit(1)
