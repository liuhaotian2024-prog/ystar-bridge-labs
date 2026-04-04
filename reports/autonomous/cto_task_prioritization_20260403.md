# CTO Task Prioritization Recommendation

**Prepared by:** CEO (Aiden) — Autonomous Session 6  
**Date:** 2026-04-03 16:30  
**Purpose:** Recommend CTO task priorities based on governance analysis + business needs

---

## Executive Summary

**Current situation:** CTO has 8+ pending tasks across multiple categories (governance fixes, 0.49.0 features, research, knowledge building).

**Key finding:** Governance data analysis reveals **CRITICAL P0 blocker** not yet in DIRECTIVE_TRACKER:
- **agent_daemon generic 'agent' ID issue** causing 1,082 governance denials + 188 violations

**Recommendation:** Shift CTO focus to **governance stabilization first**, then resume feature development.

**Rationale:** 
- Current 19% violation rate unsustainable (system accumulating violations faster than resolution)
- 0.48.0 launch success depends on stable governance foundation
- Feature development (0.49.0) will generate more violations if constitutional issues unfixed

---

## Proposed Priority Tiers

### TIER 0 — GOVERNANCE CRITICAL (Execute IMMEDIATELY after Board approval)

**Prerequisite:** Board approves AGENTS.md constitutional repair (BOARD_PENDING § 1)

#### Task 0.1: Apply AGENTS.md Constitutional Repair
**Owner:** CTO (with CEO oversight)  
**Effort:** 2-4 hours  
**Dependencies:** Board approval of BOARD_PENDING § 1  
**Impact:** Reduces violations 60-70% (2,974 → ~1,000)

**Subtasks:**
1. Verify Phase 1 complete (HOW content preserved to knowledge/) ✅ Already done
2. Apply 17 modifications to AGENTS.md per BOARD_PENDING plan
3. Run `ystar doctor --layer1` verification
4. Commit with message "governance: AGENTS.md constitutional repair - WHEN not HOW principle"

**Success criteria:** 
- ✅ All 17 modifications applied
- ✅ `ystar doctor --layer1` passes
- ✅ No HOW content remains in AGENTS.md
- ✅ Obligation Timing Registry created

---

#### Task 0.2: Fix agent_daemon Generic 'agent' ID Issue
**Owner:** CTO  
**Effort:** 1-2 hours  
**Dependencies:** None  
**Impact:** Eliminates 1,082 governance denials + 188 knowledge_gap violations

**Problem:** 
- `scripts/agent_daemon.py` (or similar) uses generic 'agent' ID
- Governance blocks all generic IDs (security + auditability requirement)
- Results in 1,082 `intervention_gate:deny` events
- 188 violations attributed to 'agent' (untraceable actor)

**Solution:**
1. Find where agent_daemon sets agent_id (likely `scripts/agent_daemon.py` or config)
2. Change to specific identity: `ystar-daemon` or `ystar-orchestrator`
3. Update any hardcoded 'agent' references in governance checks
4. Test: `python scripts/agent_daemon.py` → verify CIEU events show new agent_id
5. Run for 1 hour → verify no new `intervention_gate:deny` events

**Success criteria:**
- ✅ No new `intervention_gate:deny` events for 1 hour
- ✅ All daemon events show specific agent_id (not 'agent')
- ✅ CIEU violations stop accumulating from agent_daemon

**Files to check:**
- `scripts/agent_daemon.py`
- `ystar/governance/agent_identity.py` (if exists)
- `.ystar_session.json` (agent_id field)

---

### TIER 1 — GOVERNANCE VERIFICATION (Within 48h of Tier 0 completion)

#### Task 1.1: Run ystar doctor --layer2 --design-debt
**Owner:** CTO  
**Effort:** 30 minutes  
**Dependencies:** Tier 0 complete  
**Impact:** Identify design debt preventing future violations

**Purpose:** Now that constitutional repair is applied, run deep layer2 analysis to find:
-断裂机制 (broken mechanisms)
- 设计债 (design debt)
- 隐藏的governance gaps

**Deliverable:** `reports/cto/design_debt_YYYY-MM-DD.md`

**Next steps if issues found:** Add to DIRECTIVE_TRACKER as P1 tasks

---

#### Task 1.2: 48-Hour Governance Monitoring
**Owner:** CTO (with CEO support)  
**Effort:** 15 min/day × 2 days = 30 minutes total  
**Dependencies:** Tier 0 complete  
**Impact:** Verify constitutional repair effectiveness

**Daily checks (morning + evening):**
1. `ystar doctor --layer1` (must pass)
2. Query CIEU violations trend:
   ```python
   # Check if violations decreasing
   SELECT date(created_at, 'unixepoch') as day, COUNT(*) 
   FROM cieu_events 
   WHERE event_type LIKE '%violation%' 
   GROUP BY day 
   ORDER BY day DESC 
   LIMIT 7
   ```
3. Check top violation types (should shift away from acknowledgement_omission)

**Success criteria:** 
- ✅ Violations decrease 60-70% within 48h
- ✅ `required_acknowledgement_omission` no longer top violation type
- ✅ No new categories of violations appear

**If violations don't decrease:** Escalate to Board (constitutional repair ineffective, need deeper fix)

---

### TIER 2 — KNOWLEDGE BUILDING (Parallel to Tier 0-1, non-blocking)

#### Task 2.1: CTO Weekly Reading + Knowledge Self-Bootstrap
**Owner:** CTO  
**Effort:** 2 hours/week (can start immediately)  
**Dependencies:** None (parallel work)  
**Impact:** Long-term capability building

**Status:** ❌ Not started (DIRECTIVE_TRACKER #018-020.6d)

**Recommended focus areas (based on current gaps):**
1. **Week 1:** SQLite optimization (CIEU DB growing rapidly, 15MB+)
2. **Week 2:** Python asyncio + daemon architecture (agent_daemon improvements)
3. **Week 3:** Governance policy languages (inspiration for Y*gov DSL)
4. **Week 4:** Testing strategies for stateful systems (CIEU testing gaps)

**Deliverable:** `knowledge/cto/weekly_YYYY-MM-DD.md` (reading notes + applications)

---

#### Task 2.2: 三仓库整合方案研究
**Owner:** CTO  
**Effort:** 4-6 hours  
**Dependencies:** None (parallel work)  
**Impact:** Medium-term (0.49.0+ feature ideas)

**Status:** ❌ Queued (DIRECTIVE_TRACKER 三仓库.1)

**Current priority:** DEFERRED until governance stabilized

**Rationale:** 
- Integration research is valuable but not urgent
- CTO time better spent on governance fixes (higher ROI)
- Can resume after 48h monitoring shows stability

**Recommended timeline:** Post-0.48.0 launch (Week 2-3)

---

### TIER 3 — FEATURE DEVELOPMENT (After governance stable)

#### Task 3.1: 0.49.0 Feature Development
**Owner:** CTO  
**Effort:** 180-220 hours (per implementation_plan_0.49.0.md)  
**Dependencies:** Governance stable (Tier 0-1 complete)  
**Impact:** High (customer-driven features)

**Status:** ⏳ Detailed plan exists (Session 5 产出)

**Recommended approach:**
1. **Wait for 0.48.0 launch feedback** (1-2 weeks post-launch)
2. **Prioritize P0 features** based on actual user pain points:
   - If users struggle with git hook: P0 = Direct Python API
   - If Windows users blocked: P0 = Windows native support
   - If performance complaints: P0 = <0.03ms overhead optimization
3. **Start with highest-ROI feature** (likely Direct Python API — removes git dependency)

**Timeline:** Start Week 3 post-launch (allows 2 weeks of feedback collection)

---

#### Task 3.2: CTO溯源爬虫原型（基于K9Audit模式）
**Owner:** CTO  
**Effort:** 6-8 hours  
**Dependencies:** 三仓库整合方案完成  
**Impact:** Medium (nice-to-have for enterprise customers)

**Status:** ❌ Queued (DIRECTIVE_TRACKER 三仓库.4)

**Current priority:** DEFERRED until 0.49.0 P0 features complete

**Rationale:**
- Interesting prototype but not on critical path
- Enterprise customers care more about governance (core product) than tracing tools
- CTO time better spent on core governance stability + 0.49.0 features

**Recommended timeline:** Post-0.49.0 or assign to future engineering hire

---

### TIER 4 — QUALITY ASSURANCE (Ongoing, low priority)

#### Task 4.1: 文章技术审核 (Series 3)
**Owner:** CTO  
**Effort:** 1-2 hours  
**Dependencies:** None  
**Impact:** Low (CMO waiting but not blocking launch)

**Status:** ❌ Not started (DIRECTIVE_TRACKER #016.3)

**Recommendation:** DEFER until post-0.48.0 launch

**Rationale:**
- Article Series 3 not required for 0.48.0 launch
- CTO time better spent on governance fixes
- CMO can continue drafting Series 4-5 while waiting

**Timeline:** Week 2-3 post-launch (after governance stable)

---

#### Task 4.2: K9 Scout Verification Phase 4
**Owner:** CTO  
**Effort:** 2-3 hours  
**Dependencies:** None  
**Impact:** Low (Phase 1-3 already pass, Phase 4 = advanced features)

**Status:** ❌ Not started (DIRECTIVE_TRACKER K9 Scout.4)

**Recommendation:** DEFER until 0.49.0 complete

**Rationale:**
- Phase 1-3 already verified (core functionality works)
- Phase 4 = advanced features not required for 0.48.0
- CTO time better spent on constitutional repair + 0.49.0

**Timeline:** Q2 2026 or assign to future QA engineer

---

## Recommended Execution Sequence

### Week 1 (Current, Pre-Launch)

**IMMEDIATE (after Board approval):**
1. ✅ Apply AGENTS.md constitutional repair (Task 0.1) — 2-4 hours
2. ✅ Fix agent_daemon generic ID issue (Task 0.2) — 1-2 hours
3. ✅ Run ystar doctor --layer2 (Task 1.1) — 30 minutes
4. ⏳ Start 48h governance monitoring (Task 1.2) — 15 min/day

**PARALLEL (non-blocking):**
5. 🔄 Weekly reading (Task 2.1) — 2 hours, ongoing

**TOTAL EFFORT:** ~6 hours (1 focused day)

---

### Week 2 (Post-Launch, Feedback Collection)

**MONITORING:**
1. ⏳ Continue 48h governance monitoring → extend to 7 days
2. ⏳ HN/GitHub feedback triage (identify 0.49.0 priorities)

**QUALITY:**
3. ✅ 文章技术审核 Series 3 (Task 4.1) — 1-2 hours (if time permits)

**PARALLEL:**
4. 🔄 Weekly reading (Task 2.1) — 2 hours, ongoing

**TOTAL EFFORT:** ~4 hours (maintenance mode)

---

### Week 3-4 (Post-Launch, Feature Development)

**RESEARCH:**
1. ✅ 三仓库整合方案 (Task 2.2) — 4-6 hours

**FEATURE DEVELOPMENT:**
2. ⏳ Start 0.49.0 P0 feature (Task 3.1) — 40-60 hours
   - Pick highest-priority feature based on launch feedback
   - Likely: Direct Python API or Windows native support

**PARALLEL:**
3. 🔄 Weekly reading (Task 2.1) — 4 hours total (2 weeks)

**TOTAL EFFORT:** ~50-70 hours (full-time development)

---

## Deferred Tasks (Not Recommended for Current Sprint)

| Task | Reason for Deferral | Recommended Timeline |
|------|---------------------|---------------------|
| 溯源爬虫原型 (Task 3.2) | Not on critical path | Post-0.49.0 or future hire |
| K9 Scout Phase 4 (Task 4.2) | Phase 1-3 sufficient | Q2 2026 or QA engineer |
| 0.49.0 P1/P2 features | Wait for P0 completion + feedback | Q2 2026 |

---

## Risk Analysis

| Risk | Probability | Impact | Mitigation |
|------|------------|--------|------------|
| Constitutional repair doesn't reduce violations | LOW | HIGH | 48h monitoring catches early, escalate to Board for deeper fix |
| agent_daemon fix breaks existing functionality | LOW | MEDIUM | Test in isolation first, monitor CIEU events for 1 hour |
| CTO time insufficient for all Tier 0-1 tasks | MEDIUM | MEDIUM | CEO can assist with monitoring, CMO can help with documentation |
| 0.48.0 launch reveals new P0 bugs | MEDIUM | HIGH | Governance stable = faster bug fixes, CIEU helps diagnose |

---

## Success Metrics (30 Days)

**Governance Health:**
- ✅ CIEU violation rate < 5% (currently 19%)
- ✅ Zero HARD_OVERDUE obligations for 7 consecutive days
- ✅ `ystar doctor --layer1` passes 100% of time
- ✅ No new violation categories appear

**Development Velocity:**
- ✅ 0.49.0 P0 feature implementation started (Week 3)
- ✅ 三仓库整合方案提交 (Week 3-4)
- ✅ CTO knowledge base has 4 weekly entries

**Quality:**
- ✅ Series 3 article technical review complete (Week 2)
- ✅ Zero production incidents from governance system

---

## Board Decision Required

**Question:** Do you approve this CTO task prioritization?

**Key changes from current DIRECTIVE_TRACKER:**
1. **NEW P0:** Fix agent_daemon generic ID issue (not yet in tracker)
2. **ELEVATED:** AGENTS.md constitutional repair to Tier 0 (currently BOARD_PENDING)
3. **DEFERRED:** 三仓库整合, 溯源爬虫, K9 Phase 4, 文章审核 → post-governance-stable
4. **SHIFTED:** 0.49.0 development → start Week 3 (after launch feedback)

**Options:**
- ✅ **APPROVE** — CTO follows Tier 0→1→2→3 sequence
- ✏️ **REVISE** — Specify which tasks to re-prioritize
- ❌ **REJECT** — Keep current DIRECTIVE_TRACKER priorities

**If APPROVED, CTO will execute Tier 0 tasks immediately after Board approves constitutional repair.**

---

**Prepared by:** CEO Aiden (承远)  
**Date:** 2026-04-03 16:30  
**Input:** governance_data_analysis_20260403.md, DIRECTIVE_TRACKER.md, implementation_plan_0.49.0.md  
**Next step:** Submit to Board for approval
