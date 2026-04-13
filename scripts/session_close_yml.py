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


def update_priority_brief(company_root: Path, session_start_ts: float):
    """AMENDMENT-009 §2.3: check priority_brief.md freshness at session close.

    - If missing → generate stub with {{TODO}} markers; warn CEO must fill
    - If mtime < session_start_ts → warn CEO did not update this session
    - Emit PRIORITY_BRIEF_CHECK CIEU event and set .ystar_session_flags
    """
    brief = company_root / "reports" / "priority_brief.md"
    flags_path = company_root / ".ystar_session_flags"
    stub = """---
version: stub
status: _stub_unfilled_
---
# CEO Priority Brief (STUB — must be filled by CEO before next boot)

## 1. 当前 Labs 阶段
{{TODO}}

## 2. Top-5 真实优先级
### P0-1 {{TODO}}

## 3. DEPRECATED 清单
{{TODO}}

## 4. 下次 boot 不要做什么
{{TODO}}

## 5. Board shell 解锁清单
{{TODO}}

## 6. 本 brief 的 enforce 规则
见 AMENDMENT-009。
"""
    decision = "allow"
    if not brief.exists():
        brief.parent.mkdir(parents=True, exist_ok=True)
        brief.write_text(stub)
        print(f"[WARN] priority_brief.md missing — generated stub at {brief}", file=sys.stderr)
        with open(flags_path, "a") as f:
            f.write("PRIORITY_BRIEF_STALE=1\n")
        decision = "warn"
    else:
        mtime = brief.stat().st_mtime
        if mtime < session_start_ts:
            print(f"[WARN] priority_brief.md not updated this session (mtime={mtime} < session_start={session_start_ts})", file=sys.stderr)
            with open(flags_path, "a") as f:
                f.write("PRIORITY_BRIEF_STALE=1\n")
            decision = "warn"

    try:
        sys.path.insert(0, str(YSTAR_GOV_PATH))
        from ystar.adapters.cieu_writer import _write_session_lifecycle
        sess_cfg_path = company_root / ".ystar_session.json"
        sid = "unknown"
        if sess_cfg_path.exists():
            sid = json.loads(sess_cfg_path.read_text()).get("session_id", "unknown")
        _write_session_lifecycle(
            "PRIORITY_BRIEF_CHECK", "ceo", sid,
            str(company_root / ".ystar_cieu.db"),
            {"decision": decision, "brief_exists": brief.exists()},
        )
    except Exception as e:
        print(f"[warn] PRIORITY_BRIEF_CHECK CIEU emit failed: {e}", file=sys.stderr)


def generate_continuation(company_root: Path, agent_id: str, db_path: Path):
    """Generate memory/continuation.json — machine-readable structured state.

    v2: JSON replaces v1 markdown. Parsed by governance_boot.sh Step 10
    and enforced by hook_wrapper.py continuation compliance check.

    Reads from:
    - .ystar_memory.db (obligation memories)
    - knowledge/*/active_task.json (per-role task state)
    - DISPATCH.md (current dispatch state)

    Writes: memory/continuation.json
    """
    import re

    continuation = {
        "generated_at": time.strftime('%Y-%m-%dT%H:%M:%S'),
        "generated_by": agent_id,
    }

    # --- Section 1: Campaign (from highest-priority obligation) ---
    conn = sqlite3.connect(str(db_path))
    obs = conn.execute(
        "SELECT content, created_at FROM memories WHERE memory_type='obligation' ORDER BY created_at DESC"
    ).fetchall()
    conn.close()

    campaign = {"name": "unknown", "day": 1, "start_date": "", "target": ""}
    for content, created_at in obs:
        lower = content.lower()
        if "defuse" in lower or "\u6218\u5f79" in lower:
            campaign["name"] = "Y*Defuse 30\u5929\u6218\u5f79"
            campaign["target"] = "10K users + 20K stars"
            try:
                date_match = re.search(r'Day\s*(\d+)', content)
                if date_match:
                    campaign["day"] = int(date_match.group(1))
                date_match2 = re.search(r'(\d{4}-\d{2}-\d{2})', content)
                if date_match2:
                    campaign["start_date"] = date_match2.group(1)
            except Exception:
                pass
            break
    continuation["campaign"] = campaign

    # --- Section 2: Team state ---
    team_state = {}
    knowledge_dir = company_root / "knowledge"
    role_ids = ["cto", "cmo", "cso", "cfo", "eng-kernel", "eng-platform", "eng-governance", "eng-domains"]
    for role_id in role_ids:
        task_file = knowledge_dir / role_id / "active_task.json"
        if task_file.exists():
            try:
                task = json.loads(task_file.read_text())
                task_name = task.get("intent", {}).get("goal", task.get("task", "unknown"))[:80]
                status = task.get("status", "unknown")
                blocked = task.get("blocked", False)
                team_state[role_id] = {"task": task_name, "progress": status, "blocked": blocked}
            except (json.JSONDecodeError, KeyError):
                team_state[role_id] = {"task": "(parse error)", "progress": "unknown", "blocked": True}
    continuation["team_state"] = team_state

    # --- Section 3: Action queue (from DISPATCH + team state) ---
    action_queue = []
    dispatch_file = company_root / "DISPATCH.md"
    unchecked = []
    if dispatch_file.exists():
        dispatch_text = dispatch_file.read_text()
        unchecked = [line.strip() for line in dispatch_text.splitlines() if line.strip().startswith("- [ ]")]

    seq = 1
    for role_id, state in team_state.items():
        if state.get("progress") == "in_progress":
            task_file = knowledge_dir / role_id / "active_task.json"
            action_queue.append({
                "seq": seq,
                "action": "check_delivery",
                "agent": role_id,
                "command": f"cat {task_file}",
                "success_criteria": "task in_progress, not blocked",
                "on_fail": f"dispatch to {role_id.upper()} as P0",
            })
            seq += 1
    if unchecked:
        action_queue.append({
            "seq": seq,
            "action": "review_dispatch",
            "agent": "ceo",
            "command": f"head -40 {dispatch_file}",
            "success_criteria": f"{len(unchecked)} items tracked",
            "on_fail": "update DISPATCH.md",
        })
    continuation["action_queue"] = action_queue

    # --- Section 4: Anti-patterns ---
    continuation["anti_patterns"] = [
        "report_plumbing_to_board",
        "ask_board_approval_for_decided_items",
        "list_choices_instead_of_deciding",
    ]

    # --- Section 5: Obligations summary ---
    continuation["obligations"] = [
        {"content": content[:300], "created_at": created_at}
        for content, created_at in obs
    ]

    # Write to memory/continuation.json
    memory_dir = company_root / "memory"
    memory_dir.mkdir(exist_ok=True)
    continuation_path = memory_dir / "continuation.json"
    continuation_path.write_text(json.dumps(continuation, indent=2, ensure_ascii=False))
    print(f"\nContinuation written: {continuation_path}")
    print(f"  Obligations: {len(obs)}")
    print(f"  Pending DISPATCH items: {len(unchecked)}")
    print(f"  Action queue: {len(action_queue)} items")


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

    # Generate continuation.md for seamless next-session resume
    generate_continuation(company_root, agent_id, db_path)

    # Emit session_close CIEU event (Board 2026-04-11)
    try:
        sys.path.insert(0, str(YSTAR_GOV_PATH))
        from ystar.adapters.cieu_writer import _write_session_lifecycle
        sid = "unknown"
        sess_cfg_path = company_root / ".ystar_session.json"
        if sess_cfg_path.exists():
            sid = json.loads(sess_cfg_path.read_text()).get("session_id", "unknown")
        _write_session_lifecycle(
            "session_close", agent_id, sid, str(cieu_db_path),
            {"summary_preview": summary[:120]},
        )
        print("[ok] session_close CIEU event emitted")
    except Exception as e:
        print(f"[warn] session_close emit failed: {e}", file=sys.stderr)

    # AMENDMENT-009 §2.3: update_priority_brief check
    try:
        update_priority_brief(company_root, session_start)
    except Exception as e:
        print(f"[warn] update_priority_brief failed: {e}", file=sys.stderr)

    # Run priority_brief_validator (target schema enforcement)
    try:
        import subprocess
        validator_script = company_root / "scripts" / "priority_brief_validator.py"
        if validator_script.exists():
            result = subprocess.run(
                [sys.executable, str(validator_script)],
                capture_output=True,
                text=True,
                timeout=10
            )
            if result.returncode != 0:
                print(f"[WARN] priority_brief targets validation failed:\n{result.stderr}", file=sys.stderr)
            else:
                print(f"[ok] priority_brief targets validated: {result.stdout.strip()}")
    except Exception as e:
        print(f"[warn] priority_brief_validator failed: {e}", file=sys.stderr)

    # AMENDMENT-010 §4 S-3: trigger secretary_curate pipeline (skeleton)
    try:
        curate_script = company_root / "scripts" / "secretary_curate.py"
        if curate_script.exists():
            import subprocess
            subprocess.run([sys.executable, str(curate_script), "--trigger", "session_close", "--agent", agent_id],
                           timeout=60, capture_output=True)
            print("[ok] secretary_curate triggered (skeleton — 13-step pipeline not yet implemented)")
    except Exception as e:
        print(f"[warn] secretary_curate trigger failed: {e}", file=sys.stderr)

    # NEW: active_agent home state cleanup (方案 C)
    try:
        marker_path = company_root / ".ystar_active_agent"
        if marker_path.exists():
            current_marker = marker_path.read_text().strip()
            if current_marker and current_marker != "ceo":
                print(f"[CLEANUP] session close with active_agent='{current_marker}', resetting to ceo")
                marker_path.write_text("ceo")
    except Exception as e:
        print(f"[warn] home state cleanup failed: {e}", file=sys.stderr)

    return 0


if __name__ == "__main__":
    sys.exit(main())
