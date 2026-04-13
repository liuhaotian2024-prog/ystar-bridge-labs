# 战略备忘录：Anthropic 政策变化 + Labs 肉身迁移决策

**To**: Board
**From**: CEO Aiden
**Date**: 2026-04-13
**Urgency**: P0-EXISTENTIAL（可能已在封禁 cohort 内）
**Decision deadline**: 2026-04-14 EOD

---

## §0 TL;DR

1. **Anthropic 2026-04-04 封禁了 Max plan 通过 OpenClaw 跑自主 agent 的使用模式**——文件原话直接点 OpenClaw 为 exemplar，Max $200 plan 被发现跑 $1-5K agent 算力触发此 policy
2. **我们的 workspace 字面叫 `OpenClaw` 且行为模式完全匹配**（10 agent / 24h cron / 自主团队） — 可能已被 target
3. Anthropic 2026-04-08 推出 **Claude Managed Agents**（beta，5 天前刚发），**正是为我们这种 use case 设计的合法降落区**
4. 推荐 **Hybrid 路线 C**：Max 留 Board ↔ CEO interactive，Managed Agents 跑 24/7 自主 team
5. W1 spike：用 Managed Agents 跑 LRS C2 sleep consolidation job（最离散组件，验证迁移 feasibility）

---

## §1 证据

- **VentureBeat**: "Anthropic cuts off the ability to use Claude subscriptions with OpenClaw and third-party AI agents"
- **Official policy effective 2026-04-04**: "Claude Pro and Max subscribers can no longer use their plan limits to power tools like OpenClaw... must switch to pay-as-you-go or direct API key"
- **Managed Agents docs** (platform.claude.com/docs/en/managed-agents/overview): 专为我们场景设计——long-running hours-long sessions / persist through disconnections / multi-agent coord / memory (research preview) / MCP native / $0.08/hr + token rates

---

## §2 Labs 当前风险画像

| 风险维度 | 判断 |
|---|---|
| Workspace 名 含 "openclaw" | ⚠️ 字面 match Anthropic keyword |
| 跑 10 agent 团队 | ⚠️ 典型"subscription 跑 agent 算力"模式 |
| 24h cron + heartbeat + rituals | ⚠️ "autonomous 而非 interactive" 特征 |
| Max plan 的 api key usage | ⚠️ 可能已被 flag |
| 未收到 Anthropic 封禁通知 | ✅ 但 may be imminent |

估计：**50-70% 已在 Anthropic target cohort**，30-50% 尚未触发但接近红线。

---

## §3 四条路线对比

| 路线 | Cost/mo | ToS 风险 | 迁移工 | 24/7 | 推荐 |
|---|---|---|---|---|---|
| A 继续 Max+OpenClaw | $100 | ❌ 4/4 直接针对 | 0 | ❌ session-bound | NO |
| B 全迁 Managed Agents | $120-210 | ✅ 合法 | 中 2-4 周 | ✅ 原生 | 可选 |
| **C Hybrid**（推荐） | $160-250 | ✅ | 小 1-2 周 | ✅ 部分 | **YES** |
| D 自托管 Agent SDK | $200+ | ✅ | 大 4-6 周 | ✅ 完全 | NO（投入回报比低） |

---

## §4 Hybrid 路线 C 详细架构

```
┌────────────────────────────────────────────────────────┐
│ Interactive Layer (Claude Code Max $100)               │
│  ├─ Board ↔ CEO 对话                                   │
│  ├─ CEO 战略 session + 决策讨论                        │
│  ├─ Sub-agent interactive dispatch (Maya/Leo/Ryan/...) │
│  └─ 人机协作的主战场                                    │
└────────────────────────────────────────────────────────┘

┌────────────────────────────────────────────────────────┐
│ Autonomous Layer (Managed Agents $60-150)              │
│  ├─ LRS C2 Sleep consolidation job (nightly)           │
│  ├─ LRS C7 Conversation replay build (offline)         │
│  ├─ Ritual cron (weekly strategy / product review ...) │
│  ├─ External signals ingestion (7am daily)             │
│  ├─ Tech radar scan (weekly)                           │
│  └─ X engagement worker（Safety layer 全过）            │
└────────────────────────────────────────────────────────┘

共享：
  - 同一 GitHub 仓库（ystar-bridge-labs + Y-star-gov + gov-mcp）
  - 同一 CIEU (memory.db sync via git)
  - 同一 knowledge/ 真源
```

---

## §5 W1 Spike Plan（2-3 day）

**选 LRS C2 Sleep consolidation** 为首个 Managed Agents 迁移组件：
- 纯 offline，无用户交互依赖
- 无 hook 耦合（离线跑）
- 失败成本低（迁移失败不影响 Labs 日常）
- 成功证明 Managed Agents 可承载我们其他组件

**Spike 里程碑**：
- D1: Anthropic API key 申请 + Managed Agents beta access 启用
- D2: 1 个 agent 定义 + 1 个 environment (Python container with gov-mcp) + 手动启 session
- D3: sleep_consolidation 脚本移植 + 夜跑一次 + 产出 `memory/sleep_digest_*` 与 OpenClaw 一致

**验收**: D3 产出文件与 OpenClaw 手跑版本 ≥ 95% 一致 + token cost < $2 + runtime < 30min

---

## §6 紧迫度与决策树

```
Board review 本 memo (今日)
  │
  ├─ 批路线 C (推荐) ──→ W1 spike ──→ 成功 ──→ W2 迁移背景服务 ──→ W4 全运营
  │                              └─→ 失败 ──→ 回评路线 D 或 B 全迁
  │
  ├─ 批路线 B (全迁) ──→ 直接迁，风险较大（interactive 部分也动）
  │
  ├─ 批路线 A (留守) ──→ 接受 Anthropic 随时可能 throttle/cut 的风险
  │
  └─ 再观察 7 天 ──→ 等 Anthropic 是否实际 throttle 我们 ──→ 被动响应
```

---

## §7 Board 决策点（按建议顺序）

1. **路线选择**: A / B / **C推荐** / D
2. **W1 spike 组件**: LRS C2（我的推荐）/ 其他（ritual cron / X engagement / 选其一）
3. **预算上调批准**: 当前 $100 → $160-250/mo
4. **workspace 改名**: 是否把 `.openclaw` 改为中性名（如 `.ystar`）减少 keyword hit 风险？（工程成本：全局 find+replace 数 GB，CI/CD 改，路径全改）—— 我倾向**暂不改**（成本高，Anthropic 应该看行为模式不只 keyword）
5. **Anthropic API key**: Board 有现成 key 还是要新申请？

---

## §8 我的立场（CEO）

**强推路线 C**。理由：
- A 是鸵鸟政策，且与 Board 今晚问的"绝对无缝复活"冲突（Max session-bound 做不到真 24/7）
- B 激进，interactive 部分迁移风险高（Board 习惯 Claude Code TUI）
- D 工程投入远超收益，且落后 Anthropic 两步
- C **用 Anthropic 新产品解 Anthropic 新政策制造的问题**——最优雅、成本最低、风险最小

---

## §9 如果 Board 批 C，CEO 立即执行清单

- [ ] 派 Ryan W1 spike：Managed Agents sleep_consolidation 移植
- [ ] 派 Jordan：API key 申请 + beta access 流程
- [ ] 派 Maya：CIEU 同步方案（Managed Agents session 的 CIEU 如何回写 ystar-company 的 memory.db）
- [ ] CEO：每日早会验收 spike 进度

等 Board 签字即可启动。
