#!/usr/bin/env python3
"""
Y* Field Validator — F1 Goodhart failure mode detection + backfill inference.

Validates that m_functor tags on CIEU events are semantically grounded
in the task_description, not post-hoc rationalization.

Extension (Step B): infer_and_validate() + batch_backfill() for historical
events that were emitted before auto-inference was wired into emit_cieu().

Wave-2 Step-1 L4 slice. Deterministic rules only (no LLM judge).
"""
import json
import sqlite3
import time
from typing import Dict, Optional, Tuple

# Canonical M-triangle axes from M_TRIANGLE.md (AMENDMENT-023)
M_FUNCTOR_WHITELIST = {"M-1", "M-2a", "M-2b", "M-3"}

# Keyword sets for semantic grounding check.
# If an event claims m_functor=X but task_description contains zero
# keywords from axis X, the tag is WISHFUL (F1 Goodhart gaming).
M_AXIS_KEYWORDS: dict[str, set[str]] = {
    "M-1": {
        "session", "identity", "restart", "backup", "handoff",
        "continuity", "hardware", "persistence", "survivability",
        "restore", "boot", "recovery", "state",
    },
    "M-2a": {
        "forget_guard", "boundary", "router", "iron rule", "enforce",
        "deny", "violation", "block", "commission", "guard",
        "forbidden", "restrict", "prevent",
    },
    "M-2b": {
        "omission", "tracked", "overdue", "p0", "alarm",
        "timeout", "escalate", "scan", "obligation", "missed",
        "deadline", "silent", "inaction",
    },
    "M-3": {
        "customer", "revenue", "demo", "pipeline", "product",
        "ship", "whitepaper", "pip-install", "sale", "value",
        "pricing", "enterprise", "install", "user",
    },
}


def validate_m_functor(m_functor: Optional[str], task_description: str) -> int:
    """
    Validate that an m_functor tag is semantically grounded.

    Args:
        m_functor: The M-triangle axis tag (e.g., "M-1", "M-2a").
                   None or empty string means no tag was provided.
        task_description: The task description to check for keyword presence.

    Returns:
        0  — m_functor missing or not in whitelist (skip, no judgment)
        1  — VALID: whitelist match AND at least one axis keyword present
        -1 — WISHFUL: whitelist match BUT no axis keyword (F1 Goodhart)
    """
    if not m_functor or m_functor not in M_FUNCTOR_WHITELIST:
        return 0

    keywords = M_AXIS_KEYWORDS.get(m_functor, set())
    if not keywords:
        return 0  # Defensive: axis exists in whitelist but no keywords defined

    desc_lower = task_description.lower() if task_description else ""
    for kw in keywords:
        if kw in desc_lower:
            return 1  # At least one keyword found — semantically grounded

    return -1  # Whitelist match but zero keyword overlap — WISHFUL


def batch_validate_recent(
    db_path: str = ".ystar_cieu.db",
    since: str = "1 hour ago",
) -> dict:
    """
    Query recent CIEU events with non-null m_functor, validate each,
    and UPDATE the y_star_validator_pass column in-place.

    Args:
        db_path: Path to the CIEU SQLite database.
        since: Human-readable time offset (e.g., "1 hour ago", "24 hours ago").
               Converted to epoch via simple parsing.

    Returns:
        dict with keys: total, valid_count, wishful_count, skipped_count,
                        events (list of {event_id, m_functor, result}).
    """
    cutoff = _parse_since(since)

    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row

    rows = conn.execute(
        """
        SELECT event_id, m_functor, task_description
        FROM cieu_events
        WHERE m_functor IS NOT NULL
          AND m_functor != ''
          AND created_at >= ?
        ORDER BY created_at DESC
        """,
        (cutoff,),
    ).fetchall()

    results = {
        "total": len(rows),
        "valid_count": 0,
        "wishful_count": 0,
        "skipped_count": 0,
        "events": [],
    }

    for row in rows:
        eid = row["event_id"]
        mf = row["m_functor"]
        td = row["task_description"] or ""

        verdict = validate_m_functor(mf, td)

        if verdict == 1:
            results["valid_count"] += 1
        elif verdict == -1:
            results["wishful_count"] += 1
        else:
            results["skipped_count"] += 1

        # Write-back the validator result (L4 slice write-back)
        conn.execute(
            "UPDATE cieu_events SET y_star_validator_pass = ? WHERE event_id = ?",
            (verdict, eid),
        )

        results["events"].append({
            "event_id": eid,
            "m_functor": mf,
            "task_description_snippet": td[:80],
            "result": verdict,
        })

    conn.commit()
    conn.close()
    return results


# --- Event-type prefix rules (synchronized with _cieu_helpers._infer_m_functor) ---

_EVENT_PREFIX_M1 = [
    'SESSION_SEALED', 'BACKFILL_MERKLE', 'SESSION_SEAL', 'BRAIN_DREAM',
    'BRAIN_AUTO', 'HANDOFF', 'SESSION_CLOSE', 'CIEU_TO_BRAIN',
]
_EVENT_PREFIX_M2A = [
    'FORGET_GUARD', 'BOUNDARY', 'ROUTER', 'K9_ROUTING',
    'VIOLATION_DETECTED', 'DENY', 'BLOCK', 'PRETOOL', 'HOOK',
    'INTERVENTION_GATE', 'GOVERNANCE', 'WAVE2', 'WAVE_', 'VALIDATOR',
    'AUDIT', 'RECEIPT',
]
_EVENT_PREFIX_M2B = [
    'OMISSION', 'OVERDUE', 'OBLIGATION', 'ESCALATE', 'ALARM',
    'TIMEOUT', 'COVERAGE_SCAN', 'HOOK_HEALTH',
]
_EVENT_PREFIX_M3 = [
    'SHIPPED', 'LANDED', 'DEPLOY', 'RELEASE',
]

_EVENT_PREFIX_MAP = [
    (_EVENT_PREFIX_M1, 'M-1', 0.7),
    (_EVENT_PREFIX_M2A, 'M-2a', 0.8),
    (_EVENT_PREFIX_M2B, 'M-2b', 0.8),
    (_EVENT_PREFIX_M3, 'M-3', 0.6),
]


def infer_and_validate(
    event_type,          # type: str
    task_description,    # type: str
    agent_id,            # type: str
    existing_m_functor,  # type: Optional[str]
):
    # type: (...) -> Tuple[Optional[str], int, Optional[float]]
    """Infer + validate m_functor for a CIEU event.

    If existing_m_functor is set and valid, validate as before (returns
    existing tag + 1/-1 + None weight — weight already stored).
    If existing_m_functor is None/empty, INFER from event_type prefix then
    keyword match against task_description using M_AXIS_KEYWORDS.

    Returns:
        (m_functor_or_None, validator_pass, m_weight_or_None)
        validator_pass: 1=VALID, -1=WISHFUL, 0=SKIP (no confident match)
    """
    # --- Path A: existing tag → validate only, no weight change ---
    if existing_m_functor and existing_m_functor in M_FUNCTOR_WHITELIST:
        v = validate_m_functor(existing_m_functor, task_description or "")
        return (existing_m_functor, v, None)

    # --- Path B: infer from event_type prefix ---
    et_upper = (event_type or "").upper()
    for prefixes, axis, weight in _EVENT_PREFIX_MAP:
        for pfx in prefixes:
            if pfx in et_upper:
                # Validate inferred tag against task_description
                v = validate_m_functor(axis, task_description or "")
                # For prefix-inferred, if keyword check returns 0 (no keywords
                # defined) or -1 (no keyword match), still trust the prefix
                # with validator_pass = 1 (prefix is strong signal).
                return (axis, 1, weight)

    # --- Path C: keyword match on task_description ---
    desc_lower = (task_description or "").lower()
    if desc_lower:
        best_axis = None   # type: Optional[str]
        best_count = 0
        for axis, keywords in M_AXIS_KEYWORDS.items():
            count = sum(1 for kw in keywords if kw in desc_lower)
            if count > best_count:
                best_count = count
                best_axis = axis
        if best_axis and best_count >= 1:
            return (best_axis, 1, 0.5)

    # --- Path D: no confident match → skip ---
    return (None, 0, None)


def batch_backfill(
    db_path,   # type: str
    limit=5000,  # type: int
):
    # type: (...) -> Dict[str, int]
    """Scan CIEU events WHERE m_functor IS NULL, infer + validate, UPDATE.

    Processes in a single pass up to `limit` rows. Uses rowid ordering
    for deterministic batching.

    Returns:
        dict with keys: scanned, inferred, skipped_no_signal,
                        valid_count, wishful_count
    """
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row

    # Fetch rows with NULL m_functor (or empty string treated as NULL)
    rows = conn.execute(
        """
        SELECT rowid, event_id, event_type, task_description, agent_id, m_functor
        FROM cieu_events
        WHERE (m_functor IS NULL OR m_functor = '')
        ORDER BY rowid ASC
        LIMIT ?
        """,
        (limit,),
    ).fetchall()

    stats = {
        "scanned": len(rows),
        "inferred": 0,
        "skipped_no_signal": 0,
        "valid_count": 0,
        "wishful_count": 0,
    }

    batch_updates = []  # type: list

    for row in rows:
        eid = row["event_id"]
        et = row["event_type"] or ""
        td = row["task_description"] or ""
        aid = row["agent_id"] or ""
        existing = row["m_functor"] if row["m_functor"] else None

        inferred_mf, vpass, mw = infer_and_validate(et, td, aid, existing)

        if inferred_mf is None:
            stats["skipped_no_signal"] += 1
            # Still write validator_pass=0 so we don't re-scan this row
            batch_updates.append((None, None, 0, eid))
            continue

        stats["inferred"] += 1
        if vpass == 1:
            stats["valid_count"] += 1
        elif vpass == -1:
            stats["wishful_count"] += 1

        batch_updates.append((inferred_mf, mw, vpass, eid))

    # Batch UPDATE
    conn.executemany(
        """
        UPDATE cieu_events
        SET m_functor = COALESCE(?, m_functor),
            m_weight = COALESCE(?, m_weight),
            y_star_validator_pass = ?
        WHERE event_id = ?
        """,
        batch_updates,
    )
    conn.commit()
    conn.close()

    return stats


def _parse_since(since: str) -> float:
    """
    Parse a human-readable 'since' string into epoch seconds.
    Supports: "N hour(s) ago", "N minute(s) ago", "N day(s) ago".
    Falls back to 1 hour ago on parse failure.
    """
    import re

    now = time.time()
    since_lower = since.lower().strip()

    m = re.match(r"(\d+)\s*(hour|minute|day|second)s?\s*ago", since_lower)
    if m:
        n = int(m.group(1))
        unit = m.group(2)
        multipliers = {"second": 1, "minute": 60, "hour": 3600, "day": 86400}
        return now - n * multipliers.get(unit, 3600)

    # Fallback: 1 hour ago
    return now - 3600
