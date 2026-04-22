"""Test: PreToolUse OmissionEngine enforcement hook.

Live-fire pattern: create test DB with deliberate overdue obligation → hook stdin prompt
→ assert exit 1 + block JSON in stdout.
"""
import json
import os
import sqlite3
import subprocess
import sys
import time
import tempfile
from pathlib import Path
import pytest

HOOK = Path("/Users/haotianliu/.openclaw/workspace/ystar-company/scripts/hook_omission_enforce_pretool.py")


def _make_obligation_db(db_path: Path, entries: list[dict]) -> None:
    conn = sqlite3.connect(str(db_path))
    conn.execute("""
        CREATE TABLE obligations (
            obligation_id TEXT PRIMARY KEY,
            actor_id TEXT,
            status TEXT,
            due_at REAL,
            hard_overdue_secs REAL,
            violation_code TEXT,
            notes TEXT
        )
    """)
    for e in entries:
        conn.execute(
            "INSERT INTO obligations VALUES (?,?,?,?,?,?,?)",
            (e["obligation_id"], e["actor_id"], e.get("status", "pending"),
             e.get("due_at", time.time()), e.get("hard_overdue_secs", 0),
             e.get("violation_code", ""), e.get("notes", ""))
        )
    conn.commit()
    conn.close()


def _run_hook(tool_name: str, env_overrides: dict = None) -> subprocess.CompletedProcess:
    env = os.environ.copy()
    if env_overrides:
        env.update(env_overrides)
    return subprocess.run(
        ["python3.11", str(HOOK)],
        input=json.dumps({"tool_name": tool_name}),
        capture_output=True, text=True, timeout=10, env=env,
    )


def test_hook_allow_on_read_tool():
    """Read is in allowlist — always allow regardless of obligations."""
    r = _run_hook("Read")
    assert r.returncode == 0


def test_hook_allow_on_grep_tool():
    r = _run_hook("Grep")
    assert r.returncode == 0


def test_hook_deny_when_overdue_obligation(tmp_path, monkeypatch):
    """Live-fire: create overdue obligation → hook denies Write."""
    import importlib
    sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    import hook_omission_enforce_pretool as mod

    db = tmp_path / "omission.db"
    _make_obligation_db(db, [{
        "obligation_id": "overdue_001",
        "actor_id": "ceo",
        "status": "pending",
        "due_at": time.time() - 3600,  # 1 hour ago
        "hard_overdue_secs": 60,
        "violation_code": "test_overdue",
        "notes": "live-fire test",
    }])
    active_agent = tmp_path / "agent"
    active_agent.write_text("ceo\n")
    ceo_mode = tmp_path / "no_bg.json"

    monkeypatch.setattr(mod, "OMISSION_DB", db)
    monkeypatch.setattr(mod, "ACTIVE_AGENT_FILE", active_agent)
    monkeypatch.setattr(mod, "CEO_MODE_STATE", ceo_mode)

    # Invoke via function directly (not subprocess, for speed + monkeypatch)
    import io
    old_stdin = sys.stdin
    sys.stdin = io.StringIO(json.dumps({"tool_name": "Write"}))
    try:
        rc = mod.main()
    finally:
        sys.stdin = old_stdin
    assert rc == 1  # deny


def test_hook_allow_when_no_overdue(tmp_path, monkeypatch):
    import hook_omission_enforce_pretool as mod

    db = tmp_path / "omission.db"
    _make_obligation_db(db, [{
        "obligation_id": "future_001",
        "actor_id": "ceo",
        "status": "pending",
        "due_at": time.time() + 3600,  # 1h in future
        "hard_overdue_secs": 0,
    }])
    active_agent = tmp_path / "agent"
    active_agent.write_text("ceo\n")
    ceo_mode = tmp_path / "no_bg.json"

    monkeypatch.setattr(mod, "OMISSION_DB", db)
    monkeypatch.setattr(mod, "ACTIVE_AGENT_FILE", active_agent)
    monkeypatch.setattr(mod, "CEO_MODE_STATE", ceo_mode)

    import io
    old_stdin = sys.stdin
    sys.stdin = io.StringIO(json.dumps({"tool_name": "Write"}))
    try:
        rc = mod.main()
    finally:
        sys.stdin = old_stdin
    assert rc == 0  # allow


def test_hook_allow_when_break_glass_active(tmp_path, monkeypatch):
    """Break-glass overrides even overdue obligations (emergency exit)."""
    import hook_omission_enforce_pretool as mod

    db = tmp_path / "omission.db"
    _make_obligation_db(db, [{
        "obligation_id": "overdue_bg",
        "actor_id": "ceo",
        "status": "pending",
        "due_at": time.time() - 9999,
        "hard_overdue_secs": 0,
    }])
    active_agent = tmp_path / "agent"
    active_agent.write_text("ceo\n")
    ceo_mode = tmp_path / "bg.json"
    ceo_mode.write_text(json.dumps({
        "mode": "BREAK_GLASS",
        "hard_cap_expires_at": time.time() + 600,
    }))

    monkeypatch.setattr(mod, "OMISSION_DB", db)
    monkeypatch.setattr(mod, "ACTIVE_AGENT_FILE", active_agent)
    monkeypatch.setattr(mod, "CEO_MODE_STATE", ceo_mode)

    import io
    old_stdin = sys.stdin
    sys.stdin = io.StringIO(json.dumps({"tool_name": "Write"}))
    try:
        rc = mod.main()
    finally:
        sys.stdin = old_stdin
    assert rc == 0  # allow (BG override)


def test_hook_fail_open_when_db_missing(tmp_path, monkeypatch):
    """If DB missing, hook must fail-open (allow) to prevent bricking session."""
    import hook_omission_enforce_pretool as mod

    monkeypatch.setattr(mod, "OMISSION_DB", tmp_path / "nope.db")
    monkeypatch.setattr(mod, "ACTIVE_AGENT_FILE", tmp_path / "agent")
    (tmp_path / "agent").write_text("ceo\n")
    monkeypatch.setattr(mod, "CEO_MODE_STATE", tmp_path / "nobg.json")

    import io
    old_stdin = sys.stdin
    sys.stdin = io.StringIO(json.dumps({"tool_name": "Write"}))
    try:
        rc = mod.main()
    finally:
        sys.stdin = old_stdin
    assert rc == 0  # fail-open


def test_hook_allows_unknown_agent(tmp_path, monkeypatch):
    """Agent not in ENFORCED_AGENTS (e.g. path_a_agent) — allow (not our scope)."""
    import hook_omission_enforce_pretool as mod

    db = tmp_path / "omission.db"
    _make_obligation_db(db, [{
        "obligation_id": "o",
        "actor_id": "path_a_agent",  # synthetic
        "status": "pending",
        "due_at": time.time() - 100,
        "hard_overdue_secs": 0,
    }])
    active_agent = tmp_path / "agent"
    active_agent.write_text("path_a_agent\n")
    ceo_mode = tmp_path / "nobg.json"

    monkeypatch.setattr(mod, "OMISSION_DB", db)
    monkeypatch.setattr(mod, "ACTIVE_AGENT_FILE", active_agent)
    monkeypatch.setattr(mod, "CEO_MODE_STATE", ceo_mode)

    import io
    old_stdin = sys.stdin
    sys.stdin = io.StringIO(json.dumps({"tool_name": "Write"}))
    try:
        rc = mod.main()
    finally:
        sys.stdin = old_stdin
    assert rc == 0
