#!/usr/bin/env python3
"""Restart readiness validator - implements restart_preparation_model_v1.md §2 7-step checks.

Per Ethan #137 §8 Step B: Pre-restart verification to ensure state preserved + system clean.

Usage:
    python3 scripts/restart_readiness_check.py [--dry-run] [--cause Health|Deploy|Periodic|Emergency]

Output: JSON {readiness: READY|PARTIAL|BLOCKED, failed_steps: [list], recommendation: str}
"""

import sys
import json
import sqlite3
import subprocess
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Tuple


def check_receipts_complete() -> Tuple[bool, str]:
    """Step 1: Verify all sub-agent receipts received (dispatch_log count == REPLY_REGISTERED count)."""
    try:
        dispatch_log = Path("governance/active_dispatch_log.md")
        if not dispatch_log.exists():
            return True, "no active dispatches"

        # Count dispatches
        content = dispatch_log.read_text()
        in_flight = content.count("status: dispatched") + content.count("status: in_flight")

        # Count REPLY_REGISTERED from CIEU
        db_path = Path(".ystar_cieu.db")
        if not db_path.exists():
            return False, f"CIEU db missing, cannot verify {in_flight} dispatches"

        conn = sqlite3.connect(str(db_path))
        cursor = conn.execute("SELECT COUNT(*) FROM events WHERE event_type='REPLY_REGISTERED'")
        reply_count = cursor.fetchone()[0]
        conn.close()

        if in_flight > reply_count:
            return False, f"{in_flight} dispatches > {reply_count} receipts"
        return True, f"{in_flight} dispatches == {reply_count} receipts"
    except Exception as e:
        return False, f"receipt check failed: {e}"


def check_daemons_live() -> Tuple[bool, str]:
    """Step 2: Verify 4 daemons alive (k9_routing_subscriber, k9_alarm_consumer, cto_dispatch_broker, engineer_task_subscriber)."""
    daemons = ["k9_routing_subscriber", "k9_alarm_consumer", "cto_dispatch_broker", "engineer_task_subscriber"]
    alive = []
    dead = []

    for daemon in daemons:
        try:
            result = subprocess.run(["pgrep", "-f", daemon], capture_output=True, text=True, timeout=5)
            if result.returncode == 0:
                alive.append(daemon)
            else:
                dead.append(daemon)
        except Exception as e:
            dead.append(f"{daemon} (check failed: {e})")

    if dead:
        return False, f"{len(alive)}/4 alive (dead: {', '.join(dead)})"
    return True, "4/4 daemons alive"


def check_ac_threshold() -> Tuple[bool, float, str]:
    """Step 3: Verify AC ≥75 or document degradation justification."""
    try:
        result = subprocess.run(
            ["python3", "scripts/session_watchdog.py", "--statusline"],
            capture_output=True, text=True, timeout=10
        )
        output = result.stdout.strip()

        # Parse AC:XX from output
        if "AC:" not in output:
            return False, 0.0, "AC signal missing from watchdog"

        ac_part = output.split("AC:")[1].split()[0]
        # Strip ANSI codes
        ac_str = ac_part.replace('\x1b[0;32m', '').replace('\x1b[0m', '').replace('\x1b[1;33m', '')
        ac = float(ac_str)

        if ac < 40:
            return False, ac, "AC < 40 (critical degradation, restart mandatory)"
        elif ac < 75:
            # Check for justification file
            justification = Path("reports/governance/ac_degradation_justification.md")
            if not justification.exists():
                return False, ac, "AC < 75 without documented justification"
            return True, ac, f"AC={ac} < 75 but justified"
        return True, ac, f"AC={ac} ≥ 75"
    except Exception as e:
        return False, 0.0, f"AC check failed: {e}"


def check_session_closed() -> Tuple[bool, str]:
    """Step 4: Verify session_close_yml.py ran (memory preserved)."""
    try:
        continuation = Path("memory/continuation.json")
        if not continuation.exists():
            return False, "continuation.json missing (session_close_yml.py not run)"

        # Verify well-formed JSON
        with open(continuation) as f:
            data = json.load(f)

        # Check mtime recent
        mtime = continuation.stat().st_mtime
        now = datetime.now().timestamp()
        if now - mtime > 86400:  # 24h
            return False, f"continuation.json stale (mtime={mtime}, age={now-mtime:.0f}s > 24h)"

        return True, f"session closed (continuation.json fresh, age={now-mtime:.0f}s)"
    except json.JSONDecodeError as e:
        return False, f"continuation.json malformed: {e}"
    except Exception as e:
        return False, f"session close check failed: {e}"


def check_archive_written() -> Tuple[bool, str]:
    """Step 5: Verify .czl_subgoals.json archived."""
    try:
        archive_dir = Path("memory/archive")
        if not archive_dir.exists():
            return False, "archive/ directory missing"

        archives = list(archive_dir.glob("czl_subgoals_*.json"))
        if not archives:
            return False, "no czl_subgoals archives found"

        # Check most recent archive is fresh
        latest = max(archives, key=lambda p: p.stat().st_mtime)
        mtime = latest.stat().st_mtime
        now = datetime.now().timestamp()

        if now - mtime > 3600:  # 1h
            return False, f"latest archive stale (age={now-mtime:.0f}s > 1h)"

        return True, f"archive fresh ({latest.name}, age={now-mtime:.0f}s)"
    except Exception as e:
        return False, f"archive check failed: {e}"


def check_continuation_written() -> Tuple[bool, str]:
    """Step 6: Verify continuation.json has non-empty action_queue."""
    try:
        continuation = Path("memory/continuation.json")
        if not continuation.exists():
            return False, "continuation.json missing"

        with open(continuation) as f:
            data = json.load(f)

        action_queue = data.get("action_queue", [])
        if not action_queue:
            return False, "action_queue empty (context loss)"

        campaign = data.get("campaign", "")
        if not campaign:
            return False, "campaign field missing"

        return True, f"{len(action_queue)} actions queued, campaign={campaign}"
    except Exception as e:
        return False, f"continuation check failed: {e}"


def check_baseline_snapshot() -> Tuple[bool, str]:
    """Step 7: Verify HP+AC baseline snapshot written to reports/."""
    try:
        reports_dir = Path("reports")
        baselines = list(reports_dir.glob("restart_baseline_*.md"))

        if not baselines:
            return False, "no restart_baseline snapshot found"

        # Check most recent is fresh
        latest = max(baselines, key=lambda p: p.stat().st_mtime)
        mtime = latest.stat().st_mtime
        now = datetime.now().timestamp()

        if now - mtime > 600:  # 10min
            return False, f"latest baseline stale (age={now-mtime:.0f}s > 10min)"

        return True, f"baseline fresh ({latest.name}, age={now-mtime:.0f}s)"
    except Exception as e:
        return False, f"baseline snapshot check failed: {e}"


def main():
    """Execute 7-step readiness check and output JSON result."""
    dry_run = "--dry-run" in sys.argv
    cause = "Manual"
    for arg in sys.argv:
        if arg.startswith("--cause="):
            cause = arg.split("=")[1]

    steps = [
        ("receipts_complete", check_receipts_complete),
        ("daemons_live", check_daemons_live),
        ("ac_threshold", lambda: check_ac_threshold()),
        ("session_closed", check_session_closed),
        ("archive_written", check_archive_written),
        ("continuation_written", check_continuation_written),
        ("baseline_snapshot", check_baseline_snapshot),
    ]

    failed_steps = []
    details = {}
    ac_score = None

    for step_name, check_fn in steps:
        result = check_fn()
        if step_name == "ac_threshold":
            passed, ac_score, msg = result
        else:
            passed, msg = result

        details[step_name] = {"passed": passed, "message": msg}
        if not passed:
            failed_steps.append(step_name)

    # Determine readiness
    if not failed_steps:
        readiness = "READY"
        recommendation = "Safe to restart"
    elif "ac_threshold" in failed_steps and ac_score and ac_score < 40:
        readiness = "BLOCKED"
        recommendation = "Critical AC degradation - restart mandatory after receipt completion"
    elif "daemons_live" in failed_steps:
        readiness = "BLOCKED"
        recommendation = "Dead daemons detected - recycle before restart"
    else:
        readiness = "PARTIAL"
        recommendation = f"Fix {len(failed_steps)} issues before restart: {', '.join(failed_steps)}"

    output = {
        "readiness": readiness,
        "failed_steps": failed_steps,
        "details": details,
        "recommendation": recommendation,
        "cause": cause,
        "timestamp": datetime.now().isoformat(),
    }

    # Print human-readable to stderr first
    print("=== Restart Readiness Check ===", file=sys.stderr)
    print(f"Timestamp: {output['timestamp']}", file=sys.stderr)
    print(f"Readiness: {readiness}", file=sys.stderr)
    for step, data in details.items():
        status = "✓" if data["passed"] else "✗"
        print(f"  {status} {step}: {data['message']}", file=sys.stderr)
    print(f"Recommendation: {recommendation}\n", file=sys.stderr)

    # Print JSON to stdout
    print(json.dumps(output, indent=2))

    sys.exit(0 if readiness == "READY" else 1)


if __name__ == "__main__":
    main()
