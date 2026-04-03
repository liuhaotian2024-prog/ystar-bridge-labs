# Y*gov as a Pearl-Native Architecture
# Date: 2026-03-30
# For: arXiv paper Section 3 — "Architecture is the Theory"

## Core Argument

Y*gov was not retrofitted with Pearl's causal hierarchy — it was designed from it.

The CIEU five-tuple, the Y*_t ideal contract, and the OmissionEngine are not
engineering conveniences that happen to resemble Pearl's framework. They are
direct implementations of Pearl's three levels, embedded in the data structure
of every governance decision.

---

## Pearl's Ladder of Causation → Y*gov Architecture

### Level 1: Association — "What happened?"
**Pearl**: P(Y|X) — observational distribution from data
**Y*gov**: Every CIEU record stores **C**ontext (state before) and **E**xecution (what the agent did).

The CIEU database IS the observational dataset. 579+ records of agent behavior
with full context: agent_id, tool_name, params, decision, timestamp.

**Implementation**: CIEUStore.write() + CIEUStore.query()

### Level 2: Intervention — "What if we force X?"
**Pearl**: P(Y|do(X)) — the effect of forcing a variable to a value
**Y*gov**: check() IS the do-operator.

When check() evaluates an agent action against an IntentContract, it is
computing P(outcome | do(enforce contract)). The check is not observational —
it *intervenes* on the agent's behavior by allowing or denying the action.

**The key insight**: check() doesn't predict what will happen. It *forces* a
specific causal pathway (ALLOW or DENY) and records the outcome. This is
intervention, not observation.

**Y*_t is the intervention target**: the ideal contract at time t defines
WHAT the intervention enforces. Without Y*_t, check() has no intervention
to apply.

**Implementation**: kernel/engine.py check() + IntentContract.Y*_t field in CIEU

### Level 3: Counterfactual — "What if things had been different?"
**Pearl**: P(Y_x' | X=x, Y=y) — given what actually happened, what WOULD have
happened under different conditions?

**Y*gov implements this at THREE levels:**

**3a. Record-level counterfactual (every CIEU record)**:
Every CIEU record stores BOTH:
- What the agent actually did (Execution)
- What the agent SHOULD have done (Intent / Y*_t)

The gap between E and Y*_t IS the counterfactual: "If the agent had followed
the ideal contract, the execution would have been different." This is computed
for every single governance decision, not as a separate analysis step.

**3b. Omission counterfactual (OmissionEngine)**:
"What if the agent had done what it promised?"

OmissionEngine detects obligations that were NOT fulfilled. This is the
counterfactual of absence: P(task_completed | do(agent_acts)) vs
P(task_completed | agent_does_nothing). The detection trigger is the agent's
own next action — a causal link between non-action and detection.

**3c. Path A counterfactual (CausalEngine)**:
"If we had chosen a different wiring plan, would health have improved?"

CausalEngine.counterfactual_query() implements Pearl's three-step procedure:
1. Abduction: infer initial state parameters from observed cycle
2. Action: substitute alternative wiring plan
3. Prediction: compute expected health under alternative

---

## The CIEU Five-Tuple IS Pearl's Three Levels

| CIEU Field | Pearl Level | What It Captures |
|------------|-------------|------------------|
| **C**ontext | L1 (observation) | State before action — the observational starting point |
| **I**ntent (Y*_t) | L2 (intervention target) | What SHOULD happen — the intervention specification |
| **E**xecution | L1+L2 (observed under intervention) | What actually happened under governance |
| **U** (assessment) | L3 (counterfactual) | Gap between Y*_t and E — "what if Y*_t had been perfectly followed?" |
| prev_hash | Causal chain | SHA-256 link to the previous record — temporal causal ordering |

**Every CIEU record is simultaneously an observation (L1), the result of an
intervention (L2), and a counterfactual comparison (L3).**

No other audit system stores all three levels in every record. Traditional
audit logs store only L1 (what happened). Compliance systems store L1 + a
static policy (not L2, because the policy isn't an intervention — it's a
document). Y*gov stores L1 + L2 + L3 because the policy IS the intervention
AND the counterfactual baseline.

---

## Why This Matters for the Paper

The standard claim would be: "We added a CausalEngine module that does
Pearl-style reasoning."

The REAL claim is stronger: "The entire Y*gov architecture embodies Pearl's
causal hierarchy. The CIEU five-tuple is not an audit format — it is a
causal data structure. Y*_t is not a policy label — it is the intervention
variable. OmissionEngine is not just obligation tracking — it is
counterfactual detection of non-action."

This reframing means:
1. Pearl Level 2 is not a feature we added — it's how check() has always worked
2. Pearl Level 3 is not in one module — it's in every CIEU record (Y*_t vs E)
3. The CausalEngine formalizes what the architecture already embodies

---

## Formal Statement (for paper Section 3)

**Theorem (informal)**: Y*gov's CIEU five-tuple is isomorphic to Pearl's
three-level causal hierarchy applied to agent governance:

- Level 1 (Association): CIEU(C, E) ≅ P(E|C)
- Level 2 (Intervention): CIEU(I, E) ≅ P(E|do(I=Y*_t))
- Level 3 (Counterfactual): CIEU(U) ≅ P(E_{Y*_t} | E≠Y*_t)

The hash chain (prev_hash) provides temporal causal ordering,
making the entire CIEU database a time-indexed structural causal model
where each record is a node, each hash link is a causal edge, and
Y*_t is the intervention variable at each node.
