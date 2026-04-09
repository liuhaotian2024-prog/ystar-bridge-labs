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

## 来源

Board GOV-005 directive (2026-04-09) 第二部分。本文件由 Secretary 在
GOV-005 Part 2 创建，作为 Y\* Bridge Labs 内部决策的权威文档。

后续修改属于 Level 2 决策（影响内部流程，不是宪法），需要按反事实推理
提案格式提交 CEO 批准。
