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
import yaml
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


ROLES_V2 = ["ceo", "cto", "cmo", "cso", "cfo", "secretary",
            "eng-kernel", "eng-platform", "eng-governance", "eng-domains"]


def extract_priority_brief(company_root: Path) -> str:
    """AMENDMENT-009 §3.4: inject priority_brief.md integrally (highest weight)."""
    brief = company_root / "reports" / "priority_brief.md"
    if not brief.exists():
        return ""
    return brief.read_text(errors="replace")[:8192]


def extract_experiments_verdicts(company_root: Path) -> List[str]:
    exp_dir = company_root / "reports" / "experiments"
    if not exp_dir.exists():
        return []
    out = []
    for f in sorted(exp_dir.glob("*.md"))[-10:]:
        text = f.read_text(errors="replace")
        for line in text.splitlines():
            if any(k in line.lower() for k in ["verdict", "go/no-go", "result:"]):
                out.append(f"{f.name}: {line.strip()[:160]}")
                break
    return out


def extract_role_knowledge(company_root: Path, role: str) -> Dict[str, List[str]]:
    kn = company_root / "knowledge" / role
    buckets = {"feedback": [], "decisions": [], "lessons": [], "theory": [],
               "dead_paths": [], "cases": [], "gaps": []}
    for k in buckets:
        d = kn / k
        if not d.exists():
            continue
        for f in sorted(d.glob("*.md"))[-5:]:
            try:
                first_line = f.read_text(errors="replace").splitlines()[0] if f.read_text(errors="replace").strip() else f.name
            except Exception:
                first_line = f.name
            buckets[k].append(f"{f.name}: {first_line[:120]}")
    return buckets


def extract_git_diff_stat(company_root: Path) -> str:
    import subprocess
    try:
        r = subprocess.run(["git", "diff", "HEAD~3..HEAD", "--stat"],
                           cwd=str(company_root), capture_output=True, timeout=5, text=True)
        return r.stdout[:2048]
    except Exception:
        return ""


def extract_proposals_summary(company_root: Path) -> List[str]:
    pd = company_root / "reports" / "proposals"
    if not pd.exists():
        return []
    out = []
    for f in sorted(pd.glob("*.md"))[-10:]:
        text = f.read_text(errors="replace")
        status = "?"
        for line in text.splitlines()[:20]:
            m = re.search(r"status[:\s]+([A-Z_ ]+)", line, re.IGNORECASE)
            if m:
                status = m.group(1).strip()
                break
        title = text.splitlines()[0] if text else f.name
        out.append(f"{f.name}: [{status}] {title[:120]}")
    return out


def generate_boot_package_for_role(company_root: Path, role: str, session_id: str,
                                    session_start: float) -> dict:
    """AMENDMENT-010 §4 S-2 + §5: per-role 11-category boot pack."""
    brief = extract_priority_brief(company_root)
    role_knowledge = extract_role_knowledge(company_root, role)
    experiments = extract_experiments_verdicts(company_root)
    git_stat = extract_git_diff_stat(company_root)
    proposals = extract_proposals_summary(company_root)
    obligations = extract_uncompleted_obligations(company_root)
    continuation = extract_continuation_state(company_root)
    cieu = extract_recent_cieu_events(company_root, session_start)

    # Generate next-session action queue (category_11)
    action_queue = populate_category_11_actions(company_root, role, obligations, brief, cieu)

    pack = {
        "pack_meta": {
            "role": role,
            "session_id": session_id,
            "generated_at": int(time.time()),
            "generator": "session_wisdom_extractor.py v2 (AMENDMENT-010)",
            "schema_version": "0.1",
        },
        "category_1_identity_dna": {
            "active_agent_marker_path": ".ystar_active_agent",
            "note": "Identity DNA loaded from AGENTS.md + team_dna.md via session_boot_yml.py",
        },
        "category_2_constitutional_charter": {
            "note": "Charter loaded from governance/BOARD_CHARTER_AMENDMENTS.md + INTERNAL_GOVERNANCE.md",
        },
        "category_3_role_mandate": {
            "role": role,
            "knowledge_dir": f"knowledge/{role}/role_definition/",
        },
        "category_4_process_frameworks": {
            "note": "methodology_v1.md + strategy_frameworks.md + decision_making.md",
        },
        "category_5_skills": {
            "skills_dir": f"knowledge/{role}/skills/",
            "skills_registered": [],
        },
        "category_6_current_state": {
            "priority_brief_snippet": brief[:2048],
            "continuation": continuation,
            "open_obligations": obligations[:10],
        },
        "category_7_historical_truth": {
            "git_diff_stat": git_stat,
            "recent_cieu": cieu[:10],
        },
        "category_8_anti_patterns": {
            k: v for k, v in role_knowledge.items()
        },
        "category_9_relationship_map": {
            "board_mental_model_path": f"knowledge/{role}/board_mental_model.md",
        },
        "category_10_external_commitments": {
            "log_path": "knowledge/cso/external_commitments_log.md",
        },
        "category_11_action_queue": {
            "generated_at": int(time.time()),
            "session_id": session_id,
            "actions": action_queue
        },
        "_inputs": {
            "experiments_verdicts": experiments[:5],
            "proposals_summary": proposals[:5],
        },
    }
    return pack


def generate_boot_packages_v2(company_root: Path, session_id: str, session_start: float) -> List[Path]:
    """Generate memory/boot_packages/{role}.json x 10 roles."""
    out_dir = company_root / "memory" / "boot_packages"
    out_dir.mkdir(parents=True, exist_ok=True)
    history_dir = out_dir / "history"
    history_dir.mkdir(exist_ok=True)

    written = []
    for role in ROLES_V2:
        pack = generate_boot_package_for_role(company_root, role, session_id, session_start)
        fn = out_dir / f"{role}.json"
        fn.write_text(json.dumps(pack, ensure_ascii=False, indent=2))
        hist_fn = history_dir / f"{role}_{session_id}.json"
        hist_fn.write_text(json.dumps(pack, ensure_ascii=False, indent=2))
        written.append(fn)
    return written


import re


def populate_category_11_actions(company_root: Path, role: str, obligations: List[str],
                                   brief: str, cieu: List[str]) -> List[Dict]:
    """Populate category_11 action queue from priority_brief, obligations, CIEU hints.

    Sources (in priority order):
    1. priority_brief.md today_targets where owner=role
    2. Pending obligations (from extract_uncompleted_obligations)
    3. CIEU hints from OFF_TARGET/IDLE_PULL events

    Each action must include: action, why, how_to_verify, priority
    """
    actions = []

    # Source 1: priority_brief.md today_targets
    priority_brief_path = company_root / "reports/priority_brief.md"
    if priority_brief_path.exists():
        try:
            import yaml
            content = priority_brief_path.read_text()

            # Extract YAML front matter
            if content.startswith("---"):
                parts = content.split("---", 2)
                if len(parts) >= 3:
                    yaml_content = parts[1]
                    front_matter = yaml.safe_load(yaml_content)

                    today_targets = front_matter.get("today_targets", [])
                    for target in today_targets:
                        if target.get("owner") == role:
                            actions.append({
                                "action": target.get("target", "Unknown target"),
                                "why": f"Priority brief today_targets for {role}",
                                "how_to_verify": target.get("verify", "Target completion verified"),
                                "deadline": target.get("deadline", "EOD"),
                                "priority": "P0"
                            })
        except Exception as e:
            print(f"Warning: Failed to parse priority_brief for {role}: {e}", file=sys.stderr)

    # Source 2: Pending obligations
    for obl in obligations[:3]:  # Top 3 obligations
        if role in obl.lower() or "all" in obl.lower():
            actions.append({
                "action": obl,
                "why": "Pending obligation from previous session",
                "how_to_verify": "Obligation marked as completed in tracking",
                "priority": "P1"
            })

    # Source 3: CIEU hints (OFF_TARGET, IDLE_PULL)
    cieu_db = company_root / ".ystar_cieu.db"
    if cieu_db.exists():
        try:
            conn = sqlite3.connect(str(cieu_db))
            cursor = conn.execute("""
                SELECT event_type, task_description, params_json
                FROM cieu_events
                WHERE event_type IN ('OFF_TARGET', 'IDLE_PULL')
                ORDER BY created_at DESC
                LIMIT 5
            """)

            for event_type, task_desc, params_json in cursor.fetchall():
                hint = task_desc or ""
                if params_json:
                    try:
                        params = json.loads(params_json)
                        hint = params.get("hint", hint)
                    except:
                        pass

                if hint:
                    actions.append({
                        "action": f"Address {event_type}: {hint[:100]}",
                        "why": f"CIEU {event_type} event detected",
                        "how_to_verify": f"No new {event_type} events after fix",
                        "priority": "P1"
                    })

            conn.close()
        except Exception as e:
            print(f"Warning: Failed to extract CIEU hints: {e}", file=sys.stderr)

    # Fallback: If no actions found, add default action
    if not actions:
        actions.append({
            "action": "Review priority_brief.md for new assignments",
            "why": "No pending tasks found in wisdom extraction",
            "how_to_verify": "Found actionable items or confirmed no work needed",
            "priority": "P2"
        })

    return actions


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

    # AMENDMENT-010 §6.2: also generate per-role 11-category boot packs (v2)
    try:
        packs = generate_boot_packages_v2(company_root, session_id, session_start)
        print(f"[v2] boot packages generated: {len(packs)} roles -> memory/boot_packages/")
    except Exception as e:
        print(f"[warn] boot_packages v2 generation failed: {e}", file=sys.stderr)

    return 0


if __name__ == "__main__":
    sys.exit(main())
