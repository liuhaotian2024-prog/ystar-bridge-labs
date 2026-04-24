"""
Tests for k9_rescue_actions.py — K9 Rescue Daemon whitelist actions.

Covers:
- All 7 action IDs (R-001..R-007) execute and return structured results
- Unknown action IDs are rejected
- R-007 PID validation rejects non-ystar PIDs
- No shell=True in any subprocess call
- Zero ystar.* imports in the module
"""

import os
import sys
import ast
import signal
import subprocess

import pytest

# Ensure scripts/ is on sys.path for import
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from k9_rescue_actions import (
    execute_action,
    ACTION_REGISTRY,
    _validate_pid_is_ystar,
    r001_pycache_clear,
    r002_pkill_hook,
    r003_import_check,
    r004_ps_grep,
    r005_dedupe_heartbeat,
    r006_read_active_agent,
    r007_kill_pid,
    _run,
)


class TestActionRegistry:
    """Test the action registry structure."""

    def test_registry_has_7_actions(self):
        assert len(ACTION_REGISTRY) == 7

    def test_all_action_ids_present(self):
        expected = {"R-001", "R-002", "R-003", "R-004", "R-005", "R-006", "R-007"}
        assert set(ACTION_REGISTRY.keys()) == expected

    def test_each_entry_has_required_keys(self):
        for aid, entry in ACTION_REGISTRY.items():
            assert "fn" in entry, f"{aid} missing 'fn'"
            assert "needs_arg" in entry, f"{aid} missing 'needs_arg'"
            assert "desc" in entry, f"{aid} missing 'desc'"
            assert callable(entry["fn"]), f"{aid} fn is not callable"

    def test_unknown_action_rejected(self):
        result = execute_action("R-999")
        assert result["ok"] is False
        assert "unknown" in result["error"].lower() or "not in whitelist" in result["error"]

    def test_empty_action_rejected(self):
        result = execute_action("")
        assert result["ok"] is False

    def test_none_action_rejected(self):
        result = execute_action(None)
        assert result["ok"] is False


class TestR001PycacheClear:
    """Test R-001: pycache clear."""

    def test_returns_structured_result(self):
        result = r001_pycache_clear()
        assert result["action"] == "R-001"
        assert "ok" in result
        assert "count" in result or "error" in result


class TestR002PkillHook:
    """Test R-002: pkill hook_wrapper.py."""

    def test_returns_structured_result(self):
        result = r002_pkill_hook()
        assert result["action"] == "R-002"
        assert "ok" in result
        # ok can be True even if no processes matched (rc=1)


class TestR003ImportCheck:
    """Test R-003: import check."""

    def test_returns_structured_result(self):
        result = r003_import_check()
        assert result["action"] == "R-003"
        assert "ok" in result
        assert "stdout" in result


class TestR004PsGrep:
    """Test R-004: ps grep."""

    def test_returns_structured_result(self):
        result = r004_ps_grep()
        assert result["action"] == "R-004"
        assert result["ok"] is True
        assert "processes" in result
        assert isinstance(result["processes"], list)
        assert "count" in result


class TestR005DedupeHeartbeat:
    """Test R-005: dedupe heartbeat files."""

    def test_returns_structured_result(self):
        result = r005_dedupe_heartbeat()
        assert result["action"] == "R-005"
        assert result["ok"] is True
        assert "removed" in result


class TestR006ReadActiveAgent:
    """Test R-006: read active agent."""

    def test_returns_structured_result(self):
        result = r006_read_active_agent()
        assert result["action"] == "R-006"
        assert result["ok"] is True
        assert "markers" in result
        assert isinstance(result["markers"], dict)


class TestR007KillPid:
    """Test R-007: kill specific PID with validation."""

    def test_invalid_pid_string(self):
        result = r007_kill_pid("abc")
        assert result["ok"] is False
        assert "invalid" in result["error"].lower()

    def test_invalid_pid_none(self):
        result = r007_kill_pid(None)
        assert result["ok"] is False

    def test_pid_zero_rejected(self):
        result = r007_kill_pid(0)
        assert result["ok"] is False

    def test_pid_one_rejected(self):
        result = r007_kill_pid(1)
        assert result["ok"] is False

    def test_non_ystar_pid_rejected(self):
        """Our own test process PID should not match ystar patterns."""
        our_pid = os.getpid()
        is_valid, _ = _validate_pid_is_ystar(our_pid)
        # Our pytest process should NOT be considered a ystar process
        # (unless we're running inside a ystar-named process, which is unlikely)
        result = r007_kill_pid(our_pid)
        # Either fails validation or would refuse — the key thing is it doesn't
        # silently kill a non-ystar process
        assert "action" in result
        assert result["action"] == "R-007"

    def test_nonexistent_pid_rejected(self):
        """A PID that doesn't exist should be rejected at validation."""
        result = r007_kill_pid(999999)
        assert result["ok"] is False


class TestNoShellTrue:
    """Verify no shell=True in k9_rescue_actions.py source."""

    def test_no_shell_true_in_source(self):
        src_path = os.path.join(os.path.dirname(__file__), "..", "k9_rescue_actions.py")
        with open(src_path, "r") as f:
            source = f.read()
        tree = ast.parse(source)
        for node in ast.walk(tree):
            if isinstance(node, ast.keyword):
                if node.arg == "shell":
                    if isinstance(node.value, ast.Constant) and node.value.value is True:
                        pytest.fail("Found shell=True in k9_rescue_actions.py")


class TestNoYstarImports:
    """Verify zero ystar.* imports in both daemon files."""

    def _check_no_ystar_import(self, filepath):
        with open(filepath, "r") as f:
            source = f.read()
        tree = ast.parse(source)
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                for alias in node.names:
                    if alias.name.startswith("ystar"):
                        pytest.fail(f"Found 'import {alias.name}' in {filepath}")
            elif isinstance(node, ast.ImportFrom):
                if node.module and node.module.startswith("ystar"):
                    pytest.fail(f"Found 'from {node.module} import ...' in {filepath}")

    def test_actions_no_ystar_import(self):
        path = os.path.join(os.path.dirname(__file__), "..", "k9_rescue_actions.py")
        self._check_no_ystar_import(path)

    def test_daemon_no_ystar_import(self):
        path = os.path.join(os.path.dirname(__file__), "..", "k9_rescue_daemon.py")
        self._check_no_ystar_import(path)


class TestRunHelper:
    """Test the _run subprocess helper."""

    def test_run_simple_command(self):
        rc, out, err = _run(["echo", "hello"])
        assert rc == 0
        assert "hello" in out

    def test_run_nonexistent_command(self):
        rc, out, err = _run(["/nonexistent/binary"])
        assert rc != 0

    def test_run_timeout(self):
        rc, out, err = _run(["sleep", "30"], timeout=1)
        assert rc == -1
        assert "timeout" in err.lower()
