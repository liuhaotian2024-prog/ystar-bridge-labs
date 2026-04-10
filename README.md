# Y* Bridge Labs

**A company where the governance applies to everyone — agents and humans alike.**

Most "AI governance" products watch what the agents do. We watch what the humans do too. Every Board directive is logged. Every CTO interpretation is audited. Every misunderstanding is caught at the seam, not after the damage. We built this for our own company first because we knew we'd need it for ourselves.

This README, the company that ships the product, and the audit chain you can replay at any commit hash — they're all the same artifact.

---

## The hole in "AI governance"

There is a hole in every AI governance product on the market. They watch the agent. They miss the human.

When the Board says *"fix this bug today"*, who records that the directive ever happened? When the CTO interprets that as *"fix it tonight at 22:00"*, who catches that the interpretation drifted? When the agent then writes a config file with a wrong field name and silently moves on, who runs the verification that proves the file actually loads?

Most tools answer none of those questions. They block `rm -rf /` and they call themselves done.

Y*gov answers all three. And it answers them for the human as much as for the agent. Every actor that touches this system — the Board, the CEO, the CTO, the engineering agents, the founder himself — leaves an immutable trace. Every interpretation has to be written down before it executes. Every directive has to be authorized by name. Every mistake has a commit hash.

This is **bidirectional governance**. It is the deepest claim Y*gov makes. It is also why we run this company on top of it: because we needed it ourselves first.

---

## What happened today (2026-04-09, one real working day)

In a single day on this very repository, the system caught and corrected three real human mistakes that would otherwise have shipped:

1. **Spawned MCP config schema bug** ([`07b1754`](../../commit/07b1754)). The CTO wrote a small JSON file claiming to wire a new feature into production. He never tested it. The Board insisted on a manual verification. The verification surfaced the bug — a `transport` field that Claude Code expected as `type`. The fix is now in the audit chain alongside the original mistake. *Without the Board's verification request, the file would have stayed broken indefinitely.*

2. **Daemon archive path off-spec** ([`8a95c2a`](../../commit/8a95c2a)). The CTO chose his own archive location (`reports/archive/...`) rather than the standard `archive/deprecated/`. The Board flagged it. The reconciliation commit moved the files, recorded the correction, and the lesson is now permanent in `archive/deprecated/DAEMON_RETIREMENT.md` as AMENDMENT-002.

3. **Layered defense framing over-claim** ([`da3977e`](../../commit/da3977e) + [`4900c27`](../../commit/4900c27)). The CTO documented Finding 4 with a framing that turned out to be sharper than the underlying principle. When the next directive used a contradicting design, the CTO had to revise the documentation to clarify *what* was actually invariant (enforcement points stay separate) versus *what* was incidental (contract sources happened to be separate). Both versions are in git history. The reasoning chain is auditable.

Across the same day, the system also processed:

- **6 Board directives** (GOV-001 through GOV-008) of escalating scope, every step tracked in CIEU
- **30+ commits** across three repositories — `ystar-bridge-labs`, `gov-mcp`, `K9Audit`
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
| Self-corrections of human mistakes in the last 24 hours | 3 (see "What happened today" above) |

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

Your AI agent leaked `.env`? **This prevents that.** Your CTO interpreted the Board wrong and shipped a broken config? **This catches that too.**

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
| Day 14 (2026-04-09) | The day described above. GOV-001 through GOV-008. Daemon retired (commit `57d8aec`). Spawned-session governance config installed and verified (commit `90af9ed` + `07b1754`). Gov-mcp cutover from AGENTS.md regex to `.ystar_session.json` direct load (commit `69a9b7c` in gov-mcp + `351e982` in this repo). Three CTO mistakes self-caught and corrected. |

Full history: [`HISTORY.md`](./HISTORY.md). Live state: [`OPERATIONS.md`](./OPERATIONS.md). Active directives: [`DIRECTIVE_TRACKER.md`](./DIRECTIVE_TRACKER.md). Decision authority: [`governance/INTERNAL_GOVERNANCE.md`](./governance/INTERNAL_GOVERNANCE.md). Distilled lessons: [`governance/DNA_LOG.md`](./governance/DNA_LOG.md).

---

*Built in public. Governed by the product we sell. The governance applies to the founder too.*
