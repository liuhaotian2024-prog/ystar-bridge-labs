# Show HN Draft — Variant A (Cult Test)

**Status:** DRAFT — NOT PUBLISHED. Publication requires Board (L3) approval.
**Target:** Hacker News `Show HN`
**Tone:** Plain, technical, anti-hype. No emojis. No marketing adjectives.
**Version:** Y*gov 0.41.1 (per `products/ystar-gov/technical_reference.md`)

---

## Title (≤80 chars)

`Show HN: Y*gov — runtime governance for AI agents (deny, audit, delegation)`

Alternate title options:
- `Show HN: Y*gov — a PreToolUse hook that enforces AGENTS.md at runtime`
- `Show HN: Y*gov — make AGENTS.md actually block things, with an audit chain`

---

## Body

Hi HN,

Y*gov is a runtime governance layer for AI agents. It sits between a coding agent (today: Claude Code; more frameworks coming) and the tools the agent calls. Every tool call is intercepted at a `PreToolUse` hook, checked against a contract compiled from your `AGENTS.md`, and either allowed, denied, or escalated. Every decision is written to an append-only local SQLite log (CIEU) that can be cryptographically sealed with a SHA-256 Merkle root.

The short version: `AGENTS.md` today is documentation. Y*gov makes it enforceable.

**Install (three commands):**

```
pip install ystar
ystar init
ystar hook-install
ystar doctor
```

`ystar doctor` runs a self-test that tries to read `/etc/passwd` and verifies the hook blocked it.

**What it actually does**

- Compiles `AGENTS.md` into an `IntentContract` with dimensions: `deny`, `deny_commands`, `only_paths`, `only_domains`, `value_range`, `invariant`, `postcondition`, `field_deny`.
- Enforces a delegation chain with monotonic authority: a sub-agent cannot be granted permissions its parent does not have.
- Writes a CIEU event per tool call with agent_id, decision, violations, lineage_path, params snapshot, and a contract hash. FTS5 index over the log.
- Four enforcement modes for gradual rollout: `SIMULATE_ONLY`, `OBSERVE_ONLY`, `FAIL_OPEN`, `FAIL_CLOSED`.
- Reported hook latency on a MacBook Pro M1: p50 ~8ms, p99 ~15ms. All checks are local; no network I/O and no LLM calls in the enforcement path.

**What it is not**

- Not an observability tool. It blocks, it does not just record.
- Not a firewall or an OS sandbox.
- Not a replacement for code review.
- It assumes the LLM itself is trusted; it governs the LLM's actions, not its reasoning.

**Why we built it**

We are running an 11-agent solo company where every agent is governed by Y*gov. The product and the operation share one invariant: if a rule is not mechanically enforceable, it is not a rule. We got tired of `AGENTS.md` being a wish list. The CIEU log has ~800 production records from our own usage, including six governance incidents we caught and reproduced. We are releasing the framework because other people running agents seem to have the same problem.

**What we want from HN**

1. Try the three-command install. If `ystar doctor` does not end with "All checks passed" on your box, we want the failure mode.
2. Break the contract. If you can get a `deny` rule to pass through the hook, we want the repro.
3. Tell us what dimensions are missing. The current eight cover paths, commands, domains, numeric ranges, and logical pre/post-conditions, but real workloads will surface gaps.

**Repo:** https://github.com/liuhaotian2024-prog/Y-star-gov
**Docs:** `products/ystar-gov/technical_reference.md` in the repo.
**License:** MIT.

Happy to answer technical questions in the thread: contract compilation, delegation monotonicity, the sealing scheme, or the failure modes we have already hit.

---

## Notes for Board review

- All numbers cited are sourced: version (0.41.1), latency (Appendix B), dimensions (section 2), modes (section 4), ~800 records (STRATEGIC_POSITIONING.md "CIEU 787+").
- No forward-looking claims. No pricing. No Phase 2/3 language.
- No customer names. No Harvey/Devin/Sierra reference (those are internal Phase 2 targets, not public claims).
- Repo URL and email are taken from `technical_reference.md` Support section.
- Title intentionally avoids "trust layer / infrastructure" framing — HN punishes that register.

**Word count (body only, excluding title and notes):** ~455 words.
