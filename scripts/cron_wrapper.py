#!/usr/bin/env python3
"""
Cron Wrapper — runs a subprocess command and emits CRON_TICK + CRON_RESULT CIEU events.
Closes CZL-ARCH-7 gap: cron_ticks_7d was 0.

Usage: python3 cron_wrapper.py <cmd> [args...]
"""
import json
import os
import subprocess
import sys
import time

sys.path.insert(0, os.path.dirname(__file__))
from _cieu_helpers import emit_cieu


def run_with_cieu(cmd: list[str]) -> int:
    """Execute cmd, emit CRON_TICK before and CRON_RESULT after. Returns exit code."""
    cmd_str = " ".join(cmd)

    emit_cieu(
        event_type="CRON_TICK",
        decision="info",
        passed=1,
        task_description=f"Cron start: {cmd_str}",
        params_json=json.dumps({"cmd": cmd_str, "pid": os.getpid()}),
    )

    t0 = time.time()
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=300)
        exit_code = result.returncode
        ok = exit_code == 0
    except Exception:
        exit_code = 1
        ok = False
        result = None

    elapsed = round(time.time() - t0, 3)

    emit_cieu(
        event_type="CRON_RESULT",
        decision="info" if ok else "warn",
        passed=1 if ok else 0,
        task_description=f"Cron done: {cmd_str} rc={exit_code} {elapsed}s",
        params_json=json.dumps({
            "cmd": cmd_str,
            "exit_code": exit_code,
            "elapsed_s": elapsed,
            "stdout_tail": (result.stdout[-200:] if result and result.stdout else ""),
            "stderr_tail": (result.stderr[-200:] if result and result.stderr else ""),
        }),
    )

    return exit_code


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: cron_wrapper.py <cmd> [args...]", file=sys.stderr)
        sys.exit(1)
    sys.exit(run_with_cieu(sys.argv[1:]))
