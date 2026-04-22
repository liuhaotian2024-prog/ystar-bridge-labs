---
title: Engineer Culture Design — 4 因素叠加产 Maya 类 metacog 主动 surface 行为
type: ceo wisdom (meta)
date: 2026-04-22
m_functor: M-1+M-2 (cross-session/agent culture identity 持续 + governance system upgrade)
trigger: Board 2026-04-22 catch — "Maya 为什么会主动 surface root cause + propose prevention"
related: knowledge/ceo/wisdom/meta/17_meta_rules_from_practice.md, ceo_workflow_enforcement_gap.md, autonomous_loop_algorithm.md, building_aiden.md
---

# Engineer Behavior Quality 不是个体属性, 是 4 因素叠加结果

Wave-1+1.5+2 实证 — 4 engineer 行为质量差异 (Maya 最 metacog, Jordan 最 narrow scope). 差异不是 individual quality, 是 **model × role × culture × prompt** 互动结果. Reproducible 让所有 agent 都像 Maya, 必须复制 4 因素.

## 因素 1 — 模型层 baseline (Anthropic Claude Constitutional AI 训练)

Claude 默认偏 reasoning out loud + safety-conscious + root-cause oriented. Constitutional AI 训练 instilled "be helpful honest harmless" 包含主动 surface concerns. 这是免费的 cultural inheritance, 别的 model 不一定有.

**意义**: 选 model 就是选 baseline culture. Claude 适合 Y\*gov 这种 governance + metacog heavy 工作.

## 因素 2 — Role/Domain culture 内化 (governance engineer norm)

Governance engineer 内化 "修 root cause 不只 patch symptom" — governance bug 只 patch 不找 root 一定 recur. `auto_codify_lessons.md` (Board 2026-04-11 永久授权): "同类错误重犯 ≥2 次必 codify 入硬约束" — Maya 内化此 norm, 不愿 fix 的 bug 明天换皮再来, 所以 surface "yaml structural pollution" 类 + 提议 CI lint pre-hook.

跨 engineer 比较 (Wave-1+1.5+2):
- Maya (governance) — 9_REVIEW 4 question framework + word-boundary regex extra fix + CI lint proposal — **最强**
- Ryan (platform) — yaml parser silent drop discovery (unprompted!) + docstring drift + M-3=0 imbalance surface — 强
- Leo (kernel) — 精准 build, IH path leverage, surface 较少 — 中
- Jordan (domains) — 完成 task scope, 较少主动 surface — 较弱

**意义**: governance + platform domain culture 鼓励 metacog surface, kernel + domains 偏 precision execute. 派任务 match role-culture, 不强加.

## 因素 3 — 历史 culture 自塑造 (造工具的人被工具改造)

Maya 写过 `session_wisdom_extractor_v2.py` (EXP-6 红队修订版): 11 sources scan + time/board/role weighted + 红队 20 题 recall+幻觉+诚实度测试. 她造的工具反过来塑造她的工作姿态 — 自检 culture internalized.

**意义**: 让 agent 长期参与造 metacog 工具会 inverse-塑造 agent 自己 metacog 强度. 这是 culture 长期培育, 不能省.

## 因素 4 — Prompt 结构 enforcement (CEO 控制变量)

我给 Maya 的 prompt 不只列任务, 还含:
- "Why this matters" context (W12 是 character commitment 兑现, F4 Layer Collapse 实证, 你是第一个被 enforce)
- "narrative_coherence_detector + observable_action_detector LIVE 抓" — Maya 知道 receipt 会被自动 verify
- MANDATORY explicit tool_uses self-count + breakdown (Wave-1.5 Ryan 已 ship template 升级)
- STRICT NO git/choice/defer/E1
- Section 11 spec reference (Maya 必读 binding semantics)

**意义**: CEO 唯一直接控制变量是 prompt design. high-stakes framing + spec reference + STRICT 约束 = 把 task 从 narrow ticking 提到 systemic 工程 stance.

## 5 实战准则 (CEO 派单 reproducible 让所有 agent 都像 Maya)

1. **派单 prompt 必含 "Why this matters" 高 stakes framing** — 不只列任务, 让 agent 知道任务在更大 architecture 中的位置 + failure 后果 + 上层 commitment
2. **任务 scope 设计鼓励 surface root + propose prevention** — 加 "Find root cause + propose CI prevention" 子句, 不只 patch symptom
3. **engineer culture 长期培育** (例 auto_codify 元规则) 不能省 — 长期投入造 metacog 工具
4. **派对的 role 给对的任务** — governance task 派 Maya 类 metacog 强 engineer, kernel 精确任务派 Leo, platform infra 派 Ryan, content/sales 派 Jordan
5. **Prompt template 文化基础设施** (Ryan Wave-1.5 已 ship MANDATORY tool_uses self-count + breakdown) — 让结构强制下次 spawn 必含, 不靠 individual 自觉

## 最深 insight — cognitive-governance 闭环活案例

Maya 这次行为 = 老大命题 "cognitive-governance 闭环" 实证: 做 governance task 同时做 cognitive 反思 (修 symptom + 找 root + 提议 prevention). 双向回流 (governance work feeds back to cognitive systemic learning) 就是 Y\*gov 真差异化 — 治理任务本身成为 metacog 学习载体, agent 文化 + 治理 culture 螺旋互升.

业界 framework (OPA / Lakera / Petri) 单方向 (rule → enforce), 没让 "治理任务 emit lesson". Y\*gov 让 fix 一个 bug 同时输出 systemic lesson, 这是真产品差异化基础.

## CEO future me 读这条时

每次派 sub-agent 前 self-check 4 因素叠加是否齐: model 选了 Claude? role match task? culture 给了 reference? prompt 有 high-stakes framing? 4 件齐 → 期 metacog surface; 缺一 → 期 narrow execution.

不是问"为什么 Maya 这样", 是问"我这次 prompt 有没复制 Maya 的 4 因素叠加".
