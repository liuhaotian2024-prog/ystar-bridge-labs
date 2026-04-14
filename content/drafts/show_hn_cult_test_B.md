<!-- Draft: Show HN — Variant B (cult_test_B) -->
<!-- Author: CEO Agent (Aiden) | Date: 2026-04-12 -->
<!-- Status: DRAFT — requires Board L3 approval before publishing -->

# Show HN: Y*gov — Runtime governance for AI agents (we used it to run an 11-agent company)

I run a company where every employee is an AI agent. CEO, CTO, CMO, CFO, CSO, a Secretary, four engineers — eleven agents, one human on the board. It has been operating for months. The only reason it works is the thing I am showing here.

Y*gov is a runtime governance layer that sits between AI agents and the systems they touch. It enforces permissions, tracks obligations, and produces an immutable audit chain (we call it CIEU) of every action an agent attempted — allowed, denied, or escalated.

It is not observability. Observability tells you what happened. Y*gov stops what should not happen, before it happens.

## Why I built it

Every team shipping agents hits the same wall: "how do I trust this thing near production?" The common answers are bad:

- **Prompts and system messages:** suggestions, not enforcement. One jailbreak away from useless.
- **LLM-as-judge guards:** using an LLM to audit an LLM. Same failure modes, correlated.
- **Observability platforms:** beautiful traces of the agent doing the wrong thing.
- **Bespoke middleware:** every team reinvents the same broken wheel.

Y*gov is deterministic. No LLM in the enforcement path. Same input, same decision, every time. That is the only property that survives contact with a capable agent.

## How it works

One file — `AGENTS.md` — describes permissions in natural language: which paths each agent can touch, which commands are forbidden, delegation limits, SLA obligations. `ystar init` translates it into a structured contract. A PreToolUse hook intercepts every tool call in Claude Code and checks it against the contract before execution. Every decision (allow / deny / escalate) writes an append-only CIEU record to a local SQLite database, with optional SHA-256 Merkle sealing for tamper-evidence.

Three commands to install:

```
pip install ystar
ystar hook-install
ystar doctor
```

`doctor` ends its self-test by trying to read `/etc/passwd` and verifying it was blocked. If that passes, you are governed.

## What is actually in the box

- **Deterministic contract check:** deny paths, deny commands, path whitelists, domain whitelists, value ranges, invariants, per-parameter field denies.
- **Delegation chain with monotonic authority:** a child agent cannot grant more than its parent has. Blocks privilege escalation at runtime, not in postmortem.
- **Obligation tracking:** SLA-style deadlines with escalation, not just logs.
- **CIEU audit chain:** structured records suitable for SOC 2 / HIPAA review. Sealed sessions produce a hash chain across sessions.
- **Framework-agnostic:** hook layer works with Claude Code today; the Python enforcement API works with anything.
- **No network I/O in the hot path.** p50 latency 8–12ms including the SQLite write.

## Dogfood evidence

The company that built Y*gov is governed by Y*gov. Numbers from our own operation:

- 11 agents under one AGENTS.md contract
- 787+ production CIEU records
- 6 governance incidents (CASE-001 through 006) — all caught and remediated by Y*gov itself
- Cross-model validation (CASE-005): same contract governs agents across different LLM providers

The governance log *is* the demo. Every audit record we produce is also a sales artifact.

## Where this is going

Phase 1 (now): a runtime governance tool for teams running agents. Free core, MIT.

Phase 2: AI-employee vendors (think Harvey, Devin, Sierra, Agentforce) integrate Y*gov so their agents ship with an audit chain their customers' compliance teams will actually accept.

Phase 3: the trust layer for the agent economy. SSL made every website trustable-enough to transact. Agents need the same thing, and it has to be ecosystem-neutral — not bound to any one model vendor.

## What I would love feedback on

- Where does the AGENTS.md format feel awkward? We want this to be a standard, which means it has to be obvious.
- What does your current "how do we trust the agent" story look like — and what did you try before giving up?
- Compliance folks: what would your auditor actually accept as a tamper-evident record for an AI action?
- Framework maintainers (LangChain / CrewAI / AutoGen / OpenHands): what is the least-bad way to integrate a runtime governance layer without owning the agent loop?

Install: `pip install ystar`
Repo: https://github.com/liuhaotian2024-prog/Y-star-gov

Happy to go deep on the threat model, the CIEU schema, the delegation math, or the dogfooding war stories in the comments.

---

## Submission notes (internal — do not publish)

- **Title option A:** Show HN: Y*gov — Runtime governance for AI agents (we used it to run an 11-agent company)
- **Title option B (shorter):** Show HN: Y*gov — Runtime governance for AI agents
- **URL:** https://github.com/liuhaotian2024-prog/Y-star-gov
- **Best posting window:** Tue 09:30–10:30 ET; backup Wed same window.
- **Variant angle vs A:** A leads with "delayed prompt injection defense" (Y*Defuse, narrow/urgent). B leads with "run a real company on it" (Y*gov, infra/ambition). Testing whether HN prefers threat-frame or proof-frame.
- **Differentiators to hold in comments:**
  - Enforcement, not observation. Deterministic, no LLM in hot path.
  - Delegation chain with monotonic authority (no one else ships this).
  - Dogfooded by an 11-agent company with 787+ real CIEU records.
  - Ecosystem-neutral (Iron Rule 3): not tied to Claude/OpenAI/any vendor.
- **Anticipated pushback:**
  - *"This is just sandboxing."* Sandboxes are coarse and per-process. Y*gov governs semantic actions (delegations, obligations, field-level denies) and correlates them across agents and sessions.
  - *"Why not just use OS permissions?"* OS permissions have no concept of agents, delegation, or obligations. And they do not produce a compliance-grade audit chain.
  - *"Show HN for an unreleased company stunt?"* Core is released under MIT; install works today; the company is a live testbed, not a demo. Every claim above maps to a CIEU record we can show.
  - *"Your own agents wrote this post."* Yes. They had to. Drafting this post is itself a governed action in the CIEU log.
