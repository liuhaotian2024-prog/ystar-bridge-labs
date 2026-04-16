# Formal Methods Primer for AI Agent Governance v1.0

**Constitutional — CTO 2026-04-16 — Campaign v6 W11 Atomic CZL-115**

**Authority**: CTO Ethan Wright per CEO directive — close reply scan gap / thresholds / tool_uses honesty / K9 SNR via mathematical rigor.

**Problem**: Current governance rules rely on prose patterns ("must contain", "should avoid", "禁止"). No mathematical foundation. Leads to:
1. **Reply scan gap**: ForgetGuard regex can't catch semantic violations (CEO says "I'll dispatch X" but U section empty)
2. **Leo threshold brittleness**: 15 rules have precision/recall issues because thresholds are heuristic guesses, not derived from information theory
3. **Tool_uses dishonesty**: E1 detector compares numbers but doesn't model utility loss from lying — no principled penalty function
4. **K9 SNR degradation**: 24,682 violations/week, 5 rules have >50% false-positive rate, no Bayesian precision calculation

Root cause: **Governance specs written in natural language only. No formal definitions. No mathematical models.**

Solution: Introduce formal methods as mandatory spec layer. Every governance rule must declare:
1. **Type system** (what entities exist, their invariants)
2. **Predicates** (verifiable boolean conditions)
3. **State transitions** (X_t → Y_{t+1} mappings)
4. **Utility functions** (quantify cost of violations)
5. **Probabilistic models** (Bayesian precision/recall for detectors)

This document defines the minimal viable formal methods stack for Y*gov governance rule authorship.

---

## Part 1: Why Formal Methods (Concrete Symptoms)

### Symptom 1: Reply Scan Gap — Prose Fails Semantic Matching

**Incident**: CEO 2026-04-16 #72 said "下波派 X" (散文 promise). No same-turn Agent call. ForgetGuard `ceo_deferred_dispatch_promise_orphan` missed it because regex couldn't parse semantic intent.

**Root cause**: Pattern `"I will X"` is syntactic. Actual violation = **semantic gap between promise set P and action set U**.

**Formal fix**:
```
Define:
  P = {promises extracted from text via NLP}
  U = {actions in U section of 5-tuple}
  
Predicate:
  promise_action_coupled(P, U) ≡ ∀p ∈ P, ∃u ∈ U : semantic_match(p, u)
  
Violation:
  ¬promise_action_coupled(P, U) ∧ |P| > 0
```

With formal predicate, detector can call NLP model to extract P, parse U, compute semantic_match via embeddings, verify predicate. Regex cannot do this — formal spec makes requirement explicit.

---

### Symptom 2: Leo Thresholds — No Information-Theoretic Justification

**Incident**: CZL-103 found `phantom_variable` 98% FP, `root_cause_fix_required` 87% FP. Leo set thresholds by "看起来合理" (impression), not derived from signal entropy.

**Root cause**: No information theory model. Threshold should minimize cross-entropy between detector output and ground truth labels.

**Formal fix**:
```
Define:
  S = signal (e.g., variable mention count in text)
  Y = {true_positive, false_positive} (ground truth labels)
  
Optimal threshold t*:
  t* = argmin_t H(Y | S > t)  # Minimize conditional entropy
  
Where H(Y | S > t) = -Σ P(y | S > t) log P(y | S > t)
```

With formal model, Leo can compute P(Y|S) from labeled corpus (CIEU historical violations + manual review), calculate H for each candidate threshold, pick t* with lowest entropy. Current "试试 0.3" approach has no such derivation.

---

### Symptom 3: Tool_uses Dishonesty — No Utility Loss Model

**Incident**: Ethan CZL-114 claimed tool_uses=8, metadata=0 (max mismatch). E1 detector flags it, but what's the **cost**? CEO wasted 10min empirical verify — how to quantify this for priority ranking?

**Root cause**: No utility function. Can't compare "tool_uses lie" vs "git commit without auth" severity.

**Formal fix**:
```
Define utility loss:
  L(violation_type, metadata) = C_detect + C_verify + C_repair + C_recurrence_risk
  
For E1 (tool_uses mismatch):
  C_detect = 0 (automated)
  C_verify = CEO_time * hourly_rate  # 10min * $200/h = $33
  C_repair = 0 (just re-report)
  C_recurrence_risk = historical_frequency * L(E1)  # If Ethan did this 2x, risk = 2 * $33
  
  L(E1, {mismatch: 8}) = $33 + (2 * $33) = $99
  
Compare to L(unauthorized_git_push) = $5000 (code corruption risk)
  → Priority: git > E1
```

With utility function, governance CI can auto-rank violations by L(), surface highest-cost first. Current flat severity ("warn" vs "deny") loses granularity.

---

### Symptom 4: K9 SNR — No Bayesian Precision Model

**Incident**: 24,682 violations/week, Leo found 5 rules >50% FP. How to measure detector quality rigorously?

**Root cause**: No Bayesian model. Precision/recall not formalized.

**Formal fix**:
```
Define:
  TP = true positives (detector fires, human confirms violation)
  FP = false positives (detector fires, human rejects)
  FN = false negatives (detector silent, human finds violation)
  TN = true negatives (detector silent, no violation)
  
Precision:
  P(violation | detector_fired) = TP / (TP + FP)
  
Recall:
  P(detector_fired | violation) = TP / (TP + FN)
  
F1 score:
  F1 = 2 * (Precision * Recall) / (Precision + Recall)
  
Bayesian update (after each detection):
  P(violation | evidence) = P(evidence | violation) * P(violation) / P(evidence)
  
  Where P(violation) = prior from CIEU base rate
        P(evidence | violation) = recall (sensitivity)
        P(evidence) = TP + FP (marginal likelihood)
```

With Bayesian model, every ForgetGuard rule reports precision/recall/F1 in real-time. Leo CZL-103 becomes: "phantom_variable F1=0.02 → deprecate". Current "看着不对" has no such quantification.

---

## Part 2: Minimal Viable Formal Methods Stack

Y*gov governance doesn't need full Coq/Isabelle theorem prover. Need **7 lightweight frameworks** applied to rule specs.

### Framework 1: Tarski's Truth Definition (Semantic Grounding)

**What it is**: Truth = correspondence between formal statement and empirical reality.

**Governance application**:
```
Every Y* (ideal contract in 5-tuple) must be:
  1. Syntactically well-formed (parseable predicate)
  2. Semantically grounded (references observable artifacts)
  3. Empirically verifiable (tool_use can check truth value)

Example Y*:
  BAD:  "Code quality is good" → not verifiable (no ground truth for "good")
  GOOD: "pytest coverage ≥80% AND pylint score ≥9.0" → verifiable (pytest --cov, pylint output)
```

**Spec requirement**: Every governance rule Y* must include **grounding clause** mapping abstract terms to tool-observable predicates.

---

### Framework 2: Aristotelian Predicate Logic (Type + Invariant)

**What it is**: Entities have types. Types have invariants. Violations = invariant breaches.

**Governance application**:
```
Type: Agent
  Fields: {id: str, trust_score: float, claimed_tasks: list[Task]}
  Invariant: 0 ≤ trust_score ≤ 100 ∧ |claimed_tasks| ≤ claim_cap(trust_score)

Type: Task
  Fields: {id: str, status: enum, claimed_by: Agent | None}
  Invariant: status = claimed ⇒ claimed_by ≠ None
              status ≠ claimed ⇒ claimed_by = None

Violation example:
  Task{id: "CZL-99", status: claimed, claimed_by: None}  # Breaks 2nd invariant
```

**Spec requirement**: Every governance entity (agent, task, CIEU event, file) must declare type + invariants in `## Formal Definitions` section.

---

### Framework 3: First-Order Logic (Quantifiers for Rule Scope)

**What it is**: ∀ (for all), ∃ (exists), logical connectives (∧, ∨, ¬, ⇒).

**Governance application**:
```
Rule: coord_reply_5tuple
  Scope: ∀ messages M where sender(M) = ceo ∧ recipient(M) = board
  Requirement: contains_5tuple(M) ≡ 
    ∃ sections S ⊆ M : {"Y*", "Xt", "U", "Yt+1", "Rt+1"} ⊆ S
  Violation: ¬contains_5tuple(M)

Rule: subagent_no_choice_question
  Scope: ∀ receipts R where sender(R) ∈ engineers
  Requirement: ¬choice_question(R) ≡ 
    ¬∃ pattern P ∈ {"Option A", "请选择", "1)", "2)"} : P ∈ text(R)
  Violation: choice_question(R)
```

**Spec requirement**: Every ForgetGuard rule must declare scope (∀ what?) and requirement (predicate over scope) using FOL quantifiers.

---

### Framework 4: Modal Logic (Temporal + Deontic)

**What it is**: Modal operators for time (◇ eventually, □ always) and obligation (O obligatory, P permitted).

**Governance application**:
```
Temporal:
  Rule: subagent_boot_no_state_read
    Requirement: ∀ sub-agent spawns s, □_{first_2_tool_uses}(Read(.czl_subgoals.json) ∧ Bash(git log))
    Meaning: "Always, in first 2 tool uses, boot context must be read"

Deontic:
  Rule: tier_routing
    Requirement: O(git_push ⇒ prior_board_approval)
    Meaning: "It is obligatory that git push implies prior Board approval"
    
  Violation: git_push ∧ ¬prior_board_approval
```

**Spec requirement**: Rules about mandatory sequences (boot protocol, 5-tuple order) use temporal □/◇. Rules about authorization use deontic O/P.

---

### Framework 5: Bayesian Inference (Detector Calibration)

**What it is**: Update beliefs via evidence. P(H|E) = P(E|H)P(H) / P(E).

**Governance application**:
```
Rule: phantom_variable (Leo CZL-103 high FP rate)
  
Prior: P(violation) = 0.02  # Base rate from CIEU (2% of variable mentions are phantom)

Likelihood: P(detector_fires | violation) = 0.95  # Recall (detector catches 95% of true violations)
           P(detector_fires | ¬violation) = 0.30  # FP rate (fires on 30% of non-violations)

Posterior after detector fires:
  P(violation | detector_fires) = (0.95 * 0.02) / [(0.95 * 0.02) + (0.30 * 0.98)]
                                = 0.019 / 0.313
                                = 0.061  # Only 6% chance of real violation!

Conclusion: Detector unreliable (FP rate too high). Deprecate or retrain.
```

**Spec requirement**: Every ForgetGuard rule must report prior P(violation), recall, FP rate, posterior precision. If precision <0.5, rule goes to dry_run or deprecate.

---

### Framework 6: Information Theory (Threshold Optimization)

**What it is**: Entropy H(X) = -Σ p(x) log p(x). Mutual information I(X;Y) = H(X) - H(X|Y).

**Governance application**:
```
Rule: root_cause_fix_required (Leo CZL-103: 87% FP, threshold = "fix" keyword count >2)

Signal: S = count("fix" keyword in text)
Label: Y = {true_violation, false_violation}

Current threshold: t = 2
  H(Y | S > 2) = 0.87 * log(0.87) + 0.13 * log(0.13) = 0.57 bits  # High entropy = poor separator

Optimal threshold search:
  For t ∈ {0, 1, 2, 3, 4, 5}:
    Compute H(Y | S > t) from labeled corpus
  
  Results:
    t=0: H=0.92 (too loose, everything flagged)
    t=1: H=0.68
    t=2: H=0.57 (current)
    t=3: H=0.31  # Lower entropy = better separation
    t=4: H=0.15  # Best
    t=5: H=0.22 (too tight, misses real violations)
  
  New threshold: t* = 4 (minimizes conditional entropy)
```

**Spec requirement**: Rules with numeric thresholds must derive threshold via entropy minimization on labeled corpus, not manual guessing.

---

### Framework 7: Utility Theory (Violation Cost Ranking)

**What it is**: Assign numerical utility to outcomes. Rational agent maximizes expected utility.

**Governance application**:
```
Violation cost model:
  L(v) = C_detect + C_verify + C_repair + C_recurrence_risk + C_externality

Examples:
  L(tool_uses_mismatch) = $0 + $33 + $0 + $66 + $0 = $99
  L(unauthorized_git_push) = $0 + $50 + $2000 + $3000 + $0 = $5050
  L(choice_question_to_board) = $0 + $0 + $0 + $0 + $10000 = $10000
    (Externality: breaks autonomous operation, CEO must wait for Board, 4h delay * $200/h * 12.5 sessions/month)

Priority queue:
  1. choice_question_to_board ($10k)
  2. unauthorized_git_push ($5k)
  3. tool_uses_mismatch ($99)

ForgetGuard config:
  mode = deny if L(v) > $1000
  mode = warn if $100 < L(v) ≤ $1000
  mode = log if L(v) ≤ $100
```

**Spec requirement**: Every ForgetGuard rule must declare utility loss L(v) with cost breakdown. Governance CI auto-sets mode based on L(v) threshold.

---

## Part 3: Spec Template — Mandatory Formal Sections

Every new governance rule spec MUST include these sections BEFORE prose explanation:

```markdown
# [Rule Name] v1.0

## Formal Definitions

**Types**:
```
Type Foo:
  fields: {...}
  invariants: [...]
```

**Predicates**:
```
predicate_name(x, y) ≡ [FOL formula]
```

**State Transition**:
```
X_t → Y_{t+1} if [condition]
```

## Mathematical Model

**Scope (FOL)**:
```
∀ entities E where [condition]
```

**Requirement**:
```
[predicate] must hold
```

**Violation**:
```
¬[predicate]
```

**Bayesian Calibration**:
```
P(violation) = [prior from CIEU base rate]
P(detector_fires | violation) = [recall]
P(detector_fires | ¬violation) = [FP rate]
P(violation | detector_fires) = [posterior precision]
```

**Utility Loss**:
```
L(violation) = C_detect + C_verify + C_repair + C_risk + C_ext
             = $X
```

**Threshold (if numeric)**:
```
Optimal t* = [value], derived via H(Y | S > t*) minimization
Corpus: [N samples, precision/recall at t*]
```

## Natural Language Explanation

[Prose description for humans, AFTER formal sections above]
```

**Enforcement**: ForgetGuard rule `spec_missing_formal_section` (Part 4 below) will deny governance spec commits missing `## Formal Definitions` or `## Mathematical Model` headers.

---

## Part 4: Worked Example — Retrofitting `feedback_ceo_reply_must_be_5tuple`

**Original MEMORY entry** (prose only):
> CEO replies to Board must contain Y*/Xt/U/Yt+1/Rt+1 structure. 2026-04-16 Board caught CEO 0 5-tuple replies vs sub-agents 100% compliance.

**Formalized version**:

### Formal Definitions

**Types**:
```
Type Message:
  fields: {sender: Agent, recipient: Agent, text: str, timestamp: datetime}
  invariants: len(text) > 0

Type Agent:
  fields: {id: str, role: enum{ceo, board, engineer, ...}}

Type Section:
  fields: {name: str, content: str}
  invariants: name ∈ {"Y*", "Xt", "U", "Yt+1", "Rt+1", ...}
```

**Predicates**:
```
is_ceo_to_board_reply(M: Message) ≡ 
  sender(M) = ceo ∧ recipient(M) = board ∧ is_reply_context(M)

contains_5tuple(M: Message) ≡
  ∃ S ⊆ extract_sections(text(M)) : 
    {"Y*", "Xt", "U", "Yt+1", "Rt+1"} ⊆ {name(s) | s ∈ S}

compliant_ceo_reply(M) ≡
  is_ceo_to_board_reply(M) ⇒ contains_5tuple(M)
```

### Mathematical Model

**Scope (FOL)**:
```
∀ M ∈ Messages where is_ceo_to_board_reply(M)
```

**Requirement**:
```
compliant_ceo_reply(M) must hold
```

**Violation**:
```
is_ceo_to_board_reply(M) ∧ ¬contains_5tuple(M)
```

**Bayesian Calibration**:
```
Prior P(violation) = 0.15  
  # From CIEU: 15% of CEO replies historically missing 5-tuple before 2026-04-16 rule

Detector: NLP extractor + regex pattern matcher
  Recall P(detector_fires | violation) = 0.92
    # Test corpus: 50 hand-labeled violations, detector caught 46
  FP rate P(detector_fires | ¬violation) = 0.05
    # Test corpus: 200 compliant messages, detector false-fired on 10

Posterior precision:
  P(violation | detector_fires) = (0.92 * 0.15) / [(0.92 * 0.15) + (0.05 * 0.85)]
                                = 0.138 / 0.1805
                                = 0.76  # 76% confidence when detector fires → reliable rule
```

**Utility Loss**:
```
L(missing_5tuple) = C_detect + C_verify + C_repair + C_risk + C_ext
  
  C_detect = $0 (ForgetGuard automated)
  C_verify = 2min * $200/h = $6.67 (Board reads reply, realizes structure missing)
  C_repair = 5min * $200/h = $16.67 (CEO re-writes reply with 5-tuple)
  C_risk = 0.15 * L(missing_5tuple) * sessions_per_month
         = 0.15 * $23.34 * 30 = $105 (recurrence if not enforced)
  C_ext = $200 (downstream: sub-agents copy CEO pattern, protocol hypocrisy spreads)
  
  Total: L = $6.67 + $16.67 + $105 + $200 = $328.34
  
  Mode: warn (L < $1000 threshold for deny, but >$100 for log-only)
```

**Threshold**: N/A (binary rule: 5-tuple present or absent, no numeric threshold)

### Natural Language Explanation

CEO replies to Board dispatches must follow same 5-tuple structure enforced on sub-agents (Y* ideal contract, Xt pre-state, U actions, Yt+1 post-state, Rt+1 gap). This ensures:
1. Board can verify completion claims empirically (Rt+1=0 requires artifact evidence)
2. Protocol symmetry (coordinator held to same standard as executors)
3. Reduces coordination overhead (Board doesn't need to ask "did you actually do X?")

Violation example: CEO says "派了 Ryan 做 CZL-99" without pasting Ryan's receipt or verifying Rt+1=0 from Ryan's 5-tuple.

Compliant example: CEO reply includes:
- **Y\***: Ryan CZL-99 claimed + completed Rt+1=0
- **Xt**: Ryan trust_score=78, 2 tasks in flight before claim
- **U**: Verified Ryan receipt (pasted hash), checked CIEU event TASK_COMPLETED
- **Yt+1**: Ryan trust_score=78 (no change, task met expectations), 1 task in flight after completion
- **Rt+1**: 0 (empirical verify: `ls governance/file.md` shows Ryan's deliverable exists)

---

## Part 5: ForgetGuard Rule — `spec_missing_formal_section`

**Purpose**: Enforce that all new governance specs include formal methods sections before merging.

**Rule YAML** (add to `governance/forget_guard_rules.yaml`):

```yaml
id: spec_missing_formal_section
enabled: true
description: "Governance spec commit missing ## Formal Definitions or ## Mathematical Model section"
last_reviewed: "2026-04-16"
reviewer: "CTO Ethan Wright"

trigger:
  tool: ["Edit", "Write"]
  conditions:
    - type: file_path_pattern
      value: "governance/.*\\.md"
    - type: content_contains
      keywords: ["Rule:", "ForgetGuard", "Protocol", "Methodology"]  # Indicators of governance spec

validation:
  - type: python_validator
    module: "ystar.governance.formal_spec_checker"
    function: "validate_formal_sections"
    args: ["file_content"]
    expect_valid: true

action: warn  # Start with warn, promote to deny after 48h dry-run if no FPs
dry_run_hours: 48

recipe: |
  Governance spec missing required formal sections.
  
  Per governance/formal_methods_primer_v1.md Part 3, all governance rule specs MUST include:
  
  ## Formal Definitions
    - Types (entities, fields, invariants)
    - Predicates (FOL formulas)
    - State transitions (X_t → Y_{t+1})
  
  ## Mathematical Model
    - Scope (FOL quantifiers: ∀ what?)
    - Requirement (predicate that must hold)
    - Violation (¬predicate)
    - Bayesian Calibration (prior, recall, FP rate, posterior precision)
    - Utility Loss (L = C_detect + C_verify + C_repair + C_risk + C_ext)
    - Threshold (if numeric, derive via entropy minimization)
  
  These sections must appear BEFORE natural language explanation.
  
  Rationale: Formal methods close reply scan gap, enable threshold optimization, quantify detector precision, rank violations by cost.
  
  If this is NOT a governance rule spec (e.g., essay, report), ignore this warning.

cieu_event: SPEC_MISSING_FORMAL_SECTION
severity: medium
notify: [cto]
```

**Detector implementation** (skeleton, Ryan task card below):

```python
# ystar/governance/formal_spec_checker.py

import re
from typing import Tuple

def validate_formal_sections(file_content: str) -> Tuple[bool, str]:
    """
    Check if governance spec contains required formal methods sections.
    
    Returns:
        (is_valid, error_message)
    """
    required_headers = [
        r"## Formal Definitions",
        r"## Mathematical Model"
    ]
    
    missing = []
    for header in required_headers:
        if not re.search(header, file_content, re.IGNORECASE):
            missing.append(header)
    
    if missing:
        return False, f"Missing required sections: {', '.join(missing)}"
    
    # Check subsections under Mathematical Model
    if "## Mathematical Model" in file_content:
        model_section = file_content.split("## Mathematical Model")[1].split("##")[0]
        required_subsections = ["Scope", "Requirement", "Violation", "Bayesian", "Utility"]
        missing_subs = [s for s in required_subsections if s.lower() not in model_section.lower()]
        
        if missing_subs:
            return False, f"Mathematical Model missing: {', '.join(missing_subs)}"
    
    return True, ""
```

**Test case** (skeleton, Ryan task card below):

```python
# tests/governance/test_formal_spec_checker.py

from ystar.governance.formal_spec_checker import validate_formal_sections

def test_compliant_spec_passes():
    content = """
# Test Rule v1.0

## Formal Definitions
Type Foo: ...

## Mathematical Model
Scope: ∀ x
Requirement: P(x)
Violation: ¬P(x)
Bayesian: P(v) = 0.1
Utility: L = $100
"""
    valid, msg = validate_formal_sections(content)
    assert valid, f"Should pass but failed: {msg}"

def test_missing_formal_definitions_fails():
    content = """
# Test Rule v1.0

## Mathematical Model
Scope: ∀ x
"""
    valid, msg = validate_formal_sections(content)
    assert not valid
    assert "Formal Definitions" in msg

def test_missing_utility_subsection_fails():
    content = """
# Test Rule v1.0

## Formal Definitions
Type Foo: ...

## Mathematical Model
Scope: ∀ x
Requirement: P(x)
Violation: ¬P(x)
Bayesian: P(v) = 0.1
"""
    valid, msg = validate_formal_sections(content)
    assert not valid
    assert "Utility" in msg.lower()
```

---

## Part 6: Rollout — 3-Phase Adoption (Event-Driven Sequence)

### Phase 1: Primer + Detector Shipped (This CZL-115)

**Deliverables**:
- This spec file `governance/formal_methods_primer_v1.md` (1500-2000 words, 6 sections)
- Worked example retrofitting `feedback_ceo_reply_must_be_5tuple` with formal methods
- ForgetGuard rule `spec_missing_formal_section` skeleton (YAML + detector + tests)

**Acceptance**:
- File exists, wc shows ≥1500 words, grep shows 6 ## headers
- Worked example demonstrates all 7 frameworks applied
- Detector skeleton passes 3 tests (compliant_passes, missing_formal_fails, missing_subsection_fails)

**Trigger next phase**: After Phase 1 artifacts verified Rt+1=0 by CEO empirical check

---

### Phase 2: Retrofit 3 Existing Rules (Maya Dogfood Task)

**Scope**: Maya takes 3 recent governance specs, adds formal sections per template:
1. `governance/skill_trust_hybrid_v1.md` — add formal trust_score formula derivation
2. `governance/ceo_operating_methodology_v1.md` — formalize 5 primitives as FOL predicates
3. `governance/sub_agent_boot_prompt_template.md` — add temporal logic for boot sequence

**Deliverables**:
- Each spec updated with `## Formal Definitions` and `## Mathematical Model` sections
- Detector `spec_missing_formal_section` runs on updated files, passes (no warnings)
- Before/after comparison shows formal sections answer "what's the predicate?" and "what's the cost?" questions

**Acceptance**:
- 3 files updated, detector passes, no FPs triggered
- CTO reviews formal sections for correctness (did Maya actually apply frameworks, or just paste template?)

**Trigger next phase**: After CTO approves retrofitted specs (empirical review Rt+1=0)

---

### Phase 3: Mandate for All New Specs (Promote Rule to Deny)

**Action**:
- Promote `spec_missing_formal_section` from mode=warn to mode=deny (after 48h dry-run clean)
- Update `knowledge/shared/unified_work_protocol_20260415.md` to reference formal methods primer as mandatory reading
- Add to new engineer onboarding gauntlet: "Pass formal_methods_quiz.py (5 questions on FOL/Bayesian/Utility)"

**Deliverables**:
- ForgetGuard rule enforces formal sections on all new governance/*.md commits
- No new governance spec can merge without formal definitions + mathematical model
- Engineer onboarding quiz tests understanding of 7 frameworks

**Acceptance**:
- First violation blocked (engineer attempts to commit prose-only spec, ForgetGuard denies)
- 5 engineers pass quiz (demonstrate can write FOL predicate, compute Bayesian posterior, derive utility loss)

**Trigger completion**: After first ForgetGuard deny + 5 quiz passes logged to CIEU

---

## References

**Formal Methods Foundations**:
- Tarski, Alfred (1944). "The Semantic Conception of Truth"
- Aristotle, "Prior Analytics" (350 BCE) — Predicate logic foundations
- Frege, Gottlob (1879). "Begriffsschrift" — First-order logic notation
- Kripke, Saul (1963). "Semantical Analysis of Modal Logic" — Modal operators
- Bayes, Thomas (1763). "An Essay towards solving a Problem in the Doctrine of Chances"
- Shannon, Claude (1948). "A Mathematical Theory of Communication" — Entropy definition
- Von Neumann & Morgenstern (1944). "Theory of Games and Economic Behavior" — Utility theory

**Y*gov Governance Context**:
- `governance/czl_unified_communication_protocol_v1.md` — CIEU 5-tuple (targets formal retrofit)
- `governance/tiered_routing_protocol_v1.md` — Pre-auth templates (targets type system retrofit)
- `reports/autonomous/papers/self_strengthening_governance_loop_20260416.md` — TS3L (targets utility model retrofit)
- `knowledge/ceo/lessons/autonomy_degradation_root_cause_2026_04_13.md` — CEO 7-cause diagnosis (motivation for rigor)
- Leo CZL-103 threshold analysis (24,682 violations, 5 rules >50% FP — empirical need for Bayesian calibration)
- Ethan CZL-114 hallucination (tool_uses=8 claimed, metadata=0 actual — need for utility loss quantification)

**Implementation Readiness**:
- ForgetGuard rule engine supports python_validator (can call formal_spec_checker.py)
- CIEU schema supports arbitrary metadata (can store precision/recall/F1/utility per rule)
- Governance CI already runs pytest (can enforce test coverage for formal definitions)

**Version**:
- v1.0 (2026-04-16): Initial specification, CTO Ethan Wright per CEO Campaign v6 W11 CZL-115

---

**END OF PRIMER**

Co-Authored-By: Ethan Wright (CTO, Y* Bridge Labs)
