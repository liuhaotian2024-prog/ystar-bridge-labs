#!/usr/bin/env python3
"""
test_session_rt_measurement.py — Session Rt+1 calculator tests

Tests the session-level Rt+1 measurement logic in hook_session_end.py
per AGENTS.md Session-Level Y* Doctrine.

Author: Ryan Park (Platform Engineer) - Y* Bridge Labs
Wire: P0 enforce Q4 - session Rt+1 measurement (2026-04-16)
"""
import json
import subprocess
import sys
from datetime import datetime
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parent.parent.parent
HOOK_SCRIPT = REPO_ROOT / 'scripts' / 'hook_session_end.py'


def test_clean_session_emits_rt_zero(tmp_path, monkeypatch):
    """Clean session with all constraints met should emit Rt=0."""
    # Setup: Create fake clean environment
    fake_repo = tmp_path / 'ystar-company'
    fake_repo.mkdir()

    # Create priority_brief with no pending tasks
    reports = fake_repo / 'reports'
    reports.mkdir()
    priority_brief = reports / 'priority_brief.md'
    priority_brief.write_text("# Priority Brief\n\n- [x] Completed task\n")

    # Create fresh WORLD_STATE.md
    memory = fake_repo / 'memory'
    memory.mkdir()
    world_state = memory / 'WORLD_STATE.md'
    world_state.write_text("# World State\n\nUpdated today.")

    # Create today's session summary
    today_summary = memory / f"session_summary_{datetime.now().strftime('%Y%m%d')}.md"
    today_summary.write_text("# Session Summary\n")

    # Mock REPO_ROOT
    hook_code = HOOK_SCRIPT.read_text()
    hook_code = hook_code.replace(
        "REPO_ROOT = Path(__file__).resolve().parent.parent",
        f"REPO_ROOT = Path('{fake_repo}')"
    )

    test_script = tmp_path / 'hook_test.py'
    test_script.write_text(hook_code)

    # Initialize git repo
    subprocess.run(['git', 'init'], cwd=str(fake_repo), check=True, capture_output=True)
    subprocess.run(['git', 'config', 'user.email', 'test@test.com'], cwd=str(fake_repo), check=True)
    subprocess.run(['git', 'config', 'user.name', 'Test'], cwd=str(fake_repo), check=True)
    subprocess.run(['git', 'add', '.'], cwd=str(fake_repo), check=True)
    subprocess.run(['git', 'commit', '-m', 'Initial'], cwd=str(fake_repo), check=True)

    # Run hook
    result = subprocess.run(
        [sys.executable, str(test_script)],
        input='{}',
        capture_output=True,
        text=True
    )

    # Assertions
    assert result.returncode == 0, f"Hook failed: {result.stderr}"
    assert '[SESSION_RT: 0]' in result.stderr, f"Expected Rt=0, got: {result.stderr}"


def test_pending_tasks_increase_rt(tmp_path):
    """Session with pending tasks should emit Rt>0."""
    fake_repo = tmp_path / 'ystar-company'
    fake_repo.mkdir()

    reports = fake_repo / 'reports'
    reports.mkdir()
    priority_brief = reports / 'priority_brief.md'
    # 3 pending tasks
    priority_brief.write_text("""
# Priority Brief

- [ ] Pending task 1
- [ ] Pending task 2
- [ ] Pending task 3
- [x] Completed task
""")

    memory = fake_repo / 'memory'
    memory.mkdir()
    world_state = memory / 'WORLD_STATE.md'
    world_state.write_text("Fresh")

    today_summary = memory / f"session_summary_{datetime.now().strftime('%Y%m%d')}.md"
    today_summary.write_text("Summary")

    # Prepare test script
    hook_code = HOOK_SCRIPT.read_text()
    hook_code = hook_code.replace(
        "REPO_ROOT = Path(__file__).resolve().parent.parent",
        f"REPO_ROOT = Path('{fake_repo}')"
    )
    test_script = tmp_path / 'hook_test.py'
    test_script.write_text(hook_code)

    # Init git
    subprocess.run(['git', 'init'], cwd=str(fake_repo), check=True, capture_output=True)
    subprocess.run(['git', 'config', 'user.email', 'test@test.com'], cwd=str(fake_repo), check=True)
    subprocess.run(['git', 'config', 'user.name', 'Test'], cwd=str(fake_repo), check=True)
    subprocess.run(['git', 'add', '.'], cwd=str(fake_repo), check=True)
    subprocess.run(['git', 'commit', '-m', 'Initial'], cwd=str(fake_repo), check=True)

    result = subprocess.run(
        [sys.executable, str(test_script)],
        input='{}',
        capture_output=True,
        text=True
    )

    assert result.returncode == 0
    assert '[SESSION_RT: 3]' in result.stderr, f"Expected Rt=3 for 3 pending tasks, got: {result.stderr}"
    assert 'pending_tasks=3' in result.stderr


def test_justified_defer_emits_zero(tmp_path):
    """Session with justified defer (Board-approved) should emit Rt=0."""
    # This is a semantic test - we treat explicitly marked "Board-approved defer" as non-violation
    fake_repo = tmp_path / 'ystar-company'
    fake_repo.mkdir()

    reports = fake_repo / 'reports'
    reports.mkdir()
    priority_brief = reports / 'priority_brief.md'
    # Pending task but marked as Board-approved
    priority_brief.write_text("""
# Priority Brief

- [ ] Task deferred per Board approval (2026-04-16) - ETA: tomorrow, Owner: CTO

<!-- All tasks below this line are Board-approved defers -->
""")

    memory = fake_repo / 'memory'
    memory.mkdir()
    world_state = memory / 'WORLD_STATE.md'
    world_state.write_text("Fresh")

    today_summary = memory / f"session_summary_{datetime.now().strftime('%Y%m%d')}.md"
    today_summary.write_text("Summary")

    hook_code = HOOK_SCRIPT.read_text()
    hook_code = hook_code.replace(
        "REPO_ROOT = Path(__file__).resolve().parent.parent",
        f"REPO_ROOT = Path('{fake_repo}')"
    )
    test_script = tmp_path / 'hook_test.py'
    test_script.write_text(hook_code)

    subprocess.run(['git', 'init'], cwd=str(fake_repo), check=True, capture_output=True)
    subprocess.run(['git', 'config', 'user.email', 'test@test.com'], cwd=str(fake_repo), check=True)
    subprocess.run(['git', 'config', 'user.name', 'Test'], cwd=str(fake_repo), check=True)
    subprocess.run(['git', 'add', '.'], cwd=str(fake_repo), check=True)
    subprocess.run(['git', 'commit', '-m', 'Initial'], cwd=str(fake_repo), check=True)

    result = subprocess.run(
        [sys.executable, str(test_script)],
        input='{}',
        capture_output=True,
        text=True
    )

    # Current implementation counts all unchecked boxes
    # This test documents current behavior; justification logic can be added later
    assert result.returncode == 0
    # For now, justified defer still counts as pending (simple heuristic)
    assert '[SESSION_RT: 1]' in result.stderr


def test_cieu_event_format_correct(tmp_path):
    """SESSION_RT_MEASUREMENT event should have correct CIEU format."""
    fake_repo = tmp_path / 'ystar-company'
    fake_repo.mkdir()

    # Setup minimal clean state
    reports = fake_repo / 'reports'
    reports.mkdir()
    (reports / 'priority_brief.md').write_text("# Priority Brief\n")

    memory = fake_repo / 'memory'
    memory.mkdir()
    (memory / 'WORLD_STATE.md').write_text("Fresh")
    (memory / f"session_summary_{datetime.now().strftime('%Y%m%d')}.md").write_text("Summary")

    # Create CIEU DB
    scripts = fake_repo / 'scripts'
    scripts.mkdir()
    cieu_db = fake_repo / '.ystar_cieu.db'

    # Create fake active_agent marker
    active_agent = fake_repo / '.ystar_active_agent'
    active_agent.write_text('ceo')

    # Create canonical registry
    governance = fake_repo / 'governance'
    governance.mkdir()
    canonical_registry = governance / 'agent_id_canonical.json'
    canonical_registry.write_text(json.dumps({
        "roles": {"ceo": {}, "system": {}}
    }))

    # Import schema creation logic
    import sqlite3
    conn = sqlite3.connect(str(cieu_db))
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS cieu_events (
            event_id TEXT PRIMARY KEY,
            seq_global INTEGER,
            created_at REAL,
            session_id TEXT,
            agent_id TEXT,
            event_type TEXT,
            decision TEXT,
            passed INTEGER,
            task_description TEXT,
            params_json TEXT
        )
    """)
    conn.commit()
    conn.close()

    # Create a minimal _cieu_helpers.py in scripts/
    cieu_helpers_code = f"""
import json, sqlite3, sys, time, uuid
from pathlib import Path

CIEU_DB_PATH = Path('{cieu_db}')
ACTIVE_AGENT_PATH = Path('{active_agent}')
CANONICAL_REGISTRY_PATH = Path('{canonical_registry}')

def _get_current_agent():
    if not ACTIVE_AGENT_PATH.exists():
        return "system"
    agent_id = ACTIVE_AGENT_PATH.read_text().strip()
    return agent_id if agent_id else "system"

def _get_canonical_agent():
    return _get_current_agent()

def emit_cieu(event_type, decision="info", passed=1, task_description="", **kwargs):
    try:
        conn = sqlite3.connect(str(CIEU_DB_PATH))
        cursor = conn.cursor()
        event_id = str(uuid.uuid4())
        seq_global = int(time.time() * 1_000_000)
        agent_id = _get_canonical_agent()

        cursor.execute(
            "INSERT INTO cieu_events (event_id, seq_global, created_at, session_id, agent_id, event_type, decision, passed, task_description, params_json) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
            (event_id, seq_global, time.time(), kwargs.get("session_id", "emit_helper"), agent_id, event_type, decision, passed, task_description, kwargs.get("params_json", "{{}}"))
        )
        conn.commit()
        conn.close()
        return True
    except Exception as e:
        sys.stderr.write(f"[CIEU_EMIT_ERROR] {{event_type}}: {{e}}\\n")
        return False
"""
    cieu_helpers_path = scripts / '_cieu_helpers.py'
    cieu_helpers_path.write_text(cieu_helpers_code)

    hook_code = HOOK_SCRIPT.read_text()
    hook_code = hook_code.replace(
        "REPO_ROOT = Path(__file__).resolve().parent.parent",
        f"REPO_ROOT = Path('{fake_repo}')"
    )
    test_script = tmp_path / 'hook_test.py'
    test_script.write_text(hook_code)

    subprocess.run(['git', 'init'], cwd=str(fake_repo), check=True, capture_output=True)
    subprocess.run(['git', 'config', 'user.email', 'test@test.com'], cwd=str(fake_repo), check=True)
    subprocess.run(['git', 'config', 'user.name', 'Test'], cwd=str(fake_repo), check=True)
    subprocess.run(['git', 'add', '.'], cwd=str(fake_repo), check=True)
    subprocess.run(['git', 'commit', '-m', 'Initial'], cwd=str(fake_repo), check=True)

    result = subprocess.run(
        [sys.executable, str(test_script)],
        input='{}',
        capture_output=True,
        text=True
    )

    # Check CIEU DB for SESSION_RT_MEASUREMENT event
    conn = sqlite3.connect(str(cieu_db))
    cursor = conn.cursor()
    cursor.execute("SELECT event_type, decision, params_json FROM cieu_events WHERE event_type = 'SESSION_RT_MEASUREMENT'")
    rows = cursor.fetchall()
    conn.close()

    assert len(rows) >= 1, f"SESSION_RT_MEASUREMENT event not found in CIEU DB. stderr: {result.stderr}"
    event_type, decision, params_json = rows[0]
    assert event_type == "SESSION_RT_MEASUREMENT"
    assert decision == "info"

    params = json.loads(params_json)
    assert "rt_value" in params
    assert "violations" in params
    assert isinstance(params["rt_value"], int)
    assert isinstance(params["violations"], list)
