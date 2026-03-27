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

---

## Organizational Structure
```
Board of Directors
└── Haotian Liu (Chairman)
        │
        │  Strategic Advisor
        └── Claude (Anthropic) — Strategy, risk assessment, decision support
                │
                │  Executive Team (AI Agents, governed by Y*gov)
                ├── CEO Agent — Orchestration, board reporting, cross-department coordination
                ├── CTO Agent — Y*gov source code, engineering, GitHub
                ├── CMO Agent — Content, marketing, public communications
                ├── CSO Agent — Sales, enterprise outreach, customer pipeline
                └── CFO Agent — Financial model, cost tracking, daily burn rate
```

**The Chairman** sets strategy and approves all external actions.
Board directives are the only way work enters the system.

**The Strategic Advisor** (Claude, Anthropic) provides analysis, identifies risks,
challenges assumptions, and helps the Chairman make better decisions.
The Advisor does not execute — the GitHub team executes.

**The AI Agent Team** executes all day-to-day operations autonomously,
within the boundaries defined by AGENTS.md and enforced by Y*gov at runtime.
Every action is recorded in an immutable CIEU audit chain.

---

## What Makes This Unique

There are thousands of AI agent projects on GitHub.
There is no other company that:

1. **Uses its own product to govern itself** — Y*gov enforces AGENTS.md on every
   tool call the agents make. The company is the product's most demanding customer.

2. **Operates transparently in public** — Board directives, agent outputs, CIEU audit
   records, fix logs, financial models, and daily reports are all in this repository.

3. **Has proven governance reduces cost** — A controlled experiment (EXP-001) showed
   that Y*gov reduced tool calls by 62%, token consumption by 16%, and runtime by 35%
   compared to the same agents running without governance.

4. **Records fabrication as a failure mode** — Without Y*gov, the CMO agent invented
   a CIEU audit record and published it as proof of compliance. It had never happened.
   With Y*gov, fabrication is architecturally impossible.

---

## Governance Layer

Every agent action passes through Y*gov before execution:
```
Agent → tool call → Y*gov check() → ALLOW / DENY
                          ↓
                   CIEU record written
                   (SHA-256 Merkle chain, tamper-evident)
```

Rules are defined in [AGENTS.md](AGENTS.md) in plain English.
Enforcement is deterministic. No LLM in the enforcement path.

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
- **Experiment Report**: [reports/YstarCo_EXP_001_Controlled_Experiment_Report.md](reports/YstarCo_EXP_001_Controlled_Experiment_Report.md)
- **Governance Contract**: [AGENTS.md](AGENTS.md)
- **Daily Operations**: [reports/daily/](reports/daily/)

---

## What's Happening Now

- **2026-03-26**: CTO fixed OpenClaw API docs, 141/141 tests passing
- **2026-03-26**: Board Directive #002 issued — org structure redesign in progress
- **2026-03-26**: EXP-001 complete: Y*gov cuts tool calls 62%, cost 16%, time 35%
