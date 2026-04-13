# AMENDMENT-018: Full Positive Corpus + Behavior↔Whitelist Real-Time Sync

**Status**: PROPOSAL  
**Author**: CTO (Ethan Wright)  
**Date**: 2026-04-13  
**Authority**: Board direct instruction (2026-04-13, verbatim: "把我们labs所有的正常流程，正常的所有的规章制度岗位宪法，岗位间的合规流程，公司项目的正确流程全部列为白名单。并且建立一个agent行为与白名单时时同步机制。")  
**Related**: AMENDMENT-016 (SSoT sync transport), AMENDMENT-017 (role capability envelope)  
**RAPID**: Maya/Ryan/Leo/Ethan each own 1 corpus + sync mechanism  

---

## §0 TL;DR — Board's Paradigm Shift

**Board directive (2026-04-13)**: "把我们labs所有的正常流程，正常的所有的规章制度岗位宪法，岗位间的合规流程，公司项目的正确流程全部列为白名单。并且建立一个agent行为与白名单时时同步机制。"

**What this means**: Governance shifts from "police catching bad behavior" to "coach guiding toward correct behavior." Instead of only encoding deny rules, we now encode the full positive corpus of all legitimate workflows. Every agent action is mapped to the whitelist in real-time. Matches → reinforcement. Drifts → teaching moment.

**ROI**: This is the fundamental paradigm shift from punitive compliance to capability coaching. Whitelist is the single source of truth for "what Y* Bridge Labs agents should do," not just "what they must not do."

**Acceptance**: 7 sub-corpora built + behavior↔whitelist mapping emits CIEU events + ≥80% coverage within 72h.

---

## §1 Current State Audit — Evidence Pack `85b5c42`

### 1.1 Existing Rule Sources (Pre-AMENDMENT-018)

Today (2026-04-13), Y*gov governance rules are scattered across:

| Location | Type | Coverage | Machine-Readable |
|----------|------|----------|------------------|
| `.ystar_session.json` → `contract.deny` | Path deny list | 100% for listed paths | ✅ YAML dict |
| `.ystar_session.json` → `contract.deny_commands` | Command deny list | 100% for listed commands | ✅ YAML list |
| `AGENTS.md` Iron Rules 1-3 | Constitutional prohibitions | 3 rules | ❌ Prose |
| `governance/INTERNAL_GOVERNANCE.md` L1/L2/L3 | Decision authority | 3-tier framework | ❌ Prose |
| `governance/WORKING_STYLE.md` Article 1-11 | Work culture | 11 behavioral principles | ❌ Prose |
| `knowledge/{role}/role_definition/task_type_map.md` | Task taxonomy | ≥8 types per role × 8 roles | ✅ Markdown table |
| `products/*/PROCESS.md` | Project workflow | 6-pager, release sign-off | ❌ Prose |
| AMENDMENT-005 RAPID matrix | Who does what | 5 roles × N actions | ⚠️ Proposed, not deployed |
| AMENDMENT-009 escape hatch | Lock self-rescue | 3 scenarios | ⚠️ Proposed, not deployed |

**Key finding from A017 audit `85b5c42`**:  
- `.ystar_session.json` has **3 deny-semantic keys** (`deny`, `deny_commands`, `obligation_timing`).  
- `.ystar_session.json` has **0 allow-semantic keys**.  
- All positive behavior guidance lives in prose files agents must interpret fresh every session.

**Consequence**: Agents know what NOT to do (deterministic), but only know what TO do via re-reading prose and hoping their interpretation matches Board intent. No accumulation, no reinforcement.

### 1.2 The 7 Sub-Corpora (Source File Paths)

| # | Sub-Corpus Name | Source File(s) | Responsible Agent |
|---|-----------------|----------------|-------------------|
| 1 | `constitutional` | `AGENTS.md` (Iron Rules + Article 7-11), `governance/WORKING_STYLE.md` (Article 1-11) | CTO (Ethan) |
| 2 | `role_mandate` | `knowledge/{role}/role_definition/task_type_map.md` (all 8 roles) | Platform (Ryan) |
| 3 | `inter_role_sop` | `governance/INTERNAL_GOVERNANCE.md` (L1/L2/L3 flows, dispatch must route through CTO, etc.) | Governance (Maya) |
| 4 | `project_procedure` | `products/ystar-gov/PROCESS.md`, `products/ystar-defuse/PROCESS.md` | Kernel (Leo) |
| 5 | `event_workflow` | `reports/priority_brief.md` (always_running + event_triggers) | Platform (Ryan) |
| 6 | `rapid_matrix` | AMENDMENT-005 proposal (Recommend/Agree/Perform/Input/Decide) | Governance (Maya) |
| 7 | `escape_hatch` | AMENDMENT-009 proposal (lock self-rescue: active_agent deadlock, circuit breaker ARMED, etc.) | CTO (Ethan) |

Each corpus will be compiled into `governance/whitelist/{corpus_name}.yml` with unified schema (§2.2).

---

## §2 Proposal — Whitelist Architecture

### 2.1 Core Innovation: Behavior↔Whitelist Real-Time Sync

**Three sync mechanisms (A/B/C)**:

#### A. Hook Call → Whitelist Match (Per-Action Mapping)

Every Y*gov hook call (PreToolUse/PostToolUse) triggers whitelist matching:

```python
# Inside ystar_hook.py (post-AMENDMENT-018)
def map_action_to_whitelist(agent_id, tool_name, tool_args, context):
    """
    Map agent action to whitelist entry.
    Returns: (match_status, matched_entries, drift_report)
    """
    action_vector = extract_action_semantics(tool_name, tool_args, context)
    
    # Load all 7 corpora
    whitelist = load_whitelist_all_corpora()
    
    # Semantic matching (cosine + keyword overlap)
    matches = find_matching_entries(action_vector, whitelist, threshold=0.75)
    
    if matches:
        emit_cieu_event("WHITELIST_MATCH", {
            "agent_id": agent_id,
            "action": action_vector,
            "matched_entry_id": matches[0]["id"],
            "confidence": matches[0]["score"]
        })
        return ALLOW, matches, None
    else:
        # No match → find closest 3 for teaching
        closest = find_closest_entries(action_vector, whitelist, top_k=3)
        drift_diff = compute_diff(action_vector, closest)
        
        emit_cieu_event("WHITELIST_DRIFT", {
            "agent_id": agent_id,
            "action": action_vector,
            "closest_entries": [e["id"] for e in closest],
            "diff": drift_diff
        })
        
        # Default: ALLOW + teach (per AMENDMENT-012 deny-as-teaching)
        return ALLOW, None, drift_diff
```

**Key principles**:
- **Hook does NOT block** on whitelist miss (default ALLOW + teach).
- Matches → positive reinforcement via CIEU `WHITELIST_MATCH`.
- Drifts → teaching moment via CIEU `WHITELIST_DRIFT` with closest-3 entries + diff.
- Follows AMENDMENT-012 deny-as-teaching principle: governance is coach, not police.

#### B. Whitelist Source Change → SSoT Regeneration → Runtime Push

When any whitelist source file changes (e.g., `AGENTS.md` edited, `task_type_map.md` updated):

```bash
# Triggered by AMENDMENT-016 watcher (already implemented in b16b563)
# governance/watcher_rules.yml (new rule):
- watch_path: "AGENTS.md|governance/*.md|knowledge/*/role_definition/*.md|products/*/PROCESS.md"
  on_change:
    - action: "regenerate_whitelist"
      script: "scripts/whitelist_compiler.py"
      output: "governance/whitelist/*.yml"
    - action: "push_to_runtime"
      script: "scripts/whitelist_push.py"
      target: "all_sub_agents"
      mechanism: "cieu_event"
      event_type: "WHITELIST_UPDATE"
```

**Flow**:
1. Watcher detects source file change (AMENDMENT-016 infrastructure already live as of b16b563).
2. `whitelist_compiler.py` regenerates affected corpus YAML.
3. `whitelist_push.py` emits CIEU `WHITELIST_UPDATE` event.
4. All running sub-agents receive update in next tool call (hook reads fresh YAML).
5. Next boot: updated corpus packed into `boot_pack.category_11` (AMENDMENT-015 LRS integration).

**No manual sync steps. Zero drift by design.**

#### C. Daily Coverage Report (Cron at 00:00 UTC)

```bash
# crontab entry (post-AMENDMENT-018)
0 0 * * * cd /Users/haotianliu/.openclaw/workspace/ystar-company && \
  python3 scripts/whitelist_coverage.py && \
  python3 scripts/report_to_board.py --topic whitelist_coverage
```

`whitelist_coverage.py` computes:
- **Coverage rate**: `matched_actions / total_actions` from last 24h CIEU log.
- **Target**: ≥80%.
- **Trigger**: if <60%, emit CIEU `WHITELIST_GAP` event + Board notice via Telegram.

**Output**: `reports/whitelist_coverage_YYYY-MM-DD.md` with:
- Top-10 drifted action patterns.
- Recommended new whitelist entries (auto-drafted, pending human review).

---

### 2.2 Unified Whitelist Entry Schema

Every entry in all 7 corpora follows this schema:

```yaml
# governance/whitelist/{corpus_name}.yml
schema_version: "1.0"
corpus: "constitutional|role_mandate|inter_role_sop|project_procedure|event_workflow|rapid_matrix|escape_hatch"
last_updated: "2026-04-13T14:00:00Z"
source_files:
  - "AGENTS.md"
  - "governance/WORKING_STYLE.md"
entries:
  - id: "const-001"
    who: "all_agents|ceo|cto|eng-kernel|..."  # Role or "all_agents"
    what: "任何agent执行Level 2决策前必须提交反事实推理提案"  # Natural language description
    when_trigger: "decision_level == 2 && precheck_not_submitted"  # Condition (prose or code)
    when_complete: "gov_precheck返回approved"  # Completion signal
    prerequisites:
      - "decision_level已判定"
      - "反事实推理格式已理解(WORKING_STYLE.md §7)"
    observable_signal:
      cieu_event: "INTENT_DECLARED"
      must_contain:
        intent_type: "level2_decision"
        precheck_status: "submitted"
    source_ref:
      file: "governance/WORKING_STYLE.md"
      section: "§7 反事实推理提案规范"
      line_range: "92-131"
```

**Schema fields**:
- `id`: Unique identifier (corpus prefix + sequential number).
- `who`: Authorized agent(s). `all_agents` = universal rule.
- `what`: Natural language description of the expected behavior.
- `when_trigger`: Condition that makes this entry applicable (prose or pseudocode).
- `when_complete`: Observable signal that this behavior was executed correctly.
- `prerequisites`: Required prior states (other whitelist entries, system state, etc.).
- `observable_signal`: CIEU event type + required fields (for automated verification).
- `source_ref`: Traceability back to authoritative source document.

**Design rationale**:
- Natural language `what` keeps it human-readable.
- `observable_signal` with CIEU event schema makes it machine-verifiable.
- `source_ref` ensures every whitelist entry traces back to authoritative source.
- Prerequisites encode dependency chains (e.g., "before X, must do Y").

---

### 2.3 The 7 Sub-Corpora (Detailed Breakdown)

#### 1. Constitutional (`constitutional.yml`)

**Owner**: CTO (Ethan)  
**Sources**: `AGENTS.md` Iron Rules 1-3, Article 7-11; `governance/WORKING_STYLE.md` Article 1-11  
**Sample entries**:
- `const-001`: "Iron Rule 1: No LLM in enforcement path" (who=all_agents, trigger=any_check_call)
- `const-002`: "Iron Rule 2: No hardcoded paths" (who=all_engineers, trigger=code_commit)
- `const-003`: "Iron Rule 3: Ecosystem neutrality" (who=all_engineers, trigger=PR_review)
- `const-004`: "Article 1: 执行意志 — 不找借口" (who=all_agents, trigger=task_assigned)
- `const-005`: "Article 7: 反事实推理提案 for L2/L3" (who=all_agents, trigger=decision_level>=2)
- `const-006`: "Article 11: 第十一条 — 并行spawning" (who=ceo, trigger=autonomous_mission)

**Count estimate**: ~20 entries (3 Iron Rules + 11 Working Style articles + sub-rules).

#### 2. Role Mandate (`role_mandate.yml`)

**Owner**: Platform (Ryan)  
**Sources**: `knowledge/{role}/role_definition/task_type_map.md` for all 8 roles (ceo/cto/cmo/cso/cfo/secretary/4 engineers)  
**Sample entries**:
- `role-ceo-001`: "CEO task type: 协调分工 — 写task card到.claude/tasks/" (who=ceo, trigger=task_assignment_needed)
- `role-cto-001`: "CTO task type: 架构决策 — 审engineer commits前先跑tests" (who=cto, trigger=engineer_commit_pending)
- `role-eng-kernel-001`: "Kernel engineer scope: ystar/kernel/, session.py" (who=eng-kernel, trigger=file_write)

**Count estimate**: 8 roles × 8 task types/role = ~64 entries.

#### 3. Inter-Role SOP (`inter_role_sop.yml`)

**Owner**: Governance (Maya)  
**Sources**: `governance/INTERNAL_GOVERNANCE.md` (L1/L2/L3 decision flows, dispatch routing, sub-agent spawn rules)  
**Sample entries**:
- `sop-001`: "L1 decision: 单岗位内部、可逆 → 直接执行，无需提案" (who=all_agents, trigger=decision_level==1)
- `sop-002`: "L2 decision: 跨岗位 → 反事实提案 → CEO批准 → 执行 → 24h汇报Board" (who=all_agents, trigger=decision_level==2)
- `sop-003`: "L3 decision: 外部发布/宪法修改/金钱 → Board批准" (who=all_agents, trigger=decision_level==3)
- `sop-004`: "代码任务 → CEO不直接写，通过Agent tool调起CTO或工程师" (who=ceo, trigger=task_type==code)
- `sop-005`: "Dispatch必经CTO，CTO分派到4工程师" (who=ceo, trigger=engineering_task)

**Count estimate**: ~15 entries (L1/L2/L3 flows + dispatch rules + sub-agent spawn protocols).

#### 4. Project Procedure (`project_procedure.yml`)

**Owner**: Kernel (Leo)  
**Sources**: `products/ystar-gov/PROCESS.md`, `products/ystar-defuse/PROCESS.md`  
**Sample entries**:
- `proj-ystar-gov-001`: "Y*gov bug fix: CIEU trace first, never guess" (who=cto|eng-*, trigger=bug_report)
- `proj-ystar-gov-002`: "Y*gov source-first fixes: 修源码库,rebuild whl,reinstall" (who=cto, trigger=bug_fix)
- `proj-ystar-gov-003`: "Y*gov test gate: 86 tests must pass before merge" (who=cto, trigger=commit_ready)
- `proj-ystar-gov-004`: "Y*gov fix log: after every fix, write entry to reports/cto_fix_log.md" (who=cto, trigger=fix_complete)

**Count estimate**: ~12 entries (2 products × 6 steps/product).

#### 5. Event Workflow (`event_workflow.yml`)

**Owner**: Platform (Ryan)  
**Sources**: `reports/priority_brief.md` (always_running + event_triggers)  
**Sample entries**:
- `event-001`: "board_online trigger → CEO emits '老大，[正在做的事]' within 30s" (who=ceo, trigger=board_online_detected)
- `event-002`: "board_offline >2h trigger → CEO autonomous work per always_running priority queue" (who=ceo, trigger=board_offline_2h)
- `event-003`: "session_boot trigger → governance_boot.sh → ALL SYSTEMS GO" (who=all_agents, trigger=session_start)
- `event-004`: "session_close trigger → session_close_yml.py + rm .session_booted" (who=all_agents, trigger=session_end)
- `event-005`: "idle_5min trigger → ADE pulls from always_running queue" (who=all_agents, trigger=idle_5min)

**Count estimate**: ~20 entries (priority_brief.event_triggers has ~10 events × 2 actions/event).

#### 6. RAPID Matrix (`rapid_matrix.yml`)

**Owner**: Governance (Maya)  
**Sources**: AMENDMENT-005 proposal (RAPID = Recommend/Agree/Perform/Input/Decide)  
**Sample entries**:
- `rapid-001`: "宪法修改: Board=Decide, Secretary=Perform, All=Input" (action=amend_agents_md, R=all, A=ceo, P=secretary, I=all, D=board)
- `rapid-002`: "PyPI release: CTO=Recommend, CEO=Agree, CTO=Perform, All=Input, Board=Decide" (action=pypi_publish)
- `rapid-003`: "Blog post: CMO=Recommend, CEO=Agree, CMO=Perform, All=Input, Board=Decide" (action=blog_publish)

**Count estimate**: ~30 entries (AMENDMENT-005 covers ~30 action types).

#### 7. Escape Hatch (`escape_hatch.yml`)

**Owner**: CTO (Ethan)  
**Sources**: AMENDMENT-009 proposal (lock self-rescue: active_agent deadlock, circuit breaker ARMED, etc.)  
**Sample entries**:
- `escape-001`: "Active_agent deadlock → Board shell: echo {role} > .ystar_active_agent" (scenario=active_agent_deadlock, who=board, action=shell_override)
- `escape-002`: "Circuit breaker ARMED → gov_reset_breaker + git commit breach evidence" (scenario=breaker_armed, who=cto, action=reset_with_evidence)
- `escape-003`: "CIEU DB locked → pkill hook_daemon + restart governance_boot.sh" (scenario=db_lock, who=cto, action=daemon_restart)

**Count estimate**: ~8 entries (AMENDMENT-009 defines 3 major scenarios × 2-3 steps/scenario).

---

### 2.4 Total Whitelist Corpus Size

| Corpus | Estimated Entries | Owner |
|--------|-------------------|-------|
| 1. Constitutional | 20 | CTO (Ethan) |
| 2. Role Mandate | 64 | Platform (Ryan) |
| 3. Inter-Role SOP | 15 | Governance (Maya) |
| 4. Project Procedure | 12 | Kernel (Leo) |
| 5. Event Workflow | 20 | Platform (Ryan) |
| 6. RAPID Matrix | 30 | Governance (Maya) |
| 7. Escape Hatch | 8 | CTO (Ethan) |
| **TOTAL** | **169 entries** | **4 engineers** |

**Target**: 169 entries compiled within 72h (by 2026-04-16 14:00 UTC).

---

## §3 Acceptance Criteria

1. **All 7 corpora YAML files exist** in `governance/whitelist/` with unified schema v1.0.
2. **Boot injection**: `governance_boot.sh` loads all 7 corpora into `boot_pack.category_11` (AMENDMENT-015 LRS integration).
3. **CIEU events operational**:
   - `WHITELIST_MATCH` event emitted on every hook call that matches an entry (confidence ≥0.75).
   - `WHITELIST_DRIFT` event emitted on every hook call that misses whitelist, with closest-3 entries + diff.
   - `WHITELIST_UPDATE` event emitted on every source file change (watcher-triggered).
   - `WHITELIST_GAP` event emitted when daily coverage <60%.
4. **Coverage ≥80%** within 72h of deployment (measured by `whitelist_coverage.py` daily cron).
5. **Zero manual sync steps**: Whitelist regenerates automatically on source change (AMENDMENT-016 watcher integration).

**Verification**:
- Run `python3 scripts/whitelist_coverage.py --validate` after 72h.
- Check `reports/whitelist_coverage_2026-04-16.md` for coverage rate ≥80%.
- Query CIEU DB: `SELECT COUNT(*) FROM events WHERE event_type='WHITELIST_MATCH'` (expect >100 events/day).

---

## §4 RAPID Allocation

| Sub-Corpus | Owner (P = Perform) | Recommend | Agree | Input | Decide |
|------------|---------------------|-----------|-------|-------|--------|
| 1. Constitutional | CTO (Ethan) | Ethan | CEO | All | Board |
| 2. Role Mandate | Platform (Ryan) | Ryan | CTO | All roles | CEO |
| 3. Inter-Role SOP | Governance (Maya) | Maya | CTO | All | CEO |
| 4. Project Procedure | Kernel (Leo) | Leo | CTO | All engineers | CEO |
| 5. Event Workflow | Platform (Ryan) | Ryan | CTO | CEO | CEO |
| 6. RAPID Matrix | Governance (Maya) | Maya | CTO | All | CEO |
| 7. Escape Hatch | CTO (Ethan) | Ethan | CEO | All | Board |

**Sync mechanism ownership**:
- **A. Hook call → whitelist match**: Kernel (Leo) — integrates into `ystar_hook.py`.
- **B. Source change → SSoT regeneration → push**: Platform (Ryan) — extends AMENDMENT-016 watcher.
- **C. Daily coverage report**: Governance (Maya) — writes `whitelist_coverage.py` cron script.

**CTO (Ethan) integration**: Reviews all 7 corpora for consistency, runs full-stack test after Maya/Ryan/Leo ship their parts.

---

## §5 Risks + Mitigation

### Risk 1: Whitelist Incompleteness → Legitimate Actions Flagged as Drifts

**Scenario**: Agent performs a correct action not yet in whitelist → `WHITELIST_DRIFT` event emitted → agent treats it as "I did something wrong."

**Mitigation**:
- Default action on drift is **ALLOW + teach**, NOT deny (per AMENDMENT-012 deny-as-teaching principle).
- Drift events include closest-3 whitelist entries + diff → agent learns "you did X, should've done Y" (teaching moment, not punishment).
- Daily coverage report auto-drafts new whitelist entries for top-10 drifted patterns → CTO reviews and merges.
- Initial coverage target is ≥80%, NOT 100% — we expect 20% legitimate drift in first weeks.

**Long-term**: As coverage → 95%+, we can shift from "allow + teach" to "warn + teach" for high-confidence drifts. But that's a future AMENDMENT, not part of A018.

### Risk 2: Whitelist Source Drift (YAML Stale, Source Updated)

**Scenario**: Someone edits `AGENTS.md` but forgets to regenerate whitelist YAML → runtime uses stale whitelist.

**Mitigation**:
- AMENDMENT-016 watcher (b16b563) already monitors `AGENTS.md` and all `governance/*.md` files.
- Any edit triggers `whitelist_compiler.py` automatically → zero manual sync.
- `governance_boot.sh` validates whitelist YAML timestamps against source file mtimes → if YAML older than source, boot FAILS with "WHITELIST_STALE" error.

**No human can forget to sync. System enforces.**

### Risk 3: 169 Entries Too Large for Boot Pack

**Scenario**: Boot pack size explodes, slows down session boot.

**Mitigation**:
- AMENDMENT-015 LRS already compresses boot pack (gzip + delta encoding).
- 169 entries × ~200 bytes/entry = ~34KB raw, ~10KB compressed → negligible vs current boot pack size (~500KB).
- If size becomes issue, we lazy-load: boot pack contains only constitutional + role_mandate (84 entries), rest loaded on-demand when agent enters specific workflow (L2 decision → loads `inter_role_sop.yml`).

**Not a risk for MVP. Monitor, don't pre-optimize.**

### Risk 4: Semantic Matching False Positives

**Scenario**: Agent action "write tests" matches whitelist entry "write test plan" (high cosine similarity) → false positive match.

**Mitigation**:
- Matching threshold = 0.75 (tuned via EXP-8 red team after A018 ships).
- `observable_signal.cieu_event` field provides deterministic verification: even if semantic match scores high, CIEU event type must match (e.g., entry says "must emit INTENT_DECLARED with intent_type=test_plan" → if agent emits INTENT_DECLARED with intent_type=test_code, match fails).
- False positive rate acceptable at MVP: we're coaching, not policing. Agent gets positive reinforcement → learns faster.

**Post-MVP**: Red team tunes threshold, adds keyword-based filters for high-risk actions.

---

## §6 Relationship to AMENDMENT-016/017

### AMENDMENT-016 (SSoT→Runtime Sync)

**A016 provides**: Transport layer for whitelist updates.
- Watcher detects source file changes.
- Watcher triggers regeneration script.
- Regeneration script outputs updated YAML.
- Push mechanism emits CIEU `WHITELIST_UPDATE` event.

**A018 adds**: Payload. A016 is the pipe, A018 is the water.

**Integration point**: `governance/watcher_rules.yml` gains 7 new watch rules (one per corpus source file set).

### AMENDMENT-017 (Role Capability Envelope)

**A017 provides**: Per-role capability boundaries (what tools each role can call).
- `agent_write_paths`: which directories each role can write to.
- `restricted_write_paths`: which files require specific roles.
- `tool_access_matrix`: which MCP tools each role can invoke.

**A018 adds**: Positive corpus. A017 says "CTO can write to src/", A018 says "when CTO writes to src/, they follow Y*gov source-first fix protocol."

**Integration point**: `observable_signal.who` field in whitelist entries maps to A017's `agent_id` → whitelist matching respects role boundaries. Example:
- Whitelist entry `proj-ystar-gov-002` says `who: cto|eng-*` → only CTO or engineers can match this entry.
- If CEO tries to match it → auto-fails, emits `WHITELIST_ROLE_VIOLATION` (new CIEU event type, part of A018).

**Conceptual relationship**:
- A017 = capability envelope = "what you CAN do."
- A018 = positive corpus = "what you SHOULD do."
- Intersection = "what you can do × what you should do" = legitimate action space.

---

## §7 Implementation Timeline

**Phase 0: Design approval (Board)** — 2h  
→ Board reads this 6-pager, says "批准" or "改X后批准."

**Phase 1: Corpus compilation (4 engineers, parallel)** — 48h  
| Hour | Maya | Ryan | Leo | Ethan |
|------|------|------|-----|-------|
| 0-8 | Draft `inter_role_sop.yml` + `rapid_matrix.yml` (~45 entries) | Draft `role_mandate.yml` + `event_workflow.yml` (~84 entries) | Draft `project_procedure.yml` (~12 entries) | Draft `constitutional.yml` + `escape_hatch.yml` (~28 entries) |
| 8-16 | Write `whitelist_coverage.py` (sync mechanism C) | Extend watcher rules for A016 integration (sync mechanism B) | Implement hook matching in `ystar_hook.py` (sync mechanism A) | Integration test: all 7 corpora load + match smoke test |
| 16-24 | Test coverage report cron | Test watcher → regen → push flow | Test hook matching (10 sample actions × 7 corpora) | Full-stack test: edit source → watcher → regen → boot → coverage |
| 24-48 | Buffer for fixes | Buffer for fixes | Buffer for fixes | Final sign-off + commit |

**Phase 2: Deployment + monitoring** — 24h  
- Merge to main.
- Run `governance_boot.sh ceo` on next session → validates all 7 YAML files load.
- Monitor CIEU for `WHITELIST_MATCH` / `WHITELIST_DRIFT` events.
- Day 1 (24h post-deploy): run `whitelist_coverage.py` → expect ≥60% (bootstrap threshold).
- Day 2 (48h post-deploy): review top-10 drifts, draft new entries, merge → expect ≥70%.
- Day 3 (72h post-deploy): expect ≥80% (acceptance criterion).

**Total elapsed time**: 72h (3 days) from Board approval to acceptance verified.

**Commit message template**: 
```
proposal(charter): AMENDMENT-018 Full Positive Corpus + Behavior↔Whitelist Real-Time Sync

7 sub-corpora (169 entries):
- constitutional (AGENTS.md + WORKING_STYLE.md)
- role_mandate (task_type_map.md × 8 roles)
- inter_role_sop (INTERNAL_GOVERNANCE.md)
- project_procedure (products/*/PROCESS.md)
- event_workflow (priority_brief.md)
- rapid_matrix (AMENDMENT-005)
- escape_hatch (AMENDMENT-009)

Sync mechanisms:
- A: hook call → whitelist match → WHITELIST_MATCH/DRIFT CIEU events
- B: source change → A016 watcher → regen → push → WHITELIST_UPDATE
- C: daily cron → coverage report → WHITELIST_GAP if <60%

Target: ≥80% coverage within 72h.
Paradigm shift: governance = coach (引导对行为), not police (拦坏行为).

Board directive 2026-04-13: "把所有正常流程全部列为白名单 + 实时同步."

Co-Authored-By: Claude Opus 4.6 (1M context) <noreply@anthropic.com>
```

---

**End of AMENDMENT-018 Proposal**

**CTO Sign-Off**: Ethan Wright  
**Date**: 2026-04-13  
**Status**: ✅ Written to docs/ (CTO allowed path), ready for Board review  
**Next step**: Board reads §0-3 (15min), says "批准" → CEO coordinates final placement + BOARD_CHARTER_AMENDMENTS.md update  
**File location**: `docs/AMENDMENT_018_FULL_POSITIVE_CORPUS.md`
