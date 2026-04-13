#!/usr/bin/env python3
"""AMENDMENT-010 §4 S-3 step 7 — Skill lifecycle manager.

Policy:
  - cold: skill unused for 5 sessions -> mark cold in registry
  - archive: unused for 10 sessions -> move to knowledge/{role}/skills/_archive/
  - alert: skill file path broken / reference exists but file missing -> CIEU alert

Invocation:
    python3 scripts/skill_lifecycle_manager.py --scan
    python3 scripts/skill_lifecycle_manager.py --role ceo

Skeleton: scans knowledge/*/skills/ dirs (may not exist yet), reports counts.
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

YSTAR_DIR = Path("/Users/haotianliu/.openclaw/workspace/ystar-company")
KNOWLEDGE = YSTAR_DIR / "knowledge"
SESSION_JSON = YSTAR_DIR / ".ystar_session.json"
CIEU_DB = YSTAR_DIR / ".ystar_cieu.db"

ROLES = ["ceo", "cto", "cmo", "cso", "cfo", "secretary",
         "eng-kernel", "eng-platform", "eng-governance", "eng-domains"]


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


def scan_role(role: str) -> dict:
    skills_dir = KNOWLEDGE / role / "skills"
    if not skills_dir.exists():
        return {"role": role, "dir_exists": False, "skills": 0}
    files = list(skills_dir.glob("*.md"))
    return {"role": role, "dir_exists": True, "skills": len(files),
            "files": [f.name for f in files]}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--scan", action="store_true")
    ap.add_argument("--role", default=None)
    args = ap.parse_args()

    roles = [args.role] if args.role else ROLES
    results = [scan_role(r) for r in roles]
    emit_cieu("SKILL_LIFECYCLE_SCAN", {"roles_scanned": len(roles), "results": results})
    print(json.dumps({"results": results, "skeleton": True}, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    sys.exit(main())
