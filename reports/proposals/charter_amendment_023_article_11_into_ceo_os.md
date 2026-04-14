# AMENDMENT-023: Integrate Article 11 into CEO OS with 3-Layer Enforcement

**Status**: DRAFT → Board Approval Required  
**CTO Owner**: Ethan Wright  
**Engineers**: Maya Patel (Governance), Ryan Park (Platform)  
**Estimated Completion**: 120 minutes from approval  
**L-Tag**: L4 — Systemic Risk (CEO running decisions without 7-layer discipline = naked operation)

---

## §0 Board Command (Direct Quote)

Board detected critical gap:
> "Article 11（7层认知建构方法论）没在 CEO OS (A007) 里整合 — 修"
> "CEO OS 现在没有'主动+被动'实时调用保障机制 — 装"
> "我们真是在裸奔"

**Context**: Article 11 exists in `knowledge/ceo/working_style/WORKING_STYLE.md` as the 7-layer cognitive construction methodology (Y* → Pre-session → Decision → Memory → Execution → Track → Learn). However, A007 CEO Operating System specification does NOT enforce it, and there is ZERO runtime guarantee that CEO actually walks all 7 layers before major decisions.

**Board's Risk Assessment**: Every strategic decision without Article 11 is unauditable improvisation.

---

## §1 Current State Audit

**Article 11 Location**: `knowledge/ceo/working_style/WORKING_STYLE.md` lines 94-167  
**A007 CEO OS Spec**: `AGENTS.md` lines 1-350 (CEO section)  
**Integration Status**: ❌ Article 11 mentioned as aspirational guideline, NOT enforced  
**Runtime Enforcement**: ❌ NONE — no hooks, no CIEU events, no drift detection

**Evidence from CIEU**:
```bash
sqlite3 .ystar_cieu.db "SELECT COUNT(*) FROM cieu WHERE event_type LIKE '%ARTICLE_11%';"
# Expected: 0 (no instrumentation exists)
```

**Gap**: CEO can write strategic decisions, mission statements, or amendments WITHOUT walking layers 0-7. No proactive injection, no in-flight tracking, no post-audit.

---

## §2 Proposed Solution: 3-Layer Enforcement Mechanism

### Layer 1: Proactive Injection (Before Decision)
**Mechanism**: UserPromptSubmit hook detects decision keywords → inject Article 11 reminder into system context  
**Implementation**: Extend `scripts/hook_user_prompt_tracker.py`  
**Trigger Keywords**: `strategy`, `mission`, `amendment`, `重大`, `决策`, `战略`, `deploy`, `launch`, `roadmap`, `pivot`  
**Injection Text**:
```
[ARTICLE_11_REQUIRED] This prompt contains strategic decision keywords. CEO must walk 7-layer cognitive construction:
Layer 0: Y* (ideal contract)
Layer 1: Pre-session context (twin trace)
Layer 2: Decision (counterfactual analysis)
Layer 3: Memory (session state + LRS)
Layer 4: Execution (RAPID + constraints)
Layer 5: Track (emit CIEU events)
Layer 6: Learn (extract lessons)
Emit ARTICLE_11_LAYER_X_COMPLETE events for audit trail.
```

### Layer 2: In-Flight Enforcement (During Decision)
**Mechanism**: CEO emits `ARTICLE_11_LAYER_X_COMPLETE` events as they complete each layer  
**Implementation**: New `scripts/article_11_tracker.py` + governance rules in `governance/forget_guard_rules.yaml`  
**Event Schema**:
```json
{
  "event_type": "ARTICLE_11_LAYER_0_COMPLETE",
  "agent_id": "ceo",
  "evidence": "Y* contract: Werner Vogels — operational excellence, everything fails",
  "timestamp": "2026-04-13T..."
}
```
**Hook Enforcement**: If CEO writes decision-class output (e.g., AMENDMENT file, strategy doc) but lacks recent ARTICLE_11 events → emit `FORGET_GUARD_ARTICLE_11_BYPASS_WARNING`

### Layer 3: Post-Audit (After Decision)
**Mechanism**: Hourly cron scans for "decision keywords in user_message + missing ARTICLE_11 events in time window"  
**Implementation**: Extend `scripts/forget_guard_summary.py`  
**Output**: Emit `ARTICLE_11_DRIFT_SPIKE` when CEO made strategic decisions without layer completion events  
**Reporting**: Add to daily `reports/autonomous/forget_guard_daily.md`

---

## §3 Acceptance Criteria

**All must PASS for L4 clearance:**

| # | Criterion | Verification Method |
|---|---|---|
| AC-1 | Proactive injection works | Write prompt "we should launch new strategy" → check system-context contains `[ARTICLE_11_REQUIRED]` |
| AC-2 | Event emission works | Run `python3 scripts/article_11_tracker.py layer_complete --layer 0 --evidence "..."` → verify CIEU entry |
| AC-3 | Drift detection works | Create decision doc without events → next hourly run emits `ARTICLE_11_DRIFT_SPIKE` |
| AC-4 | E2E integration | Simulate full decision flow → all 3 layers trigger in sequence |
| AC-5 | Tests pass | `pytest tests/test_article_11_enforcement.py` ≥ 3 cases PASS |

**E2E Demo Scenario**:
1. Board writes: "we should pivot strategy to enterprise-first"
2. UserPromptSubmit hook injects Article 11 reminder
3. CEO responds, walks layers 0-7, calls `article_11_tracker.py` for each
4. CEO writes `AMENDMENT_024_ENTERPRISE_PIVOT.md`
5. PreCommit hook checks: decision doc exists + all 7 ARTICLE_11_LAYER_X_COMPLETE events present within 2h window → PASS
6. Hourly audit confirms no drift spike

---

## §4 RAPID Assignment

| Role | Who | Responsibility | Estimate |
|------|-----|----------------|----------|
| **Recommend** | Ethan (CTO) | This 6-pager charter | 15 min |
| **Agree** | Board | Approve charter | 5 min |
| **Perform** | Ryan Park | `article_11_tracker.py` + hook extensions | 60 min |
| **Perform** | Maya Patel | Governance rules + tests | 45 min |
| **Input** | Ethan (CTO) | Review code + e2e test + commit | 30 min |
| **Decide** | Board | Merge approval | 5 min |

**Parallel Work**: Ryan and Maya work simultaneously on separate files (no merge conflicts).

---

## §5 Risks & Mitigation

| Risk | Impact | Mitigation |
|------|--------|------------|
| False positives (inject on non-strategic prompts) | Noise | Tune keyword list based on first 48h CIEU data |
| CEO forgets to call tracker | Drift undetected in real-time | Layer 3 post-audit catches within 1h |
| Performance overhead (hook on every prompt) | Latency | Keyword check is O(1) regex, <5ms |
| Incomplete layer walk (CEO skips layers) | Partial compliance | `article_11_partial_walk` rule triggers warning |
| Governance recursion (Article 11 about Article 11) | Meta-loop | Exempt AMENDMENT-023 itself from enforcement during bootstrap |

---

## §6 Relationship to Existing Amendments

**A007 (CEO OS)**: This amendment EXTENDS A007 by adding runtime enforcement. Does NOT replace A007.  
**A019 (Forget Guard)**: Article 11 enforcement uses Forget Guard infrastructure (rules, CIEU events, hourly summary).  
**A020 (Session Handoff)**: Article 11 Layer 3 (Memory) directly references LRS and session state from A020.  

**Integration Point**: All 3 amendments now form a coherent loop:
- A007 defines WHAT CEO should do (OS spec)
- A019 defines HOW to detect drift (Forget Guard)
- A020 defines HOW to preserve context (LRS)
- **A023 (this)** defines HOW to ENFORCE the loop (Article 11 runtime)

---

## §7 Board Action Required

**Approval Decision**:  
☐ Approve — CTO proceed to implementation  
☐ Revise — Board feedback: _______________  
☐ Reject — Reason: _______________  

**Post-Approval**:
- CTO assigns tasks to Ryan and Maya within 10 minutes
- Target completion: 120 minutes from approval timestamp
- CTO reports commit hash + test results in single message
- Board merges after verification

---

**CTO Signature**: Ethan Wright  
**Draft Timestamp**: 2026-04-13  
**Board Review Pending**
