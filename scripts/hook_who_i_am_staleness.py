#!/usr/bin/env python3
"""
WHO_I_AM Staleness Enforcement (Milestone 10b, 2026-04-21 Board proposal).

Board catch: "我们以前就做过门卫+导游" + "你是不是很久没看 WHO_I_AM" +
"WHO_I_AM reminder 放 enforce 里面, 不仅 Aiden, 全 agent, enforce→omission".

Implementation:
- Per-agent reply counter `.ystar_reply_count_{agent_id}.json`
- Every UserPromptSubmit: increment counter
- At every Nth reply (default N=3): return INJECT payload with WHO_I_AM
  Section 1 Quick Lookup Table + rotating Section snippet
- If agent goes M replies (default M=10) without reading its WHO_I_AM file,
  emit CIEU WHO_I_AM_STALENESS_OVERDUE → OmissionEngine TrackedEntity

Aligns with existing infra (P-12 先查后造):
- router_registry.RouterResult.inject (line 177) — INJECT decision type
- hook.py REDIRECT schema — FIX_COMMAND / SKILL_REF key names
- ppid marker (lock-death #10/#11 fix) — agent_id resolution
- OmissionEngine.TrackedEntity — deadline-driven obligation

M-tag: M-2a (structural enforcement of identity alignment) +
       M-2b (防 agent 漂移不自觉 — counter → omission if stale).
"""
import json
import os
import sys
import time
from pathlib import Path

WORKSPACE = Path("/Users/haotianliu/.openclaw/workspace/ystar-company")
COUNTER_DIR = WORKSPACE / "scripts"

# Per-agent WHO_I_AM file mapping (aligned with knowledge/ directory layout)
WHO_I_AM_MAP = {
    "ceo":       WORKSPACE / "knowledge/ceo/wisdom/WHO_I_AM.md",
    "cto":       WORKSPACE / "knowledge/cto/wisdom/WHO_I_AM_ETHAN.md",
    "secretary": WORKSPACE / "knowledge/secretary/wisdom/WHO_I_AM_SAMANTHA.md",
    # Other agents: WHO_I_AM pending (CZL-MISSING-WHO-I-AM-7-AGENTS P0)
}

DEFAULT_REMINDER_INTERVAL = 3    # inject every N replies
DEFAULT_STALENESS_THRESHOLD = 10  # omission triggers after M replies stale


def _counter_path(agent_id: str) -> Path:
    safe = "".join(c for c in agent_id if c.isalnum() or c in "_-")
    return COUNTER_DIR / f".ystar_reply_count_{safe}.json"


def _read_counter(agent_id: str) -> dict:
    p = _counter_path(agent_id)
    if not p.exists():
        return {"agent_id": agent_id, "reply_count": 0,
                "last_reminder_at_reply": 0, "last_ts": 0.0}
    try:
        return json.loads(p.read_text())
    except Exception:
        return {"agent_id": agent_id, "reply_count": 0,
                "last_reminder_at_reply": 0, "last_ts": 0.0}


def _write_counter(agent_id: str, state: dict) -> None:
    _counter_path(agent_id).write_text(json.dumps(state, indent=2))


def _extract_quick_lookup_table(md_path: Path) -> str:
    """Extract Section 1 "Quick Lookup Table" from WHO_I_AM.md.
    Fallback: first 30 lines after title if Section 1 not found."""
    if not md_path.exists():
        return f"(WHO_I_AM file missing at {md_path.name} — "
    text = md_path.read_text(encoding="utf-8", errors="replace")
    # Find "Section 1" header
    marker = "## Section 1"
    start = text.find(marker)
    if start < 0:
        # Fallback: first 1500 chars
        return text[:1500]
    # Find next "## " after Section 1
    end = text.find("\n## ", start + len(marker))
    if end < 0:
        end = start + 2500
    return text[start:end].strip()[:2500]


def check_staleness(agent_id: str,
                    reminder_interval: int = DEFAULT_REMINDER_INTERVAL,
                    staleness_threshold: int = DEFAULT_STALENESS_THRESHOLD) -> dict:
    """Main entry — return dict {action, inject_text?, warn_text?} per forget_guard semantics.

    Returned action is one of:
      - "none": no inject this reply
      - "inject": include inject_text in next reply context (soft reminder)
      - "warn_overdue": agent is in staleness_overdue, stronger message
    """
    state = _read_counter(agent_id)
    state["reply_count"] = state.get("reply_count", 0) + 1
    state["last_ts"] = time.time()

    last_reminder = state.get("last_reminder_at_reply", 0)
    gap = state["reply_count"] - last_reminder

    action = "none"
    inject_text = ""
    warn_text = ""

    # Overdue check FIRST: past threshold without reminder
    if gap >= staleness_threshold:
        action = "warn_overdue"
        warn_text = (
            f"[Y*] OMISSION WARN: agent={agent_id} WHO_I_AM_STALENESS_OVERDUE "
            f"(reply #{state['reply_count']}, last reminder at "
            f"reply #{last_reminder}, gap={gap} >= {staleness_threshold})\n"
            f"FIX_COMMAND: Read your WHO_I_AM file now and acknowledge "
            f"Section 2 (M Triangle) + Section 5 (17 meta-rules) alignment.\n"
            f"SKILL_REF: {WHO_I_AM_MAP.get(agent_id, 'knowledge/...WHO_I_AM.md')}\n"
        )
        md = WHO_I_AM_MAP.get(agent_id)
        if md:
            inject_text = _extract_quick_lookup_table(md)
        state["last_reminder_at_reply"] = state["reply_count"]

    elif gap >= reminder_interval:
        action = "inject"
        md = WHO_I_AM_MAP.get(agent_id)
        if md:
            inject_text = (
                f"[Y* WHO_I_AM REMINDER — per-agent structural inject]\n"
                f"agent={agent_id}, reply #{state['reply_count']}, "
                f"last reminder #{last_reminder}.\n\n"
                f"Section 1 Quick Lookup Table (use when these情景 hit):\n\n"
                f"{_extract_quick_lookup_table(md)}\n\n"
                f"--- Trigger Section 11 持续迭代协议 if any insight this cycle. ---"
            )
        state["last_reminder_at_reply"] = state["reply_count"]

    _write_counter(agent_id, state)
    return {
        "action": action,
        "agent_id": agent_id,
        "reply_count": state["reply_count"],
        "last_reminder_at_reply": state["last_reminder_at_reply"],
        "gap": gap,
        "inject_text": inject_text,
        "warn_text": warn_text,
    }


def main():
    """Hook entry: read payload from stdin, check staleness, emit inject/warn to stdout."""
    raw = sys.stdin.read() if not sys.stdin.isatty() else ""
    try:
        payload = json.loads(raw) if raw.strip() else {}
    except json.JSONDecodeError:
        payload = {}

    agent_id = (payload.get("agent_id")
                or os.environ.get("YSTAR_ACTIVE_AGENT")
                or "ceo")
    # normalize (strip "ystar-" prefix if present)
    if agent_id.startswith("ystar-"):
        agent_id = agent_id[len("ystar-"):]

    result = check_staleness(agent_id)

    if result["action"] == "inject":
        print(result["inject_text"])
    elif result["action"] == "warn_overdue":
        print(result["warn_text"])
        if result["inject_text"]:
            print(result["inject_text"])
    # action == "none" → silent, no output

    # Always log summary to stderr (hook debug)
    print(f"[who_i_am_staleness] {result['agent_id']} reply#{result['reply_count']} "
          f"action={result['action']} gap={result['gap']}",
          file=sys.stderr)

    # Emit CIEU event for the injection/warn (M-2b auditability)
    if result["action"] != "none":
        try:
            import sqlite3
            cieu_db = WORKSPACE / ".ystar_cieu.db"
            conn = sqlite3.connect(cieu_db)
            event_type = ("WHO_I_AM_REMINDER_INJECTED"
                          if result["action"] == "inject"
                          else "WHO_I_AM_STALENESS_OVERDUE")
            conn.execute("""
                INSERT INTO cieu_events (event_id, seq_global, created_at,
                                         event_type, agent_id, result_json)
                VALUES (?, ?, ?, ?, ?, ?)
            """, (
                f"staleness_{int(time.time()*1_000_000)}",
                int(time.time() * 1_000_000),
                time.time(),
                event_type,
                result["agent_id"],
                json.dumps({
                    "reply_count": result["reply_count"],
                    "gap": result["gap"],
                }),
            ))
            conn.commit()
            conn.close()
        except Exception:
            pass

    return 0


if __name__ == "__main__":
    sys.exit(main())
