#!/usr/bin/env python3
"""
Y* Bridge Labs — Telegram notification library (Secretary-owned).

3 send paths per Board 2026-04-15 directive:
  1. send_daily(text)            — 晨报 @ 06:00 America/New_York
  2. send_event(event_type, ctx) — CIEU event trigger (CRITICAL_INSIGHT /
                                   MAJOR_INCIDENT / MILESTONE_SHIPPED)
  3. send_distillation_status()  — lesson usage feedback loop status
                                   (which lessons were actually used by agents
                                    vs dead knowledge)

Iron Rule 1.6 CIEU 5-tuple discipline: every send emits a Layer-12 audit row.

Token resolution order:
  1) env TELEGRAM_BOT_TOKEN
  2) ~/.gov_mcp_secrets.env
  3) MISSING → log + return False (Board must configure)

Chat target default: @YstarBridgeLabs  (override via TELEGRAM_CHAT_ID env)

Usage (module):
    from scripts.telegram_notify import send_daily, send_event, send_distillation_status
    send_daily("text")
    send_event("CRITICAL_INSIGHT", {"title": "...", "detail": "..."})
    send_distillation_status()

Usage (CLI, for cron / dry-run):
    python3 scripts/telegram_notify.py daily         # reuses daily_reminder
    python3 scripts/telegram_notify.py event CRITICAL_INSIGHT "title" "body"
    python3 scripts/telegram_notify.py distill
    python3 scripts/telegram_notify.py --dry-run event MAJOR_INCIDENT t b
"""
from __future__ import annotations

import json
import os
import sqlite3
import sys
import time
import urllib.parse
import urllib.request
from pathlib import Path
from typing import Any, Dict, Optional

# ── constants ────────────────────────────────────────────────────────────
WORKSPACE = Path("/Users/haotianliu/.openclaw/workspace/ystar-company")
SECRETS_PATH = Path(os.path.expanduser("~/.gov_mcp_secrets.env"))
CIEU_DB = WORKSPACE / ".ystar_cieu.db"
DEFAULT_CHAT_ID = "@YstarBridgeLabs"

EVENT_TYPES_TRIGGERING_PUSH = {
    "CRITICAL_INSIGHT",
    "MAJOR_INCIDENT",
    "MILESTONE_SHIPPED",
}


# ── token / chat resolution ──────────────────────────────────────────────
def _load_secrets() -> None:
    if not SECRETS_PATH.is_file():
        return
    try:
        with SECRETS_PATH.open() as f:
            for line in f:
                line = line.strip()
                if not line or line.startswith("#") or "=" not in line:
                    continue
                k, v = line.split("=", 1)
                os.environ.setdefault(k.strip(), v.strip())
    except Exception:
        pass


def _resolve_token() -> Optional[str]:
    _load_secrets()
    tok = os.environ.get("TELEGRAM_BOT_TOKEN", "").strip()
    return tok or None


def _resolve_chat_id() -> str:
    return os.environ.get("TELEGRAM_CHAT_ID", DEFAULT_CHAT_ID).strip()


# ── low-level HTTP ───────────────────────────────────────────────────────
def _post(token: str, chat_id: str, text: str, timeout: int = 10) -> Dict[str, Any]:
    url = f"https://api.telegram.org/bot{token}/sendMessage"
    data = urllib.parse.urlencode(
        {"chat_id": chat_id, "text": text, "parse_mode": "Markdown"}
    ).encode()
    req = urllib.request.Request(url, data=data)
    with urllib.request.urlopen(req, timeout=timeout) as resp:
        return json.loads(resp.read().decode())


# ── CIEU emit ────────────────────────────────────────────────────────────
def _emit_cieu(event_type: str, ok: bool, payload: Dict[str, Any]) -> None:
    """Best-effort Layer-12 audit row. Never raises."""
    try:
        if not CIEU_DB.exists():
            return
        now = time.time()
        event_id = f"tgnotify_{int(now * 1_000_000)}_{event_type}"
        conn = sqlite3.connect(str(CIEU_DB), timeout=2.0)
        try:
            conn.execute(
                """INSERT OR IGNORE INTO cieu_events
                   (event_id, seq_global, created_at, session_id, agent_id,
                    event_type, decision, passed, violations, drift_detected)
                   VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, 0)""",
                (
                    event_id,
                    int(now * 1_000_000),
                    now,
                    os.environ.get("CLAUDE_SESSION_ID", "telegram_notify"),
                    "samantha-secretary",
                    f"TELEGRAM_{event_type}",
                    "allow" if ok else "deny",
                    1 if ok else 0,
                    json.dumps(payload, ensure_ascii=False)[:4000],
                ),
            )
            conn.commit()
        finally:
            conn.close()
    except Exception:
        pass


# ── public API ───────────────────────────────────────────────────────────
def _send(text: str, kind: str, dry_run: bool = False) -> bool:
    token = _resolve_token()
    chat_id = _resolve_chat_id()

    if dry_run:
        print(f"[DRY-RUN {kind}] chat={chat_id} token={'SET' if token else 'MISSING'}")
        print("─── payload ───")
        print(text)
        print("─── end ───")
        _emit_cieu(f"{kind}_DRYRUN", True, {"len": len(text), "chat": chat_id})
        return True

    if not token:
        print(f"[TELEGRAM {kind}] TOKEN_MISSING — Board must set TELEGRAM_BOT_TOKEN")
        _emit_cieu(f"{kind}_FAILED", False, {"reason": "TOKEN_MISSING"})
        return False

    try:
        resp = _post(token, chat_id, text)
        ok = bool(resp.get("ok"))
        _emit_cieu(kind, ok, {"chat": chat_id, "resp_ok": ok})
        return ok
    except Exception as e:
        _emit_cieu(f"{kind}_FAILED", False, {"error": str(e)[:200]})
        return False


def send_daily(text: str, dry_run: bool = False) -> bool:
    """Morning brief — cron @ 06:00 America/New_York."""
    return _send(text, "DAILY", dry_run=dry_run)


def send_event(event_type: str, ctx: Dict[str, Any], dry_run: bool = False) -> bool:
    """Instant push for CRITICAL_INSIGHT / MAJOR_INCIDENT / MILESTONE_SHIPPED."""
    if event_type not in EVENT_TYPES_TRIGGERING_PUSH:
        print(f"[TELEGRAM EVENT] skipped: {event_type} not in push whitelist")
        return False
    title = ctx.get("title", "(no title)")
    detail = ctx.get("detail", "")
    src = ctx.get("source", "agent")
    icon = {
        "CRITICAL_INSIGHT": "💡",
        "MAJOR_INCIDENT": "🚨",
        "MILESTONE_SHIPPED": "🚢",
    }[event_type]
    text = (
        f"{icon} *{event_type}*\n"
        f"*{title}*\n\n"
        f"{detail}\n\n"
        f"_source: {src} · {time.strftime('%Y-%m-%d %H:%M %Z')}_"
    )
    return _send(text, f"EVENT_{event_type}", dry_run=dry_run)


def send_distillation_status(dry_run: bool = False) -> bool:
    """Feedback loop: which lessons agents actually used vs dead knowledge.

    Reads knowledge/*/lessons/*.md mtimes and CIEU agent_id usage recency.
    MVP: surface top-5 most-recently-touched lessons + top-5 stalest.
    Full implementation deferred (tracked as separate task A030_LESSON_USAGE_TRACKING).
    """
    lessons_root = WORKSPACE / "knowledge"
    if not lessons_root.exists():
        text = "📊 *Distillation status*\n_no knowledge/ tree yet_"
        return _send(text, "DISTILL", dry_run=dry_run)

    lessons = []
    for md in lessons_root.rglob("lessons/*.md"):
        try:
            lessons.append((md.stat().st_mtime, md.relative_to(WORKSPACE)))
        except Exception:
            continue
    lessons.sort(reverse=True)

    live = lessons[:5]
    stale = lessons[-5:] if len(lessons) > 5 else []

    def fmt(pair):
        ts, rel = pair
        age_d = (time.time() - ts) / 86400
        return f"• `{rel}` _{age_d:.1f}d_"

    text = (
        f"📊 *Distillation status* · {time.strftime('%Y-%m-%d %H:%M %Z')}\n"
        f"total lessons: {len(lessons)}\n\n"
        f"*Recently touched (likely live):*\n" + ("\n".join(fmt(l) for l in live) or "_none_") + "\n\n"
        f"*Stalest (candidate dead knowledge):*\n" + ("\n".join(fmt(l) for l in stale) or "_none_") + "\n\n"
        f"_MVP surface only · full usage tracking = A030_"
    )
    return _send(text, "DISTILL", dry_run=dry_run)


# ── CLI ──────────────────────────────────────────────────────────────────
def _cli(argv):
    dry = False
    if argv and argv[0] == "--dry-run":
        dry = True
        argv = argv[1:]
    if not argv:
        print("usage: telegram_notify.py [--dry-run] <daily|event|distill> [...]")
        return 2

    cmd = argv[0]
    if cmd == "daily":
        text = argv[1] if len(argv) > 1 else f"📋 daily ping {time.strftime('%Y-%m-%d %H:%M %Z')}"
        return 0 if send_daily(text, dry_run=dry) else 1
    if cmd == "event":
        if len(argv) < 4:
            print("usage: event <TYPE> <title> <detail>")
            return 2
        et, title, detail = argv[1], argv[2], argv[3]
        return 0 if send_event(et, {"title": title, "detail": detail, "source": "cli"}, dry_run=dry) else 1
    if cmd == "distill":
        return 0 if send_distillation_status(dry_run=dry) else 1
    print(f"unknown cmd: {cmd}")
    return 2


if __name__ == "__main__":
    sys.exit(_cli(sys.argv[1:]))
