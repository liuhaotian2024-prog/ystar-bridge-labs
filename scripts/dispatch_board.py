#!/usr/bin/env python3
"""
Dispatch Board CLI — CEO T1 task posting + engineer claim/complete
Implements dispatch board per governance/cto_role_v2_and_dispatch_board_20260416.md Appendix C (CZL-68)
"""
import argparse
import json
import sys
import fcntl
from datetime import datetime, timezone
from pathlib import Path

# Import CIEU helpers
sys.path.insert(0, str(Path(__file__).parent))
from _cieu_helpers import emit_cieu

BOARD_PATH = Path("/Users/haotianliu/.openclaw/workspace/ystar-company/governance/dispatch_board.json")


def _read_board():
    """Read dispatch board with advisory lock."""
    if not BOARD_PATH.exists():
        return {"tasks": []}
    with open(BOARD_PATH, "r") as f:
        fcntl.flock(f.fileno(), fcntl.LOCK_SH)
        data = json.load(f)
        fcntl.flock(f.fileno(), fcntl.LOCK_UN)
    return data


def _write_board(data):
    """Write dispatch board with exclusive lock."""
    BOARD_PATH.parent.mkdir(parents=True, exist_ok=True)
    with open(BOARD_PATH, "w") as f:
        fcntl.flock(f.fileno(), fcntl.LOCK_EX)
        json.dump(data, f, indent=2)
        fcntl.flock(f.fileno(), fcntl.LOCK_UN)


def post_task(args):
    """Post a new T1 task to dispatch board."""
    board = _read_board()

    # Check for duplicate atomic_id
    if any(t["atomic_id"] == args.atomic_id for t in board["tasks"]):
        print(f"ERROR: Task {args.atomic_id} already exists", file=sys.stderr)
        return 1

    task = {
        "atomic_id": args.atomic_id,
        "scope": args.scope,
        "description": args.description,
        "urgency": args.urgency,
        "estimated_tool_uses": args.estimated_tool_uses,
        "status": "open",
        "posted_at": datetime.now(timezone.utc).isoformat(),
        "claimed_by": None,
        "claimed_at": None,
        "completed_at": None,
        "completion_receipt": None,
    }

    board["tasks"].append(task)
    _write_board(board)

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

    board = _read_board()

    # Find first open task (FIFO)
    claimed = False
    for task in board["tasks"]:
        if task["status"] == "open":
            task["status"] = "claimed"
            task["claimed_by"] = args.engineer_id
            task["claimed_at"] = datetime.now(timezone.utc).isoformat()
            claimed = True

            _write_board(board)

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

    if not claimed:
        print("No open tasks available", file=sys.stderr)
        return 1


def complete_task(args):
    """Engineer marks task complete with receipt."""
    board = _read_board()

    task = next((t for t in board["tasks"] if t["atomic_id"] == args.atomic_id), None)
    if not task:
        print(f"ERROR: Task {args.atomic_id} not found", file=sys.stderr)
        return 1

    if task["status"] != "claimed":
        print(f"ERROR: Task {args.atomic_id} status={task['status']}, expected claimed", file=sys.stderr)
        return 1

    # Read receipt file
    receipt_path = Path(args.receipt_file)
    if not receipt_path.exists():
        print(f"ERROR: Receipt file {args.receipt_file} not found", file=sys.stderr)
        return 1
    receipt_text = receipt_path.read_text()

    task["status"] = "completed"
    task["completed_at"] = datetime.now(timezone.utc).isoformat()
    task["completion_receipt"] = receipt_text

    _write_board(board)

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

    args = parser.parse_args()
    return args.func(args)


if __name__ == "__main__":
    sys.exit(main())
