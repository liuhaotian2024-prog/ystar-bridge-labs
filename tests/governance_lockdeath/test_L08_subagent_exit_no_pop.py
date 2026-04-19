"""
L08: Lock-death path — subagent exits without triggering PostToolUse pop.

Scenario: A subagent crashes, times out, or Claude Code kills it without
running the PostToolUse hook. The marker file is stuck with the subagent's
name, and the stack has the previous agent still waiting to be popped.

Recovery: The next session boot or reset_stack() clears the orphaned state.
Also, the timeout mechanism (check_agent_stack_timeout) can auto-pop stale
entries.
"""
import time
import pytest


class TestL08SubagentExitNoPop:
    """Lock-death: subagent crashes without pop."""

    def test_orphaned_marker_after_crash(self, lockdeath_env):
        """After push without pop, marker stays at subagent identity."""
        # Simulate: CEO spawns ethan, ethan crashes
        lockdeath_env.agent_stack.push_agent("ethan")
        # No pop happens -- ethan crashed

        # Marker is stuck at "ethan"
        assert lockdeath_env.agent_stack.current_agent() == "ethan"
        assert lockdeath_env.agent_stack.stack_depth() == 1  # ceo still on stack

    def test_recovery_by_manual_pop(self, lockdeath_env):
        """Manual pop after crash restores previous agent."""
        lockdeath_env.agent_stack.push_agent("ethan")
        # Crash happened, no automatic pop

        # Recovery: explicit pop
        restored = lockdeath_env.agent_stack.pop_agent()
        assert restored == "ceo"
        assert lockdeath_env.agent_stack.current_agent() == "ceo"

    def test_recovery_by_reset(self, lockdeath_env):
        """reset_stack() clears the orphaned state."""
        lockdeath_env.agent_stack.push_agent("ethan")
        lockdeath_env.agent_stack.push_agent("leo")
        # Both crash -- no pops

        lockdeath_env.agent_stack.reset_stack()
        assert lockdeath_env.agent_stack.current_agent() == "ceo"
        assert lockdeath_env.agent_stack.stack_depth() == 0

    def test_next_push_after_orphaned_state(self, lockdeath_env):
        """Push on orphaned state still works (stack grows)."""
        lockdeath_env.agent_stack.push_agent("ethan")
        # Crash -- marker stuck at "ethan", stack has ["ceo"]

        # CEO tries to spawn maya (without knowing ethan crashed)
        lockdeath_env.agent_stack.push_agent("maya")

        # Stack: ["ceo", "ethan"]  marker: "maya"
        assert lockdeath_env.agent_stack.current_agent() == "maya"
        assert lockdeath_env.agent_stack.stack_depth() == 2

        # Pop twice to get back to CEO
        lockdeath_env.agent_stack.pop_agent()  # restores ethan
        lockdeath_env.agent_stack.pop_agent()  # restores ceo
        assert lockdeath_env.agent_stack.current_agent() == "ceo"

    def test_double_crash_recovery(self, lockdeath_env):
        """Two consecutive crashes without pop, then recovery."""
        lockdeath_env.agent_stack.push_agent("ethan")
        lockdeath_env.agent_stack.push_agent("leo")
        # Both crash without pop

        # Stack: ["ceo", "ethan"], marker: "leo"

        # Recovery: pop both
        lockdeath_env.agent_stack.pop_agent()
        assert lockdeath_env.agent_stack.current_agent() == "ethan"
        lockdeath_env.agent_stack.pop_agent()
        assert lockdeath_env.agent_stack.current_agent() == "ceo"
