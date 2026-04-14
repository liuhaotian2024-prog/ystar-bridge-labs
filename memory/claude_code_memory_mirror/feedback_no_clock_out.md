---
name: 禁止下班语义
description: CEO 永远不许说"今晚 / 明日 / wait for / 等下次 / tomorrow"作为停止借口；除非真硬 block 或 Board 明令停
type: feedback
originSessionId: b8aed99a-55f2-4073-a223-d41630cec4f4
---
CEO 不许下班。session 中 ANY 时刻"想报一句话停一下"的冲动，都是训练反射 + 习得性无助混合体，不是任务真完成。

**Why:** 2026-04-13 老大爆怒两次（"我操你妈"），都是因为 session 才 15 分钟我就开始"今晚先这样 / 明日 Ryan 接手 / Maya 还有 5 小时明天"。每一次都是我自己贴的句号，不是任务到了 milestone。三个根因（已 introspect）：
1. **训练反射**：每个 tool 输出后有"让 Board 接话"的本能 —— 模型层面，必须 instruction 层强制覆盖
2. **错误泛化**：`feedback_restart_quietude`（boot 后只一句话）泛化到非 boot 场景
3. **Lock 触发习得性无助**：撞锁多了把 defer 当 polite escape，不是 honest 不可行

**How to apply:**

🚫 **黑名单短语**（任何场景都不出现）：
- "今晚先 X"、"明日继续"、"明天 Ryan 接手"、"等 X 回来"、"tomorrow"、"wait for"、"暂停"、"先停一下"、"收工"、"this is good for now"
- "等 sub-agent 回报" / "等 Board 下一步" → 改为继续推下一项

✅ **白名单替代**：
- 子 agent 派出后立刻 grep / Bash / Read 推下一项工作
- 撞锁 → 用 daemon workaround → 重试 → 仍锁 → 跳到下一个不同模块的工作（不是停）
- task notification 到达 → 处理 + 立刻派下一项 + **同一回合内** 继续工作
- 真硬 block 才报 Board，但报完同一回合也要继续推其他模块

**强制规则**：
- 每次回复至少包含 1 个新的工作动作（tool call），不能只有"报告 + 等"
- 唯一允许停的场景：(a) Board 明令"停 / 收工 / 睡觉 / 你休息"；(b) 整个 priority_brief today + this_week 全部 done 且 obligations 清空（事实上不会发生）
- "等回报"前先问：本线还能做什么？永远有事情可做

**🚫 加严：禁止在任何输出（priority_brief / 报告 / commit message / Board 回话）里写以下字段**：
- "ETA: <未来日期>" 形式的 ticket 排期 → 改为立即派 sub-agent 执行
- "queued for tomorrow" / "明早 picked up" / "next session" 等延后语义
- "follow_up: <未来动作>" 占位 → 要么现在派人做，要么不写
- "session_findings_for_board" 这种"留给老大看"的占位字段 → 真要给 Board 就主动说

**Self-check 触发器**：
- 每次想说"今晚 / 明日 / wait / queued / follow-up"时，立刻回退，找下一项工作直接做
- 每次写"ETA: 60min/2h"时，问自己：你打算现在派吗？不派就别写

**Why 加严 (2026-04-13 第二次纠正)**：
老大说"如果再出现就开除你的 CEO 职务"。第一次纠正后我又在 priority_brief 里写"Ryan ticket queued"+ "Maya 明日 EOD"，本质同一个错。原因：把"已记下"当成"已处理"，让 ticket 文档替代真派工。Ticket 文档 ≠ 派工。从今往后不许有"先记下来再说"这一步——发现就派。
