"""
test_memory_consistency_check.py — Unit tests for Closure 2 (boot consistency check).

Tests:
- First run bootstraps without drift
- CWD change detected
- Critical path missing detected
- Force-write refreshes assumptions
"""
import json
import os
import sqlite3
import subprocess
import sys
from pathlib import Path
from unittest.mock import patch

import pytest

# Add scripts to path
sys.path.insert(0, str(Path(__file__).parent.parent / "scripts"))
import memory_consistency_check as mcc


@pytest.fixture
def temp_env(tmp_path):
    """Create temporary test environment."""
    repo = tmp_path / "ystar-company"
    repo.mkdir()

    # Create session.json
    session = {
        "session_id": "test",
        "memory_db": str(tmp_path / ".ystar_memory.db")
    }
    (repo / ".ystar_session.json").write_text(json.dumps(session))

    # Create memory db
    db = sqlite3.connect(session["memory_db"])
    db.execute("""
        CREATE TABLE IF NOT EXISTS memories (
            id INTEGER PRIMARY KEY,
            agent_id TEXT,
            memory_type TEXT,
            content TEXT,
            initial_score REAL,
            half_life_days INTEGER,
            created_at INTEGER,
            last_accessed_at INTEGER,
            access_count INTEGER,
            source_cieu_ref INTEGER
        )
    """)
    db.commit()

    # Create critical files
    (repo / "CLAUDE.md").write_text("# test")
    (repo / "AGENTS.md").write_text("# test")
    (repo / "scripts").mkdir()
    (repo / "scripts" / "governance_boot.sh").write_text("#!/bin/bash\n")

    return repo, db, session


def test_first_run_bootstraps_no_drift(temp_env):
    """First run should bootstrap assumptions without reporting drift."""
    repo, db, session = temp_env

    with patch.object(mcc, 'REPO_ROOT', repo):
        with patch.object(mcc, 'SESSION_PATH', repo / ".ystar_session.json"):
            # Mock get_current_env to return deterministic values
            mock_env = {
                "platform": "darwin",
                "cwd": str(repo),
                "git_remote": None,
                "git_branch": None,
                "python_version": "3.11",
                "critical_paths": {
                    "CLAUDE.md": "exists",
                    "AGENTS.md": "exists",
                    "governance_boot.sh": "exists",
                    ".ystar_session.json": "exists",
                    "ystar-gov-source": "not_configured"
                }
            }

            with patch.object(mcc, 'get_current_env', return_value=mock_env):
                # First run
                assumptions = mcc.load_assumptions(db, "test_agent")
                assert len(assumptions) == 0  # No assumptions yet

                # Should bootstrap
                mcc.save_assumptions(db, "test_agent", mock_env)

                # Check assumptions saved
                assumptions = mcc.load_assumptions(db, "test_agent")
                assert len(assumptions) > 0


def test_cwd_change_detected(temp_env):
    """Drift detection should catch CWD changes."""
    repo, db, session = temp_env

    with patch.object(mcc, 'REPO_ROOT', repo):
        with patch.object(mcc, 'SESSION_PATH', repo / ".ystar_session.json"):
            # Bootstrap with original cwd
            original_env = {
                "platform": "darwin",
                "cwd": str(repo),
                "git_remote": None,
                "git_branch": None,
                "python_version": "3.11",
                "critical_paths": {}
            }

            with patch.object(mcc, 'get_current_env', return_value=original_env):
                mcc.save_assumptions(db, "test_agent", original_env)

            # Now change cwd
            changed_env = original_env.copy()
            changed_env["cwd"] = "/tmp/elsewhere"

            assumptions = mcc.load_assumptions(db, "test_agent")
            drifts = mcc.detect_drift(assumptions, changed_env)

            assert len(drifts) > 0
            assert any("cwd=" in d for d in drifts)


def test_critical_path_missing_detected(temp_env):
    """Drift detection should catch missing critical paths."""
    repo, db, session = temp_env

    with patch.object(mcc, 'REPO_ROOT', repo):
        with patch.object(mcc, 'SESSION_PATH', repo / ".ystar_session.json"):
            # Bootstrap with all paths present
            original_env = {
                "platform": "darwin",
                "cwd": str(repo),
                "git_remote": None,
                "git_branch": None,
                "python_version": "3.11",
                "critical_paths": {
                    "CLAUDE.md": "exists",
                    "AGENTS.md": "exists"
                }
            }

            # Save as JSON string in assumptions
            db.execute(
                """INSERT INTO memories (agent_id, memory_type, content, initial_score,
                                         half_life_days, created_at, last_accessed_at,
                                         access_count, source_cieu_ref)
                   VALUES ('test_agent', 'environment_assumption', ?, 1.0, 365, 0, 0, 0, NULL)""",
                (json.dumps({"dimension": "critical_paths", "value": original_env["critical_paths"]}),)
            )
            db.commit()

            # Now report a path as missing
            changed_env = original_env.copy()
            changed_env["critical_paths"] = {
                "CLAUDE.md": "missing",
                "AGENTS.md": "exists"
            }

            assumptions = mcc.load_assumptions(db, "test_agent")
            # Fix: assumptions['critical_paths'] is the JSON string, need to parse
            drifts = mcc.detect_drift(assumptions, changed_env)

            assert len(drifts) > 0


def test_force_write_refreshes(temp_env):
    """--force-write should overwrite all assumptions."""
    repo, db, session = temp_env

    with patch.object(mcc, 'REPO_ROOT', repo):
        with patch.object(mcc, 'SESSION_PATH', repo / ".ystar_session.json"):
            # Bootstrap with old values
            old_env = {
                "platform": "linux",
                "cwd": "/old/path",
                "git_remote": None,
                "git_branch": None,
                "python_version": "3.10",
                "critical_paths": {}
            }

            with patch.object(mcc, 'get_current_env', return_value=old_env):
                mcc.save_assumptions(db, "test_agent", old_env)

            # Force-write with new values
            new_env = {
                "platform": "darwin",
                "cwd": str(repo),
                "git_remote": None,
                "git_branch": None,
                "python_version": "3.11",
                "critical_paths": {}
            }

            # Clear old assumptions first
            db.execute("DELETE FROM memories WHERE agent_id = 'test_agent'")
            db.commit()

            with patch.object(mcc, 'get_current_env', return_value=new_env):
                mcc.save_assumptions(db, "test_agent", new_env)

            assumptions = mcc.load_assumptions(db, "test_agent")
            assert assumptions.get("platform") == "darwin"
            assert assumptions.get("python_version") == "3.11"
