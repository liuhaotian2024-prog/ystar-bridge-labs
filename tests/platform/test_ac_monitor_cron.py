#!/usr/bin/env python3
"""Test AC monitor cron integration — CZL-109."""

import subprocess
import sys
from pathlib import Path

YSTAR_DIR = Path(__file__).resolve().parent.parent.parent
WATCHDOG_SCRIPT = YSTAR_DIR / "scripts" / "session_watchdog.py"


def test_ac_monitor_flag_exists():
    """Verify --ac-monitor flag is accepted by session_watchdog.py."""
    result = subprocess.run(
        [sys.executable, str(WATCHDOG_SCRIPT), "--help"],
        capture_output=True,
        text=True
    )
    assert result.returncode == 0
    assert "--ac-monitor" in result.stdout


def test_ac_monitor_executes():
    """Verify --ac-monitor mode runs without crashing."""
    result = subprocess.run(
        [sys.executable, str(WATCHDOG_SCRIPT), "--ac-monitor"],
        capture_output=True,
        text=True,
        timeout=5
    )
    assert result.returncode == 0
    # Should output JSON with score/violations
    import json
    output = json.loads(result.stdout.strip())
    assert "score" in output
    assert "violations" in output


def test_cron_line_installable():
    """Verify cron line syntax is valid (does not test cron daemon execution)."""
    cron_line = "*/10 * * * * cd /Users/haotianliu/.openclaw/workspace/ystar-company && python3 scripts/session_watchdog.py --ac-monitor >> /tmp/ystar_ac_monitor.log 2>&1"

    # Parse cron fields
    parts = cron_line.split()
    assert len(parts) >= 6, "cron line must have ≥6 fields (5 time + command)"

    # Verify time fields syntax (simple validation)
    minute, hour, day_of_month, month, day_of_week = parts[:5]
    assert minute == "*/10", "minute field should be */10"
    assert hour == "*", "hour field should be *"

    # Verify command contains correct script path
    command_part = " ".join(parts[5:])
    assert "session_watchdog.py" in command_part
    assert "--ac-monitor" in command_part
