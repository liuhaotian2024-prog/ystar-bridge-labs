# Y* Bridge Labs Engineering Backlog — 2026-04-22

Audience: CTO (Ethan) / engineering team (Leo / Maya / Ryan / Jordan) / Secretary (Samantha) / Board (Haotian Liu)
Research basis: Ethan 2026-04-21 whiteboard triage (93 unique cards, 4-bucket classification) reconsidered under Board 2026-04-22 catch "DEFER-P2 不是可以拖走不管"; today's ship audit (behavior_gov_engine + 11 launchd daemons + 6 commits + 5 OmissionEngine-tracked obligations)
Synthesis: Real engineering backlog requires P0/P1/P2 priority classification, per-item owner, deadline, and artifact-level acceptance criteria. Previous closures of DEFER-P2 bucket were wrong — "non-mainline but valuable" means "do later", not "delete". This backlog reopens all 40 DEFER-P2 as P2 tracked work, groups them by engineer scope, restores management cadence (sprint + weekly review + Board briefing).
Purpose: Single canonical engineering roadmap for next 6 weeks. Replaces scattered CZL pending queue. CEO owns backlog grooming + Board-facing synthesis. CTO owns sprint planning + engineer dispatch + delivery verification. Engineers claim + execute + produce artifact.

---

## Governance correction in this document

Before listing items: two errors being corrected here.

First, I (CEO) closed 40 DEFER-P2 cards on dispatch_board with a "DEFER-P2 reopen when natural window" receipt. That was wrong. "Defer to P2" means the work is real and valuable but non-critical; it should remain in the queue with lower priority, not be removed. This document reopens all 40 as P2 in the roadmap below. CTO + Secretary jointly approve a revert of the close in dispatch_board.json (scope belongs to Ethan, not me).

Second, I executed several engineering modules myself today (tier routing, Reflexion generator, AMENDMENT draft generator, CIEU listener, behavior gov engine, YAML rules, enforcement hook, reconcile script). These are Leo / Maya / Ryan work. I did them because sub-agents kept hitting Claude Code's stream watchdog during boot phase — but the correct response was "fix the dispatch protocol" or "split scope smaller", not "CEO executes". Going forward, new code written only by engineering team, routed via CTO. CEO verifies artifact after delivery.

---

## Priority definitions

**P0** — mainline blocker; without this M Triangle regresses; must be in-flight within 72h; Board escalation if blocked.

**P1** — mainline progress; required for current milestone; must be in-flight within 2 weeks.

**P2** — valuable but non-critical; can wait for natural window (between P0/P1 work, or when dependencies land).

Each item below has: owner / dependency / acceptance criterion (what artifact proves done) / deadline.

---

## P0 — blockers (within 7 days)

### P0-1 CZL-YSTAR-PIP-INSTALL-FIX
- **Owner**: Ryan-Platform
- **Why P0**: External user cannot install the product via pip; blocks all M-3 deployment validation. This is the product's front door.
- **Acceptance**: `pip install ystar` on a fresh Python 3.11 venv succeeds + `ystar doctor` returns green. CI matrix includes macOS + Linux.
- **Deadline**: 2026-04-29
- **Currently tracked in**: OmissionEngine obligations (ryan actor)

### P0-2 CZL-MISSING-WHO-I-AM-7-AGENTS
- **Owner**: Samantha-Secretary
- **Why P0**: 7 of 10 agents have no WHO_I_AM file; they fall back to generic role blurb; blocks M-1 Survivability per-agent persistence. Without WHO_I_AM, sub-agent identity drift is inevitable.
- **Acceptance**: `knowledge/{role}/wisdom/WHO_I_AM_{role}.md` exists for all 7 missing agents (Leo / Maya / Ryan / Jordan / Sofia / Zara / Marco). Each file has at minimum Section 0 (how to use) + Section 1 (quick lookup table). Live-fire: spawn each agent, verify hook_who_i_am_staleness injects real content.
- **Deadline**: 2026-04-29
- **Currently tracked in**: OmissionEngine (samantha actor)

### P0-3 CZL-GOV-MCP-ACTIVATE
- **Owner**: Ethan-CTO (architecture) + Ryan-Platform (impl)
- **Why P0**: gov-mcp daemon currently shows exit status 2 in launchctl list — it's loaded but crashing. Without gov-mcp, Claude Code cannot query governance state; the whole runtime governance proposition breaks.
- **Acceptance**: `launchctl list | grep gov_mcp` returns status 0. MCP tool registration succeeds (verified via a Claude Code session — `mcp__gov-mcp__*` tools loadable). At minimum `gov_health` tool callable returns a dict.
- **Deadline**: 2026-04-29 (Ethan ruling) + 2026-05-06 (Ryan impl)
- **Currently tracked in**: OmissionEngine (ethan actor)

---

## P1 — mainline progress (within 14 days)

### P1-1 CZL-SPAWN-PPID-MARKER-FIX (lock-death #11)
- **Owner**: Ryan-Platform
- **Why P1**: Sub-agent spawn doesn't update `.ystar_active_agent.ppid_<sub_pid>` marker, causing hook_wrapper to read parent's identity → sub-agent gets wrong write scope → write failures like Samantha couldn't edit `.claude/settings.json` today. Reliability blocker for all sub-agent dispatch.
- **Acceptance**: Spawn a Ryan-Platform sub-agent; inside the sub-agent's process, `scripts/.ystar_active_agent.ppid_<sub_pid>` exists and contains `ryan` (not `ceo`). 10/10 spawns pass. Pytest in `scripts/tests/test_ppid_marker_spawn.py`.
- **Deadline**: 2026-05-06
- **Currently tracked in**: OmissionEngine (ryan actor)

### P1-2 CZL-YSTAR-PRODUCT-BOUNDARY-DEHARDCODE
- **Owner**: Ryan-Platform
- **Why P1**: Hardcoded `/Users/haotianliu/` paths in product code block any deployment outside Aiden's machine. Must be config-ized before any external customer.
- **Acceptance**: `grep -r '/Users/haotianliu' Y-star-gov/ystar/ | wc -l` returns 0 (or all are test fixtures under `tests/`). Config via env var + `$HOME` expansion. Installs on a clean `/home/runner/` via CI matrix.
- **Deadline**: 2026-05-06
- **Currently tracked in**: OmissionEngine (ryan actor)

### P1-3 CZL-CHARTER-FLOW-RULE-PILOT
- **Owner**: Maya-Governance (semantics) + Ryan-Platform (router integration)
- **Why P1**: Proof-of-concept that behavior-governance rule-engine methodology (shipped today) can migrate 39 governance protocols from hand-coded hook logic into declarative YAML rules. Without this pilot, the engine is theoretical.
- **Acceptance**: 1 protocol (e.g. BOARD_CHARTER_AMENDMENTS flow) migrated from current hook logic into `scripts/behavior_gov_rules.yaml` DeadlineCheck or new handler type. Live-fire: simulated wrong-role AGENTS.md edit → engine returns block with fix_command. Pytest in `test_charter_flow_rule.py`.
- **Deadline**: 2026-05-06
- **Currently tracked in**: needs obligation registration (Ethan+Maya co-owner)

### P1-4 CZL-DIRECTIVE-PROGRESS-TAXONOMY (new, derived from gap)
- **Owner**: Samantha-Secretary + Ryan-Platform
- **Why P1**: Board asked today for "Board directive → OmissionEngine tracked_entity" auto-wiring. Requires new CIEU event types: DIRECTIVE_POSTED, DIRECTIVE_PROGRESS, GOAL_ARTIFACT_CREATED. Without these, the `goal_level_directive_untouched` rule in `behavior_gov_rules.yaml` stays disabled.
- **Acceptance**: CIEU event taxonomy updated (governance/cieu_event_taxonomy.md). UserPromptSubmit hook detects Board directive markers → emits DIRECTIVE_POSTED + registers obligation on CEO with 24h deadline. behavior_gov_engine `goal_level_directive_untouched` rule enabled.
- **Deadline**: 2026-05-06
- **Currently tracked in**: needs obligation registration

### P1-5 behavior_gov_engine rule adoption sweep
- **Owner**: Maya-Governance
- **Why P1**: Today shipped the engine + 4 rule types, but only 1 rule (`omission_overdue_block`) enabled. Goal is to migrate 5-10 existing speech-governance hooks (hook_stop_reply_scan.py inner rules, legacy forget_guard patterns) into YAML behavior rules.
- **Acceptance**: Audit existing hooks for speech-scan patterns (produces `reports/governance/speech_to_behavior_migration_2026_04.md`), migrate ≥5 to YAML, enable each with pytest coverage, retire deprecated hook code.
- **Deadline**: 2026-05-06
- **Currently tracked in**: needs obligation registration (maya actor)

---

## P2 — valuable but non-critical (natural window, 1–3 months)

Re-opening the 40 DEFER-P2 cards from Ethan 2026-04-21 triage. Grouped by engineer scope; Ethan assigns deadline per sprint capacity.

### P2 (Leo-Kernel — brain / kernel / CIEU schema)

- CZL-ETHAN-BRAIN-L3-DREAM-PARITY
- CZL-ETHAN-BRAIN-ARCH-SPEC
- CZL-ETHAN-BRAIN-IMPL-PHASE-1
- CZL-BIPARTITE-LOADER-IMPL
- CZL-LEO-BRAIN-IMPL
- CZL-BRAIN-AUTO-EXTRACT-EDGES
- CZL-BRAIN-FULL-INGEST-COVERAGE
- CZL-BRAIN-L2-WRITEBACK-IMPL (verify if MERGE superseded actually closed)
- CZL-BRAIN-METACOGNITION-LEDGER
- CZL-BRAIN-ERROR-CORRECTION-EXERCISE
- CZL-DOMINANCE-MONITOR
- CZL-L3-GUARD-RAILS-IMPL
- CZL-ESCAPE-SEMANTIC-REVERSAL (merged earlier; verify)

### P2 (Maya-Governance — governance logic / causal / omission)

- CZL-MAYA-BRAIN-IMPL
- CZL-GOVERNANCE-ROUND-TRIP-AUDIT (Iron Rules live-fire suite)
- CZL-FG-BLACKLIST-TO-WHITELIST-MIGRATION (deprecate keyword black-lists, favor intent whitelist)
- CZL-BRAIN-METACOGNITION-LEDGER (co-own with Leo)
- CZL-AIDEN-L3-AUTO-LIVE (verify)

### P2 (Ryan-Platform — adapter / hook / integration / infra)

- CZL-RYAN-BRAIN-IMPL
- CZL-JORDAN-BRAIN-IMPL (co-wire with Jordan)
- CZL-WINDOWS-COMPAT-AUDIT (POSIX-only API grep + CI matrix)
- CZL-SUBSCRIBER-SPAWN-BRIDGE (architectural limit; possible future when Claude Code relaxes nesting)
- CZL-OPS-GOV-INFO-SYNC (superseded by behavior_gov_engine; close after verify)
- CZL-UNIFIED-BUS-RUNTIME-WIRE (superseded)

### P2 (Jordan-Domains — domain packs / policy templates)

- CZL-JORDAN-BRAIN-IMPL (co-own with Ryan)
- Domain pack inventory (new card; Jordan decides priority)

### P2 (Samantha-Secretary — archival / knowledge / WHO_I_AM)

- After P0-2 WHO_I_AM-7-AGENTS completes, sweep for any remaining identity drift
- AMENDMENT-023/024 post-approval archival verification
- BOARD_CHARTER_AMENDMENTS review pipeline formalization

### P2 (unassigned / Ethan ruling needed)

- CZL-METHODOLOGY-BOOT-INTEGRATION (Ethan decide: already done via behavior_gov_engine wiring?)
- CZL-AMENDMENT-022-CHARTER (verify status)
- CZL-GODVIEW-BRAIN-INGEST (scope definition)
- remaining 10+ deferred items Ethan to grouping

---

## Cadence (restored)

- **Daily**: Ethan walks the in-flight P0 + P1 items, posts 2-line status to BOARD_PENDING.md
- **Weekly Monday**: CTO runs 30-min team review — all engineers bring "what shipped last week + what's blocking this week"; CEO attends + takes Board-facing synthesis
- **Weekly Friday**: CEO writes Board brief (1 page): shipped / in-flight / risks / asks
- **Biweekly**: backlog grooming — CEO + CTO reorder P2, promote aging P2 to P1 if they unblock mainline

Previous cadence collapsed because I (CEO) was doing engineering work instead of running cadence. Restored as of this doc.

---

## What CEO actually ships in next 48h

Not new code. These are CEO-scope:

1. BOARD_PENDING.md clean-up + today's Board brief (1 page)
2. Spawn Ethan for sprint planning session: he reviews this backlog, adjusts priorities, assigns engineers, sets sprint end date
3. After Ethan sprint plan: single Board message showing the assigned P0/P1 plus deadlines — Board approves or adjusts
4. Re-open 40 DEFER-P2 closed cards in dispatch_board — authorized for Ethan to do (governance/dispatch_board.json edit needs CTO, not CEO)
5. Weekly Friday brief starts this Friday 2026-04-26

None of these are engineering. These are the CEO job I've been ducking.
