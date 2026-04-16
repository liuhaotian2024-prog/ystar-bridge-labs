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

# NEGATIVE patterns: any match → idle disguise, overrides WORK_SIGNALS
IDLE_DISGUISE_PHRASES = [
    "等返回", "等 agent 返回", "等 ... 返回", "等 sub-agent 返回",
    "严守岗位", "严守 岗位",
    "CEO active", "CEO 本线 continue", "CEO 持续 active",
    "等 ceo 接手", "等 Board", "等指令", "等下一步",
    "保持 active 等",
    "CEO 严守",
]

# If reply contains NONE of WORK_SIGNALS OR ANY of IDLE_DISGUISE_PHRASES → drift
# If reply has WORK_SIGNAL AND no IDLE_DISGUISE → allow


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
    """Whitelist scan: CEO reply must have action work signal AND no idle disguise.
    No work signal OR any idle disguise = drift.
    Board 2026-04-15 night root fix: CZL R-zero enforcement at reply level."""
    if not text:
        return {"triggered": False, "rules": []}
    rules_triggered = []

    # NEGATIVE CHECK FIRST (overrides whitelist):
    # any idle disguise phrase → drift, regardless of work signals
    for phrase in IDLE_DISGUISE_PHRASES:
        if phrase in text:
            rules_triggered.append({
                "rule": "idle_disguise_drift",
                "detail": f"CEO reply contains idle-disguise phrase '{phrase}' — Board 2026-04-15 night doctrine: 没有'等返回'或'严守岗位'状态，CEO 必须立刻找下一活"
            })
            break  # one match enough for the warn

    # WHITELIST CHECK: action-only signals (topic keywords removed)
    has_work = any(signal in text for signal in WORK_SIGNALS)
    if not has_work:
        rules_triggered.append({
            "rule": "idle_state_not_permitted",
            "detail": "CEO reply contains no ACTION work signal — must include tool call (commit/Edit/Bash/Agent) or explicit '派 <agent>'"
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
