# Skill-Trust Hybrid Architecture v1.0

**Constitutional — Board 2026-04-16 Comprehensive Architecture**

**Context**: Board directive: "推行" batch approval of (1) Skill-based trust scoring, (2) 5 new engineer specialists, (3) Pair-programming protocol, (4) Reward mechanisms, (5) Anti-monopoly quotas. Single atomic integrated spec.

**Integration anchor**: CTO role v2 (#governance/cto_role_v2_and_dispatch_board_20260416.md), Tier-routing v1 (#governance/tiered_routing_protocol_v1.md), Dispatch board CZL-68 (Ryan in-flight).

**Purpose**: Shift from routing-by-fiat to distributed-trust-market with anti-monopoly safeguards.

---

## Part 1 — Trust Score Quantification

**Problem**: All engineers currently treated as equals. No empirical skill differentiation. No data-driven pre-authorization scope assignment.

**Solution**: Per-engineer trust score 0-100 derived from CIEU historical performance.

### Formula v1.0

```python
trust_score = (
    success_rate * 0.5 +
    (1 - e1_mismatch_ratio) * 0.2 +
    max(0, 100 - hallucination_count * 5) * 0.2 +
    on_time_delivery_bonus * 0.1
)

# Components:
# success_rate = (completed tasks with Rt+1=0) / (total tasks claimed)
# e1_mismatch_ratio = (|tool_use_claimed - tool_use_actual|) / tool_use_actual (E1 compliance)
# hallucination_count = ForgetGuard HALLUCINATION_DETECTED events count (last 30d)
# on_time_delivery_bonus = 100 if avg(completion_time) ≤ estimated_time, else 0
```

**Normalization**: Clamp to [0, 100]. Initial score for new engineers = 50 (mid-tier).

**Storage**: `governance/engineer_trust_scores.json`

```json
{
  "last_updated": "2026-04-16T14:45:00Z",
  "scores": {
    "maya-governance": {
      "score": 82,
      "success_rate": 0.91,
      "e1_mismatch_ratio": 0.03,
      "hallucination_count": 1,
      "on_time_delivery_bonus": 100,
      "total_tasks_claimed": 47,
      "tasks_completed_rt0": 43,
      "avg_completion_time_vs_estimate": 0.87,
      "last_task_at": "2026-04-16T12:30:00Z"
    },
    "ryan-platform": {
      "score": 78,
      "success_rate": 0.85,
      "e1_mismatch_ratio": 0.08,
      "hallucination_count": 2,
      "on_time_delivery_bonus": 100,
      "total_tasks_claimed": 52,
      "tasks_completed_rt0": 44,
      "avg_completion_time_vs_estimate": 0.93
    }
    // ... other engineers
  }
}
```

**Update frequency**: AI re-grain (2026-04-16): Event-driven — triggered after every 10 task completions observed OR Board requests trust audit, not hardcoded weekly schedule. Implemented via `scripts/trust_score_update.py`.

**Decay rule**: AI re-grain (2026-04-16): Trust drops -5pt after N consecutive idle observation periods (N=5 default, ~equivalent to former weekly decay over month-long inactivity if observations happen daily). No hardcoded time-grain.

**Display integration**: `governance/active_dispatch_log.md` extension — each dispatch shows trust score beside engineer_id.

**Transparency**: All scores visible to all engineers (peer accountability). Dashboard live at `governance/engineer_trust_scores.json` (committed to git, not hidden).

---

## Part 2 — Five New Engineer Charters

**Current team**: 4 engineers (Maya/Ryan/Leo/Jordan). + 1 (Samantha-Secretary hybrid role).

**New specialists** (expand to 9 engineer slots):

### eng-data (Maya expansion path)

**Full name**: Maya Patel (dual hat: governance + data analytics)

**Charter**:
- CIEU analytics: trend queries, anomaly detection, audit forensic
- Governance metrics dashboards (trust score visualization, dispatch velocity, drift event counts)
- Log forensic: root-cause analysis for complex CIEU chains (K9 causal_analyzer.py integration)
- Data export: CIEU → SQL/Parquet for Board analysis
- Governance rule authorship (ForgetGuard rules, tiered-routing classifiers)

**Files in scope**: `scripts/*_cieu*.py`, `governance/engineer_trust_scores.json`, `governance/cieu_event_taxonomy.md`, `reports/drift_hourly/*.md`, all CIEU query scripts.

**Initial trust score**: 82 (inherits Maya's existing governance track record).

**Charter file**: `.claude/agents/maya-data.md` (dual-registration with maya-governance.md, priority determined by CEO dispatch context).

---

### eng-security (new)

**Full name**: Alex Kim (new engineer, initial trust 50)

**Charter**:
- Security audit: secret detection (K9Audit Auditor integration), dependency CVE scan
- Threat modeling: CIEU audit for privilege escalation, scope violations
- Penetration testing: red-team Y*gov hooks, test ForgetGuard bypass attempts
- Incident response: handle CIEU security events (UNAUTHORIZED_FILE_ACCESS, SECRET_LEAKED)
- Security patch coordination: CVE triage for Y*gov dependencies

**Files in scope**: `scripts/k9_repo_audit.py`, `governance/security_audit_log.md`, `tests/security/*.py`, `ystar-gov/security/` (cross-repo access authorized).

**Initial trust score**: 50 (new engineer, no history).

**Charter file**: `.claude/agents/alex-security.md`

---

### eng-ml (new)

**Full name**: Priya Sharma (new engineer, initial trust 50)

**Charter**:
- Gemma fine-tune: local LLM training for Y*gov specialized tasks (CIEU summarization, task classification)
- Eval pipelines: automated quality scoring for agent outputs (hallucination detection, E1 compliance)
- Model registry: versioned Gemma checkpoint management, A/B test infrastructure
- Local inference optimization: latency profiling for Gemma endpoint (192.168.1.228:11434 or localhost per AMENDMENT-004)
- ML observability: model drift detection, cache hit rate tracking

**Files in scope**: `scripts/local_learn.py`, `scripts/gemma_*.py`, `memory/model_registry/*.json`, `tests/ml/*.py`.

**Initial trust score**: 50 (new engineer, no history).

**Charter file**: `.claude/agents/priya-ml.md`

---

### eng-perf (new)

**Full name**: Carlos Mendez (new engineer, initial trust 50)

**Charter**:
- Performance debugging: identify latency hotspots in Y*gov hook execution, CIEU writes
- Profiling: flame graphs, async trace analysis, lock contention detection
- Capacity testing: load testing for dispatch board, engineer daemon concurrent claim limits
- Optimization: refactor slow CIEU queries, reduce hook overhead
- SLO enforcement: track SLO compliance (e.g., "CIEU write ≤50ms p99"), emit alerts on breach

**Files in scope**: `scripts/perf_*.py`, `tests/perf/*.py`, `reports/performance_baseline.md`.

**Initial trust score**: 50 (new engineer, no history).

**Charter file**: `.claude/agents/carlos-perf.md`

---

### eng-compliance (new)

**Full name**: Sofia Chen (new engineer, initial trust 50)

**Charter**:
- Regulatory frameworks: GDPR/SOC2/HIPAA pattern implementation for Y*gov
- Audit trail validation: ensure CIEU logs meet regulatory retention requirements
- Compliance testing: automated checks for data deletion, consent tracking, access logs
- Documentation: compliance runbooks, audit-ready evidence packages
- External audit coordination: prepare CIEU exports for SOC2 auditors

**Files in scope**: `governance/compliance/*.md`, `scripts/compliance_*.py`, `tests/compliance/*.py`, `reports/audit_ready/*.md`.

**Initial trust score**: 50 (new engineer, no history).

**Charter file**: `.claude/agents/sofia-compliance.md`

---

## Part 3 — Pair-Programming Protocol

**Problem**: Junior engineers (trust <60) get stuck on hard tasks, waste time, produce low-quality deliverables. No mentorship mechanism.

**Solution**: Mandatory pair-programming for hard tasks (T2 or trust<60 engineer on complex T1).

### Trigger Rules

**Automatic pairing required when**:
1. Task tier = T2 (cross-engineer / architectural) AND claimed by engineer with trust <70
2. Task tier = T1 BUT estimated_tool_uses >10 AND claimed by engineer with trust <60
3. Engineer self-requests pair (via `dispatch_board.py claim --request_pair`)

**Pairing algorithm**:
- Senior pool = engineers with trust ≥70 in same skill domain
- Assign senior with lowest current pair-count (load balance mentoring)
- If no senior available in domain → escalate to CTO for cross-domain pairing

**Execution**:
- Pair on same Bash/Read/Write tool calls (senior reviews junior's edits in real-time)
- Both engineer IDs logged on CIEU events: `claimed_by: ["jordan-domains", "maya-governance"]` (array)
- Dual signoff on completion receipt (both engineers paste 5-tuple, verify Rt+1=0 consensus)

**Frequency target**: AI re-grain (2026-04-16): Each engineer participates in ≥1 pair-programming session after junior trust gap detected (trust <60 engineer claims task, OR engineer self-requests pair). Triggered by event, not hardcoded weekly mandate.

**Anti-monopoly enforcement**: AI re-grain (2026-04-16): Senior engineers (trust ≥70) MUST mentor. Quota: ≥1 pairing session triggered after junior trust gap detected OR after senior completes 10 consecutive solo tasks. If senior refuses pairing request 2x, trust score drops 10pt (forced mentorship). No hardcoded weekly cycle.

**Storage**: Pair-programming sessions logged to `governance/pair_sessions_log.md`:

```markdown
## 2026-04-16 Pair Session Log

| Session ID | Junior | Senior | Task | Duration | Outcome |
|------------|--------|--------|------|----------|---------|
| PAIR-042   | jordan-domains | maya-governance | CZL-71 template validation | 47min | Rt+1=0, both signoff |
| PAIR-043   | alex-security | ryan-platform | CZL-73 CVE scan | 35min | Rt+1=0, both signoff |
```

---

## Part 4 — Reward Mechanism

**Problem**: No incentive for high-quality work. All engineers get same pre-authorization scope regardless of track record.

**Solution**: Trust-based tiered rewards (automatic, no manual CTO intervention).

### Reward Tier 1: Pre-Auth Scope Expansion (trust ≥70)

**Current pre-auth templates** (from tier-routing v1 §3):
- Add ForgetGuard rule mode=warn
- Extend hook script try/except
- Add test assertions
- Update charter sections (additive only)
- File rename within scope

**Extended pre-auth for trust ≥70**:
- Add ForgetGuard rule mode=warn OR mode=log (but not mode=deny)
- Extend hook script + modify existing function logic (not just wrapper)
- Add test assertions + refactor test helper functions
- Update charter sections (additive + deletion of deprecated content)
- Cross-file rename (≤3 files, same module)
- Minor API change (add optional parameter, not breaking change)

**Extended pre-auth for trust ≥85**:
- All trust ≥70 permissions
- Add ForgetGuard rule mode=deny (requires CTO review, but engineer can draft + submit)
- Breaking API change (CTO review required, but engineer can propose)
- Delete deprecated code (≤50 lines)

**Enforcement**: Tier-routing classifier checks engineer trust score before applying template. If trust <70 but task requires ≥70 template → auto-escalate to T2 for CTO review.

---

### Reward Tier 2: First-Pick on Dispatch Board (trust-weighted claim race)

**Problem**: Multiple engineers claim same task simultaneously. Current race condition = random winner.

**Solution**: Trust-weighted priority. Higher trust engineer gets first-pick.

**Algorithm** (implemented in `dispatch_board.py claim`):
1. Engineer A (trust 82) and Engineer B (trust 65) both claim CZL-99 within same 2s window
2. Dispatch board locks task, checks both engineers' trust scores
3. Engineer A wins (82 > 65), claim succeeds
4. Engineer B's claim fails with error "task already claimed by higher-trust engineer"
5. Engineer B retries with next available task

**Cap**: Top-1 trust ranking gets 25% claim-rate reduction (anti-runaway safeguard, see Part 5).

---

### Reward Tier 3: Reduced CTO Oversight (trust ≥75)

**Current CTO review cadence** (from CTO role v2 spec):
- T2 tasks: 100% review (merge gate)
- T1 tasks: Weekly random 5-task spot-check

**Reduced oversight for trust ≥75**:
- T2 tasks: CTO reviews architectural design, but delegates implementation review to engineer's pair-partner (peer review instead of CTO review)
- T1 tasks: Excluded from spot-check sampling (CTO focuses on trust <75 engineers)

**Time savings**: CTO ritual (event-triggered T1 sample review per CTO role v2 Part 4) scopes to trust <75 pool only, excludes high-trust engineers.

---

### Reward Tier 4: Public Leaderboard (peer accountability)

**Dashboard**: `governance/engineer_trust_scores.json` visible to all engineers (committed to git).

**Weekly email** (Secretary sends Friday EOD):
- Top 3 engineers by trust score
- Biggest trust score Δ (up/down) this week
- Pair-programming participation leaderboard (who mentored most)

**Gamification** (optional, Board approval required):
- Achievement badges (e.g., "10 Rt+1=0 streak", "Zero E1 mismatch 30d", "Mentor Champion")
- Stored in `governance/engineer_achievements.json`

---

## Part 5 — Anti-Monopoly Quotas

**Problem**: Without safeguards, high-trust engineers could monopolize easy/high-value tasks, leaving low-trust engineers with only hard/low-reward work. Runaway feedback loop.

**Solution**: 5 anti-monopoly mechanisms.

### 1. Per-Engineer Claim-Rate Cap

**Rule**: Each engineer can claim ≤N tasks per hour (N = 2 default, configurable in `.ystar_session.json`).

**Rationale**: Prevent hoarding (engineer claims 10 tasks, completes none).

**Enforcement**: `dispatch_board.py claim` checks engineer's current claimed count (tasks with status=claimed, claimed_by=engineer_id). If count ≥ cap → claim fails with error "capacity limit reached, complete existing tasks first".

**Per-engineer custom caps** (trust-adjusted):
- Trust ≥80: cap = 3 (high-performers can handle more parallelism)
- Trust 60-79: cap = 2 (default)
- Trust <60: cap = 1 (juniors focus on quality over quantity)

---

### 2. Difficulty Quota Balance

**Problem**: High-trust engineers cherry-pick easy tasks (5 tool_use estimates), low-trust engineers stuck with hard tasks (15 tool_use estimates).

**Rule**: Each engineer must maintain balanced difficulty distribution. Target: 50% easy (≤8 tool_uses), 50% hard (>8 tool_uses) over rolling 2-week window.

**Enforcement**: Weekly CTO review (Thursday tech debt tally) checks each engineer's claimed task difficulty distribution via CIEU query. If engineer >70% easy tasks → CTO manually assigns 2 hard tasks next week to rebalance.

**Visibility**: Dashboard shows per-engineer difficulty distribution % (transparency pressure).

---

### 3. Forced Rotation (No 3-in-a-row Same Task Type)

**Problem**: Engineer specializes in one narrow task type (e.g., only claims "add ForgetGuard rule" tasks), never develops cross-cutting skills.

**Rule**: No engineer can claim same task template 3 times in a row.

**Enforcement**: `dispatch_board.py claim` checks engineer's last 2 claimed tasks. If both match same template as new claim → claim fails with error "rotation violation, claim different task type".

**Template taxonomy** (from tier-routing v1 pre-auth templates):
- ForgetGuard rule
- Hook script extension
- Test assertion
- Charter update
- File rename
- CIEU query script
- Log rotation
- Documentation

**Exception**: Emergency tasks (P0 urgency) bypass rotation rule.

---

### 4. Senior Mentor Mandate (≥1 Pairing Session/Week)

**Rule**: Engineers with trust ≥70 MUST participate in ≥1 pair-programming session per week as senior mentor.

**Rationale**: Prevent high-trust engineers from isolating themselves, force knowledge transfer.

**Enforcement**: Friday EOD cron checks `governance/pair_sessions_log.md` for each trust ≥70 engineer. If zero pair sessions this week → trust score drops 10pt + CEO notification.

**Pairing request priority**: When junior requests pair, senior with lowest pair-count this week gets assigned (load balance mentoring).

---

### 5. Top-1 Trust Ranking Cap Reduction (Anti-Runaway)

**Problem**: Highest-trust engineer gets all first-pick advantages, continuously widens gap vs #2 engineer. Positive feedback loop → monopoly.

**Rule**: Engineer with #1 trust ranking gets 25% claim-rate cap reduction.

**Example**:
- Maya trust = 82 (#1 ranking), Ryan trust = 78 (#2)
- Maya's cap = 3 tasks/h * 0.75 = 2.25 → rounds down to 2 tasks/h
- Ryan's cap = 3 tasks/h (no penalty)

**Rationale**: Force top performer to slow down, give #2/#3 engineers opportunity to catch up.

**Duration**: Cap reduction persists until another engineer surpasses #1 ranking (dynamic rebalancing).

**Visibility**: Dashboard shows current #1 engineer + cap reduction status.

---

## Part 6 — Migration Path

**Integration dependencies**:
- Dispatch board infra (CZL-68, Ryan in-flight) — MUST ship before trust-weighted claim race
- Tier-routing v1 (governance/tiered_routing_protocol_v1.md) — already shipped, pre-auth templates defined
- Sync layer (CZL-67) — already LIVE, CIEU coordinator + ForgetGuard ready

### Phase 1: Trust Score Bootstrap (Immediate Dependency)

**Ryan task CZL-69** (inline below):
- Implement `scripts/trust_score_update.py` (query CIEU for historical task completions, calculate formula v1.0)
- Generate initial `governance/engineer_trust_scores.json` (Maya/Ryan/Leo/Jordan based on existing CIEU history)
- Add 5 new engineers with trust=50 (Alex/Priya/Carlos/Sofia + Maya-data dual-hat)
- Cron job: Friday EOD auto-run `trust_score_update.py`
- Tests: `pytest tests/platform/test_trust_score.py -q` (≥3 tests: formula_calculation, decay_rule, cron_integration)

**Acceptance**: `engineer_trust_scores.json` exists + 9 engineers listed + cron job LIVE + tests PASS.

**Timeline**: 2h

---

### Phase 2: Pair-Programming First Session (Depends on: Phase 1 Complete)

**CTO Ethan task** (manual coordination):
- Assign first 2 pair sessions: (Jordan+Maya on template validation), (Alex+Ryan on CVE scan)
- Log sessions to `governance/pair_sessions_log.md`
- Verify dual signoff on receipts (both engineers paste 5-tuple)

**Acceptance**: 2 pair sessions completed + logged + dual signoff verified.

**Timeline**: 3h (2 sessions * 1.5h each)

---

### Phase 3: Trust Score Dashboard + Periodic Email (Depends on: Phase 1 Complete)

**Samantha task CZL-70** (inline below):
- Write Secretary responsibility (triggered after every N trust score updates, N=10 default): read `engineer_trust_scores.json` → generate leaderboard email (top 3, biggest Δ, mentor champion)
- Integrate into `agents/Secretary.md` §Weekly Responsibilities
- First email sent after Phase 1 trust scores bootstrapped (test run)

**Acceptance**: First leaderboard email sent + Secretary charter updated + no manual prompting required (autonomous trigger).

**Timeline**: 1h

---

### Phase 4: Dispatch Board Trust Integration (Depends on: CZL-68 Dispatch Board Infra Complete)

**Ryan task CZL-71** (extends CZL-68):
- Modify `dispatch_board.py claim` to check trust score before allowing claim (trust-weighted race resolution)
- Implement claim-rate cap enforcement (check current claimed count, apply per-trust-tier caps)
- Implement forced rotation check (last 2 claimed tasks, template match)
- Tests: `pytest tests/platform/test_dispatch_board_trust.py -q` (≥5 tests: trust_weighted_claim, claim_rate_cap, rotation_enforcement, senior_mentor_mandate_check, top1_cap_reduction)

**Acceptance**: Trust-weighted claim LIVE + caps enforced + rotation enforced + tests PASS.

**Timeline**: 3h

---

### Phase 5: Pre-Auth Template Extension (Depends on: Phase 1 Complete, Parallel with Phase 4)

**Maya task CZL-72** (governance engineer):
- Update `governance/tiered_routing_protocol_v1.md` §3 Pre-Authorization Templates with trust-tiered extensions (trust ≥70 / ≥85 templates)
- Add ForgetGuard rule `tier_routing_trust_violation` (mode=warn, triggers when trust <70 engineer attempts trust ≥70 template)
- Modify tier classifier to check `engineer_trust_scores.json` before applying template
- Tests: `pytest tests/governance/test_tier_routing_trust.py -q` (≥3 tests: trust70_template_allowed, trust60_template_denied, trust85_breaking_api_allowed)

**Acceptance**: Tier-routing v1 updated + ForgetGuard rule LIVE + classifier checks trust + tests PASS.

**Timeline**: 2h

---

### Phase 6: CTO Event-Driven Ritual Launch (Depends on: Phase 5 Complete)

**CTO Ethan task** (manual):
- Monday: First T1 sample review (5 tasks from trust <75 pool, trust ≥75 excluded)
- Tuesday: First spec sync with Board (alignment on tech debt budget, new initiatives)
- Wednesday: First 4x 15min 1-on-1s (Leo/Maya/Ryan/Jordan)
- Thursday: First tech debt tally + difficulty quota balance check
- Friday: First retrospective (time allocation review: did I hit 40% architecture / 25% code review / 15% tech debt / 10% mentor / 10% cross-cutting?)

**Deliverable**: First ritual cycle complete (triggered per CTO role v2 Part 4 event conditions), all 5 rituals logged to `.claude/cto_ritual_log.md`.

**Timeline**: 1 week

---

### Phase 7: Anti-Monopoly Full Enforcement (Depends on: Phase 4+5 Complete)

**Ryan + Maya joint task CZL-73**:
- Difficulty quota balance: Weekly cron job `scripts/difficulty_quota_check.py` queries CIEU for per-engineer task difficulty distribution, emits warnings if >70% easy tasks
- Senior mentor mandate: Friday EOD cron job `scripts/mentor_mandate_check.py` scans `pair_sessions_log.md` for trust ≥70 engineers with zero pair sessions, applies -10pt trust penalty + CEO notification
- Top-1 cap reduction: Modify `dispatch_board.py claim` to check current #1 trust ranking, apply 25% cap reduction dynamically
- Dashboard: Add anti-monopoly metrics to `engineer_trust_scores.json` (difficulty_distribution %, pair_sessions_count, top1_cap_active boolean)
- Tests: `pytest tests/governance/test_anti_monopoly.py -q` (≥4 tests: difficulty_quota_violation, mentor_mandate_penalty, top1_cap_applied, rotation_3_in_row_blocked)

**Acceptance**: All 5 anti-monopoly mechanisms LIVE + dashboard updated + tests PASS + first enforcement actions logged (if any violations detected).

**Timeline**: 3h

---

## Inline Task Cards

### Task CZL-69: Trust Score Bootstrap (Ryan)

**Engineer**: ryan-platform  
**Priority**: P0 (blocks Phase 1)  
**Tier**: T1 (single engineer, ≤15 tool_uses)

**Acceptance Criteria**:
- [ ] `scripts/trust_score_update.py` exists (≤200 lines, implements formula v1.0)
- [ ] Query CIEU for historical task completions (success_rate, e1_mismatch_ratio, hallucination_count, on_time_delivery_bonus)
- [ ] Generate `governance/engineer_trust_scores.json` with 9 engineers (Maya 82, Ryan 78, Leo 65, Jordan 70, Alex/Priya/Carlos/Sofia 50)
- [ ] Cron job integration: `scripts/trust_score_update.py` runs every Friday EOD (via governance_boot.sh or systemd timer)
- [ ] Decay rule: trust -= 5pt for engineers with last_task_at >7d ago
- [ ] Tests: `pytest tests/platform/test_trust_score.py -q` (≥3 tests: formula_calculation, decay_rule, initial_bootstrap)
- [ ] CIEU events: `TRUST_SCORE_UPDATED` emitted on each score recalculation
- [ ] No files outside `scripts/`, `governance/`, `tests/platform/` modified
- [ ] Commit message: `[L3→L4] feat(platform): trust score quantification + event-driven update (CZL-69)`

**Files in scope**: `scripts/trust_score_update.py`, `governance/engineer_trust_scores.json`, `tests/platform/test_trust_score.py`

**Yt+1**: Trust score infra shipped + initial scores bootstrapped + cron job LIVE + tests PASS + commit hash available.

**Rt+1 criteria**:
- `0.0` if all 9 acceptance criteria checked + 3 tests PASS + commit exists + CIEU event emitted
- `1.0` if infra incomplete or tests fail or no cron integration
- `0.5` if infra works but decay rule missing or tests <3

---

### Task CZL-70: Trust Score Leaderboard Email (Samantha)

**Engineer**: secretary  
**Priority**: P1  
**Tier**: T1 (single engineer, ≤10 tool_uses)

**Acceptance Criteria**:
- [ ] Update `agents/Secretary.md` §Weekly Responsibilities: Add "Friday EOD trust score leaderboard email"
- [ ] Script: `scripts/trust_score_leaderboard_email.py` (≤100 lines, reads `engineer_trust_scores.json`, formats email)
- [ ] Email format: Top 3 engineers by trust score, biggest Δ up/down this week, mentor champion (most pair sessions)
- [ ] Trigger: Autonomous (no manual prompting required, triggered after every N trust score updates per Secretary responsibility)
- [ ] First test email sent to Board (liuhaotian2024@gmail.com) after Phase 1 trust bootstrap complete (dry-run)
- [ ] No files outside `agents/`, `scripts/`, `governance/` modified
- [ ] Commit message: `[L3→L4] feat(secretary): event-driven trust score leaderboard email (CZL-70)`

**Files in scope**: `agents/Secretary.md`, `scripts/trust_score_leaderboard_email.py`

**Yt+1**: Secretary charter updated + leaderboard script shipped + first email sent + autonomous trigger LIVE.

**Rt+1 criteria**:
- `0.0` if all 6 acceptance criteria checked + first email sent + no manual prompting required
- `1.0` if script missing or email not sent or requires manual trigger
- `0.5` if email sent but charter not updated or script hardcoded (not autonomous)

---

### Task CZL-71: Dispatch Board Trust Integration (Ryan)

**Engineer**: ryan-platform  
**Priority**: P0 (blocks Phase 4)  
**Tier**: T2 (extends existing CZL-68 dispatch board, ≥3 features, >15 tool_uses estimated)

**Acceptance Criteria**:
- [ ] Modify `dispatch_board.py claim` to read `engineer_trust_scores.json` before allowing claim
- [ ] Trust-weighted race resolution: If 2 engineers claim simultaneously, higher trust wins (with ≤2s window tolerance)
- [ ] Claim-rate cap enforcement: Check current claimed count (status=claimed, claimed_by=engineer_id), apply per-trust-tier caps (trust ≥80: 3, 60-79: 2, <60: 1)
- [ ] Forced rotation check: Query engineer's last 2 claimed tasks, match template type, block if 3-in-a-row (except P0 urgency)
- [ ] Top-1 cap reduction: Query current #1 trust ranking, apply 25% cap reduction (e.g., 3 → 2)
- [ ] Tests: `pytest tests/platform/test_dispatch_board_trust.py -q` (≥5 tests: trust_weighted_claim, claim_rate_cap_enforced, rotation_3_blocked, top1_cap_applied, P0_bypasses_rotation)
- [ ] CIEU events: `CLAIM_TRUST_WEIGHTED`, `CLAIM_RATE_CAP_HIT`, `ROTATION_VIOLATION`, `TOP1_CAP_APPLIED`
- [ ] No files outside `scripts/`, `governance/`, `tests/platform/` modified
- [ ] Commit message: `[L3→L4] feat(platform): trust-weighted dispatch board claim + anti-monopoly caps (CZL-71)`

**Files in scope**: `scripts/dispatch_board.py`, `governance/engineer_trust_scores.json`, `tests/platform/test_dispatch_board_trust.py`

**Yt+1**: Dispatch board trust integration LIVE + 4 anti-monopoly mechanisms enforced + 5 tests PASS + CIEU events emitted + commit hash available.

**Rt+1 criteria**:
- `0.0` if all 9 acceptance criteria checked + 5 tests PASS + commit exists + CIEU events verified
- `1.0` if <4 mechanisms implemented or tests fail or no CIEU integration
- `0.5` if mechanisms work but tests <5 or rotation/cap logic incomplete

---

### Task CZL-72: Pre-Auth Template Trust Extension (Maya)

**Engineer**: maya-governance  
**Priority**: P1  
**Tier**: T1 (governance rule update, ≤12 tool_uses)

**Acceptance Criteria**:
- [ ] Update `governance/tiered_routing_protocol_v1.md` §3 Pre-Authorization Templates with 3 trust tiers (default, trust ≥70, trust ≥85)
- [ ] Trust ≥70 extensions: mode=log ForgetGuard rules, modify existing hook function logic, cross-file rename ≤3 files, minor API change (add optional param)
- [ ] Trust ≥85 extensions: mode=deny ForgetGuard rules (with CTO review), breaking API change proposal, delete deprecated code ≤50 lines
- [ ] Add ForgetGuard rule `tier_routing_trust_violation` (mode=warn): Triggers when trust <70 engineer attempts trust ≥70 template
- [ ] Modify tier classifier (`scripts/tier_classifier.py` or inline in CEO dispatch logic) to check `engineer_trust_scores.json` before applying template
- [ ] Tests: `pytest tests/governance/test_tier_routing_trust.py -q` (≥3 tests: trust70_template_allowed, trust60_template_escalated_to_t2, trust85_breaking_api_allowed)
- [ ] No files outside `governance/`, `scripts/`, `tests/governance/` modified
- [ ] Commit message: `[L3→L4] feat(governance): trust-tiered pre-auth templates + tier_routing_trust_violation rule (CZL-72)`

**Files in scope**: `governance/tiered_routing_protocol_v1.md`, `governance/forget_guard_rules.yaml`, `scripts/tier_classifier.py`, `tests/governance/test_tier_routing_trust.py`

**Yt+1**: Tier-routing v1 updated with 3 trust tiers + ForgetGuard rule LIVE + classifier checks trust + tests PASS + commit hash available.

**Rt+1 criteria**:
- `0.0` if all 8 acceptance criteria checked + 3 tests PASS + commit exists + ForgetGuard rule verified
- `1.0` if spec not updated or classifier unchanged or tests fail
- `0.5` if spec updated but ForgetGuard rule missing or classifier hardcoded (not reading trust_scores.json)

---

### Task CZL-73: Anti-Monopoly Full Enforcement (Ryan + Maya)

**Engineer**: ryan-platform (lead), maya-governance (pair)  
**Priority**: P1  
**Tier**: T2 (cross-engineer, ≥2 scripts, >15 tool_uses)

**Acceptance Criteria**:
- [ ] Difficulty quota balance: `scripts/difficulty_quota_check.py` (≤150 lines, queries CIEU for per-engineer task difficulty distribution, emits warnings if >70% easy tasks)
- [ ] Weekly cron job: `difficulty_quota_check.py` runs every Thursday EOD (integrated into governance_boot.sh or systemd timer)
- [ ] Senior mentor mandate: `scripts/mentor_mandate_check.py` (≤100 lines, scans `governance/pair_sessions_log.md`, applies -10pt trust penalty for trust ≥70 engineers with zero pair sessions this week)
- [ ] Mentor mandate cron job: `mentor_mandate_check.py` runs every Friday EOD (before trust_score_update.py)
- [ ] Dashboard extension: Add 3 fields to `engineer_trust_scores.json`: `difficulty_distribution` (dict: {easy: %, hard: %}), `pair_sessions_count_this_week`, `top1_cap_active` (boolean)
- [ ] Tests: `pytest tests/governance/test_anti_monopoly.py -q` (≥4 tests: difficulty_quota_violation_detected, mentor_mandate_penalty_applied, top1_cap_calculated, pair_session_count_accurate)
- [ ] CIEU events: `DIFFICULTY_QUOTA_VIOLATION`, `MENTOR_MANDATE_PENALTY`, `TOP1_CAP_ACTIVE`
- [ ] No files outside `scripts/`, `governance/`, `tests/governance/` modified
- [ ] Commit message: `[L3→L4] feat(governance): anti-monopoly full enforcement — difficulty quota + mentor mandate + top1 cap (CZL-73)`

**Files in scope**: `scripts/difficulty_quota_check.py`, `scripts/mentor_mandate_check.py`, `governance/engineer_trust_scores.json`, `tests/governance/test_anti_monopoly.py`

**Yt+1**: Anti-monopoly mechanisms LIVE + dashboard updated + cron jobs scheduled + tests PASS + CIEU events emitted + commit hash available.

**Rt+1 criteria**:
- `0.0` if all 9 acceptance criteria checked + 4 tests PASS + commit exists + cron jobs verified + CIEU events logged
- `1.0` if <2 mechanisms implemented or tests fail or no dashboard extension
- `0.5` if mechanisms work but cron jobs not integrated or tests <4 or CIEU events missing

---

## Summary (Board Review)

**6 Parts**:
1. Trust score quantification (formula, storage, decay, display)
2. 5 new engineer charters (data/security/ml/perf/compliance)
3. Pair-programming protocol (trigger rules, senior mandate, dual signoff)
4. Reward mechanism (pre-auth expansion, first-pick race, reduced oversight, leaderboard)
5. Anti-monopoly quotas (claim cap, difficulty balance, rotation, mentor mandate, top-1 reduction)
6. Migration path (7 phases, 5 inline task cards)

**Integration**:
- Dispatch board (CZL-68) — Ryan in-flight, blocks Phase 4
- Tier-routing v1 — already shipped, extends with trust tiers in Phase 5
- Sync layer (CZL-67) — already LIVE, CIEU + ForgetGuard ready
- CTO role v2 — event-driven ritual (sample / 1-on-1s / tech debt per trigger conditions) starts Phase 6

**Inline task cards**:
- CZL-69 (Ryan): Trust score bootstrap (Phase 1)
- CZL-70 (Samantha): Leaderboard email (Phase 3)
- CZL-71 (Ryan): Dispatch board trust integration (Phase 4)
- CZL-72 (Maya): Pre-auth template trust extension (Phase 5)
- CZL-73 (Ryan+Maya): Anti-monopoly full enforcement (Phase 7)

**Dependency chain**: Phase 1 (immediate) → Phase 2+3 (parallel after 1) → Phase 4+5 (parallel after CZL-68 + Phase 1) → Phase 6 (after 5) → Phase 7 (after 4+5). Wall-clock duration depends on engineer availability + claim velocity, not hardcoded timeline.

**Status**: [L1 SPEC SHIPPED]  
**Next action**: CEO dispatches inline task cards CZL-69/70/71/72/73 to respective engineers (Ryan/Samantha/Maya)  
**Board approval**: Pending (this spec serves as Board review artifact)
