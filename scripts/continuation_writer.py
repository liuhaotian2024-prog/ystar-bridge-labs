#!/usr/bin/env python3.11
"""
continuation_writer.py — Atomic streaming updates to memory/continuation.json (Closure 3).

Called from active_task.py complete() hook to maintain continuation state
in near-real-time without blocking the main task lifecycle.

Features:
- Atomic write (temp file + os.replace)
- Idempotent (identical updates produce same result modulo timestamp)
- Fail-open (all exceptions swallowed, logged to hook_debug.log)

Usage:
  from continuation_writer import rewrite_continuation
  rewrite_continuation(REPO_ROOT, {
      "event": "INTENT_COMPLETED",
      "task_id": "abc123",
      "role": "cto",
      "task": "implement feature X",
      "output": "path/to/output"
  })
"""
import json
import os
import time
from pathlib import Path


def rewrite_continuation(repo_root: Path, updates: dict) -> None:
    """
    Apply updates to memory/continuation.json atomically.

    Updates schema on INTENT_COMPLETED event:
    - action_queue: mark task done, set completed_at
    - obligations: remove those cleared by this task
    - team_state[role]: update last_completed
    - last_updated_ts: refresh to current time

    Args:
        repo_root: Repository root path
        updates: dict with keys: event, task_id, role, task, output
    """
    try:
        _rewrite_continuation_inner(repo_root, updates)
    except Exception as e:
        # Fail-open: log but don't raise
        debug_log = repo_root / "scripts" / "hook_debug.log"
        with open(debug_log, "a") as f:
            f.write(f"[{time.time()}] continuation_writer failed: {e}\n")


def _rewrite_continuation_inner(repo_root: Path, updates: dict):
    """Inner implementation (can raise exceptions)."""
    continuation_path = repo_root / "memory" / "continuation.json"

    # Load existing or create empty template
    if continuation_path.exists():
        with open(continuation_path) as f:
            state = json.load(f)
    else:
        state = {
            "generated_at": "",
            "generated_by": "system",
            "campaign": {},
            "team_state": {},
            "action_queue": [],
            "anti_patterns": [],
            "obligations": []
        }

    # Apply updates based on event type
    event = updates.get("event")
    if event != "INTENT_COMPLETED":
        return  # Only handle completed events for now

    task_id = updates.get("task_id")
    role = updates.get("role")
    task = updates.get("task")
    output = updates.get("output")
    ts = time.time()

    # Update action_queue: mark item done
    for item in state.get("action_queue", []):
        if item.get("task_id") == task_id:
            item["done"] = True
            item["completed_at"] = ts
            break

    # Update obligations: remove those cleared by this task
    state["obligations"] = [
        ob for ob in state.get("obligations", [])
        if ob.get("cleared_by") != task_id
    ]

    # Update team_state for this role
    if "team_state" not in state:
        state["team_state"] = {}

    if role:
        state["team_state"][role] = {
            "task": task or "unknown",
            "progress": "completed",
            "blocked": False,
            "last_completed": task or "unknown",
            "last_completed_at": ts
        }

    # Update timestamp
    state["last_updated_ts"] = ts
    state["generated_at"] = time.strftime("%Y-%m-%dT%H:%M:%S", time.localtime(ts))

    # Atomic write: temp file → replace
    tmp_path = continuation_path.with_suffix(f".tmp.{os.getpid()}")
    with open(tmp_path, "w") as f:
        json.dump(state, f, indent=2)

    # Atomic rename (POSIX guarantee)
    os.replace(tmp_path, continuation_path)
