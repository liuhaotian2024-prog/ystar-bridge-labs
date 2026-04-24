---
Audience: CEO (Aiden) + CTO (Ethan) + Board (Haotian) — dispatch_board.json lifecycle reviewers. Secondary: Wave-2 engineering owners (Leo/Maya/Ryan/Jordan) consulting why their tasks were re-routed.
Research basis: `python3 scripts/dispatch_board.py pending` output @ 2026-04-24 09:20 EST (27 items, OVERDUE spans 98h→9h); structural-root-cause diagnosis in scripts/engineer_task_subscriber.py:46-48 + AGENTS.md must_dispatch_via_cto rule (today-session joint Ethan+CEO finding); per-item prompt content cross-referenced with MEMORY feedback keys (梦境机制 L4 gap / enforce-as-router thesis / CTO subagent cannot async orchestrate); Y-star-gov/ filesystem verify (ls returns no such file at workspace root — sibling-workspace-only per AMENDMENT-004).
Synthesis: 27 items were never going to be picked up because the white-board subscriber channel is structurally broken (sub-agent cannot be Agent-spawned by subscriber; must_dispatch_via_cto creates the deadlock). Archive-or-reroute is the ONLY honest disposition. Of 27: 9 still carry independent value → re-route to CEO-direct Agent-spawn via wave2_active_spawnlist.md; 4 are superseded by live/later work; 2 are atomic dupes of siblings; 12 are obsolete (path-invalidated by Y-star-gov sibling-workspace refactor, or upstream-cascade-blocked, or scope-mis-routed, or need CEO pre-scoping).
Purpose: Enable CEO to (a) stop waiting on white-board for these 27 items, (b) Agent-spawn the 9 STILL-RELEVANT items directly in the next CEO session turn, (c) point Wave-2 Guard+Guide Refactor scope at the structural subscriber fix so dispatch_board stops accumulating ghost items, (d) prevent Leo from double-spawning on CZL-SPAWN-PPID-MARKER-FIX (already-live Wave-1.5 work).
---

# Dispatch Board Triage Archive — 2026-04-24

**Author**: Samantha Lin (Secretary)
**Maturity Tag**: [L3] shipped triage artifact
**Source**: `python3 scripts/dispatch_board.py pending` @ 2026-04-24 09:20 EST — 27 overdue items
**Structural root cause diagnosed**: `scripts/engineer_task_subscriber.py:46-48` cannot Agent-spawn + `must_dispatch_via_cto` rule deadlock. White-board channel is structurally broken; every item on it was destined to OVERDUE regardless of merit.
**Archive decision rule**: archive = CLOSED on white-board, no longer waiting for subscriber pickup. STILL RELEVANT items are documented in `reports/secretary/wave2_active_spawnlist.md` for CEO-direct Agent-spawn re-route.

---

## Triage Summary

| Verdict          | Count | Disposition                                             |
| ---------------- | ----- | ------------------------------------------------------- |
| STILL RELEVANT   | 9     | → `wave2_active_spawnlist.md` for CEO-direct Agent spawn |
| SUPERSEDED       | 4     | Archive here, reference succeeding item                  |
| DUPE             | 2     | Archive here, merge ref to canonical                     |
| OBSOLETE         | 12    | Archive here, environment changed or unrecoverable       |
| **TOTAL**        | **27**| 100% classified                                         |

---

## Section A — SUPERSEDED (4 items)

### A.1 `CZL-CEO-RULES-REGISTRY-CLOSE-GAP` (V1)
- **Posted**: 2026-04-22T15:26:09Z (~46h overdue)
- **Routed**: eng-governance
- **Succeeded by**: `CZL-CEO-RULES-REGISTRY-V3-EXISTING-ASSETS-FIRST` (V3 prompt header explicitly "SUPERSEDES V1+V2")
- **Verdict**: SUPERSEDED — V3 captures delta-correct engineer assignments (125 tu not 285)
- **Archive reason**: V1 asks for 285 tu work that Board caught was actually 125 tu after 2026-04 existing-assets audit

### A.2 `CZL-CEO-RULES-REGISTRY-CLOSE-GAP-V2-FRONTIER-TECH`
- **Posted**: 2026-04-22T16:16:58Z (~45h overdue)
- **Routed**: eng-governance
- **Succeeded by**: `CZL-CEO-RULES-REGISTRY-V3-EXISTING-ASSETS-FIRST` (V3 prompt header: "SUPERSEDES V1+V2")
- **Verdict**: SUPERSEDED — explicit successor in prompt
- **Archive reason**: V2 asked 285 tu; V3 corrected to 125 tu after Board catch that frontier-tech already largely built (AMENDMENT-015 Layer 3.1/3.4 + EXP-6 wisdom_extractor_v2)

### A.3 `CZL-SPAWN-PPID-MARKER-FIX`
- **Posted**: 2026-04-21T19:37:47Z (~66h overdue)
- **Routed**: eng-kernel
- **Succeeded by**: Wave-1.5 active work stream (Leo currently modifying `hook_wrapper.py` marker precedence + casing + `override_roles`; same 5-point fix set requested in prompt)
- **Verdict**: SUPERSEDED — CEO P1 context confirmed "Leo Wave-1.5 正修, 可 supersede"
- **Archive reason**: Duplicate of live engineering; keeping on white-board creates coordination confusion + merge conflict risk

### A.4 `INC-2026-04-23-ITEM-9`
- **Posted**: 2026-04-24T04:33:45Z (~9h overdue)
- **Routed**: eng-governance
- **Succeeded by**: `INC-2026-04-23-ITEM-5` (kernel import audit — same `ystar.governance.forget_guard ModuleNotFoundError` family; prompt explicitly says "same family as Item 5")
- **Verdict**: SUPERSEDED by Item 5 import-path resolution; break-glass spec delta moved to wave2_active_spawnlist as P1 follow-up
- **Archive reason**: Import fix path shared; standalone spawn wastes budget

---

## Section B — DUPE (2 items)

### B.1 `CZL-BOARD-HONESTY-G2`
- **Posted**: 2026-04-22T13:10:07Z (~49h overdue)
- **Routed**: eng-platform
- **Dupe of**: `CZL-BOARD-HONESTY-G1` (prompt explicitly: "Shared hook file with G-1. Extend the G-1 Stop hook...")
- **Verdict**: DUPE — G2 is a feature inside G1 hook, not a separate spawn
- **Archive reason**: G1 delivery ships G2 automatically per shared-file spec; merged into G1 spawnlist entry

### B.2 `INC-2026-04-23-ITEM-4`
- **Posted**: 2026-04-24T04:14:38Z (~10h overdue)
- **Routed**: eng-cto-triage
- **Dupe of**: `INC-2026-04-23-ITEM-3` (both are forget_guard None.startswith / rule-def field errors; Item 4 is the RuntimeError spam caused by Item 3 root)
- **Verdict**: DUPE — Item 3 fix (None.startswith 1-line) resolves Item 4 RuntimeError spam as downstream effect
- **Archive reason**: Atomic root fix cascades; keep Item 3, drop Item 4

---

## Section C — OBSOLETE (12 items)

### C.1 `CZL-YSTAR-PIP-INSTALL-FIX`
- **Posted**: 2026-04-20T02:40:50Z (~107h overdue)
- **Routed**: eng-platform
- **Obsolete reason**: `Y-star-gov/` directory does not exist at workspace path (`ls Y-star-gov/pyproject.toml → No such file or directory`). Sibling workspace `/Users/haotianliu/.openclaw/workspace/Y-star-gov/` per AMENDMENT-004. Import-path rebuild duplicated by INC-2026-04-23-ITEM-5 egg-info rebuild scope.
- **Verdict**: OBSOLETE — scope path no longer valid in-tree; fix duplicated by Item 5

### C.2 `CZL-YSTAR-PRODUCT-BOUNDARY-DEHARDCODE`
- **Posted**: 2026-04-20T15:49:05Z (~94h overdue)
- **Routed**: eng-cto-triage
- **Obsolete reason**: Scope `Y-star-gov/ystar/,Y-star-gov/tests/` same path issue as C.1. Premise ("Required before any external product release") — no external product release queued; PyPI ship decision gated on CZL-GOV-MCP-ACTIVATE v0.4 sections which are themselves OBSOLETE (see C.3)
- **Verdict**: OBSOLETE — blocker for release that is not being pursued this cycle; re-post after path consolidation + release plan refresh

### C.3 `CZL-GOV-MCP-ACTIVATE`
- **Posted**: 2026-04-21T17:01:19Z (~69h overdue)
- **Routed**: eng-cto-triage
- **Obsolete reason**: Task is 6-phase massive (audit + test expansion + register + smoke + PyPI + decouple). Cannot run on white-board under current spawn deadlock. Requires CTO-level multi-engineer orchestration + Board approval for PyPI ship.
- **Verdict**: OBSOLETE as dispatch_board item — too large for subscriber model; needs CTO ruling + multi-wave breakdown

### C.4 `CZL-MISSING-WHO-I-AM-7-AGENTS`
- **Posted**: 2026-04-21T17:02:41Z (~69h overdue)
- **Routed**: eng-cto-triage (but prompt says "Owner Samantha-Secretary")
- **Obsolete reason**: Mis-routed to eng-cto-triage; owner is Secretary (me). Secretary-scope task, not engineering; will execute directly as Secretary duty after Wave-1.5 settles, not via dispatch_board subscriber
- **Verdict**: OBSOLETE on dispatch_board (wrong channel) — pulled into Secretary direct-execute queue

### C.5 `CZL-COMMISSION-UNIFY-STEP-1`
- **Posted**: 2026-04-22T13:39:33Z (~49h overdue)
- **Routed**: eng-governance
- **Obsolete reason**: Depends on `forget_guard.py` import being resolvable (`ystar.governance.forget_guard ModuleNotFoundError` per INC-2026-04-23-ITEM-5). Until Item 5 lands, Step 1 cannot be verified live-fire
- **Verdict**: OBSOLETE for now — blocked by upstream import family fix; re-issue via wave2 spawnlist after Item 5

### C.6 `CZL-COMMISSION-UNIFY-STEP-2`
- **Posted**: 2026-04-22T13:39:34Z (~49h overdue)
- **Routed**: eng-cto-triage
- **Obsolete reason**: Prompt explicitly "Depends on Step 1 wire" — cascade from C.5 OBSOLETE
- **Verdict**: OBSOLETE via upstream cascade

### C.7 `CZL-COMMISSION-UNIFY-STEP-3`
- **Posted**: 2026-04-22T13:39:34Z (~49h overdue)
- **Routed**: eng-kernel
- **Obsolete reason**: "Depends on Step 1 plus 2". Cascade from C.5 + C.6. Plus `Y-star-gov/ystar/adapters/boundary_enforcer.py` path issue (C.1 family)
- **Verdict**: OBSOLETE via cascade + path

### C.8 `CZL-BRAIN-FRONTIER-1-AIDEN-DREAM-PROMOTE`
- **Posted**: 2026-04-22T21:01:25Z (~41h overdue)
- **Routed**: eng-cto-triage
- **Obsolete reason**: Per MEMORY [梦境机制 L4 gap — propose-only]: Gate 2 DENY-all is the real blocker, NOT dryrun→live flip. Ryan 2026-04-23 already built `dream_auto_reviewer.py` to emit BRAIN_DREAM_DIFF_REVIEWED. This item's premise (flip plist) is superseded by the reviewer approach
- **Verdict**: OBSOLETE — wrong fix path; auto-reviewer is the real solution already in motion

### C.9 `CZL-BRAIN-FRONTIER-2-6D-COORD-POPULATE`
- **Posted**: 2026-04-22T21:01:25Z (~41h overdue)
- **Routed**: eng-governance
- **Obsolete reason**: Scope includes `Y-star-gov/ystar/governance/cieu_brain_bridge.py` — path issue (C.1 family). Plus brain.db population depends on aiden_dream LIVE (C.8 OBSOLETE cascade)
- **Verdict**: OBSOLETE via path + upstream cascade

### C.10 `CZL-BRAIN-FRONTIER-3-CROSS-ACTOR-BRAIN`
- **Posted**: 2026-04-22T21:01:25Z (~41h overdue)
- **Routed**: eng-governance
- **Obsolete reason**: Same path issue as C.9 (Y-star-gov/ystar/governance/*). Plus heuristic backfill of 18727 nodes from file_path is lossy; prefer live ingest going forward — re-scope needed
- **Verdict**: OBSOLETE via path + re-scope required

### C.11 `CZL-BRAIN-FRONTIER-4-ARCHIVAL-SLEEPGATE`
- **Posted**: 2026-04-22T21:01:25Z (~41h overdue)
- **Routed**: eng-cto-triage
- **Obsolete reason**: brain.db size (296MB at post time) has grown further; archival policy needs Board M-triangle review (active forgetting is a Board-level identity question, not engineering config)
- **Verdict**: OBSOLETE — needs CEO pre-scoping, not engineer direct

### C.12 `CZL-BRAIN-FRONTIER-5-DETECTOR-REGISTRY`
- **Posted**: 2026-04-22T21:01:25Z (~41h overdue)
- **Routed**: eng-cto-triage
- **Obsolete reason**: Depends on `governance_audit_unified.py` import chain from Y-star-gov/ystar. Same path-family cascade
- **Verdict**: OBSOLETE via import cascade

---

## Section D — STILL RELEVANT (9 items → wave2_active_spawnlist.md)

| ID                                               | Original owner  | P-level | Justification                                       |
| ------------------------------------------------ | --------------- | ------- | --------------------------------------------------- |
| CZL-BOARD-HONESTY-G1                             | eng-platform    | P0      | Board-facing honesty guardrail; independent value (includes G2 as feature) |
| CZL-OMISSION-UNIFY-LIVEFIRE                      | eng-governance  | P0      | M-2b symmetric validation of commission unification |
| CZL-CEO-RULES-REGISTRY-V3-EXISTING-ASSETS-FIRST  | eng-governance  | P0      | Canonical rule-registry closure (supersedes V1+V2)  |
| CZL-WAVE-5-RECEIPT-STRUCTURED-SCHEMA             | eng-kernel      | P1      | Structured receipt schema — defer Wave-2 but keep   |
| INC-2026-04-23-ITEM-3                            | eng-governance  | P0      | forget_guard None.startswith 1-line fix             |
| INC-2026-04-23-ITEM-1                            | eng-platform    | P1      | Ryan commit Board sed fix                           |
| INC-2026-04-23-ITEM-5                            | eng-kernel      | P0      | CZL Gate 1 import family audit (root for multiple)  |
| INC-2026-04-23-ITEM-6                            | eng-platform    | P0      | K9 Rescue Daemon v1 ship                            |
| INC-2026-04-23-ITEM-7                            | eng-kernel      | P1      | hook tmp/bak cleanup + chmod verify                 |

Details + re-route prompts in `reports/secretary/wave2_active_spawnlist.md`.

---

## Section E — Next Step

- **Samantha (Secretary)**: this archive is the record. No git commit (scope forbids).
- **CEO (Aiden)**: read `wave2_active_spawnlist.md`, Agent-spawn the 9 relevant items directly (bypass broken white-board subscriber).
- **Leo (kernel)**: Wave-1.5 PPID marker fix supersedes A.3 — do not double-spawn.
- **White-board channel**: until `engineer_task_subscriber.py:46-48` structural fix lands (Wave-2 Guard+Guide Refactor scope), do NOT post new items here. Use direct Agent spawn.

---

## Appendix — Classification Rationale

- **SUPERSEDED** = explicit successor item exists (by prompt wording or content overlap + later timestamp)
- **DUPE** = same-atom fix covered by another item in same wave
- **OBSOLETE** = environment / path / premise changed; re-posting required after restructure
- **STILL RELEVANT** = independent value + executable today + not covered by Wave-1/1.5 live work
