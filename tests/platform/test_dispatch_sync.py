#!/usr/bin/env python3
"""
Tests for dispatch_sync.py — CZL-67 sync layer
"""
import json
import os
import sqlite3
import subprocess
import sys
from datetime import datetime, timedelta, timezone
from pathlib import Path

import pytest

DISPATCH_LOG_PATH = Path("/Users/haotianliu/.openclaw/workspace/ystar-company/governance/active_dispatch_log.md")
CIEU_DB_PATH = Path("/Users/haotianliu/.openclaw/workspace/ystar-company/.ystar_cieu.db")
DISPATCH_SYNC_SCRIPT = Path("/Users/haotianliu/.openclaw/workspace/ystar-company/scripts/dispatch_sync.py")


@pytest.fixture
def clean_dispatch_log():
    """Remove dispatch log before each test."""
    if DISPATCH_LOG_PATH.exists():
        DISPATCH_LOG_PATH.unlink()
    yield
    # Cleanup after test
    if DISPATCH_LOG_PATH.exists():
        DISPATCH_LOG_PATH.unlink()


def test_dispatch_sync_record_appends_to_log(clean_dispatch_log):
    """Test that record subcommand appends correctly to log."""
    # Execute record
    result = subprocess.run(
        [
            sys.executable,
            str(DISPATCH_SYNC_SCRIPT),
            "record",
            "ryan-platform",
            "CZL-99",
            "foo.py,bar.py",
            "--tier", "T1",
            "--expected_completion", "15m"
        ],
        capture_output=True,
        text=True
    )

    assert result.returncode == 0, f"record failed: {result.stderr}"

    # Verify log contains entry
    assert DISPATCH_LOG_PATH.exists(), "Dispatch log not created"
    log_content = DISPATCH_LOG_PATH.read_text()

    assert "CEO_DISPATCH(ryan-platform" in log_content
    assert "atomic_id=CZL-99" in log_content
    assert "['foo.py', 'bar.py']" in log_content
    assert "tier=T1" in log_content
    assert "expected_completion=15m" in log_content


def test_dispatch_sync_record_emits_cieu_event(clean_dispatch_log):
    """Test that record emits CEO_DIRECT_DISPATCH_TIER1 CIEU event."""
    # Count events before
    conn = sqlite3.connect(str(CIEU_DB_PATH))
    cursor = conn.cursor()
    cursor.execute("SELECT COUNT(*) FROM cieu_events WHERE event_type = 'CEO_DIRECT_DISPATCH_TIER1'")
    count_before = cursor.fetchone()[0]
    conn.close()

    # Execute record
    result = subprocess.run(
        [
            sys.executable,
            str(DISPATCH_SYNC_SCRIPT),
            "record",
            "leo-kernel",
            "CZL-100",
            "kernel/czl.py",
            "--tier", "T1",
            "--expected_completion", "30m"
        ],
        capture_output=True,
        text=True
    )

    assert result.returncode == 0, f"record failed: {result.stderr}"

    # Count events after
    conn = sqlite3.connect(str(CIEU_DB_PATH))
    cursor = conn.cursor()
    cursor.execute("SELECT COUNT(*) FROM cieu_events WHERE event_type = 'CEO_DIRECT_DISPATCH_TIER1'")
    count_after = cursor.fetchone()[0]

    # Verify event emitted
    assert count_after > count_before, "No CIEU event emitted"

    # Verify event payload
    cursor.execute(
        "SELECT params_json FROM cieu_events WHERE event_type = 'CEO_DIRECT_DISPATCH_TIER1' ORDER BY created_at DESC LIMIT 1"
    )
    params_json = cursor.fetchone()[0]
    conn.close()

    payload = json.loads(params_json)
    assert payload["agent_target"] == "leo-kernel"
    assert payload["atomic_id"] == "CZL-100"
    assert payload["tier"] == "T1"


def test_dispatch_sync_get_recent_filters_by_window(clean_dispatch_log):
    """Test that get_recent filters by time window."""
    # Manually populate log with entries at different times
    DISPATCH_LOG_PATH.parent.mkdir(parents=True, exist_ok=True)

    now = datetime.now(timezone.utc)
    time_1h_ago = now - timedelta(hours=1)
    time_2h_ago = now - timedelta(hours=2)
    time_25h_ago = now - timedelta(hours=25)

    entries = [
        f"[{time_1h_ago.strftime('%Y-%m-%dT%H:%M:%SZ')}] CEO_DISPATCH(ryan-platform, atomic_id=CZL-101, scope=['a.py'], tier=T1, expected_completion=15m)\n",
        f"[{time_2h_ago.strftime('%Y-%m-%dT%H:%M:%SZ')}] CEO_DISPATCH(leo-kernel, atomic_id=CZL-102, scope=['b.py'], tier=T1, expected_completion=30m)\n",
        f"[{time_25h_ago.strftime('%Y-%m-%dT%H:%M:%SZ')}] CEO_DISPATCH(maya-governance, atomic_id=CZL-103, scope=['c.py'], tier=T2, expected_completion=1h)\n",
    ]

    with open(DISPATCH_LOG_PATH, "w") as f:
        f.write("# Active CEO Dispatch Log\n\n")
        f.writelines(entries)

    # Execute get_recent with 24h window
    result = subprocess.run(
        [
            sys.executable,
            str(DISPATCH_SYNC_SCRIPT),
            "get_recent",
            "--window_hours", "24"
        ],
        capture_output=True,
        text=True
    )

    assert result.returncode == 0, f"get_recent failed: {result.stderr}"

    output = result.stdout

    # Verify only 1h and 2h entries included
    assert "CZL-101" in output, "1h entry missing"
    assert "CZL-102" in output, "2h entry missing"
    assert "CZL-103" not in output, "25h entry should be filtered out"
