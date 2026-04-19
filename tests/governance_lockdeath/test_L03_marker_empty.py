"""
L03: Lock-death path — marker file exists but is empty.

Scenario: File truncated (e.g., concurrent write, disk error, or
`echo -n "" > .ystar_active_agent`). Empty content causes identity
fallthrough to "agent".

Recovery: reset_stack() writes "ceo" to marker.
"""
import pytest


class TestL03MarkerEmpty:
    """Lock-death: marker file empty or whitespace-only."""

    def test_empty_marker_no_override(self, lockdeath_env):
        """Empty marker content does not override payload."""
        lockdeath_env.marker_file.write_text("")

        payload = {"tool_name": "Bash", "tool_input": {"command": "ls"},
                   "agent_id": "", "agent_type": "agent"}
        lockdeath_env.apply_override(payload)
        identity = lockdeath_env.get_effective_identity(payload)
        assert identity == "agent"  # bad state

    def test_whitespace_only_marker_no_override(self, lockdeath_env):
        """Whitespace-only marker is treated as empty."""
        lockdeath_env.marker_file.write_text("   \n\n  ")

        payload = {"tool_name": "Bash", "tool_input": {"command": "ls"},
                   "agent_id": "", "agent_type": "agent"}
        lockdeath_env.apply_override(payload)
        identity = lockdeath_env.get_effective_identity(payload)
        assert identity == "agent"  # bad state

    def test_recovery_via_reset(self, lockdeath_env):
        """reset_stack() recovers from empty marker."""
        lockdeath_env.marker_file.write_text("")
        lockdeath_env.agent_stack.reset_stack()

        payload = {"tool_name": "Bash", "tool_input": {"command": "ls"},
                   "agent_id": "", "agent_type": "agent"}
        lockdeath_env.apply_override(payload)
        identity = lockdeath_env.get_effective_identity(payload)
        assert identity == "ceo"
