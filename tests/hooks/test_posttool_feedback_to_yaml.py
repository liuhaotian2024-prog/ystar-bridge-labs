#!/usr/bin/env python3
"""
Tests for V3-Jordan PostToolUse hook: memory/feedback_*.md -> yaml proposal.
Covers: path filtering, tool filtering, missing proposer graceful degradation, CIEU emit.
"""
import json
import os
import sqlite3
import sys
import time
import unittest
from pathlib import Path
from unittest.mock import patch, MagicMock

# Add scripts to path so we can import the hook
REPO_ROOT = Path("/Users/haotianliu/.openclaw/workspace/ystar-company")
sys.path.insert(0, str(REPO_ROOT / "scripts"))

from hook_posttool_feedback_to_yaml import (
    hook_posttool_feedback_to_yaml,
    FEEDBACK_FILE_PATTERN,
    _emit_cieu,
    CIEU_DB,
)


class TestFeedbackFilePattern(unittest.TestCase):
    """Test that the regex correctly matches memory/feedback_*.md paths."""

    def test_matches_absolute_path(self):
        path = "/Users/haotianliu/.openclaw/workspace/ystar-company/memory/feedback_test_new.md"
        self.assertIsNotNone(FEEDBACK_FILE_PATTERN.search(path))

    def test_matches_relative_path(self):
        path = "memory/feedback_boot_no_pipe.md"
        self.assertIsNotNone(FEEDBACK_FILE_PATTERN.search(path))

    def test_no_match_src_file(self):
        path = "/Users/haotianliu/.openclaw/workspace/ystar-company/src/some_code.py"
        self.assertIsNone(FEEDBACK_FILE_PATTERN.search(path))

    def test_no_match_memory_non_feedback(self):
        path = "memory/session_summary_20260422.md"
        self.assertIsNone(FEEDBACK_FILE_PATTERN.search(path))

    def test_no_match_feedback_not_md(self):
        path = "memory/feedback_test.txt"
        self.assertIsNone(FEEDBACK_FILE_PATTERN.search(path))


class TestHookGates(unittest.TestCase):
    """Test that the hook correctly gates on tool_name and file_path."""

    def test_write_feedback_file_fires(self):
        """Test 1: Write to memory/feedback_*.md -> hook fires."""
        result = hook_posttool_feedback_to_yaml(
            tool_name="Write",
            tool_input={"file_path": "memory/feedback_test_new.md"},
            tool_result={"status": "ok"},
        )
        self.assertEqual(result["status"], "ok")
        self.assertTrue(result["fired"])

    def test_write_non_feedback_does_not_fire(self):
        """Test 2: Write to src/some_code.py -> hook does NOT fire."""
        result = hook_posttool_feedback_to_yaml(
            tool_name="Write",
            tool_input={"file_path": "src/some_code.py"},
            tool_result={"status": "ok"},
        )
        self.assertEqual(result["status"], "ok")
        self.assertFalse(result["fired"])
        self.assertEqual(result["reason"], "path_no_match")

    def test_read_tool_does_not_fire(self):
        """Test 3: Read tool -> hook does NOT fire (tool filter)."""
        result = hook_posttool_feedback_to_yaml(
            tool_name="Read",
            tool_input={"file_path": "memory/feedback_test.md"},
            tool_result={"status": "ok"},
        )
        self.assertEqual(result["status"], "ok")
        self.assertFalse(result["fired"])
        self.assertEqual(result["reason"], "not_write_tool")

    def test_bash_tool_does_not_fire(self):
        """Bash tool -> hook does NOT fire."""
        result = hook_posttool_feedback_to_yaml(
            tool_name="Bash",
            tool_input={"command": "echo hi"},
            tool_result={"status": "ok"},
        )
        self.assertFalse(result["fired"])

    def test_edit_tool_does_not_fire(self):
        """Edit tool -> hook does NOT fire (only Write, not Edit)."""
        result = hook_posttool_feedback_to_yaml(
            tool_name="Edit",
            tool_input={"file_path": "memory/feedback_edit_test.md"},
            tool_result={"status": "ok"},
        )
        self.assertFalse(result["fired"])


class TestProposerUnavailable(unittest.TestCase):
    """Test 4: Proposer script not available -> graceful skip."""

    @patch("hook_posttool_feedback_to_yaml.PROPOSER_SCRIPT")
    def test_missing_proposer_returns_ok(self, mock_script_path):
        mock_script_path.exists.return_value = False
        result = hook_posttool_feedback_to_yaml(
            tool_name="Write",
            tool_input={"file_path": "memory/feedback_test_missing_proposer.md"},
            tool_result={"status": "ok"},
        )
        self.assertEqual(result["status"], "ok")
        self.assertTrue(result["fired"])
        self.assertFalse(result["proposer_available"])
        self.assertIsNone(result["proposer_result"])


class TestCIEUEmit(unittest.TestCase):
    """Test that CIEU events are emitted on hook fire."""

    def test_cieu_event_emitted_on_feedback_write(self):
        """Verify FEEDBACK_TO_YAML_HOOK_FIRED event is recorded in CIEU DB."""
        if not CIEU_DB.exists():
            self.skipTest("CIEU DB not available in test environment")

        # Record count before
        conn = sqlite3.connect(str(CIEU_DB), timeout=2.0)
        before = conn.execute(
            "SELECT count(*) FROM cieu_events WHERE event_type='FEEDBACK_TO_YAML_HOOK_FIRED'"
        ).fetchone()[0]
        conn.close()

        # Fire the hook
        hook_posttool_feedback_to_yaml(
            tool_name="Write",
            tool_input={
                "file_path": "/Users/haotianliu/.openclaw/workspace/ystar-company/memory/feedback_cieu_test.md"
            },
            tool_result={"status": "ok"},
        )

        # Record count after
        conn = sqlite3.connect(str(CIEU_DB), timeout=2.0)
        after = conn.execute(
            "SELECT count(*) FROM cieu_events WHERE event_type='FEEDBACK_TO_YAML_HOOK_FIRED'"
        ).fetchone()[0]
        conn.close()

        self.assertGreater(after, before, "CIEU event should be emitted on feedback write")


class TestMainEntrypoint(unittest.TestCase):
    """Test the main() stdin-based entrypoint."""

    @patch("sys.stdin")
    def test_main_with_write_feedback(self, mock_stdin):
        payload = {
            "tool_name": "Write",
            "tool_input": {"file_path": "memory/feedback_main_test.md"},
            "tool_result": {"status": "ok"},
        }
        mock_stdin.read.return_value = json.dumps(payload)

        # main() calls sys.exit(0), so catch it
        from hook_posttool_feedback_to_yaml import main

        with self.assertRaises(SystemExit) as cm:
            main()
        self.assertEqual(cm.exception.code, 0)


if __name__ == "__main__":
    unittest.main()
