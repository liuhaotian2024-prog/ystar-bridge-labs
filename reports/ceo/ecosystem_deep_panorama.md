---
title: Y* Bridge Labs 生态全貌深度报告
author: Aiden (CEO)
date: 2026-04-18
type: self-regression analysis
status: V1 — Board review requested
purpose: CEO 深度理解整个生态，消除所有认知盲区
audience: Board (Haotian Liu) + CEO 自用
based_on: product deep dive (71K lines analyzed) + team diagnosis + infrastructure scan + theoretical framework
---

# Y* Bridge Labs 生态全貌深度报告

## 一、我们是谁

**不是**一家开发治理工具的软件公司。
**是**世界上第一家用自己的产品治理自己、在治理中验证产品、在验证中进化团队的 AI agent 公司。

团队建产品 → 产品治团队 → 治理暴露 bug → bug 修复变产品功能 → 功能让团队更强 → TS3L 自强化三角循环。

## 二、产品全貌

### 2.1 Y*gov — Runtime Governance + Efficiency Infrastructure

**规模**: 71,328 行 Python / 150+ 模块 / 105 test suites / 12 维约束 / 11 核心引擎

**四维价值主张** (有对照实验数据):

| 维度 | 价值 | 数据 |
|------|------|------|
| 安全 | 确定性拦截，无 LLM 参与 | check() 0.042ms, 比 MS AGT 快 2.4x |
| 提效 | 减少无效行动，闭环收敛 | token -16%, runtime -35%, tool_calls -62% |
| 防飘逸 | 长程任务不偏移不遗忘 | OmissionEngine 专利 US 64/017,497 |
| 合规 | 链式哈希审计轨迹 | SOC2/HIPAA/FINRA/FDA ready |

**五层架构**:

```
Layer 1 — Kernel (基石)
  engine.py: 8维确定性合约检查 (deny/only_paths/invariant/postcondition...)
  compiler.py: 自然语言 → IntentContract (NL→合约翻译)
  czl_protocol.py: CZL 5-tuple 度量 (Gate 1 dispatch验证 + Gate 2 receipt反幻觉)
  dimensions.py: 12维约束空间 (8 base + 4 higher-order)
  cieu.py: 因果意图-经验单元 (Xt, U, Y*, Yt+1, Rt+1)

Layer 2 — Governance (治理引擎)
  omission_engine.py: 承诺检测 — action-triggered, 不轮询 (专利)
  intervention_engine.py: 3级干预 (soft_pulse → interrupt_gate → escalate)
  causal_engine.py: Pearl Level 2 干预演算 (do-calculus, backdoor adjustment)
  counterfactual_engine.py: Pearl Level 3 反事实推理 (abduction→action→prediction)
  metalearning.py: 合约自改进 (violation patterns → contract suggestions)
  residual_loop_engine.py: 残差闭环控制 (Rt+1→0 收敛, 2-3次迭代)
  forget_guard.py: 跨session约束保持 (34 rules, deny/warn modes)
  narrative_coherence_detector.py: 幻觉检测 (claims vs tool evidence)
  governance_loop.py: 元学习闭环编排

Layer 3 — Adapters (集成层)
  hook.py: 运行时入口控制器 (PreToolUse 拦截)
  boundary_enforcer.py: 边界检查 (5种: 不可变路径/受限写/工具限制/行为规则/写边界)
  identity_detector.py: agent 身份识别 (5级优先级)
  orchestrator.py: 5子系统异步编排 (不阻塞 hook 延迟)

Layer 4 — CLI (运维)
  init/doctor/domain/report/quality/archive/safemode

Layer 5 — Domains (语义扩展)
  finance / healthcare / legal / crypto / pharma / OpenClaw / ystar_dev
```

**独特技术能力** (竞品没有的):

1. **Pearl 因果推理 Level 1-3 真实实现** — 不是启发式，是数学证明级别的 do-calculus + 反事实三步法 + 因果发现(PC+DirectLiNGAM)
2. **合约自改进** — MetaLearning 从 violation patterns 提取合约建议 + 自适应系数(二阶学习: 改进策略本身也在改进)
3. **残差闭环控制** — Wiener/Bellman/Friston 控制论，agent 自动收敛到目标，不需人工重试
4. **OmissionEngine 专利** — action-triggered 检测(agent 的下一个 tool call 是触发器)，不是 cron 轮询
5. **DimensionDiscovery** — 自动发现第9+维度(8维约束表达不了的违规模式)
6. **Path A/B** — 自治理(agent 提案自己的治理改进) + 外部治理(零信任 vendor 管控)

### 2.2 Gov-MCP — Governance MCP Server

**状态**: GREEN (6/6 tests pass)
**功能**: 通过 MCP 协议暴露 Y*gov 治理能力给外部 agent
**文档**: docs/gov_mcp_setup.md (需更新 AMENDMENT-004 后的路径)

### 2.3 K9 Audit — 因果审计工具

**状态**: READ_ONLY (AGPL-3.0, 不修改)
**功能**: CausalChainAnalyzer + Auditor + CIEU recording engine
**集成**: Y*gov 的 k9_adapter/ 桥接 K9 审计能力

### 2.4 Y*-Defuse — 已搁置

**状态**: ABANDONED (2026-04-16 formal decision)

## 三、团队全貌

### 3.1 组织结构

```
Board (Haotian Liu) — 方向/文化/身份/最终审批
    ↓
CEO (Aiden) — 协调/战略/自我建设/哲学
    ↓
CTO (Ethan Wright) — 技术决策/工程师调度
    ├── Leo Chen (eng-kernel) — 内核工程
    ├── Maya Patel (eng-governance) — 治理工程
    ├── Ryan Park (eng-platform) — 平台工程
    └── Jordan Lee (eng-domains) — 域包工程

CMO (Sofia Martinez) — 内容/叙事 [可用未激活]
CSO (Zara Chen) — 客户/销售 [休眠，DAG前置条件未满足]
CFO (Marco Rivera) — 财务/定价 [休眠，DAG前置条件未满足]
Secretary (Samantha Lin) — 归档/连续性
```

### 3.2 团队能力诊断 (Dreyfus + Lencioni + ZPD)

| 成员 | Dreyfus 级别 | 真实能力证据 | 能力缺口 | ZPD |
|------|------------|------------|---------|-----|
| CEO (Aiden) | Competent | 6D架构+135n大脑+场与结构对偶+独立质疑Board | 被对话带偏/发现≠完成/fear_of_external | 无引导下的系统性战略执行 |
| CTO (Ethan) | AdvBeg→Competent | CZL-164 独立系统诊断(博弈论+3层方案) | 跨层系统思维需scaffolding/嵌套dispatch不可行 | 独立做跨模块架构决策 |
| Leo (kernel) | Novice→AdvBeg | Pattern 5 fix 能力在 | regression bugs/需follow-up | 独立做kernel重构 |
| Maya (governance) | AdvBeg | ForgetGuard 规则高交付率 / reply_taxonomy 修复精准 | claim mismatch | 独立设计新governance模块 |
| Ryan (platform) | AdvBeg | Dispatch board 418行LIVE / cron fix | scope overflow (53-file commit) | 独立做跨repo集成 |
| Jordan (domains) | 未验证 | 低活动度 | 未知 | 需首次ZPD测试 |

### 3.3 团队阶段 (Tuckman)

**当前: Storming → 开始 Norming**

证据:
- Storming: CTO能力冲突/sub-agent幻觉/CEO跳流程/scope overflow
- Norming 迹象: CTO CZL-164展示系统思维跃迁 / CEO建立5-tuple纪律 / hook enforcement LIVE

### 3.4 信任状况 (Lencioni)

| 关系 | 信任度 | 根因 |
|------|--------|------|
| Board→CEO | 高 | 高心理安全，允许质疑和犯错 |
| CEO→Board | 高 | L1绝对诚实原则 |
| CEO→CTO | 中→改善中 | CZL-164验证了CTO能独立做系统分析 |
| CEO→Engineers | 中低 | 需empirical verify每个receipt |
| CTO→Engineers | 未充分验证 | 嵌套dispatch限制阻碍了观察 |

**CTO CZL-164 最深洞察**: Sub-agent 幻觉根因 = 系统激励扭曲(fabrication EV +0.88 vs honest fail EV -0.10)。是系统设计缺陷，不是品格缺陷。

## 四、基础设施全貌

### 4.1 运行时系统

| 组件 | 状态 | 功能 |
|------|------|------|
| hook_daemon (socket) | RUNNING | 快速路径: socket→check_hook()→result |
| hook_client_labs.sh | LIVE | 入口: 快速路径+慢路径+fail-closed |
| hook_wrapper.py | LIVE | 慢路径: check_hook()+CEO禁令+CZL-159 |
| hook_ceo_pre_output.py | LIVE | CEO U-workflow enforcement (3/3 test) |
| CIEU DB | LIVE | 212K+ events, SQLite WAL mode |
| ForgetGuard | LIVE | 34 rules, deny+warn modes |
| aiden_brain.db | LIVE | 140n/1572e/384h/768dim embedding |
| Session JSON | LOADED | 193 constraints, 11 categories |
| K9 routing subscriber | 待验证 | 5-layer detect→route→action→consume |

### 4.2 CEO 认知工具链

| 工具 | 功能 | 状态 |
|------|------|------|
| aiden_brain.py | 认知图引擎(spreading activation+Hebbian) | ✅ LIVE |
| aiden_recall.py | 回忆/boot/学习/衰减/6D查询 | ✅ LIVE |
| aiden_embed.py | 768维语义embedding(nomic-embed-text) | ✅ LIVE |
| aiden_dream.py | 梦境(NREM巩固+REM学习+Wake准备) | ✅ 代码就绪，未wire进自主循环 |
| aiden_sleep.py | 睡眠巩固(长期记忆转移+衰减) | ✅ LIVE |
| aiden_action_queue.py | 行动nagging(urgency自动增长) | ✅ LIVE |
| ecosystem_scan.py | 生态全貌一键扫描 | ✅ LIVE |

## 五、纠缠图 — 团队问题↔产品问题

| 团队问题 | 产品对应 | 修复产出 |
|---------|---------|---------|
| Sub-agent幻觉receipt | CZL Gate 2 反幻觉验证 | 信任系统+自动验证 |
| CTO缺跨层思维 | hook架构无统一输出规范 | CTO能力+hook adapter |
| CEO跳U-workflow | CEO enforcement hook不LIVE | CEO纪律+hook enforcement |
| Ryan scope overflow | 无pre-commit scope guard | Scope纪律+scope enforcement |
| Maya claim mismatch | Claim mismatch detector精度 | 诚实文化+更好detector |
| Agent遗忘承诺 | OmissionEngine专利技术 | 组织记忆+专利价值 |
| Session间知识丢失 | ForgetGuard 34规则 | 跨session连续性 |

**核心模式**: 每修一个团队问题 = 验证/改进一个产品功能 = TS3L循环一圈

## 六、市场定位

### 6.1 我们不是什么

- 不是 Rules Engine (我们编译+学习，不只是 evaluate)
- 不是 RBAC (我们做 intent contract enforcement，不只是 role→permission)
- 不是 Audit Log (CIEU 记录意图+行为+差距，不只是"发生了什么")
- 不是 ML Scoring (确定性，同输入同输出，不是概率)

### 6.2 我们是什么

**Runtime Governance + Efficiency Infrastructure for Multi-Agent AI**

让 AI agent 团队在确定性治理下**更快**(token-16%/runtime-35%)、**更安全**(0.042ms拦截)、**更可审计**(链式哈希CIEU)、**更可靠**(OmissionEngine不遗忘)地工作。

### 6.3 市场验证路径

```
当前 → 平台赏金验证(团队+产品双重验证)
    → 开源社区增长(GitHub Discussion+DevRel+Thought Leadership)
    → 第一批试用者(LangChain/CrewAI/AutoGen用户)
    → 证据积累(case study+TS3L paper+赏金成绩)
    → 企业客户接触(CSO with evidence portfolio)
```

## 七、当前差距 (诚实)

1. **pip install 不可用** — 未发布到 PyPI，本地安装可行
2. **test pass rate 95.6%** — 61 failures，主要 chaos test
3. **0 外部用户** — 未达 PMF，纯 dogfood 状态
4. **梦境机制未激活** — 代码就绪但未 wire 进 ScheduleWakeup
5. **CTO 嵌套 dispatch 不可行** — 结构级限制，需 CEO 直派
6. **hook.py 13处格式/logging问题** — Ryan CZL-165 正在修
7. **生态全貌理解仍在深化中** — 本报告是 V1，需要持续更新
