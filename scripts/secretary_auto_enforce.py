#!/usr/bin/env python3
"""
[L2] Secretary Auto-Enforce — Fix drift events automatically

Run by Secretary subagent (not cron) to auto-fix common drift patterns:
1. MATURITY_TAG_MISSING → amend commit with [LX] tag
2. IMMUTABLE_FORGOT_BREAK_GLASS → write reminder to next boot pack
3. active_agent_drift → restore correct agent to .ystar_active_agent
4. Emit SECRETARY_AUTO_FIX CIEU for each fix

NOTE: Secretary has write permissions for .ystar_active_agent (unlike other agents)
"""

import sys
import json
import sqlite3
import subprocess
from pathlib import Path
from datetime import datetime, timedelta

WORKSPACE_ROOT = Path("/Users/haotianliu/.openclaw/workspace/ystar-company")
CIEU_DB = WORKSPACE_ROOT / ".ystar_cieu.db"
ACTIVE_AGENT_FILE = WORKSPACE_ROOT / ".ystar_active_agent"
BOOT_PACK_DIR = WORKSPACE_ROOT / "memory/boot_packs"


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


def get_recent_drift(hours_back=1):
    """Get drift events from last N hours"""
    try:
        conn = sqlite3.connect(CIEU_DB)
        cursor = conn.cursor()

        cutoff_time = datetime.now() - timedelta(hours=hours_back)
        cursor.execute("""
            SELECT id, rule_id, details, timestamp FROM cieu_events
            WHERE event_type = 'FORGET_GUARD'
            AND timestamp > ?
            ORDER BY timestamp DESC
        """, (cutoff_time.isoformat(),))

        rows = cursor.fetchall()
        conn.close()
        return rows
    except Exception:
        return []


def fix_maturity_tag_missing(drift_id, details):
    """Fix missing [LX] tag in commit message"""
    try:
        # Parse details to get commit message verb
        details_data = json.loads(details) if details.startswith('{') else {"commit_msg": details}
        commit_msg = details_data.get("commit_msg", "")

        # Determine L tag based on verb (heuristic mapping)
        verb = commit_msg.split()[0].lower() if commit_msg else ""
        l_tag_map = {
            "fix": "[L1]",
            "feat": "[L3]",
            "refactor": "[L2]",
            "docs": "[L1]",
            "test": "[L2]",
            "chore": "[L1]",
            "perf": "[L2]",
            "auto": "[L2]"
        }
        l_tag = l_tag_map.get(verb, "[L1]")  # Default to L1

        # Amend last commit with L tag
        new_msg = f"{l_tag} {commit_msg}"
        subprocess.run(
            ["git", "commit", "--amend", "-m", new_msg],
            cwd=WORKSPACE_ROOT,
            capture_output=True,
            timeout=5
        )

        emit_cieu("SECRETARY_AUTO_FIX", json.dumps({
            "drift_id": drift_id,
            "fix_type": "maturity_tag",
            "old_msg": commit_msg,
            "new_msg": new_msg
        }))
        return True
    except Exception as e:
        print(f"Failed to fix maturity tag: {e}", file=sys.stderr)
        return False


def fix_immutable_forgot_break_glass(drift_id, details):
    """Write reminder to next boot pack"""
    try:
        BOOT_PACK_DIR.mkdir(parents=True, exist_ok=True)
        reminder_file = BOOT_PACK_DIR / f"break_glass_reminder_{drift_id}.md"

        reminder_file.write_text(f"""# Break Glass Reminder
Generated: {datetime.now().isoformat()}
Drift Event: {drift_id}

## Constitutional Immutables Forgotten

{details}

## Next Session Action

Before modifying any constitutional immutable:
1. Check if this is a T1 (existential) or T2 (strategic) trigger
2. Run: `python3 scripts/ceo_mode_manager.py force_break_glass --trigger T1`
3. Wait for approval before proceeding
""")

        emit_cieu("SECRETARY_AUTO_FIX", json.dumps({
            "drift_id": drift_id,
            "fix_type": "break_glass_reminder",
            "reminder_file": str(reminder_file)
        }))
        return True
    except Exception as e:
        print(f"Failed to write break glass reminder: {e}", file=sys.stderr)
        return False


def fix_active_agent_drift(drift_id, details):
    """Restore correct agent to .ystar_active_agent"""
    try:
        # Parse details to get correct agent
        details_data = json.loads(details) if details.startswith('{') else {}
        correct_agent = details_data.get("expected_agent", "ceo")  # Default to CEO

        # Write correct agent (Secretary has permission for this file)
        ACTIVE_AGENT_FILE.write_text(correct_agent)

        emit_cieu("SECRETARY_AUTO_FIX", json.dumps({
            "drift_id": drift_id,
            "fix_type": "active_agent_restore",
            "restored_agent": correct_agent
        }))
        return True
    except Exception as e:
        print(f"Failed to restore active agent: {e}", file=sys.stderr)
        return False


def main():
    """Run auto-enforcement on recent drift"""
    drift_events = get_recent_drift(hours_back=1)

    if not drift_events:
        print("No drift events to fix", file=sys.stderr)
        return

    fixed_count = 0

    for drift_id, rule_id, details, timestamp in drift_events:
        if rule_id == "MATURITY_TAG_MISSING":
            if fix_maturity_tag_missing(drift_id, details):
                fixed_count += 1
        elif rule_id == "IMMUTABLE_FORGOT_BREAK_GLASS":
            if fix_immutable_forgot_break_glass(drift_id, details):
                fixed_count += 1
        elif "active_agent_drift" in rule_id.lower():
            if fix_active_agent_drift(drift_id, details):
                fixed_count += 1

    print(f"Fixed {fixed_count}/{len(drift_events)} drift events", file=sys.stderr)


if __name__ == "__main__":
    main()
