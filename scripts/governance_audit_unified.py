#!/usr/bin/env python3
"""
Commission Error Unified Dashboard
====================================
Aggregates 11 LIVE "doing wrong" (commission) detectors' CIEU events
into a single dashboard for WORLD_STATE Section 9.

The 11 components (per Y_STAR_FIELD_THEORY_SPEC.md Section 14.2):
  1. narrative_coherence_detector  -> NARRATIVE_GAP, narrative_bias_detected
  2. observable_action_detector    -> (observable evidence gaps — detected via REPLY_TEMPLATE_VIOLATION)
  3. claim_mismatch                -> E1_TOOL_USES_CLAIM_MISMATCH, TOOL_USES_CLAIM_MISMATCH
  4. causal_chain_analyzer         -> (causal analysis — via K9_AUDIT_TRIGGERED anomalies)
  5. counterfactual_engine         -> (counterfactual verify — detected via CROBA_PHANTOM_VIOLATION_NOTE)
  6. k9_silent_fire_audit          -> K9_VIOLATION_DETECTED, K9_AUDIT_TRIGGERED
  7. unified_compliance_audit      -> CZL_DISPATCH_MISSING_5TUPLE, COORDINATOR_REPLY_MISSING_5TUPLE
  8. amendment_coverage_audit      -> CANONICAL_HASH_DRIFT, SESSION_JSON_SCHEMA_VIOLATION
  9. enforcement_observer          -> ENFORCEMENT_GAP_PERSISTENT
 10. directive_evaluator           -> DIRECTIVE_LIVENESS_EVAL, DIRECTIVE_REJECTED
 11. metalearning                  -> BEHAVIOR_RULE_VIOLATION, BEHAVIOR_RULE_WARNING

Additional commission signals caught by hooks:
  - FORGET_GUARD (deny), FORGET_GUARD_K9_WARN, FORGET_GUARD_K9_DENY
  - WIRE_BROKEN
  - REPLY_TEMPLATE_VIOLATION
  - MATURITY_TAG_MISSING
  - CEO_CODE_WRITE_DRIFT, CHOICE_IN_REPLY_DRIFT, DEFER_LANGUAGE_DRIFT
  - OFF_TARGET_WARNING

M-Axis classification (per M Triangle):
  M-1   Survivability:  SESSION_JSON_SCHEMA_VIOLATION, CANONICAL_HASH_DRIFT, WIRE_BROKEN
  M-2a  Commission:     All 11 detector signals (core)
  M-2b  Omission:       (handled by omission_engine, NOT in this dashboard)
  M-3   Value Prod:     OFF_TARGET_WARNING, MATURITY_TAG_MISSING (indirect quality impact)

Output: JSON dict with commission_error_total, by_actor, by_detector, by_axis, drift_24h_vs_7d
"""
import json
import sqlite3
import sys
from datetime import datetime, timedelta
from pathlib import Path

REPO_ROOT = Path(__file__).parent.parent
CIEU_DB = REPO_ROOT / ".ystar_cieu.db"

# ── 11-detector event type mapping ──────────────────────────────────────────
# Each detector maps to one or more CIEU event_type values.
# The SQL query uses IN + LIKE to catch variants.
COMMISSION_EVENT_TYPES = [
    # 1. narrative_coherence_detector
    "NARRATIVE_GAP",
    "narrative_bias_detected",
    # 2. observable_action_detector (fires via reply scan)
    "REPLY_TEMPLATE_VIOLATION",
    # 3. claim_mismatch
    "E1_TOOL_USES_CLAIM_MISMATCH",
    "TOOL_USES_CLAIM_MISMATCH",
    "COORDINATOR_REPLY_MISSING_5TUPLE",
    # 4. causal_chain_analyzer (fires into K9 pipeline)
    # (no dedicated event_type — captured under K9_AUDIT_TRIGGERED)
    # 5. counterfactual_engine
    "CROBA_PHANTOM_VIOLATION_NOTE",
    # 6. k9_silent_fire_audit
    "K9_VIOLATION_DETECTED",
    "K9_AUDIT_TRIGGERED",
    # 7. unified_compliance_audit
    "CZL_DISPATCH_MISSING_5TUPLE",
    # 8. amendment_coverage_audit
    "CANONICAL_HASH_DRIFT",
    "SESSION_JSON_SCHEMA_VIOLATION",
    # 9. enforcement_observer
    "ENFORCEMENT_GAP_PERSISTENT",
    # 10. directive_evaluator
    "DIRECTIVE_LIVENESS_EVAL",
    "DIRECTIVE_REJECTED",
    # 11. metalearning / behavior rules
    "BEHAVIOR_RULE_VIOLATION",
    "BEHAVIOR_RULE_WARNING",
    # Hook-level commission catches
    "FORGET_GUARD",
    "FORGET_GUARD_K9_WARN",
    "FORGET_GUARD_K9_DENY",
    "STOP_HOOK_K9_DENY",
    "WIRE_BROKEN",
    "MATURITY_TAG_MISSING",
    "CEO_CODE_WRITE_DRIFT",
    "CHOICE_IN_REPLY_DRIFT",
    "DEFER_LANGUAGE_DRIFT",
    "DEFER_IN_REPLY_DRIFT",
    "DEFER_IN_BASH_DRIFT",
    "DEFER_IN_COMMIT_DRIFT",
    "OFF_TARGET_WARNING",
    "WHITELIST_GAP",
    "WHITELIST_DRIFT",
]

# Map event_types to their originating detector (1-11)
DETECTOR_MAP = {
    "NARRATIVE_GAP": "narrative_coherence_detector",
    "narrative_bias_detected": "narrative_coherence_detector",
    "REPLY_TEMPLATE_VIOLATION": "observable_action_detector",
    "E1_TOOL_USES_CLAIM_MISMATCH": "claim_mismatch",
    "TOOL_USES_CLAIM_MISMATCH": "claim_mismatch",
    "COORDINATOR_REPLY_MISSING_5TUPLE": "claim_mismatch",
    "CROBA_PHANTOM_VIOLATION_NOTE": "counterfactual_engine",
    "K9_VIOLATION_DETECTED": "k9_silent_fire_audit",
    "K9_AUDIT_TRIGGERED": "k9_silent_fire_audit",
    "CZL_DISPATCH_MISSING_5TUPLE": "unified_compliance_audit",
    "CANONICAL_HASH_DRIFT": "amendment_coverage_audit",
    "SESSION_JSON_SCHEMA_VIOLATION": "amendment_coverage_audit",
    "ENFORCEMENT_GAP_PERSISTENT": "enforcement_observer",
    "DIRECTIVE_LIVENESS_EVAL": "directive_evaluator",
    "DIRECTIVE_REJECTED": "directive_evaluator",
    "BEHAVIOR_RULE_VIOLATION": "metalearning",
    "BEHAVIOR_RULE_WARNING": "metalearning",
    # Hook-level catches -> grouped under "hook_commission_catch"
    "FORGET_GUARD": "hook_commission_catch",
    "FORGET_GUARD_K9_WARN": "hook_commission_catch",
    "FORGET_GUARD_K9_DENY": "hook_commission_catch",
    "STOP_HOOK_K9_DENY": "hook_commission_catch",
    "WIRE_BROKEN": "hook_commission_catch",
    "MATURITY_TAG_MISSING": "hook_commission_catch",
    "CEO_CODE_WRITE_DRIFT": "hook_commission_catch",
    "CHOICE_IN_REPLY_DRIFT": "hook_commission_catch",
    "DEFER_LANGUAGE_DRIFT": "hook_commission_catch",
    "DEFER_IN_REPLY_DRIFT": "hook_commission_catch",
    "DEFER_IN_BASH_DRIFT": "hook_commission_catch",
    "DEFER_IN_COMMIT_DRIFT": "hook_commission_catch",
    "OFF_TARGET_WARNING": "hook_commission_catch",
    "WHITELIST_GAP": "hook_commission_catch",
    "WHITELIST_DRIFT": "hook_commission_catch",
}

# M-Axis classification for commission errors
M_AXIS_MAP = {
    # M-1 Survivability: config/schema/wire integrity
    "SESSION_JSON_SCHEMA_VIOLATION": "M-1",
    "CANONICAL_HASH_DRIFT": "M-1",
    "WIRE_BROKEN": "M-1",
    # M-3 Value Production: quality/maturity impact
    "OFF_TARGET_WARNING": "M-3",
    "MATURITY_TAG_MISSING": "M-3",
    # Everything else -> M-2a (commission prevention)
}

# Canonical actor normalization
ACTOR_ALIASES = {
    "ceo": "ceo",
    "Ethan-CTO": "cto",
    "ethan-cto": "cto",
    "Leo-Kernel": "eng-kernel",
    "leo-kernel": "eng-kernel",
    "Maya-Governance": "eng-governance",
    "maya-governance": "eng-governance",
    "Ryan-Platform": "eng-platform",
    "ryan-platform": "eng-platform",
    "Jordan-Domains": "eng-domains",
    "jordan-domains": "eng-domains",
    "Samantha-Secretary": "secretary",
    "samantha-secretary": "secretary",
    "system:k9_subscriber": "system",
    "orchestrator": "system",
    "agent": "system",
    "system": "system",
    "governance": "system",
    "intervention_engine": "system",
    "path_a_agent": "system",
    "unknown": "unknown",
    "unidentified": "unknown",
    "": "unknown",
}


def _normalize_actor(raw: str) -> str:
    """Normalize agent_id to canonical actor name."""
    if raw in ACTOR_ALIASES:
        return ACTOR_ALIASES[raw]
    low = raw.lower()
    if low in ACTOR_ALIASES:
        return ACTOR_ALIASES[low]
    # Partial match for known engineer names
    for prefix, canonical in [
        ("eng-kernel", "eng-kernel"), ("eng-governance", "eng-governance"),
        ("eng-platform", "eng-platform"), ("eng-domains", "eng-domains"),
        ("leo", "eng-kernel"), ("maya", "eng-governance"),
        ("ryan", "eng-platform"), ("jordan", "eng-domains"),
        ("ethan", "cto"), ("samantha", "secretary"),
    ]:
        if prefix in low:
            return canonical
    return raw


def query_commission_errors(hours: int = 24) -> dict:
    """Query CIEU DB for commission error events in the last N hours.

    Returns dict with:
      commission_error_total: int
      by_actor: {actor: count}
      by_detector: {detector_name: count}
      by_axis: {M-1: count, M-2a: count, M-3: count}
      by_event_type: {event_type: count}
      top_5_event_types: [(event_type, count), ...]
    """
    if not CIEU_DB.exists():
        return {
            "commission_error_total": 0,
            "by_actor": {},
            "by_detector": {},
            "by_axis": {"M-1": 0, "M-2a": 0, "M-3": 0},
            "by_event_type": {},
            "top_5_event_types": [],
            "error": "cieu_db_missing",
        }

    placeholders = ",".join(["?" for _ in COMMISSION_EVENT_TYPES])
    cutoff = (datetime.now() - timedelta(hours=hours)).timestamp()

    try:
        conn = sqlite3.connect(CIEU_DB)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()

        cursor.execute(
            f"""
            SELECT event_type, agent_id, COUNT(*) as cnt
            FROM cieu_events
            WHERE created_at > ?
              AND event_type IN ({placeholders})
            GROUP BY event_type, agent_id
            """,
            [cutoff] + COMMISSION_EVENT_TYPES,
        )
        rows = cursor.fetchall()
        conn.close()

        total = 0
        by_actor: dict[str, int] = {}
        by_detector: dict[str, int] = {}
        by_axis: dict[str, int] = {"M-1": 0, "M-2a": 0, "M-3": 0}
        by_event_type: dict[str, int] = {}

        for row in rows:
            et = row["event_type"]
            actor = _normalize_actor(row["agent_id"] or "unknown")
            cnt = row["cnt"]

            total += cnt

            # By actor
            by_actor[actor] = by_actor.get(actor, 0) + cnt

            # By detector
            detector = DETECTOR_MAP.get(et, "unknown")
            by_detector[detector] = by_detector.get(detector, 0) + cnt

            # By M-axis
            axis = M_AXIS_MAP.get(et, "M-2a")
            by_axis[axis] = by_axis.get(axis, 0) + cnt

            # By event type
            by_event_type[et] = by_event_type.get(et, 0) + cnt

        # Top 5 event types
        top_5 = sorted(by_event_type.items(), key=lambda x: -x[1])[:5]

        # Sort by_actor and by_detector by count descending
        by_actor = dict(sorted(by_actor.items(), key=lambda x: -x[1]))
        by_detector = dict(sorted(by_detector.items(), key=lambda x: -x[1]))

        return {
            "commission_error_total": total,
            "by_actor": by_actor,
            "by_detector": by_detector,
            "by_axis": by_axis,
            "by_event_type": by_event_type,
            "top_5_event_types": top_5,
        }

    except Exception as e:
        return {
            "commission_error_total": 0,
            "by_actor": {},
            "by_detector": {},
            "by_axis": {"M-1": 0, "M-2a": 0, "M-3": 0},
            "by_event_type": {},
            "top_5_event_types": [],
            "error": str(e),
        }


def query_drift_24h_vs_7d() -> dict:
    """Compare 24h commission error rate vs 7-day daily average.

    Returns drift dict with direction arrows per detector.
    """
    if not CIEU_DB.exists():
        return {"error": "cieu_db_missing"}

    result_24h = query_commission_errors(hours=24)
    result_7d = query_commission_errors(hours=168)  # 7 days

    drift = {}
    all_detectors = set(list(result_24h.get("by_detector", {}).keys()) +
                        list(result_7d.get("by_detector", {}).keys()))

    for det in sorted(all_detectors):
        count_24h = result_24h.get("by_detector", {}).get(det, 0)
        avg_7d = result_7d.get("by_detector", {}).get(det, 0) / 7.0

        if avg_7d == 0:
            arrow = "^" if count_24h > 0 else "="
        else:
            ratio = count_24h / avg_7d
            if ratio > 1.2:
                arrow = "^"
            elif ratio < 0.8:
                arrow = "v"
            else:
                arrow = "="
        drift[det] = {
            "24h": count_24h,
            "7d_avg_daily": round(avg_7d, 1),
            "direction": arrow,
        }

    # Total drift
    total_24h = result_24h.get("commission_error_total", 0)
    total_7d_avg = result_7d.get("commission_error_total", 0) / 7.0
    if total_7d_avg == 0:
        total_arrow = "^" if total_24h > 0 else "="
    else:
        ratio = total_24h / total_7d_avg
        if ratio > 1.2:
            total_arrow = "^"
        elif ratio < 0.8:
            total_arrow = "v"
        else:
            total_arrow = "="

    drift["_total"] = {
        "24h": total_24h,
        "7d_avg_daily": round(total_7d_avg, 1),
        "direction": total_arrow,
    }

    return drift


def full_dashboard() -> dict:
    """Return complete commission error dashboard."""
    errors_24h = query_commission_errors(hours=24)
    drift = query_drift_24h_vs_7d()

    return {
        "timestamp": datetime.now().isoformat(),
        "commission_error_total": errors_24h["commission_error_total"],
        "by_actor": errors_24h["by_actor"],
        "by_detector": errors_24h["by_detector"],
        "by_axis": errors_24h["by_axis"],
        "top_5_event_types": errors_24h["top_5_event_types"],
        "drift_24h_vs_7d": drift,
        "error": errors_24h.get("error"),
    }


def format_dashboard_md(dashboard: dict) -> str:
    """Format dashboard dict into markdown for WORLD_STATE."""
    lines = []

    if dashboard.get("error"):
        lines.append(f"**Error**: {dashboard['error']}")
        return "\n".join(lines)

    total = dashboard["commission_error_total"]
    lines.append(f"**Total commission errors (24h)**: {total}")
    lines.append("")

    # By M-axis table
    by_axis = dashboard.get("by_axis", {})
    lines.append("**By M-Axis**:")
    lines.append("")
    lines.append("| Axis | Description | 24h Count |")
    lines.append("|------|-------------|-----------|")
    axis_labels = {
        "M-1": "Survivability (schema/wire/config drift)",
        "M-2a": "Commission prevention (core 11 detectors)",
        "M-3": "Value quality (maturity/off-target)",
    }
    for axis in ["M-1", "M-2a", "M-3"]:
        count = by_axis.get(axis, 0)
        label = axis_labels.get(axis, axis)
        lines.append(f"| **{axis}** | {label} | {count} |")
    lines.append("")

    # By detector table
    by_det = dashboard.get("by_detector", {})
    if by_det:
        lines.append("**By Detector (11 components + hook catches)**:")
        lines.append("")
        lines.append("| Detector | 24h Count | Drift vs 7d |")
        lines.append("|----------|-----------|-------------|")
        drift_data = dashboard.get("drift_24h_vs_7d", {})
        for det, cnt in by_det.items():
            d = drift_data.get(det, {})
            arrow = d.get("direction", "?")
            avg = d.get("7d_avg_daily", "?")
            lines.append(f"| {det} | {cnt} | {arrow} (avg {avg}/d) |")
        lines.append("")

    # By actor table (top 10)
    by_actor = dashboard.get("by_actor", {})
    if by_actor:
        lines.append("**By Actor (top 10)**:")
        lines.append("")
        lines.append("| Actor | 24h Commission Errors |")
        lines.append("|-------|----------------------|")
        for actor, cnt in list(by_actor.items())[:10]:
            lines.append(f"| {actor} | {cnt} |")
        lines.append("")

    # Top 5 event types
    top5 = dashboard.get("top_5_event_types", [])
    if top5:
        lines.append("**Top 5 Event Types**:")
        for et, cnt in top5:
            lines.append(f"- `{et}`: {cnt}")
        lines.append("")

    # Overall drift
    drift_total = dashboard.get("drift_24h_vs_7d", {}).get("_total", {})
    if drift_total:
        direction = drift_total.get("direction", "?")
        avg = drift_total.get("7d_avg_daily", "?")
        lines.append(f"**Overall drift**: {direction} (24h={total}, 7d avg/day={avg})")

    return "\n".join(lines)


if __name__ == "__main__":
    dashboard = full_dashboard()
    print(json.dumps(dashboard, indent=2, ensure_ascii=False))
