#!/usr/bin/env python3
"""
CZL Boot Injector — HiAgent subgoal-tree compression for multi-session campaigns.
Reads .czl_subgoals.json and outputs 3 compact blocks for governance boot injection.

Usage: python3 czl_boot_inject.py <agent_id>
Output: Y* / Current / Completed (5 most recent) summaries
"""
import json
import sys
from pathlib import Path
from datetime import datetime, timezone

def main():
    if len(sys.argv) < 2:
        print("[CZL BOOT INJECT] ERROR: missing agent_id argument", file=sys.stderr)
        sys.exit(1)

    agent_id = sys.argv[1]
    ystar_company = Path(__file__).parent.parent
    czl_file = ystar_company / ".czl_subgoals.json"

    if not czl_file.exists():
        print(f"[CZL BOOT INJECT] No .czl_subgoals.json found — skipping injection (agent: {agent_id})")
        return

    try:
        data = json.loads(czl_file.read_text(encoding="utf-8"))
    except Exception as e:
        print(f"[CZL BOOT INJECT] ERROR reading {czl_file}: {e}", file=sys.stderr)
        sys.exit(1)

    # === Block 1: Y* ===
    y_star_ref = data.get("y_star_ref", "undefined")
    campaign = data.get("campaign", "undefined")
    rt1_status = data.get("rt1_status", "0/0")

    print("=" * 80)
    print("[CZL BOOT INJECT] Campaign Subgoal Tree")
    print("=" * 80)
    print(f"Y* = {y_star_ref}")
    print(f"Campaign: {campaign}")
    print(f"Rt+1 Status: {rt1_status}")
    print()

    # === Block 2: Current Subgoal ===
    current = data.get("current_subgoal")
    if current:
        goal_id = current.get("id", "?")
        goal_text = current.get("goal", "")
        owner = current.get("owner", "unassigned")
        started = current.get("started", "")
        rt1_predicate = current.get("rt1_predicate", "")

        print(f"CURRENT SUBGOAL: {goal_id}")
        print(f"  Goal: {goal_text}")
        print(f"  Owner: {owner}")
        print(f"  Started: {started}")
        print(f"  Rt+1 Predicate: {rt1_predicate}")
    else:
        print("CURRENT SUBGOAL: None — CEO must push next from remaining[]")
    print()

    # === Block 3: Completed (5 most recent) ===
    completed = data.get("completed", [])
    if completed:
        print(f"COMPLETED ({len(completed)} total, showing last 5):")
        for item in list(reversed(completed))[:5]:  # reverse to show newest first
            item_id = item.get("id", "?")
            summary = item.get("summary", "no summary")
            duration = item.get("duration_min", "?")
            print(f"  [{item_id}] {summary} ({duration} min)")
    else:
        print("COMPLETED: None yet — campaign just started")
    print()

    # === Warnings ===
    warnings = []

    # Check for vague summaries
    for item in completed:
        summary = item.get("summary", "")
        if "[SUMMARY_VAGUE]" in summary or "[AI_COMPRESS_FAILED]" in summary:
            warnings.append(f"⚠️ {item['id']} has degraded summary — CEO should review")

    # Check for stale current_subgoal
    if current and current.get("started"):
        try:
            started_dt = datetime.fromisoformat(current["started"].replace("Z", "+00:00"))
            age_hours = (datetime.now(timezone.utc) - started_dt).total_seconds() / 3600
            if age_hours > 24:
                warnings.append(f"⚠️ Current subgoal {current['id']} running for {age_hours:.1f}h — consider split or escalate")
        except:
            pass

    # Check for idle state
    remaining = data.get("remaining", [])
    if not current and remaining:
        warnings.append(f"⚠️ No current_subgoal but {len(remaining)} tasks in remaining[] — CEO must push next")

    # W5.1: Y* schema v2 validation (Campaign v3 Phase 3)
    try:
        sys.path.insert(0, str(ystar_company.parent / "Y-star-gov"))
        from ystar.governance.contract_lifecycle import validate_y_star_schema_v2

        validation_result = validate_y_star_schema_v2(data)
        if not validation_result.get("valid", False):
            errors = validation_result.get("errors", [])
            warnings.append(f"⚠️ Y* schema v2 validation: {len(errors)} error(s) — fix y_star_criteria[] structure")
            for err in errors[:3]:  # Show first 3 errors
                warnings.append(f"   - {err}")
        else:
            # Success: report compliance
            total_criteria = len(data.get("y_star_criteria", []))
            print(f"[Y* Schema v2] {total_criteria}/{total_criteria} criteria valid")
    except Exception as e:
        warnings.append(f"⚠️ Y* schema v2 validation unavailable: {e}")

    if warnings:
        print("WARNINGS:")
        for w in warnings:
            print(f"  {w}")
        print()

    print("=" * 80)

if __name__ == "__main__":
    main()
