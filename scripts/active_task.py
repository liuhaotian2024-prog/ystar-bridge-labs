#!/usr/bin/env python3.11
"""
active_task.py — GOV-010 Phase 2: Task lifecycle management.

Three actions implementing the universal task lifecycle:

  start    — declare intent: what, how many steps, estimated duration
  update   — report progress: current step, remaining estimate
  complete — close task: record output path, mark done

State persists in knowledge/{role}/active_task.json (one active task
per role at a time). Each action also writes a CIEU event so the
full lifecycle is auditable.

CIEU event types:
  INTENT_DECLARED   — task started
  PROGRESS_UPDATED  — step completed / progress reported
  INTENT_COMPLETED  — task finished
  INTENT_STALLED    — (future: scheduler detects no progress update)

Usage:
  python3.11 scripts/active_task.py start --actor cto \\
      --task "build theory library for system_architecture" \\
      --steps 4 --estimate-minutes 60

  python3.11 scripts/active_task.py update --actor cto \\
      --step 2 --note "completed search phase, starting deep-dive"

  python3.11 scripts/active_task.py complete --actor cto \\
      --output "knowledge/cto/theory/system_architecture.md" \\
      --note "4 theories added, 2 gaps identified"
"""
import argparse
import json
import os
import sys
import time
import uuid
from pathlib import Path

from ystar.governance.cieu_store import CIEUStore

REPO_ROOT = Path(__file__).resolve().parent.parent
SESSION_PATH = REPO_ROOT / ".ystar_session.json"
ROLES = {"ceo", "cto", "cmo", "cso", "cfo", "secretary"}
LEGACY = {
    "ethan_wright": "cto", "aiden_liu": "ceo", "sofia_blake": "cmo",
    "zara_johnson": "cso", "marco_rivera": "cfo", "samantha_lin": "secretary",
}


def canonical(actor: str) -> str:
    return LEGACY.get(actor, actor)


def load_db() -> str:
    try:
        with open(SESSION_PATH) as f:
            return json.load(f).get("cieu_db") or str(REPO_ROOT / ".ystar_cieu.db")
    except (OSError, json.JSONDecodeError):
        return str(REPO_ROOT / ".ystar_cieu.db")


def state_path(role: str) -> Path:
    return REPO_ROOT / "knowledge" / role / "active_task.json"


def load_state(role: str) -> dict | None:
    p = state_path(role)
    if not p.exists():
        return None
    try:
        return json.loads(p.read_text())
    except (json.JSONDecodeError, OSError):
        return None


def save_state(role: str, state: dict | None):
    p = state_path(role)
    p.parent.mkdir(parents=True, exist_ok=True)
    if state is None:
        if p.exists():
            p.unlink()
    else:
        p.write_text(json.dumps(state, indent=2, ensure_ascii=False))


def write_cieu(db: str, event_type: str, role: str, params: dict):
    cieu = CIEUStore(db_path=db)
    record = {
        "event_id": str(uuid.uuid4()),
        "session_id": params.get("task_id", "active_task"),
        "agent_id": role,
        "event_type": event_type,
        "decision": "info",
        "evidence_grade": "ops",
        "created_at": time.time(),
        "seq_global": time.time_ns() // 1000,
        "params": params,
        "violations": [],
        "drift_detected": False,
        "human_initiator": role,
    }
    cieu.write_dict(record)


# ─── start ───────────────────────────────────────────────────────────

def cmd_start(args):
    role = canonical(args.actor)
    if role not in ROLES:
        print(f"ERROR: --actor must be one of {sorted(ROLES)}", file=sys.stderr)
        return 2

    current = load_state(role)
    if current and current.get("status") == "active":
        print(f"ERROR: {role} already has an active task: {current.get('task')!r}",
              file=sys.stderr)
        print(f"  Complete it first: active_task.py complete --actor {role} ...",
              file=sys.stderr)
        return 1

    task_id = f"task_{uuid.uuid4().hex[:12]}"
    now = time.time()
    state = {
        "task_id": task_id,
        "actor": role,
        "task": args.task,
        "total_steps": args.steps,
        "current_step": 0,
        "estimate_minutes": args.estimate_minutes,
        "status": "active",
        "started_at": now,
        "last_update": now,
        "notes": [],
    }
    save_state(role, state)
    write_cieu(load_db(), "INTENT_DECLARED", role, {
        "task_id": task_id,
        "task": args.task,
        "total_steps": args.steps,
        "estimate_minutes": args.estimate_minutes,
        "declared_at": now,
    })

    print(f"OK: task started")
    print(f"  task_id : {task_id}")
    print(f"  actor   : {role}")
    print(f"  task    : {args.task}")
    print(f"  steps   : {args.steps}")
    print(f"  estimate: {args.estimate_minutes}min")
    return 0


# ─── update ──────────────────────────────────────────────────────────

def cmd_update(args):
    role = canonical(args.actor)
    current = load_state(role)
    if not current or current.get("status") != "active":
        print(f"ERROR: {role} has no active task to update", file=sys.stderr)
        return 1

    current["current_step"] = args.step
    current["last_update"] = time.time()
    if args.note:
        current["notes"].append({"step": args.step, "note": args.note, "at": time.time()})
    save_state(role, current)

    write_cieu(load_db(), "PROGRESS_UPDATED", role, {
        "task_id": current["task_id"],
        "step": args.step,
        "total_steps": current["total_steps"],
        "note": args.note or "",
        "updated_at": time.time(),
    })

    remaining = current["total_steps"] - args.step
    print(f"OK: progress updated")
    print(f"  task    : {current['task'][:60]}")
    print(f"  step    : {args.step}/{current['total_steps']}")
    print(f"  remaining: {remaining} steps")
    return 0


# ─── complete ────────────────────────────────────────────────────────

def cmd_complete(args):
    role = canonical(args.actor)
    current = load_state(role)
    if not current or current.get("status") != "active":
        print(f"ERROR: {role} has no active task to complete", file=sys.stderr)
        return 1

    now = time.time()
    duration = now - current.get("started_at", now)
    current["status"] = "completed"
    current["completed_at"] = now
    current["duration_s"] = duration
    current["output"] = args.output
    if args.note:
        current["notes"].append({"step": "complete", "note": args.note, "at": now})
    save_state(role, current)

    write_cieu(load_db(), "INTENT_COMPLETED", role, {
        "task_id": current["task_id"],
        "task": current["task"],
        "output": args.output,
        "duration_s": duration,
        "steps_completed": current["current_step"],
        "total_steps": current["total_steps"],
        "note": args.note or "",
        "completed_at": now,
    })

    print(f"OK: task completed")
    print(f"  task     : {current['task'][:60]}")
    print(f"  duration : {duration/60:.1f}min")
    print(f"  output   : {args.output}")
    return 0


# ─── main ────────────────────────────────────────────────────────────

def main():
    p = argparse.ArgumentParser(
        description="Task lifecycle: start → update → complete (GOV-010 Phase 2)",
    )
    sub = p.add_subparsers(dest="command")

    s = sub.add_parser("start", help="Declare intent to start a task")
    s.add_argument("--actor", required=True)
    s.add_argument("--task", required=True, help="What you're going to do")
    s.add_argument("--steps", type=int, required=True, help="Number of steps")
    s.add_argument("--estimate-minutes", type=int, required=True, help="Estimated duration")

    u = sub.add_parser("update", help="Report progress on active task")
    u.add_argument("--actor", required=True)
    u.add_argument("--step", type=int, required=True, help="Current step number")
    u.add_argument("--note", default="", help="Progress note")

    c = sub.add_parser("complete", help="Close the active task")
    c.add_argument("--actor", required=True)
    c.add_argument("--output", required=True, help="Output path or description")
    c.add_argument("--note", default="", help="Completion note")

    args = p.parse_args()
    if not args.command:
        p.print_help()
        return 2

    return {"start": cmd_start, "update": cmd_update, "complete": cmd_complete}[args.command](args)


if __name__ == "__main__":
    sys.exit(main())
