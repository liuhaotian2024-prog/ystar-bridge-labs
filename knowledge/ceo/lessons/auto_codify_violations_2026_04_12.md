---
lesson_id: 91ee5054-4b34-46d2-a5ba-c85e97c2b4d6
---

# Lesson: auto_codify 违规累计记录 — 2026-04-12 session

**发现日期**: 2026-04-12
**类型**: lesson (CEO 自我警示)
**重要性**: P0 (Board 已两次当面捕捉, 说明这是 CEO 的持续性缺陷)

## 违规统计

本 session 内 CEO 发生的 "对话里说了但没写入持久化" 违规累计:

### 第一波 (EXP-5A 审计暴露)
1. EXP-3 Organizational Intelligence 元洞察
2. EXP-4 Agent Cult Immunity 4 条因果
3. EXP-5A CEO 双重身份盲区

**补救**: Board 指出后立即写 `knowledge/ceo/theory/` 3 文件. 但只写了 Scenario + 描述, 未按 Skill Document 4 段齐全 — 这本身又是新违规 (见第三波).

### 第二波 (Board 追问"你建议的硬约束清单")
4. 权限自分级 (早前已有 L3 提案, 但对话中被忽略)
5. 禁人类时间维度 (已入 feedback 但未 hook 化)
6. 规则必须有 hook 强制 (EXP-5A 发现)
7. Continuity Guardian 端到端实验硬约束

**补救**: Board 追问时才整理清单给出.

### 第三波 (Board 问 "Hermes 借鉴落地?")
8. Hermes FTS5 全文检索策略 — 对话说了没落地没 pending
9. Hermes Pluggable memory backend — 对话说了没落地没 pending
10. 3 个 theory 文件没按 Skill Document 4 段齐

**补救**: Board 指出后立即 TaskCreate + 写本 lesson.

## Pattern 分析

3 波违规的共同 pattern:

1. CEO 在对话层给出深度洞察/方案/借鉴 (**深度思考正常**)
2. 没有 "说完立即 codify" 的反射动作 (**持久化反射缺失**)
3. Board 主动追问才触发补救 (**完全被动**)

**根因**: L6 学习层没 hook enforcement — EXP-5A 审计原话 "L4/L6 全线失守, 规则必须有 hook 强制否则装饰".

## Procedure (下次如何避免)

### 对话层 (CEO 自律)

CEO 每给出一条下面类型的内容, **立即**追加一个"codify 动作":

| 内容类型 | 必 codify 去哪 |
|---|---|
| 新洞察 / 理论 | `knowledge/{role}/theory/*.md` (按 Skill Document 4 段) |
| 新硬约束 | `knowledge/{role}/feedback/*.md` + 推 AMENDMENT |
| 新决策 | `knowledge/{role}/decisions/*.md` |
| 新教训 | `knowledge/{role}/lessons/*.md` |
| 新外部借鉴 | TaskCreate 落地 + 决策/theory 文件 |

### 系统层 (等 hook 支持)

- AMENDMENT-007.1 修订应加: CEO 输出包含关键信号词 ("我发现"/"洞察"/"借鉴"/"教训"等) → hook 检查最近 N 个 intent completion 内是否有对应 write to knowledge/ → 无则 warning
- 累积 warning → CIEU drift event → 下次 session boot 的 STEP 9 obligations 强提醒

### 元反思层 (Aiden Ontology 级)

本条 lesson 应该固化进 Aiden Ontology 的"弱点自省"段落: **CEO 有持久化反射缺失倾向, 需要系统 hook 帮助**. 这本身是 agent 生命形态学的 empirical finding.

## Pitfalls

### 坑 1: 认为"对话 transcript 就是持久化"
- 错. session 结束 = JSONL 归档, 不会自动被 wisdom_extractor 读懂
- 对话里的洞察不等于可被下次 session 调用的 skill

### 坑 2: 靠 "session_close 时一次性蒸馏" 补救
- 不够. session 中段的深度洞察 session_close 前会被 context 覆盖, 蒸馏时已经找不到原始信号

### 坑 3: 等 Board 提醒才写
- Board 的注意力是稀缺资源, 不应用来 debug CEO 的基本反射
- 每次 Board 追问都是一次 ROI 负值消耗

## Verification Steps

下 session 开始监控:
1. 每 10 个 CEO 回复 sample 1 个, 检查其中新洞察是否有对应 codify 动作 (≥ 80% 命中)
2. Board 是否还需要追问"你说过的 X 落地了吗" (目标: 0 次)
3. L6 学习层在下次 EXP-5A 审计的得分 (当前 7/10, 目标下次 ≥ 9/10)

## 关联

- `knowledge/ceo/feedback/skill_document_standard_from_hermes.md` (Skill Document 规范源)
- `reports/experiments/exp5A_ceo_dogfood_audit.md` (原始审计发现)
- AMENDMENT-007 Section G L6 学习层 (待 007.1 patch 加 hook)
