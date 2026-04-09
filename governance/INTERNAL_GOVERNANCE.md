# Y* Bridge Labs · 内部治理文档
# Internal Governance Document
# 创建日期：2026-04-09 · 由 Secretary 在 GOV-005 Part 2 中创建
# 服从：AGENTS.md / governance/WORKING_STYLE.md

---

## 决策权限层级 (GOV-005)

Y* Bridge Labs 内部所有决策按影响范围和可逆性划分为三级。
每级有明确的触发条件、流程和例子。

所有 Level 2 和 Level 3 的决策必须使用反事实推理提案格式，
详见 `governance/WORKING_STYLE.md` 第七条。

---

### Level 1 — 岗位自决

#### 触发条件

**同时满足**以下全部：

- 单岗位内部，不影响其他岗位
- 完全可逆
- 无外部可见性（不发布、不花钱、不对外承诺）

#### 流程

直接执行，完成后汇报结果，**无需事前请示**。
也无需提交反事实推理提案。

#### 例子

- Ethan 修 bug
- Secretary 更新归档索引
- CFO 更新 burn rate 记录
- CMO 修改内部草稿
- 任何 agent 跑 `ystar doctor`、`check_obligations.py` 等只读命令

---

### Level 2 — CEO 决策

#### 触发条件

满足以下**任一**，且不触发 Level 3 条件：

- 跨岗位协调
- 影响内部流程或规范
- 可逆但涉及多人

#### 流程

1. **责任岗位用反事实推理格式提案**（见 `governance/WORKING_STYLE.md` 第七条）
2. **CEO 审阅最优解**，直接批准或否决
3. **执行**
4. **24 小时内向 Board 汇报结果**（不需要 Board 事前批准）

#### 例子

- `agents/*.md` 修改
- `.ystar_session.json` 修改
- 义务注册（`register_obligation.py` 真实运行）
- 内部流程调整
- `DIRECTIVE_TRACKER.md` 更新
- 新建/重命名/删除 `governance/` 下的非宪法文档
- 新建/修改 `scripts/` 下的工具脚本（除非影响外部 commit / 发布行为）

---

### Level 3 — Board 决策

#### 触发条件

满足以下**任一**：

- 修改 `AGENTS.md`（公司宪法）
- 外部发布且不可撤回（HN、LinkedIn、PyPI、arXiv）
- 任何金钱支出
- 影响产品对外承诺（版本号、专利、定价、API 合同）
- 架构变更影响两个及以上岗位的核心职责

#### 流程

1. **团队用反事实推理格式提案**，给出最优解 + 次优解
2. **Board 只看结论**，说"批准"或"否决最优，用次优"
3. **CEO 记录 Board 决策并执行**
4. **Secretary 归档**到 `knowledge/decisions/`

---

## 与其他治理文档的关系

| 文档 | 作用 | 关系 |
|---|---|---|
| `AGENTS.md` | 公司宪法（机器执行层 + 文档同步层） | Level 3 决策才能修改，且必须走 BOARD_CHARTER_AMENDMENTS 流程 |
| `governance/WORKING_STYLE.md` | 工作文化宪法 + 提案格式（第七条） | 所有 Level 2/3 提案必须遵守 |
| `governance/BOARD_CHARTER_AMENDMENTS.md` | AGENTS.md 修改授权日志 | Secretary 维护，Ethan 执行 |
| `governance/TEMP_LAW.md` | 临时约法 | 所有 Level 都必须先查 |
| `agents/*.md` | 岗位行为宪法 | Secretary 在 DNA 蒸馏权限内可改（Level 2） |
| `.ystar_session.json` | Y\*gov 运行时配置（执行层） | Ethan 在 Level 2 授权下可改 |

---

## 反事实推理与三级权限的协同

```
Level 1 → 直接执行
          (无需提案)

Level 2 → 反事实提案 → CEO批准 → 执行 → 24h内汇报Board
          ↑
          (Y*gov CounterfactualEngine 在团队侧运行)

Level 3 → 反事实提案 → CEO转交 → Board批准/否决 → 执行 → Secretary归档
          ↑
          (团队完成全部分析，Board只做最终决策)
```

**核心原则**：决策点距离推理点越近越好。Level 1 的决策点和推理点是同一岗位；Level 2 的决策点是 CEO，但推理由责任岗位完成；Level 3 的决策点是 Board，但所有反事实分析由团队完成。Board 永远不当选择器。

---

## 分层治理架构 (Layered Defense, GOV-005 Finding 4)

Y\* Bridge Labs 的**治理执行**分两层,每层有自己的契约源,**by-design 不是 redundancy**。这和上面的"决策权限层级"是两个独立维度:

- **决策权限层级** (Level 1/2/3) 回答的是"谁来决定?"
- **分层治理架构** (Layer 1 命令层 / Layer 2 行为层) 回答的是"谁来执行?"

两个维度互相正交,任何一个 directive 同时受两组规则约束。

### Layer 1: 命令层(ystar Python hook)

- **契约源**: `.ystar_session.json` 的 `deny_commands`、`deny`、`obligation_agent_scope`、`restricted_write_paths`、`delegation_chain` 等结构化字段
- **执行点**: ystar Python hook (PreToolUse / PostToolUse) 在 Claude Code 的 tool layer 拦截
- **覆盖**: 所有走 Claude Code tool layer 的 file ops、bash commands、edits
- **典型 catch**: `ystar setup --yes` (GOV-005 Part 3 / AMENDMENT-001)、写 `/etc`、`rm -rf`、AGENTS.md 修改尝试
- **运行时刻**: 本地 Mac mini Python 进程,响应 Claude Code hook 调用

### Layer 2: 行为层(gov-mcp MCP server)

- **契约源**: `AGENTS.md` 的 markdown prose,通过 `gov-mcp` 的 regex parser 翻译成 `IntentContract`
- **执行点**: gov-mcp 的 `gov_check` / `gov_enforce` MCP 工具,在每次 MCP client 调用工具时拦截
- **覆盖**: 所有走 MCP 协议的 tool call(自然语言意图层面的 ALLOW/DENY)
- **典型 catch**: 合约范围外的工具使用、agent_id 越权、跨 domain 调用、监督式 agent 行为模式
- **运行时刻**: 本地 Mac mini gov-mcp server (PID 监听 :7922 SSE),响应 MCP client 请求

### 为什么是两层而不是一层?

GOV-005 Finding 4 提出了 4 个候选合并方案,Board 全部否决:

| 候选 | 做什么 | Board 否决理由 |
|---|---|---|
| α | 把 `.ystar_session.json` 的 `deny_commands` 复制到 `AGENTS.md` | **制造 redundancy + 同步漂移**: 一个文件改了另一个没改 → 两层规则不一致 → 哪一层是真相? |
| β | 改 gov-mcp 产品代码,让它同时读 `AGENTS.md` + `.ystar_session.json` | **跨 repo 改产品** = Level 3 + gov-mcp release 周期耦合 + 长期工程债 |
| γ | **接受分层 by-design,文档讲清责任域**(本节) | **采纳** ✅ |
| δ | 启用 `YSTAR_LLM_PROVIDER=anthropic`,让 gov-mcp 用 LLM 解析 `AGENTS.md` 提高 contract coverage | **违反 Iron Rule 1 (Deterministic Enforcement)**: LLM 进 ALLOW/DENY check() 路径 = 治理可被 prompt-injected。Y\*gov 的核心卖点之一就是"治理路径不带 LLM",自己破坏这个卖点 = 自杀 |

### 正确的心智模型

**两个 contract source,两个执行点,两个责任域,任何客户端同时受两层保护**:

```
      ┌──────────────────────────────────────────┐
      │ Client (Claude Code / spawned subprocess)│
      └──────┬──────────────────────┬────────────┘
             │                      │
   tool call                   MCP request
   (file/bash/edit)            (gov_check/gov_exec)
             │                      │
             ▼                      ▼
   ┌─────────────────┐    ┌──────────────────┐
   │ Layer 1         │    │ Layer 2          │
   │ ystar hook      │    │ gov-mcp server   │
   │ (PreToolUse)    │    │ (port 7922 SSE)  │
   ├─────────────────┤    ├──────────────────┤
   │ contract source:│    │ contract source: │
   │ .ystar_session  │    │ AGENTS.md        │
   │ .json           │    │ (regex parsed)   │
   ├─────────────────┤    ├──────────────────┤
   │ enforces:       │    │ enforces:        │
   │ - deny_commands │    │ - intent contract│
   │ - file deny     │    │ - delegation chain│
   │ - obligation    │    │ - agent_id scope │
   │   triggers      │    │ - MCP tool ALLOW │
   └─────────────────┘    └──────────────────┘
```

- 走 Claude Code tool layer(file ops、bash、edit)→ **Layer 1 (ystar hook) 拦截**
- 走 MCP 协议(MCP tool calls)→ **Layer 2 (gov-mcp) 拦截**
- 同一个动作如果两层都覆盖,**会被两层都检查一遍**

**这不是 redundancy,这是 defense-in-depth**。两层任何一层放过,另一层有机会拦;两层任何一层 down,另一层有机会兜底。

### 配置不同步是 feature 不是 bug

- `.ystar_session.json` 改 `deny_commands` 不需要同步到 `AGENTS.md`
- `AGENTS.md` 改 contract prose 不需要同步到 `.ystar_session.json`
- 两个文件**单独演化**,Board 在改任何一个时不需要考虑另一个
- 这降低了 cognitive load,代价是每个 client 必须知道**两个执行点都存在**

**如果未来有人提议"统一 contract source 简化架构",立刻引用 GOV-005 Finding 4 决策 + 本节 + Iron Rule 1**。这是 Y\*gov 哲学的硬约束。

### 已知 coverage gap (by-design)

| 拦截能力 | Layer 1 (ystar hook) | Layer 2 (gov-mcp) |
|---|---|---|
| `ystar setup --yes` | ✅ AMENDMENT-001 | ❌ (在 .ystar_session.json 不在 AGENTS.md) |
| `rm -rf` / `sudo` / `DROP TABLE` | ✅ deny_commands | ❌ |
| 写 `/etc` `/root` `/production` | ✅ deny | ⚠️ regex 0.7 confidence,部分覆盖 |
| GOV-001 obligation 跟踪 | ✅ obligation_agent_scope | ✅ OmissionEngine (内部) |
| AGENTS.md 不可变 | ✅ Y\*gov hook (commit 90ffd4f) | (gov-mcp 自己读 AGENTS.md,不修改) |
| Spawned MCP tool calls | ❌ (hook 不在 MCP layer) | ✅ gov_check 拦截 |
| Agent_id 越权 | ⚠️ restricted_write_paths(部分) | ✅ delegation chain |

**这些 gap 是 by-design 的两层分工**,不是 bug list。要把某个 gap 关掉,问题不是"应该关",而是"应该让哪一层关",因为关错层会破坏单层心智模型的简洁性。

---

## 来源

Board GOV-005 directive (2026-04-09) 第二部分。本文件由 Secretary 在
GOV-005 Part 2 创建，作为 Y\* Bridge Labs 内部决策的权威文档。

后续修改属于 Level 2 决策（影响内部流程，不是宪法），需要按反事实推理
提案格式提交 CEO 批准。
