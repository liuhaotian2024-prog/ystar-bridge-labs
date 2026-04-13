#!/usr/bin/env python3
"""AMENDMENT-009 §2.5a — Article 11 Pre-Response Compliance Check.

Checks whether a substantive CEO response is backed by a recent
ARTICLE_11_PASS CIEU event (within last 60s with 7 non-empty layers).

Invocation:
    python3 scripts/article11_compliance.py --check
    python3 scripts/article11_compliance.py --substantive "text..."

Config in .ystar_session.json.boot_contract.article_11_enforcement.
enforcement_enabled=false → check + emit CIEU WARN but exit 0.

NOT YET WIRED into hook_client_labs.sh. Activation sequence:
  1. Leo delivers gov_article11_pass MCP tool (seq 9 of AMENDMENT-009+010 impl)
  2. CEO practices emitting 7-layer passes for 3 sessions
  3. CEO flips enforcement_enabled=true
"""
from __future__ import annotations

import json
import re
import sqlite3
import sys
import time
from pathlib import Path

YSTAR_DIR = Path("/Users/haotianliu/.openclaw/workspace/ystar-company")
SESSION_JSON = YSTAR_DIR / ".ystar_session.json"
CIEU_DB = YSTAR_DIR / ".ystar_cieu.db"
WARN_COUNT_FILE = YSTAR_DIR / ".ystar_article11_warnings"

SUBSTANTIVE_KEYWORDS = ["派", "决定", "优先级", "战略", "动手", "启动"]
SUBSTANTIVE_LEN = 200


def load_config():
    if not SESSION_JSON.exists():
        return {}
    try:
        cfg = json.loads(SESSION_JSON.read_text())
        return cfg.get("boot_contract", {}).get("article_11_enforcement", {})
    except Exception:
        return {}


def is_substantive(text: str) -> bool:
    if len(text) > SUBSTANTIVE_LEN:
        return True
    return any(k in text for k in SUBSTANTIVE_KEYWORDS)


def recent_article11_pass(window_sec: int = 60) -> dict | None:
    if not CIEU_DB.exists():
        return None
    try:
        db = sqlite3.connect(str(CIEU_DB))
        cutoff = int(time.time()) - window_sec
        row = db.execute(
            "SELECT payload, ts FROM cieu_events WHERE event_type='ARTICLE_11_PASS' AND ts>=? "
            "ORDER BY ts DESC LIMIT 1",
            (cutoff,),
        ).fetchone()
        db.close()
        if not row:
            return None
        payload = json.loads(row[0]) if row[0] else {}
        return {"payload": payload, "ts": row[1]}
    except Exception:
        return None


def validate_layers(payload: dict) -> tuple[bool, str]:
    for i in range(1, 8):
        key = f"layer_{i}"
        v = payload.get(key, "")
        if not isinstance(v, str) or len(v.strip()) < 20:
            return False, f"{key} missing or <20 chars"
    return True, "ok"


def bump_warn():
    n = 0
    if WARN_COUNT_FILE.exists():
        try:
            n = int(WARN_COUNT_FILE.read_text().strip() or 0)
        except Exception:
            n = 0
    n += 1
    WARN_COUNT_FILE.write_text(str(n))
    return n


def reset_warn():
    if WARN_COUNT_FILE.exists():
        WARN_COUNT_FILE.unlink()


def emit_cieu(event_type: str, payload: dict):
    try:
        ygov = YSTAR_DIR.parent / "Y-star-gov"
        sys.path.insert(0, str(ygov))
        from ystar.adapters.cieu_writer import _write_session_lifecycle
        sid = "unknown"
        if SESSION_JSON.exists():
            sid = json.loads(SESSION_JSON.read_text()).get("session_id", "unknown")
        active_path = YSTAR_DIR / ".ystar_active_agent"
        active = active_path.read_text().strip() if active_path.exists() else "unknown"
        _write_session_lifecycle(event_type, active, sid, str(CIEU_DB), payload)
    except Exception:
        pass


def check(text: str | None) -> int:
    cfg = load_config()
    enforcement = bool(cfg.get("enforcement_enabled", False))
    if text is not None and not is_substantive(text):
        return 0

    recent = recent_article11_pass()
    if recent is None:
        n = bump_warn()
        emit_cieu("ARTICLE_11_MISSING",
                  {"warn_count": n, "enforcement_enabled": enforcement})
        print(json.dumps({"compliant": False, "reason": "no_article11_pass_60s",
                          "warn_count": n, "enforcement_enabled": enforcement}))
        if enforcement and n >= 3:
            return 1
        return 0

    ok, reason = validate_layers(recent["payload"])
    if not ok:
        n = bump_warn()
        emit_cieu("ARTICLE_11_INVALID",
                  {"reason": reason, "warn_count": n, "enforcement_enabled": enforcement})
        print(json.dumps({"compliant": False, "reason": reason, "warn_count": n}))
        if enforcement and n >= 3:
            return 1
        return 0

    reset_warn()
    print(json.dumps({"compliant": True, "ts": recent["ts"]}))
    return 0


def main():
    import argparse
    ap = argparse.ArgumentParser()
    ap.add_argument("--check", action="store_true")
    ap.add_argument("--substantive", default=None)
    args = ap.parse_args()
    text = args.substantive if args.substantive else (None if args.check else sys.stdin.read())
    return check(text)


if __name__ == "__main__":
    sys.exit(main())
