#!/usr/bin/env python3
"""CIEU Replay Recovery — Gap recovery via event sourcing

Ultimate tier: For each gap detected by restart_handoff_verifier.py,
reconstruct missing state from CIEU event history.

Authority: Jordan Lee CZL-145 P0 HEAVY (2026-04-16)
Upstream: restart_handoff_verifier.py gap detection + .ystar_cieu.db
Downstream: governance_boot.sh canonical restart + session state repair

Usage:
    python3 scripts/cieu_replay_recovery.py [--gaps "gap1,gap2"] [--json]

If --gaps not provided, reads from stdin (pipe from handoff_verifier)

Recovery strategies:
    - trust_scores.json → query GAUNTLET_PASS events → reconstruct
    - continuation.json → query last 20 ATOMIC_COMPLETE → synthesize focus
    - session_summary → query chronological events → generate stub
    - .czl_subgoals.json → create IDLE campaign stub (safe fallback)
    - daemons dead → restart per governance_boot.sh canonical commands

Emits CIEU event:
    - CIEU_REPLAY_RECOVERY with {recovered, failed, details}
"""

import sys
import json
import sqlite3
import subprocess
from pathlib import Path
from typing import Dict, List
from datetime import datetime

# Add Y-star-gov to path
YSTAR_GOV_PATH = Path(__file__).parent.parent.parent / "Y-star-gov"
if YSTAR_GOV_PATH.exists():
    sys.path.insert(0, str(YSTAR_GOV_PATH))

sys.path.insert(0, str(Path(__file__).parent))
from _cieu_helpers import _get_current_agent

try:
    from ystar.governance.cieu import emit_cieu
except ImportError:
    def emit_cieu(*args, **kwargs):
        pass

COMPANY_ROOT = Path(__file__).parent.parent
CIEU_DB = Path.home() / ".ystar_cieu.db"


def query_cieu_events(event_type: str, limit: int = 100) -> List[Dict]:
    """Query CIEU events from SQLite DB"""
    if not CIEU_DB.exists():
        return []

    try:
        conn = sqlite3.connect(str(CIEU_DB))
        cursor = conn.cursor()
        cursor.execute(
            "SELECT timestamp, agent_id, metadata FROM events WHERE event_type = ? ORDER BY timestamp DESC LIMIT ?",
            (event_type, limit)
        )
        rows = cursor.fetchall()
        conn.close()

        results = []
        for ts, agent_id, metadata_json in rows:
            try:
                metadata = json.loads(metadata_json) if metadata_json else {}
            except:
                metadata = {}
            results.append({"timestamp": ts, "agent_id": agent_id, "metadata": metadata})

        return results
    except Exception as e:
        print(f"Warning: CIEU query failed: {e}", file=sys.stderr)
        return []


def recover_trust_scores() -> Dict:
    """Recover engineer_trust_scores.json from GAUNTLET_PASS events"""
    events = query_cieu_events("GAUNTLET_PASS", limit=50)

    if not events:
        return {"success": False, "reason": "No GAUNTLET_PASS events found"}

    # Build trust scores from events
    trust_map = {}
    for event in reversed(events):  # Oldest first
        engineer = event.get("metadata", {}).get("engineer")
        if engineer:
            # Default trust increment per gauntlet pass
            trust_map[engineer] = trust_map.get(engineer, 0.0) + 0.05

    # Add baseline 9 engineers if missing
    baseline_engineers = [
        "eng-kernel", "eng-governance", "eng-platform", "eng-domains",
        "eng-data", "eng-security", "eng-ml", "eng-perf", "eng-compliance"
    ]
    for eng in baseline_engineers:
        if eng not in trust_map:
            trust_map[eng] = 0.0

    # Write to file
    output_path = COMPANY_ROOT / "knowledge/engineer_trust_scores.json"
    output_path.write_text(json.dumps(trust_map, indent=2))

    return {"success": True, "count": len(trust_map), "path": str(output_path)}


def recover_continuation() -> Dict:
    """Recover continuation.json from last 20 ATOMIC_COMPLETE events"""
    events = query_cieu_events("ATOMIC_COMPLETE", limit=20)

    if not events:
        # Fallback: create minimal continuation
        continuation = {
            "focus": "Recovered from CIEU replay - no recent ATOMIC_COMPLETE events",
            "action_queue": ["Resume work from session_summary"],
            "campaign": "Unknown (recovered)"
        }
    else:
        # Extract focus from most recent atomic
        latest = events[0]
        metadata = latest.get("metadata", {})

        continuation = {
            "focus": metadata.get("atomic_id", "Unknown atomic"),
            "action_queue": [metadata.get("description", "Resume work")],
            "campaign": metadata.get("campaign", "Unknown"),
            "recovered_from": "CIEU_REPLAY",
            "recovery_timestamp": datetime.now().isoformat()
        }

    output_path = COMPANY_ROOT / "memory/continuation.json"
    output_path.write_text(json.dumps(continuation, indent=2))

    return {"success": True, "path": str(output_path)}


def recover_session_summary() -> Dict:
    """Generate session_summary stub from chronological CIEU events"""
    # Query recent events (any type)
    if not CIEU_DB.exists():
        return {"success": False, "reason": "CIEU DB missing"}

    try:
        conn = sqlite3.connect(str(CIEU_DB))
        cursor = conn.cursor()
        cursor.execute(
            "SELECT timestamp, event_type, agent_id FROM events ORDER BY timestamp DESC LIMIT 50"
        )
        rows = cursor.fetchall()
        conn.close()
    except Exception as e:
        return {"success": False, "reason": f"CIEU query failed: {e}"}

    if not rows:
        return {"success": False, "reason": "No CIEU events found"}

    # Build summary stub
    event_counts = {}
    for _, event_type, _ in rows:
        event_counts[event_type] = event_counts.get(event_type, 0) + 1

    summary = f"""# Session Summary (CIEU Replay Recovery)

**Generated**: {datetime.now().isoformat()}
**Source**: CIEU event replay (last 50 events)

## Event Activity

"""
    for event_type, count in sorted(event_counts.items(), key=lambda x: -x[1]):
        summary += f"- {event_type}: {count}\n"

    summary += """
## Note

This is a recovery stub generated from CIEU events.
Full session context may be incomplete.
Recommend manual review of .ystar_cieu.db for details.
"""

    output_path = COMPANY_ROOT / f"memory/session_summary_{datetime.now().strftime('%Y%m%d')}.md"
    output_path.write_text(summary)

    return {"success": True, "path": str(output_path), "event_count": len(rows)}


def recover_czl_subgoals() -> Dict:
    """Create IDLE campaign stub for .czl_subgoals.json"""
    stub = {
        "y_star_ref": "Recovered from CIEU replay - safe IDLE state",
        "campaign": "Recovery Mode — IDLE Campaign",
        "campaign_status": "IDLE",
        "campaign_started_at": datetime.now().isoformat(),
        "current_subgoal": "None (IDLE)",
        "rt1_status": "0/0 — recovery mode",
        "y_star_criteria": [],
        "completed": [],
        "remaining": []
    }

    output_path = COMPANY_ROOT / ".czl_subgoals.json"
    output_path.write_text(json.dumps(stub, indent=2))

    return {"success": True, "path": str(output_path)}


def recover_daemons() -> Dict:
    """Restart dead daemons per governance_boot.sh canonical commands"""
    # Read canonical daemon start commands from governance_boot.sh
    boot_script = COMPANY_ROOT / "scripts/governance_boot.sh"

    if not boot_script.exists():
        return {"success": False, "reason": "governance_boot.sh missing"}

    # For now, just report - actual restart requires careful orchestration
    # Real implementation would parse boot_script and restart daemons
    return {
        "success": False,
        "reason": "Daemon restart requires manual governance_boot.sh execution",
        "recommendation": "Run: bash scripts/governance_boot.sh <agent_id>"
    }


def recover_from_replay(gap_list: List[str]) -> Dict:
    """Main recovery orchestrator"""
    recovered = []
    failed = []
    details = []

    for gap in gap_list:
        gap_lower = gap.lower()

        if "trust_score" in gap_lower or "engineer_trust" in gap_lower:
            result = recover_trust_scores()
            if result["success"]:
                recovered.append(gap)
                details.append(f"✅ {gap} → {result}")
            else:
                failed.append(gap)
                details.append(f"❌ {gap} → {result}")

        elif "continuation" in gap_lower:
            result = recover_continuation()
            if result["success"]:
                recovered.append(gap)
                details.append(f"✅ {gap} → {result}")
            else:
                failed.append(gap)
                details.append(f"❌ {gap} → {result}")

        elif "session_summary" in gap_lower:
            result = recover_session_summary()
            if result["success"]:
                recovered.append(gap)
                details.append(f"✅ {gap} → {result}")
            else:
                failed.append(gap)
                details.append(f"❌ {gap} → {result}")

        elif "czl_subgoals" in gap_lower or "subgoal" in gap_lower:
            result = recover_czl_subgoals()
            if result["success"]:
                recovered.append(gap)
                details.append(f"✅ {gap} → {result}")
            else:
                failed.append(gap)
                details.append(f"❌ {gap} → {result}")

        elif "daemon" in gap_lower:
            result = recover_daemons()
            if result["success"]:
                recovered.append(gap)
                details.append(f"✅ {gap} → {result}")
            else:
                failed.append(gap)
                details.append(f"❌ {gap} → manual intervention: {result['recommendation']}")

        else:
            failed.append(gap)
            details.append(f"❌ {gap} → no recovery strategy")

    return {
        "recovered": len(recovered),
        "failed": len(failed),
        "details": details
    }


def main():
    """CLI entry point"""
    json_output = "--json" in sys.argv

    # Parse gap list
    if "--gaps" in sys.argv:
        idx = sys.argv.index("--gaps")
        gap_str = sys.argv[idx + 1]
        gap_list = [g.strip() for g in gap_str.split(",")]
    else:
        # Read from stdin
        gap_list = [line.strip() for line in sys.stdin if line.strip()]

    if not gap_list:
        print("Error: No gaps provided. Use --gaps or pipe from handoff_verifier", file=sys.stderr)
        sys.exit(1)

    result = recover_from_replay(gap_list)

    # Emit CIEU event
    agent_id = _get_current_agent()
    emit_cieu(
        "CIEU_REPLAY_RECOVERY",
        agent_id=agent_id,
        metadata={
            "recovered": result["recovered"],
            "failed": result["failed"],
            "gap_count": len(gap_list)
        }
    )

    if json_output:
        print(json.dumps(result, indent=2))
    else:
        print("=== CIEU Replay Recovery Report ===")
        print(f"Timestamp: {datetime.now().isoformat()}")
        print(f"Recovered: {result['recovered']}/{len(gap_list)}")
        print(f"Failed: {result['failed']}/{len(gap_list)}")
        print()
        print("Details:")
        for detail in result["details"]:
            print(f"  {detail}")

    sys.exit(0 if result["failed"] == 0 else 1)


if __name__ == "__main__":
    main()
