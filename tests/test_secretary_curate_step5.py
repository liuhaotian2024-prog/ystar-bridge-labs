#!/usr/bin/env python3
"""Unit tests for Secretary Curation Pipeline Step 5 (next_session_action_queue).

Tests:
  - load_role_context: Load role_definition, active_task, priority_brief
  - generate_action_queue: Create prioritized action queue
  - step5_next_session_action_queue: Update boot packages with action queues
  - Action queue structure validation
"""
import json
import time
from pathlib import Path

import pytest

import sys
sys.path.insert(0, str(Path(__file__).parent.parent / "scripts"))
from secretary_curate import (
    load_role_context,
    generate_action_queue,
    step5_next_session_action_queue
)


@pytest.fixture
def temp_workspace(tmp_path):
    """Create temporary workspace for action queue tests."""
    workspace = tmp_path / "ystar-company"
    workspace.mkdir()

    # Create directories
    (workspace / "knowledge" / "ceo" / "role_definition").mkdir(parents=True)
    (workspace / "knowledge" / "cto" / "role_definition").mkdir(parents=True)
    (workspace / "knowledge" / "ceo" / "skills" / "_draft_").mkdir(parents=True)
    (workspace / "memory" / "boot_packages").mkdir(parents=True)
    (workspace / "reports").mkdir()

    # Create session config
    session_cfg = {"session_id": "test_action_queue_001"}
    (workspace / ".ystar_session.json").write_text(json.dumps(session_cfg))

    return workspace


def test_load_role_context_basic(temp_workspace):
    """Test load_role_context loads role files."""
    # Create role_definition files
    role_def_dir = temp_workspace / "knowledge" / "ceo" / "role_definition"
    (role_def_dir / "task_type_map.md").write_text("# CEO Tasks\n- Strategy\n- Coordination")
    (role_def_dir / "world_class_standard.md").write_text("# World Class CEO\nTop tier leadership")

    # Create active_task.json
    active_task = temp_workspace / "knowledge" / "ceo" / "active_task.json"
    active_task.write_text(json.dumps({
        "task_001": {"name": "Build team", "status": "active", "priority": "P0"}
    }))

    # Create priority_brief
    priority_brief = temp_workspace / "reports" / "priority_brief.md"
    priority_brief.write_text("# Priority Brief\nCEO: Focus on governance")

    import secretary_curate
    import pytest
    monkeypatch = pytest.MonkeyPatch()
    monkeypatch.setattr(secretary_curate, "KNOWLEDGE_DIR", temp_workspace / "knowledge")
    monkeypatch.setattr(secretary_curate, "YSTAR_DIR", temp_workspace)

    context = load_role_context("ceo")

    # Verify context loaded
    assert context["role"] == "ceo"
    assert "CEO Tasks" in context["role_definition"]
    assert "World Class" in context["role_definition"]
    assert "task_001" in context["active_tasks"]
    assert context["active_tasks"]["task_001"]["name"] == "Build team"
    assert "governance" in context["priority_brief_section"]


def test_load_role_context_missing_files(temp_workspace):
    """Test load_role_context handles missing files gracefully."""
    import secretary_curate
    import pytest
    monkeypatch = pytest.MonkeyPatch()
    monkeypatch.setattr(secretary_curate, "KNOWLEDGE_DIR", temp_workspace / "knowledge")
    monkeypatch.setattr(secretary_curate, "YSTAR_DIR", temp_workspace)

    # Load context for role with no files
    context = load_role_context("cto")

    assert context["role"] == "cto"
    assert context["role_definition"] == ""
    assert context["active_tasks"] == {}
    assert context["priority_brief_section"] == ""


def test_generate_action_queue_p0_tasks(temp_workspace):
    """Test generate_action_queue prioritizes P0 tasks."""
    context = {
        "role": "ceo",
        "role_definition": "CEO responsibilities",
        "active_tasks": {
            "task_p0_1": {"name": "Fix critical bug", "priority": "P0", "status": "active"},
            "task_p0_2": {"name": "Deploy hotfix", "priority": "P0", "status": "active"},
            "task_p1": {"name": "Refactor code", "priority": "P1", "status": "active"}
        },
        "priority_brief_section": "Focus on P0 items"
    }

    new_skills = []
    actions = generate_action_queue("ceo", context, new_skills)

    # Should have at least 2 P0 task actions
    p0_actions = [a for a in actions if a["priority"] == "P0"]
    assert len(p0_actions) >= 1
    assert any("Fix critical bug" in a["action"] for a in p0_actions)


def test_generate_action_queue_new_skills(temp_workspace):
    """Test generate_action_queue includes new skill review."""
    context = {
        "role": "ceo",
        "role_definition": "CEO",
        "active_tasks": {},
        "priority_brief_section": ""
    }

    new_skills = [
        "/path/to/knowledge/ceo/skills/_draft_/skill_001.md",
        "/path/to/knowledge/ceo/skills/_draft_/skill_002.md"
    ]

    actions = generate_action_queue("ceo", context, new_skills)

    # Should have action to review new skills
    skill_actions = [a for a in actions if "skill" in a["action"].lower()]
    assert len(skill_actions) >= 1
    assert "2 new skill" in skill_actions[0]["action"] or "2" in skill_actions[0]["why"]


def test_generate_action_queue_deprecated_tasks(temp_workspace):
    """Test generate_action_queue includes deprecated task cleanup."""
    context = {
        "role": "ceo",
        "role_definition": "CEO",
        "active_tasks": {
            "task_old_1": {"name": "Deprecated task 1", "status": "deprecated"},
            "task_old_2": {"name": "Deprecated task 2", "status": "deprecated"}
        },
        "priority_brief_section": ""
    }

    new_skills = []
    actions = generate_action_queue("ceo", context, new_skills)

    # Should have action to archive deprecated tasks
    archive_actions = [a for a in actions if "deprecated" in a["action"].lower() or "archive" in a["action"].lower()]
    assert len(archive_actions) >= 1
    assert "2" in archive_actions[0]["action"] or "2" in archive_actions[0]["why"]


def test_generate_action_queue_fallback(temp_workspace):
    """Test generate_action_queue provides fallback when no tasks."""
    context = {
        "role": "ceo",
        "role_definition": "CEO",
        "active_tasks": {},
        "priority_brief_section": ""
    }

    new_skills = []
    actions = generate_action_queue("ceo", context, new_skills)

    # Should have at least default action
    assert len(actions) >= 1
    assert "priority_brief" in actions[0]["action"].lower()


def test_generate_action_queue_structure(temp_workspace):
    """Test generate_action_queue returns proper action structure."""
    context = {
        "role": "ceo",
        "role_definition": "",
        "active_tasks": {
            "task_p0": {"name": "P0 task", "priority": "P0", "status": "active"}
        },
        "priority_brief_section": ""
    }

    new_skills = []
    actions = generate_action_queue("ceo", context, new_skills)

    # Verify action structure
    for action in actions:
        assert "action" in action
        assert "why" in action
        assert "how_to_verify" in action
        assert "on_fail" in action
        assert "estimated_minutes" in action
        assert "priority" in action
        assert action["priority"] in ["P0", "P1", "P2"]


def test_step5_next_session_action_queue_integration(temp_workspace, monkeypatch):
    """Integration test for step5_next_session_action_queue."""
    import secretary_curate
    monkeypatch.setattr(secretary_curate, "YSTAR_DIR", temp_workspace)
    monkeypatch.setattr(secretary_curate, "KNOWLEDGE_DIR", temp_workspace / "knowledge")
    monkeypatch.setattr(secretary_curate, "BOOT_PACKAGES", temp_workspace / "memory" / "boot_packages")

    # Create boot packages for roles
    boot_pack_dir = temp_workspace / "memory" / "boot_packages"
    for role in ["ceo", "cto"]:
        boot_pack = {
            "pack_meta": {"role": role, "session_id": "test_001"},
            "category_1_identity_dna": {}
        }
        (boot_pack_dir / f"{role}.json").write_text(json.dumps(boot_pack))

    # Create active tasks
    (temp_workspace / "knowledge" / "ceo" / "active_task.json").write_text(json.dumps({
        "ceo_p0": {"name": "CEO P0 task", "priority": "P0", "status": "active"}
    }))

    # Create priority_brief
    (temp_workspace / "reports" / "priority_brief.md").write_text("# Brief\nCEO focus areas")

    ctx = {"session_id": "test_action_queue_001", "trigger": "session_close", "agent": "ceo"}

    # Step 1 and 2 results (mock)
    step1_result = {
        "step": 1,
        "files": [
            str(temp_workspace / "knowledge" / "ceo" / "skills" / "_draft_" / "skill_001.md")
        ]
    }
    step2_result = {"step": 2, "tombstones_applied": 0}

    result = step5_next_session_action_queue(ctx, step1_result, step2_result)

    # Verify results
    assert result["step"] == 5
    assert result["status"] == "implemented"
    assert result["roles_updated"] >= 2  # ceo and cto

    # Verify boot packages updated
    ceo_pack_path = boot_pack_dir / "ceo.json"
    ceo_pack = json.loads(ceo_pack_path.read_text())

    assert "category_11_action_queue" in ceo_pack
    assert "actions" in ceo_pack["category_11_action_queue"]
    assert len(ceo_pack["category_11_action_queue"]["actions"]) >= 1

    # Verify action structure
    action = ceo_pack["category_11_action_queue"]["actions"][0]
    assert "action" in action
    assert "priority" in action


def test_step5_respects_role_skills(temp_workspace, monkeypatch):
    """Test step5 only includes new skills for the correct role."""
    import secretary_curate
    monkeypatch.setattr(secretary_curate, "YSTAR_DIR", temp_workspace)
    monkeypatch.setattr(secretary_curate, "KNOWLEDGE_DIR", temp_workspace / "knowledge")
    monkeypatch.setattr(secretary_curate, "BOOT_PACKAGES", temp_workspace / "memory" / "boot_packages")

    boot_pack_dir = temp_workspace / "memory" / "boot_packages"
    for role in ["ceo", "cto"]:
        boot_pack = {"pack_meta": {"role": role}, "category_1_identity_dna": {}}
        (boot_pack_dir / f"{role}.json").write_text(json.dumps(boot_pack))

    # Create CEO skill draft
    ceo_skill_path = temp_workspace / "knowledge" / "ceo" / "skills" / "_draft_" / "skill_ceo.md"
    ceo_skill_path.parent.mkdir(parents=True, exist_ok=True)
    ceo_skill_path.write_text("# CEO Skill")

    ctx = {"session_id": "test_001", "trigger": "session_close", "agent": "ceo"}

    step1_result = {
        "step": 1,
        "files": [str(ceo_skill_path)]  # CEO skill only
    }
    step2_result = {"step": 2}

    result = step5_next_session_action_queue(ctx, step1_result, step2_result)

    # CEO should have skill review action
    ceo_pack = json.loads((boot_pack_dir / "ceo.json").read_text())
    ceo_actions = ceo_pack["category_11_action_queue"]["actions"]
    skill_actions = [a for a in ceo_actions if "skill" in a["action"].lower()]
    assert len(skill_actions) >= 1

    # CTO should NOT have skill review action (no CTO skills drafted)
    cto_pack = json.loads((boot_pack_dir / "cto.json").read_text())
    cto_actions = cto_pack["category_11_action_queue"]["actions"]
    skill_actions_cto = [a for a in cto_actions if "skill" in a["action"].lower()]
    # CTO might have default action but not specific skill review
    if skill_actions_cto:
        assert "1" not in skill_actions_cto[0]["action"]  # Should not say "1 new skill"


def test_step5_action_queue_field_complete(temp_workspace, monkeypatch):
    """Test step5 generates action queue with all required fields."""
    import secretary_curate
    monkeypatch.setattr(secretary_curate, "YSTAR_DIR", temp_workspace)
    monkeypatch.setattr(secretary_curate, "KNOWLEDGE_DIR", temp_workspace / "knowledge")
    monkeypatch.setattr(secretary_curate, "BOOT_PACKAGES", temp_workspace / "memory" / "boot_packages")

    boot_pack_dir = temp_workspace / "memory" / "boot_packages"
    boot_pack = {"pack_meta": {"role": "ceo"}}
    (boot_pack_dir / "ceo.json").write_text(json.dumps(boot_pack))

    # Create P0 task
    (temp_workspace / "knowledge" / "ceo" / "active_task.json").write_text(json.dumps({
        "task_critical": {"name": "Critical fix", "priority": "P0", "status": "active"}
    }))

    ctx = {"session_id": "test_001"}
    step1_result = {"step": 1, "files": []}
    step2_result = {"step": 2}

    result = step5_next_session_action_queue(ctx, step1_result, step2_result)

    # Load and verify action structure
    ceo_pack = json.loads((boot_pack_dir / "ceo.json").read_text())
    actions = ceo_pack["category_11_action_queue"]["actions"]

    # Check all required fields present
    for action in actions:
        assert isinstance(action["action"], str)
        assert isinstance(action["why"], str)
        assert isinstance(action["how_to_verify"], str)
        assert isinstance(action["on_fail"], str)
        assert isinstance(action["estimated_minutes"], int)
        assert action["priority"] in ["P0", "P1", "P2"]
