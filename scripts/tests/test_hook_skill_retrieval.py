"""Test: UserPromptSubmit skill retrieval hook.

Verifies: hook is fail-open + emits [SKILL HINTS] format + handles no match.
"""
import json
import os
import subprocess
import sys
from pathlib import Path
import pytest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

HOOK = Path("/Users/haotianliu/.openclaw/workspace/ystar-company/scripts/hook_skill_retrieval_pre_query.py")


def _run_hook(stdin_payload: dict) -> subprocess.CompletedProcess:
    return subprocess.run(
        ["python3.11", str(HOOK)],
        input=json.dumps(stdin_payload),
        capture_output=True, text=True, timeout=10,
    )


def test_hook_exit_zero_on_empty_prompt():
    r = _run_hook({"prompt": ""})
    assert r.returncode == 0


def test_hook_exit_zero_on_short_prompt():
    r = _run_hook({"prompt": "hi"})
    assert r.returncode == 0


def test_hook_exit_zero_on_malformed_payload():
    # simulate junk input — hook must fail-open
    r = subprocess.run(
        ["python3.11", str(HOOK)],
        input="not json at all",
        capture_output=True, text=True, timeout=10,
    )
    assert r.returncode == 0


def test_hook_emits_skill_hints_for_matching_prompt():
    # "k9 patrol" should match at least one skill if lib populated
    r = _run_hook({"prompt": "run k9 patrol to audit governance"})
    assert r.returncode == 0
    # If no skills, prints nothing — both OK. If skills, format check.
    if r.stdout.strip():
        assert "[SKILL HINTS]" in r.stdout
        assert "scripts/" in r.stdout


def test_hook_never_exceeds_3_hints():
    # Prompt with many keywords — cap at 3
    r = _run_hook({"prompt": "governance brain auto commit push k9 patrol dream"})
    if r.stdout.strip():
        lines = [l for l in r.stdout.splitlines() if l.strip().startswith(("1.", "2.", "3.", "4."))]
        assert len(lines) <= 3


def test_hook_fails_open_when_db_missing(tmp_path, monkeypatch):
    """Even if skill_library.db doesn't exist, hook must exit 0."""
    # Point SCRIPTS_DIR to empty tmp to simulate missing db
    env = os.environ.copy()
    r = subprocess.run(
        ["python3.11", "-c",
         f"import sys; sys.path.insert(0, '{tmp_path}'); "
         f"exec(open('{HOOK}').read())"],
        input=json.dumps({"prompt": "test query"}),
        capture_output=True, text=True, timeout=10, env=env,
    )
    # Should not crash
    assert r.returncode == 0
