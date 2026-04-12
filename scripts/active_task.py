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
    is_mission = getattr(args, 'mission', False)

    # GOV-010 fix: auto-detect Autonomous Mission from task description
    # even if --mission flag wasn't explicitly passed
    MISSION_KEYWORDS = [
        "autonomous mission", "自主任务", "自主长期",
        "按自主框架", "autonomous", "mission",
    ]
    task_lower = args.task.lower()
    if not is_mission and any(kw in task_lower for kw in MISSION_KEYWORDS):
        print(f"[active-task] ⚠ Task description matches Autonomous Mission keywords.")
        print(f"[active-task] 按 governance/WORKING_STYLE.md 第十一条走完整四阶段闭环：")
        print(f"[active-task]   阶段一：认知建构（7 层）→ Board 批准框架报告")
        print(f"[active-task]   阶段二：执行落地（方案设计 + 伦理检查）")
        print(f"[active-task]   阶段三：观察与数据收集（48h 内）")
        print(f"[active-task]   阶段四：迭代与重新校准")
        print(f"[active-task] 自动标记为 --mission 模式。")
        is_mission = True

    state = {
        "task_id": task_id,
        "actor": role,
        "task": args.task,
        "total_steps": args.steps,
        "current_step": 0,
        "estimate_minutes": args.estimate_minutes,
        "status": "active",
        "mission": is_mission,
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

    # Closure 3: Stream continuation.json update (fail-open)
    try:
        from continuation_writer import rewrite_continuation
        rewrite_continuation(REPO_ROOT, {
            "event": "INTENT_COMPLETED",
            "task_id": current["task_id"],
            "role": role,
            "task": current["task"],
            "output": args.output,
        })
    except Exception as e:
        import time as _time
        with open(REPO_ROOT / "scripts" / "hook_debug.log", "a") as f:
            f.write(f"[{_time.time()}] continuation hook failed: {e}\n")

    print(f"OK: task completed")
    print(f"  task     : {current['task'][:60]}")
    print(f"  duration : {duration/60:.1f}min")
    print(f"  output   : {args.output}")

    # Auto knowledge check if output is in knowledge/
    _auto_knowledge_check(role, args.output)

    # Mission mode: if the original task was --mission, auto-cycle
    if current.get("mission"):
        print(f"\n[mission] Autonomous Mission cycle complete. "
              f"Next cycle can be started with:")
        print(f"  python3.11 scripts/active_task.py start --actor {role} "
              f"--task \"{current['task']}\" --steps {current['total_steps']} "
              f"--estimate-minutes {current.get('estimate_minutes', 30)} --mission")

    return 0


# ─── main ────────────────────────────────────────────────────────────

def _auto_knowledge_check(role, output_path):
    """After complete, if output is in knowledge/, run contradiction check."""
    if not output_path or "knowledge/" not in output_path:
        return
    target = REPO_ROOT / output_path
    if not target.exists() or not target.suffix == ".md":
        return
    try:
        from knowledge_check import check_file, load_config
        endpoints, model, cieu_db = load_config()
        print(f"\n[knowledge-check] scanning {target.name} for contradictions...")
        contradictions = check_file(target, role, endpoints, model, cieu_db)
        if contradictions:
            print(f"[knowledge-check] ⚠ {len(contradictions)} contradiction(s) → CIEU")
        else:
            print(f"[knowledge-check] ✓ no contradictions found")
    except Exception as e:
        print(f"[knowledge-check] skip (fail-open): {e}")


def cmd_mission_status(args):
    """Show all active/completed missions across roles."""
    print("Active tasks by role:")
    print("-" * 60)
    found = False
    for role in sorted(ROLES):
        state = load_state(role)
        if state:
            found = True
            status = state.get("status", "?")
            task = state.get("task", "?")[:50]
            step = state.get("current_step", 0)
            total = state.get("total_steps", 0)
            icon = {"active": "▶", "completed": "✓", "stalled": "⚠"}
            print(f"  {icon.get(status, '?')} {role:<10} [{status}] {task} ({step}/{total})")
    if not found:
        print("  (no active tasks)")
    return 0


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
    s.add_argument("--mission", action="store_true",
                   help="Mark as Autonomous Mission (auto-cycles, doesn't truly close)")

    u = sub.add_parser("update", help="Report progress on active task")
    u.add_argument("--actor", required=True)
    u.add_argument("--step", type=int, required=True, help="Current step number")
    u.add_argument("--note", default="", help="Progress note")

    c = sub.add_parser("complete", help="Close the active task")
    c.add_argument("--actor", required=True)
    c.add_argument("--output", required=True, help="Output path or description")
    c.add_argument("--note", default="", help="Completion note")

    ms = sub.add_parser("mission-status", help="Show all active tasks across roles")
    ms.add_argument("--actor", default=None, help="Filter by role (optional)")

    args = p.parse_args()
    if not args.command:
        p.print_help()
        return 2

    handlers = {
        "start": cmd_start,
        "update": cmd_update,
        "complete": cmd_complete,
        "mission-status": cmd_mission_status,
    }
    return handlers[args.command](args)


if __name__ == "__main__":
    sys.exit(main())
