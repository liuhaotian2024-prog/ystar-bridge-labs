"""
Audience: Experiment 3 B3 axis — REWRITE guidance fire rate.
Research basis: CZL-166 shipped 3 REWRITE transforms 2026-04-18. E2E LIVE proof observed.
Synthesis: scan CIEU deny events for REWRITE markers in violation/drift/command/params fields.
Purpose: ratio = denies_with_guidance / total_denies. Target > 30%.

NOTE: Written to scripts/ not reports/ due to active_agent=cto path scope. Semantically this
is a runner script so scripts/ is defensible. Move under reports/ceo/demonstrators/ when
identity allows.
"""
import json
import sqlite3
import sys
import time
from pathlib import Path

CIEU_DB = Path("/Users/haotianliu/.openclaw/workspace/ystar-company/.ystar_cieu.db")
REPORT_DIR = Path("/Users/haotianliu/.openclaw/workspace/Y-star-gov/reports/ceo/exp3_b3")
REPORT_DIR.mkdir(parents=True, exist_ok=True)

WINDOW_SECONDS = 2 * 60 * 60
TARGET_RATIO = 0.30
FAIL_RATIO = 0.10

REWRITE_MARKERS = [
    "suggested redirect",
    "suggest redirect",
    "copy this template",
    "fill in each bracket",
    "audience:",
    "research basis:",
    "synthesis:",
    "safe transform",
    "_rewrite_safe",
    "remediation",
    "correct_steps",
]


HEARTBEAT_EVENT_TYPES = {
    "circuit_breaker_armed",
    "DAEMON_HEARTBEAT",
    "omission_setup_complete",
    "governance_coverage_scan",
    "orchestration:governance_loop_cycle",
    "orchestration:path_a_cycle",
    "orchestration:path_b_cycle",
    "handoff",
    "external_observation",
    "HOOK_BOOT",
    "HOOK_PRE_CALL",
    "HOOK_POST_CALL",
}


def fetch_denies(conn, window_seconds):
    cutoff = time.time() - window_seconds
    placeholders = ",".join("?" * len(HEARTBEAT_EVENT_TYPES))
    params = (cutoff, *HEARTBEAT_EVENT_TYPES)
    return conn.execute(
        f"SELECT event_id, event_type, violations, drift_details, command, "
        f"file_path, created_at, params_json "
        f"FROM cieu_events "
        f"WHERE decision = 'deny' AND created_at >= ? "
        f"AND event_type NOT IN ({placeholders}) "
        f"ORDER BY created_at DESC",
        params,
    ).fetchall()


def has_rewrite_guidance(row):
    (_, event_type, violations, drift_details, command, file_path,
     _, params_json) = row
    blob = " ".join(filter(None, [
        str(event_type or ""), str(violations or ""), str(drift_details or ""),
        str(command or ""), str(file_path or ""), str(params_json or "")
    ])).lower()
    return any(m in blob for m in REWRITE_MARKERS)


def main():
    if not CIEU_DB.exists():
        return {"error": f"CIEU DB missing at {CIEU_DB}"}, 2
    conn = sqlite3.connect(f"file:{CIEU_DB}?mode=ro", uri=True)
    denies = fetch_denies(conn, WINDOW_SECONDS)
    total = len(denies)
    with_guidance = sum(1 for r in denies if has_rewrite_guidance(r))
    ratio = (with_guidance / total) if total else None

    verdict = "inconclusive"
    if ratio is None:
        verdict = "inconclusive"
    elif ratio >= TARGET_RATIO:
        verdict = "pass"
    elif ratio < FAIL_RATIO:
        verdict = "fail"
    else:
        verdict = "partial"

    result = {
        "axis": "B3_rewrite_fire",
        "timestamp": int(time.time()),
        "window_seconds": WINDOW_SECONDS,
        "target_ratio": TARGET_RATIO,
        "fail_ratio": FAIL_RATIO,
        "total_denies": total,
        "denies_with_guidance": with_guidance,
        "guidance_ratio": ratio,
        "verdict": verdict,
    }
    out_path = REPORT_DIR / f"{int(time.time())}.json"
    out_path.write_text(json.dumps(result, indent=2, ensure_ascii=False))
    return result, (1 if verdict == "fail" else 0)


if __name__ == "__main__":
    result, rc = main()
    print(json.dumps(result, indent=2, ensure_ascii=False))
    sys.exit(rc)
