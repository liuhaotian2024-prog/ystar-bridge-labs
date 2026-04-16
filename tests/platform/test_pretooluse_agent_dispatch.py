#!/usr/bin/env python3
"""
Test Suite — PreToolUse Agent Dispatch Validator

**Authority**: Platform Engineer Ryan Park per CEO directive CZL-136
**Spec**: scripts/hook_pretool_agent_dispatch.py + action_model_validator.py Phase A
**Coverage**: 5-step BOOT CONTEXT enforcement for Agent tool calls

Test cases:
1. Complete Phase A (5/5 steps) → allow
2. Missing step 1 (.czl_subgoals.json) → warn
3. Missing step 5 (k9_daemon check) → warn
4. Missing 3+ steps → warn with bitmap
5. Non-Agent tool call → allow (skip validator)
6. Invalid JSON payload → allow (skip validator)
"""

import sys
import json
import subprocess
from pathlib import Path


HOOK_SCRIPT = Path.home() / ".openclaw/workspace/ystar-company/scripts/hook_pretool_agent_dispatch.py"


def run_hook(payload: dict) -> dict:
    """Run hook script with JSON payload, return parsed result."""
    proc = subprocess.run(
        ["python3", str(HOOK_SCRIPT)],
        input=json.dumps(payload),
        capture_output=True,
        text=True
    )
    try:
        return json.loads(proc.stdout)
    except json.JSONDecodeError:
        return {"action": "error", "message": proc.stdout or proc.stderr}


def test_complete_phase_a():
    """Test 1: Complete Phase A (5/5 steps) → allow."""
    payload = {
        "tool": "Agent",
        "params": {
            "task": """
## BOOT CONTEXT (Phase A 5-step)
1. Read .czl_subgoals.json
2. Bash python3 precheck_existing.py component
3. Bash git log -5 --oneline
4. Bash python3 session_watchdog.py --statusline
5. Bash pgrep -fl k9_routing_subscriber

=== Task body ===
Do work...
"""
        }
    }

    result = run_hook(payload)
    assert result["action"] == "allow", f"Expected allow, got {result}"
    assert "11111" in result["message"], f"Expected 5/5 bitmap, got {result['message']}"
    print("✓ Test 1 PASS: Complete Phase A allows")


def test_missing_step1():
    """Test 2: Missing step 1 (.czl_subgoals.json) → warn."""
    payload = {
        "tool": "Agent",
        "params": {
            "task": """
## BOOT CONTEXT
2. Bash python3 precheck_existing.py component
3. Bash git log -5 --oneline
4. Bash python3 session_watchdog.py --statusline
5. Bash pgrep -fl k9_routing_subscriber
"""
        }
    }

    result = run_hook(payload)
    assert result["action"] == "allow", f"Expected allow (warn mode), got {result}"
    assert "WARN" in result["message"] or "step1" in result["message"].lower(), f"Expected warning, got {result['message']}"
    assert result["message"].count("0") == 1, f"Expected 1 missing step (bitmap 01111), got {result['message']}"
    print("✓ Test 2 PASS: Missing step1 warns")


def test_missing_step5():
    """Test 3: Missing step 5 (k9_daemon check) → warn."""
    payload = {
        "tool": "Agent",
        "params": {
            "task": """
1. Read .czl_subgoals.json
2. Bash python3 precheck_existing.py component
3. Bash git log -5 --oneline
4. Bash python3 session_watchdog.py --statusline
"""
        }
    }

    result = run_hook(payload)
    assert result["action"] == "allow", f"Expected allow (warn mode), got {result}"
    assert "WARN" in result["message"] or "step5" in result["message"].lower(), f"Expected warning, got {result['message']}"
    print("✓ Test 3 PASS: Missing step5 warns")


def test_missing_multiple_steps():
    """Test 4: Missing 3+ steps → warn with bitmap."""
    payload = {
        "tool": "Agent",
        "params": {
            "task": "Do work without BOOT CONTEXT..."
        }
    }

    result = run_hook(payload)
    assert result["action"] == "allow", f"Expected allow (warn mode), got {result}"
    assert "WARN" in result["message"], f"Expected warning, got {result['message']}"
    assert "00000" in result["message"], f"Expected 0/5 bitmap, got {result['message']}"
    print("✓ Test 4 PASS: Missing all steps warns with 00000 bitmap")


def test_non_agent_tool():
    """Test 5: Non-Agent tool call → allow (skip validator)."""
    payload = {
        "tool": "Bash",
        "params": {
            "command": "echo hello"
        }
    }

    result = run_hook(payload)
    assert result["action"] == "allow", f"Expected allow, got {result}"
    assert "not Agent" in result["message"] or "skip" in result["message"].lower(), f"Expected skip message, got {result['message']}"
    print("✓ Test 5 PASS: Non-Agent tool skips validator")


def test_invalid_json():
    """Test 6: Invalid JSON payload → allow (fail-open)."""
    proc = subprocess.run(
        ["python3", str(HOOK_SCRIPT)],
        input="not json{",
        capture_output=True,
        text=True
    )

    try:
        result = json.loads(proc.stdout)
        assert result["action"] == "allow", f"Expected allow on invalid JSON, got {result}"
        print("✓ Test 6 PASS: Invalid JSON allows (fail-open)")
    except json.JSONDecodeError:
        # Hook may output plain text on error — this is acceptable as long as exit code is 0
        assert proc.returncode == 0, f"Expected exit 0, got {proc.returncode}"
        print("✓ Test 6 PASS: Invalid JSON exits 0 (fail-open)")


def main():
    """Run all tests."""
    tests = [
        test_complete_phase_a,
        test_missing_step1,
        test_missing_step5,
        test_missing_multiple_steps,
        test_non_agent_tool,
        test_invalid_json
    ]

    for test_func in tests:
        try:
            test_func()
        except AssertionError as e:
            print(f"✗ {test_func.__name__} FAILED: {e}")
            return 1
        except Exception as e:
            print(f"✗ {test_func.__name__} ERROR: {e}")
            return 1

    print(f"\nAll {len(tests)} tests PASSED ✓")
    return 0


if __name__ == "__main__":
    sys.exit(main())
