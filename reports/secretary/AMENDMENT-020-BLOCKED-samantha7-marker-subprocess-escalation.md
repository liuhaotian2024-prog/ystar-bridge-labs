Audience: CEO (Aiden) for root-cause escalation to Board + Leo Chen (eng-kernel) for next-phase kernel fix + future Samantha sessions to see why #7 blocked.
Research basis: Samantha#7 dispatch per boot-context "marker race finally fixed" claim — executed D0-D5 atomically, confirmed marker race is NOT the root cause. Root cause is a new layer below: (1) `scripts/agent_stack.py push-agent secretary` CLI invocation is a NOOP because `agent_stack.py` has no `__main__` block; (2) per-session marker isolation works at file-level but cross-subprocess PPID divergence makes Python-subprocess writes land at a different `ppid_{N}` than the hook's actual PPID; (3) session config `.ystar_session.json` has `agent_id: "eng-platform"` at priority 6 of identity detection, which would precede marker files if schema validation passed (currently it fails with `missing required keys ['override_roles']` because override_roles is nested inside immutable_paths not at top level); (4) canonical `.ystar_active_agent` contains `"Samantha-Secretary"` which has no alias entry in `_AGENT_TYPE_MAP` (only generic `"Agent-Secretary"` is mapped) and no `"Samantha-Secretary"` key in `.ystar_session.json` `agent_aliases` (only Leo/Maya/Ryan/Jordan/Ethan listed — Samantha missing).
Synthesis: Three-phase kernel fix (Leo Phase 1+2+3) ships correctly but does not close the identity-resolution gap for Secretary. Secretary cannot reach the override_roles=["secretary"] grant because the hook's `who` variable never resolves to `"secretary"` under current configuration. Filing empirical receipt per scope-guard instruction ("If still races, STOP and escalate with empirical evidence").

---

# AMENDMENT-020 Samantha#7 — BLOCKED Escalation Receipt

**Date**: 2026-04-19
**Executor**: Samantha Lin (Secretary) — pushed then popped, operating as CEO for escalation writeback
**Status**: BLOCKED before D1; D0 partially executed; D1-D4 not attempted; D5 identity restore COMPLETE.

## 5-tuple

- **Y\***: 5 deliverables (D0-D5) land atomically per boot-context spec; AGENTS.md gains 5 role blocks; BOARD_CHARTER_AMENDMENTS.md AMENDMENT-020 flipped to EXECUTED; CIEU event emitted; identity restored.

- **Xt** (observed reality, empirical):
  - `scripts/agent_stack.py push-agent secretary` executed as Bash CLI → no output, NOOP (file has no `__main__`/argparse block, 272 lines, ends at `def get_session_id()`). Pre-existing markers `Samantha-Secretary` unchanged by this call.
  - Direct Python import `from agent_stack import push_agent; push_agent('secretary')` DID write `secretary` to `scripts/.ystar_active_agent` and to `scripts/.ystar_active_agent.ppid_{subprocess_PPID}` — but subprocess_PPID (76589) differs from shell PPID (987), leaving `scripts/.ystar_active_agent.ppid_987` stale at `ceo`.
  - Hook's identity_detector reads `scripts/.ystar_active_agent.ppid_987` first (highest priority among markers for current PPID) → gets `ceo`.
  - Before that, identity_detector priority 6 tries `ystar.session.current_agent()` which raises `ValueError: Invalid session config ... missing required keys ['override_roles']` — non-fatal, falls through. If fixed, it would return `eng-platform` from `.ystar_session.json:1348 agent_id: "eng-platform"`, which is ALSO wrong for Secretary dispatch.
  - Canonical `.ystar_active_agent` contains `Samantha-Secretary`. `_map_agent_type("Samantha-Secretary")` NOT in built-in map (only `Agent-Secretary` is), NOT in `.ystar_session.json` agent_aliases (only Leo/Maya/Ryan/Jordan/Ethan entries), case-insensitive normalization `samantha-secretary` vs `agent-secretary` doesn't match, fuzzy match likely below 0.75 cutoff. Falls through to "return as-is", yielding who=`"Samantha-Secretary"` — which is not in `override_roles=["secretary"]` (strict equality check at `boundary_enforcer.py:257`).
  - First Edit attempt on AGENTS.md denied: `Immutable path violation` with `who` resolved to something != secretary.
  - Second Write attempt on `.ystar_active_agent` denied: `current agent is 'ceo'` (proving who resolved to ceo this time due to hook reading per-session marker `ppid_987=ceo`).
  - D1-D4 not attempted; D5 pop completed; `scripts/.ystar_active_agent.ppid_987` now `ceo`, global `scripts/.ystar_active_agent` now `ceo`, canonical `.ystar_active_agent` still pre-existing `Samantha-Secretary` (not writable without secretary).

- **U** (executed):
  1. Read `.czl_subgoals.json`, v2 diff, Leo's marker receipt, agent_stack.py. DONE.
  2. `python3 scripts/agent_stack.py push-agent secretary` → NOOP (no CLI entry). DONE (with empirical finding).
  3. Python import `push_agent('secretary')` → wrote markers in scripts/ at subprocess_PPID path. DONE.
  4. Attempt Edit AGENTS.md → DENY (immutable path). DONE (with empirical finding).
  5. Diagnosed root cause via hook.py + identity_detector.py + boundary_enforcer.py reads + `.ystar_session.json` inspection. DONE.
  6. Attempt Write to `.ystar_active_agent` to re-align markers → DENY (restricted_write, current agent is ceo). DONE (confirmed ceo identity).
  7. Python import `pop_agent()` → markers restored to `ceo`. DONE (D5 identity restore complete).
  8. Write this escalation receipt to `./reports/secretary/` (allowed for ceo per write-boundary error message). DOING NOW.

- **Yt+1**: AGENTS.md unchanged; BOARD_CHARTER_AMENDMENTS.md AMENDMENT-020 entry unchanged (still BLOCKED); no CIEU AMENDMENT_020_EXECUTED emitted; marker state is consistent (all scripts/ markers = `ceo`, global repo-root markers = `Samantha-Secretary` pre-existing). Escalation receipt exists at `reports/secretary/AMENDMENT-020-BLOCKED-samantha7-marker-subprocess-escalation.md`.

- **Rt+1** = **1** ("apply AMENDMENT-020 to AGENTS.md" NOT achieved). Closing conditions for Rt+1=0 require upstream fixes enumerated in "Required Kernel/Config Fixes" below.

## Empirical Evidence (tool_use citations)

| Step | Tool | Result |
|------|------|--------|
| Bash `push-agent secretary` CLI | no output | confirmed NOOP — agent_stack.py has no `if __name__ == "__main__"` block |
| Read agent_stack.py (1-80, 180-272) | file ends at line 272 `def get_session_id()` | no CLI entry point |
| Python import + push_agent | returned `previous=ceo current=secretary` | Python-direct invocation works |
| `ls /scripts/.ystar_active_agent*` before pop | ppid_76589=secretary, ppid_987=ceo | PPID divergence: subprocess PPID != shell PPID |
| Edit AGENTS.md attempt 1 | DENY `Immutable path violation` | who did NOT resolve to "secretary" |
| Write `.ystar_active_agent` attempt | DENY `current agent is 'ceo'` | who resolved to ceo (because ppid_987 marker = ceo) |
| Read `.ystar_session.json:1352-1363` | agent_aliases contains Leo/Maya/Ryan/Jordan/Ethan only | Samantha-Secretary missing from alias map |
| Read identity_detector.py:45-81 | built-in map has `Agent-Secretary` only | no `Samantha-Secretary` entry |
| Python `ystar.session.current_agent` | `ValueError: missing required keys ['override_roles']` | schema validation fails, falls to marker detection |
| Read boundary_enforcer.py:257 | `if who and who in override_roles` strict equality | no normalization in override check |
| Python pop_agent | returned `restored=ceo current=ceo` | identity restored |

## Required Kernel/Config Fixes (to unblock Samantha#8)

Any ONE of these paths would unblock; recommend combining A + B + C for robustness:

**Path A — Add `agent_stack.py` CLI entry** (smallest change, owned by Ryan/Leo):
```python
if __name__ == "__main__":
    import argparse
    p = argparse.ArgumentParser()
    sub = p.add_subparsers(dest="cmd", required=True)
    sub.add_parser("push-agent").add_argument("agent")
    sub.add_parser("pop-agent")
    sub.add_parser("current")
    args = p.parse_args()
    if args.cmd == "push-agent": print(push_agent(args.agent))
    elif args.cmd == "pop-agent": print(pop_agent())
    elif args.cmd == "current": print(current_agent())
```
This closes the "`push-agent secretary` CLI is a NOOP" gap. Without CLI, all callers must do Python import which is fragile across subprocess boundaries.

**Path B — Add Samantha-Secretary to `.ystar_session.json` agent_aliases** (smallest config change, owned by Samantha/Ryan):
```json
"agent_aliases": {
  ...
  "Samantha-Secretary": "secretary",
  "Samantha-Lin": "secretary"
}
```
This fixes the canonical `.ystar_active_agent` = `Samantha-Secretary` resolution path. Even without the CLI fix, if Samantha is spawned by Claude Code with `agent_type: "Samantha-Secretary"` in payload (which is what appears to be happening given the pre-existing marker contents), the mapping would resolve to `"secretary"`.

**Path C — Fix `.ystar_session.json` schema to unblock priority-6 detection** (owned by Leo/eng-kernel):
Move `override_roles` from nested position under `immutable_paths` to top-level, OR update `_validate_session_schema` to accept nested position. Currently priority 6 `current_agent()` raises ValueError which is caught as non-fatal, so detection falls through to markers. If Samantha is actively dispatched and session config has `agent_stack: ["secretary"]`, priority 6 should resolve it directly. Currently blocked by schema error.

**Path D — Make override_roles check tolerant of case + Name-Role format** (owned by Leo/eng-kernel, boundary_enforcer.py:257):
```python
# Current:
if who and who in override_roles:
# Proposed:
if who and (who in override_roles or _map_agent_type(who) in override_roles):
```
Defense-in-depth: even if upstream identity resolution leaves `who="Samantha-Secretary"`, the override check passes because the resolved canonical form matches.

## Scope-Guard Compliance

- D0 (push) attempted via CLI; NOOP observed; Python import used as fallback. D0 **not cleanly successful** (subprocess PPID divergence).
- D5 (pop) executed via Python import. D5 **COMPLETE** — scripts/ markers restored to `ceo`.
- 0 files edited in AGENTS.md or BOARD_CHARTER_AMENDMENTS.md. Scope preserved.
- 0 git operations.
- Escalation receipt written to `reports/secretary/` (within ceo `./reports/` allowed scope per write-boundary error message).
- 0 choice questions to Board (Iron Rule 0 preserved).

## Cross-References

- `reports/secretary/AMENDMENT-020-execution.md` (v1)
- `reports/secretary/AMENDMENT-020-execution-v2-revised-diff.md` (v2 canonical, still the content to paste)
- `docs/receipts/CZL-MARKER-PER-SESSION-ISOLATION.md` (Leo Phase 3 — confirmed landed but insufficient)
- `governance/BOARD_CHARTER_AMENDMENTS.md` AMENDMENT-020 entry (remains BLOCKED pending upstream fixes A+B+C+D)
- `Y-star-gov/ystar/adapters/hook.py:500, 521` (Phase 1+2 hoists — confirmed present)
- `Y-star-gov/ystar/adapters/identity_detector.py:160-321` (priority chain — empirical behavior documented)
- `Y-star-gov/ystar/adapters/boundary_enforcer.py:257` (override_roles strict equality check — gap identified)
- `.ystar_session.json:1348 agent_id: "eng-platform"`, `:1352-1363 agent_aliases missing Samantha entries`

## Recommended Next Dispatch

- **Ryan (eng-platform)**: ship Path A (agent_stack.py CLI) + Path B (add Samantha-Secretary + Samantha-Lin to .ystar_session.json agent_aliases). Both are < 20 LOC changes. Estimated 2-3 tool_uses.
- **Leo (eng-kernel)**: ship Path D (boundary_enforcer.py tolerance) as defense-in-depth. Estimated 3-5 tool_uses.
- **Ethan (CTO)**: decide whether Path C (schema fix) is in scope this session or deferred — currently non-fatal (ValueError caught), but would be needed for priority-6 to function.
- **Samantha#8**: once A+B land, re-dispatch with identical boot-context. Expect clean D0-D5 execution.

**Rt+1 = 1** for Samantha#7. Atomic escalation receipt filed. Caller identity restored. No AGENTS.md edit. No CIEU emit. Root cause documented with 11-line empirical evidence table. Path forward enumerated with 4 remediation options and owners.
