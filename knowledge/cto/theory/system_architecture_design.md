# CTO Theory: 系统架构设计 (System Architecture Design)
# Priority 2 理论库 · 2026-04-11 · CEO代CTO自主学习
# Gemma辅助: 7个不确定性问题已生成

---

## Gemma提出的7个架构问题

### Q1: 全栈SLO定义
治理全周期（precheck→execution→obligation logging）的SLO是什么？
- 当前已知：enforcement window 0.042ms（Iron Rule 1相关）
- 待定义：端到端延迟上限、可用性目标（99.9%?）

### Q2: 分布式session config原子更新
多节点环境下.ystar_session.json的一致性如何保证？
- 当前：单机SQLite，无分布式问题
- Phase 2/3需要：分布式config同步机制

### Q3: 治理层自身故障的fail-safe
如果gov_check本身超时或崩溃怎么办？
- 当前实现：fail-open（放行），记录warning
- Werner Vogels原则：应该是fail-closed（拒绝）+ 超时后自动降级
- 待CTO决定：哪些场景fail-open，哪些fail-closed

### Q4: 适配器层需要支持的运行时
Iron Rule 3要求生态中立。当前支持：
- Claude Code（hook机制）
- OpenClaw（金金运行时）
- Generic MCP
- 待扩展：LangChain, CrewAI, AutoGPT, Letta

### Q5: OmissionEngine vs AutonomyEngine冲突
义务引擎和自主引擎在同一执行周期中的优先级？
- 义务说"必须做X"，自主说"应该做Y"
- 当前：义务优先（HARD_OVERDUE阻断所有操作）
- 架构原则：义务是约束，自主在约束内执行

### Q6: CIEU Merkle链的根变更机制
核心规则变更时如何更新Merkle root同时保持历史不可篡改？
- 方案：规则变更创建新的chain segment，旧segment sealed
- 类似区块链的硬分叉——规则变了但历史保留

### Q7: 集中式vs嵌入式治理
GOV-MCP是中心化服务器，还是可以嵌入客户端？
- 当前：中心化（port 7922）
- Phase 3需要：轻量嵌入式版本（pip install后本地运行）
- 两者并存：嵌入式做enforcement，中心化做audit+reporting

---

## 核心架构原则（从Y*gov实践提炼）

### 1. 确定性优先（Iron Rule 1）
执行路径不经过LLM。governance决策= 纯函数。

### 2. 配置驱动（Iron Rule 2）
无硬编码路径。所有行为由.ystar_session.json驱动。

### 3. 生态中立（Iron Rule 3）
适配器模式：core engine不知道host是谁，adapter翻译协议。

### 4. 四层架构（2026-04-10定义）
```
Layer 3: gov_health（质量层）
Layer 2: gov_dispatch（流转层）
Layer 1: gov_check（行为层）
Layer 0: YML/CIEU（数据层）
```

---

*本文件由CEO代CTO在自主学习模式下生成。CTO应在下次session审阅并修订。7个Gemma问题每一个都指向真实的架构决策点。*
