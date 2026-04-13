# Maturity Taxonomy v1 — CEO Internal Charter

**Status**: L2 IMPL — Written and adopted into CEO operating system  
**Effective Date**: 2026-04-13  
**Authority**: Board directive 2026-04-13 + AMENDMENT-019  
**Owner**: Aiden Liu (CEO)  
**Enforcement**: CIEU hook `maturity_tag_check.py` + Secretary weekly audit

---

## Purpose

This taxonomy provides a deterministic framework for classifying the completion state of any work product, from idea to adoption. It eliminates ambiguity in status communication between agents and Board.

**Core principle**: "Done" means different things at different maturity levels. This taxonomy makes the distinction explicit and auditable.

---

## The 5 Maturity Levels (L0-L5)

### L0 IDEA
**Definition**: Verbal or written concept, zero executable artifact, no external validation.

**Characteristics**:
- Exists in conversation, notes, or proposals (pre-submission)
- No commit hash, no file in repo (or file exists but is not reviewed/submitted)
- Cannot be executed, tested, or deployed
- Validation: none

**Evidence**: None required (pre-artifact state)

**Example**:
- "Let's build a session continuity guardian" (spoken in meeting)
- Draft proposal sitting in agent's working memory, not yet written to file

**Transition to L1**: Submit written proposal + get commit hash OR write task card with acceptance criteria

---

### L1 SPEC
**Definition**: Proposal submitted, design documented, task card created. Artifact exists but implementation has not started.

**Characteristics**:
- Written specification exists (proposal / design doc / task card)
- Commit hash available OR task card ID in `.claude/tasks/`
- Acceptance criteria defined
- Cannot be executed yet (no code/content produced)

**Evidence Required**:
- File path + commit hash, OR
- Task card ID + acceptance criteria list

**Example**:
- `reports/proposals/charter_amendment_019_article_11_v2_maturity_layer.md` [L1] — proposal written, awaiting Board approval
- `.claude/tasks/cto-20260413-phase3-architecture-skeleton.md` [L1] — task card written, not started

**Transition to L2**: Write code / draft content / deploy infrastructure (pre-test)

---

### L2 IMPL
**Definition**: Code written, content drafted, infrastructure deployed, but NOT YET TESTED or validated.

**Characteristics**:
- Implementation file exists in repo
- Commit hash available
- Code compiles (if applicable) but tests may not pass
- Content exists but not reviewed
- Feature deployed to staging but not validated

**Evidence Required**:
- Implementation file path + commit hash, OR
- Content file path + word count / line count

**Example**:
- `scripts/maturity_tag_check.py` [L2] — hook code written, tests not run yet
- `content/blog/ystar_defuse_v3.md` [L2] — blog post drafted, CMO review pending
- `knowledge/ceo/charter/maturity_taxonomy_v1.md` [L2] — this file, written but not integrated into Article 11 yet

**Transition to L3**: Run tests + pass, OR peer review + approval, OR validation complete

---

### L3 TESTED
**Definition**: Tests pass, peer review approved, validation complete. Work product verified as functional but NOT YET in production.

**Characteristics**:
- All tests pass (for code)
- Peer review approved (for content/design)
- Validation checklist complete (for infrastructure)
- Still in staging/development environment (not live)

**Evidence Required**:
- Test output (pass count, coverage %), OR
- Review approval record (reviewer name + timestamp), OR
- Validation report (checklist with all items checked)

**Example**:
- `scripts/session_boot_yml.py` [L3] — 86 tests pass, not yet integrated into governance_boot.sh
- `reports/proposals/charter_amendment_007_ceo_operating_system.md` [L3] — Board reviewed and approved, not yet adopted by CEO
- `ystar doctor --layer1` L0 fixes [L3] — fixes tested locally, not merged to main

**Transition to L4**: Deploy to production / publish content / merge to main + activate

---

### L4 SHIPPED
**Definition**: Production running, content published, feature live. Work product is in production environment and accessible to intended users.

**Characteristics**:
- Code deployed to production
- Content published (blog live, documentation public)
- Feature flag enabled in production
- Monitoring active (can observe live behavior)
- Users CAN access, but adoption not yet verified

**Evidence Required**:
- Production URL / live endpoint, OR
- Publication timestamp + public URL, OR
- Monitoring dashboard showing live traffic

**Example**:
- `ystar hook-install` [L4] — hook daemon running on user machines, monitoring active
- `governance/WORKING_STYLE.md` Article 11 v1 [L4] — published in repo, all agents can read
- AMENDMENT-015v2 LRS [L4] — C5/C7 scripts in production, not yet verified user adoption

**Transition to L5**: Capture ≥1 real user actively using + usage metric

---

### L5 ADOPTED
**Definition**: ≥1 real user/consumer actively using the work product. Adoption verified by usage metric, not just availability.

**Characteristics**:
- User-initiated usage (not agent self-testing)
- Usage metric exists (call count, page views, feature engagement)
- User feedback captured (explicit or implicit)
- Demonstrates real-world value delivery

**Evidence Required**:
- Usage log (user_id + timestamp + action), OR
- Analytics data (session count, feature usage count), OR
- User feedback (GitHub issue, support ticket, testimonial)

**Example**:
- `ystar doctor` [L5] — CTO ran it 47 times in last 7 days (CIEU audit log as evidence)
- `governance_boot.sh` [L5] — all 6 C-suite agents boot with it every session (boot count metric)
- AMENDMENT-007 CEO OS [L5] — CEO uses "今日发货" section in every daily report (usage pattern in git history)

**Beyond L5**: No higher maturity level. L5 is terminal state. Work products can scale (10 users → 1000 users) but remain L5.

---

## Application Rules

### Rule 1: All Status Communication Must Include L-Tag

**Applies to**:
- CEO → Board daily reports
- Agent → Agent handoff notes
- Git commit messages (when describing completion)
- Task card status updates
- CIEU audit log `active_task.py update` calls

**Format**:
- `[LX]` — minimal tag (e.g., "Session boot script [L3]")
- `LX STATE_NAME` — verbose tag (e.g., "Session boot script L3 TESTED")

**Examples**:
- ✅ "AMENDMENT-019 [L1] submitted for Board approval"
- ✅ "Hook code [L2] written, tests pending"
- ✅ "Blog post [L4] published, waiting for analytics"
- ❌ "Session boot script completed" (missing L-tag)
- ❌ "Feature shipped" (missing L-tag)

### Rule 2: Highest Achieved Level Wins

When an item progresses through multiple levels in one action, tag with the **highest level achieved**:

- "Wrote code [L2] and ran tests [L3]" → tag as `[L3]`
- "Deployed to prod [L4] and confirmed user adoption [L5]" → tag as `[L5]`

### Rule 3: Maturity Level Cannot Decrease

Once an item reaches LX, it cannot regress to L(X-1). If implementation breaks (L4 → broken), it's a **new incident**, not a maturity regression. Original item remains L4, new incident starts at L0.

Example:
- `ystar doctor --layer1` reached L4 (production running)
- Bug discovered, tests now fail
- Correct framing: "ystar doctor L4 SHIPPED has regression bug [L0 IDEA for fix], root cause analysis [L1] in progress"
- Incorrect framing: "ystar doctor regressed to L2" ❌

### Rule 4: L-Tag Violations Trigger CIEU Audit Event

CIEU hook `maturity_tag_check.py` scans:
- Git commit messages
- File writes to `reports/` containing completion keywords
- `active_task.py update` calls

**Completion keywords**: "done", "completed", "finished", "shipped", "deployed", "live", "published", "落盘"

**Violation = keyword present + L-tag absent**

**Action**: Emit CIEU event:
```json
{
  "event_type": "MATURITY_TAG_MISSING",
  "source": "commit_hash OR file_path OR task_id",
  "keyword_detected": "shipped",
  "timestamp": "2026-04-13T15:42:00Z",
  "agent_id": "ceo"
}
```

Secretary reviews all `MATURITY_TAG_MISSING` events weekly, flags repeat offenders.

---

## Self-Check Triggers (Automatic Cognitive Gates)

### Trigger 1: Before Any "Done" Claim
**Question**: What maturity level has this item actually reached?  
**Action**: Consult Verb → L Mapping Table (Appendix) → insert L-tag

### Trigger 2: Before Writing Commit Message
**Question**: Does this commit describe completion of something?  
**If YES**: Insert L-tag based on what was completed (code written = L2, tests pass = L3, deployed = L4)

### Trigger 3: Before Sending Daily Report to Board
**Question**: Does every "今日发货" item have an L-tag?  
**Action**: Scan report, add missing L-tags before sending

### Trigger 4: Before Handoff to Another Agent
**Question**: What maturity state should the receiving agent expect?  
**Action**: Explicitly state L-level in handoff note (e.g., "Task X [L2] code written, you need to test and reach L3")

---

## Verb → Maturity Level Mapping Table (Quick Reference)

| Action Verb / Phrase | Maturity Level | Evidence Type |
|----------------------|----------------|---------------|
| "proposed", "drafted proposal", "designed", "wrote task card" | L1 SPEC | File path + commit hash |
| "wrote code", "implemented", "built feature", "drafted content" | L2 IMPL | Code/content file + commit hash |
| "tests pass", "review approved", "validated", "QA complete" | L3 TESTED | Test output / review record |
| "deployed", "shipped", "live", "published", "merged to main", "上线" | L4 SHIPPED | Production URL / live behavior |
| "user used", "adopted by X", "usage metric", "user feedback received" | L5 ADOPTED | Usage log / analytics / feedback |
| "idea", "concept", "discussed", "brainstormed", "口头" | L0 IDEA | None (pre-artifact) |

**Edge Cases**:
- "Fixed bug" → depends on stage: code fix = L2, tests pass = L3, deployed = L4
- "Refactored" → same as above, depends on current stage
- "Documented" → if published = L4, if drafted = L2, if approved = L3

**When Uncertain**: Default to the **most conservative** (lowest) plausible level. Board prefers under-claiming maturity to over-claiming.

---

## Integration with Article 11 v2

This taxonomy is embedded into Article 11 Phase 2 (Execution) as **Layer 9 maturity gates**. See `governance/WORKING_STYLE.md` Article 11 for full context.

**Key integration points**:
1. **Layer 9.1** = L0 → L1 transition (IDEA → SPEC)
2. **Layer 9.2** = L1 → L2 transition (SPEC → IMPL)
3. **Layer 9.3** = L2 → L3 transition (IMPL → TESTED)
4. **Layer 9.4** = L3 → L4 transition (TESTED → SHIPPED)
5. **Layer 9.5** = L4 → L5 transition (SHIPPED → ADOPTED)

Each transition emits `MATURITY_TRANSITION(item_id, from_L, to_L, evidence)` CIEU event.

---

## Secretary Enforcement Protocol

**Weekly Audit** (every Monday):
1. Query CIEU database: `SELECT * FROM events WHERE event_type = 'MATURITY_TAG_MISSING' AND timestamp > last_monday`
2. Group by `agent_id`, count violations per agent
3. Report to Board: `reports/secretary/weekly_maturity_audit_YYYY-MM-DD.md`
4. Flag agents with >3 violations in one week for re-training

**Educational Approach** (first 2 weeks after AMENDMENT-019 adoption):
- Violations = warning only, no penalty
- Secretary sends direct message to violating agent with correct L-tag example
- After 2 weeks: violations count toward performance review

---

## Enforcement Lifecycle

| Phase | Timeline | Enforcement Level |
|-------|----------|-------------------|
| **Soft Launch** | Week 1-2 after AMENDMENT-019 L4 | Warning only, educational |
| **Full Enforcement** | Week 3+ | CIEU events logged, Secretary audit active |
| **Performance Integration** | Month 2+ | Violation count → performance review input |

---

## FAQ

### Q: Do I need L-tags for every single file write?
**A**: No. Only for **status communication** involving completion claims. Internal work files (drafts, notes, experiments) don't need L-tags unless you're reporting them to Board or another agent.

### Q: What if an item is between two levels (e.g., code written but partially tested)?
**A**: Use the **highest fully achieved level**. Partially tested = L2 (code exists, tests incomplete). Only claim L3 when **all** tests pass.

### Q: Can I claim L5 based on agent usage (e.g., CTO using CEO's script)?
**A**: **Yes**, if the usage is real work (not testing). CTO running `session_boot_yml.py` in production = real usage. CEO testing their own script = not L5.

### Q: What if I deployed something but no one has used it yet?
**A**: That's L4 SHIPPED. L5 requires verified usage. Be patient — track analytics, wait for first real user action.

### Q: How do I handle CIEU `MATURITY_TAG_MISSING` events about my commits?
**A**: 
1. Read the event (source commit hash)
2. Identify what was completed and at what level
3. Reply to Secretary with: "Commit [hash] should be tagged [LX]: [reasoning]"
4. Secretary updates audit log
5. Learn the mapping, don't repeat

---

## Revision History

- **v1.0** (2026-04-13): Initial version, integrated with AMENDMENT-019 Article 11 v2
- Status: L2 IMPL — written and adopted by CEO, pending full team integration (L3) and Article 11 v2 activation (L4)

---

**END OF MATURITY TAXONOMY v1 CHARTER**
