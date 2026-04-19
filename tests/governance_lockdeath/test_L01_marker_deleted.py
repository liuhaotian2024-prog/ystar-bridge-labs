"""
L01: Lock-death path — .ystar_active_agent marker file deleted.

Scenario: A cleanup script or filesystem event removes the marker file.
Without recovery, identity_detector falls through all priorities to "agent",
and all tool calls get blocked or misrouted.

Recovery: payload override gracefully handles FileNotFoundError.
Agent stack reset_stack() recreates the marker with "ceo" default.
"""
import pytest


class TestL01MarkerDeleted:
    """Lock-death: marker file deleted mid-session."""

    def test_override_survives_missing_marker(self, lockdeath_env):
        """Payload override does not crash when marker is missing."""
        # SETUP: Delete marker file
        lockdeath_env.marker_file.unlink()
        assert not lockdeath_env.marker_file.exists()

        # TRIGGER: Apply override with default payload
        payload = {"tool_name": "Bash", "tool_input": {"command": "whoami"},
                   "agent_id": "", "agent_type": "agent"}
        result = lockdeath_env.apply_override(payload)

        # ASSERT: No crash. Payload unchanged (override skipped).
        assert result["agent_id"] == ""

    def test_stack_reset_recreates_marker(self, lockdeath_env):
        """reset_stack() recreates the marker file after deletion."""
        # SETUP: Delete marker
        lockdeath_env.marker_file.unlink()

        # TRIGGER: Reset stack (recovery action)
        lockdeath_env.agent_stack.reset_stack()

        # ASSERT: Marker recreated with "ceo"
        assert lockdeath_env.marker_file.exists()
        assert lockdeath_env.agent_stack.current_agent() == "ceo"

    def test_recovery_within_3_steps(self, lockdeath_env):
        """
        Full recovery path:
        Step 1: Tool call with missing marker -> identity="agent" (bad)
        Step 2: Detect bad identity, call reset_stack()
        Step 3: Next tool call -> identity="ceo" (recovered)
        """
        # Step 1: Delete marker
        lockdeath_env.marker_file.unlink()
        payload1 = {"tool_name": "Bash", "tool_input": {"command": "ls"},
                    "agent_id": "", "agent_type": "agent"}
        lockdeath_env.apply_override(payload1)
        identity1 = lockdeath_env.get_effective_identity(payload1)
        assert identity1 == "agent"  # bad state

        # Step 2: Recovery
        lockdeath_env.agent_stack.reset_stack()

        # Step 3: Next tool call
        payload2 = {"tool_name": "Bash", "tool_input": {"command": "ls"},
                    "agent_id": "", "agent_type": "agent"}
        lockdeath_env.apply_override(payload2)
        identity2 = lockdeath_env.get_effective_identity(payload2)
        assert identity2 == "ceo"  # recovered
