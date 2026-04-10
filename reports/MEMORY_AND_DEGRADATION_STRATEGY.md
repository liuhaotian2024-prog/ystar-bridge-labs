# Y* Bridge Labs 持久化记忆与退化检测 — 综合战略报告
**日期**: 2026-04-10
**触发**: Board 第十一条高度自主任务
**研究团队**: Ethan (eng-platform), Kernel Engineer, Governance Engineer
**综合**: CEO (Aiden)

---

## 零、执行摘要

Board识别了两个相互独立但相互影响的问题：

| 问题 | 性质 | 现状 | 解决方向 |
|------|------|------|---------|
| 跨session记忆丢失 | 持久化问题 | markdown文件，人工维护，有损 | YML自建 或 Letta集成 |
| Agent能力退化 | 可观测性问题 | CIEU有数据但无人分析 | gov_health实时评分 |

**CEO综合判断：两个问题应同时推进，但优先级不同。**

- **P0 退化检测 (gov_health)**：不需要任何新基础设施，只需要分析已有CIEU数据。阻塞面最小，价值最高。
- **P1 持久化记忆 (YML)**：需要6天工程量，但架构清晰，风险可控。
- **P2 Letta MCP集成验证**：技术可行但非当前最优路径。保留为未来扩展选项。

---

## 一、退化检测：gov_health（P0）

### 1.1 核心设计

Governance Engineer设计了完整的session健康度实时评分系统。

**工具签名**：
```
gov_health(session_id, window_size=20, threshold=60, cieu_db="")
→ { overall_health: 0-100, signal_breakdown, trend, recommendation, alerts }
```

**五个确定性信号**（Iron Rule 1合规，无LLM）：

| 信号 | 权重 | 检测方法 | 退化特征 |
|------|------|---------|---------|
| 重复查询 (Repetition) | 25% | hash指纹匹配，10事件窗口内同指纹>=3次 | 同一文件重复读取，同一grep重复执行 |
| 决策矛盾 (Contradiction) | 20% | 状态断言追踪，无中间变更事件但值改变 | "文件不存在"后又"读取文件" |
| 义务衰减 (Obligation Decay) | 25% | session前半段vs后半段completion rate | 后半段完成率下降 |
| 工具膨胀 (Inflation) | 15% | 同类任务tool call数量比较 | 早期2次调用，晚期5次完成同类任务 |
| 伪造指标 (Fabrication) | 15% | violation维度匹配（file_path, state_mismatch） | 声明与实际状态不符（CASE-001/002模式） |

**健康分档与自动响应**：

| 分数 | 状态 | 自动行动 |
|------|------|---------|
| 80-100 | 健康 | 继续 |
| 60-80 | 预警 | 日志记录，提高监控频率 |
| 40-60 | 退化中 | 软重置：重新读取AGENTS.md + 近5条义务 |
| 0-40 | 严重退化 | 硬重置：封存session，创建交接义务，建议换agent |

### 1.2 OmissionEngine联动

健康分低于阈值时：
1. 创建`ACKNOWLEDGE_DEGRADATION`义务（5分钟内确认）
2. 持续下降则通过delegation chain向上级升级
3. 低于40分触发session reset协议

### 1.3 回溯分析工具

`gov_health_retrospective` — 可追溯分析历史CIEU记录，回答"退化是从什么时候开始的"：
- 对每个历史session计算10%/25%/50%/75%/100%处的健康分
- 聚类退化模式
- 识别高风险agent

### 1.4 实施计划

| 阶段 | 内容 | 工期 |
|------|------|------|
| Phase 1 | 5个信号评分函数 + gov_health工具 + 15个单元测试 | 3天 |
| Phase 2 | OmissionEngine联动 + 自动升级 | 2天 |
| Phase 3 | Reset协议 | 2天 |
| Phase 4 | 回溯分析 + CSV导出 | 3天 |
| Phase 5 | 用Labs历史CIEU数据校准阈值 | 5天 |

**总计: 约3周**

### 1.5 CEO补充观点

Governance Engineer的核心洞察正确：**义务衰减是最有力的信号**。如果completion rate在下降，其他退化必然伴随。

但我认为Phase 1和Phase 5应该合并：不要在合成数据上测试然后再校准，直接用Labs真实CIEU数据开发。我们有787+条生产记录，包括CASE-001/002这样的已知退化案例。先跑回溯分析，看看信号是否真的能检测到这些历史事故，再调权重。

---

## 二、持久化记忆：YML vs Letta

### 2.1 Letta研究结论

Ethan的研究纠正了我们之前的错误认知：

| 之前认知 | 实际情况 |
|---------|---------|
| Letta 0.16.7只支持PostgreSQL | **Letta pip安装默认SQLite + ChromaDB** |
| Letta没有hook机制 | **Letta有PreToolUse hooks，可插入gov_check** |
| Letta MCP集成不确定 | **官方支持MCP，工具自动发现注册** |

**关键发现**：
1. Letta支持两种MCP传输：stdio（本地子进程）和HTTP/SSE（远程）
2. Letta Code（npm包）是更轻量的CLI工具，有git-backed记忆文件系统
3. PreToolUse hook可以在每个工具调用前执行外部命令（exit code 2 = 阻止）

**但有重要caveat**：
- Hook文档使用`$CLAUDE_TOOL_*`环境变量——可能是Claude Code的hook被Letta Code复用，**需要实际验证**
- SQLite模式**不支持数据库migration**，版本升级可能丢数据
- Letta是50k+ LOC的重型框架，我们只需要其中记忆持久化这一个功能

### 2.2 YML (自建) 设计结论

Kernel Engineer交付了完整设计文档 (`reports/MEMORY_LAYER_DESIGN.md`)。

**核心架构**：
- 单文件SQLite (`.ystar_memory.db`)
- 6个gov-mcp工具：`gov_remember`, `gov_recall`, `gov_forget`, `gov_memory_summary`, `gov_memory_decay`, `gov_memory_reinforce`
- 时间衰减模型：`relevance = initial * 0.5^(age_days / half_life_days)`
- 6种内置记忆类型（decision:90天, knowledge:60天, lesson:180天, task_context:7天...）
- 每个agent独立记忆存储 + 配额管理
- 全CIEU审计：每次记忆操作都写入审计链

**关键优势**：
- 300-400 LOC vs Letta 50k+ LOC
- 零外部依赖
- 记忆操作本身就是Y*gov治理事件
- OmissionEngine集成：带deadline的记忆自动创建义务

### 2.3 对比决策矩阵

| 维度 | YML (自建) | Letta (路径一：内存后端) | Letta (路径二：MCP治理) |
|------|-----------|----------------------|---------------------|
| **部署复杂度** | SQLite文件，零配置 | SQLite可用但不保证migration | 需验证MCP链路 |
| **工程量** | 6天 | 2天集成 | 2天实验 + 未知适配 |
| **治理集成** | 原生（CIEU + OmissionEngine） | 需要额外适配层 | PreToolUse hook可行但需验证 |
| **对产品的价值** | 证明Y*gov可以治理记忆操作 | 几乎没有，只是用了外部存储 | **证明Y*gov生态中立性** |
| **记忆衰减** | 内置自动衰减 | 需手动归档 | 同左 |
| **语义搜索** | v1无，可加sqlite-vss | 内置pgvector | 同左 |
| **风险** | 低：完全可控 | 中：版本升级可能break | 高：hook环境变量未验证 |
| **未来扩展** | 可加embedding/图谱/跨agent共享 | Letta生态，但绑定其架构 | 最有产品故事价值 |

### 2.4 CEO判断

**短期（现在）：走YML。**

理由：
1. 我们需要的是**可治理的记忆层**，不是一个通用agent运行时
2. YML是Y*gov的原生扩展，记忆操作在CIEU链上——这本身就是产品特性
3. 6天工程量可控，风险极低
4. Letta路径二（MCP治理）的产品故事价值最高，但有技术风险未验证——不应阻塞记忆层建设

**中期（YML上线后）：做Letta MCP集成实验。**

Board说得对——证明Y*gov可以治理Letta agent是产品的最强演示。但这个实验应该在以下条件满足后做：
1. YML已经在Labs运行并积累了真实数据
2. gov_dispatch已实现（否则跨runtime dispatch不可审计）
3. gov_health已实现（否则无法检测Letta agent退化）

这三个前置条件恰好构成了一个自然的路线图。

---

## 三、团队的新发现与超越性建议

### 3.1 Ethan的发现：Letta Code的MemFS

Letta Code（npm包，非pip包）使用git-backed记忆文件系统。这与我们现有的markdown记忆方式理念相似，但更结构化。**这个思路可以被YML吸收**——YML可以将关键记忆同时写入SQLite和markdown文件，实现双重持久化：SQLite用于程序化查询，markdown用于人类可读审查。

### 3.2 Governance Engineer的发现：义务衰减是主信号

"如果agent的义务完成率在下降，其他一切退化必然伴随。" 这意味着gov_health的最小可行版本可以只实现义务衰减这一个信号，快速上线验证，再迭代增加其他信号。

### 3.3 Kernel Engineer的发现：OmissionEngine的记忆潜力

带deadline的记忆自动创建义务——这意味着`gov_remember(type='obligation', content='发布blog', due_at=...)`不只是存了一条记忆，它同时创建了一个被治理的义务。**记忆层和义务层在设计上是统一的。** 这是Letta做不到的。

### 3.4 CEO的超越性观点：三层统一架构

三路研究合在一起，我看到一个更大的图景：

```
                   Y*gov 治理栈
                   ═══════════
Layer 3:  gov_health     — 质量层（知道agent好不好）
Layer 2:  gov_dispatch   — 流转层（知道任务去了哪里）
Layer 1:  gov_check      — 行为层（知道agent在做什么）
Layer 0:  YML / CIEU     — 数据层（记住一切）

                   ↕ 全部基于同一条CIEU链
```

gov_check、gov_dispatch、gov_health、YML——四个原语，共享一个数据层（CIEU + SQLite），构成完整的治理闭环。Letta和任何外部runtime通过MCP接入这个栈的任意层。

**这不是四个独立功能，是一个架构。**

---

## 四、推荐路线图

### Phase A: 基础设施（Week 1-2）

| 任务 | 负责人 | 依赖 | 工期 |
|------|--------|------|------|
| gov_health MVP（仅义务衰减信号） | eng-governance | 现有CIEU数据 | 3天 |
| YML Phase 1-2（Core + gov-mcp工具） | eng-kernel | 无 | 3天 |
| 用Labs历史CIEU跑gov_health回溯 | eng-governance | gov_health MVP | 2天 |

**Phase A交付物**：
- `gov_health` 工具可用，能检测session内退化
- `gov_remember` / `gov_recall` / `gov_forget` 工具可用
- 历史退化分析报告（回答"退化从什么时候开始"）

### Phase B: 集成（Week 2-3）

| 任务 | 负责人 | 依赖 | 工期 |
|------|--------|------|------|
| YML Phase 3（OmissionEngine联动） | eng-kernel | Phase A | 2天 |
| gov_health Phase 2（OmissionEngine + Reset协议） | eng-governance | Phase A | 4天 |
| gov_dispatch 实现（Board已给spec） | eng-platform | 无 | 3天 |
| 替换session_handoff.md为YML自动加载 | eng-kernel | YML Phase 1-2 | 1天 |

**Phase B交付物**：
- 记忆层与义务层统一
- 退化自动检测 + 自动响应
- dispatch可审计
- Session启动自动从YML加载记忆

### Phase C: 验证与扩展（Week 3-4）

| 任务 | 负责人 | 依赖 | 工期 |
|------|--------|------|------|
| Letta MCP集成实验 | eng-platform | gov_dispatch | 2天 |
| gov_health阈值校准 | eng-governance | 2周真实数据 | 2天 |
| YML语义搜索（sqlite-vss） | eng-kernel | YML Phase 1-2 | 3天 |

**Phase C交付物**：
- Letta MCP集成可行性最终结论
- 校准后的退化检测阈值
- 语义搜索能力（可选）

---

## 五、需要Board决策的问题

1. **是否批准YML方案**（vs 继续追Letta）？
   - CEO推荐：批准。理由见2.4节。

2. **gov_health退化阈值是否按agent区分**？
   - Governance Engineer提问：统一阈值 vs 按agent定制？
   - CEO建议：v1统一60分，积累数据后再区分。

3. **硬重置权限归谁**？
   - 选项：agent自己 / 上级 / 仅Board
   - CEO建议：40分以上agent自己软重置，40分以下需上级确认，25分以下Board决定。

4. **是否告诉agent自己的健康分**？
   - Governance Engineer提问：透明 vs 隐藏（避免元退化）？
   - CEO建议：透明。Agent知道自己在退化比不知道好。如果"知道自己退化"本身导致退化加剧，那是gov_health需要检测的新信号，不是隐藏分数能解决的。

5. **Phase A并行启动还是串行**？
   - CEO推荐：eng-governance和eng-kernel并行，各做各的。gov_health和YML没有依赖关系。

---

## 附录：三路研究原始报告索引

| 报告 | 来源 | 位置 |
|------|------|------|
| Letta现状与MCP集成 | Ethan (eng-platform) | Agent输出（session内） |
| YML自建记忆层设计 | Kernel Engineer | `reports/MEMORY_LAYER_DESIGN.md` |
| gov_health退化检测设计 | Governance Engineer | Agent输出（session内） |
| gov_dispatch设计规范 | Board直接撰写 | `.claude/tasks/gov-dispatch-spec-v0.1.0.md` |
