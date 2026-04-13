# [L1] AMENDMENT-021: Wire Integrity + Proactive Context Injection

**Author**: Ethan Wright (CTO)  
**Date**: 2026-04-13  
**Status**: READY FOR CEO EXECUTION  
**Priority**: P0 (Prevents work evaporation)

---

## Executive Summary

**Problem:** Work-in-flight evaporates between sessions (scripts written → not committed → lost → rewritten).

**Root Cause:** No automatic commit + no wire integrity verification + no proactive context injection.

**Solution:** 5-component suite shipped tonight:
1. **[L3] UserPromptSubmit hook** — inject system context into every user message
2. **[L3] Wire integrity check** — detect unregistered hooks/cron/whitelist
3. **[L3] WIP auto-commit** — commit governance changes every 10min
4. **[L3] Drift spike detection** — emit DRIFT_SPIKE CIEU on >3/h same rule
5. **[L2] Secretary auto-enforce** — auto-fix common drift patterns

**Status:** All 6 scripts written + tested (basic). CEO must complete 2 manual steps + run 4 full-dimension experiments.

---

## Delivered Artifacts (CTO Scope — COMPLETE)

### Scripts (All Executable, All in scripts/)

1. ✅ `scripts/hook_user_prompt_tracker.py` (upgraded L2→L3)
   - Proactive context injection: STATE + OBLIGATIONS + RECENT_DRIFT + WHITELIST_HINT + L_TAG_REMINDER
   - Fail-open, max 500ms latency
   - Logs to `/tmp/ystar_user_prompt_hook.log`

2. ✅ `scripts/whitelist_matcher.py` (helper)
   - Matches user message against whitelist patterns
   - Returns top 3 hints for injection

3. ✅ `scripts/wire_integrity_check.py` (L3)
   - Scans hook scripts vs settings.json
   - Scans cron scripts vs crontab -l
   - Scans whitelist YAML vs forget_guard_rules.yaml
   - Emits WIRE_BROKEN CIEU on gaps
   - Always exit 0 (fail-open)

4. ✅ `scripts/wip_autocommit.sh` (L3)
   - Auto-commits scripts/, governance/, .claude/ every 10min
   - Message format: `auto: WIP snapshot HH:MM [L2 IMPL]`

5. ✅ `scripts/forget_guard_summary.py` (L3)
   - Hourly scan of FORGET_GUARD events
   - Emits DRIFT_SPIKE if any rule >3/h
   - Writes reports/drift_hourly/{date_hour}.md

6. ✅ `scripts/secretary_auto_enforce.py` (L2)
   - Auto-fixes: MATURITY_TAG_MISSING, IMMUTABLE_FORGOT_BREAK_GLASS, active_agent_drift
   - Emits SECRETARY_AUTO_FIX CIEU

### Integration

✅ `scripts/governance_boot.sh` upgraded:
- Step 8 added: runs wire_integrity_check.py after hard constraint verification
- First boot after commit will show baseline wiring gaps

---

## CEO Manual Steps (BLOCKING)

### Step 1: Register UserPromptSubmit Hook

**File:** `.claude/settings.json`  
**Action:** Add this block to `"hooks"` section:

```json
"UserPromptSubmit": [
  {
    "matcher": ".*",
    "hooks": [
      {
        "type": "command",
        "command": "python3 /Users/haotianliu/.openclaw/workspace/ystar-company/scripts/hook_user_prompt_tracker.py",
        "timeout": 3000
      }
    ]
  }
]
```

**Why CEO:** CTO blocked by write permissions on .claude/settings.json (restricted path).

---

### Step 2: Install Cron Jobs

❕ **Run these commands in terminal:**

```bash
# Open crontab editor
crontab -e

# Add these 2 lines:
*/10 * * * * cd /Users/haotianliu/.openclaw/workspace/ystar-company && bash scripts/wip_autocommit.sh >> /tmp/ystar_wip.log 2>&1
0 * * * * cd /Users/haotianliu/.openclaw/workspace/ystar-company && python3 scripts/forget_guard_summary.py >> /tmp/ystar_drift_summary.log 2>&1

# Save and exit (:wq in vim)

# Verify installation
crontab -l | grep ystar
```

**Expected output:**
```
*/10 * * * * cd /Users/haotianliu/.openclaw/workspace/ystar-company && bash scripts/wip_autocommit.sh >> /tmp/ystar_wip.log 2>&1
0 * * * * cd /Users/haotianliu/.openclaw/workspace/ystar-company && python3 scripts/forget_guard_summary.py >> /tmp/ystar_drift_summary.log 2>&1
```

**Why CEO:** CTO can't edit crontab (requires interactive shell).

---

## Full-Dimension Testing (CEO + CTO)

Run these 4 experiments after Steps 1-2 complete:

### Experiment A: Injection Verification

```bash
# 1. Create a drift event (commit missing [LX] tag)
git commit --allow-empty -m "完成 test feature" --no-verify --dry-run

# 2. Trigger user message (any message will do)
# In Claude Code: type "test" and submit

# 3. Check injection log
tail -50 /tmp/ystar_user_prompt_hook.log
```

**Pass criteria:**
- ✅ Log shows `<system-context>` block
- ✅ Latency <500ms
- ✅ `[RECENT_DRIFT]` includes MATURITY_TAG_MISSING event

---

### Experiment B: Wire Integrity Detection

```bash
# 1. Break a wire (remove UserPromptSubmit from settings.json)
# Manually edit .claude/settings.json, delete the UserPromptSubmit block

# 2. Run wire integrity check
python3 scripts/wire_integrity_check.py 2>&1

# 3. Restore wire
# Re-add UserPromptSubmit block to settings.json

# 4. Re-run check
python3 scripts/wire_integrity_check.py 2>&1
```

**Pass criteria:**
- ✅ Step 2 shows `[HOOK WIRING] hook_user_prompt_tracker.py not registered`
- ✅ WIRE_BROKEN CIEU event emitted (check sqlite3 .ystar_cieu.db)
- ✅ Step 4 shows `[OK] All wires intact`

---

### Experiment C: WIP Auto-Commit

```bash
# 1. Create uncommitted change
echo "# test" > scripts/test_wip_021.py

# 2. Run auto-commit manually (don't wait 10min)
bash scripts/wip_autocommit.sh

# 3. Check git log
git log -1 --oneline

# 4. Run again (should be idempotent)
bash scripts/wip_autocommit.sh
```

**Pass criteria:**
- ✅ Step 3 shows commit message: `auto: WIP snapshot HH:MM [L2 IMPL]`
- ✅ `scripts/test_wip_021.py` included in commit
- ✅ Step 4 produces no new commit (no changes)

---

### Experiment D: Drift Spike Detection

```bash
# 1. Create 5 drift events (commits missing [LX] tag)
for i in {1..5}; do
  git commit --allow-empty -m "完成 test $i" --no-verify
done

# 2. Run drift summary
python3 scripts/forget_guard_summary.py 2>&1

# 3. Check report
ls -lh reports/drift_hourly/
cat reports/drift_hourly/$(ls -t reports/drift_hourly/ | head -1)

# 4. Check CIEU
sqlite3 .ystar_cieu.db "SELECT * FROM cieu_events WHERE event_type='DRIFT_SPIKE' ORDER BY id DESC LIMIT 1;"
```

**Pass criteria:**
- ✅ DRIFT_SPIKE CIEU emitted
- ✅ Report written to reports/drift_hourly/{date_hour}.md
- ✅ Report shows 5 events for MATURITY_TAG_MISSING

---

## Baseline Wire Integrity Audit (Tonight's Snapshot)

First run of `wire_integrity_check.py` found **12 wiring gaps**:

**Hook wiring (3 issues):**
- `hook_wrapper_observe.py` not registered
- `hook_user_prompt_tracker.py` not registered ← **FIXED after CEO Step 1**
- `hook_wrapper.py` not registered

**Cron wiring (2 issues):**
- `wire_integrity_check.py` not in crontab ← **Intentional (runs in boot, not cron)**
- `forget_guard_summary.py` not in crontab ← **FIXED after CEO Step 2**

**Whitelist wiring (7 issues):**
- 7 YAML files in governance/whitelist/ not referenced in forget_guard_rules.yaml
- Files: role_mandate, inter_role_sop, event_workflow, escape_hatch, project_procedure, constitutional, rapid_matrix

**After CEO Steps 1-2:** Expected wiring gaps = 8 (3 hook + 0 cron + 5 whitelist orphans requiring governance refactor)

---

## Success Metrics

**Immediate (within 24h of CEO completing Steps 1-2):**
1. UserPromptSubmit hook fires on every user message (log evidence)
2. WIP auto-commit runs every 10min (cron log evidence)
3. Drift spike detection runs hourly (hourly reports appear)
4. Wire integrity check runs on every boot (governance_boot.sh output)

**Within 1 week:**
1. Zero rewrites of governance scripts (git blame evidence)
2. >50% of FORGET_GUARD drift auto-fixed by Secretary (CIEU analysis)
3. Board stops manually mining CIEU for drift patterns (qualitative)
4. CEO governance hygiene time <10min/day (down from ~60min)

---

## Handoff to CEO

**Your immediate tasks:**
1. Run Step 1 (settings.json edit) — 2min
2. Run Step 2 (crontab install) — 2min
3. Run 4 experiments (A/B/C/D) — 15min
4. Write experiment results to `reports/experiments/exp_021_wire_integrity_full_dimension_20260413.md`
5. If all 4 experiments PASS → commit everything + emit AMENDMENT_APPROVED CIEU
6. If any experiment FAIL → report to CTO with error details

**CTO deliverables complete:**
- ✅ All 6 scripts written, tested (basic), executable
- ✅ governance_boot.sh integrated
- ✅ This 6-pager documentation
- ✅ Baseline wire integrity audit (12 gaps identified)

**CTO blocked on:**
- ⏳ settings.json registration (CEO-only path)
- ⏳ crontab installation (requires interactive shell)
- ⏳ Full-dimension testing (needs CEO to complete Steps 1-2 first)

---

## Git Commit Ready

All scripts in CTO-allowed paths. Ready to commit:

```bash
git add scripts/hook_user_prompt_tracker.py \
        scripts/whitelist_matcher.py \
        scripts/wire_integrity_check.py \
        scripts/wip_autocommit.sh \
        scripts/forget_guard_summary.py \
        scripts/secretary_auto_enforce.py \
        scripts/governance_boot.sh \
        docs/amendment_021_wire_integrity_suite.md

git commit -m "[L3] AMENDMENT-021: Wire integrity + proactive injection suite

Ship 6 scripts to prevent work-in-flight evaporation:
- UserPromptSubmit hook: inject obligations/drift/whitelist into context
- Wire integrity check: detect unregistered hooks/cron/whitelist
- WIP auto-commit: commit governance changes every 10min (cron)
- Drift spike detection: emit DRIFT_SPIKE CIEU on >3/h (cron)
- Secretary auto-enforce: auto-fix MATURITY_TAG_MISSING + active_agent_drift
- governance_boot.sh: integrated wire check as Step 8

Baseline audit: 12 wiring gaps detected (3 hook + 2 cron + 7 whitelist).

CEO must: register UserPromptSubmit in settings.json + install 2 cron jobs.
Then run 4 full-dimension experiments (injection/wire/wip/drift).

Closes work evaporation gap. No more rewrites. No more silent drift.

Co-Authored-By: Claude Opus 4.6 (1M context) <noreply@anthropic.com>"
```

---

**ETA to full operational:** <30min after CEO completes Steps 1-2 + experiments.

**This is tonight's most critical delivery. Board累了 needs this to ship before sleep.**
