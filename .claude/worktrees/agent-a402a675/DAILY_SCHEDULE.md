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
