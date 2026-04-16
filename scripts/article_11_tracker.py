#!/usr/bin/env python3
"""
[L4] Article 11 Layer Completion Tracker — AMENDMENT-023

Emit CIEU events when CEO completes Article 11 layers (7-layer cognitive construction).
Check compliance before major decisions.

Usage:
    python3 scripts/article_11_tracker.py layer_complete --layer 0 --evidence "Y* contract: Vogels"
    python3 scripts/article_11_tracker.py check_compliance --window_hours 2
"""

import sys
import json
import sqlite3
import time
import argparse
from pathlib import Path
from datetime import datetime, timedelta
sys.path.insert(0, str(Path(__file__).parent))
from _cieu_helpers import _get_current_agent

WORKSPACE_ROOT = Path("/Users/haotianliu/.openclaw/workspace/ystar-company")
CIEU_DB = WORKSPACE_ROOT / ".ystar_cieu.db"
SESSION_JSON = WORKSPACE_ROOT / ".ystar_session.json"
ACTIVE_AGENT_FILE = WORKSPACE_ROOT / ".ystar_active_agent"

ARTICLE_11_LAYERS = {
    0: "Y* (ideal contract)",
    1: "Pre-session context (twin trace)",
    2: "Decision (counterfactual analysis)",
    3: "Memory (session state + LRS)",
    4: "Execution (RAPID + constraints)",
    5: "Track (emit CIEU events)",
    6: "Learn (extract lessons)"
}


def get_active_agent():
    """Read current active agent from .ystar_active_agent"""
    try:
        return ACTIVE_AGENT_FILE.read_text().strip()
    except Exception:
        return "unknown"


def get_session_id():
    """Read current session_id from .ystar_session.json"""
    try:
        with open(SESSION_JSON) as f:
            data = json.load(f)
            return data.get("session_id", "unknown")
    except Exception:
        return "unknown"


def layer_complete(layer: int, evidence: str, db_path: str = None):
    """
    Emit ARTICLE_11_LAYER_X_COMPLETE event to CIEU.

    Args:
        layer: Layer number 0-6
        evidence: Brief description of what was completed
        db_path: Path to CIEU database (defaults to CIEU_DB)
    """
    if layer not in range(7):
        print(f"[ARTICLE_11_TRACKER] ERROR: layer must be 0-6, got {layer}", file=sys.stderr)
        return False

    if not evidence or len(evidence.strip()) < 10:
        print(f"[ARTICLE_11_TRACKER] ERROR: evidence must be at least 10 chars", file=sys.stderr)
        return False

    db = Path(db_path) if db_path else CIEU_DB
    if not db.exists():
        print(f"[ARTICLE_11_TRACKER] ERROR: CIEU database not found at {db}", file=sys.stderr)
        return False

    try:
        conn = sqlite3.connect(db)
        cursor = conn.cursor()

        # Generate event metadata
        import uuid
        event_id = str(uuid.uuid4())
        seq_global = int(time.time() * 1_000_000)
        created_at = time.time()
        session_id = get_session_id()
        agent_id = get_active_agent()
        event_type = f"ARTICLE_11_LAYER_{layer}_COMPLETE"

        # Insert into cieu_events
        cursor.execute("""
            INSERT INTO cieu_events (
                event_id, seq_global, created_at, session_id, agent_id,
                event_type, decision, passed, drift_detected, drift_details
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            event_id, seq_global, created_at, session_id, agent_id,
            event_type, "complete", 1, 0, evidence[:500]
        ))

        conn.commit()
        conn.close()

        layer_name = ARTICLE_11_LAYERS[layer]
        print(f"[ARTICLE_11_TRACKER] ✓ Layer {layer} ({layer_name}) complete: {evidence[:80]}")
        return True

    except Exception as e:
        print(f"[ARTICLE_11_TRACKER] ERROR writing to CIEU: {e}", file=sys.stderr)
        return False


def check_compliance(window_hours: int = 2, db_path: str = None):
    """
    Check if all 7 Article 11 layers have been completed within the time window.

    Args:
        window_hours: Time window in hours to look for layer events
        db_path: Path to CIEU database (defaults to CIEU_DB)

    Returns:
        dict with keys: status (PASS/FAIL), completed_layers, missing_layers, events
    """
    db = Path(db_path) if db_path else CIEU_DB
    if not db.exists():
        return {
            "status": "ERROR",
            "error": f"CIEU database not found at {db}",
            "completed_layers": [],
            "missing_layers": list(range(7))
        }

    try:
        conn = sqlite3.connect(db)
        cursor = conn.cursor()

        # Calculate time window
        window_start = datetime.now() - timedelta(hours=window_hours)
        window_start_unix = window_start.timestamp()

        # Query for Article 11 layer events in window
        cursor.execute("""
            SELECT event_type, drift_details, created_at
            FROM cieu_events
            WHERE event_type LIKE 'ARTICLE_11_LAYER_%_COMPLETE'
            AND created_at > ?
            ORDER BY created_at DESC
        """, (window_start_unix,))

        rows = cursor.fetchall()
        conn.close()

        # Parse which layers are completed
        completed_layers = set()
        events = []
        for event_type, evidence, created_at in rows:
            # Extract layer number from event_type
            try:
                layer_num = int(event_type.split('_')[3])
                completed_layers.add(layer_num)
                events.append({
                    "layer": layer_num,
                    "evidence": evidence,
                    "timestamp": datetime.fromtimestamp(created_at).isoformat()
                })
            except (IndexError, ValueError):
                continue

        # Determine missing layers
        all_layers = set(range(7))
        missing_layers = sorted(all_layers - completed_layers)
        completed_layers_list = sorted(completed_layers)

        # Status determination
        status = "PASS" if len(missing_layers) == 0 else "FAIL"

        result = {
            "status": status,
            "completed_layers": completed_layers_list,
            "missing_layers": missing_layers,
            "events": events,
            "window_hours": window_hours
        }

        if status == "FAIL":
            print(f"[ARTICLE_11_TRACKER] ❌ COMPLIANCE FAIL: missing layers {missing_layers}")
            for layer in missing_layers:
                print(f"  Layer {layer}: {ARTICLE_11_LAYERS[layer]}")
        else:
            print(f"[ARTICLE_11_TRACKER] ✓ COMPLIANCE PASS: all 7 layers completed in last {window_hours}h")

        return result

    except Exception as e:
        return {
            "status": "ERROR",
            "error": str(e),
            "completed_layers": [],
            "missing_layers": list(range(7))
        }


def main():
    parser = argparse.ArgumentParser(description="Article 11 Layer Completion Tracker")
    subparsers = parser.add_subparsers(dest="command", help="Command to execute")

    # layer_complete command
    complete_parser = subparsers.add_parser("layer_complete", help="Mark a layer as complete")
    complete_parser.add_argument("--layer", type=int, required=True, choices=range(7),
                                 help="Layer number (0-6)")
    complete_parser.add_argument("--evidence", type=str, required=True,
                                 help="Evidence/description of layer completion")
    complete_parser.add_argument("--db", type=str, help="Path to CIEU database")

    # check_compliance command
    check_parser = subparsers.add_parser("check_compliance", help="Check if all layers are complete")
    check_parser.add_argument("--window_hours", type=int, default=2,
                              help="Time window in hours (default: 2)")
    check_parser.add_argument("--db", type=str, help="Path to CIEU database")

    args = parser.parse_args()

    if args.command == "layer_complete":
        success = layer_complete(args.layer, args.evidence, args.db)
        sys.exit(0 if success else 1)

    elif args.command == "check_compliance":
        result = check_compliance(args.window_hours, args.db)
        print(json.dumps(result, indent=2))
        sys.exit(0 if result["status"] == "PASS" else 1)

    else:
        parser.print_help()
        sys.exit(1)


if __name__ == "__main__":
    main()
