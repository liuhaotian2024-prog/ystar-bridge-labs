#!/usr/bin/env python3
"""
Session End → auto-generate memory/session_summary_YYYYMMDD.md
Aggregates: today's commits + campaigns closed + CIEU event counts + top lessons
Fail-open. Called from SessionEnd hook.
"""
import json, subprocess, sys, time, sqlite3
from pathlib import Path
from datetime import datetime

REPO = Path("/Users/haotianliu/.openclaw/workspace/ystar-company")
YGOV = Path("/Users/haotianliu/.openclaw/workspace/Y-star-gov")


def _git(cmd, cwd):
    try:
        r = subprocess.run(cmd, cwd=str(cwd), capture_output=True, text=True, timeout=5)
        return r.stdout.strip()
    except Exception:
        return ""


def main():
    today = datetime.now().strftime("%Y%m%d")
    out = REPO / "memory" / f"session_summary_{today}.md"

    sections = [f"# Session Summary {today}\n**Generated**: {datetime.now().isoformat()}\n"]

    # Commits
    sections.append("## Today's Commits (both repos)\n")
    for label, r in [("ystar-company", REPO), ("Y*gov", YGOV)]:
        log = _git(["git", "log", "--since=24 hours ago", "--format=- %h %ad %s", "--date=format:%H:%M"], r)
        sections.append(f"### {label}\n{log or '(none)'}\n")

    # Campaign state
    try:
        sg = json.loads((REPO / ".czl_subgoals.json").read_text(encoding="utf-8"))
        sections.append(f"\n## Active Campaign\n- Status: {sg.get('campaign_status','?')}\n- Campaign: {sg.get('campaign','?')}\n")
    except Exception:
        pass

    # CIEU 24h
    try:
        conn = sqlite3.connect(str(REPO / ".ystar_cieu.db"), timeout=3.0)
        cnt = conn.execute("SELECT COUNT(*) FROM cieu_events WHERE created_at > ?", (time.time() - 86400,)).fetchone()[0]
        types = conn.execute("SELECT event_type, COUNT(*) as c FROM cieu_events WHERE created_at > ? GROUP BY event_type ORDER BY c DESC LIMIT 8", (time.time() - 86400,)).fetchall()
        conn.close()
        sections.append(f"\n## CIEU 24h\n- Total events: {cnt}\n")
        for t, c in types:
            sections.append(f"- {t}: {c}")
    except Exception as e:
        sections.append(f"\n## CIEU 24h: err {e}\n")

    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text("\n".join(sections), encoding="utf-8")
    print(f"✅ Session summary: {out}")


if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        print(f"[fail-open] {e}", file=sys.stderr)
        sys.exit(0)
