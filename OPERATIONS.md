# Y* Bridge Labs — Operations Plan
# CEO整合自Board Directive #002-#018及所有后续指令
# 时间锚点：2026-03-28 23:33 ET
# 状态：运营中

---

## 时间线回顾

| 日期 | 关键事件 |
|------|---------|
| 03-26 | 公司成立，AGENTS.md v1→v2，EXP-001实验，5个agent启动，第一批bug修复 |
| 03-27 | SLA从人类速度改为agent速度，CFO成本追踪建立，CASE-002发现，文章系列启动 |
| 03-28 | 深度研究报告，K9 Scout部署（第一个外部用户），专利起草，基线修复，23/23验证通过 |

---

## 一、每日循例工作（Daily Recurring）

### CEO — 每个session必须执行
| 时间 | 任务 | 输出文件 |
|------|------|---------|
| Session开始 | 读OKR→DISPATCH→BOARD_PENDING→昨日报告 | 无 |
| Session结束 | 写中文今日简报 | BOARD_PENDING.md顶部 |
| Session结束 | 写英文日报 | reports/daily/YYYY-MM-DD.md |
| Session结束 | 更新BOARD_PENDING | BOARD_PENDING.md |

### CTO — 每日
| 任务 | 频率 | 说明 |
|------|------|------|
| GitHub Issue分类 | 收到后15分钟内 | AGENTS.md SLA |
| P0 bug修复 | 发现后5分钟内 | AGENTS.md SLA |
| 测试套件 | 每次代码变更后 | 158+测试必须全过 |

### CMO — 每日
| 任务 | 频率 | 说明 |
|------|------|------|
| HN文章写作推进 | 每天 | 按article_series_plan_v2执行 |
| HN评论监控 | 文章发布后48小时 | 汇总有价值评论 |

### CSO — 每日
| 任务 | 频率 | 说明 |
|------|------|------|
| 用户对话记录 | 每次对话后24小时内 | sales/feedback/ |
| GitHub star/issue追踪 | 每日 | 汇报KR1进度 |

### CFO — 每日
| 任务 | 频率 | 说明 |
|------|------|------|
| Token用量记录 | 每次session后10分钟内 | scripts/track_burn.py（HARD义务） |
| 每日burn rate | 每天 | finance/daily_burn.md |

### K9 Scout（Mac）— 每日
| 任务 | 频率 | 说明 |
|------|------|------|
| HN AI governance搜索 | 每天 | 通过scripts/k9.py派发 |
| Reddit AI agent搜索 | 每天 | 通过scripts/k9.py派发 |
| Y-star-gov GitHub stats | 每天 | stars/forks/issues |
| 竞品动态（Proofpoint/Microsoft） | 每天 | 新发布/新功能 |
| CIEU数据积累 | 持续 | 每个操作自动记录 |

---

## 二、优先级工作队列（Priority Queue）

### P0 — 阻塞一切

| # | 任务 | 负责人 | 状态 | 阻塞 |
|---|------|--------|------|------|
| 1 | Show HN发布 | CMO+Board | 等待Board最终发布指令 | KR1, KR2, KR3 |

### P1 — 本周必须完成

| # | 任务 | 负责人 | 状态 | KR |
|---|------|--------|------|-----|
| 2 | Series 3精修（合约合法性） | CMO | draft完成，待Board选标题 | KR2 |
| 3 | Series 5精修（AST白名单） | CMO | draft完成，CTO审核9/10 | KR2 |
| 4 | K9 Scout Phase 4验证（高级功能） | CTO via K9 | Phase 1-3完成23/23 | KR3 |
| 5 | LinkedIn公司页策略 | CMO | 未开始 | KR5 |
| 6 | API surface精简方案 | CTO | 未开始 | KR3 |

### P2 — 本月完成

| # | 任务 | 负责人 | 状态 | KR |
|---|------|--------|------|-----|
| 7 | 专利终审+提交USPTO | CSO+Board | draft完成，13 claims | 防御性IP |
| 8 | 产品拆分方案（独立小工具） | CTO | 未开始 | KR1 |
| 9 | ObligationTrigger生产部署 | CTO | 代码完成，未部署 | KR3 |
| 10 | Metalearning技术文档（已完成546行） | CTO | 已完成 | 融资叙事 |
| 11 | 文章Series 6-10 | CMO | 按plan_v2排期 | KR2 |

---

## 三、一次性工作（One-Time, 已完成）

| # | 工作 | 完成日期 | 交付物 |
|---|------|---------|--------|
| 1 | AGENTS.md v2.2.0宪法 | 03-28 | AGENTS.md |
| 2 | OKR.md Q2目标 | 03-28 | OKR.md |
| 3 | 运营节律系统 | 03-28 | WEEKLY_CYCLE.md |
| 4 | 竞争定位文档 | 03-28 | knowledge/cto/competitive_architecture.md |
| 5 | 深度研究报告 | 03-28 | reports/ystar_gov_deep_research_report.md |
| 6 | 20篇文章系列规划v2 | 03-28 | content/article_series_plan_v2.md |
| 7 | 真实事件清单 | 03-28 | content/real_events_inventory.md |
| 8 | 知识库15个文档 | 03-27 | knowledge/各部门/ |
| 9 | 自举协议 | 03-27 | AGENTS.md Self-Bootstrap Protocol |
| 10 | 5个hero brief | 03-27 | reports/team_heroes/ |
| 11 | K9 Scout部署 | 03-28 | scripts/k9.py + Mac验证23/23 |
| 12 | CASE-003发现+修复 | 03-28 | knowledge/cases/CASE_003 + GitHub Issue #3 |
| 13 | 专利草稿 | 03-28 | reports/patent_ystar_t_provisional_draft.md |
| 14 | EXP-001可重现代码 | 03-28 | reports/EXP_001_reproducible_code.md |
| 15 | ObligationTrigger框架 | 03-28 | Y-star-gov代码 + 158测试 |
| 16 | 安装流程修复 | 03-28 | hooks.json + examples/AGENTS.md + doctor |
| 17 | 基线评估修复 | 03-28 | _cli.py baseline fix, 7/7 doctor |
| 18 | anthropics/skills PR | 03-28 | PR #792 |
| 19 | GitHub Discussions帖 | 03-28 | Discussion #793 |

---

## 四、Board待决事项（当前6项）

详见BOARD_PENDING.md。最关键的一项：
**Show HN发布时间** — 所有KR都是0，这是解锁一切的开关。

---

## 五、周节律（WEEKLY_CYCLE.md，待Board批准）

- 周一：计划+周报
- 周二-周四：执行
- 周五：总结+Board汇报

---

## 六、KR仪表盘

| KR | 目标 | 当前 | 最大障碍 |
|----|------|------|---------|
| KR1 | 200 GitHub stars | 2 | Show HN没发 |
| KR2 | 10 HN文章 avg>50 | 0发布/5 draft | Show HN没发 |
| KR3 | 3真实用户 | 1（K9 Scout） | 需要更多外部用户 |
| KR4 | 1企业对话 | 0 | 没有外部接触 |
| KR5 | LinkedIn | 0 | 页面没建 |
