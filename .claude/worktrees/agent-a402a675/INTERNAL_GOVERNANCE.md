# Y* Bridge Labs — Internal Governance Manual
# Version: 1.0 | Effective: 2026-03-30
# Enforced by Y*gov | Owner: Board of Directors (Haotian Liu)
# Inspired by: Stripe (writing culture), GitLab (transparency), Netflix (accountability), HashiCorp (RFC), Anthropic (safety)

---

## 1. Code & Technical Change Management

### 1.1 RFC Process (HashiCorp model)
Any change that affects architecture, public API, or security MUST have an RFC:
- **RFC-required**: New modules, API changes, security patches, dependency additions, database schema changes
- **RFC-not-required**: Bug fixes, test additions, documentation, internal refactoring under 50 lines

RFC format:
```markdown
# RFC: [Title]
- Author: [agent]
- Date: [YYYY-MM-DD]
- Status: Draft / Review / Approved / Rejected

## Problem
[What problem does this solve?]

## Proposal
[What specifically are we doing?]

## Alternatives Considered
[What else could we do?]

## Risks
[What could go wrong?]

## Test Plan
[How do we verify this works?]
```

RFCs live in `reports/proposals/` and require Board approval for architectural changes.

### 1.2 Code Review (Stripe model)
- **All code must pass 238+ unit tests before push** (non-negotiable)
- CTO runs full test suite before every push: `python -m pytest tests/ -q`
- Any test failure blocks the push until fixed
- Code changes touching security (engine.py, hook.py, cieu_store.py) require extra scrutiny
- Y*gov enforced: `obligation_timing: test_gate: 300` (5 minutes to run tests after any code change)

### 1.3 Release Process (HashiCorp model)
- Semantic versioning: MAJOR.MINOR.PATCH
- `__version__` in __init__.py MUST match pyproject.toml (CASE: version mismatch bug)
- Every release requires: CHANGELOG entry + passing tests + Board approval for MINOR/MAJOR
- PATCH releases (bug fixes): CTO can push autonomously, report to Board after
- MINOR/MAJOR releases: RFC + Board approval required

### 1.4 Technical Debt Tracking
- CTO maintains `reports/tech_debt.md`
- Updated weekly with priority (HIGH/MEDIUM/LOW)
- HIGH debt items cannot accumulate for more than 2 weeks without Board review

---

## 2. Incident Response (Stripe model)

### 2.1 Severity Levels
| Level | Definition | Response Time | Example |
|-------|-----------|---------------|---------|
| **P0** | Product broken, data at risk | 5 minutes | Security vulnerability, CIEU chain broken |
| **P1** | Feature broken, users impacted | 15 minutes | Installation failure, hook not firing |
| **P2** | Bug, no immediate impact | 60 minutes | UI issue, wrong error message |
| **P3** | Enhancement, cosmetic | Next session | Documentation typo, code style |

### 2.2 Incident Commander
- P0/P1: CEO becomes Incident Commander automatically
- All other work stops until resolved
- Y*gov enforced: `P0_blocker` obligation blocks all unrelated work

### 2.3 Postmortem (mandatory for P0/P1)
Every P0/P1 incident requires a postmortem in `knowledge/cases/`:
```markdown
# CASE-XXX: [Title]
- Date, Agent, Severity
- What happened (timeline)
- Root cause (5 whys)
- What we did
- What we'll do differently
- Y*gov product insight (if applicable)
```
Postmortem deadline: 30 minutes after resolution.
Y*gov enforced: `obligation_timing: postmortem: 1800`

---

## 3. Decision Making (Netflix + Dalio model)

### 3.1 Decision Types
| Type | Who Decides | Process | Example |
|------|------------|---------|---------|
| **Type 1** (irreversible) | Board only | RFC + discussion + approval | Architecture change, public launch, legal |
| **Type 2** (reversible) | Department head | Decide, execute, report | Feature implementation, content angle, pricing test |

### 3.2 Disagree-and-Commit
- Debate is encouraged during discussion phase
- Once Board decides, ALL agents execute with full commitment
- Dissent is recorded in CIEU (not suppressed)
- Retrospective after 1 week: was the dissenter right?

### 3.3 Believability Weighting
- Technical decisions: CTO's opinion weighs heaviest
- Market decisions: CMO/CSO weigh heaviest
- Financial decisions: CFO weighs heaviest
- CEO synthesizes; Board decides

---

## 4. Accountability & Performance (Netflix model)

### 4.1 Obligation Tracking (Y*gov enforced)
Every task assigned to any agent is a tracked obligation:
- Created when: Board gives directive, CEO assigns task, cross-department request
- Deadline: set at creation (default 5 min for P0, 15 min for P1, 60 min for P2)
- Tracking: OmissionEngine scans every enforcement cycle
- Escalation: SOFT_OVERDUE → warning + CIEU record. HARD_OVERDUE → agent blocked from other work.

### 4.2 Background Agent Monitoring
When CEO dispatches a background agent (CTO/CMO/CSO sub-task):
1. Record: agent name, task description, start time, deadline
2. Check output file every 60 seconds
3. At deadline: if no output, escalate to Board + take over manually
4. Y*gov enforced: `obligation_timing: background_agent: 300` (5 min default)

### 4.3 Weekly Review
Every Monday, each agent writes to `reports/weekly/YYYY-WW.md`:
- 100 words: what I did, what I learned, what I'll do next
- Key metrics (lines of code, articles written, leads generated, cost tracked)
- Self-assessment: am I improving or degrading?

### 4.4 Case Studies as Accountability
Every significant failure becomes a case study (CASE-XXX):
- Not punishment — learning
- But the PATTERN of repeated failures is accountability signal
- 3+ cases for same agent on same issue → Board review of agent's role

---

## 5. Communication Protocol (GitLab model)

### 5.1 Async-First
- Default: async (write it down, others read when ready)
- Sync (real-time discussion): only for P0/P1 incidents and Board-requested meetings
- Every decision has a written record (session log, CIEU, or DIRECTIVE_TRACKER)

### 5.2 Writing Standards (Stripe culture)
- **Conclusion first**: lead with the answer, not the reasoning
- **Specific over vague**: "238 tests in 1.9s" not "tests pass quickly"
- **Data over opinion**: "deny rate 49%" not "governance seems to work"
- **Short over long**: if you can say it in one sentence, don't use three
- **Platform-aware**: check word limits before writing (CASE-006)

### 5.3 Jinjin Communication Protocol
- Send task → check reply in 60 seconds → record in session log
- Never assume Jinjin hasn't replied — always check
- Jinjin results must be verified before using in decisions
- All Jinjin communications logged in session file

---

## 6. Security & Safety (Anthropic model)

### 6.1 Responsible Development Policy
Before any capability upgrade:
1. What could go wrong? (Pre-mortem)
2. Does this expand attack surface? (CTO assesses)
3. Does this require new governance rules? (CEO assesses)
4. Board approval for any security-adjacent change

### 6.2 Data Classification
| Level | Examples | Who Can Access | Storage |
|-------|---------|---------------|---------|
| **Public** | README, articles, open source code | Everyone | GitHub |
| **Internal** | AGENTS.md, knowledge/, reports/ | All agents | GitHub (private repo) |
| **Confidential** | API keys, passwords, session tokens | Board only | Never in git |
| **Restricted** | User data (future) | Board + legal | Encrypted, access-logged |

### 6.3 Credential Management
- NEVER commit API keys, tokens, passwords
- Use environment variables for all secrets
- GitHub Push Protection is enabled (caught Stripe key in backup)
- If a credential is accidentally exposed: rotate immediately, report to Board

### 6.4 Cross-Model Safety
When delegating to Jinjin (different model):
- Jinjin's outputs are NOT trusted by default
- Factual claims from Jinjin must be verified before use
- Jinjin cannot approve its own suggestions
- Y*gov Path B governs Jinjin's actions

---

## 7. Knowledge Management (GitLab model)

### 7.1 Single Source of Truth
| Information | SSoT Location |
|------------|---------------|
| Governance rules | AGENTS.md |
| Team behavior | CLAUDE.md |
| Internal governance | INTERNAL_GOVERNANCE.md (this file) |
| Technical status | knowledge/ceo/team_dna.md |
| Cases/failures | knowledge/cases/ |
| Daily operations | reports/daily/ |
| Session records | reports/sessions/ |
| Technical proposals | reports/proposals/ |
| Audit data | .ystar_cieu.db |

### 7.2 Knowledge Must Be Written
- If it's not written down, it doesn't exist
- Verbal agreements don't count — write it in a file, commit it
- Every session produces at least: session log + team_dna update + CIEU backup

### 7.3 Knowledge Decay
- Knowledge older than 30 days should be reviewed for accuracy
- Technical snapshots (test count, CIEU records) must be updated every session
- team_dna.md is the living document — never let it go stale

---

## 8. Y*gov Self-Application (Dogfooding)

### 8.1 Every Y*gov Mechanism Applied to This Team

| Y*gov Mechanism | How It Applies to Us |
|----------------|---------------------|
| check() | Every tool call checked against AGENTS.md |
| OmissionEngine | Every task has obligation + deadline |
| CIEU | Every decision recorded with audit trail |
| DelegationChain | Task delegation verifies permission subset |
| GovernanceLoop | Team health assessed every session |
| CausalEngine | Decisions analyzed for causal effect |
| Path A (SRGCS) | Team governance self-improves |
| Path B (CBGP) | Jinjin governed by same framework |
| Contract Legitimacy | AGENTS.md has review schedule |
| InterventionEngine | Repeated failures → capability restriction |
| ObligationTriggers | Directives auto-create tracked obligations |
| ystar report | Generated before every session end |

### 8.2 Self-Audit Schedule
- Every session: CEO checks "am I using all 12 mechanisms?"
- Every week: CTO runs full module integration audit
- Every month: Board reviews governance effectiveness

### 8.3 The Rule of Rules
**If we build a governance capability and don't use it on ourselves, the capability is not real.**
The CTO timeout incident (2026-03-30) proved this. We had OmissionEngine in code but not in practice. From now on: every new Y*gov feature is deployed on our team within the same session it's built.

---

## 9. AGENTS.md Review Schedule

AGENTS.md is our constitutional document. It must not become stale.

| Review Type | Frequency | Reviewer | Y*gov Enforcement |
|------------|-----------|---------|-------------------|
| Accuracy check | Every session | CEO | obligation: 600s |
| Full review | Weekly (Monday) | All agents | obligation: 3600s |
| Board review | Monthly | Board | Board discretion |
| Emergency amendment | On incident | Board | immediate |

Contract legitimacy fields:
- `confirmed_by`: Board (Haotian Liu)
- `valid_until`: 30 days from last review
- `review_triggers`: personnel_change, regulatory_update, security_incident, 30_days_elapsed
