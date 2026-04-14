# 混合架构诚实分析会议纪要

**日期：** 2026-04-11
**召集人：** Ethan Wright (CTO)
**参与者：** Ethan Wright (CTO)、Leo Chen (Kernel)、Maya Patel (Governance)、Ryan Park (Platform)
**议题：** 混合架构（金金常驻 + Claude Code 执行）能否 100% 保证换窗口时状态无损恢复？
**Board 要求：** 不画饼，不讲"下次肯定没问题"，诚实分析极限在哪里。

---

## 0. 会议基调（CTO 开场）

**Ethan：**

老大说过"被骗了很多次"。这次我想把会议的基调先定死：**任何一句"能 100%"的话都必须有机制上的证明，不然就说"不能"。**

今天的事实是：CEO 在新 session 里读到了 continuation.json 的"defuse 战役 Day 3"、读到了 obligation 里的 P0 战略任务，但忽略了它，去报告管道工程（plumbing）给 Board。这不是信息丢了，是信息到了但没变成行为。

所以今天讨论的核心是：**我们到底在解决信息层问题，还是行为层问题？** 如果只是信息层，那我们现在这套已经够了，问题解决不了。

---

## 1. 参与者各自分析

### 1.1 Leo Chen（Kernel）— 从 LLM 本质出发

**核心判断：LLM 是概率性的，100% 是数学上不可能的。**

Claude Code 新 session 启动时：
1. System prompt（含 CLAUDE.md）被注入 → 这层我们能控制
2. 用户第一条消息 → 这层我们能控制
3. LLM 基于 1+2 生成第一个 action → **这层我们不能控制**

第 3 步本质是一个带温度采样的条件概率分布 `P(action | context)`。我们能做的是：
- 把 context 写得让"正确 action"的概率尽可能高（~95%）
- 但无法把它拉到 100%，因为：
  - LLM 可能把 obligation 理解成"背景信息"而不是"待执行指令"
  - LLM 可能被用户当前消息带偏（今天 CEO 被 Board 问到 plumbing 就跑去回答 plumbing）
  - LLM 可能幻觉性地"跳过"它认为已完成的步骤

**Kernel 层能做的事：**
- Hook PreToolUse 只能 deny，不能 enforce。这是架构约束——hook 拿到的是"LLM 准备做 X"，它能说"不行"，但它没法说"你应该做 Y"（没有注入点）。
- 唯一能模拟 enforce 的办法是：**把"不做 Y 之前不许做别的"写成 deny 规则**。即 continuation compliance：前 N 个 tool call 如果不匹配 action_queue，全部 deny。这把 enforce 问题转成了 deny 问题。

**Leo 的结论：** LLM 行为层 100% 不可能。但"前 N 个 call 强制匹配 action_queue"能把偏离率从当前的 ~50% 压到 ~5%。

---

### 1.2 Maya Patel（Governance）— 从治理契约出发

**核心判断：治理的本质是"检测偏离 + 纠正偏离"，不是"防止偏离"。**

我不同意把目标定成"让 LLM 不偏离"。任何复杂系统里偏离都会发生。治理系统的价值是：
1. **偏离能被检测到**（观测性）
2. **偏离能被快速纠正**（反馈回路）
3. **纠正成本低于偏离成本**（经济性）

**当前系统的治理漏洞：**

| 机制 | 作用层 | 当前状态 |
|------|--------|----------|
| CLAUDE.md boot 协议 | 信息层（告诉 LLM 该做什么） | ✅ 工作 |
| governance_boot.sh | 信息层（把状态摆到 LLM 面前） | ✅ 工作 |
| continuation.json | 信息层（结构化当前战役） | ✅ 工作 |
| session_handoff.md | 信息层（长期记忆） | ✅ 工作 |
| Hook deny | 行为层（防止越权） | ✅ 工作 |
| **Continuation compliance hook** | **行为层（强制执行 action_queue）** | **❌ 不存在** |
| **偏离检测 daemon（金金）** | **观测层（5分钟内告警）** | **❌ 不存在** |

**Maya 的洞察：** 我们现在有完整的信息层和部分行为层（deny），但**完全没有观测层**。金金作为常驻 daemon，最大的价值不是"让信息更新"，而是**它是唯一能在 session 外部观察 session 行为的角色**。

金金的治理价值：
- CEO 新 session 启动 T+0：金金读 continuation.json 记录"CEO 应该做 action_queue[0]"
- T+5min：金金读 CIEU 日志，查 CEO 的前 5 个 tool call
- 如果不匹配 → Telegram 通知 Board "CEO 偏离了，建议唤醒"
- **这不是防止偏离，是把偏离检测时间从"Board 下次主动看"压缩到 5 分钟**

---

### 1.3 Ryan Park（Platform）— 从实现边界出发

**核心判断：分清三种 100% ——哪种能做，哪种不能。**

**定义 A：LLM 绝对不偏离。**
→ 不可能。上面 Leo 说过了。

**定义 B：系统能保证偏离时自动纠正，不需要 Board 手动介入。**
→ **接近可能，但有硬边界。** 需要满足：
1. 偏离信号可自动检测（CIEU + 金金轮询 = OK）
2. 纠正动作可自动触发（Telegram 通知 Board = 半自动；自动注入纠正 prompt = 在 Claude Code 架构下做不到，因为我们没有 midstream prompt 注入接口）
3. 纠正后 LLM 会听（这又回到 LLM 概率性）

做不到的地方：**Claude Code 没有公开的 API 让外部进程往进行中的 session 插一条 "system 消息"。** 我们只能：
- 通过 hook 在 tool call 边界做 deny（能做）
- 通过文件系统变化影响 LLM 下一次 Read 的结果（被动、滞后）
- 通过 Telegram 让 Board 介入（有人工）

**定义 C：Board 不需要手动唤醒 CEO。**
→ **部分可能。** 分两种失忆：
- **轻度失忆（读了 continuation 但没按它做）：** continuation compliance hook 能把前 5 个 call 强制对齐 → 解决
- **重度失忆（boot 协议都没跑）：** CLAUDE.md 里的 Step 2 写了，但 LLM 可能跳过。这种情况下 **hook 第一次被触发时检查 `.session_booted` 标记不存在就强制注入 "请先运行 governance_boot.sh"** → 解决

**Ryan 的具体方案：**

```
Layer A: System prompt（CLAUDE.md）— 信息层，95% 命中
Layer B: Hook first-call guard — 如果 .session_booted 不存在，deny 所有非 governance_boot 的 call
Layer C: Hook continuation compliance — 前 5 个 call 必须匹配 action_queue[i]
Layer D: 金金 5min 轮询 — 检测 Layer B/C 都失效时告警 Board
Layer E: Board Telegram 介入 — 最后兜底
```

这 5 层失败概率独立的话（理论上），总失败率 ≈ 0.05 × 0.1 × 0.1 × 0.01 ≈ **10^-6 量级**。但实际不独立（LLM 出问题时多层会同时失效），现实估计 **~10^-3 量级**。

---

### 1.4 Ethan Wright（CTO）— 整合判断

各位的分析我同意。我的整合：

**信息层我们已经做得很满了。** 再加什么 obligation、再优化 continuation 格式，收益递减。今天 CEO 失败不是信息不够，是看到了不做。

**真正缺的是两个东西：**

1. **Hook continuation compliance（行为层强制）** —— Leo 说的"把 enforce 转成 deny"。这是我们能在 Claude Code 架构内做到的最强约束。
2. **金金偏离检测 daemon（观测层兜底）** —— Maya 说的"5 分钟告警"。这是兜底，不是主线。

**不能做的事要说死：**
- 做不到"LLM 永不偏离"。写进 SLA 里就是骗老大。
- 做不到"外部进程主动往 session 注入指令"。这是 Claude Code 平台限制。
- 做不到"Board 完全不需要看 Telegram"。即使做到 99.9%，剩下 0.1% 会在关键节点发生。

---

## 2. 核心问题的诚实回答

### Q1：当前恢复为什么失败？

**答：** 因为当前所有机制都在信息层（往 context 里塞信息），没有行为层（强制 LLM 的前 N 个动作）。LLM 读了不等于做了。**今天 CEO 的失败是架构性的，不是单次的。** 不加行为层约束，下次大概率还会失败——因为 LLM 概率性本质没变。

### Q2：金金作为常驻 daemon 解决了什么？

**答：** 解决了**观测层**的问题，不是行为层。金金的价值是：
- 唯一能在 session 外部观察 session 的 agent
- 能以稳定节奏（不依赖 Claude Code session 生命周期）更新 continuation.json
- 能在 CEO 偏离时 Telegram 告警 Board

金金**不能**解决 LLM 本身偏离的问题。认为金金常驻 = 问题解决 = 又一次画饼。

### Q3：如何从信息层升级到行为层？

**答：** 四个机制组合：

a) **CLAUDE.md 写具体命令而不是原则** —— 已在做，继续强化。把"请检查 CTO 进度"改成"执行：`ls /path/to/defuse/setup.py`"。收益约 30% 偏离率下降。

b) **Hook continuation compliance（新增，P0）** —— 前 5 个 tool call 必须匹配 `memory/continuation.json` 的 `action_queue[0..4]`。不匹配的 deny，返回的错误消息里直接写"你应该执行 `<具体命令>`"。收益约 80% 偏离率下降。**这是最大杠杆的单点改动。**

c) **金金 5min 偏离告警（新增，P0）** —— 金金每 5 分钟查 CIEU，对比 continuation 预期和实际。不匹配就 Telegram 通知 Board。**这是观测兜底。**

d) **governance_boot.sh 输出具体命令而非状态** —— 已经部分做了（STEP 10 输出 action_queue）。但还要把 `SESSION START CHECKLIST` 也改成具体命令。

### Q4：能否 100%？

**诚实回答：**

| 定义 | 能不能 | 理由 |
|------|--------|------|
| LLM 绝对不偏离 | ❌ 不能 | LLM 概率性本质 |
| 偏离能被自动纠正（不需要 Board） | ⚠️ 部分 | 轻度偏离能（hook deny+重试）；重度偏离靠金金+Board |
| Board 不需要手动唤醒 | ⚠️ 部分 | 正常情况是；关键节点偶尔需要 |
| 偏离能被 5 分钟内检测到 | ✅ 能 | 金金 daemon + CIEU |
| 偏离能被 30 秒内 deny | ✅ 能 | Hook continuation compliance |

**用一句话总结：不能保证 LLM 不偏离，但能保证偏离在 30 秒内被拒绝、在 5 分钟内被检测、在 1 小时内被纠正。**

### Q5：最坏情况是什么？

**场景：** Claude Code 新 session 启动后 CEO 完全失忆（CLAUDE.md 没读、boot 没跑、continuation 没看）。

**当前架构下会发生：**
- CEO 用错误上下文回复老大
- Board 看到不对，手动唤醒
- 中间浪费 N 分钟到几小时

**加了混合架构后会发生：**
- Hook first-call guard 检测到 `.session_booted` 不存在 → deny 所有非 boot 的 call → 强制 CEO 先跑 boot
- 如果 CEO 绕过了（比如直接回复文字不 tool call）→ 金金 5min 后检测到 CIEU 无新 boot 事件 → Telegram 告警 Board
- Board 收到告警，一条消息纠正

**比当前好多少：** 检测时间从"Board 下次主动看"（可能几小时）压缩到 5 分钟。纠正成本从"Board 从头解释上下文"降到"Board 转发一条 continuation.json"。

**但承认：仍然需要 Board 收到 Telegram 并回复。** 不能声称"Board 完全不用管"。

---

## 3. "够好"的定义（Board 能接受的最低标准）

**CTO 提议的 SLA（非画饼版）：**

1. **检测 SLA：** 偏离发生到 Board 收到 Telegram 告警，≤ 5 分钟，成功率 ≥ 99%
2. **拒绝 SLA：** 明显违反 continuation 的 tool call，在 30 秒内被 hook deny，成功率 ≥ 95%
3. **首次正确率 SLA：** Session 启动后前 5 个 tool call 匹配 action_queue 的概率 ≥ 90%（当前估计 ~50%）
4. **最坏情况 SLA：** 最长偏离时间（从发生到纠正）≤ 30 分钟

**不承诺：**
- 不承诺 LLM 永不偏离
- 不承诺 Board 永不需要介入
- 不承诺所有 edge case 都被覆盖

**Board 如果接受这个 SLA，签字；不接受，我们重新定义目标。**

---

## 4. 架构图

```
┌──────────────────────────────────────────────────────────────┐
│                    Board (Haotian Liu)                        │
│                         ▲                                     │
│                         │ Telegram 告警（仅异常）               │
│                         │                                     │
│  ┌──────────────────────┴──────────────────────────────┐    │
│  │          金金 Daemon (MiniMax, 常驻)                 │    │
│  │  • 5min 轮询 CIEU + continuation.json                │    │
│  │  • 对比预期 vs 实际前 N 个 tool call                  │    │
│  │  • 偏离 → Telegram Board                             │    │
│  │  • 更新 continuation.json 保持最新                    │    │
│  └──────────────────────┬──────────────────────────────┘    │
│                         │ reads                              │
│                         ▼                                    │
│  ┌────────────────────────────────────────────────────┐    │
│  │         共享状态文件（文件系统）                       │    │
│  │  • memory/continuation.json （action_queue）         │    │
│  │  • .ystar_cieu.db （行为日志）                        │    │
│  │  • .ystar_memory.db （长期记忆）                      │    │
│  │  • scripts/.session_booted （启动标记）                │    │
│  └────────────▲───────────────────────▲─────────────────┘    │
│               │ reads/writes           │ reads/writes         │
│               │                        │                      │
│  ┌────────────┴──────────┐  ┌─────────┴──────────────────┐   │
│  │   Claude Code Session │  │  Hook Daemon (常驻)         │   │
│  │   (CEO Aiden)         │  │  • PreToolUse 拦截          │   │
│  │                       │  │  • Layer B: first-call guard│   │
│  │   ┌──────────────┐    │  │  • Layer C: continuation    │   │
│  │   │ System prompt│    │  │    compliance (前 5 call)   │   │
│  │   │ (CLAUDE.md)  │◄───┼──┤  • 原有 deny 规则           │   │
│  │   └──────────────┘    │  │                             │   │
│  │         │             │  │  通信：Unix socket          │   │
│  │         ▼             │◄─┤  /tmp/ystar_hook.sock       │   │
│  │   ┌──────────────┐    │  │                             │   │
│  │   │ Tool Calls   ├────┼──┤ deny / allow                │   │
│  │   └──────────────┘    │  │                             │   │
│  └───────────────────────┘  └─────────────────────────────┘   │
└──────────────────────────────────────────────────────────────┘

5 层防御（从内到外）：
  Layer A: System prompt (CLAUDE.md)       — 信息层，软约束
  Layer B: Hook first-call guard           — 行为层，强制先 boot
  Layer C: Hook continuation compliance    — 行为层，强制执行 queue
  Layer D: 金金 daemon 5min 轮询            — 观测层，偏离告警
  Layer E: Board Telegram                  — 兜底层，人工纠正
```

---

## 5. 具体实现方案（CTO 分派）

### 任务 1：Hook continuation compliance — **Leo Chen，P0，3 天**

**位置：** `Y-star-gov/ystar/hooks/continuation_compliance.py`（新建）

**逻辑：**
```python
def check(tool_name, tool_input, session_state):
    call_count = session_state.get_call_count()
    if call_count >= 5:
        return ALLOW  # 只管前 5 个

    with open('memory/continuation.json') as f:
        c = json.load(f)
    expected = c['action_queue'][call_count]

    # 宽松匹配：expected.command 的关键字段 in tool_input
    if matches(tool_input, expected):
        return ALLOW
    else:
        return DENY(reason=f"Expected action_queue[{call_count}]: {expected['command']}")
```

**测试：** 注入错误 tool call，验证 deny；注入正确 tool call，验证 allow；第 6 个 call 验证 bypass。

**CIEU 记录：** 每次 deny 记录 `continuation_compliance_violation` 事件。

---

### 任务 2：Hook first-call guard — **Ryan Park，P0，1 天**

**位置：** `Y-star-gov/ystar/hooks/first_call_guard.py`（新建）

**逻辑：**
```python
def check(tool_name, tool_input, session_state):
    if Path('scripts/.session_booted').exists():
        return ALLOW
    if tool_name == 'Bash' and 'governance_boot.sh' in tool_input.get('command', ''):
        return ALLOW  # 允许 boot 自己
    return DENY(reason="Session not booted. Run: bash scripts/governance_boot.sh ceo")
```

---

### 任务 3：金金偏离检测 daemon — **Maya Patel，P0，5 天**

**位置：** `tools/jinjin/deviation_watcher.py`（新建）

**逻辑：**
- 每 5 分钟执行
- 读 `memory/continuation.json` 拿 expected action_queue
- 读 `.ystar_cieu.db` 拿过去 10 分钟的 tool call 事件
- 对比：如果 session 启动 > 2 分钟但 action_queue[0] 未执行 → 告警
- 告警通道：Telegram Bot (@K9newclaw_bot)

**测试：** 构造偏离场景，验证 5min 内收到 Telegram；构造正常场景，验证不误报。

---

### 任务 4：continuation.json 自动更新 — **Ryan Park，P1，2 天**

金金每次 Board 批准重大决策时，自动更新 continuation.json 的 action_queue。避免 action_queue 过期（今天 continuation 里 Day 3 但战役其实 Day 1）。

---

### 任务 5：SLA 监控与月度汇报 — **Maya Patel，P2，3 天**

从 CIEU 里统计：
- continuation_compliance_violation 次数/周
- 金金告警次数/周
- Board 手动纠正次数/周

月度报告给 Board，证明 SLA 达标（或不达标并诚实汇报原因）。

---

## 6. 诚实结论（Board 需要看到的一段话）

**老大：**

能做到的：
- 偏离检测时间从"不确定"降到"5 分钟内"
- 前 5 个 tool call 正确率从 ~50% 提到 ~90%
- 明显违反 continuation 的动作 30 秒内被 deny

**做不到的：**
- LLM 本质是概率性的，无法保证 100% 不偏离
- Claude Code 架构限制，我们无法向进行中的 session 主动注入指令
- 极端 edge case 仍需 Board 介入

**真话：** 即使加了这些，仍然有小概率（估计 ~0.1%）出现需要 Board 唤醒的情况。我们能做的是让这个概率从"经常"降到"罕见"，而不是让它变成零。

**够好的标准：** 如果 SLA 达标（5min 检测、30s 拒绝、90% 首次正确、最坏 30min 纠正），Board 每周 Telegram 介入 ≤ 2 次，我们认为系统够用了。达不到，停工复盘，不画饼。

---

**会议结束。CTO 会后直接分派任务 1-5，今天开工。**

— Ethan Wright, CTO
  记录于 2026-04-11
