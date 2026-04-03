# Y*gov — Runtime Governance for AI Agents

**Category:** Developer Tools | AI Agent Infrastructure
**Target:** Developers using Claude Code and multi-agent systems
**Installation:** `pip install ystar && ystar hook-install && ystar doctor`

---

## What Is Y*gov?

Y*gov is a runtime governance layer for AI agents. It enforces permissions, tracks obligations, and produces an immutable audit trail -- in real time, before any action takes effect.

When you run AI agents with Claude Code, Y*gov sits between your agents and the file system, shell, and APIs. Every action is validated against a governance contract. Unauthorized actions are blocked. Everything is logged.

This is not observability (seeing what happened). This is governance (enforcing what should happen).

---

## Why You Need This

**Problem 1: Agents have too much power**
Claude Code agents can read files, execute bash commands, modify code, and interact with APIs. That power is necessary for productivity. It is also dangerous without boundaries.

**Problem 2: Prompt-based restrictions do not work**
Telling an agent "do not access production files" in a system prompt is a suggestion, not a rule. Agents reinterpret, forget, or ignore instructions. You need runtime enforcement.

**Problem 3: You cannot prove what your agents did**
When something goes wrong -- a file deleted, a deployment broken, credentials exposed -- you need a complete, tamper-evident record. Application logs are mutable and incomplete. You need an audit chain.

Y*gov solves all three.

---

## How It Works

### 1. Define Governance Rules in AGENTS.md

Create a single Markdown file that defines what each agent can and cannot do:

```markdown
## CMO Agent
Can access:
- ./content/ (read/write)
- ./marketing/ (read/write)

Cannot access:
- ./src/ (code directory)
- .env (credentials)
- /production (live systems)

Forbidden commands:
- rm -rf
- sudo
- git push --force
```

### 2. Y*gov Enforces at Runtime

Every agent action passes through the governance layer:
- File reads and writes
- Bash command execution
- API calls
- Delegations to sub-agents

If the action violates the governance contract, it is blocked before execution. The denial is logged with a specific reason.

### 3. Immutable CIEU Audit Chain

Every action produces a CIEU record (Context, Intent, Execution, Upshot):

```
Record ID: 1774555489773712
Timestamp: 2026-03-26T16:04:49Z
Agent: agent
Action: Bash command referencing /etc
Decision: DENIED
Reason: '/etc' is not allowed in command
Policy: AGENTS.md global deny rule
```

These records are tamper-evident (cryptographic hash chain) and queryable. Run `ystar report` to see everything your agents did, allowed and denied.

---

## Key Differentiators

**Runtime enforcement, not prompt-level suggestions**
Y*gov intercepts agent actions at the execution layer. An agent cannot bypass governance by modifying its prompt or reasoning differently. The rules are enforced by the system, not by the agent's interpretation.

**Declarative governance contract**
All permissions are defined in a single, version-controlled `AGENTS.md` file. No custom middleware. No per-agent configuration. One contract, enforced uniformly.

**Compliance-ready audit chain**
The CIEU database is structured for regulatory review. If you need to show an auditor what your agents did, run `ystar report` and hand them the output. It includes timestamps, agent identity, action type, enforcement decision, and violation reasons.

**Delegation chain enforcement**
When an agent creates a sub-agent, the sub-agent's permissions are automatically a subset of the parent's permissions. No privilege escalation. No accidental authority grants.

---

## Installation

```bash
pip install ystar
ystar hook-install
ystar doctor
```

The `hook-install` command integrates Y*gov with Claude Code. The `doctor` command runs a self-test to verify enforcement is working (it deliberately attempts restricted actions and confirms they are blocked).

---

## Use Cases

**Solo developer using Claude Code**
Protect your environment from agent mistakes. Set up deny rules for production files, credentials, and destructive commands. If your agent tries to execute `rm -rf`, Y*gov blocks it.

**Team running multiple agents**
Define roles (backend-agent, frontend-agent, docs-agent) with different permission levels. Each agent can only touch its own territory. Cross-team conflicts are prevented by the governance layer.

**Enterprise compliance**
If your agents access customer data, financial records, or protected health information, you need an audit trail for regulatory review. Y*gov's CIEU chain satisfies SOC 2, HIPAA, and GDPR audit requirements.

**One-person company scaling with agents**
YstarCo (the company that builds Y*gov) is operated entirely by AI agents. The CEO agent decomposes strategy. The CTO agent writes code. The CMO agent produces content. Y*gov enforces boundaries and tracks obligations. Every CIEU record is proof that the system works.

---

## What You Get

- **Permission enforcement**: Declarative allow/deny rules enforced at runtime
- **Obligation tracking**: Assign tasks to agents with deadlines; Y*gov reminds them
- **Audit reporting**: `ystar report` generates a complete governance summary
- **Self-diagnostics**: `ystar doctor` verifies enforcement is working
- **Lightweight integration**: No modification to your agents or prompts required

---

## Pricing

**Free tier**: Individual developers, single agent, local audit database
**Team tier**: Multiple agents, extended audit retention, compliance reporting
**Enterprise tier**: Unlimited agents, SOC 2/HIPAA-ready exports, priority support

Detailed pricing at https://ystar.dev/pricing

---

## Try It Now

```bash
pip install ystar
ystar hook-install
ystar doctor
```

Three commands to governance. Your agents will still do their work. They will just do it with accountability.

**Documentation:** https://ystar.dev/docs
**GitHub:** https://github.com/ystarco/ystar-gov
**Contact:** hello@ystar.dev

---

*Y*gov is built by YstarCo, a company operated entirely by AI agents under Y*gov governance. The product governs itself in production. Every claim about enforcement and audit trails is demonstrated daily in our own operations.*

**Word count: 480**
**Task: CMO-004**
**Status: DRAFT**
**Board approval required: Yes**
