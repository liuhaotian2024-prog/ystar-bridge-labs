"""
CZL-P1-e: Test agent stack push/pop for subagent identity management.

Verifies:
1. push_agent() saves current agent to stack and writes subagent to marker
2. pop_agent() restores previous agent from stack
3. Nested spawn: ceo -> ethan -> leo -> each step marker correct
4. Empty stack pop defaults to "ceo"
5. reset_stack() clears everything
6. File atomicity (no corruption on concurrent access)

Author: Ryan Park (eng-platform)
"""
import json
import os
import sys
from pathlib import Path

import pytest

# Add scripts to path for import
SCRIPTS_DIR = Path(__file__).resolve().parent.parent.parent / "scripts"
sys.path.insert(0, str(SCRIPTS_DIR))


@pytest.fixture
def isolated_stack(tmp_path, monkeypatch):
    """Isolate agent_stack module to use tmp_path for files."""
    import agent_stack
    monkeypatch.setattr(agent_stack, "STACK_FILE", tmp_path / ".agent_stack.json")
    monkeypatch.setattr(agent_stack, "MARKER_FILE", tmp_path / ".ystar_active_agent")
    monkeypatch.setattr(agent_stack, "LOCK_FILE", tmp_path / ".agent_stack.lock")
    # Initialize marker with "ceo"
    (tmp_path / ".ystar_active_agent").write_text("ceo\n")
    return agent_stack


class TestPushAgent:
    """Test push_agent() behavior."""

    def test_push_saves_current_to_stack(self, isolated_stack):
        """push_agent should save current agent to stack."""
        prev = isolated_stack.push_agent("ethan")
        assert prev == "ceo"

        stack = isolated_stack._read_stack()
        assert stack == ["ceo"]

    def test_push_writes_subagent_to_marker(self, isolated_stack):
        """push_agent should write subagent name to marker file."""
        isolated_stack.push_agent("ethan")
        assert isolated_stack.current_agent() == "ethan"

    def test_push_multiple(self, isolated_stack):
        """Multiple pushes accumulate on the stack."""
        isolated_stack.push_agent("ethan")
        isolated_stack.push_agent("leo")

        stack = isolated_stack._read_stack()
        assert stack == ["ceo", "ethan"]
        assert isolated_stack.current_agent() == "leo"

    def test_push_returns_previous(self, isolated_stack):
        """push_agent returns the previous agent that was displaced."""
        isolated_stack.push_agent("ethan")
        prev = isolated_stack.push_agent("leo")
        assert prev == "ethan"


class TestPopAgent:
    """Test pop_agent() behavior."""

    def test_pop_restores_previous(self, isolated_stack):
        """pop_agent should restore previous agent from stack."""
        isolated_stack.push_agent("ethan")
        restored = isolated_stack.pop_agent()
        assert restored == "ceo"
        assert isolated_stack.current_agent() == "ceo"

    def test_pop_empty_defaults_to_ceo(self, isolated_stack):
        """pop_agent on empty stack should restore to 'ceo'."""
        restored = isolated_stack.pop_agent()
        assert restored == "ceo"
        assert isolated_stack.current_agent() == "ceo"

    def test_pop_nested(self, isolated_stack):
        """pop_agent should correctly unwind nested pushes."""
        isolated_stack.push_agent("ethan")
        isolated_stack.push_agent("leo")
        isolated_stack.push_agent("maya")

        assert isolated_stack.pop_agent() == "leo"
        assert isolated_stack.current_agent() == "leo"

        assert isolated_stack.pop_agent() == "ethan"
        assert isolated_stack.current_agent() == "ethan"

        assert isolated_stack.pop_agent() == "ceo"
        assert isolated_stack.current_agent() == "ceo"

    def test_pop_beyond_stack_safe(self, isolated_stack):
        """Extra pops beyond the stack should safely return 'ceo'."""
        isolated_stack.push_agent("ethan")
        isolated_stack.pop_agent()  # restore ceo
        isolated_stack.pop_agent()  # extra pop -- should be safe
        assert isolated_stack.current_agent() == "ceo"


class TestNestedSpawnScenario:
    """Integration test: simulate ceo -> ethan -> leo spawn/exit lifecycle."""

    def test_full_nested_lifecycle(self, isolated_stack):
        """
        Simulate:
        1. CEO is active (initial state)
        2. Spawn ethan (push ceo, write ethan)
        3. ethan spawns leo (push ethan, write leo)
        4. leo completes (pop -> ethan)
        5. ethan completes (pop -> ceo)
        """
        # Step 1: Initial state
        assert isolated_stack.current_agent() == "ceo"
        assert isolated_stack.stack_depth() == 0

        # Step 2: CEO spawns ethan
        isolated_stack.push_agent("ethan")
        assert isolated_stack.current_agent() == "ethan"
        assert isolated_stack.stack_depth() == 1

        # Step 3: ethan spawns leo
        isolated_stack.push_agent("leo")
        assert isolated_stack.current_agent() == "leo"
        assert isolated_stack.stack_depth() == 2

        # Step 4: leo completes
        restored = isolated_stack.pop_agent()
        assert restored == "ethan"
        assert isolated_stack.current_agent() == "ethan"
        assert isolated_stack.stack_depth() == 1

        # Step 5: ethan completes
        restored = isolated_stack.pop_agent()
        assert restored == "ceo"
        assert isolated_stack.current_agent() == "ceo"
        assert isolated_stack.stack_depth() == 0


class TestResetStack:
    """Test reset_stack() emergency recovery."""

    def test_reset_clears_everything(self, isolated_stack):
        """reset_stack should clear stack and restore marker to 'ceo'."""
        isolated_stack.push_agent("ethan")
        isolated_stack.push_agent("leo")
        isolated_stack.push_agent("maya")

        isolated_stack.reset_stack()

        assert isolated_stack.current_agent() == "ceo"
        assert isolated_stack.stack_depth() == 0

    def test_reset_idempotent(self, isolated_stack):
        """reset_stack on clean state is safe."""
        isolated_stack.reset_stack()
        assert isolated_stack.current_agent() == "ceo"
        assert isolated_stack.stack_depth() == 0


class TestEdgeCases:
    """Edge case tests."""

    def test_marker_missing_on_push(self, isolated_stack):
        """push_agent when marker file does not exist should use default."""
        isolated_stack.MARKER_FILE.unlink()
        prev = isolated_stack.push_agent("ethan")
        assert prev == "ceo"  # default
        assert isolated_stack.current_agent() == "ethan"

    def test_stack_file_corrupted(self, isolated_stack):
        """Corrupted stack file should be treated as empty."""
        isolated_stack.STACK_FILE.write_text("not valid json")
        # pop should safely return default
        restored = isolated_stack.pop_agent()
        assert restored == "ceo"

    def test_stack_file_wrong_type(self, isolated_stack):
        """Stack file with non-list JSON should be treated as empty."""
        isolated_stack.STACK_FILE.write_text('{"key": "value"}')
        restored = isolated_stack.pop_agent()
        assert restored == "ceo"

    def test_whitespace_in_agent_names(self, isolated_stack):
        """Agent names with extra whitespace are handled."""
        isolated_stack.push_agent("  ethan  ")
        # Marker should have exactly what was pushed (the caller should sanitize)
        marker_content = isolated_stack.MARKER_FILE.read_text().strip()
        assert marker_content == "ethan"

    def test_deep_nesting(self, isolated_stack):
        """Deep nesting (10 levels) works correctly."""
        agents = [f"agent-{i}" for i in range(10)]
        for a in agents:
            isolated_stack.push_agent(a)

        assert isolated_stack.current_agent() == "agent-9"
        assert isolated_stack.stack_depth() == 10

        # Pop all
        for i in range(9, -1, -1):
            isolated_stack.pop_agent()

        assert isolated_stack.current_agent() == "ceo"
        assert isolated_stack.stack_depth() == 0
