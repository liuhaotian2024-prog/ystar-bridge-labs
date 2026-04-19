"""
L02: Lock-death path — marker file contains literal "agent".

Scenario: A reset or failed boot writes "agent" to the marker file.
The payload override logic explicitly skips "agent" content (it is the
same as the fallback default), so identity stays broken.

Recovery: Overwrite marker with actual agent name ("ceo").
"""
import pytest


class TestL02MarkerContainsAgent:
    """Lock-death: marker contains 'agent' literal."""

    def test_agent_literal_not_overridden(self, lockdeath_env):
        """Marker containing 'agent' is correctly skipped by override."""
        # SETUP: Marker says "agent"
        lockdeath_env.marker_file.write_text("agent\n")

        payload = {"tool_name": "Bash", "tool_input": {"command": "whoami"},
                   "agent_id": "", "agent_type": "agent"}
        lockdeath_env.apply_override(payload)

        # Override skips "agent" content -> identity falls through
        identity = lockdeath_env.get_effective_identity(payload)
        assert identity == "agent"  # bad state detected

    def test_recovery_by_writing_real_agent(self, lockdeath_env):
        """Writing real agent name to marker recovers identity."""
        # SETUP: Bad state
        lockdeath_env.marker_file.write_text("agent\n")

        # RECOVERY: Write correct agent
        lockdeath_env.marker_file.write_text("ceo\n")

        payload = {"tool_name": "Bash", "tool_input": {"command": "whoami"},
                   "agent_id": "", "agent_type": "agent"}
        lockdeath_env.apply_override(payload)
        identity = lockdeath_env.get_effective_identity(payload)
        assert identity == "ceo"  # recovered

    def test_recovery_via_reset_stack(self, lockdeath_env):
        """reset_stack() overwrites 'agent' with 'ceo' in marker."""
        lockdeath_env.marker_file.write_text("agent\n")
        lockdeath_env.agent_stack.reset_stack()

        payload = {"tool_name": "Bash", "tool_input": {"command": "whoami"},
                   "agent_id": "", "agent_type": "agent"}
        lockdeath_env.apply_override(payload)
        identity = lockdeath_env.get_effective_identity(payload)
        assert identity == "ceo"
