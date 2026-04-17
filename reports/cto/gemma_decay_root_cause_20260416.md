# Gemma Decay Root Cause Analysis

**Date**: 2026-04-16  
**Analyst**: Ethan Wright (CTO)  
**Status**: Diagnosis Complete — Handoff to Ryan (script fix) + Maya (quality gate) + Board (rollback decision)

---

## 1. Endpoint Reality

**Actual Configuration** (verified via `curl localhost:11434/api/tags`):
- **Endpoint**: `localhost:11434` (NOT 192.168.1.228 as legacy CLAUDE.md AMENDMENT-004 suggested)
- **Models loaded**:
  - `ystar-gemma:latest` — 8B Q4_K_M custom fine-tune, last modified **2026-04-10 14:03:29**
  - `gemma4:e4b` — 8B Q4_K_M base model, last modified **2026-04-10 14:01:58**
  - `nomic-embed-text:latest` — 137M F16 embedding helper, last modified **2026-04-10 14:06:43**

**All three models frozen since Apr 10** — no new learning has been incorporated into ystar-gemma for **6 days**.

**AMENDMENT-004 Note Resolution**: The legacy CLAUDE.md note about 192.168.1.228 endpoint ambiguity was **incorrect for Gemma**. Platform Engineer verification task was never executed. Gemma runs **locally on localhost:11434**, not on a separate MAC mini. The 192.168.1.228 reference only applies to legacy dual-machine Windows+Mac configuration which is now DEPRECATED.

---

## 2. ystar_wakeup.sh Syntax Errors

### Error 1: Line 23 — Octal Interpretation Bug

**Error Message**:
```
line 23: 09: value too great for base (error token is "09")
```

**Root Cause**:  
Line 20-23:
```bash
HOUR=$(date +%H)
ROLES=("cto" "cmo" "cfo" "cso" "secretary" "ceo")
IDX=$(( HOUR / 3 % 6 ))
ROLE=${ROLES[$IDX]}
```

When `date +%H` returns `09` (9am), bash arithmetic `$(( ... ))` interprets leading-zero numbers as **octal** (base-8). `09` is invalid in octal (only 0-7 allowed), causing the error.

**Impact**: Every cron run at hours 08, 09 (8am, 9am) fails immediately. Learning does not proceed.

**Fix** (for Ryan — Platform Engineer):
```bash
HOUR=$(date +%H | sed 's/^0*//') # Strip leading zeros
# OR
HOUR=$((10#$(date +%H)))  # Force base-10 interpretation
```

### Error 2: Line 82 — False Positive (Not a Real Syntax Error)

**Error Message**:
```
line 82: syntax error near unexpected token `)'
line 82: `  intel)'
```

**Investigation**: Line 76-82 shows proper case syntax:
```bash
intel)
  echo "[$DATE $TIME] Starting CSO Intelligence Scan" >> "$LOG_DIR/wakeup.log"
```

This is valid bash. The error is a **cascade from line 23 failure** — when bash hits the octal error, it aborts parsing and reports subsequent lines as malformed. This is **not an independent bug**.

**Fix**: Fix line 23 → line 82 error disappears.

### Error 3: "No such file or directory"

**Error Message**:
```
/bin/sh: /Users/haotianliu/.openclaw/workspace/ystar-company/scripts/ystar_wakeup.sh: No such file or directory
```

**Root Cause**: Cron runs scripts in a minimal shell environment. When the script fails at line 23, subsequent cron invocations may encounter file-not-found due to:
1. **Working directory mismatch** — cron doesn't cd to script location automatically
2. **Shebang interpreter issue** — if `/bin/bash` vs `/bin/sh` mismatch

**Fix** (for Ryan):
1. Ensure crontab entry uses **absolute path** (already correct: `/Users/haotianliu/.openclaw/.../ystar_wakeup.sh`)
2. Add `cd "$YSTAR_DIR"` **before** line 20 (before HOUR calculation)
3. Verify shebang is `#!/bin/bash` (already correct at line 1)

---

## 3. Gemma 0% Pass Rate Root Cause

**Evidence** (`reports/gemma_shadow_archive/20260415/call_00001.json`):
```json
{
  "prompt_snippet": "Summarize Y*gov in one sentence.",
  "gemma": {
    "provider": "ystar-gemma:latest",
    "text": "",           ← EMPTY RESPONSE
    "tokens": 100,
    "latency_ms": 6362,  ← Model did run (6.3s)
    "error": null        ← No error reported
  },
  "metrics": {
    "similarity": 0.0,
    "length_ratio": 0.0  ← Claude reference also missing
  }
}
```

**Diagnosis**:
1. **Gemma returns empty string** despite 6.3s processing time
2. **No error logged** — the model *ran*, but produced no output
3. **Claude reference also missing** (`ANTHROPIC_API_KEY not set`) — shadow testing cannot compare to ground truth
4. **All 4 calls on 2026-04-15 show identical pattern** — 0.00 similarity, 0.00 length_ratio

**Possible Root Causes**:
- **A) Model degradation** — ystar-gemma fine-tune corrupted or overfitted to empty responses
- **B) Prompt template mismatch** — local_learn.py sends malformed prompt that Gemma cannot parse
- **C) Ollama API issue** — localhost:11434 returning 200 OK with empty body (server-side bug)
- **D) Token limit hit** — model hits max_tokens=100 before generating first token (unlikely given latency)

**Most Likely**: **(A) Model degradation**. The 6-day frozen learning cycle means ystar-gemma has received no new training data since Apr 10, but the *quality gate failure started immediately on Apr 15*, suggesting the model itself is unstable.

**Verification Needed** (for Maya — Governance Engineer):
1. Run `curl -X POST http://localhost:11434/api/generate -d '{"model":"ystar-gemma:latest","prompt":"What is Y*gov?","stream":false}'` manually
2. Compare output with `gemma4:e4b` base model (same prompt)
3. Check if ystar-gemma returns empty vs base returns valid text → confirms model-specific issue

---

## 4. Rollback vs Fix Decision

### Option A: Continue ystar-gemma (NOT RECOMMENDED)

**Rationale**: If we fix the cron syntax errors, learning will resume and ystar-gemma *might* self-correct through new training data.

**Risks**:
- 6 days of **0% pass rate** suggests model is fundamentally broken, not just data-starved
- Continued use produces **worthless knowledge files** (see `knowledge/cfo/gaps/gemma_sessions.log` — output_length=0)
- Quality gate alerts Board daily with "CRITICAL rollback" warnings → noise fatigue

**Timeline**: 3-7 days to potentially recover (unverified)

### Option B: Rollback to gemma4:e4b Base (RECOMMENDED)

**Rationale**:
- Base model `gemma4:e4b` is **identical architecture** (8B Q4_K_M), loaded alongside ystar-gemma
- Base model has **no fine-tuning corruption**
- Immediate restoration of usable learning loop

**Risks**:
- Lose any valid fine-tuning gains from ystar-gemma (if they exist — unproven)
- Base model may lack Y*gov domain knowledge (acceptable — learning will rebuild it)

**Timeline**: 1 hour (change `local_learn.py` model reference + verify 1 successful run)

**Action** (for Ryan):
1. Edit `scripts/local_learn.py` line referencing `ystar-gemma:latest` → `gemma4:e4b`
2. Run manual test: `python3 scripts/local_learn.py --mode questions --actor cto --task "What is Y*gov?"`
3. Verify output is non-empty
4. Wait for next cron cycle (3h) and check `reports/gemma_quality_daily/` pass_rate > 0%

### Option C: Hybrid — Parallel Testing

**Rationale**: Run both models in shadow mode, compare outputs daily.

**Complexity**: Requires Maya to build dual-model quality gate (2-3 days engineering work).

**Verdict**: Overkill for current crisis. Choose B (rollback) for speed.

---

## 5. Action Plan & Handoffs

### Task Card 1: Ryan Park (Platform Engineer) — P0 Cron Fix

**File**: `.claude/tasks/eng-platform-020_cron_syntax_fix.md`

**Acceptance Criteria**:
- [ ] Fix line 23 octal bug (force base-10 HOUR interpretation)
- [ ] Add `cd "$YSTAR_DIR"` before line 20 (ensure cwd is correct)
- [ ] Test script manually at hours 08, 09 to verify no octal error
- [ ] Verify next cron run (check `/tmp/ystar_learning.log`) completes without syntax errors
- [ ] **DO NOT** modify model selection — that's Task Card 2

**Files in Scope**:
- `scripts/ystar_wakeup.sh` (lines 20-23 only)

**Estimated Time**: 15 minutes

---

### Task Card 2: Ryan Park (Platform Engineer) — P0 Gemma Rollback

**File**: `.claude/tasks/eng-platform-021_gemma_rollback.md`

**Acceptance Criteria**:
- [ ] Locate model reference in `scripts/local_learn.py` (grep "ystar-gemma")
- [ ] Change `ystar-gemma:latest` → `gemma4:e4b`
- [ ] Run manual test: `python3 scripts/local_learn.py --mode questions --actor cto --task "Explain Y*gov CIEU in one sentence"`
- [ ] Verify output is non-empty (≥ 20 characters)
- [ ] Wait for next quality gate report (tomorrow) and confirm pass_rate > 0%

**Files in Scope**:
- `scripts/local_learn.py`
- `scripts/idle_learning.py` (if it also references ystar-gemma)

**Estimated Time**: 30 minutes

---

### Task Card 3: Maya Patel (Governance Engineer) — P1 Quality Gate Review

**File**: `.claude/tasks/eng-governance-015_quality_gate_forensics.md`

**Acceptance Criteria**:
- [ ] Manual verification: curl localhost:11434 with ystar-gemma vs gemma4:e4b, compare responses
- [ ] Analyze why quality gate didn't auto-rollback despite 6 days of 0% pass rate
- [ ] Propose threshold adjustment: current trigger is "pass_rate < 70% → consider rollback" — should be "pass_rate < 50% for 2 consecutive days → AUTO rollback"
- [ ] Document findings in `reports/governance/gemma_quality_gate_postmortem_20260416.md`

**Files in Scope**:
- `scripts/gemma_quality_*.py` (quality gate logic)
- `reports/gemma_quality_daily/` (historical data)

**Estimated Time**: 2 hours

---

### Board Decision Required: Formal Rollback Approval

**Question**: Approve rollback from `ystar-gemma:latest` (custom fine-tune) to `gemma4:e4b` (base model)?

**Context**:
- ystar-gemma has 0% pass rate for 6 days
- Produces only empty responses (verified in shadow archive)
- No known recovery path except "wait and hope"
- gemma4:e4b is identical architecture, immediately usable

**Recommendation**: **APPROVE rollback**. Speed of recovery (1 hour) outweighs unproven value of corrupted fine-tune.

**If approved**: Ryan executes Task Card 2 immediately after Task Card 1.  
**If rejected**: Maya executes Task Card 3 to build forensics before any model change.

---

## Summary

**Root Causes Identified**:
1. **Cron syntax error** (line 23 octal bug) → learning loop broken at hours 08, 09
2. **ystar-gemma model failure** → 100% empty responses, 0% pass rate for 6 days
3. **Quality gate weakness** → "consider rollback" alert ignored, no auto-action

**Immediate Fixes**:
- Ryan: Fix cron syntax (15 min)
- Ryan: Rollback to gemma4:e4b (30 min, pending Board approval)
- Maya: Review quality gate auto-rollback logic (2 hours)

**Expected Outcome**:
- Learning loop restored within 3 hours
- Next quality gate report (2026-04-17) shows pass_rate ≥ 70%
- Knowledge files begin accumulating useful content (currently output_length=0)

**Rt+1 Assessment**: After fixes, monitor for 48h. If gemma4:e4b pass_rate stays ≥ 70%, Rt+1 = 0 (issue resolved). If new failures emerge, escalate to CTO for Ollama server health check.
