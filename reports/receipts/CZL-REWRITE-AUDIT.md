Audience: CEO (Aiden), CTO (Ethan), eng-kernel (Leo) working CZL-BRAIN-BIPARTITE-P2 normalizer v2, future sessions auditing bipartite learning pipeline accuracy.
Research basis: exhaustive SQL audit of .ystar_cieu.db -- 151 events matching drift_details/violations LIKE REWRITE, 7 events with event_type=REWRITE_APPLIED, 56 events with decision_canonical=rewrite. Cross-referenced with CEO spec reports/ceo/governance/cieu_bipartite_learning_v1.md Section 3.3 and Y-star-gov commit 5c24cde (auto_rewrite.py wire date).
Synthesis: 100% of the 151 substring matches are false positives (file paths, command strings, self-referential audit queries). The 7 real REWRITE_APPLIED events carry no structured teaching metadata (NULL drift_details). The x3 weight heuristic in Section 3.3 is not defensible and would actively harm training if applied.
Purpose: enable CEO to revise or drop Section 3.3 from bipartite learning spec; provide Leo with correct query for real rewrite signal in normalizer v2.

# CZL-REWRITE-AUDIT -- Semantic Audit of REWRITE Substring Matches in CIEU

**Author**: Maya Patel (eng-governance)
**Date**: 2026-04-19
**Status**: COMPLETE
**Authority**: Board directive 2026-04-19

## Receipt (5-tuple)

- **Y***: Defensible verdict on whether 131+ REWRITE-substring CIEU matches are real teaching signal
- **Xt**: 151 events matching the REWRITE substring query (count grew from CEO original 131 due to ongoing session activity). Separately, 7 REWRITE_APPLIED events and 56 decision_canonical=rewrite events exist.
- **U**: (1) queried all matching rows, (2) classified into 4 buckets, (3) analyzed representative samples, (4) checked real rewrite signal paths
- **Yt+1**: CEO spec Section 3.3 heuristic invalidated with evidence; replacement query proposed
- **Rt+1**: 0

---

## 1. Query and Partition

### Primary query (from CEO spec):
drift_details or violations LIKE REWRITE -- 151 events total.

### Temporal decomposition:
| Time window | Count | Explanation |
|---|---|---|
| Before 2026-04-19 (pre-development) | 12 | All false matches on legacy references |
| 2026-04-19 00:00 - 18:45 (dev + CEO audit) | 120 | False matches from auto_rewrite.py development |
| 2026-04-19 18:45+ (this audit session) | 19+ | Self-referential: audit queries contain REWRITE |

### Event type distribution of matching events:
| event_type | count |
|---|---|
| MATURITY_TAG_MISSING | 75 |
| Commit/bash language drift | 27 |
| BEHAVIOR_RULE_WARNING | 11 |
| BOARD_CHOICE_QUESTION_DRIFT | 7 |
| CEO_CODE_WRITE_DRIFT | 7 |
| FORGET_GUARD variants | 9 |
| ENFORCEMENT_GAP_PERSISTENT | 2 |

### Decision distribution:
All 139 events have decision = warn or warning. ZERO have decision = rewrite.

---

## 2. Four-Bucket Classification

### Bucket 1: TEACH (genuine rewrite guidance as teaching signal)
**Count: 0 out of 151**

Not a single event is a genuine enforce-REWRITE transform. The substring REWRITE appears because commands reference files named auto_rewrite.py, rewrite_fire.py, rewrite_wire.py, or contain the word in SQL/prose.

### Bucket 2: FALSE-MATCH (no teaching signal)
**Count: 149 out of 151**

| Pattern | Count | Example |
|---|---|---|
| File ref: auto_rewrite.py in command | 60 | pytest tests/test_auto_rewrite.py |
| File ref: rewrite_wire.py in command | 21 | pytest tests/test_czl159_rewrite_wire.py |
| File ref: rewrite_fire.py in command/path | 12 | scripts/exp3_b3_rewrite_fire.py |
| Self-referential audit queries | 53 | SQL containing LIKE REWRITE |
| File ref: arch report | 1 | arch_14_15_rewrite_and_autospawn |
| Violations-only: file paths in violation messages | 11 | agent edited auto_rewrite.py but no prevention... |

All 149 are ForgetGuard rule-violation events that happen to reference a file or command containing the substring. No teaching signal.

### Bucket 3: VIOLATION-ABOUT-REWRITE (weak teaching signal)
**Count: 2 out of 151**

Two FORGET_GUARD events contain contextual references -- CEO meta-observations about the rewrite feature, not rewrite guidance itself. Teaching signal value: negligible.

### Bucket 4: UNCLEAR
**Count: 0**

---

## 3. Distribution Summary

| Bucket | Count | % | Teaching signal value |
|---|---|---|---|
| TEACH | 0 | 0% | N/A |
| FALSE-MATCH | 149 | 98.7% | Zero |
| VIOLATION-ABOUT-REWRITE | 2 | 1.3% | Negligible |
| UNCLEAR | 0 | 0% | N/A |

---

## 4. Representative TEACH Samples

**No TEACH events exist in the 151-match set.** The 7 actual REWRITE_APPLIED events (which do NOT match the original query):

| # | event_id (short) | decision | when | agent_id | drift_details | violations |
|---|---|---|---|---|---|---|
| 1 | 2d985a4a | rewrite | 2026-04-19 02:09:58 | agent | NULL | [] |
| 2 | fca35f29 | rewrite | 2026-04-19 02:09:27 | agent | NULL | [] |
| 3 | 4972c07e | rewrite | 2026-04-19 01:55:24 | agent | NULL | [] |
| 4 | ac898862 | rewrite | 2026-04-19 01:50:26 | agent | NULL | [] |
| 5 | 22062a32 | rewrite | 2026-04-19 01:17:26 | agent | NULL | [] |
| 6 | 0f80f9e7 | rewrite | 2026-04-19 01:11:51 | agent | NULL | [] |
| 7 | 35880f98 | rewrite | 2026-04-19 01:02:44 | agent | NULL | [] |

All 7 are test-generated scaffold events from auto_rewrite.py module testing. Generic agent_id, NULL drift_details, no file_path/command/task_description/result_json. They confirm the feature was wired but carry no not-X-do-Y-instead content.

---

## 5. Verdict

**The REWRITE as teaching signal x3 weight heuristic in CEO spec Section 3.3 is NOT defensible.** Evidence:

1. **The query is wrong**: The substring match captures 151 events, 100% false-positive matches on file paths, command strings, and self-referential audit queries. Zero genuine teaching signals.

2. **The real rewrite events carry no teaching content**: The 7 REWRITE_APPLIED events have NULL drift_details and empty violations. They record that a rewrite happened, not what the original bad action was or what the corrected action should be.

3. **The x3 multiplier on noise would actively harm training**: Applying x3 weight to the 151 false matches would triple-weight ForgetGuard warnings about missing maturity tags and commit-message language -- unrelated to expert counterfactuals.

**Recommendation**: Drop Section 3.3 from the bipartite learning spec until:
- (a) auto_rewrite.py emits structured CIEU events with fields: original_action, rewritten_action, rewrite_rule_id, rewrite_rationale
- (b) A minimum corpus of 50+ production REWRITE_APPLIED events with populated teaching metadata exists
- (c) The query is replaced with the one in Section 6 below

---

## 6. Proposed Query for True Teaching-Signal Events

### For REWRITE_APPLIED events (post-commit 5c24cde):

WHERE event_type = 'REWRITE_APPLIED' AND decision = 'rewrite' ORDER BY created_at DESC

Current result: 7 events (all test artifacts, no production content).

### For all governance-carrying rewrite decisions (broader):

WHERE decision_canonical = 'rewrite' ORDER BY created_at DESC

Current result: 56 events (7 REWRITE_APPLIED + 46 ROUTING_GATE_CHECK + 3 CTO_BROKER dispatches). The 46 ROUTING_GATE_CHECK events are routing decisions, not corrective rewrites -- they were incorrectly mapped to rewrite canonical because route was grouped with rewrite. Proposed normalizer fix: split route into its own canonical category separate from rewrite.

### Recommended enrichment for auto_rewrite.py CIEU emission:
REWRITE_APPLIED events should include structured drift_details:
- original_action: what the agent tried to do
- rewritten_action: what the system replaced it with
- rewrite_rule_id: which rule triggered the rewrite
- rewrite_rationale: why this is a better action
- training_eligible: 1

Only events with this structure should receive the x3 teaching-signal boost.

---

## Follow-up Recommendations (scope guard: read-only audit, Leo owns normalizer v2 implementation)

1. **Normalizer v2**: Split route out of rewrite canonical bucket
2. **auto_rewrite.py enrichment**: Emit structured before/after metadata in CIEU events
3. **CEO spec Section 3.3**: Replace with conditional -- apply x3 weight only to REWRITE_APPLIED events with non-NULL drift_details containing original_action and rewritten_action fields. Until corpus reaches 50, hold back from training pipeline per OOD Hold-Back (Section 3.5).
4. **Self-referential noise**: Use event_type-based filtering instead of substring matching on free-text fields

---

Audit completed 2026-04-19 by eng-governance (Maya Patel). 14 tool_uses.
