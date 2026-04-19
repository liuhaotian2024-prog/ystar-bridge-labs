"""
L06: Lock-death path — .ystar_session.json schema validation error.

Scenario: Session config has invalid schema (missing required fields,
wrong types, etc.). identity_detector's priority 6 calls current_agent()
which raises ValueError on schema validation. If not caught, the entire
identity detection crashes and falls through to "agent".

The fix in identity_detector.py catches ValueError as non-fatal.
The payload override provides an independent path that does not depend
on session config at all.

Recovery: The payload override from marker file works regardless of
session config state.
"""
import json
import pytest


class TestL06SessionConfigCorrupt:
    """Lock-death: corrupted or invalid session config."""

    def test_override_independent_of_session_config(self, lockdeath_env):
        """Payload override works without session config existing."""
        # No .ystar_session.json in tmp_path
        payload = {"tool_name": "Bash", "tool_input": {"command": "ls"},
                   "agent_id": "", "agent_type": "agent"}

        lockdeath_env.apply_override(payload)
        assert payload["agent_id"] == "ceo"

    def test_override_with_corrupt_session_config(self, lockdeath_env):
        """Payload override works even when session config is corrupt."""
        # Write corrupt session config to tmp
        corrupt = lockdeath_env.tmp_path / ".ystar_session.json"
        corrupt.write_text("not valid json at all {{{")

        payload = {"tool_name": "Bash", "tool_input": {"command": "ls"},
                   "agent_id": "", "agent_type": "agent"}

        lockdeath_env.apply_override(payload)
        assert payload["agent_id"] == "ceo"

    def test_override_with_missing_fields_session_config(self, lockdeath_env):
        """Session config with missing required fields doesn't affect override."""
        incomplete = lockdeath_env.tmp_path / ".ystar_session.json"
        incomplete.write_text(json.dumps({"session_id": "test"}))  # missing agent_id, agent_stack

        payload = {"tool_name": "Bash", "tool_input": {"command": "ls"},
                   "agent_id": "", "agent_type": "agent"}

        lockdeath_env.apply_override(payload)
        assert payload["agent_id"] == "ceo"

    def test_override_with_wrong_type_agent_stack(self, lockdeath_env):
        """Session config with agent_stack as string instead of list."""
        bad_types = lockdeath_env.tmp_path / ".ystar_session.json"
        bad_types.write_text(json.dumps({
            "session_id": "test",
            "agent_id": "ceo",
            "agent_stack": "not_a_list"
        }))

        payload = {"tool_name": "Bash", "tool_input": {"command": "ls"},
                   "agent_id": "", "agent_type": "agent"}

        lockdeath_env.apply_override(payload)
        assert payload["agent_id"] == "ceo"
