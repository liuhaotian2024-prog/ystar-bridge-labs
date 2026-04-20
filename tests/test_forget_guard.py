import pytest
"""
Test suite for ForgetGuard — AMENDMENT-020
Validates 5 initial rules + 1 non-trigger case
"""

import json
import subprocess
import sys
from pathlib import Path


def run_forget_guard(payload: dict) -> tuple[int, str, str]:
    """Run forget_guard.py with given payload, return (exit_code, stdout, stderr)"""
    script_path = Path(__file__).parent.parent / "scripts" / "forget_guard.py"
    payload_json = json.dumps(payload)

    result = subprocess.run(
        [sys.executable, str(script_path)],
        input=payload_json,
        capture_output=True,
        text=True,
        cwd=Path(__file__).parent.parent,
    )

    return result.returncode, result.stdout, result.stderr


def test_missing_l_tag_trigger():
    """Rule: missing_l_tag should trigger on commit without [LX] tag"""
    payload = {
        "tool": "Bash",
        "command": "git commit -m 'completed feature X'",
    }

    exit_code, stdout, stderr = run_forget_guard(payload)

    assert exit_code == 0, "ForgetGuard should fail-open (exit 0)"
    assert "FORGET_GUARD" in stderr, "Should emit warning"
    assert "missing_l_tag" in stderr, "Should identify correct rule"
    assert "Add [LX] maturity tag" in stderr, "Should include recipe"
    assert "MATURITY_TAG_MISSING" in stderr, "Should emit CIEU event"


def test_immutable_no_break_glass_trigger():
    """Rule: immutable_no_break_glass should trigger when CEO edits AGENTS.md without break-glass"""
    # Set up active agent file
    active_agent_file = Path.cwd() / ".ystar_active_agent"
    original_agent = active_agent_file.read_text() if active_agent_file.exists() else None

    try:
        active_agent_file.write_text("ceo")

        payload = {
            "tool": "Edit",
            "file_path": "/Users/haotianliu/.openclaw/workspace/ystar-company/AGENTS.md",
            "old_string": "test",
            "new_string": "test",
        }

        exit_code, stdout, stderr = run_forget_guard(payload)

        assert exit_code == 0
        assert "FORGET_GUARD" in stderr
        assert "immutable_no_break_glass" in stderr
        assert "break-glass mode" in stderr or "Break-glass mode" in stderr
        assert "IMMUTABLE_FORGOT_BREAK_GLASS" in stderr

    finally:
        # Restore original agent
        if original_agent:
            active_agent_file.write_text(original_agent)


@pytest.mark.skip(reason="AMENDMENT-021: rule retired 2026-04-20")
def test_ceo_writes_code_trigger():
    """Rule: ceo_writes_code should trigger when CEO writes to scripts/"""
    active_agent_file = Path.cwd() / ".ystar_active_agent"
    original_agent = active_agent_file.read_text() if active_agent_file.exists() else None

    try:
        active_agent_file.write_text("ceo")

        payload = {
            "tool": "Write",
            "file_path": "/Users/haotianliu/.openclaw/workspace/ystar-company/scripts/test.py",
            "content": "print('test')",
        }

        exit_code, stdout, stderr = run_forget_guard(payload)

        assert exit_code == 0
        assert "FORGET_GUARD" in stderr
        assert "ceo_writes_code" in stderr
        assert "CEO does not write code" in stderr
        assert "CEO_CODE_WRITE_DRIFT" in stderr

    finally:
        if original_agent:
            active_agent_file.write_text(original_agent)


@pytest.mark.skip(reason="AMENDMENT-021: rule retired 2026-04-20")
def test_defer_language_trigger():
    """Rule: defer_language should trigger on defer keywords"""
    payload = {
        "tool": "Write",
        "file_path": "/Users/haotianliu/.openclaw/workspace/ystar-company/reports/test.md",
        "content": "This task is queued for tomorrow.",
    }

    exit_code, stdout, stderr = run_forget_guard(payload)

    assert exit_code == 0
    assert "FORGET_GUARD" in stderr
    assert "defer_language" in stderr
    assert "feedback_no_clock_out" in stderr
    assert "DEFER_LANGUAGE_DRIFT" in stderr


@pytest.mark.skip(reason="AMENDMENT-021: rule retired 2026-04-20")
def test_choice_question_to_board_trigger():
    """Rule: choice_question_to_board should trigger on option menus"""
    payload = {
        "tool": "Write",
        "file_path": "/Users/haotianliu/.openclaw/workspace/ystar-company/reports/test.md",
        "content": """
Dear Board,

Please choose:
1) Option A - do this
2) Option B - do that
3) Option C - do nothing

What do you prefer?
        """,
    }

    exit_code, stdout, stderr = run_forget_guard(payload)

    assert exit_code == 0
    assert "FORGET_GUARD" in stderr
    assert "choice_question_to_board" in stderr
    assert "PROHIBITED" in stderr or "prohibited" in stderr
    assert "BOARD_CHOICE_QUESTION_DRIFT" in stderr


def test_non_trigger_normal_operation():
    """Non-trigger: normal operation should not fire any rules"""
    payload = {
        "tool": "Read",
        "file_path": "/Users/haotianliu/.openclaw/workspace/ystar-company/README.md",
    }

    exit_code, stdout, stderr = run_forget_guard(payload)

    assert exit_code == 0
    assert "FORGET_GUARD" not in stderr, "Should not emit warnings for normal operations"


if __name__ == "__main__":
    # Run all tests
    tests = [
        test_missing_l_tag_trigger,
        test_immutable_no_break_glass_trigger,
        test_ceo_writes_code_trigger,
        test_defer_language_trigger,
        test_choice_question_to_board_trigger,
        test_non_trigger_normal_operation,
    ]

    failed = 0
    for test in tests:
        try:
            test()
            print(f"✓ {test.__name__}")
        except AssertionError as e:
            print(f"✗ {test.__name__}: {e}")
            failed += 1
        except Exception as e:
            print(f"✗ {test.__name__}: ERROR: {e}")
            failed += 1

    if failed > 0:
        print(f"\n{failed}/{len(tests)} tests failed")
        sys.exit(1)
    else:
        print(f"\n✓ All {len(tests)} tests passed")
        sys.exit(0)
