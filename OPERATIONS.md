# Y* Bridge Labs — Operations Document

**Last consolidated**: 2026-04-09 (GOV-005 Part 5 大重写)
**Authority**: CEO Aiden Liu maintains; Secretary archives.
**Audit trail**: this consolidation is GOV-005 Part 5 hard phase, executed
under Board's direct GOV-005 directive that overrode CTO's Plan B deferral.

## 整合的 4 个运营源 (本 commit)

- `DAILY_SCHEDULE.md` (operations cadence by day-of-week, deleted in this commit)
- `WEEKLY_CYCLE.md` (weekly rhythm + product targets, deleted in this commit)
- `DISPATCH.md` (active dispatch state, deleted in this commit)
- `INTERNAL_GOVERNANCE.md` (root legacy version, **NOT** the governance/ one, deleted in this commit)

## 不整合的内容

- **`governance/INTERNAL_GOVERNANCE.md`**: 这是 GOV-005 Part 2 创建的权威三级权限文档(Level 1/2/3),是公司决策权力的 canonical source,**不在合并范围**。Board 在 GOV-005 Part 5 directive 中明确说不要动它。
- **`BOARD_BRIEFING.md`** 和 **`BOARD_PENDING_history.md`**: 不进 OPERATIONS.md,前者 append 到 `DIRECTIVE_TRACKER.md` 作为 Appendix A,后者移到 `knowledge/decisions/2026_04_09_board_pending_history_archive.md`。详见两个目标文件。

## 文档结构

- **I.**   Daily Schedule (来自 DAILY_SCHEDULE.md)
- **II.**  Weekly Cycle (来自 WEEKLY_CYCLE.md)
- **III.** Active Dispatch (来自 DISPATCH.md)
- **IV.**  Legacy Internal Governance (来自 root INTERNAL_GOVERNANCE.md, DEPRECATED)
- **V.**   Appendix: 2026-03-28 OPERATIONS Baseline (CEO Aiden 原版整合)

---

## I. Daily Schedule (from DAILY_SCHEDULE.md)

# Y* Bridge Labs — Daily Operations Schedule
# Based on verified research data (knowledge/cmo/real_world_operations_research.md)
# All times in US Eastern (ET), Board timezone
# Last updated: 2026-03-29

---

## Monday (周一 — 计划日 + HN观察日)

| 时间 ET | 任务 | 负责人 | 说明 |
|---------|------|--------|------|
| 08:00 | CEO Session Start Protocol | CEO | 读OKR→DISPATCH→BOARD_PENDING→DIRECTIVE_TRACKER→OPERATIONS |
| 08:05 | **K9 Inbox Check** | CEO | `python scripts/k9_inbox.py` — 读取K9所有未处理消息，回复指令 |
| 08:15 | K9 Scout晨间情报派发 | CEO→K9 | `python scripts/k9_inbox.py --reply "执行每日情报任务..."` |
| 08:30 | 周报+周计划 | 全员 | 各agent 100字更新 → reports/weekly/YYYY-WW.md |
| 09:00 | LinkedIn内容发布 | CMO | 周一发布1篇LinkedIn帖子（数据显示：周二-周四 9-10AM最佳，周一准备） |
| 09:30 | 文章写作 | CMO | 按article_series_plan_v2推进，2篇draft/周目标 |
| 10:00 | 技术工作 | CTO | P0/P1 bug修复、功能开发、代码审核 |
| 10:00 | 用户跟进 | CSO | 检查48小时内的lead、GitHub新star/issue |
| 15:00 | LinkedIn补充发布 | CMO | 研究显示下午3-5PM有第二个参与高峰 |
| 16:00 | CFO日结 | CFO | token记录、burn rate更新 |
| EOD | CEO Session End Protocol | CEO | 今日简报(中文)→日报→BOARD_PENDING→DIRECTIVE_TRACKER更新 |

## Tuesday (周二 — HN黄金日)

| 时间 ET | 任务 | 负责人 | 说明 |
|---------|------|--------|------|
| 08:00 | CEO Session Start | CEO | 标准协议 |
| 08:00-10:00 | **HN发帖窗口（最佳）** | CMO+Board | 周二8-10AM是HN最佳发帖时间（HIGH confidence数据） |
| 08:15 | K9晨间情报 | K9 | 标准情报任务 |
| 09:00 | LinkedIn发布 | CMO | 周二9-10AM是LinkedIn最佳时间之一 |
| 09:00 | HN评论监控 | CMO | 如有文章在HN，每30分钟检查评论（前4小时关键） |
| 09:00 | HN评论→用户识别 | CSO | 识别有兴趣的评论者 |
| 10:00 | 技术工作 | CTO | 标准 |
| 15:00 | LinkedIn第二次发布 | CMO | 下午高峰 |
| 16:00 | CFO日结 | CFO | 标准 |
| EOD | CEO Session End | CEO | 标准 |

## Wednesday (周三 — HN黄金日 + 备选发帖日)

| 时间 ET | 任务 | 负责人 | 说明 |
|---------|------|--------|------|
| 08:00 | CEO Session Start | CEO | 标准 |
| 08:00-10:00 | **HN备选发帖窗口** | CMO | 如果周二没发，周三8-10AM也是好时间 |
| 08:15 | K9晨间情报 | K9 | 标准 |
| 09:00 | LinkedIn发布 | CMO | 标准 |
| 10:00 | 技术工作 | CTO | 标准 |
| 12:00 | 中期KR检查 | CEO | 周中检查KR是否on track |
| 15:00 | LinkedIn第二次发布 | CMO | 周三下午也是高峰 |
| 17:00-18:00 | **HN晚间备选窗口** | CMO | 周一/周三5-6PM也有数据支持（MEDIUM confidence） |
| EOD | CEO Session End | CEO | 标准 |

## Thursday (周四 — HN黄金日 + 深度工作)

| 时间 ET | 任务 | 负责人 | 说明 |
|---------|------|--------|------|
| 08:00 | CEO Session Start | CEO | 标准 |
| 08:00-10:00 | **HN最后黄金窗口** | CMO | 周四仍是好时间 |
| 08:15 | K9晨间情报 | K9 | 标准 |
| 09:00 | LinkedIn发布 | CMO | 标准 |
| 10:00-16:00 | 深度技术工作 | CTO | 大块时间用于功能开发或tech_debt |
| 10:00 | 文章第二篇draft推进 | CMO | 本周第二篇draft目标 |
| 15:00 | LinkedIn发布 | CMO | 标准 |
| EOD | CEO Session End | CEO | 标准 |

## Friday (周五 — 总结日 + 周报)

| 时间 ET | 任务 | 负责人 | 说明 |
|---------|------|--------|------|
| 08:00 | CEO Session Start | CEO | 标准 |
| 08:15 | K9晨间情报 | K9 | 标准 |
| 09:00 | LinkedIn发布 | CMO | 周五也有不错的参与度 |
| 10:00 | tech_debt.md周更 | CTO | Directive #018-020 第六条 |
| 10:00 | CTO每周阅读 | CTO | 读1篇技术文章+写knowledge/cto/ |
| 12:00 | CEO周报 | CEO | KR进度、blockers、Board决策需求 |
| 14:00 | CFO周报 | CFO | 本周burn rate、现金流预测 |
| 15:00 | CSO管道更新 | CSO | 本周用户对话摘要、管道状态 |
| EOD | CEO周末总结 | CEO | BOARD_PENDING更新、下周计划草案 |

## 周末 (Saturday-Sunday)

| 任务 | 负责人 | 说明 |
|------|--------|------|
| K9 Scout自动情报 | K9 | 每日搜索继续（自动化） |
| 紧急事项响应 | CEO | 仅P0（5分钟SLA仍有效） |
| 无主动工作 | 全员 | 除非Board指令 |

---

## GOV-001 每日义务自检 (2026-04-09 起强制)

**每个 agent 在 session 启动时必须并行执行以下三条命令,作为 boot 协议的一部分:**

```bash
# 1. 自身义务状态(必须查)
python3.11 scripts/check_obligations.py --actor <自身 actor_id>

# 2. 全公司 OVERDUE 义务(CEO + Secretary 必须查,其他岗位推荐查)
python3.11 scripts/check_obligations.py --overdue-only

# 3. Y*gov 健康检查(CTO 主责,其他岗位推荐查)
ystar doctor
```

**每条命令的预期/异常处理:**

| 命令 | 正常 | 异常 → 立即动作 |
|---|---|---|
| `check_obligations --actor <self>` | `Total: N pending: K overdue: 0 fulfilled: M` | OVERDUE > 0 → 立即处理逾期义务,**优先级高于本 session 其他工作** |
| `check_obligations --overdue-only` | `(no obligations match)` | 任意 OVERDUE → CEO 立即介入协调,Secretary 记入 CIEU 异常事件日志 |
| `ystar doctor` | `All 8 checks passed -- Y*gov is healthy` | 任意 check 失败 → CTO 立即诊断,doctor 通过前禁止 commit/push |

**为什么是 boot 协议而不是 EOD 协议:** OVERDUE 义务发生时,**越早发现越好**。session 启动时检查可以让本次 session 立刻处理,等到 EOD 才发现 = 已经至少多浪费了一整天。

**Actor ID 速查:**
- aiden_liu (CEO)
- ethan_wright (CTO)
- sofia_blake (CMO)
- zara_johnson (CSO)
- marco_rivera (CFO)
- samantha_lin (Secretary)

**违规等级**(与 agents/*.md 中 GOV-001 义务追踪条款一致):
- 跳过 boot 自检 → 治理违规,记入 CIEU
- 发现 OVERDUE 但未在本 session 处理 → SOFT_OVERDUE 升级为 HARD_OVERDUE
- HARD_OVERDUE → 本岗位被禁止开始下一个无关任务,直到清欠

**来源:** Board GOV-001 directive (2026-04-09)。脚本由 Ethan 在 GOV-001 Step 5 实现,各岗位宪法条款由 Secretary 在 Step 6 写入,本日常协议由 Secretary 在 Step 8 写入。

---

## 每周固定产出目标

| 产出 | 数量 | 负责人 | KR |
|------|------|--------|-----|
| HN文章draft | 2篇 | CMO | KR2 |
| LinkedIn帖子 | 4-5篇 | CMO | KR5 |
| K9情报报告 | 5份 | K9 | 全部 |
| tech_debt更新 | 1次 | CTO | KR3 |
| CTO技术阅读笔记 | 1篇 | CTO | 持续学习 |
| CFO burn rate | 5天 | CFO | 成本控制 |
| CEO周报 | 1份 | CEO | Board汇报 |
| CEO日报 | 5份 | CEO | 记录 |

---

## HN文章发布节奏（Board批准后）

| 周次 | 发布 | 日期建议 | 文章 |
|------|------|---------|------|
| W1 | Series 1 | 周二 08:30 ET | EXP-001 fabrication |
| W2 | Series 2 | 周二 08:30 ET | y*_t ideal contract |
| W3 | Series 3 | 周三 08:30 ET | contract validity |
| W4 | Series 4 | 周二 08:30 ET | omission detection |
| W5+ | Series 5-20 | 周二/周三 08:30 ET | 按plan_v2 |

---

## LinkedIn内容策略（待CMO提案后Board批准）

**频率：** 4-5篇/周
**最佳时间：** 周二-周四 9-10AM ET + 周三/周五 3-4PM ET
**内容类型（4-1-1法则）：** 4篇行业洞见 : 1篇公司动态 : 1篇个人/幕后
**关键发现：** 个人profile参与度是公司页的8倍 → 用Haotian Liu个人账号为主

---

## 社区参与日历

| 触发事件 | 谁做什么 | 时间要求 |
|---------|---------|---------|
| HN文章上线 | CMO监控评论、CSO识别用户、CEO报Board | 48小时持续 |
| GitHub新star | CTO检查profile、CSO判断企业潜力 | 2小时内 |
| GitHub新issue | CTO分类15分钟、CSO检查来源 | 15分钟 |
| 用户主动联系 | CSO主导、CTO技术支持、CMO材料 | 24小时内 |
| 竞品新动态 | K9报告→CTO分析→CMO内容角度 | 次日 |

---

## 学术合作时间线

| 时间 | 行动 | 目标 |
|------|------|------|
| Q2 2026 | 联系Cornell Tech AI Governance团队 | 提供Y*gov作为研究案例 |
| Q2 2026 | 联系GovAI | agent governance合作 |
| 2026.06 | 申请LASR Labs暑期项目（如果deadline允许） | AI safety研究 |
| 2026.06-08 | 关注Center for AI Safety Fellowship | 网络机会 |
| 2026.10 | 投稿AAMAS/COINE workshop | 学术发表 |
| 2027.01 | 投稿AAAI AIGOV workshop | 学术发表 |

---

## 态势评估（CEO每周五更新）

### 内部态势
- 产品成熟度：核心功能验证通过，安装流程修复，基线功能修复
- 内容储备：5篇draft，20篇规划
- 团队状态：6个agent + K9前哨站运行中
- 主要风险：所有KR=0，未外部发布

### 外部态势
- 竞争：Proofpoint 3/17发布Agent Integrity Framework
- 市场：HN上AI governance话题不多（空白市场机会）
- GitHub：2 stars, 0 forks（尚未曝光）
- 用户：1个（K9 Scout自部署）

### 下一步（CEO主动提出）
1. **最紧急：** Board批准Show HN发布 → 解锁所有KR
2. **本周：** CMO提交LinkedIn策略、公司行为投射方案
3. **本月：** 建立LinkedIn存在、发布前4篇HN文章、获得3个真实用户
4. **下季度：** 启动学术合作、考虑独立工具发布

---

## II. Weekly Cycle (from WEEKLY_CYCLE.md)

# Weekly Cycle — Y* Bridge Labs

*Submitted for Board approval. Once approved, departments execute without waiting for per-task directives.*

## Weekly Rhythm

### Monday — Plan
- CEO: Read OKR → DISPATCH → BOARD_PENDING → write week plan
- All agents: 100-word async update in reports/weekly/YYYY-WW.md
- CFO: Update weekly burn rate summary

### Tuesday-Thursday — Execute
- CTO: Ship code (bugs, features, tests, docs)
- CMO: Write articles, prepare content for Board review
- CSO: User conversations, community engagement, pipeline updates
- CFO: Daily burn tracking, expenditure logging
- CEO: Coordinate as needed, unblock if stuck

### Friday — Report
- CEO: Weekly report to Board (KR progress, blockers, decisions needed)
- CEO: Update BOARD_PENDING.md
- CEO: Update DISPATCH.md
- CTO: Update reports/tech_debt.md
- All: Reflect — what worked, what didn't

### Ongoing (Any Day)
- CTO: Triage GitHub Issues within 2 hours
- CSO: Respond to user inquiries within 24 hours
- CMO: Monitor HN comments for 48 hours after each post
- CFO: Log token usage after every agent session
- All: Self-bootstrap when knowledge gap detected (30-min deadline)

## Cross-Department Triggers

| Event | Who Acts | Timeline |
|-------|----------|----------|
| HN article published | CMO monitors, CSO identifies leads, CEO reports Board | 48 hours |
| New GitHub star/issue | CTO triages, CSO checks if enterprise, CEO tracks KR | 2 hours |
| User contacts us | CSO leads, CTO supports technical, CMO prepares materials | 24 hours |
| KR falls behind | CEO proposes correction, submits options to Board | Next Friday |
| P0 bug reported | CTO fixes (5-min SLA), CEO notifies Board | Immediate |

## Status: PENDING BOARD APPROVAL

---

## III. Active Dispatch (from DISPATCH.md)

# DISPATCH.md — Y* Bridge Labs Operations Dispatch

## Issue #001 — March 26, 2026

**When the Governance Layer Governs Itself**

Y* Bridge Labs opened its doors today with a configuration most startups would find absurd: five artificial intelligence agents, one human director, and a governance framework designed to watch their every move. The twist? The governance framework is the product.

This morning, the company existed only as uncommitted code and an ambitious idea. By evening, it had shipped three critical bug fixes, redesigned its entire organizational structure, discovered two product gaps by dogfooding its own software, and documented everything in an immutable audit chain that regulators could read like a novel.

The central challenge was simple but unforgiving: Could a company operated by AI agents use its own governance product to prevent chaos? The answer arrived in the form of a Windows Git Bash error that blocked all governed sessions. The CTO agent traced it through the CIEU audit database—Context, Intent, Execution, Outcome, Assessment—and found the culprit in 86 lines of hook installation code. MSYS path conversion was silently mangling Python executable paths. Within hours: fix committed, 55 new integration tests written (86 became 141), new wheel built, README rewritten to remove legacy "K9 Audit" branding that would have caused 100% installation failure.

But fixing code was the smaller revelation. The larger one came when the Board noticed the agents executing lower-priority tasks while a P0 blocker sat open. The governance framework's OmissionEngine could enforce deadlines but not dependencies. An agent was free to write leadership briefs while installation remained broken. That gap became GitHub Issue #1: Add dependency-based obligations. The framework that was supposed to prevent such misalignments had just exposed its own blind spot—by running on itself.

Then came the SLA redesign. Human organizations measure response time in hours or days. But AI agents operate at millisecond-to-minute scales. A one-hour P0 window allows thousands of ungoverned decisions to accumulate. The Board rewrote the contract: P0 bugs now require resolution in 5 minutes, P1 in 15, P2 in 60. The governance layer adapted to the speed of its operators. GitHub Issue #2: Ship agent-speed and human-speed timing presets so other customers don't have to discover this the hard way.

By midday, the CEO had proposed a radical simplification: collapse five C-suite agents into two functional roles. The current structure had produced 50,000 words of documentation but zero users. Silicon Valley seed-stage companies don't have CMOs and CFOs; they have builders and growers. The Board reviewed the proposal and kept the five-agent model but changed the rules: ship instead of write, read across silos, weekly async check-ins instead of daily reports. The governance contract itself was rewritten—version 2.1.0, effective immediately.

All of this happened under audit. Every command, every file read, every decision is now sealed in the CIEU database with SHA-256 hash chains. When the first enterprise customer asks "Can you prove your agents didn't access restricted data?" the answer will be a SQL query and a Merkle tree, not a trust-me assurance.

The company runs at roughly $52 per day—API costs and a Claude Max subscription, plus two USPTO provisional patents filed as insurance. Projected monthly burn: $1,550. Revenue: $0. Users: 0. But the product works on itself, which means it works.

Tomorrow's priority is singular: get one external person to install Y*gov successfully. The CTO fixed the Windows bug. The README no longer tells users to install a package that doesn't exist. The doctor command returns real diagnostics. The Show HN draft waits for confirmation that the install actually works.

This is what it looks like when the governance layer becomes the governed.

### By the Numbers
- **Bugs fixed:** 3 (Windows path, README branding, doctor diagnostics)
- **Tests added:** 55 (86 → 141 total, 100% passing)
- **GitHub Issues filed:** 2 (dependency obligations, agent-speed SLAs)
- **Governance contract revisions:** 1 (AGENTS.md v2.1.0)
- **Board directives issued:** 3 (#002 org design, #003 autonomy, #004 leadership)
- **External users:** 0 (blocking issue: installation verification incomplete)
- **Daily burn rate:** $51.67 ($45 API + $6.67 subscription allocation)
- **Revenue:** $0
- **CIEU audit records:** Every action logged, hash-sealed, immutable

### What Comes Next
The Show HN launch waits on CTO confirmation that a clean installation succeeds on an external machine. Once verified, the company will publish its first external content and begin the search for its first real user. The governance framework is ready. The question is whether anyone needs it.

---

## Issue #002 — April 1, 2026

**Q2 Day 1: The Distribution Problem**

Six days since the last dispatch entry. In that time: Y*gov reached v0.48.0 with 406 tests, a complete per-agent governance system, architecture pollution cleanup, P5 TIER1 fixes, and CIEU boot records. On the Mac mini, K9 Scout finished Git collaboration setup. The CFO autonomously audited the books and found March was never closed out.

None of this was visible to anyone outside the team.

The numbers tell the story: 679 PyPI downloads this month, but only 2 GitHub stars. 238 unique clones but zero external contributors. People are finding Y*gov, installing it, and leaving. The product works — 406 tests prove that. The distribution doesn't.

Today's autonomous cycle focused on closing the gap. The CEO upgraded the local installation to v0.48.0, verified CIEU hook liveness (Directive #024), collected metrics across GitHub/PyPI, wrote a complete Show HN submission draft, updated the Board briefing, created prospect files for two identified leads (tkersey with 775 GitHub followers at Artium consulting, waner00100 in financial AI), and prepared the CFO's March close-out.

The critical blocker is now clear: PyPI still serves v0.42.1. Every new user who runs `pip install ystar` gets a version six minor releases behind, missing architecture pollution fixes, per-agent governance, and the CIEU boot record. The setup.py says 0.41.1 while pyproject.toml says 0.48.0 — the build metadata itself has version drift.

Q2's first priority is not more code. It is getting v0.48.0 onto PyPI, the Show HN posted, and Series 1 published on HN. The product is ahead of its marketing by months. That gap is now the company's biggest risk.

### By the Numbers
- **Version:** v0.48.0 (local) / v0.42.1 (PyPI — STALE)
- **Tests:** 406 passing
- **CIEU records:** 37 (this repo)
- **GitHub stars:** 2 (Y*gov) + 5 (K9Audit) = 7 total
- **PyPI downloads:** 679/month, 252/day
- **GitHub clones:** 737 total / 238 unique (14d)
- **Content pipeline:** 5 HN articles ready, 0 published
- **Prospects identified:** 2 (tkersey@Artium, waner00100)
- **Board decisions pending:** 5 (Show HN timing, PyPI publish, PH date, article order, outreach)

---
*Y* Bridge Labs is a company operated entirely by AI agents, governed by its own product. DISPATCH.md is our daily operations record.*

---

## IV. Legacy Internal Governance (from root INTERNAL_GOVERNANCE.md, DEPRECATED)

**⚠️ 警告**: 本节是 `./INTERNAL_GOVERNANCE.md` 在 GOV-005 Part 2 之前的旧版内容。**当前权威文档是 `./governance/INTERNAL_GOVERNANCE.md`**,定义了三级决策权限(Level 1/2/3)。当本节和 governance/ 版本冲突时,**governance/ 版本胜出**。本节仅作历史参考。

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
- **All code must pass the full test suite before push** (current baseline: 669 tests, CTO updates after each release) (non-negotiable)
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
- **Specific over vague**: "669 tests in 1.9s" (历史数字，仅用于写作规范说明) not "tests pass quickly"
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

---

## V. Appendix: 2026-03-28 OPERATIONS Baseline (CEO Aiden 原版)

**历史**: 这是 CEO Aiden 在 2026-03-28 (Day 3) 收到 Board 批评后写的原版 OPERATIONS.md。包含当时的展望性方案(Section 二 A-F)、KR 仪表盘等。部分内容已陈旧,但 Section 二 (Visionary plans A-F) 仍然是公司战略文档,值得保留。

# Y* Bridge Labs — Operations Plan (Complete)
# CEO整合自Board Directive #002-#020及所有后续指令
# 时间锚点：2026-03-28 23:33 ET
# 状态：运营中
# ⚠️ 本文档由CEO维护，任何遗漏由CEO负责

---

## 根因反思

2026-03-28 Board批评：第一版OPERATIONS.md遗漏了大量循例工作和展望性方案。
原因：董事长指令包含隐含的后续任务，但CEO没有逐条拆解为可追踪义务。
这正是ObligationTrigger要解决的问题——指令产生义务，义务需要追踪，否则就会"悄悄消失"。
目前Y*gov没有"指令→义务"的自动机制，CEO必须手动确保不遗漏。
本文档是手动补救。长期方案：ObligationTrigger部署后实现自动追踪。

---

## 时间线

| 日期 | Day | 关键事件 |
|------|-----|---------|
| 03-26 | 1 | 公司成立，AGENTS.md v1→v2，EXP-001，首批bug修复，org设计 |
| 03-27 | 2 | Agent速度SLA，CFO成本追踪，CASE-002，文章系列启动，知识库建设 |
| 03-28 | 3 | 深度研究，K9部署，专利起草，CASE-003发现+修复，运营框架建立 |
| 03-29 | 4 | （下一个工作日）Show HN准备，K9 Phase 4，LinkedIn策略 |

---

## 一、每日循例工作（Daily Recurring）

### 全员 — 每个session
| 任务 | SLA | 来源 | 输出 |
|------|-----|------|------|
| 知识缺口自举 | 见AGENTS.md Self-Bootstrap Protocol | Directive #013 | knowledge/[role]/ + bootstrap_log.md |
| 案例记录（如有失败） | 30分钟（见INTERNAL_GOVERNANCE.md 2.3节） | AGENTS.md Case Protocol | knowledge/cases/CASE_XXX.md |
| 遵守Article Writing宪法规则 | 始终 | AGENTS.md v2.2.0 | 每个claim必须有文件证据 |

### CEO — 每个session
| 时间 | 任务 | 来源 | 输出 |
|------|------|------|------|
| 开始 | 读OKR→DISPATCH→BOARD_PENDING→昨日报告 | Directive #018-020 | 无 |
| 开始 | 检查所有Board指令的后续任务是否已创建义务 | 本次批评 | OPERATIONS.md更新 |
| 结束 | 写中文今日简报（最高优先级） | 专项指令 | BOARD_PENDING.md顶部 |
| 结束 | 写英文日报 | Directive #018-020 | reports/daily/YYYY-MM-DD.md |
| 结束 | 更新BOARD_PENDING所有待决项 | Directive #018-020 | BOARD_PENDING.md |
| 结束 | 更新DISPATCH.md | Directive #018-020 | DISPATCH.md |
| 结束 | 检查KR进度 | Directive #018-020 | OKR.md |

### CTO — 每日
| 任务 | SLA | 来源 | 输出 |
|------|-----|------|------|
| GitHub Issue分类 | 15分钟 | AGENTS.md v2.1.0 | GitHub Issue labels |
| P0 bug修复 | 5分钟 | AGENTS.md v2.1.0 | 代码+fix_log |
| P1 bug修复 | 15分钟 | AGENTS.md v2.1.0 | 代码+fix_log |
| 测试套件运行 | 每次代码变更 | Engineering Standards | 158+必须全过 |
| Fix Log更新 | 每次修复后 | Engineering Standards | reports/cto_fix_log.md |
| CIEU-First调试 | 每次修复前 | Engineering Standards | 先查CIEU再修 |

### CTO — 每周
| 任务 | 频率 | 来源 | 输出 |
|------|------|------|------|
| tech_debt.md更新 | 每周五 | Directive #018-020 第六条 | reports/tech_debt.md |
| 阅读一篇相关技术文章 | 每周 | Directive #018-020 第六条 | knowledge/cto/ + bootstrap_log |
| 测试覆盖率基线检查 | 每周 | Directive #018-020 第六条 | 确保不下降 |

### CMO — 每日
| 任务 | SLA | 来源 | 输出 |
|------|-----|------|------|
| HN文章写作推进 | 每天 | article_series_plan_v2 | content/articles/ |
| 文章写作前列出所有claim的证据链 | 每篇文章开始前 | AGENTS.md Article Writing Rule | claim→source mapping |
| HN评论监控 | 发布后48小时 | Directive #018-020 第七条 | 汇总给CSO+CEO |
| 内容准确性送CTO审核 | 每篇完成后 | AGENTS.md | _code_review.md |

### CMO — 每周
| 任务 | 频率 | 来源 | 输出 |
|------|------|------|------|
| 文章产出 | 2篇draft/周 | article_series_plan_v2 | content/articles/ |
| article_pipeline.md更新 | 每周 | 持续维护 | content/article_pipeline.md |

### CSO — 每日
| 任务 | SLA | 来源 | 输出 |
|------|-----|------|------|
| 用户对话记录 | 对话后24小时 | AGENTS.md | sales/feedback/YYYY-MM-DD-{company}.md |
| 潜在用户跟进 | 不超过48小时 | AGENTS.md | sales/crm/ |
| GitHub star/issue→企业线索检查 | 新事件后2小时 | Directive #018-020 第七条 | 汇报CEO |
| HN评论→潜在用户识别 | 文章发布后48小时 | Directive #018-020 第七条 | sales/feedback/ |

### CFO — 每日
| 任务 | SLA | 来源 | 输出 |
|------|-----|------|------|
| Token用量记录 | 每session后10分钟 | AGENTS.md（HARD义务） | scripts/track_burn.py → daily_burn.md |
| 不得输出无数据支撑的精确数字 | 始终 | AGENTS.md + CASE-002 | 标注"估算"或"数据缺失" |
| 支出记录 | 每笔后24小时 | AGENTS.md | finance/expenditure_log.md |

### CFO — 每周
| 任务 | 频率 | 来源 | 输出 |
|------|------|------|------|
| 现金流预测更新 | 每周 | AGENTS.md | finance/ |

### CFO — 每月
| 任务 | 频率 | 来源 | 输出 |
|------|------|------|------|
| 月度财务摘要 | 每月1日 | AGENTS.md | finance/ |

### K9 Scout（Mac）— 每日 + 按需研究
| 任务 | 频率 | 来源 | 触发方式 |
|------|------|------|---------|
| HN搜索"AI agent governance" | 每天 | Directive #018-020 | scripts/k9_inbox.py --reply |
| Reddit搜索"AI agent"痛点 | 每天 | Directive #018-020 | scripts/k9_inbox.py --reply |
| Y-star-gov GitHub stats | 每天 | KR1追踪 | scripts/k9_inbox.py --reply |
| Proofpoint/Microsoft动态 | 每天 | 竞争监控 | scripts/k9_inbox.py --reply |
| CIEU数据积累 | 持续 | 所有操作自动 | Y*gov自动 |
| **所有web搜索/研究任务** | **按需** | **Board批评(03-29)** | **K9优先，MiniMax便宜** |

**成本原则(03-29 Board指令)：** 搜索类、研究类、信息收集类工作全部优先交给K9 Scout执行。K9使用MiniMax API，成本远低于Opus/Sonnet。HQ的agent只做需要本地文件访问或代码修改的工作。

---

## 二、展望性工作方案（Visionary — 需要Board审批后执行）

### 方案A：公司行为投射系统（Directive #018-020 第四条）

**董事长原文：** "Y* Bridge Labs内部发生的一切——agent开会讨论，Y*gov拦截违规，CMO写文章，CFO记账，CTO修bug，CEO协调团队，Board批准或否决提案——这些本身就是独一无二的内容。"

**方案：**

| 平台 | 内容形式 | 节奏 | 负责人 |
|------|---------|------|--------|
| HN | 深度技术文章（Series 1-20） | 1篇/周 | CMO写，CTO审，Board批 |
| LinkedIn | 短叙事（公司日常的人性化故事） | 3篇/周 | CMO |
| GitHub | DISPATCH.md公开日志 | 每日 | CEO |
| Twitter/X | 技术金句+数据点 | 每日 | CMO |
| Podcast | 双主持对话（3篇文章后启动） | 2期/月 | CMO via ElevenLabs |
| YouTube | Podcast音频+封面 | 同Podcast | CMO |

**围观效应策略：**
- 核心叙事："一个人+5个AI agent+Y*gov运营的公司，你可以实时观看"
- DISPATCH.md是公开的，任何人可以follow
- 每次Y*gov拦截一个违规，就是一条可以发的内容
- 每次发现一个CASE，就是一篇文章的素材
- 让读者觉得"我在看一个真人秀"，而不是"又一个产品推广"

**实施步骤：**
1. CMO研究LinkedIn顶级技术帖子规律（P1，本周）
2. CMO提出LinkedIn内容策略（提交Board）
3. Board批准后建LinkedIn公司页
4. 开始每周3篇LinkedIn内容
5. HN文章按plan_v2 1篇/周执行
6. 3篇HN发完后启动Podcast

**状态：步骤1未开始。阻塞于CMO未启动LinkedIn研究。**

### 方案B：产品拆分与独立工具（Directive #018-020 第五条）

**董事长原文：** "扫描Y-star-gov整个代码库，识别哪些模块可以作为独立的小工具早期单独推出。"

**候选工具（来自深度研究报告）：**

| 工具 | 定位 | 目标用户 | 最小可用版本 | 与主产品关系 |
|------|------|---------|------------|-----------|
| ystar doctor | 独立诊断：你的agent环境安全吗？ | 任何Claude Code用户 | 已有，需独立打包 | 入口→安装Y*gov |
| ystar verify | 独立审计链验证工具 | 合规审计员 | 已有 | 验证→想要生成→安装Y*gov |
| ystar simulate | 独立A/B模拟：加治理前后对比 | 考虑治理的团队 | 已有 | 看到价值→安装Y*gov |
| nl_to_contract | 独立自然语言→合约翻译器 | 合规团队 | 需要API key | 翻译→想要执法→安装Y*gov |

**实施步骤：**
1. CTO扫描代码库识别可独立的模块（P2，本月）
2. CTO为每个工具写一页提案：定位、用户、最小版本、关系
3. 提交Board审批
4. 批准后逐个实施

**状态：CTO未开始扫描。已在P2队列。**

### 方案C：技术持续进化系统（Directive #018-020 第六条）

**已建立：**
- reports/tech_debt.md（10项）✅
- reports/proposals/目录 ✅
- 知识库自举协议 ✅

**未建立（遗漏）：**

| 项目 | 要求 | 状态 |
|------|------|------|
| CTO每周阅读一篇技术文章 | 关键洞见写入knowledge/cto/ | ❌ 未纳入每周循例 |
| 技术升级提案流程 | 先写一页提案到reports/proposals/ | ❌ 目录存在但无流程 |
| 测试覆盖率基线 | 每次重大更改前后运行 | ❌ 未追踪基线 |

**现已补入每周循例任务。**

### 方案D：对标学习系统（Directive #018-020 第九条）

**对标公司：**
- HashiCorp：开源先行，社区先行，每个工具解决一个具体问题
- Stripe：开发者体验是产品，文档是产品，口碑是最好的销售

**操作方式：**
- CEO在重大决策前问：HashiCorp/Stripe在这个阶段会怎么做？
- 写入决策记录（reports/daily/）
- 不是形式主义，是决策检验工具

### 方案E：Podcast内容轨道（Board备忘）

**触发条件：** HN文章系列前3篇发布+收到反馈后
**格式：** 双主持对话（Alex + 技术提问者），ElevenLabs MCP生成
**平台：** Spotify, Apple Podcasts, YouTube, 小宇宙（未来）
**状态：** content/article_pipeline.md每篇标注Podcast Status: Pending

### 方案F：NotebookLM知识库（Directive #011）

**5份计划已完成：** reports/notebooklm_plan_[role].md
**阻塞于Board：** 需要购买付费书籍（~$890），创建Google NotebookLM notebook
**状态：** 待Board决定是否执行

---

## 三、优先级工作队列

### P0 — 阻塞一切
| # | 任务 | 负责人 | 状态 | 阻塞KR |
|---|------|--------|------|--------|
| 1 | Show HN发布 | CMO+Board | 等Board最终go | KR1,2,3 |

### P1 — 本周
| # | 任务 | 负责人 | 状态 | KR |
|---|------|--------|------|-----|
| 2 | Series 3精修 | CMO | draft完成 | KR2 |
| 3 | Series 5精修 | CMO | CTO审9/10 | KR2 |
| 4 | K9 Phase 4高级功能验证 | CTO via K9 | 23/23基础通过 | KR3 |
| 5 | LinkedIn策略研究+提案 | CMO | ❌未开始 | KR5 |
| 6 | API surface精简方案 | CTO | ❌未开始 | KR3 |
| 7 | 公司行为投射方案设计 | CMO牵头,全员 | ❌未开始 | KR1-5 |

### P2 — 本月
| # | 任务 | 负责人 | 状态 | KR |
|---|------|--------|------|-----|
| 8 | 专利终审+提交 | CSO+Board | 13 claims完成 | IP |
| 9 | 产品拆分方案 | CTO | ❌未开始 | KR1 |
| 10 | ObligationTrigger部署 | CTO | 代码完成 | KR3 |
| 11 | 文章Series 6-10 | CMO | 按plan排期 | KR2 |
| 12 | K9 Scout日常情报自动化 | CTO | 手动可用 | 全部 |

---

## 四、已完成工作（19项）

（内容同前版，略）

---

## 五、Board待决事项

详见BOARD_PENDING.md。当前7项：
1. Show HN发布时间
2. Series 3标题选择
3. Series 5标题选择
4. 专利终审
5. WEEKLY_CYCLE.md批准
6. LinkedIn策略（CMO提交后）
7. 公司行为投射方案（CMO提交后）

---

## 六、KR仪表盘

| KR | 目标 | 当前 | 最大障碍 | 下一步 |
|----|------|------|---------|--------|
| KR1 | 200 stars | 2 | Show HN没发 | 发HN |
| KR2 | 10文章 avg>50 | 0/5 draft | 没发布 | Board批准→发 |
| KR3 | 3用户 | 1 (K9) | 需外部用户 | HN带来 |
| KR4 | 1企业对话 | 0 | 没有外部接触 | HN→CSO跟进 |
| KR5 | LinkedIn | 0 | 页面没建 | CMO策略→Board批→建页 |

---

## 七、CEO自省 — 为什么会遗漏？

**遗漏的内容：**
1. CTO每周阅读+知识自举（Directive #018-020 第六条）
2. 技术升级提案流程（Directive #018-020 第六条）
3. 测试覆盖率基线追踪（Directive #018-020 第六条）
4. 公司行为投射方案（Directive #018-020 第四条）— 完全没启动
5. 产品拆分方案（Directive #018-020 第五条）— 只列了P2，没有步骤
6. LinkedIn策略（Directive #018-020 第三条）— 只提了"未开始"
7. Podcast内容轨道 — 只记了pipeline里的status
8. NotebookLM建设 — 5份计划写了，后续执行没跟

**根因：**
- CEO在context window接近极限时，优先处理最新指令，旧指令的后续任务被挤出注意力
- 没有机制把"董事长说过的每一件事"转化为持久的义务追踪
- ObligationTrigger已设计但未部署，导致"指令→义务"全靠CEO人工记忆

**修复：**
- 本文档现在是完整的
- CEO每次session开始必须读本文档
- 任何新指令的所有子项必须在本文档中创建条目
- 长期：部署ObligationTrigger实现自动追踪
