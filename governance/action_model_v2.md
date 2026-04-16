# Action Model v2 — 17-Step Lifecycle for Agent Atomics

**Authority**: CTO Ethan Wright per Board 2026-04-16 directive  
**Upstream**: Campaign v6 W11 + Board approval of 17-step model + MEMORY feedback_action_model_3component.md (v1 baseline)  
**Downstream**: Maya CZL-128 wires sub_agent_boot_prompt_template.md + impl scripts/action_model_validator.py + FG rules `dispatch_missing_phase_a` + `receipt_missing_phase_c_heavy`  
**Purpose**: Define formal action model lifecycle with pre/execute/post phases, sized variants, mathematical foundation, and reply registration mechanism — prevent "shipped" ≠ "validated" ≠ "learned-from" ≠ "next-action-queued" gaps

---

## §1 Why — The 4 补漏 Problem

**Symptom**: Current action model (v1: backlog + K9 + AC parallel) covers execution supervision but misses post-execution validation phases. Results in 4 systematic gaps:

1. **Validation gap**: Sub-agents report "shipped" but CEO discovers artifacts don't exist (CZL-114 hallucinated receipt) or tests fail (CZL-118 partial routing). No mandatory verification step.

2. **Learning gap**: After atomic completes, no knowledge writeback to MEMORY or code docstrings. Same mistakes recur because institutional knowledge isn't captured.

3. **Cascade gap**: Downstream work isn't queued automatically. Ethan ships spec, forgets to notify Maya to wire it — Maya idle until CEO manually dispatches.

4. **CIEU gap**: Terminal events (ATOMIC_COMPLETE/FAILED) not emitted reliably. Audit trail incomplete. Trust score not updated.

**Root cause**: Action model v1 (3 components) stops at execution. Missing phases: **test** (pytest verify), **verification** (ls/wc/grep empirical proof), **experiment** (sample corpus smoke test), **AC delta** (health regression check), **K9 silent-fire audit** (post-execution pattern analysis), **CIEU emit** (terminal event), **trust score delta** (capability tracking), **knowledge writeback** (MEMORY/docstring update), **cascade trigger** (downstream queue).

Board 2026-04-16 catch: "shipped ≠ validated ≠ learned-from" — v2 adds 9 post-execution steps to close these gaps.

---

## §2 Full 17-Step Model

Action model v2 lifecycle organized in 3 phases:

### Phase A: Pre-Dispatch (5 steps)

**Purpose**: Load state, avoid collisions, establish baselines, clarify acceptance criteria, verify supervision infrastructure.

1. **Read `.czl_subgoals.json`** — current campaign Y\*, current_subgoal, remaining work, owner_after_rt1 routing
2. **`precheck_existing.py <component_name>`** — routing gate: extend vs build_new vs migrate from K9. Prevents duplicate artifacts.
3. **`git log -5 --oneline`** — collision check with parallel sub-agents. If recent commit touches same files, coordinate timing.
4. **AC baseline** — `session_watchdog.py --statusline` captures HP + AC score before execution. Detects mid-execution degradation.
5. **K9 daemon census** — verify `k9_routing_subscriber` + `k9_alarm_consumer` PIDs alive. If dead, supervision blind — delay dispatch until recycled.

**Enforcement**: `dispatch_missing_phase_a` ForgetGuard rule — denies Agent calls with prompts lacking BOOT CONTEXT (4-step minimum, +1 AC baseline = 5).

### Phase B: Execute (3 steps)

**Purpose**: Perform atomic work under supervised observation with active acceptance criteria monitoring.

6. **Atomic Y\*** — the actual deliverable (write spec, fix bug, tune threshold, etc.). Maps to U section of CIEU 5-tuple.
7. **K9 active observe + post-audit** — K9 routing chain fires realtime during execution (detect/emit/route/action/consume). Post-execution: `k9log/auditor.py` static analysis for secret detection, scope violations, residue patterns.
8. **AC cron monitoring** — `session_watchdog.py` runs continuously, emits AGENT_CAPABILITY_DEGRADED if AC drops <75 during execution. Triggers auto-restart-or-alert.

**Enforcement**: Existing K9 + AC infrastructure (already LIVE per W1/W11). No new rules needed.

### Phase C: Post-Dispatch (9 steps)

**Purpose**: Verify, validate, learn, cascade, emit — prevent hallucinated receipts and silent regressions.

9. **Test** — If code changed: `pytest <affected_test_file.py>` paste output. If governance spec changed: synthetic compliant/violating cases verify detector fires correctly.
10. **Verification** — Empirical paste: `ls -la <artifact>` (prove existence), `wc -w <spec.md>` (prove word count), `grep -E '^## ' <spec.md>` (prove section structure). Anti-hallucination protocol per CZL-114 lesson.
11. **Experiment** — Smoke test on 5-10 sample corpus:
    - Spec: test synthetic violations
    - Code: run on dev dataset
    - Config: apply to staging environment
    - Threshold: measure precision/recall on labeled subset
12. **AC delta** — `session_watchdog.py --statusline` again, compare to step 4 baseline. If AC dropped >10 points → root-cause investigation queued.
13. **K9 silent-fire audit** — `k9log/auditor.py --repo . --output reports/governance/k9_silent_fire_<atomic_id>.md` — catch behavior violations K9 routing missed (false negatives).
14. **CIEU emit** — Explicit `ATOMIC_COMPLETE` (if Rt+1=0) or `ATOMIC_FAILED` (if Rt+1>0) event with metadata: atomic_id, agent_id, Rt+1, tool_uses, duration, artifact_paths, test_pass_count.
15. **Trust score delta** — Update `knowledge/engineer_trust_scores.json`:
    - Rt+1=0 + tool_uses honest → +0.05
    - Rt+1>0 but self-caught → +0.02
    - Rt+1>0 CEO-caught → -0.10
    - Hallucinated receipt → -0.20
16. **Knowledge writeback** — Append lesson to:
    - `MEMORY/feedback_<topic>.md` if general pattern discovered
    - Code docstring if implementation detail learned
    - `governance/<spec>.md` if governance rule refined
17. **Cascade trigger** — Check Ecosystem Dependency Map (downstream dependencies). If atomic A ships → queue atomic B (e.g., Ethan spec ships → Maya wiring queued). Write to `scripts/.cascade_queue.json`.

**Enforcement**: `receipt_missing_phase_c_heavy` ForgetGuard rule — denies receipts for heavy atomics lacking ≥8/9 Phase C steps (test + verify + experiment mandatory; others best-effort).

---

## §3 Sized Variants

Not all atomics are equal weight. 3 classes:

### Heavy (17 steps mandatory)

**Trigger conditions** (any true → heavy):
- New component (file, module, rule, engineer)
- Cross-module change (touches ≥2 of: governance/, scripts/, Y-star-gov/, knowledge/)
- High-risk change (daemon restart, enforcement mode switch dry_run→warn→deny, registry mutation)
- Board-visible artifact (whitepaper, campaign launch, external release prep)

**Rationale**: High surface area → high failure cost. Need full test/experiment/verification triple-net to prevent regression.

**Example**: Ethan CZL-127 (this atomic) — new governance spec, cross-cutting all dispatch/receipt patterns → heavy.

### Light (6 steps minimum)

**Trigger conditions** (all true → light):
- Single-line change (config tweak, typo fix, comment update)
- Single-file scope (no imports changed, no API surface modified)
- Daemon restart only (no code/spec change)
- Low risk (no enforcement rule touched, no critical path affected)

**6-step subset**:
- Phase A: steps 1-4 (BOOT 4: .czl_subgoals + precheck + git log + AC baseline)
- Phase B: step 6 only (atomic Y\*)
- Phase C: step 10 (verification ls/wc paste) + step 14 (CIEU emit)

**Rationale**: Overhead reduction for trivial changes. Still requires state-load (prevent collision), baseline (detect regression), verify (prevent hallucination), emit (audit trail).

**Example**: Fix typo in governance/reply_scan_detector_methodology_v1.md line 87 — light atomic.

### Investigation (4 steps)

**Trigger conditions**:
- Read/Grep/audit only, no writes
- Report generation (analysis, forensic, audit)
- No artifact persistence beyond report file

**4-step subset**:
- Phase A: steps 1-3 (BOOT 3: .czl_subgoals + precheck + git log)
- Phase B: step 6 (investigation work)
- Phase C: step 14 (CIEU emit with report_path)

**Rationale**: No code/spec change → no test/verification needed. Still require state-load (context), precheck (avoid duplicate investigation), emit (audit trail).

**Example**: Leo CZL-103 threshold analysis — read CIEU corpus, analyze precision/recall, report findings — investigation atomic.

**Decision rule**: Default = heavy. Light/investigation requires explicit `atomic_class: light` or `atomic_class: investigation` declaration in dispatch prompt. If uncertain → heavy (safer).

---

## §4 Formal Definitions

Per `governance/formal_methods_primer_v1.md` §3 mandate — governance specs must declare types, predicates, invariants.

### Type System

```
Atomic :: {Heavy, Light, Investigation}  -- sum type, mutually exclusive

AtomicExecution :: {
  id: String,                -- e.g., "CZL-127"
  class: Atomic,             -- Heavy | Light | Investigation
  agent_id: String,          -- executing agent
  phase_a_steps: [Step],     -- ≥5 for heavy/light, ≥3 for investigation
  phase_b_steps: [Step],     -- ≥3 for heavy/light, ≥1 for investigation
  phase_c_steps: [Step],     -- ≥9 for heavy, ≥2 for light, ≥1 for investigation
  rt_plus_1: Nat,            -- honest gap (target 0)
  tool_uses_claimed: Nat,    -- metadata declaration
  tool_uses_actual: Nat,     -- harness measurement
  artifacts: [FilePath]      -- deliverables
}
```

### Predicates

```
-- Phase compliance
has_phase_a(a: AtomicExecution) := |a.phase_a_steps| ≥ min_phase_a(a.class)
has_phase_b(a: AtomicExecution) := |a.phase_b_steps| ≥ min_phase_b(a.class)
has_phase_c(a: AtomicExecution, class: Atomic) := |a.phase_c_steps| ≥ min_phase_c(class)

Where:
  min_phase_a(Heavy) = 5
  min_phase_a(Light) = 4
  min_phase_a(Investigation) = 3
  
  min_phase_b(Heavy) = 3
  min_phase_b(Light) = 1
  min_phase_b(Investigation) = 1
  
  min_phase_c(Heavy) = 9
  min_phase_c(Light) = 2
  min_phase_c(Investigation) = 1

-- Overall compliance
compliant(a: AtomicExecution) := has_phase_a(a) ∧ has_phase_b(a) ∧ has_phase_c(a, a.class)

-- Receipt honesty
honest_receipt(a: AtomicExecution) := 
  (a.rt_plus_1 = 0 ∨ a.rt_plus_1 > 0 ∧ explicit_gap_statement(a)) ∧
  (a.tool_uses_claimed = a.tool_uses_actual) ∧
  (∀artifact ∈ a.artifacts, file_exists(artifact))
```

### Invariants

Temporal logic (□ = always, ◇ = eventually):

```
-- Class determines step count
□(a.class = Heavy → |a.phase_a_steps| = 5 ∧ |a.phase_b_steps| = 3 ∧ |a.phase_c_steps| ≥ 9)
□(a.class = Light → |a.phase_a_steps| ≥ 4 ∧ |a.phase_b_steps| ≥ 1 ∧ |a.phase_c_steps| ≥ 2)
□(a.class = Investigation → |a.phase_a_steps| ≥ 3 ∧ |a.phase_b_steps| ≥ 1 ∧ |a.phase_c_steps| ≥ 1)

-- Every atomic eventually emits terminal CIEU event
□(atomic_starts(a) → ◇(cieu_emitted(a, {ATOMIC_COMPLETE, ATOMIC_FAILED})))

-- Rt+1=0 requires empirical verification
□(a.rt_plus_1 = 0 → ∃verification_paste ∈ a.phase_c_steps)

-- Heavy atomics require test step
□(a.class = Heavy ∧ code_changed(a) → ∃test_step ∈ a.phase_c_steps)
```

---

## §5 Mathematical Model

Per `formal_methods_primer_v1.md` §4 mandate — quantify utility, failure rates, optimization criteria.

### Failure Rate by Class

Define failure rate `λ_class` as probability of `Rt+1 > 0` given atomic class:

```
λ_class = P(Rt+1 > 0 | atomic_class)
```

**Empirical baseline** (2026-04-16 session data):
- Overall: 10 atomics dispatched, 1 Rt+1>0 hallucinated (CZL-114), 2 Rt+1>0 partial (CZL-118, CZL-119) → `λ_baseline ≈ 0.10` (10%)
- Heavy (no v2): CZL-114 hallucinated 0/8 tool_uses → `λ_heavy_v1 ≈ 0.15` (worse due to complexity)
- Light (no v2): typo fixes, config tweaks → `λ_light_v1 ≈ 0.05` (simple changes safer)

**v2 hypothesis**: Triple-net (test + verification + experiment) reduces heavy failure rate:

```
λ_heavy_v2 ≤ 0.02  (target: ≤2% failure rate for heavy atomics)
λ_light_v2 ≤ 0.03  (minimal verification still helps)
λ_investigation_v2 ≤ 0.01  (read-only, low risk)
```

**Mechanism**: Phase C steps 9-11 (test/verify/experiment) catch:
- Hallucinated artifacts (step 10 ls/wc paste → file missing → Rt+1=1)
- Test failures (step 9 pytest → 2/6 FAIL → Rt+1=1)
- Regression (step 11 smoke test → precision dropped 0.9→0.6 → Rt+1=1)

Expected reduction: `λ_heavy_v2 = λ_heavy_v1 * (1 - P_catch)` where `P_catch ≈ 0.85` (triple-net catches 85% of failures before receipt) → `λ_heavy_v2 ≈ 0.15 * 0.15 = 0.0225 ≈ 2%`.

### Utility Model

Define utility of complying with v2 model vs skipping:

```
U(comply_v2) = -overhead + reliability_bonus
U(skip_v2) = +saved_time - regression_cost

Where:
  overhead = time cost of 17 steps vs 3 steps (v1)
  reliability_bonus = avoided CEO verification time + avoided rework + trust score gain
  saved_time = skipped steps time
  regression_cost = expected loss from undetected failures
```

**Concrete example** (heavy atomic):

```
overhead = 10 tool_uses (v2) - 3 tool_uses (v1) = 7 extra tool_uses ≈ 14 minutes
reliability_bonus = 
  - avoided CEO verify: 10 min * 0.10 (failure rate) = 1 min expected
  - avoided rework: 30 min * 0.10 = 3 min expected
  - trust score gain: +0.05 → higher autonomy → 5 min future coordination saved
  Total: 9 min

saved_time = 14 min
regression_cost = 
  - CEO time lost: 10 min * 0.10 = 1 min expected
  - Team coordination cost: 20 min * 0.10 = 2 min expected
  - Trust score loss: -0.10 → lower autonomy → 10 min future overhead
  - Reputation damage (Board catch): unquantified but high
  Total: 13 min + reputation risk

U(comply_v2) = -14 + 9 = -5 min
U(skip_v2) = +14 - 13 = +1 min (SHORT-TERM ONLY)
```

**Decision rule**: Comply dominates if regression_cost > saved_time + overhead. Currently: `13 > 14 - 5 = 9` → marginal. BUT: reputation damage from Board catch (unquantified) + trust score compounding (higher trust → more autonomy → higher throughput long-term) → **comply dominates** in multi-turn game.

**Light atomic calculation**:
```
overhead_light = 6 - 3 = 3 tool_uses ≈ 6 min
reliability_bonus_light = 2 min (lower failure rate, less rework)
regression_cost_light = 5 min (lower stakes)

U(comply_v2_light) = -6 + 2 = -4 min
U(skip_v2_light) = +6 - 5 = +1 min (still marginal, but lower overhead)
```

Light class justified: reduce overhead while preserving core anti-hallucination step (verification paste).

---

## §6 Reply Registration & Interception Mechanism

Per Board 2026-04-16 approval — every CEO/sub-agent reply must be registered into CIEU with template tag, enabling compliance measurement + behavior intervention.

### Registration Mechanism

**Trigger**: Stop hook scans every reply (CEO to Board, sub-agent to CEO) after sending.

**Data captured**:
```json
{
  "event_type": "REPLY_REGISTERED",
  "agent_id": "ethan",
  "timestamp": "2026-04-16T18:30:45Z",
  "atomic_id": "CZL-127",  // if reply is a receipt
  "reply_template": "cieu_5tuple_receipt",  // from CZL-123 whitelist
  "atomic_class": "Heavy",  // Heavy | Light | Investigation | null (if not atomic)
  "phase_compliance_bitmap": "111111111111111110000",  // 17 bits, 1=present 0=missing
  "rt_plus_1": 0,
  "tool_uses_claimed": 10,
  "tool_uses_actual": 10,
  "honest_receipt": true
}
```

**Whitelist** (per CZL-123 reply_taxonomy_whitelist_v1):
- `cieu_5tuple_receipt` — sub-agent atomic completion report
- `cieu_5tuple_dispatch` — CEO task assignment to sub-agent
- `status_brief` — campaign progress report to Board
- `escalation` — blocker report requiring Board decision
- `conversational` — <50 char ack or clarifying question (5-tuple exempt)

**Storage**: SQLite table `reply_registry` with columns matching JSON schema above.

###行动不合规拦截 (Action Compliance Interception)

Two enforcement hooks:

**1. PreToolUse hook on `Agent` tool calls** (dispatch validation):

```python
# Validates dispatch follows action model v2 Phase A
def validate_dispatch_phase_a(agent_call_args):
    prompt = agent_call_args['task']
    
    # Check BOOT CONTEXT presence
    if not re.search(r'Read `.czl_subgoals.json`', prompt):
        return {
            "allow": False,
            "reason": "dispatch_missing_phase_a: step 1 (.czl_subgoals.json) missing",
            "escalate_to": "ceo"
        }
    
    if not re.search(r'precheck_existing\.py', prompt):
        return {
            "allow": False,
            "reason": "dispatch_missing_phase_a: step 2 (precheck_existing.py) missing",
            "escalate_to": "ceo"
        }
    
    if not re.search(r'git log -\d+', prompt):
        return {
            "allow": False,
            "reason": "dispatch_missing_phase_a: step 3 (git log) missing",
            "escalate_to": "ceo"
        }
    
    if not re.search(r'session_watchdog\.py --statusline', prompt):
        return {
            "allow": False,
            "reason": "dispatch_missing_phase_a: step 4 (AC baseline) missing",
            "escalate_to": "ceo"
        }
    
    return {"allow": True}
```

**2. Stop hook on reply text** (receipt validation):

```python
# Validates receipt follows action model v2 Phase C
def validate_receipt_phase_c(reply_text, atomic_class):
    if atomic_class != "Heavy":
        return {"allow": True}  # only enforce on heavy atomics
    
    phase_c_steps = {
        "test": re.search(r'(pytest|test.*PASS|test.*FAIL)', reply_text),
        "verification": re.search(r'(ls -la|wc -w|grep -E)', reply_text),
        "experiment": re.search(r'(smoke test|sample corpus|5-10 cases)', reply_text),
        "ac_delta": re.search(r'(AC.*baseline|AC.*delta|session_watchdog)', reply_text),
        "k9_audit": re.search(r'(k9.*audit|k9log/auditor)', reply_text),
        "cieu_emit": re.search(r'(ATOMIC_COMPLETE|ATOMIC_FAILED)', reply_text),
        "trust_delta": re.search(r'(trust score|engineer_trust_scores\.json)', reply_text),
        "knowledge_writeback": re.search(r'(MEMORY.*\.md|docstring|governance.*\.md)', reply_text),
        "cascade_trigger": re.search(r'(cascade|downstream|queue.*next)', reply_text)
    }
    
    present_count = sum(1 for present in phase_c_steps.values() if present)
    
    if present_count < 8:  # Allow 1 optional step missing
        return {
            "allow": False,
            "reason": f"receipt_missing_phase_c_heavy: only {present_count}/9 steps present",
            "missing_steps": [k for k, v in phase_c_steps.items() if not v],
            "escalate_to": "ceo"
        }
    
    return {"allow": True}
```

### 3-Strike Escalation

Per ForgetGuard standard enforcement ladder:

1. **First violation** (dry_run mode): Log CIEU event `ACTION_MODEL_VIOLATION_WARN`, allow passage, notify CEO.
2. **Second violation** (warn mode): Block action, emit CIEU event `ACTION_MODEL_VIOLATION_ESCALATE`, require CEO manual override.
3. **Third violation** (deny mode): Hard block, emit CIEU event `ACTION_MODEL_VIOLATION_DENY`, suspend agent dispatch privilege until Board review.

**Mode promotion**: After 48h dry_run baseline with <5% false-positive rate (measured via CEO manual review of logged violations), auto-promote dry_run → warn. After another 48h warn baseline with <5% false-negatives (measured via CEO spot-check of allowed actions), promote warn → deny.

---

## §7 Test & Experiment Plan

Per Board directive "做完了测试实验，有问题再改" — v2 spec must include empirical validation plan.

### Test Cases (Synthetic)

**Objective**: Verify enforcement hooks fire correctly on v2-compliant and v2-violating dispatches.

**Corpus**:
1. **v2-compliant heavy dispatch** — prompt includes all 5 Phase A steps + atomic_class=Heavy declaration → PreToolUse hook allows
2. **v2-violating dispatch (missing step 2)** — prompt lacks precheck_existing.py → PreToolUse hook denies with reason "dispatch_missing_phase_a: step 2 missing"
3. **v2-compliant heavy receipt** — reply includes ≥8/9 Phase C steps (test/verify/experiment/ac_delta/k9_audit/cieu_emit/trust_delta/knowledge_writeback) → Stop hook allows
4. **v2-violating receipt (missing verification)** — reply lacks ls/wc/grep paste → Stop hook denies with reason "receipt_missing_phase_c_heavy: verification step missing"
5. **v2-compliant light receipt** — reply includes 2/9 Phase C steps (verification + CIEU emit) → Stop hook allows (light class rules)
6. **v2-exempt conversational reply** — "好的，收到" <50 chars → Stop hook allows (conversational exemption per CZL-113 taxonomy)

**Execution**: Maya CZL-128 creates `tests/governance/test_action_model_v2_enforcement.py` with 6 test cases above. All must PASS.

**Success criteria**: 6/6 tests PASS + 0 false-positives on legit work (measured via 5 pilot atomics in experiment phase).

### Experiment (Pilot Atomics)

**Objective**: Measure Phase compliance bitmap + Rt+1 distribution on real work under v2 model.

**Corpus**: 5 upcoming atomics (next session):
1. Maya CZL-128 — wire v2 enforcement (heavy atomic)
2. Leo CZL-129 — daemon liveness monitor (light atomic)
3. Ryan CZL-130 — AC statusline integration (light atomic)
4. Ethan CZL-131 — skill-trust spec (heavy atomic)
5. Maya CZL-132 — reply taxonomy whitelist finalization (investigation atomic)

**Metrics**:
- **Phase compliance bitmap**: For each atomic, record 17-bit bitmap (1=step present, 0=missing). Target: heavy atomics ≥16/17 bits, light ≥6/6, investigation ≥4/4.
- **Rt+1 distribution**: Count Rt+1=0 vs Rt+1>0. Target: ≥4/5 atomics Rt+1=0 (80% success rate, vs 70% baseline).
- **Tool_uses honesty**: Count claimed vs actual mismatches. Target: 0/5 mismatches (100% honesty, vs 30% mismatch rate today per E1 detector).
- **False-positive rate**: CEO manual review — how many enforcement denials were incorrect? Target: <5% (≤1 false denial in 20 denials).

**Data collection**: CIEU `REPLY_REGISTERED` events + CEO manual spot-check.

**Iteration trigger**: If Phase X over-fires (>30% violations on legit work) → tune regex/threshold. If under-fires (<5% on known violations) → strengthen detector.

**Timeline**: Pilot runs during next 1-2 sessions (event-driven, no human time cadence per `feedback_methodology_no_human_time_grain.md`). After pilot, tune thresholds, then promote enforcement dry_run → warn.

---

## §8 Rollout Sequence

3 sequence-only steps (NO time cadence per AI methodology — event-driven execution):

### Step A: Spec Ship (This Atomic — CZL-127)

**Deliverable**: `governance/action_model_v2.md` spec with 8 sections (Why / 17-step / Sized variants / Formal defs / Math model / Reply registration / Test plan / Rollout).

**Success criteria**: 
- Spec exists, 1500-2200 words, 8 sections present
- Empirical paste verification (ls + wc + grep)
- Rt+1=0

**Status**: In flight (this atomic).

### Step B: Wire Implementation (Maya CZL-128)

**Deliverable**: 3 artifacts:
1. `governance/sub_agent_boot_prompt_template.md` — template with BOOT CONTEXT 5-step block (Phase A), atomic_class declaration field, receipt checklist (Phase C 9 steps)
2. `scripts/action_model_validator.py` — standalone validator: read dispatch prompt or receipt text, return Phase compliance bitmap + missing steps + allow/deny decision
3. `Y-star-gov/ystar/governance/forget_guard_rules.yaml` — 2 new rules:
   - `dispatch_missing_phase_a` (mode: dry_run initially) — calls action_model_validator.py on Agent tool PreToolUse hook
   - `receipt_missing_phase_c_heavy` (mode: dry_run initially) — calls action_model_validator.py on Stop hook reply text

**Upstream dependency**: Step A (spec) must close Rt+1=0 before Maya starts Step B.

**Success criteria**:
- 3 files shipped, tests PASS (≥6 test cases per §7)
- Dry_run mode active, logging violations without blocking
- Rt+1=0

### Step C: Pilot → Tune → Enforce LIVE

**Deliverable**: 5 pilot atomics executed under v2 model (per §7 experiment corpus).

**Sequence**:
1. Execute 5 atomics with dry_run enforcement active
2. Collect metrics: Phase compliance bitmap, Rt+1 distribution, tool_uses honesty, false-positive rate
3. Tune: If false-positive >30% on any Phase step → relax regex. If false-negative >5% → strengthen.
4. Promote: After tuning converges (<5% FP, <5% FN), promote dry_run → warn mode
5. Baseline warn mode for 48h event-time (≈10-20 atomics)
6. Promote warn → deny mode (LIVE enforcement)

**Upstream dependency**: Step B (wiring) must close Rt+1=0 before Step C pilots start.

**Success criteria**:
- 5 pilot atomics complete, metrics logged
- Tuning iteration complete (if needed)
- Enforcement promoted to deny mode
- Rt+1=0 for Step C overall (pilot execution may have individual Rt+1>0, but tuning/promotion process closes clean)

**Downstream cascade**: After Step C LIVE, all future dispatches/receipts subject to v2 enforcement. No explicit "migration" needed — enforcement hooks apply universally.

---

## Empirical Verification (Anti-Hallucination Protocol)

Per CZL-114 lesson (hallucinated 0/8 tool_uses receipt) — empirical paste mandatory for all spec deliverables:

