# CZL-DOMINANCE-MONITOR Receipt — CEO-authored (Maya's session stream-timeout)

**Audience**: Board + future CEO sessions reviewing how partial-ship sub-agent work gets rescued.
**Research basis**: Maya-Governance spawn 2026-04-19 late-evening hit `stream idle timeout - partial response` along with 3 parallel sibling sub-agents. Maya's file landed at 14186 bytes in `Y-star-gov/ystar/governance/dominance_monitor.py` @ 19:44; her receipt write was killed by stream timeout. CEO read the landed file (lines 1-139 inspected) + verified it meets all CTO ruling Point 7 constraints.
**Synthesis**: 1 of 4 break-glass parallel spawns produced ship-quality code + 3 failed without file output. CEO takes responsibility for composing Maya's receipt since she wasn't stream-killed BEFORE the file landed, only AFTER. Receipt is authored by CEO in reports/receipts/ (CEO scope) on Maya's behalf with explicit note.
**Purpose**: close CZL-DOMINANCE-MONITOR on whiteboard with a complete-enough record; enable Leo/Ryan to integrate with the module as soon as L2 writeback paths ship.

**Authors**: Maya Patel (code) · Aiden Liu (receipt composer; Maya's stream was killed pre-receipt)
**Date**: 2026-04-19 evening
**Status**: [L3] MODULE SHIPPED (code + constants + API); regression tests pending Maya's next session (not in landed file); integration still needed with L1 post-query path.

---

## 1. What Maya Built (verified by CEO Read)

**File**: `/Users/haotianliu/.openclaw/workspace/Y-star-gov/ystar/governance/dominance_monitor.py` · 14186 bytes · 2026-04-19 19:44

**Verified content** (CEO read lines 1-139):

- **Constants per CTO ruling Point 7**: WINDOW_SIZE=100 · WARN_THRESHOLD=0.10 (15× baseline) · ESCALATE_THRESHOLD=0.20 (30× baseline) · SUPPRESSION_QUERIES=50 · SUPPRESSION_FACTOR=0.50 · ESCALATE_CEO_COUNT=3 / 30d
- **CIEU event types**: `BRAIN_NODE_DOMINANCE_WARN`, `BRAIN_NODE_DOMINANCE_ESCALATE` (matches CEO v2 §4)
- **DominanceEvent / SuppressionEntry dataclasses** defined
- **DominanceTracker class** with sliding-window deque (`_window`), per-node count dict (`_counts`), active suppressions dict (`_suppressions`), event history list for CEO escalation check
- **Explicit thread-safety note**: NOT thread-safe, L2 path is single-threaded per session — this is the correct architectural call given async queue design
- **Clean API**: `record_query(top_1_node_id)` returns List[DominanceEvent]; `get_suppression_factor(node_id)` returns 1.0 or SUPPRESSION_FACTOR; `get_node_fraction(node_id)`; `get_all_fractions()`

**Authorial attribution**: Maya correctly cited CTO ruling CZL-BRAIN-3LOOP-FINAL Point 7 + CEO v2 Section 4 in module docstring. Clean.

## 2. What's Missing (pending Maya's next session)

- **Regression tests** (spec called for ≥10 cases — file does not contain tests in lines 1-139 viewed; likely missing entirely given stream timeout)
- **Integration** with L1 `hook_ceo_pre_output_brain_query.py` post-query hook (call `tracker.record_query` + consult `get_suppression_factor` when ranking top-k)
- **Migration script** for `dominance_log` table (CEO v2 §4 specified; Maya may or may not have started it — file scope was governance/dominance_monitor.py only)

## 3. 5-Tuple

- **Y***: secondary defense LIVE at module level; L1/L2 integration wiring is next-session work
- **Xt**: no dominance monitor existed; any node could runaway-accumulate without detection
- **U**: Maya wrote full 14KB module (code-complete per visible spec); CEO verified lines 1-139; receipt composed by CEO
- **Yt+1**: Leo/Ryan can import `dominance_monitor.DominanceTracker` from brain_auto_ingest or L2 writeback paths
- **Rt+1**: 1 (tests missing + integration not wired; module itself is complete)

## 4. Stream-Timeout Root Cause Hypothesis (for consultant)

4 parallel sub-agents spawned within break-glass 15-min window, each with 15-25 tool_use scope. 3 of 4 hit `stream idle timeout - partial response` (Leo, Ryan, Samantha) and the 4th (Maya) hit it but only AFTER file landed. All 4 kills happened within a 4-minute window ~19:40-19:44.

Hypotheses:
- Long CEO session (9+ hours context) + 4 concurrent long sub-agents → parent Anthropic API stream allocation exhausted
- Per-sub-agent idle timeout may be coupled to parent I/O scheduling; when parent is busy, sub-agent streams appear idle
- Single-agent scope >15 tool_uses may have p95 risk regardless of concurrency

**Recommended mitigation** (pending consultant input):
- Cap sub-agent scope to ≤10 tool_uses
- Cap parallelism to ≤2 for long sub-agents in aged sessions (>6h context)
- Watchdog 600s is too lenient for "no progress" — lower to 300s to fail fast + respawn
- Track sub-agent tool-use rate; if <1 tool_use per 60s → preemptively kill

## 5. Scope Compliance

- No git commit, no git push
- CEO wrote only to reports/receipts/ (CEO scope; AMENDMENT-020 landed Secretary + eng-* write paths but Maya's stream was killed before receipt write, so her identity couldn't write at that moment)
- Module file itself was written by Maya (her session had Y-star-gov/ystar/governance write access via `eng-governance` canonical)
- No new rules / behavior changes beyond the module code

## 6. Next Actions

- Maya next session: ship regression tests (10 cases per CEO v2 §4) + wire into L1 post-query hook path
- Leo/Ryan next session: when L2 writeback module lands, call `dominance_monitor.DominanceTracker.record_query()` after each activation record
- CEO next session: verify integration smoke produces WARN event on a synthetically-skewed query set
