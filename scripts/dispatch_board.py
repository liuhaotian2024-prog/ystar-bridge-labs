#!/usr/bin/env python3
"""
Dispatch Board CLI — CEO T1 task posting + engineer claim/complete
Implements dispatch board per governance/cto_role_v2_and_dispatch_board_20260416.md Appendix C (CZL-68)
"""
import argparse
import json
import os
import sys
import fcntl
import tempfile
from datetime import datetime, timezone
from pathlib import Path

# Import CIEU helpers
sys.path.insert(0, str(Path(__file__).parent))
from _cieu_helpers import emit_cieu

BOARD_PATH = Path("/Users/haotianliu/.openclaw/workspace/ystar-company/governance/dispatch_board.json")
LOCK_PATH = BOARD_PATH.parent / ".dispatch_board.lock"


def _acquire_lock():
    """Acquire exclusive file lock for read-modify-write critical section.

    Returns lock file descriptor. Caller must call _release_lock(fd) when done.
    Uses a separate lockfile so open("w") truncation cannot race with readers.
    """
    LOCK_PATH.parent.mkdir(parents=True, exist_ok=True)
    fd = os.open(str(LOCK_PATH), os.O_CREAT | os.O_RDWR, 0o644)
    fcntl.flock(fd, fcntl.LOCK_EX)
    return fd


def _release_lock(fd):
    """Release file lock acquired by _acquire_lock."""
    fcntl.flock(fd, fcntl.LOCK_UN)
    os.close(fd)


def _read_board_locked():
    """Read dispatch board. MUST be called while holding the lock."""
    if not BOARD_PATH.exists():
        return {"tasks": []}
    with open(BOARD_PATH, "r") as f:
        data = json.load(f)
    return data


def _write_board_locked(data, prev_task_count=None):
    """Write dispatch board atomically. MUST be called while holding the lock.

    Uses temp-file-then-rename to prevent partial writes.
    Includes sanity check: refuses to write if task count drops by >50%
    when previous count exceeds 5 (wipe protection).
    """
    new_count = len(data.get("tasks", []))

    # Sanity check: detect accidental wipe
    if prev_task_count is not None and prev_task_count > 5:
        if new_count < prev_task_count * 0.5:
            msg = (
                f"WIPE PROTECTION: refusing to write dispatch_board.json — "
                f"task count would drop from {prev_task_count} to {new_count}. "
                f"This looks like an accidental wipe."
            )
            print(f"ERROR: {msg}", file=sys.stderr)
            try:
                emit_cieu(
                    "DISPATCH_BOARD_WIPE_BLOCKED",
                    decision="deny",
                    passed=0,
                    task_description=msg,
                    params_json=json.dumps({
                        "prev_count": prev_task_count,
                        "new_count": new_count,
                    })
                )
            except Exception:
                pass
            raise RuntimeError(msg)

    BOARD_PATH.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.NamedTemporaryFile(
        "w", dir=str(BOARD_PATH.parent), delete=False, suffix=".tmp"
    ) as f:
        json.dump(data, f, indent=2)
        tmp = f.name
    os.replace(tmp, str(BOARD_PATH))


def _read_board():
    """Read dispatch board (convenience wrapper, acquires lock briefly).

    For read-only operations. For read-modify-write, use
    _acquire_lock / _read_board_locked / _write_board_locked / _release_lock.
    """
    lock_fd = _acquire_lock()
    try:
        return _read_board_locked()
    finally:
        _release_lock(lock_fd)


def _write_board(data):
    """Write dispatch board (convenience wrapper for legacy callers).

    WARNING: For read-modify-write patterns, use the locked variants instead
    to avoid TOCTOU races.
    """
    lock_fd = _acquire_lock()
    try:
        _write_board_locked(data)
    finally:
        _release_lock(lock_fd)


def _czl_reject_with_guide(violated_rule: str,
                           violated_detail: str,
                           atomic_id: str = "") -> str:
    """Format REDIRECT-style reject using existing Y*gov schema
    (boundary_enforcer.py `wrong_action` + `correct_steps[]` + `skill_ref`
    + hook.py `[Y*] REDIRECT: ...` + `FIX_COMMAND: ...`).

    P-12 先查后造: aligns key names with existing boundary_enforcer +
    hook.py REDIRECT format, does NOT invent new schema. Board 2026-04-20
    "governance = 门卫 + 导游" thesis was ALREADY implemented at runtime
    layer (hook.py line 1260-1358); this helper brings dispatch_board CLI
    layer into alignment.
    """
    example_cmd = (
        f"python3 scripts/dispatch_board.py post \\\n"
        f"    --atomic_id {atomic_id or 'CZL-EXAMPLE'} \\\n"
        f"    --scope scripts/hook_wrapper.py,tests/ \\\n"
        f"    --urgency P0 --estimated_tool_uses 8 \\\n"
        f"    --description 'Fix hook_wrapper.py line X bug + add pytest + "
        f"verify zero regression on existing 17 forget_guard rules'"
    )
    return (
        f"\n[Y*] REDIRECT: {violated_rule} — {violated_detail}\n"
        f"VIOLATED_M_TAG: M-2a\n"
        f"WRONG_ACTION: dispatch_board.post(description={violated_detail!r})\n"
        f"CORRECT_STEPS:\n"
        f"  1. y_star (goal): define verifiable end state (>=20 chars)\n"
        f"  2. x_t (pre-state): describe current observable state\n"
        f"  3. u (actions): list concrete tool calls\n"
        f"  4. y_t_plus_1 (post): predicted state after delivery\n"
        f"  5. rt_value (target): 0.0 = closure\n"
        f"FIX_COMMAND: re-run dispatch_board.post with concrete --description\n"
        f"FIX_EXAMPLE:\n{example_cmd}\n"
        f"SKILL_REF: governance/czl_unified_communication_protocol_v1.md\n"
    )


def post_task(args):
    """Post a new T1 task to dispatch board.

    2026-04-21 Milestone 9b: every post ALSO publishes a CZL envelope to
    .czl_bus.jsonl so forget_guard + omission subscribers see it.
    Enforcement: description field must contain a verifiable goal statement
    (proxy for y_star) OR caller must provide --y-star / --goal. Empty or
    generic description rejected (prevents content-less whiteboard posts).
    """
    # ── CZL Enforcement Gate (门卫 + 导游) ─────────────────────────────
    # Board 2026-04-21 铁律: deny 时必给 fix_command + template + example.
    # Violating "governance = 门卫 + 导游" thesis if we only raise ERROR.
    desc = (args.description or "").strip()
    y_star = getattr(args, "y_star", None) or desc
    GENERIC_FILLERS = {"todo", "tbd", "fix", "do it", "see above", ""}
    if len(y_star) < 20 or y_star.lower() in GENERIC_FILLERS:
        reason = ("too short" if len(y_star) < 20
                  else "generic filler (TBD/TODO/etc)")
        print(_czl_reject_with_guide(
            violated_rule="czl_minimum_goal_content",
            violated_detail=(f"description/y_star {reason}, got "
                             f"{len(y_star)} chars: {y_star!r}"),
            atomic_id=args.atomic_id,
        ), file=sys.stderr)
        return 2

    lock_fd = _acquire_lock()
    try:
        board = _read_board_locked()
        prev_count = len(board["tasks"])

        # Check for duplicate atomic_id
        if any(t["atomic_id"] == args.atomic_id for t in board["tasks"]):
            print(f"ERROR: Task {args.atomic_id} already exists", file=sys.stderr)
            return 1

        posted_at = datetime.now(timezone.utc).isoformat()
        task = {
            "atomic_id": args.atomic_id,
            "scope": args.scope,
            "description": args.description,
            "urgency": args.urgency,
            "estimated_tool_uses": args.estimated_tool_uses,
            "status": "open",
            "posted_at": posted_at,
            "claimed_by": None,
            "claimed_at": None,
            "completed_at": None,
            "completion_receipt": None,
        }

        board["tasks"].append(task)
        _write_board_locked(board, prev_task_count=prev_count)
    finally:
        _release_lock(lock_fd)

    # ── CZL Bus Publish ───────────────────────────────────────────────
    try:
        import sys as _sys
        _sys.path.insert(0, str(Path(__file__).parent))
        from czl_bus import CZLMessageEnvelope, publish as czl_publish
        import time as _time
        urgency_to_deadline_sec = {"P0": 7200, "P1": 86400, "P2": 259200, "P3": 604800}
        deadline_sec = urgency_to_deadline_sec.get(args.urgency, 259200)
        env = CZLMessageEnvelope(
            y_star=y_star,
            x_t=f"posted at {posted_at}, scope={args.scope}",
            u=[args.description],  # actions description (narrative; structured later)
            y_t_plus_1=f"task {args.atomic_id} closed with Rt+1=0 receipt",
            rt_value=1.0,  # open dispatch (not yet closed)
            task_id=args.atomic_id,
            sender="ceo",
            recipient="whiteboard",
            message_type="whiteboard_post",
            deadline=_time.time() + deadline_sec,
            urgency=args.urgency,
        )
        czl_publish(env)
    except Exception as _czl_err:
        # Non-fatal: bus publish failure must not block task post, but emit warn
        print(f"[warn] czl_bus publish failed: {_czl_err}", file=sys.stderr)

    emit_cieu(
        "CEO_DISPATCH_BOARD_POST",
        decision="info",
        passed=1,
        task_description=f"Posted {args.atomic_id}",
        params_json=json.dumps({
            "atomic_id": args.atomic_id,
            "scope": args.scope,
            "urgency": args.urgency,
        })
    )

    # CZL-DISPATCH-EXEC: Write spawn-intent for CEO pickup
    # CEO main thread reads this to discover un-spawned claims.
    try:
        from dispatch_role_routing import route_scope
        routed_to = route_scope(args.scope)
    except ImportError:
        routed_to = "eng-cto-triage"  # fallback if routing module not yet available

    intent_path = Path(__file__).parent / ".pending_spawns.jsonl"
    intent = json.dumps({
        "atomic_id": args.atomic_id,
        "scope": args.scope,
        "routed_to": routed_to,
        "posted_at": task["posted_at"],
        "prompt_hint": args.description,
    })
    with open(intent_path, "a") as f:
        f.write(intent + "\n")

    print(f"Posted task {args.atomic_id} to dispatch board")
    return 0


def claim_task(args):
    """Engineer claims next available task (FIFO by posted_at)."""
    # Validate engineer_id
    VALID_ENGINEERS = [
        "eng-kernel", "eng-governance", "eng-platform", "eng-domains",
        "eng-data", "eng-security", "eng-ml", "eng-perf", "eng-compliance",
        "leo-kernel", "maya-governance", "ryan-platform", "jordan-domains"
    ]
    if args.engineer_id not in VALID_ENGINEERS:
        print(f"ERROR: Invalid engineer_id '{args.engineer_id}'. Must be one of: {', '.join(VALID_ENGINEERS)}", file=sys.stderr)
        return 1

    lock_fd = _acquire_lock()
    try:
        board = _read_board_locked()
        prev_count = len(board["tasks"])

        # Find first open task (FIFO)
        for task in board["tasks"]:
            if task["status"] == "open":
                task["status"] = "claimed"
                task["claimed_by"] = args.engineer_id
                task["claimed_at"] = datetime.now(timezone.utc).isoformat()

                _write_board_locked(board, prev_task_count=prev_count)

                emit_cieu(
                    "ENGINEER_CLAIM_TASK",
                    decision="info",
                    passed=1,
                    task_description=f"{args.engineer_id} claimed {task['atomic_id']}",
                    params_json=json.dumps({
                        "engineer_id": args.engineer_id,
                        "atomic_id": task["atomic_id"],
                        "scope": task["scope"],
                    })
                )

                print(f"Claimed task {task['atomic_id']} by {args.engineer_id}")
                return 0

        print("No open tasks available", file=sys.stderr)
        return 1
    finally:
        _release_lock(lock_fd)


def complete_task(args):
    """Engineer marks task complete with receipt."""
    # Read receipt file before acquiring lock (I/O outside critical section)
    receipt_path = Path(args.receipt_file)
    if not receipt_path.exists():
        print(f"ERROR: Receipt file {args.receipt_file} not found", file=sys.stderr)
        return 1
    receipt_text = receipt_path.read_text()

    lock_fd = _acquire_lock()
    try:
        board = _read_board_locked()
        prev_count = len(board["tasks"])

        task = next((t for t in board["tasks"] if t["atomic_id"] == args.atomic_id), None)
        if not task:
            print(f"ERROR: Task {args.atomic_id} not found", file=sys.stderr)
            return 1

        if task["status"] != "claimed":
            print(f"ERROR: Task {args.atomic_id} status={task['status']}, expected claimed", file=sys.stderr)
            return 1

        task["status"] = "completed"
        task["completed_at"] = datetime.now(timezone.utc).isoformat()
        task["completion_receipt"] = receipt_text

        _write_board_locked(board, prev_task_count=prev_count)
    finally:
        _release_lock(lock_fd)

    emit_cieu(
        "ENGINEER_COMPLETE_TASK",
        decision="info",
        passed=1,
        task_description=f"{task['claimed_by']} completed {args.atomic_id}",
        params_json=json.dumps({
            "engineer_id": task["claimed_by"],
            "atomic_id": args.atomic_id,
            "receipt_preview": receipt_text[:200],
        })
    )

    print(f"Completed task {args.atomic_id}")
    return 0


def status(args):
    """Show dispatch board status."""
    board = _read_board()

    print(f"Dispatch Board Status ({len(board['tasks'])} tasks)")
    print("=" * 80)
    for task in board["tasks"]:
        print(f"{task['atomic_id']} [{task['status']}] {task['urgency']} | {task['scope']}")
        if task["claimed_by"]:
            print(f"  Claimed by: {task['claimed_by']} at {task['claimed_at']}")
        if task["completed_at"]:
            print(f"  Completed at: {task['completed_at']}")

    return 0


def evaluate_blocks(args):
    """Evaluate directive liveness for blocked/blocked_on tasks.

    Phase 1: Reports only. Does NOT auto-unblock.
    Loads directive annotations from governance/directives/, runs evaluator
    primitives, prints verdict per directive.
    """
    # Add Y-star-gov to path for directive_evaluator import
    ygov_dir = "/Users/haotianliu/.openclaw/workspace/Y-star-gov"
    if ygov_dir not in sys.path:
        sys.path.insert(0, ygov_dir)

    try:
        from ystar.governance.directive_evaluator import (
            evaluate_all,
            print_summary,
        )
    except ImportError as e:
        print(f"ERROR: Cannot import directive_evaluator: {e}", file=sys.stderr)
        print("Ensure Y-star-gov is accessible.", file=sys.stderr)
        return 1

    # Paths
    company_dir = str(Path(__file__).parent.parent)
    directives_dir = str(Path(company_dir) / "governance" / "directives")
    board_path = str(BOARD_PATH)

    # Base dirs for file resolution (Y-star-gov for product docs, company for governance)
    base_dirs = [
        ygov_dir,
        company_dir,
    ]

    # Evaluate all directives
    results = evaluate_all(
        directives_dir,
        base_dirs=base_dirs,
        board_path=board_path,
    )

    if not results:
        print("No directive annotations found in governance/directives/")
        return 0

    # Print summary
    counts = print_summary(results)

    # Cross-reference with blocked tasks on whiteboard
    board = _read_board()
    blocked_tasks = [
        t for t in board.get("tasks", [])
        if t.get("blocked_on") or t.get("blocked_on_directive_id")
    ]

    if blocked_tasks:
        print(f"\n  Blocked tasks on whiteboard: {len(blocked_tasks)}")
        # Build directive verdict lookup
        verdict_map = {r["directive_id"]: r["verdict"] for r in results}
        for task in blocked_tasks:
            directive_ref = task.get("blocked_on_directive_id", task.get("blocked_on", ""))
            task_verdict = verdict_map.get(directive_ref, "NO_ANNOTATION")
            marker = {"LIVE": "[!]", "RELEASED": "[v]", "AMBIGUOUS": "[?]", "NO_ANNOTATION": "[-]"}
            print(f"    {marker.get(task_verdict, '[ ]')} {task['atomic_id']}: blocked_on={directive_ref} -> {task_verdict}")

    emit_cieu(
        "DIRECTIVE_LIVENESS_EVAL",
        decision="info",
        passed=1,
        task_description=f"Evaluated {len(results)} directives: LIVE={counts.get('LIVE',0)} RELEASED={counts.get('RELEASED',0)} AMBIGUOUS={counts.get('AMBIGUOUS',0)}",
        params_json=json.dumps({
            "directive_count": len(results),
            "counts": counts,
            "blocked_tasks": len(blocked_tasks) if blocked_tasks else 0,
        })
    )

    return 0


def pending_spawns(args):
    """Show un-spawned claims: intents in .pending_spawns.jsonl not yet completed/in-progress."""
    intent_path = Path(__file__).parent / ".pending_spawns.jsonl"
    if not intent_path.exists():
        print("No pending spawns (file not found)")
        return 0

    board = _read_board()
    # Build set of atomic_ids that are completed or in-progress (claimed with spawn evidence)
    completed_ids = {
        t["atomic_id"] for t in board["tasks"]
        if t["status"] in ("completed",)
    }

    pending = []
    for line in intent_path.read_text().splitlines():
        line = line.strip()
        if not line:
            continue
        try:
            intent = json.loads(line)
        except json.JSONDecodeError:
            continue
        if intent.get("atomic_id") not in completed_ids:
            pending.append(intent)

    if not pending:
        print("No pending spawns (all intents completed or no intents)")
        return 0

    from datetime import datetime, timezone
    now = datetime.now(timezone.utc)
    print(f"=== Pending Spawns ({len(pending)} un-spawned) ===")
    for intent in pending:
        posted = intent.get("posted_at", "unknown")
        age_str = ""
        try:
            posted_dt = datetime.fromisoformat(posted)
            age_secs = (now - posted_dt).total_seconds()
            if age_secs > 600:
                age_str = f" [OVERDUE {int(age_secs)}s -- hard TTL exceeded]"
            elif age_secs > 300:
                age_str = f" [SOFT OVERDUE {int(age_secs)}s]"
            else:
                age_str = f" [{int(age_secs)}s ago]"
        except Exception:
            pass
        print(json.dumps(intent) + age_str)

    return 0


def main():
    parser = argparse.ArgumentParser(description="Dispatch Board CLI")
    subparsers = parser.add_subparsers(dest="command", required=True)

    # post
    post_parser = subparsers.add_parser("post", help="Post new T1 task")
    post_parser.add_argument("--atomic_id", required=True, help="CZL-XX identifier")
    post_parser.add_argument("--scope", required=True, help="File paths (comma-separated)")
    post_parser.add_argument("--description", required=True, help="Task description")
    post_parser.add_argument("--urgency", required=True, choices=["P0", "P1", "P2"], help="Priority")
    post_parser.add_argument("--estimated_tool_uses", type=int, required=True, help="Tool use estimate")
    post_parser.set_defaults(func=post_task)

    # claim
    claim_parser = subparsers.add_parser("claim", help="Claim next available task")
    claim_parser.add_argument("--engineer_id", required=True, help="ryan-platform/leo-kernel/maya-governance/jordan-domains")
    claim_parser.set_defaults(func=claim_task)

    # complete
    complete_parser = subparsers.add_parser("complete", help="Complete claimed task")
    complete_parser.add_argument("--atomic_id", required=True, help="CZL-XX identifier")
    complete_parser.add_argument("--receipt_file", required=True, help="Path to completion receipt .md file")
    complete_parser.set_defaults(func=complete_task)

    # status
    status_parser = subparsers.add_parser("status", help="Show dispatch board status")
    status_parser.set_defaults(func=status)

    # evaluate_blocks (CZL-GOV-LIVE-EVAL Phase 1: directive liveness report)
    eval_parser = subparsers.add_parser("evaluate_blocks",
                                         help="Evaluate directive liveness for blocked tasks")
    eval_parser.set_defaults(func=evaluate_blocks)

    # pending (CZL-DISPATCH-EXEC: list un-spawned claims)
    pending_parser = subparsers.add_parser("pending", help="Show un-spawned dispatch claims")
    pending_parser.set_defaults(func=pending_spawns)

    args = parser.parse_args()
    return args.func(args)


if __name__ == "__main__":
    sys.exit(main())
