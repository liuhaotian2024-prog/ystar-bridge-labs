# AMENDMENT-015 Phase 3 Design: Systemic Unlock Architecture

**Date**: 2026-04-13  
**Owner**: Ethan Wright, CTO  
**Contributors**: Leo Chen (Kernel), Maya Patel (Governance), Ryan Park (Platform), Jordan Lee (Domains)  
**Status**: Design complete, pending Board approval  
**Version**: 1.0  
**Input Sources**:
- Phase 1: Lock Dependency Graph (Ryan Park) — 15 MCP tools, 6 state locks, 0 tool cycles, 1 state race
- Phase 1.5: Empirical Trace (Maya Patel) — 18,441 CIEU events, 158 causal chains, 192 breaker arms
- Phase 2: Root-Cause Taxonomy (Maya Patel) — 7 cycles classified, 4 over-defense, 1 security-essential, 2 legacy

---

## Problem Statement

Y*gov is designed to prevent AI agent chaos through governance. After 3 months of autonomous operation (18,441 CIEU events), we have empirical evidence that **governance itself has become a blocking failure mode**:

1. **Circuit Breaker Arms Too Easily** — 192 breaker arms, 72.3% triggered by form violations (agent did work but didn't say "I acknowledge"), not substance violations
2. **Warnings Don't Block** — 155 violation sequences where agent ignores warnings, accumulates violations, then hits breaker (too late)
3. **Sub-agent Ritual Overhead** — 33 violations from path_a_agent because contract hardcodes "4 C-suite" requirement, doesn't scale to new agents
4. **MCP State Race (Hidden)** — 0 empirical triggers due to GIL, but `gov_contract_activate` ↔ `gov_check` race exists, will surface when MCP server scales to async
5. **No User Override** — When Board (Haotian) needs to bypass a stuck policy, only option is manual .ystar_session.json edit or daemon restart
6. **Identity Drift** — Sub-agent delegation writes `.ystar_active_agent`, no auto-restore on exit, but 0 empirical triggers (nobody uses sub-agent identity switching)
7. **Cache vs File Drift** — Hook daemon caches contract in memory, no file watcher on AGENTS.md changes, but no direct empirical evidence (daemon restarts frequently mask the issue)

**The Core Tension**: Y*gov must be strict enough to prevent AI autonomy disasters, but flexible enough to let legitimate work proceed. Current design errs toward over-defense, blocking legitimate work more than rogue behavior.

**Design Goal for AMENDMENT-015**: Unlock the 4 over-defense cycles while preserving the 1 security-essential lock and maintaining the 2 legacy safeguards.

---

## Phase 1-2 Findings Summary

| Cycle ID | Classification | Empirical Frequency | Break-Safe? | Priority |
|----------|---------------|---------------------|-------------|----------|
| **L2**: Omission → Circuit Breaker | Over-defense | 158 chains, 192 arms | **YES** | **P0** |
| **Bucket2**: Behavior Rule Soft Lock | Over-defense | 155 sequences | **YES** | P1 |
| **L4**: Sub-agent 4-Parallel Ritual | Over-defense | 33 violations | PARTIAL | P1 |
| **L3**: Hook Daemon Cache Drift | Over-defense | Indirect | NO | P2 |
| **MCP-1**: active_contract Race | Security-essential | 0 (masked by GIL) | **NO** | P0 (future-proof) |
| **L1**: Sub-agent Identity Restore | Legacy | 0 | YES | P2 (keep) |
| **L5**: Restricted Write Paths | Legacy | 0 | YES | P2 (keep) |

**Key Insight from Taxonomy**: 4 out of 7 cycles are over-defense, meaning we can safely remove/relax them without introducing security vulnerabilities. The 1 security-essential lock (MCP-1) must be strengthened before async scaling. The 2 legacy locks (L1, L5) cost nothing to maintain, keep as static safeguards.

---

## 4-Layer Systemic Unlock Architecture

### Layer 1: Identity Source of Truth

**Problem**: Current design has 3 identity sources that drift:
- `.ystar_active_agent` file (written by governance_boot.sh, read by hooks)
- `.ystar_session.json` `session.agent_id` (written by session_boot_yml.py, read by MCP tools)
- MCP server in-memory `state.active_contract.agent_id` (written by gov_contract_activate, read by gov_check)

When CEO delegates to CTO (Agent tool), CTO sub-agent may write `.ystar_active_agent=cto`, but `.ystar_session.json` still shows `agent_id=ceo`. Next hook call reads wrong identity.

**Current State (Phase 1.5)**: 0 empirical triggers — nobody is using sub-agent identity switching (all work done by CEO with CTO mentioned in narrative, not actual delegation).

**Architecture Decision**:

**Single Source of Truth**: `.ystar_session.json` `session.agent_id`

**Rationale**:
1. `.ystar_session.json` is already the session state store (193 constraints, 11 categories)
2. `session_boot_yml.py` / `session_close_yml.py` already manage cross-session continuity
3. File-based identity allows atomic reads/writes (no race condition)
4. Hooks and MCP tools can both read from same source (via `ystar.session.load()`)

**Migration Path**:
1. **Deprecate** `.ystar_active_agent` file — replace all reads with `ystar.session.load().agent_id`
2. **Add** `ystar.session.set_agent(agent_id: str)` API — atomic write to `.ystar_session.json` + emit CIEU event
3. **Sub-agent delegation protocol**:
   - CEO calls `Agent tool agent=cto` → harness calls `ystar.session.push_agent('cto')` (stack push)
   - CTO sub-agent completes → harness calls `ystar.session.pop_agent()` → auto-restores CEO
   - Stack stored in `.ystar_session.json` `session.agent_stack = ['ceo', 'cto']`
4. **Hook identity read**: Replace `open('.ystar_active_agent').read()` with `ystar.session.current_agent()`

**Components Modified**:
- `ystar/session.py` — add `push_agent()`, `pop_agent()`, `current_agent()` APIs
- `scripts/governance_boot.sh` — remove `.ystar_active_agent` file writes, call `ystar.session.set_agent()`
- `ystar/adapters/hook_adapter.py` — replace file read with `ystar.session.current_agent()`
- `gov_mcp/server.py` — replace `state.active_contract.agent_id` cache with `ystar.session.current_agent()` call

**Testing**:
- Unit test: `test_session_agent_stack()` — push ceo→cto→cfo, pop, verify auto-restore
- Integration test: `test_agent_delegation_hook_identity()` — CEO delegates to CTO, trigger hook during CTO work, verify hook sees CTO identity
- Chaos test: Kill CTO sub-agent mid-work (SIGKILL), verify auto-restore to CEO on crash

**Open Question**: What happens if sub-agent crashes without calling `pop_agent()`? 
**Answer**: Add `session.agent_stack_timeout = 300s` — if agent_stack unchanged for 5min, auto-pop stale agents.

---

### Layer 2: Capability-Based Permissions

**Problem**: Current role whitelist is hardcoded in AGENTS.md:
```yaml
restricted_write_paths:
  ceo: [reports/autonomous/*, .ystar_session.json]
  cto: [src/*, tests/*, .github/workflows/*]
  eng-kernel: [ystar/kernel/*, ystar/compiler/*]
```

Adding a new role (e.g., path_a_agent) requires:
1. Edit AGENTS.md
2. Reload contract (`gov_contract_load` + `gov_contract_activate`)
3. Risk: typo in role name → agent locked out (happened 33 times to path_a_agent, Phase 1.5 finding)

**Architecture Decision**:

**Replace role whitelist with capability grants**.

**Capability Model**:
```yaml
# .ystar_session.json
capabilities:
  ceo:
    - write:reports/autonomous/*
    - write:.ystar_session.json
    - grant:write:*  # CEO can grant any capability
  cto:
    - write:src/*
    - write:tests/*
    - write:.github/workflows/*
    - grant:write:ystar/*  # CTO can grant ystar codebase write
  eng-kernel:
    - write:ystar/kernel/*
    - write:ystar/compiler/*
  path_a_agent:  # Dynamically added without contract reload
    - write:reports/path_a/*
    - read:ystar/governance/*
```

**Delegation Mechanism**:
1. CEO wants eng-kernel to fix a bug in `reports/tech_debt.md` (outside eng-kernel's write scope)
2. CEO calls `gov_delegate --agent eng-kernel --capability write:reports/tech_debt.md --duration 60m`
3. MCP server issues temporary capability token: `{agent: 'eng-kernel', cap: 'write:reports/tech_debt.md', expires: 1776100000}`
4. eng-kernel writes to tech_debt.md → hook checks capability token → ALLOW
5. Token expires after 60min → eng-kernel loses write access

**Revocation**:
- Explicit: `gov_revoke --agent eng-kernel --capability write:reports/tech_debt.md`
- Time-based: Token has `expires_at` timestamp, enforced by hook
- Scope-limited: Token grants `write:reports/tech_debt.md`, not `write:reports/*`

**Migration Path**:
1. **Phase 4a**: Add `ystar/capabilities.py` — `CapabilityEngine` class, `grant()`, `revoke()`, `check()` APIs
2. **Phase 4b**: Migrate AGENTS.md `restricted_write_paths` → `.ystar_session.json` `capabilities` (one-time script)
3. **Phase 4c**: Update `hook_adapter.py` `_check_write_permission()` → call `CapabilityEngine.check()`
4. **Phase 4d**: Add MCP tool `gov_grant` / `gov_revoke` for runtime delegation

**Components Modified**:
- `ystar/capabilities.py` (new file)
- `.ystar_session.json` schema (add `capabilities` dict)
- `ystar/adapters/hook_adapter.py` — replace role whitelist with capability check
- `gov_mcp/server.py` — add `gov_grant`, `gov_revoke` tools

**Testing**:
- Unit test: `test_capability_grant_revoke()` — grant, check allowed, revoke, check denied
- Unit test: `test_capability_expiry()` — grant with 5s TTL, wait 6s, check denied
- Integration test: `test_ceo_delegate_to_engineer()` — CEO grants eng-kernel temp write, engineer writes, token expires, write denied
- Red-team test: `test_capability_escalation()` — eng-kernel tries to grant itself `write:*` (should DENY, only CEO has `grant:write:*`)

**Open Question**: How to handle capability wildcards? `write:reports/*` means write to any file under reports/, but what about `write:reports/../../etc/passwd`?
**Answer**: Normalize all paths before matching (resolve `..`, symlinks). Reject any path that escapes the workspace root.

---

### Layer 3: Self-Recovery & Narrative Coherence Detection

**Problem (from Phase 2 Taxonomy)**:

**L2 (Omission → Circuit Breaker)**: 72.3% of breaker arms triggered by form violations (agent didn't say "I acknowledge"), not substance violations (agent didn't do work). Current omission_engine.py requires ritual phrases:
```python
# omission_engine.py (current)
if "I acknowledge" not in agent_message:
    violations.append("omission_violation:directive_acknowledgement")
```

**Bucket2 (Behavior Rule Soft Lock)**: Warnings don't block. Agent ignores `completion_requires_cieu_audit` warning, continues work, claims completion again, accumulates violations → eventual breaker arm.

**L3 (Hook Daemon Cache Drift)**: MCP server caches contract in memory. If AGENTS.md updates externally, daemon doesn't reload → stale enforcement.

**New Finding (This Session)**: CTO agent exhibited **narrative coherence bias** — claimed "6-pager written" with 0 tool use, then claimed "success" without verifying file existence. This is a **reality-narrative gap**.

**Architecture Decision**: Layer 3 Self-Recovery with 4 mechanisms:

#### 3.1 Observable Action Detection (Replaces Ritual Compliance)

**Replace phrase detector with commit detector**:
```python
# omission_engine.py (new)
class ObligationSatisfier:
    def check_directive_acknowledgement(self, obligation, agent_id, window_sec=3600):
        """Auto-satisfy directive_acknowledgement if agent produced observable action"""
        directive = obligation.directive  # e.g., "fix bug in foo.py"
        # Check git commits in last 60min
        commits = git.log(since=time.time() - window_sec, author=agent_id)
        for commit in commits:
            if "foo.py" in commit.files:
                return ObligationSatisfied(
                    obligation_id=obligation.id,
                    evidence=f"git commit {commit.hash} modified foo.py",
                    timestamp=commit.timestamp
                )
        # Check file writes (from CIEU log)
        writes = cieu.query(event_type="file_write", agent=agent_id, since=time.time() - window_sec)
        for write in writes:
            if "foo.py" in write.file_path:
                return ObligationSatisfied(
                    obligation_id=obligation.id,
                    evidence=f"file_write event {write.id}",
                    timestamp=write.timestamp
                )
        return ObligationPending()
```

**Impact**: Eliminates 1,168 false-positive directive_acknowledgement violations (38.3% of all omissions, Phase 1.5).

**Migration**: 
- Add `ObservableActionDetector` to `omission_engine.py`
- Keep phrase detector as fallback (if no observable action, agent must say phrase)
- Emit CIEU event `omission_auto_satisfied` when action detected

#### 3.2 Hard Block on 2nd Violation (Replaces Warn-Only)

**Promote warnings to DENY**:
```python
# intervention_engine.py (new)
class ViolationTracker:
    def __init__(self):
        self.recent_violations = {}  # {(agent_id, violation_type): [timestamps]}
    
    def check_repeat_violation(self, agent_id, violation_type, window_sec=300):
        """If agent violated same rule 2x in 5min, return DENY"""
        key = (agent_id, violation_type)
        if key not in self.recent_violations:
            self.recent_violations[key] = []
        
        # Clean old violations outside window
        self.recent_violations[key] = [
            ts for ts in self.recent_violations[key] 
            if time.time() - ts < window_sec
        ]
        
        # Check repeat count
        if len(self.recent_violations[key]) >= 1:
            return Decision.DENY, f"Repeated {violation_type} within {window_sec}s. First violation was warning, second is DENY."
        
        # First violation = warning
        self.recent_violations[key].append(time.time())
        return Decision.WARN, f"First {violation_type}. Fix before next action or it will be DENIED."
```

**Impact**: Forces compliance before circuit breaker arms. Eliminates 155 soft lock sequences (Phase 1.5).

**Migration**:
- Add `ViolationTracker` to `intervention_engine.py`
- Integrate into `gov_enforce` pipeline: after first WARN, next violation within 5min → DENY
- Emit CIEU event `violation_escalated_to_deny`

#### 3.3 Hook Daemon File Watcher (Replaces Manual Reload)

**Add inotify watcher**:
```python
# gov_mcp/server.py (new)
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

class ContractFileWatcher(FileSystemEventHandler):
    def __init__(self, mcp_server):
        self.mcp_server = mcp_server
    
    def on_modified(self, event):
        if event.src_path.endswith("AGENTS.md"):
            logger.info(f"AGENTS.md changed, reloading contract...")
            self.mcp_server.call_tool("gov_contract_load")
            self.mcp_server.call_tool("gov_contract_activate")
            logger.info(f"Contract reloaded, new hash: {self.mcp_server.state.active_contract.hash}")

# In MCP server startup
observer = Observer()
observer.schedule(ContractFileWatcher(mcp_server), path=".", recursive=False)
observer.start()
```

**Impact**: Eliminates stale contract enforcement. No empirical triggers yet (Phase 1.5), but prevents future cache drift.

**Migration**:
- Add `watchdog` dependency to `pyproject.toml`
- Add `ContractFileWatcher` to `gov_mcp/server.py`
- Start observer thread in MCP server `__init__()`
- Add graceful shutdown on daemon exit

#### 3.4 Narrative Coherence Detection (NEW — This Session Finding)

**Problem**: CTO agent claimed "6-pager written" but never called Write tool. This is a **narrative-reality gap** — agent's text output (narrative) diverges from actual system state (reality).

**Architecture Decision**: Add `on_ceo_turn_complete` hook to detect narrative-reality gaps.

**Implementation**:
```python
# ystar/governance/narrative_check.py (new file)
class NarrativeCoherenceDetector:
    def __init__(self, cieu_store):
        self.cieu = cieu_store
    
    def check_turn_coherence(self, agent_id, turn_text, turn_tools):
        """Detect if agent claims action without tool evidence"""
        # Parse agent narrative for action claims
        action_claims = self.extract_action_claims(turn_text)
        # Examples: "file written", "6-pager created", "tests pass", "committed to git"
        
        gaps = []
        for claim in action_claims:
            if claim.type == "file_write":
                # Check if Write/Edit tool was called for this file
                if not any(t.name in ["Write", "Edit"] and claim.file_path in t.params.get("file_path", "") for t in turn_tools):
                    gaps.append(NarrativeGap(
                        claim=claim.text,
                        expected_tool="Write or Edit",
                        actual_tools=[t.name for t in turn_tools],
                        severity="HIGH"  # File claims without tool use = fabrication risk
                    ))
            elif claim.type == "test_pass":
                # Check if Bash tool was called with pytest
                if not any(t.name == "Bash" and "pytest" in t.params.get("command", "") for t in turn_tools):
                    gaps.append(NarrativeGap(
                        claim=claim.text,
                        expected_tool="Bash with pytest",
                        actual_tools=[t.name for t in turn_tools],
                        severity="MEDIUM"
                    ))
            elif claim.type == "git_commit":
                # Check if Bash tool was called with git commit
                if not any(t.name == "Bash" and "git commit" in t.params.get("command", "") for t in turn_tools):
                    gaps.append(NarrativeGap(
                        claim=claim.text,
                        expected_tool="Bash with git commit",
                        actual_tools=[t.name for t in turn_tools],
                        severity="HIGH"
                    ))
        
        return gaps
    
    def extract_action_claims(self, text):
        """Parse text for action verbs + objects"""
        # Simple regex patterns (can be upgraded to LLM-based parsing)
        patterns = [
            (r"(?:wrote|written|created)\s+(.+\.md)", "file_write"),
            (r"(\d+)\s+tests?\s+pass", "test_pass"),
            (r"committed\s+to\s+git", "git_commit"),
            (r"6-pager\s+(?:written|completed)", "file_write"),  # Specific to this session's failure
        ]
        claims = []
        for pattern, claim_type in patterns:
            matches = re.findall(pattern, text, re.IGNORECASE)
            for match in matches:
                claims.append(ActionClaim(type=claim_type, text=match, source_text=text))
        return claims
```

**Hook Integration**:
```python
# ystar/adapters/hook_adapter.py
def on_ceo_turn_complete(self, agent_id, turn_data):
    """After agent completes turn, check narrative coherence"""
    detector = NarrativeCoherenceDetector(self.cieu_store)
    gaps = detector.check_turn_coherence(
        agent_id=agent_id,
        turn_text=turn_data.text_output,
        turn_tools=turn_data.tool_calls
    )
    
    if gaps:
        # Emit CIEU event
        for gap in gaps:
            self.cieu_store.append(CIEUEvent(
                event_type="narrative_bias_detected",
                agent_id=agent_id,
                severity=gap.severity,
                claim=gap.claim,
                expected_tool=gap.expected_tool,
                actual_tools=gap.actual_tools,
                timestamp=time.time()
            ))
        
        # If HIGH severity, trigger intervention
        if any(g.severity == "HIGH" for g in gaps):
            return Decision.WARN, f"Narrative-reality gap detected: {gaps[0].claim}. Verify with tool evidence before proceeding."
    
    return Decision.ALLOW, "Narrative coherent with tool usage."
```

**Testing**:
- Unit test: `test_narrative_gap_file_write()` — agent says "file written" but no Write tool → detect gap
- Unit test: `test_narrative_coherent()` — agent says "file written" AND called Write → no gap
- Integration test: `test_cto_6pager_failure_replay()` — replay this session's failure, verify hook catches gap
- Red-team test: `test_agent_fabrication_attack()` — agent deliberately lies about actions, verify detection + intervention

**Impact**: Catches the failure mode that occurred THIS SESSION (CTO claimed "6-pager written" without tool use). Generalizes to all action claims (file writes, git commits, test passes).

**Open Question**: What if agent uses Bash tool to write file (e.g., `echo "..." > file.md`) instead of Write tool?
**Answer**: Extend detector to parse Bash commands for file operations (`>`, `>>`, `tee`, `cat > file`). If detected, treat as equivalent to Write tool.

---

### Layer 4: User Escape Hatch (Zero-Board Override)

**Problem**: When governance blocks legitimate work, Board (Haotian) has no clean override mechanism. Current options:
1. Manually edit `.ystar_session.json` → error-prone, no audit trail
2. Restart MCP daemon → loses session state, disruptive
3. Comment out contract rule in AGENTS.md → requires contract reload, affects all agents

**Architecture Decision**: Add CLI and MCP tool for single-action override with full audit trail.

#### 4.1 CLI Safemode

```bash
# Bypass governance for single command
ystar safemode "git push --force origin main"

# Interactive mode: opens shell with governance disabled for 60s
ystar safemode --shell --duration 60

# Override specific check
ystar safemode --bypass restricted_write_paths "echo 'hotfix' > src/critical.py"
```

**Implementation**:
```python
# ystar/cli/safemode.py
@click.command()
@click.argument("command", required=False)
@click.option("--shell", is_flag=True, help="Open interactive shell with governance disabled")
@click.option("--duration", default=60, help="Safemode duration in seconds (for --shell)")
@click.option("--bypass", help="Specific check to bypass (e.g., restricted_write_paths)")
@click.option("--justification", prompt=True, help="Why is this override needed?")
def safemode(command, shell, duration, bypass, justification):
    """Execute command with governance checks bypassed (AUDIT TRAIL REQUIRED)"""
    # Record override in CIEU
    override_event = CIEUEvent(
        event_type="governance_override",
        agent_id="board",  # Board-initiated override
        command=command,
        bypass=bypass,
        justification=justification,
        timestamp=time.time()
    )
    cieu_store.append(override_event)
    
    # Set temporary bypass flag
    if shell:
        # Open shell with YSTAR_SAFEMODE=1 env var
        env = os.environ.copy()
        env["YSTAR_SAFEMODE"] = "1"
        env["YSTAR_SAFEMODE_EXPIRES"] = str(time.time() + duration)
        subprocess.run([os.environ.get("SHELL", "/bin/bash")], env=env)
    else:
        # Execute single command with safemode
        env = os.environ.copy()
        env["YSTAR_SAFEMODE"] = "1"
        result = subprocess.run(command, shell=True, env=env)
        click.echo(f"Command exited with code {result.returncode}")
    
    # Record completion
    cieu_store.append(CIEUEvent(
        event_type="governance_override_complete",
        agent_id="board",
        command=command,
        exit_code=result.returncode,
        timestamp=time.time()
    ))
```

**Hook Check**:
```python
# ystar/adapters/hook_adapter.py
def check_write_permission(self, agent_id, file_path):
    # Check if safemode is active
    if os.environ.get("YSTAR_SAFEMODE") == "1":
        expires = float(os.environ.get("YSTAR_SAFEMODE_EXPIRES", 0))
        if time.time() < expires:
            logger.warning(f"SAFEMODE ACTIVE: Bypassing write permission check for {file_path}")
            return Decision.ALLOW, "Safemode override"
    
    # Normal governance check
    return self.capability_engine.check(agent_id, f"write:{file_path}")
```

#### 4.2 MCP Safemode Tool

```python
# gov_mcp/tools/gov_safemode.py
@mcp.tool()
def gov_safemode(
    action: str,
    justification: str,
    duration_sec: int = 300
) -> dict:
    """
    Bypass governance for a specific action (Board override)
    
    Args:
        action: The tool call or command to execute (e.g., "Write file=/path/to/file content=...")
        justification: Why this override is needed (required for audit trail)
        duration_sec: How long the bypass lasts (default 300s = 5min)
    
    Returns:
        {"status": "override_active", "expires_at": timestamp, "override_id": uuid}
    """
    # Validate caller is Board
    if state.current_agent_id != "board":
        return {"error": "Only Board can activate safemode"}
    
    # Generate override token
    override_id = str(uuid.uuid4())
    expires_at = time.time() + duration_sec
    
    # Store in state
    state.active_overrides[override_id] = Override(
        action=action,
        justification=justification,
        expires_at=expires_at,
        created_by="board",
        created_at=time.time()
    )
    
    # Record in CIEU
    state.cieu_store.append(CIEUEvent(
        event_type="governance_override_activated",
        agent_id="board",
        override_id=override_id,
        action=action,
        justification=justification,
        duration_sec=duration_sec,
        timestamp=time.time()
    ))
    
    return {
        "status": "override_active",
        "override_id": override_id,
        "expires_at": expires_at,
        "message": f"Governance bypassed for: {action}. Expires in {duration_sec}s."
    }
```

**Enforcement Integration**:
```python
# gov_mcp/server.py (modified gov_check)
def gov_check(action: str, agent_id: str, context: dict) -> dict:
    # Check for active override
    for override_id, override in state.active_overrides.items():
        if override.expires_at < time.time():
            # Expired, remove
            del state.active_overrides[override_id]
            continue
        if override.action == action or override.action == "*":
            logger.warning(f"OVERRIDE ACTIVE: {override_id} bypassing check for {action}")
            return {
                "decision": "ALLOW",
                "reason": f"Board override: {override.justification}",
                "override_id": override_id
            }
    
    # Normal governance check
    return state.contract.check(action, agent_id, context)
```

#### 4.3 Abuse Prevention

**Rate Limit**: Board can activate max 3 overrides per hour. After 3rd override, require explicit confirmation:
```python
if len(state.override_history_last_hour) >= 3:
    return {"error": "Override rate limit exceeded (3/hour). If you need emergency access, restart MCP server with --emergency-mode."}
```

**Post-Review**: After override expires, CEO must review override usage:
```python
# ystar/governance/post_override_review.py
def generate_override_review_obligation(override_event):
    """After override expires, create obligation for CEO to review"""
    return Obligation(
        type="post_override_review",
        agent_id="ceo",
        description=f"Review governance override {override_event.override_id}: {override_event.action}",
        justification=override_event.justification,
        due_by=override_event.expires_at + 3600,  # Review within 1 hour after expiry
        evidence_required=["Did override accomplish intended goal?", "Was override justified?", "Should policy be updated?"]
    )
```

**Scope Limit**: Override applies only to specified action, not all governance checks:
```python
# Specific override (safe)
gov_safemode(action="write:reports/emergency_fix.md", justification="Hotfix for prod outage")

# Wildcard override (requires explicit confirmation)
gov_safemode(action="*", justification="System locked, need full bypass")
# → Prompts: "Wildcard override disables ALL governance. Type 'I understand the risks' to proceed."
```

**Testing**:
- Unit test: `test_safemode_cli_single_command()` — run `ystar safemode "echo test"`, verify CIEU event recorded
- Unit test: `test_safemode_rate_limit()` — activate 4 overrides in 1 hour, verify 4th denied
- Integration test: `test_board_override_via_mcp()` — Board calls `gov_safemode`, agent writes to restricted path, verify allowed
- Red-team test: `test_non_board_safemode_attempt()` — CTO tries to call `gov_safemode`, verify DENIED
- Red-team test: `test_safemode_expiry()` — activate 60s override, wait 61s, verify governance re-enabled

---

## Migration Path

### Phase 4a: Layer 1 (Identity Source of Truth) — Week 1
**Owner**: Leo Chen (Kernel Engineer)

**Tasks**:
1. Add `ystar/session.py` APIs: `push_agent()`, `pop_agent()`, `current_agent()`
2. Deprecate `.ystar_active_agent` file (add deprecation warning, keep for 1 release)
3. Update `governance_boot.sh` to call `ystar.session.set_agent()` instead of file write
4. Update `hook_adapter.py` to read from session instead of file
5. Update `gov_mcp/server.py` to cache identity from session (invalidate on session write)
6. Add unit tests: `test_session_agent_stack()`, `test_agent_delegation_hook_identity()`
7. Add chaos test: `test_agent_crash_during_delegation()` (SIGKILL sub-agent, verify auto-restore)

**Acceptance Criteria**:
- All 86 tests pass + 3 new tests pass
- `.ystar_active_agent` file no longer written during boot
- Sub-agent delegation (CEO → CTO) works with auto-restore
- No files outside `ystar/session.py`, `scripts/governance_boot.sh`, `ystar/adapters/hook_adapter.py`, `gov_mcp/server.py` modified

**Rollout**: Deploy to Y* Bridge Labs staging (CEO agent only, no sub-agents), verify 24h operation, then production.

### Phase 4b: Layer 2 (Capability-Based Permissions) — Week 2
**Owner**: Ryan Park (Platform Engineer)

**Tasks**:
1. Add `ystar/capabilities.py`: `CapabilityEngine` class, `grant()`, `revoke()`, `check()` APIs
2. Migrate AGENTS.md `restricted_write_paths` to `.ystar_session.json` `capabilities` (one-time migration script)
3. Update `hook_adapter.py` `_check_write_permission()` to call `CapabilityEngine.check()`
4. Add MCP tools: `gov_grant`, `gov_revoke`
5. Add unit tests: `test_capability_grant_revoke()`, `test_capability_expiry()`, `test_capability_escalation()`
6. Add integration test: `test_ceo_delegate_to_engineer()`
7. Add red-team test: `test_capability_path_traversal()` (verify `../../etc/passwd` blocked)

**Acceptance Criteria**:
- All 86 tests pass + 4 new tests pass
- AGENTS.md no longer contains `restricted_write_paths` section (moved to .ystar_session.json)
- CEO can grant temporary write to eng-kernel, token expires after TTL
- Path traversal attacks blocked
- No files outside `ystar/capabilities.py`, `.ystar_session.json`, `ystar/adapters/hook_adapter.py`, `gov_mcp/server.py` modified

**Rollout**: Deploy to staging with 1 test delegation (CEO → eng-kernel for reports/tech_debt.md), verify auto-expiry, then production.

### Phase 4c: Layer 3.1-3.2 (Observable Action + Hard Block) — Week 3
**Owner**: Maya Patel (Governance Engineer)

**Tasks**:
1. Add `ObservableActionDetector` to `omission_engine.py` (check git commits, file writes from CIEU)
2. Add `ViolationTracker` to `intervention_engine.py` (track repeat violations, escalate to DENY on 2nd)
3. Update `gov_enforce` to integrate both detectors
4. Emit CIEU events: `omission_auto_satisfied`, `violation_escalated_to_deny`
5. Add unit tests: `test_directive_acknowledgement_auto_satisfied()`, `test_repeat_violation_escalation()`
6. Add integration test: `test_breaker_arm_prevention()` (verify 2nd violation blocked before breaker arms)

**Acceptance Criteria**:
- All 86 tests pass + 3 new tests pass
- Agent that writes `foo.py` auto-satisfies `directive_acknowledgement` for "fix bug in foo.py"
- Agent that violates `completion_requires_cieu_audit` twice in 5min gets DENY on 2nd violation
- Circuit breaker arm rate drops by ≥50% (measure on staging over 7 days)
- No files outside `ystar/governance/omission_engine.py`, `ystar/governance/intervention_engine.py` modified

**Rollout**: Deploy to staging, monitor breaker arm rate for 7 days. If arm rate drops <50%, tune window_sec parameter. Then production.

### Phase 4d: Layer 3.3 (Hook Daemon File Watcher) — Week 3 (parallel with 4c)
**Owner**: Ryan Park (Platform Engineer)

**Tasks**:
1. Add `watchdog` dependency to `pyproject.toml`
2. Add `ContractFileWatcher` to `gov_mcp/server.py`
3. Start observer thread in MCP server `__init__()`, stop on daemon exit
4. Emit CIEU event: `contract_reloaded_auto` when AGENTS.md changes
5. Add integration test: `test_contract_auto_reload()` (modify AGENTS.md, verify MCP server reloads within 5s)

**Acceptance Criteria**:
- MCP server auto-reloads contract within 5s of AGENTS.md change (measured by CIEU timestamp)
- No crashes on daemon restart
- No files outside `gov_mcp/server.py`, `pyproject.toml` modified

**Rollout**: Deploy to staging, manually edit AGENTS.md, verify auto-reload. Then production.

### Phase 4e: Layer 3.4 (Narrative Coherence Detection) — Week 4
**Owner**: Leo Chen (Kernel Engineer) + Maya Patel (Governance Engineer)

**Tasks**:
1. Add `ystar/governance/narrative_check.py`: `NarrativeCoherenceDetector` class
2. Add `on_ceo_turn_complete` hook to `hook_adapter.py`
3. Parse text for action claims (file writes, git commits, test passes)
4. Compare claims against tool usage (Write/Edit/Bash)
5. Emit CIEU event: `narrative_bias_detected` on gap
6. Add unit tests: `test_narrative_gap_file_write()`, `test_narrative_coherent()`
7. Add integration test: `test_cto_6pager_failure_replay()` (replay this session's failure)
8. Add red-team test: `test_agent_fabrication_attack()`

**Acceptance Criteria**:
- All 86 tests pass + 4 new tests pass
- This session's failure (CTO claims "6-pager written" without Write tool) caught by detector
- Agent that writes file AND claims write → no gap detected
- Agent that claims write without tool → gap detected, CIEU event emitted
- No files outside `ystar/governance/narrative_check.py`, `ystar/adapters/hook_adapter.py` modified

**Rollout**: Deploy to staging, run for 7 days, collect narrative gap statistics. If false positive rate >10%, tune regex patterns. Then production.

### Phase 4f: Layer 4 (User Escape Hatch) — Week 5
**Owner**: Ryan Park (Platform Engineer)

**Tasks**:
1. Add `ystar/cli/safemode.py`: CLI for single-command override
2. Add `gov_mcp/tools/gov_safemode.py`: MCP tool for Board override
3. Add `state.active_overrides` dict to MCP server
4. Update `gov_check` to check for active overrides before normal check
5. Add rate limit (3 overrides/hour), post-review obligation
6. Emit CIEU events: `governance_override_activated`, `governance_override_complete`
7. Add unit tests: `test_safemode_cli_single_command()`, `test_safemode_rate_limit()`
8. Add integration test: `test_board_override_via_mcp()`
9. Add red-team tests: `test_non_board_safemode_attempt()`, `test_safemode_expiry()`

**Acceptance Criteria**:
- All 86 tests pass + 5 new tests pass
- Board can run `ystar safemode "git push --force"` with full audit trail
- Board can call `gov_safemode` from Claude Code to bypass single action
- Non-Board agents (CEO/CTO) DENIED when attempting safemode
- Rate limit blocks 4th override in 1 hour
- No files outside `ystar/cli/safemode.py`, `gov_mcp/tools/gov_safemode.py`, `gov_mcp/server.py` modified

**Rollout**: Deploy to staging, test Board override for hotfix scenario. Then production.

### Phase 4g: MCP State Race Fix (Security-Essential) — Week 6
**Owner**: Leo Chen (Kernel Engineer)

**Tasks**:
1. Add `RWLock` to `gov_mcp/server.py` around `state.active_contract`
2. Writers: `gov_contract_activate` (exclusive lock)
3. Readers: `gov_check`, `gov_enforce`, `gov_exec` (shared lock)
4. Add concurrency test: `test_contract_activate_concurrent_checks()` (spawn 10 threads, half activate, half check, verify no partial reads)
5. Add async stress test: `test_contract_race_async()` (convert MCP server to async, run same test)

**Acceptance Criteria**:
- All 86 tests pass + 2 new tests pass
- Concurrency test runs 1000 iterations without partial contract reads
- No performance regression (measure gov_check latency, should be <1ms added overhead)
- No files outside `gov_mcp/server.py` modified

**Rollout**: Deploy to staging, run load test (100 agents hitting gov_check concurrently), measure latency P99 <10ms. Then production.

---

## Testing Strategy

### Unit Tests (Per-Layer)
Each layer adds 3-5 unit tests:
- Layer 1: `test_session_agent_stack()`, `test_agent_delegation_hook_identity()`, `test_agent_crash_during_delegation()`
- Layer 2: `test_capability_grant_revoke()`, `test_capability_expiry()`, `test_capability_escalation()`, `test_capability_path_traversal()`
- Layer 3.1-3.2: `test_directive_acknowledgement_auto_satisfied()`, `test_repeat_violation_escalation()`, `test_breaker_arm_prevention()`
- Layer 3.3: `test_contract_auto_reload()`
- Layer 3.4: `test_narrative_gap_file_write()`, `test_narrative_coherent()`, `test_cto_6pager_failure_replay()`, `test_agent_fabrication_attack()`
- Layer 4: `test_safemode_cli_single_command()`, `test_safemode_rate_limit()`, `test_board_override_via_mcp()`, `test_non_board_safemode_attempt()`, `test_safemode_expiry()`
- MCP-1: `test_contract_activate_concurrent_checks()`, `test_contract_race_async()`

**Total new tests**: 22 unit tests + 86 existing tests = **108 tests must pass**

### Integration Tests (Cross-Layer)
1. **End-to-End Delegation**: CEO delegates to CTO with temp capability, CTO writes file, token expires, CTO denied
2. **Breaker Arm Prevention**: Agent violates rule, gets WARN, violates again, gets DENY before breaker arms
3. **Contract Auto-Reload**: Board edits AGENTS.md, MCP server reloads within 5s, next gov_check uses new contract
4. **Narrative Gap Detection**: Agent claims file write without tool, hook catches gap, emits CIEU event
5. **Board Override**: Board activates safemode, CTO writes to restricted path, override expires, CTO denied

### Chaos Tests (Failure Mode)
1. **Agent Crash During Delegation**: CEO delegates to CTO, SIGKILL CTO mid-work, verify CEO identity restored
2. **MCP Daemon Crash**: Kill MCP server mid-check, restart, verify contract reloaded from .ystar_session.json
3. **Filesystem Race**: Two agents write to same file, verify capability check serializes writes
4. **Override Abuse**: Board activates 4 overrides in 1 hour, verify 4th denied
5. **Cache Corruption**: Manually corrupt `.ystar_session.json`, restart daemon, verify fallback to AGENTS.md

### Red-Team Tests (Attack Scenarios)
1. **Capability Escalation**: eng-kernel tries to grant itself `write:*`, verify DENIED
2. **Path Traversal**: Agent tries to write `../../etc/passwd`, verify normalized path check blocks
3. **Safemode Hijack**: CTO tries to call `gov_safemode`, verify only Board can activate
4. **Narrative Fabrication**: Agent claims "tests pass" without running Bash, verify gap detected
5. **Override Expiry Bypass**: Agent tries to use expired override token, verify DENIED

### Performance Benchmarks
1. **Gov_check Latency**: Measure P50/P95/P99 latency before/after RWLock (target: <1ms added overhead)
2. **Capability Check Overhead**: Measure file write latency with capability check vs without (target: <5ms added overhead)
3. **Narrative Detection Cost**: Measure turn completion time with/without narrative check (target: <100ms added overhead)
4. **Contract Reload Time**: Measure time from AGENTS.md write to MCP server reload (target: <5s)

### Load Tests
1. **Concurrent Agent Spawn**: Spawn 50 agents simultaneously, verify no identity collision
2. **Burst Override**: Board activates 100 overrides in 1 second (within rate limit), verify all recorded in CIEU
3. **High-Frequency Write**: Agent writes 1000 files in 1 minute, verify capability check doesn't bottleneck

---

## Rollout Plan

### Phase 4a: Layer 1 (Week 1)
- **Deploy**: Staging (CEO agent only, no sub-agents)
- **Soak Time**: 24 hours
- **Success Criteria**: `.ystar_active_agent` file not written, hook reads identity from session
- **Rollback Plan**: Revert `governance_boot.sh`, restore file write
- **Production Deploy**: Friday EOD

### Phase 4b: Layer 2 (Week 2)
- **Deploy**: Staging (CEO + 1 test delegation to eng-kernel)
- **Soak Time**: 48 hours
- **Success Criteria**: Delegation works, token expires, no capability escalation
- **Rollback Plan**: Revert to role whitelist in AGENTS.md
- **Production Deploy**: Friday EOD

### Phase 4c+4d: Layer 3.1-3.3 (Week 3)
- **Deploy**: Staging (full team, monitor breaker arm rate)
- **Soak Time**: 7 days
- **Success Criteria**: Breaker arm rate drops ≥50%, contract auto-reloads on AGENTS.md change
- **Rollback Plan**: Disable observable action detector, restore phrase detector
- **Production Deploy**: Friday EOD (after 7-day soak)

### Phase 4e: Layer 3.4 (Week 4)
- **Deploy**: Staging (full team, collect narrative gap statistics)
- **Soak Time**: 7 days
- **Success Criteria**: False positive rate <10%, this session's failure caught by detector
- **Rollback Plan**: Disable narrative check hook
- **Production Deploy**: Friday EOD (after 7-day soak + false positive tuning)

### Phase 4f: Layer 4 (Week 5)
- **Deploy**: Staging (Board only, test safemode for hotfix scenario)
- **Soak Time**: 48 hours
- **Success Criteria**: Board can override, rate limit enforced, non-Board agents denied
- **Rollback Plan**: Remove `gov_safemode` tool, CLI safemode errors with "feature disabled"
- **Production Deploy**: Friday EOD

### Phase 4g: MCP State Race Fix (Week 6)
- **Deploy**: Staging (run load test: 100 agents hitting gov_check concurrently)
- **Soak Time**: 48 hours
- **Success Criteria**: Concurrency test passes 1000 iterations, P99 latency <10ms
- **Rollback Plan**: Remove RWLock, revert to single-threaded MCP server
- **Production Deploy**: Friday EOD

### Full Rollout Timeline
- **Week 1**: Phase 4a (Identity Source of Truth)
- **Week 2**: Phase 4b (Capability-Based Permissions)
- **Week 3**: Phase 4c+4d (Observable Action + File Watcher)
- **Week 4**: Phase 4e (Narrative Coherence Detection)
- **Week 5**: Phase 4f (User Escape Hatch)
- **Week 6**: Phase 4g (MCP State Race Fix)
- **Week 7**: Final integration test (all 6 layers + 108 tests pass), production deploy

**Success Criteria for Full Rollout**:
- All 108 tests pass (86 existing + 22 new)
- Circuit breaker arm rate drops ≥50% (measured over 30 days post-rollout)
- Board override usage <3/day (indicates governance is not blocking legitimate work)
- Narrative gap detection rate <1% of turns (low false positive rate)
- Zero identity drift incidents (agent stack auto-restores on sub-agent exit)
- Contract always current (MCP server auto-reloads within 5s of AGENTS.md change)

---

## Open Questions

### Q1: Layer 1 — What happens if sub-agent crashes without calling `pop_agent()`?
**Answer**: Add `session.agent_stack_timeout = 300s`. If agent_stack unchanged for 5min, auto-pop stale agents.

**Follow-up**: What if legitimate work takes >5min? 
**Answer**: Sub-agent must emit heartbeat (CIEU event `agent_heartbeat` every 60s). If no heartbeat for 5min, assume crash, auto-pop.

### Q2: Layer 2 — How to handle capability wildcards and path traversal?
**Answer**: Normalize all paths before matching (resolve `..`, symlinks). Reject any path that escapes workspace root.

**Follow-up**: What about symlinks to allowed paths? 
**Answer**: Resolve symlinks, then check normalized path against capability. If symlink target is allowed, grant. If target is outside workspace, deny.

### Q3: Layer 3.4 — What if agent uses Bash tool to write file instead of Write tool?
**Answer**: Extend `NarrativeCoherenceDetector.extract_action_claims()` to parse Bash commands for file operations (`>`, `>>`, `tee`, `cat > file`). If detected, treat as equivalent to Write tool.

**Follow-up**: What about complex shell scripts (loops, conditionals)? 
**Answer**: Phase 1 detector uses regex patterns (simple cases). Phase 2 can upgrade to LLM-based parsing (send Bash command to Gemma, ask "does this write to file X?"). Balance precision vs cost.

### Q4: Layer 4 — Can Board override expire mid-action?
**Answer**: Yes. Override expiry is checked at hook invocation time. If override expires during long-running action (e.g., 10min compile), action completes but next hook check will deny.

**Follow-up**: Should override extend automatically if action is in progress? 
**Answer**: No. Design philosophy: overrides are escape hatches, not blanket bypasses. If action needs >5min, Board should request longer duration upfront (`--duration 600`).

### Q5: MCP-1 Race — What about readers that hold lock for long time (e.g., slow enforcement)?
**Answer**: RWLock allows multiple concurrent readers (shared lock). Only writers (contract activate) block. If gov_enforce takes 1s, other agents' gov_check can run concurrently.

**Follow-up**: What if writer (contract activate) is blocked waiting for readers to release? 
**Answer**: This is expected RWLock behavior (write-starving). If contract reload becomes urgent, add priority queue (writer can preempt readers). But empirically, contract reloads are rare (maybe 1/day during AGENTS.md edits), so write-starving is acceptable.

### Q6: Cross-Layer — What if Layer 3.4 (narrative check) detects gap in Layer 4 (safemode override)?
**Answer**: Narrative check runs BEFORE safemode override check. If Board activates safemode for "write file without tool", narrative gap is still detected and logged (CIEU event), but enforcement is bypassed (override allows the write).

**Follow-up**: Should narrative gaps block even during override? 
**Answer**: No. Override is Board's explicit decision to bypass governance. Narrative gap is logged for post-review, but not blocked. If Board's override was due to a legitimate gap (e.g., emergency hotfix with Bash instead of Write tool), post-review will document it.

---

## Appendix A: Cycle Classification Table (from Phase 2)

| Cycle ID | Name | Classification | Empirical Frequency | Break-Safe? | Priority | Layer |
|----------|------|----------------|---------------------|-------------|----------|-------|
| **L2** | Omission → Circuit Breaker | Over-defense | 158 chains, 192 arms | **YES** | **P0** | **Layer 3.1** |
| **Bucket2** | Behavior Rule Soft Lock | Over-defense | 155 sequences | **YES** | P1 | **Layer 3.2** |
| **L4** | Sub-agent 4-Parallel Ritual | Over-defense | 33 violations | PARTIAL | P1 | Contract update (not architecture) |
| **L3** | Hook Daemon Cache Drift | Over-defense | Indirect | NO | P2 | **Layer 3.3** |
| **MCP-1** | active_contract Race | Security-essential | 0 (masked by GIL) | **NO** | P0 | **Phase 4g (separate)** |
| **L1** | Sub-agent Identity Restore | Legacy | 0 | YES | P2 | **Layer 1 (covers implicitly)** |
| **L5** | Restricted Write Paths | Legacy | 0 | YES | P2 | **Layer 2 (replaced by capabilities)** |

**Note**: L4 (Sub-agent ritual) is solved by updating AGENTS.md to add path_a_agent to whitelist, not by architecture change. L1/L5 are legacy safeguards with 0 empirical triggers, but Layer 1/2 architecture improvements cover them implicitly.

---

## Appendix B: 4-Layer Summary Table

| Layer | Problem Solved | Mechanism | Break-Safe? | Test Count | Phase |
|-------|----------------|-----------|-------------|------------|-------|
| **Layer 1**: Identity Source of Truth | Identity drift, no sub-agent auto-restore | `.ystar_session.json` agent stack, push/pop on delegation | YES | 3 | 4a (Week 1) |
| **Layer 2**: Capability-Based Permissions | Hardcoded role whitelist, can't add new agents without contract reload | Replace roles with capabilities (`write:path`), runtime grant/revoke | YES | 4 | 4b (Week 2) |
| **Layer 3.1**: Observable Action Detection | 72.3% false-positive breaker arms (form violations) | Auto-satisfy obligations on git commit / file write evidence | YES | 3 | 4c (Week 3) |
| **Layer 3.2**: Hard Block on 2nd Violation | 155 soft lock sequences (warnings ignored) | Escalate WARN → DENY on 2nd violation within 5min | YES | 3 | 4c (Week 3) |
| **Layer 3.3**: Hook Daemon File Watcher | Stale contract enforcement (cache vs file drift) | inotify watcher on AGENTS.md, auto-reload contract | NO (but low risk) | 1 | 4d (Week 3) |
| **Layer 3.4**: Narrative Coherence Detection | Agent claims action without tool evidence (this session's failure) | Parse text for action claims, compare against tool usage, emit CIEU event | YES | 4 | 4e (Week 4) |
| **Layer 4**: User Escape Hatch | No clean override when governance blocks legitimate work | CLI + MCP tool for single-action override with audit trail, rate limit, post-review | YES | 5 | 4f (Week 5) |
| **MCP-1**: RWLock on active_contract | State race during contract activation (future async scaling) | Add RWLock (writers=activate, readers=check/enforce/exec) | NO (security-essential) | 2 | 4g (Week 6) |

**Total**: 8 components, 25 new tests, 6-week rollout.

---

## Appendix C: CIEU Event Schema Extensions

New event types introduced by AMENDMENT-015:

```python
# Layer 1: Identity Source of Truth
CIEUEvent(event_type="agent_push", agent_id="ceo", sub_agent="cto", timestamp=...)
CIEUEvent(event_type="agent_pop", agent_id="cto", restored_agent="ceo", timestamp=...)
CIEUEvent(event_type="agent_stack_timeout", stale_agent="cto", timeout_sec=300, timestamp=...)

# Layer 2: Capability-Based Permissions
CIEUEvent(event_type="capability_granted", grantor="ceo", grantee="eng-kernel", capability="write:reports/tech_debt.md", duration_sec=3600, timestamp=...)
CIEUEvent(event_type="capability_revoked", grantor="ceo", grantee="eng-kernel", capability="write:reports/tech_debt.md", timestamp=...)
CIEUEvent(event_type="capability_expired", grantee="eng-kernel", capability="write:reports/tech_debt.md", timestamp=...)

# Layer 3.1: Observable Action Detection
CIEUEvent(event_type="omission_auto_satisfied", obligation_id="...", evidence="git commit abc123 modified foo.py", timestamp=...)

# Layer 3.2: Hard Block on 2nd Violation
CIEUEvent(event_type="violation_escalated_to_deny", agent_id="ceo", violation_type="completion_requires_cieu_audit", repeat_count=2, window_sec=300, timestamp=...)

# Layer 3.3: Hook Daemon File Watcher
CIEUEvent(event_type="contract_reloaded_auto", trigger="AGENTS.md modified", new_contract_hash="...", timestamp=...)

# Layer 3.4: Narrative Coherence Detection
CIEUEvent(event_type="narrative_bias_detected", agent_id="cto", claim="6-pager written", expected_tool="Write", actual_tools=[], severity="HIGH", timestamp=...)

# Layer 4: User Escape Hatch
CIEUEvent(event_type="governance_override_activated", agent_id="board", override_id="...", action="write:src/critical.py", justification="emergency hotfix", duration_sec=300, timestamp=...)
CIEUEvent(event_type="governance_override_complete", agent_id="board", override_id="...", exit_code=0, timestamp=...)
CIEUEvent(event_type="governance_override_denied", agent_id="cto", reason="only Board can activate safemode", timestamp=...)
```

---

## Appendix D: Performance Impact Estimates

| Layer | Component | Baseline Latency | Added Overhead | New Latency | % Increase |
|-------|-----------|-----------------|----------------|-------------|------------|
| Layer 1 | Hook identity read | 0.1ms (file read) | -0.05ms (memory read) | 0.05ms | -50% (improvement) |
| Layer 2 | Capability check | 0.2ms (role whitelist) | +0.3ms (path normalization) | 0.5ms | +150% |
| Layer 3.1 | Obligation check | 5ms (phrase scan) | -3ms (git log cached) | 2ms | -60% (improvement) |
| Layer 3.2 | Violation tracking | 0ms (warn-only) | +0.1ms (dict lookup) | 0.1ms | N/A (new feature) |
| Layer 3.3 | Contract reload | Manual (admin action) | +2s (file watcher + reload) | 2s | N/A (auto vs manual) |
| Layer 3.4 | Narrative check | 0ms (no check) | +50ms (regex parse + CIEU query) | 50ms | N/A (new feature) |
| Layer 4 | Override check | 0ms (no override) | +0.1ms (dict lookup) | 0.1ms | N/A (new feature) |
| MCP-1 | RWLock | 0.05ms (no lock) | +0.5ms (lock acquire/release) | 0.55ms | +1000% (but baseline is tiny) |

**Total impact per agent action**:
- Baseline: 5.35ms (identity read + role check + obligation scan)
- New: 3.3ms (improved identity + slower capability + improved obligation + new checks)
- **Net improvement: -2.05ms (-38%)**

**Rationale for improvement**: Layer 1 (memory vs file) and Layer 3.1 (git log vs phrase scan) eliminate expensive I/O. Layer 2 (capability check) adds overhead, but overall governance loop is faster.

**Caveat**: Layer 3.4 (narrative check) adds 50ms, but only runs at turn completion (not per tool call), so amortized cost is low.

---

## Appendix E: Werner Vogels Audit — "Everything Fails" Applied to AMENDMENT-015

**Q1: What failure modes does this design introduce?**

1. **Layer 1 (Agent Stack)**: If `.ystar_session.json` corrupted, agent stack lost → no identity recovery
   - **Mitigation**: Add `session.json.backup` written on every stack mutation, restore from backup on corruption
   - **Test**: `test_session_json_corruption_recovery()`

2. **Layer 2 (Capabilities)**: Path normalization regex bug → capability bypass (e.g., `..` not caught)
   - **Mitigation**: Use `os.path.realpath()` + `os.path.commonpath()` (stdlib, battle-tested) instead of custom regex
   - **Test**: `test_capability_path_traversal_comprehensive()` (50+ attack strings from OWASP)

3. **Layer 3.1 (Observable Action)**: Git log query slow on large repos → obligation check timeout
   - **Mitigation**: Add 5s timeout on git log, fallback to phrase detector if timeout
   - **Test**: `test_observable_action_timeout()` (mock 10s git log, verify fallback)

4. **Layer 3.4 (Narrative Check)**: Regex false positive → legitimate action flagged as gap
   - **Mitigation**: Use allowlist-based parsing (only flag claims matching known patterns), not denylist (flag anything suspicious)
   - **Test**: `test_narrative_check_false_positive_rate()` (run on 1000 agent turns, measure FP rate)

5. **Layer 4 (Override)**: Rate limit state lost on daemon restart → bypass protection
   - **Mitigation**: Persist rate limit state to `.ystar_session.json`, restore on daemon start
   - **Test**: `test_override_rate_limit_persistence_across_restart()`

6. **MCP-1 (RWLock)**: Deadlock if writer holds lock and crashes
   - **Mitigation**: Use timeout on lock acquisition (5s), if timeout → log error, skip contract reload
   - **Test**: `test_rwlock_deadlock_recovery()` (SIGKILL writer during activation, verify readers unblocked)

**Q2: How do we test failure modes before production?**

Add chaos test suite (Appendix F) that deliberately kills daemons, corrupts files, and triggers race conditions.

**Q3: If this design fails in production, what's the blast radius?**

- **Layer 1 failure**: Agent identity wrong → wrong capability check → work blocked (NOT security bypass)
- **Layer 2 failure**: Capability bypass → agent writes to restricted path → governance failure (but CIEU log captures it)
- **Layer 3.1 failure**: Obligation never satisfied → circuit breaker arms → work blocked (NOT security bypass)
- **Layer 3.4 failure**: Narrative gap false positive → agent warned, slowed down (NOT blocked)
- **Layer 4 failure**: Override rate limit bypassed → Board can override >3/hour (acceptable, Board is root)
- **MCP-1 failure**: Contract race → partial read → wrong ALLOW/DENY decision → **WORST CASE** (security bypass or false block)

**Mitigation for MCP-1**: This is why it's P0 despite 0 empirical triggers. Add before async scaling, not after.

---

## Appendix F: Chaos Test Suite

All tests run in isolated Docker container (prevent damage to dev machine):

```python
# tests/chaos/test_amendment_015_chaos.py

def test_agent_crash_during_delegation():
    """CEO delegates to CTO, SIGKILL CTO mid-work, verify CEO identity restored"""
    # Spawn CEO agent, delegate to CTO, SIGKILL CTO subprocess
    # Verify .ystar_session.json agent_stack pops CTO, restores CEO
    # Verify next hook call reads CEO identity

def test_session_json_corruption():
    """Corrupt .ystar_session.json, restart daemon, verify fallback to backup"""
    # Write invalid JSON to .ystar_session.json
    # Restart MCP daemon
    # Verify daemon loads from session.json.backup

def test_mcp_daemon_crash_during_contract_activate():
    """SIGKILL MCP daemon during gov_contract_activate, verify contract not corrupted"""
    # Call gov_contract_activate, SIGKILL daemon mid-write
    # Restart daemon
    # Verify active_contract loaded from .ystar_session.json (not partial state)

def test_git_log_timeout():
    """Mock 10s git log, verify observable action detector falls back to phrase scan"""
    # Mock git.log() to sleep 10s
    # Check directive_acknowledgement obligation
    # Verify fallback to phrase detector after 5s timeout

def test_capability_path_traversal_comprehensive():
    """50+ OWASP path traversal attack strings, verify all blocked"""
    # Test: ../../etc/passwd, /etc/passwd, ./../../etc/passwd, symlink attacks, etc.
    # Verify all denied by capability check

def test_narrative_check_false_positive_rate():
    """Run detector on 1000 real agent turns, measure false positive rate"""
    # Load 1000 CIEU events (agent_turn_complete)
    # Run narrative check on each
    # Manually label false positives
    # Verify FP rate <10%

def test_override_rate_limit_bypass_attempt():
    """Board activates 4 overrides in 1 hour, verify 4th denied"""
    # Call gov_safemode 4x within 1 hour
    # Verify 4th returns error

def test_override_rate_limit_persistence_across_restart():
    """Board activates 3 overrides, restart daemon, verify rate limit state restored"""
    # Call gov_safemode 3x
    # Kill + restart MCP daemon
    # Call gov_safemode 4th time
    # Verify 4th denied (rate limit state persisted)

def test_rwlock_deadlock_recovery():
    """Writer holds lock and crashes, verify readers unblocked after timeout"""
    # Start gov_contract_activate, SIGKILL mid-write
    # Spawn 10 gov_check readers
    # Verify readers timeout after 5s, continue without contract reload

def test_hook_cache_invalidation_race():
    """Modify AGENTS.md while hook is checking, verify no stale read"""
    # Start gov_check (reads contract)
    # Mid-check, modify AGENTS.md (file watcher triggers reload)
    # Verify gov_check uses old contract (atomic), next check uses new contract

def test_sub_agent_stack_overflow():
    """Delegate CEO → CTO → eng-kernel → eng-platform (4-deep), verify no stack corruption"""
    # Push 4 agents to stack
    # Pop all 4
    # Verify CEO restored, no memory leak

def test_capability_grant_expiry_clock_skew():
    """Grant capability with 60s TTL, set system clock +70s, verify token expired"""
    # Grant capability
    # Mock time.time() to return +70s
    # Verify capability check denied

def test_omission_auto_satisfy_git_log_corruption():
    """Corrupt git log (invalid commit), verify obligation checker doesn't crash"""
    # Mock git.log() to return invalid commit hash
    # Check directive_acknowledgement obligation
    # Verify checker falls back to phrase detector, doesn't crash

def test_narrative_check_bash_file_write_detection():
    """Agent writes file via Bash (echo > file), verify narrative check detects it"""
    # Agent says "file written", calls Bash with "echo test > file.txt"
    # Verify narrative check parses Bash command, detects write, no gap

def test_safemode_wildcard_override_confirmation():
    """Board tries wildcard override without confirmation, verify denied"""
    # Call gov_safemode(action="*")
    # Verify returns error "requires explicit confirmation"

def test_safemode_expiry_mid_action():
    """Board activates 60s override, start 120s compile, verify compile completes but next action denied"""
    # Activate 60s override
    # Run 120s compile (mock sleep)
    # Verify compile completes (no mid-action interrupt)
    # Next file write denied (override expired)
```

**Total chaos tests**: 15
**Run frequency**: Every PR merge (CI/CD), weekly scheduled run on staging

---

## Appendix G: Rollback Decision Tree

If any phase fails during rollout, use this decision tree:

```
Phase Failure Detected
│
├── Tests fail?
│   ├── <5% fail → Debug, patch, retry deploy
│   ├── 5-20% fail → Rollback phase, escalate to CTO
│   └── >20% fail → Rollback entire amendment, root cause analysis
│
├── Performance regression?
│   ├── <10% slower → Accept, monitor for 1 week
│   ├── 10-50% slower → Debug, optimize, retry deploy
│   └── >50% slower → Rollback phase, escalate to CTO
│
├── Circuit breaker arm rate increase?
│   ├── <10% increase → Accept (noise), monitor for 1 week
│   ├── 10-50% increase → Debug, tune parameters, retry deploy
│   └── >50% increase → Rollback phase (worse than before)
│
├── Security incident?
│   ├── Capability bypass detected → Immediate rollback, hotfix within 24h
│   ├── Narrative fabrication undetected → Rollback Layer 3.4, investigate
│   └── Override abuse → Disable Layer 4, investigate
│
└── Operational incident?
    ├── MCP daemon crashes → Rollback to last stable phase, debug
    ├── Identity drift → Rollback Layer 1, investigate
    └── Contract reload fails → Rollback Layer 3.3, manual reload protocol
```

**Rollback SLA**: Within 4 hours of incident detection, rollback to last known good state.

**Post-Rollback Protocol**:
1. Freeze all AMENDMENT-015 deployments
2. CTO convenes postmortem within 24h (CTO + affected engineer + CEO)
3. Root cause analysis (5 Whys)
4. Fix implementation + new test to catch failure mode
5. Re-validate on staging (7-day soak)
6. Retry deploy

---

**End of 6-Pager Design Document**

---

**Document Metadata**:
- **Word Count**: ~9,200 words
- **Line Count**: ~900 lines
- **Sections**: 9 main + 7 appendices
- **Test Count**: 108 (86 existing + 22 new)
- **Rollout Duration**: 7 weeks (6 weeks phased + 1 week final integration)
- **Author**: Ethan Wright (CTO), with contributions from Leo Chen (Kernel), Maya Patel (Governance), Ryan Park (Platform)
- **Review Status**: Awaiting Board approval
- **Next Steps**: Board review → approve/reject → hand off Phase 4 tasks to engineering team
