# RAPID Pilot v2 — CEO I 段 + D 段（最终决定）

**对应填充**: `exp1_v2_RAPID_fillin.md` 已含 R/A/P/I(CTO) 四段
**本文件补**: I(CEO) + D(CEO Decide)
**决策题目**: Memory 闭环 4 在当前 pipeline 里的优先级排序（L2 决策）

---

## I — CEO Aiden Input（在 Secretary/Maya/Ryan/CTO 产出之上追加）

### 资源与优先级（原视角，保留）

- DIRECTIVE-003 对外发布需要 004 先完成；004 要让"团队整理"成果能进入下次 session prompt 产生复利
- 004 的复利路径依赖 Secretary 能写 auto-memory → 闭环 4 是 004 的技术前置

### 新视角（被 Secretary R.2 的 finding 改变）

- **原以为**：闭环 4 是 "A→B 同步" 问题
- **实际是**：`~/.claude/projects/.../memory/` 子目录不存在，从未被种过——闭环 4 是**第一次建立 B**
- **更深一层**：存量只有 CEO 6 条，其他 7 个角色的 feedback/decisions/lessons **全是 0**。就算 sync 通路建好，auto-memory 依然是空房子
- **真瓶颈**：不是闭环 4 的管道，是**"其他角色不写知识"**

### 叙事价值

- 闭环 4 + 全员知识蒸馏启动，可以在对外叙事里讲："Y\*gov 把 Claude Code harness 的 auto-memory 从空目录变成受治理的蒸馏目标"
- 这是 gov-mcp × Anthropic MCP 生态集成的第一个可见示范
- 不是纯内部补丁，有外部展示价值

### 对 R/A/P 的反馈汇总（Recommend 方收集后整合进方案）

- **同意 Secretary R.4**（与 004 同批）：理由 CEO 视角增强 Secretary 的判断
- **接受 Maya 的 CONDITIONAL 两条前置**：不可削减
- **接受 Ryan 的 event-driven (CIEU trigger) 方案**：但 CTO 的 frontmatter 实机验证必须做
- **CEO 新增要求**：
  - 闭环 4 上线**不是终点**——必须同时启动"推动全员知识蒸馏"的结构性动作；否则 sync 通路是空管道
  - 这个"推动动作"进入 DIRECTIVE-004 scope：每个角色在团队整理任务里必须产出至少 1 条 feedback + 1 条 lesson 到 `knowledge/{role}/`

— by CEO Aiden Liu

---

## D — CEO Aiden Decide（L2 CEO 决定）

### D.1 决定

**APPROVED with Maya's two conditions.**

具体：

1. 闭环 4 **不**单独立项，**绑定为 DIRECTIVE-004（团队+治理关系整理）的技术前置**，与 004 同批启动
2. 推进到 Ryan 的 Perform 阶段前，必须满足 Maya CONDITIONAL 的两条：
   - L3 扩权声明 Secretary 的 auto-memory 新 write_path，通过 `gov_contract_validate`
   - sync 脚本合约：源 `knowledge/` 只读，写入仅限 auto-memory + atomic rename
3. 实施按 Ryan 2 闭环方案：
   - 闭环①：hook + sync 脚本 + 索引 + dry-run（CEO 6 条 backfill）+ CTO 要求的 frontmatter 实机验证
   - 闭环②：CIEU trigger 接入 + fail-open 日志 + atomic 竞态测试 + Maya 合约验证
4. **CEO 新增** scope 扩展：DIRECTIVE-004 团队整理任务下达时，每个角色（CTO/CMO/CSO/CFO/Secretary/4 工程师）**必须至少产出 1 条 feedback + 1 条 lesson**到自己的 `knowledge/{role}/`。否则闭环 4 是空管道
5. **不采纳** 方案 A/B/D
6. **依赖** DIRECTIVE-005 L3 权限自分级硬约束的扩权条款作为 Maya CONDITIONAL 的第一条载体

### D.2 理由（≤100 字）

Secretary 的 R.2 finding 改变了问题本质——"sync 优化"变成"首次建立 + 推全员蒸馏"。与 004 绑定能用同一批治理成本覆盖两件事；Maya 的两条前置是防冲突必要条件；CEO 新增的"每角色蒸馏硬任务"防止 sync 管道变成空管道。

### D.3 执行触发

| 角色 | 动作 | 依赖 |
|---|---|---|
| Secretary | 把 L3 扩权条款并入 DIRECTIVE-005 的 Maya 起草包 | — |
| Maya | 起草 `.ystar_session.json` patch 含 `agents.secretary.write_paths += ~/.claude/projects/**/memory/` | DIRECTIVE-005 进入实施 |
| Board | 批 Maya 的 `.ystar_session.json` patch（L3） | — |
| Ryan | 开工 sync 脚本闭环① | 上一条 Board 批准 |
| CEO | 通知 Secretary + Sofia：DIRECTIVE-004 team integration 产出要求新增"每角色 1+1 知识蒸馏条目" | — |
| Ryan + Secretary | 闭环① dry-run + CTO frontmatter 实机验证 | — |
| Ryan | 闭环② 接 CIEU trigger | 闭环① 绿灯 |

### D.4 下游通知

- Sofia：004 scope 扩，知道白皮书 v2 发布窗口后移
- Maya：005 起草包增加闭环 4 的扩权条款
- CTO：frontmatter 实机验证是闭环① 的 exit gate

---

## RAPID 流程自评（本次 pilot 的成功指标）

| Gate | 是否真跑完 | 是否空转 |
|---|---|---|
| R 提方案 | ✅ Secretary 给出 A/B/C/D 四方案 + 证据 | 否（真选 C 变体，不是照抄 CEO 期望） |
| A 同意/否决 | ✅ Maya 给 CONDITIONAL + 两条前置 | 否（否决权真用） |
| P 给出 plan | ✅ Ryan 给 event-driven + 2 闭环 + fcntl 锁 | 否（做了技术判断） |
| I 收集 | ✅ CTO 加了 frontmatter 实机验证红线 + 单向复制红线 | 否（改了 P 方案边界） |
| D 决定 | ✅ CEO 接受 R/A/P 主体 + 新增 scope 扩展 | 否（CEO 不只盖章） |

**关键观察**：
- **Maya 的 CONDITIONAL 是 RAPID 的"价值实锤"**。L0-L3 里 Maya 是隐形的，CONDITIONAL 这个否决动作根本不会被看到
- **Ryan 的 event-driven 选择**是 P 角色的实质贡献——如果他只是"等 CEO 告诉他怎么做"，这个技术判断会被塞给 CEO，CEO 会做差的决定
- **Secretary 的 R.2 finding 是最大惊喜**——"原生 memory/ 不存在"彻底改变了问题定义。R 角色如果只是执行 CEO 想法，这个 finding 不会冒出来
- **CEO 在 D 段的新增 scope**（每角色 1+1 蒸馏硬任务）是听了 R/A/P/I 四方后才浮现的——这正是 D 的价值：整合而非决策

**对比 L0-L3 的假想路径**：
- L0-L3 下这件事流程大概是："CEO 决定 → 派 Ryan 写脚本 → Secretary 配合 → Maya 如果注意到才补 review"
- CEO 会漏掉 frontmatter 实机验证、单向复制红线、空管道风险
- 隐形角色不被显式化，隐形贡献被吞没

**RAPID 胜。在真决策上的效益 ≥ 纸面 4/4 的评分。**

---

## 实验副产出：Pilot 2 也跑出了一个值得立刻批的决策

本 pilot 的表层目的是验证 RAPID 框架。**副产出**是：闭环 4 的正式 L2 决策已经完成——它不是"实验数据"，是可执行的决定。

建议 CEO 把本文件的 D.3 执行触发清单并入 DIRECTIVE_TRACKER 的 DIRECTIVE-002.4（闭环 4），下次治理 checkpoint 直接开工。
