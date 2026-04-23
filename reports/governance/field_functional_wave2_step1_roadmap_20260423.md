---
Y_star: "Produce atomic Wave-2 Step-1 roadmap converting field functional spec to first live runtime signal"
Xt: "Spec is 562-line L1 (2026-04-22). Zero runtime: no schema columns, no scripts, no CIEU events. Leo bg on patent Merkle sealing wire-up."
U: "Read spec + 3 audits + CIEU schema; design smallest vertical cut; write roadmap"
Yt_plus_1: "Roadmap with dependency graph, file breakdown, conflict check, verification plan"
Rt_plus_1: "0 — roadmap complete, single failure mode selected, verification SQL provided"
author: "Jordan Lee (eng-governance)"
date: "2026-04-23"
tool_uses_self_count: 12
---

# Wave-2 Step-1 Roadmap — Field Functional First Runtime Signal

## 1. Design Summary

The field functional converts Y\*gov's mission alignment from narrative to structure. Today, every 5-tuple's Y\* is free text -- an agent writes "M-2 governability" but nothing enforces that the claim maps back to the M Triangle. The xi field (Section 2.3 of spec) assigns each state X a local Y\*(X) vector; the Phi_t functor (Section 2.2) projects ultimate mission M into task-level Y\*_t and must be invertible (pushback to at least one M component); the gradient gives the next-U direction; the attractor basin is where R_{t+1} converges to 0. Five failure modes (F1 Goodhart gaming, F2 self-audit paradox, F3 validator capture, F4 layer collapse, F5 cognitive capture) protect against the field itself becoming a governance liability. What this answers that CROBA/OmissionEngine/IntentContract cannot: "Is this agent's stated Y\* structurally traceable to the company mission, or is it post-hoc rationalization?" Current engines enforce behavioral compliance (don't do X, must do Y). The field enforces mission-level alignment -- compliant behavior that pulls M nowhere is still a gap.

## 2. Spec-to-Runtime Dependency Graph

```
L1: ALTER TABLE cieu_events ADD COLUMN m_functor TEXT
    ADD COLUMN m_weight REAL DEFAULT 0
    ADD COLUMN y_star_validator_pass INTEGER DEFAULT 0
    (schema migration -- kernel/platform owns DB)
        |
        v
L2: emit_cieu() in _cieu_helpers.py gains m_functor kwarg
    (kernel -- wire kwargs to INSERT columns)
        |
        v
L3: forget_guard rule y_star_no_m_functor (YAML rule, governance)
    triggers: content contains Y*: but missing m_functor tag
    action: deny with recipe
        |
        v
L4: y_star_field_validator.py (governance)
    reads m_functor + task_description from CIEU row
    validates: m_functor in whitelist AND required keywords present
    writes y_star_validator_pass = 1 (valid) or -1 (wishful) back to row
        |
        v
L5+: gradient, visualizer, metacognition, red team (later layers)
```

Step-1 scope: L1 + L2 + L4 (schema + emit wiring + validator). L3 (forget_guard deny rule) is deferred to Step-1b because enforcing denial before the team has practice writing m_functor will produce high false-deny rate. Step-1 produces signal (validator marks events valid/wishful) without blocking work.

## 3. Atomic Step-1 Slice — Failure Mode F1 (Goodhart's Law)

I select **F1 (Goodhart gaming)** as the first failure mode to detect. Rationale:

- F1 is the highest-probability failure in production today. Agents already write narrative Y\* tags in 5-tuples. When m_functor becomes a schema field, the path of least resistance is to stamp "M-2" on everything without semantic grounding. F1 detection catches exactly this.
- F1 is implementable with pure deterministic rules (spec Section 11.2 mandates no LLM judge). The validator checks: does the task_description contain at least one keyword from the M-axis keyword set corresponding to the claimed m_functor? If not, the m_functor is Goodhart gaming -- the label claims M alignment but the content has no lexical trace.
- F2 (self-audit paradox) requires writer/judge/enforcer separation architecture -- structurally more complex. F3 (capture) requires adversarial injection daemon. F4 (layer collapse) requires shadow audit log. F5 (cognitive capture) requires metacognition probes. All are heavier lifts.
- F1 detection produces the clearest empirical signal: a SQL query showing "X% of m_functor tags are WISHFUL (validator_pass = -1)" is immediately actionable and Board-legible.

**CIEU event_type emitted**: `Y_STAR_FIELD_VALIDATOR_PASS` (y_star_validator_pass = 1) and `Y_STAR_FIELD_VALIDATOR_WISHFUL` (y_star_validator_pass = -1). Both written as new CIEU rows referencing the original event_id.

**SQL proof-of-life query**:
```sql
SELECT y_star_validator_pass, COUNT(*) 
FROM cieu_events 
WHERE m_functor IS NOT NULL 
GROUP BY y_star_validator_pass;
```
Non-zero rows with validator_pass in {1, -1} = Step-1 LIVE.

## 4. File-Level Work Breakdown

| # | File | Action | Owner | LOC est | tool_uses est |
|---|---|---|---|---|---|
| 1 | `ystar/governance/cieu_store.py` | ALTER TABLE migration (add 3 columns: m_functor, m_weight, y_star_validator_pass) | Ryan (platform) | ~25 | 3 |
| 2 | `ystar/governance/cieu_store.py` | Update _insert_dict to write m_functor/m_weight from kwargs | Ryan (platform) | ~10 | 2 |
| 3 | `ystar/adapters/_cieu_helpers.py` or equivalent emit entry | Add m_functor, m_weight kwargs to emit_cieu signature + pass-through | Leo (kernel) | ~15 | 2 |
| 4 | `ystar/governance/y_star_field_validator.py` | NEW: M_FUNCTOR_WHITELIST, M_AXIS_KEYWORDS dict, validate_m_functor() function, batch_validate_session() | Maya (governance) | ~80 | 5 |
| 5 | `tests/test_field_validator.py` | NEW: test valid m_functor, test wishful m_functor, test missing m_functor, test unknown axis | Maya (governance) | ~60 | 3 |
| 6 | `scripts/y_star_field_validator_run.py` | NEW: CLI entry point that reads recent CIEU events and runs validator, emits result events | Maya (governance) | ~40 | 3 |

**Subtotals**: Leo 2 tu, Ryan 5 tu, Maya 11 tu. **Total: 18 tool_uses.** Under the 30 tu cap. No split needed.

Note: Jordan (domains) has no Step-1 work. Historical backfill (auto-inferring m_functor for 714K existing events) is Step-2 scope.

## 5. Conflict Check with Leo's Patent Wire-Up

Leo's current bg task (per `reports/kernel/patent_claim1_runtime_audit_20260423.md`): wire `seal_session()` call into session close path + backfill script for 714K unsealed events.

| File | Leo touches? | Step-1 touches? | Conflict? |
|---|---|---|---|
| `ystar/governance/cieu_store.py` | YES (seal_session caller addition, possibly session close hook) | YES (ALTER TABLE + _insert_dict kwargs) | **POTENTIAL** -- both modify cieu_store.py. Mitigated: Leo adds a call site for seal_session (existing function). Step-1 adds columns + modifies _insert_dict. These are non-overlapping code regions. Merge conflict risk: LOW if both use separate commits on separate line ranges. |
| `ystar/session.py` or `scripts/session_close_yml.py` | YES (session close trigger for seal_session) | NO | No conflict |
| `ystar/adapters/_cieu_helpers.py` | NO | YES (emit_cieu kwargs) | No conflict |
| DB schema (cieu_events table) | NO (sealed column already exists) | YES (3 new columns) | No conflict -- additive ALTER TABLE, sealed column untouched |
| `sealed_sessions` table | YES (new rows from seal_session) | NO | No conflict |

**Verdict**: One file overlap (cieu_store.py), zero semantic conflict. Recommend: Leo merges first (his change is smaller, ~15 LOC). Step-1 rebases after. Alternatively, concurrent branches merge cleanly since line ranges are disjoint.

## 6. Verification Plan

**SQL query (acceptance test)**:
```sql
-- After running y_star_field_validator_run.py on at least one session:
SELECT 
  y_star_validator_pass,
  COUNT(*) as cnt,
  GROUP_CONCAT(DISTINCT m_functor) as axes
FROM cieu_events 
WHERE m_functor IS NOT NULL 
  AND y_star_validator_pass != 0
GROUP BY y_star_validator_pass;
```
Expected: at least 1 row with validator_pass = 1 (valid) or -1 (wishful). Zero rows = Step-1 not producing signal.

**Live-fire scenario**: 
1. Manually emit one CIEU event with `m_functor='M-3'` and `task_description='routine maintenance cleanup'` (no M-3 keywords like customer/revenue/demo).
2. Run `y_star_field_validator_run.py`.
3. Assert the event now has `y_star_validator_pass = -1` (wishful -- F1 Goodhart detected).
4. Emit a second event with `m_functor='M-3'` and `task_description='build customer demo for enterprise pipeline'`.
5. Run validator. Assert `y_star_validator_pass = 1` (valid).

Both assertions passing = Step-1 produces non-zero F1 detection signal. CEO acceptance test complete.

---

**Recommendation**: Step-1 ready to dispatch -- estimated total 18 tool_uses, split between 3 engineers (Leo 2, Ryan 5, Maya 11), zero semantic conflict with Leo's patent wire-up (one file overlap in cieu_store.py, disjoint line ranges, merge-safe with sequenced commits).
