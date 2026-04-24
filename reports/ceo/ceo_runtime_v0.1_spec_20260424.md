---
Audience: Board (Haotian) — architectural approval before Phase 1 ship; Ethan (CTO) — Wave-2+ primary lead for runtime impl; Leo/Maya/Ryan/Jordan — subsystem owners; future CEO sessions — methodology scaffold once enforced
Research basis: Board 2026-04-24 full CEO Runtime Methodology spec (8-step Management Cycle + 7-mode detector + 3-layer Y* binder + multi-dim Rt+1); tonight's CZL termination drift lesson + U_v2 schema experiment + memory project_enforce_as_router_thesis (Board 2026-04-18); Microsoft Agent Governance Toolkit 7-component comparison (2026-04-02, reports/ceo/yggov_full_dimensional_audit_scope_20260423.md §1.55)
Synthesis: CEO Runtime 8-step Management Cycle is the SESSION-level counterpart of U_v2 ACTION-level schema. Together they form dual-scale cognitive enforcement (action scale + session scale + cross-session continuity). This upgrade transforms Y*gov from "rule-based commission governance" (Microsoft AGT tier) to "dynamic goal-tracking management runtime" (generation-ahead positioning per enforce-as-router thesis).
Purpose: (1) Empirical integration table mapping 8-step to existing mechanisms + gaps; (2) 4-layer permanence spec (schema → hook → dashboard → cross-session); (3) Ship plan sequenced with U_v2 experiment; (4) Competitive positioning as Y*gov v0.6 (v0.5 = U_v2 action-scale, v0.6 = CEO Runtime session-scale)
---

# CEO Runtime v0.1 Spec — Dynamic Management Cycle Enforcement

## 0. North-Star reframe

Traditional AI governance (Microsoft AGT tier): `rules fixed → detect violation`. Commission layer only.

Y*gov v0.6 (this spec): `goals dynamic → runtime-bind current Y* → detect whether action reduces residual`. Commission + omission + goal-alignment at management granularity.

This IS the enforce-as-router thesis (memory `project_enforce_as_router_thesis`, Board 2026-04-18) operationalized at session scale.

---

## 1. Integration table — 8-step × existing mechanisms

| 8-step cycle slot | Existing Y*gov mechanism | Integration gap + action |
|---|---|---|
| 1. Situation (mode detect) | `ecosystem_scan.py` outputs + CIEU event patterns + `gov_doctor` health | **NEW component**: `ceo_runtime_mode_detector.py` consumes above, outputs enum {Survival, Product, Engineering, Growth, Governance, Crisis, Research} with reasoning trace |
| 2. Goal Binding 3-layer | 场泛函 goal_tree (Y_001/Y_002/Y_003/... flat list, no phase scope) + M Triangle M(t) constitutional | **EXTEND goal_tree schema**: add `phase_scope: {north_star, phase, cycle}` field; North-Star = M Triangle (fixed); Phase = monthly/quarterly (editable); Cycle = per-session ephemeral (bind on boot, dissolve on close) |
| 3. Residual multi-dim | Current single `Rt+1` scalar in 5-tuple receipts | **NEW schema** (extends CZL): `rt_plus_1_dict: {product, revenue, distribution, execution, trust, architecture}` — mode determines which dimension is pri_1 |
| 4. Constraint analysis | Implicit in prompt + memory context | **NEW structured field**: `constraint_set: {time_window, cash_runway, blocker_commit, market_uncertainty, agent_failure, user_feedback_missing}` — populated before intervention choice |
| 5. Intervention Choice | CEO intuition-pick currently | **NEW scorer**: rank candidate interventions by `rt_plus_1_delta_expected / tool_uses_cost`, pick max; surface top-3 for CEO final |
| 6. Delegation | Agent tool + break_glass + must_dispatch_via_cto (partial) | **EXTEND**: add structured `delegation_rationale` field to Agent spawn (owner_role justification + permission grant + completion criteria + live-fire gate) |
| 7. Verification | Iron Rule 不信自报 + U_v2 `empirical_basis` field | **REUSE U_v2 schema directly** — no new work, just wire session-scale verification to action-scale artifacts |
| 8. State Update | WORLD_STATE.md + `session_close_yml.py` + `brain_auto_ingest` (partial) | **WIRE cycle-trigger**: state write happens at cycle close, not only session close; `brain_auto_ingest` consumes cycle Rt+1 delta as learning signal |

---

## 2. Mode detector — the missing primitive

### 7 runtime modes (from Board spec)

| Mode | Detection signals | CEO priority action |
|---|---|---|
| **Survival** | cash runway < 60d OR revenue near-zero OR existential threat | Find fastest monetization path |
| **Product** | product unclear OR MVP unvalidated OR 0 users | Compress to single-user first-success experience |
| **Engineering** | ≥1 P0 architectural blocker OR ≥5 hot regressions (tonight's state!) | Clear P0 blockers, pause growth |
| **Growth** | product live + stable + 0 distribution | SEO / build-in-public / X / PH / HN |
| **Governance** | agent team failing delegation OR omission OR evidence gap | Fix delegation + omission + verification layer |
| **Crisis** | system outage OR cascading errors OR trust loss | Stop expansion, restore trusted execution |
| **Research** | new concept needs validation | Design minimum experiment (this is what U_v2 experiment IS!) |

### Detection algorithm sketch (for `ceo_runtime_mode_detector.py`)

```python
def detect_mode() -> tuple[Mode, rationale_str]:
    signals = gather_signals()  # CIEU 24h / ecosystem_scan / gov_doctor / cash state / overdue count
    # Priority rules (first match wins):
    if signals.cascading_errors or signals.system_outage:
        return Crisis, "cascading pattern in CIEU + outage events"
    if signals.cash_runway_days < 60:
        return Survival, f"runway {days}d < 60d threshold"
    if signals.p0_blockers >= 1 or signals.regression_count >= 5:
        return Engineering, f"{p0}P0 + {regressions} regressions"
    if signals.agent_delegation_fail_rate > 0.3 or signals.omission_overdue > 10:
        return Governance, f"delegation fail {rate}% / omission queue {n}"
    ...
```

**Current tonight empirical state**: Engineering mode (92 regressions in flight + Items #4 #9 failed + shadow cleanup cascade). THIS is why we've been firefighting — mode correctly identified, just not structurally enforced.

### Empirical validation for mode detector

- Backtest against session_summary log last 30d — does detector output match what CEO actually prioritized?
- Live-fire: artificially inject mode-switch signal (e.g. mock cash < 60d) → detector flips + CIEU event emit

---

## 3. 4-layer permanence spec

### Layer A — Schema (structure to enforce)

**File**: `Y-star-gov/governance/schemas/ceo_runtime_cycle_schema_v0.1.yaml`

```yaml
required_fields:
  situation:
    mode: enum [Survival, Product, Engineering, Growth, Governance, Crisis, Research]
    mode_rationale: str (min_length: 50)
    signals_consulted: list of evidence refs
  goal_binding:
    north_star: "M(t) = ..."  # fixed (loads from constitutional)
    phase_y_star: str + phase_scope date range
    cycle_y_star: str (session-specific, ephemeral)
  residual_diag:
    rt_plus_1_dict:
      product: {gap: str, metric: str|null}
      revenue: {...}
      distribution: {...}
      execution: {...}
      trust: {...}
      architecture: {...}
    top_residual_dimension: enum (mode-appropriate)
  constraint_analysis:
    active_constraints: list from 6-constraint vocabulary
    hardest_constraint: str + justification
  intervention_choice:
    candidates: list (≥2 options, forcing real comparison not single-pick)
    chosen: str
    chosen_rationale: str (why this beats other candidates on rt_plus_1_delta/tu_cost)
  delegation:
    owner_role: str
    permission_grant: path_allowlist
    completion_criteria: str
    live_fire_gate: str  # specific deliberate-violation test
  verification:
    empirical_basis: list (same schema as U_v2 empirical_basis field)
    rt_plus_1_actual_post: {dict same shape as residual_diag}
  state_update:
    world_state_delta: str
    memory_lesson: path (if new lesson)
    baseline_updated: bool
```

### Layer B — Hook runtime enforce

**File**: `scripts/hook_stop_ceo_cycle_check.py` (new) OR extend existing stop_hook

```
Trigger: Stop event on CEO reply → scan reply text for "Board:" or "老大" addressing
Action:
  - parse YAML frontmatter of reply
  - validate against ceo_runtime_cycle_schema_v0.1
  - missing field → DENY + REDIRECT recipe per schema
  - emit CIEU event:
    - CEO_RUNTIME_CYCLE_COMPLETE (success)
    - CEO_RUNTIME_SCHEMA_INCOMPLETE_DENY
    - CEO_RUNTIME_THEATER_DETECTED (field present but artifact ref empty)
  - break-glass: ≥3 consecutive DENY in 5min → escalate to Board (audit log entry)
```

### Layer C — Mode-aware dashboard (default component)

**File**: `scripts/ceo_runtime_dashboard.py` + auto-invoke on `governance_boot.sh ceo`

Output sample (replaces "10 fixed fields" checklist):

```
=== CEO RUNTIME v0.1 — 2026-04-24T15:30Z ===

MODE: Engineering
  Rationale: 92 Y-star-gov pytest regressions + 2 Wave-1 items failed + 27 dispatch_board overdue
  Transitioned from: Governance (2026-04-23 night, hook deadlock incident)

Y* BINDING:
  North-Star: M(t) = 证明 AI agent team can autonomously run real company with real value
  Phase (2026-04 month): Enforce-as-Router migration Phase 2 + Guard+Guide framework ship
  Cycle (this session): Wave-1.5 ship + U_v2 experiment Phase 1 start + regression triage

RT+1 MULTI-DIM:
  [TOP] architecture: 92 regressions in Y-star-gov pytest + shadow dir cascade unverified
  [P1] execution: 9/27 overdue still need Agent-spawn; subscriber broken
  [P1] trust: wave-1 Item #9 break-glass feature L2 not L4
  [P2] product: gov-mcp pypi未deploy (60h overdue)
  [P2] revenue: gov-mcp卖线deferred
  [P2] distribution: Sofia blog待写

CONSTRAINTS:
  [HARDEST] cognitive_budget_depletion — session 跑 ~180 tu+, 5 Board catches tonight, regression pattern
  time_window: session_length_soft_cap (~250 tu est)
  agent_failure: subscriber can't Agent-spawn (structural Claude Code limit)

CANDIDATE INTERVENTIONS (ranked):
  1. Dispatch 5 parallel engineers close Rt+1 items NOW
     expected_delta: -40% on architecture + execution + trust
     cost: ~100 tu
     score: 0.4
  2. Session checkpoint + handoff for next session
     expected_delta: 0 (defers residual)
     cost: 10 tu  
     score: 0 (Board just caught this pattern as CZL drift!)
  3. Build CEO Runtime v0.1 implementation (this doc's Phase 1)
     expected_delta: long-term -60% regression rate via schema
     cost: ~80 tu
     score: long-term high, short-term 0

RECOMMENDED: (1) + (3) parallel (1 for immediate Rt+1, 3 for永固 mechanism)

DELEGATION READY: Ethan (92 triage) / Maya (Item #4 + czl_termination_drift rule) / Leo (Item #9 + U_v2 validator) / Ryan (U_v2 instrument) — all spawned 2026-04-24 mid-session
```

### Layer D — Cross-session continuity

**File extension**: `scripts/session_close_yml.py` + `governance_boot.sh`

- session_close writes: `exit_mode`, `phase_y_star_current`, `rt_plus_1_snapshot`
- governance_boot reads exit_mode first thing, detects transition:
  - Same mode → resume same intervention priority (don't re-diagnose)
  - Mode changed → re-run mode detector, re-bind cycle Y*
- Guards against "new session starts from blank, ignores last session residual" anti-pattern

---

## 4. Ship plan — sequenced with U_v2 experiment

**Wave-2a** (depends on Wave-1.5 close + 5 engineers returning):
- Leo: U_v2 validator v0.1 (already dispatched tonight)
- Ryan: U_v2 instrument (already dispatched tonight)
- Maya: czl_termination_drift hook rule (already dispatched tonight)

**Wave-2b** (builds on 2a):
- Ethan orchestrate: draft `ceo_runtime_cycle_schema_v0.1.yaml` + validator (mirrors U_v2 pattern)
- Jordan: mode_detector signal vocabulary + backtest harness (against 30d session_summary)
- Maya: hook_stop_ceo_cycle_check.py wire + live-fire test

**Wave-2c**:
- Ryan: ceo_runtime_dashboard.py + governance_boot.sh integration
- Leo: session_close_yml extension + boot transition detect

**Wave-2d** (empirical validation):
- 4-phase experiment (mirror U_v2 protocol): schema → A/B → persistence → cross-session + theater
- Pre-registered H1: ceo_runtime_schema 使 mode_detection accuracy ≥0.9 + cycle_completion ≥0.85 + cross-session transition_correctness ≥0.9 (vs ~unmeasured baseline)

---

## 5. Competitive positioning — Y*gov v0.6

| Layer | Y*gov v0.4 (today) | Y*gov v0.5 (U_v2 shipping) | Y*gov v0.6 (this spec) | Microsoft AGT |
|---|---|---|---|---|
| Action scale | forget_guard + boundary_enforcer (rule engine) | **U_v2 schema on every tool call** | same | policy engine亚毫秒 |
| Session scale | implicit (prose advisory) | same | **CEO Runtime 8-step cycle enforced** | ABSENT |
| Cross-session | session_close_yml (partial) | same | **mode transition + phase Y* continuity** | ABSENT |
| Mode-awareness | none (static "P0 top priority" list) | none | **7-mode detector + mode-specific intervention ranking** | ABSENT |
| Goal dynamics | flat goal_tree | same | **3-layer Y* (North-Star + Phase + Cycle) binding** | ABSENT |
| Omission | OmissionEngine (partial) | same | **residual multi-dim auto-fires per mode** | ABSENT |

**Generation-ahead claim** (provable): Microsoft AGT is commission-layer policy engine. Y*gov v0.6 is **management runtime** — operates on goals, modes, residuals, interventions, not just actions. Dogfood evidence: tonight's session itself is Engineering-mode firefight; CEO Runtime would have forced mode detection at session boot → different prioritization from the start.

---

## 6. 诚实 reservations (P-14)

1. **Overhead risk**: session-scale schema adds ~500-1000 tokens per Board reply. Most Board interactions don't need full 8-step — need tiered (short reply / major decision / strategy review 3 tiers).
2. **Mode detector accuracy unknown**: no backtest yet. Could misclassify, sending CEO down wrong priority. Mitigation: phase-gate ship with human-in-loop verify initially.
3. **Integration with tonight's regression pile**: if we ship runtime too fast, might add layers on unstable base. Proper sequence: close Wave-1.5 Rt+1 FIRST (92 regression triage), THEN layer v0.6.
4. **Schema theater risk**: same as U_v2 — agent rubber-stamp fields. Must have theater detection.
5. **Board intervention still load-bearing**: this spec reduces CEO regression frequency but doesn't eliminate. Board-in-loop remains until compound rate empirically ≥ 95% methodology-applied across 3+ sessions.

---

## 7. Integration with tonight's in-flight work

- 5 engineers already running Wave-1.5+2 tonight (Ethan regression triage / Maya Item #4 + czl_termination_drift rule / Leo Item #9 + U_v2 validator / Ryan U_v2 instrument + orchestrator).
- They return → Wave-2b starts with this spec as methodology scaffold.
- czl_termination_drift rule (Maya in flight) is a concrete precursor of ceo_runtime_cycle_enforce — both stop-hook pattern enforce on CEO reply.
- U_v2 schema (Leo validator + Ryan instrument in flight) is the action-scale half of this dual-scale design.

Session coherent: tonight's work naturally extends into Wave-2b without re-architecture. The 3 docs (lesson + U_v2 schema + this CEO Runtime spec) form a triangle — lesson identifies the pattern, U_v2 enforces at action scale, CEO Runtime enforces at session scale.

---

## 8. 立等 Ethan peer review

本 spec CEO authored, Ethan Wave-2 kickoff 首 task = peer review + Phase 1 spec finalize + dispatch subsystem owners. 不 propose — 已 committed as Wave-2 primary scope.
