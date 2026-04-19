"""
Shared fixtures for lock-death regression tests (CZL-P1-f).

Each test simulates a specific lock-death scenario:
1. Setup: deliberately break the system (delete marker, corrupt stack, etc.)
2. Trigger: apply the payload override logic (simulating a tool call)
3. Assert: system recovers to correct identity within the allowed recovery path

Author: Ryan Park (eng-platform)
"""
import json
import os
import sys
from pathlib import Path

import pytest

SCRIPTS_DIR = Path(__file__).resolve().parent.parent.parent / "scripts"
sys.path.insert(0, str(SCRIPTS_DIR))


@pytest.fixture
def lockdeath_env(tmp_path, monkeypatch):
    """
    Create an isolated environment for lock-death testing.

    Provides:
    - marker_file: path to .ystar_active_agent (initialized to "ceo")
    - stack_file: path to .agent_stack.json (empty)
    - apply_override: function that simulates hook_wrapper payload override
    - agent_stack: the agent_stack module with patched paths
    """
    import agent_stack

    marker_file = tmp_path / ".ystar_active_agent"
    stack_file = tmp_path / ".agent_stack.json"

    # Initialize clean state
    marker_file.write_text("ceo\n")
    stack_file.write_text("[]")

    # Patch agent_stack module to use tmp paths
    monkeypatch.setattr(agent_stack, "STACK_FILE", stack_file)
    monkeypatch.setattr(agent_stack, "MARKER_FILE", marker_file)
    monkeypatch.setattr(agent_stack, "LOCK_FILE", tmp_path / ".agent_stack.lock")

    def apply_override(payload: dict) -> dict:
        """
        Simulate the CZL-P1-a payload override logic from hook_wrapper.py.
        Uses the tmp_path marker file.
        """
        try:
            content = marker_file.read_text(encoding="utf-8").strip()
            if content and content != "agent":
                payload["agent_id"] = content
                if payload.get("agent_type") in ("", "agent", None):
                    payload.pop("agent_type", None)
        except FileNotFoundError:
            pass
        except Exception:
            pass
        return payload

    def get_effective_identity(payload: dict) -> str:
        """
        Determine what identity check_hook would see after the override.
        Simulates _detect_agent_id priority 1 + 1.5 logic.
        """
        aid = payload.get("agent_id", "")
        if aid and aid != "agent":
            return aid
        agent_type = payload.get("agent_type", "")
        if agent_type and agent_type != "agent":
            return agent_type  # simplified -- real code maps this
        return "agent"

    class Env:
        pass

    env = Env()
    env.marker_file = marker_file
    env.stack_file = stack_file
    env.apply_override = apply_override
    env.get_effective_identity = get_effective_identity
    env.agent_stack = agent_stack
    env.tmp_path = tmp_path
    return env
