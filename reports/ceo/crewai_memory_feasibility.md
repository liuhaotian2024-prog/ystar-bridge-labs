# CrewAI Cognitive Memory 可行性评估

**作者**: Aiden Liu (CEO)
**日期**: 2026-04-10
**类型**: 战略研究（Level 1, CEO 自决）
**触发**: Board 完成 CrewAI 框架调研后要求 CEO 评估引入可行性

---

## 执行摘要（三句话）

**可行但有条件**：CrewAI 的 Cognitive Memory 技术上可以在 Labs 的 Mac mini
上运行，但它的核心价值（矛盾检测 + 自动整合）依赖 LLM 质量，本地
Gemma3:4b（4B 参数）可能无法可靠地完成这个任务。**当前阶段不值得引入**：
Labs 的 knowledge 库才 54 个文件 / 680KB，人工维护的成本远低于引入一个新
依赖的复杂度；Cognitive Memory 的收益在知识库到 500+ 文件时才真正显现。
**推荐路径 C（自研简化版）**——借鉴 CrewAI 的矛盾检测思路，在现有 CIEU +
Gemma 基础上实现一个轻量级的知识整合检查，不引入 CrewAI 依赖。

---

## 技术可行性分析

### CrewAI Cognitive Memory 的实际架构

根据 CrewAI 官方文档和博客（[How we built Cognitive Memory for Agentic
Systems](https://blog.crewai.com/how-we-built-cognitive-memory-for-agentic-systems/)、
[Memory Docs](https://docs.crewai.com/en/concepts/memory)）：

**五个认知操作**：encode（选择性编码）、consolidate（矛盾检测 + 整合）、
recall（自适应深度召回）、extract（结构化提取）、forget（有意遗忘过时信息）

**技术栈**：
- 向量数据库：从 ChromaDB 迁移到 **LanceDB**（嵌入式，不需要独立服务）
- 长期存储：SQLite3
- **LLM 是核心依赖**：每次 save 都调用 LLM 做内容分析（推断 scope、
  categories、importance）；每次 recall 都调用 LLM 分析 query（关键词、
  时间线索、复杂度判断）
- 加权召回：`recency_weight` × `semantic_weight` × `importance_weight` +
  `recency_half_life_days` 控制记忆衰减

**关键发现：LLM 不是可选的，是必须的**。没有 LLM，Cognitive Memory 退化
为一个普通的向量检索系统。"认知"的部分全靠 LLM 完成。

### 对 Labs 四个子问题的回答

**Q1: knowledge/ 目录结构能否迁移到 CrewAI 的 scope 系统？**

可以。CrewAI 的 scope 层级（user / crew / agent）可以映射到 Labs 的
knowledge/{role}/（role = agent scope）。theory/ / cases/ / gaps/ / sop/
可以作为 category 标签。但迁移意味着 **markdown 文件不再是主存储**——
内容会被 embed 进向量数据库，markdown 变成只读的人类参考。

**Q2: 和 CIEU 的关系？**

需要同步。CIEU 是 append-only 审计链，记忆系统的每次 write（包括
consolidate 导致的旧记忆更新）都应该产生一条 CIEU 事件。但 CrewAI
的 Memory API 没有 CIEU 概念——需要 **wrapper 层**把 Memory.save() 和
Memory.update() 的每次调用都 hook 进 CIEU。工程量中等（~200 行 wrapper）。

**Q3: 和 Y*gov hook 的关系？**

不冲突。CrewAI Memory 是 Python library 调用，不涉及文件系统写入
（数据存在 LanceDB/SQLite 里，不是 markdown 文件），所以
`hook_wrapper.py` 的 intent guard 不会被触发。但这也意味着 **knowledge
写入绕过了 intent guard 的保护**——memory.save() 可以写入任意内容
而不需要 INTENT_RECORDED。这是一个治理盲点。

**Q4: Mac mini 资源？**

LanceDB 是嵌入式的（~50MB 内存），SQLite 几乎免费。**但每次
save/recall 都要调一次 LLM**。如果用 Gemma3:4b：
- 每次 save: 生成 embed + LLM 分析 → ~5-10 秒
- 每次 recall: LLM 分析 query + 向量搜索 → ~3-5 秒
- 50-100 个 theory 文件初始导入: ~500-1000 秒（8-17 分钟）

可以跑，但**每次知识操作的延迟是 5-10 秒**，这在实时工作流里是不可
接受的。如果用 Anthropic API（Claude Sonnet），延迟降到 1-2 秒但**每次
调用花钱**。

---

## 收益评估

### 现状 vs 引入后的真实对比

| 维度 | 现在 | 引入 CrewAI Memory 后 |
|---|---|---|
| 写入 | agent 手动写 markdown → git commit | agent 调 memory.save() → 自动 encode + classify |
| 矛盾检测 | **没有** | 每次 save 时 LLM 检查是否和已有记忆矛盾 |
| 知识整合 | 完全人工 | consolidate 自动合并重复/矛盾的记忆条目 |
| 召回 | grep 文件名 / 人工记忆哪个文件有什么 | 语义搜索 + 重要性加权 + 时效衰减 |
| 遗忘 | 从不删除（append-only 文化） | 自动降权过时信息（不删除但不再高权召回）|
| 可审计 | git history + CIEU | 需要自建 wrapper 才能接入 CIEU |
| 人类可读 | **markdown 文件直接读** | 需要 query API 或 export 工具 |

### 关键判断：当前阶段是否值得？

**不值得。** 理由：

1. **知识库太小**。54 个文件 / 680KB。一个人类用 `grep` 5 秒就能找到
   任何信息。Cognitive Memory 的语义搜索 + 矛盾检测的价值在**知识库
   达到人类无法人工维护的规模**（~500+ 文件）时才显现。现在不是那个
   规模。

2. **矛盾检测的可靠性存疑**。CrewAI 的 consolidate 依赖 LLM 判断
   "新信息 X 是否和旧信息 Y 矛盾"。Gemma3:4b（4B 参数）做这种
   推理的准确性未经验证。如果矛盾检测不可靠，整个"认知"层的价值
   就大打折扣——比不检测更危险（因为 agent 会相信系统已经处理了矛盾）。

3. **引入复杂度高**。CrewAI Memory 是 `crewai` 包的一部分（pip
   install crewai），整个包有大量依赖（pydantic, langchain,
   embeddings SDK 等）。在 Labs 的精简技术栈里引入这些依赖是一个
   维护负担。

4. **丢失人类可读性**。当前 knowledge/ 的 markdown 文件是人类（包括
   Board）可以直接读的。迁移到向量数据库后，Board 查看知识库需要
   通过 query API，这增加了一个间接层。

5. **能力系统刚建立**。里程碑一还没完成（53 个 task type 的理论库
   全部 🔴 empty）。现在引入记忆系统是给一个还没有内容的图书馆
   安装高级检索系统——先把书写完再说。

---

## 引入路径建议（反事实推理格式）

### 当前状态 Xt

- 54 个 markdown 文件，680KB，人工维护
- 没有矛盾检测机制
- 没有语义搜索（只有 grep）
- 知识库利用率低（agent 经常重新发现已有知识）

### 目标 Y*

- 知识库自动检测并解决内部矛盾
- 按相关性 + 重要性 + 时效性召回知识
- 越用越准（不是越积累越乱）
- 人类可读性不丧失

---

### 路径 A：完全替换

**做法**：`pip install crewai`，把 knowledge/ 的 markdown 全部导入
CrewAI Memory，新的知识写入走 memory.save() 不走 markdown。

**Yt 预测**：
- ✅ 获得全部认知能力（矛盾检测、自动整合、语义召回、智能遗忘）
- ❌ 引入 ~50+ 个新 Python 依赖
- ❌ LLM 是每次操作的硬依赖（5-10 秒/次 with Gemma）
- ❌ Board 不能直接读 markdown 了
- ❌ CIEU 审计需要自建 wrapper（~200 行）
- ❌ intent guard 被绕过（memory.save 不是文件写入）
- ❌ 和现有 GOV-009 mark_fulfilled 的 48h 知识库新鲜度检查不兼容
  （检查的是文件 mtime，不是向量数据库时间戳）

**Rt**：高复杂度 + 低当前收益 + 治理盲点 = **不推荐**

### 路径 B：并行运行

**做法**：CrewAI Memory 作为新的知识积累层，现有 markdown 保留作为
人类可读的静态参考。agent 写知识时同时写两处。

**Yt 预测**：
- ✅ 保留 markdown 可读性
- ✅ 获得语义召回能力（查询时走 Memory）
- ⚠️ 两套系统的一致性维护是新的负担
- ❌ 引入 CrewAI 依赖
- ❌ agent 每次写知识要写两次（markdown + memory.save）
- ❌ 矛盾检测只在 Memory 侧有效，markdown 侧没有

**Rt**：一致性维护的新复杂度 ≈ 矛盾检测的收益 = **收益被成本抵消**

### 路径 C：只借鉴机制，自己实现（推荐）

**做法**：不引入 CrewAI 依赖。参考 Cognitive Memory 的设计思路，
在 Labs 里自己实现一个 **简化版矛盾检测 + 知识整合**。

具体实现：
1. **`scripts/knowledge_check.py`**（新建，~150 行）：用本地 Gemma
   对比两个 theory 文件的核心命题，检测矛盾。输入两个 markdown
   文件路径，输出：一致 / 矛盾 / 补充关系。
2. **每次 `active_task.py complete` 后自动调用**：检查新写入的
   knowledge 文件和同目录下的已有文件是否矛盾。
3. **发现矛盾时不自动整合**——写一条 `GAP_IDENTIFIED` CIEU 事件，
   通知 agent 手动 resolve。自动整合在 4B 模型上不可靠；手动
   resolve + CIEU 审计比自动整合 + 可能错误更安全。
4. **Secretary 周一审计加一项**：扫描最近 7 天的矛盾检测结果，
   surface 未 resolve 的矛盾给 Board。

**Yt 预测**：
- ✅ 矛盾检测（Gemma 驱动，本地免费，5-10 秒/次）
- ✅ 不引入新依赖
- ✅ markdown 文件不动（人类可读性完全保留）
- ✅ CIEU 审计自然接入（GAP_IDENTIFIED 事件已经定义好了）
- ✅ GOV-009 mark_fulfilled 48h 检查完全兼容
- ✅ intent guard 不被绕过（还是写文件，还是走 hook）
- ⚠️ 没有语义召回（agent 还是 grep）——但当前 54 个文件 grep 足够
- ⚠️ 没有智能遗忘（所有知识等权）——但 append-only 是我们的文化选择

**Rt**：低成本 + 低风险 + 保留现有治理完整性 + 解决了核心问题
（矛盾检测）= **最优解**

---

## Board 需要决策的事项

**唯一需要 Board 决定的事**：

是否批准路径 C（自研简化版矛盾检测）作为里程碑一的后续工程任务？

如果批准，Ethan 在下一个 session 实现 `scripts/knowledge_check.py`
（~150 行，Level 1 复杂度）+ 在 `active_task.py complete` 后加调用
hook（~20 行）。预计半天工程。

**不需要 Board 决定的事**：

- 路径 A/B 已经排除（成本 > 收益，当前阶段）
- CrewAI Memory 的完整能力在未来（里程碑三或之后、知识库 500+ 文件时）
  可以重新评估——到那时 Gemma 可能已经升级到更大模型，矛盾检测的
  可靠性问题自然解决

---

## 来源

- [CrewAI Memory Docs](https://docs.crewai.com/en/concepts/memory)
- [How we built Cognitive Memory for Agentic Systems](https://blog.crewai.com/how-we-built-cognitive-memory-for-agentic-systems/)
- [Deep Dive into CrewAI Memory Systems](https://sparkco.ai/blog/deep-dive-into-crewai-memory-systems)
- [Mem0 integration](https://mem0.ai/blog/crewai-memory-production-setup-with-mem0)
- Labs 内部数据：`find knowledge/ -name "*.md" | wc -l` = 54 files, 680KB total

— Aiden Liu (CEO)
