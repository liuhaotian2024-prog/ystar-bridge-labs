"""
L05: Lock-death path — YSTAR_AGENT_ID environment variable stale.

Scenario: The CEO temporary patch set YSTAR_AGENT_ID from the marker file
at script import time (lines 1-11, now cleaned up by P1-a). If the env var
was set to a subagent's name and never updated, every subsequent hook call
uses the stale identity.

The P1-a fix removed the env var approach entirely in favor of direct
payload injection, which is evaluated fresh on every hook call.

Recovery: Unset YSTAR_AGENT_ID; the payload override provides fresh identity.
"""
import os
import pytest


class TestL05EnvVarStale:
    """Lock-death: stale YSTAR_AGENT_ID environment variable."""

    def test_env_var_does_not_affect_override(self, lockdeath_env, monkeypatch):
        """Payload override uses marker file, not env var."""
        # SETUP: Set stale env var
        monkeypatch.setenv("YSTAR_AGENT_ID", "eng-kernel")

        payload = {"tool_name": "Bash", "tool_input": {"command": "whoami"},
                   "agent_id": "", "agent_type": "agent"}

        lockdeath_env.apply_override(payload)

        # Override should set from marker ("ceo"), not env var
        assert payload["agent_id"] == "ceo"

    def test_env_var_cleared_does_not_break(self, lockdeath_env, monkeypatch):
        """System works fine when YSTAR_AGENT_ID is not set."""
        monkeypatch.delenv("YSTAR_AGENT_ID", raising=False)

        payload = {"tool_name": "Bash", "tool_input": {"command": "whoami"},
                   "agent_id": "", "agent_type": "agent"}

        lockdeath_env.apply_override(payload)
        assert payload["agent_id"] == "ceo"

    def test_stale_env_var_identity_conflict(self, lockdeath_env, monkeypatch):
        """
        Demonstrates the conflict: env var says 'eng-kernel' but marker
        says 'ceo'. Payload override wins (marker-based).
        """
        monkeypatch.setenv("YSTAR_AGENT_ID", "eng-kernel")
        lockdeath_env.marker_file.write_text("ceo\n")

        payload = {"tool_name": "Bash", "tool_input": {"command": "ls"},
                   "agent_id": "", "agent_type": ""}

        lockdeath_env.apply_override(payload)

        # Marker-based override takes precedence
        assert payload["agent_id"] == "ceo"
