# Commission Infra Root Cause + Unification Plan — 2026-04-22

Audience: Ethan-CTO (sprint planning scope) / Ryan-Platform (implementation) / Maya-Governance (rule semantics) / Board (Haotian Liu) review
Research basis: Board 2026-04-22 catch "commission 的那部分 也没有真实的启动, 也是缺方法论框架"; empirical grep: `hook_wrapper.py` contains 0 references to `forget_guard`; `forget_guard_rules.yaml` exists in governance/ with 32 rules schema 1.1; `boundary_enforcer.py` post-surgery has 25 hardcoded `_check_*` functions; `scripts/behavior_gov_rules.yaml` (shipped by CEO today) is a third parallel YAML; Y-star-gov governance modules reference forget_guard in 10 files but the hook layer does not invoke it
Synthesis: Commission infrastructure exists in 3 places (25 Python hardcoded in boundary_enforcer + 32 YAML in forget_guard_rules + 4 YAML in behavior_gov_rules) with NO unified engine. Forget_guard 32 rules are dead code — hook_wrapper.py never calls the forget_guard engine. Boundary_enforcer's 25 Python-hardcoded rules DO fire via hook_wrapper, but cannot be modified without code change. The third YAML (shipped today by CEO) is a duplicated attempt that did not know forget_guard existed — P-12 violation by CEO. Root cause of "commission 不起作用": not missing infra, missing hook-layer integration + unification.
Purpose: Single plan document for CTO. Three-step resolution: (1) wire forget_guard into hook_wrapper so its 32 rules fire, (2) unify forget_guard YAML + behavior_gov_rules YAML into single schema + engine, (3) migrate boundary_enforcer's 25 Python rules into YAML incrementally. Result: one YAML + one engine handles both Commission (prevent wrong action) and Omission (prevent missing action).

---

## Diagnosis — why Commission did not stop CEO lazy / deception

**Hypothesis** (Board's): commission layer is装的 but not LIVE.
**Empirical check**:

```
grep -cE "forget_guard" scripts/hook_wrapper.py          # → 0
grep -c "^def _check_" Y-star-gov/.../boundary_enforcer.py   # → 25
wc -l governance/forget_guard_rules.yaml                 # → 32 rules in YAML
```

So 25 Python rules fire via hook_wrapper (LIVE), and 32 YAML rules sit in a file that no hook reads (dead). That's why Board sees governance inconsistency — some commission checks pass (restricted_write_paths, must_dispatch_via_cto, immutable_paths) because they're in the LIVE path, others (forget_guard YAML — things like "no choice questions to Board", "L-tag required", "board-facing format compliance") do not fire.

My ship today (behavior_gov_engine + scripts/behavior_gov_rules.yaml) is a **third** parallel YAML. I did not check for forget_guard_rules.yaml before creating a new one. P-12 violation. My 4 handler types reinvent what forget_guard schema 1.1 already expresses.

**Board's catch is precise**: commission methodology framework is incomplete not because it doesn't exist, but because three parallel implementations exist with no unification + one is dead-coded.

---

## Three-step unification plan (engineering scope, not CEO)

### Step 1: Wire forget_guard to hook_wrapper (Ryan-Platform)

**Why first**: 32 YAML rules go LIVE with one integration point. Highest return per engineer-hour.

**Spec**:
- Import forget_guard engine from Y-star-gov.ystar.governance into scripts/hook_wrapper.py
- On PreToolUse event, after existing boundary_enforcer check, invoke forget_guard.evaluate(tool_input, tool_name, agent_id, cieu_db)
- If forget_guard returns deny → block tool call with its recipe message
- If warn → log CIEU event + continue (don't block)
- If allow → continue

**Acceptance**: live-fire — deliberately violate one of the 32 rules (e.g. "missing L-tag" by writing a completion claim without tag), verify hook blocks/warns with the correct recipe from YAML.

**Deadline** (via OmissionEngine obligation on ryan actor): 2026-04-29

### Step 2: Unify behavior_gov_rules + forget_guard_rules YAML schemas (Maya-Governance)

**Why**: 2 YAML files with different schemas fragments methodology. Single schema = single mental model for future rule authors.

**Spec**:
- Choose forget_guard schema (more mature: trigger.conditions with path_match/content_contains/command_contains, AND/OR logic, recipe templates, CIEU event emission) as canonical
- Migrate 4 rules from scripts/behavior_gov_rules.yaml into forget_guard_rules.yaml syntax
- Retire scripts/behavior_gov_rules.yaml + behavior_gov_engine.py (deprecate with redirect comment)
- behavior_gov_engine's 4 handler types (DeadlineCheck / FrequencyCheck / StatePresenceCheck / ToolCountCheck) become extensions of forget_guard engine if not already present

**Acceptance**: single YAML contains Commission + Omission rules. behavior_gov_engine.py deleted or reduced to stub. forget_guard engine handles all 36 rules (32 existing + 4 migrated).

**Deadline**: 2026-05-06

### Step 3: Migrate boundary_enforcer's 25 Python rules into YAML incrementally (Maya + Ryan)

**Why**: 25 hardcoded rules need code change to edit. YAML version means new governance requirement = YAML entry, not code commit.

**Spec**:
- For each of 25 `_check_*` functions in boundary_enforcer.py, determine if it expresses a pattern expressible in forget_guard YAML schema (trigger + condition + action + recipe).
- If yes: migrate to YAML, delete Python function + call site, add pytest regression.
- If no (rule needs custom Python logic): keep as Python, document why in a "Python-required commission rules" list.
- Expected migration rate: 18-22 of 25 are YAML-expressible. 3-7 may stay Python (e.g. CIEU query + comparison).

**Acceptance**: boundary_enforcer.py post-migration ≤ 800 lines (from 2639). All 25 rules still fire (via YAML or residual Python). 0 pytest regression on tests/adapters/.

**Deadline**: 2026-05-20 (slower, riskier, can slip)

---

## G-1..G-4 guardrails (today) reframed as YAML rule additions

My principle document earlier today proposed 4 guardrails G-1..G-4 for Board-facing honesty. These should NOT become new hooks (my mistake in the Ethan spawn prompt). They should be added as forget_guard_rules.yaml entries:

- G-1 "Board-facing claim must contain artifact reference" → new forget_guard rule, trigger: Write+Edit on reports/ceo/board* paths, condition: content_contains keywords like "closed"/"done"/"处理", without artifact keywords like "commit"/"hash"/"grep"/"pytest", action: warn, recipe pointing to verify-first procedure
- G-2 "CEO claim emit CIEU audit" → trigger: same, action: cieu_event CEO_CLAIM_TO_BOARD
- G-3 "Board directive auto-track" → this is Omission not Commission; belongs in behavior_gov_rules.yaml (or post-unify, single YAML) as DeadlineCheck activated by UserPromptSubmit hook emitting DIRECTIVE_POSTED event
- G-4 "reply-pre-write verification" → forget_guard warn rule, trigger: Write on reports/ceo/board*, action: inject reminder

Ethan's current in-flight spawn (agentId af593e0564163c3af) is working on G-1..G-4 as new hooks. When it returns, redirect the specs into this unification plan — same 4 behaviors, but as YAML entries to the existing forget_guard engine post-Step-1 wiring.

---

## CEO's own role

- I do not implement any of Step 1/2/3. Those are Ryan + Maya.
- I do not write new hooks. I redirect Ethan's existing spawn (when it returns) into this unified plan.
- I keep my own OmissionEngine obligation (shipped earlier today) with 7-day deadline to see these 3 steps ship. If Ethan/Ryan/Maya miss dates, OmissionEngine blocks my tool calls.
- I write Board brief every Friday summarizing progress.

---

## Register 3 step-obligations for tracking (Ethan/Ryan/Maya actors)

OmissionEngine obligations to post for this unification work:
- Step 1 → actor=ryan, deadline=2026-04-29, "wire forget_guard to hook_wrapper"
- Step 2 → actor=maya, deadline=2026-05-06, "unify YAML schemas"
- Step 3 → actor=maya, deadline=2026-05-20, "migrate 25 Python rules to YAML"

These 3 registrations stays pending on Ethan's current spawn result — he should add them in his ruling pipeline.
