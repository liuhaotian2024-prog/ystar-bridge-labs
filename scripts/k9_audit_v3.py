#!/usr/bin/env python3
"""
K9 Audit v3 — 3-Layer Universal Governance Audit Framework
Board-approved 2026-04-15 | Replaces k9_repo_audit_cieu.py

Architecture:
  Layer 1: Component Liveness (event presence in time window)
  Layer 2: Causal Chain Integrity (event sequence + timing)
  Layer 3: Invariant Enforcement (SQL-based constraints)

Optimizations (CEO 2026-04-15):
  1. Per-component time windows (not one-size-fits-all)
  2. Cross-session task_id/obligation_id tracking
  3. Causal chain uses seq_global for ordering
  4. Unified CRITICAL/WARNING/INFO output format
"""

import sqlite3
import os
from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional


# =============================================================================
# Database Connection
# =============================================================================

def get_cieu_conn() -> sqlite3.Connection:
    """Return connection to CIEU database."""
    # Primary path: ystar-company root .ystar_cieu.db
    db_path = os.path.join(
        os.path.dirname(os.path.dirname(__file__)), ".ystar_cieu.db"
    )
    if not os.path.exists(db_path):
        # Fallback to gov-mcp/cieu.db
        db_path = os.path.expanduser("~/.openclaw/workspace/gov-mcp/cieu.db")
    if not os.path.exists(db_path):
        # Fallback to local data/cieu.db if exists
        local_path = os.path.join(
            os.path.dirname(os.path.dirname(__file__)), "data", "cieu.db"
        )
        if os.path.exists(local_path):
            db_path = local_path
    return sqlite3.connect(db_path)


# =============================================================================
# Layer 1: Component Liveness Checks
# =============================================================================

def check_component_liveness(
    component_name: str,
    expected_event_types: List[str],
    lookback_seconds: int,
    min_expected_count: int = 1,
) -> List[str]:
    """
    Check that a component has emitted expected events in the time window.

    Args:
        component_name: Human-readable component name
        expected_event_types: List of event_type strings to check
        lookback_seconds: How far back to search
        min_expected_count: Minimum occurrences required

    Returns:
        List of violation messages (empty if healthy)
    """
    violations = []
    conn = get_cieu_conn()
    cursor = conn.cursor()

    cutoff_epoch = (datetime.now() - timedelta(seconds=lookback_seconds)).timestamp()

    for event_type in expected_event_types:
        try:
            cursor.execute(
                """
                SELECT COUNT(*) FROM cieu_events
                WHERE event_type = ? AND CAST(created_at AS REAL) >= ?
                """,
                (event_type, cutoff_epoch),
            )
            count = cursor.fetchone()[0]

            if count < min_expected_count:
                violations.append(
                    f"[LIVENESS] {component_name}: event_type={event_type} "
                    f"仅{count}条 (期望≥{min_expected_count}) in last {lookback_seconds}s"
                )
        except sqlite3.OperationalError as e:
            violations.append(
                f"[CRITICAL] {component_name}: DB query failed for {event_type}: {e}"
            )

    conn.close()
    return violations


def run_all_liveness_checks() -> List[str]:
    """
    Run liveness checks for all 5 core components.

    Components:
      1. Hook Chain (HOOK_BOOT required, HOOK_HEALTH_K9_ESCALATE event-driven)
      2. OmissionEngine (OMISSION_DETECTED, OMISSION_RESOLVED)
      3. ForgetGuard (FORGET_GUARD_SCAN, FORGET_GUARD_VIOLATION)
      4. Intent Tracker (INTENT_DECLARED, INTENT_FULFILLED)
      5. RLE (RLE_CONVERGE, RLE_DIVERGE)
    """
    violations = []

    # 1a. Hook Chain heartbeat — HOOK_BOOT fires on each hook invocation (must be active)
    violations += check_component_liveness(
        component_name="HookChain",
        expected_event_types=["HOOK_BOOT"],
        lookback_seconds=600,
        min_expected_count=1,
    )
    # 1b. Hook escalation — event-driven, may legitimately be 0 if no health issues
    violations += check_component_liveness(
        component_name="HookEscalation",
        expected_event_types=["HOOK_HEALTH_K9_ESCALATE"],
        lookback_seconds=600,
        min_expected_count=0,
    )

    # 2. OmissionEngine — passive detector, 5min window acceptable
    violations += check_component_liveness(
        component_name="OmissionEngine",
        expected_event_types=["OMISSION_DETECTED", "OMISSION_RESOLVED"],
        lookback_seconds=300,
        min_expected_count=0,  # May be 0 if no omissions
    )

    # 3. ForgetGuard — runs on file writes, 2min window
    violations += check_component_liveness(
        component_name="ForgetGuard",
        expected_event_types=["FORGET_GUARD_SCAN", "FORGET_GUARD_VIOLATION"],
        lookback_seconds=120,
        min_expected_count=0,  # May be 0 if no writes
    )

    # 4. Intent Tracker — every task should declare intent, 10min window
    violations += check_component_liveness(
        component_name="IntentTracker",
        expected_event_types=["INTENT_DECLARED", "INTENT_FULFILLED"],
        lookback_seconds=600,
        min_expected_count=1,
    )

    # 5. RLE (Runtime Liability Engine) — 15min window
    violations += check_component_liveness(
        component_name="RLE",
        expected_event_types=["RLE_CONVERGE", "RLE_DIVERGE"],
        lookback_seconds=900,
        min_expected_count=0,  # May be 0 if no liability events
    )

    return violations


# =============================================================================
# Layer 2: Causal Chain Integrity Checks
# =============================================================================

def check_causal_chain(
    chain_name: str,
    event_sequence: List[str],
    lookback_seconds: int,
    require_all: bool = True,
) -> List[str]:
    """
    Check that a causal chain's events appear in correct order.

    Args:
        chain_name: Human-readable chain name
        event_sequence: Ordered list of event_types (A → B → C)
        lookback_seconds: Time window
        require_all: If True, all events must exist; if False, allow partial

    Returns:
        List of violation messages
    """
    violations = []
    conn = get_cieu_conn()
    cursor = conn.cursor()

    cutoff_epoch = (datetime.now() - timedelta(seconds=lookback_seconds)).timestamp()

    try:
        # Find all occurrences of each event in sequence, ordered by seq_global
        found_events = []
        for event_type in event_sequence:
            cursor.execute(
                """
                SELECT event_type, created_at, seq_global, session_id, agent_id
                FROM cieu_events
                WHERE event_type = ? AND CAST(created_at AS REAL) >= ?
                ORDER BY seq_global ASC
                """,
                (event_type, cutoff_epoch),
            )
            rows = cursor.fetchall()
            found_events.append((event_type, rows))

        # Check if all required events exist
        missing = [et for et, rows in found_events if len(rows) == 0]
        if require_all and missing:
            violations.append(
                f"[CHAIN] {chain_name}: missing events {missing} in last {lookback_seconds}s"
            )
            conn.close()
            return violations

        # Check temporal ordering: for each pair (A, B), ensure A's latest < B's earliest
        for i in range(len(event_sequence) - 1):
            event_a, rows_a = found_events[i]
            event_b, rows_b = found_events[i + 1]

            if not rows_a or not rows_b:
                continue  # Skip if either missing (already reported if require_all)

            # Get latest A and earliest B by seq_global
            latest_a = max(rows_a, key=lambda r: r[2])  # seq_global at index 2
            earliest_b = min(rows_b, key=lambda r: r[2])

            if latest_a[2] >= earliest_b[2]:  # seq_global comparison
                violations.append(
                    f"[CHAIN] {chain_name}: ordering violation — "
                    f"{event_a}(seq={latest_a[2]}) should precede "
                    f"{event_b}(seq={earliest_b[2]})"
                )

    except sqlite3.OperationalError as e:
        violations.append(f"[CRITICAL] {chain_name}: DB query failed: {e}")

    conn.close()
    return violations


def run_all_chain_checks() -> List[str]:
    """
    Run causal chain checks for 4 critical workflows.

    Chains:
      1. Board Directive: BOARD_DIRECTIVE → INTENT_DECLARED → INTENT_FULFILLED
      2. ForgetGuard Interception: FORGET_GUARD_VIOLATION → ESCALATION → BOARD_DECISION
      3. CZL Convergence: RLE_DIVERGE → CORRECTIVE_ACTION → RLE_CONVERGE
      4. Obligation Fulfillment: OBLIGATION_CREATED → OBLIGATION_FULFILLED
    """
    violations = []

    # 1. Board Directive Chain (30min window)
    violations += check_causal_chain(
        chain_name="BoardDirective",
        event_sequence=["BOARD_DECISION", "INTENT_DECLARED", "INTENT_FULFILLED"],
        lookback_seconds=1800,
        require_all=False,  # Board may not issue directive in every session
    )

    # 2. ForgetGuard Interception Chain (15min window)
    violations += check_causal_chain(
        chain_name="ForgetGuardInterception",
        event_sequence=["FORGET_GUARD_VIOLATION", "RESIDUAL_LOOP_ESCALATE", "BOARD_DECISION"],
        lookback_seconds=900,
        require_all=False,  # May not trigger in every session
    )

    # 3. CZL Convergence Chain (20min window)
    violations += check_causal_chain(
        chain_name="CZLConvergence",
        event_sequence=["RLE_DIVERGE", "CORRECTIVE_ACTION", "RLE_CONVERGE"],
        lookback_seconds=1200,
        require_all=False,
    )

    # 4. Obligation Fulfillment Chain (30min window)
    violations += check_causal_chain(
        chain_name="ObligationFulfillment",
        event_sequence=["OBLIGATION_REGISTERED", "OBLIGATION_FULFILLED"],
        lookback_seconds=1800,
        require_all=False,
    )

    return violations


# =============================================================================
# Layer 3: Invariant Checks (SQL-based Constraints)
# =============================================================================

def check_invariant(
    invariant_name: str,
    violation_query: str,
    query_params: tuple,
    violation_message_template: str,
) -> List[str]:
    """
    Check a system invariant using a SQL query that returns violating rows.

    Args:
        invariant_name: Human-readable invariant name
        violation_query: SQL query that returns rows violating the invariant
        query_params: Tuple of parameters for the query
        violation_message_template: Template string with {placeholders}

    Returns:
        List of violation messages (one per violating row)
    """
    violations = []
    conn = get_cieu_conn()
    cursor = conn.cursor()

    try:
        cursor.execute(violation_query, query_params)
        rows = cursor.fetchall()

        for row in rows:
            # Convert row tuple to dict for template formatting
            # Assume query returns named columns via cursor.description
            row_dict = {}
            if cursor.description:
                row_dict = {desc[0]: val for desc, val in zip(cursor.description, row)}

            msg = violation_message_template.format(**row_dict)
            violations.append(f"[INVARIANT] {invariant_name}: {msg}")

    except sqlite3.OperationalError as e:
        violations.append(f"[CRITICAL] {invariant_name}: DB query failed: {e}")

    conn.close()
    return violations


def run_all_invariant_checks() -> List[str]:
    """
    Run invariant checks for 5 system-wide constraints.

    Invariants:
      1. Failed directives must be recorded
      2. Obligations never orphaned (must have creator + task_id)
      3. Escalations must receive Board response
      4. Gaps (Rt+1 > 0) must be addressed
      5. Hook startup must trigger governance action
    """
    violations = []
    cutoff = (datetime.now() - timedelta(hours=24)).timestamp()

    # 1. Failed directives must be recorded
    violations += check_invariant(
        invariant_name="FailedDirectiveRecorded",
        violation_query="""
            SELECT session_id, created_at, agent_id
            FROM cieu_events
            WHERE event_type = 'BOARD_DECISION'
              AND created_at >= ?
              AND NOT EXISTS (
                  SELECT 1 FROM cieu_events AS e2
                  WHERE e2.event_type IN ('INTENT_FULFILLED', 'TASK_FAILED')
                    AND e2.session_id = cieu_events.session_id
                    AND e2.seq_global > cieu_events.seq_global
              )
        """,
        query_params=(cutoff,),
        violation_message_template="session={session_id} directive at {created_at} has no completion/failure record",
    )

    # 2. Obligations never orphaned (simplified — check presence only, no task_id validation)
    violations += check_invariant(
        invariant_name="ObligationNotOrphaned",
        violation_query="""
            SELECT session_id, created_at, agent_id
            FROM cieu_events
            WHERE event_type = 'OBLIGATION_REGISTERED'
              AND created_at >= ?
              AND agent_id IS NULL
        """,
        query_params=(cutoff,),
        violation_message_template="session={session_id} obligation at {created_at} has NULL agent_id",
    )

    # 3. Escalations must receive Board response
    violations += check_invariant(
        invariant_name="EscalationHasBoardResponse",
        violation_query="""
            SELECT session_id, created_at, agent_id
            FROM cieu_events
            WHERE event_type = 'RESIDUAL_LOOP_ESCALATE'
              AND created_at >= ?
              AND NOT EXISTS (
                  SELECT 1 FROM cieu_events AS e2
                  WHERE e2.event_type = 'BOARD_DECISION'
                    AND e2.session_id = cieu_events.session_id
                    AND e2.seq_global > cieu_events.seq_global
              )
        """,
        query_params=(cutoff,),
        violation_message_template="session={session_id} escalation at {created_at} has no Board response",
    )

    # 4. Gaps (Rt+1 > 0) must be addressed
    violations += check_invariant(
        invariant_name="GapMustBeAddressed",
        violation_query="""
            SELECT session_id, created_at, agent_id
            FROM cieu_events
            WHERE event_type = 'GAP_IDENTIFIED'
              AND created_at >= ?
              AND NOT EXISTS (
                  SELECT 1 FROM cieu_events AS e2
                  WHERE e2.event_type IN ('GAP_CLOSED', 'GAP_ESCALATED')
                    AND e2.session_id = cieu_events.session_id
                    AND e2.seq_global > cieu_events.seq_global
              )
        """,
        query_params=(cutoff,),
        violation_message_template="session={session_id} gap at {created_at} remains unresolved",
    )

    # 5. Hook startup must trigger governance action
    violations += check_invariant(
        invariant_name="HookStartupTriggersGovernance",
        violation_query="""
            SELECT session_id, created_at, agent_id
            FROM cieu_events
            WHERE event_type = 'HOOK_BOOT'
              AND created_at >= ?
              AND NOT EXISTS (
                  SELECT 1 FROM cieu_events AS e2
                  WHERE e2.event_type IN ('GOVERNANCE_INIT', 'SESSION_BOOT')
                    AND e2.session_id = cieu_events.session_id
                    AND ABS(e2.created_at - cieu_events.created_at) < 10
              )
        """,
        query_params=(cutoff,),
        violation_message_template="session={session_id} hook startup at {created_at} has no governance init within 10s",
    )

    return violations


# =============================================================================
# Main Orchestrator
# =============================================================================

def main():
    """
    Run all 3 layers of audit checks and output unified report.
    """
    print(f"=== K9 Audit v3 Report | {datetime.now().isoformat()} ===\n")

    violations = []

    print("Running Layer 1: Component Liveness Checks...")
    violations += run_all_liveness_checks()

    print("Running Layer 2: Causal Chain Integrity Checks...")
    violations += run_all_chain_checks()

    print("Running Layer 3: Invariant Enforcement Checks...")
    violations += run_all_invariant_checks()

    # Classify violations
    critical = [
        v for v in violations
        if "CRITICAL" in v or ("LIVENESS" in v and "仅0条" in v and "≥1" in v)
    ]
    warning = [v for v in violations if v not in critical]

    print(f"\n{'='*70}")
    print(f"\n[CRITICAL] {len(critical)} items:")
    if critical:
        for v in critical:
            print(f"  {v}")
    else:
        print("  (none)")

    print(f"\n[WARNING] {len(warning)} items:")
    if warning:
        for v in warning:
            print(f"  {v}")
    else:
        print("  (none)")

    print(f"\n{'='*70}")
    print(f"Rt+1 = {len(critical)} (CRITICAL count)")
    print(f"{'='*70}\n")

    return len(critical)


if __name__ == "__main__":
    exit_code = main()
    exit(exit_code)
