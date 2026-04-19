"""
Goal 4 Demonstrator — Y*gov 全部功能都活 + 起治理作用

Audience: Board (Goal 4 module-liveness evidence).
Research basis: Labs Atlas already flagged 8+ dead modules in Y*gov
(`ml_registry / metrics / ml_discovery / retro_store / delegation_policy
 / rule_advisor / residual_loop_engine / ml_loop`). Import graph via
grep + CIEU fire query gives the dynamic live/dead picture.
Synthesis: 全活 = LIVE+DORMANT with known trigger, DEAD=0. This
demonstrator counts the gap.

Run: python3 reports/ceo/demonstrators/goal_4_ystar_symbol_liveness.py
Output: markdown dashboard to reports/ceo/demonstrators/goal_4_output.md
"""
import ast
import json
import os
import sqlite3
import subprocess
import time
from pathlib import Path

YSTAR_ROOT = "/Users/haotianliu/.openclaw/workspace/Y-star-gov/ystar"
CIEU_DB = "/Users/haotianliu/.openclaw/workspace/ystar-company/.ystar_cieu.db"
OUT = "/Users/haotianliu/.openclaw/workspace/ystar-company/reports/ceo/demonstrators/goal_4_output.md"


def collect_modules(root=YSTAR_ROOT):
    mods = []
    for dirpath, _, files in os.walk(root):
        for fn in files:
            if fn.endswith(".py") and fn != "__init__.py":
                path = os.path.join(dirpath, fn)
                rel = os.path.relpath(path, os.path.dirname(root)).replace("/", ".").replace(".py", "")
                mods.append((rel, path))
    return mods


def count_callers(symbol, root=YSTAR_ROOT):
    try:
        out = subprocess.run(
            ["grep", "-r", "-l", "--include=*.py", symbol, root],
            capture_output=True, text=True, timeout=5,
        )
        files = [l for l in out.stdout.splitlines() if "test_" not in l and "__pycache__" not in l]
        return max(0, len(files) - 1)  # subtract the self-defining file
    except Exception:
        return 0


def cieu_fires(cur, symbol, since):
    cur.execute(
        """SELECT COUNT(*) FROM cieu_events
           WHERE created_at > ? AND (params_json LIKE ? OR violations LIKE ?)""",
        (since, f"%{symbol}%", f"%{symbol}%"),
    )
    return int((cur.fetchone() or (0,))[0] or 0)


def classify(fires_7d, fires_30d, callers):
    if fires_7d > 0:
        return "LIVE"
    if callers > 0 and fires_30d > 0:
        return "DORMANT"
    if callers > 0:
        return "DORMANT"
    return "DEAD"


def scan(max_symbols=200):
    now = time.time()
    mods = collect_modules()
    results = []
    if not Path(CIEU_DB).exists():
        return {"error": f"CIEU db missing at {CIEU_DB}"}
    conn = sqlite3.connect(CIEU_DB)
    try:
        cur = conn.cursor()
        count = 0
        for qualified, path in mods:
            if count >= max_symbols:
                break
            last_name = qualified.rsplit(".", 1)[-1]
            callers = count_callers(last_name)
            f7 = cieu_fires(cur, last_name, now - 7 * 86400)
            f30 = cieu_fires(cur, last_name, now - 30 * 86400)
            results.append({
                "module": qualified,
                "file": path,
                "callers": callers,
                "fires_7d": f7,
                "fires_30d": f30,
                "category": classify(f7, f30, callers),
            })
            count += 1
    finally:
        conn.close()
    return {"generated_at": now, "scanned": len(results), "results": results}


def write_md(data):
    Path(OUT).parent.mkdir(parents=True, exist_ok=True)
    lines = ["# Goal 4 Demonstrator — Y*gov Module Liveness (CEO_ENGINEERING_OVERRIDE 2026-04-18)\n"]
    lines.append(f"Generated: {time.strftime('%Y-%m-%dT%H:%M:%S', time.localtime(data['generated_at']))}\n\n")
    if "error" in data:
        lines.append(f"**Error**: {data['error']}\n")
    else:
        c = {"LIVE": 0, "DORMANT": 0, "DEAD": 0}
        for r in data["results"]:
            c[r["category"]] += 1
        total = data["scanned"]
        live_pct = round(100.0 * c["LIVE"] / total, 1) if total else 0
        lines.append(f"**Summary**: scanned={total} LIVE={c['LIVE']} ({live_pct}%) DORMANT={c['DORMANT']} DEAD={c['DEAD']}\n\n")
        lines.append("## Top DEAD candidates (archive for Strangler Fig)\n\n")
        lines.append("| module | callers | fires_30d |\n|---|---|---|\n")
        dead = [r for r in data["results"] if r["category"] == "DEAD"][:30]
        for r in dead:
            lines.append(f"| `{r['module']}` | {r['callers']} | {r['fires_30d']} |\n")
        lines.append("\n## LIVE modules (sample)\n\n")
        live = [r for r in data["results"] if r["category"] == "LIVE"][:20]
        lines.append("| module | callers | fires_7d |\n|---|---|---|\n")
        for r in live:
            lines.append(f"| `{r['module']}` | {r['callers']} | {r['fires_7d']} |\n")
    with open(OUT, "w", encoding="utf-8") as f:
        f.writelines(lines)
    return OUT


if __name__ == "__main__":
    data = scan()
    path = write_md(data)
    print(json.dumps({
        "report": path,
        "scanned": data.get("scanned", 0),
        "counts": {k: sum(1 for r in data.get("results", []) if r["category"] == k) for k in ("LIVE", "DORMANT", "DEAD")},
    }, indent=2))
