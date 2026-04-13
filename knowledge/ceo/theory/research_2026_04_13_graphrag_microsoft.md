---
name: GraphRAG (Microsoft) 研究 — Labs RAG v2 升级候选
type: theory / external-tech-research
created: 2026-04-13
trigger: routine v2 weekly_research 第 2 篇，AMENDMENT-015 §3.2 + Jordan RAG v1 (BM25) 升级需求
researcher: CEO Aiden（autonomous, routine-driven）
---

# 1. 技术 Profile

- **官方**: github.com/microsoft/graphrag
- **GitHub**: ~26K stars（Microsoft 原厂）
- **License**: MIT
- **论文**: "From Local to Global: A Graph RAG Approach to Query-Focused Summarization" (Edge et al, 2024, arXiv 2404.16130)
- **Maturity**: 0.80/1.00（产线 stable，有 hosted 服务 graphrag.com）

# 2. 核心 idea（vs 我们 RAG v1）

| 维度 | Labs RAG v1 (Jordan `cfc4760`) | GraphRAG |
|---|---|---|
| 索引 | BM25 + Maya weighted scoring（time×Board×role） | Entity-Relationship graph + community detection (Leiden) |
| Query 模式 | 单文档级 retrieval → top-K | 两种模式：local (entity-neighborhood) + global (community summary) |
| 长 context 处理 | 单文档切片 | 分层 summary tree（leaf → community → global） |
| 因果链 retrieval | 无 | entity 间关系 edge 直接支持多跳推理 |
| 适合场景 | "这条 lesson 怎么写的" | "所有 agent 是怎么协作的 / 今晚所有 amendment 间是啥关系" |

# 3. 对 Labs 的具体价值（dogfooding case）

### 3.1 已实证的 v1 局限
今晚实测：
- 查 `"AutonomyEngine"` → v1 精准返回 autonomy_engine.py ✅
- 查 `"agent peer collaboration"` → v1 返回 CrewAI/LangGraph tech_radar 结果 ✅
- 查 `"what's the relationship between AMENDMENT-012 and AMENDMENT-013 and AMENDMENT-014"` → v1 **无法推理**，只能返回各自 proposal 文件（需人脑合成）

### 3.2 GraphRAG 能解的新用例
- **"本月我们修了哪些 bug 它们之间因果链是什么"** — 需要 commit × lesson × CIEU 的多跳图
- **"哪些 amendment 互相依赖"** — 需要 amendment × amendment edge graph
- **"全公司本周最重要决策 Top-3 + 推导路径"** — 需要 community-level summary
- **"Maya 和 Ryan 合作过哪些 task"** — 需要 agent × task × commit 图

# 4. 借鉴 vs Replace 决策（Preservation Guard）

| 维度 | 借 idea | 替 SDK |
|---|---|---|
| Entity-relationship graph | ✅ 借——上层加 entity extraction pass | ❌ 不替 BM25（BM25 + graph 互补） |
| Community detection (Leiden algorithm) | ✅ 借——对 CIEU events 聚类识别工作流 | ❌ 不直接 import graphrag SDK（重依赖） |
| Hierarchical summary tree | ✅ 借——可用于 priority_brief 多层 target 的进度 rollup | ❌ 不替 priority_brief schema |
| Entity typing | ✅ 借——agent/commit/amendment/skill/lesson 是预定义实体类型 | ❌ 不替 tech_radar catalog |

**Red Line 检测**:
- ⚠️ Iron Rule 1: GraphRAG 用 LLM 做 entity extraction + community summary——**离线 build 阶段**可以用（sleep consolidation job 时段跑），runtime retrieval 是纯 graph traversal（不违 Iron Rule 1）
- ✅ CIEU schema: 不替换，是 consumer
- ✅ 12 项创新均不冲突

**结论**: borrowed_pattern_only=YES，部分借（仅索引构建阶段用 LLM，retrieval 纯确定性），无红线。

# 5. Labs RAG v2 实装路径（feed to Maya/Jordan）

**分两阶段**：

### Phase 1 (4h): Entity Index + Multi-Hop 查询
- 离线 sleep job 跑：
  - 扫全 CIEU + commits + amendments + lessons
  - 提取 entities: agents (Aiden/Ethan/Maya/...) / subsystems (CIEU/OmissionEngine/ADE/...) / artifacts (commits/amendments/skills) / concepts (Iron Rule 1/12 项创新/...)
  - 提取 relations: `Maya` `ship` `commit 2224c60`; `commit 2224c60` `implements` `AMENDMENT-014`; `AMENDMENT-014` `depends_on` `CIEU 5-tuple`
  - 存 SQLite 图表（nodes + edges）
- 在线 query API 加 `gov_recall_v2(query, mode='graph', hops=2)`：图遍历返回相关实体邻域

### Phase 2 (8h): Community Detection + Global Summary
- Sleep job 跑 Leiden algorithm 找 community（如"governance infra repair 群" / "tech radar 扫描群"）
- 每 community 生成 summary（LLM 离线）
- 新工具 `gov_recall_v3(query, mode='global')` 返回 community-level answer（多跳推理型问题）

# 6. CEO 视角 takeaway

- **v1 已满足"找得到 + 语义匹配" 80%**——日常 dogfooding 够用（AutonomyEngine 那次就是 v1 的胜利）
- **v2 的必要性**主要在**"关系类 query"**——我今晚写 AMENDMENT-015 时自己脑子里做"Letta × Mem0 × 我们 boot_pack"的关系整合；未来应该**让 gov_recall_v3 自己输出**这种整合
- **暂不急着做 v2**——AMENDMENT-011/012/013/014/015 还没落完，Phase 2 等 sleep consolidation job (AMENDMENT-015 A) 上了自然顺势跑

# 7. 下一步

1. 写 `.claude/tasks/labs_rag_v2_graph_mode.md` task 卡，等 Q2 (AMENDMENT-015 W4 后) 拾起
2. 本 research 结论进 AMENDMENT-015 §3.2 的借鉴列表（补 GraphRAG 详情）
3. 今天继续 routine v2 余项：AutoGen 0.4 研究（多 agent 编排）

**研究耗时**: ~25 min（第 2 篇，routine v2 上手顺）
