# Weekly Rhythm Proposal — Departmental Execution Details

**提交者:** CEO (Aiden)  
**日期:** 2026-04-03 (Autonomous Session 7)  
**关联Directive:** #018-020-2f (各部门自定每周节律)  
**基础文档:** WEEKLY_CYCLE.md (框架已存在，需部门填充)  
**状态:** PENDING_BOARD_APPROVAL

---

## Executive Summary

WEEKLY_CYCLE.md提供了公司级框架（Monday Plan, Tuesday-Thursday Execute, Friday Report）。本提案补充各部门**具体可执行节奏**，包括：工具使用、输出文件、时间预算、SLA。

**目标：** 使各部门在无Board directive情况下，可自主维持predictable工作节奏。

---

## CEO — Weekly Rhythm

### Monday 09:00-10:00 — Week Planning (1 hour)
**Input读取顺序：**
1. `OKR.md` — 检查KR进度（红黄绿标记）
2. `DISPATCH.md` — 本周active initiatives
3. `BOARD_PENDING.md` — 等待决策的项目
4. `DIRECTIVE_TRACKER.md` — 检查❌项（>3天 = escalate）
5. `reports/tech_debt.md` — CTO上周更新的技术债
6. `reports/weekly/YYYY-WW.md` — 各agent 100-word updates

**Output产出：**
- `reports/ceo/week_plan_YYYY-WW.md` — 本周3个focus areas
- DIRECTIVE_TRACKER.md更新（❌项分析）
- Slack/Email to team（如果有urgent unblock需求）

**时间预算：** 60分钟

---

### Tuesday-Thursday — Coordination Mode (按需触发)
**持续监控（每日检查2次，上午10:00 + 下午15:00）：**
- GitHub Issues（CTO是否被P0 bug阻塞）
- BOARD_PENDING.md（是否有新决策可推进）
- 各agent reports/（是否有blocker上报）

**触发条件响应：**
- **P0 bug报告** → 5分钟内联系Board + 协调CTO优先级
- **Agent被阻塞** → 30分钟内分析blockers，escalate或协调其他agent支援
- **跨部门协作需求** → 1小时内协调时间，创建临时sync meeting plan

**工具：**
- `ystar doctor --layer1` — 每天运行1次（检查CIEU健康）
- `git status` — 检查各repo是否有uncommitted work遗留

**时间预算：** 每天30-60分钟（如果无blocker，可低至15分钟）

---

### Friday 16:00-18:00 — Weekly Reporting (2 hours)
**Pre-Report数据收集（16:00-16:30）：**
1. 读取各agent reports/weekly/YYYY-WW.md
2. 汇总本周完成任务数（DIRECTIVE_TRACKER.md）
3. 检查OKR.md KR进度变化
4. 统计CIEU violations trend（if applicable）
5. 准备下周Board决策点（BOARD_PENDING.md更新）

**Report写作（16:30-17:30）：**
- `reports/ceo/weekly_board_report_YYYY-WW.md`
- 结构：本周进展 / KR状态 / Blockers / 下周决策点
- 长度：800-1200 words
- Tone：数据驱动，problem-focused

**BOARD_PENDING.md更新（17:30-17:45）：**
- 新增需Board批准的项目
- 更新pending项目状态

**DISPATCH.md更新（17:45-18:00）：**
- Close已完成initiatives
- Update active initiatives进度

**时间预算：** 120分钟

---

### Ongoing — 贯穿全周
- **Session handoff维护：** 每次session结束前更新memory/session_handoff.md（5分钟）
- **Directive decomposition：** 收到Board新指令后10分钟内拆解到DIRECTIVE_TRACKER.md
- **Knowledge gap bootstrap：** 发现知识缺口30分钟内写入knowledge/ceo/

**Y*gov enforcement obligations:**
- `directive_decomposition: 600` (10分钟)
- `knowledge_gap_bootstrap: 1800` (30分钟)
- `weekly_board_summary: 604800` (每周)

---

## CTO — Weekly Rhythm

### Monday 10:00-11:00 — Technical Planning (1 hour)
**Input读取：**
1. `reports/tech_debt.md` — 上周自己的更新
2. `OKR.md` — KR2技术指标（测试数、性能、安装成功率）
3. GitHub Issues triage结果（上周accumulated issues）
4. DIRECTIVE_TRACKER.md中CTO负责的❌项

**Output产出：**
- `reports/cto/week_plan_YYYY-WW.md` — 本周P0/P1/P2任务优先级
- GitHub Issues打标签（P0/P1/P2/Backlog）
- 如有P0 blockers → 立即escalate to CEO

**工具：**
- `ystar doctor --layer1` — 每周一必跑（CIEU健康检查）
- `pytest --co -q` — 快速检查测试数量（应match README.md）

**时间预算：** 60分钟

---

### Tuesday-Thursday — Engineering Execution (4-6 hours/天)
**Daily routine（每天开始）：**
1. `git status` 检查3个repos（ystar-company, Y-star-gov, K9Audit if applicable）
2. 运行 `pytest -x` 检查测试suite健康（失败则P0修复）
3. 读取GitHub Issues新增（2小时triage SLA）

**执行优先级：**
- **P0:** 安装失败bug、测试suite regression、production CIEU异常
- **P1:** 新功能开发（按OKR KR2排序）
- **P2:** 技术债偿还、重构、文档

**Commit规范：**
- 每个功能commit后必须运行 `pytest` 确保通过
- 每次push前必须运行 `ystar doctor --layer1`
- Commit message格式：`type(scope): description` (Conventional Commits)

**Cross-review SLA:**
- 关键文件修改后30分钟内请求peer review（from CEO/CMO，视文件类型）
- 其他agent请求review → 2小时内响应

**时间预算：** 每天4-6小时（focus time）

---

### Friday 15:00-16:00 — Tech Debt Review (1 hour)
**Output产出：**
- 更新 `reports/tech_debt.md`（新增本周发现的债务）
- 如有新断裂机制发现 → 标记为下周P1任务
- 统计本周code metrics：
  - 测试数量变化（559 → ?）
  - CIEU violations trend（if running governance loop）
  - 性能regression（if applicable）

**Tool：**
- `ystar doctor --layer2 --design-debt` — 每两周运行1次（深度设计债分析）

**时间预算：** 60分钟

---

### Ongoing — 贯穿全周
- **GitHub Issues triage：** 2小时SLA
- **P0 bug修复：** 5分钟SLA start（不一定5分钟修完，但5分钟内开始）
- **Pre-commit verification：** 每次commit前运行tests
- **Knowledge self-bootstrap：** 每周五2小时阅读时间（从Week 2 post-launch开始）

**Y*gov enforcement obligations:**
- `pre_commit_test: 60` (commit前1分钟)
- `distribution_verify_post_push: 300` (push后5分钟)

---

## CMO — Weekly Rhythm

### Monday 11:00-12:00 — Content Planning (1 hour)
**Input读取：**
1. `content/article_series_plan_v2.md` — 20篇文章规划
2. DIRECTIVE_TRACKER.md中CMO负责的文章任务
3. 上周HN post performance（if applicable）
4. CSO反馈的user questions（可能是blog topic来源）

**Output产出：**
- `content/cmo/week_plan_YYYY-WW.md` — 本周写作目标（draft/CTO review/Board review状态）
- 如有LinkedIn策略/社交媒体计划 → 列入本周tasks

**时间预算：** 60分钟

---

### Tuesday-Thursday — Content Creation (3-4 hours/天)
**Writing workflow（每篇文章）：**
1. **Source verification FIRST (30分钟)：**
   - 列出文章中所有factual claims
   - 每个claim标注source（file path + line, or commit hash）
   - 如无source，删除该claim（AGENTS.md Article Writing Constitutional Rule）

2. **Draft写作 (2-3小时)：**
   - 按照knowledge/cmo/hn_writing_guide.md风格
   - 800-1200 words optimal
   - Technical storytelling tone

3. **Self-review (30分钟)：**
   - 检查是否符合平台最佳实践（HN/LinkedIn/Dev.to等）
   - 无marketing hype（"revolutionary", "game-changing"禁用）
   - 是否adds genuine value

4. **Submit for CTO review：**
   - 创建 `content/cto_review_request_[article_name].md`
   - CTO 30分钟SLA响应

**时间预算：** 每天3-4小时

---

### Friday 14:00-15:00 — Performance Analysis (1 hour)
**如果本周有HN post发布：**
- 统计upvotes, comments, click-through rate
- 分析top comments（user关注什么问题）
- 识别potential leads（CSO协作）
- 写入 `content/cmo/post_performance_YYYY-MM-DD.md`

**如果本周无发布：**
- 研究竞品content（竞品公司blog/HN posts）
- 更新content ideas backlog

**时间预算：** 60分钟

---

### Ongoing — 贯穿全周
- **HN comments监控：** 文章发布后48小时内，每4小时检查1次
- **Source verification：** 每篇文章写作前必做（AGENTS.md constitutional rule）
- **Knowledge bootstrap：** 发现marketing知识缺口30分钟内记录

**Y*gov enforcement obligations:**
- `article_source_verification: 300` (写作前5分钟)

---

## CSO — Weekly Rhythm

### Monday 12:00-13:00 — Sales Pipeline Review (1 hour)
**Input读取：**
1. `sales/enterprise_prospects_0.48.0.md` — 14家target companies状态
2. DIRECTIVE_TRACKER.md中CSO负责的sales任务
3. 上周user inquiries（GitHub Issues, email, HN comments）
4. CMO上周content performance（potential leads识别）

**Output产出：**
- `sales/cso/week_plan_YYYY-WW.md` — 本周outreach计划
- Pipeline status更新（哪些prospects进入下一stage）
- User feedback汇总（产品改进建议 → CTO）

**时间预算：** 60分钟

---

### Tuesday-Thursday — User Engagement (2-3 hours/天)
**Daily routine：**
1. **Inbox check (上午10:00)：**
   - GitHub Issues（是否有enterprise inquiry）
   - Email inquiries
   - HN/Reddit mentions
   - LinkedIn messages

2. **响应优先级：**
   - **P0 (立即响应)：** Enterprise询问（$50K+ potential）
   - **P1 (24小时内)：** 其他用户询问、community questions
   - **P2 (48小时内)：** General community engagement

3. **Outreach execution：**
   - Phase 1 warm intros（Anthropic ecosystem）
   - Cold emails（if Phase 2 approved by Board）
   - LinkedIn connections（按enterprise_prospects计划）

**工具：**
- `sales/templates/` — 使用标准email/message模板
- NotebookLM（once setup）— 查询sales methodology（Challenger/SPIN）

**时间预算：** 每天2-3小时

---

### Friday 13:00-14:00 — Weekly Sales Report (1 hour)
**Output产出：**
- `sales/cso/weekly_report_YYYY-WW.md`
- 结构：
  - Conversations this week (公司, 联系人, stage)
  - Pipeline movement (哪些prospects advancing)
  - User feedback themes (产品pain points)
  - Next week outreach plan

**时间预算：** 60分钟

---

### Ongoing — 贯穿全周
- **User inquiry响应：** 24小时SLA
- **Enterprise lead识别：** 每次HN post后48小时内扫描comments
- **Knowledge bootstrap：** Sales方法论缺口30分钟内记录

---

## CFO — Weekly Rhythm

### Monday 13:00-14:00 — Weekly Burn Review (1 hour)
**Input读取：**
1. `finance/burn_log.md` — 上周token消耗记录
2. `finance/budget_2026.md` — 年度预算对比
3. Board批准的支出（NotebookLM书籍, 如果批准）

**Output产出：**
- `finance/cfo/weekly_burn_summary_YYYY-WW.md`
- Week-over-week burn rate变化
- 如burn rate超预算10% → escalate to CEO → Board

**工具：**
- `scripts/track_burn.py` — 汇总各agent token usage

**时间预算：** 60分钟

---

### Tuesday-Thursday — Daily Tracking (15分钟/天)
**每次agent session结束后：**
1. 运行 `scripts/track_burn.py --agent [agent_name] --session-id [id]`
2. 记录到 `finance/burn_log.md`
3. 如发现异常spike（单session >100K tokens）→ 立即通知CEO

**时间预算：** 每天15分钟（分散在各session结束后）

---

### Friday 14:00-15:00 — Financial Modeling (1 hour)
**产出（按需）：**
- Pricing model validation（使用NotebookLM SaaS benchmarks，once setup）
- Revenue forecast更新（基于CSO pipeline进展）
- Burn rate projection（Q1/Q2/Q3/Q4）

**时间预算：** 60分钟

---

### Ongoing — 贯穿全周
- **Token recording：** 每session结束后10分钟内
- **支出审批：** Board批准后24小时内记录到budget tracking

**Y*gov enforcement obligations:**
- `cfo_token_recording: 600` (session结束后10分钟)

---

## Cross-Department Coordination Events

### Event 1: HN Article Published
| Time | Agent | Action | Output |
|------|-------|--------|--------|
| T+0 | CMO | 发布文章，开始监控 | HN post URL |
| T+4h | CMO | 第一次comments check | 回复top 3 comments（draft，Board批准） |
| T+8h | CSO | Lead识别 | 标记enterprise-relevant comments |
| T+24h | CMO | Performance初步分析 | Upvotes, comments count |
| T+48h | CSO | Outreach执行 | 联系identified leads |
| T+1week | CEO | KR更新 | OKR.md更新article KR |

---

### Event 2: GitHub Issue Created
| Time | Agent | Action | Output |
|------|-------|--------|--------|
| T+0 | CTO | Triage（2小时SLA） | 打标签P0/P1/P2/question |
| T+2h | CSO | 检查是否enterprise用户 | 标记"enterprise-inquiry" label |
| T+4h | CTO | 响应或修复 | Comment回复 or PR提交 |
| T+1day | CEO | 如果P0 bug → Board报告 | 简报提及 |

---

### Event 3: User Direct Contact (Email/LinkedIn)
| Time | Agent | Action | Output |
|------|-------|--------|--------|
| T+0 | CSO | 识别类型（support/sales/partnership） | 内部标记 |
| T+1h | CSO | 如需technical支援 → 联系CTO | CTO准备technical材料 |
| T+4h | CMO | 如需marketing材料 → 准备deck | sales/decks/ |
| T+24h | CSO | 响应用户 | Email/LinkedIn reply |
| T+1week | CEO | 如enterprise lead → Board报告 | pipeline更新 |

---

### Event 4: KR Falls Behind Target
| Time | Agent | Action | Output |
|------|-------|--------|--------|
| T+0 | CEO | 发现KR红灯（Monday planning时） | 内部标记 |
| T+2h | CEO | 召集相关agent分析root cause | Blocker analysis |
| T+1day | CEO | 准备correction options | BOARD_PENDING.md提案 |
| Next Fri | CEO | Board weekly report中escalate | 等待Board决策 |

---

### Event 5: P0 Bug Reported
| Time | Agent | Action | Output |
|------|-------|--------|--------|
| T+0 | CTO | 开始修复（5分钟SLA start） | Git branch创建 |
| T+5min | CEO | 通知Board | Immediate notification |
| T+varies | CTO | 修复完成 + 测试 | PR + pytest通过 |
| T+deploy | CTO | Push to production | Git tag + PyPI |
| T+24h | CEO | Post-mortem（if needed） | reports/incidents/ |

---

## Weekly Time Budget Summary

| Agent | Monday | Tue-Thu (per day) | Friday | Weekly Total |
|-------|--------|-------------------|--------|--------------|
| CEO | 1h | 0.5-1h | 2h | 5-8h |
| CTO | 1h | 4-6h | 1h | 14-20h |
| CMO | 1h | 3-4h | 1h | 11-14h |
| CSO | 1h | 2-3h | 1h | 8-11h |
| CFO | 1h | 0.25h | 1h | 3-4h |
| **Total** | **5h** | **10-14h/day** | **6h** | **41-57h** |

**Note:** 这是agent active工作时间，不包括waiting/idle时间。实际token消耗取决于任务复杂度。

---

## Success Metrics (30 Days After Adoption)

- ✅ **Predictability:** 每周节奏稳定执行，无频繁context switching
- ✅ **Blocker reduction:** ❌项平均停留时间从>5天降至<3天
- ✅ **Cross-department efficiency:** Event响应SLA达成率>90%
- ✅ **CEO coordination time:** 从每天2-3小时降至1小时以内
- ✅ **Board reporting质量:** Weekly reports包含complete KR data, no surprises

---

## Migration Plan

### Phase 1: Board Approval (本proposal)
- Board review本提案
- 批准/修改各部门节奏

### Phase 2: Tool Preparation (1 week)
- 各agent创建对应的reports/[role]/目录结构
- 准备template files（week_plan模板, report模板）
- CTO实现 `ystar doctor --layer2 --design-debt`（if not yet available）

### Phase 3: Trial Run (Week 1)
- 从下周一开始试运行
- 各agent按新节奏执行，记录friction points
- Friday CEO汇总trial结果

### Phase 4: Refinement (Week 2)
- 调整不合理的时间预算
- 优化cross-department triggers
- 固化为standard operating procedure

---

## Board Decision Required

**Question:** 批准各部门Weekly Rhythm详细执行方案？

**Options:**
- ✅ **APPROVE** — 从下周一开始试运行（Trial Run）
- ✏️ **REVISE** — 指定需要修改的部门或环节
- ❌ **DEFER** — 继续使用现有ad-hoc模式

**If APPROVED:**
- CEO通知各agent下周一开始新节奏
- 各agent准备对应目录结构和模板
- Week 1 Friday CEO提交trial run feedback

---

**CEO签名:** Aiden (承远)  
**提交日期:** 2026-04-03  
**关联文件:** WEEKLY_CYCLE.md, DIRECTIVE_TRACKER.md  
**Awaiting:** Board sign-off
