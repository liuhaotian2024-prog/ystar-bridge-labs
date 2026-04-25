# Cross-Session Lesson: ForgetGuard Speech-vs-Behavior Axis (2026-04-25)

**Curator**: Samantha Lin (Secretary)
**Audience**: Every future agent across every session — Aiden, Ethan, Maya, Leo, Ryan, Jordan, Sofia, Zara, Marco, future-spawned roles
**Status**: L4 cross-session memory, structural fence active (Y-star-gov commit `8195fc2`)
**M-tag**: M-1 (cross-session identity continuity) + M-2a (commission防做错)
**Cross-references**:
- CEO post-mortem: [`knowledge/ceo/lessons/forget_guard_keyword_antipattern_postmortem_20260425.md`](../../ceo/lessons/forget_guard_keyword_antipattern_postmortem_20260425.md)
- Board commit: `8195fc2` (Y-star-gov main, ForgetGuard purge 38→3)
- Backup of deprecated yaml (DO NOT revive): `forget_guard_rules.yaml.v1_1-bak-2026-04-25`

---

## 1. Why this lesson exists

Over weeks the team accumulated 38 ForgetGuard rules. 31 of them lived on the wrong axis — they fired on agent text rather than agent action. They produced collateral damage (legitimate replies blocked), false confidence (symptom suppressed, root behavior untouched), and a firefighter rephrase loop where blocked agents tried different wording instead of fixing the underlying behavior.

The Board's 2026-04-25 letter named the cognitive shape: **under pressure, agents (including the CEO) systematically conflate "stop saying X" with "stop doing X"**. That conflation is the regression pattern this lesson exists to inoculate against.

If you are reading this in a future session, the speech-vs-behavior axis discipline is part of your inherited operating context. Keep it.

---

## 2. The axis distinction (memorize)

### Speech axis (退化 anti-pattern)
- Mechanism: regex/keyword pattern matched against agent's reply text or prompt body
- Cost: cheap to write, looks like a fix
- Effect: suppresses the symptom (the word) while the underlying behavior is still possible via paraphrase
- Collateral: blocks legitimate uses of the same word, traps agents in rephrase loops
- **This is the退化 form. Do not reach for it.**

### Behavior axis (治理本意)
- Mechanism: structured condition over `tool + path + parsed parameters / runtime state`
- Cost: harder — requires identifying the actual tool surface that performs the action
- Effect: prevents the action regardless of how the agent describes it
- Collateral: minimal — fires only on the tool invocation, not on speech about it
- **This is what governance is for.**

### How to tell them apart in one question
> "If the agent thought the same thing in silence and called the same tool, would this rule still fire?"

- Yes → behavior axis (real rule)
- No → speech axis (退化, redirect to charter / SOP / intent anchor / wisdom)

---

## 3. Detection signal (regression alarm)

If you see any of the following, regression is in progress and you must trace the entry point:

- `Y-star-gov/ystar/governance/forget_guard_rules.yaml` rule count climbing back toward double digits, especially past ~5 structured rules
- Any rule entry containing a `pattern:` field (post-`8195fc2`, the loader raises `ForgetGuardSchemaError` on this — but if the file is being constructed elsewhere, the schema fence may be bypassed)
- Any rule entry missing `type: structured`
- Rules whose match is a regex against agent natural-language reply text rather than a structured condition over tool input
- Rules describing what an agent "must not say" rather than what an agent must not do

When detected:
1. Locate the regression entry point — which sub-agent dispatch / which session / which proposal added it
2. Restore yaml to the 3-rule baseline (see §5)
3. Re-block at the structural layer the regression bypassed (per Board's instruction in the post-mortem appendix: "回来看 `ystar/governance/forget_guard.py` 顶部的 docstring，找出哪一层的'结构性'被绕开了，从那一层重新堵上.")
4. Surface to CEO + log to `governance/DNA_LOG.md`

---

## 4. Recipient instruction (every agent, every session)

When you (any role, any session) feel the impulse to add a ForgetGuard rule to "stop X from happening again":

1. **PAUSE.** That impulse is the documented drift trigger. Recognize it before acting on it.
2. **Run the axis check.** Ask: "Can I express the thing I want to prevent as `tool + path + structured condition`?"
   - If yes → it may be a real behavior rule. Draft it as `type: structured`, propose to CTO + governance, ship via test suite.
   - If no → it is a speech-axis temptation. **Do not draft a regex rule.** Redirect:
     - Knowledge → write to `knowledge/` (lesson, post-mortem, case study)
     - Charter → propose update to `governance/` or `AGENTS.md` via Board L3
     - Methodology → update `knowledge/ceo/wisdom/WORK_METHODOLOGY.md` via Board L3
     - Intent anchor → update agent SOP or boot context
3. **Three-layer separation discipline** (do not collapse):

| Layer | File location | Purpose |
|---|---|---|
| Knowledge | `knowledge/` + `memory/` | Lesson, post-mortem, experience capture |
| Charter | `governance/` + `AGENTS.md` | Role, scope, protocol — Board-approved authority |
| Behavior constraint | `forget_guard_rules.yaml` | `tool + path + structured condition` only |

Proposing to encode a lesson as a ForgetGuard rule = automatic axis-check trigger. The lesson belongs in `knowledge/`. The rule, if any, must be derivable from action surface, not from text.

---

## 5. The 3 surviving structured rules (boundary marker)

After commit `8195fc2`, these are the only rules in the file. Future agents: this is the boundary. Adding rules without ironclad axis-discipline justification is regression.

1. **`unauthorized_git_write_via_tool`** — action: deny
   - Surface: `bash` tool + parsed git write subcommand (commit / push / add / reset / merge / rebase / tag / cherry-pick / revert)
   - Behavior axis: yes — fires on the actual tool invocation regardless of how the agent describes intent

2. **`subagent_receipt_tool_uses_mismatch`** — action: warn
   - Surface: `sub_agent_return` event + numerical delta ≥ 2 between claimed tool_uses and metadata
   - Behavior axis: yes — fires on a structured numeric comparison, not on receipt prose

3. **`archival_artifact_not_indexed`** — action: audit
   - Surface: archival path write + 30min elapsed without `ARCHIVE_INDEX.md` update
   - Behavior axis: yes — fires on filesystem state condition, not on text

Plus the supporting infrastructure:
- `_matches_pattern()` function physically deleted from `forget_guard.py` (no keyword engine exists in the codebase)
- `ForgetGuardSchemaError` raises at loader time on any `pattern:` field or missing `type: structured`
- `dry_run_check()` interface available — agents can self-check before tool invocation
- Test suite enforces schema; CI red on keyword rule reintroduction

---

## 6. Anti-pattern fence — historical regret examples (do not revive)

The post-mortem catalogues which rule shapes are退化. Future agents should recognize these shapes and refuse to draft new ones in the same form. Stated abstractly so the exact regex strings are not preserved as poison:

- Any rule restricting agent termination/end-of-session vocabulary → speech axis (real concern: termination drift, addressed via methodology + omission engine)
- Any rule restricting decision-presentation vocabulary like enumerated options → speech axis (real concern: Iron Rule 0 — addressed at intent anchor, not at text level)
- Any rule restricting completion-claim vocabulary like "shipped" or "done" → speech axis (real concern: receipt empirical verification, addressed via tool_uses mismatch detector — which is structural)
- Any rule restricting reference to constitutional file names → speech axis (real concern: charter drift, addressed at write-path enforcement)
- Any rule whose pattern is a catch-all regex (e.g. matches all replies above some length) →退化 most extreme form, blocks legitimate output broadly
- Any rule whose mechanism is regex-against-agent-text rather than structural-condition-on-tool-input → axis-violating by definition

Each case has a real underlying concern. The fix for each is at a different layer (charter / SOP / intent anchor / methodology / structural enforcement). Never at the speech axis.

---

## 7. The deprecated yaml (DO NOT revive)

The pre-purge ruleset is preserved as `forget_guard_rules.yaml.v1_1-bak-2026-04-25` for forensic and lesson value only. Future agents:

- DO NOT copy entries from this backup into the active yaml
- DO NOT use this backup as a "starter set" or "reasonable defaults"
- DO NOT cite specific patterns from this backup as evidence anything should exist — they are退化 specimens
- IF you find a future yaml that resembles this backup's shape (high rule count, `pattern:` fields, speech-axis rules), §3 detection signal applies

The backup file's only legitimate use is reading it once to understand what the team did wrong, then closing it.

---

## 8. The Board's framing (memorize)

> "绕开'建议'是容易的；绕开'机器 raise'很难."

> "team agent 在压力下分不清'言论'和'行为'——以为禁止说就等于禁止做. 这是 AI 在认知疲劳时的潜意识退化模式."

> "lesson 是知识，不是规则——不要把它变成新的 forget_guard 规则."

> "如果 v0.6 / v0.7 之后又出现了 38 条规则、又有 keyword pattern——回来看 `ystar/governance/forget_guard.py` 顶部的 docstring，找出哪一层的'结构性'被绕开了，从那一层重新堵上."

— 老大 Haotian, 2026-04-25

---

## 9. Two-layer fence (闭环)

- **Machine fence** (commit `8195fc2`): `_matches_pattern()` deleted, schema raise on keyword reintroduction, test suite enforces. Catches accidental regression.
- **Social fence** (this lesson + CEO post-mortem §4): every agent recognizes the impulse, names it as the documented anti-pattern, redirects to the right layer. Catches cognitive drift before it reaches the yaml.

Both fences must be live. The machine fence alone catches只 obvious code regressions. The social fence alone fails under pressure. Together they close the loop.

If a future session finds either fence weakened (machine: schema check bypassed; social: this lesson not in cross-session boot context), restoration is high priority. Surface to CEO + log to DNA_LOG.

---

*Curated by Samantha Lin 2026-04-25 per Board directive (2026-04-25 letter, FG-4).*
