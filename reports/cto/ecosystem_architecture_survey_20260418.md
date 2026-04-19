# Ecosystem Architecture Survey — Y* Bridge Labs

**Date**: 2026-04-18
**Author**: Ethan Wright, CTO
**Audience**: Board (Haotian Liu) as primary decision maker; CEO (Aiden) for migration planning; all engineers for implementation context.
**Research basis**: Full source-code audit of three repositories (ystar-company, Y-star-gov, gov-mcp) via Read/Grep/Glob tooling. CEO migration plan (enforce_as_router_migration_plan_20260418.md). Board memory entries (enforce_as_router_thesis, whiteboard_not_direct_spawn, posted_not_executed_hallucination). Prior architecture experience from Werner Vogels' "everything fails" principle and OS kernel design literature.
**Synthesis**: This survey identifies the root structural failures causing the lock-death, identity drift, feature invisibility, and governance deadlock patterns observed throughout 2026-04-16 to 2026-04-18.

---

## 1. Three-Repository Topology (Current State)

### 1.1 ystar-company (Labs)

**Role**: Company operations, governance contracts, agent memory, knowledge, scripts, marketing, sales, finance, content.

**Scale**:
- `scripts/*.py`: ~110 Python files
- `scripts/*.sh`: ~28 shell scripts
- `governance/*.md`: ~40 protocol documents
- `knowledge/**/*.md`: ~600+ knowledge files
- Total: ~850+ files

**Key interfaces**:
- `AGENTS.md` — governance contract source (3000+ lines, 20+ Iron Rules/amendments)
- `CLAUDE.md` — Claude Code system prompt overlay
- `.ystar_session.json` — runtime session config
- `.ystar_active_agent` — agent identity marker file
- `.ystar_cieu.db` — CIEU audit database (SQLite)
- `scripts/hook_wrapper.py` — **the actual enforcement entry point** (thin shell calling Y-star-gov's check_hook)
- `scripts/governance_boot.sh` — session boot orchestrator
- `scripts/dispatch_board.py` — whiteboard task system
- `scripts/per_rule_detectors.py` — custom rule detectors imported by Y-star-gov

### 1.2 Y-star-gov (Product)

**Role**: Runtime governance framework. The "product" that the company builds and sells.

**Scale**:
- `ystar/kernel/` — contract compiler, engine, check()
- `ystar/adapters/` — hook.py (1740 lines), boundary_enforcer.py (3070 lines), identity_detector.py, cieu_writer.py
- `ystar/governance/` — CIEU store, omission engine, causal engine, counterfactual engine, router_registry (new), ~30 modules
- `ystar/domains/` — openclaw, finance, crypto, devops, healthcare
- `ystar/path_a/` — meta-agent
- `ystar/path_b/` — external governance loop
- Total: ~100+ Python modules
- Tests: 806+ passing

**Key interfaces**:
- `check()` — core deterministic policy check (0.042ms)
- `enforce()` — full governance path with delegation/drift/CIEU
- `check_hook()` — the hook entry point called by Labs' hook_wrapper.py
- `RouterRegistry` — new Phase 2 skeleton for enforce-as-router

### 1.3 gov-mcp (Distribution Channel)

**Role**: MCP server wrapping Y-star-gov for external consumers. Installable via `pip install gov-mcp`.

**Scale**:
- `gov_mcp/server.py` — MCP server with FastMCP, ~2000 lines
- `gov_mcp/router.py` — deterministic command classifier
- `gov_mcp/dispatch_logic.py` — delegation/obligation logic
- `gov_mcp/plugin_tools.py` — marketplace plugin tools
- `gov_mcp/benchmark.py` — performance benchmarking
- Total: ~10 Python modules

**Key interfaces**:
- `gov_check` — MCP tool that runs check()/enforce()
- `gov_delegate` — delegation chain management
- `gov_doctor` — health diagnostics
- `gov_query_cieu` — audit log query
- `gov_install` — one-command setup for external users

---

## 2. Data Flow Diagram (Current)

```
                    Claude Code Process
                           |
                    PreToolUse hook event
                           |
                           v
              ┌─────────────────────────┐
              │  hook_wrapper.py (Labs)  │  <-- sys.path.insert(Y-star-gov)
              │  - reads .ystar_active_  │
              │    agent for identity    │
              │  - CEO code-write block  │
              │  - CZL-159 pre-output    │
              │  - Agent stack push      │
              │  - CZL Gate 1 dispatch   │
              └──────────┬──────────────┘
                         │
                         v
              ┌─────────────────────────┐
              │  check_hook() (Y*gov)   │  <-- ystar.adapters.hook
              │  - identity detection   │
              │  - session config load  │
              │  - boundary enforcement │
              │  - CIEU writing         │
              │  - enforce() or check() │
              └─────────────────────────┘
                         │
                    ALLOW / DENY
                         │
                         v
              ┌─────────────────────────┐
              │  stdout JSON response   │
              │  → Claude Code reads    │
              └─────────────────────────┘


    SEPARATE PROCESS (optional):

              ┌─────────────────────────┐
              │  gov-mcp server         │  <-- imports ystar directly
              │  localhost:7922 SSE     │
              │  - gov_check MCP tool   │
              │  - gov_delegate         │
              │  - gov_doctor           │
              └─────────────────────────┘
```

---

## 3. Problem Catalog (16 Specific Issues)

### P1. Identity Detection Deadlock (CRITICAL — live-demonstrated this session)

**What**: hook_wrapper.py reads `.ystar_active_agent`, finds "Ethan-CTO", but identity_detector.py's `_AGENT_TYPE_MAP` has no entry for "Ethan-CTO" (only "Agent-CTO", "ystar-cto"). Maps to generic "agent". Governance then blocks all actions because "agent" has no permissions. Cannot fix identity file because fixing requires a write, which is blocked.

**Root cause**: Three independent identity systems with no reconciliation:
1. `.ystar_active_agent` file (Labs) — arbitrary strings
2. `_AGENT_TYPE_MAP` dict (Y-star-gov) — fixed enum
3. Claude Code's `agent_type` payload field — yet another format

**Severity**: P0. Total system lock. CTO session completely unable to execute Bash commands.

### P2. sys.path.insert Pandemic (CRITICAL)

**What**: 90+ occurrences of `sys.path.insert(0, ...)` across both repos. Labs scripts insert Y-star-gov path. Y-star-gov modules insert Labs scripts path. Circular cross-repo imports via runtime path manipulation.

**Root cause**: No proper Python packaging relationship. Labs is not a package. Y-star-gov is a package but Labs references it via hardcoded absolute paths, not `pip install`.

**Severity**: P0. This is the single largest source of fragility. Any path change (user rename, new machine, different Python version) breaks everything. Violates Iron Rule 2 (no hardcoded paths).

### P3. Hook Wrapper Is a God Object (CRITICAL)

**What**: `hook_wrapper.py` in Labs has grown to include:
- Identity override logic (should be in Y-star-gov)
- CEO code-write prohibition (should be a boundary rule)
- CZL-159 pre-output content validation (should be a router rule)
- Agent stack push/pop (should be in Y-star-gov)
- CZL Gate 1 dispatch validation (should be a router rule)
- Direct CIEU writes (duplicates Y-star-gov's cieu_writer)
- Session boot enforcement

This file is simultaneously a thin wrapper AND a fat policy engine. It has absorbed governance logic that belongs in the product.

**Root cause**: Easier to add code to the wrapper than to ship a new Y-star-gov version.

### P4. boundary_enforcer.py Is a 3070-Line Monolith

**What**: Single file containing all boundary enforcement logic. Imports Labs' `per_rule_detectors.py` via sys.path.insert, creating a reverse dependency from product to company.

**Root cause**: Organic growth without module extraction. No clear separation between core enforcement (belongs in kernel) and company-specific rules (belongs in config).

### P5. Duplicate Unreachable Code in hook.py

**What**: `_result_to_response()` in hook.py contains 7+ identical return blocks after the first return statement. All blocks after the first are dead code.

**Root cause**: Copy-paste errors during rapid development. No linting, no dead-code detection in CI.

### P6. gov-mcp Is Orphaned from Labs Workflow

**What**: gov-mcp imports ystar directly (correct). But Labs' hook_wrapper.py does NOT go through gov-mcp. The MCP server sits to the side, running on port 7922 as a parallel path. The AGENTS.md says "agents MUST use gov_check MCP tool" but the actual enforcement path is hook_wrapper.py -> check_hook(). The MCP server and the hook are two completely separate enforcement paths with no shared state.

**Root cause**: gov-mcp was built as an external distribution channel, then repurposed as an internal tool. The dual-use was never architecturally reconciled.

### P7. CIEU Database Fragmentation

**What**: Multiple CIEU databases exist:
- `ystar-company/.ystar_cieu.db` — written by hook_wrapper
- `ystar-company/.ystar_cieu_omission.db` — written by omission engine
- `gov-mcp/cieu.db` — written by gov-mcp server
- In-memory CIEU stores in various test/module contexts

Queries against one database miss events written to another. No cross-database query capability.

**Root cause**: Each entry point (hook, MCP, direct) creates its own CIEUStore. No single audit trail.

### P8. Configuration Hierarchy Undefined

**What**: At least 5 configuration sources with no defined precedence:
1. `.ystar_session.json` — session config
2. `AGENTS.md` — governance contract (prose, parsed by regex, confidence 0.5-0.7)
3. `CLAUDE.md` — Claude Code system prompt
4. `.claude/settings.json` — Claude Code project settings
5. `~/.claude/settings.json` — Claude Code global settings

When they conflict, behavior is undefined. Session config says one thing, AGENTS.md says another, CLAUDE.md says a third.

**Root cause**: Organic accumulation. No single-source-of-truth architecture.

### P9. Feature Discovery Failure (Board's Core Question)

**What**: 850+ files exist. Agents cannot find them. Features that exist are not features that work. The opt-in model (agent must remember and call the right script) fundamentally fails because:
- Context windows compress and lose detail
- New sessions inherit memory index, not wiring
- Sub-agents get task prompts, not ecosystem maps
- Drift causes agents to forget features first

**Root cause**: Architecture assumes omniscient agents. Agents are amnesiac by nature. This is the #1 reason Board asked for this review.

### P10. Lock-Death Patterns (10 Known)

**What**: Governance enforcement creates circular deadlocks. Examples:
- Identity file corrupt -> cannot write to fix identity -> all actions blocked
- Session not booted -> boot script blocked by hook -> cannot boot
- Agent type unknown -> all Bash blocked -> cannot run git/pytest to diagnose

**Root cause**: Fail-closed enforcement with no break-glass that actually works at the hook level.

### P11. Test Isolation Failure

**What**: Y-star-gov has 806 tests. Labs has scattered test scripts. gov-mcp has its own test suite. No cross-repo integration tests exist. A change in Y-star-gov's identity_detector breaks Labs' hook_wrapper, but no test catches this until runtime.

**Root cause**: Three repos with independent CI. No integration test harness.

### P12. Version Coupling Without Semver

**What**: Labs uses `sys.path.insert(0, "/Users/haotianliu/.openclaw/workspace/Y-star-gov")` to access Y-star-gov. This means Labs always uses HEAD of the Y-star-gov repo, whatever state it's in. No version pinning. A broken commit in Y-star-gov instantly breaks all Labs governance.

**Root cause**: Development convenience prioritized over release engineering.

### P13. Naming Collision and Concept Overlap

**What**: Multiple overlapping concepts with different names:
- `check()` vs `enforce()` vs `check_hook()` — three governance entry points
- `CIEU` vs `K9` vs `ForgetGuard` — three monitoring/audit systems
- `RouterRegistry` vs `router.py` (gov-mcp) — two "routers" in different repos
- `DelegationChain` vs `agent_stack` — two delegation tracking systems
- `OmissionEngine` vs `check_obligations.py` — two obligation systems
- `intervention` vs `omission` vs `causal` vs `counterfactual` — overlapping governance concepts with unclear boundaries

**Root cause**: Features built by different agents at different times without architectural reconciliation.

### P14. Hardcoded Path Violations (Iron Rule 2 Breach)

**What**: Despite Iron Rule 2 explicitly prohibiting hardcoded paths, the codebase contains:
- `"/Users/haotianliu/.openclaw/workspace/Y-star-gov"` hardcoded in ~20 files
- `"/Users/haotianliu/.openclaw/workspace/ystar-company"` hardcoded in ~10 files
- `192.168.1.228:7922` in AGENTS.md (legacy, may be stale)
- Hardcoded marker file path in hook_wrapper.py

**Root cause**: sys.path.insert pattern requires absolute paths. The path hack IS the Iron Rule 2 violation.

### P15. Reverse Dependency: Product Imports Company

**What**: Y-star-gov's boundary_enforcer.py does `sys.path.insert(0, ystar-company/scripts)` and imports `per_rule_detectors`. Y-star-gov's `k9_routing_subscriber.py` imports from company scripts. The product depends on the company. This means the product cannot be installed by any external user without also cloning ystar-company.

**Root cause**: Company-specific enforcement rules were pushed down into the product instead of being injected via configuration.

### P16. Agent Scope Boundaries Are Prose, Not Code

**What**: AGENTS.md defines agent permissions in natural language ("CTO can access ./src/, ./tests/"). These are then hand-translated into identity_detector maps and boundary_enforcer logic. The translation is incomplete, inconsistent, and drifts as AGENTS.md is amended.

**Root cause**: No contract compiler that reads AGENTS.md and emits machine-checkable permission sets. The "nl_to_contract" module exists in gov-mcp but is not used by the hook path.

---

## 4. Scale Summary

| Dimension | Count | Assessment |
|-----------|-------|------------|
| Labs Python scripts | ~110 | 70%+ are workflow, should be in enforce |
| Labs shell scripts | ~28 | Mixed; most are orchestrators |
| Labs governance docs | ~40 | 90%+ are protocols, should be enforce rules |
| Labs knowledge files | ~600+ | Mostly reference (KEEP), some are routing-adjacent |
| Y-star-gov Python modules | ~100+ | Core product, needs cleanup |
| Y-star-gov tests | 806+ | Strong, but isolated |
| gov-mcp Python modules | ~10 | Clean, but orphaned |
| sys.path.insert calls | 90+ | P0 violation of Iron Rule 2 |
| CIEU databases | 3+ | Fragmented audit trail |
| Config sources | 5+ | No defined precedence |
| Identity formats | 3+ | No reconciliation |

---

*End of survey. Master architecture proposal follows in ecosystem_architecture_master_20260418.md.*
