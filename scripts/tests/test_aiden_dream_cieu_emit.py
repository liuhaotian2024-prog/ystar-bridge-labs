"""
Test: aiden_dream._emit_cieu writes CIEU event with seq_global NOT NULL.

Regression 2026-04-21: bug found during Milestone 4 launchd dream daemon smoke —
`_emit_cieu` INSERT 缺 seq_global column, violating production CIEU schema
`seq_global INTEGER NOT NULL`. Fix inserts int(time.time()*1_000_000).

M-tag: M-2a (audit chain completeness, no silent CIEU drop).
"""
import os
import sys
import sqlite3
import tempfile
import time
import pytest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from aiden_dream import _emit_cieu


def _make_production_cieu_db(path):
    """Create a CIEU db with production schema (seq_global NOT NULL)."""
    conn = sqlite3.connect(path)
    conn.execute("""
        CREATE TABLE cieu_events (
            rowid INTEGER PRIMARY KEY AUTOINCREMENT,
            event_id TEXT,
            seq_global INTEGER NOT NULL,
            created_at REAL,
            session_id TEXT,
            agent_id TEXT,
            event_type TEXT,
            decision TEXT,
            passed INTEGER,
            violations TEXT,
            result_json TEXT,
            params_json TEXT,
            evidence_grade TEXT
        )
    """)
    conn.commit()
    conn.close()


def test_emit_cieu_production_schema_writes_seq_global():
    """Empirical: _emit_cieu succeeds on production schema with seq_global NOT NULL."""
    with tempfile.TemporaryDirectory() as td:
        db = os.path.join(td, "cieu.db")
        _make_production_cieu_db(db)

        ok = _emit_cieu("BRAIN_DREAM_TEST", {"action": "test_action", "result": "ok"}, cieu_db=db)
        assert ok is True, "emit should return True on success"

        conn = sqlite3.connect(db)
        rows = conn.execute(
            "SELECT event_id, seq_global, created_at, event_type FROM cieu_events"
        ).fetchall()
        conn.close()

        assert len(rows) == 1, f"expected 1 event, got {len(rows)}"
        event_id, seq_global, created_at, event_type = rows[0]

        assert seq_global is not None, "seq_global MUST NOT be NULL"
        assert seq_global > 0, f"seq_global must be positive, got {seq_global}"
        assert event_type == "BRAIN_DREAM_TEST"
        assert created_at > 0


def test_emit_cieu_two_events_have_increasing_seq_global():
    """seq_global should be monotonic (later event > earlier event)."""
    with tempfile.TemporaryDirectory() as td:
        db = os.path.join(td, "cieu.db")
        _make_production_cieu_db(db)

        _emit_cieu("EVENT_ONE", {"action": "first"}, cieu_db=db)
        time.sleep(0.01)  # ensure clock ticks
        _emit_cieu("EVENT_TWO", {"action": "second"}, cieu_db=db)

        conn = sqlite3.connect(db)
        rows = conn.execute(
            "SELECT seq_global, event_type FROM cieu_events ORDER BY rowid"
        ).fetchall()
        conn.close()

        assert len(rows) == 2
        assert rows[0][1] == "EVENT_ONE"
        assert rows[1][1] == "EVENT_TWO"
        assert rows[1][0] > rows[0][0], \
            f"seq_global monotonic expected, got {rows[0][0]} then {rows[1][0]}"


def test_emit_cieu_simple_schema_still_works():
    """Regression: simple/test schema (no seq_global col) should still auto-create + insert."""
    with tempfile.TemporaryDirectory() as td:
        db = os.path.join(td, "cieu.db")
        # Don't create table — let _emit_cieu create simple schema

        ok = _emit_cieu("SIMPLE_TEST", {"action": "simple"}, cieu_db=db)
        assert ok is True

        conn = sqlite3.connect(db)
        cols = [r[1] for r in conn.execute("PRAGMA table_info(cieu_events)").fetchall()]
        rows = conn.execute("SELECT COUNT(*) FROM cieu_events").fetchone()
        conn.close()

        assert "timestamp" in cols
        assert rows[0] == 1
