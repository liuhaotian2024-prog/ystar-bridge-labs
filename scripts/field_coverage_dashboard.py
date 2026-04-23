#!/usr/bin/env python3
"""
Y* Field Functional Coverage Dashboard
---------------------------------------
One-shot CLI that prints m_functor coverage statistics from the CIEU database.

Usage:
    python3 scripts/field_coverage_dashboard.py
    python3 scripts/field_coverage_dashboard.py --json
    python3 scripts/field_coverage_dashboard.py --db-path /path/to/.ystar_cieu.db
"""
import argparse
import json
import os
import sqlite3
import sys
from datetime import datetime, timezone

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DEFAULT_DB = os.path.join(PROJECT_ROOT, ".ystar_cieu.db")

# M-triangle label map for human-readable output
M_LABELS = {
    "M-1": "Survivability",
    "M-2a": "Commission",
    "M-2b": "Omission",
    "M-3": "Value",
}

TARGET_COVERAGE_PCT = 90.0
BACKFILL_ROWS_PER_RUN = 10000
BACKFILL_INTERVAL_MINUTES = 15


def _query_coverage(db_path):
    """Return coverage stats dict from CIEU database (read-only)."""
    conn = sqlite3.connect("file:{}?mode=ro".format(db_path), uri=True)
    conn.row_factory = sqlite3.Row

    # Total and tagged counts
    row = conn.execute(
        "SELECT COUNT(*) AS total, "
        "SUM(CASE WHEN m_functor IS NOT NULL AND m_functor != '' THEN 1 ELSE 0 END) AS tagged "
        "FROM cieu_events"
    ).fetchone()
    total = row["total"]
    tagged = row["tagged"] if row["tagged"] else 0

    # Distribution by m_functor
    dist_rows = conn.execute(
        "SELECT m_functor, COUNT(*) AS cnt "
        "FROM cieu_events "
        "WHERE m_functor IS NOT NULL AND m_functor != '' "
        "GROUP BY m_functor "
        "ORDER BY cnt DESC"
    ).fetchall()
    distribution = []
    for dr in dist_rows:
        distribution.append({
            "functor": dr["m_functor"],
            "label": M_LABELS.get(dr["m_functor"], "Unknown"),
            "count": dr["cnt"],
            "pct": round(100.0 * dr["cnt"] / tagged, 1) if tagged > 0 else 0.0,
        })

    # Agent alignment (top agents by tagged events)
    agent_rows = conn.execute(
        "SELECT agent_id, m_functor, COUNT(*) AS cnt "
        "FROM cieu_events "
        "WHERE m_functor IS NOT NULL AND m_functor != '' "
        "GROUP BY agent_id, m_functor "
        "ORDER BY agent_id, cnt DESC"
    ).fetchall()

    agents = {}
    for ar in agent_rows:
        aid = ar["agent_id"]
        if aid not in agents:
            agents[aid] = {"total": 0, "functors": {}}
        agents[aid]["total"] += ar["cnt"]
        agents[aid]["functors"][ar["m_functor"]] = ar["cnt"]

    # Sort agents by total tagged events descending, take top 5
    sorted_agents = sorted(agents.items(), key=lambda x: x[1]["total"], reverse=True)[:5]
    agent_alignment = []
    for aid, data in sorted_agents:
        agent_alignment.append({
            "agent_id": aid,
            "total": data["total"],
            "functors": data["functors"],
        })

    # Latest backfill run timestamp
    backfill_row = conn.execute(
        "SELECT created_at, params_json FROM cieu_events "
        "WHERE event_type = 'WAVE2_BACKFILL_COMPLETE' "
        "ORDER BY created_at DESC LIMIT 1"
    ).fetchone()

    latest_backfill = None
    latest_backfill_rows = 0
    if backfill_row:
        latest_backfill = datetime.fromtimestamp(
            backfill_row["created_at"], tz=timezone.utc
        ).strftime("%Y-%m-%d %H:%M UTC")
        try:
            params = json.loads(backfill_row["params_json"] or "{}")
            latest_backfill_rows = params.get("rows_inferred", 0)
        except (json.JSONDecodeError, TypeError):
            pass

    conn.close()

    # ETA calculation
    remaining = max(0, total - tagged)
    coverage_pct = round(100.0 * tagged / total, 2) if total > 0 else 0.0

    # ~75% skip rate observed, so effective infer rate ~2500/run
    effective_per_run = BACKFILL_ROWS_PER_RUN * 0.25
    runs_needed = remaining / effective_per_run if effective_per_run > 0 else float("inf")
    eta_minutes = runs_needed * BACKFILL_INTERVAL_MINUTES
    if eta_minutes < 60:
        eta_str = "~{:.0f} minutes".format(eta_minutes)
    elif eta_minutes < 1440:
        eta_str = "~{:.0f} hours".format(eta_minutes / 60)
    else:
        eta_str = "~{:.1f} days".format(eta_minutes / 1440)

    return {
        "total": total,
        "tagged": tagged,
        "coverage_pct": coverage_pct,
        "target_pct": TARGET_COVERAGE_PCT,
        "distribution": distribution,
        "agent_alignment": agent_alignment,
        "latest_backfill": latest_backfill,
        "latest_backfill_rows": latest_backfill_rows,
        "eta_to_target": eta_str,
        "remaining": remaining,
        "timestamp": datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC"),
    }


def _print_human(stats):
    """Print human-readable dashboard."""
    print("")
    print("===== Y* Field Functional Coverage Dashboard =====")
    print("Total CIEU events: {:,}".format(stats["total"]))
    print("Tagged (m_functor != NULL): {:,} ({:.2f}%)".format(
        stats["tagged"], stats["coverage_pct"]))
    print("Target: {:.0f}%+".format(stats["target_pct"]))
    print("")
    print("Distribution:")
    for d in stats["distribution"]:
        label = "{} ({})".format(d["functor"], d["label"])
        print("  {:<25s} {:>6,} ({:>5.1f}%)".format(
            label + ":", d["count"], d["pct"]))
    print("")
    print("Agent alignment (top 5 agents by tagged events):")
    for a in stats["agent_alignment"]:
        parts = []
        for f, c in sorted(a["functors"].items()):
            parts.append("{} {}".format(c, f))
        print("  {:<20s} {}".format(a["agent_id"] + ":", " / ".join(parts)))
    print("")
    if stats["latest_backfill"]:
        print("Latest backfill run: {} (+{} rows)".format(
            stats["latest_backfill"], stats["latest_backfill_rows"]))
    else:
        print("Latest backfill run: none recorded")
    print("ETA to {:.0f}% coverage @ {:,}/{:d}min: {}".format(
        stats["target_pct"], BACKFILL_ROWS_PER_RUN,
        BACKFILL_INTERVAL_MINUTES, stats["eta_to_target"]))
    print("")


def main():
    parser = argparse.ArgumentParser(
        description="Y* Field Functional Coverage Dashboard"
    )
    parser.add_argument(
        "--db-path",
        default=DEFAULT_DB,
        help="Path to CIEU SQLite database (default: .ystar_cieu.db)",
    )
    parser.add_argument(
        "--json",
        action="store_true",
        dest="json_output",
        help="Output results as JSON",
    )
    args = parser.parse_args()

    if not os.path.exists(args.db_path):
        sys.stderr.write("ERROR: CIEU database not found at {}\n".format(args.db_path))
        sys.exit(1)

    stats = _query_coverage(args.db_path)

    if args.json_output:
        print(json.dumps(stats, indent=2))
    else:
        _print_human(stats)


if __name__ == "__main__":
    main()
