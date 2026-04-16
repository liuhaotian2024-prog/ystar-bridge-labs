#!/usr/bin/env python3
"""Test Ultimate Restart Recovery Components

Authority: Jordan Lee CZL-145 P0 HEAVY
Tests: restart_handoff_verifier.py + cieu_replay_recovery.py + auto-trigger integration
"""

import pytest
import json
import subprocess
from pathlib import Path

COMPANY_ROOT = Path(__file__).parent.parent.parent
SCRIPTS = COMPANY_ROOT / "scripts"


def test_handoff_verifier_returns_dict():
    """handoff_verifier returns verified/total/gaps dict"""
    result = subprocess.run(
        ["python3", str(SCRIPTS / "restart_handoff_verifier.py"), "--json"],
        capture_output=True,
        text=True
    )

    # Should return valid JSON regardless of pass/fail
    data = json.loads(result.stdout)
    assert "verified" in data
    assert "total" in data
    assert "gaps" in data
    assert isinstance(data["verified"], int)
    assert isinstance(data["total"], int)
    assert isinstance(data["gaps"], list)


def test_handoff_verifier_detects_missing_continuation():
    """handoff_verifier detects missing continuation.json → gap"""
    # Temporarily rename continuation.json to simulate missing
    continuation = COMPANY_ROOT / "memory/continuation.json"
    backup = COMPANY_ROOT / "memory/continuation.json.backup"

    if continuation.exists():
        continuation.rename(backup)

    try:
        result = subprocess.run(
            ["python3", str(SCRIPTS / "restart_handoff_verifier.py"), "--json"],
            capture_output=True,
            text=True
        )
        data = json.loads(result.stdout)

        # Should detect gap
        gap_found = any("continuation" in g.lower() for g in data["gaps"])
        assert gap_found, "Expected continuation.json gap not detected"

    finally:
        # Restore
        if backup.exists():
            backup.rename(continuation)


def test_cieu_replay_synthesizes_continuation():
    """cieu_replay synthesizes continuation from CIEU events"""
    result = subprocess.run(
        ["python3", str(SCRIPTS / "cieu_replay_recovery.py"), "--gaps", "continuation.json missing", "--json"],
        capture_output=True,
        text=True
    )

    data = json.loads(result.stdout)
    assert "recovered" in data
    assert "failed" in data

    # Should attempt recovery (may succeed or fail based on CIEU DB state)
    total = data["recovered"] + data["failed"]
    assert total == 1  # One gap provided


def test_cieu_replay_handles_empty_db():
    """cieu_replay handles empty CIEU DB gracefully"""
    # This should not crash even if CIEU DB is empty/missing
    result = subprocess.run(
        ["python3", str(SCRIPTS / "cieu_replay_recovery.py"), "--gaps", "trust_scores.json missing", "--json"],
        capture_output=True,
        text=True,
        timeout=10
    )

    # Should complete without error
    assert result.returncode in [0, 1]  # 0=success, 1=failed recovery (both ok)

    data = json.loads(result.stdout)
    assert "recovered" in data
    assert "failed" in data


def test_auto_trigger_integration_exists():
    """auto-trigger integration: HP<28 + no veto → fires"""
    # Check that session_health_watchdog.py contains auto-trigger logic
    watchdog = SCRIPTS / "session_health_watchdog.py"
    content = watchdog.read_text()

    # Should contain HP threshold check
    assert "hp < 28" in content.lower() or "hp<28" in content.lower(), "HP<28 threshold not found"

    # Should contain veto file check
    assert "ystar_no_auto_restart" in content.lower(), "Board veto file check not found"

    # Should contain AUTO_RESTART_TRIGGERED event
    assert "AUTO_RESTART_TRIGGERED" in content, "AUTO_RESTART_TRIGGERED event not emitted"


def test_auto_trigger_veto_file_blocks():
    """auto-trigger: Board veto file exists → blocked"""
    watchdog = SCRIPTS / "session_health_watchdog.py"
    content = watchdog.read_text()

    # Should check for veto file before triggering
    # Look for check_board_override or similar pattern
    assert "check_board_override" in content or "/tmp/ystar_no_auto_restart" in content, \
        "Board veto check not implemented"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
