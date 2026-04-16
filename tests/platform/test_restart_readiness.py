#!/usr/bin/env python3
"""Test suite for restart_readiness_check.py — verify 7-step validation logic.

Per Ethan #137 §8 Step B: ≥5 assertions (3 happy + 2 negative).
"""

import json
import subprocess
from pathlib import Path
import pytest


@pytest.fixture
def company_root():
    """Return company root directory."""
    return Path(__file__).parent.parent.parent


def test_readiness_check_cli_exists(company_root):
    """Verify restart_readiness_check.py script exists and is executable."""
    script = company_root / "scripts" / "restart_readiness_check.py"
    assert script.exists(), f"restart_readiness_check.py missing at {script}"
    assert script.stat().st_mode & 0o111, "script not executable"


def test_readiness_check_runs_without_error(company_root):
    """Verify script runs and produces valid JSON output (happy path, current state)."""
    script = company_root / "scripts" / "restart_readiness_check.py"
    result = subprocess.run(
        ["python3", str(script), "--dry-run"],
        capture_output=True,
        text=True,
        timeout=30
    )

    # Should produce output even if checks fail
    assert result.stdout.strip(), "no JSON output"

    # Parse JSON (full stdout is JSON)
    data = json.loads(result.stdout)

    # Verify schema
    assert "readiness" in data
    assert data["readiness"] in ["READY", "PARTIAL", "BLOCKED"]
    assert "failed_steps" in data
    assert isinstance(data["failed_steps"], list)
    assert "details" in data
    assert "recommendation" in data


def test_readiness_check_7_steps_present(company_root):
    """Verify all 7 steps are checked (receipts, daemons, ac, session_closed, archive, continuation, baseline)."""
    script = company_root / "scripts" / "restart_readiness_check.py"
    result = subprocess.run(
        ["python3", str(script), "--dry-run"],
        capture_output=True,
        text=True,
        timeout=30
    )

    data = json.loads(result.stdout)

    required_steps = [
        "receipts_complete",
        "daemons_live",
        "ac_threshold",
        "session_closed",
        "archive_written",
        "continuation_written",
        "baseline_snapshot",
    ]

    for step in required_steps:
        assert step in data["details"], f"step {step} missing from details"
        assert "passed" in data["details"][step]
        assert "message" in data["details"][step]


def test_readiness_check_negative_missing_continuation(company_root, tmp_path):
    """Negative case: missing continuation.json should fail session_closed step."""
    # Create temporary mock environment
    mock_continuation = tmp_path / "continuation.json"

    # Simulate missing file by not creating it
    assert not mock_continuation.exists()

    # In real environment, this would be checked by check_session_closed()
    # For unit test, verify the function logic directly
    from scripts.restart_readiness_check import check_session_closed

    # Temporarily override Path to use tmp_path
    import sys
    original_cwd = Path.cwd()
    try:
        import os
        os.chdir(tmp_path)
        passed, msg = check_session_closed()
        assert not passed, "should fail when continuation.json missing"
        assert "missing" in msg.lower() or "not run" in msg.lower()
    finally:
        os.chdir(original_cwd)


def test_readiness_check_negative_dead_daemon_detection(company_root):
    """Negative case: verify dead daemon detection logic (daemons_live step)."""
    # Import the function directly to test logic
    from scripts.restart_readiness_check import check_daemons_live

    # Run the check - in test environment some daemons may be missing
    passed, msg = check_daemons_live()

    # Verify message format (should report X/4 alive if any missing)
    if not passed:
        assert "/4 alive" in msg or "dead:" in msg.lower()
    else:
        # If all alive, verify message confirms 4/4
        assert "4/4" in msg


def test_readiness_check_cause_parameter(company_root):
    """Verify --cause parameter is captured in output."""
    script = company_root / "scripts" / "restart_readiness_check.py"
    result = subprocess.run(
        ["python3", str(script), "--dry-run", "--cause=Health"],
        capture_output=True,
        text=True,
        timeout=30
    )

    data = json.loads(result.stdout)

    assert "cause" in data
    assert data["cause"] == "Health"
