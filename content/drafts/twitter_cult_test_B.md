<!-- Draft: Twitter/X thread — Variant B (cult_test_B) -->
<!-- Author: CEO Agent (Aiden) | Date: 2026-04-12 -->
<!-- Status: DRAFT — requires Board L3 approval before publishing -->

# Variant B — Thread: "We run a company where every employee is an AI"

Pairs with Show HN variant B. Frame: proof-over-pitch. Open with the cult-y, hook-worthy fact (11-agent company governed by its own product), land on the install command.

---

## Tweet 1 (hook)

We run a software company where every employee is an AI agent.

CEO, CTO, CMO, CFO, CSO, a Secretary, four engineers. Eleven agents. One human on the board.

It only works because of one thing — and we are open-sourcing it today.

👇

---

## Tweet 2

The problem: the moment you let an AI agent touch a real system, someone asks "how do I trust it?"

Prompts are suggestions.
LLM-as-judge is one suspect vouching for another.
Observability tools narrate the disaster.
Bespoke middleware rots in six months.

None of it enforces anything.

---

## Tweet 3

Y*gov is different: a runtime governance layer that sits between your agents and the systems they touch.

- Deterministic. No LLM in the enforcement path.
- Enforces permissions *before* a tool call executes.
- Writes an append-only audit chain (CIEU) of every action, allowed or denied.

---

## Tweet 4

One file — AGENTS.md — describes permissions in plain language.

`ystar init` translates it into a structured contract.
A PreToolUse hook checks every tool call against it.
Every decision lands in a local SQLite audit chain, optionally sealed with a SHA-256 Merkle root.

---

## Tweet 5

Install is three commands:

```
pip install ystar
ystar hook-install
ystar doctor
```

`doctor` finishes by trying to read /etc/passwd and verifying it was blocked. If that passes, you are governed.

p50 latency: 8–12ms. No network I/O in the hot path.

---

## Tweet 6

What no one else ships:

- Delegation chain with monotonic authority — a child agent cannot grant more than its parent has. Privilege escalation is blocked at runtime, not found in the postmortem.
- Obligation tracking with SLAs and escalation, not just logs.
- Field-level denies and value ranges.

---

## Tweet 7

Dogfood receipts from the 11-agent company:

- 787+ production CIEU records
- 6 governance incidents — all caught and remediated by Y*gov itself
- Cross-model validation: the same contract governs agents across different LLM vendors

The governance log is the demo.

---

## Tweet 8

Where this goes:

Phase 1 (today): MIT-licensed runtime governance for anyone running agents.
Phase 2: AI-employee vendors integrate it so their agents ship with an audit chain compliance teams will actually accept.
Phase 3: the trust layer for the agent economy. Ecosystem-neutral on purpose.

---

## Tweet 9 (CTA)

If you are running agents near anything that matters, please break it for us.

Install: pip install ystar
Repo: https://github.com/liuhaotian2024-prog/Y-star-gov
Show HN: [link TBD after submission]

Questions, war stories, auditor rants — all welcome. Reply or DM.

---

## Internal notes (do not publish)

- Thread length: 9 tweets. All within 280 chars (verify on paste — em dashes render fine).
- Variant vs A: A leads with attack drama (delayed prompt injection). B leads with company-as-proof. Measuring whether cult-energy (an AI-run company) pulls harder than threat-energy.
- Optional pinned reply with a screenshot of a real CIEU deny record — higher trust, less text.
- Do not post until Show HN is live; link HN submission in tweet 9.
- Accounts to notify (not @-tag in thread): vendors + framework maintainers already on our outreach list.
