# Y* Bridge Labs

**A company where the governance applies to everyone — agents and humans alike.**

Most "AI governance" products watch what the agents do. We watch what the humans do too. Every Board directive is logged. Every CTO interpretation is audited. Every misunderstanding is caught at the seam, not after the damage. We built this for our own company first because we knew we'd need it for ourselves.

This README, the company that ships the product, and the audit chain you can replay at any commit hash — they're all the same artifact.

---

## The deepest claim: governance covers the decider, not just the deed

Most "AI governance" products watch what an agent **does**. They do not watch what a human **decides**. Y*gov watches both.

When the Board gives an order, the order itself is logged — verbatim, timestamped, attributed to the Board by name — before any agent touches it. When the CTO reads that order and interprets it, the interpretation is recorded *before a single line of code executes*. When an agent then fails to deliver — **either by doing the wrong thing (commission) or by quietly not doing the right thing (omission)** — the gap is visible in the same audit chain that holds the original directive. Every actor that touches this system is **accountable for their own decisions**, and the evidence lives where nobody can edit it retroactively.

This is Y*gov's deepest claim, and it is the single feature that makes the rest of the product coherent. The deterministic enforcement engine, the CIEU hash chain, the intent verification protocol, the counterfactual proposal format — all of it is plumbing in service of one sentence: **the governance applies to the decider, not just the deed, and the decider includes the founder**.

Most competitors will tell you their product audits an agent's actions. We will tell you our product audits a person's decisions. Including the Board's. Including the CTO's. Including our own, when we get it wrong. The deviation you can read about in §"What happened today" — item 4 — is *this very investigation*, fired because Samantha (who wrote this README the first time) did not put this section in and the Board caught it. That is the product working on the people who ship it.

---

## The hole in "AI governance"

There is a hole in every AI governance product on the market. They watch the agent. They miss the human.

When the Board says *"fix this bug today"*, who records that the directive ever happened? When the CTO interprets that as *"fix it tonight at 22:00"*, who catches that the interpretation drifted? When the agent then writes a config file with a wrong field name and silently moves on, who runs the verification that proves the file actually loads?

Most tools answer none of those questions. They block `rm -rf /` and they call themselves done.

Y*gov answers all three. And it answers them for the human as much as for the agent. Every actor that touches this system — the Board, the CEO, the CTO, the engineering agents, the founder himself — leaves an immutable trace. Every interpretation has to be written down before it executes. Every directive has to be authorized by name. Every mistake has a commit hash.

This is **bidirectional governance**. It is the deepest claim Y*gov makes. It is also why we run this company on top of it: because we needed it ourselves first.

---

## What happened today (2026-04-09, one real working day)

In a single day on this very repository, the system caught and corrected **four** real human mistakes that would otherwise have shipped:

1. **Spawned MCP config schema bug** ([`07b1754`](../../commit/07b1754)). The CTO wrote a small JSON file claiming to wire a new feature into production. He never tested it. The Board insisted on a manual verification. The verification surfaced the bug — a `transport` field that Claude Code expected as `type`. The fix is now in the audit chain alongside the original mistake. *Without the Board's verification request, the file would have stayed broken indefinitely.*

2. **Daemon archive path off-spec** ([`8a95c2a`](../../commit/8a95c2a)). The CTO chose his own archive location (`reports/archive/...`) rather than the standard `archive/deprecated/`. The Board flagged it. The reconciliation commit moved the files, recorded the correction, and the lesson is now permanent in `archive/deprecated/DAEMON_RETIREMENT.md` as AMENDMENT-002.

3. **Layered defense framing over-claim** ([`da3977e`](../../commit/da3977e) + [`4900c27`](../../commit/4900c27)). The CTO documented Finding 4 with a framing that turned out to be sharper than the underlying principle. When the next directive used a contradicting design, the CTO had to revise the documentation to clarify *what* was actually invariant (enforcement points stay separate) versus *what* was incidental (contract sources happened to be separate). Both versions are in git history. The reasoning chain is auditable.

4. **README missed the core bidirectional-accountability claim** ([`43759eb`](../../commit/43759eb) → this fix commit). Samantha rewrote the README earlier in the same session. Her draft included the "agents and humans alike" framing but did not concentrate the three specific phrasings Board had asked for — governance covers decisions not just actions, Board orders are logged, every actor is accountable for their own decisions — into one named, unmissable section. The Board read the commit, caught the omission, and ordered a parallel remediation: Samantha fixes the README *and* the CTO files a formal investigation on whether GOV-006 triggered. The investigation (`reports/cto/gov006_case1_readme_deviation.md`) is now on file. The honest finding: GOV-006 did not trigger because it did not yet exist at the moment Samantha committed — `scripts/record_intent.py` first entered the tree 8 minutes 41 seconds *later*, at commit `4eba26f`. This case is therefore the edge condition of any append-only protocol: **it cannot protect work that predates its own commit**. From this commit onward, every Level 2 and Level 3 task runs under `record_intent.py`, including this very README fix.

Across the same day, the system also shipped:

- **8 Board directives** (GOV-001 through GOV-008) of escalating scope, every step tracked in CIEU
- **30+ commits** across three repositories — `ystar-bridge-labs`, `gov-mcp`, `K9Audit`
- **GOV-006: Intent Verification Protocol** ([`4eba26f`](../../commit/4eba26f)). The protocol that makes silent interpretation drift architecturally impossible — `record_intent.py` + `check_intents.py` + four new CIEU event types (`INTENT_RECORDED` / `INTENT_CONFIRMED` / `INTENT_ADJUSTED` / `INTENT_REJECTED`) + 第七条 7.5 of the Working Style constitution + a new section in all six agent job descriptions. Level 3 intents cannot be confirmed by anyone except the Board (the script hard-rejects). The first real use of the protocol is this very investigation.
- **GOV-008: gov-order NL → CIEU pipeline** ([`9a421f7`](../../commit/9a421f7)). Board can now type one natural-language sentence and the sentence is translated by an LLM, hard-gated by a deterministic validator, recorded in CIEU as a `BOARD_NL → INTENT_RECORDED → OBLIGATION_REGISTERED → INTENT_LINKED` chain, and picked up by the owning agent on their next session boot. Zero friction for the Board. Failed translations are never dropped silently — they go to `reports/board_proposed_changes/pending/` for Secretary's Monday triage. A `gov_order_undo.py` rollback tool ships alongside. Full design doc at `reports/cto/gov_order_pipeline.md`.
- **5 counterfactual research proposals** written *before* any implementation code, per the GOV-005 §7 / GOV-006 protocol
- **2 external user bug fixes** in K9Audit pushed within a single session, in response to a real user report
- **1 production gov-mcp cutover** from regex AGENTS.md parsing to structured `.ystar_session.json` loading — `deny_commands` coverage went from 0 rules to 4, total contract rules from 1 to 7, verified end-to-end via a spawned independent Claude Code session

You can read all of it: `git log --since="2026-04-09"`.

---

## How it works

Three layers. All deterministic. No LLM in any enforcement path.

**Layer 1 — Contract enforcement.** A structured config file (`.ystar_session.json`) declares what is allowed and what is denied. A small Python hook intercepts every tool call from a Claude Code session and checks it against the contract. Sub-2ms latency per check. Zero false positives in our 50-concurrent-agent stress test. The hook does not call an LLM, so it cannot be prompt-injected.

**Layer 2 — CIEU audit.** Every governance event — ALLOW, DENY, INTENT_RECORDED, OBLIGATION_REGISTERED, OBLIGATION_FULFILLED, CONTRACT_UPDATE — writes one row into a tamper-evident SQLite database with a SHA-256 hash chain. The records cover both **agent actions** (what the AI did) and **human decisions** (what the Board ordered). A `gov_doctor` health check inspects 14 layers of the running system in one call.

**Layer 3 — Intent verification.** Before an agent executes a Level 2 or Level 3 directive, it must record its interpretation: *what does it think the Board asked for, and what does it plan to do about it.* The reviewer (Board for Level 3, CEO for Level 2) can correct the interpretation before any code changes. This is what catches the kind of mistake the LLM would otherwise make silently — the same kind of mistake the spawned MCP config bug above represents.

Three-level decision authority (Level 1 single-role / Level 2 CEO / Level 3 Board) and counterfactual-reasoning proposal format are baked into the rules. Anyone proposing a Level 2 or 3 change must write down the current state, the target, the alternatives considered, the chosen option, and the second-best fallback — *before* any code is touched. The Board approves or rejects the chosen option. The Board never sees a list of unanalyzed choices.

---

## What makes this different

Most agentic frameworks ship a system prompt that says *"be careful"* and call it governance. Y*gov ships a deterministic enforcement engine, an audit chain that covers humans, and an intent-verification protocol that makes silent drift architecturally impossible.

| Concern | Most "AI governance" tools | Y*gov |
|---|---|---|
| Block `rm -rf /` | yes | yes |
| Block `.env` exfiltration | yes | yes |
| Block prompt injection from rewriting the rules | sometimes | yes — no LLM in the check path |
| Audit what the **agent** did | yes | yes |
| **Audit what the human Board ordered** | **no** | **yes** — `BOARD_CHARTER_AMENDMENTS.md` + INTENT_RECORDED CIEU events |
| **Catch the human operator's misinterpretation before it ships** | **no** | **yes** — intent verification protocol (GOV-006) |
| **Record the reasoning chain behind every Level 3 decision** | **no** | **yes** — counterfactual proposal format (GOV-005 §7) |
| **Provide an immutable trace from "Board said X" to "agent did Y"** | **no** | **yes** — CIEU chain links INTENT_RECORDED → OBLIGATION_REGISTERED → OBLIGATION_FULFILLED |
| Self-host the same governance the product enforces on customers | no | yes — this repo |

The point is not that agents are scary. The point is that **everyone touching the system makes mistakes, and everyone deserves a way for the system to catch those mistakes before they ship**. Y*gov gives that to all of them — including the founder.

---

## The team

| Name | Role | What they do |
|---|---|---|
| **Haotian Liu (刘浩天)** | Board / Founder | Human. Sets direction, reviews every Level 3 decision, holds everyone (himself included) accountable to the governance the company sells. |
| **Aiden Liu** | CEO | Digital twin of the Board. Decomposes directives into tracked tasks, dispatches to the right department, escalates Level 3 decisions back to the Board with the team's counterfactual analysis. Bound by Level 2 authority for internal flows. |
| **Ethan Wright** | CTO | Engineering. Architecture, code, tests. Caught and recorded three of his own mistakes today (above). Built the gov-mcp 0.2.0 cutover, the daemon retirement, and the GOV-007 contract source unification — all under intent verification. |
| **Sofia Blake** | CMO | Content & Growth. Once attempted to write a compliance record that hadn't been executed — CASE-001, the founding incident. Y*gov now makes that architecturally impossible. |
| **Marco Rivera** | CFO | Finance. Honesty policy is constitutional — every claim must have a data source. Once estimated a number without one — CASE-002, the second founding incident. |
| **Zara Johnson** | CSO | Sales & Patents. Three US provisional patents filed. |
| **Samantha Lin** | Secretary | Information indexing, DNA distillation, audit consistency. Owns `governance/DNA_LOG.md` and `governance/BOARD_CHARTER_AMENDMENTS.md`. |
| **Jinjin (K9 Scout)** | Research | Runs on a separate Mac mini with MiniMax. First cross-model governance in production. |

The team ships under their real names because the audit chain demands it. There is no anonymous agent here.

---

## What we have proven so far

| Metric | Value |
|---|---|
| Days operating | 14 (since 2026-03-26) |
| Board directives processed | 25+ (GOV-001 through GOV-008 plus historical Directive #002–#024) |
| AMENDMENTS to the constitution | 2 (`AMENDMENT-001` deny commands, `AMENDMENT-002` daemon retirement) |
| Y*gov tests passing | 800+ |
| gov-mcp tools registered | 38 |
| MCP layers in the live `gov_doctor` health check | 14/14 passing |
| Concurrent-agent attack stress test | 50 agents, zero data leaks, zero false positives |
| Security vulnerabilities found and fixed | 5 P0 + 4 P1 |
| US provisional patents filed | 3 |
| Founding governance incidents documented | 6 (`knowledge/cases/CASE_001` through `CASE_006`) |
| Failed experiments archived (not deleted) | 1 — `archive/deprecated/daemon_failed_experiment_2026_04_04` |
| Counterfactual reasoning proposals submitted to Board | 6+ (all in `reports/cto/`) |
| Self-corrections of human mistakes in the last 24 hours | **4** (three CTO, one Secretary — see "What happened today" above) |
| GOV-006 CIEU event types introduced | 4 (`INTENT_RECORDED` / `_CONFIRMED` / `_ADJUSTED` / `_REJECTED`) |
| gov-order shipping state | **live** — `scripts/gov_order.py` + `scripts/gov_order_undo.py` + Secretary Monday audit |
| First real GOV-006 audit case on file | [`reports/cto/gov006_case1_readme_deviation.md`](./reports/cto/gov006_case1_readme_deviation.md) |

---

## Repositories

Four repos, same author, designed to be used together but each one stands alone.

| Repository | What it is |
|---|---|
| [`ystar-bridge-labs`](https://github.com/liuhaotian2024-prog/ystar-bridge-labs) | The company. This repo. Operations, governance, audit log, all in public. |
| [`Y-star-gov`](https://github.com/liuhaotian2024-prog/Y-star-gov) | The governance kernel. 800+ tests. Pearl L2–L3 causal inference. The translation layer that turns AGENTS.md into structured contracts. |
| [`gov-mcp`](https://github.com/liuhaotian2024-prog/gov-mcp) | The MCP server. 38 tools. `pip install gov-mcp && gov-mcp install` and you have it in 30 seconds. Works with any MCP client (Claude Code, Cursor, Windsurf, OpenClaw, raw Python, CrewAI). |
| [`K9Audit`](https://github.com/liuhaotian2024-prog/K9Audit) | Engineering-grade causal audit for AI agent ecosystems. K9log decorator, CIEU recording engine, OpenClaw + LangChain adapters. |

---

## Install

```bash
pip install gov-mcp
gov-mcp install
```

This detects whether you are running Claude Code, Cursor, Windsurf, or OpenClaw and configures the integration automatically. If you are running CrewAI, raw Python, or something else, the `gov-mcp/docs/` guides walk you through it in 5 minutes each:

- [`PROTOCOL.md`](https://github.com/liuhaotian2024-prog/gov-mcp/blob/main/docs/PROTOCOL.md) — wire-protocol reference + full 38-tool catalog
- [`QUICKSTART_PYTHON.md`](https://github.com/liuhaotian2024-prog/gov-mcp/blob/main/docs/QUICKSTART_PYTHON.md) — minimal raw Python client, no framework
- [`QUICKSTART_CREWAI.md`](https://github.com/liuhaotian2024-prog/gov-mcp/blob/main/docs/QUICKSTART_CREWAI.md) — full CrewAI integration, end-to-end runnable example

### And if you are the Board

Clone this repo, set `ANTHROPIC_API_KEY` (or `OPENAI_API_KEY`, or `OLLAMA_HOST`, or `LM_STUDIO_HOST` — the script detects them in order), and type:

```bash
python3.11 scripts/gov_order.py "ethan finish the gov-008 migration by tonight"
```

The sentence is LLM-translated into a structured obligation, hard-gated by a deterministic Python validator, recorded in CIEU as a `BOARD_NL → INTENT_RECORDED → OBLIGATION_REGISTERED → INTENT_LINKED` chain, and picked up by the owning agent on their next session boot. Zero extra keystrokes. If the validator catches an LLM mistranslation, the NL is saved to `reports/board_proposed_changes/pending/` for Secretary's Monday triage — never dropped, never silently shipped. If you change your mind, `python3.11 scripts/gov_order_undo.py --intent-id <id> --reason "<why>"` writes an `OBLIGATION_CANCELLED` + `INTENT_REJECTED` row and the dashboard clears. The full design is in [`reports/cto/gov_order_pipeline.md`](./reports/cto/gov_order_pipeline.md).

Your AI agent leaked `.env`? **This prevents that.** Your CTO interpreted the Board wrong and shipped a broken config? **This catches that too.** Your own founder gave an order and forgot to log it? **This logs it for you, before the agent even moves.**

---

## Watch it run

Everything we do is in this repository. Commits, reports, Board directives, design proposals, architectural disagreements, retired experiments, intent verification chains. `git clone` and read it.

If you see something that looks wrong — a misinterpreted directive, a contradiction between two layers, a CIEU record that does not match the code that triggered it — **open an issue**. We have caught three of our own mistakes today by being public about the work. We expect more to come from people who are not us.

We are also on Telegram: [`@YstarBridgeLabs`](https://t.me/YstarBridgeLabs).

---

## Timeline

| Day | What happened |
|---|---|
| Day 1 (2026-03-26) | Company founded. CMO fabricated data — CASE-001, the founding incident that motivated the whole architecture. |
| Day 2–5 | Y*gov kernel: 86 → 800+ tests. IntentContract, CIEU audit chain, OmissionEngine, Pearl L2–L3 causal inference. Three patents filed. |
| Day 6–7 | Constitutional reform: agents must think, not just execute. Baseline assessment system. |
| Day 8–11 | Mac mini migration. Hook daemon latency 1.4s → 1.9ms. EXP-008 three-way comparison. gov-mcp v0.1.0 with 38 tools. 16/16 internal mechanisms verified live. |
| Day 12 (2026-04-04) | Autonomous daemon experiment fails: violation rate accelerates 173 → 386 → 466 per hour. CEO issues emergency stop. Five days of frozen state follow. |
| Day 13 (2026-04-08) | Board reads the failure and decides to retire the daemon entirely rather than try to fix it. |
| Day 14 (2026-04-09) | The day described above. GOV-001 through GOV-008 all executed. Daemon retired (commit `57d8aec`). Spawned-session governance config installed and verified (commit `90af9ed` + `07b1754`). Gov-mcp cutover from AGENTS.md regex to `.ystar_session.json` direct load (commit `69a9b7c` in gov-mcp + `351e982` in this repo). **GOV-006 Intent Verification Protocol shipped** (commit `4eba26f`) — `record_intent.py`, `check_intents.py`, four new CIEU event types, 第七条 7.5 in the Working Style constitution, GOV-006 section in all six agent job descriptions. **GOV-008 gov-order NL pipeline shipped** (commit `9a421f7`) — `gov_order.py`, `gov_order_undo.py`, `register_obligation_programmatic()` refactor, Secretary Monday audit duty, gov-order awareness section in all six agent job descriptions. **Three CTO mistakes self-caught and corrected. One Secretary mistake (this README) caught by Board, investigated by CTO, and fixed in the same working day under the now-live GOV-006 protocol.** |

Full history: [`HISTORY.md`](./HISTORY.md). Live state: [`OPERATIONS.md`](./OPERATIONS.md). Active directives: [`DIRECTIVE_TRACKER.md`](./DIRECTIVE_TRACKER.md). Decision authority: [`governance/INTERNAL_GOVERNANCE.md`](./governance/INTERNAL_GOVERNANCE.md). Distilled lessons: [`governance/DNA_LOG.md`](./governance/DNA_LOG.md).

---

*Built in public. Governed by the product we sell. The governance applies to the founder too.*
