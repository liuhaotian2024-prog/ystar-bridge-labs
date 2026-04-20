Audience: Maya-Governance — engineer task card for CZL-BRAIN-3LOOP-LIVE L3-Phase-1 (manual CLI + dry-run + diff audit gate)
Research basis: CEO 2026-04-19 correction withdrawing L3 auto scheduling; Board L3 risk diagnosis (echo chamber + bias amplification + CZL-ESCAPE-SEMANTIC-REVERSAL proving CEO spec symbol error); Maya prior round delivered 4 consolidation patterns (A-D) + 8 CIEU event types code-complete in aiden_dream.py
Synthesis: L3 dream consolidation must NOT auto-run. Phase 1 adds dry-run mode that computes weight deltas + writes diff report without touching aiden_brain.db. Real commits require explicit --commit flag gated on BRAIN_DREAM_DIFF_REVIEWED CIEU event + Board approval flag. This prevents bias fixation while allowing controlled learning.
Purpose: Enable Maya to add dry-run/commit CLI modes to aiden_dream.py in <=5 tool_uses, delivering the CEO-mandated audit gate before any L3 auto scheduling can be considered

## Task: CZL-BRAIN-3LOOP-LIVE L3-Phase-1 — Manual CLI + Dry-Run + Diff Audit Gate

**Tier**: 1 (immediate)
**Engineer**: Maya-Governance
**Priority**: P0
**Dispatch ID**: CZL-BRAIN-3LOOP-LIVE (L3 subset)
**Depends on**: CZL-BRAIN-L2-WRITEBACK-IMPL (Ryan+Leo, in flight) — L3 needs L2 activation_log data to consolidate
**Budget**: <=5 tool_uses

---

### CEO Correction Context (MUST READ — shapes entire implementation)

CEO withdrew L3 auto scheduling. Board identified 3 risks:
1. Hebbian consolidation structurally biased toward echo chamber
2. CEO in decision loop without external anchor amplifies bias
3. CZL-ESCAPE-SEMANTIC-REVERSAL proved CEO spec had inverted polarity on escape samples (negative pull where positive learning signal was correct)

Result: L3 splits into Phase-1 (this task) and Phase-2 (future, requires >=5 manual dry-runs reviewed + Board charter amendment).

### Scope

**Maya delivers**: Modified `scripts/aiden_dream.py` with two new CLI modes + diff writer

### Files in scope (HARD BOUNDARY)

- `scripts/aiden_dream.py` (MODIFY — add --dry-run and --commit modes)
- `reports/ceo/brain_dream_diffs/` (NEW directory — diff reports land here)
- `scripts/.last_dream_timestamp` (existing sentinel — respect idempotency)

### What Maya Already Has (from prior round)

- 4 consolidation patterns (A: new edges from co-activation, B: ecosystem entanglement nodes, C: archive/prune low-access, D: blind spot new nodes)
- 8 CIEU event types (BRAIN_DREAM_CYCLE_START, BRAIN_DREAM_PROPOSAL_WRITTEN, BRAIN_DREAM_CYCLE_COMPLETE, BRAIN_NODE_PROPOSED, BRAIN_EDGE_PROPOSED, BRAIN_ARCHIVE_PROPOSED, plus 2 others)

### What Maya Must Add

1. **`--dry-run` flag**: Runs all 4 patterns (A-D), computes proposed weight deltas and node/edge changes, writes a human-readable diff report to `reports/ceo/brain_dream_diffs/dream_diff_YYYYMMDD_HHMMSS.md` — but does NOT write to `aiden_brain.db`. Report format:

```
# Brain Dream Diff Report
Timestamp: 2026-04-19T23:45:00
Mode: DRY-RUN (no changes applied)
Activation log rows scanned: N

## Proposed New Edges (Pattern A)
| Source | Target | Proposed Weight | Co-activation Count |
|--------|--------|-----------------|---------------------|
| node_a | node_b | 0.15            | 4                   |

## Proposed New Nodes (Pattern D - Blind Spots)
| Proposed ID | Reason | Prompt Contexts |
|-------------|--------|-----------------|

## Proposed Archive (Pattern C)
| Node ID | Access Count (30d) | Reason |
|---------|-------------------|--------|

## Weight Delta Summary
| Edge | Old Weight | New Weight | Delta |
|------|-----------|------------|-------|

## Risk Assessment
- Echo chamber score: X (ratio of self-reinforcing vs diversifying changes)
- Bias direction: [which topics get stronger vs weaker]
```

2. **`--commit` flag**: Before applying changes, checks for:
   - A corresponding dry-run diff file exists in `reports/ceo/brain_dream_diffs/`
   - A CIEU event `BRAIN_DREAM_DIFF_REVIEWED` exists with timestamp AFTER the dry-run timestamp
   - If either check fails: print error message and exit without changes
   - If both pass: apply the changes from the diff to aiden_brain.db, emit `BRAIN_DREAM_COMMITTED` CIEU event

3. **Remove any auto-scheduling triggers**: If current code has session_close or Board-offline triggers that auto-invoke dream consolidation, comment them out with `# L3-Phase-2: auto scheduling disabled per CEO 2026-04-19 correction`

4. **CLI usage after changes**:
```
python3.11 scripts/aiden_dream.py --dry-run     # compute + write diff, no DB changes
python3.11 scripts/aiden_dream.py --commit       # apply after review gate passes
python3.11 scripts/aiden_dream.py --nrem         # existing NREM (unchanged)
python3.11 scripts/aiden_dream.py --full         # existing full cycle (unchanged)
python3.11 scripts/aiden_dream.py --report       # existing report (unchanged)
```

### Acceptance Criteria

- [ ] `--dry-run` produces diff report in `reports/ceo/brain_dream_diffs/` without touching aiden_brain.db
- [ ] Diff report includes all 4 pattern outputs + weight delta summary + echo chamber risk score
- [ ] `--commit` gate checks: (a) dry-run diff file exists, (b) BRAIN_DREAM_DIFF_REVIEWED CIEU event exists after dry-run timestamp
- [ ] `--commit` refuses to apply if gate checks fail (prints clear error, exits non-zero)
- [ ] `--commit` applies changes + emits BRAIN_DREAM_COMMITTED CIEU event when gates pass
- [ ] Any existing auto-scheduling triggers commented out with L3-Phase-2 note
- [ ] Existing --nrem, --full, --report modes unchanged (backward compatible)
- [ ] No git commit/push/add/reset operations

### Atomic Prompt Skeleton

```
You are eng-governance (Maya) delivering CZL-BRAIN-3LOOP-LIVE L3-Phase-1.

CRITICAL CONTEXT: CEO withdrew L3 auto scheduling. Board identified echo chamber + bias amplification risks. L3 must be MANUAL ONLY with dry-run audit gate.

BOOT — read these files FIRST:
1. scripts/aiden_dream.py — your prior code with 4 patterns + 8 CIEU event types
2. reports/ceo/governance/brain_3loop_live_architecture_v1.md — Section 4 (L3 spec, now partially superseded by CEO correction)
3. This task card (full acceptance criteria)

YOUR DELIVERABLES:
1. Add --dry-run to aiden_dream.py:
   - Run patterns A-D, compute all proposed changes
   - Write diff report to reports/ceo/brain_dream_diffs/dream_diff_YYYYMMDD_HHMMSS.md
   - Include: proposed edges, proposed nodes, proposed archives, weight deltas, echo chamber risk score
   - DO NOT touch aiden_brain.db

2. Add --commit to aiden_dream.py:
   - Gate check 1: dry-run diff file must exist in reports/ceo/brain_dream_diffs/
   - Gate check 2: CIEU event BRAIN_DREAM_DIFF_REVIEWED must exist with timestamp > dry-run timestamp
   - If gates fail: print error, exit(1)
   - If gates pass: apply changes to aiden_brain.db, emit BRAIN_DREAM_COMMITTED CIEU event

3. Disable auto-scheduling:
   - Comment out any session_close or Board-offline auto-triggers
   - Add comment: "L3-Phase-2: auto scheduling disabled per CEO 2026-04-19 correction"

4. Preserve existing modes (--nrem, --full, --report) backward compatible

CONSTRAINTS: No git ops. Scope: aiden_dream.py + reports/ceo/brain_dream_diffs/ only. <=5 tool_uses.
Receipt: reports/receipts/CZL-BRAIN-3LOOP-L3-PHASE1.md with 5-tuple.
```
