"""
L07: Lock-death path — .agent_stack.json corrupted.

Scenario: Stack file has invalid JSON (partial write, disk error, concurrent
access without locking). pop_agent() fails to read the stack and cannot
restore the previous agent identity.

Recovery: _read_stack() returns empty list on JSON error.
pop_agent() falls back to writing "ceo" when stack is empty.
"""
import json
import pytest


class TestL07StackCorrupted:
    """Lock-death: agent stack file corrupted."""

    def test_pop_with_invalid_json(self, lockdeath_env):
        """pop_agent handles invalid JSON in stack file."""
        # SETUP: Corrupt stack file
        lockdeath_env.stack_file.write_text("not json {{{")

        # Push changes marker to subagent
        lockdeath_env.marker_file.write_text("eng-kernel\n")

        # TRIGGER: Pop should handle corrupt stack gracefully
        restored = lockdeath_env.agent_stack.pop_agent()

        # ASSERT: Falls back to default "ceo"
        assert restored == "ceo"
        assert lockdeath_env.agent_stack.current_agent() == "ceo"

    def test_pop_with_wrong_type_json(self, lockdeath_env):
        """Stack file contains JSON but not a list."""
        lockdeath_env.stack_file.write_text('{"not": "a list"}')
        lockdeath_env.marker_file.write_text("eng-kernel\n")

        restored = lockdeath_env.agent_stack.pop_agent()
        assert restored == "ceo"

    def test_pop_with_truncated_json(self, lockdeath_env):
        """Stack file truncated mid-write."""
        lockdeath_env.stack_file.write_text('["ceo", "eth')

        restored = lockdeath_env.agent_stack.pop_agent()
        assert restored == "ceo"

    def test_push_after_corrupt_stack(self, lockdeath_env):
        """push_agent works after stack was corrupted (creates new stack)."""
        lockdeath_env.stack_file.write_text("corrupt data")

        # Push should still work -- reads corrupt stack as empty, appends
        lockdeath_env.agent_stack.push_agent("ethan")

        # Stack should now have ["ceo"] (current was ceo, pushed before writing ethan)
        stack = lockdeath_env.agent_stack._read_stack()
        assert stack == ["ceo"]
        assert lockdeath_env.agent_stack.current_agent() == "ethan"

    def test_full_recovery_corrupt_to_normal(self, lockdeath_env):
        """Full cycle: corrupt stack -> push -> pop -> correct state."""
        lockdeath_env.stack_file.write_text("garbage")

        lockdeath_env.agent_stack.push_agent("ethan")
        assert lockdeath_env.agent_stack.current_agent() == "ethan"

        restored = lockdeath_env.agent_stack.pop_agent()
        assert restored == "ceo"
        assert lockdeath_env.agent_stack.current_agent() == "ceo"
