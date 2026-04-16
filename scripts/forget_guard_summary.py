#!/usr/bin/env python3
"""
[L2→L3] Forget Guard Summary — Hourly drift spike detection

@cron: Every hour, scan last 1h FORGET_GUARD DRIFT events
Emit DRIFT_SPIKE CIEU if >3/h of any category
Write reports/drift_hourly/{date_hour}.md
"""

import sys
import json
import sqlite3
from pathlib import Path
from datetime import datetime, timedelta
from collections import Counter
sys.path.insert(0, str(Path(__file__).parent))
from _cieu_helpers import _get_current_agent

WORKSPACE_ROOT = Path("/Users/haotianliu/.openclaw/workspace/ystar-company")
CIEU_DB = WORKSPACE_ROOT / ".ystar_cieu.db"
DRIFT_HOURLY_DIR = WORKSPACE_ROOT / "reports/drift_hourly"


def emit_cieu(event_type, details):
    """Emit CIEU event"""
    try:
        conn = sqlite3.connect(CIEU_DB)
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO cieu_events (timestamp, event_type, details)
            VALUES (?, ?, ?)
        """, (datetime.now().isoformat(), event_type, details))
        conn.commit()
        conn.close()
    except Exception:
        pass


def get_drift_events(hours_back=1):
    """Get FORGET_GUARD drift events from last N hours"""
    try:
        conn = sqlite3.connect(CIEU_DB)
        cursor = conn.cursor()

        cutoff_time = datetime.now() - timedelta(hours=hours_back)
        cursor.execute("""
            SELECT event_type, drift_details, created_at FROM cieu_events
            WHERE event_type LIKE 'FORGET_GUARD%'
            AND created_at > ?
            ORDER BY created_at DESC
        """, (cutoff_time.timestamp(),))

        rows = cursor.fetchall()
        conn.close()

        # Parse rule_id from drift_details JSON
        parsed = []
        for event_type, details_json, timestamp in rows:
            try:
                details = json.loads(details_json) if details_json else {}
                rule_id = details.get('rule_id', event_type)
            except (json.JSONDecodeError, AttributeError):
                rule_id = event_type

            parsed.append((rule_id, details_json, datetime.fromtimestamp(timestamp).isoformat()))

        return parsed
    except Exception as e:
        print(f"Error querying CIEU: {e}", file=sys.stderr)
        return []


def analyze_drift(events):
    """Analyze drift patterns"""
    if not events:
        return {}, {}

    rule_counts = Counter(e[0] for e in events)
    time_distribution = {}

    for rule_id, details, timestamp in events:
        hour = datetime.fromisoformat(timestamp).strftime("%Y-%m-%d %H:00")
        if hour not in time_distribution:
            time_distribution[hour] = Counter()
        time_distribution[hour][rule_id] += 1

    return rule_counts, time_distribution


def write_hourly_report(rule_counts, time_dist, events):
    """Write hourly drift report"""
    DRIFT_HOURLY_DIR.mkdir(parents=True, exist_ok=True)

    now = datetime.now()
    report_path = DRIFT_HOURLY_DIR / f"{now.strftime('%Y%m%d_%H')}00.md"

    content = f"""# Drift Hourly Summary
Generated: {now.isoformat()}
Period: Last 1 hour

## Summary

Total drift events: {len(events)}

## By Rule Category

"""

    for rule_id, count in rule_counts.most_common():
        content += f"- `{rule_id}`: {count} events\n"

    content += "\n## Time Distribution\n\n"
    for hour, counts in sorted(time_dist.items()):
        content += f"### {hour}\n"
        for rule_id, count in counts.most_common():
            content += f"- `{rule_id}`: {count}\n"

    content += "\n## Spike Detection\n\n"
    spikes = [rule_id for rule_id, count in rule_counts.items() if count > 3]
    if spikes:
        content += f"**DRIFT_SPIKE detected**: {len(spikes)} categories exceeded 3/h threshold\n\n"
        for rule_id in spikes:
            content += f"- `{rule_id}`: {rule_counts[rule_id]} events\n"
    else:
        content += "No spikes detected (all categories ≤3/h)\n"

    report_path.write_text(content)
    return report_path, spikes


def detect_article_11_drift(hours_back=1):
    """
    [AMENDMENT-023] Layer 3: Post-audit drift detection.
    Scan for user_message containing decision keywords + missing ARTICLE_11 events in time window.
    Returns list of drift incidents.
    """
    DECISION_KEYWORDS = [
        "strategy", "mission", "amendment", "roadmap", "pivot", "reorg",
        "restructure", "deploy", "launch", "重大", "决策", "战略", "架构"
    ]

    try:
        conn = sqlite3.connect(CIEU_DB)
        cursor = conn.cursor()

        cutoff_time = datetime.now() - timedelta(hours=hours_back)
        cutoff_unix = cutoff_time.timestamp()

        # Find user_message events with decision keywords
        cursor.execute("""
            SELECT event_id, created_at, drift_details FROM cieu_events
            WHERE event_type = 'user_message'
            AND created_at > ?
            ORDER BY created_at DESC
        """, (cutoff_unix,))

        user_messages = cursor.fetchall()

        incidents = []
        for event_id, msg_time, msg_content in user_messages:
            if not msg_content:
                continue

            # Check if message contains decision keywords
            has_decision_keyword = any(kw in msg_content.lower() for kw in DECISION_KEYWORDS)
            if not has_decision_keyword:
                continue

            # Check for Article 11 events within +/- 1h window of message
            window_start = msg_time - 3600  # 1h before
            window_end = msg_time + 3600    # 1h after

            cursor.execute("""
                SELECT COUNT(*) FROM cieu_events
                WHERE event_type LIKE 'ARTICLE_11_LAYER_%_COMPLETE'
                AND created_at BETWEEN ? AND ?
            """, (window_start, window_end))

            article_11_count = cursor.fetchone()[0]

            if article_11_count == 0:
                # No Article 11 events around decision message → drift
                incidents.append({
                    "event_id": event_id,
                    "timestamp": datetime.fromtimestamp(msg_time).isoformat(),
                    "message_preview": msg_content[:100],
                    "matched_keyword": next((kw for kw in DECISION_KEYWORDS if kw in msg_content.lower()), "unknown")
                })

        conn.close()
        return incidents

    except Exception as e:
        print(f"[ARTICLE_11_DRIFT] Error detecting drift: {e}", file=sys.stderr)
        return []


def main():
    """Run hourly drift summary"""
    events = get_drift_events(hours_back=1)

    if not events:
        print("No drift events in last 1h", file=sys.stderr)
    else:
        rule_counts, time_dist = analyze_drift(events)
        report_path, spikes = write_hourly_report(rule_counts, time_dist, events)

        print(f"Report written: {report_path}", file=sys.stderr)

        if spikes:
            emit_cieu("DRIFT_SPIKE", json.dumps({
                "period": "1h",
                "total_events": len(events),
                "spike_categories": spikes,
                "spike_counts": {rule_id: rule_counts[rule_id] for rule_id in spikes},
                "report": str(report_path)
            }))
            print(f"DRIFT_SPIKE emitted: {len(spikes)} categories", file=sys.stderr)

    # [AMENDMENT-023] Layer 3: Article 11 drift detection
    article_11_incidents = detect_article_11_drift(hours_back=1)
    if article_11_incidents:
        print(f"[ARTICLE_11_DRIFT] Detected {len(article_11_incidents)} decision messages without Article 11 events", file=sys.stderr)

        emit_cieu("ARTICLE_11_DRIFT_SPIKE", json.dumps({
            "period": "1h",
            "incident_count": len(article_11_incidents),
            "incidents": article_11_incidents[:5]  # Top 5 incidents
        }))

        # Write to hourly report
        if 'report_path' in locals() and report_path:
            with open(report_path, 'a') as f:
                f.write(f"\n\n## Article 11 Drift Detection\n\n")
                f.write(f"**{len(article_11_incidents)} decision messages without Article 11 discipline**\n\n")
                for inc in article_11_incidents[:5]:
                    f.write(f"- {inc['timestamp']} | keyword: `{inc['matched_keyword']}` | preview: {inc['message_preview']}\n")


if __name__ == "__main__":
    main()
