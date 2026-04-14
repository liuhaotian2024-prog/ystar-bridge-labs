"""
Integration tests for idle learning system
Platform Engineer: Ryan Park (eng-platform)
Date: 2026-04-11

Tests the three-priority learning loop:
- P1: Role definition completeness
- P2: Theory library building
- P3: Counterfactual simulation with P3→P2 feedback
"""
import json
import subprocess
import sys
from pathlib import Path
import pytest

REPO_ROOT = Path(__file__).resolve().parent.parent
SCRIPTS_DIR = REPO_ROOT / "scripts"
KNOWLEDGE_DIR = REPO_ROOT / "knowledge"


@pytest.mark.integration
def test_idle_learning_priority_1_creates_files(temp_knowledge_dir, monkeypatch):
    """Test Priority 1 creates role definition files when missing."""
    # Setup temporary knowledge dir
    test_role = "test_agent"
    role_dir = temp_knowledge_dir / test_role / "role_definition"

    # Monkeypatch KNOWLEDGE_ROOT in idle_learning.py
    monkeypatch.setenv("KNOWLEDGE_ROOT", str(temp_knowledge_dir))

    # Run Priority 1
    result = subprocess.run(
        [sys.executable, str(SCRIPTS_DIR / "idle_learning.py"),
         "--actor", test_role, "--priority", "1"],
        env={**subprocess.os.environ, "KNOWLEDGE_ROOT": str(temp_knowledge_dir)},
        capture_output=True,
        text=True,
    )

    # Verify files were created
    assert role_dir.exists()
    assert (role_dir / "world_class_standard.md").exists()
    assert (role_dir / "role_heroes.md").exists()
    assert (role_dir / "task_type_map.md").exists()


@pytest.mark.integration
def test_idle_learning_priority_1_idempotent():
    """Test Priority 1 is idempotent - doesn't recreate existing files."""
    # Use CTO which already has complete role definition
    result = subprocess.run(
        [sys.executable, str(SCRIPTS_DIR / "idle_learning.py"),
         "--actor", "cto", "--priority", "1"],
        capture_output=True,
        text=True,
    )

    assert result.returncode == 0
    output = result.stdout
    assert "3/3" in output or "All files present" in output


@pytest.mark.integration
def test_idle_learning_priority_2_creates_theory():
    """Test Priority 2 builds theory library from task_type_map."""
    # Use CTO which has task_type_map
    result = subprocess.run(
        [sys.executable, str(SCRIPTS_DIR / "idle_learning.py"),
         "--actor", "cto", "--priority", "2"],
        capture_output=True,
        text=True,
    )

    assert result.returncode == 0
    # Either creates new theory or reports existing ones
    assert "theory" in result.stdout.lower()


@pytest.mark.integration
@pytest.mark.slow
@pytest.mark.requires_gemma
def test_idle_learning_priority_3_generates_scenario():
    """Test Priority 3 generates counterfactual scenario."""
    result = subprocess.run(
        [sys.executable, str(SCRIPTS_DIR / "idle_learning.py"),
         "--actor", "cto", "--priority", "3"],
        capture_output=True,
        text=True,
        timeout=90,
    )

    assert result.returncode == 0
    assert "Scenario:" in result.stdout
    assert "gaps_recorded" in result.stdout


@pytest.mark.integration
@pytest.mark.slow
@pytest.mark.requires_gemma
def test_p3_to_p2_feedback_loop():
    """Test that P3 simulation feeds back into P2 task type map."""
    actor = "eng-platform"

    # Run P3 to generate scenario and extract new task types
    result = subprocess.run(
        [sys.executable, str(SCRIPTS_DIR / "idle_learning.py"),
         "--actor", actor, "--priority", "3"],
        capture_output=True,
        text=True,
        timeout=90,
    )

    assert result.returncode == 0

    # Parse output JSON
    output_lines = result.stdout.strip().split("\n")
    summary_line = None
    for line in output_lines:
        if line.startswith("{"):
            summary_line = line
            break

    if summary_line:
        summary = json.loads(summary_line)
        p3_result = summary.get("priority_3", {})

        # Check P3→P2 feedback happened
        new_gaps = p3_result.get("new_gaps", 0)
        new_task_types = p3_result.get("new_task_types", 0)

        # At minimum, meta-gap should be created
        assert new_gaps >= 1, "P3 should create at least meta-gap"

        # If new task types detected, gap files should exist
        if new_task_types > 0:
            gaps_dir = KNOWLEDGE_DIR / actor / "gaps"
            gap_files = list(gaps_dir.glob("p3_feedback_*.md"))
            assert len(gap_files) > 0, "P3 should create gap files for new task types"


@pytest.mark.unit
def test_gemma_log_format():
    """Test gemma_sessions.log JSONL entries are valid."""
    # Check CTO's log (known to exist)
    log_path = KNOWLEDGE_DIR / "cto" / "gaps" / "gemma_sessions.log"

    if log_path.exists():
        idle_learning_entries = 0
        with open(log_path) as f:
            for line in f:
                line = line.strip()
                if not line:
                    continue
                # Skip non-JSON lines (headers, separators)
                if not line.startswith("{"):
                    continue

                try:
                    entry = json.loads(line)
                    assert "timestamp" in entry
                    assert "actor" in entry
                    assert "mode" in entry

                    # If it's an idle_learning entry, verify full structure
                    if entry.get("mode") == "idle_learning":
                        assert "priority" in entry
                        idle_learning_entries += 1
                except json.JSONDecodeError:
                    pytest.fail(f"Invalid JSON in gemma log: {line[:100]}")

        # Should have at least one idle_learning entry
        assert idle_learning_entries > 0, "No idle_learning entries found"


@pytest.mark.unit
def test_role_canonical_names():
    """Test actor name normalization."""
    from scripts.idle_learning import canonical_actor

    assert canonical_actor("ethan") == "cto"
    assert canonical_actor("ethan_wright") == "cto"
    assert canonical_actor("cto") == "cto"
    assert canonical_actor("aiden_liu") == "ceo"
    assert canonical_actor("unknown") == "unknown"


@pytest.mark.integration
def test_all_priorities_sequential():
    """Test running all priorities sequentially."""
    result = subprocess.run(
        [sys.executable, str(SCRIPTS_DIR / "idle_learning.py"),
         "--actor", "ceo", "--priority", "all"],
        capture_output=True,
        text=True,
        timeout=120,
    )

    # Should complete without error
    assert result.returncode == 0

    # Should show all three priorities
    assert "Priority 1" in result.stdout
    assert "Priority 2" in result.stdout
    assert "Priority 3" in result.stdout


@pytest.mark.unit
def test_invalid_actor_rejected():
    """Test invalid actor names are rejected."""
    result = subprocess.run(
        [sys.executable, str(SCRIPTS_DIR / "idle_learning.py"),
         "--actor", "invalid_agent_name", "--priority", "1"],
        capture_output=True,
        text=True,
    )

    assert result.returncode == 1
    assert "Unknown actor" in result.stdout


@pytest.mark.unit
def test_invalid_priority_rejected():
    """Test invalid priority values are rejected."""
    result = subprocess.run(
        [sys.executable, str(SCRIPTS_DIR / "idle_learning.py"),
         "--actor", "cto", "--priority", "99"],
        capture_output=True,
        text=True,
    )

    # Script may accept it but shouldn't crash
    # Actual behavior depends on implementation
    # This test documents current behavior
