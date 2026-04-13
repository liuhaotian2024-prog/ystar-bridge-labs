#!/usr/bin/env python3
"""
Governance config watcher — monitors identity + rules + session config.

Watches:
- .ystar_active_agent (agent identity)
- AGENTS.md (governance rules)
- .ystar_session.json (session config)

On change → invalidates daemon cache → next hook call reloads config.

Backported from exp7_watcher_prototype.py (71fd6db) with multi-file support.
Latency target: <5s from file write → daemon cache invalidation.
"""
import os
import time
import json
import hashlib
import threading
from pathlib import Path
from typing import Optional, Callable


class GovernanceWatcher:
    """Watch governance config files, invalidate daemon cache on change."""

    def __init__(self, repo_root: str, poll_interval: float = 2.0, log_fn: Optional[Callable] = None):
        self.repo_root = Path(repo_root)
        self.active_agent = self.repo_root / ".ystar_active_agent"
        self.agents_md = self.repo_root / "AGENTS.md"
        self.session_json = self.repo_root / ".ystar_session.json"
        self.poll_interval = poll_interval
        self.log = log_fn or print

        # Track file hashes for change detection
        self._hashes = {
            "active_agent": None,
            "agents_md": None,
            "session_json": None,
        }

        self._running = False
        self._thread = None
        self._cache_invalidation_callback = None

    def set_invalidation_callback(self, callback: Callable):
        """Set callback to invalidate daemon cache when files change."""
        self._cache_invalidation_callback = callback

    def _compute_hash(self, file_path: Path) -> str:
        """SHA256 of file for change detection."""
        if not file_path.exists():
            return ""
        try:
            with open(file_path, "rb") as f:
                return hashlib.sha256(f.read()).hexdigest()
        except Exception as e:
            self.log(f"[gov-watcher] hash error {file_path.name}: {e}")
            return ""

    def _check_file_change(self, key: str, file_path: Path) -> bool:
        """Check if file changed since last poll. Returns True if changed."""
        current_hash = self._compute_hash(file_path)
        if current_hash == self._hashes[key]:
            return False

        # File changed
        old_hash = self._hashes[key]
        self._hashes[key] = current_hash

        if old_hash is not None:  # Skip log on first poll
            self.log(f"[gov-watcher] {file_path.name} changed (hash: {current_hash[:8]})")

        return old_hash is not None  # Only return True if this is a real change, not first poll

    def _invalidate_cache(self, changed_files: list):
        """Invalidate daemon cache when config changes."""
        if self._cache_invalidation_callback:
            try:
                self._cache_invalidation_callback(changed_files)
                self.log(f"[gov-watcher] cache invalidated: {', '.join(changed_files)}")
            except Exception as e:
                self.log(f"[gov-watcher] cache invalidation failed: {e}")
        else:
            self.log(f"[gov-watcher] files changed but no invalidation callback set: {changed_files}")

    def _poll_cycle(self) -> None:
        """Single poll cycle — check all files, invalidate if any changed."""
        try:
            changed = []

            if self._check_file_change("active_agent", self.active_agent):
                changed.append(".ystar_active_agent")

            if self._check_file_change("agents_md", self.agents_md):
                changed.append("AGENTS.md")

            if self._check_file_change("session_json", self.session_json):
                changed.append(".ystar_session.json")

            if changed:
                self._invalidate_cache(changed)

        except Exception as e:
            self.log(f"[gov-watcher] poll error: {e}")

    def _watch_loop(self):
        """Background polling loop."""
        self.log(f"[gov-watcher] started (poll={self.poll_interval}s)")

        # Initial hash capture (no invalidation)
        for key, path in [
            ("active_agent", self.active_agent),
            ("agents_md", self.agents_md),
            ("session_json", self.session_json),
        ]:
            self._hashes[key] = self._compute_hash(path)

        # Poll loop
        while self._running:
            time.sleep(self.poll_interval)
            self._poll_cycle()

    def start(self):
        """Start background watcher thread."""
        if self._running:
            self.log("[gov-watcher] already running")
            return

        self._running = True
        self._thread = threading.Thread(target=self._watch_loop, daemon=True, name="GovernanceWatcher")
        self._thread.start()

    def stop(self):
        """Stop watcher thread."""
        self._running = False
        if self._thread:
            self._thread.join(timeout=5)
            self.log("[gov-watcher] stopped")


def create_watcher(repo_root: str, log_fn: Optional[Callable] = None) -> GovernanceWatcher:
    """Factory function for hook_wrapper.py integration."""
    return GovernanceWatcher(repo_root, poll_interval=2.0, log_fn=log_fn)


if __name__ == "__main__":
    # Standalone test
    import sys
    repo = sys.argv[1] if len(sys.argv) > 1 else os.getcwd()

    def test_callback(changed_files):
        print(f"[TEST] Cache invalidated for: {changed_files}")

    watcher = create_watcher(repo, log_fn=print)
    watcher.set_invalidation_callback(test_callback)
    watcher.start()

    print("Watcher running. Edit .ystar_active_agent, AGENTS.md, or .ystar_session.json to test.")
    print("Ctrl+C to stop.")
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        watcher.stop()
        print("\nWatcher stopped.")
