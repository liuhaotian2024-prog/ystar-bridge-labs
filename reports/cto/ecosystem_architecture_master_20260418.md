# Ecosystem Architecture Master Proposal — Y* Bridge Labs

**Date**: 2026-04-18
**Author**: Ethan Wright, CTO
**Audience**: Board (Haotian Liu) as primary approver; CEO (Aiden) for migration oversight; CTO (self) for implementation ownership; all engineers for execution.
**Research basis**: Full 3-repo source audit (survey document). OS kernel architecture (Liedtke L4 microkernel, Mach). Hexagonal Architecture (Cockburn 2005). Domain-Driven Design (Evans 2003). Event-Driven Architecture (Fowler 2006). Open Policy Agent (CNCF). Service Mesh control/data plane separation (Istio). Actor Model (Hewitt 1973, Erlang OTP). Constitutional AI (Anthropic 2023). MCP (Model Context Protocol, Anthropic 2024). Chaos Engineering (Netflix 2011). Martin Fowler's "Strangler Fig" migration pattern.
**Synthesis**: This proposal presents a single unified architecture that resolves the 16 problems identified in the survey. The architecture is a 4-layer model inspired by OS kernel design and service mesh topology, applied to multi-agent governance.

---

## Part A — Theoretical Foundations

### Theory 1: Microkernel Architecture (L4/Mach — OS Design)

**(a) Core pattern**: A minimal kernel provides only the essential primitives (IPC, address spaces, scheduling). All other functionality — drivers, filesystems, networking — runs as user-space servers that communicate through the kernel's IPC.

**(b) Mapping to our ecosystem**: Y-star-gov's `check()` + `enforce()` + `CIEU` is the microkernel. Everything else — identity detection, boundary enforcement, session boot, dispatch routing, obligation scanning — should be user-space "servers" (router rules) that plug into the kernel, not compiled into it.

**(c) Adoption rationale**: ADOPT. Our current architecture is monolithic — boundary_enforcer.py at 3070 lines is a monolithic kernel module. The microkernel pattern gives us: (1) crash isolation (a bad router rule cannot kill the enforcement kernel), (2) independent deployment (rules can be updated without recompiling the kernel), (3) clear trust boundary (kernel is auditable, user-space rules can be swapped). The counter-argument is performance — microkernel IPC overhead. But our check() runs in 0.042ms; the overhead of calling router rules via function dispatch is negligible compared to the ~50-100ms Python process startup that hook_wrapper.py already pays per invocation.

### Theory 2: Hexagonal Architecture / Ports-and-Adapters (Cockburn 2005)

**(a) Core pattern**: The application core (business logic) has no dependencies on external systems. External systems connect through "ports" (interfaces) and "adapters" (implementations). The core is testable in isolation.

**(b) Mapping**: Y-star-gov's kernel (check/enforce/CIEU) is the hexagonal core. The "ports" are: HookPort (receives tool-call events), MCPPort (receives MCP tool calls), CLIPort (receives CLI commands). The "adapters" are: Claude Code adapter (hook_wrapper), OpenClaw adapter, gov-mcp adapter. Currently, the adapters contain business logic (identity, boundary, routing) that belongs in the core.

**(c) Adoption rationale**: ADOPT. This directly supports Iron Rule 3 (ecosystem neutrality). Every adapter should be a thin translator. Currently hook_wrapper.py is a fat adapter — it contains identity override, CEO code-write block, CZL-159 validation, dispatch gate, and agent stack logic. All of this must move to the core.

### Theory 3: Control Plane / Data Plane Separation (Istio Service Mesh)

**(a) Core pattern**: In a service mesh, the data plane (Envoy proxies) handles every request inline — routing, load balancing, TLS termination. The control plane (Istiod) configures the data plane — pushes policy, collects telemetry, manages certificates. They share no runtime dependencies; the data plane operates even if the control plane is down.

**(b) Mapping**: The hook (data plane) intercepts every tool call and makes ALLOW/DENY/REDIRECT decisions using pre-compiled policy. Labs (control plane) manages contracts, assigns tasks, generates policy updates, collects audit data. gov-mcp is a second data-plane instance for external consumers. The control plane updates the data plane by writing to `.ystar_session.json` and router rule registrations, not by being imported at runtime.

**(c) Adoption rationale**: ADOPT. This is the key insight that solves the sys.path.insert pandemic. The data plane (Y-star-gov) must NEVER import from the control plane (Labs). The control plane pushes configuration TO the data plane (writes JSON/YAML files, registers router rules). The data plane reads configuration; it does not import source code.

### Theory 4: Event-Driven Architecture (Fowler 2006, Event Sourcing)

**(a) Core pattern**: State changes are recorded as an immutable sequence of events. Current state is derived by replaying events. Components communicate through events, not direct calls.

**(b) Mapping**: CIEU IS event sourcing — every governance decision is an event. The missing piece is that other components (dispatch, session boot, obligation) should communicate through CIEU events, not through direct file reads or sys.path imports.

**(c) Adoption rationale**: ADOPT for inter-component communication. All workflow triggers (session start, obligation overdue, dispatch post) should be CIEU events that router rules subscribe to.

### Theory 5: Open Policy Agent (OPA, CNCF)

**(a) Core pattern**: Policy decisions are separated from policy enforcement. OPA provides a general-purpose policy engine (Rego language) that any service can query. Policies are documents, not code baked into services.

**(b) Mapping**: Y-star-gov's check() is analogous to OPA's evaluation engine. AGENTS.md is analogous to Rego policy documents. The `nl_to_contract` translation in gov-mcp is a partial implementation of policy compilation.

**(c) Adoption rationale**: ADOPT the principle (policy as data, not code). Our current AGENTS.md is 3000+ lines of prose. It should compile to a structured policy document (JSON/YAML) that the enforcement engine consumes without regex parsing. This is already partially done via `.ystar_session.json` (confidence 0.98 vs AGENTS.md confidence 0.5-0.7). Complete the transition.

### Theory 6: Actor Model (Hewitt 1973, Erlang OTP)

**(a) Core pattern**: Actors are isolated units of computation. Each actor has a mailbox (message queue), processes one message at a time, and can create new actors. Failure isolation is built-in — a crashed actor doesn't take down the system.

**(b) Mapping**: Each Y* Bridge Labs agent (CEO, CTO, engineers) is an actor. The dispatch_board is a message broker. The hook is a supervisor (monitors all actions). Currently, "actors" share mutable global state (`.ystar_active_agent` file) which violates actor isolation.

**(c) Adoption rationale**: ADOPT the principle. Agent identity must be per-invocation (carried in the payload), not global mutable file state. The `.ystar_active_agent` file is a concurrency hazard — two parallel agents writing to it creates race conditions.

### Theory 7: Domain-Driven Design — Bounded Contexts (Evans 2003)

**(a) Core pattern**: Large systems are decomposed into bounded contexts. Each context has its own ubiquitous language, its own models, and explicit interfaces to other contexts. Anti-corruption layers prevent model leakage across boundaries.

**(b) Mapping**: Three bounded contexts: (1) Governance Kernel (check, enforce, CIEU), (2) Company Operations (Labs, agents, content, knowledge), (3) Distribution (gov-mcp, CLI, marketplace). Currently there is no anti-corruption layer — Labs directly imports governance internals, governance directly imports Labs scripts.

**(c) Adoption rationale**: ADOPT. Each repo should have a clean public API. Cross-context communication goes through defined interfaces (JSON events, CLI commands, configuration files), never through Python imports.

### Theory 8: Strangler Fig Migration (Fowler 2004)

**(a) Core pattern**: Replace a legacy system incrementally. New functionality wraps around the old system. As each piece is migrated, the old system shrinks. Eventually the old system is removed entirely.

**(b) Mapping**: The enforce-as-router migration IS a strangler fig. New router rules wrap around old Labs scripts. As each workflow is migrated to a router rule, the corresponding Labs script becomes dead code. Phase 4 removes dead scripts.

**(c) Adoption rationale**: ADOPT. This is the only safe migration strategy. Big-bang rewrites fail. The CEO's 4-phase migration plan already follows this pattern; this proposal formalizes it.

---

## Part B — The Architecture

### Layer Model (4 Layers)

```
┌─────────────────────────────────────────────────────────────┐
│                    LAYER 4: INTERFACE                        │
│                                                             │
│  Claude Code Hook  │  gov-mcp Server  │  CLI  │  OpenClaw   │
│  (thin adapter)    │  (MCP adapter)   │       │  (adapter)  │
│                                                             │
│  Responsibility: Protocol translation ONLY                  │
│  - Receives platform-specific payload                       │
│  - Translates to IngressRequest                             │
│  - Forwards to Layer 3                                      │
│  - Translates IngressResponse back to platform format       │
│  - ZERO business logic                                      │
└──────────────────────────┬──────────────────────────────────┘
                           │ IngressRequest / IngressResponse
                           v
┌─────────────────────────────────────────────────────────────┐
│                    LAYER 3: ROUTING                          │
│                                                             │
│  RouterRegistry (Y-star-gov)                                │
│  - Registered rules evaluated in priority order             │
│  - Constitutional rules (priority 1000+)                    │
│  - Workflow rules (priority 100-999)                        │
│  - Advisory rules (priority 1-99)                           │
│                                                             │
│  Responsibility: WHICH governance path to take              │
│  - Identity resolution (deterministic from payload)         │
│  - Rule matching (detector functions)                       │
│  - Decision routing (INVOKE / INJECT / REDIRECT / PASS)     │
│  - Chain depth guard (prevents loops)                       │
│                                                             │
│  New decisions:                                             │
│  - INVOKE(rule_id) → execute rule's executor                │
│  - INJECT(context) → append context to ALLOW response       │
│  - REDIRECT(fix_cmd) → return fix instructions              │
│  - AUTO_POST(task) → auto-post whiteboard task              │
│  - PASS → fall through to Layer 2                           │
└──────────────────────────┬──────────────────────────────────┘
                           │ (PASS decisions only)
                           v
┌─────────────────────────────────────────────────────────────┐
│                    LAYER 2: ENFORCEMENT                      │
│                    (The Microkernel)                         │
│                                                             │
│  check() → deterministic policy evaluation                  │
│  enforce() → full governance (delegation, drift, CIEU)      │
│                                                             │
│  Responsibility: IS this action allowed                     │
│  - Contract-based access control                            │
│  - Boundary enforcement (paths, tools, domains)             │
│  - Delegation chain verification                            │
│  - Drift detection                                          │
│  - ALLOW / DENY / ESCALATE                                  │
│                                                             │
│  Invariants:                                                │
│  - No LLM (Iron Rule 1)                                     │
│  - No hardcoded paths (Iron Rule 2)                         │
│  - No external imports (no sys.path.insert)                 │
│  - Deterministic: same input → same output                  │
│  - Audit: every decision writes to CIEU                     │
└──────────────────────────┬──────────────────────────────────┘
                           │ (all decisions)
                           v
┌─────────────────────────────────────────────────────────────┐
│                    LAYER 1: EVIDENCE                         │
│                                                             │
│  CIEU Store (single instance per process)                   │
│  - Contextual / Intervention / Execution / Update events    │
│  - SHA-256 Merkle chain                                     │
│  - Writer-token anti-fabrication                            │
│  - Event sourcing: state = replay(events)                   │
│                                                             │
│  Responsibility: WHAT happened (tamper-evident audit trail)  │
│  - Records every decision from Layer 2/3                    │
│  - Records every workflow action from Layer 3 executors     │
│  - Single database per deployment                           │
│  - Queryable by all layers (read-only for 3/4)              │
└─────────────────────────────────────────────────────────────┘
```

### Three-Repository New Positioning

#### Labs (ystar-company) = Control Plane + Content Store

**IS**: The company's operational headquarters. Manages contracts, assigns tasks, stores knowledge, produces content.

**IS NOT**: An enforcement engine. Does not contain governance logic. Does not contain routing logic. Does not contain identity detection. Does not import Y-star-gov at the Python module level.

**New structure**:
```
ystar-company/
├── AGENTS.md              ← Source contract (compiled to .ystar_policy.json)
├── CLAUDE.md              ← Claude Code overlay
├── .ystar_policy.json     ← COMPILED policy (machine-readable, generated)
├── .ystar_session.json    ← Session runtime config
├── .ystar_cieu.db         ← Single CIEU database
├── hooks/
│   └── pretool.sh         ← 3-line thin adapter: reads stdin, pipes to
│                             `python -m ystar.adapters.hook`, writes stdout
├── router_rules/          ← NEW: company-specific router rules (Python)
│   ├── identity_rules.py  ← Identity reconciliation rules
│   ├── session_rules.py   ← Session boot/end workflow rules
│   ├── dispatch_rules.py  ← Whiteboard dispatch rules
│   ├── ceo_guard_rules.py ← CEO code-write prohibition, pre-output
│   └── ...
├── content/               ← Blog, articles, video scripts (KEEP)
├── reports/               ← Performance, debt, experiments (KEEP)
├── knowledge/             ← Lessons, theory, gaps, cases (KEEP)
├── governance/            ← Charter, amendments, DNA log (KEEP)
├── scripts/               ← REDUCED: only content tools + utilities
├── memory/                ← Session handoff, continuation (KEEP)
└── archive/               ← Migrated scripts (dead code preserved)
```

#### Y-star-gov = Governance Kernel + Runtime Engine (Layers 1-3)

**IS**: The product. Installable via `pip install ystar`. Contains the microkernel (check/enforce/CIEU), the routing layer (RouterRegistry), and all adapters (hook, MCP, CLI).

**IS NOT**: A company-specific tool. Does not import from Labs. Does not contain Labs' hook_wrapper.py logic. Does not contain hardcoded paths to Labs directories.

**New structure**:
```
Y-star-gov/
├── ystar/
│   ├── kernel/            ← Layer 2: check(), enforce(), contract compiler
│   │   ├── engine.py      ← Core check logic
│   │   ├── compiler.py    ← AGENTS.md → policy.json compiler
│   │   ├── dimensions.py  ← IntentContract, DelegationChain
│   │   └── ...
│   ├── governance/        ← Layer 1+2: CIEU, omission, causal
│   │   ├── cieu_store.py  ← Single CIEU store implementation
│   │   ├── omission_engine.py
│   │   ├── router_registry.py  ← Layer 3: RouterRegistry
│   │   └── ...
│   ├── adapters/          ← Layer 4: Thin protocol translators
│   │   ├── hook.py        ← Claude Code adapter (THIN: translate + call Layer 3)
│   │   ├── mcp.py         ← MCP adapter (replaces gov-mcp/server.py core)
│   │   ├── cli.py         ← CLI adapter
│   │   └── openclaw.py    ← OpenClaw adapter
│   ├── rules/             ← Built-in router rules (universal, not company-specific)
│   │   ├── break_glass.py ← Emergency break-glass rule (priority 2000)
│   │   ├── identity.py    ← Default identity resolution
│   │   └── boundary.py    ← Default boundary enforcement
│   └── contrib/           ← Community-contributed router rules
└── tests/
    ├── test_kernel/
    ├── test_routing/
    ├── test_adapters/
    └── test_integration/  ← NEW: cross-layer integration tests
```

#### gov-mcp = Distribution Adapter (Layer 4 for MCP)

**IS**: A thin MCP server that wraps Y-star-gov for external consumers. Installable via `pip install gov-mcp`. Contains ONLY protocol translation (MCP JSON-RPC <-> IngressRequest).

**IS NOT**: A governance engine. Does not duplicate enforce/check logic. Does not maintain its own CIEU store. Does not contain dispatch logic (moves to Y-star-gov).

**New structure**:
```
gov-mcp/
├── gov_mcp/
│   ├── server.py          ← FastMCP server (THIN: translate MCP calls to ystar API)
│   ├── installer.py       ← One-command setup (detects environment, configures)
│   └── health.py          ← Health check endpoints
├── plugin.json            ← MCP marketplace manifest
└── tests/
```

### Connection Mechanism (The Critical Wire)

#### 1. Hook Entry Point (Claude Code -> Y-star-gov)

**Current**: Labs' hook_wrapper.py (220+ lines) does sys.path.insert, identity override, CEO blocks, dispatch gates, then calls check_hook.

**Target**: A 10-line shell script or Python one-liner.

```bash
#!/usr/bin/env bash
# hooks/pretool.sh — Y*gov Claude Code hook (thin adapter)
exec python3 -m ystar.adapters.hook --rules-dir "$YSTAR_RULES_DIR" 2>/dev/null
```

Or in Python:
```python
#!/usr/bin/env python3
"""Y*gov Claude Code hook — thin adapter. All logic in ystar package."""
import sys, json
from ystar.adapters.hook import handle_hook_event
payload = json.loads(sys.stdin.buffer.read().decode('utf-8-sig'))
result = handle_hook_event(payload, rules_dir=os.environ.get("YSTAR_RULES_DIR"))
sys.stdout.write(json.dumps(result))
```

All the logic that currently lives in hook_wrapper.py moves into:
- Identity resolution -> `ystar.rules.identity` (built-in router rule)
- CEO code-write block -> `labs/router_rules/ceo_guard_rules.py` (company router rule, registered at boot)
- CZL-159 pre-output -> `labs/router_rules/ceo_guard_rules.py` (company router rule)
- Agent stack push -> `ystar.governance.agent_stack` (built-in, event-driven)
- CZL Gate 1 dispatch -> `labs/router_rules/dispatch_rules.py` (company router rule)

#### 2. Router Rule Registration (Labs -> Y-star-gov at boot time)

Labs registers company-specific router rules during session boot:
```python
# router_rules/session_rules.py
from ystar.governance.router_registry import RouterRule, RouterResult

session_boot_rule = RouterRule(
    rule_id="labs.session_boot",
    detector=lambda p: p.get("event_type") == "session_start",
    executor=lambda p: RouterResult(
        decision="invoke",
        script="session_boot",
        args={"agent_id": p.get("agent_id")},
    ),
    priority=500,
    metadata={"migrated_from": "governance_boot.sh"},
)
```

Registration happens via CLI:
```bash
ystar rules register --dir ./router_rules/
```

Or programmatically during boot:
```python
from ystar.governance.router_registry import get_default_registry
from router_rules import all_rules

registry = get_default_registry()
for rule in all_rules:
    registry.register_rule(rule)
```

#### 3. Policy Compilation (AGENTS.md -> .ystar_policy.json)

```bash
ystar compile-policy --agents-md ./AGENTS.md --output .ystar_policy.json
```

This replaces the current regex-based nl_to_contract translation. The compiled policy is a structured JSON file that the enforcement kernel reads. Changes to AGENTS.md require recompilation. The compiler validates consistency (no conflicting rules, no undefined agents).

#### 4. CIEU Unification

Single CIEU database per deployment. All entry points (hook, MCP, CLI) write to the same database. Path configured via `.ystar_session.json` or environment variable `YSTAR_CIEU_DB`.

#### 5. Version Management (Eliminates sys.path.insert)

Labs depends on Y-star-gov as a pip package:
```
# ystar-company/requirements.txt
ystar>=0.49.0,<1.0.0
```

Install in development:
```bash
pip install -e /path/to/Y-star-gov  # editable install for dev
```

This eliminates ALL sys.path.insert calls. Y-star-gov is importable as `import ystar` because it's properly installed. No path manipulation needed.

---

## Part C — Board Suggestion Evaluation: "Y*gov Directly Into Hook Enforce"

### Board's Exact Words
"我甚至在想要不要把 Y*gov 直接塞进 hook enforce 里面？"

### Assessment: ADOPT WITH BOUNDARIES

The Board's instinct is correct. The diagnosis is precise: governance features that exist outside the enforcement path are invisible to agents. Moving features INTO the enforcement path makes them automatically active.

**What to adopt**: The router-registry model. Every workflow, protocol, and knowledge-routing function registers as a router rule in Y-star-gov. The enforce hook evaluates all matching rules on every tool call. This IS "Y*gov directly in hook enforce" — the hook becomes the universal entry point for all agent governance.

**What boundary to preserve**: The distinction between KERNEL and RULES. Using the OS microkernel analogy:

- **Kernel** (must remain small, auditable, deterministic): `check()`, `enforce()`, `CIEU`, `DelegationChain`, `RouterRegistry` mechanism. This is the trust root. If this code has a bug, all governance fails. It must stay minimal (~2000 lines).

- **Rules** (can be large, company-specific, swappable): All the router rules that implement company workflows. Identity rules, session boot rules, dispatch rules, CEO guard rules, obligation rules. These run THROUGH the kernel's RouterRegistry but are not compiled INTO the kernel.

**Why not full monolith**: If we compile all 850 Labs files into a single enforcement binary:
1. Any bug in any script can crash the entire enforcement path
2. The enforcement layer becomes impossible to audit (violates Iron Rule 1's spirit)
3. External users cannot install Y-star-gov without Labs (violates product independence)
4. A change to a marketing script could break governance (blast radius)

**The correct analogy is Linux, not DOS**: Linux's kernel is ~30M lines. But device drivers, filesystems, and network stacks are loadable modules. They run at kernel privilege level (fast, integrated) but are separately compiled, separately tested, and separately loaded. Our router rules are kernel modules — they run inside the enforcement path (Board's goal achieved) but are separately maintained (product independence preserved).

### Technical Implementation

The existing `RouterRegistry` already supports this. The `register_rule()` API allows external code to register rules at runtime. The `priority` field controls evaluation order. The `MAX_CHAIN_DEPTH` guard prevents loops. The `execute_rule()` method catches exceptions so a crashing rule doesn't kill the kernel.

The missing pieces are:
1. A `rules_dir` parameter that loads all `.py` files from a directory and registers their rules
2. An `unregister_all()` method for clean session restart
3. An `IngressRequest` data class that normalizes payloads from different adapters
4. Integration with the existing `check_hook()` flow — router rules run BEFORE check/enforce

---

## Part D — Migration Roadmap

### Phase 1: Foundation (Eliminate Deadlocks) — ~200 tool_uses

**Y***: All 10 known lock-death patterns resolved. No agent session can enter a deadlocked state.

**Work**:
1. Fix identity resolution: Make `_detect_agent_id` accept ALL known name formats (including "Ethan-CTO", "Aiden-CEO", "cto", "ystar-cto") via case-insensitive fuzzy matching and configurable alias map loaded from `.ystar_session.json`.
2. Add break-glass: If identity cannot be resolved, default to "guest" with read-only permissions instead of blocking everything. Log a CIEU event.
3. Fix `_result_to_response` dead code (7 duplicate return blocks).
4. Remove reverse dependency: boundary_enforcer.py must not import from Labs. Per-rule detectors become router rules registered externally.
5. Write 10 lock-death regression tests.

### Phase 2: Thin Adapter + Rule Migration — ~500 tool_uses

**Y***: hook_wrapper.py reduced from 220+ lines to 10 lines. All its logic migrated to router rules registered via RouterRegistry.

**Work**:
1. Create `IngressRequest` dataclass in Y-star-gov (normalizes all hook payloads).
2. Add `load_rules_dir(path)` to RouterRegistry — scans directory, imports, registers.
3. Create `ystar-company/router_rules/` directory with:
   - `identity_rules.py` — identity alias resolution
   - `ceo_guard_rules.py` — CEO code-write block + CZL-159
   - `session_rules.py` — session boot/end workflow
   - `dispatch_rules.py` — whiteboard auto-post + stuck-claim watchdog
   - `obligation_rules.py` — obligation registration + overdue detection
4. Modify `check_hook()` to run RouterRegistry before check/enforce.
5. Replace hook_wrapper.py with thin adapter.
6. Eliminate sys.path.insert from Y-star-gov (install Labs' ystar dependency via pip -e).

### Phase 3: Consolidation + External Readiness — ~300 tool_uses

**Y***: External user can `pip install ystar && ystar hook-install && ystar doctor` on a fresh machine. gov-mcp becomes a thin MCP adapter. Single CIEU database per deployment.

**Work**:
1. Move gov-mcp's dispatch_logic.py and relevant server.py logic into ystar core.
2. Reduce gov-mcp to thin MCP adapter (~200 lines).
3. Implement `ystar compile-policy` CLI command.
4. Unify CIEU database (single path, configurable).
5. Write cross-repo integration test suite (10+ tests covering hook -> router -> enforce -> CIEU pipeline).
6. Archive migrated Labs scripts to `archive/`.
7. Update README, installation guide, troubleshooting.

### Success Criteria (Rt+1 = 0)

Board's goal is: "Labs team becomes a truly effective team governed by our own rules, efficiency, and commands across all dimensions."

Quantified:
1. **Zero lock-death**: No agent session enters a deadlocked state. Regression test suite covers all 10 known patterns plus 5 additional chaos scenarios.
2. **Zero sys.path.insert**: All cross-repo imports go through pip-installed packages.
3. **Feature discovery 100%**: A fresh agent (no memory, no CLAUDE.md reading) receives correct router-injected context on its first tool call. Tested by spawning a blank agent and verifying it can complete a standard task.
4. **Single audit trail**: All CIEU events from all entry points (hook, MCP, CLI) land in one database. `ystar verify` validates the complete chain.
5. **Hook adapter < 20 lines**: hook_wrapper.py is replaced by a thin adapter with zero business logic.
6. **External install < 5 minutes**: Time from `pip install ystar` to first governed tool call on a clean machine.
7. **Identity resolution 100%**: All known agent name formats resolve correctly. Test matrix covers 15+ name variants.
8. **Enforcement kernel < 3000 lines**: check() + enforce() + CIEU + RouterRegistry mechanism stays under 3000 lines total. Company-specific logic lives in rules/, not kernel.

### Risk Assessment

| Risk | Mitigation |
|------|------------|
| Router rule migration breaks existing enforcement | Strangler fig: old hook_wrapper.py and new router rules run in parallel during Phase 2. Old code removed only after new code passes all tests. |
| INVOKE chain loops | MAX_CHAIN_DEPTH guard already implemented (default 5). Add CIEU event on depth > 3 as early warning. |
| INJECT context pollution (prompt bloat) | Each INJECT rule has a token budget. Total injected context capped at 2000 tokens per tool call. Priority-based truncation. |
| pip -e editable install breaks on user machines | Phase 3 publishes Y-star-gov to PyPI. External users use release versions, not editable installs. |
| Regression during migration | 806+ existing Y-star-gov tests must pass at every commit. 10 new lock-death tests added in Phase 1. Cross-repo integration tests added in Phase 3. |

### Failure Rollback

If Phase 2 migration fails (new router rules produce incorrect enforcement decisions):
1. Revert hook_wrapper.py to current version (git revert)
2. Disable RouterRegistry evaluation in check_hook (feature flag: `YSTAR_ROUTER_ENABLED=0`)
3. Diagnose failed rules using CIEU event trail
4. Fix rules, re-enable, re-test

The feature flag approach means we can turn off the new routing layer without touching any code. This is the standard gradual rollout pattern.

---

## Part E — Whiteboard Tasks (Phase 1 Implementation)

The following tasks are ready for dispatch. Each is atomic (one deliverable), scoped to specific files, and has clear acceptance criteria.

### CZL-ARCH-1: Identity Resolution Hardening

- **atomic_id**: CZL-ARCH-1
- **scope**: `Y-star-gov/ystar/adapters/identity_detector.py`
- **description**: Expand `_AGENT_TYPE_MAP` with all known name variants including human-readable names ("Ethan-CTO", "Aiden-CEO", "Leo-Kernel", etc.). Add case-insensitive fuzzy matching fallback. Add "guest" default with read-only permissions instead of blocking on unknown identity. Add configurable alias map loaded from `.ystar_session.json` field `agent_aliases`.
- **acceptance criteria**:
  - All 15+ known agent name formats resolve to correct governance ID
  - Unknown agent names resolve to "guest" (not "agent")
  - "guest" has read-only permissions (Read, Glob, Grep allowed; Write, Edit, Bash denied)
  - 806+ existing tests pass
  - 5 new identity resolution tests added
- **estimated_tool_uses**: 40
- **engineer**: eng-kernel

### CZL-ARCH-2: Dead Code Cleanup in hook.py

- **atomic_id**: CZL-ARCH-2
- **scope**: `Y-star-gov/ystar/adapters/hook.py`
- **description**: Remove 6 duplicate unreachable return blocks in `_result_to_response()`. Add `# unreachable` comment lint rule. Run existing test suite to verify no behavior change.
- **acceptance criteria**:
  - `_result_to_response()` has exactly 1 return block for deny path
  - hook.py line count reduced by ~100 lines
  - 806+ existing tests pass
  - No behavioral change in any test
- **estimated_tool_uses**: 15
- **engineer**: eng-kernel

### CZL-ARCH-3: Remove Reverse Dependency (boundary_enforcer -> Labs)

- **atomic_id**: CZL-ARCH-3
- **scope**: `Y-star-gov/ystar/adapters/boundary_enforcer.py`
- **description**: Remove `sys.path.insert(0, ystar-company/scripts)` and the import of `per_rule_detectors`. Make per-rule detectors register as router rules via RouterRegistry instead of being imported as Python modules. Create a `ystar.adapters.boundary_enforcer_contrib` extension point that boundary_enforcer checks IF available (graceful degradation).
- **acceptance criteria**:
  - boundary_enforcer.py has zero imports from ystar-company
  - boundary_enforcer.py has zero sys.path.insert calls
  - Per-rule detector functionality preserved via router rule registration
  - 806+ existing tests pass
- **estimated_tool_uses**: 60
- **engineer**: eng-governance

### CZL-ARCH-4: RouterRegistry Rules Loader

- **atomic_id**: CZL-ARCH-4
- **scope**: `Y-star-gov/ystar/governance/router_registry.py`
- **description**: Add `load_rules_dir(path: Path)` method to RouterRegistry. Scans all `.py` files in the given directory, imports each, looks for `RULES` list at module level (list of RouterRule), and registers all. Add `unregister_all()` for clean restart. Add `IngressRequest` dataclass to normalize hook payloads from different adapters.
- **acceptance criteria**:
  - `load_rules_dir` successfully loads rules from a test directory
  - `unregister_all` clears all rules
  - `IngressRequest` normalizes Claude Code, MCP, and CLI payloads to uniform format
  - 5 new tests for loader and IngressRequest
  - Existing RouterRegistry tests still pass
- **estimated_tool_uses**: 45
- **engineer**: eng-kernel

### CZL-ARCH-5: Break-Glass Emergency Override

- **atomic_id**: CZL-ARCH-5
- **scope**: `Y-star-gov/ystar/rules/break_glass.py` (new file), `Y-star-gov/ystar/adapters/hook.py`
- **description**: Create a break-glass router rule at priority 2000 (highest). When environment variable `YSTAR_BREAK_GLASS=1` is set, all enforcement is bypassed — all actions ALLOW with CIEU event `BREAK_GLASS_ACTIVE`. This is the escape hatch for lock-death scenarios. Log every action taken during break-glass for post-incident review.
- **acceptance criteria**:
  - Setting `YSTAR_BREAK_GLASS=1` allows all actions
  - Every action during break-glass writes CIEU event with grade `break_glass`
  - Unsetting the variable restores normal enforcement
  - Break-glass CIEU events are visually flagged in `ystar report`
  - 3 new tests
- **estimated_tool_uses**: 35
- **engineer**: eng-platform

### CZL-ARCH-6: Thin Hook Adapter Prototype

- **atomic_id**: CZL-ARCH-6
- **scope**: `ystar-company/hooks/pretool_v2.py` (new), `Y-star-gov/ystar/adapters/hook.py`
- **description**: Create a prototype thin hook adapter (< 20 lines) that replaces hook_wrapper.py. Uses `python -m ystar.adapters.hook` with `--rules-dir` flag pointing to `ystar-company/router_rules/`. Requires CZL-ARCH-4 (RouterRegistry loader) to be complete first. Run side-by-side with existing hook_wrapper.py (feature-flagged via env var `YSTAR_HOOK_V2=1`).
- **acceptance criteria**:
  - New hook adapter is < 20 lines of code
  - With `YSTAR_HOOK_V2=1`, enforcement uses new adapter
  - Without the flag, old hook_wrapper.py is used (zero regression)
  - Identity resolution, CEO guard, and boundary enforcement all work via router rules
  - 5 integration tests comparing old vs new hook behavior
- **estimated_tool_uses**: 80
- **engineer**: eng-platform
- **depends_on**: CZL-ARCH-4

---

## Summary

The Y* Bridge Labs ecosystem has a sound product kernel (check/enforce/CIEU) buried under layers of organic growth, cross-repo coupling, and identity fragmentation. The architecture proposed here does not discard what works — it restructures how the pieces connect.

The core moves are:
1. **Eliminate sys.path.insert** — use proper pip packaging
2. **Thin the adapters** — hook_wrapper.py becomes 10 lines, all logic moves to router rules
3. **Separate kernel from rules** — microkernel stays small and auditable, company-specific logic registers externally
4. **Single CIEU database** — unified audit trail
5. **Identity resolution hardened** — fuzzy matching + guest fallback + no deadlock

Board's instinct ("put Y*gov into the hook") is validated and adopted as the router-registry architecture. The boundary preserved is kernel vs rules — not because the Board is wrong about integration, but because the same separation that makes Linux reliable makes Y*gov reliable.

---

**CTO Ethan Wright**
**Y* Bridge Labs**
**2026-04-18**
