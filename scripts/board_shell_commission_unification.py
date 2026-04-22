#!/usr/bin/env python3.11
"""Board-shell Commission Unification — one-shot surgery.

Board 2026-04-22 directive: merge two forget_guard YAMLs, wire commission真连线,
remove time-concept pollution in favor of sequence-driven semantics.

Run from Board's external shell (bypasses CEO boundary + sub-agent watchdog):

    python3.11 /Users/haotianliu/.openclaw/workspace/ystar-company/scripts/board_shell_commission_unification.py

Exits 0 on PASS, 1 on FAIL. Idempotent — safe to re-run.

Steps:
  A. Patch Y-star-gov forget_guard.py _load_rules to parse BOTH schemas
     (v0.42 "name" + 1.1 "id") and load BOTH yaml files (Y-star-gov internal
     + ystar-company governance/).
  B. Verify engine loads total rules ≥ 50 (35 + 32 minus dedup).
  C. Reframe pending obligations from time-driven to sequence-framed notes;
     due_at stays as safety-net (30d) not driver per Board 无硬时间编排.
  D. Live-fire: check_forget_violation on CEO→engineer dispatch, expect deny.
"""
from __future__ import annotations

import re
import sqlite3
import subprocess
import sys
import time
from pathlib import Path

WORKSPACE = Path("/Users/haotianliu/.openclaw/workspace")
YGOV_ENGINE = WORKSPACE / "Y-star-gov/ystar/governance/forget_guard.py"
COMPANY_YAML = WORKSPACE / "ystar-company/governance/forget_guard_rules.yaml"
OMISSION_DB = WORKSPACE / "ystar-company/.ystar_cieu_omission.db"

NEW_LOAD_RULES_BODY = '''    def _load_rules(self):
        """Load rules from YAML file(s). Supports BOTH schema v0.42 (name/pattern/mode)
        and schema 1.1 (id/trigger/conditions/action/recipe). Merges Y-star-gov
        internal YAML + ystar-company governance YAML (Board 2026-04-22 unification)."""
        yaml_paths = [self.rules_path]
        secondary = Path("/Users/haotianliu/.openclaw/workspace/ystar-company/governance/forget_guard_rules.yaml")
        if secondary.exists() and secondary not in yaml_paths:
            yaml_paths.append(secondary)

        all_rule_data = []
        for yp in yaml_paths:
            if not yp.exists():
                continue
            try:
                with open(yp) as f:
                    data = yaml.safe_load(f) or {}
                all_rule_data.extend(data.get("rules", []))
            except Exception:
                continue

        seen_names = set()
        for rule_data in all_rule_data:
            if "name" in rule_data and "pattern" in rule_data:
                nm = rule_data["name"]
                if nm in seen_names:
                    continue
                seen_names.add(nm)
                self.rules.append(ForgetGuardRule(
                    name=nm,
                    pattern=rule_data["pattern"],
                    mode=rule_data.get("mode", "warn"),
                    message=rule_data["message"],
                    rationale=rule_data.get("rationale", ""),
                    dry_run_until=rule_data.get("dry_run_until"),
                    created_at=rule_data.get("created_at", ""),
                ))
            elif "id" in rule_data:
                nm = rule_data["id"]
                if nm in seen_names:
                    continue
                seen_names.add(nm)
                trigger = rule_data.get("trigger", {}) or {}
                conds = trigger.get("conditions", []) if isinstance(trigger, dict) else []
                keywords = []
                for c in conds:
                    if isinstance(c, dict):
                        kws = c.get("keywords", [])
                        if isinstance(kws, list):
                            keywords.extend(str(k) for k in kws)
                pattern = "|".join(keywords) if keywords else ""
                recipe = rule_data.get("recipe", "")
                if isinstance(recipe, str):
                    recipe = recipe[:500]
                self.rules.append(ForgetGuardRule(
                    name=nm,
                    pattern=pattern,
                    mode=rule_data.get("action", "warn"),
                    message=recipe if recipe else rule_data.get("description", ""),
                    rationale=rule_data.get("description", ""),
                    dry_run_until=None,
                    created_at=rule_data.get("last_reviewed", ""),
                ))
'''


def step_a_patch_engine():
    if not YGOV_ENGINE.exists():
        return False, f"engine file not found: {YGOV_ENGINE}"
    text = YGOV_ENGINE.read_text()
    # Idempotent detection: any existing dual-schema patch marker is acceptable
    already_patched = (
        "Board 2026-04-22 unification" in text
        or "Supports two schemas" in text
        or "secondary company-side" in text.lower()
        or ("schema 1.1" in text and "id" in text and "trigger" in text)
    )
    if already_patched:
        return True, "already patched (Ryan Step-2 or prior run — idempotent skip)"
    pat = re.compile(r'    def _load_rules\(self\):.*?(?=\n    def |\n\nclass |\Z)', re.DOTALL)
    m = pat.search(text)
    if not m:
        return False, "could not locate _load_rules method"
    YGOV_ENGINE.write_text(text[:m.start()] + NEW_LOAD_RULES_BODY + text[m.end():])
    return True, f"patched {YGOV_ENGINE.name}"


def step_b_verify_count():
    r = subprocess.run(
        ["python3.11", "-c",
         "import sys; sys.path.insert(0,'/Users/haotianliu/.openclaw/workspace/Y-star-gov');"
         "from ystar.governance.forget_guard import ForgetGuard; g = ForgetGuard();"
         "print('TOTAL=' + str(len(g.rules)))"],
        capture_output=True, text=True, timeout=10,
    )
    if r.returncode != 0:
        return False, f"import failed: {r.stderr[:250]}"
    m = re.search(r'TOTAL=(\d+)', r.stdout)
    if not m:
        return False, f"no count: {r.stdout[:200]}"
    n = int(m.group(1))
    return (n >= 50), f"total_rules={n} (need ≥50)"


def step_c_reframe_obligations():
    if not OMISSION_DB.exists():
        return True, "no omission db, skipping"
    now = time.time()
    SAFETY = 30 * 86400
    conn = sqlite3.connect(str(OMISSION_DB), timeout=5)
    updated = 0
    for rid, trig, fulfill in [
        ("COMMISSION-UNIFY-STEP-1", "FORGET_GUARD_LIVE_FIRE_VERIFIED", "FORGET_GUARD_WIRE_LIVE"),
        ("COMMISSION-UNIFY-STEP-2", "FORGET_GUARD_WIRE_LIVE", "UNIFIED_ENGINE_LIVE"),
        ("COMMISSION-UNIFY-STEP-3", "UNIFIED_ENGINE_LIVE", "BOUNDARY_ENFORCER_MIGRATED"),
    ]:
        res = conn.execute(
            "UPDATE obligations SET notes = ?, due_at = ? "
            "WHERE notes LIKE ? AND status = 'pending'",
            (f"[sequence-driven] Trigger: {trig}; Fulfill: {fulfill}; "
             f"Safety 30d not driver per Board 2026-04-22 无硬时间",
             now + SAFETY, f"%{rid}%")
        )
        updated += res.rowcount
    conn.commit()
    conn.close()
    return True, f"reframed {updated} obligations"


def step_d_live_fire():
    r = subprocess.run(
        ["python3.11", "-c",
         "import sys; sys.path.insert(0,'/Users/haotianliu/.openclaw/workspace/Y-star-gov');"
         "from ystar.governance.forget_guard import check_forget_violation;"
         "v = check_forget_violation({'agent_id':'ceo','action_type':'task_assignment',"
         "'action_payload':'Agent tool_name=Ryan-Platform do code','target_agent':'eng-kernel'});"
         "print('V=' + ('yes' if v else 'no'));"
         "print('R=' + (v.get('rule_name','') if v else ''))"],
        capture_output=True, text=True, timeout=10,
    )
    if r.returncode != 0:
        return False, f"run fail: {r.stderr[:250]}"
    fired = "V=yes" in r.stdout
    rule = re.search(r'R=(\S+)', r.stdout)
    return fired, f"fired={fired} rule={rule.group(1) if rule else 'n/a'}"


def main() -> int:
    print("=== Board-shell Commission Unification ===")
    steps = [
        ("A. patch engine dual-schema + dual-yaml", step_a_patch_engine),
        ("B. verify total rules >= 50", step_b_verify_count),
        ("C. reframe obligations sequence-driven", step_c_reframe_obligations),
        ("D. live-fire CEO->engineer deny", step_d_live_fire),
    ]
    all_ok = True
    for label, fn in steps:
        try:
            ok, msg = fn()
        except Exception as e:
            ok, msg = False, f"exc: {type(e).__name__}: {e}"
        mark = "PASS" if ok else "FAIL"
        print(f"  [{mark}] {label} — {msg}")
        if not ok:
            all_ok = False
    print("=== OVERALL: " + ("PASS" if all_ok else "FAIL") + " ===")
    return 0 if all_ok else 1


if __name__ == "__main__":
    sys.exit(main())
