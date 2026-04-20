#!/usr/bin/env python3
"""
Brain L2 Writeback Wiring — regression tests.

Engineer: Ryan Park (eng-platform)
Grant: CZL-BRAIN-L2-HOOK-WIRE-CONTINUATION

Tests:
  1. Hook entries exist in settings.json (PostToolUse Agent + Stop drain)
  2. PostToolUse(Agent) enqueue writes to .brain_writeback_queue.jsonl
  3. Stop drain reads L1 cache + processes queue entries
  4. Failure path: writeback error does not drop data, emits persistent entry
"""

import json
import os
import sys
import tempfile
import time
import types
import unittest
from unittest import mock

# ── Paths ──
COMPANY_ROOT = os.path.abspath(
    os.path.join(os.path.dirname(__file__), "..", "..")
)
SCRIPTS_DIR = os.path.join(COMPANY_ROOT, "scripts")
SETTINGS_PATH = os.path.join(COMPANY_ROOT, ".claude", "settings.json")

# Import the queue module directly
sys.path.insert(0, SCRIPTS_DIR)
import brain_writeback_queue as bwq


class TestHookWiringInSettings(unittest.TestCase):
    """Case 1: Verify hooks are actually registered in .claude/settings.json."""

    def setUp(self):
        with open(SETTINGS_PATH, "r", encoding="utf-8") as f:
            self.settings = json.load(f)

    def test_post_tool_use_agent_enqueue_hook_exists(self):
        """PostToolUse must have an Agent-matched entry calling brain_writeback_queue.py enqueue."""
        post_hooks = self.settings.get("hooks", {}).get("PostToolUse", [])
        found = False
        for group in post_hooks:
            matcher = group.get("matcher", "")
            if matcher != "Agent":
                continue
            for hook in group.get("hooks", []):
                cmd = hook.get("command", "")
                if "brain_writeback_queue.py" in cmd and "enqueue" in cmd:
                    found = True
                    self.assertTrue(
                        hook.get("async", False),
                        "brain_writeback_queue enqueue hook must be async"
                    )
                    break
        self.assertTrue(found, "PostToolUse Agent hook for brain_writeback_queue.py enqueue not found")

    def test_stop_drain_hook_exists(self):
        """Stop must have an entry calling brain_writeback_queue.py drain."""
        stop_hooks = self.settings.get("hooks", {}).get("Stop", [])
        found = False
        for group in stop_hooks:
            for hook in group.get("hooks", []):
                cmd = hook.get("command", "")
                if "brain_writeback_queue.py" in cmd and "drain" in cmd:
                    found = True
                    break
        self.assertTrue(found, "Stop hook for brain_writeback_queue.py drain not found")


class TestEnqueuePostToolUse(unittest.TestCase):
    """Case 2: PostToolUse(Agent) enqueue writes entry to .jsonl queue."""

    def setUp(self):
        self._orig_queue = bwq._QUEUE_PATH
        self._orig_cache = bwq._L1_CACHE_PATH
        self._tmpdir = tempfile.mkdtemp()
        bwq._QUEUE_PATH = os.path.join(self._tmpdir, "queue.jsonl")
        bwq._L1_CACHE_PATH = os.path.join(self._tmpdir, "l1_cache.json")

    def tearDown(self):
        bwq._QUEUE_PATH = self._orig_queue
        bwq._L1_CACHE_PATH = self._orig_cache

    def test_enqueue_writes_pending_entry(self):
        """enqueue() must append a JSON line with status=pending."""
        l1 = {"query": "test_query", "timestamp": time.time(), "hits": []}
        entry_id = bwq.enqueue(l1_cache_entry=l1, outcome_events=[{"type": "test"}])
        self.assertTrue(os.path.isfile(bwq._QUEUE_PATH))
        with open(bwq._QUEUE_PATH, "r") as f:
            lines = [json.loads(line) for line in f if line.strip()]
        self.assertEqual(len(lines), 1)
        self.assertEqual(lines[0]["entry_id"], entry_id)
        self.assertEqual(lines[0]["status"], "pending")
        self.assertIsNotNone(lines[0]["l1_cache"])

    def test_enqueue_reads_l1_cache_when_none(self):
        """enqueue(l1_cache_entry=None) must auto-read from .brain_l1_cache.json."""
        cache_data = {"query": "auto_read", "timestamp": time.time(), "hits": ["h1"]}
        with open(bwq._L1_CACHE_PATH, "w") as f:
            json.dump(cache_data, f)
        entry_id = bwq.enqueue()
        with open(bwq._QUEUE_PATH, "r") as f:
            entry = json.loads(f.readline())
        self.assertEqual(entry["l1_cache"]["query"], "auto_read")


class TestStopDrain(unittest.TestCase):
    """Case 3: Stop drain reads L1 cache + processes queue entries."""

    def setUp(self):
        self._orig_queue = bwq._QUEUE_PATH
        self._orig_cache = bwq._L1_CACHE_PATH
        self._orig_drain = bwq._LAST_DRAIN_PATH
        self._tmpdir = tempfile.mkdtemp()
        bwq._QUEUE_PATH = os.path.join(self._tmpdir, "queue.jsonl")
        bwq._L1_CACHE_PATH = os.path.join(self._tmpdir, "l1_cache.json")
        bwq._LAST_DRAIN_PATH = os.path.join(self._tmpdir, "last_drain")

    def tearDown(self):
        bwq._QUEUE_PATH = self._orig_queue
        bwq._L1_CACHE_PATH = self._orig_cache
        bwq._LAST_DRAIN_PATH = self._orig_drain

    def test_drain_processes_pending_entries(self):
        """drain_queue(force=True) must call writeback and mark entries processed."""
        l1 = {"query": "drain_test", "timestamp": time.time()}
        bwq.enqueue(l1_cache_entry=l1)

        fake_writeback = mock.MagicMock(return_value={"neurons_updated": 3})
        fake_module = types.ModuleType("hook_ceo_post_output_brain_writeback")
        fake_module.writeback = fake_writeback
        with mock.patch.dict(sys.modules, {
            "hook_ceo_post_output_brain_writeback": fake_module
        }):
            result = bwq.drain_queue(force=True)

        self.assertEqual(result["processed"], 1)
        self.assertEqual(result["failed"], 0)
        fake_writeback.assert_called_once()
        self.assertFalse(os.path.exists(bwq._QUEUE_PATH))

    def test_drain_with_no_entries_is_noop(self):
        """drain_queue on empty queue returns zero counts without error."""
        result = bwq.drain_queue(force=True)
        self.assertEqual(result["processed"], 0)
        self.assertEqual(result["failed"], 0)
        self.assertEqual(result["skipped"], 0)


class TestFailurePathPreservation(unittest.TestCase):
    """Case 4: Failures must not drop data — entries stay in queue."""

    def setUp(self):
        self._orig_queue = bwq._QUEUE_PATH
        self._orig_cache = bwq._L1_CACHE_PATH
        self._orig_drain = bwq._LAST_DRAIN_PATH
        self._tmpdir = tempfile.mkdtemp()
        bwq._QUEUE_PATH = os.path.join(self._tmpdir, "queue.jsonl")
        bwq._L1_CACHE_PATH = os.path.join(self._tmpdir, "l1_cache.json")
        bwq._LAST_DRAIN_PATH = os.path.join(self._tmpdir, "last_drain")

    def tearDown(self):
        bwq._QUEUE_PATH = self._orig_queue
        bwq._L1_CACHE_PATH = self._orig_cache
        bwq._LAST_DRAIN_PATH = self._orig_drain

    def test_writeback_error_preserves_entry_in_queue(self):
        """If writeback() raises, entry must remain in queue with status=failed."""
        l1 = {"query": "fail_test", "timestamp": time.time()}
        bwq.enqueue(l1_cache_entry=l1)

        fake_writeback = mock.MagicMock(side_effect=RuntimeError("DB connection lost"))
        fake_module = types.ModuleType("hook_ceo_post_output_brain_writeback")
        fake_module.writeback = fake_writeback
        with mock.patch.dict(sys.modules, {
            "hook_ceo_post_output_brain_writeback": fake_module
        }):
            result = bwq.drain_queue(force=True)

        self.assertEqual(result["failed"], 1)
        self.assertEqual(result["processed"], 0)
        self.assertTrue(os.path.exists(bwq._QUEUE_PATH))
        with open(bwq._QUEUE_PATH, "r") as f:
            preserved = json.loads(f.readline())
        self.assertEqual(preserved["status"], "failed")
        self.assertIn("DB connection lost", preserved.get("error", ""))

    def test_missing_writeback_module_preserves_entries(self):
        """If Leo's module not importable, entries stay in queue (failed count)."""
        l1 = {"query": "no_module", "timestamp": time.time()}
        bwq.enqueue(l1_cache_entry=l1)

        # Remove from sys.modules cache so drain_queue attempts fresh import
        saved = sys.modules.pop("hook_ceo_post_output_brain_writeback", None)
        real_import = builtins_import = __builtins__.__import__ if isinstance(__builtins__, dict) is False and hasattr(__builtins__, '__import__') else __import__

        def blocking_import(name, *args, **kwargs):
            if name == "hook_ceo_post_output_brain_writeback":
                raise ImportError("Module not found (test mock)")
            return real_import(name, *args, **kwargs)

        try:
            with mock.patch("builtins.__import__", side_effect=blocking_import):
                result = bwq.drain_queue(force=True)
        finally:
            if saved is not None:
                sys.modules["hook_ceo_post_output_brain_writeback"] = saved

        self.assertEqual(result["failed"], 1)
        self.assertTrue(os.path.exists(bwq._QUEUE_PATH))


if __name__ == "__main__":
    unittest.main()
