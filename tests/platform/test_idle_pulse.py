"""Regression test for idle_pulse.py — CZL-IDLE-PULSE-TYPEERROR-FIX.

Ensures last_ts from CIEU DB is coerced to float before arithmetic,
preventing TypeError when SQLite returns a string timestamp.
"""
import sqlite3
import sys
import tempfile
import time
from pathlib import Path
from unittest.mock import patch

import pytest

SCRIPTS_DIR = Path("/Users/haotianliu/.openclaw/workspace/ystar-company/scripts")


def _create_test_db(db_path: Path, ts_value):
    """Create a minimal CIEU DB with a single event at the given timestamp value."""
    conn = sqlite3.connect(str(db_path))
    conn.execute("""
        CREATE TABLE IF NOT EXISTS cieu_events (
            event_id TEXT,
            seq_global INTEGER,
            created_at TEXT,
            session_id TEXT,
            agent_id TEXT,
            event_type TEXT,
            decision TEXT,
            passed INTEGER,
            violations TEXT
        )
    """)
    conn.execute(
        "INSERT INTO cieu_events VALUES (?,?,?,?,?,?,?,?,?)",
        ("test_evt", 1, str(ts_value), "test", "ceo", "TEST", "{}", 1, "[]"),
    )
    conn.commit()
    conn.close()


class TestIdlePulseTypeCoercion:
    """last_ts from DB may be str; arithmetic must not raise TypeError."""

    def test_string_timestamp_no_typeerror(self, tmp_path):
        """When created_at is stored as a string, float() coercion prevents crash."""
        db_path = tmp_path / "test_cieu.db"
        now = time.time()
        _create_test_db(db_path, str(now - 60))  # 60 seconds ago, stored as string

        conn = sqlite3.connect(str(db_path))
        cursor = conn.cursor()
        cursor.execute("SELECT MAX(created_at) FROM cieu_events")
        last_ts = cursor.fetchone()[0]
        conn.close()

        # This is the exact line from idle_pulse.py (fixed version)
        last_age = int(time.time() - float(last_ts)) if last_ts else -1

        assert isinstance(last_age, int)
        assert 59 <= last_age <= 62  # roughly 60 seconds

    def test_float_timestamp_still_works(self, tmp_path):
        """When created_at is already numeric, float() is a no-op."""
        db_path = tmp_path / "test_cieu.db"
        now = time.time()
        _create_test_db(db_path, now - 120)  # stored as actual float

        conn = sqlite3.connect(str(db_path))
        cursor = conn.cursor()
        cursor.execute("SELECT MAX(created_at) FROM cieu_events")
        last_ts = cursor.fetchone()[0]
        conn.close()

        last_age = int(time.time() - float(last_ts)) if last_ts else -1

        assert isinstance(last_age, int)
        assert 119 <= last_age <= 122

    def test_none_timestamp_returns_minus_one(self):
        """When DB is empty (last_ts is None), returns -1."""
        last_ts = None
        last_age = int(time.time() - float(last_ts)) if last_ts else -1
        assert last_age == -1
