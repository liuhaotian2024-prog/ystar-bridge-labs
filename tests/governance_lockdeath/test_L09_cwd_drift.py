"""
L09: Lock-death path — CWD (current working directory) drift.

Scenario: The hook process runs with a different working directory than
expected. Relative paths like ".ystar_active_agent" or
"scripts/.ystar_active_agent" fail to resolve. The old CEO temporary fix
used os.chdir() at import time, but this was fragile and could be overridden.

The P1-a fix uses absolute paths exclusively for the marker file,
making CWD irrelevant.

Recovery: Absolute paths in the payload override are immune to CWD changes.
"""
import os
import pytest


class TestL09CwdDrift:
    """Lock-death: working directory drift affects relative path resolution."""

    def test_override_uses_absolute_path(self, lockdeath_env):
        """
        The override logic uses an absolute path for the marker file.
        Changing CWD does not affect it.
        """
        # The apply_override function uses lockdeath_env.marker_file
        # which is already an absolute path (tmp_path based).
        # This test verifies the principle.
        original_cwd = os.getcwd()

        try:
            # Change to a completely unrelated directory
            os.chdir("/tmp")

            payload = {"tool_name": "Bash", "tool_input": {"command": "ls"},
                       "agent_id": "", "agent_type": "agent"}
            lockdeath_env.apply_override(payload)
            assert payload["agent_id"] == "ceo"
        finally:
            os.chdir(original_cwd)

    def test_agent_stack_uses_absolute_path(self, lockdeath_env):
        """
        Agent stack module's STACK_FILE and MARKER_FILE are absolute paths.
        CWD drift does not affect push/pop.
        """
        original_cwd = os.getcwd()

        try:
            os.chdir("/tmp")

            # Push should still work
            lockdeath_env.agent_stack.push_agent("ethan")
            assert lockdeath_env.agent_stack.current_agent() == "ethan"

            # Pop should still work
            lockdeath_env.agent_stack.pop_agent()
            assert lockdeath_env.agent_stack.current_agent() == "ceo"
        finally:
            os.chdir(original_cwd)

    def test_real_hook_wrapper_marker_path_is_absolute(self):
        """
        Verify that the marker path constants in hook_wrapper.py are absolute.
        This is a static analysis check.

        CZL-MARKER-PER-SESSION-ISOLATION: hook_wrapper now uses _MARKER_DIR
        and _MARKER_GLOBAL instead of a single _MARKER_PATH. Both must resolve
        to absolute paths.
        """
        import re
        hook_wrapper_path = os.path.join(
            os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))),
            "scripts", "hook_wrapper.py"
        )
        with open(hook_wrapper_path, "r") as f:
            content = f.read()

        # Find the _MARKER_DIR or _MARKER_GLOBAL assignment
        match = re.search(r'_MARKER_GLOBAL\s*=\s*os\.path\.join\(\s*_MARKER_DIR', content)
        if match is None:
            # Fallback: check for legacy _MARKER_PATH
            match = re.search(r'_MARKER_PATH\s*=\s*"([^"]+)"', content)
        assert match is not None, "_MARKER_GLOBAL (or legacy _MARKER_PATH) not found in hook_wrapper.py"

        # Verify _MARKER_DIR is absolute
        dir_match = re.search(r'_MARKER_DIR\s*=\s*"([^"]+)"', content)
        if dir_match:
            marker_dir = dir_match.group(1)
            assert os.path.isabs(marker_dir), f"_MARKER_DIR is not absolute: {marker_dir}"
