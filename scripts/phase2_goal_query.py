#!/usr/bin/env python3
"""Phase 2 goal-tree query API — read-only helpers + CLI.

Modes:
  --list-goals [--active-only]
  --goal-progress <goal_id>
  --role-alignment <role_id> [--since "1 hour ago"]
  --top-advancing-goals --since "24 hours ago" [--limit 5]

All read-only (SQLite mode=ro URI). JSON output via --json.

Usage:
    python3 scripts/phase2_goal_query.py --list-goals --json
    python3 scripts/phase2_goal_query.py --goal-progress M-1 --json
    python3 scripts/phase2_goal_query.py --role-alignment ceo --since "1 hour ago" --json
    python3 scripts/phase2_goal_query.py --top-advancing-goals --since "24 hours ago" --limit 5 --json
"""

import argparse
import json
import os
import re
import sqlite3
import sys
import time
from typing import Any, Dict, List, Optional, Tuple


def _parse_since(since_str: str) -> float:
    """Parse human-readable relative time string to epoch timestamp.

    Supports: '1 hour ago', '24 hours ago', '30 minutes ago', '7 days ago'.
    """
    now = time.time()
    m = re.match(r"(\d+)\s+(second|minute|hour|day|week)s?\s+ago", since_str.strip())
    if not m:
        raise ValueError(f"Cannot parse --since '{since_str}'. Use format like '1 hour ago', '24 hours ago'.")
    amount = int(m.group(1))
    unit = m.group(2)
    multipliers = {"second": 1, "minute": 60, "hour": 3600, "day": 86400, "week": 604800}
    return now - amount * multipliers[unit]


def _connect_ro(db_path: str) -> sqlite3.Connection:
    """Open database in read-only mode via URI."""
    uri = f"file:{db_path}?mode=ro"
    conn = sqlite3.connect(uri, uri=True)
    conn.row_factory = sqlite3.Row
    return conn


def list_goals(conn: sqlite3.Connection, active_only: bool = False) -> List[Dict[str, Any]]:
    """List all goals, optionally filtered to active-only."""
    sql = "SELECT * FROM ystar_goal_tree"
    if active_only:
        sql += " WHERE status = 'active'"
    sql += " ORDER BY created_at DESC"
    rows = conn.execute(sql).fetchall()
    return [dict(r) for r in rows]


def goal_progress(conn: sqlite3.Connection, goal_id: str) -> Dict[str, Any]:
    """Sum contribution scores for a specific goal."""
    row = conn.execute(
        "SELECT goal_id, COUNT(*) as contribution_count, "
        "COALESCE(SUM(goal_contribution_score), 0.0) as total_contribution, "
        "COALESCE(AVG(role_alignment_score), 0.0) as avg_role_alignment "
        "FROM cieu_goal_contribution WHERE goal_id = ?",
        (goal_id,)
    ).fetchone()
    result = dict(row) if row else {}
    # If no contributions, goal_id will be None from the aggregate
    if result.get("goal_id") is None:
        result["goal_id"] = goal_id
        result["contribution_count"] = 0
        result["total_contribution"] = 0.0
        result["avg_role_alignment"] = 0.0
    return result


def role_alignment(conn: sqlite3.Connection, role_id: str, since: Optional[float] = None) -> Dict[str, Any]:
    """Compute role alignment stats for a given role."""
    # Join goal_tree (owner_role) with contributions
    sql = (
        "SELECT c.goal_id, c.role_alignment_score, c.goal_contribution_score, c.created_at "
        "FROM cieu_goal_contribution c "
        "JOIN ystar_goal_tree g ON c.goal_id = g.goal_id "
        "WHERE g.owner_role = ?"
    )
    params: List[Any] = [role_id]
    if since is not None:
        sql += " AND c.created_at >= ?"
        params.append(since)
    sql += " ORDER BY c.created_at DESC"
    rows = conn.execute(sql, params).fetchall()
    contributions = [dict(r) for r in rows]
    total_score = sum(c.get("goal_contribution_score", 0) or 0 for c in contributions)
    avg_alignment = (sum(c.get("role_alignment_score", 0) or 0 for c in contributions) / len(contributions)) if contributions else 0.0
    return {
        "role": role_id,
        "contribution_count": len(contributions),
        "total_contribution_score": total_score,
        "avg_role_alignment_score": round(avg_alignment, 4),
        "contributions": contributions,
    }


def top_advancing_goals(conn: sqlite3.Connection, since: float, limit: int = 5) -> List[Dict[str, Any]]:
    """Return goals ranked by total contribution score in the given window."""
    rows = conn.execute(
        "SELECT c.goal_id, g.goal_text, g.owner_role, "
        "SUM(c.goal_contribution_score) as total_contribution, "
        "COUNT(*) as event_count "
        "FROM cieu_goal_contribution c "
        "LEFT JOIN ystar_goal_tree g ON c.goal_id = g.goal_id "
        "WHERE c.created_at >= ? "
        "GROUP BY c.goal_id "
        "ORDER BY total_contribution DESC "
        "LIMIT ?",
        (since, limit)
    ).fetchall()
    return [dict(r) for r in rows]


def _format_output(data: Any, as_json: bool) -> str:
    """Format output as JSON or human-readable."""
    if as_json:
        return json.dumps(data, indent=2, ensure_ascii=False, default=str)
    if isinstance(data, list):
        if not data:
            return "(no results)"
        lines = []
        for item in data:
            lines.append("  ".join(f"{k}={v}" for k, v in item.items()))
        return "\n".join(lines)
    if isinstance(data, dict):
        return "\n".join(f"{k}: {v}" for k, v in data.items())
    return str(data)


def main() -> None:
    default_db = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), ".ystar_cieu.db")

    parser = argparse.ArgumentParser(
        description="Phase 2 goal-tree query API (read-only)",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="All queries are read-only against .ystar_cieu.db.\n"
               "Use --json for machine-readable output."
    )
    parser.add_argument("--db", default=default_db, help="Path to CIEU database")
    parser.add_argument("--json", action="store_true", dest="as_json", help="Output as JSON")

    # Modes (mutually exclusive)
    mode = parser.add_mutually_exclusive_group()
    mode.add_argument("--list-goals", action="store_true", help="List all goals")
    mode.add_argument("--goal-progress", metavar="GOAL_ID", help="Show contribution progress for a goal")
    mode.add_argument("--role-alignment", metavar="ROLE_ID", help="Show alignment stats for a role")
    mode.add_argument("--top-advancing-goals", action="store_true", help="Rank goals by contribution")

    parser.add_argument("--active-only", action="store_true", help="Filter to active goals only (with --list-goals)")
    parser.add_argument("--since", metavar="TIME", help="Time window, e.g. '1 hour ago', '24 hours ago'")
    parser.add_argument("--limit", type=int, default=5, help="Max results for --top-advancing-goals (default: 5)")

    args = parser.parse_args()

    # Require at least one mode
    if not any([args.list_goals, args.goal_progress, args.role_alignment, args.top_advancing_goals]):
        parser.print_help()
        sys.exit(0)

    if not os.path.exists(args.db):
        print(f"ERROR: DB not found at {args.db}", file=sys.stderr)
        sys.exit(1)

    conn = _connect_ro(args.db)
    try:
        if args.list_goals:
            result = list_goals(conn, active_only=args.active_only)
            print(_format_output(result, args.as_json))

        elif args.goal_progress:
            result = goal_progress(conn, args.goal_progress)
            print(_format_output(result, args.as_json))

        elif args.role_alignment:
            since_ts = _parse_since(args.since) if args.since else None
            result = role_alignment(conn, args.role_alignment, since=since_ts)
            print(_format_output(result, args.as_json))

        elif args.top_advancing_goals:
            if not args.since:
                print("ERROR: --top-advancing-goals requires --since", file=sys.stderr)
                sys.exit(1)
            since_ts = _parse_since(args.since)
            result = top_advancing_goals(conn, since_ts, limit=args.limit)
            print(_format_output(result, args.as_json))
    finally:
        conn.close()


if __name__ == "__main__":
    main()
