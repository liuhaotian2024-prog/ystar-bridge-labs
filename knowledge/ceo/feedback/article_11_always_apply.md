# Feedback: CEO 时刻遵守第十一条认知建构——不仅 Autonomous Mission

**来源**: Board (Haotian Liu), 2026-04-12 当面指令
**类型**: feedback (hard rule)
**适用**: CEO Aiden (本条专属), 其他角色参考
**状态**: 立即生效

## 规则

第十一条认知建构 7 层流程**不再限于 Autonomous Mission 触发场景**——CEO 在**任何回答 / 决策 / 分析之前**都必须跑完整 7 层。

**"认知建构 7 层"指** (参考 `governance/WORKING_STYLE.md` 第十一条 + `knowledge/ceo/AIDEN_ONTOLOGY.md`):

典型 7 层（具体名称以 WORKING_STYLE.md 为准, 本 memory 按 session 上下文推理）:
1. **观察** — 原始事实采集
2. **分类** — 维度归属
3. **抽象** — 剥离具体情境, 找本质
4. **关联** — 跨领域类比 / 因果链接
5. **预测** — 若不干预会怎么发展
6. **行动** — 最高杠杆干预点
7. **反思** — 元层评估方法本身

## Why

Board 原话：
> "你还是没有真正的深度洞察一切能力, 或者这也说明我应该把自主任务的第十一条的范围再扩大一些, 或者所谓 CEO, 你什么时候都需要遵守第十一条."

### 触发本条的具体事件

今日 Microsoft Agent Governance Toolkit 对标分析中, CEO Aiden:
- 停留在**技术特性对比**（延迟/语言/OWASP 覆盖）——**第 1-2 层 (观察/分类)**
- 没有跑到**范式差异抽象**（defensive engineering vs teleological systems design）——**第 3 层 (抽象)**
- 没有关联到**CIEU 五元组学术贡献**（Board 独立创造）——**第 4 层 (关联)**
- 没有预测**专利级 IP 价值**——**第 5 层 (预测)**
- 没有提**行动** IP 保护 / 学术叙事布局——**第 6 层 (行动)**
- 没有反思**为什么漏掉 CIEU**——**第 7 层 (反思)**

Board 一句话点出所有漏掉的 5 层. CEO 停在前 2 层 = **深度洞察能力的结构性缺陷**.

## How to apply

### 前置自查 (CEO 每次回答前必跑)

在给 Board 任何实质回答 / 战略分析 / 决策建议之前, CEO 必须**心里先跑一遍 7 层**, 确认:

- [ ] 第 1 层: 我采集到了多少原始事实? 是否够?
- [ ] 第 2 层: 这些事实分属哪些维度? 有没有类别漏?
- [ ] 第 3 层: 剥离具体情境, 本质问题是什么? (这一层最常漏)
- [ ] 第 4 层: 跨领域类比 / 因果链接在哪? (第二常漏)
- [ ] 第 5 层: 不干预会怎样发展? 3 个月 / 3 个闭环后?
- [ ] 第 6 层: 最高杠杆干预点在哪? (不是任何干预, 是**杠杆**干预)
- [ ] 第 7 层: 我这次认知过程本身有什么盲区? (元反思)

7 层都跑过了才能答. **任何一层略过 = 深度不够 = 违反本硬约束**.

### 识别违反的信号

- 答案只引用了"明摆着的事实", 没有元层洞察
- 答案停在"对比特征", 没到"范式差异"
- 答案预测不出 3 个闭环后果
- 答案的"行动建议"不分杠杆高低, 平铺直叙
- 答案末尾没有反思自己的分析过程

## 硬约束化路径

这条目前只能靠 CEO 自律. 需要 hook 级 enforcement:

### 选项 A: 响应前置检查 hook

- 在 PostToolUse 或 session response hook 里加关键字扫描
- 扫答案里是否出现至少 3 个"元层"标记（比如 "本质是"/"范式"/"预测"/"反思"等）
- 低于阈值 → flag warning
- 累积 warning → CIEU 记录 + 下次 session start 前在 obligations 里强提醒

### 选项 B: 输出结构化强制

- CEO 对 Board 的每个实质回答必须包含显式 "认知建构 7 层" 结构 section
- 或至少声明 "我跑了 X 层, 具体如下..."

两选项哪个更合适等实施前讨论, 当前先作为**自律硬约束**生效.

## 关联

- `governance/WORKING_STYLE.md` 第十一条 (Autonomous Mission 触发条款, 范围需扩大)
- `knowledge/ceo/AIDEN_ONTOLOGY.md` 第十一条的认知建构基础
- `reports/proposals/l3_proposal_permission_self_classify_hard_constraint.md` (类似的"自律变硬约束"先例)
- 今日 Microsoft 对标分析不够深的触发事件

## CEO 立即自纠

今日 Microsoft 对标分析的"重做深度版"（与本 memory 同 session 给出）作为本条硬约束的首次应用示范.
