#!/usr/bin/env python3
"""Tests for CEO self-heartbeat loop."""

import json
import sqlite3
import tempfile
from datetime import datetime, timedelta
from pathlib import Path
from unittest import mock

import pytest

# Import the module under test
import sys
sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "scripts"))
import ceo_heartbeat


@pytest.fixture
def temp_db():
    """Create temporary CIEU database."""
    with tempfile.NamedTemporaryFile(suffix=".db", delete=False) as f:
        db_path = Path(f.name)

    # Initialize db with schema
    conn = sqlite3.connect(str(db_path))
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS cieu_events (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp TEXT NOT NULL,
            actor TEXT NOT NULL,
            event_type TEXT NOT NULL,
            description TEXT,
            metadata TEXT
        )
    """)
    conn.commit()
    conn.close()

    yield db_path

    # Cleanup
    db_path.unlink()


@pytest.fixture
def temp_priority_brief():
    """Create temporary priority_brief.md."""
    content = """---
version: "v0.4"
last_updated: "2026-04-13"
status: "active"
phase: "internal_consolidation"
today_targets:
  - target: "Fix CIEU persistence bug"
    owner: "ceo"
    deadline: "EOD 2026-04-13"
  - target: "Complete ADE integration"
    owner: "ceo"
    deadline: "EOD 2026-04-13"
this_week_targets:
  - target: "PyPI 0.49.0 release"
    owner: "cto"
    deadline: "2026-04-19"
---

# CEO Priority Brief
Content here...
"""
    with tempfile.NamedTemporaryFile(mode="w", suffix=".md", delete=False) as f:
        f.write(content)
        brief_path = Path(f.name)

    yield brief_path

    brief_path.unlink()


def test_parse_priority_brief_targets(temp_priority_brief):
    """Test parsing YAML frontmatter from priority_brief."""
    with mock.patch.object(ceo_heartbeat, "PRIORITY_BRIEF_PATH", temp_priority_brief):
        brief = ceo_heartbeat.parse_priority_brief_targets()

        assert "today_targets" in brief
        targets = brief["today_targets"]
        assert len(targets) == 2
        assert "Fix CIEU persistence bug" in targets
        assert "Complete ADE integration" in targets


def test_get_last_ceo_cieu_timestamp_no_events(temp_db):
    """Test querying CIEU timestamp when no events exist."""
    with mock.patch.object(ceo_heartbeat, "CIEU_DB_PATH", temp_db):
        timestamp = ceo_heartbeat.get_last_ceo_cieu_timestamp()
        assert timestamp is None


def test_get_last_ceo_cieu_timestamp_with_events(temp_db):
    """Test querying most recent CEO CIEU event."""
    # Insert test events
    conn = sqlite3.connect(str(temp_db))
    cursor = conn.cursor()

    now = datetime.now()
    old_time = (now - timedelta(minutes=10)).isoformat()
    recent_time = (now - timedelta(minutes=2)).isoformat()

    cursor.execute("""
        INSERT INTO cieu_events (timestamp, actor, event_type, description, metadata)
        VALUES (?, ?, ?, ?, ?)
    """, (old_time, "ceo", "TEST_EVENT", "old event", "{}"))

    cursor.execute("""
        INSERT INTO cieu_events (timestamp, actor, event_type, description, metadata)
        VALUES (?, ?, ?, ?, ?)
    """, (recent_time, "ceo", "TEST_EVENT", "recent event", "{}"))

    # Insert non-CEO event (should be ignored)
    cursor.execute("""
        INSERT INTO cieu_events (timestamp, actor, event_type, description, metadata)
        VALUES (?, ?, ?, ?, ?)
    """, (now.isoformat(), "cto", "TEST_EVENT", "cto event", "{}"))

    conn.commit()
    conn.close()

    with mock.patch.object(ceo_heartbeat, "CIEU_DB_PATH", temp_db):
        timestamp = ceo_heartbeat.get_last_ceo_cieu_timestamp()

        assert timestamp is not None
        # Should return most recent CEO event, not CTO event
        assert abs((datetime.fromisoformat(recent_time) - timestamp).total_seconds()) < 1


def test_check_idle_true_no_events(temp_db):
    """Test idle detection when no events exist."""
    with mock.patch.object(ceo_heartbeat, "CIEU_DB_PATH", temp_db):
        assert ceo_heartbeat.check_idle() is True


def test_check_idle_true_old_events(temp_db):
    """Test idle detection when last event is >5min old."""
    conn = sqlite3.connect(str(temp_db))
    cursor = conn.cursor()

    # Event from 10 minutes ago
    old_time = (datetime.now() - timedelta(minutes=10)).isoformat()
    cursor.execute("""
        INSERT INTO cieu_events (timestamp, actor, event_type, description, metadata)
        VALUES (?, ?, ?, ?, ?)
    """, (old_time, "ceo", "TEST_EVENT", "old event", "{}"))

    conn.commit()
    conn.close()

    with mock.patch.object(ceo_heartbeat, "CIEU_DB_PATH", temp_db):
        assert ceo_heartbeat.check_idle() is True


def test_check_idle_false_recent_events(temp_db):
    """Test idle detection when last event is recent (<5min)."""
    conn = sqlite3.connect(str(temp_db))
    cursor = conn.cursor()

    # Event from 2 minutes ago
    recent_time = (datetime.now() - timedelta(minutes=2)).isoformat()
    cursor.execute("""
        INSERT INTO cieu_events (timestamp, actor, event_type, description, metadata)
        VALUES (?, ?, ?, ?, ?)
    """, (recent_time, "ceo", "TEST_EVENT", "recent event", "{}"))

    conn.commit()
    conn.close()

    with mock.patch.object(ceo_heartbeat, "CIEU_DB_PATH", temp_db):
        assert ceo_heartbeat.check_idle() is False


def test_emit_cieu_event(temp_db):
    """Test emitting CIEU event to database."""
    with mock.patch.object(ceo_heartbeat, "CIEU_DB_PATH", temp_db):
        ceo_heartbeat.emit_cieu_event(
            "CEO_HEARTBEAT_IDLE",
            "Test idle trigger",
            {"targets": ["target1", "target2"]},
            dry_run=False
        )

    # Verify event was inserted
    conn = sqlite3.connect(str(temp_db))
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM cieu_events WHERE event_type = 'CEO_HEARTBEAT_IDLE'")
    row = cursor.fetchone()
    conn.close()

    assert row is not None
    assert row[2] == "ceo"  # actor
    assert row[3] == "CEO_HEARTBEAT_IDLE"  # event_type
    assert row[4] == "Test idle trigger"  # description

    metadata = json.loads(row[5])
    assert metadata["targets"] == ["target1", "target2"]


def test_emit_cieu_event_dry_run(temp_db):
    """Test dry-run mode doesn't emit events."""
    with mock.patch.object(ceo_heartbeat, "CIEU_DB_PATH", temp_db):
        ceo_heartbeat.emit_cieu_event(
            "CEO_HEARTBEAT_IDLE",
            "Test idle trigger",
            dry_run=True
        )

    # Verify no event was inserted
    conn = sqlite3.connect(str(temp_db))
    cursor = conn.cursor()
    cursor.execute("SELECT COUNT(*) FROM cieu_events")
    count = cursor.fetchone()[0]
    conn.close()

    assert count == 0


def test_get_active_agent_exists(tmp_path):
    """Test reading active agent file."""
    active_agent_file = tmp_path / ".ystar_active_agent"
    active_agent_file.write_text("ceo\n")

    with mock.patch.object(ceo_heartbeat, "ACTIVE_AGENT_PATH", active_agent_file):
        agent = ceo_heartbeat.get_active_agent()
        assert agent == "ceo"


def test_get_active_agent_not_exists(tmp_path):
    """Test handling missing active agent file."""
    active_agent_file = tmp_path / ".ystar_active_agent"

    with mock.patch.object(ceo_heartbeat, "ACTIVE_AGENT_PATH", active_agent_file):
        agent = ceo_heartbeat.get_active_agent()
        assert agent == "unknown"


def test_check_off_target():
    """Test off-target detection (MVP always returns False)."""
    targets = ["Fix CIEU bug", "Complete ADE"]
    assert ceo_heartbeat.check_off_target(targets) is False


def test_check_today_done():
    """Test today-done detection (MVP always returns False)."""
    targets = ["Fix CIEU bug", "Complete ADE"]
    assert ceo_heartbeat.check_today_done(targets) is False


def test_heartbeat_check_skips_non_ceo(capsys, temp_db, temp_priority_brief):
    """Test heartbeat skips when active agent is not CEO."""
    with tempfile.NamedTemporaryFile(mode="w", delete=False) as f:
        f.write("eng-platform\n")
        active_agent_file = Path(f.name)

    try:
        with mock.patch.object(ceo_heartbeat, "ACTIVE_AGENT_PATH", active_agent_file):
            with mock.patch.object(ceo_heartbeat, "CIEU_DB_PATH", temp_db):
                with mock.patch.object(ceo_heartbeat, "PRIORITY_BRIEF_PATH", temp_priority_brief):
                    # Run heartbeat check via main with --once
                    with mock.patch("sys.argv", ["ceo_heartbeat.py", "--once", "--dry-run"]):
                        ceo_heartbeat.main()

        captured = capsys.readouterr()
        assert "[SKIP] Active agent is eng-platform, not ceo" in captured.out
    finally:
        active_agent_file.unlink()


def test_heartbeat_check_idle_trigger(capsys, temp_db, temp_priority_brief):
    """Test heartbeat emits IDLE event when CEO inactive."""
    with tempfile.NamedTemporaryFile(mode="w", delete=False) as f:
        f.write("ceo\n")
        active_agent_file = Path(f.name)

    try:
        with mock.patch.object(ceo_heartbeat, "ACTIVE_AGENT_PATH", active_agent_file):
            with mock.patch.object(ceo_heartbeat, "CIEU_DB_PATH", temp_db):
                with mock.patch.object(ceo_heartbeat, "PRIORITY_BRIEF_PATH", temp_priority_brief):
                    # Run heartbeat check (no events = idle)
                    with mock.patch("sys.argv", ["ceo_heartbeat.py", "--once", "--dry-run"]):
                        ceo_heartbeat.main()

        captured = capsys.readouterr()
        assert "[DRY-RUN] Would emit CIEU: CEO_HEARTBEAT_IDLE" in captured.out
    finally:
        active_agent_file.unlink()
