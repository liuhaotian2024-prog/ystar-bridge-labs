#!/usr/bin/env python3
"""Digital Twin Evolution Report - Progress dashboard for Board → CEO evolution

Similar to learning_report.py, aggregates digital twin evolution metrics:
- Board values extracted (YML lessons with tag=board_value)
- CEO capability coverage (theory files vs world-class standard)
- Limitation compensation status (recent 7 days)
- Last evolution activity date

Usage:
    python3 scripts/twin_report.py
"""

import json
import sqlite3
import sys
import time
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
KNOWLEDGE_ROOT = REPO_ROOT / "knowledge"
MEMORY_DB = REPO_ROOT / ".ystar_memory.db"
CIEU_DB = REPO_ROOT / ".ystar_cieu.db"
GEMMA_LOG = KNOWLEDGE_ROOT / "ceo" / "gaps" / "gemma_sessions.log"


def count_board_values() -> int:
    """Count lessons with board_value tag in YML."""
    if not MEMORY_DB.exists():
        return 0

    try:
        conn = sqlite3.connect(MEMORY_DB)
        cursor = conn.execute("""
            SELECT COUNT(*) FROM memories
            WHERE agent_id = 'ceo'
            AND memory_type = 'lesson'
            AND context_tags LIKE '%board_value%'
        """)
        count = cursor.fetchone()[0]
        conn.close()
        return count
    except Exception:
        return 0


def get_capability_coverage() -> tuple:
    """Get CEO theory coverage.

    Returns:
        (theory_count, expected_count, coverage_percentage)
    """
    role_def_dir = KNOWLEDGE_ROOT / "ceo" / "role_definition"
    theory_dir = KNOWLEDGE_ROOT / "ceo" / "theory"

    theory_count = len(list(theory_dir.glob("*.md"))) if theory_dir.exists() else 0

    task_type_map = role_def_dir / "task_type_map.md"
    expected_count = 0
    if task_type_map.exists():
        content = task_type_map.read_text()
        expected_count = content.count("### ")

    coverage_pct = 0
    if expected_count > 0:
        coverage_pct = (theory_count / expected_count) * 100

    return theory_count, expected_count, coverage_pct


def get_limitation_status() -> dict:
    """Get limitation compensation metrics for last 7 days."""
    if not CIEU_DB.exists():
        return {
            "emotional_volatility": 0,
            "unauthorized_dispatches": 0,
            "missing_prechecks": 0
        }

    cutoff_time = time.time() - (7 * 86400)

    try:
        conn = sqlite3.connect(CIEU_DB)

        # Emotional volatility
        cursor = conn.execute("""
            SELECT session_id, COUNT(*) as adjust_count
            FROM cieu_events
            WHERE agent_id IN ('ceo', 'board')
            AND event_type = 'INTENT_ADJUSTED'
            AND created_at >= ?
            GROUP BY session_id
            HAVING adjust_count > 3
        """, (cutoff_time,))
        volatile_sessions = len(cursor.fetchall())

        # Unauthorized dispatches
        cursor = conn.execute("""
            SELECT COUNT(*) FROM cieu_events
            WHERE agent_id IN ('eng-kernel', 'eng-governance', 'eng-platform', 'eng-domains')
            AND created_at >= ?
            AND session_id IN (
                SELECT DISTINCT session_id FROM cieu_events WHERE agent_id = 'ceo'
            )
            AND session_id NOT IN (
                SELECT DISTINCT session_id FROM cieu_events WHERE agent_id = 'cto'
            )
        """, (cutoff_time,))
        unauthorized = cursor.fetchone()[0]

        # Missing prechecks
        cursor = conn.execute("""
            SELECT event_id, session_id, created_at
            FROM cieu_events
            WHERE agent_id = 'ceo'
            AND event_type = 'INTENT_DECLARED'
            AND created_at >= ?
        """, (cutoff_time,))

        intent_events = cursor.fetchall()
        missing_precheck = 0

        for event_id, session_id, created_at in intent_events:
            precheck_cursor = conn.execute("""
                SELECT COUNT(*) FROM cieu_events
                WHERE session_id = ?
                AND created_at < ?
                AND (task_description LIKE '%gov_check%' OR task_description LIKE '%gov_precheck%')
            """, (session_id, created_at))

            if precheck_cursor.fetchone()[0] == 0:
                missing_precheck += 1

        conn.close()

        return {
            "emotional_volatility": volatile_sessions,
            "unauthorized_dispatches": unauthorized,
            "missing_prechecks": missing_precheck
        }
    except Exception:
        return {
            "emotional_volatility": 0,
            "unauthorized_dispatches": 0,
            "missing_prechecks": 0
        }


def get_last_evolution_date() -> str:
    """Get date of last twin evolution activity.

    Reads gemma_sessions.log for most recent twin_evolution entry.

    Returns:
        "YYYY-MM-DD" or "Never"
    """
    if not GEMMA_LOG.exists():
        return "Never"

    try:
        last_timestamp = None
        with open(GEMMA_LOG, "r") as f:
            for line in f:
                try:
                    entry = json.loads(line.strip())
                    if entry.get("mode") == "twin_evolution":
                        ts = entry.get("timestamp", 0)
                        if last_timestamp is None or ts > last_timestamp:
                            last_timestamp = ts
                except json.JSONDecodeError:
                    continue

        if last_timestamp:
            return time.strftime("%Y-%m-%d", time.localtime(last_timestamp))
        else:
            return "Never"
    except Exception:
        return "Never"


def main():
    print("=== Digital Twin Evolution Report ===\n")

    # Board values extraction
    board_values = count_board_values()
    print(f"Board价值观已提取: {board_values}条 (YML中tag=board_value的lesson)")

    # CEO capability coverage
    theory_count, expected_count, coverage_pct = get_capability_coverage()
    print(f"CEO能力覆盖率: {theory_count}/{expected_count} theory files ({coverage_pct:.0f}%)")

    # Limitation compensation status
    limitations = get_limitation_status()
    print("\n局限补偿状态 (最近7天):")
    print(f"  情绪波动检测: {limitations['emotional_volatility']}次异常 / 阈值 3")
    print(f"  越权指挥检测: {limitations['unauthorized_dispatches']}次 / 阈值 0")
    print(f"  无预检决策: {limitations['missing_prechecks']}次 / 阈值 2")

    # Overall status
    print("\n总体评估:")
    total_violations = (
        limitations['emotional_volatility'] +
        limitations['unauthorized_dispatches'] +
        limitations['missing_prechecks']
    )

    if total_violations == 0:
        print("  ✓ CEO运行状态良好 - 未检测到Board的已知局限")
    else:
        print(f"  ⚠ 检测到 {total_violations} 项局限表现 - 建议加强补偿机制")

    # Last evolution date
    last_date = get_last_evolution_date()
    print(f"\n最后进化日期: {last_date}")

    if last_date == "Never":
        print("\n建议: 运行 python3 scripts/twin_evolution.py --mode all 启动数字分身进化")

    return 0


if __name__ == "__main__":
    sys.exit(main())
