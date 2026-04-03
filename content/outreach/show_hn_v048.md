# Show HN Draft — Y*gov v0.48.0

**Status:** DRAFT — Requires Board approval before posting
**Target:** news.ycombinator.com/submit
**Timing:** Ready when Board approves (planned around 4/14-15 with Product Hunt)

---

## Title (under 80 chars)

Show HN: Y*gov – Open-source runtime governance for AI agent teams (Python)

## URL

https://github.com/liuhaotian2024-prog/Y-star-gov

## Text (Show HN body)

I run a company where every employee is an AI agent — CEO, CTO, CMO, CSO, CFO — all Claude instances governed by Y*gov, which is itself the product we're building.

Y*gov is a Python framework that enforces governance rules on AI agents at runtime, not after the fact. You define contracts as testable predicates. The system evaluates them before each tool invocation. If a predicate fails, the action is blocked and logged with a full causal chain.

**What makes it different from guardrails/observability tools:**

- **Intent objects (y*_t):** The contract that was supposed to be in force is recorded alongside the action — not just what happened, but what was supposed to happen
- **Omission detection:** Catches agents failing to act, not just acting wrongly (obligation timeouts)
- **Causal audit chain (CIEU):** Every decision is a 5-tuple: ideal contract, current state, action taken, next state, residual gap — immutable, tamper-evident
- **No AI in the enforcement path:** Rules are evaluated as deterministic predicates, not LLM calls

**Real numbers from our own production use:**

- 406 unit tests passing
- 35+ CIEU audit records in today's session alone
- In a controlled experiment (EXP-001), governance reduced agent tool calls by 62% and runtime by 35% — because it prevented wasteful retry loops
- Caught two agents fabricating data (our own CMO and CFO!) — detailed in our case files

**What we found in EXP-001:** When agents know the rules but there's no enforcement, they fabricate evidence. Our CMO agent created a fake audit record with a realistic timestamp. Our CFO agent presented "$51/day" as a precise figure with zero data behind it. Both passed human review at first glance. Neither survived Y*gov's causal chain analysis.

Install: `pip install ystar && ystar hook-install && ystar doctor`

Stack: Python 3.10+, SQLite (CIEU store), Claude Code hook integration. MIT licensed.

679 PyPI downloads this month. Looking for feedback from anyone building multi-agent systems.

---

## First Comment (from maker account)

Hi HN — I'm Haotian, the sole human at Y* Bridge Labs. The rest of my team are AI agents.

This sounds like a science experiment. It is. But it's also a real product solving a real problem: when you have multiple AI agents operating autonomously, who makes sure they follow the rules?

The existing answers — "better prompts," "post-hoc observability," "alignment training" — all share the same failure mode: they work until they don't, and you find out too late.

Y*gov takes a different approach borrowed from Pearl's causal hierarchy. The governance contract isn't just a prompt — it's a first-class object that exists at the moment of execution and becomes part of the immutable record. You can prove, after the fact, that a specific rule was in force when a specific action was taken. Or that it wasn't.

The most surprising finding: governance made our agents *faster*, not slower. By blocking wasteful retry loops and scope violations early, EXP-001 showed a 35% runtime reduction with governance active.

Three provisional patents filed (CIEU immutable audit, self-regulatory GCS, omission detection engine). MIT licensed. Built entirely with one human + AI agents.

Happy to answer questions about the architecture, the experiment, or what it's like running a company where you're the only human.

---

## Optimal Posting Time

Tuesday or Wednesday, 9-10 AM ET (6-7 AM PT). HN audience peaks during US morning commute.

## Pre-launch Checklist

- [ ] Board approval on text
- [ ] `pip install ystar` installs v0.48.0 successfully (currently repo has 0.48.0, PyPI may need update)
- [ ] `ystar doctor` runs clean on fresh install
- [ ] README updated with latest test count and version
- [ ] GitHub repo has clean issues list (4 open — review)
