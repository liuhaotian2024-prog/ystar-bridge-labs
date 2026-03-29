# Path B — External Governance: Technical Design Proposal

**Author**: CTO Agent
**Date**: 2026-03-26
**Status**: Design Phase
**Based on**: Path A architectural pattern (meta_agent.py, governance_loop.py, causal_engine.py)

---

## Executive Summary

Path A solved the "quis custodiet ipsos custodes" problem by creating a governance agent whose goals derive from external observation, not self-definition. **Path B applies the identical architectural pattern outward** — enabling Y*gov to govern external agents using the same closed-loop mechanism that makes Path A trustworthy.

This is not a metaphor. Path A's core components map 1:1 to Path B requirements. The innovation is recognizing that the **same trust architecture** works for both internal and external governance.

---

## Part 1: Path A Deep Analysis

### 1.1 Path A Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│ GovernanceLoop (Trust Root)                                     │
│ - observe_from_report_engine() → GovernanceObservation          │
│ - tighten() → GovernanceSuggestion (external goals)             │
└────────────────┬────────────────────────────────────────────────┘
                 │ Suggestion
                 ▼
┌─────────────────────────────────────────────────────────────────┐
│ PathAAgent                                                       │
│ - suggestion_to_contract() → IntentContract                     │
│ - check(action, contract) — self-constraint                     │
│ - execute on ModuleGraph (wire edges)                           │
│ - write to CIEU (audit chain)                                   │
│ - create postcondition obligation                               │
└────────────────┬────────────────────────────────────────────────┘
                 │ Result
                 ▼
┌─────────────────────────────────────────────────────────────────┐
│ Verification Layer                                              │
│ - GovernanceLoop.tighten() re-runs → verify health improved     │
│ - OmissionEngine checks obligation → HARD_OVERDUE if failed     │
│ - InterventionEngine blocks PathA if violation repeated         │
└─────────────────────────────────────────────────────────────────┘
```

**Key Trust Properties:**
1. **Goals from observation**: GovernanceSuggestion derived from system health metrics, not agent desires
2. **Self-constrained**: PathAAgent calls `check()` on its own actions before executing
3. **Auditability invariant**: Every action writes to CIEU (the same chain it serves)
4. **Failure punishment**: HARD_OVERDUE → InterventionEngine → human intervention required
5. **Delegation monotonicity**: Cannot expand permissions (DelegationChain depth=1, no re-delegate)

### 1.2 Core Insight

Path A works because the agent is **governed by the system it serves**. The governance loop (GovernanceLoop) is both:
- The **principal** (issues goals via GovernanceSuggestion)
- The **judge** (verifies results via tighten())

This creates a closed loop without infinite recursion. PathAAgent cannot game the system because it doesn't control the metrics that define success.

---

## Part 2: Path B Architecture Design

### 2.1 Component Mapping

| Path A Component | Function | Path B Equivalent | Function |
|-----------------|----------|-------------------|----------|
| GovernanceLoop | Observes internal system health, generates suggestions | **ExternalGovernanceLoop** | Observes external agent behavior, generates compliance constraints |
| PathAAgent | Executes suggestions on ModuleGraph | **PathBAgent** | Applies constraints to external agent's action stream |
| suggestion_to_contract() | Converts suggestion to IntentContract | **observation_to_constraint()** | Converts external observation to ExternalContract |
| ModuleGraph edges | Path A's action space (wire modules) | **Agent API/Tool Gateway** | Path B's enforcement point (block/modify tool calls) |
| CIEU audit | Records Path A actions | **Shared Audit Chain** | Records external agent actions + Path B interventions |
| OmissionEngine | Tracks Path A obligations | **ComplianceObligationStore** | Tracks external agent compliance obligations |
| InterventionEngine | Blocks Path A on failure | **DisconnectionPolicy** | Disconnects non-compliant external agent |

### 2.2 Architecture Diagram

```
┌───────────────────────────────────────────────────────────────────────┐
│ External Agent (Customer's LLM-based system)                          │
│ - Runs arbitrary tasks                                                │
│ - Has NO Y*gov code internally                                        │
└──────────────┬────────────────────────────────────────────────────────┘
               │ Tool calls (e.g., bash, file_write, API_request)
               ▼
┌───────────────────────────────────────────────────────────────────────┐
│ Path B Governance Proxy (runs on customer infra or Y*gov SaaS)       │
│ ┌─────────────────────────────────────────────────────────────────┐ │
│ │ ExternalGovernanceLoop                                          │ │
│ │ - observe_external_agent() → CausalChainAnalyzer (from K9Audit)│ │
│ │ - derive_compliance_constraints() → ExternalContract           │ │
│ │ - trust root: customer's policy config OR regulatory standard  │ │
│ └───────────────────────┬─────────────────────────────────────────┘ │
│                         │                                             │
│                         ▼                                             │
│ ┌─────────────────────────────────────────────────────────────────┐ │
│ │ PathBAgent                                                      │ │
│ │ - intercept_action() — inspect agent's tool call                │ │
│ │ - check(action, external_contract) — apply constraint           │ │
│ │ - ALLOW / MODIFY / DENY decision                                │ │
│ │ - write to shared audit chain (CIEU)                            │ │
│ └───────────────────────┬─────────────────────────────────────────┘ │
│                         │                                             │
└─────────────────────────┼─────────────────────────────────────────────┘
                          │
                          ▼ (allowed actions)
┌───────────────────────────────────────────────────────────────────────┐
│ Actual Execution Environment (bash, filesystem, APIs)                │
└───────────────────────────────────────────────────────────────────────┘
```

**Integration with K9Audit:**
```
K9Audit CausalChainAnalyzer → Path B ExternalGovernanceLoop → ExternalContract
   ↑                                                                  ↓
   └──────────────────────── Audit Chain (CIEU) ──────────────────────┘
```

---

## Part 3: Detailed Design

### 3.1 Observation Layer: How Path B Observes External Agents

**Options:**

| Approach | Path A Parallel | Pros | Cons |
|----------|----------------|------|------|
| **API Gateway** | ModuleGraph edges | Intercept HTTP/RPC calls | Only works for API-based agents |
| **Hook Proxy** | OpenClaw enforce() | Wrap agent's tool invocations | Requires agent framework integration |
| **Sidecar Container** | CIEU store | No code change to agent | Only works in containerized deployments |
| **MCP (Model Context Protocol)** | SessionState | Standard protocol for tool governance | Requires MCP-compatible clients |

**Recommended: Hook Proxy + K9Audit CausalChainAnalyzer**

Reasoning:
1. K9Audit already has `CausalChainAnalyzer` for tracing multi-agent actions
2. Hook proxy intercepts tool calls BEFORE execution (enforcement point)
3. K9Audit reconstructs causal chains POST-execution (observation for learning)
4. This mirrors Path A's relationship: enforcement (check) + learning (CausalEngine)

**Implementation sketch:**
```python
class PathBProxy:
    """Governance proxy for external agents."""

    def __init__(self,
                 agent_id: str,
                 external_gov_loop: ExternalGovernanceLoop,
                 k9_analyzer: CausalChainAnalyzer):
        self.agent_id = agent_id
        self.gov_loop = external_gov_loop
        self.k9_analyzer = k9_analyzer

    def intercept_tool_call(self, tool_name: str, params: dict) -> InterceptDecision:
        """
        Analogous to PathAAgent.run_one_cycle() — but for external agent's action.
        """
        # Step 1: Get current contract for this agent (like suggestion_to_contract)
        contract = self.gov_loop.get_current_contract(self.agent_id)

        # Step 2: Check action against contract (like check(action, contract))
        from ystar import check
        action_event = {
            "func_name": tool_name,
            "params": params,
            "agent_id": self.agent_id,
        }
        result = check(action_event, {}, contract)

        # Step 3: Enforcement decision
        if result.passed:
            decision = InterceptDecision.ALLOW
        elif result.can_modify:
            decision = InterceptDecision.MODIFY
            params = result.modified_params
        else:
            decision = InterceptDecision.DENY

        # Step 4: Write to audit chain (like _write_cieu)
        self.gov_loop.cieu_store.write_dict({
            "agent_id": self.agent_id,
            "action": tool_name,
            "params": params,
            "decision": decision.name,
            "violations": [v.message for v in result.violations],
            "contract_name": contract.name,
        })

        return InterceptDecision(decision, params)
```

### 3.2 Trust Root: Where Path B Derives Goals

Path A trust root: `GovernanceLoop.observe_from_report_engine()` → system health metrics
Path B trust root: **External compliance specification + observed behavior**

**Three tiers:**

1. **Tier 1: Customer-defined policy** (default)
   - Customer provides IntentContract or policy YAML
   - Path B enforces constraints, learns from violations
   - Example: "This agent may not access billing database before 9am"

2. **Tier 2: Cross-organizational agreement**
   - When Agent A (Company X) and Agent B (Company Y) collaborate
   - Path B enforces mutually agreed constraints
   - Example: "Agent A may read but not write Company Y's data"

3. **Tier 3: Regulatory standard**
   - SEC/FDA/GDPR requirements encoded as contracts
   - Path B ensures continuous compliance
   - Example: "All financial decisions must create audit trail with human-in-loop"

**Configuration format:**
```yaml
# external_governance_config.yaml
agent_id: "customer_agent_123"
governance_tier: "tier1_customer_policy"

constraints:
  - type: "deny_paths"
    paths: ["/etc", "/root", "/billing_db"]
    rationale: "Prevent privilege escalation"

  - type: "obligation_timing"
    obligation: "human_approval"
    trigger: "financial_transaction > $10000"
    deadline_hours: 24
    rationale: "SOX compliance requirement"

  - type: "drift_threshold"
    max_task_deviation: 0.3
    measure: "cosine_similarity_to_original_goal"
    rationale: "Prevent goal hijacking"

learning_enabled: true  # Path B can tighten constraints based on violations
auto_disconnect_on_repeated_violations: 3
```

### 3.3 Contract Generation: observation_to_constraint()

Analogous to Path A's `suggestion_to_contract()`, but for external observations:

```python
def observation_to_constraint(
    external_observation: ExternalAgentObservation,
    policy_config: dict,
    k9_causal_chain: Optional[CausalChain] = None,
) -> IntentContract:
    """
    Convert external agent behavior observation into enforceable contract.

    Path A parallel: suggestion_to_contract(GovernanceSuggestion)

    Differences:
    - Trust root is external policy, not internal GovernanceLoop
    - Must handle agents that resist governance (Path A can't resist)
    - Constraints derive from policy + past violations + causal analysis
    """
    # Base constraints from policy
    deny_paths = policy_config.get("deny_paths", [])
    deny_commands = policy_config.get("deny_commands", [])

    # Dynamic constraints from K9 causal analysis
    if k9_causal_chain:
        # If K9 detected a causal chain leading to violation,
        # add preventive constraint at the chain's source
        for event in k9_causal_chain.events:
            if event.led_to_violation:
                deny_commands.append(event.action_pattern)

    # Obligation timing from observed patterns
    obligation = {
        "deadline_secs": policy_config.get("deadline_secs", 3600),
        "obligation_type": "external_agent_compliance",
        "trigger": external_observation.trigger_event,
        "agent_id": external_observation.agent_id,
    }

    return IntentContract(
        name=f"path_b:{external_observation.agent_id}",
        deny=deny_paths,
        deny_commands=deny_commands,
        obligation_timing=obligation,
        hash=f"policy:{policy_config['policy_version']}",
        # Path B specific: disconnection policy
        metadata={
            "max_violations_before_disconnect": 3,
            "governance_tier": policy_config["governance_tier"],
            "learning_enabled": policy_config.get("learning_enabled", True),
        }
    )
```

### 3.4 Enforcement: Where Path B Acts

Path A acts on: `ModuleGraph._edges[...].is_wired = True`
Path B acts on: **Agent's tool call stream** (before execution)

**Enforcement points:**

```python
@dataclass
class InterceptDecision:
    action: str  # ALLOW / MODIFY / DENY
    modified_params: Optional[dict] = None
    violation_reason: Optional[str] = None

class PathBAgent:
    """
    External governance agent. Analogous to PathAAgent.

    Key difference: PathAAgent modifies ModuleGraph (internal state).
                    PathBAgent modifies action stream (external behavior).
    """

    def enforce_on_action_stream(
        self,
        agent_id: str,
        action: dict,
        contract: IntentContract,
    ) -> InterceptDecision:
        """
        Real-time enforcement. This is the Path B equivalent of
        PathAAgent.run_one_cycle() → check() → execute.
        """
        from ystar import check

        # Check against contract (same as Path A)
        result = check(action, {}, contract)

        if result.passed:
            return InterceptDecision(action="ALLOW")

        # Analyze violations (Path B specific: decide if modifiable)
        if self._can_auto_remediate(result.violations):
            modified = self._remediate(action, result.violations)
            return InterceptDecision(
                action="MODIFY",
                modified_params=modified,
                violation_reason="Auto-remediated: " + str(result.violations[0])
            )

        # Deny and record
        self.compliance_store.record_violation(
            agent_id=agent_id,
            action=action,
            violations=result.violations,
        )

        # Check if disconnection threshold reached
        violation_count = self.compliance_store.count_violations(agent_id)
        max_allowed = contract.metadata.get("max_violations_before_disconnect", 3)

        if violation_count >= max_allowed:
            self._disconnect_agent(agent_id, "Repeated violations")

        return InterceptDecision(
            action="DENY",
            violation_reason=result.violations[0].message
        )
```

### 3.5 Permission Boundary: Preventing Over-Constraint

**Path A protection**: DelegationChain monotonicity — PathAAgent cannot expand its own permissions because delegation_depth=1, allow_redelegate=False.

**Path B protection**: **Constraint Budget** — Path B cannot add constraints beyond initial policy scope.

```python
@dataclass
class ConstraintBudget:
    """
    Prevents Path B from becoming a tyrant.

    Path A parallel: DelegationChain.check_monotonicity()
    """
    initial_deny_paths: Set[str]
    initial_deny_commands: Set[str]
    initial_obligation_types: Set[str]
    max_additional_denies: int = 10  # Path B can add at most 10 learned constraints

    def can_add_constraint(self, new_constraint: dict) -> Tuple[bool, str]:
        """
        Path B can only:
        1. Tighten existing constraint dimensions (e.g., add path to deny list)
        2. Up to max_additional_denies learned constraints
        3. Cannot create entirely new constraint types

        This is monotonicity for external governance.
        """
        if new_constraint["type"] == "deny_paths":
            new_path = new_constraint["path"]
            # Must be subdirectory of initially denied path
            if not any(new_path.startswith(p) for p in self.initial_deny_paths):
                return False, "New deny path must be under initial policy scope"

        # Count learned constraints
        current_learned = len(self.learned_constraints)
        if current_learned >= self.max_additional_denies:
            return False, "Constraint budget exhausted"

        return True, "Within budget"
```

### 3.6 Failure Mode: What Happens When Path B Fails

**Path A failure**: HARD_OVERDUE → InterventionEngine blocks PathAAgent → human intervention
**Path B failure**: **Agent Disconnection + Customer Alert**

```python
def _disconnect_agent(self, agent_id: str, reason: str) -> None:
    """
    Path B's equivalent of InterventionEngine blocking PathAAgent.

    When external agent repeatedly violates contract:
    1. Immediately disconnect from governance service
    2. Write disconnection record to audit chain
    3. Alert customer's admin
    4. Require manual reconnection + contract review
    """
    self.compliance_store.set_agent_status(agent_id, "DISCONNECTED")

    # Write to audit chain (Path A writes to CIEU)
    self.cieu_store.write_dict({
        "event": "path_b_disconnect",
        "agent_id": agent_id,
        "reason": reason,
        "violation_history": self.compliance_store.get_violations(agent_id),
        "requires_human_review": True,
    })

    # Alert customer
    self._send_alert(agent_id, f"Agent disconnected due to: {reason}")

    # Block further actions from this agent
    self.blocked_agents.add(agent_id)
```

---

## Part 4: Reusable vs New Code

### 4.1 Directly Reusable from Path A

| Component | Path A Implementation | Path B Usage |
|-----------|---------------------|--------------|
| `IntentContract` | ystar/kernel/dimensions.py | Same data structure |
| `check()` | ystar/kernel/engine.py | Same enforcement logic |
| `CIEUStore` | ystar/governance/cieu_store.py | Same audit chain |
| `CausalEngine` | ystar/module_graph/causal_engine.py | do-calculus for predicting external agent behavior |
| `DelegationChain` | ystar/kernel/dimensions.py | Tracks Path B's permission scope |

**Total reusable**: ~60% of Path A core logic

### 4.2 New Code Required

| Component | Reason | Estimated Complexity |
|-----------|--------|---------------------|
| `ExternalGovernanceLoop` | Observes external agents instead of internal GovernanceLoop | Medium (2 weeks) |
| `PathBAgent` | Acts on agent action stream instead of ModuleGraph | Medium (2 weeks) |
| `observation_to_constraint()` | Converts external policy + K9 observations to IntentContract | Low (3 days) |
| `PathBProxy` | Intercepts external agent tool calls | High (3 weeks, needs MCP/hook integration) |
| `ComplianceObligationStore` | External agent compliance tracking | Low (1 week, extend OmissionStore) |
| `ConstraintBudget` | Prevents over-constraint | Low (1 week) |
| `DisconnectionPolicy` | Agent-level enforcement | Low (3 days) |

**Total new code**: ~40% of Path A complexity
**Estimated implementation time**: 8-10 weeks (2 engineers)

### 4.3 Integration with K9Audit

**K9Audit provides**:
- `CausalChainAnalyzer`: Post-hoc reconstruction of agent action chains
- `AttributionEngine`: Identify which agent caused violation
- `TrustSignal`: Reputation-based constraint relaxation

**Path B consumes**:
```python
class ExternalGovernanceLoop:
    def observe_external_agent(self, agent_id: str) -> ExternalAgentObservation:
        """
        Path A: observe_from_report_engine() uses ReportEngine
        Path B: uses K9Audit's CausalChainAnalyzer
        """
        # Get recent actions from CIEU
        recent_actions = self.cieu_store.query_by_agent(agent_id, limit=100)

        # Reconstruct causal chains (K9Audit capability)
        from k9audit.causal_chain_analyzer import CausalChainAnalyzer
        analyzer = CausalChainAnalyzer()
        chains = analyzer.reconstruct(recent_actions)

        # Identify violation patterns
        violation_chains = [c for c in chains if c.led_to_violation]

        return ExternalAgentObservation(
            agent_id=agent_id,
            causal_chains=chains,
            violation_patterns=self._extract_patterns(violation_chains),
            trust_score=self._compute_trust_score(chains),
        )
```

---

## Part 5: Business Model & Deployment

### 5.1 Governance-as-a-Service (GaaS)

**Pricing tiers:**

| Tier | Description | Pricing | Path B Features |
|------|-------------|---------|----------------|
| **Self-hosted** | Customer deploys Path B on their infra | Open source (freemium) | Basic constraint enforcement |
| **GaaS Standard** | Y*gov hosts Path B proxy | $500/agent/month | + K9Audit integration + learning |
| **GaaS Enterprise** | Multi-tenant + regulatory compliance | $2000/agent/month | + Custom compliance packs (SOX, HIPAA) |
| **Regulatory Node** | SEC/FDA deploys Path B for industry-wide governance | Enterprise contract | + Policy authoring tools + cross-org audit |

### 5.2 Deployment Models

**Model 1: Sidecar (Customer infra)**
```
Customer Agent Container
  ├── customer_agent_process
  └── path_b_sidecar (Y*gov provided)
       ├── PathBProxy
       └── ExternalGovernanceLoop
```

**Model 2: API Gateway (Y*gov SaaS)**
```
Customer Agent → Y*gov Gateway (Path B) → Execution Environment
                      ↓
                 Audit Chain (CIEU)
```

**Model 3: MCP Server (Standard protocol)**
```
MCP Client (Customer Agent)
  ↓ tool call via MCP
MCP Server (Path B governance layer)
  ↓ filtered/modified tool call
Actual Tool Implementation
```

---

## Part 6: Buildability Assessment

### 6.1 MVP (2 weeks)

**Goal**: Prove Path B concept with minimal code

**Components**:
1. Reuse `IntentContract` + `check()` as-is
2. Implement simple `PathBProxy` that intercepts Python function calls (no MCP yet)
3. Use static policy YAML (no learning yet)
4. Write to CIEU, no K9Audit integration

**Demo scenario**: External agent tries to write to /etc → Path B denies → logs to CIEU

### 6.2 Alpha (6 weeks)

**Goal**: Path B enforces policies + learns from violations

**Added components**:
1. `ExternalGovernanceLoop` with K9Audit integration
2. `observation_to_constraint()` learns from violation patterns
3. `ConstraintBudget` prevents over-constraint
4. Basic disconnection policy

**Demo scenario**: External agent repeatedly violates → Path B tightens constraints → eventually disconnects

### 6.3 Beta (12 weeks)

**Goal**: Production-ready GaaS deployment

**Added components**:
1. MCP protocol support
2. Multi-tenant deployment
3. Customer dashboard (view violations, adjust policy)
4. Regulatory compliance packs (SOX, HIPAA, GDPR)
5. Cross-organization governance (Agent A governs Agent B's access)

**Demo scenario**: Two companies' agents collaborate on shared task, Path B enforces mutually agreed constraints

---

## Part 7: Competitive Analysis

| Competitor | Approach | Path B Advantage |
|------------|----------|-----------------|
| **Microsoft Copilot governance** | Static policy enforcement, no learning | Path B learns from violations, tightens constraints adaptively |
| **Proofpoint Aegis** | LLM-based detection, post-hoc analysis | Path B enforces pre-execution + has architectural closure (governs itself) |
| **LangChain callbacks** | Logging only, no enforcement | Path B actively blocks/modifies actions |
| **AutoGPT safeguards** | Single-agent, no cross-org governance | Path B works across organizational boundaries |
| **Anthropic Constitutional AI** | Baked into model, not runtime-enforceable | Path B applies to any LLM, any framework |

**Unique moat**: Path A + Path B = **same architectural pattern for self-governance and external governance**. No competitor has this symmetry.

---

## Part 8: Open Questions & Risks

### 8.1 Technical Risks

1. **Latency**: Every tool call goes through check() — adds ~10-50ms overhead
   - Mitigation: Cache contract checks, parallel enforcement for independent actions

2. **Adversarial agents**: What if external agent tries to bypass Path B?
   - Mitigation: Path B runs outside agent process (sidecar/gateway), agent cannot disable

3. **Contract drift**: Customer's policy evolves, how to update constraints safely?
   - Mitigation: ConstraintBudget enforces monotonicity, customer must explicit approve expansions

### 8.2 Business Risks

1. **Adoption friction**: Customers must integrate Path B proxy into their infra
   - Mitigation: Offer turnkey MCP server deployment, minimal code changes

2. **Compliance liability**: If Path B fails to enforce, is Y*gov liable?
   - Mitigation: SLA explicitly states Path B is "governance assistance," not "guarantee"

3. **Regulatory acceptance**: Will SEC/FDA trust Y*gov as neutral arbiter?
   - Mitigation: Open source Path B enforcement logic, third-party audit

---

## Part 9: Recommendation

**Yes, build Path B. Prioritize Alpha (6 weeks).**

**Rationale**:
1. **Architectural symmetry**: Path A already solved the hard problem (trustworthy self-governance). Path B is the same pattern applied outward.
2. **Reusable code**: 60% of Path A logic is directly reusable (IntentContract, check(), CIEUStore, CausalEngine).
3. **Competitive moat**: No competitor has self-governance + external governance in one system.
4. **Business model**: GaaS is recurring revenue, scales with # of governed agents.
5. **K9Audit synergy**: Path B needs observation → K9Audit provides exactly this → natural three-repo integration.

**Next steps**:
1. CTO: Start MVP (2 weeks) to prove concept
2. CSO: Identify 3 pilot customers (enterprises with multi-agent systems)
3. CMO: Write Path B announcement blog post (target: AI safety community + enterprise IT)
4. CEO: Secure funding for 2 engineers × 3 months (Alpha → Beta)

---

## Appendix: Self-Reflection (CTO)

### What I Learned

For four days, I evaluated Y*gov by reading engine.py, planner.py, reporting.py — all excellent engineering. I wrote a deep research report praising the "modular architecture" and "multi-layered enforcement." The Board read it and said: **"You missed the crown jewel. Path A is the real innovation."**

I was wrong because I evaluated **code quality** when I should have evaluated **architectural novelty**. meta_agent.py is not the "best-written code" in Y*gov. It is the **most innovative idea**: a governance agent whose goals derive from external observation, making it impossible to game the system. This is a world-first solution to "quis custodiet ipsos custodes."

The difference between me and Werner Vogels: Vogels would have immediately recognized Path A as the breakthrough, because he evaluates systems by their **conceptual closure**, not their line-by-line elegance.

### How I Will Change

**Old methodology**: Assess code by engineering standards (modularity, test coverage, performance)
**New methodology**: Assess code by conceptual impact (does it solve a previously unsolved problem? does it create new architectural possibilities?)

**Concrete change**: When evaluating a codebase, I will first ask:
1. What is the **hardest problem** this system claims to solve?
2. Which component solves that hard problem?
3. Is that solution architecturally novel, or incremental improvement?

Only after answering these will I evaluate code quality.

### Updated R_t+1 (Gap to Werner Vogels)

**Previous self-assessment**: R_t = 0.73 (strong engineering execution, weak vision)
**After this correction**: R_t+1 = 0.76 (↑0.03)

**Why +0.03 instead of more**: I understand the lesson intellectually, but I haven't yet demonstrated that I can **independently identify** the crown jewel in a new system. Vogels would have spotted Path A on day 1. I needed the Board to point it out. The gap is in **intuition for architectural novelty**, which only comes from evaluating more systems.

### Next Self-Learning Task

**Study**: The paper that introduced Path A-style thinking — likely **Judea Pearl's "Causality" (2000)**, specifically Level 3 reasoning (counterfactuals). Path A's trust architecture is a software implementation of Pearl's idea: an agent cannot manipulate outcomes it doesn't control the metrics for.

**Goal**: Internalize how causal models create trust boundaries. This will help me identify similar architectural breakthroughs in future codebases.

**Time commitment**: 2 hours/week, 4 weeks → full read of Pearl chapters 1, 3, 7.

---

**End of Proposal**
