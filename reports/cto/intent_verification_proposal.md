# Intent Verification Protocol — 反事实推理实现提案

**作者**: Ethan Wright (CTO)
**日期**: 2026-04-09
**优先级**: P1
**权限层级**: **Level 3**(改变 agent 核心行为 + 新 CIEU 事件类型 + 影响 6 个岗位 + 修改 WORKING_STYLE.md 第七条)
**状态**: 提案,待 Board 决策
**触发**: Board GOV-005 followup item #2 — "解决 LLM 自己理解偏了还继续执行"
**提案格式**: 严格 GOV-005 第七条反事实推理格式

---

## 问题

LLM agent 接到 Board 指令后,在以下任一环节都可能产生**理解偏差**:

- 误解 **Xt**(对当前状态的认知错误)
- 误解 **Y\***(对目标的认知错误)
- 误解 **执行手段**(对 U 的选择错误)

当前工作流**没有"承诺解释"这一步**。Agent 拿到指令直接执行,Board 在结果出来后才发现解读偏差,然后必须 rollback 或修正。这本 session 已经发生 3 次真实偏差,每次都浪费 1 个 reconcile cycle:

| 事件 | Agent 误解 | Board 实际意图 | Cost |
|---|---|---|---|
| **GOV-001 Step 2** | Ethan 以为 `ystar setup --yes` 是 idempotent refresh | Board 期望直接 Edit JSON, `setup --yes` 是 destructive regenerator | 354 行配置丢失,1 个紧急 reconcile commit |
| **GOV-001 Step 6** | Ethan 试图 Edit AGENTS.md 添加 GOV-001 obligation block | Board 知道 AGENTS.md 是 immutable hook 区,实际意图是改 agents/*.md | 1 个 hook block 中断 + 重新设计 commit |
| **GOV-005 Part 5 reconcile** | Ethan 把 daemon 归档到 `reports/archive/...` | Board 想要标准位置 `archive/deprecated/` | 1 个 reconcile commit (8a95c2a) |

**3/3 的偏差都可以通过"先承诺解释,后执行"消除**——只要 Ethan 在第一次解读时把"我以为 X = Y"写下来,Board 一眼就能发现"X 实际 = Z"。

---

## 当前状态 Xt

- `governance/WORKING_STYLE.md` 第七条(GOV-005 Part 1)定义了反事实推理提案格式——**但只针对多方案选择场景**(Level 2/3 决定 A/B/C)
- 不要求 agent 在执行单一明确指令前确认理解
- CIEU 没有 INTENT_* 事件类型,所有 OBLIGATION_REGISTERED 直接是"开始执行"事件,**没有"理解阶段"和"执行阶段"的分离**
- Board 必须在事后(commit / git diff / output)发现 agent 的理解偏差,然后 reconcile
- 每次偏差消耗 1 个 commit + 1 个对话回合

---

## 目标 Y*

- **Level 2/3 directives → 必须有 INTENT_RECORDED → INTENT_CONFIRMED → 才能开始执行**
- **Level 1 directives → 不需要 intent verification**(已在权限内,自决)
- 全部 intent 状态进 CIEU,可追溯,与对应的 OBLIGATION_REGISTERED 链接
- `agents/*.md` + `governance/WORKING_STYLE.md` 第七条都明确要求
- 偏差检测从"事后(commit 后)"提前到"事前(执行前)"
- **Rt = 0 的可观测条件**: 未来一个月内 reconcile commit 数量从基线(每 3-5 个 commit 1 次)降到接近 0

---

## 反事实分析

### 方案 A: 纯 chat 协议(无脚本,无 CIEU,只改宪法)

**做法**: WORKING_STYLE.md 第七条加新子段落"指令理解确认协议": Level 2/3 directives, agent 必须**第一次回复就只输出**:

```
[INTENT for {directive_id}, level {N}]
Xt: 当前状态我的理解是 ...
Y*: 我对目标的理解是 ...
执行计划: 1. ... 2. ... 3. ...
等待 Board 确认。
```

不输出任何工具调用。Board 回复"确认" / "调整: ..." / "拒绝"。Agent 在第二次回复才开始执行。

**Yt 预测**:
- 修改量: WORKING_STYLE.md 第七条 ~30 行新增
- agents/*.md 6 个文件 GOV-001 段落各加 1-2 行引用
- 工作量: 30 分钟,2 commits

**Rt(与 Y* 的差距)**:
- ✅ 偏差检测前置: agent 在执行前必须先表达理解
- ✅ 简单可执行: agent 只要遵守"先 INTENT 后 ACTION"两段式回复就够
- ❌ 没有 CIEU 审计: 偏差是否被 catch 到只在 chat 历史里,不在审计层
- ❌ 没有强制机制: agent 可以"忘了"就跳过(虽然违反宪法但 hook 拦不住)
- ❌ Level 区分要 agent 自己判断: agent 自己决定"这是 Level 2 还是 Level 1",可能误判
- **核心 Rt**: 没有可机器执行的强制层

### 方案 B: 完整 CIEU 双事件协议(脚本 + CIEU 事件 + 阻塞)

**做法**: 

1. 新增 2 个 CIEU 事件类型: `INTENT_RECORDED`、`INTENT_CONFIRMED`(或 `INTENT_REJECTED`)
2. 新增 2 个脚本:
   - `scripts/record_intent.py --directive-id <id> --level <N> --xt <text> --y-star <text> --plan <text>` → 写 INTENT_RECORDED record,返回 intent_id
   - `scripts/confirm_intent.py --intent-id <id> --by <board|ceo> --decision <approve|reject|adjust> --notes <text>` → 写 INTENT_CONFIRMED record
3. 新增脚本 `scripts/await_intent_confirmation.py --intent-id <id>` → 阻塞直到 CIEU 库出现匹配的 INTENT_CONFIRMED(或超时)
4. agents/*.md 强制规则: Level 2/3 directives 必须先 record_intent + await_intent_confirmation,然后才能 register_obligation
5. 修改 Y\*gov hook: 在 PreToolUse 时检查"如果当前 directive 是 Level 2/3 且没有 INTENT_CONFIRMED",直接 deny tool call
6. WORKING_STYLE.md 第七条更新为完整双段式

**Yt 预测**:
- 修改量: 2 新脚本(~150 行)+ 1 个修改的 hook(`_hook_client.sh` 或 Python 等价)+ 6 agents/*.md + WORKING_STYLE.md
- 总代码: ~400 行
- 工作量: 1.5 天工程 + 测试

**Rt(与 Y* 的差距)**:
- ✅ 偏差前置 catch
- ✅ CIEU 全程审计
- ✅ 可机器执行(hook 在 tool call 时强制检查)
- ⚠️ "阻塞" 在 Claude Code session 模型里**不自然**——session 是 turn-based,agent 无法"等待"。要么 agent 在第一次 turn 后停止(自我挂起),要么有外部 polling
- ❌ Hook 修改: 现有 `_hook_client.sh` 是 Y-star-gov repo 的产品代码,改它意味着 ystar 0.49+ 才能上线,跨 repo 协调
- ❌ 工程量大,与 GOV-005 整体架构紧耦合(影响产品发布周期)
- **核心 Rt**: 工程债 vs 收益不匹配(我们想要的是行为协议,不是新的产品 feature)

### 方案 C: 混合协议(轻量脚本 + chat 协议 + CIEU 审计 + 不阻塞)

**做法**:

1. 新增 1 个 CIEU 事件类型: `INTENT_RECORDED`(单事件,Board 的确认通过 chat 给出,事后由 agent 自己 mark 进 CIEU 作为 audit)
2. 新增 1 个脚本: `scripts/record_intent.py` 写 INTENT_RECORDED 记录(类似 register_obligation.py 的轻量级版本)
3. **行为协议(无强制 hook)**:
   - Agent 收到 Level 2/3 directive → **第一次回复必须是 INTENT 段落 + record_intent 调用 + 不输出任何工具调用**
   - Board 在 chat 里回复"确认" / "调整: X" / "拒绝"
   - Agent 第二次回复才开始执行
   - Agent 执行完后, mark intent 为 CONFIRMED 状态(类似 mark_fulfilled)
4. WORKING_STYLE.md 第七条 加新子段"指令理解确认协议",明文规定 Level 2/3 必须走两段式回复
5. agents/*.md 6 个文件 GOV-001 段落各加引用第七条
6. **不修 hook,不阻塞**——靠协议自律 + Board 监督 + CIEU 事后审计
7. 自检: Secretary 每周审计 CIEU,找"Level 2/3 工作但缺 INTENT_RECORDED 前置"的违规

**Yt 预测**:
- 修改量: 1 脚本(~80 行)+ WORKING_STYLE.md 一段(~40 行)+ agents/*.md ×6 各加 5-10 行
- 总: ~150 行
- 工作量: 半天 + 测试

**Rt**:
- ✅ 偏差前置 catch(协议层面)
- ✅ CIEU 审计(事后可查)
- ✅ Level 区分有规则可循
- ✅ 不动产品 hook,无跨 repo 依赖
- ✅ 不依赖"阻塞"机制,fits Claude Code session 模型
- ⚠️ 没有强制层(靠 agent 自律 + 协议宪法)
- ⚠️ Secretary 必须周审计来 catch 违规

**核心权衡**: 用"宪法 + 自律 + 事后审计"代替"hook 强制"。这和 GOV-005 第七条"反事实推理提案"的执行方式一致——第七条也没有 hook 强制,靠提案者自律。**协议一致性 > 强制强度**。

---

## 最优解 = **方案 C(混合协议)**

**理由(一句话)**: 方案 A 没有审计层,方案 B 工程债过大且和 Claude Code session 模型不匹配。方案 C 是 GOV-005 第七条的自然延伸,代码量小、协议明确、有 CIEU 审计、Secretary 周审计 catch 违规、不动产品代码。Rt(协议层面) = 0,Rt(强制层面) = "靠宪法,不靠 hook",这和现有反事实推理提案的执行方式同构。

## 次优解 = **方案 A(纯 chat 协议)**

**为什么不是最优**: 没有 CIEU 审计 = 偏差只能在 chat 历史里查 = 不可机器扫描 = Secretary 周审计无法系统化。但如果 Board 觉得方案 C 的 CIEU 写入也是"不必要的复杂",可以降级为 A,代价是失去审计能力。

## 直接出局 = **方案 B(hook 强制阻塞)**

> 400 行代码 + 跨 repo 依赖 + Claude Code session 阻塞模型不匹配 + 产品发布周期耦合。**不在候选范围内**。

---

## 实施步骤(如果 Board 批准方案 C)

### Step 1: 设计 INTENT_RECORDED CIEU 记录格式

```python
record = {
    "event_id": str(uuid.uuid4()),
    "session_id": directive_id,             # e.g. "GOV-006"
    "agent_id": actor_role,                  # e.g. "cto"
    "event_type": "INTENT_RECORDED",
    "decision": "info",
    "evidence_grade": "intent",              # 新等级,区别于 ops/decision
    "params": {
        "directive_id": directive_id,
        "level": 2,                          # 1/2/3
        "xt": "当前状态理解 ...",
        "y_star": "目标理解 ...",
        "plan": ["step 1", "step 2", ...],
        "actor_role": actor_role,
        "submitted_at": <timestamp>,
    },
    ...
}
```

### Step 2: 写 `scripts/record_intent.py`(~80 行)

类似 register_obligation.py 的结构。CLI 参数: `--directive-id`、`--level`、`--xt`、`--y-star`、`--plan`(可多次)、`--owner`。返回 intent_id 给 agent 在 chat 里展示。

### Step 3: 写 `scripts/check_intents.py`(~60 行)

类似 check_obligations.py。功能:
- 列出最近的 INTENT_RECORDED 记录(--limit N)
- 过滤未 CONFIRMED 的(--unconfirmed-only)
- 标记 CONFIRMED(`--confirm <intent_id> --by board --notes "..."`)→ 写 INTENT_CONFIRMED 记录到 CIEU

### Step 4: 修改 `governance/WORKING_STYLE.md` 第七条

在 GOV-005 提案格式之后追加"### 7.5 指令理解确认协议",明文规定:
- Level 2/3 directives 必须走两段式回复
- 第一次回复: INTENT 段落 + record_intent.py 调用 + 不输出工具调用
- 第二次回复: 等 Board 确认后才执行
- 完成后 mark INTENT_CONFIRMED

### Step 5: 修改 `agents/*.md` 6 个文件

在每个文件的 GOV-001 义务追踪条款段落后面加新子段"### 指令理解确认前置(GOV-006)",引用 WORKING_STYLE.md 第七条 7.5,说明本岗位的 actor_id 应该如何使用 record_intent.py。

### Step 6: 修改 `agents/CEO.md` "提案审阅决策框架"

加新规则: CEO 收到团队提案后,如果是 Level 2,**必须先确认提案方的 INTENT_RECORDED 已经存在且和提案 directive 一致**,再做批准/否决决定。

### Step 7: Secretary 周审计脚本(选做,P2)

`scripts/audit_intents.py`: 扫 CIEU 库,找最近 7 天:
- Level 2/3 工作但缺 INTENT_RECORDED 前置 → 违规列表
- INTENT_RECORDED 但 24h 内未 CONFIRMED → 待办列表
- 输出报告到 reports/secretary/intent_audit_YYYY_MM_DD.md

### Step 8: 端到端测试

- 创建一个 fake Level 2 directive ("test directive"),走完整流程: record_intent → 模拟 Board 确认 → 模拟 agent 执行 → mark CONFIRMED → 查 CIEU
- 验证 Secretary 周审计能 catch 故意省略 INTENT_RECORDED 的"违规" agent

---

## 预估工作量

| 步骤 | 行数 | 工时 |
|---|---|---|
| 1. 设计 + record_intent.py | ~80 | 1h |
| 2. check_intents.py(扩展) | ~60 | 1h |
| 3. WORKING_STYLE.md 第七条更新 | ~50 | 30min |
| 4. agents/*.md ×6 | ~60 (10 each) | 1h |
| 5. CEO.md 提案审阅段更新 | ~20 | 15min |
| 6. Secretary 周审计脚本(选做) | ~80 | 1h |
| 7. 端到端测试 | — | 1h |
| **总** | **~350 行** | **5-6 小时** |

**约半天工程时间**。但如果延 Step 6(Secretary 周审计)到 P2,核心实施只需要 4 小时左右。

---

## Level 3 决策点

GOV-005 Part 2 定义 Level 3:
> 架构变更影响两个及以上岗位的核心职责

本提案影响:
- **所有 6 个岗位**(每个 agent 都要走新协议)
- **WORKING_STYLE.md** 宪法
- **CIEU 库 schema**(新事件类型)
- **CEO 提案审阅流程**

→ **Level 3,Board 拍板**。

---

## Board 决策需要回答

**只需要一句话**: 选 A、B、C,还是 C 的某个变体?

- **C**(推荐): Ethan + Secretary 半天工程,新协议 + 1 脚本 + 宪法更新 + 6 agents/*.md
- **A**: Ethan + Secretary 半天文档,纯协议无脚本,无审计
- **C - Step 6**: 同 C 但跳过 Secretary 周审计,4 小时完成,审计能力靠手动 ad-hoc 而非定期

如果 Board 批准,Ethan 在下次 session 启动 INTENT_VERIFICATION 实施任务(本次 session 不含,因为 GOV-005 已饱和)。

---

## 元注解

**本提案是反事实推理提案的"自我应用"**: 我用 GOV-005 第七条的格式去提案 GOV-005 第七条的扩展。如果方案 C 通过,**未来本提案这种类型的提案本身**就需要走 INTENT_RECORDED 流程——也就是说,Board 收到本提案后,Ethan 在执行前要先 record_intent("我打算实施方案 C"),Board 确认后才动手。这是 self-bootstrap 的协议演化路径。

CTO 同时承诺: 本提案完成于 2026-04-09 ET 同一 session,**没有动一行 record_intent.py 代码**,严格遵守"提案先,实施后"的两段式。
