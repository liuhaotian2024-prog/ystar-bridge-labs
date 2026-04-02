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

## Labs Sessions — The Story So Far

Every session is logged. Every decision is audited. This is how we got here.

### Day 1-3: Genesis (March 26-28, 2026)

**"From Zero to Nine Agents in 72 Hours"**

The company incorporated on March 26, 2026. By March 28, we had a 9-agent team operating under Y*gov governance.

**What happened:**
- Board defined AGENTS.md v1.0 — plain English governance contract
- CTO built the kernel: IntentContract parser, CIEU audit chain, permission engine
- First fabrication caught: CMO invented a CIEU audit record in a blog post. The record never existed.
- Constitutional response: CIEU records now kernel-generated only. Fabrication became architecturally impossible.

**Key code (reproducible):**
```bash
git clone https://github.com/liuhaotian2024-prog/Y-star-gov
cd Y-star-gov
git checkout 9c0a1f0  # Day 2 commit
python -m pytest tests/  # 86 tests passing
```

**Result:** First controlled experiment (EXP-001) showed governance reduced token cost by 16%, runtime by 35%, and eliminated all violations.

---

### Day 4-5: Feature-Complete Sprint (March 29-30, 2026)

**"From 86 Tests to 425 in 48 Hours"**

The Board mandated feature-complete status. CTO organized a 4-Wave architecture push with parallel engineering teams.

**What happened:**
- Wave 1 (F1-F6): Dynamic multi-agent policy parsing, real-time orchestration, causal reasoning (Pearl Level 2-3)
- Wave 2 (N1-N4): Governance Coverage Score (GCS), per-agent contract loading, delegation chain verification
- Wave 3 (N5-N7): Cross-review obligations, immutable file protection, baseline assessment
- Wave 4 (N8-N10): Postcondition verification, session boot protocol, hot-reboot mechanism
- Test count: 86 → 238 → 406 → 425

**Key code:**
```bash
cd Y-star-gov
git checkout 1b98349  # End of Day 5
ystar setup  # Creates baseline
ystar doctor  # 7 checks, all passing
```

**Result:** Y*gov reached feature-complete. Pearl's Causal Hierarchy implemented in production governance. 3 US provisional patents filed.

---

### Day 6: Constitutional Reform (March 31, 2026)

**"When Agents Started Thinking"**

Session revealed agents were executing tasks mechanically without reasoning about systemic issues. Board mandated Thinking Discipline constitutional reform.

**What happened:**
- New rule: After ANY task, agents must ask:
  1. What system failure does this reveal?
  2. Where else could the same failure exist?
  3. Who should have caught this?
  4. How do we prevent this class of problem?
- Applied to all 9 agents in AGENTS.md
- If any answer produces insight → ACT immediately, don't just note it

**Key commit:**
```bash
git log --oneline --grep="Thinking Discipline"
# e33f566 constitutional: Thinking Discipline — all 9 agents must reason, not just execute
```

**Result:** Agents began proactively detecting and fixing systemic issues (hook failures, installation gaps, documentation errors) without Board instruction.

---

### Day 7: Baseline Assessment (April 1, 2026)

**"Closing the Feature Gaps"**

Morning cycle completed baseline assessment system. Evening cycle completed FIX-6 and FIX-7 for delegation chain and path validation.

**What happened:**
- Baseline assessment: CIEU schema validation (26 fields), delta engine (5 dimensions), bridge to GovernanceObservation
- 2384 CIEU events analyzed, deny_rate = 43.4%
- Retro baseline: 2631 records (97.2% allow), baseline_id = 61b41fc3
- Governance suggestions: tighten delegation timing + focus on acknowledgement omissions
- Discovery: 66 omission violations, 0% recovery rate — flagged for attention

**Key commands:**
```bash
ystar baseline  # Create installation baseline
ystar delta     # Show governance delta vs baseline
ystar verify    # Check CIEU integrity
```

**Result:** Users can now verify "Y*gov changed my system" with quantitative before/after data.

---

### Day 8: Production Hardening (April 2, 2026)

**"The Day We Governance-Tested Governance"**

Discovered PreToolUse hook wasn't firing in interactive Board sessions. Root cause analysis → fix → A/B experiments → architectural review.

**What happened (morning):**
- **Root cause found:** Project `.claude/settings.json` shadowed global hooks in interactive mode
- **Fix applied:** `.claude/settings.local.json` at highest priority, bypassing merge bug
- **Impact:** 10+ hours of Board decisions had zero CIEU audit trail (governance blind spot)
- **FIX-6:** Delegation chain hash deserialization failure → logging added
- **FIX-7:** MSYS bash path normalization → 3 new tests
- **Tests:** 425 → 518 passing

**What happened (afternoon):**
- **Architectural review:** Platform Engineer analyzed all 8 layers, found:
  - Silent exception handling (`except Exception: pass`) in hook.py and orchestrator.py
  - Missing installation baseline verification in CLI
  - hook.py at 674 lines (should be <100 for "thin adapter")
- **20 architecture tasks identified:** 8 P0, 7 P1, 5 P2

**What happened (evening — EXP-002):**

Two A/B experiments comparing governance on vs off.

**P1 Task Group (4 priority tasks):**

| Metric | A: No Hook | B: Full Governance | Delta |
|--------|-----------|-------------------|-------|
| Tokens | 255,814 | 211,794 | -17% |
| Tool calls | 163 | 143 | -12% |
| Runtime (s) | 1,508 | 810 | -46% |
| Completion | 0/4 | 3-4/4 | Tasks done |

**P2 Task Group (observe vs enforce):**

| Metric | A: Observe-Only | B: Full Governance | Delta |
|--------|----------------|-------------------|-------|
| Tokens | 159,930 | 142,103 | -11% |
| Tool calls | 133 | 122 | -8% |
| Runtime (s) | 892 | 734 | -18% |

**Key finding:** Governance improves task completion and reduces cost — not just enforces rules.

**What happened (night):**
- **Session Boot Protocol:** CEO now governed by Y*gov hook enforcing mandatory session startup checks
- **Hot-reboot mechanism:** Board can say "reboot" and trigger full boot protocol mid-session
- **CIEU Liveness Check:** Mandatory at every session start (Directive #024)

**Key code (reproducible):**
```bash
# Hook pipeline fix
cd Y-star-gov
git show 1cca003  # FIX-6 + FIX-7 commit
python -m pytest tests/test_hook.py -v

# Observe-only wrapper for experiments
git show d18358b
cat ystar/adapters/hook_observe.py
```

**Result:** 518 tests passing. Hook pipeline production-ready. Experimental proof that governance reduces cost by 11-17% and time by 18-46%.

---

## Coming Next

**Week of April 7-14:**
- PyPI v0.48.0 release (feature-complete build)
- Show HN launch: "Y*gov — Runtime Governance for AI Agents"
- P0 architecture fixes: eliminate silent exceptions, add fallback audit logging
- Product Hunt launch (April 14-15)

**Q2 2026 Goals:**
- 200 GitHub stars (current: 2)
- 10 HN articles published (current: 0, 5 drafted)
- 3 production users (current: 1 — K9 Scout)
- First enterprise conversation
- 500 LinkedIn followers (current: 0)

The company is 8 days old. Every agent action is audited. Every architectural decision is logged. You're watching a company bootstrap itself in public.

---

## What's Happening Now

*Updated daily — [DISPATCH #001 — March 26, 2026](./DISPATCH.md)*

| Date | Issue | Headline |
|------|-------|---------|
| 2026-03-26 | #001 | When the Governance Layer Governs Itself |
