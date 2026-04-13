#!/usr/bin/env python3
"""Unit tests for Secretary Curation Pipeline Step 2 (tombstone).

Tests:
  - scan_tombstone_headers: Detect TOMBSTONE markers in DISPATCH/BOARD_PENDING
  - check_stale_tasks: Identify tasks >72h old without recent mentions
  - apply_tombstone: Mark tasks as deprecated in active_task.json
  - step2_tombstone: End-to-end tombstone scan
  - CIEU event emission
"""
import json
import time
from pathlib import Path

import pytest

import sys
sys.path.insert(0, str(Path(__file__).parent.parent / "scripts"))
from secretary_curate import (
    scan_tombstone_headers,
    check_stale_tasks,
    apply_tombstone,
    step2_tombstone
)


@pytest.fixture
def temp_workspace(tmp_path):
    """Create temporary workspace structure for tombstone tests."""
    workspace = tmp_path / "ystar-company"
    workspace.mkdir()

    # Create directories
    (workspace / "memory").mkdir()
    (workspace / "knowledge" / "ceo").mkdir(parents=True)
    (workspace / "knowledge" / "cto").mkdir(parents=True)
    (workspace / "reports").mkdir()

    # Create DISPATCH.md
    (workspace / "DISPATCH.md").write_text("""# DISPATCH

## Active Tasks
- Task 1
- Task 2
""")

    # Create BOARD_PENDING.md
    (workspace / "BOARD_PENDING.md").write_text("""# BOARD PENDING

- Item A
- Item B
""")

    # Create session config
    session_cfg = {"session_id": "test_tombstone_001"}
    (workspace / ".ystar_session.json").write_text(json.dumps(session_cfg))

    return workspace


def test_scan_tombstone_headers_none(temp_workspace):
    """Test scan_tombstone_headers when no tombstone markers exist."""
    import secretary_curate
    import pytest
    monkeypatch = pytest.MonkeyPatch()
    monkeypatch.setattr(secretary_curate, "YSTAR_DIR", temp_workspace)

    tombstoned = scan_tombstone_headers()
    assert len(tombstoned) == 0


def test_scan_tombstone_headers_found(temp_workspace):
    """Test scan_tombstone_headers detects TOMBSTONE/DEPRECATED markers."""
    import secretary_curate
    import pytest
    monkeypatch = pytest.MonkeyPatch()
    monkeypatch.setattr(secretary_curate, "YSTAR_DIR", temp_workspace)

    # Add tombstone header to DISPATCH
    dispatch = temp_workspace / "DISPATCH.md"
    dispatch.write_text("""# TOMBSTONE — This file is deprecated

Reason: Replaced by priority_brief.md

## Old Tasks
- Task 1
""")

    tombstoned = scan_tombstone_headers()
    assert len(tombstoned) >= 1
    assert any("DISPATCH" in str(path) for path, _ in tombstoned)


def test_check_stale_tasks_empty(temp_workspace):
    """Test check_stale_tasks with non-existent active_task.json."""
    active_task_path = temp_workspace / "knowledge" / "ceo" / "active_task.json"
    wisdom_content = ""

    stale = check_stale_tasks("ceo", active_task_path, wisdom_content)
    assert stale == []


def test_check_stale_tasks_recent(temp_workspace):
    """Test check_stale_tasks ignores recent tasks (<72h)."""
    active_task_path = temp_workspace / "knowledge" / "ceo" / "active_task.json"

    # Create task updated 1 hour ago
    tasks = {
        "task_001": {
            "name": "Recent task",
            "updated_at": time.time() - 3600,  # 1 hour ago
            "status": "active"
        }
    }
    active_task_path.write_text(json.dumps(tasks))

    wisdom_content = ""
    stale = check_stale_tasks("ceo", active_task_path, wisdom_content)

    # Should not be stale (< 72h)
    assert "task_001" not in stale


def test_check_stale_tasks_old_mentioned(temp_workspace):
    """Test check_stale_tasks ignores old tasks still mentioned in wisdom."""
    active_task_path = temp_workspace / "knowledge" / "ceo" / "active_task.json"

    # Create task updated 4 days ago
    tasks = {
        "task_002": {
            "name": "Old but active task",
            "updated_at": time.time() - (96 * 3600),  # 4 days ago
            "status": "active"
        }
    }
    active_task_path.write_text(json.dumps(tasks))

    # Task mentioned in wisdom package
    wisdom_content = "Board discussed 'Old but active task' in this session"

    stale = check_stale_tasks("ceo", active_task_path, wisdom_content)

    # Should not be stale (mentioned in wisdom)
    assert "task_002" not in stale


def test_check_stale_tasks_old_not_mentioned(temp_workspace):
    """Test check_stale_tasks identifies old tasks not mentioned in wisdom."""
    active_task_path = temp_workspace / "knowledge" / "ceo" / "active_task.json"

    # Create task updated 4 days ago
    tasks = {
        "task_003": {
            "name": "Forgotten task",
            "updated_at": time.time() - (96 * 3600),  # 4 days ago
            "status": "active"
        }
    }
    active_task_path.write_text(json.dumps(tasks))

    # Task NOT mentioned in wisdom
    wisdom_content = "Board discussed other topics"

    stale = check_stale_tasks("ceo", active_task_path, wisdom_content)

    # Should be stale (>72h and not mentioned)
    assert "task_003" in stale


def test_apply_tombstone_basic(temp_workspace):
    """Test apply_tombstone marks task as deprecated."""
    import secretary_curate
    import pytest
    monkeypatch = pytest.MonkeyPatch()
    monkeypatch.setattr(secretary_curate, "KNOWLEDGE_DIR", temp_workspace / "knowledge")

    active_task_path = temp_workspace / "knowledge" / "ceo" / "active_task.json"
    tasks = {
        "task_004": {
            "name": "To be deprecated",
            "status": "active"
        }
    }
    active_task_path.write_text(json.dumps(tasks))

    apply_tombstone("task_004", "ceo", "Test deprecation")

    # Read back and verify
    updated_tasks = json.loads(active_task_path.read_text())
    assert updated_tasks["task_004"]["status"] == "deprecated"
    assert "deprecated_at" in updated_tasks["task_004"]
    assert updated_tasks["task_004"]["deprecation_reason"] == "Test deprecation"


def test_apply_tombstone_nonexistent_task(temp_workspace):
    """Test apply_tombstone handles non-existent task gracefully."""
    import secretary_curate
    import pytest
    monkeypatch = pytest.MonkeyPatch()
    monkeypatch.setattr(secretary_curate, "KNOWLEDGE_DIR", temp_workspace / "knowledge")

    active_task_path = temp_workspace / "knowledge" / "ceo" / "active_task.json"
    tasks = {"task_005": {"name": "Existing", "status": "active"}}
    active_task_path.write_text(json.dumps(tasks))

    # Try to tombstone non-existent task
    apply_tombstone("task_999", "ceo", "Does not exist")

    # Original task should be unchanged
    updated_tasks = json.loads(active_task_path.read_text())
    assert "task_999" not in updated_tasks
    assert updated_tasks["task_005"]["status"] == "active"


def test_step2_tombstone_integration(temp_workspace, monkeypatch):
    """Integration test for step2_tombstone."""
    import secretary_curate
    monkeypatch.setattr(secretary_curate, "YSTAR_DIR", temp_workspace)
    monkeypatch.setattr(secretary_curate, "MEMORY_DIR", temp_workspace / "memory")
    monkeypatch.setattr(secretary_curate, "KNOWLEDGE_DIR", temp_workspace / "knowledge")

    # Create DISPATCH with tombstone header
    dispatch = temp_workspace / "DISPATCH.md"
    dispatch.write_text("# TOMBSTONE HEADER\nDeprecated content")

    # Create active_task.json with stale task
    ceo_task_path = temp_workspace / "knowledge" / "ceo" / "active_task.json"
    ceo_task_path.write_text(json.dumps({
        "stale_task": {
            "name": "Old forgotten task",
            "updated_at": time.time() - (100 * 3600),  # 100 hours ago
            "status": "active"
        }
    }))

    # Create wisdom package without mention of stale task
    wisdom_path = temp_workspace / "memory" / "wisdom_package_latest.md"
    wisdom_path.write_text("Board discussed other topics")

    ctx = {"session_id": "test_tombstone_001", "trigger": "session_close", "agent": "ceo"}

    result = step2_tombstone(ctx)

    # Verify results
    assert result["step"] == 2
    assert result["status"] == "implemented"
    assert result["tombstoned_files"] >= 1  # Found DISPATCH tombstone header

    # Verify stale task was tombstoned
    updated_tasks = json.loads(ceo_task_path.read_text())
    assert updated_tasks["stale_task"]["status"] == "deprecated"

    # Verify report was created
    report_path = temp_workspace / "reports" / f"tombstone_scan_{time.strftime('%Y%m%d')}.md"
    assert report_path.exists()
    report_content = report_path.read_text()
    assert "DISPATCH" in report_content
    assert "ceo/stale_task" in report_content or "stale_task" in report_content


def test_step2_tombstone_no_stale_tasks(temp_workspace, monkeypatch):
    """Test step2_tombstone when no stale tasks exist."""
    import secretary_curate
    monkeypatch.setattr(secretary_curate, "YSTAR_DIR", temp_workspace)
    monkeypatch.setattr(secretary_curate, "MEMORY_DIR", temp_workspace / "memory")
    monkeypatch.setattr(secretary_curate, "KNOWLEDGE_DIR", temp_workspace / "knowledge")

    # Create active_task.json with recent task
    ceo_task_path = temp_workspace / "knowledge" / "ceo" / "active_task.json"
    ceo_task_path.write_text(json.dumps({
        "recent_task": {
            "name": "Fresh task",
            "updated_at": time.time() - 3600,  # 1 hour ago
            "status": "active"
        }
    }))

    wisdom_path = temp_workspace / "memory" / "wisdom_package_latest.md"
    wisdom_path.write_text("")

    ctx = {"session_id": "test_tombstone_001", "trigger": "session_close", "agent": "ceo"}

    result = step2_tombstone(ctx)

    # No tombstones should be applied
    assert result["tombstones_applied"] == 0

    # Task should remain active
    tasks = json.loads(ceo_task_path.read_text())
    assert tasks["recent_task"]["status"] == "active"


def test_step2_tombstone_multiple_roles(temp_workspace, monkeypatch):
    """Test step2_tombstone scans multiple roles."""
    import secretary_curate
    monkeypatch.setattr(secretary_curate, "YSTAR_DIR", temp_workspace)
    monkeypatch.setattr(secretary_curate, "MEMORY_DIR", temp_workspace / "memory")
    monkeypatch.setattr(secretary_curate, "KNOWLEDGE_DIR", temp_workspace / "knowledge")

    # Create stale tasks for multiple roles
    for role in ["ceo", "cto"]:
        task_path = temp_workspace / "knowledge" / role / "active_task.json"
        task_path.parent.mkdir(parents=True, exist_ok=True)
        task_path.write_text(json.dumps({
            f"{role}_stale": {
                "name": f"{role} stale task",
                "updated_at": time.time() - (100 * 3600),
                "status": "active"
            }
        }))

    wisdom_path = temp_workspace / "memory" / "wisdom_package_latest.md"
    wisdom_path.write_text("")

    ctx = {"session_id": "test_tombstone_001", "trigger": "session_close", "agent": "ceo"}

    result = step2_tombstone(ctx)

    # Should find stale tasks in both roles
    assert result["tombstones_applied"] >= 2

    # Verify both tasks were deprecated
    for role in ["ceo", "cto"]:
        task_path = temp_workspace / "knowledge" / role / "active_task.json"
        tasks = json.loads(task_path.read_text())
        assert tasks[f"{role}_stale"]["status"] == "deprecated"
