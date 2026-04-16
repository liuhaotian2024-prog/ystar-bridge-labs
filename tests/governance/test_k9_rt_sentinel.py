#!/usr/bin/env python3
"""
Unit + Integration tests for K9-RT Sentinel

L3 Tested requirements:
- 8+ assertions
- Detects Rt>0 → warning with violation_type="rt_not_closed"
- Detects 3D role mismatch → "3d_role_mismatch"
- No false positives on clean events (Rt=0, role alignment OK)
- Append-only JSON lines format
- Graceful handling of corrupt CIEU DB
"""

import json
import sqlite3
import tempfile
from datetime import datetime
from pathlib import Path

import pytest

from ystar.governance.k9_rt_sentinel import (
    _check_restricted_path_violation,
    _extract_closure_gap,
    _extract_role_violation,
    poll_rt_measurements,
    scan_and_emit_warnings,
)

# Override paths for testing
import ystar.governance.k9_rt_sentinel as sentinel_module


@pytest.fixture
def temp_cieu_db(tmp_path):
    """Create temporary CIEU DB with schema matching sentinel expectations."""
    db_path = tmp_path / ".ystar_cieu.db"
    conn = sqlite3.connect(db_path)
    conn.execute(
        """
        CREATE TABLE cieu_events (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            event_type TEXT NOT NULL,
            created_at REAL NOT NULL,
            payload TEXT NOT NULL
        )
        """
    )
    conn.commit()
    conn.close()
    return db_path


@pytest.fixture
def temp_warning_queue(tmp_path):
    """Create temporary warning queue file."""
    queue_path = tmp_path / ".ystar_warning_queue.json"
    return queue_path


@pytest.fixture(autouse=True)
def patch_sentinel_paths(temp_cieu_db, temp_warning_queue, monkeypatch):
    """Patch sentinel module paths to use temp files."""
    monkeypatch.setattr(sentinel_module, "CIEU_DB_PATH", temp_cieu_db)
    monkeypatch.setattr(sentinel_module, "WARNING_QUEUE_PATH", temp_warning_queue)


def insert_rt_event(db_path: Path, event: dict):
    """Helper: insert RT_MEASUREMENT event into CIEU DB."""
    conn = sqlite3.connect(db_path)
    conn.execute(
        "INSERT INTO cieu_events (event_type, created_at, payload) VALUES (?, ?, ?)",
        ("RT_MEASUREMENT", datetime.utcnow().timestamp(), json.dumps(event)),
    )
    conn.commit()
    conn.close()


# Unit Tests: Path violation detection


def test_restricted_path_detection():
    """Unit: restricted path check catches CEO engineering writes."""
    assert _check_restricted_path_violation("write to reports/cto/foo.md") is True
    assert _check_restricted_path_violation("edit src/ystar/core.py") is True
    assert _check_restricted_path_violation("create tests/test_new.py") is True
    assert _check_restricted_path_violation("reports/eng-kernel/bar.md") is True
    assert _check_restricted_path_violation("reports/ceo/status.md") is False
    assert _check_restricted_path_violation("content/blog/post.md") is False


# Unit Tests: Role violation extraction


def test_role_violation_ceo_engineering_write():
    """Unit: CEO producer+executor writing to engineering paths → 3d_role_mismatch."""
    event = {
        "task_id": "task-001",
        "rt_value": 0.0,
        "y_star": "fix bug in src/ystar/kernel/core.py",
        "u": ["edit file"],
        "agent_id": "ceo",
        "role_tags": {"producer": "ceo", "executor": "ceo", "governed": "ceo"},
    }
    warning = _extract_role_violation(event)
    assert warning is not None
    assert warning["violation_type"] == "3d_role_mismatch"
    assert warning["task_id"] == "task-001"
    assert "engineering paths" in warning["details"]


def test_role_violation_cto_executor_allowed():
    """Unit: CEO producer + CTO executor → no violation (proper delegation)."""
    event = {
        "task_id": "task-002",
        "rt_value": 0.0,
        "y_star": "fix bug in src/ystar/kernel/core.py",
        "u": ["delegate to CTO"],
        "agent_id": "cto",
        "role_tags": {"producer": "ceo", "executor": "cto", "governed": "cto"},
    }
    warning = _extract_role_violation(event)
    assert warning is None  # No violation: executor != ceo


def test_role_violation_ceo_nonengineering_allowed():
    """Unit: CEO writing to CEO territory → no violation."""
    event = {
        "task_id": "task-003",
        "rt_value": 0.0,
        "y_star": "write reports/ceo/status.md",
        "u": ["write file"],
        "agent_id": "ceo",
        "role_tags": {"producer": "ceo", "executor": "ceo", "governed": "ceo"},
    }
    warning = _extract_role_violation(event)
    assert warning is None  # No restricted path match


# Unit Tests: Closure gap detection


def test_closure_gap_rt_greater_than_zero():
    """Unit: Rt+1 > 0 → rt_not_closed warning."""
    event = {
        "task_id": "task-004",
        "rt_value": 0.42,
        "y_star": "deploy to prod with 100% uptime",
        "agent_id": "ceo",
        "role_tags": {"producer": "ceo", "executor": "ceo", "governed": "ceo"},
    }
    warning = _extract_closure_gap(event)
    assert warning is not None
    assert warning["violation_type"] == "rt_not_closed"
    assert warning["rt_value"] == 0.42
    assert "Rt+1=0.42" in warning["details"]


def test_closure_gap_rt_zero_clean():
    """Unit: Rt+1 == 0 → no warning (clean closure)."""
    event = {
        "task_id": "task-005",
        "rt_value": 0.0,
        "y_star": "complete task successfully",
        "agent_id": "ceo",
        "role_tags": {"producer": "ceo", "executor": "ceo", "governed": "ceo"},
    }
    warning = _extract_closure_gap(event)
    assert warning is None


# Integration Tests: CIEU DB polling


def test_poll_rt_measurements_returns_events(temp_cieu_db):
    """Integration: poll_rt_measurements reads RT_MEASUREMENT events from DB."""
    event1 = {
        "task_id": "task-db-001",
        "rt_value": 0.1,
        "y_star": "test event",
        "timestamp": "2026-04-16T10:00:00Z",
    }
    event2 = {
        "task_id": "task-db-002",
        "rt_value": 0.0,
        "y_star": "clean event",
        "timestamp": "2026-04-16T11:00:00Z",
    }
    insert_rt_event(temp_cieu_db, event1)
    insert_rt_event(temp_cieu_db, event2)

    events = poll_rt_measurements(limit=10)
    assert len(events) == 2
    assert events[0]["task_id"] == "task-db-002"  # DESC order
    assert events[1]["task_id"] == "task-db-001"


def test_poll_rt_measurements_corrupt_db(monkeypatch, tmp_path):
    """Integration: corrupt CIEU DB → graceful empty list return."""
    bad_db = tmp_path / "corrupt.db"
    bad_db.write_text("not a sqlite db")
    monkeypatch.setattr(sentinel_module, "CIEU_DB_PATH", bad_db)

    events = poll_rt_measurements()
    assert events == []  # Graceful degradation


# Integration Tests: End-to-End warning emission


def test_scan_and_emit_warnings_dual_axis(temp_cieu_db, temp_warning_queue):
    """Integration: scan detects both 3D role + closure gap, emits correct warnings."""
    # Event 1: CEO engineering write (role violation)
    event_role = {
        "task_id": "task-e2e-001",
        "rt_value": 0.0,
        "y_star": "edit src/ystar/core.py directly",
        "u": ["write file"],
        "agent_id": "ceo",
        "role_tags": {"producer": "ceo", "executor": "ceo", "governed": "ceo"},
    }
    # Event 2: Rt > 0 (closure gap)
    event_closure = {
        "task_id": "task-e2e-002",
        "rt_value": 0.33,
        "y_star": "incomplete task",
        "u": ["action"],
        "agent_id": "cmo",
        "role_tags": {"producer": "cmo", "executor": "cmo", "governed": "cmo"},
    }
    insert_rt_event(temp_cieu_db, event_role)
    insert_rt_event(temp_cieu_db, event_closure)

    count = scan_and_emit_warnings()
    assert count == 2  # 1 role + 1 closure

    # Verify warning queue contents
    warnings = [json.loads(line) for line in temp_warning_queue.read_text().strip().split("\n")]
    assert len(warnings) == 2

    # Check role violation warning
    role_warning = next(w for w in warnings if w["violation_type"] == "3d_role_mismatch")
    assert role_warning["task_id"] == "task-e2e-001"
    assert "engineering paths" in role_warning["details"]

    # Check closure gap warning
    closure_warning = next(w for w in warnings if w["violation_type"] == "rt_not_closed")
    assert closure_warning["task_id"] == "task-e2e-002"
    assert closure_warning["rt_value"] == 0.33


def test_scan_and_emit_warnings_no_false_positives(temp_cieu_db, temp_warning_queue):
    """Integration: clean event (Rt=0, proper role delegation) → no warnings."""
    clean_event = {
        "task_id": "task-clean-001",
        "rt_value": 0.0,
        "y_star": "CEO delegates to CTO for kernel fix",
        "u": ["delegate"],
        "agent_id": "cto",
        "role_tags": {"producer": "ceo", "executor": "cto", "governed": "cto"},
    }
    insert_rt_event(temp_cieu_db, clean_event)

    count = scan_and_emit_warnings()
    assert count == 0  # No violations
    assert not temp_warning_queue.exists()  # No file created if no warnings


def test_scan_and_emit_warnings_append_only(temp_cieu_db, temp_warning_queue):
    """Integration: multiple scans append to queue (no overwrites), dedup prevents re-scan."""
    processed = set()
    event1 = {
        "task_id": "task-append-001",
        "rt_value": 0.1,
        "y_star": "task 1",
        "agent_id": "ceo",
        "role_tags": {"producer": "ceo", "executor": "ceo", "governed": "ceo"},
    }
    insert_rt_event(temp_cieu_db, event1)
    scan_and_emit_warnings(processed)

    event2 = {
        "task_id": "task-append-002",
        "rt_value": 0.2,
        "y_star": "task 2",
        "agent_id": "ceo",
        "role_tags": {"producer": "ceo", "executor": "ceo", "governed": "ceo"},
    }
    insert_rt_event(temp_cieu_db, event2)
    scan_and_emit_warnings(processed)  # Re-use same processed set (dedup)

    warnings = [json.loads(line) for line in temp_warning_queue.read_text().strip().split("\n")]
    assert len(warnings) == 2  # Append-only, no overwrites
    assert warnings[0]["task_id"] == "task-append-001"
    assert warnings[1]["task_id"] == "task-append-002"
