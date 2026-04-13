#!/usr/bin/env python3
"""AMENDMENT-010 §4 S-3 — Secretary Curation Pipeline (13-step).

PARTIAL IMPLEMENTATION (Steps 1, 2, 5) — Ryan Park, Platform Engineer
Deadline: 72h from 2026-04-13

Steps implemented:
  1. skill_extract         — extract reusable skills from session data
  2. tombstone             — mark stale items as deprecated
  5. next_session_action_queue — generate per-role action queue for next boot

Steps remaining (skeleton):
  3. boot_directive_gen
  4. truth_triangulation
  6. redteam_secretary
  7. skill_lifecycle
  8. article_11_enforce
  9. curation_decision_log
  10. version_diff
  11. secrets_scrub
  12. circuit_breaker
  13. time_layering

Hard red lines (S-4): Secretary does NOT write strategy, decisions,
charter amendments, production code, or external content. This pipeline
ENFORCES those constraints.

Invocation:
    python3 scripts/secretary_curate.py --trigger session_close --agent ceo
"""
from __future__ import annotations

import argparse
import json
import re
import sqlite3
import subprocess
import sys
import time
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

YSTAR_DIR = Path("/Users/haotianliu/.openclaw/workspace/ystar-company")
SESSION_JSON = YSTAR_DIR / ".ystar_session.json"
CIEU_DB = YSTAR_DIR / ".ystar_cieu.db"
MEMORY_DIR = YSTAR_DIR / "memory"
BOOT_PACKAGES = MEMORY_DIR / "boot_packages"
KNOWLEDGE_DIR = YSTAR_DIR / "knowledge"

# S-4 red-line keywords (Secretary must not generate these)
FORBIDDEN_KEYWORDS = [
    "decide", "approve", "commit production", "merge to main",
    "strategy", "board decision", "charter amendment", "external release"
]


def emit_cieu(event_type: str, payload: dict):
    """Emit CIEU event with session tracking."""
    try:
        ygov = YSTAR_DIR.parent / "Y-star-gov"
        sys.path.insert(0, str(ygov))
        from ystar.adapters.cieu_writer import _write_session_lifecycle

        sid = "unknown"
        if SESSION_JSON.exists():
            sid = json.loads(SESSION_JSON.read_text()).get("session_id", "unknown")

        payload["session_id"] = sid
        payload["agent_id"] = "secretary_curate_pipeline"
        _write_session_lifecycle(event_type, "secretary_curate_pipeline", sid, str(CIEU_DB), payload)
    except Exception as e:
        print(f"[warn] CIEU emit failed: {e}", file=sys.stderr)


def check_redline_violation(content: str) -> Optional[str]:
    """Check if generated content violates S-4 red lines.

    Returns violation keyword if found, None otherwise.
    """
    content_lower = content.lower()
    for keyword in FORBIDDEN_KEYWORDS:
        if keyword in content_lower:
            return keyword
    return None


# ============================================================================
# STEP 1: skill_extract — Extract reusable skills from session data
# ============================================================================

def extract_board_corrections(cieu_db: Path, session_start: float) -> List[Dict[str, Any]]:
    """Query CIEU for Board correction events in last 24h."""
    corrections = []
    if not cieu_db.exists():
        return corrections

    try:
        conn = sqlite3.connect(str(cieu_db))
        cursor = conn.execute("""
            SELECT event_type, task_description, params_json, created_at
            FROM cieu_events
            WHERE created_at >= ?
              AND (event_type LIKE '%Board%' OR event_type LIKE '%PIVOT%' OR event_type = 'INTENT_ADJUSTED')
            ORDER BY created_at DESC
            LIMIT 20
        """, (session_start - 86400,))  # Last 24h

        for event_type, task_desc, params_json, created_at in cursor.fetchall():
            corrections.append({
                "type": event_type,
                "description": task_desc or "",
                "params": params_json or "{}",
                "timestamp": created_at
            })
        conn.close()
    except Exception as e:
        print(f"[warn] CIEU query failed in extract_board_corrections: {e}", file=sys.stderr)

    return corrections


def extract_behavior_changes() -> List[str]:
    """Get recent git diff to identify behavior changes."""
    try:
        result = subprocess.run(
            ["git", "diff", "HEAD~5", "HEAD", "--stat"],
            capture_output=True, text=True, cwd=str(YSTAR_DIR), timeout=10
        )
        if result.returncode == 0:
            return result.stdout.split("\n")
        return []
    except Exception as e:
        print(f"[warn] git diff failed: {e}", file=sys.stderr)
        return []


def identify_skill_patterns(
    corrections: List[Dict[str, Any]],
    wisdom_package_path: Path,
    handoff_path: Path
) -> List[Dict[str, str]]:
    """Identify reusable skill patterns from Board corrections.

    Pattern: Board correction → CEO/role produces concrete method → reusable

    Returns list of skill drafts (not yet formatted as Hermes 4-section).
    """
    patterns = []

    # Read wisdom package for recent events
    wisdom_content = ""
    if wisdom_package_path.exists():
        wisdom_content = wisdom_package_path.read_text()

    # Read handoff for ending state
    handoff_content = ""
    if handoff_path.exists():
        handoff_content = handoff_path.read_text()

    # Pattern 1: Board correction + immediate agent response
    for correction in corrections:
        desc = correction.get("description", "")
        if not desc:
            continue

        # Check if this correction led to a new procedure
        # (Simplified heuristic: look for procedural language in nearby context)
        if any(word in desc.lower() for word in ["must", "should", "always", "never", "禁止", "必须"]):
            patterns.append({
                "trigger_event": correction["type"],
                "context": desc[:200],
                "source": "board_correction",
                "timestamp": correction["timestamp"]
            })

    # TODO: More sophisticated pattern matching (LLM-based extraction)
    # For MVP, we identify 2 simple patterns:
    # 1. Repeated keywords in corrections
    # 2. New constraints mentioned in wisdom package

    return patterns[:2]  # MVP: limit to 2 patterns


def format_skill_draft(pattern: Dict[str, str], session_id: str) -> str:
    """Format skill pattern as Hermes 4-section draft.

    Sections: trigger / procedure / principles / red_lines
    """
    timestamp = int(pattern.get("timestamp", time.time()))
    dt = datetime.fromtimestamp(timestamp)

    trigger_event = pattern.get("trigger_event", "unknown")
    context = pattern.get("context", "")

    # Generate skill name from trigger event
    skill_name = f"skill_{trigger_event.lower().replace('_', '-')}_{session_id[:8]}"

    draft = f"""# Skill: {skill_name} (DRAFT)

**Type**: Hermes skill (4-section)
**Extracted from**: Session {session_id}
**Date**: {dt.strftime('%Y-%m-%d')}
**Status**: DRAFT — requires role owner signature to activate

---

## 1. Trigger

When: {trigger_event}

Context:
{context}

## 2. Procedure

[TODO: Role owner must fill in concrete steps]

1. Identify [X]
2. Execute [Y]
3. Verify [Z]

## 3. Principles

- [TODO: Underlying principles that make this procedure work]

## 4. Red Lines

- DO NOT [TODO: Common pitfalls to avoid]

---

**Note**: This is an AUTOMATICALLY GENERATED DRAFT from Secretary curation.
Role owner MUST review, revise, and sign before this becomes active.
"""
    return draft


def step1_skill_extract(ctx: dict) -> dict:
    """Step 1: Extract skills from session data and write to _draft/."""
    session_start = time.time() - 3600  # Last 1h (simplified)

    # Data sources
    wisdom_pkg = MEMORY_DIR / "wisdom_package_latest.md"
    handoff = MEMORY_DIR / "session_handoff.md"

    corrections = extract_board_corrections(CIEU_DB, session_start)
    behavior_changes = extract_behavior_changes()

    patterns = identify_skill_patterns(corrections, wisdom_pkg, handoff)

    skills_drafted = []
    for pattern in patterns:
        # Determine target role (simplified: default to ceo)
        # TODO: More sophisticated role detection
        role = "ceo"

        skill_draft_dir = KNOWLEDGE_DIR / role / "skills" / "_draft_"
        skill_draft_dir.mkdir(parents=True, exist_ok=True)

        session_id = ctx.get("session_id", "unknown")
        draft_content = format_skill_draft(pattern, session_id)

        # Check red-line violation
        violation = check_redline_violation(draft_content)
        if violation:
            emit_cieu("REDLINE_VIOLATION", {
                "step": "skill_extract",
                "keyword": violation,
                "role": role,
                "action": "rejected"
            })
            continue

        # Write draft
        skill_name = f"skill_{pattern['trigger_event'].lower()[:20]}_{session_id[:8]}.md"
        skill_file = skill_draft_dir / skill_name
        skill_file.write_text(draft_content)

        skills_drafted.append(str(skill_file))
        emit_cieu("SKILL_DRAFT_CREATED", {
            "skill_file": str(skill_file),
            "role": role,
            "trigger": pattern["trigger_event"]
        })

    return {
        "step": 1,
        "name": "skill_extract",
        "status": "implemented",
        "skills_drafted": len(skills_drafted),
        "files": skills_drafted,
        "corrections_analyzed": len(corrections),
        "patterns_found": len(patterns)
    }


# ============================================================================
# STEP 2: tombstone — Mark stale items as deprecated
# ============================================================================

def scan_tombstone_headers() -> List[Tuple[Path, str]]:
    """Scan DISPATCH.md and BOARD_PENDING.md for tombstone headers."""
    tombstoned = []

    for file in [YSTAR_DIR / "DISPATCH.md", YSTAR_DIR / "BOARD_PENDING.md"]:
        if not file.exists():
            continue

        content = file.read_text()
        # Pattern: ## TOMBSTONE or DEPRECATED header
        if "TOMBSTONE" in content or "DEPRECATED" in content:
            tombstoned.append((file, "has_tombstone_header"))

    return tombstoned


def check_stale_tasks(role: str, active_task_path: Path, wisdom_content: str) -> List[str]:
    """Check if tasks in active_task.json are stale.

    Stale = Board hasn't mentioned in this session + >72h since update + has dead_path match
    """
    stale = []
    if not active_task_path.exists():
        return stale

    try:
        tasks = json.loads(active_task_path.read_text())

        # Handle case where tasks might be a list or not a dict
        if not isinstance(tasks, dict):
            return stale

        current_time = time.time()

        for task_id, task_data in tasks.items():
            # Skip if task_data is not a dict (malformed data)
            if not isinstance(task_data, dict):
                continue

            # Check timestamp (72h threshold)
            mtime = task_data.get("updated_at", 0)
            if current_time - mtime < 72 * 3600:
                continue  # Not stale yet

            # Check if mentioned in recent wisdom package
            task_name = task_data.get("name", "")
            if task_name and task_name in wisdom_content:
                continue  # Still active

            # TODO: Check dead_path match
            # For MVP, mark as stale if >72h and not in wisdom
            stale.append(task_id)

    except Exception as e:
        print(f"[warn] Failed to check stale tasks for {role}: {e}", file=sys.stderr)

    return stale


def apply_tombstone(task_id: str, role: str, reason: str):
    """Mark task as deprecated in active_task.json."""
    active_task_path = KNOWLEDGE_DIR / role / "active_task.json"
    if not active_task_path.exists():
        return

    try:
        tasks = json.loads(active_task_path.read_text())
        if task_id in tasks:
            tasks[task_id]["status"] = "deprecated"
            tasks[task_id]["deprecated_at"] = time.time()
            tasks[task_id]["deprecation_reason"] = reason

            active_task_path.write_text(json.dumps(tasks, indent=2))

            emit_cieu("TOMBSTONE_APPLIED", {
                "obligation_id": task_id,
                "role": role,
                "reason": reason,
                "detected_via": "stale_task_scan"
            })
    except Exception as e:
        print(f"[warn] Failed to apply tombstone to {task_id}: {e}", file=sys.stderr)


def step2_tombstone(ctx: dict) -> dict:
    """Step 2: Scan and mark stale tasks/campaigns as deprecated."""

    # Scan tombstone headers
    tombstoned_files = scan_tombstone_headers()

    # Read wisdom package for context
    wisdom_pkg = MEMORY_DIR / "wisdom_package_latest.md"
    wisdom_content = ""
    if wisdom_pkg.exists():
        wisdom_content = wisdom_pkg.read_text()

    # Scan active_task.json for each role
    tombstones_applied = []
    roles = ["ceo", "cto", "cmo", "cso", "cfo", "secretary",
             "eng-kernel", "eng-platform", "eng-governance", "eng-domains"]

    for role in roles:
        active_task_path = KNOWLEDGE_DIR / role / "active_task.json"
        if not active_task_path.exists():
            continue

        stale_tasks = check_stale_tasks(role, active_task_path, wisdom_content)
        for task_id in stale_tasks:
            reason = "Stale >72h, not mentioned in recent session"
            apply_tombstone(task_id, role, reason)
            tombstones_applied.append(f"{role}/{task_id}")

    # Write tombstone scan report
    report_path = YSTAR_DIR / "reports" / f"tombstone_scan_{datetime.now().strftime('%Y%m%d')}.md"
    report_path.parent.mkdir(parents=True, exist_ok=True)

    report = f"""# Tombstone Scan Report
Generated: {datetime.now().isoformat()}
Session: {ctx.get('session_id', 'unknown')}

## Files with Tombstone Headers
{chr(10).join(f"- {path}" for path, _ in tombstoned_files)}

## Tasks Marked as Deprecated
{chr(10).join(f"- {task}" for task in tombstones_applied)}

Total tombstones applied: {len(tombstones_applied)}
"""
    report_path.write_text(report)

    return {
        "step": 2,
        "name": "tombstone",
        "status": "implemented",
        "tombstones_applied": len(tombstones_applied),
        "tombstoned_files": len(tombstoned_files),
        "report": str(report_path)
    }


# ============================================================================
# STEP 5: next_session_action_queue — Generate per-role action queue
# ============================================================================

def load_role_context(role: str) -> Dict[str, Any]:
    """Load role context from role_definition, active_task, priority_brief."""
    context = {
        "role": role,
        "role_definition": "",
        "active_tasks": {},
        "priority_brief_section": ""
    }

    # Load role_definition
    role_def_dir = KNOWLEDGE_DIR / role / "role_definition"
    if role_def_dir.exists():
        for file in role_def_dir.glob("*.md"):
            context["role_definition"] += file.read_text() + "\n\n"

    # Load active_task.json
    active_task_path = KNOWLEDGE_DIR / role / "active_task.json"
    if active_task_path.exists():
        try:
            context["active_tasks"] = json.loads(active_task_path.read_text())
        except:
            pass

    # Load priority_brief relevant section
    priority_brief = YSTAR_DIR / "reports" / "priority_brief.md"
    if priority_brief.exists():
        # TODO: Extract role-specific section
        context["priority_brief_section"] = priority_brief.read_text()[:2000]

    return context


def generate_action_queue(role: str, context: Dict[str, Any], new_skills: List[str]) -> List[Dict[str, Any]]:
    """Generate action queue for role's next session.

    Returns list of actions with format:
    {action, why, how_to_verify, on_fail, estimated_minutes, priority}
    """
    actions = []

    # Priority 0: Check if role has any active P0 tasks
    active_tasks = context.get("active_tasks", {})
    p0_tasks = [t for t in active_tasks.values()
                if isinstance(t, dict) and t.get("priority") == "P0" and t.get("status") != "deprecated"]

    if p0_tasks:
        for task in p0_tasks[:2]:  # Limit to 2 P0 tasks
            actions.append({
                "action": f"Resume P0 task: {task.get('name', 'unknown')}",
                "why": "P0 task incomplete from previous session",
                "how_to_verify": f"Check task status in {role}/active_task.json",
                "on_fail": "Report to CEO as blocked",
                "estimated_minutes": 30,
                "priority": "P0"
            })

    # Priority 1: Apply new skills learned in this session
    if new_skills:
        actions.append({
            "action": f"Review and sign {len(new_skills)} new skill draft(s)",
            "why": "Secretary extracted reusable skills from last session",
            "how_to_verify": f"Check knowledge/{role}/skills/ for new signed skills",
            "on_fail": "Skills remain in _draft/, not activated",
            "estimated_minutes": 15,
            "priority": "P1"
        })

    # Priority 2: Check for deprecated tasks needing cleanup
    deprecated_tasks = [t for t in active_tasks.values()
                       if isinstance(t, dict) and t.get("status") == "deprecated"]
    if deprecated_tasks:
        actions.append({
            "action": f"Archive {len(deprecated_tasks)} deprecated task(s)",
            "why": "Tombstone scan marked these as stale",
            "how_to_verify": "Deprecated tasks moved to archive/",
            "on_fail": "Tasks stay in active list, cluttering workspace",
            "estimated_minutes": 10,
            "priority": "P2"
        })

    # Fallback: If no specific actions, provide default
    if not actions:
        actions.append({
            "action": "Review priority_brief.md for new assignments",
            "why": "No pending tasks found",
            "how_to_verify": "Found at least one actionable item",
            "on_fail": "Request task from CEO",
            "estimated_minutes": 5,
            "priority": "P1"
        })

    return actions


def step5_next_session_action_queue(ctx: dict, step1_result: dict, step2_result: dict) -> dict:
    """Step 5: Generate per-role action queue for next boot."""

    roles = ["ceo", "cto", "cmo", "cso", "cfo", "secretary",
             "eng-kernel", "eng-platform", "eng-governance", "eng-domains"]

    queues_generated = []

    for role in roles:
        # Load role context
        context = load_role_context(role)

        # Get new skills for this role (from step 1)
        new_skills = [f for f in step1_result.get("files", []) if f"/{role}/" in f]

        # Generate action queue
        action_queue = generate_action_queue(role, context, new_skills)

        # Update boot package
        boot_pack_path = BOOT_PACKAGES / f"{role}.json"
        if boot_pack_path.exists():
            try:
                boot_pack = json.loads(boot_pack_path.read_text())

                # Add or update category_11_action_queue
                boot_pack["category_11_action_queue"] = {
                    "generated_at": time.time(),
                    "session_id": ctx.get("session_id", "unknown"),
                    "actions": action_queue
                }

                boot_pack_path.write_text(json.dumps(boot_pack, indent=2))
                queues_generated.append(role)

                emit_cieu("ACTION_QUEUE_UPDATED", {
                    "role": role,
                    "actions_count": len(action_queue),
                    "priorities": [a["priority"] for a in action_queue]
                })
            except Exception as e:
                print(f"[warn] Failed to update boot pack for {role}: {e}", file=sys.stderr)

    return {
        "step": 5,
        "name": "next_session_action_queue",
        "status": "implemented",
        "roles_updated": len(queues_generated),
        "roles": queues_generated
    }


# ============================================================================
# Skeleton steps (3, 4, 6-13) — kept as stubs
# ============================================================================

SKELETON_STEPS = [
    (3, "boot_directive_gen", "generate per-role JSON + narrative boot pack"),
    (4, "truth_triangulation", "cross-check transcript / CIEU / GitHub / FS"),
    (6, "redteam_secretary", "internal red team on own curation output"),
    (7, "skill_lifecycle", "cold/archive/alert per 5/10 session rule"),
    (8, "article_11_enforce", "emit ARTICLE_11_PASS per substantive edit"),
    (9, "curation_decision_log", "CIEU for every edit decision"),
    (10, "version_diff", "persist boot_packages/history/{role}_{ts}.json"),
    (11, "secrets_scrub", "redact .env patterns, key signatures"),
    (12, "circuit_breaker", "3x No-Go -> disable, alert Board"),
    (13, "time_layering", "split actions: immediate / session / campaign"),
]


def run_skeleton_step(idx: int, name: str, desc: str, ctx: dict) -> dict:
    """Skeleton stub for unimplemented steps."""
    emit_cieu("SECRETARY_CURATION_DECISION", {
        "step": idx,
        "name": name,
        "desc": desc,
        "status": "skeleton_noop",
        "trigger": ctx.get("trigger"),
        "agent": ctx.get("agent")
    })
    return {"step": idx, "name": name, "status": "skeleton_noop"}


# ============================================================================
# Main pipeline
# ============================================================================

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--trigger", default="manual")
    ap.add_argument("--agent", default="unknown")
    args = ap.parse_args()

    # Get session ID
    session_id = "unknown"
    if SESSION_JSON.exists():
        try:
            session_id = json.loads(SESSION_JSON.read_text()).get("session_id", "unknown")
        except:
            pass

    ctx = {
        "trigger": args.trigger,
        "agent": args.agent,
        "session_id": session_id,
        "ts": int(time.time())
    }

    emit_cieu("SECRETARY_CURATE_START", ctx)

    results = []

    # Run implemented steps
    print("[Step 1/13] skill_extract...", file=sys.stderr)
    r1 = step1_skill_extract(ctx)
    results.append(r1)

    print("[Step 2/13] tombstone...", file=sys.stderr)
    r2 = step2_tombstone(ctx)
    results.append(r2)

    # Skeleton step 3-4
    for idx, name, desc in SKELETON_STEPS[:2]:
        results.append(run_skeleton_step(idx, name, desc, ctx))

    print("[Step 5/13] next_session_action_queue...", file=sys.stderr)
    r5 = step5_next_session_action_queue(ctx, r1, r2)
    results.append(r5)

    # Skeleton steps 6-13
    for idx, name, desc in SKELETON_STEPS[2:]:
        results.append(run_skeleton_step(idx, name, desc, ctx))

    # Summary
    implemented_steps = [r for r in results if r.get("status") == "implemented"]
    skeleton_steps = [r for r in results if r.get("status") == "skeleton_noop"]

    emit_cieu("SECRETARY_CURATE_COMPLETE", {
        "steps_run": len(results),
        "implemented": len(implemented_steps),
        "skeleton": len(skeleton_steps),
        **ctx
    })

    summary = {
        "status": "ok",
        "session_id": session_id,
        "steps_total": len(results),
        "steps_implemented": [r["name"] for r in implemented_steps],
        "steps_skeleton": [r["name"] for r in skeleton_steps],
        "results": results
    }

    print(json.dumps(summary, indent=2))
    return 0


if __name__ == "__main__":
    sys.exit(main())
