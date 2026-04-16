#!/usr/bin/env python3
"""Session Health Watchdog — Event-driven health monitoring (Iron Rule 1 compliant)

Zero LLM, zero uncertainty. Pure thresholds.

Monitors:
1. JSONL file size (context proxy)
2. Session call count
3. Session runtime
4. Hook deny rate (recent 50 calls)
5. Subagent output accumulation
6. CIEU drift events (recent 10)

Triggers graceful save when ANY yellow-line threshold reached.

Board override: `touch /tmp/ystar_no_auto_restart`

Usage:
    python3 scripts/session_health_watchdog.py [--once]

    --once: Check once and exit (for testing)
    default: Event-driven loop (monitors JSONL file size changes)
"""

import sys
import time
import json
import sqlite3
from pathlib import Path
from typing import Dict, Optional, Tuple
import os
import glob
sys.path.insert(0, str(Path(__file__).parent))
from _cieu_helpers import _get_current_agent


# === Thresholds (Board-approved 2026-04-12) ===
THRESHOLD_JSONL_MB = 3.0  # ~50% context estimate
THRESHOLD_CALL_COUNT = 500
THRESHOLD_RUNTIME_HOURS = 6.0  # Hard constraint
THRESHOLD_DENY_RATE = 0.30  # 30% deny rate in recent 50
THRESHOLD_SUBAGENT_KB = 500
THRESHOLD_DRIFT_COUNT = 3  # out of recent 10 CIEU events


class HealthMetrics:
    """Health metrics snapshot (all deterministic)"""

    def __init__(self):
        self.jsonl_size_mb: float = 0.0
        self.call_count: int = 0
        self.runtime_hours: float = 0.0
        self.deny_rate: float = 0.0
        self.subagent_kb: float = 0.0
        self.drift_count: int = 0

        self.thresholds_breached: Dict[str, bool] = {}
        self.yellow_line_triggered: bool = False
        self.reason: str = ""


def find_current_jsonl(company_root: Path) -> Optional[Path]:
    """Find current session JSONL file (most recently modified)"""
    jsonl_pattern = str(Path.home() / ".claude/projects/-Users-haotianliu--openclaw-workspace-ystar-company/*.jsonl")
    files = glob.glob(jsonl_pattern)

    if not files:
        return None

    # Return most recently modified
    files.sort(key=lambda f: os.path.getmtime(f), reverse=True)
    return Path(files[0])


def get_session_boot_time(company_root: Path) -> float:
    """Get session boot timestamp"""
    boot_marker = company_root / "scripts/.session_booted"
    if not boot_marker.exists():
        return time.time()  # Assume just started
    return boot_marker.stat().st_mtime


def get_call_count(company_root: Path) -> int:
    """Get session call count"""
    count_file = company_root / "scripts/.session_call_count"
    if not count_file.exists():
        return 0
    try:
        return int(count_file.read_text().strip())
    except (ValueError, FileNotFoundError):
        return 0


def get_hook_deny_rate(company_root: Path) -> float:
    """Get hook deny rate from recent 50 calls"""
    cieu_db = company_root / ".ystar_cieu.db"
    if not cieu_db.exists():
        return 0.0

    try:
        conn = sqlite3.connect(str(cieu_db))
        cursor = conn.execute("""
            SELECT decision FROM cieu_events
            WHERE event_type LIKE 'HOOK_%'
            ORDER BY created_at DESC
            LIMIT 50
        """)

        decisions = [row[0] for row in cursor.fetchall()]
        conn.close()

        if not decisions:
            return 0.0

        deny_count = sum(1 for d in decisions if d and 'deny' in d.lower())
        return deny_count / len(decisions)
    except Exception:
        return 0.0


def get_drift_count(company_root: Path) -> int:
    """Get drift detection count from recent 10 CIEU events"""
    cieu_db = company_root / ".ystar_cieu.db"
    if not cieu_db.exists():
        return 0

    try:
        conn = sqlite3.connect(str(cieu_db))
        cursor = conn.execute("""
            SELECT event_type, params_json FROM cieu_events
            ORDER BY created_at DESC
            LIMIT 10
        """)

        drift_count = 0
        for event_type, params_json in cursor.fetchall():
            if event_type and 'drift' in event_type.lower():
                drift_count += 1
            elif params_json:
                try:
                    params = json.loads(params_json)
                    if params.get('drift_detected') or params.get('health_degradation'):
                        drift_count += 1
                except json.JSONDecodeError:
                    pass

        conn.close()
        return drift_count
    except Exception:
        return 0


def get_subagent_output_size(company_root: Path) -> float:
    """Get cumulative subagent output size in KB"""
    # Check .claude/cache for subagent outputs
    cache_dir = Path.home() / ".claude/cache"
    if not cache_dir.exists():
        return 0.0

    total_bytes = 0

    # Count recent subagent outputs (modified since session boot)
    boot_time = get_session_boot_time(company_root)

    for file in cache_dir.rglob("*"):
        if file.is_file():
            try:
                if file.stat().st_mtime >= boot_time:
                    total_bytes += file.stat().st_size
            except OSError:
                pass

    return total_bytes / 1024.0  # Convert to KB


def collect_health_metrics(company_root: Path) -> HealthMetrics:
    """Collect all health metrics (deterministic, zero LLM)"""
    metrics = HealthMetrics()

    # 1. JSONL size
    jsonl_path = find_current_jsonl(company_root)
    if jsonl_path and jsonl_path.exists():
        metrics.jsonl_size_mb = jsonl_path.stat().st_size / (1024 * 1024)
        if metrics.jsonl_size_mb >= THRESHOLD_JSONL_MB:
            metrics.thresholds_breached['jsonl_size'] = True

    # 2. Call count
    metrics.call_count = get_call_count(company_root)
    if metrics.call_count >= THRESHOLD_CALL_COUNT:
        metrics.thresholds_breached['call_count'] = True

    # 3. Runtime
    boot_time = get_session_boot_time(company_root)
    metrics.runtime_hours = (time.time() - boot_time) / 3600.0
    if metrics.runtime_hours >= THRESHOLD_RUNTIME_HOURS:
        metrics.thresholds_breached['runtime'] = True

    # 4. Hook deny rate
    metrics.deny_rate = get_hook_deny_rate(company_root)
    if metrics.deny_rate >= THRESHOLD_DENY_RATE:
        metrics.thresholds_breached['deny_rate'] = True

    # 5. Subagent output
    metrics.subagent_kb = get_subagent_output_size(company_root)
    if metrics.subagent_kb >= THRESHOLD_SUBAGENT_KB:
        metrics.thresholds_breached['subagent_output'] = True

    # 6. Drift count
    metrics.drift_count = get_drift_count(company_root)
    if metrics.drift_count >= THRESHOLD_DRIFT_COUNT:
        metrics.thresholds_breached['drift'] = True

    # Yellow line triggered if ANY threshold breached
    metrics.yellow_line_triggered = len(metrics.thresholds_breached) > 0

    if metrics.yellow_line_triggered:
        reasons = [f"{k}={getattr(metrics, k.replace('_count', '_count').replace('_rate', '_rate')):.2f}"
                   for k in metrics.thresholds_breached.keys()]
        metrics.reason = f"YELLOW_LINE: {', '.join(reasons)}"

    return metrics


def write_trigger_signal(company_root: Path, metrics: HealthMetrics):
    """Write signal file to trigger graceful save"""
    signal_file = Path("/tmp/ystar_health_yellow")

    signal_data = {
        "triggered_at": time.time(),
        "metrics": {
            "jsonl_mb": metrics.jsonl_size_mb,
            "call_count": metrics.call_count,
            "runtime_hours": metrics.runtime_hours,
            "deny_rate": metrics.deny_rate,
            "subagent_kb": metrics.subagent_kb,
            "drift_count": metrics.drift_count,
        },
        "breached": list(metrics.thresholds_breached.keys()),
        "reason": metrics.reason
    }

    signal_file.write_text(json.dumps(signal_data, indent=2))
    print(f"[WATCHDOG] Yellow line triggered: {metrics.reason}")
    print(f"[WATCHDOG] Signal written to {signal_file}")


def emit_cieu_health_check(company_root: Path, metrics: HealthMetrics):
    """Emit CIEU event for health check (audit trail)"""
    cieu_db = company_root / ".ystar_cieu.db"
    if not cieu_db.exists():
        return

    try:
        emit_cieu(
            event_type="SESSION_HEALTH_CHECK",
            decision="info" if not metrics.yellow_line_triggered else "yellow_line",
            passed=1,
            task_description=metrics.reason if metrics.yellow_line_triggered else "Health OK",
            session_id="watchdog",
            params_json=json.dumps({
                "jsonl_mb": metrics.jsonl_size_mb,
                "call_count": metrics.call_count,
                "runtime_hours": metrics.runtime_hours,
                "deny_rate": metrics.deny_rate,
                "subagent_kb": metrics.subagent_kb,
                "drift_count": metrics.drift_count,
                "yellow_line": metrics.yellow_line_triggered
            })
        )
    except Exception as e:
        print(f"[WATCHDOG] Warning: CIEU emit failed: {e}", file=sys.stderr)


def check_board_override() -> bool:
    """Check if Board disabled auto-restart"""
    return Path("/tmp/ystar_no_auto_restart").exists()


def run_once(company_root: Path) -> Tuple[HealthMetrics, bool]:
    """Run single health check, return (metrics, triggered)"""

    if check_board_override():
        print("[WATCHDOG] Auto-restart disabled by Board (/tmp/ystar_no_auto_restart exists)")
        return HealthMetrics(), False

    metrics = collect_health_metrics(company_root)

    # Emit health check to CIEU
    emit_cieu_health_check(company_root, metrics)

    # Print status
    print(f"[WATCHDOG] Health check at {time.strftime('%H:%M:%S')}")
    print(f"  JSONL: {metrics.jsonl_size_mb:.2f} MB (threshold: {THRESHOLD_JSONL_MB})")
    print(f"  Calls: {metrics.call_count} (threshold: {THRESHOLD_CALL_COUNT})")
    print(f"  Runtime: {metrics.runtime_hours:.2f}h (threshold: {THRESHOLD_RUNTIME_HOURS})")
    print(f"  Deny rate: {metrics.deny_rate:.1%} (threshold: {THRESHOLD_DENY_RATE:.0%})")
    print(f"  Subagent: {metrics.subagent_kb:.1f} KB (threshold: {THRESHOLD_SUBAGENT_KB})")
    print(f"  Drift: {metrics.drift_count} (threshold: {THRESHOLD_DRIFT_COUNT})")

    if metrics.yellow_line_triggered:
        print(f"\n  ⚠️  YELLOW LINE TRIGGERED")
        print(f"  Breached: {list(metrics.thresholds_breached.keys())}")
        write_trigger_signal(company_root, metrics)
        return metrics, True
    else:
        print("  ✓ All metrics green")
        return metrics, False


def event_loop(company_root: Path):
    """Event-driven monitoring loop (watches JSONL file changes)"""
    print("[WATCHDOG] Starting event-driven health monitoring...")
    print(f"[WATCHDOG] Company root: {company_root}")
    print(f"[WATCHDOG] Board override: touch /tmp/ystar_no_auto_restart to disable")
    print("")

    last_check_time = time.time()
    last_jsonl_size = 0.0

    while True:
        # Check for Board override
        if check_board_override():
            print("[WATCHDOG] Auto-restart disabled by Board. Exiting.")
            break

        # Get current JSONL size
        jsonl_path = find_current_jsonl(company_root)
        current_size = 0.0
        if jsonl_path and jsonl_path.exists():
            current_size = jsonl_path.stat().st_size / (1024 * 1024)

        # Trigger check if:
        # - JSONL grew by 0.5 MB+ since last check
        # - OR 5 minutes elapsed (fallback)
        time_since_last = time.time() - last_check_time
        size_delta = current_size - last_jsonl_size

        should_check = (size_delta >= 0.5) or (time_since_last >= 300)

        if should_check:
            metrics, triggered = run_once(company_root)
            last_check_time = time.time()
            last_jsonl_size = current_size

            if triggered:
                print("[WATCHDOG] Yellow line triggered. Watchdog exiting (wrapper will handle restart).")
                break

        # Sleep briefly
        time.sleep(10)


def main():
    company_root = Path(__file__).parent.parent

    # Parse args
    once_mode = "--once" in sys.argv

    if once_mode:
        metrics, triggered = run_once(company_root)
        return 0 if not triggered else 1
    else:
        event_loop(company_root)
        return 0


if __name__ == "__main__":
    sys.exit(main())
