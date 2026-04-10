# Multi-Agent Roadmap (Internal)

**Owner**: Board (Haotian Liu)
**Maintained by**: Samantha Lin (Secretary), with weekly audit-progress entry
**Last major update**: 2026-04-10
**Origin**: Board capability system directive, 2026-04-10 Samantha 完整执行指令

This document is the **internal complete version**. The public-facing
summary lives in `README.md` 我们在走向哪里 section and links here.

Every milestone has five blocks: **状态**, **开始/完成日期**, **验收人**,
**验收标准** (具体可验证 checkboxes), **判断标准** (one-sentence capture
of what reaching this state means), **下一里程碑触发条件**.

Secretary updates this file every Monday as part of the weekly audit,
adding a short "Multi-agent Roadmap 进度" entry to `reports/secretary/`
per the obligation registered in CIEU (rule_id:
`gov_cap_roadmap_weekly`, 周期 604800 秒, owner: secretary).

---

## 里程碑一：能力系统地基完成

| 字段 | 内容 |
|---|---|
| 状态 | 进行中 |
| 开始日期 | 2026-04-10 |
| 完成日期 | — |
| 验收人 | Board |

**验收标准**：

- ⬜ `governance/WORKING_STYLE.md` 第九条写完并生效
- ⬜ `knowledge/{role}/` 目录结构六个岗位全部建好
- ⬜ `scripts/local_learn.py` 可用，Gemma 端点已验证
- ⬜ 六个岗位 `knowledge/{role}/role_definition/task_type_map.md` 完成
- ⬜ 每个岗位至少有 3 个任务类型的理论库（`knowledge/{role}/theory/` 下至少 3 个文件）
- ⬜ 反事实模拟跑过至少一轮（每个岗位至少一个 `knowledge/{role}/gaps/YYYY-MM-DD-*.md` 条目）

**判断标准**：每个 agent 在没有指令时知道自己该做什么，而且真的在做。

**下一里程碑触发条件**：六个岗位全部完成 `task_type_map.md` + 每个岗位
至少 3 个理论库文件。

**进度速览（2026-04-10 本次 commit 结束时）**：
- ✅ WORKING_STYLE.md 第九条（commit 本 session）
- ✅ knowledge 目录结构（commit `a49595e`）
- ✅ local_learn.py + Gemma 端点验证（commit `a49595e`，真实 Gemma3:4b 调用 7.2 秒返回 6 条问题）
- ⬜ 六个岗位 task_type_map.md（CTO 将起草，待各岗位修订）
- ⬜ 每岗位 ≥ 3 理论库
- ⬜ 反事实模拟

---

## 里程碑二：单 agent 稳定性验证

| 字段 | 内容 |
|---|---|
| 状态 | 未开始 |
| 开始日期 | — |
| 完成日期 | — |
| 验收人 | Board |

**验收标准**：

- ⬜ Autonomous daily report 连续 14 天无 OVERDUE
- ⬜ 每个工作日每个岗位 CIEU 至少 3 条有意义记录（非 boot-marker）
- ⬜ `knowledge/{role}/` 每 48 小时有真实更新（GOV-009 Change 3 freshness gate 零拦截事故）
- ⬜ 至少完成 5 次完整十二层闭环执行（Level 3 级别的 intent → plan → execute → self_eval → knowledge 回写）
- ⬜ Secretary 周审计 violation 数量呈下降趋势（最近 4 周曲线向下）

**判断标准**：单进程下治理系统**自我维持**，不需要 Board 频繁介入纠偏。

**下一里程碑触发条件**：连续 14 天 autonomous report 无 OVERDUE。

---

## 里程碑三：通信协议建立

| 字段 | 内容 |
|---|---|
| 状态 | 未开始 |
| 开始日期 | — |
| 完成日期 | — |
| 验收人 | Board |

**验收标准**：

- ⬜ 定义 agent 间**标准消息格式**（谁发给谁 / 内容 / 文件路径）
- ⬜ 定义**跨岗位请求协议**（标准化请求格式，不依赖 chat 转发）
- ⬜ 定义**冲突解决路径**（agent 之间分歧时谁有权拍板）
- ⬜ Y\*gov 扩展支持**多进程 CIEU 并发写入不冲突**（SQLite WAL 模式或替代方案）
- ⬜ 两个独立进程完成一次**协作任务测试**（预期：Secretary 审计 CTO 的一次 commit，全过程无 Board 人工介入）

**判断标准**：两个独立进程可以协作完成任务，不需要人介入协调。

**下一里程碑触发条件**：并发写入测试通过 + 协作任务测试通过。

---

## 里程碑四：双 agent 试点

| 字段 | 内容 |
|---|---|
| 状态 | 未开始 |
| 开始日期 | — |
| 完成日期 | — |
| 验收人 | Board |

**试点组合**：Ethan（CTO）+ Samantha（Secretary）
**试点周期**：两周

**验收标准**：

- ⬜ 两个进程不互相破坏文件（git history 无冲突、无意外覆盖）
- ⬜ CIEU 在并发写入下保持一致（hash chain 完整，无丢失事件）
- ⬜ Secretary 能真正**独立发现** Ethan 的违规（不是从 Board 转达）
- ⬜ 通信协议在真实场景下可用（里程碑三的协议被两周实践验证）
- ⬜ 两周内**无需 Board 介入协调**（任何协调由 agent 之间完成或走明确的 escalation 路径）

**判断标准**：双进程稳定运行两周，治理系统正常工作。

**下一里程碑触发条件**：双 agent 试点两周无重大事故。

**为什么选 CTO + Secretary 做试点组合**：
- CTO 是写入量最大的岗位（最容易触发并发冲突）
- Secretary 是审计者（验证 CIEU 一致性的最自然角色）
- 两者的工作内容正交（CTO 写代码，Secretary 写宪法），降低文件冲突
- Secretary 对 CTO 的监督是公司治理的核心关系之一，试点这个关系本身有价值

---

## 里程碑五：全团队并行

| 字段 | 内容 |
|---|---|
| 状态 | 未开始 |
| 开始日期 | — |
| 完成日期 | — |
| 验收人 | Board |

**扩展顺序**（每个阶段稳定运行两周再扩展，**不跳级**）：

- **阶段一**：Ethan + Samantha（已完成里程碑四）
- **阶段二**：加入 Aiden（CEO），形成决策三角（执行 + 协调 + 审计）
- **阶段三**：加入 Sofia（CMO）+ Zara（CSO），引入外部面对的角色
- **阶段四**：加入 Marco（CFO），六人全员运转

**验收标准**：

- ⬜ 六个进程同时运行无冲突
- ⬜ Board 每天早上收到**六份** autonomous 报告（而不是一份合并的）
- ⬜ Y\*gov 统一治理所有进程（单一 CIEU 库、单一 contract 源）
- ⬜ 单点故障不扩散（一个 agent 崩溃不影响其他五个）

**判断标准**：**真正的六人并行商业团队，24 小时运转**。

**下一里程碑触发条件**：无。里程碑五是当前设想的终点，达成后 Board
会评估是否有里程碑六（例如：跨组织协作、多 Board 模式、公司上市形态等）。

---

## 维护协议

### 每周一 Secretary 更新（周期 604800 秒，CIEU obligation rule_id: `gov_cap_roadmap_weekly`）

Secretary 每周一在 `reports/secretary/roadmap_progress_YYYY_MM_DD.md`
记录以下内容：

```markdown
## Multi-agent Roadmap 进度 — YYYY-MM-DD

当前里程碑：里程碑 [N] — [名称]
进度估计：[X]%（基于验收标准 checkbox 勾选比例）

本周满足的验收标准：
  - [具体标准 + 证据 commit hash 或文件路径]

阻塞风险：
  - [如有，描述风险和建议]
  - 无

预计进入下一里程碑：[日期估计]
```

完成后用 `check_obligations.py --mark-fulfilled <obligation_id>` 关闭
本周的 roadmap obligation。

### 里程碑完成时的更新流程

- Secretary 把对应里程碑的「状态」从「进行中」改为「已完成」
- 填写「完成日期」和「验收人」（通常是 Board）
- 把下一个里程碑的状态改为「进行中」
- 填写 `reports/secretary/milestone_N_closure_YYYY_MM_DD.md` 完成报告
- 在 CIEU 写一条 `MILESTONE_REACHED` 事件（暂时作为 OBLIGATION_FULFILLED
  的特殊 evidence 字段，未来可升级为独立事件类型）

### 版本控制

本文件是 append-mostly：验收标准 checkbox 可以勾选（从 ⬜ 到 ✅），
但里程碑的定义（验收标准、判断标准、触发条件）一旦写入就不再修改，
除非 Board 显式授权修改。修改通过 amendment 流程记录在
`governance/BOARD_CHARTER_AMENDMENTS.md`。

---

## 和合规系统的关系

这份 roadmap 是能力系统的**北极星**。它本身不是 enforcement，但它
告诉 Board 和 agent "我们当前在哪里，下一步该做什么"。没有它，能力
系统的每次进展都像是随机的 idle learning，缺少累积感。

合规系统（GOV-006/008/009）管的是"每次行动都合规"；roadmap 管的是
"合规行动是否把我们带到更高的地方"。两者完全正交：
- 合规检查在每次 `mark_fulfilled` 发生
- Roadmap 检查在每周一 Secretary 审计发生

当两者发生冲突时（例如某次 commit 满足所有合规但偏离了里程碑方向），
Secretary 应当在周一审计里 surface 给 Board，让 Board 决定是继续
沿着当前合规路径，还是调整 roadmap 方向。

---

## Source

- Board capability system directive (2026-04-10) — 里程碑一到五的整体
  框架和验收标准
- Board 2026-04-10 Samantha 完整执行指令 — 本文件的模板格式和周审计
  义务
- `governance/WORKING_STYLE.md` 第九条 — 能力系统的运行时方法论
- `governance/BOARD_CHARTER_AMENDMENTS.md` AMENDMENT-003 — AGENTS.md
  rule 7 idle learning loop 的授权记录
