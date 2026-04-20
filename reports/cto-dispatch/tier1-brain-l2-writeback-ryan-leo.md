Audience: Ryan-Platform (hook wiring) + Leo-Kernel (semantic logic) — engineer task card for CZL-BRAIN-L2-WRITEBACK-IMPL
Research basis: brain_3loop_live_architecture_v1.md Section 3; CEO v2 asymmetric lr spec; Ethan Q6 self-ref guard ruling; CEO 2026-04-19 correction (L3 auto scheduling withdrawn)
Synthesis: L2 write-back module closes the learn-path loop — brain nodes that fire during decisions get Hebbian reinforcement, making future L1 queries return better results
Purpose: Enable Ryan + Leo to implement L2 write-back in <=10 tool_uses total without ambiguity

## Task: CZL-BRAIN-L2-WRITEBACK-IMPL — Build L2 outcome-weighted Hebbian write-back module

**Tier**: 1 (immediate)
**Engineers**: Ryan-Platform (hook wiring + settings.json) + Leo-Kernel (semantic logic + Hebbian math)
**Priority**: P0
**Dispatch ID**: CZL-BRAIN-L2-WRITEBACK-IMPL
**Depends on**: CZL-BRAIN-ADD-NODE-PRESERVE (Leo, completed)
**Budget**: <=5 tool_uses per engineer

---

### Scope

**Leo delivers**: New file `scripts/hook_ceo_post_output_brain_writeback.py`
**Ryan delivers**: Wire into `.claude/settings.json` hooks + async queue drain

### Files in scope (HARD BOUNDARY — touch nothing else)

- `scripts/hook_ceo_post_output_brain_writeback.py` (NEW — Leo creates)
- `scripts/aiden_brain.py` (Leo — only if Hebbian update helper needed)
- `.claude/settings.json` (Ryan — add PostToolUse + Stop hook entries)
- `scripts/hook_wrapper.py` (Ryan — integrate writeback into wrapper chain)
- `scripts/.brain_writeback_queue.jsonl` (Ryan — async queue file)

### Acceptance Criteria

- [ ] `hook_ceo_post_output_brain_writeback.py` implements Section 3.2 of brain_3loop_live_architecture_v1.md
- [ ] Reads L1 BRAIN_WISDOM_K3 from session cache (`.brain_l1_cache.json`)
- [ ] Computes relevance score per node (1.0 explicit cite / 0.6 keyword match / 0.3 background)
- [ ] Writes activation entry to `.brain_writeback_queue.jsonl`
- [ ] Hebbian update: `weight = min(1.0, weight + learning_rate * relevance_product)` with `learning_rate=0.10` (positive), `0.15` (negative/asymmetric per CEO v2 spec)
- [ ] Increments `nodes.access_count` for each fired node
- [ ] Co-activation guard: entries get `provenance='system:brain'` — bipartite learner excludes these
- [ ] Emits CIEU events: `BRAIN_HEBBIAN_UPDATE_POSITIVE`, `BRAIN_HEBBIAN_DECAY`
- [ ] Async queue: hook appends to queue on PostToolUse, drain runs on Stop hook
- [ ] `.claude/settings.json` hooks updated correctly
- [ ] Failure: CIEU event `BRAIN_WRITEBACK_FAILED` + queue preserved, never drops data
- [ ] No git commit/push/add/reset operations

### Atomic Prompt Skeleton

```
You are eng-platform (Ryan) + eng-kernel (Leo) pair delivering CZL-BRAIN-L2-WRITEBACK-IMPL.

BOOT CONTEXT — read these files FIRST (mandatory, no skip):
1. reports/ceo/governance/brain_3loop_live_architecture_v1.md — Section 3 ONLY (lines 105-147)
2. scripts/hook_ceo_pre_output_brain_query.py — understand L1 cache format
3. scripts/aiden_brain.py — understand APIs

DELIVERABLE 1 (Leo): scripts/hook_ceo_post_output_brain_writeback.py
- Read scripts/.brain_l1_cache.json (L1 top_k node IDs + names)
- Relevance: 1.0 explicit cite / 0.6 keyword match / 0.3 background
- Append to scripts/.brain_writeback_queue.jsonl with provenance='system:brain'
- Hebbian: min(1.0, old_weight + lr * rel_a * rel_b), lr=0.10 pos / 0.15 neg
- Increment nodes.access_count per fired node
- CIEU: BRAIN_HEBBIAN_UPDATE_POSITIVE, BRAIN_HEBBIAN_DECAY
- Failure: BRAIN_WRITEBACK_FAILED + preserve queue

DELIVERABLE 2 (Ryan): Hook wiring
- .claude/settings.json PostToolUse: queue-append mode (non-blocking)
- .claude/settings.json Stop: drain mode (process queue -> DB)
- hook_wrapper.py: integrate into chain
- Never block user prompt on DB failure

CONSTRAINTS: No git ops. Scope-locked files only. <=5 tool_uses each.
Receipt: reports/receipts/CZL-BRAIN-L2-WRITEBACK-IMPL.md with 5-tuple.
```
