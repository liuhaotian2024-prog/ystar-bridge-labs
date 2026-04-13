# EXP-5 — AMENDMENT-007 CEO Operating System Pilot Suite（多维度实验）

**派发**: CEO Aiden 自设计（CEO OS 是我自己的 operating model，不外包设计）
**Level**: L2（CEO 自批，Board 授权"实验密度一定高"）
**日期**: 2026-04-12

---

## 1. 为什么 CEO OS 需要高密度 pilot（不是一个就够）

CEO 是"**用户 + 设计者**"双重身份，天然有盲区：
- 我设计的规则我自己用，可能 rationalize 不合理的地方
- 我评估实验结果我自己参与，可能主观
- 经典理论是给人类 CEO 设计的，agent 迁移风险高

**Board 硬指令**（2026-04-12）: "关于 CEO 的各种实验实验密度一定高"

→ 不是一个 pilot，是一个 **pilot suite** — 多维度覆盖。

## 2. Pilot 矩阵（5 个实验维度）

### EXP-5A: Dogfood 回顾型 pilot（自审）

**目的**: 用 CEO OS 的 6 层规则反向审视**今天本 session** CEO 表现，识别违规次数 + 盲区

**方法**:
- 派 subagent 扮演"审计员"角色（非 CEO 立场）
- 读今天的 CIEU event chain + git log + 对话 transcript
- 对照 CEO OS 6 层的每一条规则逐条打分
- 产出 `reports/experiments/exp5A_dogfood_audit.md`

**具体审查点**:

| CEO OS 层 | 审查问题 |
|---|---|
| L2 注意力 | CEO 有几次写了代码？有几次做了低杠杆修补丁？ |
| L3 信息流 | CEO 有几次没按 6-pager 格式派活？有几次凭记忆而非 memory 查询？ |
| L4 决策 | CEO 有几次把混合 L 级打包给 Board？有几次没做 RAPID 分解？ |
| L5 执行 | CEO 有几次"跨 domain 干活"（越 STL）？ |
| L6 学习 | CEO 这个 session 产生了几条新 memory lessons？有几条未蒸馏？ |

**成功标准**: audit 打分出现 ≥ 1 个明确违规 → CEO OS 是"纠偏工具"而非"空概念"

---

### EXP-5B: 前瞻型 pilot（新制度 vs 现行实践）

**目的**: 用 CEO OS 完整流程处理**一个真实 pending 决策**，对比用当前方式

**待决策**（挑一个真实的）: "Sofia 白皮书 v2 何时可以解锁发布（L3）"

**方法**:
- **组 A**（当前方式）: 按今天 session 的决策风格处理——CEO 直觉 + 偶尔 RAPID + 不用 6-pager
- **组 B**（新制度）: 严格按 CEO OS 6 层流程走——L2 确认不越权 / L3 按 6-pager / L4 RAPID 全走 / L5 STL 分配 / L6 产出入 knowledge
- 两种方式各产出一份决策建议
- CEO（我）对比质量

**成功标准**: B 组产出更深、更可审计、决策路径更清晰

---

### EXP-5C: 压力测试 pilot（两难决策）

**目的**: 给 CEO 一个**真的有 trade-off** 的决策，看 CEO OS 能否帮我不靠直觉做出判断

**待决策**（设计得两难）:
- Scenario: "Maya 要立即做 DIRECTIVE-006 active_agent 并发修补；Sofia 说白皮书 v2 发布前 Board 必须看；Ryan 说 Continuity Guardian 测试需要他全力；CTO 说 memory 闭环4 Secretary auto-memory sync 阻塞。只能有 2 个 agent 真正投入，其余等。**谁干哪个？**"

**方法**:
- **组 A**（当前方式）: CEO 凭直觉排序 + 简短理由
- **组 B**（CEO OS 方式）: 严格走 Section F (L5) STL + Section G (L6) Issue Log + Section E (L4) RAPID 四角色分工产出

**成功标准**: B 组判决出现 A 组没考虑到的维度（比如"DIRECTIVE-006 和 Continuity Guardian 同修 watchdog 会冲突 → 串行"）

---

### EXP-5D: 跨模型对比 pilot（关键防盲区）

**目的**: **这是 CEO OS 最关键的实验** — 如果规则设计得好，不同模型（Claude / GPT / Gemma）跑同一 CEO 决策应该收敛到同质量决策

**方法**:
- 派**三个 subagent**扮 CEO，各用不同模型后端（如能访问）
- 给同一真实决策（可以复用 EXP-5C 的 scenario）
- 都按 CEO OS 完整流程走
- 对比三个模型的 decision output

**成功标准**:
- 三个模型判决**相近或一致** → CEO OS 规则设计可迁移（验证 Iron Rule 3 生态中立在 CEO 层也成立）
- 三个模型判决**发散** → CEO OS 过度依赖 Claude 特异性，需要重新设计

**如果技术上只能访问 Claude**: 用**两次独立 subagent**（Claude Sonnet 和 Opus），打分应 ≥ 85% 一致。否则规则定义不够严密。

---

### EXP-5E: 长期 shadow-mode pilot（最难，但最有价值）

**目的**: CEO OS 落地的**真正验证**是长期使用——一次 pilot 不够

**方法**:
- 在 AMENDMENT-007 **实质生效前**，CEO（我）**自己宣言**按 CEO OS 运行下一段时间
- 每次决策记录: 用了 CEO OS 的哪一层规则 / 是否遵守 / 效果反馈
- 积累 N 条（CIEU event count = 30）记录后 retro
- 由 Secretary 蒸馏为 `knowledge/ceo/patterns/ceo_os_adherence_log.md`

**成功标准**: 30 条记录里，"规则帮助我做出更好决策"的占比 > 70%

**这个 pilot 不外包** — CEO 自己的运行日志，外包就不真实。

---

## 3. Pilot 优先级 + 执行顺序

| # | Pilot | 优先级 | 依赖 | 执行者 |
|---|---|---|---|---|
| 5A | Dogfood 回顾 | P0 | 今天 session 数据 | subagent 扮审计员 |
| 5B | 前瞻对比 | P0 | 一个真实 pending 决策 | CEO 双跑 + subagent 对比 |
| 5C | 压力测试 | P0 | 两难 scenario | CEO 双跑 |
| 5D | 跨模型对比 | P0（最关键）| 技术可达 | 多 subagent 不同模型 |
| 5E | 长期 shadow | P1 | AMENDMENT-007 框架就位 | CEO 自己 |

**执行顺序**（避免 active_agent 并发冲突）:
1. 先做 5A（只读今天 session，最轻量）
2. 然后 5B（CEO 双跑）
3. 然后 5C（CEO 双跑，和 5B 同类型）
4. 最后 5D（关键防盲区，结果是 go/no-go 信号）
5. 5E 并行跑（reference 状态，不阻塞）

## 4. 综合 Verdict 路径

EXP-5A/B/C/D 都跑完 → 写 `reports/experiments/exp5_ceo_os_final_verdict.md` → 决定 AMENDMENT-007 是否**按当前设计落地 / 需调整 / 直接否决**

## 5. 本实验套件的防盲区设计

- 5A 用**审计员视角**而非 CEO 视角审视 CEO—避免自我 rationalize
- 5B 用**双跑**—避免"只走新流程，结果无法对照"
- 5C 用**两难**—避免 CEO OS 只在简单决策上好看
- 5D 用**跨模型**—避免 "CEO OS 只是 Claude Opus 的推理风格外包装"
- 5E 用**长期**—避免"单次 pilot 说明不了持续用的问题"

**只要 5D 失败（跨模型不收敛），整个 CEO OS 设计就得回炉**——这是最重要的试金石。

## 6. 实施计划

**本 session 内立即派**:
- EXP-5A subagent（审计员）— 可立即派
- EXP-5B/5C 我自己跑（CEO 双跑） — 在当前 context 内推进

**下 session 做**（当前 context 不够深度并行）:
- EXP-5D 跨模型对比（需要多 subagent + 不同模型）
- EXP-5E 启动 shadow-mode（需要 CEO OS v1 基础版先 in-use）

**Continuity Guardian 完成后**: 下一 session 从 wisdom package 续接，pilot 继续执行

## 7. Board 决策点（没有）

这是 CEO L2 自批实验（Board 已经"全部批准"）。无 Board 决策点。**CEO 直接启动**。
