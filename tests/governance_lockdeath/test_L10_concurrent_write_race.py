"""
L10: Lock-death path — concurrent write race on marker/stack files.

Scenario: Two hook processes fire simultaneously (e.g., parallel tool calls).
Both read the marker, both try to write it. Without atomicity, the marker
can be corrupted (truncated, partial write, interleaved bytes).

Recovery: agent_stack uses atomic writes (write to .tmp then os.replace).
The marker file is small enough that write+flush is effectively atomic on
most filesystems. Corrupted state is handled by fallback to "ceo".
"""
import json
import os
import threading
import pytest


class TestL10ConcurrentWriteRace:
    """Lock-death: concurrent write race on marker and stack files."""

    def test_atomic_write_stack(self, lockdeath_env):
        """Stack file write uses atomic rename pattern."""
        # Verify no .tmp file persists after write
        lockdeath_env.agent_stack.push_agent("ethan")

        tmp_file = str(lockdeath_env.stack_file) + ".tmp"
        assert not os.path.exists(tmp_file), ".tmp file should not persist after atomic write"

    def test_concurrent_pushes(self, lockdeath_env):
        """Multiple concurrent pushes do not corrupt the stack."""
        errors = []
        results = []

        def push_agent(name):
            try:
                lockdeath_env.agent_stack.push_agent(name)
                results.append(name)
            except Exception as e:
                errors.append(str(e))

        threads = [
            threading.Thread(target=push_agent, args=(f"agent-{i}",))
            for i in range(5)
        ]

        for t in threads:
            t.start()
        for t in threads:
            t.join(timeout=5)

        # No exceptions should have occurred
        assert errors == [], f"Concurrent push errors: {errors}"

        # Stack should be valid JSON
        stack = lockdeath_env.agent_stack._read_stack()
        assert isinstance(stack, list)

        # Marker should have a valid agent name
        current = lockdeath_env.agent_stack.current_agent()
        assert current != ""

    def test_push_pop_interleaved(self, lockdeath_env):
        """Interleaved push and pop operations should not corrupt state."""
        # Sequential interleaving (deterministic)
        lockdeath_env.agent_stack.push_agent("a1")
        lockdeath_env.agent_stack.push_agent("a2")
        lockdeath_env.agent_stack.pop_agent()
        lockdeath_env.agent_stack.push_agent("a3")
        lockdeath_env.agent_stack.pop_agent()
        lockdeath_env.agent_stack.pop_agent()

        # Should be back to ceo
        assert lockdeath_env.agent_stack.current_agent() == "ceo"
        assert lockdeath_env.agent_stack.stack_depth() == 0

    def test_recovery_after_simulated_corruption(self, lockdeath_env):
        """
        Simulate a partial write (truncated file) and verify recovery.
        """
        lockdeath_env.agent_stack.push_agent("ethan")

        # Simulate corruption: truncate stack file mid-write
        with open(lockdeath_env.stack_file, "w") as f:
            f.write('["ce')  # truncated JSON

        # Pop should handle gracefully
        restored = lockdeath_env.agent_stack.pop_agent()
        assert restored == "ceo"  # fallback to default

        # State should be clean
        assert lockdeath_env.agent_stack.current_agent() == "ceo"
