#!/usr/bin/env python3
"""
Integration tests for K9-RT Sentinel cron wrapper.
Verifies wrapper script exists, is executable, and invokes sentinel without crash.
Checks for K9_RT_SENTINEL_TICK CIEU event emission (monitor visibility).

Scope: Platform engineer (Ryan Park) QA responsibility.
"""

import json
import os
import sqlite3
import subprocess
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[2]
WRAPPER_SCRIPT = REPO_ROOT / "scripts" / "k9_rt_sentinel_run.sh"
CIEU_DB_PATH = REPO_ROOT / ".ystar_cieu.db"


def test_wrapper_script_exists():
    """Verify wrapper script exists at expected path."""
    assert WRAPPER_SCRIPT.exists(), f"Wrapper script missing: {WRAPPER_SCRIPT}"


def test_wrapper_script_executable():
    """Verify wrapper script has executable permissions."""
    assert os.access(WRAPPER_SCRIPT, os.X_OK), f"Wrapper script not executable: {WRAPPER_SCRIPT}"


def test_wrapper_invokes_sentinel_without_crash():
    """
    Integration test: dry-run wrapper script, verify exit code 0 and output.
    """
    result = subprocess.run(
        [str(WRAPPER_SCRIPT)],
        cwd=str(REPO_ROOT),
        capture_output=True,
        text=True,
        timeout=10,
    )

    # Exit code 0 on success
    assert result.returncode == 0, f"Wrapper crashed: {result.stderr}"

    # Output should contain sentinel confirmation
    assert "[K9-RT Sentinel]" in result.stdout, f"Missing sentinel output: {result.stdout}"


def test_sentinel_emits_tick_event():
    """
    Verify K9_RT_SENTINEL_TICK CIEU event is emitted after wrapper invocation.
    Confirms sentinel is wired for monitoring.
    """
    if not CIEU_DB_PATH.exists():
        pytest.skip("CIEU DB not available (test environment)")

    # Run wrapper
    subprocess.run(
        [str(WRAPPER_SCRIPT)],
        cwd=str(REPO_ROOT),
        capture_output=True,
        timeout=10,
    )

    # Query CIEU DB for TICK event
    conn = sqlite3.connect(CIEU_DB_PATH)
    conn.row_factory = sqlite3.Row

    tables_cursor = conn.execute("SELECT name FROM sqlite_master WHERE type='table'")
    tables = [row[0] for row in tables_cursor.fetchall()]

    if "events" in tables:
        # Production schema
        cursor = conn.execute(
            "SELECT metadata FROM events WHERE event_type = 'K9_RT_SENTINEL_TICK' ORDER BY timestamp DESC LIMIT 1"
        )
        row = cursor.fetchone()
        assert row is not None, "No K9_RT_SENTINEL_TICK event found in production DB"
        payload = json.loads(row["metadata"])
    elif "cieu_events" in tables:
        # Test schema
        cursor = conn.execute(
            "SELECT payload FROM cieu_events WHERE event_type = 'K9_RT_SENTINEL_TICK' ORDER BY created_at DESC LIMIT 1"
        )
        row = cursor.fetchone()
        assert row is not None, "No K9_RT_SENTINEL_TICK event found in test DB"
        payload = json.loads(row["payload"])
    else:
        pytest.fail("CIEU DB has no known schema (events or cieu_events)")

    conn.close()

    # Verify payload structure
    assert "scanned" in payload, "TICK event missing 'scanned' field"
    assert "warnings_emitted" in payload, "TICK event missing 'warnings_emitted' field"
    assert "timestamp" in payload, "TICK event missing 'timestamp' field"
