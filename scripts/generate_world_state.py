#!/usr/bin/env python3
"""
Mission Control / WORLD_STATE Generator
========================================
Auto-aggregate CEO's single wakeup context from 5 tool outputs.

Data Sources:
1. reports/priority_brief.md → company strategy (Y* + current phase)
2. knowledge/{role}/active_task.json → each role's status
3. .czl_subgoals.json → current campaign progress
4. scripts/wire_integrity_check.py → system health
5. .ystar_memory.db → CIEU 24h events + OVERDUE obligations
6. reports/daily/<today>_morning.md → external signals
7. BOARD_PENDING.md → Board unanswered questions

Output: memory/WORLD_STATE.md (single file, 7 sections)
"""
import json
import sqlite3
from datetime import datetime, timedelta
from pathlib import Path

REPO_ROOT = Path(__file__).parent.parent
OUTPUT_PATH = REPO_ROOT / "memory" / "WORLD_STATE.md"


def read_json(path: Path, default=None):
    """Safe JSON read with fallback."""
    if not path.exists():
        return default or {}
    try:
        return json.loads(path.read_text())
    except Exception:
        return default or {}


def read_md(path: Path, default=""):
    """Safe markdown read."""
    if not path.exists():
        return default
    return path.read_text()


def extract_priority_brief():
    """Extract company strategy from priority_brief.md."""
    brief_path = REPO_ROOT / "reports" / "priority_brief.md"
    content = read_md(brief_path, default="[priority_brief.md not found]")
    # Extract YAML frontmatter phase
    if "phase:" in content:
        phase_line = [l for l in content.split("\n") if "phase:" in l][0]
        phase = phase_line.split(":", 1)[1].strip().strip('"')
    else:
        phase = "unknown"
    
    # Extract next_session_p0_carryover (first 3 items)
    p0_items = []
    in_p0 = False
    for line in content.split("\n"):
        if "next_session_p0_carryover:" in line:
            in_p0 = True
            continue
        if in_p0 and line.strip().startswith("- "):
            p0_items.append(line.strip())
            if len(p0_items) >= 3:
                break
        elif in_p0 and not line.strip().startswith("- ") and line.strip():
            break
    
    return {"phase": phase, "p0_carryover": p0_items}


def extract_role_status():
    """Extract each role's active_task.json status."""
    roles = ["ceo", "cto", "cmo", "cso", "cfo", "secretary", 
             "eng-kernel", "eng-governance", "eng-platform", "eng-domains"]
    status = {}
    for role in roles:
        task_path = REPO_ROOT / "knowledge" / role / "active_task.json"
        task_data = read_json(task_path, default={"status": "no_active_task"})
        if task_data.get("status") == "deprecated":
            status[role] = "idle (deprecated task)"
        elif task_data.get("status") == "in_progress":
            status[role] = f"in_progress: {task_data.get('task_id', 'unknown')}"
        else:
            status[role] = task_data.get("status", "unknown")
    return status


def extract_campaign_progress():
    """Extract current campaign from .czl_subgoals.json."""
    czl_path = REPO_ROOT / ".czl_subgoals.json"
    czl = read_json(czl_path, default={})
    campaign = czl.get("campaign", "none")
    completed_count = len(czl.get("completed", []))
    remaining_count = len(czl.get("remaining", []))
    rt1 = czl.get("rt1_status", "unknown")
    current_sub = czl.get("current_subgoal")
    return {
        "campaign": campaign,
        "completed": completed_count,
        "remaining": remaining_count,
        "rt1_status": rt1,
        "current_subgoal": current_sub
    }


def extract_system_health():
    """Run wire_integrity_check.py and extract total_issues."""
    import subprocess
    try:
        result = subprocess.run(
            ["python3", str(REPO_ROOT / "scripts" / "wire_integrity_check.py")],
            capture_output=True, text=True, timeout=10
        )
        output = result.stdout

        # Parse output: "[OK] All wires intact" = 0 issues
        if "[OK] All wires intact" in output:
            return {"total_issues": 0}

        # Parse "total_issues: X" pattern (if wire_integrity adds this)
        if "total_issues" in output:
            for line in output.split("\n"):
                if "total_issues" in line.lower():
                    parts = line.split(":")
                    if len(parts) > 1:
                        try:
                            return {"total_issues": int(parts[1].strip())}
                        except ValueError:
                            pass

        # Fallback: count "[BROKEN]" lines
        broken_count = output.count("[BROKEN]")
        if broken_count > 0:
            return {"total_issues": broken_count}

        return {"total_issues": 0}  # Default: assume healthy if no explicit error
    except Exception as e:
        return {"total_issues": f"check_failed: {e}"}


def extract_cieu_24h():
    """Query CIEU DB for 24h event count + OVERDUE obligations."""
    db_path = REPO_ROOT / ".ystar_cieu.db"  # Corrected: was .ystar_memory.db
    if not db_path.exists():
        return {"event_count_24h": 0, "overdue_obligations": 0}
    
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # 24h event count
        yesterday_ts = (datetime.now() - timedelta(days=1)).timestamp()
        cursor.execute("SELECT COUNT(*) FROM cieu_events WHERE created_at > ?", (yesterday_ts,))
        event_count = cursor.fetchone()[0]
        
        # OVERDUE obligations (status=pending AND due_by < now)
        # Note: cieu_obligations table may not exist in .ystar_cieu.db, fail-open
        now_ts = datetime.now().timestamp()
        try:
            cursor.execute(
                "SELECT COUNT(*) FROM cieu_obligations WHERE status='pending' AND due_by < ?",
                (now_ts,)
            )
            overdue_count = cursor.fetchone()[0]
        except sqlite3.OperationalError:
            overdue_count = 0  # Table doesn't exist, fail-open
        
        conn.close()
        return {"event_count_24h": event_count, "overdue_obligations": overdue_count}
    except Exception as e:
        return {"event_count_24h": f"query_failed: {e}", "overdue_obligations": 0}


def extract_external_signals():
    """Read today's morning report (first 5 lines)."""
    today = datetime.now().strftime("%Y-%m-%d")
    morning_path = REPO_ROOT / "reports" / "daily" / f"{today}_morning.md"
    content = read_md(morning_path, default="[No morning report today]")
    lines = content.split("\n")[:5]
    return "\n".join(lines)


def extract_board_pending():
    """Read BOARD_PENDING.md if exists (truncate to first 20 lines)."""
    pending_path = REPO_ROOT / "BOARD_PENDING.md"
    content = read_md(pending_path, default="[No pending Board questions]")
    lines = content.split("\n")
    if len(lines) > 20:
        truncated = "\n".join(lines[:20])
        return f"{truncated}\n\n... ({len(lines) - 20} more lines, see BOARD_PENDING.md)"
    return content


def generate_world_state():
    """Generate memory/WORLD_STATE.md from all data sources."""
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    strategy = extract_priority_brief()
    roles = extract_role_status()
    campaign = extract_campaign_progress()
    health = extract_system_health()
    cieu = extract_cieu_24h()
    signals = extract_external_signals()
    pending = extract_board_pending()
    
    md_output = f"""# WORLD_STATE — Mission Control
**Generated**: {timestamp}
**Purpose**: Single file CEO reads on boot to restore full company context

---

## 1. Company Strategy
**Phase**: {strategy['phase']}
**Top 3 P0 Carryovers**:
{chr(10).join(strategy['p0_carryover']) if strategy['p0_carryover'] else '(none)'}

---

## 2. Role Status
"""
    for role, status in roles.items():
        md_output += f"- **{role}**: {status}\n"
    
    md_output += f"""
---

## 3. Current Campaign
**Campaign**: {campaign['campaign']}
**Progress**: {campaign['completed']} completed, {campaign['remaining']} remaining
**Rt+1 Status**: {campaign['rt1_status']}
**Current Subgoal**: {campaign['current_subgoal'] or '(none)'}

---

## 4. System Health
**Wire Integrity**: {health['total_issues']} issues
**CIEU 24h Events**: {cieu['event_count_24h']}
**Overdue Obligations**: {cieu['overdue_obligations']}

---

## 5. External Signals (Today)
```
{signals}
```

---

## 6. Board Pending
{pending}

---

## 7. Reserved (Auto-Expansion Slot)
(Future: K9 audit summary, stress test alerts, etc.)
"""
    
    OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT_PATH.write_text(md_output)
    print(f"✅ WORLD_STATE generated: {OUTPUT_PATH}")
    print(f"   Sections: 7 | Roles: {len(roles)} | Campaign: {campaign['campaign']}")


if __name__ == "__main__":
    generate_world_state()
