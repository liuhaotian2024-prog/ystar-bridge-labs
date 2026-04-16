# Y* Bridge Labs

**A company where the governance applies to everyone — agents and humans alike.**

Most "AI governance" products watch what the agents do. We watch what the humans do too. Every Board directive is logged. Every CTO interpretation is audited. Every misunderstanding is caught at the seam, not after the damage. We built this for our own company first because we knew we'd need it for ourselves.

This README, the company that ships the product, and the audit chain you can replay at any commit hash — they're all the same artifact.

---

## CZL: Causal Zero Loop — Making Agents Prove They Worked

**Y\* Bridge Labs 的核心方法论**，2026-04-15 创造。

CZL 五元组：
- **Y\***：人类定义的完成标准（不由 agent 自动生成）
- **Xt**：当前状态快照
- **U**：行动
- **Yt+1**：实际结果
- **Rt+1 = distance(Yt+1, Y\*)** — 量化的因果残差

**Rt+1=0 才算真完成**。Rt+1≠0 继续执行，不飘逸。

### 核心文档 (canonical locations)

- `governance/WORKING_STYLE.md §第十二条` — CZL 任务工作法
- `AGENTS.md §Session-Level Y* Doctrine` — Session-level 5 条硬约束
- `AGENTS.md §Rule Verification Three-Layer Doctrine` — 规则写了/在跑/在拦三层
- `governance/sub_agent_atomic_dispatch.md` — Atomic Dispatch (1 dispatch = 1 deliverable)
- `knowledge/shared/methodology_assets_20260415.md` — 12 项方法论完整 lookup index
- `scripts/k9_audit_v3.py` — 3-Layer audit (Liveness + Causal Chain + Invariant)
- `.czl_subgoals.json` — HiAgent working memory 子目标树 (CEO dogfood live)

### 2026-04-15 实证数据

- 5 campaigns 全 Rt+1=0 ship
- Architecture Fix Campaign: 72 tool_uses / 10 件 constitutional ship
- Pre-atomic baseline: 47 tool_uses / 0 件 (60x 效率改善)
- 100+ live CIEU events 作可审计证据链

### 与其他框架对比

CZL vs Cursor (自承 "periodic fresh starts to combat drift")
CZL vs VeriMAP (EACL 2026, 子任务局部验证，无顶层 Y\*)
CZL vs Ralph Loop (pass/fail 布尔，无方向性 Rt+1)

详见 `reports/ceo/campaign_v7_business_pivot_plan_20260415.md`。

---

## The deepest claim: governance covers the decider, not just the deed

Most "AI governance" products watch what an agent **does**. They do not watch what a human **decides**. Y*gov watches both.

When the Board gives an order, the order itself is logged — verbatim, timestamped, attributed to the Board by name — before any agent touches it. When the CTO reads that order and interprets it, the interpretation is recorded *before a single line of code executes*. When an agent then fails to deliver — **either by doing the wrong thing (commission) or by quietly not doing the right thing (omission)** — the gap is visible in the same audit chain that holds the original directive. Every actor that touches this system is **accountable for their own decisions**, and the evidence lives where nobody can edit it retroactively.

This is Y*gov's deepest claim, and it is the single feature that makes the rest of the product coherent. The deterministic enforcement engine, the CIEU hash chain, the intent verification protocol, the counterfactual proposal format — all of it is plumbing in service of one sentence: **the governance applies to the decider, not just the deed, and the decider includes the founder**.

Most competitors will tell you their product audits an agent's actions. We will tell you our product audits a person's decisions. Including the Board's. Including the CTO's. Including our own, when we get it wrong.

---

## The hole in "AI governance"

There is a hole in every AI governance product on the market. They watch the agent. They miss the human.

When the Board says *"fix this bug today"*, who records that the directive ever happened? When the CTO interprets that as *"fix it tonight at 22:00"*, who catches that the interpretation drifted? When the agent then writes a config file with a wrong field name and silently moves on, who runs the verification that proves the file actually loads?

Most tools answer none of those questions. They block `rm -rf /` and they call themselves done.

Y*gov answers all three. And it answers them for the human as much as for the agent. Every actor that touches this system — the Board, the CEO, the CTO, the engineering agents, the founder himself — leaves an immutable trace. Every interpretation has to be written down before it executes. Every directive has to be authorized by name. Every mistake has a commit hash.

This is **bidirectional governance**. It is the deepest claim Y*gov makes. It is also why we run this company on top of it: because we needed it ourselves first.

---

## How it works

Three layers. All deterministic. No LLM in any enforcement path.

**Layer 1 — Contract enforcement.** A structured config file (`.ystar_session.json`) declares what is allowed and what is denied. A small Python hook intercepts every tool call from a Claude Code session and checks it against the contract. Sub-2ms latency per check. Zero false positives in our 50-concurrent-agent stress test. The hook does not call an LLM, so it cannot be prompt-injected.

**Layer 2 — CIEU audit.** Every governance event — ALLOW, DENY, INTENT_RECORDED, OBLIGATION_REGISTERED, OBLIGATION_FULFILLED, CONTRACT_UPDATE — writes one row into a tamper-evident SQLite database with a SHA-256 hash chain. The records cover both **agent actions** (what the AI did) and **human decisions** (what the Board ordered). A `gov_doctor` health check inspects 14 layers of the running system in one call.

**Layer 3 — Intent verification.** Before an agent executes a Level 2 or Level 3 directive, it must record its interpretation: *what does it think the Board asked for, and what does it plan to do about it.* The reviewer (Board for Level 3, CEO for Level 2) can correct the interpretation before any code changes. This is what catches the kind of mistake an LLM would otherwise make silently.

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
| **Catch agents writing outside their role before the write commits** | **no** | **yes** — CROBA pre-action boundary injection (AMENDMENT-025) |
| Self-host the same governance the product enforces on customers | no | yes — this repo |

The point is not that agents are scary. The point is that **everyone touching the system makes mistakes, and everyone deserves a way for the system to catch those mistakes before they ship**. Y*gov gives that to all of them — including the founder.

---

## The team

| Name | Role | What they do |
|---|---|---|
| **Haotian Liu** | Board / Founder | Human. Sets direction, reviews every Level 3 decision, holds everyone (himself included) accountable to the governance the company sells. |
| **Aiden Liu** | CEO | Digital twin of the Board. Decomposes directives into tracked tasks, dispatches to the right department, escalates Level 3 decisions back to the Board with the team's counterfactual analysis. Bound by Level 2 authority for internal flows. |
| **Ethan Wright** | CTO | Engineering. Architecture, code, tests. Caught and recorded three of his own mistakes during one working day under intent verification. |
| **Sofia Blake** | CMO | Content & Growth. Once attempted to write a compliance record that hadn't been executed — CASE-001, the founding incident. Y*gov now makes that architecturally impossible. |
| **Marco Rivera** | CFO | Finance. Honesty policy is constitutional — every claim must have a data source. Once estimated a number without one — CASE-002, the second founding incident. |
| **Zara Johnson** | CSO | Sales & Patents. Three US provisional patents filed. |
| **Samantha Lin** | Secretary | Information indexing, DNA distillation, audit consistency. Owns `governance/DNA_LOG.md` and `governance/BOARD_CHARTER_AMENDMENTS.md`. |
| **Leo / Maya / Ryan / Jordan** | Engineers | Kernel, governance, platform, domains. Four specialist sub-agents under the CTO. |
| **Jinjin (K9 Scout)** | Research | Runs on a separate model (MiniMax). First cross-model governance in production. |

The team ships under their real names because the audit chain demands it. There is no anonymous agent here.

---

## What we have proven so far

| Metric | Value |
|---|---|
| Days operating | 18 (since 2026-03-26) |
| Board directives processed | 25+ (GOV-001 through GOV-008 plus historical Directive #002–#024) |
| AMENDMENTs to the constitution | 25+ (`AMENDMENT-001` through `AMENDMENT-027`) |
| Y*gov tests passing | 800+ |
| gov-mcp tools registered | 38 |
| MCP layers in the live `gov_doctor` health check | 14/14 passing |
| Concurrent-agent attack stress test | 50 agents, zero data leaks, zero false positives |
| Security vulnerabilities found and fixed | 5 P0 + 4 P1 |
| US provisional patents filed | 3 |
| Founding governance incidents documented | 6 (`knowledge/cases/CASE_001` through `CASE_006`) |
| Failed experiments archived (not deleted) | 1 — `archive/deprecated/daemon_failed_experiment_2026_04_04` |
| Live pre-action boundary catches (CROBA) | 2 real cases on file (CTO + CEO both blocked) |
| GOV-006 CIEU event types introduced | 4 (`INTENT_RECORDED` / `_CONFIRMED` / `_ADJUSTED` / `_REJECTED`) |
| gov-order shipping state | **live** — `scripts/gov_order.py` + `scripts/gov_order_undo.py` + Secretary Monday audit |

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

The sentence is LLM-translated into a structured obligation, hard-gated by a deterministic Python validator, recorded in CIEU as a `BOARD_NL → INTENT_RECORDED → OBLIGATION_REGISTERED → INTENT_LINKED` chain, and picked up by the owning agent on their next session boot. Zero extra keystrokes. If the validator catches an LLM mistranslation, the NL is saved to `reports/board_proposed_changes/pending/` for Secretary's Monday triage — never dropped, never silently shipped.

Your AI agent leaked `.env`? **This prevents that.** Your CTO interpreted the Board wrong and shipped a broken config? **This catches that too.** Your own founder gave an order and forgot to log it? **This logs it for you, before the agent even moves.**

---

## Watch it run

Everything we do is in this repository. Commits, reports, Board directives, design proposals, architectural disagreements, retired experiments, intent verification chains. `git clone` and read it.

If you see something that looks wrong — a misinterpreted directive, a contradiction between two layers, a CIEU record that does not match the code that triggered it — **open an issue**. We have caught our own mistakes repeatedly by being public about the work. We expect more to come from people who are not us.

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
| Day 14 (2026-04-09) | GOV-001 through GOV-008 all executed. Daemon retired. Spawned-session governance config installed. gov-mcp cutover from AGENTS.md regex to `.ystar_session.json` direct load. **GOV-006 Intent Verification Protocol shipped.** **GOV-008 gov-order NL pipeline shipped.** |
| Day 15–18 (2026-04-10 → 2026-04-13) | AMENDMENT-011 through AMENDMENT-027. CROBA pre-action boundary enforcement ships. Two live catches on file (CTO + CEO both blocked attempting cross-role writes). Self-heal P2 whitelist ships. Continuity Guardian v2 with role-specific DNA slicing. |

Full history: [`HISTORY.md`](./HISTORY.md). Live state: [`OPERATIONS.md`](./OPERATIONS.md). Active directives: [`DIRECTIVE_TRACKER.md`](./DIRECTIVE_TRACKER.md). Decision authority: [`governance/INTERNAL_GOVERNANCE.md`](./governance/INTERNAL_GOVERNANCE.md). Distilled lessons: [`governance/DNA_LOG.md`](./governance/DNA_LOG.md).

---

## Daily Morning Briefs

Historical morning briefs, one per day. Each brief is the CEO's autonomous overnight report for the Board. Click the date to read.

- [2026-04-13](./reports/daily/2026-04-13_morning_summary.md) — Phase 2 experiment matrix; AMENDMENT-011/012/013 proposals; four pain-point codification (serial dispatch, Ryan context ceiling, governance deadlock, truth-source split)
- [2026-04-12](./reports/daily/2026-04-12_morning.md) — Pre-Phase-2 state; CEO self-assessment
- [2026-04-11](./reports/daily/2026-04-11_morning_final.md) — Mac-only single-machine consolidation (AMENDMENT-004)
- [2026-04-02](./reports/daily/2026-04-02.md) — Early team-definition pass
- [2026-04-01](./reports/daily/2026-04-01.md) — Day-1 of April autonomous run

Briefs prior to 2026-04-01 are in [`reports/daily/`](./reports/daily/). Historical briefs may be in Chinese (archival internal working notes); this README and all top-level reports are English-only.

---

## Major Insights

Deep discoveries from Y* Bridge Labs operations. Each insight is one report. These are the findings that changed how we build the product, not daily status.

- [Scenario C — CROBA pre-action boundary violation, first live catches](./reports/insights/scenario_c_croba_discovery_20260414_en.md) — 2026-04-14 — Two agents (CTO Ethan, then CEO Aiden himself) attempted cross-role writes. The governance layer injected a contract-violation warning into the next prompt before either agent re-tried. Both self-corrected. Zero Board intervention. No prior art in LangChain / AutoGen / CrewAI / NeMo Guardrails. **This is the real USP.**
- [Full insights index](./reports/insights/INSIGHTS_INDEX.md) — chronological catalogue of every operational discovery since Day 1 (founding incidents, experiment verdicts, pain-point codifications, architectural pivots).

---

*Built in public. Governed by the product we sell. The governance applies to the founder too.*
