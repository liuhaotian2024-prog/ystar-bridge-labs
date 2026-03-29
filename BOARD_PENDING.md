# Board Pending — Items Awaiting Board Decision

*Updated by CEO at end of each session. Board reviews and decides.*
*Last updated: 2026-03-28*

---

## 今日简报 2026-03-28

✅ 今天完成了：
- 建立了公司运营宪法框架（OKR、周节律、Board汇报机制），公司从"等指令"变成"自主运转"
- 写完了竞争定位核心文档：Y*gov是唯一执法路径里不含AI模型的治理系统，竞争对手Proofpoint用AI判AI，可被注入攻击
- 修复了Windows安装问题（hook脚本用了Windows不认识的命令），新用户现在能正常安装了
- 添加了示例配置文件，新用户可以直接复制使用，不用从零开始写
- 写完了metalearning完整技术文档（546行），为未来融资叙事和文章系列准备素材
- 专利修改完成：核心Claim保护范围扩大了（从具体技术改为通用描述），新增Claim 13覆盖所有类型的自主系统
- 完成了Y*gov深度研究报告：发现代码库里有8000多行已实现但用户完全不知道的功能
- HN文章Series 5初稿完成（如何安全执行用户表达式），技术审核9/10分
- 文章系列20篇总规划获批，可以开始批量生产

⏳ 正在进行中：
- Series 3文章（合约合法性问题）等待董事长选标题和最终确认
- Show HN帖子等待最终发布指令
- LinkedIn公司页策略CMO还没提交方案

❓ 需要董事长决定：
- Series 3标题选哪个？三个候选在draft文件里
- Show HN是否现在发？安装流程已修复，CTO确认可用
- 专利终审：13条Claims是否满意？满意后可以交律师审核
- Series 5标题选哪个？（"唯一安全执行用户表达式的方法"等三个候选）

📊 KR进度：
- KR1 GitHub stars: 0/200（Show HN还没发）
- KR2 HN文章发布: 0/10篇（5篇draft就绪，0篇发布）
- KR3 真实用户: 0/3（安装流程刚修好）
- KR4 企业对话: 0/1（还没开始外部接触）
- KR5 LinkedIn关注者: 0/500（页面还没建）

⚠️ 风险提示：
- 所有KR都还是0，Q2已经开始。Show HN发布是解锁一切的关键动作，建议尽快决定发布时间。
- 专利如果拖太久，竞争对手可能先申请类似Claims。Proofpoint 3月17日刚发了自己的框架。

---

## Awaiting Approval

### 1. Series 3 Article — Contract Validity
- **File:** content/articles/004_contract_validity_HN_draft.md
- **Status:** Draft complete, needs Board review and title selection
- **Title options:** Board to choose
- **Blocking:** KR2 (HN articles)
- **Added:** 2026-03-28

### 2. ~~Article Series Plan v2~~ — APPROVED (2026-03-28)
- **Decision:** Approved with adjustments: Series 16 merged into 10, Series 9 confirmed at position 9
- **Action:** CMO to propose replacement for Series 16 slot
- **No longer blocking:** Series 5 production can begin

### 3. Show HN Post
- **File:** sales/first_user_plan.md
- **Status:** Draft approved with revisions (applied). CTO clean install confirmed.
- **Blocking:** KR1 (stars), KR3 (users)
- **Decision needed:** Final go to post
- **Added:** 2026-03-26

### 4. ObligationTrigger Implementation — Deploy to Production
- **File:** reports/proposal_obligation_triggers.md
- **Status:** Framework approved, code implemented (158 tests passing), not yet deployed
- **Decision needed:** Approve deployment timeline (enable triggers one at a time)
- **Blocking:** Product completeness for KR3
- **Added:** 2026-03-28

### 5. Product Split Proposals (Pending — CTO to submit)
- **Status:** CTO tasked with scanning codebase for standalone tools
- **Decision needed:** Approve individual tool proposals when submitted
- **Blocking:** KR1 (more entry points for users)
- **Added:** 2026-03-28

### 6. LinkedIn Company Page
- **Status:** CMO to research and propose strategy
- **Decision needed:** Approve strategy before CMO creates page
- **Blocking:** KR5
- **Added:** 2026-03-28

---

## Recently Decided

| Date | Item | Decision |
|------|------|----------|
| 2026-03-28 | Priority reorder: P0 install, P1 API surface, P2 metalearning | Approved |
| 2026-03-28 | Competitive architecture positioning (no LLM in enforcement) | Approved — written to knowledge + README |
| 2026-03-28 | Article Series Plan v2.1 | Approved with adjustments (Series 16→10 merge) |
| 2026-03-28 | Article Writing Constitutional Rule | Approved — AGENTS.md v2.2.0 |
| 2026-03-27 | ObligationTrigger framework design | Approved — triggers #1,2,7,9 |
| 2026-03-27 | Agent-speed SLAs | Approved — P0=5min, P1=15min |
| 2026-03-26 | AGENTS.md v2.0.0 | Approved with modifications |
| 2026-03-26 | Show HN draft revisions | Approved |
