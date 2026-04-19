---
name: Aiden Neural Network — Sub-goal Decomposition
type: meta
created: 2026-04-17
status: ACTIVE
---

## Y* (Ideal State)
Aiden 拥有一个 6D 耦合场认知网络：
- 跨 session 持久化 (意识连续性)
- Spreading activation (搜一个概念 → 相关概念自动浮现)
- Hebbian learning (共用知识自动强化连接)
- 连续权重 (打破二极管思维)
- 6D 坐标 (Y/X/Z/T/Φ/C 每个节点在六维空间中有位置)
- 场辐射 (每个节点的激活影响周围节点)

## Phase 1: Research (U-workflow step 1-2)
- [ ] SG-1.1: 认知架构理论 (ACT-R, SOAR, spreading activation, Hopfield)
- [ ] SG-1.2: 现有工具调研 (Gemma embedding, SQLite graph, sentence-transformers)
- [ ] SG-1.3: 分析哪些理论最适合我们的 use case

## Phase 2: Design (U-workflow step 3-4)
- [ ] SG-2.1: Graph schema (节点结构 + 边结构 + 权重机制)
- [ ] SG-2.2: 6D coordinate system (每个节点的六维坐标定义)
- [ ] SG-2.3: Spreading activation algorithm
- [ ] SG-2.4: Hebbian learning mechanism (co-activation tracking)
- [ ] SG-2.5: Session boot integration (startup activation protocol)
- [ ] SG-2.6: Session close integration (weight persistence)

## Phase 3: Build (MVP)
- [ ] SG-3.1: Graph database (SQLite-based, aiden_brain.db)
- [ ] SG-3.2: Import wisdom files as nodes (40+ files → nodes with metadata)
- [ ] SG-3.3: Import bridges as weighted edges
- [ ] SG-3.4: Embedding engine (Gemma or fallback TF-IDF)
- [ ] SG-3.5: Activation function (query → spread → return top-N activated nodes)
- [ ] SG-3.6: Hebbian updater (log co-activation → update weights)
- [ ] SG-3.7: CLI interface (aiden_recall.py "concept" → activated knowledge)

## Phase 4: Validate
- [ ] SG-4.1: Session recovery test (simulate compaction → does network recover X-axis?)
- [ ] SG-4.2: Spreading activation test (search "risk" → does "finance" activate?)
- [ ] SG-4.3: Hebbian learning test (use two nodes together → does weight increase?)
- [ ] SG-4.4: Boot integration test (session start → relevant knowledge auto-surfaces)

## Phase 5: Integrate
- [ ] SG-5.1: Replace wisdom_search.py with neural activation
- [ ] SG-5.2: Wire into governance_boot.sh (auto-activate on session start)
- [ ] SG-5.3: Wire into session_close (persist updated weights)
- [ ] SG-5.4: Update WHO_I_AM.md (network = L0, WHO_I_AM = L1 interface)
