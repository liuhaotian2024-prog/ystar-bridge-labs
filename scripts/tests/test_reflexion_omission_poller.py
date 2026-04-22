"""Test: Reflexion OmissionEngine poller — external consumer of overdue events."""
import json
import os
import sqlite3
import sys
import time
from pathlib import Path
import pytest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


def _make_mock_cieu(db_path: Path, events: list):
    conn = sqlite3.connect(str(db_path))
    conn.execute("""
        CREATE TABLE cieu_events (
            event_id TEXT PRIMARY KEY,
            event_type TEXT,
            rt_value INTEGER,
            payload TEXT
        )
    """)
    for e in events:
        conn.execute(
            "INSERT INTO cieu_events VALUES (?, ?, ?, ?)",
            (e["event_id"], e["event_type"], e.get("rt_value", 1),
             e.get("payload", ""))
        )
    conn.commit()
    conn.close()


def test_poller_handles_no_db(tmp_path, monkeypatch):
    import reflexion_omission_poller as mod
    monkeypatch.setattr(mod, "CIEU_DB", tmp_path / "nope.db")
    monkeypatch.setattr(mod, "CIEU_MAIN_DB", tmp_path / "nope2.db")
    monkeypatch.setattr(mod, "SENTINEL", tmp_path / "sentinel.json")
    assert mod.main() == 0


def test_poller_queries_overdue_events(tmp_path, monkeypatch):
    import reflexion_omission_poller as mod
    db = tmp_path / "cieu.db"
    _make_mock_cieu(db, [
        {"event_id": "evt1", "event_type": "OMISSION_OVERDUE", "rt_value": 2},
        {"event_id": "evt2", "event_type": "SOMETHING_ELSE", "rt_value": 0},
        {"event_id": "evt3", "event_type": "RT_NONZERO", "rt_value": 1},
    ])
    results = mod._query_overdue_events(db)
    event_ids = {r["event_id"] for r in results}
    assert "evt1" in event_ids
    assert "evt3" in event_ids
    assert "evt2" not in event_ids  # different event_type, filtered


def test_poller_idempotent_via_sentinel(tmp_path, monkeypatch):
    import reflexion_omission_poller as mod
    db = tmp_path / "cieu.db"
    _make_mock_cieu(db, [
        {"event_id": "evtA", "event_type": "OMISSION_OVERDUE", "rt_value": 1},
    ])
    monkeypatch.setattr(mod, "CIEU_DB", db)
    monkeypatch.setattr(mod, "CIEU_MAIN_DB", tmp_path / "no.db")
    monkeypatch.setattr(mod, "SENTINEL", tmp_path / "sentinel.json")

    # Mock reflection generator to avoid Ollama call
    def fake_gen(event):
        return True
    monkeypatch.setattr(mod, "_generate_reflection_for_event", fake_gen)

    mod.main()
    first_sentinel = json.loads((tmp_path / "sentinel.json").read_text())
    first_processed = first_sentinel["processed_total"]

    # Run again — already processed this event, should not double-count
    mod.main()
    second_sentinel = json.loads((tmp_path / "sentinel.json").read_text())
    assert second_sentinel["processed_this_run"] == 0


def test_poller_sentinel_tracks_last_event_id(tmp_path, monkeypatch):
    import reflexion_omission_poller as mod
    db = tmp_path / "cieu.db"
    _make_mock_cieu(db, [
        {"event_id": "x001", "event_type": "OMISSION_OVERDUE", "rt_value": 1},
        {"event_id": "x002", "event_type": "OMISSION_OVERDUE", "rt_value": 1},
    ])
    monkeypatch.setattr(mod, "CIEU_DB", db)
    monkeypatch.setattr(mod, "CIEU_MAIN_DB", tmp_path / "no.db")
    monkeypatch.setattr(mod, "SENTINEL", tmp_path / "sentinel.json")
    monkeypatch.setattr(mod, "_generate_reflection_for_event", lambda e: True)

    mod.main()
    sentinel = json.loads((tmp_path / "sentinel.json").read_text())
    assert sentinel["last_event_id"] == "x002"
    assert sentinel["processed_this_run"] == 2


def test_poller_handles_missing_schema_gracefully(tmp_path, monkeypatch):
    """If CIEU table has unexpected schema, poller returns empty list, exit 0."""
    import reflexion_omission_poller as mod
    db = tmp_path / "weird.db"
    conn = sqlite3.connect(str(db))
    conn.execute("CREATE TABLE not_cieu (foo TEXT)")
    conn.commit()
    conn.close()
    results = mod._query_overdue_events(db)
    assert results == []
