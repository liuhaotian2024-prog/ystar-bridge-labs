"""
L04: Lock-death path — payload.agent_type="agent" causes priority 1.5 short-circuit.

Scenario: Claude Code root process sends agent_type="agent" (the default).
In identity_detector, priority 1.5 maps "agent" -> "agent" via _map_agent_type
and returns early, before reaching the marker file at priority 7.

The P1-a fix clears agent_type when it is "agent" to prevent this short-circuit.

Recovery: The payload override removes agent_type="agent" when marker
provides a valid identity.
"""
import pytest


class TestL04AgentTypeShortCircuit:
    """Lock-death: agent_type='agent' short-circuits identity detection."""

    def test_agent_type_agent_cleared_by_override(self, lockdeath_env):
        """Override removes agent_type='agent' when marker has valid agent."""
        payload = {"tool_name": "Bash", "tool_input": {"command": "whoami"},
                   "agent_id": "", "agent_type": "agent"}

        lockdeath_env.apply_override(payload)

        # agent_type should be removed
        assert "agent_type" not in payload
        # agent_id should be set from marker
        assert payload["agent_id"] == "ceo"

    def test_agent_type_empty_cleared(self, lockdeath_env):
        """Override removes agent_type='' when marker has valid agent."""
        payload = {"tool_name": "Bash", "tool_input": {"command": "whoami"},
                   "agent_id": "", "agent_type": ""}

        lockdeath_env.apply_override(payload)

        assert "agent_type" not in payload
        assert payload["agent_id"] == "ceo"

    def test_real_agent_type_preserved(self, lockdeath_env):
        """Real agent_type (e.g. 'Agent-CTO') is NOT cleared."""
        payload = {"tool_name": "Bash", "tool_input": {"command": "whoami"},
                   "agent_id": "", "agent_type": "Agent-CTO"}

        lockdeath_env.apply_override(payload)

        # Real agent_type should be preserved
        assert payload["agent_type"] == "Agent-CTO"
        # But agent_id should still be set from marker
        assert payload["agent_id"] == "ceo"

    def test_without_override_short_circuit_happens(self, lockdeath_env):
        """Without the override, agent_type='agent' would be picked up."""
        # Simulate what happens WITHOUT the P1-a fix
        payload = {"tool_name": "Bash", "tool_input": {"command": "whoami"},
                   "agent_id": "", "agent_type": "agent"}

        # Do NOT apply override -- simulate pre-fix behavior
        identity = lockdeath_env.get_effective_identity(payload)
        assert identity == "agent"  # this is the lock-death state
