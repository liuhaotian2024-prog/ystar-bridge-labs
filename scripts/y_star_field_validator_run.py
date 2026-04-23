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

from ystar.governance.y_star_field_validator import batch_validate_recent, batch_backfill


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
    parser.add_argument(
        "--backfill",
        action="store_true",
        help="Run backfill mode: infer m_functor for historical NULL rows",
    )
    parser.add_argument(
        "--limit",
        type=int,
        default=5000,
        help="Max rows to process per backfill run (default 5000)",
    )
    args = parser.parse_args()

    if args.backfill:
        _run_backfill(args)
    else:
        _run_validate(args)


def _run_validate(args):
    """Original validation mode."""
    results = batch_validate_recent(db_path=args.db_path, since=args.since)
    event_id = _emit_landed_event(results, args.db_path)

    if args.json_output:
        output = {
            "validator_results": results,
            "landed_event_id": event_id,
        }
        print(json.dumps(output, indent=2))
    else:
        print("Y* Field Validator — F1 Goodhart Detection")
        print("  Window:   {}".format(args.since))
        print("  Total:    {}".format(results['total']))
        print("  Valid:    {}".format(results['valid_count']))
        print("  Wishful:  {}".format(results['wishful_count']))
        print("  Skipped:  {}".format(results['skipped_count']))
        print("  Landed:   {}".format(event_id))
        if results["events"]:
            print("\n  Events:")
            for ev in results["events"]:
                label = {1: "VALID", -1: "WISHFUL", 0: "SKIP"}[ev["result"]]
                print("    [{}] {} | {}... | {}".format(
                    label, ev['m_functor'], ev['event_id'][:12],
                    ev['task_description_snippet'][:50])
                )


def _run_backfill(args):
    """Backfill mode: infer m_functor for historical NULL rows."""
    import sqlite3 as _sql

    db_path = args.db_path
    limit = args.limit

    # Process in batches of 5000
    batch_size = 5000
    total_stats = {
        "scanned": 0, "inferred": 0, "skipped_no_signal": 0,
        "valid_count": 0, "wishful_count": 0,
    }
    remaining = limit
    batch_num = 0

    while remaining > 0:
        this_batch = min(batch_size, remaining)
        stats = batch_backfill(db_path=db_path, limit=this_batch)

        for k in total_stats:
            total_stats[k] += stats[k]

        batch_num += 1
        print("[batch {}] scanned={} inferred={} skipped={}".format(
            batch_num, stats["scanned"], stats["inferred"],
            stats["skipped_no_signal"]))

        remaining -= this_batch

        # If we got fewer rows than requested, table is exhausted
        if stats["scanned"] < this_batch:
            break

    # Compute post-backfill coverage
    try:
        conn = _sql.connect(db_path)
        row = conn.execute(
            "SELECT COUNT(*) total, "
            "SUM(CASE WHEN m_functor IS NOT NULL AND m_functor != '' THEN 1 ELSE 0 END) with_tag "
            "FROM cieu_events"
        ).fetchone()
        total_rows = row[0] if row else 0
        with_tag = row[1] if row else 0
        coverage_pct = round(100.0 * with_tag / total_rows, 2) if total_rows > 0 else 0.0
        conn.close()
    except Exception:
        total_rows, with_tag, coverage_pct = 0, 0, 0.0

    # Emit WAVE2_BACKFILL_COMPLETE CIEU event
    event_id = _emit_backfill_event(total_stats, coverage_pct, db_path)

    output_data = {
        "backfill_stats": total_stats,
        "coverage": {
            "total_rows": total_rows,
            "with_tag": with_tag,
            "coverage_pct": coverage_pct,
        },
        "backfill_event_id": event_id,
    }

    if args.json_output:
        print(json.dumps(output_data, indent=2))
    else:
        print("\nY* Field Validator — Backfill Complete")
        print("  Scanned:       {}".format(total_stats['scanned']))
        print("  Inferred:      {}".format(total_stats['inferred']))
        print("  Skipped:       {}".format(total_stats['skipped_no_signal']))
        print("  Valid:          {}".format(total_stats['valid_count']))
        print("  Wishful:       {}".format(total_stats['wishful_count']))
        print("  Coverage:      {}/{} ({:.2f}%)".format(with_tag, total_rows, coverage_pct))
        print("  CIEU Event:    {}".format(event_id))


def _emit_backfill_event(stats, coverage_pct, db_path):
    # type: (dict, float, str) -> str
    """Emit WAVE2_BACKFILL_COMPLETE summary CIEU event."""
    try:
        from scripts._cieu_helpers import emit_cieu

        summary = {
            "rows_inferred": stats["inferred"],
            "valid_count": stats["valid_count"],
            "wishful_count": stats["wishful_count"],
            "skipped": stats["skipped_no_signal"],
            "coverage_pct_post_backfill": coverage_pct,
        }

        event_id = emit_cieu(
            event_type="WAVE2_BACKFILL_COMPLETE",
            decision="auto_approve",
            passed=1,
            task_description="Backfill m_functor inference on historical CIEU events",
            m_functor="M-2a",
            m_weight=0.9,
            file_path="scripts/y_star_field_validator_run.py",
            params_json=json.dumps(summary),
        )
        return event_id or "EMIT_FAILED"

    except Exception as e:
        sys.stderr.write("[BACKFILL_COMPLETE] emit failed: {}\n".format(e))
        return "EMIT_FAILED: {}".format(e)


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
