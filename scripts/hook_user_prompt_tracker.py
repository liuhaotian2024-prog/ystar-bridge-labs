#!/usr/bin/env python3
"""
[L3] UserPromptSubmit Hook — Proactive Context Injection + Board tracking

On every user message:
1. Update scripts/.ystar_last_board_msg with current timestamp
2. Revoke CEO mode (Board presence → back to standard)
3. INJECT system context into user prompt (L2→L3 AMENDMENT-021)

Registered in .claude/settings.json as UserPromptSubmit hook
"""

import sys
import time
import json
import subprocess
from pathlib import Path
from datetime import datetime

WORKSPACE_ROOT = Path("/Users/haotianliu/.openclaw/workspace/ystar-company")
YGOV_ROOT = Path("/Users/haotianliu/.openclaw/workspace/Y-star-gov")
LAST_BOARD_MSG_FILE = WORKSPACE_ROOT / "scripts/.ystar_last_board_msg"
MODE_MANAGER_SCRIPT = WORKSPACE_ROOT / "scripts/ceo_mode_manager.py"
ACTIVE_AGENT_FILE = WORKSPACE_ROOT / ".ystar_active_agent"
SESSION_JSON = WORKSPACE_ROOT / ".ystar_session.json"
CIEU_DB = WORKSPACE_ROOT / ".ystar_cieu.db"
WHITELIST_MATCHER = WORKSPACE_ROOT / "scripts/whitelist_matcher.py"
INJECT_LOG = Path("/tmp/ystar_user_prompt_hook.log")
DIALOGUE_CONTRACT_LOG = WORKSPACE_ROOT / "scripts/.logs/dialogue_contract.log"
DIALOGUE_CONTRACT_SCRIPT = WORKSPACE_ROOT / "scripts/dialogue_to_contract_worker.py"
CLAUDE_PROJECT_DIR = Path.home() / ".claude/projects/-Users-haotianliu--openclaw-workspace-ystar-company"


def get_active_agent():
    """Read current active agent"""
    try:
        return ACTIVE_AGENT_FILE.read_text().strip()
    except Exception:
        return "unknown"


def get_ceo_mode():
    """Read CEO mode from session.json"""
    try:
        with open(SESSION_JSON) as f:
            data = json.load(f)
            return data.get("ceo_mode", "standard")
    except Exception:
        return "unknown"


def get_session_age():
    """Calculate session age in minutes"""
    try:
        import sqlite3
        conn = sqlite3.connect(CIEU_DB)
        cursor = conn.cursor()
        cursor.execute("""
            SELECT timestamp FROM cieu_events
            WHERE event_type = 'session_start'
            ORDER BY id DESC LIMIT 1
        """)
        row = cursor.fetchone()
        conn.close()
        if row:
            start_time = datetime.fromisoformat(row[0])
            age_seconds = (datetime.now() - start_time).total_seconds()
            return int(age_seconds / 60)
    except Exception:
        pass
    return 0


def get_top_obligations():
    """Get top 3 pending obligations from CIEU"""
    try:
        import sqlite3
        conn = sqlite3.connect(CIEU_DB)
        cursor = conn.cursor()
        cursor.execute("""
            SELECT details FROM cieu_events
            WHERE event_type = 'obligation_created'
            AND details NOT LIKE '%completed%'
            ORDER BY id DESC LIMIT 3
        """)
        rows = cursor.fetchall()
        conn.close()
        return [r[0][:80] for r in rows] if rows else []
    except Exception:
        return []


def get_recent_drift():
    """Get last 5 FORGET_GUARD events from CIEU (last 1h)"""
    try:
        import sqlite3
        conn = sqlite3.connect(CIEU_DB)
        cursor = conn.cursor()
        one_hour_ago = (datetime.now().timestamp() - 3600)
        cursor.execute("""
            SELECT rule_id, details FROM cieu_events
            WHERE event_type = 'FORGET_GUARD'
            AND timestamp > datetime(?, 'unixepoch')
            ORDER BY id DESC LIMIT 5
        """, (one_hour_ago,))
        rows = cursor.fetchall()
        conn.close()
        return [f"{r[0]}: {r[1][:50]}" for r in rows] if rows else []
    except Exception:
        return []


def get_whitelist_hints(user_msg):
    """Get top 3 whitelist entries matching user message"""
    try:
        result = subprocess.run(
            ["python3", str(WHITELIST_MATCHER), user_msg],
            capture_output=True,
            timeout=2,
            text=True
        )
        if result.returncode == 0:
            lines = result.stdout.strip().split('\n')
            return lines[:3] if lines else []
    except Exception:
        pass
    return []


def get_current_session_id():
    """Extract current session ID from CLAUDE_SESSION_ID env or fallback to latest transcript"""
    import os
    session_id = os.environ.get("CLAUDE_SESSION_ID")
    if session_id:
        return session_id

    # Fallback: find most recently modified .jsonl file
    try:
        jsonl_files = list(CLAUDE_PROJECT_DIR.glob("*.jsonl"))
        if jsonl_files:
            latest = max(jsonl_files, key=lambda p: p.stat().st_mtime)
            return latest.stem
    except Exception:
        pass
    return None


def detect_assistant_defer_drift():
    """
    [L7] ForgetGuard: scan last assistant message for defer language.
    Returns (snippet, full_text) if defer detected, else (None, None).
    Fail-open (returns None on any error).
    """
    try:
        session_id = get_current_session_id()
        if not session_id:
            return None, None

        transcript = CLAUDE_PROJECT_DIR / f"{session_id}.jsonl"
        if not transcript.exists():
            return None, None

        # Read last 200 lines (efficient for large transcripts)
        last_assistant_text = None
        with open(transcript, 'r') as f:
            lines = f.readlines()
            for line in reversed(lines[-200:]):
                try:
                    msg = json.loads(line)
                    if msg.get('role') == 'assistant' or msg.get('type') == 'assistant':
                        content = msg.get('message', {}).get('content') or msg.get('content')
                        if isinstance(content, list):
                            for item in content:
                                if isinstance(item, dict) and item.get('type') == 'text':
                                    last_assistant_text = item.get('text', '')
                                    break
                        elif isinstance(content, str):
                            last_assistant_text = content
                        if last_assistant_text:
                            break
                except Exception:
                    continue

        if not last_assistant_text:
            return None, None

        # Defer pattern matching (case-insensitive)
        import re
        defer_patterns = [
            r'明日|明早|下周|下次|未来.*内',
            r'tomorrow|next\s+(session|time|week)',
            r'queued?\s+for|wait\s+for|稍后|later',
            r'TBD|待研究|to\s+be\s+determined',
            r'\d+[-~]\d+\s*月',  # "3-6月"
            r'\d+\s*月内',       # "N月内"
            r'等.*回|等回报',     # CEO's "等回报" pattern
        ]

        for pattern in defer_patterns:
            match = re.search(pattern, last_assistant_text, re.IGNORECASE)
            if match:
                snippet = last_assistant_text[max(0, match.start()-20):match.end()+30]
                return snippet.strip(), last_assistant_text

        return None, None

    except Exception as e:
        # Fail-open: log error but don't block hook
        sys.stderr.write(f"[ASSISTANT_DEFER_DRIFT] parse_error: {e}\n")
        return None, None


def detect_decision_context(user_msg):
    """
    [AMENDMENT-023] Detect strategic decision keywords in user message.
    Returns True if message contains decision-making context requiring Article 11.
    """
    if not user_msg:
        return False

    DECISION_KEYWORDS = [
        "strategy", "mission", "amendment", "重大", "决策", "战略",
        "deploy", "launch", "roadmap", "pivot", "reorg", "restructure",
        "架构", "重组", "发布", "上线", "部署"
    ]

    user_msg_lower = user_msg.lower()
    return any(kw in user_msg_lower for kw in DECISION_KEYWORDS)


def inject_context(user_msg_preview=""):
    """Generate system context injection block"""
    active_agent = get_active_agent()
    ceo_mode = get_ceo_mode()
    session_age = get_session_age()
    obligations = get_top_obligations()
    recent_drift = get_recent_drift()
    whitelist_hints = get_whitelist_hints(user_msg_preview)
    defer_snippet, defer_full_text = detect_assistant_defer_drift()
    is_decision_context = detect_decision_context(user_msg_preview)

    context = f"""<system-context auto-injected="UserPromptSubmit">
[STATE] active_agent={active_agent} | ceo_mode={ceo_mode} | session_age={session_age}min
[OBLIGATIONS] {len(obligations)} pending
"""
    for i, obl in enumerate(obligations, 1):
        context += f"  {i}. {obl}\n"

    # [M-X] CROBA contract injection — consume once
    croba_contract_file = Path(f"/tmp/ystar_contract_inject_{active_agent}.txt")
    if croba_contract_file.exists():
        try:
            croba_content = croba_contract_file.read_text().strip()
            if croba_content:
                context += f"[CROBA_CONTRACT] {croba_content}\n"
            croba_contract_file.unlink()  # Consume once
        except Exception as e:
            sys.stderr.write(f"[CROBA_CONTRACT] read_error: {e}\n")

    if recent_drift:
        context += f"[RECENT_DRIFT] {len(recent_drift)} events (last 1h)\n"
        for drift in recent_drift:
            context += f"  - {drift}\n"

    if whitelist_hints:
        context += "[WHITELIST_HINT] Matching patterns:\n"
        for hint in whitelist_hints:
            context += f"  - {hint}\n"

    # [L7] ForgetGuard: detect defer drift in last assistant reply
    if defer_snippet:
        context += f"[⚠️ LAST_REPLY_DEFER] You wrote \"{defer_snippet}\" in your previous reply.\n"
        context += "  Recipe: respond now with \"I dispatched X NOW\" or \"I am doing X right now\" not future tense.\n"
        # Emit CIEU event
        try:
            import sqlite3
            import uuid
            conn = sqlite3.connect(CIEU_DB)
            cursor = conn.cursor()
            event_id = str(uuid.uuid4())
            seq_global = int(time.time() * 1_000_000)
            session_json = {}
            try:
                with open(SESSION_JSON) as f:
                    session_json = json.load(f)
            except:
                pass
            session_id = session_json.get('session_id', 'unknown')
            cursor.execute("""
                INSERT INTO cieu_events (
                    event_id, seq_global, created_at, session_id, agent_id,
                    event_type, decision, passed, drift_detected, drift_details
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                event_id, seq_global, time.time(), session_id, active_agent,
                "FORGET_GUARD", "warn", 0, 1, defer_snippet[:200]
            ))
            conn.commit()
            conn.close()
            sys.stderr.write(f"[ASSISTANT_DEFER_DRIFT] last reply contains: '{defer_snippet}'\n")
        except Exception as e:
            sys.stderr.write(f"[ASSISTANT_DEFER_DRIFT] cieu_write_error: {e}\n")

    # [AMENDMENT-023] Article 11 Enforcement — Proactive Injection (Layer 1)
    if is_decision_context and active_agent == "ceo":
        context += """
[ARTICLE_11_REQUIRED] This prompt contains strategic decision keywords. CEO must walk 7-layer cognitive construction:
  Layer 0: Y* (ideal contract) — What would Werner Vogels do?
  Layer 1: Pre-session context (twin trace) — Read memory/session_handoff.md
  Layer 2: Decision (counterfactual analysis) — What if I decide X vs Y?
  Layer 3: Memory (session state + LRS) — Check .ystar_session.json + CIEU
  Layer 4: Execution (RAPID + constraints) — Who does what, when?
  Layer 5: Track (emit CIEU events) — python3 scripts/article_11_tracker.py layer_complete --layer X --evidence "..."
  Layer 6: Learn (extract lessons) — What did this decision teach me?

After completing each layer, emit event via:
  python3 scripts/article_11_tracker.py layer_complete --layer N --evidence "brief description"

Before finalizing decision, verify compliance:
  python3 scripts/article_11_tracker.py check_compliance --window_hours 2
"""

    context += "[L_TAG_REMINDER] All status reports must include [LX] tag (Iron Rule 1.5)\n"
    context += "[BREAK_GLASS_AVAILABLE] python3 scripts/ceo_mode_manager.py force_break_glass --trigger T1\n"
    context += "</system-context>\n"

    return context


def trigger_dialogue_contract_translation(user_msg: str):
    """
    AMENDMENT-022: Fork dialogue text to async nl_to_contract pipeline.
    Fire-and-forget background subprocess, emits DIALOGUE_CONTRACT_DRAFT CIEU event.
    """
    if not user_msg or len(user_msg.strip()) < 10:
        return  # Skip empty/trivial messages

    try:
        # Launch background worker (fire-and-forget)
        subprocess.Popen(
            ["python3", str(DIALOGUE_CONTRACT_SCRIPT), user_msg[:1000]],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
            start_new_session=True  # Detach from parent
        )
    except Exception as e:
        # Log error but never fail the hook
        with open(DIALOGUE_CONTRACT_LOG, "a") as f:
            f.write(f"{datetime.now().isoformat()} | spawn_error: {e}\n")


def detect_governance_doc_changes():
    """Gap 3 & Gap 4: Detect changes in AGENTS.md, WORKING_STYLE.md, .claude/agents/*.
    Returns injected context string if changes detected, else empty string."""
    mtime_cache_file = Path("/tmp/ystar_gov_md_mtime.json")
    context_diff = ""

    try:
        # Load previous mtimes
        prev_mtimes = {}
        if mtime_cache_file.exists():
            with open(mtime_cache_file, 'r') as f:
                prev_mtimes = json.load(f)

        current_mtimes = {}
        changed_files = []

        # Track AGENTS.md and WORKING_STYLE.md
        for doc_path in [WORKSPACE_ROOT / "AGENTS.md", WORKSPACE_ROOT / "WORKING_STYLE.md"]:
            if doc_path.exists():
                current_mtime = doc_path.stat().st_mtime_ns
                current_mtimes[str(doc_path)] = current_mtime
                if prev_mtimes.get(str(doc_path), -1) != current_mtime:
                    changed_files.append(str(doc_path.relative_to(WORKSPACE_ROOT)))

        # Track .claude/agents/*.md
        agents_dir = WORKSPACE_ROOT / ".claude" / "agents"
        if agents_dir.exists():
            for agent_file in agents_dir.glob("*.md"):
                current_mtime = agent_file.stat().st_mtime_ns
                current_mtimes[str(agent_file)] = current_mtime
                if prev_mtimes.get(str(agent_file), -1) != current_mtime:
                    changed_files.append(f".claude/agents/{agent_file.name}")

        # If changes detected, inject alert
        if changed_files:
            context_diff = f"\n[⚠️ GOV_DOC_CHANGED] Runtime governance files modified:\n"
            for f in changed_files[:5]:  # Limit to 5 files
                context_diff += f"  - {f}\n"
            context_diff += "  Recipe: If spawning sub-agents, ensure they read updated configs. Consider session restart for full propagation.\n"

        # Save updated mtimes
        with open(mtime_cache_file, 'w') as f:
            json.dump(current_mtimes, f)

    except Exception as e:
        # Fail-open: log error but don't block
        sys.stderr.write(f"[GOV_DOC_CHANGES] detect_error: {e}\n")

    return context_diff

def main():
    """Hook entry point (fail-open, max 500ms)"""
    start_time = time.time()

    try:
        # Update last Board message timestamp
        now = time.time()
        LAST_BOARD_MSG_FILE.write_text(str(now))

        # Gap 3 & Gap 4: Detect governance doc changes
        gov_doc_diff = detect_governance_doc_changes()

        # Revoke CEO mode (Board is back → exit autonomous/break_glass)
        try:
            subprocess.run(
                ["python3", str(MODE_MANAGER_SCRIPT), "revoke"],
                capture_output=True,
                timeout=3
            )
        except subprocess.SubprocessError:
            pass  # Non-critical if mode manager fails

        # Inject context to stdout (Claude Code prepends to user prompt)
        # Read stdin for user message preview (if available)
        user_msg_preview = ""
        if not sys.stdin.isatty():
            try:
                user_msg_preview = sys.stdin.read(1000)  # Read full message for contract analysis
            except Exception:
                pass

        context = inject_context(user_msg_preview[:200])  # Inject uses first 200 chars

        # Append gov doc changes alert (Gap 3 & Gap 4)
        if gov_doc_diff:
            context += gov_doc_diff

        print(context, file=sys.stdout)

        # AMENDMENT-022: Async dialogue→contract translation (non-blocking)
        if user_msg_preview:
            trigger_dialogue_contract_translation(user_msg_preview)

        # Log injection for audit trail
        elapsed_ms = int((time.time() - start_time) * 1000)
        log_entry = f"{datetime.now().isoformat()} | {elapsed_ms}ms | injected {len(context)} chars\n"
        with open(INJECT_LOG, "a") as f:
            f.write(log_entry)
            f.write(context)
            f.write("\n---\n")

    except Exception as e:
        # Fail-open: log error but don't block user message
        with open(INJECT_LOG, "a") as f:
            f.write(f"{datetime.now().isoformat()} | ERROR: {e}\n")


if __name__ == "__main__":
    main()
