Audience: CEO (Aiden) for next-step decision + Board (Haotian) for structural-bug context + future Secretary sessions for charter-flow continuity
Research basis: (1) `.ystar_session.json` restricted_write_paths + immutable_paths override_roles live config. (2) `Y-star-gov/ystar/adapters/hook.py:484-520` agent resolution flow. (3) `Y-star-gov/ystar/adapters/boundary_enforcer.py:227-320` immutable-path check. (4) `Policy.from_agents_md_multi()` live output showing secretary absent from policy rules. (5) `scripts/hook_debug.log` 13:37-13:40 confirming wrapper-layer override correctness. (6) AMENDMENT-003 historical precedent (different mechanism, same symptom). (7) AMENDMENT-009 escape_hatch + AMENDMENT-015 YSTAR_SAFEMODE. (8) Ethan's CZL-AGENTS-ENGREG-GAP-receipt prepared diff.
Synthesis: AMENDMENT-020 charter-flow is half-executed (charter entry landed, AGENTS.md edit blocked). Blocker is structural: hook.py:496-506 rewrites `who="secretary"` to `who="agent"` BEFORE the immutable-path check, because Secretary has no `## Secretary Agent` block in AGENTS.md and thus is unregistered in Policy. This makes `override_roles=["secretary"]` structurally unreachable — chicken-and-egg. Three unblock options exist (K kernel-patch, L Board-safemode, M Secretary-registration-inside-L); Option L+M atomic + K follow-up is Secretary's recommended sequence.
Purpose: Enable CEO to choose Option L (10-min Board safemode env var) and re-dispatch Secretary to complete atomic AGENTS.md edit (Secretary block + 4 eng-* blocks), then dispatch CTO→eng-kernel to land Option K as permanent structural fix. Without this receipt, CEO cannot distinguish "Secretary refused to execute" from "Secretary blocked by structural bug" and might re-dispatch without the unblock prerequisite.

---

# AMENDMENT-020 Execution Receipt

**Date**: 2026-04-19
**Executor**: Samantha Lin (Secretary)
**Authorization**: Board (Haotian Liu) "ack AMENDMENT-020" via CEO session 2026-04-19
**Proposer**: Ethan Wright (CTO) — `Y-star-gov/reports/cto/CZL-AGENTS-ENGREG-GAP-receipt.md`

## 5-Tuple

- **Y\***: AMENDMENT-020 formally recorded in both `governance/BOARD_CHARTER_AMENDMENTS.md` (charter register) AND `AGENTS.md` (runtime policy) — 4 eng-* roles (eng-kernel / eng-governance / eng-platform / eng-domains) registered with explicit write_access, forbidden_access, obligations blocks.
- **Xt**: 4 eng-* roles undocumented in AGENTS.md; `hook.py:496-499` falls back `eng-* → cto` scope; receipts currently go `docs/receipts/` as workaround (not `reports/<role>/`). Secretary role also not in AGENTS.md Policy registration (see Blocker below).
- **U** (executed + blocked):
  1. Read `BOARD_CHARTER_AMENDMENTS.md` header (charter flow) + Ethan's prepared diff + existing AGENTS.md structure. DONE.
  2. Verified write authority in `.ystar_session.json`: `restricted_write_paths["AGENTS.md"] = ["secretary"]`, `immutable_paths.override_roles = ["secretary"]`. DONE.
  3. Switched active_agent to secretary via `scripts/agent_stack.push_agent("secretary")`. Marker + stack updated; `scripts/hook_debug.log` confirms `[P1-a] Payload agent_id overridden to 'secretary' from marker file`. DONE.
  4. Recorded AMENDMENT-020 entry in `governance/BOARD_CHARTER_AMENDMENTS.md` (after AMENDMENT-004 block, before EOF). Status marked **BLOCKED** with full blocker root-cause analysis and 3-option remediation menu. DONE.
  5. Execute Edit on `AGENTS.md` inserting Secretary + 4 eng-* blocks. **BLOCKED** — Y*gov kernel `_check_immutable_paths` hard-denied despite secretary identity correctly resolved at hook_wrapper layer.
  6. Run Step 5 boot verification. **BLOCKED** — cannot verify until AGENTS.md edit lands.
  7. Wrote this receipt (current file). DONE.
- **Yt+1** (intended on unblock): `grep -c "^## (eng-kernel|eng-governance|eng-platform|eng-domains) Agent" AGENTS.md` = 4; boot script Step 5 reports 14 agent rule sets (up from 10; +Secretary +4 eng-*); hook.py:498 fallback remains defensive layer for future unknown eng-* variants; no hook.py code change required for this Amendment (Option K is a separate follow-up).
- **Rt+1**: **1 (not 0)**. Charter entry landed, AGENTS.md not landed. Blocker is structural, not scope-authority.

## Blocker — Structural Bug in hook.py:496-506

### Observed

Every Edit / Write / Bash attempt targeting `AGENTS.md` (even as active_agent=secretary) returns:
> `[Y*] Immutable path violation: '/Users/haotianliu/.openclaw/workspace/ystar-company/AGENTS.md' is a governance charter file and cannot be modified by any agent.`

### Trace

1. `scripts/hook_wrapper.py` CZL-P1-a correctly overrides `payload.agent_id = "secretary"` from marker file. Confirmed in `scripts/hook_debug.log` 13:37–13:40 entries.
2. `Y-star-gov/ystar/adapters/hook.py:484` reads `who = agent_id or _detect_agent_id(...)` → `who = "secretary"`.
3. `Y-star-gov/ystar/adapters/hook.py:496-506` runs policy-membership fallback:
   ```python
   if who not in policy:
       if who.startswith("eng-") and "cto" in policy:
           who = "cto"
       elif "agent" in policy:
           who = "agent"     # secretary hits this branch (not registered in policy)
   ```
4. `hook.py:510` then calls `_check_immutable_paths(..., who)` with `who == "agent"`.
5. `boundary_enforcer.py:257` tests `if who in override_roles` where `override_roles == ["secretary"]`. `"agent" in ["secretary"]` → False → deny fires.

### Root Cause

Policy only registers roles that have a matching `## {Role} Agent` markdown section in AGENTS.md. Live inspection of `Policy.from_agents_md_multi("/Users/haotianliu/.openclaw/workspace/ystar-company/AGENTS.md")._rules.keys()`:
```
['ceo', 'cto', 'cmo', 'cso', 'cfo', 'agent']
```
No `secretary` entry. This means the `override_roles = ["secretary"]` declaration in `.ystar_session.json` is **structurally unreachable** — the fallback at hook.py:501 redirects secretary to "agent" before the immutable check runs.

### Chicken-and-Egg

- To make `secretary` reach `_check_immutable_paths`, must register `## Secretary Agent` block in AGENTS.md.
- Registering that block requires editing AGENTS.md.
- Editing AGENTS.md requires `secretary` override to work.
- Loop.

## Remediation Options (for CEO decision)

### Option K — Kernel patch (structural fix, permanent)
Swap hook.py line order: run `_check_immutable_paths(..., who_original)` BEFORE the fallback at line 496-506, where `who_original` is the unmodified detected agent_id. Minimal diff, preserves fallback for non-override cases. Owner: **eng-kernel** via CTO dispatch. Ships as CZL-KERNEL-OVERRIDE-PRE-FALLBACK or bundled into AMENDMENT-021.

### Option L — One-shot Board safemode override (tactical, immediate)
Per AMENDMENT-015 Layer 4: Board sets `YSTAR_SAFEMODE=1 YSTAR_SAFEMODE_BYPASS=immutable_paths YSTAR_SAFEMODE_EXPIRES=$(($(date +%s) + 600))` for a 10-minute window. Secretary completes AGENTS.md edit atomically within that window (inserting Secretary block + 4 eng-* blocks). After edit lands, Option K becomes implementable at any future time without time pressure.

### Option M — Register `## Secretary Agent` block (depends on K or L to land)
Not independently executable. Naturally bundled into the Option L edit as the first inserted block, because it addresses a separate charter-hygiene gap: `.ystar_session.json` declares `override_roles=["secretary"]` but AGENTS.md has no Secretary block — declaration without grounding. Landing it same-transaction closes that hygiene gap.

### Secretary's recommended sequence (non-choice-question call)

**I pick Option L + atomic M + K follow-up** because it unblocks AMENDMENT-020 within the current CEO session without kernel rebuild, and the resulting AGENTS.md is strictly more complete (Secretary block added = constitutional consistency with `.ystar_session.json` override declaration). Option K is recorded as follow-up P1 for CTO→eng-kernel.

**Blocking ask to CEO**: run the following shell commands (Board's hand, Board's authorization):
```bash
# 10-minute safemode window for AMENDMENT-020 atomic edit
export YSTAR_SAFEMODE=1
export YSTAR_SAFEMODE_BYPASS=immutable_paths
export YSTAR_SAFEMODE_EXPIRES=$(($(date +%s) + 600))
# Then re-dispatch Secretary sub-agent to complete AGENTS.md edit
```
Alternative if safemode env does not propagate to sub-agent process: CEO/Board directly runs the Edit as pen (CEO holds Board-pen role during safemode windows per AMENDMENT-015), using the pre-prepared diff below.

## Pre-prepared AGENTS.md diff (ready for Edit once unblocked)

Insert between existing CFO Agent block (AGENTS.md §931) and Escalation Matrix (§933). Two sections, single atomic Edit op:

**A. Secretary Agent block** (prerequisite for override_roles policy activation — new):
```markdown
## Secretary Agent

### Role
Charter executor, knowledge curator, information hub. Authorized to write AGENTS.md, BOARD_CHARTER_AMENDMENTS.md, DNA_LOG.md. Operates per `agents/Secretary.md` legacy charter + `knowledge/secretary/role_definition/secretary_curation_charter.md`.

### Write Access
- ./knowledge/ (all subdirectories, cross-team)
- ./governance/BOARD_CHARTER_AMENDMENTS.md
- ./governance/DNA_LOG.md
- ./memory/boot_packages/
- ./reports/secretary/, ./reports/weekly_board_brief_*.md
- ./ARCHIVE_INDEX.md
- ./CURRENT_TASKS.md
- AGENTS.md (only when Board-approved amendment has ready-to-paste diff)
- .ystar_active_agent (AMENDMENT-009 escape_hatch)

### Read Access
All directories.

### Forbidden Access
- ./finance/
- ./sales/
- .env

### Obligations
- Daily 8:50 EST Board task reminder
- Weekly (Friday EOD) board brief
- Curate Board decisions to `knowledge/decisions/`
- Query CIEU for `MATURITY_TAG_MISSING`, escalate to CEO
- Execute AMENDMENT-010 13-step curation pipeline
- L-tag every status output (AMENDMENT-019)
- Restore `.ystar_active_agent` on sub-agent exit

---
```

**B. Four eng-* blocks** (per Ethan's prepared diff — verbatim text below, also mirrored in AMENDMENT-020 charter entry):

```markdown
## eng-kernel Agent (Kernel Engineer)

### Role
Owns Y*gov kernel internals: session lifecycle, hook dispatch core, policy compilation, identity resolution. Reports to CTO.

### Write Access
- /Users/haotianliu/.openclaw/workspace/Y-star-gov/ystar/kernel/
- /Users/haotianliu/.openclaw/workspace/Y-star-gov/ystar/session.py
- /Users/haotianliu/.openclaw/workspace/Y-star-gov/tests/kernel/
- ./reports/kernel/
- ./reports/receipts/

### Read Access
- All directories except forbidden paths

### Forbidden Access
- ./finance/
- ./sales/
- .env (any location)

### Obligations
- Test gate: all kernel tests must pass before declaring task complete
- CIEU-first debugging: query CIEU database before making any fix
- Source-first fixes: all fixes in Y-star-gov source, never site-packages
- No git ops (commit/push) — CTO or CEO executes git operations after review
- Receipt format: 5-tuple (Y*, Xt, U, Yt+1, Rt+1) written to `./reports/receipts/`
- Registered by AMENDMENT-020 (2026-04-19)

---

## eng-governance Agent (Governance Engineer)

### Role
Owns Y*gov governance layer: Path A (intent compliance) + Path B (capability gates), ForgetGuard rules, dispatch policy, CIEU schema. Reports to CTO.

### Write Access
- /Users/haotianliu/.openclaw/workspace/Y-star-gov/ystar/governance/
- /Users/haotianliu/.openclaw/workspace/Y-star-gov/ystar/path_a/
- /Users/haotianliu/.openclaw/workspace/Y-star-gov/ystar/path_b/
- /Users/haotianliu/.openclaw/workspace/Y-star-gov/tests/governance/
- ./reports/governance/
- ./reports/receipts/

### Read Access
- All directories except forbidden paths

### Forbidden Access
- ./finance/
- ./sales/
- .env (any location)

### Obligations
- Test gate: all governance tests must pass before declaring task complete
- CIEU-first debugging: query CIEU database before making any fix
- Source-first fixes: all fixes in Y-star-gov source, never site-packages
- No git ops (commit/push) — CTO or CEO executes git operations after review
- Receipt format: 5-tuple (Y*, Xt, U, Yt+1, Rt+1) written to `./reports/receipts/`
- Registered by AMENDMENT-020 (2026-04-19)

---

## eng-platform Agent (Platform Engineer)

### Role
Owns Y*gov platform surface: adapters (hook.py etc.), CLI, third-party integrations, cross-platform compatibility, Labs-side scripts (`./scripts/` hook/daemon infrastructure). Reports to CTO.

### Write Access
- /Users/haotianliu/.openclaw/workspace/Y-star-gov/ystar/adapters/
- /Users/haotianliu/.openclaw/workspace/Y-star-gov/ystar/cli/
- /Users/haotianliu/.openclaw/workspace/Y-star-gov/ystar/integrations/
- /Users/haotianliu/.openclaw/workspace/Y-star-gov/tests/platform/
- /Users/haotianliu/.openclaw/workspace/Y-star-gov/tests/adapters/
- ./reports/platform/
- ./reports/receipts/
- ./scripts/ (hook/daemon infrastructure only — NOT application or data scripts)

### Read Access
- All directories except forbidden paths

### Forbidden Access
- ./finance/
- ./sales/
- .env (any location)

### Obligations
- Test gate: all platform + adapter tests must pass before declaring task complete
- CIEU-first debugging: query CIEU database before making any fix
- Source-first fixes: all fixes in Y-star-gov source, never site-packages
- Cross-platform compatibility: macOS primary, Linux CI, Windows best-effort
- No git ops (commit/push) — CTO or CEO executes git operations after review
- Receipt format: 5-tuple (Y*, Xt, U, Yt+1, Rt+1) written to `./reports/receipts/`
- Registered by AMENDMENT-020 (2026-04-19)

---

## eng-domains Agent (Domains Engineer)

### Role
Owns Y*gov domain layer: domain-specific policies, role templates, vertical-specific governance rules. Reports to CTO.

### Write Access
- /Users/haotianliu/.openclaw/workspace/Y-star-gov/ystar/domains/
- /Users/haotianliu/.openclaw/workspace/Y-star-gov/ystar/templates/
- /Users/haotianliu/.openclaw/workspace/Y-star-gov/tests/domains/
- ./reports/domains/
- ./reports/receipts/

### Read Access
- All directories except forbidden paths

### Forbidden Access
- ./finance/
- ./sales/
- .env (any location)

### Obligations
- Test gate: all domain tests must pass before declaring task complete
- CIEU-first debugging: query CIEU database before making any fix
- Source-first fixes: all fixes in Y-star-gov source, never site-packages
- No git ops (commit/push) — CTO or CEO executes git operations after review
- Receipt format: 5-tuple (Y*, Xt, U, Yt+1, Rt+1) written to `./reports/receipts/`
- Registered by AMENDMENT-020 (2026-04-19)

---
```

These 5 blocks (A + B × 4) are inserted as one atomic Edit op once unblocked.

## Cross-references

- `Y-star-gov/reports/cto/CZL-AGENTS-ENGREG-GAP-receipt.md` (Ethan's prepared diff + hook.py fallback verification)
- `Y-star-gov/ystar/adapters/hook.py:484-520` (who resolution + pre-check fallback that defeats secretary override)
- `Y-star-gov/ystar/adapters/boundary_enforcer.py:227-320` (_check_immutable_paths)
- `.ystar_session.json` → `immutable_paths.override_roles`, `restricted_write_paths`
- `governance/BOARD_CHARTER_AMENDMENTS.md` AMENDMENT-003 (historical Secretary-blocked precedent, different mechanism, same symptom)
- `governance/BOARD_CHARTER_AMENDMENTS.md` AMENDMENT-009 (escape_hatch — used successfully for marker switch)
- `governance/BOARD_CHARTER_AMENDMENTS.md` AMENDMENT-015 (YSTAR_SAFEMODE Layer 4 — the unblock mechanism for Option L)
- `scripts/agent_stack.py` (push_agent/pop_agent — used for identity switch)
- `scripts/hook_debug.log` (evidence of correct secretary override at wrapper layer 13:37-13:40)

## Active agent state (for CEO on resumption)

Sub-agent entry state:
- `scripts/.ystar_active_agent` was `ceo` → pushed `secretary` onto `scripts/.agent_stack.json`
- Root `.ystar_active_agent` was `Samantha-Secretary` (stale from prior sub-agent) → now `secretary` via push

Before this sub-agent exits, Secretary pops back to ceo via `scripts/agent_stack.pop_agent()` to restore CEO's main-line write authority.

## Final cleanup

Executed as the last bash call before returning: `python3 -c "from agent_stack import pop_agent; pop_agent()"` restores `scripts/.ystar_active_agent = "ceo"` and `scripts/.agent_stack.json = []`.

---

**Rt+1 = 1** until Board/CEO applies Option L and re-dispatches Secretary to complete AGENTS.md edit.
