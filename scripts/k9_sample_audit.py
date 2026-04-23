#!/usr/bin/env python3
"""
k9_sample_audit.py — Tier 2 K9 Sampling Audit for CIEU Events

Picks a configurable percentage (10-30%) of recent CIEU events that have both
params_json and result_json populated, and performs semantic consistency checks.
Reports anomalies to reports/cto/k9_sample_audits/audit_<ISO>.md.

K9 is a PURE READER — this script NEVER writes to .ystar_cieu.db.
All findings go to report files only.

Usage:
    python3 scripts/k9_sample_audit.py --sample-rate 0.2 --since "1 hour ago" [--agent-filter ryan]
    python3 scripts/k9_sample_audit.py --help

Exit codes:
    0 = no anomalies found
    1 = anomalies found (see report)
    2 = error (bad args, DB not found, etc.)
"""

import argparse
import datetime
import json
import os
import random
import re
import sqlite3
import sys
import uuid


# ── Paths ──────────────────────────────────────────────────────────────────────
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
REPO_ROOT = os.path.dirname(SCRIPT_DIR)
DEFAULT_DB = os.path.join(REPO_ROOT, ".ystar_cieu.db")
REPORT_DIR = os.path.join(REPO_ROOT, "reports", "cto", "k9_sample_audits")


# ── Time parsing ───────────────────────────────────────────────────────────────
def parse_since(since_str: str) -> float:
    """Parse human-readable time offset into a Unix timestamp.

    Supported formats:
        "N hour(s) ago", "N minute(s) ago", "N day(s) ago"
        ISO 8601 timestamp (2026-04-23T12:00:00)
        Unix timestamp (float)
    """
    now = datetime.datetime.utcnow()

    # Try relative format: "N unit ago"
    m = re.match(r"(\d+)\s+(hour|minute|min|day|second|sec)s?\s+ago", since_str, re.IGNORECASE)
    if m:
        value = int(m.group(1))
        unit = m.group(2).lower()
        if unit in ("hour",):
            delta = datetime.timedelta(hours=value)
        elif unit in ("minute", "min"):
            delta = datetime.timedelta(minutes=value)
        elif unit in ("day",):
            delta = datetime.timedelta(days=value)
        elif unit in ("second", "sec"):
            delta = datetime.timedelta(seconds=value)
        else:
            delta = datetime.timedelta(hours=1)
        return (now - delta).timestamp()

    # Try ISO 8601
    for fmt in ("%Y-%m-%dT%H:%M:%S", "%Y-%m-%d %H:%M:%S", "%Y-%m-%d"):
        try:
            return datetime.datetime.strptime(since_str, fmt).timestamp()
        except ValueError:
            continue

    # Try raw float
    try:
        return float(since_str)
    except ValueError:
        pass

    print(f"ERROR: Cannot parse --since value: {since_str!r}", file=sys.stderr)
    sys.exit(2)


# ── Semantic consistency checks ────────────────────────────────────────────────

def check_task_result_alignment(event: dict) -> list[str]:
    """Check if result_json semantically references concepts from task_description / params_json."""
    anomalies = []
    task_desc = (event.get("task_description") or "").lower()
    params_raw = event.get("params_json") or "{}"
    result_raw = event.get("result_json") or "{}"

    try:
        params = json.loads(params_raw) if isinstance(params_raw, str) else params_raw
    except (json.JSONDecodeError, TypeError):
        params = {}
    try:
        result = json.loads(result_raw) if isinstance(result_raw, str) else result_raw
    except (json.JSONDecodeError, TypeError):
        result = {}

    # Heuristic 1: If task_description mentions a specific file/script, result should reference it
    file_patterns = re.findall(r'[\w/\\]+\.(?:py|md|json|yaml|yml|sh|toml)', task_desc)
    if file_patterns:
        result_str = json.dumps(result).lower() if isinstance(result, dict) else str(result).lower()
        for fp in file_patterns:
            base = os.path.basename(fp).lower()
            if base not in result_str and fp.lower() not in result_str:
                anomalies.append(
                    f"TASK_FILE_NOT_IN_RESULT: task mentions '{fp}' but result_json does not reference it"
                )

    # Heuristic 2: Decision-result coherence — if decision is "deny" but result says "success"
    decision = (event.get("decision") or "").lower()
    result_str_lower = json.dumps(result).lower() if isinstance(result, dict) else str(result).lower()
    if decision == "deny" and any(w in result_str_lower for w in ("success", "completed", "approved", "shipped")):
        anomalies.append(
            f"DENY_BUT_SUCCESS: decision=deny yet result contains success-family word"
        )

    # Heuristic 3: Empty result for substantive task
    if isinstance(result, dict) and len(result) == 0 and len(task_desc) > 20:
        anomalies.append(
            f"EMPTY_RESULT_SUBSTANTIVE_TASK: task_description is {len(task_desc)} chars but result_json is empty dict"
        )

    # Heuristic 4: params_json references an agent, but result_json references a different agent
    params_str = json.dumps(params).lower() if isinstance(params, dict) else str(params).lower()
    known_agents = ["leo", "maya", "ryan", "jordan", "ethan", "aiden", "sofia", "marco", "zara", "samantha"]
    params_agents = [a for a in known_agents if a in params_str]
    result_agents = [a for a in known_agents if a in result_str_lower]
    if params_agents and result_agents:
        # If params mention agent X but result only mentions agent Y (and X not in Y set)
        params_only = set(params_agents) - set(result_agents)
        if params_only and len(params_agents) <= 2:
            # Only flag if params mentioned 1-2 agents and result has none of them
            if not set(params_agents) & set(result_agents):
                anomalies.append(
                    f"AGENT_MISMATCH: params references {params_agents} but result references {result_agents}"
                )

    # Heuristic 5: Suspiciously short result for long params
    if len(params_raw) > 500 and len(result_raw) < 20:
        anomalies.append(
            f"DISPROPORTIONATE_RESULT: params_json is {len(params_raw)} bytes but result_json is only {len(result_raw)} bytes"
        )

    return anomalies


def check_temporal_consistency(event: dict) -> list[str]:
    """Check for temporal anomalies in the event."""
    anomalies = []

    created_at = event.get("created_at")
    if created_at:
        now = datetime.datetime.utcnow().timestamp()
        if created_at > now + 3600:  # More than 1 hour in the future
            anomalies.append(
                f"FUTURE_EVENT: created_at is {(created_at - now)/3600:.1f} hours in the future"
            )
        if created_at < 1700000000:  # Before ~Nov 2023
            anomalies.append(
                f"ANCIENT_EVENT: created_at {created_at} predates Y*gov existence"
            )

    return anomalies


def check_violation_consistency(event: dict) -> list[str]:
    """If passed=0 but violations is empty/null, or passed=1 but violations non-empty."""
    anomalies = []
    passed = event.get("passed", 0)
    violations_raw = event.get("violations")

    violations = []
    if violations_raw:
        try:
            violations = json.loads(violations_raw) if isinstance(violations_raw, str) else violations_raw
        except (json.JSONDecodeError, TypeError):
            violations = []

    if passed == 0 and isinstance(violations, list) and len(violations) > 0:
        # This is actually expected — passed=0 with violations is normal
        pass
    if passed == 1 and isinstance(violations, list) and len(violations) > 0:
        anomalies.append(
            f"PASSED_WITH_VIOLATIONS: passed=1 but violations array has {len(violations)} entries"
        )

    return anomalies


# ── Main audit logic ───────────────────────────────────────────────────────────

def run_audit(db_path: str, sample_rate: float, since: float, agent_filter: str | None) -> tuple[list[dict], int, int]:
    """
    Run the sampling audit.

    Returns: (anomalies_list, total_candidates, sampled_count)
    """
    if not os.path.exists(db_path):
        print(f"ERROR: CIEU database not found at {db_path}", file=sys.stderr)
        sys.exit(2)

    # Open read-only
    uri = f"file:{db_path}?mode=ro"
    conn = sqlite3.connect(uri, uri=True)
    conn.row_factory = sqlite3.Row

    # Build query
    query = """
        SELECT event_id, agent_id, event_type, decision, passed,
               created_at, file_path, task_description,
               params_json, result_json, violations,
               drift_detected, drift_details
        FROM cieu_events
        WHERE created_at > ?
    """
    params = [since]

    if agent_filter:
        query += " AND LOWER(agent_id) LIKE ?"
        params.append(f"%{agent_filter.lower()}%")

    # Only sample events with substantive data (params or result populated)
    query += " AND (params_json IS NOT NULL OR result_json IS NOT NULL)"
    query += " ORDER BY created_at DESC"

    cursor = conn.execute(query, params)
    all_candidates = [dict(row) for row in cursor.fetchall()]
    conn.close()

    total_candidates = len(all_candidates)
    if total_candidates == 0:
        return [], 0, 0

    # Sample
    sample_size = max(1, int(total_candidates * sample_rate))
    sample_size = min(sample_size, total_candidates)
    sampled = random.sample(all_candidates, sample_size)

    # Run checks on each sampled event
    all_anomalies = []
    for event in sampled:
        event_anomalies = []
        event_anomalies.extend(check_task_result_alignment(event))
        event_anomalies.extend(check_temporal_consistency(event))
        event_anomalies.extend(check_violation_consistency(event))

        if event_anomalies:
            all_anomalies.append({
                "event_id": event["event_id"],
                "agent_id": event["agent_id"],
                "event_type": event["event_type"],
                "decision": event["decision"],
                "created_at": event["created_at"],
                "anomalies": event_anomalies,
            })

    return all_anomalies, total_candidates, sample_size


def write_report(anomalies: list[dict], total: int, sampled: int,
                 sample_rate: float, since_str: str, agent_filter: str | None) -> str:
    """Write audit report to reports/cto/k9_sample_audits/audit_<ISO>.md. Returns path."""
    os.makedirs(REPORT_DIR, exist_ok=True)
    now_iso = datetime.datetime.utcnow().strftime("%Y%m%dT%H%M%SZ")
    report_path = os.path.join(REPORT_DIR, f"audit_{now_iso}.md")

    lines = [
        f"# K9 Sample Audit Report — {now_iso}",
        "",
        "## Parameters",
        f"- Sample rate: {sample_rate:.0%}",
        f"- Since: {since_str}",
        f"- Agent filter: {agent_filter or 'none'}",
        f"- Total candidates (with params/result): {total}",
        f"- Sampled: {sampled}",
        f"- Anomalies found: {len(anomalies)}",
        "",
    ]

    if not anomalies:
        lines.append("## Result: CLEAN")
        lines.append("")
        lines.append("No semantic inconsistencies detected in sampled events.")
    else:
        lines.append("## Anomalies Detected")
        lines.append("")
        for i, a in enumerate(anomalies, 1):
            created_iso = ""
            if a.get("created_at"):
                try:
                    created_iso = datetime.datetime.utcfromtimestamp(a["created_at"]).strftime("%Y-%m-%d %H:%M:%S UTC")
                except (OSError, ValueError):
                    created_iso = str(a["created_at"])
            lines.append(f"### Anomaly {i}")
            lines.append(f"- **event_id**: `{a['event_id']}`")
            lines.append(f"- **agent_id**: `{a['agent_id']}`")
            lines.append(f"- **event_type**: `{a['event_type']}`")
            lines.append(f"- **decision**: `{a['decision']}`")
            lines.append(f"- **created_at**: {created_iso}")
            lines.append(f"- **findings**:")
            for finding in a["anomalies"]:
                lines.append(f"  - {finding}")
            lines.append("")

    lines.append("---")
    lines.append(f"*Generated by k9_sample_audit.py at {now_iso}. K9 is a pure reader — no CIEU writes.*")

    with open(report_path, "w") as f:
        f.write("\n".join(lines) + "\n")

    return report_path


# ── CLI ────────────────────────────────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser(
        description="K9 Tier 2 Sampling Audit — semantic consistency checks on CIEU events",
        epilog="K9 is a PURE READER. This script NEVER writes to .ystar_cieu.db.",
    )
    parser.add_argument(
        "--sample-rate", type=float, default=0.2,
        help="Fraction of candidate events to sample (0.0-1.0, default 0.2 = 20%%)",
    )
    parser.add_argument(
        "--since", type=str, default="1 hour ago",
        help='Time window start. Examples: "1 hour ago", "30 minutes ago", "2026-04-23T12:00:00"',
    )
    parser.add_argument(
        "--agent-filter", type=str, default=None,
        help="Filter events by agent_id substring (case-insensitive). Example: ryan",
    )
    parser.add_argument(
        "--db-path", type=str, default=DEFAULT_DB,
        help=f"Path to CIEU database (default: {DEFAULT_DB})",
    )
    parser.add_argument(
        "--json", action="store_true",
        help="Output summary as JSON to stdout (in addition to report file)",
    )
    args = parser.parse_args()

    if not 0.0 < args.sample_rate <= 1.0:
        print("ERROR: --sample-rate must be between 0.0 (exclusive) and 1.0 (inclusive)", file=sys.stderr)
        sys.exit(2)

    since_ts = parse_since(args.since)
    anomalies, total, sampled = run_audit(args.db_path, args.sample_rate, since_ts, args.agent_filter)

    # Write report
    report_path = write_report(anomalies, total, sampled, args.sample_rate, args.since, args.agent_filter)

    # Summary output
    summary = {
        "report_path": report_path,
        "total_candidates": total,
        "sampled": sampled,
        "sample_rate": args.sample_rate,
        "anomalies_count": len(anomalies),
        "anomaly_event_ids": [a["event_id"] for a in anomalies],
        "clean": len(anomalies) == 0,
    }

    if args.json:
        print(json.dumps(summary, indent=2))
    else:
        print(f"K9 Sample Audit Complete")
        print(f"  Candidates: {total}")
        print(f"  Sampled: {sampled} ({args.sample_rate:.0%})")
        print(f"  Anomalies: {len(anomalies)}")
        print(f"  Report: {report_path}")

    if anomalies:
        sys.exit(1)  # Anomalies found
    else:
        sys.exit(0)  # Clean


if __name__ == "__main__":
    main()
