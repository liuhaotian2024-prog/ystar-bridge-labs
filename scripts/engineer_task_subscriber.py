#!/usr/bin/env python3
"""
Engineer Task Subscriber Daemon — poll dispatch board + auto-claim tasks
Implements engineer daemon per governance/cto_role_v2_and_dispatch_board_20260416.md Appendix C (CZL-68)
"""
import argparse
import json
import sys
import subprocess
import time
from pathlib import Path

# Import CIEU helpers
sys.path.insert(0, str(Path(__file__).parent))
from _cieu_helpers import emit_cieu

BOARD_PATH = Path("/Users/haotianliu/.openclaw/workspace/ystar-company/governance/dispatch_board.json")
PID_FILE = Path("/Users/haotianliu/.openclaw/workspace/ystar-company/scripts/.engineer_subscriber.pid")


def start_daemon(engineer_id: str, poll_interval: int = 10):
    """Start polling daemon for engineer."""
    # Write PID file
    PID_FILE.parent.mkdir(parents=True, exist_ok=True)
    import os
    PID_FILE.write_text(str(os.getpid()))

    emit_cieu("ENGINEER_DAEMON_START", {"engineer_id": engineer_id})

    print(f"Engineer {engineer_id} daemon started (poll interval: {poll_interval}s)", file=sys.stderr)

    while True:
        try:
            # Try to claim next available task
            result = subprocess.run(
                [sys.executable, str(Path(__file__).parent / "dispatch_board.py"), "claim", "--engineer_id", engineer_id],
                capture_output=True,
                text=True,
            )

            if result.returncode == 0:
                # Successfully claimed task
                claimed_id = result.stdout.strip()
                print(f"Claimed task: {claimed_id}", file=sys.stderr)
                # ARCH RULING CZL-DISPATCH-EXEC (2026-04-19):
                # Subscriber CANNOT spawn Agent tool calls -- structural Claude Code boundary.
                # Only the main Claude session's tool-use loop can originate Agent calls.
                # A Python subprocess has no mechanism to inject Agent calls into the parent.
                # Execution is CEO-session-owned. Subscriber role: claim reservation + CIEU audit only.
                # See Y-star-gov/reports/cto/CZL-DISPATCH-EXEC-ruling.md
                emit_cieu(
                    "SUBSCRIBER_CLAIM_PENDING_SPAWN",
                    decision="info",
                    passed=1,
                    task_description=f"Claim pending CEO spawn: {claimed_id} by {engineer_id}",
                    params_json=json.dumps({
                        "atomic_id": claimed_id,
                        "engineer_id": engineer_id,
                        "spawn_owner": "ceo-main-session",
                    })
                )

            time.sleep(poll_interval)

        except KeyboardInterrupt:
            emit_cieu("ENGINEER_DAEMON_STOP", {"engineer_id": engineer_id})
            PID_FILE.unlink(missing_ok=True)
            print(f"\nEngineer {engineer_id} daemon stopped", file=sys.stderr)
            break


def stop_daemon():
    """Stop running daemon."""
    if not PID_FILE.exists():
        print("No daemon running (no PID file)", file=sys.stderr)
        return 1

    pid = int(PID_FILE.read_text().strip())
    import os
    import signal
    try:
        os.kill(pid, signal.SIGTERM)
        PID_FILE.unlink()
        print(f"Stopped daemon (PID {pid})", file=sys.stderr)
        return 0
    except ProcessLookupError:
        print(f"Daemon PID {pid} not running (stale PID file removed)", file=sys.stderr)
        PID_FILE.unlink()
        return 1


def daemon_status():
    """Check daemon status."""
    if not PID_FILE.exists():
        print("Daemon: NOT RUNNING", file=sys.stderr)
        return 1

    pid = int(PID_FILE.read_text().strip())
    import os
    try:
        os.kill(pid, 0)  # Signal 0 checks if process exists
        print(f"Daemon: RUNNING (PID {pid})", file=sys.stderr)
        return 0
    except ProcessLookupError:
        print(f"Daemon: STALE PID {pid} (process not found)", file=sys.stderr)
        PID_FILE.unlink()
        return 1


def main():
    parser = argparse.ArgumentParser(description="Engineer Task Subscriber Daemon")
    subparsers = parser.add_subparsers(dest="command", required=True)

    # start
    start_parser = subparsers.add_parser("start", help="Start daemon")
    start_parser.add_argument("--engineer_id", required=True, help="ryan-platform/leo-kernel/maya-governance/jordan-domains")
    start_parser.add_argument("--poll_interval", type=int, default=10, help="Poll interval in seconds")
    start_parser.set_defaults(func=lambda args: start_daemon(args.engineer_id, args.poll_interval))

    # stop
    stop_parser = subparsers.add_parser("stop", help="Stop daemon")
    stop_parser.set_defaults(func=lambda args: stop_daemon())

    # status
    status_parser = subparsers.add_parser("status", help="Check daemon status")
    status_parser.set_defaults(func=lambda args: daemon_status())

    args = parser.parse_args()
    return args.func(args)


if __name__ == "__main__":
    sys.exit(main())
