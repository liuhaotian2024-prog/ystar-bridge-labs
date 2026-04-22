#!/usr/bin/env python3
"""
Mission Control / WORLD_STATE Generator
========================================
Auto-aggregate CEO's single wakeup context from multiple tool outputs.

Data Sources:
1. reports/priority_brief.md → company strategy (Y* + current phase)
2. knowledge/{role}/active_task.json → each role's status
3. .czl_subgoals.json → current campaign progress
4. scripts/wire_integrity_check.py → system health
5. .ystar_cieu.db → CIEU 24h events + OVERDUE obligations
6. reports/daily/<today>_morning.md → external signals
7. BOARD_PENDING.md → Board unanswered questions
8. Y* Field State (ξ) → M-axis frequency from CIEU + 7d drift
9. Commission Error Heatmap → 11-component unified dashboard (governance_audit_unified.py)
10-12. Ecosystem: Y*gov repo, gov-mcp, K9Audit, today's commits

Output: memory/WORLD_STATE.md (single file, 13 sections)
"""
import json
import sqlite3
from datetime import datetime, timedelta
from pathlib import Path

# Local imports (fail-open if not available)
try:
    from governance_audit_unified import full_dashboard, format_dashboard_md
except ImportError:
    try:
        import sys
        sys.path.insert(0, str(Path(__file__).parent))
        from governance_audit_unified import full_dashboard, format_dashboard_md
    except ImportError:
        full_dashboard = None  # type: ignore
        format_dashboard_md = None  # type: ignore

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
    """Run wire_integrity_check.py and extract total_issues + Y* schema v2 compliance."""
    import subprocess
    result_dict = {}

    # Wire integrity check
    try:
        result = subprocess.run(
            ["python3", str(REPO_ROOT / "scripts" / "wire_integrity_check.py")],
            capture_output=True, text=True, timeout=10
        )
        output = result.stdout

        # Parse output: "[OK] All wires intact" = 0 issues
        if "[OK] All wires intact" in output:
            result_dict["total_issues"] = 0
        elif "total_issues" in output:
            for line in output.split("\n"):
                if "total_issues" in line.lower():
                    parts = line.split(":")
                    if len(parts) > 1:
                        try:
                            result_dict["total_issues"] = int(parts[1].strip())
                        except ValueError:
                            pass
        else:
            # Fallback: count "[BROKEN]" lines
            broken_count = output.count("[BROKEN]")
            result_dict["total_issues"] = broken_count if broken_count > 0 else 0
    except Exception as e:
        result_dict["total_issues"] = f"check_failed: {e}"

    # W5.1: Y* schema v2 compliance (W5.2: fixed to iterate criteria, not validate entire dict)
    try:
        import sys
        sys.path.insert(0, str(REPO_ROOT.parent / "Y-star-gov"))
        from ystar.governance.contract_lifecycle import validate_y_star_schema_v2

        czl_path = REPO_ROOT / ".czl_subgoals.json"
        if czl_path.exists():
            czl_data = json.loads(czl_path.read_text())
            criteria = czl_data.get("y_star_criteria", [])
            total = len(criteria)
            valid_count = 0
            all_errors = []

            for criterion in criteria:
                validation_result = validate_y_star_schema_v2(criterion)
                if validation_result.get("valid", False):
                    valid_count += 1
                else:
                    all_errors.extend(validation_result.get("errors", []))

            if valid_count == total:
                result_dict["y_star_schema_v2"] = f"{valid_count}/{total} valid"
            else:
                result_dict["y_star_schema_v2"] = f"{valid_count}/{total} valid ({len(all_errors)} errors)"
        else:
            result_dict["y_star_schema_v2"] = "no_campaign"
    except Exception as e:
        result_dict["y_star_schema_v2"] = f"check_unavailable: {e}"

    return result_dict


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


def extract_y_star_field_state():
    """8th source: Y* Field State (ξ) — Mission axis frequency + 7-day drift.

    Classifies 24h CIEU events into M-axis buckets via keyword hierarchy (KH path)
    from Y_STAR_FIELD_THEORY_SPEC.md Section 11:
      M-1 Survivability:  handoff / boot / session / restore / persist
      M-2a Commission:    forget_guard / deny / enforce / wire_broken
      M-2b Omission:      omission / overdue / alarm / circuit_breaker
      M-3  Value Prod:    customer / revenue / dogfood / demo / sale / pricing

    Drift = today's axis share vs prior 7-day average axis share (↑/↓/→).
    """
    db_path = REPO_ROOT / ".ystar_cieu.db"
    if not db_path.exists():
        return {
            "M-1": 0, "M-2a": 0, "M-2b": 0, "M-3": 0,
            "total_24h": 0, "drift_24h": {}, "error": "cieu_db_missing"
        }

    # SQL for M-axis keyword classification across event_type + task_description
    # Using LIKE patterns (case-insensitive in SQLite by default for ASCII)
    axis_sql = """
    SELECT
      SUM(CASE WHEN event_type LIKE '%handoff%'
               OR event_type LIKE '%HOOK_BOOT%'
               OR event_type LIKE '%session%'
               OR event_type LIKE '%boot%'
               OR LOWER(task_description) LIKE '%restore%'
               OR LOWER(task_description) LIKE '%persist%'
               OR LOWER(task_description) LIKE '%handoff%'
               OR LOWER(task_description) LIKE '%session%'
           THEN 1 ELSE 0 END) as m1,
      SUM(CASE WHEN event_type LIKE '%FORGET_GUARD%'
               OR event_type LIKE '%deny%'
               OR event_type LIKE '%enforce%'
               OR event_type LIKE '%WIRE_BROKEN%'
               OR LOWER(task_description) LIKE '%forget_guard%'
               OR LOWER(task_description) LIKE '%deny%'
               OR LOWER(task_description) LIKE '%enforce%'
           THEN 1 ELSE 0 END) as m2a,
      SUM(CASE WHEN event_type LIKE '%omission%'
               OR event_type LIKE '%OVERDUE%'
               OR event_type LIKE '%alarm%'
               OR event_type LIKE '%circuit_breaker%'
               OR LOWER(task_description) LIKE '%omission%'
               OR LOWER(task_description) LIKE '%overdue%'
               OR LOWER(task_description) LIKE '%alarm%'
           THEN 1 ELSE 0 END) as m2b,
      SUM(CASE WHEN event_type LIKE '%customer%'
               OR event_type LIKE '%revenue%'
               OR event_type LIKE '%dogfood%'
               OR LOWER(task_description) LIKE '%customer%'
               OR LOWER(task_description) LIKE '%revenue%'
               OR LOWER(task_description) LIKE '%dogfood%'
               OR LOWER(task_description) LIKE '%demo%'
               OR LOWER(task_description) LIKE '%sale%'
               OR LOWER(task_description) LIKE '%pricing%'
           THEN 1 ELSE 0 END) as m3,
      COUNT(*) as total
    FROM cieu_events
    WHERE created_at > ?
    """

    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()

        now_ts = datetime.now().timestamp()
        day_ago = now_ts - 86400
        week_ago = now_ts - 7 * 86400

        # 24h counts
        cursor.execute(axis_sql, (day_ago,))
        row_24h = cursor.fetchone()
        m1_24h = row_24h[0] or 0
        m2a_24h = row_24h[1] or 0
        m2b_24h = row_24h[2] or 0
        m3_24h = row_24h[3] or 0
        total_24h = row_24h[4] or 0

        # 7-day counts (for drift baseline — compute daily average)
        cursor.execute(axis_sql, (week_ago,))
        row_7d = cursor.fetchone()
        m1_7d = row_7d[0] or 0
        m2a_7d = row_7d[1] or 0
        m2b_7d = row_7d[2] or 0
        m3_7d = row_7d[3] or 0
        total_7d = row_7d[4] or 1  # avoid div/0

        conn.close()

        # Compute drift: compare 24h share vs 7-day average share
        # share = axis_count / total_count for the period
        def _drift_indicator(count_24h, total_24h_val, count_7d, total_7d_val):
            """Return drift arrow: ↑ (>20% above baseline), ↓ (<20% below), → (stable)."""
            if total_24h_val == 0 or total_7d_val == 0:
                return "→"
            share_24h = count_24h / total_24h_val
            share_7d = count_7d / total_7d_val
            if share_7d == 0:
                return "↑" if share_24h > 0 else "→"
            ratio = share_24h / share_7d
            if ratio > 1.2:
                return "↑"
            elif ratio < 0.8:
                return "↓"
            return "→"

        drift = {
            "M-1": _drift_indicator(m1_24h, total_24h, m1_7d, total_7d),
            "M-2a": _drift_indicator(m2a_24h, total_24h, m2a_7d, total_7d),
            "M-2b": _drift_indicator(m2b_24h, total_24h, m2b_7d, total_7d),
            "M-3": _drift_indicator(m3_24h, total_24h, m3_7d, total_7d),
        }

        # Compute 7d daily averages for context
        avg_7d = {
            "M-1": round(m1_7d / 7),
            "M-2a": round(m2a_7d / 7),
            "M-2b": round(m2b_7d / 7),
            "M-3": round(m3_7d / 7),
        }

        return {
            "M-1": m1_24h, "M-2a": m2a_24h, "M-2b": m2b_24h, "M-3": m3_24h,
            "total_24h": total_24h,
            "avg_7d": avg_7d,
            "drift_24h": drift,
        }
    except Exception as e:
        return {
            "M-1": 0, "M-2a": 0, "M-2b": 0, "M-3": 0,
            "total_24h": 0, "drift_24h": {}, "error": str(e)
        }


def extract_commission_error_dashboard():
    """9th source: Commission Error Heatmap — 11-component unified dashboard.

    Queries governance_audit_unified.py for 24h commission error aggregation
    across all 11 LIVE detectors (per Y_STAR_FIELD_THEORY_SPEC.md Section 14.2).
    Fail-open: returns placeholder if module unavailable.
    """
    if full_dashboard is None or format_dashboard_md is None:
        return "(governance_audit_unified module not available — run `python3 scripts/governance_audit_unified.py` standalone)"
    try:
        dashboard = full_dashboard()
        return format_dashboard_md(dashboard)
    except Exception as e:
        return f"(commission error dashboard failed: {e})"


def _run_git(cmd, cwd):
    import subprocess
    try:
        r = subprocess.run(cmd, cwd=str(cwd), capture_output=True, text=True, timeout=5)
        return r.stdout.strip()
    except Exception as e:
        return f"(err: {e})"


def extract_ystar_gov_state():
    """W12 — scan Y*gov product repo."""
    import subprocess
    ygov = Path("/Users/haotianliu/.openclaw/workspace/Y-star-gov")
    if not ygov.exists():
        return "**Y*gov**: path not found"
    head = _run_git(["git", "log", "-1", "--format=%h %s"], ygov)[:100]
    commits_24h = _run_git(["git", "log", "--since=24 hours ago", "--oneline"], ygov).count("\n") + 1 if _run_git(["git", "log", "--since=24 hours ago", "--oneline"], ygov) else 0
    ahead = _run_git(["git", "rev-list", "--count", "origin/main..HEAD"], ygov) or "0"
    tests_count = len(list((ygov / "tests").glob("*.py"))) if (ygov / "tests").exists() else 0
    version = "?"
    try:
        toml = (ygov / "pyproject.toml").read_text(encoding="utf-8")
        for line in toml.split("\n"):
            if "version" in line and "=" in line:
                version = line.split("=")[1].strip().strip('"')
                break
    except Exception:
        pass
    return f"**HEAD**: `{head}`\n**24h commits**: {commits_24h}\n**ahead origin**: {ahead}\n**test files**: {tests_count}\n**version**: {version}"


def extract_gov_mcp_state():
    """W12 — gov-mcp nested in Y*gov."""
    govmcp = Path("/Users/haotianliu/.openclaw/workspace/Y-star-gov/gov_mcp")
    if not govmcp.exists():
        return "**gov-mcp**: not found"
    server = govmcp / "server.py"
    loc = "?"
    try:
        loc = str(len(server.read_text().split("\n")))
    except Exception:
        pass
    local_health = Path("/Users/haotianliu/.openclaw/workspace/ystar-company/gov_mcp/health.py")
    return f"**location**: `{govmcp}`\n**server.py LoC**: {loc}\n**ystar-company side health.py**: {'exists' if local_health.exists() else 'missing'}"


def extract_today_commits():
    """W-continuity: 24h git log aggregated across 2 repos."""
    ystar_company = Path("/Users/haotianliu/.openclaw/workspace/ystar-company")
    ygov = Path("/Users/haotianliu/.openclaw/workspace/Y-star-gov")
    lines = []
    for label, repo in [("ystar-company", ystar_company), ("Y*gov", ygov)]:
        log = _run_git(["git", "log", "--since=24 hours ago", "--format=%h %ad %s", "--date=format:%H:%M"], repo)
        if log:
            lines.append(f"\n**{label}** ({len(log.split(chr(10)))} commits):")
            for l in log.split("\n")[:20]:
                lines.append(f"- {l[:120]}")
        else:
            lines.append(f"\n**{label}**: no commits")
    return "\n".join(lines) if lines else "(empty)"


def extract_k9audit_state():
    """W12 — K9Audit read-only reference."""
    import time
    k9 = Path("/tmp/K9Audit")
    if not k9.exists():
        return "**K9Audit**: not cloned locally (run: `git clone https://github.com/liuhaotian2024-prog/K9Audit /tmp/K9Audit`)"
    head = _run_git(["git", "log", "-1", "--format=%h %s"], k9)[:100]
    stale_s = time.time() - (k9 / ".git").stat().st_mtime
    stale_days = int(stale_s / 86400)
    return f"**local clone**: `/tmp/K9Audit`\n**HEAD**: `{head}`\n**stale days**: {stale_days}\n**migration queue**: CausalChainAnalyzer + Auditor + k9_repo_audit.py → CIEU (TODO)"


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
    field = extract_y_star_field_state()

    # Format ξ field state section
    def _fmt_field_section(f):
        if f.get("error"):
            return f"**Error**: {f['error']}"
        lines = []
        lines.append(f"**Total CIEU events (24h)**: {f['total_24h']}")
        lines.append("")
        lines.append("| M-Axis | Description | 24h Count | 7d Avg/Day | Drift |")
        lines.append("|--------|-------------|-----------|------------|-------|")
        axis_labels = {
            "M-1": "Survivability (session/boot/handoff/persist)",
            "M-2a": "Commission prevention (forget_guard/deny/enforce)",
            "M-2b": "Omission prevention (omission/overdue/alarm)",
            "M-3": "Value production (customer/revenue/dogfood/demo)",
        }
        for axis in ["M-1", "M-2a", "M-2b", "M-3"]:
            count = f.get(axis, 0)
            avg = f.get("avg_7d", {}).get(axis, 0)
            drift = f.get("drift_24h", {}).get(axis, "?")
            label = axis_labels[axis]
            lines.append(f"| **{axis}** | {label} | {count} | {avg} | {drift} |")

        # Coverage ratio: what fraction of 24h events hit at least one axis
        classified = f["M-1"] + f["M-2a"] + f["M-2b"] + f["M-3"]
        coverage = round(classified / f["total_24h"] * 100, 1) if f["total_24h"] > 0 else 0
        lines.append("")
        lines.append(f"**Classified coverage**: {classified}/{f['total_24h']} ({coverage}%)")
        lines.append(f"**Unclassified**: {f['total_24h'] - classified} events (routine ops / K9 routing)")
        # Drift interpretation
        drift_vals = f.get("drift_24h", {})
        up_axes = [k for k, v in drift_vals.items() if v == "↑"]
        down_axes = [k for k, v in drift_vals.items() if v == "↓"]
        if up_axes:
            lines.append(f"**Drift alert**: {', '.join(up_axes)} trending UP vs 7d baseline")
        if down_axes:
            lines.append(f"**Drift alert**: {', '.join(down_axes)} trending DOWN vs 7d baseline")
        if not up_axes and not down_axes:
            lines.append("**Drift**: all axes stable vs 7d baseline")
        return "\n".join(lines)

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
**Y* Schema v2 Compliance**: {health.get('y_star_schema_v2', 'unknown')}
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
(Future: stress test alerts, campaign analytics, etc.)

---

## 8. Y* Field State (xi) — Mission axis frequency + drift
{_fmt_field_section(field)}

---

## 9. Commission Error Heatmap — 11-component unified dashboard
{extract_commission_error_dashboard()}

---

## 10. Ecosystem — Y*gov Product Repo
{extract_ystar_gov_state()}

---

## 11. Ecosystem — gov-mcp (nested in Y*gov)
{extract_gov_mcp_state()}

---

## 12. Ecosystem — K9Audit (read-only reference)
{extract_k9audit_state()}

---

## 13. Today's Commits (24h) — both repos

{extract_today_commits()}
"""

    OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT_PATH.write_text(md_output)
    print(f"✅ WORLD_STATE generated: {OUTPUT_PATH}")
    print(f"   Sections: 13 | Roles: {len(roles)} | Campaign: {campaign['campaign']}")
    # Print ξ field summary to stdout for livefire verification
    print(f"   ξ Field: M-1={field.get('M-1',0)} M-2a={field.get('M-2a',0)} M-2b={field.get('M-2b',0)} M-3={field.get('M-3',0)} (total_24h={field.get('total_24h',0)})")


if __name__ == "__main__":
    generate_world_state()
