#!/usr/bin/env python3
"""
Governance config watcher — monitors identity + rules + session config + whitelists.

Watches:
- .ystar_active_agent (agent identity)
- AGENTS.md (governance rules)
- .ystar_session.json (session config)
- governance/whitelist/*.yaml (procedure whitelists)

On change → invalidates daemon cache → next hook call reloads config.
Emits WHITELIST_UPDATE CIEU event when whitelist files change.

Backported from exp7_watcher_prototype.py (71fd6db) with multi-file support.
Extended for A018 Phase 1 (whitelist sync mechanism B).
Latency target: <5s from file write → daemon cache invalidation.
"""
import os
import time
import json
import hashlib
import threading
from pathlib import Path
from typing import Optional, Callable, Dict, List


class GovernanceWatcher:
    """Watch governance config files + whitelists, invalidate daemon cache on change."""

    def __init__(self, repo_root: str, poll_interval: float = 2.0, log_fn: Optional[Callable] = None, cieu_emit_fn: Optional[Callable] = None):
        self.repo_root = Path(repo_root)
        self.active_agent = self.repo_root / ".ystar_active_agent"
        self.agents_md = self.repo_root / "AGENTS.md"
        self.session_json = self.repo_root / ".ystar_session.json"
        self.whitelist_dir = self.repo_root / "governance" / "whitelist"
        self.poll_interval = poll_interval
        self._base_poll_interval = poll_interval  # Store base interval for storm backoff
        self.log = log_fn or print
        self.cieu_emit = cieu_emit_fn  # Optional CIEU event emitter

        # Track file hashes for change detection (static files)
        self._hashes = {
            "active_agent": None,
            "agents_md": None,
            "session_json": None,
        }

        # Track mtime for quick change detection (before expensive hash)
        self._mtimes = {
            "active_agent": None,
            "agents_md": None,
            "session_json": None,
        }

        # Track whitelist YAML hashes (dynamic: multiple files)
        self._whitelist_hashes: Dict[str, str] = {}
        self._whitelist_mtimes: Dict[str, float] = {}

        # High-frequency mtime storm detection (DOS mitigation)
        self._mtime_change_count: Dict[str, int] = {}  # file -> consecutive change count
        self._skip_until_poll: Dict[str, int] = {}     # file -> skip N polls

        # Debounce: coalesce rapid mtime changes (DOS mitigation)
        self._pending_invalidation = set()
        self._last_change_time = 0.0
        self._debounce_window = 0.1  # 100ms

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
        if not file_path.exists():
            return False

        try:
            current_mtime = file_path.stat().st_mtime
        except Exception:
            return False

        # Fast path: mtime unchanged → skip hash
        if current_mtime == self._mtimes[key]:
            return False

        # mtime changed → compute hash to confirm real change (not just touch)
        current_hash = self._compute_hash(file_path)
        if current_hash == self._hashes[key]:
            # False alarm: mtime changed but content same (touch without edit)
            self._mtimes[key] = current_mtime
            return False

        # Real change
        old_hash = self._hashes[key]
        self._hashes[key] = current_hash
        self._mtimes[key] = current_mtime

        if old_hash is not None:  # Skip log on first poll
            self.log(f"[gov-watcher] {file_path.name} changed (hash: {current_hash[:8]})")

        return old_hash is not None  # Only return True if this is a real change, not first poll

    def _scan_whitelist_yamls(self) -> List[Path]:
        """Scan governance/whitelist/ for *.yaml files."""
        if not self.whitelist_dir.exists():
            return []
        try:
            return list(self.whitelist_dir.glob("*.yaml"))
        except Exception as e:
            self.log(f"[gov-watcher] whitelist scan error: {e}")
            return []

    def _check_whitelist_changes(self) -> List[str]:
        """Check all whitelist YAML files for changes. Returns list of changed filenames."""
        changed = []
        current_yamls = {p.name: p for p in self._scan_whitelist_yamls()}

        # Check existing files for changes + detect new files
        for name, path in current_yamls.items():
            # Storm mitigation: skip files in cooldown
            if name in self._skip_until_poll:
                self._skip_until_poll[name] -= 1
                if self._skip_until_poll[name] <= 0:
                    del self._skip_until_poll[name]
                    del self._mtime_change_count[name]
                    self.log(f"[gov-watcher] storm cooldown ended: {name}")
                continue

            try:
                current_mtime = path.stat().st_mtime
            except Exception:
                continue

            old_mtime = self._whitelist_mtimes.get(name)
            old_hash = self._whitelist_hashes.get(name)

            # Fast path: mtime unchanged → skip + reset storm counter
            if old_mtime is not None and current_mtime == old_mtime:
                if name in self._mtime_change_count:
                    del self._mtime_change_count[name]
                continue

            # Storm detection: if file changed <0.5s ago → active storm → skip hash
            if old_mtime is not None:
                time_since_change = time.time() - current_mtime
                if time_since_change < 0.5:  # File modified in last 500ms → storm
                    self._mtime_change_count[name] = self._mtime_change_count.get(name, 0) + 1
                    if self._mtime_change_count[name] == 1:
                        self.log(f"[gov-watcher] STORM suspected on {name} (mtime delta={time_since_change:.3f}s), deferring hash")
                    if self._mtime_change_count[name] >= 3:
                        self._skip_until_poll[name] = 5  # Skip next 5 polls
                        self.log(f"[gov-watcher] STORM confirmed on {name}, entering 10s cooldown")
                    self._whitelist_mtimes[name] = current_mtime  # Update mtime, skip hash
                    continue

            # mtime changed, not storm → compute hash
            current_hash = self._compute_hash(path)
            if current_hash != old_hash:
                self._whitelist_hashes[name] = current_hash
                self._whitelist_mtimes[name] = current_mtime
                if old_hash is not None:  # File was tracked before → it changed
                    changed.append(f"governance/whitelist/{name}")
                    self.log(f"[gov-watcher] whitelist/{name} changed (hash: {current_hash[:8]})")
                elif old_hash is None and name in self._whitelist_hashes:
                    # New file creation (not in initial hash capture)
                    # Note: this branch won't hit on first poll because we do initial capture
                    # But if a file is created AFTER startup, old_hash is None
                    changed.append(f"governance/whitelist/{name} [NEW]")
                    self.log(f"[gov-watcher] whitelist/{name} created (hash: {current_hash[:8]})")
            else:
                # False alarm: mtime changed but content same
                self._whitelist_mtimes[name] = current_mtime

        # Detect new files (not in previous poll but exists now)
        new_files = set(current_yamls.keys()) - set(self._whitelist_hashes.keys())
        for name in new_files:
            path = current_yamls[name]
            current_hash = self._compute_hash(path)
            self._whitelist_hashes[name] = current_hash
            changed.append(f"governance/whitelist/{name} [NEW]")
            self.log(f"[gov-watcher] whitelist/{name} created (hash: {current_hash[:8]})")

        # Detect deleted files
        deleted = set(self._whitelist_hashes.keys()) - set(current_yamls.keys())
        for name in deleted:
            del self._whitelist_hashes[name]
            changed.append(f"governance/whitelist/{name} [DELETED]")
            self.log(f"[gov-watcher] whitelist/{name} deleted")

        return changed

    def _emit_whitelist_update_event(self, changed_files: List[str]):
        """Emit WHITELIST_UPDATE CIEU event when whitelist files change."""
        if self.cieu_emit:
            try:
                self.cieu_emit(
                    event_type="WHITELIST_UPDATE",
                    data={
                        "changed_files": changed_files,
                        "timestamp": time.time(),
                        "whitelist_dir": str(self.whitelist_dir),
                    },
                    severity="info"
                )
                self.log(f"[gov-watcher] CIEU event emitted: WHITELIST_UPDATE ({len(changed_files)} files)")
            except Exception as e:
                self.log(f"[gov-watcher] CIEU emission failed: {e}")

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
        """Single poll cycle — check all files + whitelists, invalidate if any changed."""
        try:
            changed = []

            if self._check_file_change("active_agent", self.active_agent):
                changed.append(".ystar_active_agent")

            if self._check_file_change("agents_md", self.agents_md):
                changed.append("AGENTS.md")

            if self._check_file_change("session_json", self.session_json):
                changed.append(".ystar_session.json")

            # Check whitelist YAMLs
            whitelist_changed = self._check_whitelist_changes()
            if whitelist_changed:
                changed.extend(whitelist_changed)
                self._emit_whitelist_update_event(whitelist_changed)

            if changed:
                # Debounce: defer invalidation, coalesce rapid changes
                self._pending_invalidation.update(changed)
                self._last_change_time = time.time()

        except Exception as e:
            self.log(f"[gov-watcher] poll error: {e}")

    def _watch_loop(self):
        """Background polling loop."""
        self.log(f"[gov-watcher] started (poll={self.poll_interval}s)")

        # Initial hash + mtime capture (no invalidation)
        for key, path in [
            ("active_agent", self.active_agent),
            ("agents_md", self.agents_md),
            ("session_json", self.session_json),
        ]:
            self._hashes[key] = self._compute_hash(path)
            try:
                self._mtimes[key] = path.stat().st_mtime if path.exists() else None
            except Exception:
                self._mtimes[key] = None

        # Initial whitelist hash + mtime capture
        for yaml_path in self._scan_whitelist_yamls():
            self._whitelist_hashes[yaml_path.name] = self._compute_hash(yaml_path)
            try:
                self._whitelist_mtimes[yaml_path.name] = yaml_path.stat().st_mtime
            except Exception:
                self._whitelist_mtimes[yaml_path.name] = None

        # Poll loop
        while self._running:
            time.sleep(self.poll_interval)
            self._poll_cycle()

            # Flush debounced invalidations
            if self._pending_invalidation:
                if time.time() - self._last_change_time > self._debounce_window:
                    self._invalidate_cache(list(self._pending_invalidation))
                    self._pending_invalidation = set()

            # Storm backoff: if any file in cooldown, increase poll interval
            if self._skip_until_poll:
                self.poll_interval = self._base_poll_interval * 3  # 6s during storm
            else:
                self.poll_interval = self._base_poll_interval  # Restore normal 2s

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


def create_watcher(repo_root: str, log_fn: Optional[Callable] = None, cieu_emit_fn: Optional[Callable] = None) -> GovernanceWatcher:
    """Factory function for hook_wrapper.py integration."""
    return GovernanceWatcher(repo_root, poll_interval=2.0, log_fn=log_fn, cieu_emit_fn=cieu_emit_fn)


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
