Audience: CEO (Aiden) for sub-agent dispatch; Engineers (Leo/Maya/Ryan/Samantha) for task execution
Research basis: INC-2026-04-23 incident report, Board sed fix, CTO root cause analysis of 4 bugs, Iron Rule 3-channel protocol
Synthesis: 7 task cards derived from 9-point audit; Items #1-#2 done by CTO directly, Items #3-#9 require engineer dispatch
Purpose: Enable CEO to spawn sub-agents with precise scope, acceptance criteria, and safety constraints for each remaining audit item

# INC-2026-04-23 Task Cards (Items #3-#9)

Written by CTO (Ethan Wright) for CEO to dispatch via sub-agent spawn.
Governance hook blocked `.claude/tasks/` writes (CTO sub-agent resolved as "ceo").
Task specs are consolidated here; CEO can copy to `.claude/tasks/` or reference directly in dispatch prompts.

---

## Item #3 — Bug 3: FORGET_GUARD None.startswith 1-line fix

- **Owner**: eng-governance (Maya Patel)
- **Priority**: P0
- **Tool uses budget**: 8
- **No git push**: true
- **Paths allowlist**: `scripts/forget_guard.py`, `scripts/tests/test_forget_guard*.py`
- **Incident ref**: `reports/incidents/2026-04-23-hook-fail-closed-deadlock.md`

### Context
`tool_input.get("file_path")` returns None when the key is absent. Code calls `.startswith()` directly on the result without null-checking. Fail-open (exception caught) but masks real errors in hook_debug.log.

### Acceptance Criteria
- [ ] Find the `.startswith()` call on potentially-None `file_path` in forget_guard.py
- [ ] Add `or ""` default or explicit None guard before the `.startswith()` call
- [ ] Write/update a pytest that passes `tool_input={}` (no file_path key) and verifies no crash
- [ ] `python3 -m pytest` on the touched test file passes
- [ ] No files outside paths_allowlist modified

### Scope Guard
- NO git commit / git push / git add / git reset
- Write ONLY to paths in allowlist above

---

## Item #4 — Bug 4: article_11_board_offline_30m obligation rule fields

- **Owner**: eng-kernel (Leo Chen) or eng-governance (Maya Patel)
- **Priority**: P1
- **Tool uses budget**: 10
- **No git push**: true
- **Paths allowlist**: `scripts/`, Y-star-gov `ystar/`
- **Incident ref**: `reports/incidents/2026-04-23-hook-fail-closed-deadlock.md`

### Context
hook_debug.log spammed with RuntimeError from `article_11_board_offline_30m` obligation registration. Missing/malformed required fields. Not primary deadlock cause but produces log noise masking real errors.

### Acceptance Criteria
- [ ] Grep for `article_11_board_offline_30m` to find the rule definition
- [ ] Identify the missing/malformed fields causing RuntimeError
- [ ] Fix the rule definition to include all required obligation fields
- [ ] Verify no RuntimeError in a dry-run import
- [ ] No files outside allowlist modified

### Scope Guard
- NO git commit / git push / git add / git reset

---

## Item #5 — CZL Gate 1: Transitive import family audit

- **Owner**: eng-kernel (Leo Chen)
- **Priority**: P0
- **Tool uses budget**: 20
- **No git push**: true
- **Paths allowlist**: Y-star-gov `ystar/`, `scripts/`, `reports/`
- **Incident ref**: `reports/incidents/2026-04-23-hook-fail-closed-deadlock.md`

### Context
`validate_dispatch` has transitive import residue pulling in `ystar.governance.identity_detector` and `ystar.governance.forget_guard`, both raising ModuleNotFoundError. grep shows 0 live refs yet error persists (stale pip egg-info / dynamic imports / sys.path conflict).

### Acceptance Criteria
- [ ] `grep -rn "validate_dispatch"` in Y-star-gov — confirm 0 live refs or identify hidden refs
- [ ] `grep -rn "from ystar.governance"` — map full import graph
- [ ] Check for stale `.egg-info` / `__pycache__` / `dist-info` referencing deleted modules
- [ ] `python3 -c "import ystar.adapters.hook"` — verify no ModuleNotFoundError
- [ ] `python3 -c "import ystar.governance.identity_detector"` — verify or identify breakage
- [ ] `python3 -c "import ystar.governance.forget_guard"` — verify or identify breakage
- [ ] If stale artifacts found: rm + `pip install -e .` rebuild
- [ ] Write findings to `reports/cto_import_audit_20260423.md`

### Scope Guard
- NO git commit / git push / git add / git reset

---

## Item #6 — K9 Rescue Daemon v1 ship

- **Owner**: eng-platform (Ryan Park)
- **Priority**: P0
- **Tool uses budget**: 40
- **No git push**: true
- **Paths allowlist**: `scripts/k9_rescue_daemon.py`, `scripts/k9_rescue_actions.py`, `scripts/com.ystar.k9rescue.plist`, `scripts/tests/test_k9_rescue*.py`, `reports/`
- **Incident ref**: `reports/incidents/2026-04-23-hook-fail-closed-deadlock.md`
- **Iron Rule ref**: `reports/ceo/iron_rule_incident_response_3channel_20260423.md`

### 5 Design Principles (Board-ratified)
1. Physical isolation: launchd independent service
2. Zero governance dependency: must NOT import ystar.* or touch CIEU DB
3. Whitelist-driven: hardcoded action IDs only
4. FIFO single-direction: agent writes to `/tmp/ystar_rescue_fifo`, daemon reads
5. Auditable: independent rescue-chain Merkle log

### v1 Whitelist (R-001 through R-007)
| ID | Action | Command |
|---|---|---|
| R-001 | pycache clear | `find scripts/ -name '__pycache__' -exec rm -rf {} +` |
| R-002 | pkill hook | `pkill -f hook_wrapper.py` |
| R-003 | import check | `python3 -c "import ystar.adapters.hook; print('OK')"` |
| R-004 | ps grep | `ps aux \| grep -E 'ystar\|hook_wrapper\|gov-mcp'` |
| R-005 | dedupe heartbeat | remove duplicate `.session_booted` / `.session_call_count` |
| R-006 | read active_agent | `cat .ystar_active_agent` (read-only) |
| R-007 | kill specific pid | `kill <pid>` (pid must match ystar/hook process) |

### Acceptance Criteria
- [ ] `k9_rescue_daemon.py`: FIFO listener loop
- [ ] `k9_rescue_actions.py`: hardcoded action map R-001..R-007
- [ ] `com.ystar.k9rescue.plist`: launchd service definition
- [ ] Merkle audit log
- [ ] R-007 validates PID belongs to ystar/hook process before kill
- [ ] No shell=True in subprocess calls
- [ ] pytest unit + integration tests

### Scope Guard
- NO git commit / git push / git add / git reset
- NO imports from ystar.* in daemon code

---

## Item #7 — hook.py.tmp/.bak cleanup + hook_wrapper.py chmod

- **Owner**: eng-platform (Ryan Park)
- **Priority**: P1
- **Tool uses budget**: 5
- **No git push**: true
- **Paths allowlist**: `scripts/`, Y-star-gov `ystar/adapters/`

### Acceptance Criteria
- [ ] `find scripts/ -name "*.tmp" -o -name "*.bak"` — list and remove
- [ ] `find Y-star-gov/ystar/adapters/ -name "*.tmp" -o -name "*.bak"` — same
- [ ] `ls -la scripts/hook_wrapper.py` — verify executable bit; chmod +x if needed
- [ ] Report findings

### Scope Guard
- NO git commit / git push / git add / git reset
- Only delete .tmp/.bak files

---

## Item #8 — priority_brief.md refresh (106h stale)

- **Owner**: secretary (Samantha Lin)
- **Priority**: P1
- **Tool uses budget**: 15
- **No git push**: true
- **Paths allowlist**: `reports/priority_brief.md`, `memory/`

### Acceptance Criteria
- [ ] Read current priority_brief.md
- [ ] Read incident and Iron Rule docs
- [ ] Update with: INC-2026-04-23 status, K9 Daemon P0, 9-point audit progress, test count
- [ ] Timestamp the update

### Scope Guard
- NO git commit / git push / git add / git reset

---

## Item #9 — ForgetGuard CEO-bypass + ystar.governance.forget_guard ModuleNotFoundError

- **Owner**: eng-kernel (Leo) or eng-governance (Maya)
- **Priority**: P0
- **Tool uses budget**: 15
- **No git push**: true
- **Paths allowlist**: Y-star-gov `ystar/governance/`, `scripts/forget_guard.py`, `scripts/tests/`

### Context
Two related issues:
1. `from ystar.governance.forget_guard import ...` fails at runtime (transitive import family)
2. CEO needs emergency break-glass write access during lock-death

### Acceptance Criteria
- [ ] `python3 -c "from ystar.governance.forget_guard import ForgetGuard"` — identify exact error
- [ ] Fix import chain
- [ ] Design CEO break-glass bypass: when `.k9_rescue_mode` flag exists OR 3+ consecutive DENY for CEO in 5min, auto-escalate CEO write scope
- [ ] pytest for clean import
- [ ] pytest for CEO break-glass path

### Scope Guard
- NO git commit / git push / git add / git reset
