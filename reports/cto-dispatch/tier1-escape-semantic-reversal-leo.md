Audience: Leo-Kernel — engineer task card for CZL-ESCAPE-SEMANTIC-REVERSAL (bipartite loader polarity fix)
Research basis: CEO 2026-04-19 correction + Board consultant insight; cieu_bipartite_learning_v1.md Section 3.2 (revised lines 71-77, pre-hook escape = +0.6 positive signal, post-hook escape = -0.3 negative); bipartite_loader_phase2_algorithm_spec.md line 152 still has blanket escape = -0.3 (THE BUG); PRE_HOOK_CUTOFF = 2026-04-16 05:07:20 UTC per Ethan Ruling H.7
Synthesis: Pre-hook escape samples (51K+ events before hooks existed) are blindspot coordinates where governance was blind — the brain must learn TOWARD recognizing these patterns, not away. The bipartite loader spec and any in-flight code must split escape into pre-hook (+0.6) and post-hook (-0.3) using created_at vs PRE_HOOK_CUTOFF timestamp. This must ship same-batch as L3-Phase-1 because L3 dream consolidation would otherwise inherit the inverted polarity.
Purpose: Enable Leo to fix the escape partition split in the bipartite loader spec + any implementation code, preventing bias fixation if L3 runs on corrupted training signals

## Task: CZL-ESCAPE-SEMANTIC-REVERSAL — Fix escape sample polarity in bipartite loader

**Tier**: 1 (immediate, blocks L3 correctness)
**Engineer**: Leo-Kernel
**Priority**: P0
**Dispatch ID**: CZL-ESCAPE-SEMANTIC-REVERSAL
**Depends on**: CZL-BRAIN-BIPARTITE-P2 (Leo, completed — data baseline verified)
**Blocks**: CZL-BRAIN-3LOOP-LIVE L3 (Maya) — L3 consolidation uses bipartite weights; if escape polarity is wrong, L3 amplifies the error
**Budget**: <=5 tool_uses

---

### The Bug

`docs/kernel/bipartite_loader_phase2_algorithm_spec.md` line 152:
```
| escape | decision_canonical = 'escape' AND passed = 0 | -0.3 |
```

This treats ALL escape samples as negative pull. But pre-hook escapes (created before 2026-04-16 05:07:20 UTC) are blindspot coordinates where governance WAS blind — they are the most valuable positive teaching signal. Pushing the brain AWAY from these coordinates makes the brain LESS capable of recognizing future blindspots.

The CEO spec v1 (cieu_bipartite_learning_v1.md) already documents the correction at lines 71-77 (Ethan Ruling H.7), but the Phase 2 algorithm spec was written before the correction landed.

### The Fix

Split the escape partition into two:

| Partition | SQL predicate | Weight | Rationale |
|-----------|---------------|--------|-----------|
| escape_pre_hook | `decision_canonical = 'escape' AND passed = 0 AND created_at < '2026-04-16T05:07:20'` | **+0.6** | Blindspot coordinates: brain should learn TOWARD these patterns |
| escape_post_hook | `decision_canonical = 'escape' AND passed = 0 AND created_at >= '2026-04-16T05:07:20'` | **-0.3** | Genuine rule-edge-case: push brain away |

Constant: `PRE_HOOK_CUTOFF = '2026-04-16T05:07:20'` (first HOOK_PRE_CALL CIEU event)

### Files in scope (HARD BOUNDARY)

- `docs/kernel/bipartite_loader_phase2_algorithm_spec.md` (MODIFY — split escape partition table + update weight composition rules + update batch composition math)
- `/Users/haotianliu/.openclaw/workspace/Y-star-gov/ystar/governance/cieu_bipartite_learner.py` (CREATE or MODIFY if exists — implement split in code)
- `reports/ceo/governance/cieu_bipartite_learning_v1.md` (READ ONLY — reference for correct weights, do NOT modify)

### Acceptance Criteria

- [ ] Phase 2 algorithm spec partition table (Section B.1) splits escape into `escape_pre_hook` (+0.6) and `escape_post_hook` (-0.3)
- [ ] `PRE_HOOK_CUTOFF = '2026-04-16T05:07:20'` defined as a named constant
- [ ] Weight composition rules updated: drift_detected modifier still applies additively (pre-hook escape + drift = +0.4, post-hook escape + drift = -0.5)
- [ ] Batch composition math (Section B.3) updated: escape_count now sums both sub-partitions; the 5% floor applies to combined escape presence
- [ ] If `cieu_bipartite_learner.py` exists, the `load_training_batch()` function implements the split
- [ ] If `cieu_bipartite_learner.py` does not exist yet, the spec changes are sufficient — implementation ships in the next batch when the module is created
- [ ] WeightedEvent dataclass partition field updated: `'escape_pre_hook' | 'escape_post_hook'` instead of bare `'escape'`
- [ ] REWRITE multiplier section left as-is (already retracted per Maya's audit)
- [ ] No git commit/push/add/reset operations

### Atomic Prompt Skeleton

```
You are eng-kernel (Leo) delivering CZL-ESCAPE-SEMANTIC-REVERSAL.

CRITICAL CONTEXT: CEO spec had escape sample polarity inverted. Pre-hook escapes (before 2026-04-16 05:07:20 UTC) are POSITIVE teaching signals (+0.6), not negative pull. Board consultant caught this — these are blindspot coordinates where governance WAS blind, brain must learn TOWARD them. Post-hook escapes (after cutoff) are genuine edge-case failures, keep at -0.3.

BOOT — read these files FIRST:
1. docs/kernel/bipartite_loader_phase2_algorithm_spec.md — YOUR spec, Section B.1 partition table is THE BUG (line 152: blanket escape = -0.3)
2. reports/ceo/governance/cieu_bipartite_learning_v1.md — Section 3.2 lines 71-77 has the CORRECT weights (Ethan Ruling H.7)

YOUR DELIVERABLES:
1. Fix docs/kernel/bipartite_loader_phase2_algorithm_spec.md:
   - Section B.1: split escape row into escape_pre_hook (+0.6) and escape_post_hook (-0.3)
   - Add constant: PRE_HOOK_CUTOFF = '2026-04-16T05:07:20' (first HOOK_PRE_CALL CIEU event)
   - SQL predicate for pre-hook: created_at < PRE_HOOK_CUTOFF
   - SQL predicate for post-hook: created_at >= PRE_HOOK_CUTOFF
   - Section B.1 weight composition: pre-hook + drift = +0.4, post-hook + drift = -0.5
   - Section B.3 batch composition: escape_count = sum(pre_hook + post_hook), 5% floor applies to combined
   - WeightedEvent.partition: add 'escape_pre_hook' | 'escape_post_hook' variants

2. Check if Y-star-gov/ystar/governance/cieu_bipartite_learner.py exists:
   - If YES: implement the split in load_training_batch()
   - If NO: spec changes are the full deliverable for this task; the code implementation ships when the module is built

3. Do NOT touch:
   - REWRITE section (already retracted)
   - cieu_bipartite_learning_v1.md (CEO doc, read-only for you)
   - Any other file

CONSTRAINTS: No git ops. Scope-locked files only. <=5 tool_uses.
Receipt: reports/receipts/CZL-ESCAPE-SEMANTIC-REVERSAL.md with 5-tuple.
```
