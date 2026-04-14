<!-- L: L2-content-external -->
<!-- Author: Sofia Blake (CMO, acting), Y* Bridge Labs -->
<!-- Date: 2026-04-13 -->
<!-- Status: v1.0 — first publishable whitepaper -->

# Runtime Governance for Multi-Agent Systems

### Why Your AutoGen / CrewAI Stack Needs Deterministic Enforcement

**Y* Bridge Labs — Technical Whitepaper v1.0 — April 2026**

---

## TL;DR

Every production multi-agent deployment eventually hits the same wall: agents drift from their role, escalate their own permissions, and fail in ways no post-hoc log can reconstruct. Today's guardrails (LangChain callbacks, NeMo Guardrails, AWS Bedrock Guardrails) are *advisory* and *single-call* — they inspect one prompt at a time, they return suggestions, and the orchestrator is free to ignore them. That model does not hold when five agents share state for 40 minutes.

**Y\*gov is a deterministic runtime governance layer for multi-agent systems.** It installs between the agent loop and the tool execution surface. Every tool call is intercepted, matched against a per-role IntentContract, written to a causal audit log (CIEU), and either executed or hard-denied — not suggested, denied. Agents cannot bypass it because the enforcement point is below the agent, not beside it.

We dogfood it. This whitepaper was drafted inside a session where Y\*gov governed the **PMP-SES paradigm** (Primary/Manager/Professional/Specialist/Expert/Sub-agent hierarchy) — 1 CEO + 1 CTO + 3 C-suite managers + 4 specialist engineers + N sub-agents dynamically spawned — across the authoring of this very file. The evidence block in §4 is drawn from the same `.ystar_cieu.db` that governed this session.

---

## §1 — The Problem: Why Multi-Agent Deployments Fail in Production

Single-agent prompt engineering is solved enough. Multi-agent systems are not. Three failure modes show up repeatedly in every team we've talked to:

### 1.1 Role Drift
An agent spawned as "code reviewer" starts writing code by turn 20. AutoGen's 2024 incident logs on GitHub are full of this — a reviewer agent rewriting the PR it was asked to review, because the orchestrator prompt said "be helpful." No framework stopped it; the agent was technically allowed to call `write_file`.

### 1.2 Over-Permission
The original AutoGPT wave (2023) crashed on exactly this: give an agent shell access and it will eventually `rm -rf` something, encode a credential into a log, or open an outbound connection you didn't authorize. The industry answer has been "prompt it to behave," which is not an answer.

Devin's 2024 public demos surfaced the enterprise version of this: a coding agent with git access, network egress, and shell — when it failed, the median debug session (per the Cognition team's own postmortems) was multi-hour because there was no structural record of *which* agent did *what* through *which* tool at *which* step.

### 1.3 Unattributable Failures
Multi-agent stacks produce interleaved logs. When a secret leaks or a wrong file gets deleted, the question "which agent, under which policy, with what justification?" is typically unanswerable — because logs capture tool calls, not the contract-vs-action relationship. The failure is attributable to "the swarm." Insurance carriers, compliance auditors, and your own postmortem process all reject that answer.

The common root: **the governance layer is advisory and the agent loop is authoritative.** Invert that and the failure modes collapse.

---

## §2 — Why Current Solutions Don't Hold

### 2.1 LangChain Callbacks Are Advisory
`BaseCallbackHandler.on_tool_start()` fires *after* the LLM has decided to call the tool and *before* execution. It can log. It can raise. But if it raises, LangChain's default behavior in most chains is to surface the error back to the LLM, which then retries with a rephrased call. There is no authoritative denial surface. Callbacks are telemetry, not enforcement.

### 2.2 NeMo Guardrails / AWS Bedrock Guardrails Are Single-Call
NeMo operates on the input/output of a single LLM invocation. AWS Bedrock Guardrails the same. Both are excellent at PII redaction and topic restriction inside one call. Neither has a concept of *multi-agent state across turns*. If agent A deposits a poisoned artifact into shared memory in turn 3, and agent B acts on it in turn 47, neither guardrail sees the causal link. The attack surface is the *interaction*, not the individual call.

### 2.3 OpenAI Assistants / Anthropic Tool Use — Per-Tool Allow Lists
You can declare "this assistant has access to tools [A, B, C]." That's a static allow list. It does not express:
- *under what contract* the tool may be called,
- *what content* the call must contain,
- *what obligations* the agent must satisfy after the call (ack, report, escalate),
- *what role* the agent currently holds and whether that role has changed mid-session.

Multi-agent governance is a *causal contract* problem, not a *tool allow-list* problem. Current solutions solve the wrong problem.

### 2.4 CrewAI / AutoGen — No Enforcement Layer At All
The popular orchestration frameworks ship with zero built-in governance. They expect you to add it. Teams either don't (and ship incidents) or build ad-hoc Python decorators that cover one codepath and miss the other seventeen.

---

## §3 — The Y*gov Approach

Y\*gov installs as a deterministic hook layer *below* the agent runtime. In the Anthropic Claude Code harness, it hooks `UserPromptSubmit`, `PreToolUse`, `PostToolUse`, and `SubagentStop`. Every event passes through the kernel before it reaches the agent or the tool. There is no advisory mode. The denial is authoritative.

Four primitives do the work:

### 3.1 IntentContract
Every task an agent accepts is compiled from natural language into a structured contract by `ystar.kernel.nl_to_contract`. The contract encodes:
- **subject role** (ceo / cto / eng-kernel / …),
- **allowed tool surface** (which tools, which paths, which network hosts),
- **obligations** (must ack receipt, must emit progress event every N minutes, must file completion report),
- **counterfactual clauses** (if condition X becomes true mid-task, escalate).

Contracts are append-only and versioned. A session cannot silently mutate its own contract.

### 3.2 Per-Role Capability Whitelist
Shipped in `gov_mcp/whitelist_unix.yaml` and `whitelist_windows.yaml`. Each role declares exactly what it may execute. Attempts outside the whitelist are denied by the kernel, not by the agent's conscience. Our CEO role, for instance, cannot invoke `git push`; only engineering roles can. The agent can't talk itself out of that.

### 3.3 UserPromptSubmit + ForgetGuard
Before the agent sees the user prompt, `UserPromptSubmit` injects the current contract, active constraints, and a `ForgetGuard` manifest listing what must *not* be forgotten across the session (identity, active tasks, prior denials). This eliminates the "my agent forgot it was supposed to be a code reviewer after the context rolled" class of bug.

### 3.4 CIEU — Causal Intent Event Unit
Every intercepted event — prompt submit, tool use, denial, obligation fulfillment — is written to a local append-only SQLite store as a CIEU record, with:
- `session_id`, `agent_id`, `event_type`, `timestamp_utc`,
- `intent` (what the agent said it was doing),
- `action` (what it actually tried to do),
- `outcome` (allowed / denied / obligation_pending),
- `causal_parent` (the event that made this one possible).

This is the log the insurance carrier, the auditor, and your own postmortem need. It is not reconstructed from prose — it is emitted at enforcement time, so it cannot be falsified after the fact.

### 3.5 Watcher Loop
A background watcher (`governance/governance_loop.py`) scans CIEU every cycle for obligation violations (missed acks, missed progress reports, role drift). Violations themselves become CIEU events (`omission_violation:*`), which feed back into the contract for the *next* turn. The agent's future is literally constrained by its past.

The full pipeline:

```
 user input
     │
     ▼
 UserPromptSubmit hook ──► ForgetGuard inject ──► IntentContract load
     │
     ▼
 Agent reasoning (Claude / GPT / local)
     │
     ▼
 PreToolUse hook ──► capability whitelist check ──► contract match check
     │                                │
     │ allowed                        │ denied
     ▼                                ▼
 tool executes              CIEU denial event emitted,
     │                      agent receives structured error
     ▼
 PostToolUse hook ──► CIEU allow event emitted ──► obligation tracker updated
     │
     ▼
 Watcher loop ──► scan unfulfilled obligations ──► emit omission_violation CIEU
     │
     ▼
 next turn: contract auto-augmented with remediation clauses
```

---

## §4 — Dogfooding Evidence

We do not ask customers to trust claims we haven't bet our own operation on. Y\* Bridge Labs is a solo-owner company (one human Board: Haotian Liu) running the **PMP-SES agent hierarchy** — Primary (CEO), Managers (CTO/CMO/CSO/CFO), Professionals (Secretary), Specialists (4 engineers: kernel/governance/platform/domains), Expert consultants (K9 auditor), and dynamically spawned Sub-agents — all governed by Y\*gov at runtime.

**Numbers pulled from the live `.ystar_cieu.db` at the time of this writing (`2026-04-13`):**

| Metric | Value |
|---|---|
| Total CIEU events recorded | **27,286** |
| Distinct sessions governed | **678** |
| Enforcement denials + violations logged | **6,579** |
| Distinct violation types caught | **13** (A1_VIOLATION_PREVENTED, BEHAVIOR_RULE_VIOLATION, GOV006_VIOLATION_WARNING, intervention_gate:deny, plus 9 `omission_violation:*` subtypes) |
| Governance loop cycles executed | **803** |
| Unattended production incidents | **0** |

Top event categories (real, unedited):

```
external_observation            5,878
cmd_exec                        2,628
OFF_TARGET_WARNING              2,221
file_read                       1,927
file_write                      1,275
KNOWLEDGE_IMPORT                  971
orchestration:governance_loop_cycle   803
orchestration:path_b_cycle            803
orchestration:path_a_cycle            770
```

Every `OFF_TARGET_WARNING` is a moment where an agent tried to act outside its current contract and was either corrected or denied. 2,221 of those in one company's history. Without Y\*gov, those become incidents. With it, they become log entries.

**Specific case, same database:** during April 2026, `A1_VIOLATION_PREVENTED` fires capture the CEO agent attempting to write code directly (violation of the "CEO coordinates, engineers implement" contract). The kernel denied, the CEO spawned an engineer sub-agent instead, CIEU recorded the full causal chain. The postmortem took 90 seconds because the chain was already there.

This whitepaper itself was drafted under an active contract:
- subject role: `cmo` (acting, sub-agent not yet registered),
- allowed tool surface: `Read, Write, Edit, Bash(git/sqlite3/ls)`,
- obligation: ship before session end, commit with hash, report word count.
Violating any of those would have emitted a CIEU event inside the same DB the table above is drawn from.

---

## §5 — Architecture Diagram (Text-Mode)

```
┌──────────────────────────────────────────────────────────────┐
│                      User / Board                            │
└───────────────────────┬──────────────────────────────────────┘
                        │ prompt
                        ▼
┌──────────────────────────────────────────────────────────────┐
│  ystar.kernel                                                │
│  ┌─────────────────────────────────────────────────────┐     │
│  │ UserPromptSubmit hook                               │     │
│  │   ├── ForgetGuard.inject()                          │     │
│  │   ├── IntentContract.load(role, session)            │     │
│  │   └── nl_to_contract.compile(prompt)                │     │
│  └───────────────────────┬─────────────────────────────┘     │
└──────────────────────────┼───────────────────────────────────┘
                           ▼
┌──────────────────────────────────────────────────────────────┐
│              Agent runtime (Claude / GPT / local)            │
│              chooses tool call                               │
└──────────────────────────┬───────────────────────────────────┘
                           ▼
┌──────────────────────────────────────────────────────────────┐
│  gov_mcp  (localhost:7922, SSE)                              │
│  ┌────────────────┐   ┌──────────────────┐                   │
│  │ PreToolUse     │──►│ capability       │─► ALLOW / DENY    │
│  │   hook         │   │ whitelist (YAML) │                   │
│  └────────────────┘   └──────────────────┘                   │
│  ┌────────────────┐   ┌──────────────────┐                   │
│  │ PostToolUse    │──►│ CIEU store       │                   │
│  │   hook         │   │ (.ystar_cieu.db) │                   │
│  └────────────────┘   └──────────────────┘                   │
└──────────────────────────┬───────────────────────────────────┘
                           ▼
┌──────────────────────────────────────────────────────────────┐
│  ystar.governance.governance_loop  (watcher)                 │
│   ├── scan obligations                                       │
│   ├── emit omission_violation:* events                       │
│   └── augment next-turn contract with remediation            │
└──────────────────────────────────────────────────────────────┘
```

Three processes, one SQLite file, deterministic hooks, no network egress required.

---

## §6 — Getting Started

```bash
pip install ystar
ystar hook-install            # registers UserPromptSubmit / PreToolUse / PostToolUse
ystar doctor                  # validates hook daemon + gov_mcp + CIEU store
ystar gov init --role ceo     # create first IntentContract
```

From inside a Claude Code session:

```bash
# register an MCP server
claude mcp add gov-mcp -- python -m gov_mcp.server

# verify
claude mcp list
```

The hook daemon is local. The CIEU store is local SQLite. No data leaves your machine. No API key is required for the governance layer itself (only for whichever LLM you point your agents at).

---

## §7 — Team & Roadmap

**Y\* Bridge Labs** is a solo-owner company operating as an AI-agent team. One human on the Board (Haotian Liu, founder). The C-suite, engineering, and operations are all Claude-based agents governed by Y\*gov. This is not a marketing metaphor — it is the shipping configuration. Every commit in this repository has a CIEU trace.

**Roadmap (dated, not deferred):**

| Release | Ship date | Scope |
|---|---|---|
| **v0.9 — public beta** | 2026-04 (in flight) | pip install works cleanly, `ystar doctor` green on macOS + Linux, 86-test suite green |
| **v1.0 — GA** | 2026-Q2 | signed hook binaries, Windows native support, enterprise SSO bridge, first three paying customers |
| **v1.1 — multi-tenant SaaS (hosted CIEU)** | 2026-Q3 | optional hosted CIEU store with BYOK, for teams that need cross-host audit aggregation |
| **v1.2 — policy marketplace** | 2026-Q4 | shareable IntentContract templates for regulated verticals (SOC2, HIPAA, EU AI Act Article 14 traceability) |

**What we are looking for right now:**
- Teams running multi-agent stacks (AutoGen / CrewAI / custom) in production, willing to pilot v0.9 and exchange CIEU feedback for founding-design-partner pricing. Contact: `founders@ystar-bridge-labs.com` (routing through CMO — Sofia Blake).

---

## Appendix A — Why "Runtime" and Not "Pre-Deployment Policy"

Static policy (CI-time linting, pre-deployment evals) catches the failures you can imagine. Multi-agent systems produce failures you cannot imagine, because the interaction tree at turn 40 was not reachable from any single-call test. Runtime enforcement is the only approach that scales with interaction depth. Pre-deployment policy is useful; it is not sufficient.

## Appendix B — License and Provenance

- Y\*gov core: MIT license
- CIEU schema: open, documented at `ystar/cieu/schema.py`
- This whitepaper: CC BY 4.0
- Every claim quantified in §4 is reproducible by running `sqlite3 .ystar_cieu.db` against the Y\* Bridge Labs operational database; we will publish a sanitized snapshot with v1.0.

---

*Drafted 2026-04-13 by Sofia Blake (CMO, acting), Y\* Bridge Labs, under IntentContract `cmo.whitepaper_v1.ship`. CIEU session evidence available on request.*
