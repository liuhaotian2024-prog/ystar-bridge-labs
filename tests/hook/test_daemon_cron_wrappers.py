#!/usr/bin/env python3
"""
Tests for hook_daemon_wrapper.py and cron_wrapper.py CIEU emission.
CZL-ARCH-7 — daemon + cron behaviour enters CIEU audit trail.
"""
import json
import os
import sqlite3
import sys
import tempfile
import importlib
import unittest
from unittest.mock import patch
from pathlib import Path

# Ensure scripts/ is importable
SCRIPTS_DIR = os.path.join(os.path.dirname(__file__), "..", "..", "scripts")
sys.path.insert(0, SCRIPTS_DIR)


def _make_temp_db():
    """Create a temporary CIEU DB with the cieu_events table."""
    fd, path = tempfile.mkstemp(suffix=".db")
    os.close(fd)
    conn = sqlite3.connect(path)
    conn.execute("""
        CREATE TABLE cieu_events (
            event_id TEXT PRIMARY KEY,
            seq_global INTEGER,
            created_at REAL,
            session_id TEXT,
            agent_id TEXT,
            event_type TEXT,
            decision TEXT,
            passed INTEGER,
            task_description TEXT,
            params_json TEXT,
            drift_detected INTEGER,
            drift_details TEXT,
            drift_category TEXT,
            file_path TEXT,
            command TEXT,
            evidence_grade TEXT
        )
    """)
    conn.commit()
    conn.close()
    return path


class TestDaemonHeartbeat(unittest.TestCase):
    def test_heartbeat_writes_cieu(self):
        db_path = _make_temp_db()
        try:
            import _cieu_helpers
            with patch.object(_cieu_helpers, "CIEU_DB_PATH", Path(db_path)):
                import hook_daemon_wrapper
                importlib.reload(hook_daemon_wrapper)
                ok = hook_daemon_wrapper.heartbeat_once()

            self.assertTrue(ok)
            conn = sqlite3.connect(db_path)
            rows = conn.execute(
                "SELECT event_type, params_json FROM cieu_events WHERE event_type='DAEMON_HEARTBEAT'"
            ).fetchall()
            conn.close()
            self.assertEqual(len(rows), 1)
            params = json.loads(rows[0][1])
            self.assertIn("pid", params)
        finally:
            os.unlink(db_path)


class TestCronWrapper(unittest.TestCase):
    def test_cron_success_writes_tick_and_result(self):
        db_path = _make_temp_db()
        try:
            import _cieu_helpers
            with patch.object(_cieu_helpers, "CIEU_DB_PATH", Path(db_path)):
                import cron_wrapper
                importlib.reload(cron_wrapper)
                rc = cron_wrapper.run_with_cieu(["echo", "hello"])

            self.assertEqual(rc, 0)
            conn = sqlite3.connect(db_path)
            types = [r[0] for r in conn.execute(
                "SELECT event_type FROM cieu_events ORDER BY seq_global"
            ).fetchall()]
            conn.close()
            self.assertIn("CRON_TICK", types)
            self.assertIn("CRON_RESULT", types)
        finally:
            os.unlink(db_path)

    def test_cron_failure_does_not_crash(self):
        db_path = _make_temp_db()
        try:
            import _cieu_helpers
            with patch.object(_cieu_helpers, "CIEU_DB_PATH", Path(db_path)):
                import cron_wrapper
                importlib.reload(cron_wrapper)
                rc = cron_wrapper.run_with_cieu(["false"])

            self.assertNotEqual(rc, 0)
            conn = sqlite3.connect(db_path)
            result_rows = conn.execute(
                "SELECT passed, task_description FROM cieu_events WHERE event_type='CRON_RESULT'"
            ).fetchall()
            conn.close()
            self.assertEqual(len(result_rows), 1)
            self.assertEqual(result_rows[0][0], 0)  # passed=0
        finally:
            os.unlink(db_path)


if __name__ == "__main__":
    unittest.main()
