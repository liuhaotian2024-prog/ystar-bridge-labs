#!/usr/bin/env python3
"""Session close script - write session summary to YML (.ystar_memory.db)

New capability: Auto-detect Board-surprising decisions from CIEU and write lessons.

Usage:
    python scripts/session_close_yml.py <agent_id> <summary_text>

Or with stdin:
    echo "Session summary here" | python scripts/session_close_yml.py <agent_id>
"""

import sys
import time
import json
import sqlite3
from pathlib import Path
from typing import List, Dict

# Add Y-star-gov to path if needed
YSTAR_GOV_PATH = Path(__file__).parent.parent.parent / "Y-star-gov"
if YSTAR_GOV_PATH.exists():
    sys.path.insert(0, str(YSTAR_GOV_PATH))

from ystar.memory import MemoryStore, Memory


def extract_board_lessons(company_root: Path, session_start_time: float) -> List[Dict]:
    """
    Scan CIEU events from this session for Board-surprising decisions.

    Indicators:
    - INTENT_ADJUSTED events (CEO's intent was adjusted by Board)
    - DIRECTIVE_REJECTED events (Board rejected CEO proposal)
    - GOV_ORDER events with severity HIGH/CRITICAL

    Returns list of lesson dicts.
    """
    cieu_db = company_root / ".ystar_cieu.db"

    if not cieu_db.exists():
        return []

    conn = sqlite3.connect(cieu_db)

    # Query for surprise indicators
    cursor = conn.execute("""
        SELECT event_id, event_type, created_at, agent_id, task_description, params_json
        FROM cieu_events
        WHERE created_at >= ?
          AND event_type IN ('INTENT_ADJUSTED', 'DIRECTIVE_REJECTED', 'GOV_ORDER')
        ORDER BY created_at ASC
    """, (session_start_time,))

    lessons = []

    for row in cursor.fetchall():
        event_id, event_type, created_at, agent_id, task_desc, params_json = row

        # Parse details from task_description or params_json
        details = {}
        if task_desc:
            try:
                details = json.loads(task_desc) if isinstance(task_desc, str) else {}
            except json.JSONDecodeError:
                pass

        if not details and params_json:
            try:
                details = json.loads(params_json) if isinstance(params_json, str) else {}
            except json.JSONDecodeError:
                pass

        # Extract lesson based on event type
        if event_type == "INTENT_ADJUSTED":
            original_intent = details.get("original_intent", "")
            adjusted_intent = details.get("adjusted_intent", "")
            reason = details.get("reason", "Board intervention")

            lesson = f"Board adjusted intent: {original_intent} → {adjusted_intent}. Reason: {reason}"
            lessons.append({
                "cieu_id": event_id,
                "event_type": event_type,
                "lesson": lesson,
                "context_tags": ["board_adjustment", "intent_change"]
            })

        elif event_type == "DIRECTIVE_REJECTED":
            directive_id = details.get("directive_id", "unknown")
            rejection_reason = details.get("reason", "Not aligned with governance")

            lesson = f"Board rejected directive {directive_id}: {rejection_reason}"
            lessons.append({
                "cieu_id": event_id,
                "event_type": event_type,
                "lesson": lesson,
                "context_tags": ["board_rejection", "directive_failed"]
            })

        elif event_type == "GOV_ORDER":
            severity = details.get("severity", "").upper()
            if severity in ["HIGH", "CRITICAL"]:
                order_content = details.get("order", "")
                lesson = f"Board issued {severity} governance order: {order_content}"
                lessons.append({
                    "cieu_id": event_id,
                    "event_type": event_type,
                    "lesson": lesson,
                    "context_tags": ["gov_order", f"severity:{severity.lower()}"]
                })

    conn.close()
    return lessons


def write_board_lessons(lessons: List[Dict], store: MemoryStore, cieu_db_path: Path):
    """Write Board lesson memories and CIEU audit records."""
    import uuid

    if not lessons:
        return

    print(f"\nFound {len(lessons)} Board-surprising decisions in this session:")
    print("-" * 70)

    conn = sqlite3.connect(cieu_db_path)

    for lesson_data in lessons:
        lesson_content = lesson_data["lesson"]
        context_tags = lesson_data["context_tags"]

        print(f"  [{lesson_data['event_type']}] {lesson_content}")

        # Create lesson memory
        mem = Memory(
            agent_id="ceo",  # Board lessons are CEO's responsibility to learn
            memory_type="lesson",
            content=lesson_content,
            initial_score=1.0,
            half_life_days=180,  # Board lessons decay very slowly
            context_tags=context_tags + ["source:board_decision", "session_close"],
            metadata={
                "source_cieu_id": lesson_data["cieu_id"],
                "import_time": time.time()
            }
        )

        # Write CIEU audit for lesson creation (using existing schema)
        event_id = str(uuid.uuid4())
        seq_global = int(time.time() * 1_000_000)

        conn.execute("""
            INSERT INTO cieu_events (
                event_id, seq_global, created_at, session_id, agent_id, event_type,
                decision, passed, task_description, params_json
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            event_id,
            seq_global,
            time.time(),
            "session_close",
            "ceo",
            "BOARD_LESSON_LEARNED",
            "allow",
            1,
            lesson_content,
            json.dumps({
                "lesson": lesson_content,
                "source_event": lesson_data["event_type"],
                "source_cieu_id": lesson_data["cieu_id"]
            })
        ))

        store.remember(mem, cieu_ref=event_id)

    conn.commit()
    conn.close()

    print("-" * 70)
    print(f"{len(lessons)} Board lessons written to YML")


def main():
    if len(sys.argv) < 2:
        print("Usage: session_close_yml.py <agent_id> [summary_text]", file=sys.stderr)
        print("  Or pipe summary via stdin", file=sys.stderr)
        return 1

    agent_id = sys.argv[1]

    # Get summary from args or stdin
    if len(sys.argv) >= 3:
        summary = " ".join(sys.argv[2:])
    else:
        summary = sys.stdin.read().strip()

    if not summary:
        print("Error: No summary provided", file=sys.stderr)
        return 1

    # Initialize memory store
    company_root = Path(__file__).parent.parent
    db_path = company_root / ".ystar_memory.db"
    cieu_db_path = company_root / ".ystar_cieu.db"

    store = MemoryStore(db_path=str(db_path))

    # Create memory object for session summary
    mem = Memory(
        agent_id=agent_id,
        content=summary,
        memory_type="task_context",  # Short-term session state
        initial_score=1.0,
        context_tags=["session_summary"],
        half_life_days=7.0,  # 7-day half-life for session context
    )

    # Store the memory
    memory_id = store.remember(mem)

    print(f"Session summary stored: {memory_id}")
    print(f"Agent: {agent_id}")
    print(f"Content: {summary[:100]}{'...' if len(summary) > 100 else ''}")

    # Auto-detect Board lessons from this session
    # Use session start time = 1 hour ago as default window
    session_start = time.time() - 3600

    lessons = extract_board_lessons(company_root, session_start)
    write_board_lessons(lessons, store, cieu_db_path)

    return 0


if __name__ == "__main__":
    sys.exit(main())
