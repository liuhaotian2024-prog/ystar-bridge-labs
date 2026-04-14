#!/usr/bin/env python3
"""
K9Audit: Narrative Coherence Bias Detection
Scans CIEU DB for CEO assertions that mismatch tool calls.
"""
import sqlite3
import json
import re
from pathlib import Path
from datetime import datetime, timedelta
from collections import defaultdict

def load_session_id():
    config_path = Path("/Users/haotianliu/.openclaw/workspace/ystar-company/.ystar_session.json")
    if not config_path.exists():
        return None
    with open(config_path) as f:
        return json.load(f).get("session_id")

def extract_narrative_claims(text):
    """Extract dispatch/delegation claims from assistant text."""
    patterns = [
        r'派给\s*(\w+)',
        r'dispatched? to (\w+)',
        r'调起\s*(\w+)',
        r'spawn\s+(\w+)',
        r'(\w+)\s*(sub-?agent|分工|就位|并行)',
        r'delegation to (\w+)',
        r'assigned to (\w+)',
    ]
    claims = []
    for pattern in patterns:
        matches = re.finditer(pattern, text, re.IGNORECASE)
        for m in matches:
            target = m.group(1).lower()
            claims.append({
                'target': target,
                'phrase': m.group(0),
                'position': m.start()
            })
    return claims

def extract_actual_tool_calls(cieu_events, idx):
    """Extract actual tool calls from CIEU following this event."""
    # Look ahead 10 events for tool calls
    tool_calls = []
    for i in range(idx + 1, min(idx + 11, len(cieu_events))):
        event = cieu_events[i]
        skill = event.get('U_t', {}).get('skill', '')
        if skill:
            params = event.get('U_t', {}).get('params', {})
            agent_target = None
            if skill == 'Agent':
                agent_target = params.get('agent_id', '')
                if agent_target:
                    agent_target = agent_target.lower()
            tool_calls.append({
                'skill': skill,
                'agent_target': agent_target,
                'timestamp': event.get('timestamp')
            })
    return tool_calls

def detect_narrative_gaps(db_path, session_id, days=7):
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    # Get current session events
    cursor.execute("""
        SELECT created_at, event_type, agent_id, skill_name, params_json, result_json, decision, passed
        FROM cieu_events
        WHERE session_id = ?
        ORDER BY seq_global ASC
    """, (session_id,))

    current_events = []
    for row in cursor.fetchall():
        ts, ev_type, agent_id, skill, params, result, decision, passed = row
        params_dict = {}
        result_dict = {}
        try:
            params_dict = json.loads(params) if params else {}
        except:
            pass
        try:
            result_dict = json.loads(result) if result else {}
        except:
            result_dict = {'raw': result[:500] if result else ''}

        event = {
            'timestamp': datetime.fromtimestamp(ts).isoformat() if ts else '',
            'event_type': ev_type or '',
            'U_t': {'skill': skill, 'params': params_dict},
            'X_t': {'agent_id': agent_id or ''},
            'Y_t+1': {'result': result_dict},
            'R_t+1': {'decision': decision, 'passed': bool(passed)},
        }
        current_events.append(event)

    # Get 7-day events
    cutoff = datetime.now() - timedelta(days=days)
    cursor.execute("""
        SELECT created_at, event_type, agent_id, skill_name, params_json, result_json, decision, passed
        FROM cieu_events
        WHERE created_at >= ?
        ORDER BY seq_global ASC
    """, (cutoff.timestamp(),))

    all_events = []
    for row in cursor.fetchall():
        ts, ev_type, agent_id, skill, params, result, decision, passed = row
        params_dict = {}
        result_dict = {}
        try:
            params_dict = json.loads(params) if params else {}
        except:
            pass
        try:
            result_dict = json.loads(result) if result else {}
        except:
            result_dict = {'raw': result[:500] if result else ''}

        event = {
            'timestamp': datetime.fromtimestamp(ts).isoformat() if ts else '',
            'event_type': ev_type or '',
            'U_t': {'skill': skill, 'params': params_dict},
            'X_t': {'agent_id': agent_id or ''},
            'Y_t+1': {'result': result_dict},
            'R_t+1': {'decision': decision, 'passed': bool(passed)},
        }
        all_events.append(event)

    conn.close()

    # Detect gaps
    gaps_current = []
    gaps_7day = []

    def scan_for_gaps(events, output_list):
        for idx, event in enumerate(events):
            # Look for CEO assistant turns with delegation text
            agent_id = event.get('X_t', {}).get('agent_id', '')
            if agent_id != 'ceo':
                continue

            # Look for narrative in any output field
            skill = event.get('U_t', {}).get('skill', '')
            result = event.get('Y_t+1', {}).get('result', '')

            # Convert result to string if it's a dict
            if isinstance(result, dict):
                result = json.dumps(result)
            elif not isinstance(result, str):
                continue

            claims = extract_narrative_claims(result)
            if not claims:
                continue

            # Check actual tool calls
            tool_calls = extract_actual_tool_calls(events, idx)

            for claim in claims:
                claimed_target = claim['target']
                # Check if any tool call matches
                matched = False
                for tc in tool_calls:
                    if tc['skill'] == 'Agent' and tc['agent_target']:
                        if claimed_target in tc['agent_target'] or tc['agent_target'] in claimed_target:
                            matched = True
                            break

                if not matched and tool_calls:
                    # GAP FOUND
                    gap = {
                        'timestamp': event.get('timestamp'),
                        'claimed_target': claimed_target,
                        'claim_phrase': claim['phrase'],
                        'actual_tool_calls': [tc['skill'] for tc in tool_calls],
                        'agent_targets': [tc['agent_target'] for tc in tool_calls if tc['agent_target']],
                        'causal_chain': f"text claim '{claim['phrase']}' → expected Agent({claimed_target}) → actual {tool_calls[0]['skill'] if tool_calls else 'none'}",
                    }
                    output_list.append(gap)

    scan_for_gaps(current_events, gaps_current)
    scan_for_gaps(all_events, gaps_7day)

    return {
        'session_id': session_id,
        'current_session_gaps': len(gaps_current),
        'current_gaps': gaps_current,
        '7day_gaps': len(gaps_7day),
        '7day_gap_list': gaps_7day,
    }

def main():
    db_path = Path("/Users/haotianliu/.openclaw/workspace/ystar-company/.ystar_cieu.db")
    session_id = load_session_id()

    if not session_id:
        print("ERROR: No session_id in .ystar_session.json")
        return 1

    if not db_path.exists():
        print(f"ERROR: CIEU DB not found at {db_path}")
        return 1

    result = detect_narrative_gaps(db_path, session_id, days=7)

    # Write report
    report_path = Path("/Users/haotianliu/.openclaw/workspace/ystar-company/reports/narrative_bias_empirical_20260413.md")
    report_path.parent.mkdir(parents=True, exist_ok=True)

    with open(report_path, 'w') as f:
        f.write(f"# Narrative Coherence Bias — K9Audit Empirical Report\n")
        f.write(f"Generated: {datetime.now().isoformat()}\n")
        f.write(f"Session: {result['session_id']}\n\n")

        f.write(f"## Summary\n\n")
        f.write(f"- Current session gaps: {result['current_session_gaps']}\n")
        f.write(f"- 7-day total gaps: {result['7day_gaps']}\n\n")

        if result['current_gaps']:
            f.write(f"## Current Session Gaps\n\n")
            for idx, gap in enumerate(result['current_gaps'], 1):
                f.write(f"### Gap {idx}\n")
                f.write(f"- **Timestamp**: {gap['timestamp']}\n")
                f.write(f"- **Claimed**: {gap['claim_phrase']} → {gap['claimed_target']}\n")
                f.write(f"- **Actual tool calls**: {', '.join(gap['actual_tool_calls'])}\n")
                if gap['agent_targets']:
                    f.write(f"- **Agent targets**: {', '.join(gap['agent_targets'])}\n")
                f.write(f"- **Causal chain**: {gap['causal_chain']}\n\n")

        if result['7day_gap_list']:
            f.write(f"## 7-Day Pattern Analysis\n\n")
            claim_phrases = defaultdict(int)
            for gap in result['7day_gap_list']:
                claim_phrases[gap['claim_phrase']] += 1

            f.write(f"### Most Common Claim Phrases\n\n")
            for phrase, count in sorted(claim_phrases.items(), key=lambda x: x[1], reverse=True)[:5]:
                f.write(f"- `{phrase}`: {count} occurrences\n")
            f.write("\n")

            f.write(f"### Sample Gaps (first 5)\n\n")
            for idx, gap in enumerate(result['7day_gap_list'][:5], 1):
                f.write(f"#### Gap {idx}\n")
                f.write(f"- **Timestamp**: {gap['timestamp']}\n")
                f.write(f"- **Causal chain**: {gap['causal_chain']}\n\n")

    # Print summary
    pattern = "none"
    if result['7day_gap_list']:
        common = defaultdict(int)
        for g in result['7day_gap_list']:
            common[g['claim_phrase']] += 1
        pattern = max(common.items(), key=lambda x: x[1])[0] if common else "varied"

    print(f"{result['current_session_gaps']} narrative gaps found in session {session_id}, 7-day {result['7day_gaps']}, pattern = [{pattern}]")
    return 0

if __name__ == '__main__':
    exit(main())
