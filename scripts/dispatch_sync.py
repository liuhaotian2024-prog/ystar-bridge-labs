#!/usr/bin/env python3
"""
Dispatch Sync Layer — CEO T1 fast-lane awareness for CTO
Implements 3-layer sync per governance/tiered_routing_protocol_v1_sync_addendum.md CZL-67
"""
import argparse
import json
import sys
import time
from datetime import datetime, timedelta, timezone
from pathlib import Path

# Import CIEU helpers
sys.path.insert(0, str(Path(__file__).parent))
from _cieu_helpers import emit_cieu

DISPATCH_LOG_PATH = Path("/Users/haotianliu/.openclaw/workspace/ystar-company/governance/active_dispatch_log.md")


def record(engineer: str, atomic_id: str, scope: str, tier: str = "T1", reason: str = "", expected_completion: str = "30m"):
    """
    Append dispatch record to active_dispatch_log.md + emit CIEU event.

    Args:
        engineer: ryan-platform / leo-kernel / maya-governance / jordan-domains
        atomic_id: CZL-XX identifier
        scope: File paths (comma-separated)
        tier: T1 / T2 / T3
        reason: Optional human-readable reason
        expected_completion: Window estimate (15m/30m/1h/2h)
    """
    # Ensure log file exists
    if not DISPATCH_LOG_PATH.exists():
        DISPATCH_LOG_PATH.parent.mkdir(parents=True, exist_ok=True)
        DISPATCH_LOG_PATH.write_text(
            "# Active CEO Dispatch Log\n\n"
            "Format: [timestamp] CEO_DISPATCH(engineer, atomic_id=X, scope=[...], tier=T1, expected_completion=Xm)\n"
            "**IMMUTABLE APPEND-ONLY** — do NOT edit past entries.\n\n"
        )

    # Parse scope into list
    scope_list = [s.strip() for s in scope.split(",")]

    # Append record
    timestamp = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    record_line = (
        f"[{timestamp}] CEO_DISPATCH({engineer}, atomic_id={atomic_id}, "
        f"scope={scope_list}, tier={tier}, expected_completion={expected_completion})\n"
    )

    with open(DISPATCH_LOG_PATH, "a") as f:
        f.write(record_line)

    # Emit CIEU event
    payload = {
        "agent_target": engineer,
        "atomic_id": atomic_id,
        "file_paths_in_scope": scope_list,
        "tier": tier,
        "expected_completion_window": expected_completion,
        "reason": reason
    }

    emit_cieu(
        event_type="CEO_DIRECT_DISPATCH_TIER1",
        decision="info",
        passed=1,
        task_description=f"CEO dispatched {engineer} for {atomic_id}",
        params_json=json.dumps(payload)
    )

    print(f"✓ Dispatch recorded: {engineer} {atomic_id} ({tier})")
    print(f"  Scope: {scope_list}")
    print(f"  CIEU event: CEO_DIRECT_DISPATCH_TIER1 emitted")


def get_recent(window_hours: int = 24):
    """
    Retrieve recent dispatch records within window_hours.

    Args:
        window_hours: Time window in hours (default 24)

    Returns:
        Formatted list of recent dispatches (newest-first)
    """
    if not DISPATCH_LOG_PATH.exists():
        print("No dispatch log found.", file=sys.stderr)
        return

    cutoff_time = datetime.now(timezone.utc) - timedelta(hours=window_hours)

    entries = []
    with open(DISPATCH_LOG_PATH, "r") as f:
        for line in f:
            if not line.startswith("[2"):
                continue  # Skip header/empty lines

            # Parse timestamp from [YYYY-MM-DDTHH:MM:SSZ]
            try:
                ts_end = line.index("]")
                ts_str = line[1:ts_end]
                entry_time = datetime.fromisoformat(ts_str.replace("Z", "+00:00"))

                if entry_time >= cutoff_time:
                    entries.append(line.strip())
            except (ValueError, IndexError):
                continue  # Malformed line

    # Print newest-first
    for entry in reversed(entries):
        print(entry)


def main():
    parser = argparse.ArgumentParser(description="Dispatch Sync Layer CLI")
    subparsers = parser.add_subparsers(dest="command", required=True)

    # record subcommand
    record_parser = subparsers.add_parser("record", help="Record new dispatch")
    record_parser.add_argument("engineer", help="Target engineer (ryan-platform/leo-kernel/maya-governance/jordan-domains)")
    record_parser.add_argument("atomic_id", help="CZL-XX identifier")
    record_parser.add_argument("scope", help="File paths (comma-separated)")
    record_parser.add_argument("--tier", default="T1", help="Tier (T1/T2/T3)")
    record_parser.add_argument("--reason", default="", help="Optional reason")
    record_parser.add_argument("--expected_completion", default="30m", help="Window estimate")

    # get_recent subcommand
    recent_parser = subparsers.add_parser("get_recent", help="Get recent dispatches")
    recent_parser.add_argument("--window_hours", type=int, default=24, help="Time window in hours")

    args = parser.parse_args()

    if args.command == "record":
        record(
            engineer=args.engineer,
            atomic_id=args.atomic_id,
            scope=args.scope,
            tier=args.tier,
            reason=args.reason,
            expected_completion=args.expected_completion
        )
    elif args.command == "get_recent":
        get_recent(window_hours=args.window_hours)


if __name__ == "__main__":
    main()
