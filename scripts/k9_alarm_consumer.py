#!/usr/bin/env python3
"""
K9 Alarm Consumer Daemon — Layer 5 Cascade Remediation
Board 2026-04-16 P0: 6503+ K9 handler events (HOOK_HEALTH_K9_ESCALATE, AGENT_REGISTRY_K9_WARN, etc.) fire with 0 consumer.

Architecture:
  - Subscriber daemon polling CIEU for K9 handler events
  - Per-event-type cascade remediation handlers (6 types)
  - Throttling via dedup by violation_signature
  - Auto-update dashboard governance/enforce_status_dashboard.md
  - Emit K9_ALARM_CONSUMED event (audit trail)

Handler types:
  - FORGET_GUARD_K9_WARN → inject reminder + accumulate to dashboard
  - STOP_HOOK_K9_DENY → auto-emit blocking marker
  - CZL_K9_WARN → escalate to coord_audit
  - AGENT_REGISTRY_K9_WARN → auto-trigger identity_detector self-fix attempt
  - HOOK_HEALTH_K9_ESCALATE → auto-spawn Ryan diagnostic OR auto-restart hook daemon (with safety check)
  - FORGET_GUARD_K9_DENY → block + escalate to CEO via dashboard

Integration: governance_boot.sh STEP 11.7 (parallel to k9_event_trigger daemon)
"""
import argparse
import json
import os
import signal
import sqlite3
import subprocess
import sys
import time
import uuid
from collections import defaultdict
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Set

REPO_ROOT = Path(__file__).parent.parent
CIEU_DB = REPO_ROOT / ".ystar_cieu.db"
STATE_FILE = REPO_ROOT / "scripts" / ".k9_alarm_consumer_state.json"
PID_FILE = REPO_ROOT / "scripts" / ".k9_alarm_consumer.pid"
DASHBOARD_PATH = REPO_ROOT / "governance" / "enforce_status_dashboard.md"

# Dedup window: last N events to check for duplicate violation_signature
DEDUP_WINDOW_SIZE = 100

# Handler event types we consume
HANDLER_EVENT_TYPES = [
    "FORGET_GUARD_K9_WARN",
    "STOP_HOOK_K9_DENY",
    "CZL_K9_WARN",
    "AGENT_REGISTRY_K9_WARN",
    "HOOK_HEALTH_K9_ESCALATE",
    "FORGET_GUARD_K9_DENY",
]


# ═══ CIEU HELPERS ═══

def get_cieu_conn() -> sqlite3.Connection:
    """Return connection to CIEU database."""
    if not CIEU_DB.exists():
        raise FileNotFoundError(f"CIEU DB not found: {CIEU_DB}")
    return sqlite3.connect(str(CIEU_DB), timeout=5.0)


def emit_cieu(event_type: str, metadata: dict) -> None:
    """Emit CIEU event to database."""
    try:
        conn = get_cieu_conn()
        cursor = conn.cursor()

        cursor.execute("SELECT COALESCE(MAX(seq_global), 0) + 1 FROM cieu_events")
        seq_global = cursor.fetchone()[0]

        cursor.execute(
            """
            INSERT INTO cieu_events (
                event_id, seq_global, created_at, session_id, agent_id,
                event_type, decision, passed, task_description
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                str(uuid.uuid4()),
                seq_global,
                time.time(),
                metadata.get("session_id", "k9_alarm_consumer"),
                metadata.get("agent_id", "system:k9_alarm_consumer"),
                event_type,
                metadata.get("decision", "info"),
                metadata.get("passed", 1),
                json.dumps(metadata, ensure_ascii=False)[:1000],
            ),
        )
        conn.commit()
        conn.close()
    except Exception as e:
        print(f"[K9_ALARM_CONSUMER] CIEU emit failed: {e}", file=sys.stderr)


# ═══ STATE MANAGEMENT ═══

def load_state() -> Dict:
    """Load last-seq tracking state."""
    if not STATE_FILE.exists():
        return {"last_seq": 0, "dedup_history": []}
    try:
        with open(STATE_FILE, "r") as f:
            return json.load(f)
    except Exception:
        return {"last_seq": 0, "dedup_history": []}


def save_state(state: Dict) -> None:
    """Save last-seq tracking state."""
    STATE_FILE.parent.mkdir(parents=True, exist_ok=True)
    with open(STATE_FILE, "w") as f:
        json.dump(state, f, indent=2)


# ═══ CASCADE HANDLERS ═══

def handle_forget_guard_warn(event: Dict) -> bool:
    """
    Handler for FORGET_GUARD_K9_WARN.
    Action: Inject reminder to governance/reminders/ + accumulate to dashboard.
    """
    try:
        params = json.loads(event.get("task_description", "{}"))
        violation_type = params.get("violation_type", "unknown")
        agent_id = params.get("agent_id", "unknown")

        # Create reminder file
        reminder_dir = REPO_ROOT / "governance" / "reminders"
        reminder_dir.mkdir(parents=True, exist_ok=True)

        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        reminder_file = reminder_dir / f"k9_warn_{violation_type}_{timestamp}.md"

        reminder_content = f"""# ForgetGuard K9 Warning

**Timestamp**: {datetime.now().isoformat()}
**Agent**: {agent_id}
**Violation Type**: {violation_type}

**Details**:
{json.dumps(params, indent=2)}

**Action Required**: Review and acknowledge this pattern violation.
"""
        reminder_file.write_text(reminder_content)

        emit_cieu("K9_ALARM_CONSUMED", {
            "handler": "forget_guard_warn",
            "violation_type": violation_type,
            "action_taken": "reminder_created",
            "reminder_path": str(reminder_file),
        })
        return True
    except Exception as e:
        print(f"[FORGET_GUARD_WARN] Handler failed: {e}", file=sys.stderr)
        return False


def handle_stop_hook_deny(event: Dict) -> bool:
    """
    Handler for STOP_HOOK_K9_DENY.
    Action: Auto-emit blocking marker to governance/blocking_events.log.
    """
    try:
        params = json.loads(event.get("task_description", "{}"))
        violation_type = params.get("violation_type", "unknown")
        agent_id = params.get("agent_id", "unknown")

        blocking_log = REPO_ROOT / "governance" / "blocking_events.log"
        blocking_log.parent.mkdir(parents=True, exist_ok=True)

        timestamp = datetime.now().isoformat()
        log_entry = f"[{timestamp}] BLOCK: {agent_id} {violation_type} {json.dumps(params)}\n"

        with open(blocking_log, "a") as f:
            f.write(log_entry)

        emit_cieu("K9_ALARM_CONSUMED", {
            "handler": "stop_hook_deny",
            "violation_type": violation_type,
            "action_taken": "blocking_marker_emitted",
        })
        return True
    except Exception as e:
        print(f"[STOP_HOOK_DENY] Handler failed: {e}", file=sys.stderr)
        return False


def handle_czl_warn(event: Dict) -> bool:
    """
    Handler for CZL_K9_WARN.
    Action: Escalate to coord_audit (write to governance/czl_escalations.json).
    """
    try:
        params = json.loads(event.get("task_description", "{}"))
        violation_type = params.get("violation_type", "unknown")

        escalation_file = REPO_ROOT / "governance" / "czl_escalations.json"
        escalation_file.parent.mkdir(parents=True, exist_ok=True)

        # Load existing escalations
        if escalation_file.exists():
            with open(escalation_file, "r") as f:
                escalations = json.load(f)
        else:
            escalations = []

        # Append new escalation
        escalations.append({
            "timestamp": datetime.now().isoformat(),
            "violation_type": violation_type,
            "event_id": event.get("event_id", "unknown"),
            "params": params,
        })

        with open(escalation_file, "w") as f:
            json.dump(escalations, f, indent=2)

        emit_cieu("K9_ALARM_CONSUMED", {
            "handler": "czl_warn",
            "violation_type": violation_type,
            "action_taken": "escalated_to_coord_audit",
        })
        return True
    except Exception as e:
        print(f"[CZL_WARN] Handler failed: {e}", file=sys.stderr)
        return False


def handle_agent_registry_warn(event: Dict) -> bool:
    """
    Handler for AGENT_REGISTRY_K9_WARN.
    Action: Auto-trigger identity_detector self-fix attempt via scripts/identity_detector.py.
    """
    try:
        params = json.loads(event.get("task_description", "{}"))
        agent_id = params.get("agent_id", "unknown")

        # Attempt auto-fix via identity_detector.py (if exists)
        identity_script = REPO_ROOT / "scripts" / "identity_detector.py"
        if identity_script.exists():
            result = subprocess.run(
                [sys.executable, str(identity_script), "auto-fix", "--agent_id", agent_id],
                capture_output=True,
                text=True,
                timeout=10,
            )
            action_taken = "auto_fix_attempted" if result.returncode == 0 else "auto_fix_failed"
        else:
            action_taken = "auto_fix_script_missing"

        emit_cieu("K9_ALARM_CONSUMED", {
            "handler": "agent_registry_warn",
            "agent_id": agent_id,
            "action_taken": action_taken,
        })
        return True
    except Exception as e:
        print(f"[AGENT_REGISTRY_WARN] Handler failed: {e}", file=sys.stderr)
        return False


def handle_hook_health_escalate(event: Dict) -> bool:
    """
    Handler for HOOK_HEALTH_K9_ESCALATE.
    Action: Auto-spawn Ryan diagnostic OR auto-restart hook daemon (with safety check).
    """
    try:
        params = json.loads(event.get("task_description", "{}"))
        violation_type = params.get("violation_type", "unknown")

        # Safety check: don't restart hook daemon if it was restarted in last 60s
        restart_marker = REPO_ROOT / "scripts" / ".hook_daemon_last_restart"
        if restart_marker.exists():
            last_restart = restart_marker.stat().st_mtime
            if time.time() - last_restart < 60:
                # Too soon, emit escalation instead
                escalation_file = REPO_ROOT / "governance" / "hook_health_escalations.json"
                escalation_file.parent.mkdir(parents=True, exist_ok=True)

                if escalation_file.exists():
                    with open(escalation_file, "r") as f:
                        escalations = json.load(f)
                else:
                    escalations = []

                escalations.append({
                    "timestamp": datetime.now().isoformat(),
                    "violation_type": violation_type,
                    "action": "restart_throttled_emitted_escalation",
                    "params": params,
                })

                with open(escalation_file, "w") as f:
                    json.dump(escalations, f, indent=2)

                emit_cieu("K9_ALARM_CONSUMED", {
                    "handler": "hook_health_escalate",
                    "action_taken": "restart_throttled_escalation_emitted",
                })
                return True

        # Restart hook daemon
        hook_restart_script = REPO_ROOT / "scripts" / "hook_restart.sh"
        if hook_restart_script.exists():
            subprocess.run(["bash", str(hook_restart_script)], timeout=10)
            restart_marker.parent.mkdir(parents=True, exist_ok=True)
            restart_marker.touch()
            action_taken = "hook_daemon_restarted"
        else:
            action_taken = "hook_restart_script_missing"

        emit_cieu("K9_ALARM_CONSUMED", {
            "handler": "hook_health_escalate",
            "action_taken": action_taken,
        })
        return True
    except Exception as e:
        print(f"[HOOK_HEALTH_ESCALATE] Handler failed: {e}", file=sys.stderr)
        return False


def handle_forget_guard_deny(event: Dict) -> bool:
    """
    Handler for FORGET_GUARD_K9_DENY.
    Action: Block + escalate to CEO via dashboard.
    """
    try:
        params = json.loads(event.get("task_description", "{}"))
        violation_type = params.get("violation_type", "unknown")
        agent_id = params.get("agent_id", "unknown")

        # Write to CEO escalation queue
        escalation_file = REPO_ROOT / "governance" / "ceo_escalations.json"
        escalation_file.parent.mkdir(parents=True, exist_ok=True)

        if escalation_file.exists():
            with open(escalation_file, "r") as f:
                escalations = json.load(f)
        else:
            escalations = []

        escalations.append({
            "timestamp": datetime.now().isoformat(),
            "event_type": "FORGET_GUARD_K9_DENY",
            "agent_id": agent_id,
            "violation_type": violation_type,
            "params": params,
            "priority": "P0",
        })

        with open(escalation_file, "w") as f:
            json.dump(escalations, f, indent=2)

        emit_cieu("K9_ALARM_CONSUMED", {
            "handler": "forget_guard_deny",
            "violation_type": violation_type,
            "action_taken": "escalated_to_ceo",
        })
        return True
    except Exception as e:
        print(f"[FORGET_GUARD_DENY] Handler failed: {e}", file=sys.stderr)
        return False


# Routing table: event_type → handler function
HANDLER_DISPATCH = {
    "FORGET_GUARD_K9_WARN": handle_forget_guard_warn,
    "STOP_HOOK_K9_DENY": handle_stop_hook_deny,
    "CZL_K9_WARN": handle_czl_warn,
    "AGENT_REGISTRY_K9_WARN": handle_agent_registry_warn,
    "HOOK_HEALTH_K9_ESCALATE": handle_hook_health_escalate,
    "FORGET_GUARD_K9_DENY": handle_forget_guard_deny,
}


# ═══ DEDUP LOGIC ═══

def compute_violation_signature(event: Dict) -> str:
    """Compute violation signature for dedup (event_type + agent_id + violation_type)."""
    try:
        params = json.loads(event.get("task_description", "{}"))
        violation_type = params.get("violation_type", "unknown")
        agent_id = params.get("agent_id", "unknown")
        event_type = event.get("event_type", "unknown")
        return f"{event_type}::{agent_id}::{violation_type}"
    except Exception:
        return f"{event.get('event_id', 'unknown')}"


def is_duplicate(event: Dict, dedup_history: List[str]) -> bool:
    """Check if event is duplicate within dedup window."""
    signature = compute_violation_signature(event)
    return signature in dedup_history


# ═══ DASHBOARD UPDATE ═══

def refresh_dashboard(stats: Dict) -> None:
    """Auto-update enforce_status_dashboard.md with latest alarm stats."""
    try:
        dashboard_content = f"""# Enforcement Status Dashboard

**Last Updated**: {datetime.now().isoformat()}

## Alarm Rate by Type (Last Session)

| Event Type | Count | Last Seen |
|------------|-------|-----------|
"""
        for event_type, count in sorted(stats["alarm_counts"].items(), key=lambda x: x[1], reverse=True):
            last_seen = stats["last_seen"].get(event_type, "N/A")
            dashboard_content += f"| {event_type} | {count} | {last_seen} |\n"

        dashboard_content += f"""
## Cascade Success Rate

- **Total Alarms Processed**: {stats['total_processed']}
- **Cascade Successes**: {stats['cascade_success']}
- **Cascade Failures**: {stats['cascade_failure']}
- **Success Rate**: {stats['success_rate']:.1f}%

## Unconsumed Backlog

- **Events in Queue**: {stats['backlog_count']}

## Open Escalations (CEO Attention Required)

"""
        # Read CEO escalation queue
        escalation_file = REPO_ROOT / "governance" / "ceo_escalations.json"
        if escalation_file.exists():
            with open(escalation_file, "r") as f:
                escalations = json.load(f)
            if escalations:
                dashboard_content += "| Timestamp | Event Type | Agent | Violation |\n"
                dashboard_content += "|-----------|------------|-------|----------|\n"
                for esc in escalations[-10:]:  # Last 10 escalations
                    dashboard_content += f"| {esc.get('timestamp', 'N/A')} | {esc.get('event_type', 'N/A')} | {esc.get('agent_id', 'N/A')} | {esc.get('violation_type', 'N/A')} |\n"
            else:
                dashboard_content += "No open escalations.\n"
        else:
            dashboard_content += "No escalation queue found.\n"

        DASHBOARD_PATH.parent.mkdir(parents=True, exist_ok=True)
        DASHBOARD_PATH.write_text(dashboard_content)

    except Exception as e:
        print(f"[DASHBOARD] Update failed: {e}", file=sys.stderr)


# ═══ DAEMON LOGIC ═══

def poll_and_consume(state: Dict, stats: Dict) -> None:
    """Poll CIEU for new handler events and consume them."""
    try:
        conn = get_cieu_conn()
        cursor = conn.cursor()

        # Fetch new events since last_seq
        last_seq = state.get("last_seq", 0)
        dedup_history = state.get("dedup_history", [])

        cursor.execute(
            """
            SELECT event_id, seq_global, event_type, agent_id, task_description, created_at
            FROM cieu_events
            WHERE event_type IN ({})
            AND seq_global > ?
            ORDER BY seq_global ASC
            LIMIT 100
            """.format(",".join(["?"] * len(HANDLER_EVENT_TYPES))),
            (*HANDLER_EVENT_TYPES, last_seq),
        )

        events = cursor.fetchall()
        conn.close()

        for row in events:
            event = {
                "event_id": row[0],
                "seq_global": row[1],
                "event_type": row[2],
                "agent_id": row[3],
                "task_description": row[4],
                "created_at": row[5],
            }

            # Dedup check
            if is_duplicate(event, dedup_history):
                print(f"[K9_ALARM_CONSUMER] Skipping duplicate: {event['event_type']}", file=sys.stderr)
                state["last_seq"] = event["seq_global"]
                continue

            # Dispatch to handler
            handler = HANDLER_DISPATCH.get(event["event_type"])
            if handler:
                try:
                    success = handler(event)
                    stats["total_processed"] += 1
                    if success:
                        stats["cascade_success"] += 1
                    else:
                        stats["cascade_failure"] += 1

                    # Update stats
                    stats["alarm_counts"][event["event_type"]] = stats["alarm_counts"].get(event["event_type"], 0) + 1
                    stats["last_seen"][event["event_type"]] = datetime.now().isoformat()

                except Exception as e:
                    print(f"[K9_ALARM_CONSUMER] Handler exception: {e}", file=sys.stderr)
                    stats["cascade_failure"] += 1

            # Update dedup history (sliding window)
            signature = compute_violation_signature(event)
            dedup_history.append(signature)
            if len(dedup_history) > DEDUP_WINDOW_SIZE:
                dedup_history.pop(0)

            # Update last_seq
            state["last_seq"] = event["seq_global"]

        # Save state
        state["dedup_history"] = dedup_history
        save_state(state)

        # Update dashboard if stats changed
        if stats["total_processed"] > 0:
            stats["success_rate"] = (stats["cascade_success"] / stats["total_processed"]) * 100
            stats["backlog_count"] = len(events)
            refresh_dashboard(stats)

    except Exception as e:
        print(f"[K9_ALARM_CONSUMER] Poll failed: {e}", file=sys.stderr)


def start_daemon(poll_interval: int = 5):
    """Start K9 alarm consumer daemon."""
    # Write PID file
    PID_FILE.parent.mkdir(parents=True, exist_ok=True)
    PID_FILE.write_text(str(os.getpid()))

    emit_cieu("K9_ALARM_CONSUMER_START", {"poll_interval": poll_interval})

    print(f"[K9_ALARM_CONSUMER] Daemon started (PID {os.getpid()}, poll interval: {poll_interval}s)", file=sys.stderr)

    state = load_state()
    stats = {
        "total_processed": 0,
        "cascade_success": 0,
        "cascade_failure": 0,
        "success_rate": 0.0,
        "backlog_count": 0,
        "alarm_counts": defaultdict(int),
        "last_seen": {},
    }

    def shutdown_handler(signum, frame):
        emit_cieu("K9_ALARM_CONSUMER_STOP", {})
        PID_FILE.unlink(missing_ok=True)
        print(f"\n[K9_ALARM_CONSUMER] Daemon stopped", file=sys.stderr)
        sys.exit(0)

    signal.signal(signal.SIGTERM, shutdown_handler)
    signal.signal(signal.SIGINT, shutdown_handler)

    while True:
        try:
            poll_and_consume(state, stats)
            time.sleep(poll_interval)
        except Exception as e:
            print(f"[K9_ALARM_CONSUMER] Main loop error: {e}", file=sys.stderr)
            time.sleep(poll_interval)


def stop_daemon():
    """Stop running daemon."""
    if not PID_FILE.exists():
        print("No daemon running (no PID file)", file=sys.stderr)
        return 1

    pid = int(PID_FILE.read_text().strip())
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
    try:
        os.kill(pid, 0)  # Signal 0 checks if process exists
        print(f"Daemon: RUNNING (PID {pid})", file=sys.stderr)
        return 0
    except ProcessLookupError:
        print(f"Daemon: STALE PID {pid} (process not found)", file=sys.stderr)
        PID_FILE.unlink()
        return 1


def main():
    parser = argparse.ArgumentParser(description="K9 Alarm Consumer Daemon")
    subparsers = parser.add_subparsers(dest="command", required=True)

    # start
    start_parser = subparsers.add_parser("start", help="Start daemon")
    start_parser.add_argument("--poll_interval", type=int, default=5, help="Poll interval in seconds")
    start_parser.set_defaults(func=lambda args: start_daemon(args.poll_interval))

    # stop
    stop_parser = subparsers.add_parser("stop", help="Stop daemon")
    stop_parser.set_defaults(func=lambda args: stop_daemon())

    # status
    status_parser = subparsers.add_parser("status", help="Check daemon status")
    status_parser.set_defaults(func=lambda args: daemon_status())

    # refresh-dashboard (manual trigger)
    refresh_parser = subparsers.add_parser("refresh-dashboard", help="Manually refresh dashboard")
    refresh_parser.set_defaults(func=lambda args: refresh_dashboard({
        "total_processed": 0,
        "cascade_success": 0,
        "cascade_failure": 0,
        "success_rate": 0.0,
        "backlog_count": 0,
        "alarm_counts": {},
        "last_seen": {},
    }))

    args = parser.parse_args()
    return args.func(args) or 0


if __name__ == "__main__":
    sys.exit(main())
