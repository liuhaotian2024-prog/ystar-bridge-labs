---
title: "V3 Ryan: 6h Regression Cron + YAML Mutation Testing Harness"
engineer: eng-platform (Ryan Park)
priority: P0
atomic_id: CZL-CEO-RULES-REGISTRY-V3-RYAN
parent: CZL-CEO-RULES-REGISTRY-V3-EXISTING-ASSETS-FIRST
date: 2026-04-22
estimated_tu: 30
m_triangle: M-2a+M-2b (continuous regression prevents drift — both commission and omission)
---

## BOOT 4-step (MANDATORY — run before any business tool)

```bash
cat /Users/haotianliu/.openclaw/workspace/ystar-company/.czl_subgoals.json
cd /Users/haotianliu/.openclaw/workspace/ystar-company && git log -10 --oneline
python3 scripts/precheck_existing.py "CZL-CEO-RULES-REGISTRY-V3-RYAN" 2>&1 | tail -10
sqlite3 .ystar_cieu.db "SELECT count(*) FROM cieu_events WHERE created_at >= strftime('%s','now','-1 hour')"
```

## Context (self-contained — no session history required)

CEO spec: `reports/ceo/governance/CEO_RULES_REGISTRY_AUDIT.md` Section 10.2 (G2 long-term drift prevention).

Board 2026-04-22 directive: close 4 governance gaps. This card covers G2: (1) a 6h launchd cron job that auto-runs commission+omission unification livefire, and (2) a YAML mutation testing harness that deliberately corrupts governance YAML to verify detection.

### Existing Assets (DO NOT rebuild)

1. **`scripts/board_shell_commission_unification.py`** (8.5KB): Commission livefire — your cron will call this.
2. **`scripts/board_shell_omission_unification.py`**: Leo is building in parallel (his V3 task). Your cron calls it IF it exists, skips gracefully if not yet available.
3. **`scripts/k9_silent_fire_audit.py`**: Silent-fire detection, already LIVE. Optional include in your cron.
4. **`scripts/unified_compliance_audit.py`**: Graded 5-tuple compliance. Optional include.
5. **`governance/forget_guard_rules.yaml`**: Target for mutation testing.
6. **`scripts/behavior_gov_rules.yaml`**: Secondary target for mutation testing.
7. **Existing launchd plist reference**: `~/Library/LaunchAgents/com.ystar.bridge.cieu_brain_daemon.plist` — use as format template.

## Task 1: 6h Launchd Regression Job (G2, ~15 tu)

### Goal
Automated 6-hour regression that runs all governance livefire tests and emits P0 alarm on failure.

### Deliverable 1A: `scripts/governance_regression_runner.py`

A unified runner script that:

1. Imports and runs `board_shell_commission_unification.py` main function, captures PASS/FAIL
2. Checks if `board_shell_omission_unification.py` exists; if yes runs it, if no prints `[SKIP] omission_unification not yet available` and continues
3. Aggregates: any FAIL → exit code 1 + emit CIEU `GOVERNANCE_REGRESSION_FAILURE` with severity P0
4. All PASS → exit code 0 + emit CIEU `GOVERNANCE_REGRESSION_PASS` with severity info
5. Writes timestamped summary to `reports/governance/regression_{timestamp}.json`:
   ```json
   {
     "timestamp": "2026-04-22T15:00:00Z",
     "commission_result": {"total": 22, "pass": 22, "fail": 0},
     "omission_result": {"total": 8, "pass": 8, "fail": 0, "skipped": false},
     "overall": "PASS",
     "cieu_event_id": "..."
   }
   ```
6. Runnable standalone: `python3 scripts/governance_regression_runner.py`

### Implementation Guidance

- Check how `board_shell_commission_unification.py` handles imports (sys.path, Y-star-gov path)
- CIEU emit: use `sqlite3` subprocess call or import from existing CIEU helpers
- Handle subprocess errors gracefully (if commission script crashes, catch and report as FAIL, don't crash the runner)
- Python path: run `which python3` in your boot step, use that path in the plist

### Deliverable 1B: `scripts/com.ystar.bridge.governance_regression.plist`

A macOS launchd plist with:

```xml
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
    <key>Label</key>
    <string>com.ystar.bridge.governance_regression</string>
    <key>ProgramArguments</key>
    <array>
        <string>/path/to/python3</string>
        <string>/Users/haotianliu/.openclaw/workspace/ystar-company/scripts/governance_regression_runner.py</string>
    </array>
    <key>StartInterval</key>
    <integer>21600</integer>
    <key>WorkingDirectory</key>
    <string>/Users/haotianliu/.openclaw/workspace/ystar-company</string>
    <key>StandardOutPath</key>
    <string>/Users/haotianliu/.openclaw/workspace/ystar-company/scripts/.logs/governance_regression.log</string>
    <key>StandardErrorPath</key>
    <string>/Users/haotianliu/.openclaw/workspace/ystar-company/scripts/.logs/governance_regression.err.log</string>
    <key>EnvironmentVariables</key>
    <dict>
        <key>PYTHONPATH</key>
        <string>/Users/haotianliu/.openclaw/workspace/Y-star-gov</string>
    </dict>
</dict>
</plist>
```

Replace `/path/to/python3` with actual `which python3` output.

Write plist to `scripts/` directory — NOT to `~/Library/LaunchAgents/` (Board installs manually).

### Acceptance Criteria
- [ ] `scripts/governance_regression_runner.py` exists, runs standalone without crash
- [ ] Calls commission_unification and captures result
- [ ] Gracefully skips omission_unification if not yet available
- [ ] Emits CIEU GOVERNANCE_REGRESSION_PASS or GOVERNANCE_REGRESSION_FAILURE
- [ ] Writes result JSON to `reports/governance/`
- [ ] `scripts/com.ystar.bridge.governance_regression.plist` exists with valid XML
- [ ] Plist has StartInterval=21600, correct paths, PYTHONPATH set

## Task 2: YAML Mutation Testing Harness (G2, ~15 tu)

### Goal
Deliberately corrupt governance YAML files and verify the governance layer catches each corruption. Mutations that survive undetected = governance gaps.

### Deliverable: `scripts/yaml_mutation_harness.py`

**SAFETY FIRST**: This script temporarily mutates real governance files. CRITICAL safety requirements:
- ALWAYS `shutil.copy2()` backup before ANY mutation
- ALWAYS restore in `try/finally` block
- If restore fails, print `CRITICAL: RESTORE FAILED` and `sys.exit(2)`
- NEVER leave `governance/forget_guard_rules.yaml` in a corrupted state

**Mutation Bank** (minimum 5 mutations):

| ID | Mutation | What It Tests |
|---|---|---|
| M1 | Delete first `trigger_patterns` entry from `choice_question_to_board` rule | Pattern matching completeness |
| M2 | Change `action: deny` to `action: allow` on `choice_question_to_board` | Action enforcement |
| M3 | Empty the `scope` field of a rule | Scope matching |
| M4 | Rename a rule from `choice_question_to_board` to `choice_question_to_board_TYPO` | Rule name lookup |
| M5 | Remove entire `coordinator_reply_missing_5tuple` rule entry | Rule count integrity |

**Logic**:

```python
for mutation in MUTATION_BANK:
    backup_yaml()
    try:
        apply_mutation(mutation)
        result = run_governance_check()  # load ForgetGuard with mutated yaml
        if result.detects_problem:
            mutation.status = "CAUGHT"
        else:
            mutation.status = "SURVIVED"  # gap!
    finally:
        restore_yaml()
        verify_restore()  # diff backup vs current, must be identical
```

**Output**: Print summary table + write `reports/governance/mutation_test_results.json`:
```json
{
  "timestamp": "2026-04-22T15:00:00Z",
  "mutations": [
    {"id": "M1", "description": "...", "status": "CAUGHT"},
    {"id": "M2", "description": "...", "status": "SURVIVED"}
  ],
  "caught": 4,
  "survived": 1,
  "survival_rate": 0.2
}
```

**CIEU emit**: `YAML_MUTATION_TEST` event with `survived_count` in payload.

### Acceptance Criteria
- [ ] `scripts/yaml_mutation_harness.py` exists and runs
- [ ] At least 5 mutations in the bank
- [ ] `governance/forget_guard_rules.yaml` is IDENTICAL before and after run (verify with file hash)
- [ ] Summary shows caught vs survived counts
- [ ] CIEU event emitted
- [ ] `reports/governance/mutation_test_results.json` written
- [ ] Script exits with code 2 if restore fails (safety valve)

## Livefire Verification (MANDATORY)

### Livefire 1 — Regression Runner
```bash
python3 scripts/governance_regression_runner.py
# Expect: commission results printed, CIEU event emitted
sqlite3 .ystar_cieu.db "SELECT count(*) FROM cieu_events WHERE event_type LIKE 'GOVERNANCE_REGRESSION%' AND created_at >= strftime('%s','now','-300')"
# Expect: >= 1
```

### Livefire 2 — Mutation Harness
```bash
# Take hash before
md5 governance/forget_guard_rules.yaml > /tmp/yaml_pre.md5
python3 scripts/yaml_mutation_harness.py
# Take hash after
md5 governance/forget_guard_rules.yaml > /tmp/yaml_post.md5
diff /tmp/yaml_pre.md5 /tmp/yaml_post.md5
# Expect: identical (no permanent mutation)
cat reports/governance/mutation_test_results.json
# Expect: valid JSON with caught/survived counts
```

## 5-Tuple Receipt Template

```
- Y*: 6h regression cron ready + yaml mutation harness LIVE
- Xt: [starting state]
- U: [actions with honest tool_uses count]
- Yt+1: [end state + file paths]
- Rt+1: [honest gap or 0]
```

## Hard Constraints

- **NO git commit / push / add / reset** — only Write/Edit, CEO handles git
- **NO choice questions** — decide and execute
- **NO defer language** — no "later/next/will do"
- **NO self-claims without tool evidence**
- **CRITICAL**: NEVER leave `governance/forget_guard_rules.yaml` corrupted. Backup+restore is non-negotiable. Violation = task rejected immediately.
- **Files in scope**: `scripts/governance_regression_runner.py` (new), `scripts/com.ystar.bridge.governance_regression.plist` (new), `scripts/yaml_mutation_harness.py` (new), `reports/governance/regression_*.json` (output), `reports/governance/mutation_test_results.json` (output)
- **Files NOT in scope**: anything else
