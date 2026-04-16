#!/usr/bin/env python3
"""Session Watchdog — Lightweight in-session health monitor.

Checks 4 signals and returns a composite health score (0-100):
  1. Session age        (weight 25%)  — time since .session_booted created
  2. Context pressure   (weight 25%)  — context window usage percentage
  3. CIEU repetition    (weight 30%)  — repeated action fingerprints in recent events
  4. Obligation decay   (weight 20%)  — overdue obligations vs total

Usage:
    # Quick check (for hooks/statusline — <50ms target)
    python3 scripts/session_watchdog.py --quick

    # Full check with details
    python3 scripts/session_watchdog.py --full

    # Accept context_pct from stdin (hook mode)
    echo '{"context_pct": 72.5}' | python3 scripts/session_watchdog.py --quick

Output: JSON to stdout
    {"score": 78, "status": "OK", "signals": {...}, "recommendation": null}
    {"score": 42, "status": "WARNING", "signals": {...}, "recommendation": "Save state soon"}
    {"score": 28, "status": "RESTART_NOW", "signals": {...}, "recommendation": "Execute save-and-restart"}

Thresholds (aligned with gov_health):
    >= 70  OK
    40-69  WARNING
    < 40   RESTART_NOW
"""

from __future__ import annotations

import json
import os
import sys
import time
import sqlite3
import hashlib
from pathlib import Path
from typing import Optional

YSTAR_DIR = Path(__file__).resolve().parent.parent
CIEU_DB = YSTAR_DIR / ".ystar_cieu.db"
SESSION_MARKER = YSTAR_DIR / "scripts" / ".session_booted"
CALL_COUNT_FILE = YSTAR_DIR / "scripts" / ".session_call_count"

# Thresholds
SCORE_OK = 70
SCORE_WARNING = 40
SESSION_MAX_HOURS = 8  # after 8h, session age signal = 0
SESSION_WARN_HOURS = 3  # below this, full score
REPETITION_WINDOW = 30  # last N CIEU events to check
REPETITION_THRESHOLD = 0.30  # 30% repetition = score 0

# Weights
W_AGE = 0.25
W_CONTEXT = 0.25
W_REPETITION = 0.30
W_OBLIGATION = 0.20


def get_session_age_score() -> dict:
    """Score based on session age. Full marks if <3h, zero at 8h."""
    if not SESSION_MARKER.exists():
        return {"score": 100, "hours": 0, "detail": "no active session marker"}

    age_s = time.time() - SESSION_MARKER.stat().st_mtime
    hours = age_s / 3600

    if hours <= SESSION_WARN_HOURS:
        score = 100
    elif hours >= SESSION_MAX_HOURS:
        score = 0
    else:
        # Linear decay from 100 to 0 between WARN and MAX
        score = 100 * (1 - (hours - SESSION_WARN_HOURS) / (SESSION_MAX_HOURS - SESSION_WARN_HOURS))

    return {"score": round(score, 1), "hours": round(hours, 1), "detail": f"{hours:.1f}h elapsed"}


def get_context_score(context_pct: float | None) -> dict:
    """Score based on context window usage. Full marks if <50%, zero at 95%."""
    if context_pct is None:
        return {"score": 100, "pct": None, "detail": "no context data"}

    if context_pct <= 50:
        score = 100
    elif context_pct >= 95:
        score = 0
    else:
        score = 100 * (1 - (context_pct - 50) / 45)

    return {"score": round(score, 1), "pct": round(context_pct, 1), "detail": f"{context_pct:.0f}% used"}


def event_fingerprint(event_type: str, file_path: str | None, command: str | None,
                      agent_id: str | None = None, task_desc: str | None = None) -> str:
    """Stable semantic fingerprint for an action (matches gov_health algorithm).

    W14 fix: when file_path and command are both empty (common for
    external_observation / cmd_exec events), fall back to agent_id +
    task_description[:40] to distinguish actions. Without this fallback,
    8+ events with different semantic content collide to the same fingerprint,
    producing false-positive repetition signal.
    """
    parts = [event_type or "", file_path or "", command or ""]
    # Fallback: if primary params empty, distinguish by agent + task prefix
    if not (file_path or command):
        parts.append(agent_id or "")
        parts.append((task_desc or "")[:40])
    return hashlib.sha256("|".join(parts).encode()).hexdigest()[:16]


def get_repetition_score() -> dict:
    """Score based on action repetition in recent CIEU events."""
    if not CIEU_DB.exists():
        return {"score": 100, "repetition_rate": 0, "detail": "no CIEU DB"}

    try:
        conn = sqlite3.connect(CIEU_DB, timeout=2)
        conn.execute("PRAGMA journal_mode=WAL")
        # Exclude guard/watchdog infrastructure events — repetition among those
        # reflects active enforcement (healthy), not agent loop.
        rows = conn.execute(
            "SELECT event_type, file_path, command, agent_id, task_description FROM cieu_events "
            "WHERE agent_id NOT IN ('forget_guard', 'subagent_scan', 'reply_scan', 'cieu_watcher', 'orchestrator', 'intervention_engine') "
            "AND event_type NOT LIKE '%_DRIFT' "
            "AND event_type NOT LIKE 'CIEU_%' "
            "AND event_type NOT LIKE 'orchestration:%' "
            "AND event_type NOT IN ('HOOK_BOOT', 'circuit_breaker_armed', 'omission_setup_complete', 'governance_coverage_scan', 'handoff', 'intervention_gate:deny') "
            "ORDER BY created_at DESC LIMIT ?",
            (REPETITION_WINDOW,)
        ).fetchall()
        conn.close()
    except Exception:
        return {"score": 100, "repetition_rate": 0, "detail": "CIEU read error"}

    if len(rows) < 5:
        return {"score": 100, "repetition_rate": 0, "detail": f"only {len(rows)} events"}

    fps = [event_fingerprint(r[0], r[1], r[2], r[3] if len(r) > 3 else None, r[4] if len(r) > 4 else None) for r in rows]
    unique = len(set(fps))
    total = len(fps)
    repetition_rate = 1 - (unique / total) if total > 0 else 0

    if repetition_rate <= 0.05:
        score = 100
    elif repetition_rate >= REPETITION_THRESHOLD:
        score = 0
    else:
        score = 100 * (1 - repetition_rate / REPETITION_THRESHOLD)

    return {
        "score": round(score, 1),
        "repetition_rate": round(repetition_rate, 3),
        "unique": unique,
        "total": total,
        "detail": f"{repetition_rate:.0%} repetition in last {total} events"
    }


def get_obligation_score() -> dict:
    """Score based on overdue obligations ratio."""
    if not CIEU_DB.exists():
        return {"score": 100, "overdue": 0, "total": 0, "detail": "no CIEU DB"}

    try:
        conn = sqlite3.connect(CIEU_DB, timeout=2)
        now = time.time()

        # Count registered obligations
        registered = conn.execute(
            "SELECT COUNT(*) FROM cieu_events WHERE event_type = 'OBLIGATION_REGISTERED'"
        ).fetchone()[0]

        # Count fulfilled
        fulfilled = conn.execute(
            "SELECT COUNT(*) FROM cieu_events WHERE event_type = 'OBLIGATION_FULFILLED'"
        ).fetchone()[0]

        # Count cancelled (also closed state, not pending)
        cancelled = conn.execute(
            "SELECT COUNT(*) FROM cieu_events WHERE event_type = 'OBLIGATION_CANCELLED'"
        ).fetchone()[0]

        # Count overdue (registered but not fulfilled, with due_at in the past)
        # Simplified: just look at recent session obligations
        overdue_rows = conn.execute("""
            SELECT COUNT(*) FROM cieu_events
            WHERE event_type = 'OBLIGATION_REGISTERED'
            AND params_json LIKE '%due_at%'
            AND created_at > ?
        """, (now - 86400,)).fetchall()  # last 24h

        conn.close()

        pending = max(0, registered - fulfilled - cancelled)
        closed = fulfilled + cancelled
        if registered == 0:
            score = 100
        else:
            fulfillment_rate = closed / registered
            if fulfillment_rate >= 0.7:
                score = 100
            elif fulfillment_rate <= 0.3:
                score = 0
            else:
                score = 100 * (fulfillment_rate - 0.3) / 0.4

        return {
            "score": round(score, 1),
            "registered": registered,
            "fulfilled": fulfilled,
            "pending": pending,
            "detail": f"{fulfilled}/{registered} fulfilled"
        }
    except Exception:
        return {"score": 100, "overdue": 0, "total": 0, "detail": "query error"}


def get_daemon_liveness_score() -> dict:
    """Score based on daemon process health. Full marks if 4/4 alive, zero if 0/4."""
    daemon_names = [
        "k9_routing_subscriber",
        "k9_alarm_consumer",
        "cto_dispatch_broker",
        "engineer_task_subscriber"
    ]
    alive = 0
    try:
        import subprocess
        for name in daemon_names:
            result = subprocess.run(
                ["pgrep", "-f", name],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE
            )
            if result.returncode == 0:
                alive += 1
    except Exception:
        pass

    total = len(daemon_names)
    score = (alive / total) * 100 if total > 0 else 0
    return {
        "score": round(score, 1),
        "alive": alive,
        "total": total,
        "detail": f"{alive}/{total} daemons alive"
    }


def get_subagent_receipt_accuracy_score() -> dict:
    """Score based on sub-agent receipt tool_uses claim accuracy. Full marks if 100% match."""
    if not CIEU_DB.exists():
        return {"score": 100, "matches": 0, "total": 0, "detail": "no CIEU DB"}

    try:
        conn = sqlite3.connect(CIEU_DB, timeout=2)
        rows = conn.execute(
            "SELECT params_json FROM cieu_events "
            "WHERE event_type = 'RECEIPT_AUTO_VALIDATED' "
            "ORDER BY created_at DESC LIMIT 10"
        ).fetchall()
        conn.close()
    except Exception:
        return {"score": 100, "matches": 0, "total": 0, "detail": "query error"}

    if not rows:
        return {"score": 100, "matches": 0, "total": 0, "detail": "no receipts"}

    matches = 0
    total = 0
    for row in rows:
        try:
            params = json.loads(row[0])
            status = params.get("validation_status", "")
            if status in ("passed", "no_artifacts_to_check"):
                matches += 1
            elif status == "rt_mismatch":
                claimed = params.get("claimed_rt")
                actual = params.get("actual_rt")
                if claimed is not None and actual is not None and abs(float(claimed) - float(actual)) < 0.5:
                    matches += 1
            total += 1
        except Exception:
            continue

    score = (matches / total) * 100 if total > 0 else 100
    return {
        "score": round(score, 1),
        "matches": matches,
        "total": total,
        "detail": f"{matches}/{total} validated"
    }


def get_k9_signal_noise_ratio_score() -> dict:
    """Score based on K9 signal quality. Full marks if 0% false positives."""
    if not CIEU_DB.exists():
        return {"score": 100, "fp_rate": 0, "total": 0, "detail": "no CIEU DB"}

    try:
        conn = sqlite3.connect(CIEU_DB, timeout=2)
        rows = conn.execute(
            "SELECT agent_id, event_type FROM cieu_events "
            "WHERE event_type IN ('K9_VIOLATION_DETECTED', 'AGENT_REGISTRY_K9_WARN', 'HOOK_HEALTH_K9_ESCALATE') "
            "ORDER BY created_at DESC LIMIT 200"
        ).fetchall()
        conn.close()
    except Exception:
        return {"score": 100, "fp_rate": 0, "total": 0, "detail": "query error"}

    if not rows:
        return {"score": 100, "fp_rate": 0, "total": 0, "detail": "no K9 events"}

    # Load canonical aliases
    alias_file = YSTAR_DIR / "governance" / "agent_id_canonical.json"
    known_agents = set()
    if alias_file.exists():
        try:
            data = json.loads(alias_file.read_text())
            for entry in data:
                known_agents.add(entry.get("canonical_id", ""))
                known_agents.update(entry.get("aliases", []))
        except Exception:
            pass

    false_positives = 0
    signal = 0
    total = len(rows)
    for row in rows:
        agent_id, evt = row[0], row[1]
        # FP definition: AGENT_REGISTRY/HOOK_HEALTH warns about an agent_id NOT resolvable through canonical registry
        # K9_VIOLATION_DETECTED is always signal (real behavioral audit hit)
        if evt == "K9_VIOLATION_DETECTED":
            signal += 1
        elif agent_id in ("unknown", "UNKNOWN", "???", "agent") or (known_agents and agent_id not in known_agents):
            false_positives += 1
        else:
            signal += 1

    fp_rate = false_positives / total if total > 0 else 0
    score = (1 - fp_rate) * 100
    return {
        "score": round(score, 1),
        "fp_rate": round(fp_rate, 3),
        "false_positives": false_positives,
        "signal": signal,
        "total": total,
        "detail": f"{signal} signal / {false_positives} FP / {total} total"
    }


def get_api_health_score() -> dict:
    """Score based on sub-agent dispatch API responsiveness. Full marks if 0% timeout."""
    if not CIEU_DB.exists():
        return {"score": 100, "timeout_rate": 0, "total": 0, "detail": "no CIEU DB"}

    try:
        conn = sqlite3.connect(CIEU_DB, timeout=2)
        rows = conn.execute(
            "SELECT params_json FROM cieu_events "
            "WHERE event_type LIKE 'SUBAGENT_DISPATCH%' "
            "ORDER BY created_at DESC LIMIT 10"
        ).fetchall()
        conn.close()
    except Exception:
        return {"score": 100, "timeout_rate": 0, "total": 0, "detail": "query error"}

    if not rows:
        return {"score": 100, "timeout_rate": 0, "total": 0, "detail": "no dispatches"}

    timeouts = 0
    total = 0
    for row in rows:
        try:
            params = json.loads(row[0])
            duration_ms = params.get("duration_ms", 0)
            if duration_ms > 1500_000:  # 1.5x normal max
                timeouts += 1
            total += 1
        except Exception:
            continue

    timeout_rate = timeouts / total if total > 0 else 0
    score = (1 - timeout_rate) * 100
    return {
        "score": round(score, 1),
        "timeout_rate": round(timeout_rate, 3),
        "timeouts": timeouts,
        "total": total,
        "detail": f"{timeout_rate:.0%} timeout rate"
    }


def get_routing_compliance_score() -> dict:
    """Score based on NEW-file Write events WITH preceding ROUTING_GATE_CHECK. Full marks if 100% compliance."""
    if not CIEU_DB.exists():
        return {"score": 100, "compliance": 0, "total": 0, "detail": "no CIEU DB"}

    try:
        conn = sqlite3.connect(CIEU_DB, timeout=2)
        # Get last 50 NEW-file Write events (file_path not previously written)
        # Heuristic: look for Write events in governance/ or ystar/governance/
        rows = conn.execute(
            "SELECT created_at, file_path FROM cieu_events "
            "WHERE event_type = 'write' "
            "AND (file_path LIKE '%governance/%' OR file_path LIKE '%ystar/governance/%') "
            "ORDER BY created_at DESC LIMIT 50"
        ).fetchall()
        conn.close()
    except Exception:
        return {"score": 100, "compliance": 0, "total": 0, "detail": "query error"}

    if not rows:
        return {"score": 100, "compliance": 0, "total": 0, "detail": "no write events"}

    compliance = 0
    total = 0
    for created_at, file_path in rows:
        # Check if there's a ROUTING_GATE_CHECK event within 30s before this Write
        try:
            conn = sqlite3.connect(CIEU_DB, timeout=2)
            gate_count = conn.execute(
                "SELECT COUNT(*) FROM cieu_events "
                "WHERE event_type = 'ROUTING_GATE_CHECK' "
                "AND created_at BETWEEN ? AND ?",
                (created_at - 30, created_at)
            ).fetchone()[0]
            conn.close()
            if gate_count > 0:
                compliance += 1
            total += 1
        except Exception:
            continue

    score = (compliance / total) * 100 if total > 0 else 100
    return {
        "score": round(score, 1),
        "compliance": compliance,
        "total": total,
        "detail": f"{compliance}/{total} with precheck"
    }


def get_formal_section_compliance_score() -> dict:
    """Score based on governance/*.md files having both ## Formal Definitions + ## Mathematical Model sections."""
    governance_dir = YSTAR_DIR / "governance"
    if not governance_dir.exists():
        return {"score": 100, "compliance": 0, "total": 0, "detail": "no governance dir"}

    try:
        # Get all .md files modified in last 7 days
        import time
        now = time.time()
        seven_days_ago = now - (7 * 86400)
        files = []
        for md_file in governance_dir.glob("*.md"):
            if md_file.stat().st_mtime > seven_days_ago:
                files.append(md_file)
    except Exception:
        return {"score": 100, "compliance": 0, "total": 0, "detail": "glob error"}

    if not files:
        return {"score": 100, "compliance": 0, "total": 0, "detail": "no recent files"}

    compliance = 0
    total = 0
    for md_file in files:
        try:
            content = md_file.read_text(encoding="utf-8", errors="ignore")
            has_formal = "## Formal Definitions" in content
            has_math = "## Mathematical Model" in content
            if has_formal and has_math:
                compliance += 1
            total += 1
        except Exception:
            continue

    score = (compliance / total) * 100 if total > 0 else 100
    return {
        "score": round(score, 1),
        "compliance": compliance,
        "total": total,
        "detail": f"{compliance}/{total} with formal sections"
    }


def get_call_count() -> int:
    """Read current tool call count from marker file."""
    try:
        return int(CALL_COUNT_FILE.read_text().strip())
    except Exception:
        return 0


def increment_call_count() -> int:
    """Increment and return new call count."""
    count = get_call_count() + 1
    CALL_COUNT_FILE.write_text(str(count))
    return count


def compute_agent_capability_score() -> dict:
    """Compute composite Agent Capability (AC) score from 6 signals.

    Weights (rebalanced for 6 signals):
        daemon_liveness: 17%
        subagent_receipt_accuracy: 17%
        k9_signal_noise_ratio: 17%
        api_health: 17%
        routing_compliance: 16%
        formal_section_compliance: 16%
    Total: 100%

    Alarm: score < 75 emits CIEU event AGENT_CAPABILITY_DEGRADED.
    """
    signals = {
        "daemon_liveness": get_daemon_liveness_score(),
        "subagent_receipt_accuracy": get_subagent_receipt_accuracy_score(),
        "k9_signal_noise_ratio": get_k9_signal_noise_ratio_score(),
        "api_health": get_api_health_score(),
        "routing_compliance": get_routing_compliance_score(),
        "formal_section_compliance": get_formal_section_compliance_score(),
    }

    composite = (
        0.17 * signals["daemon_liveness"]["score"]
        + 0.17 * signals["subagent_receipt_accuracy"]["score"]
        + 0.17 * signals["k9_signal_noise_ratio"]["score"]
        + 0.17 * signals["api_health"]["score"]
        + 0.16 * signals["routing_compliance"]["score"]
        + 0.16 * signals["formal_section_compliance"]["score"]
    )
    score = round(composite, 1)

    # Alarm if < 75
    violations = []
    if score < 75:
        for name, sig in signals.items():
            if sig["score"] < 75:
                violations.append(f"{name}={sig['detail']}")

    # Emit CIEU event if alarm triggered
    if violations and CIEU_DB.exists():
        try:
            import uuid
            conn = sqlite3.connect(CIEU_DB, timeout=2)
            event_id = str(uuid.uuid4())
            now = time.time()
            params = json.dumps({
                "score": score,
                "violations": violations,
                "recommendation": _get_ac_recommendation(violations)
            })
            conn.execute(
                "INSERT INTO cieu_events (event_id, seq_global, created_at, session_id, agent_id, "
                "event_type, decision, passed, params_json) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)",
                (event_id, int(now * 1e6), now, "current", "session_watchdog",
                 "AGENT_CAPABILITY_DEGRADED", "escalate", 0, params)
            )
            conn.commit()
            conn.close()
        except Exception:
            pass

    return {
        "score": score,
        "signals": signals,
        "violations": violations,
        "timestamp": time.time(),
    }


def _get_ac_recommendation(violations: list[str]) -> str:
    """Generate recommendation based on AC violations."""
    recommendations = []
    for v in violations:
        if "daemon_liveness" in v:
            recommendations.append("Restart daemons: bash scripts/daemon_restart.sh")
        elif "subagent_receipt_accuracy" in v:
            recommendations.append("Investigate receipt hallucinations: check sub-agent logs")
        elif "k9_signal_noise_ratio" in v:
            recommendations.append("Update K9 registry: add missing agent_id aliases")
        elif "api_health" in v:
            recommendations.append("Check API latency: inspect SUBAGENT_DISPATCH durations")
    return "; ".join(recommendations) if recommendations else "Review AC signal breakdown"


def compute_health(context_pct: float | None = None) -> dict:
    """Compute composite health score and recommendation."""
    signals = {
        "session_age": get_session_age_score(),
        "context": get_context_score(context_pct),
        "repetition": get_repetition_score(),
        "obligation": get_obligation_score(),
    }

    composite = (
        W_AGE * signals["session_age"]["score"]
        + W_CONTEXT * signals["context"]["score"]
        + W_REPETITION * signals["repetition"]["score"]
        + W_OBLIGATION * signals["obligation"]["score"]
    )
    score = round(composite, 1)

    if score >= SCORE_OK:
        status = "OK"
        recommendation = None
    elif score >= SCORE_WARNING:
        status = "WARNING"
        recommendation = "Session degrading. Save state soon and prepare for restart."
    else:
        status = "RESTART_NOW"
        recommendation = (
            "SESSION HEALTH CRITICAL. Execute save-and-restart protocol NOW:\n"
            "1. Run: python3 scripts/session_close_yml.py ceo \"auto-restart: health score {}\"\n"
            "2. Run: bash scripts/session_auto_restart.sh save\n"
            "3. Tell Board: session needs restart"
        ).format(score)

    # Check for any single critical signal
    critical_signals = [
        name for name, sig in signals.items()
        if sig["score"] <= 10
    ]
    if critical_signals and status == "OK":
        status = "WARNING"
        recommendation = f"Critical signal(s): {', '.join(critical_signals)}"

    return {
        "score": score,
        "status": status,
        "signals": signals,
        "recommendation": recommendation,
        "call_count": get_call_count(),
        "timestamp": time.time(),
    }


def restart_dead_daemon(daemon_name: str) -> bool:
    """Restart a dead daemon using canonical command from governance_boot.sh.

    Returns True if restart attempted, False if daemon unknown or restart failed.
    """
    restart_map = {
        "k9_routing_subscriber": "cd /Users/haotianliu/.openclaw/workspace/ystar-company && nohup python3 scripts/k9_routing_subscriber.py > /tmp/k9_routing_subscriber.log 2>&1 &",
        "k9_alarm_consumer": "cd /Users/haotianliu/.openclaw/workspace/ystar-company && nohup python3 scripts/k9_alarm_consumer.py > /tmp/k9_alarm_consumer.log 2>&1 &",
        "cto_dispatch_broker": "cd /Users/haotianliu/.openclaw/workspace/ystar-company && nohup python3 scripts/cto_dispatch_broker.py > /tmp/cto_dispatch_broker.log 2>&1 &",
        "engineer_task_subscriber": "cd /Users/haotianliu/.openclaw/workspace/ystar-company && nohup python3 scripts/engineer_task_subscriber.py > /tmp/engineer_task_subscriber.log 2>&1 &",
    }

    command = restart_map.get(daemon_name)
    if not command:
        return False

    try:
        import subprocess
        subprocess.run(command, shell=True, check=False, timeout=5)
        return True
    except Exception:
        return False


def main():
    import argparse
    parser = argparse.ArgumentParser(description="Session health watchdog")
    parser.add_argument("--quick", action="store_true", help="Quick check (for statusline)")
    parser.add_argument("--full", action="store_true", help="Full check with details")
    parser.add_argument("--increment", action="store_true", help="Increment call count before check")
    parser.add_argument("--context-pct", type=float, default=None, help="Context window usage percentage")
    parser.add_argument("--statusline", action="store_true", help="Output for statusline (compact)")
    parser.add_argument("--ac-monitor", action="store_true", help="AC monitor mode: check daemon liveness, emit CIEU if <75, auto-restart dead daemons")
    args = parser.parse_args()

    # Try reading context_pct from stdin if not provided
    context_pct = args.context_pct
    if context_pct is None and not sys.stdin.isatty():
        try:
            stdin_data = json.loads(sys.stdin.read())
            context_pct = stdin_data.get("context_pct") or stdin_data.get("context_window", {}).get("used_percentage")
        except Exception:
            pass

    if args.increment:
        increment_call_count()

    # AC monitor mode: compute AC, emit CIEU if <75, auto-restart dead daemons
    if args.ac_monitor:
        ac_result = compute_agent_capability_score()
        score = ac_result["score"]
        violations = ac_result["violations"]

        # Auto-restart dead daemons if daemon_liveness signal failed
        daemon_liveness = ac_result["signals"]["daemon_liveness"]
        if daemon_liveness["score"] < 100:
            daemon_names = ["k9_routing_subscriber", "k9_alarm_consumer", "cto_dispatch_broker", "engineer_task_subscriber"]
            import subprocess
            for name in daemon_names:
                result = subprocess.run(["pgrep", "-f", name], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
                if result.returncode != 0:  # daemon dead
                    restarted = restart_dead_daemon(name)
                    print(f"[ac-monitor] {name} dead, restart={'OK' if restarted else 'FAILED'}", file=sys.stderr)

        print(json.dumps({"score": score, "violations": violations}))
        return

    result = compute_health(context_pct)

    if args.statusline:
        # Compact output for statusline: HP + AC scores
        hp_score = result["score"]
        hp_status = result["status"]
        if hp_status == "OK":
            hp_color = "\033[0;32m"  # green
        elif hp_status == "WARNING":
            hp_color = "\033[1;33m"  # yellow
        else:
            hp_color = "\033[1;31m"  # red
        reset = "\033[0m"

        # Compute AC score
        ac_result = compute_agent_capability_score()
        ac_score = ac_result["score"]
        if ac_score >= 75:
            ac_color = "\033[0;32m"  # green
        elif ac_score >= 50:
            ac_color = "\033[1;33m"  # yellow
        else:
            ac_color = "\033[1;31m"  # red

        print(f"{hp_color}HP:{hp_score:.0f}{reset} {ac_color}AC:{ac_score:.0f}{reset}", end="")
    elif args.quick:
        # Minimal JSON
        print(json.dumps({
            "score": result["score"],
            "status": result["status"],
            "recommendation": result["recommendation"]
        }))
    else:
        # Full JSON
        print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
