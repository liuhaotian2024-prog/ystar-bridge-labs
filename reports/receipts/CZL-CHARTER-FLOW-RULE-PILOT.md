Audience: CEO (Aiden), CTO (Ethan) for P2-d follow-up scoping, Board for governance coverage audit progress tracking.
Research basis: RouterRegistry API (commit 3c7c295, router_registry.py), BOARD_CHARTER_AMENDMENTS.md header (Board 2026-04-10 flow), CEO governance_coverage_audit_v1 Section 2-3 (charter amendment flow gap row), Ethan CZL-P2-resume-receipt P2-d conditional ruling (3-rule proving batch).
Synthesis: Charter amendment flow is now the first governance protocol migrated from prose to machine-enforced router rule. RULE-CHARTER-001 detects non-secretary writes to charter files and returns REDIRECT with fix_command pointing to Samantha-Secretary. 31/31 tests pass, live-fire smoke confirms correct REDIRECT decision. This proves the methodology for migrating the remaining 39 protocols in CZL-P2-d.
Purpose: Close CZL-CHARTER-FLOW-RULE-PILOT atomic; provide baseline evidence for CZL-P2-d batch migration; update CEO governance coverage audit charter row from "Partial" to "LIVE (router rule)".

# CZL-CHARTER-FLOW-RULE-PILOT Receipt

**Author**: Maya Patel (eng-governance)
**Date**: 2026-04-19
**Status**: COMPLETE (Rt+1 = 0)

---

## CIEU 5-Tuple

- **Y***: Charter amendment flow is machine-enforced -- wrong-role AGENTS.md edit gets REDIRECTED to Samantha-Secretary in real-time, not blocked post-hoc
- **Xt**: Flow documented in 3 prose files (BOARD_CHARTER_AMENDMENTS.md, AGENTS.md:941, feedback memory), no router rule; CEO routed AGENTS.md edit to Ethan (wrong role) today without detection
- **U**: 3 files created/edited (see Artifacts below), 31 pytest cases, live-fire smoke
- **Yt+1**: CEO simulated wrong-role attempt and saw REDIRECT with correct fix_command + injected_context; baseline for next protocol migrations
- **Rt+1**: 0 -- rule ships, 31/31 tests pass, smoke produces expected REDIRECT decision

---

## Artifacts

### 1. NEW: `Y-star-gov/ystar/governance/rules/charter_amendment_flow.py` (175 lines)

Router rule RULE-CHARTER-001 implementing:
- **Detector**: Matches Write/Edit/NotebookEdit targeting AGENTS.md, BOARD_CHARTER_AMENDMENTS.md, or .claude/agents/*.md where actor is NOT secretary. Also detects Agent spawn targeting charter edits by non-secretary roles.
- **Executor**: Returns `RouterResult(decision="redirect")` with:
  - `fix_command`: Agent spawn command for Samantha-Secretary
  - `injected_context`: Full charter amendment flow (Board 2026-04-10 header)
  - `args`: attempted_tool, attempted_file, violating_agent metadata
- **Priority**: 1000 (constitutional)
- **Rule ID**: RULE-CHARTER-001
- **CIEU event**: CHARTER_FLOW_REDIRECT

### 2. EDITED: `Y-star-gov/ystar/governance/router_registry.py` (+18 lines)

- Added `_governance_rules_dir()` helper to locate `ystar/governance/rules/`
- Added `load_governance_rules()` public API for explicit loading
- Modified `get_default_registry()` to auto-load governance rules on first creation
- Added `load_governance_rules` to `__all__`

### 3. NEW: `Y-star-gov/tests/governance/test_charter_flow_rule.py` (31 tests)

| Test Class | Count | Description |
|---|---|---|
| TestRuleStructure | 4 | Rule ID, priority, metadata, callables |
| TestSecretaryAllowed | 4 | Secretary/Samantha editing charter files -> no fire |
| TestCEORedirect | 4 | CEO editing AGENTS.md -> REDIRECT with fix_command |
| TestCTORedirect | 2 | CTO editing BOARD_CHARTER_AMENDMENTS.md -> REDIRECT |
| TestEngineerRedirect | 2 | Engineer editing .claude/agents/*.md -> REDIRECT |
| TestBoundaryNoFire | 5 | Non-charter files, Read tool, Bash tool -> no fire |
| TestAgentSpawnRedirect | 2 | CEO spawning Ethan to edit charter -> REDIRECT |
| TestAgentSpawnSamanthaAllowed | 2 | CEO spawning Samantha -> no fire |
| TestEdgeCases | 6 | Empty payload, missing keys, case sensitivity |

### 4. NEW: `Y-star-gov/ystar/governance/rules/__init__.py` (12 lines)

Package init for governance-layer router rules.

---

## Test Output

```
31 passed in 0.13s
```

Pre-existing router registry tests: 42 passed, 1 pre-existing failure (`test_all_seven_decisions` expects 7 decisions but REWRITE added 8th -- documented in CZL-P2-resume-receipt as known gap, not caused by this PR).

---

## Live-Fire Smoke Log

```
=== LIVE-FIRE SMOKE: CEO tries to Edit AGENTS.md ===

Matching rules: 1
  - RULE-CHARTER-001 (priority=1000)

Decision: redirect
Rule ID: RULE-CHARTER-001
Execution time: 0.00ms
Message: CHARTER FLOW VIOLATION: ceo tried to Edit AGENTS.md...

fix_command:
  Agent(subagent_type='Samantha-Secretary', prompt='Charter amendment requested...')

injected_context contains BOARD_CHARTER_AMENDMENTS header: True
fix_command contains Samantha-Secretary: True

CIEU event type from metadata: CHARTER_FLOW_REDIRECT
Rule authority: Board charter amendment flow (2026-04-10)

Secretary edit AGENTS.md - matching rules: 0 (expected 0)
CEO edit src/main.py - matching rules: 0 (expected 0)

=== SMOKE TEST COMPLETE ===

AUTO-LOAD VERIFIED: governance/rules/ is loaded on first get_default_registry() call
```

---

## Design Decisions

1. **Used .py instead of .rule.yaml**: The task spec mentioned YAML but `load_rules_dir()` only supports `.py` files with `RULES = [RouterRule(...)]` module-level lists. Creating a YAML parser would be scope creep and diverge from Ethan's P2-a ruling. The .py format provides the same declarative benefits with full Python expressiveness for detectors.

2. **Priority 1000 (constitutional)**: Charter amendment flow is constitutional authority (Board-approved process). Per RouterRule convention, 1000+ is constitutional.

3. **Auto-load in get_default_registry()**: Instead of requiring every caller to manually load governance rules, the default registry auto-loads from `ystar/governance/rules/` on first creation. This is idempotent (already-registered rules skipped) and ensures the charter rule is always active.

4. **Agent spawn detection**: Beyond direct Write/Edit, the detector catches CEO spawning non-secretary agents with charter-edit intent in the prompt. This covers the exact failure from today's session (CEO routed to Ethan instead of Samantha).

---

## Scope Compliance

- Touched exactly 4 files (3 new + 1 edit) in Y-star-gov only
- NO git commit, NO git push
- Single rule only -- did NOT start migrating other protocols
- Honored RouterRule/RouterResult/IngressRequest contracts per ARCH-17
