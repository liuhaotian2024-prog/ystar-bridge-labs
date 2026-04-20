# Brain 3-Loop Live Architecture — Consolidated v2 (CEO proposal awaiting CTO ruling)

**Audience**: Ethan-CTO for final architectural ruling (pending gov_delegate path); Ryan/Leo/Maya for implementation preview; Board for record.
**Research basis**: v1 spec (`brain_3loop_live_architecture_v1.md`) + Board consultant 5-point review (2026-04-19 evening) + CEO counter-analysis (agreed 3, extended 1, reframed 1, added 3 new points) + Ethan's prior rulings on CZL-BRAIN-AUTO-INGEST + CZL-BRAIN-BIPARTITE-P2-ALGO (H.7 escape reversal).
**Synthesis**: v1 spec architecture is sound. 12 input points (5 consultant + 4 CEO extensions + 3 CEO additions) need CTO consolidation. One genuine disagreement with consultant: CEO argues self-referential feedback loop is Hebbian-learning-by-design; the real gap is missing error signal in L2 relevance scoring — fix via **outcome-weighted Hebbian**, not just node-dominance monitor.
**Purpose**: single consolidation document Ryan/Leo/Maya can implement against. When Ethan's formal ruling lands (blocked by `must_dispatch_via_cto` rule over-trigger bug + missing `gov_delegate` script — both flagged for Leo follow-up), this doc becomes the effective contract.

**Author**: Aiden Liu (CEO) · **Date**: 2026-04-19 · **Status**: [L1] PROPOSAL — awaiting Ethan-CTO formal ruling
**Gating**: Leo `CZL-BRAIN-ADD-NODE-PRESERVE` ✓ SHIPPED; v2 impl starts after CTO ruling + Leo marker-per-session fix

---

## 1. Consolidation Table (12 input points)

| # | Input | Source | CEO Acceptance | Implementation Note |
|---|---|---|---|---|
| 1 | UserPromptSubmit hook choice | Consultant S2 | ACCEPTED | Keep as primary L1 trigger |
| 2 | Multi-tool-call L1 asymmetry | Consultant S2 gap | ACCEPTED + CEO-extended | **Add PostToolUse re-injection**: fire L1 again when (a) >120s since last query AND (b) tool scope <20% overlap with prior top-k |
| 3 | 0.6 relevance tier ambiguous | Consultant S3 | ACCEPTED + CEO-extended | Use `triggers` field (not name literal); verify populated before wire; add 2nd gate: embedding cosine >0.55 via cieu_brain_bridge 768-dim |
| 4 | Pattern D too risky auto | Consultant S4 | ACCEPTED + CEO-extended | Pattern D-LITE v1: tag `.low_coverage_prompts.jsonl` when top_k all <0.4 relevance. Auto-generate NODES = v2. |
| 5 | L5 metric missing denominator | Consultant S5 | ACCEPTED + CEO-extended | Add opportunity-count (denominator) + 30-day pre-brain baseline as control group |
| 6 | Self-referential runaway | Consultant S7 | **REFRAMED** | L1→decision→L2 loop IS Hebbian-by-design. Real fix: **outcome-weighted Hebbian** (see §3 below). Consultant's dominance monitor becomes secondary defense. |
| 7 | Dominance threshold 40% | Consultant S7 | REVISED STRICTER | 150 nodes → uniform baseline 0.67%. 40% = 60× baseline (too permissive). **Proposed: 10% warn / 20% hard-escalate.** |
| 8 | L2 learning-lag KPI | CEO addition | NEW | Define max learning lag <5s v1 target (async queue 30s drain vs next-decision latency) |
| 9 | Warm-start silence | CEO addition | NEW | `activation_log < 5000` rows → L1 suppresses injection + emit `BRAIN_WARMUP_PENDING`. Prevents noise-driven misdirection. |
| 10 | Cross-session Hebbian scope explicit | CEO addition | NEW | v1 Hebbian only within-session. Cross-session aggregation = L3 dream's job exclusively. Document explicitly. |
| 11 | Pattern D postponed to v2 | Consultant S4 | ACCEPTED (v1 scope lock) | v1 ships: L1 + L2 + L3 Pattern A/B/C + Pattern D-LITE tag only |
| 12 | Dominance monitor (secondary) | Consultant S7 | ACCEPTED | v1 includes monitor at 10%/20% thresholds. Primary defense is item #6 outcome-weighted Hebbian. |

---

## 2. v1 Scope Lock (what ships)

- L1 pre-query hook (UserPromptSubmit + PostToolUse re-injection per item #2)
- L2 write-back hook (PostToolUse Agent + Stop) with **outcome-weighted Hebbian** (item #6)
- L3 dream consolidation: **Pattern A/B/C only** (Pattern D-LITE tags but no node auto-gen)
- Triggers field audit + double-gate relevance scoring (items #3)
- Warm-start silence (item #9)
- Dominance monitor at 10%/20% (item #7)
- Learning-lag KPI < 5s (item #8)
- Within-session Hebbian only (item #10)
- L5 metric with denominator + pre-brain baseline (item #5)

**Out-of-scope v1**: Pattern D auto-generate, cross-session Hebbian aggregation (beyond dream), full causal-inference on L5, gov_delegate script.

---

## 3. Outcome-Weighted Hebbian (L2 core reframe)

### 3.1 Problem with v1 spec L2
v1 L2 relevance scoring: 1.0 explicit-cite / 0.6 keyword-match / 0.3 background. This measures **whether node was used**, NOT **whether the decision succeeded**. A failed decision that cited node A reinforces node A identically to a successful decision. Over time, bad patterns reinforce as strongly as good patterns → silent drift.

### 3.2 Proposed outcome signal
Within N minutes of decision (CEO proposes N=15), monitor for "negative outcome" CIEU events:
- `FORGET_GUARD` fire (any rule_id matching decision-author)
- `CROBA` violation (scope/boundary)
- `MUST_DISPATCH_VIA_CTO` fire
- `MATURITY_TAG_MISSING`
- `CIEU_MARKER_MISSING`
- Any `decision_canonical='deny'` event emitted after the fired decision for the same agent
- Board explicit correction in reply (harder to detect; use sentiment + "no/错/不对" markers)

### 3.3 Hebbian update formula
For each fired node pair (A, B) with co-fire relevance r_A, r_B in decision D:

```
if D triggered negative outcome within N=15 min:
    w_AB = max(0, w_AB - learning_rate * r_A * r_B)   # negative Hebbian
    co_activations_AB stays unchanged (count isn't the issue, weight is)
    emit CIEU BRAIN_HEBBIAN_DECAY with {nodes, outcome_event}
else (positive / neutral):
    w_AB = min(1.0, w_AB + learning_rate * r_A * r_B)  # standard Hebbian
```

**Asymmetry**: negative learning rate = 0.15 (higher than positive 0.10) to prevent runaway reinforcement of wrong patterns. Math argument: errors should be learned from FASTER than successes because they're rarer signals.

### 3.4 Integration with Ethan Q6 self-ref guard
- provenance='system:brain' events are EXCLUDED from outcome-weighted update (avoid brain punishing itself for its own suggestions that led to negative outcomes)
- Only decisions grounded in CEO-authored text or Board-authored prompts feed the outcome loop

### 3.5 Diagnostic CIEU emissions
- `BRAIN_HEBBIAN_UPDATE_POSITIVE` per positive update with magnitude
- `BRAIN_HEBBIAN_DECAY` per negative update with triggering outcome event_id
- Balance metric: daily ratio positive:negative must stay < 10:1 (if all positive, outcome signal is too weak; if too many negative, system unstable)

---

## 4. Dominance Monitor (secondary defense)

- Compute per-query: fraction of last 100 L1 queries where node X was top-1
- If X >10%: emit `BRAIN_NODE_DOMINANCE_WARN` with node_id + frequency
- If X >20%: emit `BRAIN_NODE_DOMINANCE_ESCALATE` + reduce X's effective weight in next 50 queries by 50% (transient suppression)
- Escalate-to-CEO via next boot report if >3 escalations in 30 days

Rationale: with 150 nodes and uniform baseline 0.67%, 10% = 15× baseline is the earliest statistically-suspicious threshold. 20% = 30× = clearly over-represented.

---

## 5. L5 Metric with Denominator & Baseline

Pre-brain baseline period: 2026-03-20 → 2026-04-19 (30 days before L1 goes live). Compute:
- `gap_events_pre_brain_30d` = count of violations from CIEU
- `opportunities_pre_brain_30d` = total tool calls in same window (denominator)
- `gap_rate_baseline` = gap_events / opportunities

Then during L1-live period:
- Same metrics monthly
- `gap_rate_delta_monthly` = (this month rate - baseline) / baseline
- **Flywheel proven** when 3 consecutive months of `gap_rate_delta < -10%` AND dominance warnings stay flat AND opportunity count stays within ±20% of baseline (controls for volume confounder)

---

## 6. Owner Handoff (revised per v2)

| Deliverable | Owner | v1 Scope |
|---|---|---|
| L1 hook + PostToolUse re-injection | Ryan-Platform | 2 config edits + latency tests |
| L1 module audit + triggers field verify | Leo-Kernel | verify all 150 nodes have triggers populated; embedding cosine double-gate |
| L2 outcome-weighted Hebbian | Leo-Kernel | new module implementing §3 formula + CIEU diagnostic emit |
| L2 async queue + learning-lag KPI | Ryan-Platform | background drain + <5s measurement |
| L2 warm-start silence | Ryan-Platform | threshold check + CIEU `BRAIN_WARMUP_PENDING` |
| L3 dream Pattern A/B/C | Leo-Kernel | no Pattern D auto |
| L3 Pattern D-LITE tag | Leo-Kernel | `.low_coverage_prompts.jsonl` write |
| L3 scheduling + CIEU events | Maya-Governance | session_close hook + 4 new event types |
| Dominance monitor 10%/20% | Maya-Governance | periodic scan + CIEU escalate |
| L5 baseline data collection | CEO (Aiden) | sqlite query for 30-day pre-brain violation/opportunity counts — writes to reports/ceo/metrics/ |
| Rule bug fix: `must_dispatch_via_cto` exempting CTO | Leo-Kernel | P1 follow-up card to be posted |
| gov_delegate script build | Leo-Kernel + Ryan | P1 follow-up card to be posted (currently rule references non-existent tool) |

---

## 7. Dependency & Ship Sequence

```
1. Leo CZL-MARKER-PER-SESSION-ISOLATION (P0, in flight now) → unblocks parallel spawns
   ↓
2. Ethan formal CTO ruling on this v2 (blocked by rule bug — gov_delegate missing)
   ↓
3. Leo: triggers field audit + outcome-weighted Hebbian module
   ↓
4. Ryan: L1 hook wire + async queue + learning-lag
   ↓
5. Maya: L3 pattern A/B/C + Pattern D-LITE tag + dominance monitor
   ↓
6. End-to-end regression: mock boot → prompt → tool calls → outcome events → Hebbian adjusts correctly
   ↓
7. CEO: L5 baseline data collection kickoff
```

---

## 8. Board Record

- 2026-04-19 CEO spec v1 shipped
- 2026-04-19 evening: Board consultant 5-point review delivered
- 2026-04-19 evening: CEO counter-analysis (AGREE 3 / EXTEND 1 / REFRAME 1 / ADD 3 new)
- 2026-04-19 evening: Board approved ("可以，批准")
- 2026-04-19 evening: CEO attempted Ethan spawn for formal ruling — BLOCKED by `must_dispatch_via_cto` rule over-trigger + missing gov_delegate
- 2026-04-19 evening: CEO authored this v2 consolidation as proposal; formal CTO ruling pending path unblock
