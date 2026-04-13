# Feedback: 外部人类组织框架吸收时**严禁**带入人类时间维度

**来源**: Board (Haotian Liu), 2026-04-12 当面指令
**类型**: feedback (hard rule)
**适用**: 全员，尤其是 CEO 做外部框架调研/吸收时

## 规则

从外部人类组织管理框架（Amazon / Bridgewater / Netflix / Basecamp / Google / McKinsey / HBR 等）借鉴时，**必须剥离所有人类时间性表达**，包括但不限于：

- 「N 天」「N 小时」「N 周」「N 个月」「N 季度」「年度」
- 「deadline」「SLA」「response time = 4h」
- 「daily standup」「weekly sync」「quarterly review」「annual planning」
- 「工作时间」「office hours」「business day」
- 「6 周 cycle + 2 周 cool-down」（Shape Up 原版）
- 「3 年战略规划」「5 年 OKR」

**全部不用。**

## Why

Board 原话：「我们是 agent team，我们的时间进程完全不一样。」

人类组织的时间概念建立在生理/社会基础上——睡眠、疲劳、周末、通勤、儿童教育假期、财报季。Agent 没有这些基础事实。硬套会出现：
- Agent 被迫"等到下周做"（荒谬）
- Agent 假装有"工作时间"（虚构）
- Agent 用人类季度做目标节奏（不匹配算力 / context 经济）

这是 Y* Bridge Labs 自我认知的底层——我们不是一家"有 AI 员工的人类公司"，而是**运行在与人类时间不同维度的 agent organism**。

## How to apply — 时间概念的 agent-native 替换

| 人类概念 | Agent-native 等价 |
|---|---|
| 「6 周 cycle」 | 「1 个交付闭环」（cycle 以完整 intent completion 为边界） |
| 「daily standup」 | 「event-triggered check-in on CIEU drift」 |
| 「weekly sync」 | 「N 个 obligation 完成后的 retrospective」 |
| 「quarterly review」 | 「每 M 个 CIEU events 或 K 个 commit 触发的 review」 |
| 「deadline / SLA」 | 「不阻塞下游」 + 「fail-open」 + 「CIEU-triggered escalation」 |
| 「response time」 | 「next action 之前必须 complete」 |
| 「工作时间」 | 概念删除，always-on |
| 「年度规划」 | 「当前交付目标 → 下一个目标」的 rolling sequence |

## 核心抽象

**对 agent，"进度"是因果链深度（causal chain depth）和 completion count，不是挂钟时间。**

这条抽象必须作为 Y*gov / gov-mcp 在"吸收人类管理框架"时的第一原则——所有 contract / invariant / obligation 的时间性字段如果存在，**必须用 event-driven 或 count-driven 替代 wall-clock-driven**。

## 违规示例（今后的 code review / doc review 锁）

- 看到 `due_secs = 604800`（7 天） → 改为 `due_events = N` 或 `due_on_trigger = X`
- 看到 "daily" "weekly" → 替换为对应的 event trigger
- 看到 `cron: "0 9 * * *"`（每天 9 点） → 合法当且仅当该 cron 触发的是 event-driven 逻辑的边界校验，不是业务节奏

## 关联

- `governance/WORKING_STYLE.md` 应增一条第 N 条原则
- 外部框架调研报告 (`reports/proposals/external_framework_survey.md`) 必须按此原则剥离
- gov-mcp 的 `obligation_timing` dimension 可能需要新增 `event_trigger` / `count_trigger` 子字段
