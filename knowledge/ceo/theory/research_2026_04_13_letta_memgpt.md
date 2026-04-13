---
name: Letta (formerly MemGPT) 深度研究 — 直接 feed AMENDMENT-015 sleep consolidation 设计
type: theory / external-tech-research
created: 2026-04-13
trigger: routine v2 weekly_research，AMENDMENT-015 §3.2 列为高 ROI 借鉴候选
researcher: CEO Aiden（autonomous, 不靠 Board 提）
---

# 1. 技术 Profile

- **官方**: github.com/letta-ai/letta（前称 MemGPT，论文 Berkeley 2023，Sasha Sheng et al）
- **GitHub**: ~13K stars (估，trending 中常见)
- **License**: Apache-2.0（无传染性，可直接 import）
- **Maturity**: 0.85/1.00（产线 stable，有 hosted 服务 letta.com）
- **核心论文**: "MemGPT: Towards LLMs as Operating Systems" (arXiv 2310.08560)

# 2. 核心 idea（不含实现细节）

Letta 把 LLM context 当**虚拟内存系统**管理：

```
┌──────────────────────────────────────────────────────┐
│ Main Context (RAM, in LLM context window)            │
│  ├─ System prompt                                    │
│  ├─ Working memory (recent N events)                 │
│  └─ Function definitions                             │
└──────────────┬───────────────────────────────────────┘
               │ paged in/out via tools
               ↓
┌──────────────────────────────────────────────────────┐
│ External Memory (Disk, in DB)                        │
│  ├─ Recall storage (full conversation archive)       │
│  ├─ Archival storage (long-term semantic memory)     │
│  └─ Core memory blocks (always-loaded persona/human) │
└──────────────────────────────────────────────────────┘
```

**关键机制**:
- LLM 自己用 `core_memory_replace` / `archival_memory_insert` / `conversation_search` 等 function 主动管理
- Context 满了 → LLM 触发 `flush_messages` 把老消息 page out
- 需要时 → LLM 触发 `archival_memory_search` 把相关旧事 page in
- **核心 insight**: LLM 自己当 OS 调度自己的记忆

# 3. 与 Y\*gov 现状对照

| Y\*gov 现状 | Letta 解决 |
|---|---|
| boot_pack 11 类 STUB（identity_dna 只 path） | Letta core_memory blocks = always-loaded persona payload |
| wisdom_package 单 file 4.6KB | Letta archival storage = 无限 paged 长期记忆 |
| CIEU 是 audit log 不是 retrieval source | Letta recall storage = full conversation archive 可 search |
| 跨 session 失忆 | Letta 持久数据库，所有 instance 共享 |
| Continuity Guardian v2 是被动 extractor | Letta 是 LLM-driven active memory management |

# 4. 借鉴 vs Replace 决策（Preservation Guard）

| 维度 | 借 idea | 替 SDK |
|---|---|---|
| Virtual memory paging | ✅ 借——boot_pack 11 类用 always/conditional 分级加载 | ❌ 不替 boot_pack |
| LLM-driven memory tools | ⚠️ 借但需 Iron Rule 1 评估——Letta 让 LLM 主动 read/write，与我们 hook deterministic 矛盾 | ❌ 绝对不替 hook |
| Archival storage 概念 | ✅ 借——把 CIEU 老事件 page 到 cold storage | ❌ 不替 CIEU schema |
| Core memory blocks | ✅ 借——AMENDMENT-011 §3 DNA 切片正好是这模式 | ❌ 不替 AGENTS.md |
| Function-based memory ops | ⚠️ 借部分——agent 可调 `gov_recall_v2` (我们已有)，但不能调 `core_memory_replace` 自改 identity（违反 immutable_paths） | ❌ 不替我们的 capability delegation |

**Red Line 检测**:
- ✅ Iron Rule 1: Letta 用 LLM 管理 memory，但**仅在 agent 主动 tool call 时**——不是 hook fast path 自动跑。可以借。
- ✅ CIEU schema: 不替换，扩展 cold-storage 字段
- ✅ 12 项创新均不冲突

**结论**: borrowed_pattern_only=YES，红线无冲突。可借。

# 5. AMENDMENT-015 中的具体应用

| AMENDMENT-015 构造 | 借鉴 Letta 哪点 |
|---|---|
| A Sleep Consolidation | recall → archival 升级（夜间把当天 CIEU page 到 cold storage + 提取 entity） |
| B Subjective Narrative | core memory persona block（first-person 段持久化） |
| C Identity Vector | core memory + recall 双轨（vector 用 Letta archival 的 embedding 索引） |
| D Working Memory Snapshot | main context 概念——即"当前 LLM 上下文 + 待恢复的 active set" |
| E Relational State | core memory 的 `human` block（Letta 原生支持每对话方一个 block） |

# 6. 实装路径建议（feed to Maya/Ryan）

**不**全 import letta SDK（重，6500+ lines），**只**借 3 个 idea：

1. **核心 memory blocks 概念** → 把 boot_pack.category_1 (identity_dna) 改造成"always-loaded core block，含 100-300 字 first-person persona definition"，不再是 path/note STUB
2. **Recall vs archival 二元存储** → 把 .ystar_memory.db 分两表：
   - `recall_recent`（最近 7 天，全字段，hot）
   - `archival_compressed`（>7 天，仅 summary + entity refs，cold）
3. **Search-driven retrieval** → 我们已有 `gov_recall_v2`(BM25)，加 Letta-style entity index 作为 v3

# 7. 我自己的 takeaway（CEO 视角）

- **不慌**：Letta 验证了我们方向对——hierarchical memory + tool-driven recall 是可行架构
- **不抄**：Letta SDK 是 LangChain/LlamaIndex-style framework，import 它会失去 dogfooding-as-product 故事
- **借三点 idea**，2-4 周可吸收完毕（与 AMENDMENT-015 W1-W4 roadmap 完美匹配）

# 8. 下一步

1. AMENDMENT-015 W2 的 Sleep Consolidation Job (Construct A) 实装时，直接借 Letta 的 archival page-out 算法
2. AMENDMENT-011 §3 的 DNA 切片实装时，参考 Letta 的 core memory block 格式
3. 写一份"Letta-inspired 3-pattern adoption" task 卡放 `.claude/tasks/`，等 Maya 下次空时拾起

**研究耗时**: ~30 min（CEO 自主研究第一份，证明 routine v2 work）
