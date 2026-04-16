#!/usr/bin/env python3
"""Digital Twin Evolution - Board's decision principles → CEO's governing DNA

Mirrors idle_learning.py architecture for Board's digital twin evolution.

Three modes:

1. extract-values: Extract Board decision principles from CIEU events
   - Scans CIEU for agent_id="board" INTENT_CONFIRMED/INTENT_ADJUSTED events
   - Extracts decision rationale from event details
   - Writes to YML as lessons (memory_type="lesson", half_life_days=365)
   - Deduplicates against existing board_value lessons

2. capability-gap: Analyze CEO capability coverage vs world-class standard
   - Reads knowledge/ceo/role_definition/world_class_standard.md
   - Counts knowledge/ceo/theory/*.md files
   - Calculates coverage percentage
   - Outputs gap analysis

3. compensation-check: Detect Board's known limitations in CEO's recent behavior
   - Emotional volatility → High INTENT_ADJUSTED frequency in single session
   - Systemic management weakness → CEO dispatching to engineers without CTO authorization
   - Intuition over analysis → Decisions without gov_precheck
   - Writes gap memories + recommendations

Usage:
    python3 scripts/twin_evolution.py --mode extract-values
    python3 scripts/twin_evolution.py --mode capability-gap
    python3 scripts/twin_evolution.py --mode compensation-check
    python3 scripts/twin_evolution.py --mode all
"""

import argparse
import json
import sqlite3
import sys
import time
import uuid
from pathlib import Path
from typing import List, Dict, Set
sys.path.insert(0, str(Path(__file__).parent))
from _cieu_helpers import _get_current_agent

# Add Y-star-gov to path
YSTAR_GOV_PATH = Path(__file__).parent.parent.parent / "Y-star-gov"
if YSTAR_GOV_PATH.exists():
    sys.path.insert(0, str(YSTAR_GOV_PATH))

REPO_ROOT = Path(__file__).resolve().parent.parent
KNOWLEDGE_ROOT = REPO_ROOT / "knowledge"
CIEU_DB = REPO_ROOT / ".ystar_cieu.db"
MEMORY_DB = REPO_ROOT / ".ystar_memory.db"
GEMMA_LOG = KNOWLEDGE_ROOT / "ceo" / "gaps" / "gemma_sessions.log"

# Board's self-described limitations (from Board's self-assessment)
BOARD_LIMITATIONS = {
    "emotional_volatility": {
        "description": "情绪波动大 - 同一session内决策反复调整",
        "threshold": 3,  # More than 3 INTENT_ADJUSTED in one session
        "detector": "intent_adjusted_frequency"
    },
    "systemic_management_gap": {
        "description": "管理系统性不足 - 直接指挥工程师跳过CTO",
        "threshold": 0,  # Any dispatch without authority is violation
        "detector": "unauthorized_dispatch"
    },
    "intuition_over_analysis": {
        "description": "直觉优于分析 - 决策前无gov_precheck记录",
        "threshold": 2,  # More than 2 decisions without precheck in 7 days
        "detector": "missing_precheck"
    }
}


def write_gemma_log(mode: str, action: str, result: dict):
    """Write JSONL entry to gemma_sessions.log."""
    GEMMA_LOG.parent.mkdir(parents=True, exist_ok=True)

    entry = {
        "timestamp": time.time(),
        "actor": "ceo",
        "mode": "twin_evolution",
        "submode": mode,
        "action": action,
        "result": result,
    }

    with open(GEMMA_LOG, "a") as f:
        f.write(json.dumps(entry) + "\n")


def write_cieu_event(mode: str, action: str, outcome: str, details: dict = None):
    """Write CIEU event for twin evolution execution."""
    if not CIEU_DB.exists():
        return

    event_id = str(uuid.uuid4())
    seq_global = int(time.time() * 1_000_000)

    conn = sqlite3.connect(CIEU_DB)
    conn.execute("""
        INSERT INTO cieu_events (
            event_id, seq_global, created_at, session_id, agent_id, event_type,
            decision, passed, task_description, params_json
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        event_id,
        seq_global,
        time.time(),
        "twin_evolution",
        "ceo",
        "TWIN_EVOLUTION",
        "allow",
        1,
        f"{mode}: {action}",
        json.dumps({
            "mode": mode,
            "action": action,
            "outcome": outcome,
            "details": details or {}
        })
    ))
    conn.commit()
    conn.close()


def get_existing_board_values() -> Set[str]:
    """Get existing board_value lessons from YML to avoid duplicates.

    Returns set of normalized lesson content strings.
    """
    if not MEMORY_DB.exists():
        return set()

    try:
        from ystar.memory import MemoryStore
        store = MemoryStore(db_path=str(MEMORY_DB))

        # Query memories with board_value tag
        existing_lessons = set()

        # Direct SQL query for efficiency
        conn = sqlite3.connect(MEMORY_DB)
        cursor = conn.execute("""
            SELECT content FROM memories
            WHERE agent_id=_get_current_agent()
            AND memory_type = 'lesson'
            AND context_tags LIKE '%board_value%'
        """)

        for row in cursor.fetchall():
            # Normalize: lowercase, strip whitespace
            normalized = row[0].lower().strip()
            existing_lessons.add(normalized)

        conn.close()
        return existing_lessons
    except Exception:
        return set()


def extract_board_values() -> dict:
    """Mode 1: Extract Board decision principles from CIEU.

    Returns:
        {"total_events": int, "lessons_extracted": int, "duplicates_skipped": int}
    """
    if not CIEU_DB.exists():
        return {
            "total_events": 0,
            "lessons_extracted": 0,
            "duplicates_skipped": 0,
            "error": "CIEU database not found"
        }

    conn = sqlite3.connect(CIEU_DB)

    # Find Board's participation events
    cursor = conn.execute("""
        SELECT event_id, event_type, created_at, task_description, params_json, result_json
        FROM cieu_events
        WHERE agent_id = 'board'
        AND event_type IN ('INTENT_CONFIRMED', 'INTENT_ADJUSTED', 'DIRECTIVE_REJECTED', 'GOV_ORDER')
        ORDER BY created_at DESC
        LIMIT 100
    """)

    existing_values = get_existing_board_values()
    lessons_to_write = []
    duplicates = 0

    for row in cursor.fetchall():
        event_id, event_type, created_at, task_desc, params_json, result_json = row

        # Extract principle from event details
        principle = None

        if event_type == "INTENT_CONFIRMED":
            # Board confirmed a decision - extract the confirmation rationale
            try:
                params = json.loads(params_json) if params_json else {}
                # Expanded fallback chain to cover all Board event metadata fields
                principle = (
                    params.get("confirmation_reason") or
                    params.get("rationale") or
                    (json.loads(result_json).get("rationale") if result_json else None) or
                    (json.loads(result_json).get("reason") if result_json else None) or
                    task_desc or
                    params.get("notes") or  # Board INTENT_CONFIRMED typically uses notes field
                    params.get("status") or
                    params.get("decision")
                )
            except json.JSONDecodeError:
                pass

        elif event_type == "INTENT_ADJUSTED":
            # Board adjusted CEO's intent - this is a learning moment
            try:
                params = json.loads(params_json) if params_json else {}
                original = params.get("original_intent", "")
                adjusted = params.get("adjusted_intent", "")
                reason = params.get("reason", "")

                if original and adjusted and reason:
                    principle = f"Board adjusted: {original} → {adjusted}. Reason: {reason}"
            except json.JSONDecodeError:
                pass

        elif event_type == "DIRECTIVE_REJECTED":
            # Board rejected a directive - critical lesson
            try:
                params = json.loads(params_json) if params_json else {}
                directive = params.get("directive_id", "unknown")
                reason = params.get("reason", "Not aligned with governance")
                principle = f"Board rejected directive {directive}: {reason}"
            except json.JSONDecodeError:
                pass

        elif event_type == "GOV_ORDER":
            # High-severity governance order
            try:
                params = json.loads(params_json) if params_json else {}
                severity = params.get("severity", "").upper()
                if severity in ["HIGH", "CRITICAL"]:
                    order_content = params.get("order", "")
                    if order_content:
                        principle = f"Board issued {severity} order: {order_content}"
            except json.JSONDecodeError:
                pass

        if principle:
            # Check for duplicates
            normalized = principle.lower().strip()
            if normalized in existing_values:
                duplicates += 1
                continue

            lessons_to_write.append({
                "principle": principle,
                "source_event": event_type,
                "source_cieu_id": event_id,
                "timestamp": created_at
            })
            existing_values.add(normalized)  # Prevent duplicates within this run

    conn.close()

    # Write lessons to YML
    lessons_written = 0
    if lessons_to_write:
        try:
            from ystar.memory import MemoryStore, Memory
            store = MemoryStore(db_path=str(MEMORY_DB))

            for lesson_data in lessons_to_write:
                mem = Memory(
                    agent_id=_get_current_agent(),
                    memory_type="lesson",
                    content=lesson_data["principle"],
                    initial_score=1.0,
                    half_life_days=365,  # Board values decay very slowly (1 year)
                    context_tags=["board_value", "digital_twin", f"source:{lesson_data['source_event']}"],
                    metadata={
                        "source_cieu_id": lesson_data["source_cieu_id"],
                        "import_time": time.time(),
                        "original_timestamp": lesson_data["timestamp"]
                    }
                )
                store.remember(mem)
                lessons_written += 1
        except Exception as e:
            return {
                "total_events": len(lessons_to_write) + duplicates,
                "lessons_extracted": lessons_written,
                "duplicates_skipped": duplicates,
                "error": str(e)
            }

    return {
        "total_events": len(lessons_to_write) + duplicates,
        "lessons_extracted": lessons_written,
        "duplicates_skipped": duplicates
    }


def capability_gap_analysis() -> dict:
    """Mode 2: Analyze CEO capability coverage vs world-class standard.

    Returns:
        {"standard_exists": bool, "theory_count": int, "coverage_notes": str}
    """
    role_def_dir = KNOWLEDGE_ROOT / "ceo" / "role_definition"
    theory_dir = KNOWLEDGE_ROOT / "ceo" / "theory"

    standard_file = role_def_dir / "world_class_standard.md"
    standard_exists = standard_file.exists()

    theory_files = list(theory_dir.glob("*.md")) if theory_dir.exists() else []
    theory_count = len(theory_files)

    # Read task_type_map to understand expected theory coverage
    task_type_map = role_def_dir / "task_type_map.md"
    expected_theories = 0
    if task_type_map.exists():
        # Count task types (simplified - count ### headers)
        content = task_type_map.read_text()
        expected_theories = content.count("### ")

    coverage_pct = 0
    if expected_theories > 0:
        coverage_pct = (theory_count / expected_theories) * 100

    coverage_notes = []
    if not standard_exists:
        coverage_notes.append("world_class_standard.md missing - CEO lacks performance benchmark")

    if theory_count == 0:
        coverage_notes.append("No theory entries - CEO operating without documented principles")
    elif coverage_pct < 50:
        coverage_notes.append(f"Theory coverage {coverage_pct:.0f}% - significant gaps in CEO knowledge")

    return {
        "standard_exists": standard_exists,
        "theory_count": theory_count,
        "expected_theories": expected_theories,
        "coverage_percentage": coverage_pct,
        "coverage_notes": coverage_notes
    }


def compensation_check(lookback_days: int = 7) -> dict:
    """Mode 3: Check if CEO exhibits Board's known limitations.

    Args:
        lookback_days: How many days back to analyze

    Returns:
        {"limitations_detected": List[str], "recommendations": List[str]}
    """
    if not CIEU_DB.exists():
        return {
            "limitations_detected": [],
            "recommendations": [],
            "error": "CIEU database not found"
        }

    cutoff_time = time.time() - (lookback_days * 86400)

    conn = sqlite3.connect(CIEU_DB)

    # Check 1: Emotional volatility (INTENT_ADJUSTED frequency per session)
    cursor = conn.execute("""
        SELECT session_id, COUNT(*) as adjust_count
        FROM cieu_events
        WHERE agent_id IN ('ceo', 'board')
        AND event_type = 'INTENT_ADJUSTED'
        AND created_at >= ?
        GROUP BY session_id
        HAVING adjust_count > ?
    """, (cutoff_time, BOARD_LIMITATIONS["emotional_volatility"]["threshold"]))

    volatile_sessions = cursor.fetchall()

    # Check 2: Unauthorized dispatch (CEO dispatching to engineers without CTO)
    # Look for eng-* agent_id in events where CEO is initiator
    cursor = conn.execute("""
        SELECT COUNT(*) as unauthorized_count
        FROM cieu_events
        WHERE agent_id IN ('eng-kernel', 'eng-governance', 'eng-platform', 'eng-domains')
        AND created_at >= ?
        AND session_id IN (
            SELECT DISTINCT session_id FROM cieu_events WHERE agent_id=_get_current_agent()
        )
        AND session_id NOT IN (
            SELECT DISTINCT session_id FROM cieu_events WHERE agent_id = 'cto'
        )
    """, (cutoff_time,))

    unauthorized_count = cursor.fetchone()[0]

    # Check 3: Missing precheck (INTENT_DECLARED without prior gov_check)
    cursor = conn.execute("""
        SELECT event_id, session_id, created_at
        FROM cieu_events
        WHERE agent_id=_get_current_agent()
        AND event_type = 'INTENT_DECLARED'
        AND created_at >= ?
    """, (cutoff_time,))

    intent_events = cursor.fetchall()
    missing_precheck_count = 0

    for event_id, session_id, created_at in intent_events:
        # Check if there was a gov_check/gov_precheck before this intent
        precheck_cursor = conn.execute("""
            SELECT COUNT(*) FROM cieu_events
            WHERE session_id = ?
            AND created_at < ?
            AND (task_description LIKE '%gov_check%' OR task_description LIKE '%gov_precheck%')
        """, (session_id, created_at))

        if precheck_cursor.fetchone()[0] == 0:
            missing_precheck_count += 1

    conn.close()

    # Analyze results
    limitations_detected = []
    recommendations = []

    if volatile_sessions:
        limitations_detected.append(
            f"Emotional volatility: {len(volatile_sessions)} sessions with excessive intent adjustments"
        )
        recommendations.append(
            "Recommendation: Implement cooling-off period before major decisions. "
            "CEO should draft decisions and wait 1 hour before finalizing."
        )

    if unauthorized_count > BOARD_LIMITATIONS["systemic_management_gap"]["threshold"]:
        limitations_detected.append(
            f"Systemic management gap: {unauthorized_count} unauthorized engineer dispatches (bypassing CTO)"
        )
        recommendations.append(
            "Recommendation: Enforce chain of command. All engineering tasks must route through CTO. "
            "Add governance rule: CEO cannot dispatch to eng-* without CTO approval."
        )

    if missing_precheck_count > BOARD_LIMITATIONS["intuition_over_analysis"]["threshold"]:
        limitations_detected.append(
            f"Intuition over analysis: {missing_precheck_count} decisions without gov_precheck"
        )
        recommendations.append(
            "Recommendation: Make gov_precheck mandatory before INTENT_DECLARED. "
            "Add pre-commit hook to enforce governance checks."
        )

    # Write gap memories if limitations detected
    if limitations_detected:
        try:
            from ystar.memory import MemoryStore, Memory
            store = MemoryStore(db_path=str(MEMORY_DB))

            for limitation in limitations_detected:
                mem = Memory(
                    agent_id=_get_current_agent(),
                    memory_type="gap",
                    content=f"[Board Limitation Detected] {limitation}",
                    initial_score=1.0,
                    half_life_days=30,  # Gap memories decay faster - need to demonstrate improvement
                    context_tags=["limitation_compensation", "board_weakness", "auto_detected"],
                    metadata={
                        "detection_time": time.time(),
                        "lookback_days": lookback_days
                    }
                )
                store.remember(mem)
        except Exception:
            pass

    return {
        "limitations_detected": limitations_detected,
        "recommendations": recommendations,
        "metrics": {
            "volatile_sessions": len(volatile_sessions),
            "unauthorized_dispatches": unauthorized_count,
            "missing_prechecks": missing_precheck_count
        }
    }


def main():
    parser = argparse.ArgumentParser(description="Digital Twin Evolution - Board → CEO")
    parser.add_argument(
        "--mode",
        required=True,
        choices=["extract-values", "capability-gap", "compensation-check", "all"],
        help="Evolution mode to execute"
    )
    args = parser.parse_args()

    modes = []
    if args.mode == "all":
        modes = ["extract-values", "capability-gap", "compensation-check"]
    else:
        modes = [args.mode]

    results = {}

    for mode in modes:
        print(f"\n=== Digital Twin Evolution: {mode} ===")

        if mode == "extract-values":
            result = extract_board_values()
            action = "board_value_extraction"

            if "error" in result:
                print(f"Error: {result['error']}")
                outcome = f"failed: {result['error']}"
            else:
                print(f"Total Board events analyzed: {result['total_events']}")
                print(f"New lessons extracted: {result['lessons_extracted']}")
                print(f"Duplicates skipped: {result['duplicates_skipped']}")
                outcome = f"{result['lessons_extracted']} new lessons extracted"

        elif mode == "capability-gap":
            result = capability_gap_analysis()
            action = "ceo_capability_gap"

            print(f"World-class standard exists: {result['standard_exists']}")
            print(f"Theory entries: {result['theory_count']}/{result['expected_theories']}")
            print(f"Coverage: {result['coverage_percentage']:.0f}%")

            if result['coverage_notes']:
                print("\nGaps identified:")
                for note in result['coverage_notes']:
                    print(f"  - {note}")

            outcome = f"{result['coverage_percentage']:.0f}% theory coverage"

        elif mode == "compensation-check":
            result = compensation_check()
            action = "limitation_compensation_check"

            if "error" in result:
                print(f"Error: {result['error']}")
                outcome = f"failed: {result['error']}"
            else:
                if result['limitations_detected']:
                    print(f"Limitations detected: {len(result['limitations_detected'])}")
                    for limitation in result['limitations_detected']:
                        print(f"  - {limitation}")

                    print("\nRecommendations:")
                    for rec in result['recommendations']:
                        print(f"  - {rec}")

                    outcome = f"{len(result['limitations_detected'])} limitations detected"
                else:
                    print("No Board limitations detected in CEO's recent behavior")
                    outcome = "clean - no limitations detected"

        results[mode] = result

        # Write logs
        write_gemma_log(mode, action, result)
        write_cieu_event(mode, action, outcome, result)

    print(f"\n=== Evolution Summary ===")
    print(json.dumps(results, indent=2))

    return 0


if __name__ == "__main__":
    sys.exit(main())
