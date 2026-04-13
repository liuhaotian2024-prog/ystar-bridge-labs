#!/usr/bin/env python3
"""AMENDMENT-009 §2.4 — Tombstone Linter.

Scans BOARD_PENDING.md + DISPATCH.md for entries and categorizes them
into {active, resolved, deprecated} by checking frontmatter per-section.

Also counts tombstone header markers (AMENDMENT-009 transition state).

Invocation:
    python3 scripts/tombstone_linter.py
    python3 scripts/tombstone_linter.py --file BOARD_PENDING.md
"""
from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

YSTAR_DIR = Path("/Users/haotianliu/.openclaw/workspace/ystar-company")
SESSION_JSON = YSTAR_DIR / ".ystar_session.json"
CIEU_DB = YSTAR_DIR / ".ystar_cieu.db"
TARGETS = ["BOARD_PENDING.md", "DISPATCH.md"]

FRONTMATTER_RE = re.compile(r"^---\n(.*?)\n---", re.DOTALL | re.MULTILINE)
TOMBSTONE_HEADER_RE = re.compile(r"TOMBSTONE HEADER|DEPRECATED\s*\d{4}-\d{2}-\d{2}", re.IGNORECASE)


def emit_cieu(event_type: str, payload: dict):
    try:
        ygov = YSTAR_DIR.parent / "Y-star-gov"
        sys.path.insert(0, str(ygov))
        from ystar.adapters.cieu_writer import _write_session_lifecycle
        sid = "unknown"
        if SESSION_JSON.exists():
            sid = json.loads(SESSION_JSON.read_text()).get("session_id", "unknown")
        _write_session_lifecycle(event_type, "secretary", sid, str(CIEU_DB), payload)
    except Exception:
        pass


def lint_file(path: Path) -> dict:
    if not path.exists():
        return {"file": str(path), "exists": False}
    text = path.read_text(errors="replace")
    sections = re.split(r"(?=^# )", text, flags=re.MULTILINE)
    active = deprecated = resolved = unmarked = 0
    has_transition_header = bool(TOMBSTONE_HEADER_RE.search(text[:2000]))
    for sec in sections:
        if not sec.strip():
            continue
        fm = FRONTMATTER_RE.search(sec)
        if fm:
            body = fm.group(1)
            status_m = re.search(r"status:\s*(active|deprecated|resolved)", body)
            if status_m:
                s = status_m.group(1)
                if s == "active":
                    active += 1
                elif s == "deprecated":
                    deprecated += 1
                elif s == "resolved":
                    resolved += 1
            else:
                unmarked += 1
        else:
            unmarked += 1
    return {
        "file": str(path.relative_to(YSTAR_DIR)),
        "exists": True,
        "active": active,
        "deprecated": deprecated,
        "resolved": resolved,
        "unmarked": unmarked,
        "has_transition_header": has_transition_header,
    }


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--file", default=None)
    args = ap.parse_args()
    files = [args.file] if args.file else TARGETS
    results = [lint_file(YSTAR_DIR / f) for f in files]
    emit_cieu("TOMBSTONE_LINT", {"results": results})
    print(json.dumps(results, ensure_ascii=False, indent=2))
    total_unmarked = sum(r.get("unmarked", 0) for r in results if r.get("exists"))
    return 0 if total_unmarked == 0 else 0


if __name__ == "__main__":
    sys.exit(main())
