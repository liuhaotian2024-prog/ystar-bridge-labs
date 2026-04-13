# Feedback: Skill Document 模式——借鉴 Hermes Agent

**来源**: Board 2026-04-12 指令"查 Hermes Claw 有什么值得借鉴" + CEO 现场调研发现
**类型**: feedback (设计规范)
**适用**: 全员, 尤其 Secretary (知识蒸馏权责) + CEO (元洞察产出)
**状态**: 立即生效, 作为 `knowledge/{role}/theory/` 和 `knowledge/{role}/lessons/` 的新标准

## 规则

任何"完成复杂任务后的经验产出"（元洞察 / 教训 / 方法论 / 基因）必须按 **Skill Document 模式**写, 不能只写感受或结论:

### Skill Document 标准结构

```
# Skill: <技能名>

## 适用场景
什么样的任务/问题 trigger 加载这份 skill

## Procedure（步骤）
1. 第一步做什么
2. 第二步做什么
...

## Pitfalls（坑）
- 常见错误 1 + 如何规避
- 常见错误 2 + 如何规避
...

## Verification Steps（验证）
怎么判断这次执行是成功的
```

## Why

**Hermes Agent** (Nous Research, MIT, 开源) 发现: 完成复杂任务后写 **Skill Document** 的 agent, 下次遇到同类任务能 **加载 skill 而不是从头重解**. 是 agent "学习" 的 core primitive.

我们今天跑 EXP-3/4/5A/6 产出的 3 条元洞察 (organizational_intelligence / agent_cult_immunity / designer_user_blindspot) **本质是 skill document**, 但:
- 只写了"发现"+"对管理的意义"
- 缺**Procedure**（下次遇到类似情况怎么做）
- 缺**Pitfalls**（容易踩哪些坑）
- 缺**Verification**（怎么验证成功）

这让"元洞察"停在了**描述层**, 没升到**可复用行动层**. Hermes 的 skill document 模式补上这个空缺.

## How to apply

### 立即动作

1. **现有 3 条 `knowledge/ceo/theory/*.md`** 需要补充 Procedure / Pitfalls / Verification 三段——**补充而非重写**
2. 以后任何 CEO / Secretary 写新的 theory / lesson / pattern 文件**必须包含 4 段**（场景 / 程序 / 坑 / 验证）, 否则退回

### 工程配合

- `scripts/session_wisdom_extractor.py` v2 应该**优先蒸馏**有 Skill Document 格式的文件——这些是**可复用知识**, 胜过裸叙述
- 新 session 启动时 Aiden 读 Skill Document 不只是"知道", 是"**下次加载执行**"
- 长期: `.ystar_memory.db` 增加 `memory_type='skill'` 作为一级公民

### Secretary 蒸馏权责扩展

Secretary 的 DNA 蒸馏职责现在包含:
- 扫 `knowledge/*/theory/*.md` 是否符合 Skill Document 格式
- 不符合的主动推 agent 补齐 4 段
- 蒸馏 Board session 的"方法论"部分成 Skill Document 存到对应角色 knowledge/

## 与 Hermes 的差异化

Hermes 的 skill document 用 **LLM 自动生成**. 我们的 skill document 要求:
- **Procedure / Pitfalls / Verification 由 agent 显式写**（Iron Rule 1 精神: 不让 LLM 决定什么是"好 skill"）
- **CIEU 事件作为 verification ground truth**（比 Hermes 靠 LLM 评估更可靠）
- **pluggable interface** preview: 未来 Y*gov 可以把我们的 skill library 暴露给其他 agent 框架（类似 Hermes v0.7.0 的 memory backend plugin）

## 硬约束化路径

- `.ystar_session.json` 可加 `knowledge_schema: {theory_must_have_4_sections: true}`
- hook 在 CEO / Secretary 写 `knowledge/*/theory/*.md` 时检查 4 段结构, 缺段 → warn
- 进入 AMENDMENT-007 (CEO OS) 的 L6 学习层

## 关联

- `knowledge/ceo/theory/organizational_intelligence.md` (待补 4 段)
- `knowledge/ceo/theory/agent_cult_immunity.md` (待补 4 段)
- `knowledge/ceo/theory/designer_user_blindspot.md` (待补 4 段)
- `reports/experiments/exp6_continuity_guardian_lifecycle_integrity_brief.md` v2 修订 (wisdom_extractor 应优先蒸馏 Skill Document)
- Hermes Agent 源: https://github.com/nousresearch/hermes-agent
