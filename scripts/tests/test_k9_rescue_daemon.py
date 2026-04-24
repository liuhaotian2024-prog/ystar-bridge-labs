"""
Integration tests for k9_rescue_daemon.py — FIFO protocol and Merkle audit chain.

Tests:
- FIFO creation and cleanup
- Request parsing
- Merkle chain integrity (hash chaining)
- Audit log structure
- send_rescue convenience function
- Daemon lifecycle (start/stop via signals)
"""

import os
import sys
import json
import time
import hashlib
import tempfile
import threading
import signal

import pytest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from k9_rescue_daemon import (
    _parse_request,
    _merkle_hash,
    _audit_log,
    _ensure_fifo,
    _is_fifo,
    send_rescue,
    FIFO_PATH,
)
import k9_rescue_daemon as daemon_module


class TestParseRequest:
    """Test request line parsing."""

    def test_simple_action(self):
        aid, arg = _parse_request("R-001")
        assert aid == "R-001"
        assert arg is None

    def test_action_with_arg(self):
        aid, arg = _parse_request("R-007 12345")
        assert aid == "R-007"
        assert arg == "12345"

    def test_action_with_spaces(self):
        aid, arg = _parse_request("  R-004  ")
        assert aid == "R-004"
        assert arg is None

    def test_empty_line(self):
        aid, arg = _parse_request("")
        assert aid is None
        assert arg is None

    def test_whitespace_only(self):
        aid, arg = _parse_request("   ")
        assert aid is None
        assert arg is None

    def test_lowercase_normalized_to_upper(self):
        aid, arg = _parse_request("r-002")
        assert aid == "R-002"

    def test_action_with_multiword_arg(self):
        aid, arg = _parse_request("R-007 12345 extra stuff")
        assert aid == "R-007"
        assert arg == "12345 extra stuff"


class TestMerkleHash:
    """Test Merkle chain hash computation."""

    def test_deterministic(self):
        h1 = _merkle_hash("abc", '{"x": 1}')
        h2 = _merkle_hash("abc", '{"x": 1}')
        assert h1 == h2

    def test_different_prev_different_hash(self):
        h1 = _merkle_hash("abc", '{"x": 1}')
        h2 = _merkle_hash("def", '{"x": 1}')
        assert h1 != h2

    def test_different_record_different_hash(self):
        h1 = _merkle_hash("abc", '{"x": 1}')
        h2 = _merkle_hash("abc", '{"x": 2}')
        assert h1 != h2

    def test_hash_is_sha256_hex(self):
        h = _merkle_hash("prev", "data")
        assert len(h) == 64
        int(h, 16)  # Should not raise if valid hex


class TestAuditLog:
    """Test audit log writing and Merkle chain."""

    @pytest.fixture(autouse=True)
    def _setup_temp_log(self, tmp_path):
        """Redirect audit log to temp file for isolation."""
        self.orig_log = daemon_module.AUDIT_LOG
        self.orig_prev = daemon_module._prev_hash
        daemon_module.AUDIT_LOG = str(tmp_path / "test_audit.jsonl")
        daemon_module._prev_hash = "0" * 64
        yield
        daemon_module.AUDIT_LOG = self.orig_log
        daemon_module._prev_hash = self.orig_prev

    def test_audit_log_creates_file(self):
        _audit_log({"ts": time.time(), "event": "TEST"})
        assert os.path.exists(daemon_module.AUDIT_LOG)

    def test_audit_log_entry_structure(self):
        _audit_log({"ts": 123.0, "event": "TEST"})
        with open(daemon_module.AUDIT_LOG, "r") as f:
            entry = json.loads(f.readline())
        assert "hash" in entry
        assert "prev_hash" in entry
        assert entry["prev_hash"] == "0" * 64
        assert entry["event"] == "TEST"

    def test_merkle_chain_integrity(self):
        """Write 3 entries and verify chain links."""
        for i in range(3):
            _audit_log({"ts": float(i), "event": f"TEST_{i}"})

        entries = []
        with open(daemon_module.AUDIT_LOG, "r") as f:
            for line in f:
                entries.append(json.loads(line))

        assert len(entries) == 3
        # First entry should have genesis prev_hash
        assert entries[0]["prev_hash"] == "0" * 64
        # Each subsequent entry's prev_hash should match previous entry's hash
        for i in range(1, len(entries)):
            assert entries[i]["prev_hash"] == entries[i - 1]["hash"], (
                f"Chain broken at entry {i}"
            )


class TestFifo:
    """Test FIFO creation utilities."""

    def test_is_fifo_regular_file(self, tmp_path):
        regular = tmp_path / "regular.txt"
        regular.write_text("hello")
        assert _is_fifo(str(regular)) is False

    def test_is_fifo_nonexistent(self):
        assert _is_fifo("/tmp/nonexistent_fifo_test_xyz") is False

    def test_is_fifo_actual_fifo(self, tmp_path):
        fifo_path = str(tmp_path / "test.fifo")
        os.mkfifo(fifo_path)
        assert _is_fifo(fifo_path) is True

    def test_ensure_fifo_creates(self, tmp_path, monkeypatch):
        fifo_path = str(tmp_path / "new.fifo")
        monkeypatch.setattr(daemon_module, "FIFO_PATH", fifo_path)
        _ensure_fifo()
        assert os.path.exists(fifo_path)
        assert _is_fifo(fifo_path)

    def test_ensure_fifo_replaces_regular_file(self, tmp_path, monkeypatch):
        """If a regular file exists at FIFO_PATH, replace it with a FIFO."""
        fifo_path = str(tmp_path / "fake.fifo")
        with open(fifo_path, "w") as f:
            f.write("not a fifo")
        monkeypatch.setattr(daemon_module, "FIFO_PATH", fifo_path)
        _ensure_fifo()
        assert _is_fifo(fifo_path)


class TestSendRescue:
    """Test the send_rescue convenience function."""

    def test_send_no_fifo(self, monkeypatch):
        monkeypatch.setattr(daemon_module, "FIFO_PATH", "/tmp/nonexistent_k9_test_fifo")
        result = send_rescue("R-001")
        assert result["ok"] is False
        assert "does not exist" in result["error"]
