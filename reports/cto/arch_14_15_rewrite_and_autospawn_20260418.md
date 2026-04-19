# CZL-ARCH-14 REWRITE + CZL-ARCH-15 Auto-Spawn Daemon -- Architecture Supplement

**Date**: 2026-04-18
**Author**: Ethan Wright, CTO
**Audience**: Board (Haotian Liu) -- primary approver; CEO (Aiden) for dispatch oversight; eng-kernel (Leo), eng-platform (Ryan) for implementation.
**Research basis**: Board 2026-04-18 afternoon directives (verbatim below), Y-star-gov `EnforceDecision` enum (adapter.py:91-99), `RouterRegistry` (router_registry.py:146+), ARCH-8 NEXT_ACTION design, ARCH-11a/b/c/d mandatory invoke pipeline, ARCH-13 routing-as-universal-solver philosophy doc. Industry analogs: black/prettier auto-format, Istio mTLS auto-inject, SQL parameterized query sanitization, Rust clippy `--fix`, Go `goimports`.
**Synthesis**: Board identified two structural gaps that existing ARCH tasks do not close: (1) governance warns but does not repair non-compliant actions, leaving the agent to interpret and often ignore guidance; (2) whiteboard tasks accumulate but nobody spawns an agent to execute them. This document designs two new mechanisms -- REWRITE (auto-repair at the enforcement layer) and Auto-Spawn Daemon (whiteboard-to-execution bridge) -- and positions them within the existing 4-layer architecture.

---

## Board Directives (Verbatim)

1. "不能靠自律和简单命令解决 -- 要在某地方让 agent 一定按规则完成任务"
2. "能不能有个模块把 agent 做的不合规的地方**直接修改到合规**然后顺利推进"
3. "为什么写完白板都没人响应"

These are not feature requests. They are architectural requirements. Directive 1 is the invariant: governance must enforce, not advise. Directives 2 and 3 are the two mechanisms.

---

## Part A: CZL-ARCH-14 -- REWRITE Decision Design

### A.1 Problem Statement

The current enforcement pipeline has three response modes:
- **DENY**: block the action, return reason text. Agent must interpret free-text, decide what to do, and may ignore it.
- **REDIRECT**: return fix instructions (FIX_COMMAND + THEN_RETRY). Agent sees the guidance but still must choose to execute it. Today's evidence: agents see REDIRECT guidance and hardwrite anyway (Board catch 2026-04-18).
- **INVOKE**: hook layer auto-executes a fix command. This is the right direction (ARCH-11a) but only handles known fix-command patterns, not payload transformation.

The missing mode is: **the governance layer silently transforms the non-compliant payload into a compliant one and proceeds**. The agent does not need to interpret, decide, or act. The governance layer has already fixed the problem.

### A.2 REWRITE Semantics

**Definition**: A REWRITE decision means the enforcement layer detects a non-compliant tool-call payload, applies a deterministic transformation to make it compliant, and returns the transformed payload for execution. The original payload is never executed. The agent is notified post-hoc that a rewrite occurred.

**Formal predicate** (FOL):

```
Let P = original payload, T = transformation function, P' = T(P)
REWRITE(P) iff:
  1. exists rule R in router_registry where R.detector(P) = true
  2. R.executor(P).decision = "rewrite"
  3. R.executor(P).rewritten_payload = P' where P' != P
  4. check(P') = ALLOW  (the rewritten payload must itself be compliant)
  5. T is in SAFE_TRANSFORMS whitelist
```

**Critical invariant**: `check(P') = ALLOW`. If the rewrite produces a payload that itself fails enforcement, the REWRITE degrades to DENY. This prevents rewrite chains or rewrite-to-rewrite loops.

**EnforceDecision enum extension**:

```python
class EnforceDecision(str, Enum):
    ALLOW     = "allow"
    DENY      = "deny"
    ESCALATE  = "escalate"
    REDIRECT  = "redirect"
    INVOKE    = "invoke"
    INJECT    = "inject"
    AUTO_POST = "auto_post"
    REWRITE   = "rewrite"     # NEW: transform payload to compliant version
```

### A.3 Rewrite Transformations Whitelist (5 Modes)

Each transformation mode is a category of safe, deterministic payload changes. Only whitelisted modes are permitted. Unknown transformations are rejected.

| # | Mode | Detector Pattern | Transformation | Example | Safety Class |
|---|------|-----------------|----------------|---------|--------------|
| 1 | **path-alias** | `file_path` contains legacy/wrong path prefix | Replace path prefix with canonical path from `.ystar_session.json` | `C:\Users\liuha\...\Y-star-gov\` -> `/Users/haotianliu/.openclaw/workspace/Y-star-gov/` | SAFE: bijective mapping, no data loss |
| 2 | **arg-injection** | Command missing required flag/argument | Append required argument to command string | `git commit` -> `git commit --no-verify` (when in test mode) | SAFE: additive only, original args preserved |
| 3 | **next-action-append** | ALLOW response has no NEXT guidance | Append computed NEXT_ACTION to permissionDecisionReason | `{}` -> `{"permissionDecisionReason": "NEXT: resume CZL-ARCH-8"}` | SAFE: enrichment only, does not alter allow/deny |
| 4 | **format-normalize** | Payload contains malformed JSON / encoding issues | Fix BOM, normalize unicode, repair truncated JSON | `\xef\xbb\xbf{"tool":...}` -> `{"tool":...}` | SAFE: canonical form, no semantic change |
| 5 | **command-expand** | Bash command is an alias or partial that will fail | Expand to full canonical command | `ystar doctor` -> `python3 -m ystar.cli doctor` (when ystar not on PATH) | SAFE: semantic equivalence, tested expansion table |

**Unsafe rewrites (DENIED -- always fall through to DENY)**:
- Changing `tool_name` (e.g., rewriting a Write to a Read -- changes semantics entirely)
- Changing `file_path` to a different logical target (e.g., rewriting write to `reports/x.md` into write to `src/y.py`)
- Removing content from a Write/Edit payload
- Altering the user's code logic in any way
- Any transformation not in the 5-mode whitelist

### A.4 Industry Analogs

| System | What It Rewrites | Safety Boundary | Transparency |
|--------|-----------------|-----------------|--------------|
| **black** (Python formatter) | Whitespace, quotes, line length | AST-preserving (parses, reformats, re-parses, asserts AST equality) | `--diff` shows before/after |
| **prettier** (JS/TS formatter) | Same class as black for JS ecosystem | AST-preserving | `--write` modifies in-place with diff output |
| **Istio mTLS auto-inject** | Plain HTTP -> mutual TLS | Only wraps transport, never modifies application payload | Envoy access logs show `upstream_tls_version` |
| **SQL parameterized queries** | Raw string interpolation -> parameterized `?` placeholders | Semantic equivalence (same query, safe binding) | Query plan unchanged |
| **Rust clippy --fix** | Code patterns that clippy warns about | Only applies machine-applicable fixes (subset of all warnings) | `--fix` requires explicit opt-in; shows diff |
| **Go goimports** | Missing/unused imports | Adds missing, removes unused; no logic changes | Diff output |

**Common pattern**: All of these systems (a) preserve semantics / AST, (b) have an explicit "safe subset" of transformations, (c) log what changed for transparency, (d) can be disabled. ARCH-14 REWRITE follows the same design.

### A.5 CIEU Schema for REWRITE_APPLIED Event

Every REWRITE produces a CIEU event for full audit trail. The event captures before, after, which rule triggered it, and whether the rewritten payload passed re-check.

```json
{
  "event_type": "REWRITE_APPLIED",
  "grade": "governance_rewrite",
  "agent_id": "ceo",
  "timestamp": "2026-04-18T15:30:00.000Z",
  "dimensions": {
    "rule_ref": "labs.path_alias_normalizer",
    "rewrite_mode": "path-alias",
    "original_payload": {
      "tool_name": "Write",
      "file_path": "C:\\Users\\liuha\\...\\Y-star-gov\\ystar\\foo.py",
      "content": "..."
    },
    "rewritten_payload": {
      "tool_name": "Write",
      "file_path": "/Users/haotianliu/.openclaw/workspace/Y-star-gov/ystar/foo.py",
      "content": "..."
    },
    "recheck_result": "allow",
    "original_would_have_been": "deny",
    "transformation_deterministic": true,
    "safe_transform_verified": true
  },
  "context": "Agent used legacy Windows path. REWRITE normalized to canonical macOS path. Rewritten payload passed re-check."
}
```

**Key fields**:
- `original_would_have_been`: what the enforcement layer WOULD have returned for the original payload. This proves the rewrite was necessary. If this is already "allow", the rewrite is redundant and should not fire (detector should not match).
- `recheck_result`: must be "allow" for the REWRITE to proceed. If "deny", the entire response degrades to DENY with additional context explaining why the rewrite also failed.
- `transformation_deterministic`: always true for whitelisted modes. If false, the rewrite rule is misconfigured and should be disabled.

### A.6 "Safe" vs "Unsafe" Rewrite Criteria

A rewrite transformation T is **safe** iff ALL of the following hold:

1. **Semantic preservation**: The agent's intent is unchanged. T modifies form (path encoding, argument ordering, format) not meaning (target file, content, operation type).
2. **Deterministic**: Given the same input P, T always produces the same output P'. No randomness, no LLM inference, no heuristic matching.
3. **Reversible in log**: The CIEU REWRITE_APPLIED event contains enough information to reconstruct the original payload exactly.
4. **Whitelisted mode**: T falls into one of the 5 defined modes. No ad-hoc transformations.
5. **Re-check passes**: `check(T(P)) = ALLOW`. The transformed payload must itself be compliant.
6. **No privilege escalation**: T does not grant access to resources the agent's role does not permit. (e.g., path-alias must map to a path within the agent's write scope, not to a new scope.)
7. **Idempotent**: `T(T(P)) = T(P)`. Applying the rewrite twice produces the same result as applying it once. This prevents rewrite loops.

A rewrite that fails any of these criteria is **unsafe** and MUST NOT be applied. The enforcement layer falls back to DENY with the reason including which safety criterion failed.

### A.7 Stop Hook Learning Hint Injection

After a REWRITE, the agent should learn from it to avoid triggering the same rewrite next time. The Stop hook (PostToolUse) injects a one-line learning hint into the next response context:

```
[Y*gov REWRITE] Your action was auto-corrected: {rewrite_mode}. 
Original: {summary_of_original}
Corrected to: {summary_of_rewritten}
Rule: {rule_ref}
To avoid this rewrite: {prevention_hint}
```

Example:
```
[Y*gov REWRITE] Your action was auto-corrected: path-alias.
Original: file_path="C:\Users\liuha\...\Y-star-gov\ystar\foo.py"
Corrected to: file_path="/Users/haotianliu/.openclaw/workspace/Y-star-gov/ystar/foo.py"
Rule: labs.path_alias_normalizer
To avoid this rewrite: Use canonical macOS paths. Legacy Windows paths are deprecated (AMENDMENT-004).
```

This is injected via the existing INJECT mechanism at priority 900 (high, so the agent sees it immediately). The injection is ephemeral -- it appears once, not on every subsequent tool call.

### A.8 REWRITE Decision Flow (hook.py Integration)

```
PreToolUse payload arrives
    |
    v
RouterRegistry.evaluate(payload)
    |
    +-- Rule matches with decision="rewrite"?
    |       |
    |       YES --> rewritten_payload = rule.executor(payload).rewritten_payload
    |       |       |
    |       |       v
    |       |   check(rewritten_payload) == ALLOW?
    |       |       |           |
    |       |       YES         NO
    |       |       |           |
    |       |       v           v
    |       |   CIEU emit       CIEU emit REWRITE_FAILED
    |       |   REWRITE_APPLIED return DENY + "rewrite also failed"
    |       |   |
    |       |   v
    |       |   Return {"permissionDecision": "replace",
    |       |           "replacementPayload": rewritten_payload,
    |       |           "permissionDecisionReason": "REWRITE: ..."}
    |       |
    |       NO --> fall through to next rule / check/enforce
    |
    v
Normal enforce flow (ALLOW / DENY / REDIRECT / etc.)
```

**Note on Claude Code hook protocol**: The Claude Code PreToolUse hook protocol does not natively support `replacementPayload`. The hook can return `permissionDecision: "allow"` or `"deny"`. To implement REWRITE, we use the following mechanism:

- For payload fields that are in the `permissionDecisionReason` (agent-visible text), we inject the corrected value as guidance and let the agent re-issue.
- For path-alias rewrites specifically, we DENY with a structured REDIRECT containing the correct path, combined with ARCH-11a auto-invoke to automatically re-issue with the corrected path.

This means REWRITE at the hook level is actually **DENY + auto-INVOKE(corrected)** -- the same two-step that ARCH-11a provides, but with the rewrite rule computing the correction automatically. The CIEU event still records it as REWRITE_APPLIED because from the agent's perspective, their action was transparently corrected.

For the MCP adapter and future SDK-native hooks that support payload replacement, REWRITE can be a true in-place transformation.

---

## Part B: CZL-ARCH-15 -- Auto-Spawn Daemon Design

### B.1 Problem Statement

The dispatch_board.json currently has 15+ tasks. Of those:
- Most are status "claimed" but have no `completion_receipt` -- meaning an agent was assigned but never executed (or stalled at 600s watchdog).
- The `cto_dispatch_broker.py` writes routing metadata (`claimed_by`, `claimed_at`) but does NOT spawn an agent to do the work.
- The CEO must manually run `Agent` tool calls to spawn sub-agents for each task. If CEO forgets, or stalls, or the session ends, tasks rot.

Board's question -- "为什么写完白板都没人响应" -- has a precise structural answer: **the broker routes but does not execute. There is no daemon that converts a whiteboard task into a running agent.**

### B.2 Architecture: Auto-Spawn Daemon

```
                    dispatch_board.json
                         |
                         v
              +--------------------------+
              | dispatch_auto_spawner.py |
              | (daemon, polls board)     |
              +--------------------------+
                         |
                    detects open/stale tasks
                         |
                         v
              +--------------------------+
              | .pending_spawns.json     |
              | (queue file)              |
              +--------------------------+
                         |
                    read by hook_wrapper.py
                    on CEO's next tool_use
                         |
                         v
              +--------------------------+
              | hook_wrapper.py          |
              | (PreToolUse / PostToolUse)|
              | triggers Agent spawn     |
              +--------------------------+
                         |
                         v
              +--------------------------+
              | Agent("eng-kernel", ...) |
              | runs task, writes receipt |
              +--------------------------+
                         |
                         v
              dispatch_board.json
              (status: completed,
               completion_receipt: ...)
```

### B.3 Subagent Type Inference Rules

The daemon must decide WHICH agent to spawn for a given task. This is a deterministic mapping from task scope to agent role.

| Scope Prefix / Pattern | Inferred Role | Agent Definition |
|------------------------|---------------|-----------------|
| `Y-star-gov/ystar/kernel/` | `eng-kernel` | `.claude/agents/eng-kernel.md` |
| `Y-star-gov/ystar/governance/` | `eng-governance` | `.claude/agents/eng-governance.md` |
| `Y-star-gov/ystar/adapters/` | `eng-platform` | `.claude/agents/eng-platform.md` |
| `Y-star-gov/ystar/rules/` | `eng-governance` | `.claude/agents/eng-governance.md` |
| `Y-star-gov/ystar/domains/` | `eng-domains` | `.claude/agents/eng-domains.md` |
| `Y-star-gov/tests/` | (same as source scope) | infer from test path |
| `scripts/` | `eng-platform` | `.claude/agents/eng-platform.md` |
| `scripts/hook_*` | `eng-platform` | `.claude/agents/eng-platform.md` |
| `governance/` | `eng-governance` | `.claude/agents/eng-governance.md` |
| `content/` | `cmo` | `.claude/agents/cmo.md` |
| `reports/cto/` | `cto` | (doc-only: CTO writes directly) |
| `reports/ceo/` | `ceo` | (doc-only: CEO writes directly) |
| `marketing/` | `cmo` | `.claude/agents/cmo.md` |
| `sales/` | `cso` | `.claude/agents/cso.md` |
| `finance/` | `cfo` | `.claude/agents/cfo.md` |

**Ambiguity resolution**: If scope spans multiple prefixes (e.g., `Y-star-gov/ystar/adapters/hook.py,scripts/hook_wrapper.py`), the daemon picks the agent whose scope contains the FIRST listed file. If still ambiguous, default to `eng-kernel` (broadest engineering scope).

**Trust gating**: Only agents with trust score >= 1.0 (from session history) are auto-spawned for P0 tasks. New/untrusted agents get P2 tasks first. Trust score is a simple counter: `completed_tasks / (completed_tasks + stalled_tasks + failed_tasks)`. Initial trust = 0.5 (neutral). This prevents a stalling agent from being repeatedly auto-spawned for the same task.

### B.4 Daemon Core Logic (dispatch_auto_spawner.py)

```python
# Pseudocode -- implementation by eng-platform
import json, time
from pathlib import Path

BOARD_PATH = Path("governance/dispatch_board.json")
PENDING_PATH = Path("scripts/.pending_spawns.json")
POLL_INTERVAL_EVENTS = 5  # check after every N CIEU events (not wallclock)

def scan_and_queue():
    board = json.loads(BOARD_PATH.read_text())
    pending = _load_pending()
    
    for task in board["tasks"]:
        if task["status"] in ("open", "posted"):
            # Not yet claimed -- auto-claim + queue spawn
            agent_type = infer_agent_type(task["scope"])
            if agent_type and not _already_pending(task["atomic_id"], pending):
                pending.append({
                    "atomic_id": task["atomic_id"],
                    "agent_type": agent_type,
                    "prompt_template": _build_prompt(task),
                    "queued_at": time.time(),
                    "retries": 0,
                })
        
        elif task["status"] == "claimed" and _is_stale(task):
            # Claimed but stale (>600s no receipt) -- re-queue
            agent_type = infer_agent_type(task["scope"])
            if agent_type and not _already_pending(task["atomic_id"], pending):
                pending.append({
                    "atomic_id": task["atomic_id"],
                    "agent_type": agent_type,
                    "prompt_template": _build_prompt(task),
                    "queued_at": time.time(),
                    "retries": task.get("retries", 0) + 1,
                })
    
    PENDING_PATH.write_text(json.dumps(pending, indent=2))

def _is_stale(task):
    """Task is stale if claimed > 600s ago with no completion."""
    if not task.get("claimed_at"):
        return False
    claimed_ts = _parse_iso(task["claimed_at"])
    return time.time() - claimed_ts > 600 and not task.get("completed_at")

def _build_prompt(task):
    """Build the subagent spawn prompt from task card."""
    return f"""## Task: {task['atomic_id']}
{task['description']}

Scope: {task['scope']}
Priority: {task['urgency']}

BOOT CONTEXT: Read .czl_subgoals.json + git log -10 before starting.
SCOPE GUARD: No git commit/push/add/reset. Write only to files listed in scope.
RECEIPT: Return 5-tuple (Y*/Xt/U/Yt+1/Rt+1) on completion.
"""
```

### B.5 Hook Integration (hook_wrapper.py reads .pending_spawns.json)

The hook_wrapper.py PostToolUse handler checks for pending spawns after each CEO tool call:

```python
# In PostToolUse handler (after normal processing)
def _check_pending_spawns():
    pending_path = Path(REPO_ROOT) / "scripts" / ".pending_spawns.json"
    if not pending_path.exists():
        return None
    
    pending = json.loads(pending_path.read_text())
    if not pending:
        return None
    
    # Take first pending spawn
    spawn = pending[0]
    remaining = pending[1:]
    pending_path.write_text(json.dumps(remaining, indent=2))
    
    # Return Agent spawn instruction
    return {
        "action": "spawn_agent",
        "agent_type": spawn["agent_type"],
        "prompt": spawn["prompt_template"],
        "atomic_id": spawn["atomic_id"],
    }
```

**Critical constraint**: Claude Code's hook protocol does NOT support the hook spawning agents directly. The hook can only return allow/deny JSON. The actual Agent spawn must happen in the main conversation thread.

**Workaround -- INJECT-based auto-spawn trigger**:

Instead of the hook spawning agents, the PostToolUse hook INJECTs a high-priority message into the conversation:

```
[Y*gov AUTO-SPAWN] Task {atomic_id} is pending execution.
Agent type: {agent_type}
Action required: Spawn agent now.
Command: Agent("eng-kernel", "Execute task CZL-ARCH-14: ...")
```

Combined with ARCH-11c (reply-scan for action promises), this creates an obligation: if the CEO sees the AUTO-SPAWN inject and does NOT spawn the agent within the next 2 tool calls, the obligation engine blocks subsequent tool calls until the spawn happens.

**Future state** (post ARCH-11d GuidancePayload): The GuidancePayload dataclass includes `invoke_cmd` and `then_retry_original`. The auto-spawn could set `invoke_cmd` to the Agent spawn call, making it truly automatic via ARCH-11a's mandatory invoke mode.

### B.6 Failure Modes and Mitigations

| Failure Mode | Detection | Mitigation |
|---|---|---|
| **Daemon process dies** | No new entries in `.pending_spawns.json` despite open tasks on board | CIEU event `SPAWNER_HEARTBEAT` every 60s. Missing heartbeat > 5 min triggers CIEU `SPAWNER_DEAD` alert. Recovery: restart daemon via `governance_boot.sh` |
| **Claude Code ignores INJECT spawn guidance** | Agent does not issue Agent tool call within 2 tool_uses of seeing AUTO-SPAWN inject | ARCH-11b OmissionEngine creates obligation with TTL=3. Third tool_use without spawn = DENY + "must spawn pending agent first" |
| **Agent spawn stalls (600s watchdog)** | Task remains "claimed" with no receipt after 600s | Daemon marks task as stale (retry +1). Max 3 retries. After 3 failures: mark task as "blocked", emit CIEU `AUTO_SPAWN_EXHAUSTED`, escalate to CEO as P0 |
| **Concurrent spawns overwhelm context** | Multiple pending spawns queued simultaneously | Rate limit: max 1 pending spawn at a time. Daemon queues in FIFO. Next spawn only after current completes or times out |
| **Daemon writes corrupt JSON** | `.pending_spawns.json` not valid JSON | Atomic write pattern: write to `.pending_spawns.json.tmp`, rename. Reader uses `try/except` with empty-list fallback |
| **Scope inference wrong** | Task dispatched to wrong agent type | Agent's scope guard (from task card + AGENTS.md boundary) will cause enforcement DENY on out-of-scope file access. CIEU records the scope violation. Daemon re-queues with corrected agent type based on the DENY reason |

### B.7 Success Criteria

**The minimal viable test**: 

1. Post 1 new task to `dispatch_board.json` with status "open"
2. Daemon runs `scan_and_queue()` 
3. `.pending_spawns.json` contains 1 entry with correct `agent_type`
4. CEO runs any Bash command (e.g., `ls`)
5. PostToolUse hook reads pending, INJECTs auto-spawn guidance
6. CEO's next reply includes Agent spawn call (or ARCH-11a auto-invokes it)
7. Agent runs, writes completion receipt
8. `dispatch_board.json` task status updated to "completed"

**Wall-clock target**: From task post to agent spawn < 2 CEO tool_uses (< 30 seconds in practice).

---

## Part C: Relationship to Existing ARCH Tasks

### C.1 ARCH-14 REWRITE Extends ARCH-13 "Routing as Universal Solver"

ARCH-13 (doc task, in queue) argues that every chronic agent problem maps to a router rule `detector + executor` pair. ARCH-14 adds a new executor OUTPUT TYPE:

| ARCH Task | Router Decision | What Executor Does | Agent Must Act? |
|-----------|----------------|--------------------|----|
| ARCH-13 (theory) | any | (philosophy doc) | n/a |
| Existing DENY | `deny` | Block + return reason text | YES -- agent interprets text |
| ARCH-P1-c REDIRECT | `redirect` | Return FIX_COMMAND + THEN_RETRY | YES -- agent must run fix |
| ARCH-11a INVOKE | `invoke` | Hook auto-executes fix command | NO -- hook runs command |
| **ARCH-14 REWRITE** | `rewrite` | **Transform payload to compliant version + re-check + proceed** | **NO -- governance fixes it** |

**Progression**: DENY (agent interprets) -> REDIRECT (agent follows instructions) -> INVOKE (hook runs fix, agent retries) -> REWRITE (governance fixes payload, agent unaware). Each step reduces agent discretion and increases enforcement certainty. This is the trajectory Board identified: "不能靠自律."

**REWRITE is ARCH-13's strongest answer to chronic problems**:
- Legacy path usage? REWRITE (path-alias mode) -- agent never sees old path in response
- Missing NEXT guidance? REWRITE (next-action-append mode) -- every ALLOW includes what to do next
- BOM encoding errors? REWRITE (format-normalize mode) -- cleaned before enforcement checks

### C.2 ARCH-15 Auto-Spawn Makes ARCH-8 NEXT_ACTION Active

ARCH-8 adds a `next_action_inject` router rule at priority 50 that tells the agent what to do next. But ARCH-8 is **passive** -- it injects a hint into the ALLOW response. The agent must read and follow the hint.

ARCH-15 makes this **active**:

```
ARCH-8 alone:
  Tool call -> enforce -> ALLOW + "NEXT: work on CZL-ARCH-14"
  (agent may or may not follow)

ARCH-8 + ARCH-15:
  Tool call -> enforce -> ALLOW + "NEXT: work on CZL-ARCH-14"
  + daemon detects CZL-ARCH-14 is open on board
  + daemon writes pending spawn for eng-kernel
  + next tool call -> PostToolUse INJECTs "AUTO-SPAWN eng-kernel for CZL-ARCH-14"
  + ARCH-11b creates obligation: must spawn within 3 tool_uses
  (agent MUST follow -- obligation-enforced)
```

**The key insight**: ARCH-8 provides the intelligence (what should happen next). ARCH-15 provides the execution mechanism (making it happen). Together they close Board's "不空转" requirement with structural enforcement, not behavioral expectation.

### C.3 Dependency Graph

```
ARCH-13 (philosophy: routing solves everything)
    |
    +-- ARCH-14 (REWRITE: new decision type)
    |       |
    |       +-- Depends on: EnforceDecision enum (P1-c, DONE)
    |       +-- Depends on: RouterRegistry (P2-a, DONE)  
    |       +-- Depends on: ARCH-11d GuidancePayload (for structured rewrite output)
    |       +-- Depends on: ARCH-11a INVOKE (for DENY+auto-invoke fallback on hook)
    |
    +-- ARCH-15 (Auto-Spawn: board -> execution bridge)
            |
            +-- Depends on: dispatch_board.json schema (EXISTS)
            +-- Depends on: cto_dispatch_broker.py routing metadata (EXISTS)
            +-- Depends on: ARCH-11b OmissionEngine (for obligation enforcement)
            +-- Depends on: ARCH-8 NEXT_ACTION (for intelligence layer)
            +-- Optional: ARCH-11a INVOKE (for true auto-spawn without CEO relay)

ARCH-8 (NEXT_ACTION inject) -----> ARCH-15 uses as intelligence source
ARCH-11a (INVOKE) -----> ARCH-14 uses as fallback; ARCH-15 uses for auto-exec
ARCH-11b (OmissionEngine) -----> ARCH-15 uses for spawn obligation
ARCH-11d (GuidancePayload) -----> ARCH-14 uses for structured output
```

### C.4 Implementation Priority

Given Board's urgency and the dependency chain:

1. **ARCH-11d** (GuidancePayload dataclass) -- foundation, unblocks both ARCH-14 and ARCH-15
2. **ARCH-15** (Auto-Spawn Daemon) -- highest Board pain ("no one responds to whiteboard")
3. **ARCH-14** (REWRITE) -- powerful but requires more safety infrastructure
4. **ARCH-11a** (INVOKE) -- makes ARCH-15 truly automatic (CEO not in loop)
5. **ARCH-11b** (OmissionEngine obligation) -- makes ARCH-15 obligation-enforced

ARCH-15 can ship in a reduced form WITHOUT ARCH-11a/11b: the daemon queues spawns, the hook INJECTs guidance, and the CEO (or a behavioral norm) handles the actual Agent call. The obligation enforcement and auto-invoke can be layered on after.

ARCH-14 ships in two stages: Stage 1 with path-alias and format-normalize modes only (pure string transformations, no semantic changes). Stage 2 adds arg-injection and command-expand after the safety infrastructure (re-check, CIEU logging, learning hint injection) is battle-tested.

---

## Summary

Board identified two structural gaps:

1. **Governance advises but does not repair.** ARCH-14 REWRITE closes this by adding a new enforcement decision type that transforms non-compliant payloads to compliant ones, constrained by a 5-mode safe transformation whitelist and a re-check invariant. Industry precedent is strong (auto-formatters, service mesh auto-inject, SQL sanitization).

2. **Whiteboard tasks accumulate but no agent executes them.** ARCH-15 Auto-Spawn Daemon closes this by polling the dispatch board, inferring the correct agent type from scope, queuing spawn requests, and having the hook layer inject spawn obligations into the CEO's tool flow. Combined with ARCH-8 (intelligence) and ARCH-11b (obligation enforcement), this creates a closed loop from task posting to agent execution.

Both mechanisms maintain the 4-layer architecture from the master proposal:
- REWRITE is a Layer 3 (Routing) decision type, evaluated in the RouterRegistry, logged in Layer 1 (CIEU)
- Auto-Spawn is a Layer 3 workflow rule that uses Layer 4 (hook) for spawn triggering and Layer 1 (CIEU) for audit

Neither introduces new architectural layers or new external dependencies. Both are router rules that plug into the existing RouterRegistry infrastructure.

---

**CTO Ethan Wright**
**Y* Bridge Labs**
**2026-04-18**
