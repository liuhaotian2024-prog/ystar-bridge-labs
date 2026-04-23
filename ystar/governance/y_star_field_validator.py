#!/usr/bin/env python3
"""
Y* Field Validator — F1 Goodhart failure mode detection.

Validates that m_functor tags on CIEU events are semantically grounded
in the task_description, not post-hoc rationalization.

Wave-2 Step-1 L4 slice. Deterministic rules only (no LLM judge).
"""
import json
import sqlite3
import time
from typing import Optional

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
