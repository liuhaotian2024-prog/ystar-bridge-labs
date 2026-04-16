# Auto-Commit + Auto-Push Mechanism v1 — Design Specification

**Owner**: CTO (Ethan Wright)  
**Status**: Spec (L2) — implementation deferred to Ryan atomic  
**Created**: 2026-04-16  
**Context**: Campaign v6 W11 follow-up; Memory rule about d2852174 53-file commit disaster; current accumulation of 30+ uncommitted artifacts per session

## 1. Problem Statement

**Current state**: Y* Bridge Labs generates 20-40 artifacts per autonomous session (governance specs, reports, tests, daemon scripts, agent definitions). These accumulate as uncommitted changes until Board manually triggers cleanup or restart scripts flush them. This creates three risks:

1. **Work loss**: Session crash loses all uncommitted governance/knowledge artifacts
2. **Audit gap**: CIEU events fire but git history lags, breaking causal reconstruction
3. **Context pollution**: git status noise (40+ modified files) obscures actionable diffs

**Anti-pattern reference**: Commit d2852174 (Ryan 2026-04-16 P0 wire task) swept 53 files in one commit — thematic grouping was lost, bisect became impossible, and the commit message couldn't capture 7 distinct logical changes.

**Existing auto-push points** (grep + audit confirms):
- `publish_morning_to_readme.py` (cron daily 06:00) — commits+pushes README.md
- `restart.sh` (5 occurrences in 3 restart scripts) — dead-string "git push" calls, never reached
- Secretary `commit_watcher.py` — WATCHER only, Telegram notify, NOT a committer

**Gap**: No commit-then-push pipeline for governance/knowledge/test artifacts. No thematic auto-grouping. No event-driven trigger.

---

## 2. Trigger Model — Event-Driven (NOT Cron-Cadence)

Per Memory rule `feedback_methodology_no_human_time_grain.md`: AI agent cycles operate at ms (atomic tool_use) / min (session turn) / hour (campaign batch) granularity, NOT human cadences (daily/weekly/sprint).

**Primary trigger**: Stop hook fires after meaningful uncommitted change accumulates  
**Definition of "meaningful"**:
- ≥3 files modified in same thematic category (see §3), OR
- ≥1 governance/*.md spec file created/modified, OR
- ≥5 CIEU events emitted since last commit (threshold calibrated by W11 Agent Capability Monitor)

**Secondary trigger**: Campaign subgoal closes with Rt+1=0 (per `.czl_subgoals.json` completed array)  
**Rationale**: Natural checkpoint for batch commit — captures "W1 K9 healing" as atomic git history unit

**Rejected alternatives**:
- ❌ Cron hourly: artificially groups unrelated work (same problem as d2852174)
- ❌ Pre-commit hook: blocks agent tool_use flow, adds 200-400ms latency per file write
- ❌ Every tool_use: git overhead dominates (40 commits/session = noise)

**Implementation entry point**: `scripts/hook_stop_reply_scan.py` (existing daemon hook) calls `scripts/auto_commit_batch.py` when threshold crossed.

---

## 3. Commit Grouping — Thematic Auto-Classify

**Rule**: NEVER bundle >10 files in one commit unless they share a single logical change.

**Categories** (auto-detect via file path patterns):

| Category | Path patterns | Commit prefix | Example |
|----------|--------------|---------------|---------|
| Governance | `governance/*.md`, `AGENTS.md`, `CLAUDE.md` | `docs(governance):` | governance specs, rules, CHARTER_MAP |
| Tests | `tests/**/*.py`, `Y-star-gov/tests/**` | `test(scope):` | pytest files, test data |
| Scripts | `scripts/*.py`, `scripts/*.sh`, hook files | `feat(platform):` | daemon scripts, hooks, boot |
| Knowledge | `knowledge/**/*.md`, `.claude/agents/*.md` | `docs(knowledge):` | methodologies, trust scores, agent charters |
| Y-star-gov | changes in Y-star-gov workspace sibling | `feat(ystar-gov):` | source code, ystar core |
| Reports | `reports/**/*.md` | `chore(reports):` | daily/hourly/autonomous reports |
| Memory | `memory/*.md`, `memory/*.json` | `chore(state):` | session handoff, world state |

**Mixed-category handling**: If a Stop hook batch contains files from 2+ categories, split into N commits (one per category). Preserve chronological order of CIEU events within each category.

**Commit message format**:
```
<prefix>: <5-tuple summary extracted from CIEU events>

Y*: <what this batch was trying to achieve>
Xt: <state before>
U: <N actions taken>
Yt+1: <state after>
Rt+1: <remaining gap>

CIEU events: <count> | Files: <count> | Campaign: <id if applicable>
```

**Auto-extraction heuristic**: Parse CIEU events since last commit → identify agent_id + event_type frequency → generate Y*/Xt/U/Yt+1 summary (≤200 chars per field).

---

## 4. Push Policy — Opt-In Per Repo

**Default policies**:

| Repo | Auto-push | Rationale |
|------|-----------|-----------|
| `ystar-company` (this repo) | **YES** for non-sensitive paths | Governance/knowledge/reports are append-only; Board reviews via Telegram, not pre-push gate |
| `Y-star-gov` (product source) | **NO** — requires CTO sign-off | Code changes need test gate + manual review; auto-commit OK, auto-push deferred |
| `gov-mcp` (server daemon) | **NO** | External dependency; never auto-push |

**Sensitive path exclusions** (NEVER commit, enforced by ForgetGuard scope checks):
- `.env`, `*.env`, `*_secrets.env`
- `.ystar_session.json` (contains API keys)
- `scripts/hook_debug.log`, `scripts/hook_observe.log` (may contain PII from prompts)
- `.ystar_cieu.db`, `.ystar_cieu.db-wal`, `.ystar_cieu.db-shm` (SQLite runtime, not source)
- `.session_booted`, `.session_call_count` (ephemeral session markers)
- Any file matching ForgetGuard rule `file_path_forbidden` patterns

**Pre-commit validation** (reuse existing tooling):
1. Run `scripts/governance_ci.py check` (if exists) to verify no rule violations in staged changes
2. Scan staged files against ForgetGuard `file_path_forbidden` patterns
3. If any file is blocked → skip auto-commit, emit CIEU `AUTO_COMMIT_BLOCKED` event with reason
4. Accumulate blocked files in `.auto_commit_pending.json` for Board manual review

**Push execution** (only if auto-push policy = YES):
```python
subprocess.run(["git", "push", "origin", "main"], cwd=repo_root, timeout=30)
```
If push fails (network, merge conflict, hook rejection) → emit CIEU `AUTO_PUSH_FAILED`, do NOT retry (Board handles manually).

---

## 5. Safety Guards — Reuse ForgetGuard Scope Checks

**Integration with existing governance**:

1. **ForgetGuard rule `subagent_unauthorized_git_op`** (just shipped f00e91ac) — prevents sub-agents from git commit/push/add/reset. Auto-commit pipeline runs as **CEO-owned background task**, NOT sub-agent, so this rule does NOT block it.

2. **CIEU audit trail**: Every auto-commit must emit 3 CIEU events:
   - `AUTO_COMMIT_TRIGGERED` (threshold crossed, N files staged)
   - `AUTO_COMMIT_GROUPED` (N commits created, categories listed)
   - `AUTO_COMMIT_COMPLETE` (commit hashes, push success/skip)

3. **Rollback safety**: If auto-commit creates commit X, but subsequent validation (e.g., pytest run in Y-star-gov) fails → emit `AUTO_COMMIT_ROLLBACK_CANDIDATE` CIEU event, do NOT auto-revert (Board decides).

4. **Conflict detection**: Before auto-commit, run `git fetch && git diff origin/main..HEAD` to detect upstream changes. If non-fast-forward → skip auto-commit, emit `AUTO_COMMIT_CONFLICT`, wait for Board manual merge.

5. **Rate limiting**: Max 1 auto-commit per 5 minutes per repo (prevent runaway loop if Stop hook misfires). Track last commit timestamp in `.auto_commit_state.json`.

**Failure modes documented**:
- Network outage during push → files committed locally, push deferred to next trigger
- ForgetGuard blocks sensitive file → auto-commit skips that file, proceeds with rest
- Git hook (e.g., pre-commit linter) rejects → entire batch aborted, CIEU event emitted

---

## 6. Implementation Skeleton — `scripts/auto_commit_batch.py`

**Pseudocode** (≤30 lines, full implementation deferred to Ryan atomic):

```python
#!/usr/bin/env python3
"""Auto-commit batching with thematic grouping."""
import os, json, subprocess, time
from pathlib import Path
from collections import defaultdict

REPO_ROOT = Path(__file__).resolve().parent.parent
STATE_FILE = REPO_ROOT / ".auto_commit_state.json"
CATEGORY_PATTERNS = {
    "governance": ["governance/*.md", "AGENTS.md", "CLAUDE.md"],
    "tests": ["tests/**/*.py", "Y-star-gov/tests/**/*.py"],
    "scripts": ["scripts/*.py", "scripts/*.sh", "scripts/hook_*.py"],
    "knowledge": ["knowledge/**/*.md", ".claude/agents/*.md"],
    "reports": ["reports/**/*.md"],
    "memory": ["memory/*.md", "memory/*.json"],
}

def should_trigger():
    """Check if Stop hook threshold crossed."""
    # Read git status, count modified files per category
    # Return True if ≥3 files in same category OR ≥1 governance spec modified
    pass

def classify_files(changed_files):
    """Group files by category using CATEGORY_PATTERNS."""
    groups = defaultdict(list)
    for f in changed_files:
        # Match against patterns, assign to category
        pass
    return groups

def commit_group(category, files, cieu_events):
    """Create one commit for this category."""
    # Extract 5-tuple summary from cieu_events
    # Format commit message per §3
    # Run git add <files> && git commit -m "..."
    pass

def main():
    if not should_trigger():
        return
    # Load state, check rate limit (§5)
    # Run git status --short, parse changed files
    # Classify files into categories (§3)
    # For each category: commit_group(...)
    # If auto-push policy = YES: git push
    # Emit CIEU events (§5)
    # Update STATE_FILE timestamp
    pass
```

**Integration points**:
1. Called by `scripts/hook_stop_reply_scan.py` after reply emitted
2. Reads `.czl_subgoals.json` to detect campaign subgoal closures (secondary trigger)
3. Queries `.ystar_cieu.db` for events since last commit (threshold + message extraction)
4. Updates `memory/continuation.json` with "last auto-commit timestamp" for next session boot

**Testing strategy** (deferred to Ryan CZL-111 follow-up):
- Unit tests: file classification, 5-tuple extraction, rate limiting
- Integration test: trigger auto-commit in sandbox repo, verify N commits created
- Smoke test: run in production for 1 session, verify no sensitive files committed

---

## 7. Rollout Plan

**Phase 1** (Ryan atomic CZL-111): Implement `auto_commit_batch.py` with dry-run mode (emit CIEU events, do NOT git commit)  
**Phase 2** (48h soak): Monitor CIEU `AUTO_COMMIT_TRIGGERED` frequency, tune thresholds  
**Phase 3** (CTO approval gate): Flip dry-run → live for ystar-company repo only  
**Phase 4** (post-v0.42 ship): Extend to Y-star-gov repo with stricter test gate

**Success metrics**:
- Zero sensitive files committed (validate via `git log --all -- .env`)
- ≤10 files per commit (validate via `git log --stat`)
- Auto-commit triggered ≤12 times per 8h session (rate limit working)
- CIEU events `AUTO_COMMIT_BLOCKED` <5% of triggers (low false-positive rate)

**Abort criteria**:
- Any `.env` or credential file committed → immediate rollback, CTO P0 investigation
- >3 auto-push failures in 24h → disable auto-push, revert to commit-only mode

---

## Metadata

**Spec version**: v1  
**Words**: 1847  
**Sections**: 7 (Problem / Trigger / Grouping / Push Policy / Safety / Implementation / Rollout)  
**Dependencies**: Stop hook (live), ForgetGuard (live), CIEU DB (live), .czl_subgoals.json (live)  
**Downstream**: Ryan CZL-111 implementation atomic (queued)  
**Cross-cutting**: K9 audit captures pre-commit file scope per CIEU event  
**EDM upstream**: Memory d2852174 53-file disaster / ForgetGuard subagent git-op rule  
**EDM downstream**: Ryan implementation / Agent Capability Monitor W11 threshold calibration  
**EDM cross-cutting**: CIEU event schema expansion (3 new event types)  
**EDM naming**: No collision — auto_commit_batch.py is new file

---

**CTO attestation**: This spec defines event-driven (NOT cron), thematic grouping (NOT bundle-everything), opt-in push policy, ForgetGuard integration, and safety guards. Implementation skeleton provided. Ready for Ryan atomic execution.
