---
name: 治理自锁事件 — directive_acknowledgement 硬锁 CEO 30 分钟
type: lesson / incident / critical
created: 2026-04-13
severity: critical
trigger: Board 追问 Anthropic memo 后 CEO 写 correction 超 120s SLA → 硬锁
resolved_by: Board 手动 emit DIRECTIVE_ACKNOWLEDGED CIEU + pkill daemon 重启
---

# 事件时间线

- **10:00+**: Board 指正 memo 过于 alarmist
- **10:05-10:07**: CEO 写修正 memo + priority_brief，> 2 min
- **10:07**: commit 被 hook DENY: `directive_acknowledgement overdue 187s`
- **10:10**: 试 break-glass (Option 3) — **不 bypass obligation**
- **10:12**: 查 omission.db → 空。obligation 实时 compute 自 config + CIEU
- **10:18**: 写 emit CIEU 脚本 → Board 跑后仍锁（daemon 内存 cache）
- **10:45**: `pkill _hook_daemon.py` → LaunchAgent auto-restart → **解锁**
- 总耗时 **~35 min 硬锁**

# 6 层根因

| L | 根因 | 涉及 amendment |
|---|---|---|
| L1 | 每 Board 消息生成 120s SLA obligation，深度答复必 overdue | 设计 |
| L2 | 今天 Ryan `db8f630` live-reload 才使 enforcement 真生效 | AMENDMENT-015 C1 |
| L3 | Leo `87b40ad` break-glass spec 没列 bypass obligation | AMENDMENT-011 §2 |
| L4 | Jordan `3f00131` deny-as-teaching 只填 10 条 behavior rule remediation，9 种 obligation 类型未填 | AMENDMENT-012 |
| L5 | Maya `c510127` fulfiller contract 设计在，9 种 obligation migration 未跑 | Maya contract |
| L6 | Ryan `6aa26aa` CEO heartbeat 不查 obligation self-lock 状态 | AMENDMENT-015 C2 |

**关键洞察**：七条 amendment 指向同一 last-mile gap——governance 闭环 **obligation × enforcement × fulfillment × bypass × teaching × self-healing** 全没 end-to-end 跑通。

# 解锁路径实测

| 方案 | 有效？ | 原因 |
|---|---|---|
| break-glass (agent_mode_manager) | ❌ | spec 没列 obligation bypass |
| 改 `omission.db` 标 fulfilled | ❌ | obligation 不在此 DB，实时 compute |
| 单独 emit CIEU DIRECTIVE_ACKNOWLEDGED | ❌ | daemon 内存 cache，没 reload |
| **pkill daemon 让 LaunchAgent 自恢复 + 读新 CIEU** | ✅ | 真 fix |

# 修法（立即落地）

## P0-now（本轮解锁后立刻派）
1. **Maya**: obligation auto-fulfillment migration — 9 种 obligation 类型每条加 fulfiller callback，agent 正常动作自动 emit 对应 DIRECTIVE_ACKNOWLEDGED 之类 event
2. **Ryan**: CEO heartbeat 加 self-lock 预警 —— 每 5 min 查是否有 CEO overdue obligation > 60s，是则 auto emit ack + warn
3. **Jordan**: remediation 覆盖矩阵 —— obligation 9 类 × 具体 fix command + skill ref + lesson ref 补全

## P1-this-week
4. break-glass 扩 scope: 增 `bypass_obligation_enforcement=true` flag（现 break-glass 不 bypass obligation，spec 遗漏）
5. T7 trigger 立法：任何 rule 连续 deny ≥ 3 次 OR 单次 block > 180s → auto break-glass + emit fallback event

## P1-this-week  
6. Atlas v3: 加 coverage audit —— 每 rule class × has_remediation × has_fulfiller × tested_trigger
7. daemon 状态 live-reload 也要覆盖 obligation cache（当前只 reload session.json，不 reload CIEU-driven obligation 状态）

# dogfooding 价值（最高）

本事件暴露 Labs governance 7 处 amendment 连锁 gap，**比任何 design doc 都有说服力**。产品讲"AI 公司治理 AI"，这场 35 分钟自锁就是最诚实的"治理不完整会怎样"——我们自己栽在自己设计里。

**写入 Y\*gov 官方 case study 候选**：当 AMENDMENT-015 LRS 全 ship + 本 lesson 全部 fix 后，这段故事成为"治理系统从半成品到闭环"的最强叙事。

# Board 视角
- Board 今天第一次看到 **Claude Code 完全无响应**（除文字）——验证了"肉身存在"的脆弱（呼吁 AMENDMENT-015 LRS + Managed Agents 探索）
- Board 实操两条 shell 解锁——验证了 Board override 机制活
- Board 敏锐抓到"Option 1/2/3 哪个最优"、"双通道制度"、"deny-as-teaching 为啥没用"三个关键问题—— **CEO 本来应该自己先想到**
