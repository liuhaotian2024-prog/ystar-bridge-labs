#!/usr/bin/env python3
"""
test_forget_guard_and_logic.py — Forget Guard AND/OR Logic Tests
=================================================================

Validates Maya's fix for OR-bug (W16 附加任务):
- CEO writing AGENTS.md in normal mode → DENY (AND logic: all 3 conditions match)
- CEO writing AGENTS.md in break_glass mode → ALLOW (AND fails: ceo_mode mismatch)
- CTO writing AGENTS.md → ALLOW (AND fails: active_agent mismatch)

This ensures `logic: AND` in yaml + evaluate_rule correctly enforce ALL conditions.
"""
import json
import os
import sys
import tempfile
from pathlib import Path

import pytest


@pytest.fixture
def temp_env():
    """Create temp environment with .ystar_active_agent and .ystar_session.json"""
    with tempfile.TemporaryDirectory() as tmpdir:
        orig_cwd = os.getcwd()
        os.chdir(tmpdir)

        # Create minimal session file
        session_data = {
            "session_id": "test_forget_guard",
            "ceo_mode": {"status": "normal"},
        }
        Path(".ystar_session.json").write_text(json.dumps(session_data))

        # Create minimal CIEU DB (forget_guard checks existence)
        import sqlite3
        conn = sqlite3.connect(".ystar_cieu.db")
        c = conn.cursor()
        c.execute("""
            CREATE TABLE IF NOT EXISTS cieu_events (
                event_id TEXT PRIMARY KEY,
                seq_global INTEGER,
                created_at REAL,
                session_id TEXT,
                agent_id TEXT,
                event_type TEXT,
                decision TEXT,
                passed INTEGER,
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

        # Copy forget_guard_rules.yaml to temp dir (preserve governance/ structure)
        rules_src = Path(orig_cwd) / "governance" / "forget_guard_rules.yaml"
        if rules_src.exists():
            import shutil
            gov_dir = Path(tmpdir) / "governance"
            gov_dir.mkdir(exist_ok=True)
            shutil.copy(rules_src, gov_dir / "forget_guard_rules.yaml")

        yield tmpdir

        os.chdir(orig_cwd)


def run_forget_guard(payload: dict) -> dict:
    """Run forget_guard.py with given payload, return JSON result"""
    # Import forget_guard module
    import sys
    from pathlib import Path

    # Add scripts/ to path
    scripts_dir = Path(__file__).parent.parent / "scripts"
    if str(scripts_dir) not in sys.path:
        sys.path.insert(0, str(scripts_dir))

    # Import the module
    import forget_guard

    # Mock stdin
    import io
    original_stdin = sys.stdin
    sys.stdin = io.StringIO(json.dumps(payload))

    # Capture stdout
    import io
    original_stdout = sys.stdout
    sys.stdout = io.StringIO()

    try:
        forget_guard.main()
        output = sys.stdout.getvalue()
    except SystemExit:
        # forget_guard.main() calls sys.exit(0), capture output before exit
        output = sys.stdout.getvalue()
    finally:
        sys.stdin = original_stdin
        sys.stdout = original_stdout

    # Parse JSON output
    try:
        result = json.loads(output.strip())
    except json.JSONDecodeError:
        result = {"action": "error", "output": output}

    return result


def test_ceo_normal_write_agents_md_deny(temp_env):
    """
    Case 1: CEO writing AGENTS.md in normal mode → DENY

    All 3 AND conditions match:
    - path_match: AGENTS.md ✓
    - active_agent_equals: ceo ✓
    - ceo_mode_not_equals: break_glass ✓ (mode is normal)

    Expected: rule triggered, action=deny
    """
    # Set active agent to CEO
    Path(".ystar_active_agent").write_text("ceo")

    payload = {
        "tool": "Edit",
        "tool_name": "Edit",
        "file_path": "/Users/test/ystar-company/AGENTS.md",
        "old_string": "foo",
        "new_string": "bar",
    }

    result = run_forget_guard(payload)

    # Verify action is warn or deny (not allow)
    assert result["action"] in ("warn", "deny"), \
        f"Expected warn/deny when CEO edits AGENTS.md in normal mode, got {result}"

    # Verify immutable_no_break_glass rule specifically triggered (AND logic)
    assert "immutable_no_break_glass" in result.get("rules_triggered", []), \
        f"Expected immutable_no_break_glass rule to trigger. Got: {result.get('rules_triggered', [])}"


def test_ceo_break_glass_write_agents_md_allow(temp_env):
    """
    Case 2: CEO writing AGENTS.md in break_glass mode → immutable_no_break_glass does NOT trigger

    AND conditions check:
    - path_match: AGENTS.md ✓
    - active_agent_equals: ceo ✓
    - ceo_mode_not_equals: break_glass ✗ (mode IS break_glass)

    Expected: immutable_no_break_glass rule NOT triggered (AND logic: one condition failed)

    Note: OTHER rules may still fire (ceo_engineering_boundary, etc.), but we're testing
    that the AND logic specifically prevents immutable_no_break_glass from firing.
    """
    # Set active agent to CEO
    Path(".ystar_active_agent").write_text("ceo")

    # Set CEO mode to break_glass
    session_data = {
        "session_id": "test_forget_guard",
        "ceo_mode": {"status": "break_glass"},
    }
    Path(".ystar_session.json").write_text(json.dumps(session_data))

    payload = {
        "tool": "Edit",
        "tool_name": "Edit",
        "file_path": "/Users/test/ystar-company/AGENTS.md",
        "old_string": "foo",
        "new_string": "bar",
    }

    result = run_forget_guard(payload)

    # Verify immutable_no_break_glass specifically did NOT trigger (AND logic worked)
    assert "immutable_no_break_glass" not in result.get("rules_triggered", []), \
        f"Expected immutable_no_break_glass NOT to trigger in break_glass mode. Got: {result.get('rules_triggered', [])}"


def test_cto_write_agents_md_allow(temp_env):
    """
    Case 3: CTO writing AGENTS.md → immutable_no_break_glass does NOT trigger

    AND conditions check:
    - path_match: AGENTS.md ✓
    - active_agent_equals: ceo ✗ (agent is cto, not ceo)
    - ceo_mode_not_equals: break_glass ✓

    Expected: immutable_no_break_glass rule NOT triggered (AND logic: one condition failed)
    """
    # Set active agent to CTO
    Path(".ystar_active_agent").write_text("cto")

    payload = {
        "tool": "Edit",
        "tool_name": "Edit",
        "file_path": "/Users/test/ystar-company/AGENTS.md",
        "old_string": "foo",
        "new_string": "bar",
    }

    result = run_forget_guard(payload)

    # Verify immutable_no_break_glass specifically did NOT trigger (AND logic: agent mismatch)
    assert "immutable_no_break_glass" not in result.get("rules_triggered", []), \
        f"Expected immutable_no_break_glass NOT to trigger for CTO. Got: {result.get('rules_triggered', [])}"


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
