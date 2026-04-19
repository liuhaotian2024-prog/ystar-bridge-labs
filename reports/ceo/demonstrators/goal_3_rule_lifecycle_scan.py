"""
Goal 3 Demonstrator — 治理规则是 Labs 活 DNA，不是手册字

Audience: Board (Goal 3 rule-liveness evidence).
Research basis: Rules that never fire are documentation, not DNA.
CIEU event store is the authoritative fire record. Cross-referenced
with forget_guard_rules.yaml top-level rule ids.
Synthesis: DNA = runtime-active + measurable. This script produces
the measurement that separates "rule we wrote" from "rule that runs".

Run: python3 reports/ceo/demonstrators/goal_3_rule_lifecycle_scan.py
Output: markdown dashboard to reports/ceo/demonstrators/goal_3_output.md
"""
import json
import sqlite3
import time
from pathlib import Path

CIEU_DB = "/Users/haotianliu/.openclaw/workspace/ystar-company/.ystar_cieu.db"
FG_YAML = "/Users/haotianliu/.openclaw/workspace/ystar-company/governance/forget_guard_rules.yaml"
OUT = "/Users/haotianliu/.openclaw/workspace/ystar-company/reports/ceo/demonstrators/goal_3_output.md"


def rule_ids_from_yaml(path=FG_YAML):
    if not Path(path).exists():
        return []
    ids = []
    with open(path, "r", encoding="utf-8") as f:
        for line in f:
            stripped = line.rstrip("\n")
            if (
                stripped
                and stripped.endswith(":")
                and not line.startswith((" ", "\t", "#", "-"))
            ):
                key = stripped[:-1].strip()
                if key and key not in ("rules", "metadata", "version", "forget_guard_rules"):
                    ids.append(key)
    return ids


def fires_count(cur, rule_id, since):
    cur.execute(
        """SELECT COUNT(*), MAX(created_at) FROM cieu_events
           WHERE created_at > ? AND (violations LIKE ? OR params_json LIKE ?)""",
        (since, f"%{rule_id}%", f"%{rule_id}%"),
    )
    row = cur.fetchone() or (0, None)
    return int(row[0] or 0), row[1]


def classify(fires_7d, fires_30d):
    if fires_7d > 0:
        return "LIVE"
    if fires_30d > 0:
        return "DORMANT"
    return "DEAD"


def scan():
    if not Path(CIEU_DB).exists():
        return {"error": f"CIEU db missing at {CIEU_DB}"}
    now = time.time()
    rule_ids = rule_ids_from_yaml()
    results = []
    conn = sqlite3.connect(CIEU_DB)
    try:
        cur = conn.cursor()
        for rid in rule_ids:
            f7, last = fires_count(cur, rid, now - 7 * 86400)
            f30, _ = fires_count(cur, rid, now - 30 * 86400)
            results.append({
                "rule_id": rid,
                "fires_7d": f7,
                "fires_30d": f30,
                "category": classify(f7, f30),
                "last_fire_ts": last,
            })
    finally:
        conn.close()
    return {
        "generated_at": now,
        "total_rules": len(results),
        "results": sorted(results, key=lambda r: (r["category"], -r["fires_7d"], r["rule_id"])),
    }


def write_md(data):
    Path(OUT).parent.mkdir(parents=True, exist_ok=True)
    lines = ["# Goal 3 Demonstrator — Rule Lifecycle (CEO_ENGINEERING_OVERRIDE 2026-04-18)\n"]
    lines.append(f"Generated: {time.strftime('%Y-%m-%dT%H:%M:%S', time.localtime(data['generated_at']))}\n\n")
    if "error" in data:
        lines.append(f"**Error**: {data['error']}\n")
    else:
        counts = {"LIVE": 0, "DORMANT": 0, "DEAD": 0}
        for r in data["results"]:
            counts[r["category"]] += 1
        total = data["total_rules"]
        live_pct = round(100.0 * counts["LIVE"] / total, 1) if total else 0
        lines.append(f"**Summary**: total={total} LIVE={counts['LIVE']} ({live_pct}%) DORMANT={counts['DORMANT']} DEAD={counts['DEAD']}\n\n")
        lines.append("| rule_id | category | fires_7d | fires_30d |\n|---|---|---|---|\n")
        for r in data["results"]:
            lines.append(f"| `{r['rule_id']}` | {r['category']} | {r['fires_7d']} | {r['fires_30d']} |\n")
    with open(OUT, "w", encoding="utf-8") as f:
        f.writelines(lines)
    return OUT


if __name__ == "__main__":
    data = scan()
    path = write_md(data)
    print(json.dumps({
        "report": path,
        "total_rules": data.get("total_rules", 0),
        "summary": {k: sum(1 for r in data.get("results", []) if r["category"] == k) for k in ("LIVE", "DORMANT", "DEAD")},
    }, indent=2))
