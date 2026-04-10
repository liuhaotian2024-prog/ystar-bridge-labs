# Natural-Language → Contract Pipeline 可行性研究

**作者**: Ethan Wright (CTO)
**日期**: 2026-04-09
**优先级**: P0(GOV-007 Step 2 scope 扩展)
**权限层级**: **Level 3**(架构变更 + 跨 repo + 影响 Y\*gov 翻译流水线 + 影响 .ystar_session.json 写入路径 + 影响 GOV-005 Finding 4 的层级架构定位)
**状态**: 研究 only,等 Board 确认才动代码
**触发**: Board GOV-007 Step 2 scope 扩展指令 (2026-04-09)
**前置文档**: `reports/cto/gov_mcp_session_integration.md` (GOV-007 Step 1 提案,commit `e80b24e`)
**严格遵守**: GOV-006 intent verification 协议(Board 已批 C 方案)精神 — research → confirm → execute

---

## Board 的 4 个核心问题(逐项回答的目标)

Board 说: "你们首先验证是否可行,用反事实推理是否合理,是否会引发系统冲突,是否可以实现以后我或者用户对自己的agent团队说任何一句话都不会被agent随意曲解或者忽略的这个功能目标?"

拆成 4 个独立问题:

1. **是否可行?** → 技术可行性
2. **反事实推理是否合理?** → 设计合理性
3. **是否会引发系统冲突?** → 跟现有架构的兼容性
4. **是否实现"任何一句话不被曲解/忽略"的目标?** → 功能目标的真实可达性

下面逐项回答。

---

## 先澄清: 两件事被概念性混淆了,需要分开讨论

Board 的 directive 实际包含**两个不同 level 的治理需求**,混在一起讨论会失焦:

### Level α: "执行某条具体指令" (task-level intent)

例: "今天晚上 10 点之前把 OPERATIONS.md 重写完"。

- **是一次性的任务**,不是持久规则
- 只影响这一次 agent 行为
- **GOV-006 Intent Verification (任务 #57, Board 已批 C 方案)** 解决的就是这一层 — agent 必须先 record_intent,Board 确认后才执行。这条已经 lined up 实施。

### Level β: "添加/修改持久规则" (contract-level rule update)

例: "从今往后,任何 agent 不许在没我确认的情况下动 production database"。

- **是规则变更**,不是具体任务
- 影响所有未来 agent 行为
- **当前没有顺畅的输入路径** — Board 必须手动找 Ethan 改 `.ystar_session.json`,或走 BOARD_CHARTER_AMENDMENTS 流程改 AGENTS.md
- **本次 Board directive 真正在问的是这一层** — 是否能建立 NL → translate → diff → Board confirm → .ystar_session.json 的自动化通道

这两个 Level 都对应 Board 说的"agent 不要曲解或忽略我的话",但**解决方案完全不同**:

| Level | 问题 | 解决方案 | 状态 |
|---|---|---|---|
| α (task) | "我让你做 X,你做了 Y" | GOV-006 record_intent + Board confirm + execute | task #57,Board 已批 C 方案,等下次 session 实施 |
| β (rule) | "我说过不要做 X,你又做了" | NL pipeline → translate_to_contract → .ystar_session.json → gov-mcp 自动加载 | **本提案研究的对象** |

**重要的诚实说明**: Level α 的 GOV-006 已经在 lined up,Level β 的 NL pipeline 是新研究。Board 的 directive 把两件事并入"GOV-007 Step 2 一起做",**我个人建议拆开**(下面详述),但这是 Board 的决策权。

---

## Q1: 是否可行?

### 技术可行性: **YES**

所有需要的组件都存在,工程量是中等而非未知:

| 组件 | 现状 | 工程量 |
|---|---|---|
| `translate_to_contract(text, api_call_fn)` | ✅ Y\*gov 已有,签名稳定,默认 regex,可选 LLM(api_call_fn 注入) | 0 (复用) |
| `.ystar_session.json` schema | ✅ 已知 schema,GOV-007 Step 2 会加 `schema_version: "1.0"` | 0 (本来就要做) |
| gov-mcp 读 `.ystar_session.json` | ⏳ GOV-007 Step 2 原始 scope,~80 行 | 半天 |
| 文件写入与原子替换 | 标准操作,write → tmp → atomic mv | 半天 |
| **NL → diff 工具(新)** | ❌ 不存在,需要新建 | 1-2 天 |
| **Diff review UI(新)** | ❌ 不存在,需要新建(可以是 markdown report 形式,不是 GUI) | 半天 |
| **gov-mcp / ystar hook reload .ystar_session.json**(新) | ⚠️ 部分存在 — 需要 SIGHUP 或 file watch 或重启机制 | 1 天 |

**总工程量估计**: ~4-5 天工程 + 测试,跨 ystar-company + Y-star-gov + gov-mcp 三个 repo。

### Iron Rule 1 兼容性: **YES,但需要明确边界**

`translate_to_contract(text, api_call_fn=anthropic_api)` 在 LLM 模式下 **是允许的**,因为:

- LLM 在**翻译**步骤(offline contract authoring)
- 翻译产出**确定性 contract dict**
- contract dict 被人工审核后写入 `.ystar_session.json`
- check() / gov_check() 在运行时**只读 frozen rules,不再调用 LLM**

**LLM 在 contract 制造,deterministic regex 在 contract 执行** —— 这是对 Iron Rule 1 的精确遵守:

```
Iron Rule 1 原文: "Y*gov的enforcement层不含LLM,所有ALLOW/DENY决定都从contract确定性计算"

Iron Rule 1 不约束的事:
- contract 的"创作"过程
- contract 的"翻译"过程
- contract 的"diff 评审"过程
- contract 的"持久化写入"过程

Iron Rule 1 严格约束的事:
- check() / gov_check() 内部不能调 LLM
- ALLOW/DENY 决策路径不能依赖任何概率推理
```

**这条边界是清晰的,不是 grey area**。但**必须在文档里明文说清**,否则未来有人会把 NL pipeline 当成"gov-mcp 用 LLM 做决策",违反 Iron Rule 1。

### 文件 reload 机制可行性: **YES,有 3 个选项**

GOV-007 Step 2 之后,gov-mcp 启动时读 `.ystar_session.json`。如果 NL pipeline 更新了这个文件,gov-mcp 怎么知道?

| 选项 | 机制 | 优 | 劣 |
|---|---|---|---|
| **A. SIGHUP 信号** | gov-mcp 监听 SIGHUP,收到则 re-read .ystar_session.json | 简单 + 确定性 + 显式 | 需要外部触发 `kill -HUP <pid>`,需要知道 PID |
| **B. File watch** | gov-mcp 用 watchdog/inotify 监听 .ystar_session.json mtime | 自动 + 用户无感 | 跨平台依赖 (Linux inotify, macOS FSEvents),增加 dependency |
| **C. 周期 poll** | gov-mcp 每 N 秒 stat() 检查 mtime | 零依赖 + 跨平台 | 浪费 (大部分检查都是 noop),最差延迟 N 秒 |

**推荐**: A (SIGHUP)。由 NL pipeline 在写完 .ystar_session.json 后主动 `kill -HUP $(pgrep -f gov_mcp)`。简单确定,显式控制 reload 时机,易测试,易回滚。

ystar Python hook 同样的问题:hook 是无状态的,每次 PreToolUse 都是新进程,自动读最新 .ystar_session.json,**不需要 reload 机制**。这是 hook 的天然优势。

---

## Q2: 反事实推理是否合理?

按 GOV-005 第七条做 counterfactual analysis,3 个候选方案:

### 方案 A: GOV-007 Step 2 原始版(只换数据源)

**做什么**: gov-mcp 启动时读 `.ystar_session.json` 而不是解析 AGENTS.md。新增 `--session-config` 参数。`--agents-md` 保留为 deprecated fallback。**不做 NL pipeline**。

**Yt 预测**:
- 工程量: 1 天(GOV-007 Step 1 提案估算)
- 跨 1 repo (gov-mcp) + 1 行 ystar-company (加 schema_version)
- gov-mcp 0.2.0 release scope 不变

**Rt(与 Y\* 的差距)**:
- ✅ Board GOV-007 directive 字面满足
- ✅ confidence ≥0.95
- ❌ **不解决 Level β 问题**(NL → 持久规则的输入通道不存在)
- ❌ 不解决 Board 表达的 "agent 不要曲解我的话" 在规则层面

### 方案 B: GOV-007 Step 2 扩展版(本次 directive)

**做什么**: 方案 A + NL pipeline (Level β 解决方案)。`scripts/board_say.py` 新工具:

```bash
python3.11 scripts/board_say.py "从今往后任何 agent 不许在没我确认的情况下动 production database"
```

工具执行:
1. 调 `translate_to_contract(text, api_call_fn=anthropic_api)` 拿到 contract dict
2. 计算 diff vs 当前 .ystar_session.json
3. 写 diff 到 `reports/board_proposed_changes/2026_04_09_HHMMSS.md`(Markdown 表格 + diff 块)
4. 在 chat 里显示 diff,等 Board 说 "确认" 或 "调整 X"
5. Board 确认后:
   - 把 contract dict merge 进 .ystar_session.json
   - atomic write
   - 发 SIGHUP 给 gov-mcp(强制 reload)
   - 写 CIEU 记录: `event_type=CONTRACT_UPDATE`, source=board_say, intent_id=...
6. 输出 success,显示新规则在 `.ystar_session.json` 里的位置

**Yt 预测**:
- 工程量: 4-5 天(包含 NL pipeline 新 + reload 机制 + diff UI + 测试)
- 跨 3 repos: gov-mcp (Step 2 原始)+ Y-star-gov (translate_to_contract + LLM api_call_fn 验证)+ ystar-company (board_say.py + diff review template)
- 引入新 dependency: anthropic SDK (LLM api_call_fn 注入用)
- gov-mcp 0.2.0 release scope **5x 于原始 Board GOV-007 估算**
- 触发新 deliverables: board_say.py 工具、diff review markdown 模板、CONTRACT_UPDATE CIEU 事件类型、SIGHUP reload mechanism

**Rt**:
- ✅ Board GOV-007 directive 字面满足
- ✅ confidence ≥0.95
- ✅ Level β 问题从"无通道"到"有通道"
- ⚠️ 仍然不解决 Level α(那是 GOV-006 task #57 的 scope)
- ⚠️ 工程量 5x,gov-mcp 0.2.0 release timeline 受影响
- ⚠️ NL pipeline 自身的失败模式(下面 Q4 详述)
- ❌ **改变了 GOV-005 Finding 4 的层级架构定位**(下面 Q3 详述)

### 方案 C: 拆分 — Step 2 原始先做,NL pipeline 作为 GOV-008 独立 directive

**做什么**: GOV-007 Step 2 严格只做"换数据源"(方案 A),NL pipeline 作为新 directive GOV-008 单独提案 + 单独 Board 决策。

**Yt 预测**:
- Step 2: 1 天(同方案 A)
- GOV-008 提案 (research): 半天 (本提案 + Q4 + 风险拆解)
- GOV-008 实施(后续 directive): 4-5 天
- 总: 1 + 0.5 + 4-5 天,但**关键依次发生**: Step 2 完成 → gov-mcp 0.2.0 release → 然后做 GOV-008 + Y-star-gov 0.49

**Rt**:
- ✅ Step 2 字面 scope 不变,gov-mcp 0.2.0 release 不延迟
- ✅ NL pipeline 作为独立 directive,Board 可以专门评估它的 trade-offs
- ✅ 错误成本可控:Step 2 出 bug 不连累 NL pipeline,反之亦然
- ✅ GOV-005 Finding 4 的架构定位有时间专门讨论(下面 Q3)
- ❌ Board 当下表达的 intent 是"两件事一起做",拆分是部分违背 directive
- ⚠️ "两件事一起做" 的好处:NL pipeline 实施时立即受益于 Step 2 的 .ystar_session.json 数据源切换。拆开做会让 NL pipeline 多等一阵

### 推荐: **方案 C(拆分)**,但接受 Board 选 B 也合理

**理由(一句话)**: 方案 B 把 1 天的 Step 2 扩展成 5 天的 multi-component delivery,引入新的 LLM dependency,改变 Finding 4 架构定位 —— 任何一个子组件出问题都可能 block gov-mcp 0.2.0 release。方案 C 拆开做可以保持各 directive 的清晰边界 + 错误隔离 + 增量验证。

**但方案 B 也合理**——如果 Board 优先级是 "尽快有 NL pipeline" 而不是 "尽快有 0.2.0 release",B 是直接路径。**这是 Board 的优先级判断**,不是技术正确性问题。

**我的 honest answer 给 Q2**: 反事实推理**合理**(方案 B 和方案 C 都是合理的,只是 trade-off 不同),**但 Board 应该明确选哪个**,而不是让 Ethan silently 走 B 然后发现 5x 工程量。

---

## Q3: 是否会引发系统冲突?

### 冲突 #1: 跟 GOV-005 Finding 4 的层级架构定位

**Finding 4 当前文档**(`governance/INTERNAL_GOVERNANCE.md` 我刚写的"分层治理架构"段):

> Layer 1 (ystar hook): contract 源 = `.ystar_session.json`
> Layer 2 (gov-mcp): contract 源 = `AGENTS.md` (regex)
> 两层 contract 源 by-design 分离

**GOV-007 Step 2 之后**:

> Layer 1 (ystar hook): contract 源 = `.ystar_session.json`
> Layer 2 (gov-mcp): contract 源 = `.ystar_session.json` ← **改了**

**两层共用同一个 contract source**。Finding 4 的"两套 contract source 分离"消失了。

**这是冲突吗?** 取决于 Finding 4 真正在保护什么:

- **如果 Finding 4 保护的是"两套独立 contract source"**(防止 single source of failure)→ **Step 2 违反 Finding 4**,需要重新考虑
- **如果 Finding 4 保护的是"两个 enforcement points 独立工作"**(防止 single enforcement failure)→ **Step 2 不违反**,只是统一了 source,enforcement points 还分离

我重读 Finding 4 / DNA #007 的原文:

> "两个 contract source,两个执行点,两个责任域,任何客户端同时受两层保护"
> "不是 redundancy,是 defense-in-depth"
> "两层任何一层放过,另一层有机会拦"

**关键句**: "两层任何一层放过,另一层有机会拦"。这是 enforcement point 的独立性,**不是 contract source 的独立性**。Source 统一 + enforcement 点分离,defense-in-depth 仍然成立(同一规则在两个 enforcement 点各检查一次)。

**结论**: GOV-007 Step 2 **不违反 Finding 4 的精神**,但**违反 Finding 4 的字面表述**。需要**回头修订 INTERNAL_GOVERNANCE.md 的"分层治理架构"段**,把"两个 contract source"改成"两个 enforcement points",澄清架构定位。

**这是文档维护工作,不是设计冲突**。Refinement,不是 retraction。

### 冲突 #2: NL pipeline 跟 GOV-005 Part 1 的反事实提案规范

GOV-005 第七条规定 Level 2/3 决策必须用反事实推理格式。如果 Board 用 NL pipeline 一句话生成新规则,**这一句话**算是 Level 3 提案(改 contract = 改宪法)。但 NL pipeline 把它**直接转成了 contract diff**,跳过了反事实推理格式。

**这是 fast path bypass 还是合理简化?**

- 严格立场: 任何 Level 3 决策必须有完整的反事实分析。NL pipeline 跳过反事实 = 违反 GOV-005。
- 务实立场: Board 自己说的话本来就是 Level 3 决策的 source,NL pipeline 是把 Board 的话转成 contract,反事实分析的"团队侧"由 NL pipeline 工具完成(diff review 就是反事实展示),"Board 侧"由 Board 看 diff 后说"确认"完成。

**我倾向务实立场**,但**必须在 board_say.py 工具里做明确**: diff review markdown 模板必须强制包含:

- "Xt": 当前规则
- "Y\*": Board 想要的状态
- "proposed contract changes": diff
- "为什么这个翻译是合理的": 翻译器的 confidence + 关键 ambiguity 警告
- "alternative interpretations rejected": LLM 在翻译中考虑过的其它 reading,以及为什么不选

这样**diff review 本身就是反事实分析的一种 instantiation**,符合 GOV-005 第七条的精神(让 Board 看到完整推理,只做 approve/reject 决策)。

### 冲突 #3: NL pipeline 跟 GOV-006 Intent Verification

GOV-006 (task #57,Board 已批 C 方案) 的 INTENT_RECORDED → INTENT_CONFIRMED 闭环是为 Level 2/3 task 做的。NL pipeline 是 Level 3 contract update。**NL pipeline 应不应该走 INTENT_RECORDED 流程?**

我的判断: **应该走**。因为:

- 任何 Level 3 决策都应该有 intent 审计链
- contract update 是最敏感的 Level 3 决策(改宪法)
- GOV-006 协议本来就是为这种场景设计的
- diff review 步骤天然契合 INTENT_RECORDED → INTENT_CONFIRMED 模式

**如果方案 B 落地**: board_say.py 必须在 commit 之前先调用 `record_intent.py`(记录 "我打算把 NL 'X' 翻译成 contract 'Y'"),Board 在 chat 里说"确认"对应 confirm_intent.py(写 INTENT_CONFIRMED),然后才允许 .ystar_session.json 写入。**完整的 audit chain**: NL → INTENT_RECORDED → diff → INTENT_CONFIRMED → contract write → SIGHUP → gov-mcp reload。

这个 chain **依赖 GOV-006 task #57 先实施**。如果 Board 还没让 GOV-006 落地,NL pipeline 落地会有 audit gap。**这是依赖关系**,需要在排期上明确。

### 冲突 #4: NL pipeline 跟 layered defense 的 by-design 分离

如果 NL pipeline 自动写 `.ystar_session.json`,人类失去了"一个文件就是一个手写源" 的简单心智模型。文件可能被自动化修改,可能跟 AGENTS.md (人类文档) 大幅 drift。

**这违反 layered defense 吗?** 部分。layered defense 说"两层独立演化,配置不同步是 feature"。NL pipeline 把 .ystar_session.json 变成"自动 + 手动混合写",AGENTS.md 仍然是手动写,二者 drift 会更频繁。

**Mitigation**:
- NL pipeline 写入 .ystar_session.json 时**也写 commit message-style log 到 reports/board_proposed_changes/**,记录 NL 原文 + diff + 时间戳
- 定期(每周)把这个 log 翻译成 AGENTS.md prose 更新(可以是 GOV-008 的 sub-task 或 Secretary 的 weekly 任务)
- AGENTS.md 顶部 README 段说明 ".ystar_session.json 是机器源,本文是人类源,二者可能短暂 drift,以 .ystar_session.json 为准"

这是**可以接受的复杂性**,但需要 Board 知道。

---

## Q4: 是否实现 "任何一句话不被曲解或忽略" 的目标?

**诚实回答**: **部分实现,不能完全实现**。这是一个重要的诚实陈述,Board 应该听到。

### 能实现的部分

NL pipeline + GOV-006 Intent Verification + Layered defense 三件事**组合后**,能 substantially 提高"Board 一句话被忠实执行"的概率,涵盖以下场景:

| Board 句子类型 | 解决机制 | 实现度 |
|---|---|---|
| "今天做 X" (task) | GOV-006 record_intent + Board confirm + agent 执行 | ~90%(intent 写错时 Board 一眼能看到) |
| "从今往后不许 X" (deny rule) | NL pipeline → translate → diff → Board confirm → .ystar_session.json | ~80%(取决于翻译质量) |
| "X 必须有 Y 才能做" (conditional rule) | NL pipeline 翻译 → .ystar_session.json (invariant 字段) | ~70%(条件规则更难翻译) |
| "未来 N 天内 X 是 P0" (priority/scheduling) | 部分 NL pipeline + 部分 task/calendar 系统 | ~60%(priority 和 deadline 的语义不在 IntentContract 内) |
| "我希望团队朝 X 方向努力" (value/direction) | **NL pipeline 不能解决** | 0%(value 不能转 deterministic rules) |

**总和评估**: 大约 70-80% 的 Board 句子能被结构化捕捉。这是 substantial 的进步(目前接近 0% 自动化),但不是 100%。

### 不能实现的部分

**1. 模糊语义不能确定化**

"小心一点,production database 不要乱动"
- "小心一点" 是态度,不是规则
- "乱动" 是主观判断,不是 deterministic 谓词
- 没有任何 translate_to_contract 能把这变成 ALLOW/DENY 函数

**Mitigation**: Board 得自己在 NL pipeline 反馈"翻译失败,请用更具体的句子"时改写。这不是缺陷,是诚实的边界。

**2. 价值观陈述不能 enforced**

"我们要诚实,不要给 Board 看美化数据"
- 这是价值观,不是 rule
- 可以 monitored (CIEU 审计 fabrication 事件),但不能 prevented at check() time

**Mitigation**: 价值观陈述应该归 AGENTS.md 的 prose 段,**不该走 NL pipeline**。NL pipeline 拒绝接收非 deterministic-rule 句子,直接告诉 Board "这条建议归 AGENTS.md 的人类文档段,不是 .ystar_session.json 的机器规则段"。

**3. LLM 翻译错误**

LLM 不是完美翻译器。Board 说 "禁止动 X",LLM 可能翻译成 "禁止 read X" 或 "禁止 write X",取决于 prompt 和模型。**这是不可避免的失败模式**。

**Mitigation**: 强制 diff review。Board 在确认前必须看到 LLM 翻译的具体 contract 字段。如果 LLM 翻译错了,Board 在 diff 里能看到,说"调整: 我说的是禁止 write 不是禁止 read",NL pipeline 重新翻译 + 重新 review。这是 human-in-loop。

**4. Board 自己的歧义**

有时 Board 说话本身就有歧义。"production database" 指哪个?prod-1 还是 prod-2?"动" 指 read 还是 write?**翻译器没法消除 Board 自己的歧义**。

**Mitigation**: 翻译器在 diff 里显式标注 ambiguity:"Board 的 'production database' 我翻译成 contract 字段 only_paths=['/var/db/prod-1', '/var/db/prod-2'],如果你只想限制 prod-1 请调整"。Board 看到歧义被 surface 后,在 chat 里 disambiguation。

### 终极诚实陈述给 Board

**"任何一句话不被曲解或忽略"是一个 aspirational 目标,不是一个 binary 可达成状态**。

NL pipeline 能把这个目标推进 60-80%,**主要靠 4 个机制叠加**:
1. **NL pipeline 让 Board 的话进入正式翻译流程**(不再被 agent 听完就忘)
2. **diff review 让 LLM 翻译错误被 Board 一眼发现**(不再 silent failure)
3. **GOV-006 INTENT_RECORDED 让 task-level 解读偏差被审计**(catch 非规则层的 misunderstanding)
4. **Iron Rule 1 让确认后的 contract 在运行时不可被曲解**(check() 是 deterministic)

**剩下的 20-40%** 是:
- 模糊语义(不能 deterministic 化)
- 价值观陈述(应归 prose 不归 rules)
- Board 自己的歧义(需要双向 disambiguation)
- LLM 翻译的 false negative(rules 没被生成,Board 没注意到 review 不全)

这 20-40% **不能靠任何工具完全消除**,只能靠 Board 自己保持注意力和 Secretary 的周审计。**承认这个边界比假装"100% 解决" 更可信**。

---

## 系统集成架构(如果方案 B 落地)

```
┌─────────────────────────────────────────────────────────────────┐
│ Board chat input                                                │
│ "从今往后任何 agent 不许动 production database 没我确认"        │
└────────────────────────────────┬────────────────────────────────┘
                                 │
                                 ▼
┌─────────────────────────────────────────────────────────────────┐
│ scripts/board_say.py (NEW, ~200 行)                             │
│ - 调 record_intent.py 写 INTENT_RECORDED (依赖 GOV-006 task#57) │
│ - 调 translate_to_contract(text, api_call_fn=anthropic_api)     │
│ - 拿到 contract dict                                            │
│ - 计算 diff vs 当前 .ystar_session.json                         │
│ - 写 reports/board_proposed_changes/YYYY-MM-DD-HHMMSS.md        │
│ - 在 chat 里展示 diff + 等 Board 说"确认"                       │
└────────────────────────────────┬────────────────────────────────┘
                                 │
                            Board confirms
                                 │
                                 ▼
┌─────────────────────────────────────────────────────────────────┐
│ board_say.py 后半段                                             │
│ - 调 confirm_intent.py 写 INTENT_CONFIRMED                      │
│ - merge contract dict 进 .ystar_session.json (atomic write)     │
│ - kill -HUP $(pgrep -f gov_mcp) 触发 gov-mcp reload             │
│ - 写 CIEU CONTRACT_UPDATE 事件 (新事件类型)                     │
│ - 输出 success 报告                                             │
└────────────────────────────────┬────────────────────────────────┘
                                 │
                                 ▼
┌─────────────────────────────────────────────────────────────────┐
│ gov-mcp (PID 62861) 收到 SIGHUP                                 │
│ - 重新 read .ystar_session.json                                 │
│ - 重建 active_contract                                          │
│ - 通知 in-flight clients 通过 SSE event "contract_changed"      │
│ - 后续 gov_check 走新规则                                       │
└─────────────────────────────────────────────────────────────────┘

并行: ystar Python hook 是 stateless 的,每次 PreToolUse 都读最新
.ystar_session.json,不需要 reload 信号,自然 pickup 新规则.
```

**关键依赖**:
- GOV-006 task #57 必须先实施(record_intent + confirm_intent)
- Y-star-gov 必须支持 LLM api_call_fn(`translate_to_contract` 现在支持,但需要测试 anthropic API key 注入路径)
- gov-mcp 必须接 SIGHUP handler(新加,~20 行)
- .ystar_session.json schema_version: "1.0" 必须先存在(GOV-007 Step 2 的前置)

**新文件**:
- `scripts/board_say.py` (~200 行,主流程)
- `reports/board_proposed_changes/` 目录 + 一个 markdown template
- gov-mcp 内部新增 SIGHUP handler (~20 行)

---

## 推荐结论给 Board

**Q1 (可行?)**: ✅ Yes,所有组件存在,4-5 天工程,跨 3 repo

**Q2 (反事实合理?)**: ✅ 合理,但**强烈建议 Board 显式选方案 B(一起做)还是方案 C(拆开做)**,不要让 Ethan 默认走 B。我个人推荐 C,理由:错误隔离 + gov-mcp 0.2.0 release 不延迟 + GOV-005 Finding 4 文档可以专门更新。

**Q3 (系统冲突?)**: ⚠️ 4 个 alignment 问题,全部可以处理但需要 Board 知道:
- Finding 4 layered defense 的字面表述需要更新(从"两个 source"到"两个 enforcement points")—— 文档工作,不是设计冲突
- GOV-005 第七条 反事实提案规范跟 NL pipeline 的关系需要明确(diff review 是反事实的 instantiation)
- GOV-006 INTENT 流程是 NL pipeline 的依赖(必须先实施 task #57)
- AGENTS.md ↔ .ystar_session.json drift 会加速,需要 Secretary weekly 维护机制

**Q4 (功能目标实现度?)**: ⚠️ **70-80% 实现,不可能 100%**。这个 honest 边界 Board 应该听到:
- task-level 偏差(GOV-006 task #57 解决): ~90%
- deny rule (NL pipeline 解决): ~80%
- conditional rule: ~70%
- value/direction 陈述: 0%(归 AGENTS.md prose,不归 rules)
- LLM 翻译错误: 必然存在 false positive 和 false negative,靠 diff review human-in-loop 兜底

---

## Open questions for Board (5 个,等回答)

1. **方案 B vs 方案 C**: Board 倾向"一起做" (B, 5 天 + delay 0.2.0 release) 还是"拆开做" (C, 1+5 天 + 0.2.0 不延迟)?
2. **NL pipeline LLM provider**: Anthropic API (Claude) 还是 OpenAI 还是其它?需要 API key 配置 + 成本控制(每次 board_say 大约 1k-3k tokens)
3. **依赖排序**: NL pipeline 依赖 GOV-006 task #57 (intent verification)。Board 是否同意 task #57 必须先实施,然后才启动 NL pipeline?
4. **Finding 4 文档更新**: 我现在就更新 INTERNAL_GOVERNANCE.md 的"分层治理架构"段(从 source 分离 → enforcement point 分离),还是等 Step 2 实施时一起更新?
5. **NL pipeline 失败回退**: 如果 LLM 翻译完全失败(API down, parse error),board_say.py 该怎么办?
   - A. Refuse,告诉 Board 重新说一遍
   - B. Fallback 到 regex translate_to_contract(可能 confidence 低,但有总比没有好)
   - C. Save NL 原文到 reports/pending/,等 Secretary 手动翻译

---

## 严格遵守 GOV-006 协议(尽管它还没实施)

**我没动一行代码**。**我没改 .ystar_session.json**。**我没碰 gov-mcp 任何文件**。**我没创建 board_say.py**。**我没改 Y-star-gov translate_to_contract**。

本提案完成于 2026-04-09 ET 同一 session,deliverable 是 1 个 markdown research 文档(`reports/cto/nl_to_contract_pipeline_feasibility.md`)。Board 看完后告诉我 5 个 open questions 的答案,然后我才启动 Step 2(无论方案 B 还是 C)。

这是 Y\* Bridge Labs 第二次实践 GOV-006 intent verification 协议的精神(第一次是 GOV-007 Step 1 提案),**Board 在 directive 里字面要求 "首先验证是否可行"** —— 这就是 record_intent 阶段。我现在交付 intent 内容,等 Board 的 confirm 信号。

---

**End of feasibility study.** 等 Board 决定:
1. 方案 B 还是 C
2. LLM provider
3. 依赖排序
4. Finding 4 文档更新时机
5. NL pipeline 失败回退策略
