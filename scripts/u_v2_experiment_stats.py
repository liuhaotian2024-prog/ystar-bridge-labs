#!/usr/bin/env python3
"""
U_v2 Experiment Statistics — methodology_applied_rate measurement

Queries CIEU events emitted by the U_v2 hook instrument to compute:
  - % receipt with m_tag present
  - % receipt with empirical_basis (>=1 ref)
  - % receipt with counterfactual (>=30 chars)
  - % receipt with preexisting_search
  - % receipt with rt_plus_1_honest (non-performative 0)
  - composite = mean of above 5 rates

Usage:
  python3 scripts/u_v2_experiment_stats.py [--db PATH] [--since HOURS] [--json]

Platform Engineer: eng-platform
Experiment: reports/experiments/exp_u_v2_schema_persistence_20260424.md
"""
from __future__ import annotations

import argparse
import json
import os
import sqlite3
import sys
import time
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
DEFAULT_DB = REPO_ROOT / ".ystar_cieu.db"

U_V2_EVENT_TYPES = (
    "U_V2_SCHEMA_COMPLETE",
    "U_V2_SCHEMA_INCOMPLETE_DENY",
    "U_V2_THEATER_DETECTED",
)


def _connect(db_path: str) -> sqlite3.Connection:
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    return conn


def query_u_v2_events(db_path: str, since_hours: float = 0) -> list[dict]:
    """Fetch all U_V2_SCHEMA_* events from CIEU."""
    conn = _connect(db_path)
    placeholders = ",".join("?" for _ in U_V2_EVENT_TYPES)
    sql = f"""
        SELECT event_id, event_type, agent_id, created_at, params
        FROM cieu_events
        WHERE event_type IN ({placeholders})
    """
    params: list = list(U_V2_EVENT_TYPES)

    if since_hours > 0:
        cutoff = time.time() - since_hours * 3600
        sql += " AND created_at > ?"
        params.append(cutoff)

    sql += " ORDER BY created_at ASC"

    try:
        rows = conn.execute(sql, params).fetchall()
    except sqlite3.OperationalError:
        # Table may not exist yet
        return []
    finally:
        conn.close()

    results = []
    for row in rows:
        d = dict(row)
        if d.get("params"):
            try:
                d["params"] = json.loads(d["params"])
            except (json.JSONDecodeError, TypeError):
                pass
        results.append(d)
    return results


def compute_stats(events: list[dict]) -> dict:
    """
    Compute methodology_applied_rate from U_V2 CIEU events.

    Each event's params.field_status dict has per-field {present, theater} booleans.
    """
    total = len(events)
    if total == 0:
        return {
            "total_receipts": 0,
            "complete": 0,
            "incomplete": 0,
            "theater": 0,
            "field_rates": {},
            "composite_methodology_applied_rate": 0.0,
            "note": "No U_V2 events found. Ensure YSTAR_U_V2_EXPERIMENT=1 is set.",
        }

    complete = sum(1 for e in events if e.get("event_type") == "U_V2_SCHEMA_COMPLETE")
    incomplete = sum(1 for e in events if e.get("event_type") == "U_V2_SCHEMA_INCOMPLETE_DENY")
    theater = sum(1 for e in events if e.get("event_type") == "U_V2_THEATER_DETECTED")

    # Per-field rates from params.field_status
    fields = ["m_tag", "empirical_basis", "counterfactual",
              "preexisting_search", "rt_plus_1_honest"]
    field_present_count = {f: 0 for f in fields}
    field_nontheater_count = {f: 0 for f in fields}

    for ev in events:
        params = ev.get("params", {})
        if isinstance(params, str):
            try:
                params = json.loads(params)
            except (json.JSONDecodeError, TypeError):
                params = {}
        field_status = params.get("field_status", {})
        for f in fields:
            fs = field_status.get(f, {})
            if fs.get("present", False):
                field_present_count[f] += 1
                if not fs.get("theater", False):
                    field_nontheater_count[f] += 1

    field_rates = {}
    for f in fields:
        pct_present = (field_present_count[f] / total * 100) if total else 0
        pct_quality = (field_nontheater_count[f] / total * 100) if total else 0
        field_rates[f] = {
            "present_pct": round(pct_present, 1),
            "quality_pct": round(pct_quality, 1),  # present AND non-theater
        }

    # Composite = mean of quality_pct across 5 fields
    quality_values = [field_rates[f]["quality_pct"] for f in fields]
    composite = round(sum(quality_values) / len(quality_values), 1) if quality_values else 0.0

    return {
        "total_receipts": total,
        "complete": complete,
        "incomplete": incomplete,
        "theater": theater,
        "field_rates": field_rates,
        "composite_methodology_applied_rate": composite,
    }


def print_report(stats: dict, as_json: bool = False) -> None:
    """Print human-readable or JSON stats report."""
    if as_json:
        print(json.dumps(stats, indent=2))
        return

    total = stats["total_receipts"]
    print("=" * 60)
    print("U_v2 Experiment Statistics — methodology_applied_rate")
    print("=" * 60)
    print(f"Total receipts analyzed: {total}")
    print(f"  COMPLETE:  {stats['complete']}")
    print(f"  INCOMPLETE (DENY): {stats['incomplete']}")
    print(f"  THEATER DETECTED:  {stats['theater']}")
    print()

    if total == 0:
        print(stats.get("note", "No data."))
        return

    print("Per-field rates:")
    print(f"  {'Field':<25} {'Present%':>10} {'Quality%':>10}")
    print(f"  {'-'*25} {'-'*10} {'-'*10}")
    for f, rates in stats["field_rates"].items():
        print(f"  {f:<25} {rates['present_pct']:>9.1f}% {rates['quality_pct']:>9.1f}%")
    print()
    print(f"  COMPOSITE methodology_applied_rate: {stats['composite_methodology_applied_rate']:.1f}%")
    print()
    print("Quality% = present AND non-theater (substantive content)")
    print("=" * 60)


def main():
    parser = argparse.ArgumentParser(description="U_v2 experiment statistics")
    parser.add_argument("--db", default=str(DEFAULT_DB), help="CIEU database path")
    parser.add_argument("--since", type=float, default=0,
                        help="Only events from last N hours (0 = all)")
    parser.add_argument("--json", action="store_true", help="Output as JSON")
    args = parser.parse_args()

    if not os.path.exists(args.db):
        print(f"CIEU database not found: {args.db}", file=sys.stderr)
        sys.exit(1)

    events = query_u_v2_events(args.db, args.since)
    stats = compute_stats(events)
    print_report(stats, as_json=args.json)


if __name__ == "__main__":
    main()
