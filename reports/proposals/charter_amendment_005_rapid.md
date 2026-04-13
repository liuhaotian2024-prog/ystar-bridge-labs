# AMENDMENT-005 — L0-L3 Decision Tier → RAPID Decision Framework

| 字段 | 内容 |
|---|---|
| Level | 3（宪法伴随文档 · 架构变更影响全部 5 个 C-suite + 4 工程师 + Secretary 的决策权责） |
| 起草人 | Samantha Lin (Secretary) |
| 起草日期 | 2026-04-12 |
| Board 授权起草日 | 2026-04-12 |
| 提案依据 | Board 2026-04-12 批准引入 Bain RAPID + Amazon 6-pager 两个外部框架；Pilot EXP-1 (RAPID 真决策) + EXP-2 (6-pager v2) 证据链完整 |
| 提案位置 | `reports/proposals/charter_amendment_005_rapid.md`（本文件）|
| 配套提案 | AMENDMENT-006（6-pager 派活格式统一）|

---

## 1. 摘要（一句话）

将 Y* Bridge Labs 现行 "L0-L3 四级决策权限" 全面替换为 Bain & Company 的 **RAPID** 五角色显式分配框架（R/A/P/I/D），所有跨岗位决策必须显式写明五角色归属，由 `.ystar_session.json` 的 `require_rapid_role_assignment` 规则在 hook 层强制执行。

---

## 2. 事实对照（现行 L0-L3 vs RAPID）

### 2.1 L0-L3 当前定义（`governance/INTERNAL_GOVERNANCE.md` §决策权限层级）

| 层级 | 触发条件 | 决策权 |
|---|---|---|
| L0 | Agent 空闲自学，只写 `knowledge/{role}/` | Agent 自身 |
| L1 | 单岗位、完全可逆、无外部可见性 | 岗位自决 |
| L2 | 跨岗位、影响内部流程、可逆但涉及多人 | CEO |
| L3 | 宪法修改 / 外部发布 / 金钱 / 产品对外承诺 / 架构变更 | Board |

**核心缺陷**（EXP-1 pilot 证据）：
- 单一维度（升级链条），无法同时表达"谁提方案 / 谁可否决 / 谁执行 / 谁提供输入 / 谁最终拍板"
- 在 L0-L3 下 Maya（治理合规审查）、Secretary（证据收集者）、Ryan（技术执行者）的贡献**隐形**
- EXP-1 真决策（memory 闭环 4 优先级）下，若走 L0-L3 路径，CEO 会漏掉 Maya 的 CONDITIONAL 两条前置、Ryan 的 event-driven 选择、Secretary R.2 的"原生 memory/ 不存在" finding
- 违反本公司 DNA #7（反事实推理 + Board 不当选择器）的精神：L0-L3 没有把"推理点 ≠ 决策点"的分离明确落到角色

### 2.2 RAPID 五角色（Bain & Company 官方定义）

来源：[Bain & Company — RAPID Decision-Making](https://www.bain.com/insights/rapid-decision-making/) / [Asana — RAPID (2025)](https://asana.com/resources/rapid-decision-making) / [Bridgespan](https://www.bridgespan.org/insights/nonprofit-organizational-effectiveness/rapid-decision-making)

| 角色 | 职责 | 关键边界 |
|---|---|---|
| **R** — Recommend | 提方案、收集证据、推动提案前进 | 必须给出 ≥2 备选方案 + 推荐解 + 反事实分析 |
| **A** — Agree | 在其专业域内有正式否决权（veto），通常用于合规/治理/法律 | 必须显式给 AGREE / CONDITIONAL AGREE / REJECT 三态之一 |
| **P** — Perform | 决策做出后执行 | 必须给出可执行 plan（工作量 / 前置依赖 / 失败处理）|
| **I** — Input | 提供专业输入，**不能阻断** | 可改 R 方案的边界，但不能投否决票 |
| **D** — Decide | 最终拍板，**每个决策有且仅有一个 D** | 整合 R/A/P/I 四方后出 D.1 决定 + D.2 理由 + D.3 执行触发 + D.4 下游通知 |

**自然流**：R → I → A → D → P

**相对于 L0-L3 的表达力优势**：
- A（否决权）与 D（决定权）是独立轴，不再混淆
- 隐形贡献者（I 的输入、A 的合规审查）被显式登记
- Pilot EXP-1 证据：Maya 的 CONDITIONAL 两条前置在 L0-L3 下不会被 catch，在 RAPID 下是 A 角色的 first-class 输出

---

## 3. 修改前 / 修改后 diff

### 3.1 `governance/INTERNAL_GOVERNANCE.md` — 整个"决策权限层级"章节重写

**修改前**（§决策权限层级，L0-L3 四小节）：如 `INTERNAL_GOVERNANCE.md` 当前 §8–§133。

**修改后**（整段替换）：

```markdown
## 决策权限层级 (AMENDMENT-005)

Y* Bridge Labs 内部所有跨岗位决策按 Bain RAPID 五角色框架显式分配。
单一维度的 L0-L3 升级链条 retire（见 AMENDMENT-005 §4 迁移表）。

每个跨岗位决策必须由 R 发起，附五角色归属表，走
`R → I → A → D → P` 流程。每个决策**有且仅有一个 D**。

所有涉及 A / D ≠ R 自身的决策，提案必须使用 Amazon 6-pager v2 格式
（见 AMENDMENT-006）+ RAPID 五角色归属表。

### RAPID 角色职责

（各小节详见下文 §3.2）

### Board 的位置

Board 不再是"L3 升级终点"。Board 在 RAPID 里是**某些决策的 D**，
由决策性质决定（见下文 §4 迁移表）。Board 只对其为 D 的决策做
final call；其他决策 Board 是旁观者（或在被邀请时作为 I）。

### 与反事实推理的协同

`governance/WORKING_STYLE.md` 第七条（反事实推理提案规范）继续有效，
作为 R 角色产出"≥2 备选方案 + 推荐解 + Rt 分析"的标准格式。RAPID
替换的是"谁决定"，不是"如何推理"。
```

### 3.2 新增"RAPID 角色职责"小节（写入 `governance/INTERNAL_GOVERNANCE.md` §决策权限层级 之后）

```markdown
### R — Recommend

**触发条件**: 任何跨岗位决策的发起点。岗位发现问题 / 收到 directive /
CIEU 报警触发改进 → 该岗位自动成为 R（或 R 指派到更合适的岗位）。

**权责边界**:
- 必须给出 ≥2 备选方案（否则提案不合格，退回）
- 必须给出推荐解 + Rt (反事实差距) 分析
- 必须在提案里显式标注 R/A/P/I/D 五角色各自的 agent_id
- 可在提案里请求 I 扩展（邀请额外岗位提供输入）

**违规处理**:
- 只给一个方案 → A 退回 R，不走到 D
- R/A/P/I/D 五角色未全部填写 → hook (require_rapid_role_assignment) 硬拒

### A — Agree

**触发条件**: R 的提案在其专业域内需要 A 的正式同意才能送到 D。
默认 A 候选池：治理合规（Maya / eng-governance）、Secretary（宪法一致性）、
CTO（技术可行性）、CFO（预算影响）、CSO（客户承诺影响）、CMO（对外发布口径）。
一个提案可能有多个 A（各自负责不同专业域）。

**权责边界**:
- 必须显式输出 `AGREE` / `CONDITIONAL AGREE with [前置条件列表]` / `REJECT [理由]` 三态之一
- CONDITIONAL 的前置条件是硬约束，P 必须全部满足才能启动
- A 不是多数表决机制——任一 A 的 REJECT 阻断提案送到 D

**违规处理**:
- A 未给出三态之一（例如"看起来 OK"）→ R 退回请求明确
- A 在自身专业域外越权否决 → D 可驳回 A 的 REJECT（并记录 CIEU）

### P — Perform

**触发条件**: D 做出决定后自动激活。

**权责边界**:
- 必须给出可执行 plan：工作量以 intent completion 闭环数计（非人类时间）、前置依赖、失败处理
- 遇到 plan 与 A 的 CONDITIONAL 冲突 → 停 + 回 A 重议，不自行绕过
- P 执行中的战术调整是 L1 等价（本岗位自决），不需要重走 RAPID

**违规处理**:
- P 未满足 A 的 CONDITIONAL 前置即启动 → hook 拦截 + CIEU 告警
- P 执行偏离 D 决定 → 回到 R 重新走一轮

### I — Input

**触发条件**: 被 R 邀请，或 I 岗位主动发现决策缺少其专业视角时自荐。

**权责边界**:
- 提供专业输入（技术红线 / 合规提示 / 历史经验）
- **不能阻断提案**（区别于 A）
- 可以改变 R 方案的边界（如 CTO 在 memory 闭环 4 pilot 中加了 frontmatter 实机验证红线）
- 一个决策可以有 0 个或多个 I

**违规处理**:
- I 滥用"输入"作为事后否决 → D 驳回，记 CIEU
- 关键 I 岗位被遗漏 → A 可以要求 R 补邀请

### D — Decide

**触发条件**: R/A/P/I 四方输出齐备，A 无 REJECT，则自动送到 D。

**权责边界**:
- **每个决策有且仅有一个 D**（violate → hook 拦截）
- D 必须产出 D.1 决定 + D.2 理由（≤100 字）+ D.3 执行触发清单 + D.4 下游通知
- D 不是盖章机：如果 R/A/P/I 不充分，D 应退回补充，而非勉强决策
- D 的 scope 扩展（如 CEO 在 EXP-1 D 段新增"每角色 1+1 蒸馏硬任务"）是 D 的合法权力
- Board 在某类决策中是 D（见 §4 迁移表），其他决策 Board 不是 D

**违规处理**:
- 两个岗位同时自称 D → hook 硬拒（duplicate_decider）
- D 直接拍板未读 R/A/P/I 输出 → CIEU 审计可追溯，Secretary 周审计会 catch

### RAPID 流程的 CIEU 审计锚点

| 阶段 | CIEU event | 必需字段 |
|---|---|---|
| R 发起 | `RAPID_PROPOSAL_DRAFTED` | recommender, decider, alternatives≥2 |
| I 输入 | `RAPID_INPUT_ADDED` | input_role, delta_to_proposal |
| A 决断 | `RAPID_AGREE_STATE` | agree_role, state∈{AGREE,CONDITIONAL,REJECT} |
| D 决定 | `RAPID_DECIDED` | decider_role, decision, rationale |
| P 执行 | `RAPID_PERFORM_START/END` | performer_role, completion_intent_id |
```

### 3.3 `.ystar_session.json` 新增 `require_rapid_role_assignment` 规则

**修改前**：`agent_behavior_rules` 下无此字段。

**修改后**：在每个角色块的 agent_behavior_rules 末尾（或作为 global rule）新增：

```json
"require_rapid_role_assignment": {
  "enabled": true,
  "description": "任何跨岗位决策（提案、directive、amendment）必须在 CIEU 记录里含 R/A/P/I/D 五角色显式 agent_id。缺失任一角色 → hook 硬拒。",
  "scope": "cross_role_decisions_only",
  "exemption": [
    "L0_equivalent_single_role_self_learning",
    "daily_check_obligations",
    "read_only_commands"
  ],
  "enforce_point": "record_intent.py 的 CLI parse 阶段 + gov_check MCP 层",
  "violation_action": "exit_2_with_message"
}
```

新增一个顶层字段：

```json
"rapid_contract": {
  "version": 1,
  "roles": ["R", "A", "P", "I", "D"],
  "unique_decider": true,
  "agree_states": ["AGREE", "CONDITIONAL", "REJECT"],
  "minimum_alternatives_in_R": 2,
  "default_A_by_domain": {
    "governance_compliance": ["eng-governance", "secretary"],
    "technical_feasibility": ["cto"],
    "budget_impact": ["cfo"],
    "customer_commitment": ["cso"],
    "external_narrative": ["cmo"]
  }
}
```

### 3.4 `CLAUDE.md` — "Board Decision Rules" 段落修改

**修改前**（§ Board Decision Rules）：

```
All external releases, code merges, and actual payments require manual
confirmation from Haotian Liu.
All other work may be executed autonomously by agents.
```

**修改后**（保留原文 + 增加 RAPID 指向）：

```
All external releases, code merges, and actual payments require manual
confirmation from Haotian Liu.
All other work may be executed autonomously by agents.

Decision rights within the company follow the RAPID five-role assignment
framework (see AMENDMENT-005 and `governance/INTERNAL_GOVERNANCE.md`
§决策权限层级). Board is the D for decisions listed in the
"Board-as-D" row of the AMENDMENT-005 §4 migration table; for all other
cross-role decisions, Board's role is I (may contribute input) or
bystander.
```

---

## 4. L0-L3 → RAPID 迁移映射表

| 旧 Level | 典型场景 | 新 RAPID 角色归属 | D 默认岗位 |
|---|---|---|---|
| **L0** | Agent 空闲自学（`knowledge/{role}/` 只写） | 单角色 D=自身, R=自身, 无 A 无 P 无 I | 本岗位 |
| **L1** | 单岗位可逆操作（bug fix、归档更新） | D=本岗位, R=本岗位, A=（通常无；触发合规才有） | 本岗位 |
| **L2 · 跨岗位协调** | memory 闭环、义务注册、agent_write_paths 小改 | R=责任岗位, A=eng-governance 或 secretary, P=执行岗位, I=相关 C-suite, **D=CEO** | CEO |
| **L2 · 内部流程规范** | WORKING_STYLE 小修、agents/*.md 更新 | R=Secretary, A=eng-governance, P=Secretary, I=受影响角色, **D=CEO** | CEO |
| **L3 · 宪法/架构变更** | AMENDMENT / AGENTS.md / 架构 refactor | R=起草岗位, A=Secretary+eng-governance, P=Secretary, I=全部 C-suite, **D=Board** | Board |
| **L3 · 外部发布** | HN/LinkedIn/PyPI/blog/whitepaper | R=CMO/CEO, A=CMO (口径) + Secretary (宪法一致), P=CMO/CTO, I=相关方, **D=Board** | Board |
| **L3 · 金钱支出** | 预算动用、付费工具 | R=CFO, A=Secretary (治理), P=CFO, I=C-suite, **D=Board** | Board |
| **L3 · 产品对外承诺** | 定价 / API 合约 / 版本号 / 专利 | R=CSO 或 CTO, A=Secretary+CFO, P=责任岗位, I=全员, **D=Board** | Board |
| **Autonomous Mission** | Board 明确授权的长期任务 | Mission 内战术决策 D=Mission Owner；跨周期策略 D=CEO；资源/对外 D=Board | 分层（见 `INTERNAL_GOVERNANCE.md` 现 Autonomous Mission 节，保留不动） |

**核心变化**：
- L2 下"CEO 一人独断"被替换为"CEO 是 D，但必须收到 R/A/P/I 四方齐备输出"
- L3 下"Board 当选择器"被彻底移除——Board 是 D，但 R/A/P/I 全部由团队完成
- 隐形角色（A 的合规否决、I 的技术输入）被显式登记到 CIEU

---

## 5. 影响评估 + 必须同步修改的文件清单

### 5.1 硬依赖（必须改，否则系统自相矛盾）

| 文件 | 修改内容 | 责任 |
|---|---|---|
| `governance/INTERNAL_GOVERNANCE.md` | §决策权限层级整段重写 + 新增 RAPID 角色职责 | Secretary |
| `governance/WORKING_STYLE.md` 第七条 | 保留反事实格式，加一句"R 角色产出遵循本条" | Secretary |
| `governance/WORKING_STYLE.md` 7.5 (GOV-006 intent 协议) | 原"Level 2/3 directive" → "D≠R 的 RAPID 提案" | Secretary |
| `.ystar_session.json` | 新增 `require_rapid_role_assignment` + `rapid_contract` 顶层字段 | Secretary (Maya 合约审查) |
| `CLAUDE.md` § Board Decision Rules | 增加 RAPID 指向段 | Secretary |
| `agents/CEO.md` / `agents/CTO.md` / `agents/CMO.md` / `agents/CSO.md` / `agents/CFO.md` / `agents/Secretary.md` | 搜全部 `Level 2` / `Level 3` / `L2` / `L3` 字样，替换为"作为 D 的 RAPID 决策" / "作为 A 的 RAPID 决策"语义 | Secretary |
| `.claude/agents/ceo.md` 等 5 个 C-suite + 4 工程师 subagent 定义 | 同上 | Secretary |
| `scripts/record_intent.py` | 新增必填参数 `--rapid-R --rapid-A --rapid-P --rapid-I --rapid-D`；缺失 exit 2 | eng-platform（P） |
| `scripts/check_intents.py` | `--confirm` 时显示 RAPID 五角色和 A 的状态 | eng-platform |

### 5.2 软依赖（文档一致性，可分批补）

- `memory/session_handoff.md`（下次 session boot 时补）
- `reports/proposals/*.md`（历史提案不回写；新提案强制 RAPID 格式）
- `knowledge/{role}/role_definition/task_type_map.md`（各角色自行更新 task 类型的 RAPID 角色归属）
- `BOARD_CHARTER_AMENDMENTS.md`（本 AMENDMENT-005 记录自身是第一个依据）

### 5.3 不改的项目

- `AGENTS.md`（immutable-path，Board 自行编辑）——但 L0-L3 字样在 AGENTS.md 里零出现，这条是零工作量
- `archive/deprecated/*`（历史档案不回写）
- Autonomous Mission 小节（保留原结构，但映射到 RAPID——见 §4 最后一行）

### 5.4 grep 证据（现有 L0-L3 引用扫描）

- `governance/` 下 Level/L 字样：68 处（`INTERNAL_GOVERNANCE.md` 24 / `WORKING_STYLE.md` 41 / 其他 3）
- `agents/*.md`：CEO/CTO/CMO/CSO/CFO/Secretary 6 个文件有引用
- `reports/experiments/*`：pilot 报告含 L0-L3 对比叙事，不回写

---

## 6. 风险与回退

### 6.1 已识别风险

| # | 风险 | 概率 | 缓解 |
|---|---|---|---|
| R1 | RAPID 在某个跨岗位决策下卡住（A 无法明确三态、I 过多导致瘫痪） | 中 | D 有权在 `RAPID_DEADLOCK` CIEU event 后驳回并强制简化；默认 A 池兜底 |
| R2 | 岗位对自己是 R 还是 A 不清楚 → 双 R / 双 D | 中 | `rapid_contract.default_A_by_domain` 提供显式查找表；hook 的 `unique_decider` 约束在执行前 catch |
| R3 | 历史 Level 2/3 intent 在新 schema 下失效 | 高（必然） | 参照 GOV-009 先例：老 intent 自动标 `pre_amendment_005_legacy`，不回溯 |
| R4 | Board 在"Board-as-D" 条目外被错误邀请当 D | 低 | CLAUDE.md 新段落明示 Board 的 D 范围；`rapid_contract` 明确 Board 默认 role |
| R5 | pilot EXP-1 的 4/4 胜出仅覆盖一个决策类型（memory loop 优先级），其他决策类型可能有不同 pattern | 中 | 见 §6.3 回退门 |

### 6.2 回退机制

**回退触发条件（任一）**：
- 连续 3 个 RAPID 决策在 `D` 阶段卡住（CIEU event `RAPID_D_STUCK`）超过该 agent 正常 plan 闭环数 × 2
- Board 明确要求回退
- `hook_enforce_require_rapid_role_assignment` 误拒率 >10%（以 Secretary 周审计为准）

**回退动作**：
1. `.ystar_session.json` `require_rapid_role_assignment.enabled = false`（软下线）
2. 回到 L0-L3 模式：`INTERNAL_GOVERNANCE.md` 保留 L0-L3 历史章节（本 AMENDMENT 不物理删除，只添加新章节 + 标记旧章节 `DEPRECATED after AMENDMENT-005`）——这让回退是一个 feature flag 切换，不是代码 revert
3. 本 AMENDMENT 状态改为 `ROLLED_BACK`，Secretary 起草 AMENDMENT-005b 记录回退原因

### 6.3 再 Pilot 门

本 AMENDMENT 生效后的第 1、5、10 个 RAPID 决策必须由 Secretary 写一份 "RAPID retrospective"（位于 `reports/experiments/rapid_retro_NNN.md`），对比实际效果与 EXP-1 的 4/4 指标。连续 3 份 retro 出现"隐形角色未显式化"或"D 空转"即触发 §6.2 回退。

---

## 7. Board 三个签字位

**签字位 1**：批准用 RAPID 五角色框架替换 L0-L3 作为内部跨岗位决策的 authoritative schema（§1 + §2 + §4）。

☐ APPROVED ☐ REJECTED ☐ APPROVED-WITH-CONDITIONS

**签字位 2**：批准 §3.1-§3.4 的具体 diff（`INTERNAL_GOVERNANCE.md` 重写 / RAPID 角色职责新增 / `.ystar_session.json` 增加 `require_rapid_role_assignment` + `rapid_contract` / `CLAUDE.md` 段落增补）。

☐ APPROVED ☐ REJECTED ☐ APPROVED-WITH-CONDITIONS

**签字位 3**：授权 Secretary 按 §5.1-§5.2 清单逐项同步全部硬依赖与软依赖文件，并在 `BOARD_CHARTER_AMENDMENTS.md` 追加 AMENDMENT-005 条目。 `scripts/record_intent.py` 修改委派给 eng-platform 作为 P 角色执行。

☐ APPROVED ☐ REJECTED ☐ APPROVED-WITH-CONDITIONS

**Board 签字**：________________________ **日期**：__________________

---

## 8. 引用来源

**外部框架**：
- [Bain & Company — RAPID Decision-Making](https://www.bain.com/insights/rapid-decision-making/)
- [Mindtools — Bain's RAPID Framework](https://www.mindtools.com/av8ceid/bains-rapid-framework/)
- [Bridgespan — RAPID for Nonprofits](https://www.bridgespan.org/insights/nonprofit-organizational-effectiveness/rapid-decision-making)
- [Asana — RAPID Decision Making (2025)](https://asana.com/resources/rapid-decision-making)
- [Uncertainty Project — RAPID tool](https://www.theuncertaintyproject.org/tools/rapid-framework)

**内部证据**：
- `reports/proposals/external_framework_survey.md` §3.4 (RAPID 分析 + §1 表格 L0-L3 → RAPID 映射推荐)
- `reports/experiments/exp1_v2_RAPID_fillin.md`（R/A/P/I(CTO) 四段真决策产出）
- `reports/experiments/exp1_v2_RAPID_decision.md`（I(CEO) + D 段 + pilot 4/4 自评）
- `knowledge/ceo/feedback/no_human_time_dimension_in_agent_frameworks.md`（硬约束来源）

**Hard constraint 遵守声明**：本提案全文不含人类时间维度（N天/N小时/N周/quarterly/deadline 等）。一切进度以 intent completion 闭环数、CIEU event count、causal chain depth 计量。
