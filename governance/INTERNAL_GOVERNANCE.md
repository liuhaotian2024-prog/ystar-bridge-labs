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

## 分层治理架构 (Layered Defense — GOV-005 Finding 4 + GOV-007 Step 2 update)

Y\* Bridge Labs 的**治理执行**分两层。**Source 共享,enforcement points 独立**——这是 GOV-007 Step 2 (2026-04-09) 之后的稳定架构。

> **历史注**: 本节最初由 GOV-005 Finding 4 (2026-04-09) 写入,当时 Layer 2 从 `AGENTS.md` regex 解析 contract,与 Layer 1 的 `.ystar_session.json` 是两套独立 source。GOV-007 Step 2 把 Layer 2 的 source 切换到 `.ystar_session.json`,与 Layer 1 共用。**Defense-in-depth 的精神不变**(两个 enforcement points 各自独立检查),但 framing 从"两个 source"修订为"共享 source + 独立 enforcement"。两个原则在不同维度,互不矛盾:

- **Single source of truth at the contract level** 解决"一致性"(零 drift,零同步成本)
- **Defense-in-depth at the enforcement point level** 解决"鲁棒性"(任一 enforcement point 失效另一兜底)

这和"决策权限层级"也是正交维度:

- **决策权限层级** (Level 1/2/3) 回答"谁来决定?"
- **分层治理架构** (Layer 1 命令层 / Layer 2 行为层) 回答"谁来执行?"

任何一个 directive 同时受两组维度约束。

### 共享 contract source: `.ystar_session.json`

两层都从同一个文件读规则:

| 字段 | 用途 | Layer 1 (hook) | Layer 2 (gov-mcp) |
|---|---|---|---|
| `schema_version` | 协议版本协调 | ignore (兼容) | ✅ 启动校验 |
| `contract.deny` | 路径 deny 列表 | ✅ | ✅ post Step 2 |
| `contract.deny_commands` | 命令 deny 列表 | ✅ | ✅ post Step 2 |
| `contract.obligation_timing` | 义务时限 | ✅ | ✅ post Step 2 |
| `obligation_agent_scope` | 义务 ↔ agent 映射 | ✅ | ⚠️ Layer 2 暂不利用 (GOV-008 候选) |
| `agent_write_paths` | per-role 写权限 | ✅ | ⚠️ 同上 |
| `restricted_write_paths` | file ↔ allowed agent | ✅ | ⚠️ 同上 |
| `delegation_chain` | 委派链 | ✅ | ✅ |

`.ystar_session.json` 是**单一真相源 (single source of truth)**,所有规则的 authoritative 拷贝住在这里。`AGENTS.md` 退化为**人类可读的伴随文档**(human story / rationale),**不是 enforcement source**。

### Layer 1: 命令层(ystar Python hook)

- **契约源**: `.ystar_session.json`(直接 dict load,无翻译)
- **执行点**: ystar Python hook (PreToolUse / PostToolUse) 在 Claude Code 的 tool layer 拦截
- **覆盖**: 所有走 Claude Code tool layer 的 file ops、bash commands、edits
- **典型 catch**: `ystar setup --yes` (AMENDMENT-001)、写 `/etc`、`rm -rf`、AGENTS.md 修改尝试
- **运行时刻**: 本地 Mac mini Python 进程,响应 Claude Code hook 调用
- **生命周期**: 无状态,每次 PreToolUse 都是新进程,自动读最新 `.ystar_session.json`,不需要 reload 信号

### Layer 2: 行为层(gov-mcp MCP server)

- **契约源**: `.ystar_session.json`(post GOV-007 Step 2,通过 `--session-config` flag 启动)
  - **历史**(pre GOV-007 Step 2): 从 `AGENTS.md` 用 regex 解析,confidence ≤0.7,只能提取部分规则
  - **现在**: 直接 dict load,confidence ≥0.95(structured data, no parsing)
  - **`--agents-md` 仍保留为 deprecated fallback**(向后兼容旧部署)
- **执行点**: gov-mcp 的 `gov_check` / `gov_enforce` MCP 工具,在每次 MCP client 调用工具时拦截
- **覆盖**: 所有走 MCP 协议的 tool call(自然语言意图层面的 ALLOW/DENY)
- **典型 catch**: 合约范围外的工具使用、agent_id 越权、跨 domain 调用、监督式 agent 行为模式
- **运行时刻**: 本地 Mac mini gov-mcp server (PID 监听 :7922 SSE),响应 MCP client 请求
- **生命周期**: 长驻进程,启动时读 `.ystar_session.json`,需要重启或 SIGHUP (待 GOV-008 NL pipeline) 才能 reload

### Finding 4 的 4 个候选方案历史回顾

GOV-005 Finding 4 (2026-04-09 早些时候)曾提出 4 个候选合并方案。Board 当时全部否决,**post GOV-007 Step 2 视角下的复盘**:

| 候选 | 当时做什么 | Board 当时否决理由 | post Step 2 复盘 |
|---|---|---|---|
| α | 把 `.ystar_session.json` deny_commands **复制**到 AGENTS.md prose | redundancy + drift | **当时正确** —— 复制是错的。GOV-007 Step 2 用 "Layer 2 直接读 source" 而不是 "复制 source",解决了 underlying 问题 |
| β | gov-mcp 同时读 AGENTS.md + .ystar_session.json (改产品代码) | 跨 repo + Level 3 + 工程债 | **GOV-007 Step 2 是 β 的精简版**: 不"同时读两个"而是"只读 .ystar_session.json"。工程量从 β 估的"重大改动"降为 ~80 行 |
| γ | 接受当前架构,文档讲清责任域 | 采纳 ✅ | **现在被 GOV-007 Step 2 superseded** —— γ 是 short-term mitigation,Step 2 是 long-term fix |
| δ | 启用 LLM-based contract translation 提高 regex 覆盖率 | **违反 Iron Rule 1** | **永久否决,不可逆** —— Iron Rule 1 是宪法层硬约束,GOV-007 Step 2 之后仍然严守 |

**GOV-007 Step 2 的本质**: 在保持 Iron Rule 1 (no LLM in check()) 和 Finding 4 enforcement-point 分离原则的前提下,通过更窄的 scope 实现了 β 的 underlying intent。这是 architectural refinement,**不是反转 Finding 4**。

### 正确的心智模型(post GOV-007 Step 2)

```
                         .ystar_session.json
                         (single source of truth)
                                  │
                ┌─────────────────┴─────────────────┐
                │                                   │
                ▼                                   ▼
       ┌──────────────────┐               ┌──────────────────┐
       │ Layer 1          │               │ Layer 2          │
       │ ystar Python hook│               │ gov-mcp server   │
       │ (PreToolUse)     │               │ (port 7922 SSE)  │
       │ stateless,每次   │               │ long-lived,启动 │
       │ tool call 重读   │               │ 时 load,需 reload│
       └────────┬─────────┘               └────────┬─────────┘
                │                                   │
        intercepts                          intercepts
        Claude Code tool calls              MCP protocol calls
        (Bash/Read/Edit/Write/etc.)         (gov_check/gov_exec/etc.)
                │                                   │
                ▼                                   ▼
              ALLOW or DENY                 ALLOW or DENY
              (deterministic, no LLM)       (deterministic, no LLM)
```

- **Source: 1 个**(`.ystar_session.json`)→ 零 drift,零同步成本
- **Enforcement points: 2 个**(hook + MCP server)→ defense-in-depth,任一失效另一兜底
- **Source ↔ enforcement 关系**: 1-to-many (一个 source 喂两个 enforcement points)

### 已知 coverage matrix(post GOV-007 Step 2)

| 拦截能力 | Layer 1 (ystar hook) | Layer 2 (gov-mcp) | 改善 |
|---|---|---|---|
| `ystar setup --yes` | ✅ AMENDMENT-001 | ✅ post Step 2 | ⬆️ pre-Step-2 是 ❌ |
| `rm -rf` / `sudo` / `DROP TABLE` | ✅ deny_commands | ✅ post Step 2 | ⬆️ pre-Step-2 是 ❌ |
| 写 `/etc` `/root` `/production` | ✅ deny | ✅ post Step 2 | ⬆️ pre-Step-2 是 ⚠️(regex 0.7) |
| GOV-001 obligation 跟踪 | ✅ obligation_agent_scope | ✅ OmissionEngine (内部) | unchanged |
| AGENTS.md 不可变 | ✅ Y\*gov hook (commit 90ffd4f) | (gov-mcp 不修改 AGENTS.md) | unchanged |
| Spawned MCP tool calls | ❌ (hook 不在 MCP layer) | ✅ gov_check 拦截 | unchanged |
| Agent_id 越权 | ⚠️ restricted_write_paths(部分) | ✅ delegation chain | unchanged |
| `obligation_agent_scope` 利用 | ✅ | ⚠️ Layer 2 暂不利用 | GOV-008 候选 |

**post GOV-007 Step 2 的最大实际改进**: 前 3 行从"Layer 2 ❌"变成"Layer 2 ✅"。Defense-in-depth 现在在前 4 项上是**双层兜底**而不是单层。

### 如果未来有人提议"再回到两个独立 source"

引用本节 + GOV-005 Finding 4 历史 + GOV-007 Step 2 commit 链。**两层独立 enforcement points 是要保留的(defense-in-depth),两套独立 sources 是 GOV-007 之前的临时状态,不应该回滚**。

### 如果未来有人提议"在 check() 路径加 LLM"

引用 Iron Rule 1 + Finding 4 δ 候选历史 + DNA #007。**永远 No,不讨论**。LLM 可以用在 contract authoring(GOV-008 NL pipeline),不能用在 contract enforcement。这是宪法层硬约束。

---

## 来源

Board GOV-005 directive (2026-04-09) 第二部分。本文件由 Secretary 在
GOV-005 Part 2 创建，作为 Y\* Bridge Labs 内部决策的权威文档。

后续修改属于 Level 2 决策（影响内部流程，不是宪法），需要按反事实推理
提案格式提交 CEO 批准。
