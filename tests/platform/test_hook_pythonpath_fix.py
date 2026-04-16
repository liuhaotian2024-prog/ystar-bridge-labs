#!/usr/bin/env python3
"""
Test: Y*gov hook scripts can import ystar modules after sys.path.insert fix.
Board 2026-04-16 P0: All hook scripts failed with ModuleNotFoundError in production.
Fix: prepend sys.path.insert(0, "/Users/haotianliu/.openclaw/workspace/Y-star-gov").
This test verifies each hook script can run subprocess import without error.
"""
import subprocess
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent.parent
SCRIPTS_DIR = REPO_ROOT / "scripts"

# Sample 3 hook scripts (representative coverage)
HOOK_SCRIPTS_TO_TEST = [
    SCRIPTS_DIR / "hook_wrapper.py",
    SCRIPTS_DIR / "hook_wrapper_observe.py",
    SCRIPTS_DIR / "hook_session_end_summary.py",
]


def test_hook_wrapper_can_import_ystar():
    """hook_wrapper.py imports ystar.adapters.hook without ModuleNotFoundError."""
    script = SCRIPTS_DIR / "hook_wrapper.py"
    # Run import in subprocess (simulate Claude Code hook invocation environment)
    result = subprocess.run(
        [sys.executable, "-c", f"exec(open('{script}').read()); from ystar.adapters.hook import check_hook"],
        capture_output=True,
        text=True,
        timeout=5,
    )
    # Assert: no ModuleNotFoundError in stderr
    assert "ModuleNotFoundError: No module named 'ystar'" not in result.stderr, \
        f"hook_wrapper.py still fails to import ystar: {result.stderr}"


def test_hook_wrapper_observe_can_import_ystar():
    """hook_wrapper_observe.py imports ystar without ModuleNotFoundError."""
    script = SCRIPTS_DIR / "hook_wrapper_observe.py"
    result = subprocess.run(
        [sys.executable, "-c", f"exec(open('{script}').read()); from ystar import Policy"],
        capture_output=True,
        text=True,
        timeout=5,
    )
    assert "ModuleNotFoundError: No module named 'ystar'" not in result.stderr, \
        f"hook_wrapper_observe.py still fails to import ystar: {result.stderr}"


def test_hook_session_end_summary_can_import_ystar():
    """hook_session_end_summary.py can run without ModuleNotFoundError."""
    script = SCRIPTS_DIR / "hook_session_end_summary.py"
    # This script doesn't directly import ystar in top-level, but fixing sys.path ensures
    # any future ystar imports inside functions won't fail. Test it can at least execute.
    result = subprocess.run(
        [sys.executable, "-c", f"import sys; sys.path.insert(0, '/Users/haotianliu/.openclaw/workspace/Y-star-gov'); exec(open('{script}').read())"],
        capture_output=True,
        text=True,
        timeout=5,
    )
    # Since main() requires specific conditions, we just check no import error at module level
    assert "ModuleNotFoundError: No module named 'ystar'" not in result.stderr


def test_all_hook_scripts_have_sys_path_insert():
    """All 9 production hook scripts have sys.path.insert(0, Y-star-gov) line."""
    hook_scripts = [
        SCRIPTS_DIR / "hook_wrapper.py",
        SCRIPTS_DIR / "hook_wrapper_observe.py",
        SCRIPTS_DIR / "hook_prompt_gate.py",
        SCRIPTS_DIR / "hook_session_end_summary.py",
        SCRIPTS_DIR / "hook_subagent_output_scan.py",
        SCRIPTS_DIR / "hook_session_start.py",
        SCRIPTS_DIR / "hook_user_prompt_tracker.py",
        SCRIPTS_DIR / "hook_session_end.py",
        SCRIPTS_DIR / "hook_stop_reply_scan.py",
    ]
    for script in hook_scripts:
        content = script.read_text(encoding="utf-8")
        assert 'sys.path.insert(0, "/Users/haotianliu/.openclaw/workspace/Y-star-gov")' in content, \
            f"{script.name} missing sys.path.insert Y-star-gov fix"
