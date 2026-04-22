# Whiteboard Backlog Triage 2026-04-21

**Audience**: Board (Haotian Liu), CEO (Aiden), CTO self-reference for dispatch planning
**Research basis**: Full scan of scripts/.pending_spawns.jsonl (115 lines, 93 unique after dedup) cross-referenced against governance/dispatch_board.json (36 completed, 84 claimed, 2 blocked). Empirical dedup analysis, supersedence tracing, M Triangle alignment check per AMENDMENT-023.
**Synthesis**: 4-bucket classification (RETIRE/MERGE/SPAWN-NOW/DEFER-P2) for every unique pending card. Test artifacts and completed-but-lingering cards retired. Superseded cards merged into live work. Remaining cards sorted by M Triangle alignment and mainline criticality.
**Purpose**: Unblock the 94-card overdue governance gap. Root cause: CZL-SUBSCRIBER-SPAWN-BRIDGE (subscriber cannot truly spawn sub-agents, cards accumulate). This triage clears the queue for manual dispatch or future bus-based auto-spawn.

## Summary

| Bucket | Count | Description |
|--------|-------|-------------|
| RETIRE | 16 | Test artifacts, dups, completed-still-pending, obsolete |
| MERGE | 17 | Subsumable into live milestone or sibling card |
| SPAWN-NOW | 20 | Mainline M Triangle, actionable now |
| DEFER-P2 | 40 | Valuable but non-critical, wait for natural window |

## Triage Table

| atomic_id | bucket | reason |
|-----------|--------|--------|
| CZL-996 | RETIRE | Test artifact (3 dups), no real work |
| CZL-997 | RETIRE | Test artifact (3 dups), no real work |
| CZL-998 | RETIRE | Test artifact (3 dups), no real work |
| CZL-999 | RETIRE | Test artifact (3 dups), no real work |
| CZL-DUP | RETIRE | Test residue stub (2 dups), completed in board |
| CZL-GOOD-POST | RETIRE | Test artifact (4 dups), bus publish test |
| CZL-TEST-GUIDE | RETIRE | Test artifact (3 dups), guide stub |
| T-P0 | RETIRE | Test artifact (4 dups), deadline test |
| T-P1 | RETIRE | Test artifact (4 dups), deadline test |
| T-INTEGRATION | RETIRE | Test artifact (4 dups), integration test stub |
| CZL-WHITEBOARD-WIPE-RCA | RETIRE | Already completed in dispatch_board |
| CZL-WHITEBOARD-BROKER-SUB-SAMEFIX | RETIRE | Already completed in dispatch_board |
| CZL-NORMALIZER-V3-ROUTE-FIX | RETIRE | Already completed in dispatch_board |
| CZL-KERNEL-OVERRIDE-PRE-FALLBACK-PHASE2 | RETIRE | Already completed in dispatch_board |
| CZL-MARKER-PER-SESSION-ISOLATION | RETIRE | Already completed in dispatch_board |
| CZL-BRAIN-AUTO-INGEST | RETIRE | Already completed in dispatch_board |
| CZL-ACTIVE-AGENT-PATH-MISMATCH | MERGE | Subsumes into CZL-SPAWN-PPID-MARKER-FIX (same lock-death family) |
| CZL-ACTIVE-AGENT-AUTO-RESTORE | MERGE | Subsumes into CZL-SPAWN-PPID-MARKER-FIX (agent restore = ppid fix) |
| CZL-AUTO-COMMIT-PUSH-CADENCE | MERGE | Superseded by CZL-AUTO-COMMIT-PUSH-IMPL + RESUSCITATE-M13 |
| CZL-BRAIN-3LOOP-LIVE | MERGE | Superseded by CZL-BRAIN-FULL-PIPELINE-WIRE (broader scope) |
| CZL-BRAIN-L2-WRITEBACK-IMPL | MERGE | Subsumes into CZL-BRAIN-FULL-PIPELINE-WIRE (L2 is subset) |
| CZL-BRAIN-ALL-INTERACTION-WRITEBACK | MERGE | Subsumes into CZL-BRAIN-FULL-PIPELINE-WIRE (all-hook writeback is subset) |
| CZL-AIDEN-L3-AUTO-LIVE | MERGE | Superseded by CZL-AIDEN-L3-AUTO-TRIGGER-WITH-CHECKPOINT (refined version) |
| CZL-NULL-CIEU-STORE-FIX | MERGE | Subsumes into CZL-NULLCIEUSTORE-FAIL-CLOSED (same root cause, broader fix) |
| CZL-ESCAPE-SEMANTIC-REVERSAL | MERGE | Subsumes into CZL-BIPARTITE-LOADER-IMPL (reversal is spec input to loader) |
| CZL-IDLE-PULSE-TYPEERROR-FIX | MERGE | Subsumes into CZL-OPS-GOV-INFO-SYNC (ops stability) |
| CZL-WIP-AUTOCOMMIT-RESUSCITATE | MERGE | Superseded by CZL-AUTO-COMMIT-PUSH-RESUSCITATE-M13 |
| CZL-GODVIEW-BRAIN-INGEST | MERGE | Subsumes into CZL-BRAIN-FULL-INGEST-COVERAGE (full ingest covers god-view) |
| CZL-AMENDMENT-022-CHARTER | MERGE | Charter text already in AGENTS.md; subsumes into METHODOLOGY-BOOT-INTEGRATION |
| CZL-FG-PROACTIVE-GODVIEW-CHECK | MERGE | Subsumes into CZL-FG-BLACKLIST-TO-WHITELIST-MIGRATION (FG overhaul) |
| CZL-FG-PROACTIVE-PRINCIPLE-TO-WHOIAM | MERGE | Subsumes into CZL-FG-BLACKLIST-TO-WHITELIST-MIGRATION (FG overhaul) |
| CZL-WHO-I-AM-MEMORY-CONSOLIDATION | MERGE | Subsumes into CZL-WHO-I-AM-SYSTEM-BINDING (binding is broader) |
| CZL-WHO-I-AM-EMPIRICAL-VALIDATION | MERGE | Subsumes into CZL-WHO-I-AM-SYSTEM-BINDING (validation is step within binding) |
| CZL-UNIFIED-BUS-RUNTIME-WIRE | SPAWN-NOW | M-2a+M-2b: unifies whiteboard+dispatch, fixes root cause of 94-card backlog |
| CZL-OPS-GOV-INFO-SYNC | SPAWN-NOW | M-2a: prevents governance misfires (today expect-word false positive) |
| CZL-SPAWN-PPID-MARKER-FIX | SPAWN-NOW | M-2a: lock-death #11 fix, blocks all sub-agent reliability |
| CZL-NULLCIEUSTORE-FAIL-CLOSED | SPAWN-NOW | M-2a: CIEU persistence fail-closed, prevents silent data loss |
| CZL-AUTO-COMMIT-PUSH-RESUSCITATE-M13 | SPAWN-NOW | M-1: 0 commits flowing to external repo, consultants see stale |
| CZL-AUTO-COMMIT-PUSH-IMPL | SPAWN-NOW | M-1: systematic auto-commit, complement to RESUSCITATE |
| CZL-YSTAR-PIP-INSTALL-FIX | SPAWN-NOW | M-3: blocks external user adoption, pip install broken |
| CZL-MUST-DISPATCH-REGRESSION-2026-04-21 | SPAWN-NOW | M-2a: enforcement regression, boot reports NOT ENFORCING |
| CZL-CONTINUOUS-MIRROR-RESUSCITATE | SPAWN-NOW | M-1: mirror stale since Apr 16, single point of failure |
| CZL-GOV-MCP-ACTIVATE | SPAWN-NOW | M-2a: v0.4 architecture blocker, Ethan identified as #1 |
| CZL-BRAIN-FULL-PIPELINE-WIRE | SPAWN-NOW | M-1: brain 13k nodes but pipeline unwired, Board empirical gap |
| CZL-METHODOLOGY-BOOT-INTEGRATION | SPAWN-NOW | M-2a: AMENDMENT-023/024 post-approval, must wire to boot |
| CZL-SUBSCRIBER-SPAWN-BRIDGE | SPAWN-NOW | M-2b: root cause of this 94-card backlog, must resolve |
| CZL-GEMMA-SPEED-TUNING-M14 | SPAWN-NOW | M-1+M-3: local-first speed, Board directive, research done |
| CZL-K9AUDIT-REVIVE | SPAWN-NOW | M-2a: K9 patrol 5 days dead, cross-validation broken |
| CZL-YSTAR-PRODUCT-BOUNDARY-DEHARDCODE | SPAWN-NOW | M-3: hardcoded paths block any external deployment |
| CZL-MISSING-WHO-I-AM-7-AGENTS | SPAWN-NOW | M-2b: 7/10 agents lack WHO_I_AM, omission gap |
| CZL-YSTAR-HARDCODED-AVOIDANCE-PHRASES | SPAWN-NOW | M-2a: hardcoded hook phrases, product code quality |
| CZL-AIDEN-L3-AUTO-TRIGGER-WITH-CHECKPOINT | SPAWN-NOW | M-1: L3 dream auto-trigger with safety checkpoint |
| CZL-CHARTER-FLOW-RULE-PILOT | SPAWN-NOW | M-2a: pilot validates router-rule methodology for 39 protocols |
| CZL-ETHAN-BRAIN-L3-DREAM-PARITY | DEFER-P2 | Nice-to-have, Aiden L3 should stabilize first |
| CZL-ETHAN-BRAIN-ARCH-SPEC | DEFER-P2 | Spec exists, impl card (IMPL-PHASE-1) covers work |
| CZL-ETHAN-BRAIN-IMPL-PHASE-1 | DEFER-P2 | Depends on brain pipeline wire landing first |
| CZL-BIPARTITE-LOADER-IMPL | DEFER-P2 | Brain algo, depends on pipeline wire + L2 landing |
| CZL-DOMINANCE-MONITOR | DEFER-P2 | Brain health monitor, needs L1/L2 live first |
| CZL-BRAIN-FULL-INGEST-COVERAGE | DEFER-P2 | Audit pass after pipeline wire lands |
| CZL-L3-GUARD-RAILS-IMPL | DEFER-P2 | Guard rails before L3 auto, but L3 trigger card exists |
| CZL-RYAN-BRAIN-IMPL | DEFER-P2 | Wave 5, depends on Ethan brain pattern stabilizing |
| CZL-LEO-BRAIN-IMPL | DEFER-P2 | Wave 5, depends on Ethan brain pattern stabilizing |
| CZL-MAYA-BRAIN-IMPL | DEFER-P2 | Wave 5, depends on Ethan brain pattern stabilizing |
| CZL-JORDAN-BRAIN-IMPL | DEFER-P2 | Wave 5, depends on Ethan brain pattern stabilizing |
| CZL-BRAIN-ERROR-CORRECTION-EXERCISE | DEFER-P2 | Brain training, needs pipeline live first |
| CZL-BRAIN-METACOGNITION-LEDGER | DEFER-P2 | Brain meta layer, needs L1/L2/L3 stable |
| CZL-BRAIN-BLOOM-LEVEL-TAGGING | DEFER-P2 | Brain enrichment, needs stable pipeline |
| CZL-BRAIN-AUTO-EXTRACT-EDGES | DEFER-P2 | Brain graph extraction, needs ingest stable |
| CZL-WINDOWS-COMPAT-AUDIT | DEFER-P2 | Pre-release audit, not blocking current milestone |
| CZL-FIRST-SILICON-PERSON-VERIFICATION | DEFER-P2 | Narrative research, not blocking engineering |
| CZL-AIDEN-SELF-EDUCATION-SCHEDULER | DEFER-P2 | Self-education scaffolding, not blocking ops |
| CZL-MEETING-ROOM-PLATFORM-RULING | DEFER-P2 | Meeting room Phase 1, large scope, non-mainline |
| CZL-MEETING-ROOM-GUEST-INVITATION | DEFER-P2 | Meeting room Phase 1, depends on platform ruling |
| CZL-MEETING-ROOM-VOICE-VIDEO | DEFER-P2 | Meeting room Phase 1, depends on platform ruling |
| CZL-MEETING-ROOM-DIGITAL-HUMAN-INTEGRATION | DEFER-P2 | Meeting room Phase 1, depends on platform ruling |
| CZL-DREAM-OUT-OF-SESSION-ARCH | DEFER-P2 | Out-of-session dream, architectural, non-urgent |
| CZL-PARENT-SESSION-REGISTER-AS-ENTITY | DEFER-P2 | God-view, depends on OPS-GOV-INFO-SYNC landing |
| CZL-INTERVENTION-PULSE-FOR-PARENT | DEFER-P2 | God-view pulse, depends on entity registration |
| CZL-REPORT-ENGINE-CONTEXT-SUMMARY | DEFER-P2 | God-view summary, depends on entity registration |
| CZL-AMENDMENT-ENGINE-AUTO-PROPOSE | DEFER-P2 | God-view amendment auto, low frequency need |
| CZL-ADAPTIVE-RULE-TUNING-FOR-FG | DEFER-P2 | FG tuning, needs 90-day baseline per spec |
| CZL-ALL-AGENTS-REGISTER-AS-ENTITIES | DEFER-P2 | God-view extension, after parent registration |
| CZL-FG-BLACKLIST-TO-WHITELIST-MIGRATION | DEFER-P2 | Strategic FG overhaul, large scope, non-urgent |
| CZL-M-ALIGNMENT-FG-RULE | DEFER-P2 | FG rule addition, after methodology wires |
| CZL-METHODOLOGY-FG-RULE | DEFER-P2 | FG rule addition, after boot integration |
| CZL-WHO-I-AM-SYSTEM-BINDING | DEFER-P2 | Kernel-level binding, large scope change |
| CZL-EXTERNAL-TOOL-TRIAGE-REVIEW | DEFER-P2 | External tool review, awaiting CEO spec |
| CZL-GOVERNANCE-ROUND-TRIP-AUDIT | DEFER-P2 | Live-fire audit, run after SPAWN-NOW fixes land |
| CZL-K9-RESTORE-CROSS-VALIDATE | DEFER-P2 | K9 cross-validate, after K9AUDIT-REVIVE lands |
| CZL-CIEU-SCHEMA-TEXT-DRIFT-2ROW | DEFER-P2 | Only 2 rows affected, cosmetic fix |
| CZL-CIEU-SECOND-ORDER-SILENT-AUDIT | DEFER-P2 | Audit pass, run after NULLCIEUSTORE fix |
| CZL-AUTO-COMMIT-INTELLIGENT-FILTER | DEFER-P2 | Enhancement to auto-commit, after base lands |
| CZL-K9-SPEECH-GOVERNANCE-SWEEP | DEFER-P2 | Gated on K9AUDIT-REVIVE, sweep after patrol live |

## Root Cause: CZL-SUBSCRIBER-SPAWN-BRIDGE

The 94-card overdue backlog exists because the subscriber system can claim cards but cannot truly spawn sub-agents (Claude Code architecture limitation: nested sub-sub-agent blocking). Cards enter the queue via `dispatch_board.py post` but have no exit path. The SPAWN-NOW bucket above includes this card as a priority fix. Until resolved, CEO must manually read pending and dispatch via Agent calls.

## Counts Verification

- RETIRE: 16 (10 test artifacts + 6 completed-still-pending)
- MERGE: 17 (superseded or subsumed into live sibling)
- SPAWN-NOW: 20 (mainline M Triangle aligned, actionable)
- DEFER-P2: 40 (valuable, non-blocking, gated on dependencies)
- **Total unique cards triaged: 93**

Note: 115 lines in .pending_spawns.jsonl, 93 unique after dedup (22 duplicates from test runs and repeated posts). The `dispatch_board.py pending` command reported 94 because it counts raw lines with partial dedup. The authoritative deduped count is 93 unique cards, all triaged above.
