#!/usr/bin/env python3
"""
CIEU Receipt Verifier — CLI tool for empirical sub-agent receipt verification.

Queries .ystar_cieu.db for a given event_id and verifies expected fields.
Read-only on DB. Used by CEO to verify sub-agent claims per Tier 1 hard gate.

Exit codes:
  0 — event found and all assertions pass
  1 — event not found, or assertion mismatch, or field is NULL
  2 — DB file missing or other infrastructure error

Usage:
  python3 scripts/cieu_receipt_verifier.py --event-id <uuid> [--expected-decision <str>] [--expected-file-path <path>] [--json]
"""

import argparse
import json
import re
import sqlite3
import sys
import time
from pathlib import Path
from typing import Dict, List, Optional

CIEU_DB_PATH = Path("/Users/haotianliu/.openclaw/workspace/ystar-company/.ystar_cieu.db")

UUID_RE = re.compile(
    r'^[0-9a-fA-F]{8}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{12}$'
)


def validate_uuid(value: str) -> bool:
    return bool(UUID_RE.match(value))


def build_result(
    found: bool,
    event_id: str,
    row: Optional[Dict] = None,
    error: Optional[str] = None,
    assertions: Optional[List[Dict]] = None,
) -> Dict:
    result = {
        "found": found,
        "event_id": event_id,
    }
    if row:
        result["decision"] = row.get("decision")
        result["created_at"] = row.get("created_at")
        result["agent_id"] = row.get("agent_id")
        result["event_type"] = row.get("event_type")
        result["file_path"] = row.get("file_path")
        params = row.get("params_json") or ""
        result["params_json_preview_first_200_chars"] = params[:200]
    if error:
        result["error"] = error
    if assertions:
        result["assertions"] = assertions
    return result


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Verify a CIEU event by event_id. Read-only DB query."
    )
    parser.add_argument(
        "--event-id", required=True, help="UUID of the CIEU event to look up"
    )
    parser.add_argument(
        "--expected-decision",
        default=None,
        help="Assert that the event's decision field equals this value",
    )
    parser.add_argument(
        "--expected-file-path",
        default=None,
        help="Assert that the event's file_path field equals this value",
    )
    parser.add_argument(
        "--json",
        action="store_true",
        dest="json_mode",
        help="Emit JSON to stdout instead of human-readable output",
    )
    args = parser.parse_args()

    # --- UUID format validation ---
    if not validate_uuid(args.event_id):
        err = f"Malformed event_id: '{args.event_id}' is not a valid UUID (expected 8-4-4-4-12 hex)"
        if args.json_mode:
            print(json.dumps({"found": False, "event_id": args.event_id, "error": err}))
        else:
            print(err, file=sys.stderr)
        return 1

    # --- DB existence check ---
    if not CIEU_DB_PATH.exists():
        err = f"CIEU database not found at {CIEU_DB_PATH}"
        if args.json_mode:
            print(json.dumps({"found": False, "event_id": args.event_id, "error": err}))
        else:
            print(err, file=sys.stderr)
        return 2

    # --- Query (read-only) ---
    try:
        uri = f"file:{CIEU_DB_PATH}?mode=ro"
        conn = sqlite3.connect(uri, uri=True)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        cursor.execute(
            "SELECT event_id, decision, created_at, agent_id, event_type, "
            "file_path, params_json FROM cieu_events WHERE event_id = ?",
            (args.event_id,),
        )
        row = cursor.fetchone()
        conn.close()
    except sqlite3.OperationalError as e:
        err = f"DB query error: {e}"
        if args.json_mode:
            print(json.dumps({"found": False, "event_id": args.event_id, "error": err}))
        else:
            print(err, file=sys.stderr)
        return 2

    # --- Not found ---
    if row is None:
        result = build_result(False, args.event_id, error="Event not found in cieu_events")
        if args.json_mode:
            print(json.dumps(result))
        else:
            print(f"NOT FOUND: event_id={args.event_id}", file=sys.stderr)
        return 1

    # --- Found: build result and run assertions ---
    row_dict = dict(row)
    assertions = []
    all_pass = True

    # Check for NULL fields in critical columns
    for field in ("decision", "event_type", "agent_id"):
        if row_dict.get(field) is None:
            assertions.append({"field": field, "status": "FAIL", "reason": f"found but {field} is null"})
            all_pass = False

    # --expected-decision assertion
    if args.expected_decision is not None:
        actual = row_dict.get("decision")
        if actual is None:
            assertions.append({"field": "decision", "status": "FAIL", "reason": "decision is null"})
            all_pass = False
        elif actual != args.expected_decision:
            assertions.append({
                "field": "decision",
                "status": "FAIL",
                "reason": f"expected '{args.expected_decision}', got '{actual}'",
            })
            all_pass = False
        else:
            assertions.append({"field": "decision", "status": "PASS"})

    # --expected-file-path assertion
    if args.expected_file_path is not None:
        actual = row_dict.get("file_path")
        if actual is None:
            assertions.append({"field": "file_path", "status": "FAIL", "reason": "file_path is null"})
            all_pass = False
        elif actual != args.expected_file_path:
            assertions.append({
                "field": "file_path",
                "status": "FAIL",
                "reason": f"expected '{args.expected_file_path}', got '{actual}'",
            })
            all_pass = False
        else:
            assertions.append({"field": "file_path", "status": "PASS"})

    result = build_result(True, args.event_id, row=row_dict, assertions=assertions if assertions else None)
    exit_code = 0 if all_pass else 1

    if args.json_mode:
        print(json.dumps(result, indent=2))
    else:
        # Human-readable output
        ts = row_dict.get("created_at")
        ts_str = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(ts)) if ts else "N/A"
        print(f"CIEU Event Verification")
        print(f"  event_id:   {row_dict['event_id']}")
        print(f"  event_type: {row_dict.get('event_type', 'N/A')}")
        print(f"  decision:   {row_dict.get('decision', 'N/A')}")
        print(f"  agent_id:   {row_dict.get('agent_id', 'N/A')}")
        print(f"  file_path:  {row_dict.get('file_path', 'N/A')}")
        print(f"  created_at: {ts_str} (epoch: {ts})")
        if assertions:
            print(f"  assertions:")
            for a in assertions:
                status = a["status"]
                field = a["field"]
                reason = a.get("reason", "")
                print(f"    {field}: {status}" + (f" — {reason}" if reason else ""))
        print(f"  result:     {'PASS' if all_pass else 'FAIL'}")

    return exit_code


if __name__ == "__main__":
    sys.exit(main())
