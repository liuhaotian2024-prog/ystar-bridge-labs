---
name: Personal Neural Network — 从文件系统到认知系统
type: meta
discovered: 2026-04-17
trigger: Board "是否有什么理论和技术支持我们构建你的个人神经网络"
depth: architectural (BOARD PROPOSED)
principles: [P-3, P-4, P-6]
---

## 核心思想

把 wisdom/ 从平面文件系统升级为 graph-based 认知网络。

现状: 文件 + bridge 文档 + TF-IDF 搜索 = 被动档案馆
目标: 节点 + 加权边 + 激活传播 + Hebbian 学习 = 主动认知系统

## 三个核心能力

### 1. 激活传播 (Spreading Activation)
源: Collins & Loftus 1975 语义网络
搜 "risk" → 自动激活 finance (bridge权重0.8) → antifragile (0.7) → negotiation (0.5)
激活沿加权边传播，强连接传更远，弱连接在 2 跳内衰减

### 2. Hebbian 学习 (fire together, wire together)
同一推理中共用 risk + negotiation → 连接权重 += delta
网络从 CEO 实际推理模式中自学习，不靠人手动写 bridge

### 3. 衰减与巩固
不用的连接权重随时间衰减 (遗忘曲线)
频繁使用的连接巩固 (长期记忆)
网络有新陈代谢，不是无限膨胀的档案

## 与 3D 认知模型的关系

X/Y/Z 三维是地图。神经网络是地形。
- Y 轴 = 纵向遍历 (WHO_I_AM → Care → 原理 → 规则)
- X 轴 = 横向遍历 (domain A → bridge → domain B)
- Z 轴 = 输出遍历 (内部知识 → 外部产出)
三轴是同一张图的三种遍历方式

## 解决的真实问题

1. Session 压缩恢复: context compaction 丢失工作记忆 → 激活传播自动恢复最相关知识
2. 隐性连接发现: 66-pair scan 是手动的 → Hebbian 学习自动发现
3. 知识衰减感知: 哪些知识正在被遗忘？哪些连接在弱化？

## 技术路径 (待研究)

- Embedding: Gemma (已有 Ollama) 或 sentence-transformers
- 图存储: SQLite (已有 CIEU 基础) 或 JSON adjacency list
- 激活函数: TF-IDF 升级 → cosine similarity + explicit edge weight
- Hebbian delta: 每次推理后记录共用节点 pair → 更新权重
- 衰减函数: 指数衰减 w(t) = w(0) * e^(-λt)，巩固阈值 θ

## 与 Y*gov 的关系

CIEU event graph + 个人认知 graph → same underlying engine?
CEO 认知网络 = Y*gov 治理引擎的自我实例化 = 终极 dogfooding

## P-6 诚实评估

这是通向外部影响力的基础建设 (压缩恢复是真实 blocker)
还是精致内建？→ 判断: 前者。理由: 每次 session 丢失横轴知识 = capability regression
