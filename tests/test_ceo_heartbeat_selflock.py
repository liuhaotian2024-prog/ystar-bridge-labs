#!/usr/bin/env python3
"""
Tests for CEO heartbeat self-lock detection and auto-recovery.

Test scenarios:
1. No denies → no warning
2. 3 consecutive denies in 5min → warning + auto-recovery
3. Single deny blocking >180s → warning + auto-recovery
4. Fulfillment events auto-emitted correctly
"""

import json
import sqlite3
import tempfile
import time
from datetime import datetime
from pathlib import Path
from unittest.mock import patch, MagicMock

import pytest
import sys

# Add parent to path to import ceo_heartbeat
sys.path.insert(0, str(Path(__file__).parent.parent / "scripts"))
import ceo_heartbeat


@pytest.fixture
def temp_cieu_db():
    """Create temporary CIEU database with schema."""
    with tempfile.NamedTemporaryFile(mode='w', suffix='.db', delete=False) as f:
        db_path = Path(f.name)

    conn = sqlite3.connect(str(db_path))
    cursor = conn.cursor()

    # Create CIEU events table (minimal schema for tests)
    cursor.execute("""
        CREATE TABLE cieu_events (
            rowid        INTEGER PRIMARY KEY AUTOINCREMENT,
            event_id     TEXT    NOT NULL UNIQUE,
            seq_global   INTEGER NOT NULL,
            created_at   REAL    NOT NULL,
            session_id   TEXT    NOT NULL,
            agent_id     TEXT    NOT NULL,
            event_type   TEXT    NOT NULL,
            decision     TEXT    NOT NULL,
            passed       INTEGER NOT NULL DEFAULT 0,
            violations   TEXT,
            file_path    TEXT,
            command      TEXT,
            url          TEXT
        )
    """)

    conn.commit()
    conn.close()

    yield db_path

    # Cleanup
    db_path.unlink()


def insert_deny_event(db_path: Path, agent_id: str, created_at: float, violations: list = None):
    """Helper to insert a deny event into test database."""
    conn = sqlite3.connect(str(db_path))
    cursor = conn.cursor()

    violations_json = json.dumps(violations) if violations else None

    cursor.execute("""
        INSERT INTO cieu_events (
            event_id, seq_global, created_at, session_id, agent_id,
            event_type, decision, passed, violations
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        f"test-{int(created_at * 1000000)}",
        int(created_at * 1000000),
        created_at,
        "test-session",
        agent_id,
        "external_observation",
        "deny",
        0,
        violations_json
    ))

    conn.commit()
    conn.close()


def test_no_denies_no_warning(temp_cieu_db):
    """Test: no deny events → no self-lock warning."""
    with patch.object(ceo_heartbeat, 'CIEU_DB_PATH', temp_cieu_db):
        with patch.object(ceo_heartbeat, 'emit_cieu_event') as mock_emit:
            result = ceo_heartbeat.check_self_lock(dry_run=False)

            assert result is False
            mock_emit.assert_not_called()


def test_three_denies_triggers_warning(temp_cieu_db):
    """Test: ≥3 deny events in 5min → self-lock warning + auto-recovery."""
    now = time.time()

    # Insert 3 deny events in last 5 minutes
    for i in range(3):
        insert_deny_event(
            temp_cieu_db,
            "ceo",
            now - (i * 60),  # 0, 60, 120 seconds ago
            violations=[{"reason": f"obligation overdue test {i}"}]
        )

    with patch.object(ceo_heartbeat, 'CIEU_DB_PATH', temp_cieu_db):
        with patch.object(ceo_heartbeat, 'emit_cieu_event') as mock_emit:
            result = ceo_heartbeat.check_self_lock(dry_run=False)

            assert result is True

            # Check that warning was emitted
            calls = mock_emit.call_args_list
            assert len(calls) >= 1

            # First call should be CEO_SELF_LOCK_WARNING
            warning_call = calls[0]
            assert warning_call[0][0] == "CEO_SELF_LOCK_WARNING"
            assert "3 consecutive denies" in warning_call[0][1]
            assert warning_call[0][2]["deny_count"] == 3

            # Should also emit fulfillment events
            fulfillment_events = [c for c in calls if "ACKNOWLEDGED" in c[0][0] or "DECLARED" in c[0][0]]
            assert len(fulfillment_events) >= 1


def test_single_deny_long_block_triggers_warning(temp_cieu_db):
    """Test: single deny blocking >180s → self-lock warning."""
    now = time.time()

    # Insert single deny event 200 seconds ago (>180s threshold)
    insert_deny_event(
        temp_cieu_db,
        "ceo",
        now - 200,
        violations=[{"reason": "obligation overdue: directive_acknowledgement"}]
    )

    with patch.object(ceo_heartbeat, 'CIEU_DB_PATH', temp_cieu_db):
        with patch.object(ceo_heartbeat, 'emit_cieu_event') as mock_emit:
            result = ceo_heartbeat.check_self_lock(dry_run=False)

            assert result is True

            calls = mock_emit.call_args_list
            warning_call = calls[0]
            assert warning_call[0][0] == "CEO_SELF_LOCK_WARNING"
            assert "single deny blocking" in warning_call[0][1]
            assert warning_call[0][2]["trigger_rule"] == "single block >180s"
            assert warning_call[0][2]["seconds_blocked"] >= 180


def test_single_deny_short_block_no_warning(temp_cieu_db):
    """Test: single deny <180s → no warning (not stuck yet)."""
    now = time.time()

    # Insert single deny event 60 seconds ago (<180s threshold)
    insert_deny_event(temp_cieu_db, "ceo", now - 60)

    with patch.object(ceo_heartbeat, 'CIEU_DB_PATH', temp_cieu_db):
        with patch.object(ceo_heartbeat, 'emit_cieu_event') as mock_emit:
            result = ceo_heartbeat.check_self_lock(dry_run=False)

            assert result is False
            mock_emit.assert_not_called()


def test_fulfillment_events_emitted(temp_cieu_db):
    """Test: fulfillment events are emitted correctly."""
    now = time.time()

    # Insert 3 denies to trigger auto-recovery
    for i in range(3):
        insert_deny_event(temp_cieu_db, "ceo", now - (i * 60))

    with patch.object(ceo_heartbeat, 'CIEU_DB_PATH', temp_cieu_db):
        with patch.object(ceo_heartbeat, 'emit_cieu_event') as mock_emit:
            ceo_heartbeat.check_self_lock(dry_run=False)

            # Extract fulfillment event types
            fulfillment_events = [
                call[0][0] for call in mock_emit.call_args_list
                if call[0][0] in ["DIRECTIVE_ACKNOWLEDGED", "INTENT_DECLARED", "PROGRESS_UPDATED"]
            ]

            # Should emit all 3 common fulfillment events
            assert "DIRECTIVE_ACKNOWLEDGED" in fulfillment_events
            assert "INTENT_DECLARED" in fulfillment_events
            assert "PROGRESS_UPDATED" in fulfillment_events


def test_other_agent_denies_ignored(temp_cieu_db):
    """Test: deny events from other agents don't trigger CEO self-lock."""
    now = time.time()

    # Insert 3 denies for different agent
    for i in range(3):
        insert_deny_event(temp_cieu_db, "cto", now - (i * 60))

    with patch.object(ceo_heartbeat, 'CIEU_DB_PATH', temp_cieu_db):
        with patch.object(ceo_heartbeat, 'emit_cieu_event') as mock_emit:
            result = ceo_heartbeat.check_self_lock(dry_run=False)

            assert result is False
            mock_emit.assert_not_called()


def test_dry_run_no_emit(temp_cieu_db):
    """Test: dry_run=True doesn't emit events."""
    now = time.time()

    # Insert 3 denies
    for i in range(3):
        insert_deny_event(temp_cieu_db, "ceo", now - (i * 60))

    with patch.object(ceo_heartbeat, 'CIEU_DB_PATH', temp_cieu_db):
        # Don't mock emit_cieu_event, let it run in dry mode
        result = ceo_heartbeat.check_self_lock(dry_run=True)

        assert result is True

        # Verify no events were actually written to DB
        conn = sqlite3.connect(str(temp_cieu_db))
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM cieu_events WHERE event_type = 'CEO_SELF_LOCK_WARNING'")
        count = cursor.fetchone()[0]
        conn.close()

        assert count == 0  # dry-run should not write to DB


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
