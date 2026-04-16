#!/usr/bin/env python3
"""
W10 — Stop Hook: Post-reply prose scan
Purpose: Scan CEO assistant reply after Claude finishes (Stop event), detect
  defer_language / choice_question / drift keywords, emit CIEU event.
  Warn-level only (does NOT block, reply already sent). Fail-open.

Wiring: .claude/settings.json `hooks.Stop` entry invokes this.
"""
import json
import os
import re
import sqlite3
import sys
import time
import uuid
from pathlib import Path

REPO_ROOT = Path("/Users/haotianliu/.openclaw/workspace/ystar-company")
CIEU_DB = REPO_ROOT / ".ystar_cieu.db"

# ═══ WHITELIST DESIGN (Board 2026-04-15 night) ═══
# CEO 只有两种合法状态。不在白名单 = deny。
# 比黑名单（N 个 defer 词永远追不完）根本性优越。
#
# State A: Board 工作状态（Board 在线 → 执行 Board 指令）
# State B: 自主工作学习状态（Board 离线 → Article 11 / 系统测试 / 学习 / 长期设计）
# 没有第三种状态。"idle" / "等指令" / "报告完等下步" 不存在。

# ACTION-ONLY whitelist (Board 2026-04-15 night root fix — topic keywords 被剥离)
# 原设计 bug: "Rt+1/归零/Campaign" 是 topic keywords 不是 action，reply 提到 topic
# 就被当 "在工作"，实际零 action = idle 伪装进白名单后门。
WORK_SIGNALS = [
    # ONLY tool call evidence (CEO 真在做事)
    "commit", "push", "Bash", "Edit", "Write", "Agent", "grep", "Read",
    "pytest", "python3", "git ", "dispatch",
    # ONLY active verb (CEO 说下一步具体动作)
    "立刻", "正在",
    # sub-agent EXPLICIT spawn reference (含 agent_id 前缀才算)
    "派 Ethan", "派 Maya", "派 Leo", "派 Ryan", "派 Samantha", "派 Sofia", "派 Marco", "派 Zara",
    "sub-agent 派",
]

# ═══ STATE MACHINE WHITELIST (Board 2026-04-15 night 真根治) ═══
# 黑名单永远列不完。CEO 只有 3 个合法 state，其他全 deny:
#
# STATE_BOARD_DIRECTIVE: 正在执行 Board 明确指令的任务
# STATE_AUTONOMOUS_WORK: 既有 active campaign 未 Rt+1=0，继续推进
# STATE_BOARD_STOP:      Board 明确指令停止 (唯一合法停止)
#
# Reply 必须含 ≥1 of these state-evidence patterns (whitelist):

import re

STATE_EVIDENCE_PATTERNS = [
    # Pattern 1: commit hash evidence (CEO/sub-agent 真 ship 了)
    re.compile(r'\b[0-9a-f]{7,40}\b'),  # git short/full hash
    # Pattern 2: 显式 dispatch (派 + 任意 agent name OR sub-agent ID)
    re.compile(r'派\s*(Ethan|Maya|Leo|Ryan|Samantha|Sofia|Marco|Zara|sub-agent)'),
    re.compile(r'\b(a[0-9a-f]{16})\b'),  # sub-agent id pattern (today's format)
    # Pattern 3: Board 直接引用 (含"老大"/"Board"+ 任务 quote)
    re.compile(r'(老大|Board)[^\n]{0,80}["「『]'),
    # Pattern 4: tool action evidence (commit/push/edit/agent 真发生)
    re.compile(r'(commit|push|Edit|Write|Bash|Agent|Read|Grep)\s*\(?[^\s]'),
    # Pattern 5: Rt+1 verify action (实际归零证据，非 topic mention)
    re.compile(r'Rt\+1\s*=\s*0\s*[✓✅]'),
    # Pattern 6: Board explicit stop quote
    re.compile(r'Board\s*(明令停|说停|说收工|stop|今晚到这)'),
]

# 任意 1 pattern match = STATE 在白名单 = allow
# 0 pattern match = STATE_UNDEFINED = drift event


def _read_last_assistant_reply(payload: dict) -> str:
    """Try to extract the latest assistant reply from hook payload."""
    # Claude Code Stop hook payload shape is evolving; best-effort extract
    txt = payload.get("assistant_message", "") or payload.get("reply_text", "")
    if txt:
        return txt
    # Fallback: read session transcript if path given
    tp = payload.get("transcript_path")
    if tp and Path(tp).exists():
        try:
            lines = Path(tp).read_text(encoding="utf-8").strip().split("\n")
            for line in reversed(lines[-20:]):
                try:
                    obj = json.loads(line)
                    if obj.get("role") == "assistant":
                        content = obj.get("content", "")
                        if isinstance(content, list):
                            for block in content:
                                if block.get("type") == "text":
                                    return block.get("text", "")
                        return str(content)
                except Exception:
                    continue
        except Exception:
            pass
    return ""


def _scan(text: str) -> dict:
    """STATE MACHINE WHITELIST (Board 2026-04-15 night 真根治).
    CEO 只有 3 合法 state. Reply 必须含 ≥1 STATE_EVIDENCE_PATTERN.
    任何不在白名单的 state = STATE_UNDEFINED drift.
    根本性优于黑名单（永远列不完）。"""
    if not text:
        return {"triggered": False, "rules": []}
    rules_triggered = []

    # WHITELIST: 任意 1 pattern match = legal state
    matched_patterns = []
    for pattern in STATE_EVIDENCE_PATTERNS:
        if pattern.search(text):
            matched_patterns.append(pattern.pattern[:60])

    if not matched_patterns:
        rules_triggered.append({
            "rule": "state_undefined_drift",
            "detail": "CEO reply 不在合法 state 白名单 (BOARD_DIRECTIVE/AUTONOMOUS_WORK/BOARD_STOP). 缺 ≥1 of: commit hash / dispatch (派 <agent>) / Board quote / tool action / Rt+1=0✓ / Board explicit stop. 此 reply 等价 IDLE/UNDEFINED."
        })

    # Legacy choice pattern check (still useful as explicit violation)
    CHOICE_PATTERNS = [
        r"请选择.*[方案]?\s*[12二]",
        r"Option [AB]",
        r"\b1[\)）]\s*.*2[\)）]",
        r"方案[12一二]",
    ]
    for pat in CHOICE_PATTERNS:
        if re.search(pat, text):
            rules_triggered.append({"rule": "choice_question_in_reply", "pattern": pat})
            break
    return {"triggered": bool(rules_triggered), "rules": rules_triggered}


def _emit_cieu(event_type: str, metadata: dict) -> None:
    try:
        conn = sqlite3.connect(str(CIEU_DB), timeout=2.0)
        conn.execute(
            "INSERT INTO cieu_events (event_id, seq_global, created_at, session_id, agent_id, event_type, decision, passed, task_description) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)",
            (
                str(uuid.uuid4()),
                0,
                time.time(),
                "reply_scan",
                "ceo",
                event_type,
                "warn",
                1,
                json.dumps(metadata, ensure_ascii=False)[:500],
            ),
        )
        conn.commit()
        conn.close()
    except Exception:
        pass  # fail-open


def main():
    try:
        payload = json.loads(sys.stdin.read() or "{}")
    except Exception:
        payload = {}
    reply = _read_last_assistant_reply(payload)
    scan = _scan(reply)
    if scan["triggered"]:
        for r in scan["rules"]:
            _emit_cieu("DEFER_IN_REPLY_DRIFT" if r["rule"] == "defer_in_reply" else "CHOICE_IN_REPLY_DRIFT", r)
    # Stop hook: never block, always exit 0
    print(json.dumps({"action": "allow", "scanned": scan["triggered"]}))
    sys.exit(0)


if __name__ == "__main__":
    main()
