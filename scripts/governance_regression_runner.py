#!/usr/bin/env python3
"""Governance Regression Runner — 6h automated livefire.

Runs commission + omission unification livefire tests, emits CIEU events,
writes result JSON, and triggers P0 alarm on failure.

Board 2026-04-22 directive: G2 long-term drift prevention.
CZL-CEO-RULES-REGISTRY-V3-RYAN

Usage:
    python3 scripts/governance_regression_runner.py
"""
from __future__ import annotations

import json
import os
import sqlite3
import subprocess
import sys
import time
import uuid
from datetime import datetime, timezone
from pathlib import Path

WORKSPACE = Path("/Users/haotianliu/.openclaw/workspace/ystar-company")
CIEU_DB = WORKSPACE / ".ystar_cieu.db"
WARNING_QUEUE = WORKSPACE / ".ystar_warning_queue.json"
REPORTS_DIR = WORKSPACE / "reports" / "governance"
COMMISSION_SCRIPT = WORKSPACE / "scripts" / "board_shell_commission_unification.py"
OMISSION_SCRIPT = WORKSPACE / "scripts" / "board_shell_omission_unification.py"

# Use the same python that the existing plists use
PYTHON = "/opt/homebrew/bin/python3.11"
if not os.path.exists(PYTHON):
    PYTHON = sys.executable  # fallback


def emit_cieu(event_type: str, decision: str, passed: int, details: str) -> str:
    """Emit a CIEU event to the database. Returns event_id."""
    event_id = str(uuid.uuid4())
    now = time.time()
    seq = int(now * 1_000_000)
    session_id = os.environ.get("YSTAR_SESSION_ID", "regression-cron")
    agent_id = "eng-platform"

    try:
        conn = sqlite3.connect(str(CIEU_DB), timeout=10)
        conn.execute(
            """INSERT INTO cieu_events
               (event_id, seq_global, created_at, session_id, agent_id,
                event_type, decision, passed, drift_details, task_description)
               VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
            (event_id, seq, now, session_id, agent_id,
             event_type, decision, passed, details,
             "6h governance regression cron"),
        )
        conn.commit()
        conn.close()
    except Exception as e:
        print(f"  [WARN] CIEU emit failed: {e}", file=sys.stderr)
        return event_id
    return event_id


def emit_p0_alarm(failure_details: str):
    """Write a P0 alarm to .ystar_warning_queue.json."""
    alarm = {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "severity": "P0",
        "source": "governance_regression_runner",
        "agent": "eng-platform",
        "message": f"GOVERNANCE REGRESSION FAILURE: {failure_details}",
        "action_required": "Board review — governance livefire regression failed",
    }
    try:
        queue = []
        if WARNING_QUEUE.exists():
            try:
                queue = json.loads(WARNING_QUEUE.read_text())
                if not isinstance(queue, list):
                    queue = []
            except (json.JSONDecodeError, Exception):
                queue = []
        queue.append(alarm)
        WARNING_QUEUE.write_text(json.dumps(queue, indent=2, ensure_ascii=False))
        print(f"  [P0] Alarm written to {WARNING_QUEUE}")
    except Exception as e:
        print(f"  [WARN] Could not write P0 alarm: {e}", file=sys.stderr)


def run_commission() -> dict:
    """Run commission unification livefire, return result dict."""
    if not COMMISSION_SCRIPT.exists():
        return {
            "status": "SKIP",
            "detail": f"script not found: {COMMISSION_SCRIPT}",
            "total": 0, "pass": 0, "fail": 0, "skipped": True,
        }
    try:
        r = subprocess.run(
            [PYTHON, str(COMMISSION_SCRIPT)],
            capture_output=True, text=True, timeout=60,
            cwd=str(WORKSPACE),
            env={**os.environ, "PYTHONPATH": str(WORKSPACE.parent / "Y-star-gov")},
        )
        output = r.stdout + r.stderr
        # Parse PASS/FAIL counts from output
        pass_count = output.count("[PASS]")
        fail_count = output.count("[FAIL]")
        total = pass_count + fail_count
        overall = "PASS" if r.returncode == 0 and fail_count == 0 else "FAIL"
        return {
            "status": overall,
            "detail": output[-500:] if len(output) > 500 else output,
            "total": total, "pass": pass_count, "fail": fail_count,
            "skipped": False, "exit_code": r.returncode,
        }
    except subprocess.TimeoutExpired:
        return {
            "status": "FAIL", "detail": "timeout after 60s",
            "total": 0, "pass": 0, "fail": 0, "skipped": False,
        }
    except Exception as e:
        return {
            "status": "FAIL", "detail": f"exception: {type(e).__name__}: {e}",
            "total": 0, "pass": 0, "fail": 0, "skipped": False,
        }


def run_omission() -> dict:
    """Run omission unification livefire if available."""
    if not OMISSION_SCRIPT.exists():
        print("  [SKIP] omission_unification not yet available")
        return {
            "status": "SKIP",
            "detail": "board_shell_omission_unification.py not yet available",
            "total": 0, "pass": 0, "fail": 0, "skipped": True,
        }
    try:
        r = subprocess.run(
            [PYTHON, str(OMISSION_SCRIPT)],
            capture_output=True, text=True, timeout=60,
            cwd=str(WORKSPACE),
            env={**os.environ, "PYTHONPATH": str(WORKSPACE.parent / "Y-star-gov")},
        )
        output = r.stdout + r.stderr
        pass_count = output.count("[PASS]")
        fail_count = output.count("[FAIL]")
        total = pass_count + fail_count
        overall = "PASS" if r.returncode == 0 and fail_count == 0 else "FAIL"
        return {
            "status": overall,
            "detail": output[-500:] if len(output) > 500 else output,
            "total": total, "pass": pass_count, "fail": fail_count,
            "skipped": False, "exit_code": r.returncode,
        }
    except subprocess.TimeoutExpired:
        return {
            "status": "FAIL", "detail": "timeout after 60s",
            "total": 0, "pass": 0, "fail": 0, "skipped": False,
        }
    except Exception as e:
        return {
            "status": "FAIL", "detail": f"exception: {type(e).__name__}: {e}",
            "total": 0, "pass": 0, "fail": 0, "skipped": False,
        }


def write_report(commission_result: dict, omission_result: dict, overall: str, event_id: str) -> Path:
    """Write JSON report to reports/governance/."""
    REPORTS_DIR.mkdir(parents=True, exist_ok=True)
    ts = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    report = {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "commission_result": {
            "total": commission_result["total"],
            "pass": commission_result["pass"],
            "fail": commission_result["fail"],
            "skipped": commission_result.get("skipped", False),
        },
        "omission_result": {
            "total": omission_result["total"],
            "pass": omission_result["pass"],
            "fail": omission_result["fail"],
            "skipped": omission_result.get("skipped", False),
        },
        "overall": overall,
        "cieu_event_id": event_id,
    }
    path = REPORTS_DIR / f"regression_{ts}.json"
    path.write_text(json.dumps(report, indent=2, ensure_ascii=False))
    return path


def main() -> int:
    print("=" * 60)
    print("  Governance Regression Runner")
    print(f"  Time: {datetime.now(timezone.utc).isoformat()}")
    print("=" * 60)

    # Run commission
    print("\n--- Commission Unification Livefire ---")
    commission_result = run_commission()
    print(f"  Result: {commission_result['status']} "
          f"(pass={commission_result['pass']}, fail={commission_result['fail']})")
    if commission_result.get("detail"):
        for line in commission_result["detail"].strip().split("\n")[-6:]:
            print(f"    {line}")

    # Run omission
    print("\n--- Omission Unification Livefire ---")
    omission_result = run_omission()
    if not omission_result.get("skipped"):
        print(f"  Result: {omission_result['status']} "
              f"(pass={omission_result['pass']}, fail={omission_result['fail']})")

    # Determine overall
    failures = []
    if commission_result["status"] == "FAIL":
        failures.append("commission")
    if omission_result["status"] == "FAIL":
        failures.append("omission")
    overall = "FAIL" if failures else "PASS"

    # Emit CIEU
    if overall == "PASS":
        event_id = emit_cieu(
            "GOVERNANCE_REGRESSION_PASS", "allow", 1,
            f"commission={commission_result['status']}, omission={omission_result['status']}",
        )
    else:
        event_id = emit_cieu(
            "GOVERNANCE_REGRESSION_FAILURE", "deny", 0,
            f"failures: {', '.join(failures)}; "
            f"commission={commission_result['status']}, omission={omission_result['status']}",
        )
        emit_p0_alarm(f"Failed components: {', '.join(failures)}")

    # Write report
    report_path = write_report(commission_result, omission_result, overall, event_id)

    print(f"\n{'=' * 60}")
    print(f"  OVERALL: {overall}")
    print(f"  CIEU event: {event_id}")
    print(f"  Report: {report_path}")
    print(f"{'=' * 60}")

    return 0 if overall == "PASS" else 1


if __name__ == "__main__":
    sys.exit(main())
