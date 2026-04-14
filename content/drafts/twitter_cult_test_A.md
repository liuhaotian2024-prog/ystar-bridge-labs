# Twitter/X Thread Draft — Variant A (Cult Test)

**Status:** DRAFT — NOT PUBLISHED. Publication requires Board (L3) approval.
**Target:** Twitter/X thread, 8 tweets.
**Tone:** Plain, technical, no emojis, no hype adjectives.
**Version referenced:** Y*gov 0.41.1.
**Handle assumption:** posted from Y* Bridge Labs account.

---

## Thread

**1/8**
Your `AGENTS.md` is a wish list. Nothing enforces it at runtime.

We shipped Y*gov: a PreToolUse hook that compiles `AGENTS.md` into a contract and blocks violating tool calls before they execute. Open source, MIT.

Show HN + repo link below.

---

**2/8**
Install is three commands:

```
pip install ystar
ystar init
ystar hook-install
ystar doctor
```

`doctor` ends by trying to read `/etc/passwd` and verifying the hook blocked it. If the self-test fails, install is not done.

---

**3/8**
Contract dimensions compiled from your AGENTS.md:

- deny (paths)
- deny_commands
- only_paths (whitelist)
- only_domains
- value_range (numeric)
- invariant / postcondition (logical)
- field_deny (per-parameter)

No LLM in the enforcement path. Deterministic checks only.

---

**4/8**
Delegation is monotonic.

A parent agent cannot grant a child permissions it does not itself hold. Privilege escalation through sub-agent spawning is blocked at the hook, not discovered in a post-mortem.

`chain_depth` is a first-class contract dimension.

---

**5/8**
Every decision is an append-only row in a local SQLite log (CIEU) with:
agent_id, decision, violations, lineage_path, params snapshot, contract hash.

FTS5 index on top. Sessions can be sealed with a SHA-256 Merkle root for tamper evidence.

---

**6/8**
Latency we measured on an M1 MacBook, Python 3.11:
- contract check: 2-5ms
- CIEU write (SQLite WAL): 3-7ms
- full hook cycle: p50 ~8ms, p99 ~15ms

No network I/O. Your agent does not get slower in any way a human can feel.

---

**7/8**
Four enforcement modes so you do not have to go FAIL_CLOSED on day one:

SIMULATE_ONLY -> OBSERVE_ONLY -> FAIL_OPEN -> FAIL_CLOSED

Run it in shadow for a while, read the CIEU log with `ystar audit`, then turn enforcement on when the deny set is calibrated.

---

**8/8**
We are running an 11-agent company on this. CIEU log has ~800 production records, six real governance incidents caught.

If you run agents and `AGENTS.md` is documentation today, try it and break it.

Repo: https://github.com/liuhaotian2024-prog/Y-star-gov
License: MIT.

---

## Notes for Board review

- Character counts: each tweet drafted under 280 chars; tweets 2 and 3 contain code/list blocks that may wrap — acceptable on X.
- Every claim maps to `technical_reference.md` (latency: Appendix B; dimensions: §2; modes: §4 table) or `STRATEGIC_POSITIONING.md` (11 agents, CIEU 787+ production records, 6 incidents CASE-001..006).
- No pricing, no competitors named, no "trust infrastructure" framing, no forward-looking statements.
- Repo URL identical across both drafts for consistency.

**Word count (tweets only, excluding notes):** ~340 words across 8 tweets.
