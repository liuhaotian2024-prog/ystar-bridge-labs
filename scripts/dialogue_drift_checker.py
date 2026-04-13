#!/usr/bin/env python3
"""
AMENDMENT-022: Dialogue Contract Drift Detector
Scans recent DIALOGUE_CONTRACT_DRAFT events vs whitelist, emits DIALOGUE_DRIFT warnings.

Designed to run as cron job every 5min or manually after each session.
"""
import sys
import json
import sqlite3
from datetime import datetime, timedelta
from pathlib import Path

WORKSPACE_ROOT = Path("/Users/haotianliu/.openclaw/workspace/ystar-company")
CIEU_DB = WORKSPACE_ROOT / ".ystar_cieu.db"
WHITELIST_DIR = WORKSPACE_ROOT / "governance/whitelist"
DRIFT_LOG = WORKSPACE_ROOT / "scripts/.logs/dialogue_drift.log"

# Whitelist corpus files (7-corpus system from AMENDMENT-019)
WHITELIST_FILES = [
    "agent_permissions.yaml",
    "banned_commands.yaml",
    "safe_paths.yaml",
    "api_endpoints.yaml",
    "time_constraints.yaml",
    "value_ranges.yaml",
    "obligations.yaml"
]


def load_whitelist():
    """Load all whitelist entries from 7-corpus files"""
    whitelist = {
        "deny": set(),
        "only_paths": set(),
        "deny_commands": set(),
        "only_domains": set(),
        "temporal": {},
        "value_range": {},
        "obligation_timing": {}
    }

    for filename in WHITELIST_FILES:
        filepath = WHITELIST_DIR / filename
        if not filepath.exists():
            continue

        try:
            import yaml
            with open(filepath) as f:
                data = yaml.safe_load(f)
                if not data:
                    continue

                # Extract relevant fields based on file content
                for key in ["deny", "only_paths", "deny_commands", "only_domains"]:
                    if key in data:
                        whitelist[key].update(data[key])

        except Exception as e:
            print(f"Warning: Failed to load {filename}: {e}", file=sys.stderr)

    return whitelist


def get_recent_dialogue_contracts(minutes=10):
    """Fetch DIALOGUE_CONTRACT_DRAFT events from last N minutes"""
    try:
        import time
        conn = sqlite3.connect(CIEU_DB)
        cursor = conn.cursor()

        cutoff = time.time() - (minutes * 60)
        cursor.execute("""
            SELECT rowid, created_at, task_description FROM cieu_events
            WHERE event_type = 'DIALOGUE_CONTRACT_DRAFT'
            AND created_at > ?
            ORDER BY rowid DESC
        """, (cutoff,))

        rows = cursor.fetchall()
        conn.close()

        results = []
        for event_id, created_at, task_desc_json in rows:
            try:
                details = json.loads(task_desc_json) if task_desc_json else {}
                results.append((event_id, created_at, details))
            except json.JSONDecodeError:
                continue

        return results
    except Exception as e:
        print(f"Error reading CIEU: {e}", file=sys.stderr)
        return []


def check_drift(contract, whitelist):
    """Check if contract contains constraints not in whitelist"""
    drifts = []

    # Check deny list
    for item in contract.get("deny", []):
        if item not in whitelist["deny"]:
            drifts.append(f"deny: {item}")

    # Check deny_commands
    for cmd in contract.get("deny_commands", []):
        if cmd not in whitelist["deny_commands"]:
            drifts.append(f"deny_commands: {cmd}")

    # Check only_paths
    for path in contract.get("only_paths", []):
        if path not in whitelist["only_paths"]:
            drifts.append(f"only_paths: {path}")

    # Check only_domains
    for domain in contract.get("only_domains", []):
        if domain not in whitelist["only_domains"]:
            drifts.append(f"only_domains: {domain}")

    return drifts


def emit_drift_event(event_id, timestamp, contract_summary, drifts):
    """Emit DIALOGUE_DRIFT CIEU event"""
    try:
        import uuid
        import time

        conn = sqlite3.connect(CIEU_DB)
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO cieu_events (
                event_id, seq_global, created_at, session_id, agent_id,
                event_type, decision, passed, task_description, drift_detected
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            str(uuid.uuid4()),
            int(time.time() * 1_000_000),
            time.time(),
            "drift_checker",
            "forget_guard",
            "DIALOGUE_DRIFT",
            "warn",
            0,  # Drift = violation
            json.dumps({
                "source_event_id": event_id,
                "source_timestamp": timestamp,
                "drifts": drifts,
                "contract_summary": contract_summary
            }),
            1  # drift_detected flag
        ))
        conn.commit()
        conn.close()
        return True
    except Exception as e:
        print(f"Error emitting DIALOGUE_DRIFT: {e}", file=sys.stderr)
        return False


def main():
    """Main drift checking loop"""
    start_time = datetime.now()

    # Load whitelist
    whitelist = load_whitelist()

    # Get recent dialogue contracts
    events = get_recent_dialogue_contracts(minutes=10)

    drift_count = 0
    with open(DRIFT_LOG, "a") as log:
        log.write(f"\n=== Drift Check {start_time.isoformat()} ===\n")
        log.write(f"Scanned {len(events)} DIALOGUE_CONTRACT_DRAFT events\n")

        for event_id, timestamp, details in events:
            contract = details.get("contract", {})
            if not contract:
                continue

            # Check for drift
            drifts = check_drift(contract, whitelist)

            if drifts:
                drift_count += 1
                log.write(f"\nDRIFT DETECTED (event {event_id}):\n")
                for drift in drifts:
                    log.write(f"  - {drift}\n")

                # Emit CIEU event
                contract_summary = f"msg: {details.get('user_msg_preview', '')[:100]}"
                if emit_drift_event(event_id, timestamp, contract_summary, drifts):
                    log.write(f"  → Emitted DIALOGUE_DRIFT event\n")

        log.write(f"Total drifts: {drift_count}\n")

    # Print summary to stdout (for cron/logging)
    print(f"Drift check complete: {drift_count} drifts in {len(events)} events")
    return 0 if drift_count == 0 else 1


if __name__ == "__main__":
    sys.exit(main())
