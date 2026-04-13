#!/usr/bin/env python3
"""
whitelist_coverage.py — A018 Phase 1 sync mechanism C覆盖率计算器

计算给定时间窗口内，governance/whitelist/ 白名单条目在 CIEU 数据库中的覆盖率。

覆盖率定义：
    (匹配到白名单 cieu_markers 的 hook event count) / (总 hook event count)

用途：
    - 验证白名单是否真正覆盖现有 governance 流程
    - 识别白名单 gap (coverage < 60% 时 emit WHITELIST_GAP CIEU)
    - 为 A018 sync 机制 C 提供量化证据

Created: 2026-04-13 by Maya Patel (eng-platform)
"""

import argparse
import datetime
import sqlite3
import sys
from pathlib import Path
from typing import Dict, List, Set

import yaml


def load_whitelist_entries(whitelist_dir: Path) -> Dict[str, List[str]]:
    """
    从 governance/whitelist/*.yaml 加载所有白名单条目的 cieu_markers。

    返回:
        {
            "SOP-001": ["INTENT_DECLARED", "INTENT_COMPLETED"],
            "RAPID-001": ["INTENT_DECLARED", "INTENT_COMPLETED"],
            ...
        }
    """
    entries = {}
    for yaml_file in whitelist_dir.glob("*.yaml"):
        with open(yaml_file, "r", encoding="utf-8") as f:
            data = yaml.safe_load(f)

        if not isinstance(data, dict):
            print(f"[WARN] Skipping {yaml_file.name}: not a dict", file=sys.stderr)
            continue

        if "entries" not in data:
            print(f"[WARN] Skipping {yaml_file.name}: no 'entries' key", file=sys.stderr)
            continue

        if not isinstance(data["entries"], list):
            print(f"[WARN] Skipping {yaml_file.name}: 'entries' is not a list", file=sys.stderr)
            continue

        for entry in data["entries"]:
            entry_id = entry.get("flow_id") or entry.get("decision_type_id")
            cieu_markers = entry.get("cieu_markers", [])

            if entry_id and cieu_markers:
                entries[entry_id] = cieu_markers

    return entries


def query_cieu_events(db_path: Path, start_time: str, end_time: str) -> List[Dict]:
    """
    从 CIEU 数据库查询给定时间窗口内的所有 hook event。

    返回:
        [
            {"event_type": "INTENT_DECLARED", "created_at": 1713024000.0, ...},
            {"event_type": "INTENT_COMPLETED", "created_at": 1713024600.0, ...},
            ...
        ]
    """
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()

    # Convert ISO timestamp to Unix timestamp
    import datetime
    start_unix = datetime.datetime.fromisoformat(start_time).timestamp()
    end_unix = datetime.datetime.fromisoformat(end_time).timestamp()

    query = """
        SELECT event_type, created_at, session_id, agent_id, decision, violations
        FROM cieu_events
        WHERE created_at >= ? AND created_at <= ?
        ORDER BY created_at ASC
    """

    cursor.execute(query, (start_unix, end_unix))
    events = [dict(row) for row in cursor.fetchall()]

    conn.close()
    return events


def calculate_coverage(
    events: List[Dict],
    whitelist_entries: Dict[str, List[str]]
) -> Dict:
    """
    计算白名单覆盖率。

    返回:
        {
            "total_events": 1234,
            "matched_events": 890,
            "coverage_rate": 0.72,
            "matched_by_entry": {
                "SOP-001": 45,
                "RAPID-003": 102,
                ...
            },
            "unmatched_event_types": {"SOME_EVENT": 12, ...}
        }
    """
    total_events = len(events)
    matched_events = 0
    matched_by_entry = {entry_id: 0 for entry_id in whitelist_entries.keys()}
    unmatched_event_types = {}

    # 提取所有白名单 markers
    all_markers = set()
    for markers in whitelist_entries.values():
        all_markers.update(markers)

    for event in events:
        event_type = event["event_type"]

        if event_type in all_markers:
            matched_events += 1

            # 记录到具体 entry
            for entry_id, markers in whitelist_entries.items():
                if event_type in markers:
                    matched_by_entry[entry_id] += 1
        else:
            unmatched_event_types[event_type] = unmatched_event_types.get(event_type, 0) + 1

    coverage_rate = matched_events / total_events if total_events > 0 else 0.0

    return {
        "total_events": total_events,
        "matched_events": matched_events,
        "coverage_rate": coverage_rate,
        "matched_by_entry": matched_by_entry,
        "unmatched_event_types": unmatched_event_types
    }


def emit_whitelist_gap_cieu(db_path: Path, coverage_rate: float):
    """
    如果 coverage < 60%，向 CIEU 数据库 emit WHITELIST_GAP 事件。
    """
    if coverage_rate >= 0.60:
        return

    import uuid

    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    now_unix = datetime.datetime.utcnow().timestamp()
    event_id = str(uuid.uuid4())
    session_id = "whitelist_cron"
    agent_id = "eng-platform"

    violations_json = str({
        "coverage_rate": coverage_rate,
        "threshold": 0.60,
        "severity": "P1",
        "action_required": "Update whitelist YAMLs or investigate unmatched event types"
    })

    cursor.execute(
        """
        INSERT INTO cieu_events (
            event_id, seq_global, created_at, session_id, agent_id, event_type,
            decision, passed, violations, contract_hash
        )
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """,
        (
            event_id,
            int(now_unix * 1_000_000),  # seq_global = μs timestamp
            now_unix,
            session_id,
            agent_id,
            "WHITELIST_GAP",
            "escalate",
            0,  # passed=0 (violation)
            violations_json,
            "whitelist_coverage_v1"
        )
    )

    conn.commit()
    conn.close()

    print(f"[ALERT] WHITELIST_GAP emitted to CIEU: coverage={coverage_rate:.2%}", file=sys.stderr)


def main():
    parser = argparse.ArgumentParser(description="Calculate whitelist coverage from CIEU events")
    parser.add_argument(
        "--db-path",
        type=Path,
        default=Path.home() / ".openclaw/workspace/ystar-company/.ystar_cieu.db",
        help="Path to CIEU database (default: ystar-company/.ystar_cieu.db)"
    )
    parser.add_argument(
        "--whitelist-dir",
        type=Path,
        default=Path.home() / ".openclaw/workspace/ystar-company/governance/whitelist",
        help="Path to whitelist directory (default: governance/whitelist/)"
    )
    parser.add_argument(
        "--start-time",
        type=str,
        default=(datetime.datetime.utcnow() - datetime.timedelta(hours=24)).isoformat(),
        help="Start time (ISO format, default: 24h ago)"
    )
    parser.add_argument(
        "--end-time",
        type=str,
        default=datetime.datetime.utcnow().isoformat(),
        help="End time (ISO format, default: now)"
    )
    parser.add_argument(
        "--emit-gap",
        action="store_true",
        help="Emit WHITELIST_GAP CIEU event if coverage < 60%"
    )
    parser.add_argument(
        "--verbose",
        "-v",
        action="store_true",
        help="Verbose output"
    )

    args = parser.parse_args()

    # 1. Load whitelist entries
    whitelist_entries = load_whitelist_entries(args.whitelist_dir)
    total_entries = len(whitelist_entries)
    total_markers = sum(len(markers) for markers in whitelist_entries.values())

    if args.verbose:
        print(f"Loaded {total_entries} whitelist entries with {total_markers} unique CIEU markers")

    # 2. Query CIEU events
    if not args.db_path.exists():
        print(f"[ERROR] CIEU database not found: {args.db_path}", file=sys.stderr)
        sys.exit(1)

    events = query_cieu_events(args.db_path, args.start_time, args.end_time)

    if args.verbose:
        print(f"Queried {len(events)} CIEU events from {args.start_time} to {args.end_time}")

    # 3. Calculate coverage
    result = calculate_coverage(events, whitelist_entries)

    # 4. Output
    print(f"Coverage Rate: {result['coverage_rate']:.2%}")
    print(f"Total Events: {result['total_events']}")
    print(f"Matched Events: {result['matched_events']}")
    print(f"Unmatched Events: {result['total_events'] - result['matched_events']}")

    if args.verbose:
        print("\n=== Matched by Entry ===")
        for entry_id, count in sorted(result['matched_by_entry'].items(), key=lambda x: -x[1]):
            if count > 0:
                print(f"  {entry_id}: {count}")

        print("\n=== Top 10 Unmatched Event Types ===")
        for event_type, count in sorted(result['unmatched_event_types'].items(), key=lambda x: -x[1])[:10]:
            print(f"  {event_type}: {count}")

    # 5. Emit WHITELIST_GAP if needed
    if args.emit_gap:
        emit_whitelist_gap_cieu(args.db_path, result['coverage_rate'])

    # 6. Exit code
    if result['coverage_rate'] < 0.60:
        sys.exit(1)
    else:
        sys.exit(0)


if __name__ == "__main__":
    main()
