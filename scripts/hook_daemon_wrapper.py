#!/usr/bin/env python3
"""
Hook Daemon Heartbeat Wrapper — emits DAEMON_HEARTBEAT CIEU event every interval.
Closes CZL-ARCH-7 gap: daemon_heartbeats_7d was 0.
"""
import json
import os
import sys
import time

sys.path.insert(0, os.path.dirname(__file__))
from _cieu_helpers import emit_cieu


def heartbeat_once() -> bool:
    """Emit a single DAEMON_HEARTBEAT CIEU event. Returns success."""
    return emit_cieu(
        event_type="DAEMON_HEARTBEAT",
        decision="info",
        passed=1,
        task_description="Hook daemon heartbeat",
        params_json=json.dumps({"pid": os.getpid(), "ts": time.time()}),
    )


def run_loop(interval: int = 60):
    """Run heartbeat loop forever at `interval` seconds."""
    while True:
        heartbeat_once()
        time.sleep(interval)


if __name__ == "__main__":
    interval = int(sys.argv[1]) if len(sys.argv) > 1 else 60
    run_loop(interval)
