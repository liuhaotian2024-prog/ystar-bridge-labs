---
name: Sub-agent 派单必须任务原子化（单次 dispatch 单一 deliverable）
type: lesson / methodology
created: 2026-04-13
severity: medium-high
trigger_session: 2026-04-12 夜 CEO autonomous session
cieu_evidence: Ryan-Platform 被派 4 次同 session，每次半活
lesson_id: 1eea8b02-af54-4a09-b1be-cf7454d837bf
---

# 规则
CEO / CTO 派 sub-agent 时，**每次 Agent 调用必须有且仅有一个 deliverable + 一个 commit 目标**。任务打包（一次塞 2+ 活）会导致 sub-agent 在 ~40-50 tool_use 预算内耗尽 context，停在测试或 commit 前的最后一步。

# Why — 实证 (2026-04-12 夜)

今晚派 Ryan-Platform 4 次，每次都停在"测试即将绿"或"即将 commit"的最后一步：

| # | 任务 | tool_uses | 停在哪 |
|---|---|---|---|
| 1 | 秘书 Step 1/2/5 实装 | 40 | 成功 ship（单活）✅ |
| 2 | CEO 双模式 + parallel rule | 47 | "add rule to session config" 前 |
| 3 | 续双模式 + secretary 3-13 + parallel rule | 42 | "session start protocol blocking tests" |
| 4 | ship + 修 session_start + parallel rule | 40 | "run full suite" 前 |

**对比**：单活交付（Ryan 1 + Maya Continuity Guardian v2）均 100% ship。多活打包全部半活。

根因：
- Claude sub-agent 单次调用的 tool_use 预算约 40-50 次
- 我每次塞 2-3 活，单活 ~15-20 tool calls（探索 + 写 + 测试 + 调试 + commit），2 活就 40+，3 活必溢出
- 溢出时 sub-agent 优雅退出，但 work-in-progress **没 commit**，下次派任务要**重新发现工作**再续

反事实：如果 Ryan 第 2 次只派"CEO 双模式"一个活（不塞 parallel rule）：
- 20 tool_uses 做完核心实装
- 10 tool_uses 跑测试
- 5 tool_uses commit + 报告
- ~35 tool_uses 留出余量 → **100% ship**

然后再派一次"parallel rule"也一样能 ship。**两次小派 ≪ 一次大派失败**。

# How to apply

### 硬规则（拟立 `atomic_task_per_dispatch`）
每个 Agent 调用 prompt 必须满足：
1. **单一 deliverable**：1 代码文件 / 1 report / 1 feature，不混合
2. **单一 commit 目标**：完成即 commit，commit message 写在 prompt 里
3. **工期预算 ≤ 30 tool_uses**（保留 ~10 tool_uses 给测试 + commit + 报告）
4. **明确的"完成" / "卡住" 二态判断**，不要让 sub-agent 在"还差一点"状态下耗尽

### 反模式（不要这样派）
```
❌ "Ryan，干三件事：
    活 A: 续完 X
    活 B: 实装 Y
    活 C: 补 Z 硬约束"
```

### 正模式（这样派）
```
✅ "Ryan，单活：续完 X
    - 具体 deliverable: scripts/X.py 跑通 + tests/test_X.py 绿
    - commit: 'feat: X implementation'
    - 卡住立即 ping CEO 不要继续"

[完成后下一轮消息再派 Y，再下轮再派 Z]
```

### 批量派单情况
当有多个独立任务**给不同 engineers**（如 Leo + Maya + Jordan），用 `parallel_dispatch_required` 硬约束批量发——每个 engineer 仍然遵守原子化（单活），但多个 engineer 并行。这是**水平并行 + 每个人串行原子**的组合。

# 集成点

- **`parallel_dispatch_required`**（Ryan 实装中）：横向并行 3 个 engineer 一起跑
- **`atomic_task_per_dispatch`**（本 lesson → 待立硬约束）：纵向每次派单原子化
- 两者正交：**前者拉开并行度，后者收窄任务粒度**，联合效果 = 高吞吐 + 高交付率

# 验证指标

实装 `atomic_task_per_dispatch` 后，每次 sub-agent 任务应满足：
- ≥ 90% 任务在 tool_use ≤ 35 时 ship（commit + 报告 filed）
- 任务半活率（tool_use 耗尽但未 commit）≤ 10%
- 今晚基线：Ryan 半活率 75%（4 次 3 半活），目标降至 ≤ 10%
