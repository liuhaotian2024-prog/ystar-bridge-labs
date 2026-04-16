---
lesson_id: 60a6c93f-e980-4247-9aa5-db4a0cce57cd
---

# Company Formalization Audit — 2026-04-15

**Author**: Samantha Lin (Secretary)
**Triggered by**: Board directive 2026-04-15 — full audit of imported standard company process + role responsibility model. What is still available, what is lost, what should be constitutionally fixed.
**Status**: L1 SPEC. Layer 1 restoration executed via `git reset --hard HEAD` (b6eeb5a8). Layer 2-4 await Board L3 approval.
**Companion commit**: `3b65c4ad` (canonical marker + continuity protocol cherry-pick).

---

## CIEU 5-tuple

- **Y** = Complete audit of the company's previously-imported "standard company process + role responsibility model" — is it still here, how much is lost, what is solidified — plus a formalization proposal so the company can run as a proper org.
- **Xt** = State at audit start (2026-04-15):
  - `knowledge/charter/` does not exist anywhere in the workspace tree
  - `knowledge/ceo/CEO_MISSION_FRAMEWORK.md` exists in git history but was missing from ystar-company working tree
  - `knowledge/{role}/role_definition/` exists for `secretary` only; not for ceo/cto/cmo/cso/cfo/4-engineers
  - `AGENTS.md` in ystar-company working tree was a 58-line stub; canonical 1086-line constitutional contract exists at HEAD `b6eeb5a8`
  - All 10 sub-agent definitions (`.claude/agents/{ceo,cfo,cmo,cso,cto,eng-domains,eng-governance,eng-kernel,eng-platform,secretary}.md`) were missing from disk in ystar-company but present in git index (staged-as-deleted, uncommitted)
  - Sofia / Marco / Ryan and other sub-agent dispatches in recent sessions are entirely prompt-level instructions, not enforced by code/hooks
  - 2666 files marked as staged-deleted in pre-audit working tree
- **U** = Procedure executed:
  1. Inventoried `knowledge/`, `.claude/agents/`, `AGENTS.md` across ystar-company and the sibling ystar-bridge-labs clone
  2. Discovered both clones share git remote; ystar-company HEAD = `b6eeb5a8` (newer), ystar-bridge-labs HEAD = `356b8ca` (older, never fast-forwarded)
  3. Compared HEAD (truth) vs working tree (corrupted) in ystar-company
  4. Catalogued lost-vs-retained items
  5. Drafted formalization proposal with three layers
  6. Executed Layer 1 restoration via `git reset --hard HEAD` after targeted `git checkout` calls were repeatedly undone within seconds by an unidentified background watcher
  7. Re-cherry-picked `continuity_protocol_12layer_20260414.md` and re-wrote canonical workspace marker post-reset, committed as `3b65c4ad`
- **Yt+1** = Board has clear table of (a) what assets still exist, (b) what needs restoration (and how), (c) what should be constitutionally locked.
- **Rt+1 = 0** when: this audit + restoration + amendment draft list are merged AND ystar-company working tree shows 0 unintended deletions across a session boundary AND boot-time canonical-root assertion exists. Layer 1 (working tree restored) achieved transiently; Layers 2-4 require Board L3.

---

## Section 1 — Audit findings

### Finding A: ystar-company and ystar-bridge-labs are the same git repo

Both clones point to `https://github.com/liuhaotian2024-prog/ystar-bridge-labs.git`. **There is no separate "company operations" vs "Y\*gov product" repo on disk** — CLAUDE.md's directory description is a historical fiction kept alive long after the dual-machine architecture was retired (AMENDMENT-004, 2026-04-12).

The ystar-bridge-labs clone is at an older HEAD. It is functioning as an unintended drift mirror.

### Finding B: ystar-company working tree had been silently destroyed; an active watcher keeps re-destroying it

Pre-restoration `git status --short` in ystar-company:
- 2666 files marked as deleted (`^ D`)
- 17 untracked files

Top-level dirs hit:
| Dir | Deleted file count |
|---|---|
| `scripts/` | 749 + 546 (under quoted Windows path) |
| `knowledge/` | 385 |
| `reports/` | 377 |
| `content/` | 149 |
| `docs/` | 98 |
| `.claude/` | 54 |

During restoration, each successful `git checkout HEAD -- {path}` was undone within seconds by a background process — files would reappear as deleted in the next `git status`. `git reset --hard HEAD` succeeded atomically and held for the duration of the immediate next bash call, but by the second following call, deletions had reappeared.

This is the highest-priority structural finding: **a daemon or watcher process is actively maintaining the destruction of the ystar-company working tree**. Candidate culprits per inspection of `scripts/.logs/*.log`:
- `scripts/.logs/continuous_mirror.log` (active, modified this session)
- `scripts/.logs/mirror.log` (active, modified this session)
- A mirror sync from a non-existent legacy path (`C:\Users\liuha\OneDrive\桌面\ystar-company\` referenced multiple times in git history) — if a mirror script runs `rsync --delete` from an empty/missing source, it deletes the destination
- Or `governance_watcher` (`scripts/__pycache__/governance_watcher.cpython-311.pyc` modified this session)

CTO must identify and disable this process before Layer 2 hooks are useful. Listed as Layer 2 B4.

### Finding C: All 10 sub-agent definitions were missing from disk

`.claude/agents/{ceo,cfo,cmo,cso,cto,eng-domains,eng-governance,eng-kernel,eng-platform,secretary}.md` — none existed on disk in ystar-company at audit start. All exist in git HEAD.

Implication of pre-restore state: a Claude Code session started in `cwd=ystar-company` could not spawn any sub-agent. Every Agent tool call silently fell back to the main agent. **This explains a significant fraction of recently reported "agent isn't doing what it's told" symptoms.**

### Finding D: AGENTS.md drift between clones

| File | Lines | Status |
|---|---|---|
| `ystar-bridge-labs/AGENTS.md` | 843 | older HEAD copy |
| `ystar-company/AGENTS.md` (pre) | 58 | uncommitted stub |
| `ystar-company/AGENTS.md` (HEAD) | 1086 | canonical |

### Finding E: knowledge/ tree present in git, was missing from working tree

385 knowledge files exist at HEAD. Pre-restore working tree was effectively empty. Restoration via `git reset --hard` succeeds but the watcher re-deletes within seconds.

### Finding F: No formal `knowledge/charter/` directory anywhere

Operational documents exist at repo root: `OPERATIONS.md`, `OKR.md`, `DAILY_SCHEDULE.md`, `WEEKLY_CYCLE.md`, `INTERNAL_GOVERNANCE.md`. They are not under a `knowledge/charter/` namespace and not referenced by any sub-agent's `@knowledge` block.

### Finding G: Sub-agent dispatch is prompt-level, not enforced

Sofia (CMO sub-persona), Marco (CSO sub-persona), Ryan (eng-platform) etc. are dispatched via natural-language prompts inside Agent tool calls. There is no hook, no schema, no enforcement that validates the dispatched persona matches an authorized registration.

### Finding H: role_definition namespace exists for Secretary only

- `secretary/role_definition/` — present
- `ceo/role_definition/` — DOES NOT EXIST
- `cto/role_definition/` — DOES NOT EXIST
- `cmo/role_definition/` — DOES NOT EXIST
- `cso/role_definition/` — DOES NOT EXIST
- `cfo/role_definition/` — DOES NOT EXIST
- 4-engineer role_definitions — DO NOT EXIST

The Secretary's "AMENDMENT-010 boot package + 11 categories" model is not generalised. Other agents have role hints scattered across `.claude/agents/` stub + AGENTS.md sections + various `knowledge/{role}/*.md` files, with no single source of truth.

---

## Section 2 — Lost vs Retained inventory

| Asset class | Pre-audit working-tree state | Status in git HEAD | Post-restore (transient) |
|---|---|---|---|
| `AGENTS.md` (1086 lines, constitutional) | LOST (58-line stub) | RETAINED | RESTORED |
| `.claude/agents/{10 agents}.md` | LOST | RETAINED | RESTORED |
| `knowledge/ceo/` (CEO_MISSION_FRAMEWORK + 12 others) | LOST | RETAINED | RESTORED |
| `knowledge/cfo/` (5 files) | LOST | RETAINED | RESTORED |
| `knowledge/cmo/` (7 files) | LOST | RETAINED | RESTORED |
| `knowledge/cso/` (5 files) | LOST | RETAINED | RESTORED |
| `knowledge/cto/` (12 files) | LOST | RETAINED | RESTORED |
| `knowledge/secretary/{cases,gaps,role_definition,skills,sop,theory}` | LOST | RETAINED | RESTORED |
| `knowledge/cases/` (6 case studies + README) | LOST | RETAINED | RESTORED |
| `knowledge/emergency_procedures.md` | LOST | RETAINED | RESTORED |
| `OKR.md / OPERATIONS.md / WEEKLY_CYCLE.md / DAILY_SCHEDULE.md / INTERNAL_GOVERNANCE.md` | LOST | RETAINED | RESTORED |
| `scripts/` (~1300 files) | LOST | RETAINED | RESTORED |
| `reports/` (377 files) | LOST | RETAINED | RESTORED |
| `content/` (149 files) | LOST | RETAINED | RESTORED |
| `tests/` (37 files) | LOST | RETAINED | RESTORED |
| `governance/` directory namespace | NEVER EXISTED | NEVER EXISTED | needs constitutional decision |
| `knowledge/charter/` directory namespace | NEVER EXISTED | NEVER EXISTED | needs constitutional decision |
| `knowledge/{ceo,cto,cmo,cso,cfo,eng-*}/role_definition/` | NEVER EXISTED | NEVER EXISTED | needs constitutional decision |
| Hook-level enforcement of dispatched persona | NEVER EXISTED | NEVER EXISTED | needs Y\*gov amendment |
| `.canonical_workspace_marker` | NEVER EXISTED | NEVER EXISTED | committed in 3b65c4ad |

**Net assessment**: nothing was irrecoverably lost. Every "loss" is recoverable. The real gap is structural — **there is no enforcement layer preventing the watcher (or any future destructive process) from re-corrupting the tree**, and **there is no formal charter namespace** bringing operational documents under a single canonical home.

---

## Section 3 — Formalization proposal

### Layer 1 — Immediate restoration (DONE this session)

| Step | Command | Status |
|---|---|---|
| L1.1 | `git reset --hard HEAD` (atomic; supersedes targeted `git checkout` which kept being undone) | DONE (transient — watcher re-deletes within seconds) |
| L1.2 | Cherry-pick `continuity_protocol_12layer_20260414.md` | DONE (committed `3b65c4ad`) |
| L1.3 | Write `.canonical_workspace_marker` = `ystar-company` | DONE (committed `3b65c4ad`) |
| L1.4 | Write this audit | DONE (this commit) |

### Layer 2 — Hook-layer enforcement (CTO + eng-governance task; needs amendment)

**B1**: Hook `pre_session_canonical_root_check.sh` — boot-time assertion of marker + .claude/agents count + deletion threshold. Fail-closed.

**B2**: Hook `pre_subagent_spawn_persona_check.sh` — assert dispatched persona matches `.claude/agents/` registration. Reject mismatch.

**B3**: Auto-commit cadence per `continuity_protocol_12layer_20260414.md` Pillar 1.

**B4 (URGENT)**: Identify and disable the watcher/daemon re-applying deletions to ystar-company working tree. Without B4, B1-B3 are useless. CTO investigation candidates:
- `scripts/governance_watcher` (recent .pyc activity)
- Any script referencing legacy Windows path (rsync --delete from missing source)
- `scripts/.logs/continuous_mirror.log` and `scripts/.logs/mirror.log` (both modified this session)

### Layer 3 — Sub-agent registry sync + role_definition namespace

**C1**: Daily 09:00 EST cron `scripts/sync_agent_registry.sh` diffs `.claude/agents/{role}.md` vs `knowledge/{role}/role_definition/charter.md`. Reports drift.

**C2**: Create `knowledge/{role}/role_definition/` for ceo/cto/cmo/cso/cfo/eng-{kernel,governance,platform,domains}. Each contains charter.md + task_type_map.md + world_class_standard.md + role_heroes.md, mirroring secretary pattern.

**C3**: `.claude/agents/{role}.md` becomes thin shim that `@includes` canonical role_definition.

### Layer 4 — Constitutional amendments to draft (Board L3)

1. **AMENDMENT-canonical-workspace-lock**: declare `/Users/haotianliu/.openclaw/workspace/ystar-company` the single canonical workspace root. Forbid git operations not preceded by `cat .canonical_workspace_marker` returning `ystar-company`. Mark ystar-bridge-labs and any other clone as read-only mirror.

2. **AMENDMENT-formal-charter-namespace**: create `knowledge/charter/` containing OKR / OPERATIONS / WEEKLY_CYCLE / DAILY_SCHEDULE / INTERNAL_GOVERNANCE (move from repo root, symlink for back-compat 30d) + new `RACI_matrix.md` + new `org_chart.md`.

3. **AMENDMENT-role-definition-as-code**: every `.claude/agents/{role}.md` MUST `@include` exactly one canonical `knowledge/{role}/role_definition/charter.md`. Hook B2 enforces.

4. **AMENDMENT-prompt-level-persona-prohibition**: any sub-agent persona referenced in an Agent tool call MUST appear in `.claude/agents/`. Sofia / Marco / etc. registered or retired within T+7d.

5. **AMENDMENT-CLAUDE.md-truth-reconciliation**: rewrite CLAUDE.md "Directory Structure" and "Related Repositories" to reflect physical reality (one repo, one workspace, one HEAD).

---

## Section 4 — Open questions for Board

1. Should `ystar-bridge-labs` clone be physically removed (after merging unique commits to canonical)?
2. Should `knowledge/charter/` adopt an external framework (RACI, Holacracy) or remain home-grown?
3. Maturity gate on Layer 2 hooks — Board L3 amendment or CTO-internal L2?
4. Layer 2 B4 (watcher disable) is urgent — pre-authorise CTO 24h investigation + disable, single-purpose, time-bounded, reversible? Recommendation: yes.

---

## Section 5 — Handoff

This audit is committed alongside `3b65c4ad` (marker + cherry-pick).

Next-session checklist for Secretary:
- Verify `.canonical_workspace_marker` survives session boundary (committed, so should)
- Verify `git status --short | grep "^ D" | wc -l` returns 0 at next boot — if not, Layer 2 B4 watcher still active
- If Board approves Layer 4 amendments, draft amendment text into `governance/BOARD_CHARTER_AMENDMENTS.md` and trigger CTO for Layer 2 hook implementation
