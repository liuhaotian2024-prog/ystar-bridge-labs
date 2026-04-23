#!/usr/bin/env python3
"""
CLI wrapper for Y* Field Validator — batch-validate recent CIEU events
and emit a WAVE2_STEP1_VALIDATOR_LANDED summary event.

Usage:
    python3 scripts/y_star_field_validator_run.py [--since "1 hour ago"] [--db-path .ystar_cieu.db] [--json]
"""
import argparse
import json
import sys
import os

# Ensure project root is on sys.path
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, PROJECT_ROOT)

from ystar.governance.y_star_field_validator import batch_validate_recent


def main():
    parser = argparse.ArgumentParser(
        description="Y* Field Validator — F1 Goodhart detection on CIEU events"
    )
    parser.add_argument(
        "--since",
        default="1 hour ago",
        help='Time window (e.g., "1 hour ago", "24 hours ago")',
    )
    parser.add_argument(
        "--db-path",
        default=os.path.join(PROJECT_ROOT, ".ystar_cieu.db"),
        help="Path to CIEU SQLite database",
    )
    parser.add_argument(
        "--json",
        action="store_true",
        dest="json_output",
        help="Output results as JSON",
    )
    args = parser.parse_args()

    # Run batch validation
    results = batch_validate_recent(db_path=args.db_path, since=args.since)

    # Emit WAVE2_STEP1_VALIDATOR_LANDED CIEU event
    event_id = _emit_landed_event(results, args.db_path)

    if args.json_output:
        output = {
            "validator_results": results,
            "landed_event_id": event_id,
        }
        print(json.dumps(output, indent=2))
    else:
        print(f"Y* Field Validator — F1 Goodhart Detection")
        print(f"  Window:   {args.since}")
        print(f"  Total:    {results['total']}")
        print(f"  Valid:    {results['valid_count']}")
        print(f"  Wishful:  {results['wishful_count']}")
        print(f"  Skipped:  {results['skipped_count']}")
        print(f"  Landed:   {event_id}")
        if results["events"]:
            print(f"\n  Events:")
            for ev in results["events"]:
                label = {1: "VALID", -1: "WISHFUL", 0: "SKIP"}[ev["result"]]
                print(f"    [{label}] {ev['m_functor']} | {ev['event_id'][:12]}... | {ev['task_description_snippet'][:50]}")


def _emit_landed_event(results: dict, db_path: str) -> str:
    """Emit the WAVE2_STEP1_VALIDATOR_LANDED summary CIEU event."""
    try:
        # Import emit_cieu from the project's helpers
        from scripts._cieu_helpers import emit_cieu

        summary = {
            "total_events_validated": results["total"],
            "valid_count": results["valid_count"],
            "wishful_count": results["wishful_count"],
            "f1_goodhart_live": True,
        }

        event_id = emit_cieu(
            event_type="WAVE2_STEP1_VALIDATOR_LANDED",
            decision="auto_approve",
            passed=1,
            task_description="F1 Goodhart field validator batch run complete",
            m_functor="M-2a",
            m_weight=0.9,
            file_path="scripts/y_star_field_validator_run.py",
            params_json=json.dumps(summary),
        )
        return event_id or "EMIT_FAILED"

    except Exception as e:
        sys.stderr.write(f"[VALIDATOR_LANDED] emit failed: {e}\n")
        return f"EMIT_FAILED: {e}"


if __name__ == "__main__":
    main()
