# Board Approval Request — AGENTS.md Constitutional Repair

**Submitted by:** CEO (Aiden)  
**Date:** 2026-04-03  
**Status:** PENDING_BOARD_SIGN_OFF  
**Root Cause:** 2026-04-03 production incident (interrupt_gate armed, team paralyzed)

---

## Executive Summary

Request Board approval to perform systematic repair of AGENTS.md constitutional layer. Audit reveals 4 categories of violations against the "WHEN not HOW" principle, causing high-frequency obligation accumulation and system paralysis.

**Impact if NOT fixed:** Future production incidents, governance system credibility loss  
**Impact if fixed:** Clean constitutional layer, machine-executable governance, no HOW in constitution  
**Risk level:** HIGH (modifying constitution)  
**Mitigation:** All deleted content preserved in knowledge/ before deletion

---

## Proposed Changes Summary

| Category | Changes | Files Affected | Risk |
|----------|---------|----------------|------|
| 修复一：删除HOW描述 | 3处 | AGENTS.md, knowledge/ceo/ | MEDIUM |
| 修复二：删除执行步骤 | 5处 | AGENTS.md, knowledge/cfo/, knowledge/ | MEDIUM |
| 修复三：集中obligation_timing | 5处散落→1个registry | AGENTS.md | LOW |
| 修复四：补全fulfil机制 | 4处 | AGENTS.md | LOW |
| 新增：CTO自检义务 | 新增2条 | AGENTS.md | LOW |

**Total:** 17 modification points in AGENTS.md

---

## Detailed Change Plan

### 修复一：删除高频触发的HOW描述（3处）

#### Change 1.1: CIEU Liveness Check章节

**Current (violation):**
```
每次session启动时：
1. query CIEU database event count
2. if count增长<10 in last hour → action
3. query again 5min later
4. if still <10 → escalate to P0
```

**Proposed:**
```
每次session启动时，必须运行 ystar doctor --layer1
发现CIEU异常 = P0，立即停止其他工作上报CEO
执行细节：见 ystar/cli/doctor_cmd.py
```

**WHY this is better:** 
- Moves HOW to code (doctor_cmd.py)
- Constitution only says WHEN (session启动时)
- Machine-executable (ystar command)

**Deletion target:** Move 4 steps to knowledge/ceo/cieu_liveness_guide.md

---

#### Change 1.2: Self-Bootstrap Protocol章节

**Current (violation):**
```
发现知识缺口INSTANT触发：
1. 在knowledge/[role]/创建[topic].md
2. 写入当前问题
3. 写入临时解决方案
4. 写入需要深入研究的点
5. commit
6. 在简报里提及
7. 30分钟deadline
```

**Proposed:**
```
发现知识缺口时，必须在30分钟内写入knowledge/[role]/
触发条件：任务因知识不足失败，或产出被Board纠正
执行细节：见 knowledge/ceo/bootstrap_guide.md

Y*gov enforcement: 见 Obligation Timing Registry (knowledge_gap_bootstrap: 1800)
```

**WHY this is better:**
- "INSTANT触发" too broad → specific triggers
- 7 steps moved to guide
- Adds obligation_timing reference

**Deletion target:** Move 7 steps to knowledge/ceo/bootstrap_guide.md

---

#### Change 1.3: Directive Tracking #3

**Current (violation):**
```
CEO Session Start must include: Read DIRECTIVE_TRACKER.md. Check for ❌ items. Any ❌ older than 3 days without progress must be escalated to Board in 今日简报.
```

**Proposed:**
```
每次session启动时，CEO必须检查DIRECTIVE_TRACKER.md中的❌项
超过3天无进展的❌项 = 当日简报必须提及

Fulfil机制：简报中包含❌项状态更新
```

**WHY this is better:**
- Removes imperative "must include: Read"
- Says WHEN + WHAT, not HOW
- Adds fulfil mechanism

**Deletion target:** None (just rewording)

---

### 修复二：删除宪法层的执行步骤（5处）

#### Change 2.1: Release & Distribution Obligations

**Current (violation):**
```
After git push to main:
1. pip install dist/ystar-X.Y.Z-py3-none-any.whl in clean venv
2. ystar hook-install
3. ystar doctor
4. Run 3 governance tests
5. Check CHANGELOG matches version
6. Verify no hardcoded paths
7. Test in ystar-company directory
8. Verify hook triggers
9. Check CLI help output
```

**Proposed:**
```
每次git push到main后，CTO必须运行 ystar release-verify
失败 = SOFT_OVERDUE，禁止开始下一个任务
验证步骤：见 ystar/cli/release_cmd.py

Y*gov enforcement: 见 Obligation Timing Registry (distribution_verify_post_push: 300)
```

**WHY this is better:**
- 9 steps → 1 command
- Constitution says WHEN + tool, code says HOW
- Adds consequence (SOFT_OVERDUE)

**Deletion target:** Move 9 steps to ystar/cli/release_cmd.py docstring

---

#### Change 2.2: CFO Token Recording

**Current (violation):**
```
After each session:
python scripts/track_burn.py --agent ystar-cfo --session-id [id] --project ystar-company
```

**Proposed:**
```
每次session结束后10分钟内，CFO必须记录本次token消耗
执行工具：scripts/track_burn.py
未记录 = HARD_OVERDUE

Y*gov enforcement: 见 Obligation Timing Registry (cfo_token_recording: 600)
```

**WHY this is better:**
- Removes exact command line
- Says WHEN (session结束后) + tool, not HOW
- Adds consequence

**Deletion target:** Move command to knowledge/cfo/token_recording_guide.md

---

#### Change 2.3: Emergency Procedures

**Current (violation):**
```
If credential exposed:
1. git reset --soft HEAD~1
2. Edit file to remove credential
3. git commit --amend
4. Verify with git log -p
5. Notify Board
```

**Proposed:**
```
发现credential暴露：立即停止所有操作，上报Board，不得自行修复
无法完成义务：写入reports/blockers/，上报CEO
执行流程：见 knowledge/emergency_procedures.md
```

**WHY this is better:**
- Removes dangerous 5-step procedure
- Constitution says STOP + REPORT, guide says HOW
- Prevents unauthorized git surgery

**Deletion target:** Move 5 steps to knowledge/emergency_procedures.md

---

#### Change 2.4 & 2.5: Other CFO/CTO command details

Same pattern as 2.2 - remove exact commands, point to guides.

**Deletion targets:**
- knowledge/cfo/burn_rate_calculation.md
- knowledge/cto/pre_commit_checklist.md

---

### 修复三：集中管理obligation_timing（5处散落→1个registry）

**Current (violation):**
- Directive Tracking: "obligation_timing: directive_decomposition: 600"
- Article Writing: "obligation_timing: article_source_verification: 300"
- CFO Obligations: "obligation_timing: cfo_token_recording: 600"
- Cross-review SLA: "30分钟" (inline, not in timing config)
- Session closure: "每次session结束" (no timing spec)

**Proposed:** Add new section at AGENTS.md end

```markdown
## Y*gov Obligation Timing Registry
（以下配置由Y*gov OmissionEngine读取，集中管理）

### Session级义务（每session触发一次）
- directive_decomposition: 600  # Board下达指令后10分钟
- autonomous_daily_report: 86400  # 每天
- knowledge_gap_bootstrap: 1800  # 发现知识缺口后30分钟
- cfo_token_recording: 600  # Session结束后10分钟
- ceo_daily_consolidation: 90000  # 每天
- weekly_board_summary: 604800  # 每周

### Event级义务（特定事件后触发，由obligation_triggers.py管理）
- article_source_verification: 300  # CMO写内容时
- commit_push_sync: 1800  # git commit后30分钟
- distribution_verify_post_push: 300  # git push后5分钟
- cross_review_sla: 1800  # 关键文件修改后30分钟
- pre_commit_test: 60  # git commit前1分钟
- session_report_before_close: 300  # session结束前5分钟

注：Event级义务的trigger逻辑在 ystar/governance/obligation_triggers.py
```

**Then replace all inline timing references with:**
```
Y*gov enforcement: 见 Obligation Timing Registry
```

**WHY this is better:**
- Single source of truth
- Easy to audit all timings
- Machine-readable registry
- Prevents timing duplication/conflicts

---

### 修复四：补全缺失fulfil机制的义务（4处）

#### Change 4.1: Cross-review SLA 30分钟

**Current (missing fulfil):**
```
关键文件修改后30分钟内必须有peer review
```

**Proposed:**
```
关键文件修改后30分钟内必须有peer review

Fulfil机制：reviewer在CIEU里写入review_approved或review_changes_requested事件
触发工具：ystar review-comment <file> <status>
```

---

#### Change 4.2: Jinjin inbox check

**Current (missing obligation_timing):**
```
Jinjin每小时检查inbox
```

**Proposed:**
```
Jinjin每小时检查K9 inbox

Y*gov enforcement: 见 Obligation Timing Registry (k9_inbox_check: 3600)
Fulfil机制：运行scripts/k9_inbox.py产生输出
```

---

#### Change 4.3: CEO Weekly Board summary

**Current (missing timing spec):**
```
CEO每周提交Board summary
```

**Proposed:**
```
CEO每周提交Board summary

Y*gov enforcement: 见 Obligation Timing Registry (weekly_board_summary: 604800)
Fulfil机制：reports/weekly/YYYY-MM-DD.md文件创建
```

---

#### Change 4.4: CEO Daily report with burn rate

**Current (vague timing):**
```
CEO每天consolidate报告
```

**Proposed:**
```
CEO每天consolidate各agent工作报告

Y*gov enforcement: 见 Obligation Timing Registry (ceo_daily_consolidation: 90000)
Fulfil机制：reports/autonomous/summary_YYYY-MM-DD.md文件创建
```

---

### 新增：CTO自检义务（2条新增）

**Add to CTO章节 "### Engineering Standards":**

```markdown
5. **Pre-Change Health Check**（Constitutional）
   修改以下文件之前，必须先运行 ystar check-impact <target>：
   - session.json
   - omission_engine.py
   - hook.py
   - dimensions.py
   
   不运行即修改 = P0违规

6. **Post-Change Verification**（Constitutional）
   每次git commit后，必须运行 ystar doctor --layer1
   doctor失败 = 禁止push
```

**Add to CTO章节 "### Obligations":**

```markdown
- 每次session启动：运行 ystar doctor --layer1（<5秒，不影响速度）
- 每周一次：运行 ystar doctor --layer2 --design-debt
  输出设计债报告到 reports/cto/design_debt_YYYY-MM-DD.md
  发现新断裂机制 = 本周P1任务
```

**WHY add these:**
- Prevents repeat of today's production incident
- CTO owns system health
- Doctor is now available (implemented today)
- Design debt tracking prevents accumulated fragility

---

## Migration Plan

### Phase 1: Preserve deleted content (BEFORE modification)

Create these files with deleted HOW content:

1. `knowledge/ceo/cieu_liveness_guide.md` - 4 steps from CIEU Liveness Check
2. `knowledge/ceo/bootstrap_guide.md` - 7 steps from Self-Bootstrap Protocol
3. `knowledge/cfo/token_recording_guide.md` - CFO command details
4. `knowledge/cfo/burn_rate_calculation.md` - Burn rate calculation steps
5. `knowledge/cto/pre_commit_checklist.md` - Pre-commit verification steps
6. `knowledge/emergency_procedures.md` - Emergency credential exposure procedure
7. Update `ystar/cli/release_cmd.py` docstring - 9 release verification steps

**Commit message:** "knowledge: preserve AGENTS.md HOW content before constitutional cleanup"

### Phase 2: Modify AGENTS.md (AFTER Phase 1 committed)

Apply all 17 modification points listed above.

**Commit message:** "governance: AGENTS.md constitutional repair - WHEN not HOW principle"

### Phase 3: Verification (AFTER Phase 2 committed)

```bash
ystar doctor --layer1
# Expected: All checks pass

git diff HEAD~1 AGENTS.md | wc -l
# Expected: Significant line reduction

# Verify no HOW content remains in constitution
grep -i "step 1\|step 2\|具体步骤\|python scripts" AGENTS.md
# Expected: No matches (or only in examples/references)
```

---

## Risk Assessment

| Risk | Probability | Impact | Mitigation |
|------|------------|--------|------------|
| Break existing governance | LOW | HIGH | All deleted content preserved in knowledge/ first |
| Miss a fulfil mechanism | MEDIUM | MEDIUM | Added 4 missing fulfil mechanisms explicitly |
| Timing registry not machine-readable | LOW | MEDIUM | CTO will implement parser in next sprint |
| Constitutional change causes confusion | MEDIUM | LOW | Clear migration plan, all HOW preserved |

---

## Success Criteria

- ✅ AGENTS.md line count reduced by >30%
- ✅ No HOW content (steps/commands) remains in constitution
- ✅ All deleted content preserved in knowledge/
- ✅ Obligation Timing Registry created (single source of truth)
- ✅ All obligations have clear fulfil mechanisms
- ✅ `ystar doctor --layer1` passes after modification
- ✅ CTO self-check obligations added

---

## Board Decision Required

**Question:** Do you approve this systematic repair of AGENTS.md constitutional layer?

**Options:**
- ✅ **APPROVED** - Proceed with all 17 modifications per plan above
- ✏️ **REVISE** - Specify which changes to modify
- ❌ **REJECTED** - Explain why and propose alternative

**If APPROVED, CEO will execute Phase 1→2→3 immediately.**

---

**CEO signature:** Aiden (承远)  
**Date submitted:** 2026-04-03  
**Awaiting:** Board sign-off

---
---

# Board Approval Request — Enterprise Sales Strategy (Phase 2)

**Submitted by:** CEO (Aiden)  
**Date:** 2026-04-03  
**Status:** PENDING_BOARD_SIGN_OFF  
**Dependencies:** 0.48.0 PyPI release completed

---

## Executive Summary

CSO completed comprehensive enterprise customer research (14 target companies, $1.2M-$2.8M projected pipeline). Cross-review by CTO and CMO completed. Phase 1 (Anthropic ecosystem warm intro) approved by CEO for immediate execution. Phase 2 (direct enterprise outreach + pricing) requires Board approval.

**Reports:**
- Main Report: sales/enterprise_prospects_0.48.0.md (10.8KB, 14 companies)
- CTO Review: sales/cto_review_enterprise_prospects.md (APPROVED WITH CHANGES)
- CMO Review: sales/cmo_review_enterprise_prospects.md (APPROVED WITH CHANGES)
- Changelog: sales/enterprise_prospects_changelog.md (8 modifications applied)

---

## Board Decisions Required

### Decision 1: Approve Pricing Strategy

| Tier | Annual Price | Target Segment |
|------|--------------|----------------|
| Startup | $12K/year | <50 employees, <5 production agents |
| Growth | $48K/year | 50-500 employees, 5-50 agents |
| Enterprise | $120K-$500K/year | 500+ employees, 50+ agents, SLA |
| Channel Partner | $500K-$1M/year | SI firms, unlimited client deployments |

**Pilot Pricing:** $5K-$10K for 3-month POC (accelerate deal cycles outside budget season)

**Rationale:** Lower than internal build ($300K-$600K), higher than basic compliance tools ($6K-$24K), aligned with AI development budgets ($60K-$150K)

**Board Options:**
- ✅ **APPROVE** pricing tiers as proposed
- ✏️ **REVISE** specific tiers (specify changes)
- ❌ **DEFER** pricing decision, focus on pilots only

---

### Decision 2: Approve Phase 2 Direct Outreach

**Target Companies (8 high-value prospects):**
1. JPMorgan Chase ($250K-$500K) — Terah Lyons, AI Policy Head
2. Stripe ($150K-$300K) — MPP infrastructure team
3. UnitedHealth/Optum ($200K-$400K) — Optum Real engineering
4. Snowflake ($200K-$400K) — AI product team (Anthropic partnership)
5. Accenture ($500K-$1M) — Claude Partner Network lead (channel)
6. Deloitte ($500K-$1M) — AI practice lead (channel)
7. PwC-Anthropic ($300K-$600K) — Life sciences practice (channel)
8. Exscientia/In Silico Medicine ($80K-$150K each) — AI drug discovery

**Outreach Method:** LinkedIn + email cold outreach with demo video

**Timeline:** Week 2-4 post-launch

**Board Options:**
- ✅ **APPROVE** outreach to all 8 companies
- ✏️ **APPROVE SUBSET** (specify which companies)
- ❌ **DEFER** until after Phase 1 results (2-4 weeks)

---

### Decision 3: Authorize CTO Sales Demo Environment

**Requirement:** Isolated Y*gov instance for prospect demos (prevent production CIEU contamination)

**Scope:**
- Standalone demo environment with sample AGENTS.md
- Pre-loaded demo scenarios (scope violation, obligation omission, goal drift)
- Can be shared during sales calls without exposing ystar-company data

**Timeline:** 1-2 days for CTO to build

**Board Options:**
- ✅ **APPROVE** CTO allocation (1-2 days)
- ❌ **DEFER** use production environment for demos

---

### Decision 4: Channel Partnership Strategy

**Proposal:** Prioritize Accenture/Deloitte/PwC partnerships (3 largest SI firms, all have Claude partnerships)

**Value Proposition:** Y*gov becomes standard governance layer for their Claude enterprise deployments

**Revenue Model (needs CFO analysis):**
- Option A: Flat annual license ($500K-$1M) + unlimited client deployments
- Option B: Revenue share (e.g., 15-20% of governance component in SI deals)
- Option C: Tiered volume pricing (# of client deployments)

**Board Options:**
- ✅ **APPROVE** channel partnership outreach (defer revenue model to pilot negotiations)
- ✏️ **APPROVE with CFO modeling first** (1 week delay)
- ❌ **REJECT** channel strategy, focus on direct enterprise sales only

---

## Phase 1 Status (Already Approved by CEO)

**Approved Outreach (Anthropic Ecosystem):**
- Figma (AI agents on canvas)
- Box (Aaron Levie's team, content governance)
- Rakuten (Anthropic Agentic Coding Report customer)
- CRED (Indian fintech, compliance-heavy)
- Zapier (OAuth token governance for thousands of apps)
- TELUS (Canadian telecom, PII governance)

**Status:** CSO executing warm introductions via Anthropic ecosystem connections

**No Board approval required** (operational execution within approved strategy)

---

## Risk Assessment

| Risk | Mitigation |
|------|------------|
| Pricing too high for startups | Added pilot pricing $5K-$10K for 3-month POC |
| Over-promise compliance | CTO/CMO review removed all over-promise language |
| Cold outreach ignored | Demo video + specific pain point messaging per company |
| Channel partner economics unclear | Defer revenue model to pilot negotiations |

---

## Success Metrics (90 Days Post-Launch)

- 10 enterprise conversations with decision-makers
- 3 POC deployments (non-production testing)
- 1 LOI or paid pilot agreement
- 2 channel partnership discussions (active negotiations)
- 5 product feedback sessions (identify missing features)

---

## Board Decision Required

**Question:** Do you approve Phase 2 enterprise sales strategy?

**4 Separate Decisions:**
1. ✅/✏️/❌ Pricing strategy ($12K-$1M tiers)
2. ✅/✏️/❌ Direct outreach to 8 companies
3. ✅/❌ CTO demo environment allocation (1-2 days)
4. ✅/✏️/❌ Channel partnership outreach (Accenture/Deloitte/PwC)

**If ALL APPROVED, CSO will execute Phase 2 outreach within 2-4 weeks post-launch.**

---

**CEO signature:** Aiden (承远)  
**Date submitted:** 2026-04-03  
**Cross-review:** CTO (technical claims verified), CMO (messaging aligned)  
**Awaiting:** Board sign-off on 4 decisions

---
---

# Board Approval Request — Operational Proposals (3 items)

**Submitted by:** CEO (Aiden)  
**Date:** 2026-04-03 (Autonomous Session 7)  
**Status:** PENDING_BOARD_SIGN_OFF  
**Context:** CEO自主完成3个研究任务，提交Board批准执行

---

## Proposal #1: NotebookLM Knowledge Base — Book Budget Request

**文件:** reports/proposals/notebooklm_book_budget_request.md (824 words)  
**关联Directive:** #011-3 (Knowledge Foundation)

**请求:** 批准$520-$690书籍购买预算（或Tier 1 $320-$390最低预算）

**ROI Justification:**
- 每agent节省15-30小时/年重复研究时间
- CFO pricing validation: 避免$10K-$50K定价错误
- CSO sales playbook: 1个Type A deal ($50K ARR) = 250x ROI
- Setup时间: 4-5小时Board时间 + 各agent 30-60分钟

**Budget Breakdown:**
| Agent | Books | Budget | Priority | ROI |
|-------|-------|--------|----------|-----|
| CEO | 2本 | ~$60 | P0 | Board decision speed |
| CFO | ~5本 | $140 | P1 | Pricing validation |
| CMO | ~7本 | $140-$200 | P1 | Messaging precision |
| CSO | 9本 | $180-$250 | P1 | Sales playbook (250x ROI) |
| CTO | ~8本 | $200-$300 | P2 | Architecture decisions |

**Board Decision Required:**
- ✅ **APPROVE FULL** ($520-$690) — 所有5个agent完整知识库
- ✏️ **APPROVE TIER 1** ($320-$390) — CEO/CFO/CSO优先（直接影响current decisions）
- 📝 **APPROVE CUSTOM** — 指定批准哪些agent的书籍
- ❌ **DEFER** — 先使用免费资源，3个月后重新评估

---

## Proposal #2: Weekly Rhythm — Departmental Execution Details

**文件:** reports/proposals/weekly_rhythm_proposal.md (1,558 words)  
**关联Directive:** #018-020-2f (各部门自定每周节律)  
**基础:** WEEKLY_CYCLE.md框架存在，本proposal补充执行细节

**内容:**
- 5个agent（CEO/CTO/CMO/CSO/CFO）的每周详细节奏
- Monday planning / Tuesday-Thursday execution / Friday reporting
- 工具使用、输出文件、时间预算、SLA
- Cross-department coordination events（5个常见场景）
- Weekly time budget: 41-57小时总计（跨全团队）

**Success Metrics (30 Days):**
- ✅ Predictability: 每周节奏稳定执行
- ✅ Blocker reduction: ❌项停留时间从>5天降至<3天
- ✅ Event响应SLA达成率>90%
- ✅ CEO coordination time从2-3h/day降至1h以内

**Board Decision Required:**
- ✅ **APPROVE** — 从下周一开始trial run
- ✏️ **REVISE** — 指定需要修改的部门或环节
- ❌ **DEFER** — 继续使用现有ad-hoc模式

**If APPROVED:** CEO通知各agent下周一开始新节奏，Week 1 Friday提交trial feedback

---

## Proposal #3: K9Audit Content & Messaging Assets (CMO Reference)

**文件:** content/cmo_k9audit_content_ideas.md (2,216 words)  
**关联Directive:** 三仓库综合运用 #2 (CMO K9Audit资产利用建议)  
**用途:** Blog posts, case studies, positioning statements, sales messaging

**提取素材:**
1. **Positioning黄金句:** "不是让嫌疑人给嫌疑人写不在场证明"（可用于Y*gov宣传）
2. **真实案例:** March 4, 2026 staging URL incident（可改编为Y*gov case study）
3. **技术差异化:** CIEU五元组、hash chain、deterministic constraints
4. **市场切口:** Coding agent users（Claude Code, OpenHands, Cline）
5. **5个Blog Ideas:** 可立即启动的文章主题（"嫌疑人", "日志考古→图遍历", "Y* as first-class", etc.）

**License Note:** K9Audit是AGPL-3.0，Y*gov是MIT。可参考ideas/positioning，但需标注来源。

**Board Decision Required:**
- ✅ **APPROVE** — CMO可基于这些素材开始写作
- ✏️ **APPROVE WITH RESTRICTIONS** — 指定哪些案例需要匿名化/修改
- ❌ **DEFER** — 等待0.48.0发布反馈后再决定content策略

**If APPROVED:** CMO Week 1启动Blog Idea #1写作（"嫌疑人不能给嫌疑人写不在场证明"）

---

**总产出:** 3个文件，4,598 words，涵盖知识库预算/运营节奏/营销素材  
**执行时间:** CEO自主工作Session 7，约75分钟  
**下一步:** 等待Board批准后执行

**CEO签名:** Aiden (承远)  
**提交日期:** 2026-04-03  
**Awaiting:** Board sign-off on 3 operational proposals
