#!/usr/bin/env python3
"""
Gemma quality nightly comparison script.

Runs daily @ 06:10 (via k9_daily_patrol.sh Step 5).
Analyzes yesterday's shadow records, computes metrics, writes daily report.

Design: Samantha 871b1b9e quality monitor spec.
CIEU event: llm_quality_audit_summary
Path: scripts/quality_compare.py
Scope: eng-kernel (Leo Chen)
"""

import json
import os
import sqlite3
from datetime import datetime, timedelta
from difflib import SequenceMatcher
from pathlib import Path
from typing import Any

# ── Configuration ────────────────────────────────────────────────────────────

REPORT_DIR = Path("/Users/haotianliu/.openclaw/workspace/ystar-company/reports/gemma_quality_daily")
CIEU_DB = Path("/Users/haotianliu/.openclaw/workspace/ystar-company/.ystar_cieu.db")
SHADOW_ARCHIVE = Path("/Users/haotianliu/.openclaw/workspace/ystar-company/reports/gemma_shadow_archive")

# Quality thresholds (Board-tunable)
SIMILARITY_MIN = 0.70
KEY_INFO_RETENTION_MIN = 0.80
LENGTH_RATIO_BAND = (0.5, 2.0)

# Telegram alert config (future: read from .ystar_session.json)
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN", "")
TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID", "")


# ── Metrics computation ──────────────────────────────────────────────────────

def compute_similarity(gemma_out: str, claude_out: str) -> float:
    """SequenceMatcher ratio (0.0-1.0)."""
    if not gemma_out or not claude_out:
        return 0.0
    return SequenceMatcher(None, gemma_out, claude_out).ratio()


def compute_key_info_retention(gemma_out: str, claude_out: str) -> float:
    """Jaccard similarity of token sets (0.0-1.0)."""
    g_tokens = set(gemma_out.lower().split())
    c_tokens = set(claude_out.lower().split())
    if not c_tokens:
        return 1.0
    return len(g_tokens & c_tokens) / len(c_tokens)


def compute_length_ratio(gemma_out: str, claude_out: str) -> float:
    """Length ratio: len(gemma) / len(claude)."""
    if not claude_out:
        return 0.0
    return len(gemma_out) / len(claude_out)


# ── Data loading ─────────────────────────────────────────────────────────────

def fetch_shadow_records(date_str: str) -> list[dict[str, Any]]:
    """
    Load all shadow records from reports/gemma_shadow_archive/YYYYMMDD/*.json.

    Returns:
        List of dicts with keys: call_id, prompt_hash, gemma_out, claude_out, etc.
    """
    day_dir = SHADOW_ARCHIVE / date_str
    if not day_dir.exists():
        return []

    records = []
    for json_file in sorted(day_dir.glob("call_*.json")):
        try:
            with open(json_file, "r", encoding="utf-8") as f:
                data = json.load(f)
                records.append({
                    "call_id": data["call_id"],
                    "prompt_hash": data["prompt_hash"],
                    "gemma_out": data["gemma"]["text"],
                    "claude_out": data["claude"]["text"],
                    "gemma_error": data["gemma"]["error"],
                    "claude_error": data["claude"]["error"],
                })
        except Exception:
            # Skip corrupted records
            continue

    return records


# ── Report generation ────────────────────────────────────────────────────────

def write_daily_report(report_path: Path, results: list[dict[str, Any]]) -> None:
    """
    Write daily quality report in markdown format.

    Front-matter:
        date, total_calls, shadow_calls, pass, fail, pass_rate, similarity_avg, retention_avg, alerts_pushed

    Body:
        Summary + failure table + action items
    """
    total = len(results)
    passes = [r for r in results if r["pass"]]
    fails = [r for r in results if not r["pass"]]

    pass_count = len(passes)
    fail_count = len(fails)
    pass_rate = pass_count / total if total > 0 else 0.0

    similarity_avg = sum(r["similarity"] for r in results) / total if total > 0 else 0.0
    retention_avg = sum(r["retention"] for r in results) / total if total > 0 else 0.0

    date_str = report_path.stem  # YYYYMMDD
    date_formatted = datetime.strptime(date_str, "%Y%m%d").strftime("%Y-%m-%d")

    # Count alerts (computed later in run_nightly)
    alerts_pushed = 1 if fail_count > 0 else 0

    # Front-matter
    front_matter = f"""---
date: {date_formatted}
total_calls: {total}
shadow_calls: {total}
pass: {pass_count}
fail: {fail_count}
pass_rate: {pass_rate:.3f}
similarity_avg: {similarity_avg:.2f}
retention_avg: {retention_avg:.2f}
alerts_pushed: {alerts_pushed}
---

# Gemma Quality Daily — {date_formatted}

## Summary
- {total} calls, {pass_count} pass ({pass_rate*100:.1f}%), {fail_count} fail
- Avg similarity {similarity_avg:.2f}, retention {retention_avg:.2f}
- {alerts_pushed} alert(s) pushed to Telegram

"""

    # Failures table
    if fails:
        front_matter += f"\n## Failures ({fail_count})\n\n"
        front_matter += "| call_id | prompt_hash | sim | retention | length_ratio | reason |\n"
        front_matter += "|---------|-------------|-----|-----------|--------------|--------|\n"

        for r in fails:
            reason = []
            if r["similarity"] < SIMILARITY_MIN:
                reason.append(f"similarity {r['similarity']:.2f} < {SIMILARITY_MIN}")
            if r["retention"] < KEY_INFO_RETENTION_MIN:
                reason.append(f"retention {r['retention']:.2f} < {KEY_INFO_RETENTION_MIN}")
            if not (LENGTH_RATIO_BAND[0] <= r["length_ratio"] <= LENGTH_RATIO_BAND[1]):
                reason.append(f"length_ratio {r['length_ratio']:.2f} out of band")
            reason_str = "; ".join(reason)

            front_matter += f"| {r['call_id']} | {r['prompt_hash']} | {r['similarity']:.2f} | {r['retention']:.2f} | {r['length_ratio']:.2f} | {reason_str} |\n"

    # Action items
    front_matter += "\n## Action items\n"
    if fail_count == 0:
        front_matter += "- No failures today. Continue monitoring.\n"
    else:
        front_matter += f"- Review {fail_count} failed call(s) in `reports/gemma_shadow_archive/{date_str}/`\n"
        if pass_rate < 0.70:
            front_matter += f"- **CRITICAL**: pass_rate {pass_rate*100:.1f}% below 70% threshold. Consider Gemma rollback.\n"

    # Write report
    report_path.parent.mkdir(parents=True, exist_ok=True)
    with open(report_path, "w", encoding="utf-8") as f:
        f.write(front_matter)


# ── Telegram alert ───────────────────────────────────────────────────────────

def push_telegram_alert(date_str: str, fail_count: int, total_count: int, report_path: Path) -> None:
    """
    Push Telegram alert when quality threshold breached.

    Message template:
        [Y* Gemma Quality Alert] YYYY-MM-DD
        pass_rate XX% (Y/Z), threshold 70%
        Report: reports/gemma_quality_daily/YYYYMMDD.md
        Action: review + consider rollback
    """
    if not TELEGRAM_BOT_TOKEN or not TELEGRAM_CHAT_ID:
        # No Telegram config, skip
        return

    pass_rate = (total_count - fail_count) / total_count if total_count > 0 else 0.0
    date_formatted = datetime.strptime(date_str, "%Y%m%d").strftime("%Y-%m-%d")

    message = f"""[Y* Gemma Quality Alert] {date_formatted}
pass_rate {pass_rate*100:.1f}% ({total_count - fail_count}/{total_count}), threshold 70%
Report: {report_path.relative_to(Path.cwd())}
Action: review + consider rollback
"""

    try:
        import requests
        requests.post(
            f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage",
            json={"chat_id": TELEGRAM_CHAT_ID, "text": message},
            timeout=10,
        )
    except Exception:
        # Fail-open: Telegram push failure doesn't block report
        pass


# ── CIEU summary event ───────────────────────────────────────────────────────

def emit_cieu_summary(date_str: str, results: list[dict[str, Any]]) -> None:
    """
    Emit CIEU llm_quality_audit_summary event to .ystar_cieu.db.

    Schema:
        C: llm_quality_audit_summary
        I: {date, total_calls, pass, fail, pass_rate, similarity_avg, retention_avg}
        E: quality_summary_daily
        U: quality_compare
        τ: <timestamp>
    """
    try:
        total = len(results)
        pass_count = sum(1 for r in results if r["pass"])
        fail_count = total - pass_count
        pass_rate = pass_count / total if total > 0 else 0.0
        similarity_avg = sum(r["similarity"] for r in results) / total if total > 0 else 0.0
        retention_avg = sum(r["retention"] for r in results) / total if total > 0 else 0.0

        intent_data = {
            "date": date_str,
            "total_calls": total,
            "pass": pass_count,
            "fail": fail_count,
            "pass_rate": pass_rate,
            "similarity_avg": similarity_avg,
            "retention_avg": retention_avg,
        }

        conn = sqlite3.connect(CIEU_DB)
        cur = conn.cursor()
        cur.execute("""
            INSERT INTO events (C, I, E, U, tau)
            VALUES (?, ?, ?, ?, ?)
        """, (
            "llm_quality_audit_summary",
            json.dumps(intent_data),
            "quality_summary_daily",
            "quality_compare",
            datetime.now().timestamp(),
        ))
        conn.commit()
        conn.close()
    except Exception:
        # Fail-open
        pass


# ── Main entry point ─────────────────────────────────────────────────────────

def run_nightly() -> Path:
    """
    Main nightly routine.

    1. Fetch yesterday's shadow records
    2. Compute metrics per record
    3. Write daily report
    4. Push Telegram alert if threshold breached
    5. Emit CIEU summary event

    Returns:
        Path to daily report
    """
    yesterday = (datetime.now() - timedelta(days=1)).strftime("%Y%m%d")

    # 1) Fetch shadow records
    records = fetch_shadow_records(yesterday)

    if not records:
        # No shadow records for yesterday (e.g., Gemma not used)
        print(f"No shadow records found for {yesterday}. Skipping quality compare.")
        return None

    # 2) Compute metrics per record
    results = []
    for r in records:
        sim = compute_similarity(r["gemma_out"], r["claude_out"])
        retention = compute_key_info_retention(r["gemma_out"], r["claude_out"])
        length = compute_length_ratio(r["gemma_out"], r["claude_out"])

        pass_flag = (
            sim >= SIMILARITY_MIN
            and retention >= KEY_INFO_RETENTION_MIN
            and LENGTH_RATIO_BAND[0] <= length <= LENGTH_RATIO_BAND[1]
        )

        results.append({
            **r,
            "similarity": sim,
            "retention": retention,
            "length_ratio": length,
            "pass": pass_flag,
        })

    # 3) Write daily report
    report_path = REPORT_DIR / f"{yesterday}.md"
    write_daily_report(report_path, results)

    # 4) Push Telegram alert if needed
    fails = [r for r in results if not r["pass"]]
    if fails:
        push_telegram_alert(yesterday, len(fails), len(results), report_path)

    # 5) Emit CIEU summary event
    emit_cieu_summary(yesterday, results)

    print(f"Quality compare complete. Report: {report_path}")
    return report_path


if __name__ == "__main__":
    run_nightly()
