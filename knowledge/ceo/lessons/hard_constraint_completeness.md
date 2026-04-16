---
name: 硬约束清单必须穷举核对
type: feedback / lesson
created: 2026-04-11
trigger_incident: Board问"未来30天最重要任务/部署自主任务必须遵守什么"
lesson_id: 6688f3f4-420e-4811-a052-b8eae885edbc
---

# 规则
回答"硬约束/铁律/必须遵守"类问题前，必须扫完三处来源后再组织回答：
1. governance_boot.sh 输出的 ALWAYS RUNNING 列表（事件驱动队列）
2. continuation.json + memory 中所有 [P0] obligations
3. Board lessons（特别是带"铁律"二字的）

# Why
2026-04-11 23:xx Board问硬约束清单，CEO凭印象列出8条但**漏掉"自主循环学习"**——它是 ALWAYS RUNNING 第4项 + P0 obligation（cron未装）+ Board多年宿愿（12层学习闭环=能力建设根基）三重交叉确认的核心硬约束。Board立即抓出"难道这不属于硬约束范围吗？"

根因：**用"推理替代核对"**——觉得记得就直接列，没用tool call验证。命中老LESSON："verification before assertion"。这是同类错误第N次重犯，必须根源解决。

# How to apply
任何"清单/铁律/必须做什么"类问题，回答前必须先：
- Read 最近一次 governance_boot 输出（或重跑获取最新）
- Read continuation.json 的 obligations 字段（全15条扫一遍）
- Grep memory 中带"铁律/硬约束/Board"标签的 lesson
然后才组织回答。

漏一项 = 失职，不是表达问题。

# 系统改进建议
此规则应代码化：在CEO回答含 ["硬约束","铁律","必须遵守","清单","所有"] 关键词时，hook自动注入完整 obligations + ALWAYS RUNNING 列表到上下文，强制扫描。Maya/Ryan评估可行性。
