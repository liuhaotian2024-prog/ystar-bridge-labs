# GOV A2A — Agent-to-Agent Governance Layer
# Internal Planning Document — Do Not Publish
# Created: 2026-04-05
# Status: Pre-planning (awaiting gov-mcp market validation)

---

## 1. Product Positioning

**Y*gov is the governance layer for the A2A ecosystem, not a competitor.**

- A2A (Google) solves: how agents communicate across frameworks
- MCP (Anthropic) solves: how agents access tools and resources
- **Y*gov solves: whether the communication/access is compliant, auditable, and authorized**

The relationship:

```
A2A Protocol (transport)
    |
    v
GOV A2A (governance checkpoint)  ← Phase 2
    |
    v
Agent Framework (execution)
    |
    v
GOV MCP (tool governance)  ← Phase 1 (current, 33 tools)
```

## 2. Relationship to Existing Products

| Product | Scope | Status |
|---|---|---|
| Y-star-gov | Governance kernel (engine, CIEU, OmissionEngine, DelegationChain) | v0.48+ released |
| gov-mcp | MCP tool call governance (33 tools, auto-execute, delegation) | v0.1.0 ready for PyPI |
| **gov-a2a** | A2A agent-to-agent communication governance | **Phase 2 planning** |

**Dependency chain:** gov-a2a → Y-star-gov kernel (same as gov-mcp)

**Key insight:** gov-mcp proves the governance model works for tool calls. gov-a2a extends it to agent-to-agent messages. Same kernel, different transport.

## 3. Phase 2 Technical Design

### 3.1 A2A Protocol Integration Points

A2A defines AgentCard, Task, and Message primitives. GOV A2A intercepts at:

```
Agent A                        Agent B
   |                              |
   |-- A2A Task Request -------->|
   |   [GOV A2A checkpoint]      |
   |   - Check: is A authorized  |
   |     to delegate to B?       |
   |   - Check: does the task    |
   |     scope fit A's contract? |
   |   - Record: CIEU event      |
   |                              |
   |<-- A2A Task Response -------|
   |   [GOV A2A checkpoint]      |
   |   - Check: did B stay       |
   |     within its contract?    |
   |   - Record: CIEU event      |
```

### 3.2 Core Components

| Component | Description | Reuses from Y-star-gov |
|---|---|---|
| A2A Interceptor | Middleware that sits between A2A agents | New |
| Contract Mapper | Maps A2A AgentCard → IntentContract | New (uses nl_to_contract) |
| Delegation Bridge | Maps A2A task delegation → DelegationChain | DelegationChain |
| CIEU A2A Writer | Records A2A events in CIEU format | CIEUStore |
| Cross-Agent Audit | Tracks full conversation chain across agents | New (extends CIEU) |

### 3.3 CIEU Five-Tuple Extension for A2A

Current CIEU: `(agent_id, action, decision, contract_hash, timestamp)`

A2A extension: `(source_agent, target_agent, action, decision, contract_hash, task_id, timestamp)`

Two new fields:
- `target_agent`: the receiving agent (A2A specific)
- `task_id`: A2A task identifier for conversation threading

### 3.4 New GOV A2A Tools (Preliminary)

| Tool | Description |
|---|---|
| `gov_a2a_check` | Check if agent A can delegate task to agent B |
| `gov_a2a_register` | Register an A2A agent with its governance contract |
| `gov_a2a_audit` | Cross-agent audit trail for A2A conversations |
| `gov_a2a_verify` | Verify CIEU chain integrity across A2A interactions |
| `gov_a2a_route` | Governance-aware agent routing (pick the right agent) |

## 4. Core Functionality Checklist

### Must-Have (Phase 2 MVP)

- [ ] A2A AgentCard → IntentContract translation
- [ ] Task-level governance check (before delegation)
- [ ] Response-level governance check (after completion)
- [ ] CIEU recording for all A2A interactions
- [ ] DelegationChain integration (A2A task = delegation)
- [ ] Cross-agent audit report

### Should-Have

- [ ] A2A AgentCard discovery with governance metadata
- [ ] Rate limiting per A2A agent pair
- [ ] Escalation mechanism (agent can't complete → escalate)
- [ ] Multi-hop governance (A→B→C chain validation)

### Nice-to-Have

- [ ] Real-time A2A governance dashboard
- [ ] A2A compliance report templates (FINRA, EU AI Act)
- [ ] A2A agent reputation scoring based on CIEU history

## 5. Timeline

| Phase | Timeline | Milestone |
|---|---|---|
| Phase 1: GOV MCP | 2026 Q2 (current) | PyPI release, Show HN, first 10 users |
| Phase 2 Start | 2026 Q3 | A2A protocol study + prototype |
| Phase 2 MVP | 2026 Q3 end | gov_a2a_check + gov_a2a_register + CIEU |
| Phase 2 Complete | 2026 Q4 start | Full A2A governance + audit |
| Phase 3: Gov Pipeline | 2026 Q4 | End-to-end workflow governance |

**Trigger for Phase 2 start:** gov-mcp has 100+ active users OR enterprise customer requests A2A governance.

## 6. Risks

| Risk | Mitigation |
|---|---|
| A2A protocol changes rapidly | Build on stable AgentCard/Task primitives only |
| Market doesn't need A2A governance yet | Phase 2 starts only after Phase 1 validates demand |
| Competing governance frameworks emerge | Speed + CIEU audit trail is our moat |
| A2A adoption slower than expected | gov-mcp is standalone value; A2A is bonus |

## 7. Decision Points (Board)

1. **When to start Phase 2:** After gov-mcp first 100 users? Or after first enterprise deal?
2. **GitHub repo timing:** Create gov-a2a repo when MVP is ready, not before
3. **Patent:** A2A governance layer may be patentable (P8 candidate)
4. **Pricing:** A2A governance is enterprise-only ($2999/month tier)?
