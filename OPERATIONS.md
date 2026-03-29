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
| 知识缺口自举 | 发现后30分钟 | Directive #013 | knowledge/[role]/ + bootstrap_log.md |
| 案例记录（如有失败） | 失败后1小时 | AGENTS.md Case Protocol | knowledge/cases/CASE_XXX.md |
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

### K9 Scout（Mac）— 每日
| 任务 | 频率 | 来源 | 触发方式 |
|------|------|------|---------|
| HN搜索"AI agent governance" | 每天 | Directive #018-020 | scripts/k9.py |
| Reddit搜索"AI agent"痛点 | 每天 | Directive #018-020 | scripts/k9.py |
| Y-star-gov GitHub stats | 每天 | KR1追踪 | scripts/k9.py |
| Proofpoint/Microsoft动态 | 每天 | 竞争监控 | scripts/k9.py |
| CIEU数据积累 | 持续 | 所有操作自动 | Y*gov自动 |

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
