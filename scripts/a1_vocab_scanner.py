#!/usr/bin/env python3
"""AMENDMENT-010 §5 — A1 Two-State Vocab Scanner.

Pre-response hook helper. Scans a text payload for A1-forbidden vocab
(rest/tonight/tomorrow — violates always_running hard constraint).

Invocation:
    echo "text" | python3 scripts/a1_vocab_scanner.py
    python3 scripts/a1_vocab_scanner.py --text "..."

Exit 0 = clean, exit 1 = violation (with matched term + offset on stdout as JSON).

Reads config from .ystar_session.json.boot_contract.a1_two_state_enforcement.
If enforcement_enabled=false → scans but returns 0 (log-only mode).

NOT YET WIRED into hook_client_labs.sh. Activation requires:
  1. Red-team pass on false-positive rate with <literal-time-reference> exempt tag
  2. CEO flip enforcement_enabled=true in .ystar_session.json
"""
from __future__ import annotations

import json
import re
import sys
import time
from pathlib import Path

YSTAR_DIR = Path("/Users/haotianliu/.openclaw/workspace/ystar-company")
SESSION_JSON = YSTAR_DIR / ".ystar_session.json"
CIEU_DB = YSTAR_DIR / ".ystar_cieu.db"


def load_config():
    if not SESSION_JSON.exists():
        return {}
    try:
        cfg = json.loads(SESSION_JSON.read_text())
        return cfg.get("boot_contract", {}).get("a1_two_state_enforcement", {})
    except Exception:
        return {}


def scan(text: str, cfg: dict) -> dict:
    vocab = cfg.get("forbidden_vocab_pre_response_scan", [])
    exempt_tag = cfg.get("exempt_tag", "<literal-time-reference>")
    scrubbed = re.sub(
        re.escape(exempt_tag) + r".*?" + re.escape(exempt_tag.replace("<", "</")),
        "",
        text,
        flags=re.DOTALL,
    )
    hits = []
    for term in vocab:
        for m in re.finditer(re.escape(term), scrubbed):
            hits.append({"term": term, "offset": m.start()})
    return {"hits": hits, "clean": not hits}


def emit_cieu(event_type: str, payload: dict):
    try:
        ygov = YSTAR_DIR.parent / "Y-star-gov"
        sys.path.insert(0, str(ygov))
        from ystar.adapters.cieu_writer import _write_session_lifecycle
        sid = "unknown"
        if SESSION_JSON.exists():
            sid = json.loads(SESSION_JSON.read_text()).get("session_id", "unknown")
        active = (YSTAR_DIR / ".ystar_active_agent").read_text().strip() if (YSTAR_DIR / ".ystar_active_agent").exists() else "unknown"
        _write_session_lifecycle(event_type, active, sid, str(CIEU_DB), payload)
    except Exception:
        pass


def main():
    import argparse
    ap = argparse.ArgumentParser()
    ap.add_argument("--text", default=None)
    args = ap.parse_args()
    text = args.text if args.text is not None else sys.stdin.read()

    cfg = load_config()
    result = scan(text, cfg)
    enforcement = bool(cfg.get("enforcement_enabled", False))
    action = cfg.get("action_on_match", "DENY_RESPONSE_REQUIRE_REWRITE")

    if not result["clean"]:
        emit_cieu(cfg.get("emit_cieu", "A1_VIOLATION_PREVENTED"),
                  {"hits": result["hits"], "enforcement_enabled": enforcement, "action": action})
        print(json.dumps({"violation": True, "hits": result["hits"],
                          "enforcement_enabled": enforcement}, ensure_ascii=False))
        return 1 if enforcement else 0

    print(json.dumps({"violation": False}))
    return 0


if __name__ == "__main__":
    sys.exit(main())
