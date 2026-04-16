#!/usr/bin/env python3
"""
Precheck Review Script — Closed-loop Learning from gov_precheck

Compares historical gov_precheck assumptions with actual directive outcomes.
Identifies deviations and writes lessons to YML.

Process:
1. Load all gov_precheck events from .ystar_cieu.db
2. For each precheck, find corresponding directive completion
3. Compare: assumption & worst_case vs. what actually happened
4. Deviations → write as lesson memories to YML
5. Generate deviation report
"""

import sys
import json
import sqlite3
import time
from pathlib import Path
from typing import List, Dict, Optional, Tuple

# Add Y-star-gov to path
sys.path.insert(0, "/Users/haotianliu/.openclaw/workspace/Y-star-gov")

from ystar.memory.store import MemoryStore
from ystar.memory.models import Memory
sys.path.insert(0, str(Path(__file__).parent))
from _cieu_helpers import _get_current_agent

COMPANY_ROOT = Path("/Users/haotianliu/.openclaw/workspace/ystar-company")
CIEU_DB_PATH = COMPANY_ROOT / ".ystar_cieu.db"
MEMORY_DB_PATH = COMPANY_ROOT / ".ystar_memory.db"


def load_precheck_events() -> List[Dict]:
    """Load all gov_precheck events from CIEU database."""
    conn = sqlite3.connect(CIEU_DB_PATH)

    cursor = conn.execute("""
        SELECT event_id, created_at, agent_id, task_description, params_json
        FROM cieu_events
        WHERE event_type = 'GOV_PRECHECK'
        ORDER BY created_at ASC
    """)

    events = []
    for row in cursor.fetchall():
        event_id, created_at, agent_id, task_desc, params_json = row

        # Try to extract details from task_description or params_json
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

        events.append({
            "cieu_id": event_id,  # Map event_id to cieu_id for compatibility
            "timestamp": created_at,
            "agent_id": agent_id,
            "details": details
        })

    conn.close()
    return events


def find_directive_completion(directive_id: str, after_timestamp: float) -> Optional[Dict]:
    """Find directive completion event after given timestamp."""
    conn = sqlite3.connect(CIEU_DB_PATH)

    cursor = conn.execute("""
        SELECT event_id, created_at, agent_id, event_type, task_description, params_json
        FROM cieu_events
        WHERE event_type IN ('DIRECTIVE_COMPLETED', 'DIRECTIVE_FAILED', 'DIRECTIVE_REJECTED')
          AND created_at > ?
          AND (task_description LIKE ? OR params_json LIKE ?)
        ORDER BY created_at ASC
        LIMIT 1
    """, (after_timestamp, f'%{directive_id}%', f'%{directive_id}%'))

    row = cursor.fetchone()
    conn.close()

    if not row:
        return None

    event_id, created_at, agent_id, event_type, task_desc, params_json = row

    details = {}
    if task_desc:
        try:
            details = json.loads(task_desc) if isinstance(task_desc, str) else {}
        except json.JSONDecodeError:
            pass

    return {
        "cieu_id": event_id,
        "timestamp": created_at,
        "agent_id": agent_id,
        "event_type": event_type,
        "details": details
    }


def compare_precheck_outcome(precheck: Dict, outcome: Optional[Dict]) -> Optional[Dict]:
    """
    Compare precheck assumptions with actual outcome.

    Returns deviation dict if significant deviation found, None otherwise.
    """
    if not outcome:
        # Directive never completed — potential deviation
        return {
            "deviation_type": "NEVER_COMPLETED",
            "precheck": precheck,
            "outcome": None,
            "lesson": f"Directive {precheck['details'].get('directive_id', 'unknown')} was prechecked but never completed. Precheck may have been too cautious or directive was abandoned."
        }

    # Extract key fields
    assumption = precheck["details"].get("assumption", "")
    worst_case = precheck["details"].get("worst_case", "")
    risk_level = precheck["details"].get("risk_level", "unknown")

    outcome_status = outcome["event_type"]
    outcome_details = outcome["details"]

    # Deviation patterns
    deviations = []

    # Pattern 1: Low risk precheck but directive failed
    if risk_level in ["LOW", "MINIMAL"] and outcome_status == "DIRECTIVE_FAILED":
        deviations.append({
            "deviation_type": "UNEXPECTED_FAILURE",
            "precheck": precheck,
            "outcome": outcome,
            "lesson": f"Precheck assumed {assumption} with risk {risk_level}, but directive failed. Risk assessment may have been too optimistic."
        })

    # Pattern 2: High risk precheck but smooth completion
    if risk_level == "HIGH" and outcome_status == "DIRECTIVE_COMPLETED":
        elapsed = outcome["timestamp"] - precheck["timestamp"]
        if elapsed < 60:  # Completed within 1 minute
            deviations.append({
                "deviation_type": "OVERESTIMATED_RISK",
                "precheck": precheck,
                "outcome": outcome,
                "lesson": f"Precheck marked HIGH risk for {assumption}, but directive completed smoothly in {elapsed:.0f}s. Future prechecks for similar tasks can be less conservative."
            })

    # Pattern 3: Worst case actually happened
    if worst_case and outcome_status == "DIRECTIVE_FAILED":
        failure_reason = outcome_details.get("reason", "")
        if worst_case.lower() in failure_reason.lower():
            deviations.append({
                "deviation_type": "WORST_CASE_OCCURRED",
                "precheck": precheck,
                "outcome": outcome,
                "lesson": f"Worst case scenario predicted: '{worst_case}'. This actually occurred. Precheck was accurate but mitigation was insufficient."
            })

    return deviations[0] if deviations else None


def write_lesson_to_yml(deviation: Dict, store: MemoryStore):
    """Write deviation as lesson memory to YML."""
    import uuid

    lesson_content = f"{deviation['deviation_type']}: {deviation['lesson']}"

    mem = Memory(
        agent_id="cto",
        memory_type="lesson",
        content=lesson_content,
        initial_score=1.0,
        half_life_days=120,  # Lessons decay slower
        context_tags=[
            "source:precheck_review",
            f"deviation:{deviation['deviation_type']}",
            "category:governance"
        ],
        metadata={
            "precheck_cieu_id": deviation["precheck"]["cieu_id"],
            "outcome_cieu_id": deviation.get("outcome", {}).get("cieu_id"),
            "import_time": time.time()
        }
    )

    # Write CIEU audit (using existing schema)
    event_id = str(uuid.uuid4())
    seq_global = int(time.time() * 1_000_000)

    conn = sqlite3.connect(CIEU_DB_PATH)
    conn.execute("""
        INSERT INTO cieu_events (
            event_id, seq_global, created_at, session_id, agent_id, event_type,
            decision, passed, task_description, params_json
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        event_id,
        seq_global,
        time.time(),
        "precheck_review",
        "cto",
        "PRECHECK_LESSON_LEARNED",
        "allow",
        1,
        lesson_content,
        json.dumps({
            "deviation_type": deviation["deviation_type"],
            "lesson": deviation["lesson"]
        })
    ))
    conn.commit()
    conn.close()

    store.remember(mem, cieu_ref=event_id)


def main():
    """Main precheck review process."""
    print("Y*gov Precheck Review — Closed-loop Learning")
    print("=" * 70)
    print(f"CIEU DB: {CIEU_DB_PATH}")
    print(f"Memory DB: {MEMORY_DB_PATH}")
    print()

    # Initialize memory store
    store = MemoryStore(str(MEMORY_DB_PATH))

    # Load all precheck events
    print("Loading gov_precheck events...")
    prechecks = load_precheck_events()
    print(f"Found {len(prechecks)} precheck events")
    print()

    if not prechecks:
        print("No precheck events found. Exiting.")
        return

    # Process each precheck
    deviations_found = []

    print("Comparing prechecks with outcomes...")
    print("-" * 70)

    for pc in prechecks:
        directive_id = pc["details"].get("directive_id", "unknown")
        timestamp = pc["timestamp"]

        # Find outcome
        outcome = find_directive_completion(directive_id, timestamp)

        # Compare
        deviation = compare_precheck_outcome(pc, outcome)

        if deviation:
            deviations_found.append(deviation)
            print(f"\nDEVIATION FOUND:")
            print(f"  Type: {deviation['deviation_type']}")
            print(f"  Directive: {directive_id}")
            print(f"  Lesson: {deviation['lesson']}")

            # Write to YML
            write_lesson_to_yml(deviation, store)

    print()
    print("=" * 70)
    print("REVIEW COMPLETE")
    print(f"Total prechecks analyzed: {len(prechecks)}")
    print(f"Deviations found: {len(deviations_found)}")
    print(f"Lessons written to YML: {len(deviations_found)}")
    print()

    # Deviation breakdown
    if deviations_found:
        print("Deviation Breakdown:")
        types = {}
        for dev in deviations_found:
            dtype = dev["deviation_type"]
            types[dtype] = types.get(dtype, 0) + 1

        for dtype, count in types.items():
            print(f"  {dtype}: {count}")

    print()
    print("CIEU audit records written to .ystar_cieu.db")


if __name__ == "__main__":
    main()
