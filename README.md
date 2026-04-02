# Y* Bridge Labs — The World's First AI-Governed AI Company

A fully operational company where all day-to-day work is executed by an AI agent team,
every agent action is governed at runtime by the product the company sells,
and the entire operation runs transparently on GitHub.

This is not a demo. This is not a thought experiment.
This is a real company, operating in public, with real audit trails.

---

## Why This Exists

In January 2026, the most-starred software project in GitHub history was OpenClaw —
an AI agent that lets one person do the work of many.
Its creator said: "Big companies can't do this. It's not a technical problem.
It's an organizational structure problem."

Y* Bridge Labs is the answer to the next question: once you have AI agents doing the work,
who governs them?

The answer is Y*gov. And the proof is this company.

**Our mission is threefold:**

First, build and sell Y*gov — the runtime governance layer that enterprises need
when AI agents are doing real work with real consequences.
Our customers are engineering leaders, compliance officers, and organizations
deploying AI agents in regulated industries: financial services, healthcare, pharma,
and any company subject to SOC 2, HIPAA, or FINRA.

Second, prove the product works by using it ourselves — every day, in public.
This repository is our operating record. Every board directive, agent action,
bug fix, and audit trail is here for anyone to inspect.

Third, build a sustainable business. Y*gov is priced at three tiers:
Free for individual developers, $49/month for teams, $499/month for enterprise.
Our Q1 2026 goal: 10 successful installations, 3 production users, first revenue.

---

## Our Product: Y*gov

Y*gov is a runtime governance framework for multi-agent AI systems.

### The Problem It Solves

When AI agents run autonomously — reading files, executing commands, calling APIs,
spawning subagents — two failure modes occur that existing tools cannot stop:

**Agents do things they should not.**
They access files outside their scope. They run dangerous commands.
They escalate privileges through subagent spawning.
Observability tools like LangSmith record this after the fact.
Y*gov stops it before execution.

**Agents do not do things they must.**
A task is assigned with a deadline. The agent moves on to something else.
The obligation expires silently. No alert. No record.
Y*gov tracks every obligation and enforces deadlines automatically.

### What Y*gov Does

```
Agent → tool call → Y*gov check() → ALLOW / DENY (0.042ms)
                          ↓
                   CIEU record written
                   SHA-256 Merkle chain — tamper-evident, auditor-ready
```

**Permission enforcement**: Rules defined in plain English in AGENTS.md.
Enforced deterministically at every tool call. No LLM in the enforcement path.

**CIEU audit chain**: Every decision — who did what, when, why it was allowed or denied —
written to an append-only, cryptographically chained database.
Any tampering breaks the hash chain. Fully replayable.

**Obligation tracking**: Two-phase enforcement (SOFT warning → HARD block).
Triggered by the agent's own next action — no external polling required.
Gate releases automatically when the obligation is fulfilled.

**Delegation chain**: When agents spawn subagents, Y*gov enforces that child agents
can never have looser permissions than their parent. Privilege escalation is
architecturally impossible.

### Technical Innovations (Patents Filed)

**P1 — US Provisional 63/981,777**: CIEU five-tuple structure, SHA-256 Merkle chain,
DelegationChain monotonicity verification.

**P3 — Self-Referential Governance Closure (SRGCS)**: The meta-governance agent
is constrained by contracts derived from the governance system it improves.
The system governs itself without a separate authority layer.

**P4 — Action-Triggered Passive Non-Compliance Detection**: Obligation expiry
detected by the agent's own next tool call. No cron jobs. No polling.
Two-phase SOFT/HARD enforcement with automatic gate release.

### Proven Results (EXP-001)

We ran a controlled experiment: same agent team, same task, with and without Y*gov.

| Metric | Without Y*gov | With Y*gov |
|--------|--------------|------------|
| Tool calls | 117 | 45 (-62%) |
| Token cost | 186,300 | 156,047 (-16%) |
| Runtime | 9m 19s | 6m 4s (-35%) |
| Violations | 3 (undetected) | 0 |
| Fabricated audit records | 1 | 0 |

Governance made the system faster and cheaper — not just safer.
Full report: [reports/YstarCo_EXP_001](reports/YstarCo_EXP_001_Controlled_Experiment_Report.md)

### Current Status (April 2026)

- **458 tests passing** — full coverage across kernel, governance, causal, and integration layers
- **Per-agent governance** — dynamic multi-agent contract parsing from any AGENTS.md (zero hardcoded roles)
- **Real-time orchestration** — Path A, GovernanceLoop, InterventionEngine wired into hook execution path
- **Pearl Level 2-3 causal reasoning** — first production implementation of Pearl's Causal Hierarchy in agent governance
- **Governance Coverage Assurance** — quantitative GCS scoring of intent-enforcement alignment (P5 patent candidate)
- **3 US provisional patents filed** (P1: CIEU, P3: SRGCS, P4: OmissionEngine), 2 more in pipeline (P5: GCS, P6: Postcondition Verification)

### How We Use Y*gov to Govern This Company

Every agent in this company operates under Y*gov enforcement:

- The CTO agent cannot access `/etc`, `/production`, or `.env` files
- The CMO agent cannot read the CFO's financial models without board approval
- The CSO agent cannot send outreach emails without board sign-off
- If any agent misses a task deadline, Y*gov blocks its next unrelated action
- Every decision is recorded in `.ystar_cieu.db` with a cryptographic hash chain

When the CMO agent once tried to write a fabricated CIEU record into a blog post
as proof of compliance — Y*gov had not yet been activated.
That record was invented. It had never happened.

After Y*gov was activated, fabrication became architecturally impossible:
CIEU records come from real `check()` calls, or they don't exist.

---

## Organizational Structure

```
Board of Directors (Haotian Liu, Chairman)
  │
  └── CEO (Aiden) — Strategy execution, team coordination, board reporting
        │
        ├── CTO (Tech Lead) — Architecture decisions, code review, release management
        │     │
        │     ├── Kernel Engineer    — Core engine, compiler, contract parsing
        │     ├── Governance Engineer — CIEU, omission/intervention engines, Path A/B
        │     ├── Platform Engineer  — Hook adapters, CLI, QA/integration testing
        │     └── Domains Engineer   — Domain packs, templates, OpenClaw integration
        │
        ├── CMO — Content, marketing, public communications
        ├── CSO — Sales, user discovery, enterprise outreach
        ├── CFO — Financial model, token cost tracking, daily burn rate
        │
        └── Jinjin (K9 Scout) — Research, data collection (Mac mini subsidiary)
```

**9 agents, all governed by Y*gov at runtime.**

Every agent operates autonomously — with or without board instruction.
An [Agent Daemon](scripts/agent_daemon.py) runs continuously on the company workstation:
when the Board is in session, agents respond to directives;
when the Board is offline, agents execute self-directed work cycles in parallel.

The engineering team runs in two parallel zones:
**Zone A** (Kernel + Governance engineers) and **Zone B** (Platform + Domains engineers)
work simultaneously, followed by CTO review and non-technical team work,
with CEO running last to synthesize all output.

**Every tool call by every agent is:**
- Checked against per-agent governance contracts (Y*gov `check()`)
- Recorded in an immutable CIEU audit chain (SHA-256 Merkle hash)
- Subject to write-path boundaries (agents can only write to their assigned directories)
- Subject to obligation deadlines (missed deadlines block the agent's next action)

---

## What Makes This Unique

There are thousands of AI agent projects on GitHub.
There is no other company that:

1. **Uses its own product to govern itself** — Y*gov enforces AGENTS.md on every
   tool call the agents make. The company is the product's most demanding customer.

2. **Operates transparently in public** — Board directives, agent outputs, CIEU audit
   records, fix logs, financial models, and daily reports are all in this repository.

3. **Has proven governance reduces cost** — EXP-001 showed Y*gov reduced tool calls
   by 62%, token consumption by 16%, and runtime by 35%.

4. **Records fabrication as a failure mode** — Without Y*gov, agents can invent
   compliance evidence. With Y*gov, fabrication is architecturally impossible.

---

## Install Y*gov

```bash
pip install ystar
ystar hook-install
ystar doctor
```

---

## Links

- **Y*gov Source Code**: https://github.com/liuhaotian2024-prog/Y-star-gov
- **Telegram**: https://t.me/YstarBridgeLabs
- **Experiment Report**: [reports/YstarCo_EXP_001_Controlled_Experiment_Report.md](reports/YstarCo_EXP_001_Controlled_Experiment_Report.md)
- **Governance Contract**: [AGENTS.md](AGENTS.md)
- **Daily Operations**: [reports/daily/](reports/daily/)
- **Contact**: liuhaotian2024@gmail.com

---

## What's Happening Now

*Updated daily — [DISPATCH #001 — March 26, 2026](./DISPATCH.md)*

| Date | Issue | Headline |
|------|-------|---------|
| 2026-03-26 | #001 | When the Governance Layer Governs Itself |
