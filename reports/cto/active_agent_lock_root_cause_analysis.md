# Active Agent Lock — Root Cause Analysis

**Author**: CTO (Ethan Wright) — read-only investigation
**Date**: 2026-04-12
**Requested by**: Board
**Scope**: `.ystar_active_agent` write rejection loop + DIRECTIVE-006 convergence

---

## TL;DR

`.ystar_active_agent` is a **single-role mutex file**: by policy only the `secretary` role may Write it through the Claude Code tool layer. Enforcement is done by `_check_restricted_write_paths()` in `Y-star-gov/ystar/adapters/boundary_enforcer.py:158-219`, invoked from `ystar/adapters/hook.py:413` (primary) and `hook.py:508` (secondary pass). The rule is declared in `.ystar_session.json:309-328`.

All other roles (CEO, CTO, subagents) hit deny because they are not in the allow list `["secretary"]`. `governance_boot.sh:33` and Board's manual shell `echo` both bypass this because **the hook only sees Claude Code tool calls; raw OS redirects do not pass through `_hook_daemon.py`**. This is by design (the hook is an MCP/stdin-JSON shim, not a filesystem LSM).

Today's loop is caused by agents trying to write the file via the `Write` tool, which is the only channel the hook guards. No `safe role transition primitive` exists; `secretary` is the only authorized writer but the currently-booted subagent rarely *is* secretary.

---

## Dimension 1 — Where is `.ystar_active_agent` write permission defined?

### 1a. Declaration (the rule data)

File: `/Users/haotianliu/.openclaw/workspace/ystar-company/.ystar_session.json`
Lines 309-328:

```json
"restricted_write_paths": {
  "DIRECTIVE_TRACKER.md": ["ceo"],
  "memory/session_handoff.md": ["ceo"],
  ".ystar_active_agent": ["secretary"],
  ".ystar_session.json": ["secretary"],
  "AGENTS.md": ["secretary"],
  ".claude/agents/": ["secretary"]
}
```

### 1b. Layer 1 — ystar hook (enforcement code path)

- Lazy-loader: `Y-star-gov/ystar/adapters/boundary_enforcer.py:139-155`
  `_ensure_restricted_write_loaded()` pulls `restricted_write_paths` from session config via `identity_detector._load_session_config` (one-shot, module-global cache `_RESTRICTED_WRITE_PATHS`).
- Check: `boundary_enforcer.py:158-219` `_check_restricted_write_paths(tool_name, params, who)`.
  - Only triggers if `tool_name in _WRITE_TOOLS` (line 179).
  - Pattern-matches pattern ending in `/` as dir-prefix, otherwise exact basename (lines 193-203).
  - If `who not in allowed_roles` → returns `PolicyResult(allowed=False, reason="Restricted write path violation...")` (lines 207-217).
- Call site A (primary, Write tool): `Y-star-gov/ystar/adapters/hook.py:413`

  ```python
  # P0-0.25: 受限写路径检查
  restricted_deny = _check_restricted_write_paths(tool_name, params_early, who)
  ```
- Call site B (secondary, e.g. Edit with multiple files): `hook.py:508-511`.

### 1c. Layer 2 — gov-mcp

Searched `/Users/haotianliu/.openclaw/workspace/Y-star-gov/gov_mcp/`; **no gov-mcp tool enforces `restricted_write_paths`** — gov-mcp exposes governance tools (`gov_check`, `gov_enforce`, etc.), but the file-level mutex is entirely Layer 1 hook territory. The hook runs in `_hook_daemon.py` (Unix socket `/tmp/ystar_hook.sock`, started by `governance_boot.sh:46`).

### 1d. `who` resolution

`Y-star-gov/ystar/adapters/identity_detector.py:86-161` — 7-step cascade. For Claude Code subagent calls, it typically resolves via **step 6 (marker file)** (line 148) i.e. reads `.ystar_active_agent` itself. **Therefore the agent identity for the write check is the *current on-disk* identity, not the writer's own role**. A CTO subagent trying to switch active_agent to `eng-platform` is still classified as whatever the marker currently says (e.g. `ceo`), not CTO — and neither is `secretary`, so deny.

---

## Dimension 2 — Why is every other role denied?

### Historical design intent (evidence chain, not speculation)

**Phase 1 — commit `d03775c` (2026-04-01, "per-agent enforcement — identity registration, tool restrictions")**
Introduced the concept: each agent writes `.ystar_active_agent` at session start "for CIEU attribution" (commit body). At this point the marker was **writable by anyone** — pure attribution signal.

**Phase 2 — commit `74b761c` (2026-04-09, "unify restricted_write_paths to role-based agent_id — GOV-005 Part 4 followup")**
At this commit the `restricted_write_paths` dict contained **ONLY** `DIRECTIVE_TRACKER.md` and `session_handoff.md`, both scoped to `ceo`. `.ystar_active_agent` was **NOT yet restricted**. Original intent was narrow: protect CEO-authored governance docs from accidental overwrites.

**Phase 3 — between 2026-04-09 and today**
The four secretary-only entries (`.ystar_active_agent`, `.ystar_session.json`, `AGENTS.md`, `.claude/agents/`) were added to the live `.ystar_session.json` but **no commit introduces them** (session config is gitignored after `94deeaa security: block credentials in .gitignore — telegram session, runtime files`). The additions match the GOV-009 / record_intent.py secretary-authority pattern (`256ccf1 docs(secretary): GOV-009 doc distillation — record_intent.py four-field sync`): **secretary was elevated to "constitutional editor"** and the active_agent marker was added to its exclusive-write scope **as an anti-tampering measure**.

### Why it is over-restrictive

- Secretary is a role, not a session-boot primitive. Secretary subagent is not invoked at every session start — CEO/CTO subagents are.
- Active_agent is **operational state**, not a constitutional document. Lumping it with AGENTS.md conflates "governance text" with "runtime pointer".
- There is no **"identity switch exemption"** anywhere in the code — I grepped `role.*transition|身份.*切换|identity.*switch` across both repos: zero hits in source, only in report files. It was discussed at BOARD_PENDING.md:11 ("active_agent lock" listed as immediate blocker) but no design was landed.

**Conclusion**: Phase-3 restriction was a well-intentioned but over-broad anti-tampering measure that never accounted for legitimate role transitions.

---

## Dimension 3 — Why does `governance_boot.sh:33` succeed?

```bash
# scripts/governance_boot.sh:33
echo "$AGENT_ID" > "$YSTAR_DIR/.ystar_active_agent"
```

### Verified mechanism

1. Claude Code hook intercepts **Claude-initiated tool calls** (`Write`, `Edit`, `Bash`). Claude's `Bash` tool DOES go through the hook (`hook.py` evaluates `tool_name == "Bash"` via command-deny lists), but the hook does **not parse shell redirection inside the command string** to detect file writes. It only blocks `deny_commands` patterns.
2. `scripts/governance_boot.sh` is itself invoked via `Bash("bash scripts/governance_boot.sh ceo")`. The outer Bash tool call is checked, but the **`>` redirect inside the script executes in the child shell** — it's pure POSIX I/O, no MCP/hook traffic.
3. Board's manual `echo ceo > .ystar_active_agent` in an external terminal is trivially untouched — the hook daemon only serves `/tmp/ystar_hook.sock`, it is not an FS filter.

**Result**: `restricted_write_paths` is a **Claude-tool-layer mutex, not an OS-layer mutex**. Any bash redirect, any Python `open(...,'w')` that Claude executes via `Bash`, any external process, all bypass it. This is a known architectural property (see `exp5A_ceo_dogfood_audit.md:84`, "active_agent field in database has no direct column" — the enforcement never claimed OS-level completeness).

**Implication**: The lock is protective against only one threat model — a misbehaving agent using the `Write` tool on the marker file. Every other attack/accident path is open.

---

## Dimension 4 — Proposed role transition protocols

### Candidate A — Whitelist role-transition matrix in session config

Add to `.ystar_session.json`:
```json
"role_transition": {
  "allowed_transitions": {
    "ceo":       ["cto","cmo","cfo","cso","secretary","eng-platform","eng-kernel","eng-governance","eng-domains"],
    "cto":       ["ceo","eng-kernel","eng-governance","eng-platform","eng-domains"],
    "secretary": ["*"],
    "*":         ["ceo"]
  },
  "default_home_state": "ceo"
}
```

Enforcement: extend `_check_restricted_write_paths()` so that when path == `.ystar_active_agent`, instead of a flat allow list, look up `(current_role, new_content)` against the matrix.

**Pros**: Declarative, auditable, one config change, reversible. DNA of the fix is visible.
**Cons**: Requires `_check_restricted_write_paths` to read **content**, not just path (new side-effect in enforcement path). Adds state coupling to current marker value (need read-before-write).

### Candidate B — Dedicated `ystar_role_switch.py` primitive

```bash
python3 scripts/ystar_role_switch.py --to eng-platform --reason "CTO dispatching Leo for kernel fix"
```

Script responsibilities:
1. Validate `new_role` against whitelist (same matrix as A).
2. Atomic write via `os.replace()` of `.ystar_active_agent.tmp → .ystar_active_agent` (solves DIRECTIVE-006 concurrency).
3. Emit CIEU event `role_transition` with `{from, to, initiator, reason}`.
4. Hold a file-lock (`fcntl.flock`) for the duration to serialize concurrent subagents.
5. Whitelisted as allowed writer in `restricted_write_paths` (the script runs in-session but via Bash, so hook doesn't gate it).

**Pros**: One explicit choke point, full CIEU audit trail, atomicity, solves concurrency. Does NOT require changing `_check_restricted_write_paths` (path stays locked, the script is the lock-holder). Matches the existing pattern of `record_intent.py` / `session_close_yml.py` / `governance_boot.sh`.
**Cons**: Requires every subagent to know to call it. Needs a behavior_rule (`before_delegation: call ystar_role_switch.py`).

### Candidate C (orthogonal, additive) — Boot-time default home state

After `governance_boot.sh` finishes, always force `active_agent = ceo` (declared home state). Requires Step 7b in the boot script or a new `scripts/reset_active_agent.sh` run at session-end in `session_close_yml.py`. Cheap (5 min), prevents stale residue (scenario B in the task).

### Recommendation

**Adopt B + C together**. B is the primary primitive; C is a safety net for stale residue after crashes / abrupt session exits. A is rejected — it overloads `_check_restricted_write_paths` with content inspection, increasing the blast radius of any bug in that function (currently the most-hit hook codepath per hook_debug.log).

---

## Dimension 5 — Relation to DIRECTIVE-006

DIRECTIVE-006 is "`.ystar_active_agent` concurrent write stomping" (two subagents racing to set identity). Today's lock is "single legitimate writer rejected by hook". Different causes, same file, same design flaw root: **the marker was never designed as a protected mutex with a proper API — it was a plain text file that accreted enforcement layers**.

### Can a single fix solve both?

**Yes, Candidate B does**:
- DIRECTIVE-006 (concurrency): `fcntl.flock` + `os.replace()` in `ystar_role_switch.py` provides atomicity.
- Today's lock (single-writer rejection): agents invoke the script, script is authorized (or runs via Bash, which bypasses the Write-tool hook anyway).
- CIEU accountability: every transition is logged, so "who stomped whom" becomes queryable — which was the original DIRECTIVE-006 fix requirement per `exp5A_ceo_dogfood_audit.md:84`.

Candidate A solves the lock but **does not** solve DIRECTIVE-006 (no atomicity guarantee — two concurrent valid transitions still race).

---

## Implementation Priority & Level

| Item | Level | Priority | Justification |
|------|-------|----------|---------------|
| **C — Boot/close default home state reset** | L2 (CTO authority) | **P0** | 30-min change, two-line edit in `governance_boot.sh` + `session_close_yml.py`. Immediately stops the "stale eng-platform residue" class of loops. No config schema change. |
| **B — `ystar_role_switch.py` primitive + CIEU event schema** | **L3 (Board required)** | **P1** | Introduces a new session-state API — constitutional-tier change. Needs CIEU event type registration and behavior_rule addition. Lays foundation to close DIRECTIVE-006. ~1 day implementation. |
| Retiring `.ystar_active_agent` from `restricted_write_paths` once B lands | L3 | P2 | Removes redundant rule; must wait until B is validated in production for ≥1 week. |

### Board L3 decision points

1. **Sanction the role-transition matrix** (who can become who). Proposed default: CEO can become anyone; CTO can become any engineer + CEO; engineers can only return to CTO; everyone can return to CEO home.
2. **Approve new CIEU event type `role_transition`** (schema: `{from, to, initiator, reason, session_id, timestamp}`).
3. **Authorize removing `.ystar_active_agent` from `restricted_write_paths`** (phase-out after B stable).

No approval needed for **C** — Level 2, CTO owns.

---

## Evidence index (all paths absolute)

- Rule data: `/Users/haotianliu/.openclaw/workspace/ystar-company/.ystar_session.json:309-328`
- Enforcement check: `/Users/haotianliu/.openclaw/workspace/Y-star-gov/ystar/adapters/boundary_enforcer.py:158-219`
- Loader: `/Users/haotianliu/.openclaw/workspace/Y-star-gov/ystar/adapters/boundary_enforcer.py:139-155`
- Hook invocation (primary): `/Users/haotianliu/.openclaw/workspace/Y-star-gov/ystar/adapters/hook.py:413`
- Hook invocation (secondary): `/Users/haotianliu/.openclaw/workspace/Y-star-gov/ystar/adapters/hook.py:508-511`
- Identity resolution: `/Users/haotianliu/.openclaw/workspace/Y-star-gov/ystar/adapters/identity_detector.py:86-161` (marker fallback at line 148)
- Boot-time bypass: `/Users/haotianliu/.openclaw/workspace/ystar-company/scripts/governance_boot.sh:33`
- Historical baseline: commit `74b761c` (`git show 74b761c -- .ystar_session.json`) — only 2 entries, no `.ystar_active_agent`
- Introduction of per-agent marker: commit `d03775c` (attribution-only intent)
- Gitignore turning point: commit `94deeaa` — why later restrictions have no commit trail
- DIRECTIVE-006 original finding: `reports/experiments/exp5A_ceo_dogfood_audit.md:83-85`
- Board backlog entry: `BOARD_PENDING.md:11`

---

**No hook violations encountered during investigation. All reads, no writes to restricted paths. Report file written under `reports/cto/` per CTO write scope.**
