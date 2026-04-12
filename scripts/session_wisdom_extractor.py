#!/usr/bin/env python3
"""Session Wisdom Extractor — Distill session essence for next-session injection

Zero fabrication. Extract patterns from CIEU + memory.db + continuation.json.

Output ≤ 10KB "wisdom package" containing:
- Top 3-5 core decisions
- Top 3 new knowledge/patterns
- Uncompleted obligations / next actions
- Top 2-3 new methodologies/genes
- Recent 5 important CIEU events summary

This is NOT a transcript. This is "10-second CEO briefing on what you were just doing".

Usage:
    python3 scripts/session_wisdom_extractor.py [--output <path>]

Outputs to memory/wisdom_package_<session_id>.md
Links as memory/wisdom_package_latest.md
"""

import sys
import time
import json
import sqlite3
from pathlib import Path
from typing import List, Dict, Optional
from collections import Counter


def get_session_id(company_root: Path) -> str:
    """Get current session ID from .ystar_session.json"""
    session_cfg = company_root / ".ystar_session.json"
    if not session_cfg.exists():
        return time.strftime("%Y%m%d_%H%M%S")

    try:
        cfg = json.loads(session_cfg.read_text())
        return cfg.get("session_id", time.strftime("%Y%m%d_%H%M%S"))
    except Exception:
        return time.strftime("%Y%m%d_%H%M%S")


def extract_core_decisions(company_root: Path, session_start: float) -> List[str]:
    """Extract top decisions from this session's CIEU events

    Look for: INTENT_ADJUSTED, DIRECTIVE_*, GOV_ORDER, major ALLOW decisions
    """
    cieu_db = company_root / ".ystar_cieu.db"
    if not cieu_db.exists():
        return []

    try:
        conn = sqlite3.connect(str(cieu_db))
        cursor = conn.execute("""
            SELECT event_type, task_description, params_json, created_at
            FROM cieu_events
            WHERE created_at >= ?
              AND event_type IN ('INTENT_ADJUSTED', 'DIRECTIVE_APPROVED', 'DIRECTIVE_REJECTED',
                                 'GOV_ORDER', 'BOARD_DECISION', 'DELEGATION_AUTHORIZED')
            ORDER BY created_at DESC
            LIMIT 5
        """, (session_start,))

        decisions = []
        for event_type, task_desc, params_json, created_at in cursor.fetchall():
            timestamp = time.strftime("%H:%M", time.localtime(created_at))

            # Parse details
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

            # Format decision
            if event_type == "INTENT_ADJUSTED":
                original = details.get("original_intent", "")[:80]
                adjusted = details.get("adjusted_intent", "")[:80]
                decisions.append(f"[{timestamp}] Intent adjusted: {original} → {adjusted}")

            elif event_type in ["DIRECTIVE_APPROVED", "DIRECTIVE_REJECTED"]:
                directive_id = details.get("directive_id", "unknown")
                status = "approved" if event_type == "DIRECTIVE_APPROVED" else "rejected"
                reason = details.get("reason", "")[:100]
                decisions.append(f"[{timestamp}] Directive {directive_id} {status}: {reason}")

            elif event_type == "GOV_ORDER":
                order = details.get("order", task_desc or "")[:120]
                decisions.append(f"[{timestamp}] Governance order: {order}")

            elif event_type == "BOARD_DECISION":
                decision = details.get("decision", task_desc or "")[:120]
                decisions.append(f"[{timestamp}] Board decision: {decision}")

            elif event_type == "DELEGATION_AUTHORIZED":
                from_agent = details.get("from_agent", "")
                to_agent = details.get("to_agent", "")
                task = details.get("task", "")[:80]
                decisions.append(f"[{timestamp}] Delegated {from_agent} → {to_agent}: {task}")

        conn.close()
        return decisions[:5]  # Top 5
    except Exception as e:
        print(f"Warning: Failed to extract decisions: {e}", file=sys.stderr)
        return []


def extract_new_knowledge(company_root: Path, session_start: float) -> List[str]:
    """Extract new knowledge/patterns learned this session"""
    memory_db = company_root / ".ystar_memory.db"
    if not memory_db.exists():
        return []

    try:
        conn = sqlite3.connect(str(memory_db))
        cursor = conn.execute("""
            SELECT content, context_tags FROM memories
            WHERE memory_type IN ('lesson', 'knowledge', 'pattern')
              AND created_at >= ?
            ORDER BY created_at DESC
            LIMIT 3
        """, (session_start,))

        knowledge = []
        for content, tags_json in cursor.fetchall():
            content_preview = content[:200] if content else ""
            knowledge.append(content_preview)

        conn.close()
        return knowledge
    except Exception as e:
        print(f"Warning: Failed to extract knowledge: {e}", file=sys.stderr)
        return []


def extract_uncompleted_obligations(company_root: Path) -> List[str]:
    """Extract active obligations (not completed)"""
    memory_db = company_root / ".ystar_memory.db"
    if not memory_db.exists():
        return []

    try:
        conn = sqlite3.connect(str(memory_db))
        cursor = conn.execute("""
            SELECT content FROM memories
            WHERE memory_type = 'obligation'
            ORDER BY created_at DESC
            LIMIT 10
        """)

        obligations = []
        for (content,) in cursor.fetchall():
            # Extract first line or up to 150 chars
            first_line = content.split('\n')[0] if content else ""
            preview = first_line[:150] if len(first_line) > 150 else first_line
            obligations.append(preview)

        conn.close()
        return obligations
    except Exception as e:
        print(f"Warning: Failed to extract obligations: {e}", file=sys.stderr)
        return []


def extract_methodologies(company_root: Path, session_start: float) -> List[str]:
    """Extract new methodologies/thinking patterns from this session"""

    # Methodologies often appear in CIEU events with certain patterns
    cieu_db = company_root / ".ystar_cieu.db"
    if not cieu_db.exists():
        return []

    try:
        conn = sqlite3.connect(str(cieu_db))

        # Look for events with "methodology", "pattern", "approach", "framework" in description
        cursor = conn.execute("""
            SELECT task_description, params_json FROM cieu_events
            WHERE created_at >= ?
              AND (task_description LIKE '%methodology%'
                   OR task_description LIKE '%pattern%'
                   OR task_description LIKE '%approach%'
                   OR task_description LIKE '%framework%'
                   OR task_description LIKE '%principle%')
            ORDER BY created_at DESC
            LIMIT 5
        """, (session_start,))

        methodologies = []
        for task_desc, params_json in cursor.fetchall():
            if task_desc:
                preview = task_desc[:200] if len(task_desc) > 200 else task_desc
                methodologies.append(preview)

        conn.close()
        return methodologies[:3]  # Top 3
    except Exception as e:
        print(f"Warning: Failed to extract methodologies: {e}", file=sys.stderr)
        return []


def extract_recent_cieu_events(company_root: Path, session_start: float) -> List[str]:
    """Extract recent 5 important CIEU events"""
    cieu_db = company_root / ".ystar_cieu.db"
    if not cieu_db.exists():
        return []

    try:
        conn = sqlite3.connect(str(cieu_db))

        # Filter for "important" event types
        cursor = conn.execute("""
            SELECT event_type, decision, task_description, created_at FROM cieu_events
            WHERE created_at >= ?
              AND event_type NOT LIKE 'HOOK_%'
            ORDER BY created_at DESC
            LIMIT 10
        """, (session_start,))

        events = []
        for event_type, decision, task_desc, created_at in cursor.fetchall():
            timestamp = time.strftime("%H:%M", time.localtime(created_at))
            preview = (task_desc[:80] if task_desc else "")
            events.append(f"[{timestamp}] {event_type} ({decision}): {preview}")

        conn.close()
        return events[:5]
    except Exception as e:
        print(f"Warning: Failed to extract CIEU events: {e}", file=sys.stderr)
        return []


def extract_continuation_state(company_root: Path) -> Dict:
    """Extract continuation state"""
    continuation_file = company_root / "memory/continuation.json"
    if not continuation_file.exists():
        return {}

    try:
        return json.loads(continuation_file.read_text())
    except Exception:
        return {}


def generate_wisdom_package(company_root: Path, session_id: str, session_start: float) -> str:
    """Generate wisdom package markdown (≤ 10KB)"""

    wisdom = []

    wisdom.append(f"# Session Wisdom Package — {session_id}")
    wisdom.append(f"Generated: {time.strftime('%Y-%m-%d %H:%M:%S')}")
    wisdom.append(f"Session started: {time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(session_start))}")
    wisdom.append("")
    wisdom.append("---")
    wisdom.append("")

    # 1. Core Decisions
    decisions = extract_core_decisions(company_root, session_start)
    wisdom.append("## Core Decisions (Top 5)")
    wisdom.append("")
    if decisions:
        for i, decision in enumerate(decisions, 1):
            wisdom.append(f"{i}. {decision}")
    else:
        wisdom.append("(No major decisions recorded)")
    wisdom.append("")

    # 2. New Knowledge
    knowledge = extract_new_knowledge(company_root, session_start)
    wisdom.append("## New Knowledge/Patterns (Top 3)")
    wisdom.append("")
    if knowledge:
        for i, item in enumerate(knowledge, 1):
            wisdom.append(f"{i}. {item}")
    else:
        wisdom.append("(No new knowledge recorded)")
    wisdom.append("")

    # 3. Uncompleted Obligations
    obligations = extract_uncompleted_obligations(company_root)
    wisdom.append("## Active Obligations / Next Actions")
    wisdom.append("")
    if obligations:
        for i, obl in enumerate(obligations[:5], 1):  # Top 5 only
            wisdom.append(f"- {obl}")
    else:
        wisdom.append("(No active obligations)")
    wisdom.append("")

    # 4. Methodologies
    methodologies = extract_methodologies(company_root, session_start)
    wisdom.append("## New Methodologies/Genes (Top 3)")
    wisdom.append("")
    if methodologies:
        for i, method in enumerate(methodologies, 1):
            wisdom.append(f"{i}. {method}")
    else:
        wisdom.append("(No new methodologies recorded)")
    wisdom.append("")

    # 5. Recent CIEU Events
    cieu_events = extract_recent_cieu_events(company_root, session_start)
    wisdom.append("## Recent Important Events (Last 5)")
    wisdom.append("")
    if cieu_events:
        for event in cieu_events:
            wisdom.append(f"- {event}")
    else:
        wisdom.append("(No events recorded)")
    wisdom.append("")

    # 6. Continuation State Summary
    continuation = extract_continuation_state(company_root)
    wisdom.append("## Continuation State")
    wisdom.append("")
    if continuation:
        campaign = continuation.get("campaign", {})
        if campaign:
            wisdom.append(f"**Campaign**: {campaign.get('name', 'unknown')} (Day {campaign.get('day', '?')})")
            wisdom.append(f"**Target**: {campaign.get('target', 'unknown')}")
            wisdom.append("")

        team_state = continuation.get("team_state", {})
        if team_state:
            wisdom.append("**Team State**:")
            for role, state in team_state.items():
                task_preview = state.get("task", "")[:60]
                progress = state.get("progress", "unknown")
                wisdom.append(f"- {role}: {task_preview} [{progress}]")
            wisdom.append("")

        action_queue = continuation.get("action_queue", [])
        if action_queue:
            wisdom.append(f"**Next Actions**: {len(action_queue)} items queued")
    else:
        wisdom.append("(No continuation state)")

    wisdom.append("")
    wisdom.append("---")
    wisdom.append("")
    wisdom.append("**This is your immediate past. You just woke up. Continue from here.**")

    return "\n".join(wisdom)


def main():
    company_root = Path(__file__).parent.parent

    # Get session start time (use .session_booted as proxy)
    boot_marker = company_root / "scripts/.session_booted"
    if boot_marker.exists():
        session_start = boot_marker.stat().st_mtime
    else:
        session_start = time.time() - 3600  # Default: 1 hour ago

    session_id = get_session_id(company_root)

    # Generate wisdom package
    wisdom_text = generate_wisdom_package(company_root, session_id, session_start)

    # Check size
    wisdom_bytes = len(wisdom_text.encode('utf-8'))
    wisdom_kb = wisdom_bytes / 1024.0

    if wisdom_kb > 10.0:
        print(f"Warning: Wisdom package is {wisdom_kb:.1f} KB (target: ≤10 KB)", file=sys.stderr)
        print("Truncating to meet target...", file=sys.stderr)
        # Truncate to ~10KB
        max_chars = int(10 * 1024 * 0.9)  # 90% of 10KB to be safe
        wisdom_text = wisdom_text[:max_chars] + "\n\n... (truncated to meet 10KB limit)"

    # Write to memory/
    memory_dir = company_root / "memory"
    memory_dir.mkdir(exist_ok=True)

    output_path = memory_dir / f"wisdom_package_{session_id}.md"
    latest_path = memory_dir / "wisdom_package_latest.md"

    output_path.write_text(wisdom_text)

    # Create symlink for latest
    if latest_path.exists() or latest_path.is_symlink():
        latest_path.unlink()
    latest_path.symlink_to(output_path.name)

    print(f"Wisdom package generated: {output_path}")
    print(f"Size: {wisdom_kb:.2f} KB")
    print(f"Latest link: {latest_path}")

    return 0


if __name__ == "__main__":
    sys.exit(main())
