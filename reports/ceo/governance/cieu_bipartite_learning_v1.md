# CZL-BRAIN-BIPARTITE — CIEU Bipartite Learning System (Anti-Feedback-Loop)

**Audience**: CTO Ethan for architectural ruling; eng-kernel (Leo) for normalizer + loader; eng-governance (Maya) for outcome weighting + oversample logic; future sessions auditing whether this actually mitigates feedback-loop bias.
**Research basis**: empirical CIEU distribution at 2026-04-19T15:35 on `.ystar_cieu.db` (394,350 total events): passed=1 280,981 / passed=0 113,369 / violations non-empty 29,141 / drift_detected=1 38,855 / **escape samples (passed=0 + decision=allow) 611** / **REWRITE guidance in drift+violations 131**. Tesla 2025 FSD retrogression documented as feedback-loop failure where self-labeled shadow-mode decisions reinforced prior biases without contrastive signal; our CIEU structure carries bipartite outcome labels Tesla lacked.
**Synthesis**: CIEU's decision/passed/violations/drift_detected fields form a natively bipartite supervision signal — positive (Rt+1=0) and negative (Rt+1≠0) samples both carry structured metadata. Escape samples (611 records) are the rarest and highest-value training signal. But `decision` field has 20+ raw values with case variance and near-synonyms; a normalization pass is prerequisite.
**Purpose**: design a 5-strategy bipartite learning pipeline that (1) doesn't double-down on prior decisions the way Tesla did, (2) actively contrasts against negative samples, (3) oversamples rare failures, (4) protects against OOD drift from new event types entering training without sufficient evidence.

**Author**: Aiden Liu (CEO)
**Date**: 2026-04-19
**Status**: [L1] SPEC — ready for CTO architectural review
**Authority**: Board directive 2026-04-19 — "研究 CIEU 包含正确 Rt+1=0 和失败 Rt+1≠0 两种 → 用更聪明的方法避免加倍偏见"

---

## 1. Empirical Verification (done before design)

Query run on `.ystar_cieu.db` 2026-04-19T15:35:

| Sample category | Filter | Count | % of total |
|---|---|---|---|
| Positive (Rt+1=0) | `passed=1` | 280,981 | 71.2% |
| Negative (Rt+1≠0) | `passed=0` | 113,369 | 28.8% |
| Violations-detailed | `violations not null, not '[]'` | 29,141 | 7.4% |
| Drift-detected | `drift_detected=1` | 38,855 | 9.9% |
| **Escape (rarest)** | `passed=0 AND decision='allow'` | **611** | **0.15%** |
| **REWRITE guidance** | drift_details or violations LIKE '%REWRITE%' | **131** | **0.03%** |

**Gotcha**: `decision` field has 20+ distinct values, not just {allow, deny, escalate}:
- Case variance: `ALLOW` (3) vs `allow` (70,586)
- Near-synonyms: `accept` (6), `approved` (1), `reject` (7), `rewrite` (7)
- Operational: `route` (46), `dispatch` (2), `complete` (29), `error` (181)
- Meta-signals: `warn` (56,036), `warning` (438), `info` (155,163), `unknown` (32,302)
- Corruption: embedded JSON fragments (agent reports leaked into decision field)

A **decision normalizer** is prerequisite before bipartite sampling.

## 2. Prerequisite: Decision Normalizer

`Y-star-gov/ystar/governance/cieu_decision_normalizer.py`:

```python
CANONICAL = {
    'allow': {'allow', 'ALLOW', 'accept', 'approved', 'pass'},
    'deny':  {'deny', 'reject', 'blocked', 'denied'},
    'escalate': {'escalate', 'warn', 'warning'},
    'rewrite':  {'rewrite', 'route', 'dispatch'},  # guidance-carrying decisions
    'info':     {'info', 'complete', 'log'},        # non-supervisory signals
    'unknown':  {'unknown', 'error', '<embedded_json>'},
}
```

Output: migration script that adds `decision_canonical` column. Original `decision` preserved (audit trail). Downstream sampling uses canonical only.

## 3. Five Bias-Avoidance Strategies

### 3.1 Contrastive Drift (not averaging)

Node coordinates in brain graph update as:
```
new_coord = positive_centroid + α * (positive_centroid - negative_centroid)
```
α ∈ [0.1, 0.3]. α=0 degenerates to Tesla's averaging-over-all-firings pattern. α>0 pushes representations **away** from negative centroid, not just toward positive mean.

### 3.2 Weight-by-Outcome (not filter) — **REVISED 2026-04-19 per Ethan Ruling H.7**

| Sample | Weight | Rationale |
|---|---|---|
| passed=1 + violations=[] | +1.0 | clean positive |
| passed=1 + violations has warning | +0.5 | soft positive |
| passed=0 + decision=deny (correctly blocked) | +0.8 | teaching signal: "good deny" |
| **pre-hook escape** (`created_at < PRE_HOOK_CUTOFF` + decision ∈ {allow,warn} + passed=0) | **+0.6** | **blindspot coordinates — brain correctly detected but system lacked authority to block (Board consultant insight)** |
| **post-hook escape** (`created_at >= PRE_HOOK_CUTOFF` + decision ∈ {allow,warn} + passed=0) | **-0.3** | genuine rule-edge-case — push brain away |
| passed=0 + drift_detected=1 | -0.2 | soft negative |

**Critical reversal from v1**: pre-hook escape events (51K from 2026-04-09 → 2026-04-16 05:07:20 window) are **positive teaching signal**, not negative-pull. They are the coordinates where governance WAS blind; the brain should learn TOWARDS recognizing these patterns, not away. Post-hook escapes (near-zero today) are the true negative class.

`PRE_HOOK_CUTOFF` = 2026-04-16 05:07:20 UTC (first HOOK_PRE_CALL CIEU event). Constant defined in `cieu_bipartite_learner.py`.

Authority: Ethan CTO Ruling H.7 (`Y-star-gov/reports/cto/CZL-BRAIN-BIPARTITE-P2-ALGO-ruling.md`).

### 3.3 REWRITE Path Teaching-Signal Boost — **RETRACTED 2026-04-19**

> **STRIKE-THROUGH**: this section is invalidated by `reports/receipts/CZL-REWRITE-AUDIT.md` (Maya-Governance, 2026-04-19). 151 substring matches are 100% false positives — captured file-path references (`auto_rewrite.py`) and command strings, not real teaching signals. Only 7 genuine `REWRITE_APPLIED` events exist and all are test scaffold with NULL drift_details / no structured before-after metadata. Applying × 3 weight would actively poison training by triple-weighting irrelevant ForgetGuard warnings.
>
> **Revised stance**: the REWRITE teaching-signal pathway is a future possibility, not a current capability. It requires (a) auto_rewrite.py emitting structured `original_action`/`rewritten_action` metadata, AND (b) production corpus reaching ≥50 REWRITE_APPLIED events. Until both conditions met, treat REWRITE as a placeholder — do NOT apply × 3 multiplier in any loader or training pass.
>
> **Methodology lesson**: substring matching on free-text fields (`drift_details LIKE '%REWRITE%'`) is fundamentally unreliable for semantic classification. All future bipartite-training heuristics must use structured fields (`event_type`, `decision`, `decision_canonical`) AND include a 10+ event spot-check before activation — this is now a mandatory validation gate, propagated into the Phase 2 algorithm spec open questions.

~~`drift_details` or `violations` containing `REWRITE` → `weight × 3`. These are the expert-annotated counterfactuals ("not X, do Y instead"). 131 records currently — small corpus but precious. Multiplier kept high until corpus grows past ~1000.~~

~~↑ This paragraph superseded by the retraction above. Kept in strikethrough for audit trail — do NOT remove from the document.~~

### 3.4 Rare-Failure Oversample

Escape samples (611 records, 0.15%) sampled at **inverse proportion** — in each training minibatch, ensure ≥5% escape samples. Prevents brain from losing coverage of the rarest and most dangerous failure mode.

### 3.5 OOD Hold-Back (temporal guard)

For each `event_type`, track sample count in `event_type_coords` table. If new event_type appears with `samples < 50`, **hold back** inclusion in contrastive drift until corpus stabilizes. Meanwhile, log OOD events for human (Board / CTO) review.

Why: a new event_type with insufficient samples could be a drift symptom itself; training on it prematurely would bake in noise as signal.

## 4. Feedback-Loop Mitigation Audit

To prove we don't replicate Tesla's failure, ship a **feedback-loop detector** that runs weekly:

- Compare the current brain's prediction on a held-out sample vs what the brain would have predicted 30 days ago on the same sample.
- If the divergence is monotonic (always moving away) without corresponding improvement in production outcomes, flag as feedback-loop drift.
- Action: freeze training for 3 days, run Board review, then decide whether to rollback to 30-day-ago weights or continue.

## 5. Implementation Phases

| Phase | Deliverable | Owner | Target |
|---|---|---|---|
| 1 | Decision normalizer + canonical column + migration | Leo-Kernel | L3 same-round |
| 2 | Bipartite loader with 5 strategies above | Maya-Governance | L3 |
| 3 | OOD hold-back logic + event_type sample threshold | Leo-Kernel | L3 |
| 4 | Feedback-loop detector + weekly cron | Ryan-Platform | L3 |
| 5 | Brain training integrated with weighted loader; first A/B run vs current brain | Leo-Kernel + CEO observe | L4 SHIPPED |
| 6 | 30-day live run + monthly audit | CEO owns audit | L5 PROVEN |

## 6. Integration with Existing Work

- **ARCH-18 CIEU-as-Brain-Corpus** (Ethan's draft today) already frames CIEU as training substrate; this spec is the concrete bipartite extension.
- **CZL-GOV-LIVE-EVAL** uses same CIEU events for directive liveness checks; the canonical `decision` column benefits both.
- **`hebbian_learning`** in `aiden_recall.py`: the weight-by-outcome pattern here replaces / augments naive Hebbian; CTO ruling needed on whether Hebbian sub-system gets retrofit or runs parallel.

## 7. Open Questions (for CTO architectural review)

1. Hebbian compatibility — retrofit or parallel? (see Section 6)
2. Where does `decision_canonical` column live — `.ystar_cieu.db` migration (invasive, but single source) or a materialized view (non-invasive, slower)? Lean migration.
3. α (contrastive drift scale) initial value — start at 0.15 or 0.25? Bayesian argument either way; suggest 0.15 for safety, tune up if brain under-differentiates.
4. Feedback-loop detector's "divergence threshold" — need a concrete metric (KL divergence on output distribution? L2 on weight deltas?). CTO to rule.

## 8. Success Criteria

- L3: normalizer + loader + OOD hold-back shipped, unit tests pass.
- L4: first A/B run — new-weights brain vs current brain on held-out CIEU month → new brain ≥ baseline on escape-sample recall (611 escape events should be recognized at higher rate than current brain).
- L5: 30-day prod run with 0 feedback-loop drift alarms + monthly Board audit satisfied.
