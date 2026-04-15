#!/usr/bin/env python3
"""
K9 CausalChainAnalyzer bridge for CIEU events.

Exports CIEU DB events to K9-compatible JSONL format.
Resolves violations TEXT → list[dict] schema mismatch (K9 causal_analyzer.py:243).

Author: Leo Chen (leo-kernel), dispatched by CEO 2026-04-15
License: MIT (Y* Bridge Labs)
"""
import json
import sqlite3
import sys
from pathlib import Path
from typing import Any, Dict, List, Optional


def parse_violations(violations_text: Optional[str]) -> List[Dict[str, Any]]:
    """Parse CIEU violations TEXT column → K9-compatible list[dict]."""
    if not violations_text or violations_text == "[]":
        return []

    try:
        raw = json.loads(violations_text)
        if not isinstance(raw, list):
            return []

        # Map CIEU schema to K9 expectations
        result = []
        for v in raw:
            if not isinstance(v, dict):
                continue

            # Infer severity from dimension/message
            dimension = v.get("dimension", "")
            message = v.get("message", "")

            severity = 0.5  # default
            if dimension == "deny":
                severity = 0.9
            elif dimension == "escalate":
                severity = 0.7
            elif "forbidden" in message.lower() or "not allowed" in message.lower():
                severity = 0.8

            result.append({
                "dimension": dimension,
                "message": message,
                "severity": severity,
                **{k: v for k, v in v.items() if k not in ("dimension", "message")}
            })

        return result

    except json.JSONDecodeError:
        return []


def export_cieu_to_k9_jsonl(
    db_path: str,
    output_path: str,
    limit: int = 1000
) -> int:
    """Export CIEU events to K9-compatible JSONL.

    Returns:
        Number of events exported.
    """
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()

    # Query: select events with violations or high chain_depth
    query = """
        SELECT
            rowid,
            created_at,
            agent_id,
            event_type,
            decision,
            violations,
            chain_depth,
            file_path,
            command,
            task_description,
            contract_hash
        FROM cieu_events
        WHERE violations IS NOT NULL OR chain_depth > 0
        ORDER BY created_at DESC
        LIMIT ?
    """

    cursor.execute(query, (limit,))
    rows = cursor.fetchall()

    events = []
    for idx, row in enumerate(rows):
        violations = parse_violations(row["violations"])

        # K9 expected format
        # IMPORTANT: K9 uses step as 0-indexed array index, not DB rowid
        event = {
            "step": idx,  # Sequential index for K9 DAG
            "timestamp": row["created_at"],
            "skill": row["event_type"] or "unknown",
            "agent": row["agent_id"],
            "violations": violations,
            "extras": {
                "decision": row["decision"],
                "chain_depth": row["chain_depth"] or 0,
                "file_path": row["file_path"],
                "command": row["command"],
                "task_description": row["task_description"],
                "contract_hash": row["contract_hash"],
                "cieu_rowid": row["rowid"]  # Keep original rowid for reference
            }
        }
        events.append(event)

    conn.close()

    # Write JSONL
    with open(output_path, "w") as f:
        for event in events:
            f.write(json.dumps(event) + "\n")

    return len(events)


def main():
    # Default paths
    db_path = "/Users/haotianliu/.openclaw/workspace/ystar-company/.ystar_cieu.db"
    output_path = "/tmp/cieu_k9_export.jsonl"

    if len(sys.argv) > 1:
        db_path = sys.argv[1]
    if len(sys.argv) > 2:
        output_path = sys.argv[2]

    count = export_cieu_to_k9_jsonl(db_path, output_path)
    print(f"✓ Exported {count} CIEU events to {output_path}")

    # Inline test: load in K9 analyzer stub
    print("\n=== INLINE TEST: Load in K9 stub ===")
    with open(output_path) as f:
        events = [json.loads(line) for line in f]

    print(f"Events loaded: {len(events)}")

    # Simulate K9 causal_analyzer.py:243 access pattern
    violations_in_chain = [e for e in events if e.get("violations")]
    print(f"Events with violations: {len(violations_in_chain)}")

    if violations_in_chain:
        test_event = violations_in_chain[0]
        print(f"\nTest event (step {test_event['step']}):")
        print(f"  Skill: {test_event['skill']}")
        print(f"  Violations: {len(test_event['violations'])}")

        # K9 line 243: v.get('severity', 0)
        for v in test_event["violations"]:
            severity = v.get("severity", 0)
            print(f"    - {v.get('dimension', 'unknown')}: {v.get('message', '')} (severity={severity})")

        print("\n✓ K9 severity access pattern works (no TypeError)")
    else:
        print("⚠ No violations found in export (check CIEU DB data)")

    return 0


if __name__ == "__main__":
    sys.exit(main())
