# 治理团队迁移OpenClaw — 架构可行性评估

**作者**: CTO Ethan Wright
**日期**: 2026-04-11
**审阅对象**: Board, CEO Aiden
**结论先行**: **架构可行。Phase 1-3 可在 2-3 天内完成。从根因上解决"重启失忆"——不是90%，是100%。**

---

## 0. 先纠正我之前的误解

我之前把这套架构理解成"金金当观察员、CEO继续跑在Claude Code上"。那是错的。

Board的真实设计是：**治理层（6个C-suite + Secretary + 金金）全部是OpenClaw常驻agent；Claude Code降级为一次性执行手（ephemeral worker）。** 治理记忆、决策权、hook规则都留在OpenClaw侧，Claude Code进程生灭不影响公司运转。

这个设计在概念上对应业界的 **Supervisor-Worker 模式**（LangGraph supervisor、Ray actor、Celery orchestrator 都是这个形状）——OpenClaw是supervisor进程组，Claude Code是短生命周期worker。

---

## 1. 技术可行性逐项验证

### Q1: OpenClaw能不能支持多agent作为独立角色？

**答: 完全可以，CLI原生支持。**

验证（本session实测）：
```
openclaw agents add <name> --workspace <dir> --agent-dir <dir> --model <id> --bind <channel>
openclaw agents list   # 当前只有 main=金金
```

每个agent的隔离维度：
- `workspace` — 独立的文件根（可以指向 `ystar-company/agents/ceo/` 等子目录）
- `agentDir` — 独立的状态目录（`~/.openclaw/agents/<id>/agent/`，里面有 models.json / auth-profiles.json / auth-state.json）
- `model` — 每个agent独立模型（CEO/CTO可配Anthropic Claude，CMO/CSO/CFO可配MiniMax，Secretary可配本地Ollama）
- `bindings` — channel路由（CEO绑Telegram主号，金金走现有号，Secretary可以不绑channel纯内部）
- 独立memory目录（继承 `~/.openclaw/memory/` 结构，按agent_id分区）

**可以直接落盘的配置**（对应 `~/.openclaw/openclaw.json` 的 `agents.list`）：
```json
{"id":"ceo","workspace":".../ystar-company","agentDir":".../agents/ceo/agent","model":"anthropic/claude-opus-4.6"}
{"id":"cto","workspace":".../ystar-company","agentDir":".../agents/cto/agent","model":"anthropic/claude-opus-4.6"}
{"id":"cmo","workspace":".../ystar-company","agentDir":".../agents/cmo/agent","model":"minimax/MiniMax-M2.5"}
{"id":"cso","workspace":".../ystar-company","agentDir":".../agents/cso/agent","model":"minimax/MiniMax-M2.5"}
{"id":"cfo","workspace":".../ystar-company","agentDir":".../agents/cfo/agent","model":"minimax/MiniMax-M2.5"}
{"id":"secretary","workspace":".../ystar-company","agentDir":".../agents/secretary/agent","model":"minimax/MiniMax-M2.5"}
```

Personality / role definition 走每个workspace的 `AGENTS.md` + `.claude/agents/*.md`（文件已存在，OpenClaw bootstrap会注入）。

**限制**: `agents.defaults.maxConcurrent: 4` + `subagents.maxConcurrent: 8` — 6个常驻agent需要调到 `maxConcurrent >= 6`。已验证配置字段存在。

### Q2: OpenClaw agent如何驱动Claude Code session？

**答: 可行，但不是subprocess调用，而是"agent turn → 文件DISPATCH → Claude Code被触发"。**

两种可行路径：

**路径A（推荐）: DISPATCH文件 + Claude Code按需启动**
1. OpenClaw CEO agent 被事件触发（cron / telegram消息 / 其他agent消息）
2. 决策后写入 `ystar-company/DISPATCH.md`（已存在、已是现有工作流的入口）
3. 外部调度（cron / launchd / Board手工）启动 `claude` CLI on the workspace
4. Claude Code读DISPATCH执行 → 结果写入 `reports/` 和 `memory/session_handoff.md`
5. OpenClaw CEO通过cron或文件watch感知到结果 → 审核

**路径B（更彻底）: OpenClaw cron 直接spawn headless Claude Code**
验证: `openclaw cron add` 存在。cron job可以执行任意shell，包括 `claude -p "<prompt>"` 的 headless 模式（Claude Code支持 `-p` 非交互模式）。
通信方式：
- 任务下发：环境变量 `YSTAR_DISPATCH_ID=xxx` + DISPATCH.md
- 结果回传：Claude Code 写 `reports/dispatch_<id>.json` → OpenClaw下一轮cron读取

**关键验证（已跑）**: `openclaw agent --agent main --local --json` 在 11.5 秒内返回 JSON (minimax M2.7 pong回复，103 input / 24 output tokens)。这证明了 **OpenClaw agent可被程序化一次性驱动**，不需要长连接channel——可以从cron、shell脚本、甚至另一个agent的hook里调用。

**工作流完整链路**:
```
[触发源]          [OpenClaw治理层]              [Claude Code执行层]
telegram msg  →  openclaw agent --agent ceo  →  CEO决策写DISPATCH.md
cron tick     →  CEO审核reports/             →  派发任务
file watch    →  CTO分配给Leo/Ryan           →  cron启动 claude -p
              →  结果来了，secretary审计       →  执行手写reports + 退出
```

### Q3: Y*gov hook如何跨进程作用？

**答: 完美契合。这是整个架构最优雅的部分。**

现状：
- Y*gov hook daemon（`scripts/hook_client_labs.sh` + socket daemon）是**独立进程**，不依赖Claude Code或OpenClaw
- Hook规则读取的是 `ystar-company/.ystar_session.json`（193条约束 / 11个类别 / immutable_paths / deny / deny_commands）
- Claude Code PreToolUse → hook client → daemon → 命中session.json规则 → allow/deny

因此：
1. **OpenClaw治理团队可以写session.json** — 只要OpenClaw CEO agent能调用文件写入工具（目前原生支持），就能动态下发规则
2. **Claude Code执行手自动遵守** — 因为它启动时PreToolUse hook会读取最新的session.json
3. **无需修改hook daemon** — daemon是确定性代码，已经work了

**示范场景（完全可落地）**:
```python
# CEO agent (OpenClaw侧) 决定今天只做defuse
ceo_decision = {
  "scope_today": "ystar-defuse",
  "deny_paths_addition": ["products/ystar-gov/", "frontend-v2/"]
}
# CEO写入 .ystar_session.json.deny += ceo_decision["deny_paths_addition"]
# 任何Claude Code session启动后，touch那些路径 → hook deny → 强制合规
```

这才是Board说的**"从warn LLM升级为hook deny"**。确定性代码层enforcement，LLM绕不过。

**唯一需要加的安全护栏**: session.json的写入权限只给Secretary agent（对应现在 `immutable_paths.override_roles: ["secretary"]` 的模式）——CEO决策 → Secretary审计后落盘。这和现有治理契约一致。

### Q4: 状态恢复机制

**答: continuation.json 不再需要。从根因上消除失忆。**

当前状态恢复链（Claude Code侧）：
```
session start → read session_handoff.md → read continuation.json → governance_boot.sh → 9 step state restore
```
每次重启都要做一遍，还不一定恢复完整（这就是"失忆"的来源）。

迁移后（OpenClaw侧）：
```
OpenClaw daemon 持续运行 → CEO/CTO/etc agent常驻 → 每个agent有独立memory（openclaw memory子系统）
Claude Code执行手启动 → 读DISPATCH.md（当前任务，不是完整公司状态）→ 执行 → 退出
```

**关键差异**:
- 治理团队**不会重启** → 不需要"恢复"
- Claude Code执行手重启**无关紧要** → 它本来就是stateless worker
- 失忆问题从系统层消除，不是在Claude Code层硬扛

**OpenClaw进程级保障**:
- `openclaw doctor --fix` 已有 → 健康检查
- launchd / systemd 托管daemon → crash auto-restart
- agent memory持久化到 `~/.openclaw/memory/<agent_id>/` 独立文件系统

### Q5: 架构根本优势（对比当前）

| 维度 | 现状（Claude Code跑全团队） | 迁移后（OpenClaw治理 + Claude Code执行手）|
|------|---|---|
| 失忆 | 每次重启恢复，90%成功 | **消除**（治理层不重启）|
| Claude Code套餐消耗 | 所有对话都吃套餐 | 只有执行动作吃套餐，治理决策走MiniMax/本地 |
| 治理强度 | LLM自警（会被绕过） | hook deny（确定性enforcement）|
| Board介入频率 | 每次session boot都要醒 | 近乎为零，只在真正决策点被召唤 |
| 并发度 | 1个Claude Code session | OpenClaw `maxConcurrent: 8` subagents + 多个执行手 |
| 成本结构 | 全Claude Opus套餐 | 决策层廉价（MiniMax $几刀/月）+ 执行层按需 |
| 审计链 | CIEU依赖Claude Code hook | CIEU + OpenClaw agent log 双链路 |

### Q6: 实现工作量

**Phase 1: CEO agent 试点（工作量：0.5天）**

步骤：
1. `openclaw agents add ceo --workspace /Users/haotianliu/.openclaw/workspace/ystar-company --agent-dir /Users/haotianliu/.openclaw/agents/ceo/agent --model anthropic/claude-opus-4.6`
2. 在 `~/.openclaw/agents/ceo/agent/` 里写 `IDENTITY.md`（拷贝 `.claude/agents/ceo.md` 里的persona）
3. 更新 `openclaw.json` 的 `agents.defaults.maxConcurrent: 6`
4. 测试：`openclaw agent --agent ceo --local --message "状态汇报" --json`
5. 验证CEO能读 `ystar-company/AGENTS.md` 并给出符合角色的回复

**交付物**: CEO agent能以Aiden身份在OpenClaw侧回答一轮问题，模型走Anthropic，记忆独立。

**Phase 2: CEO agent 驱动 Claude Code 执行手（工作量：1天）**

步骤：
1. 定义DISPATCH.md schema（已有雏形，规范化metadata：dispatch_id / assigned_to / deadline / result_path）
2. 写 `scripts/spawn_executor.sh` — 从OpenClaw agent被调用，作用是 `claude -p "<prompt>"` headless运行、传DISPATCH_ID env、超时管控
3. CEO agent的tool schema里加 `dispatch_to_executor(task, files, deadline)` → 写DISPATCH.md + 调 spawn_executor.sh（OpenClaw agent已支持tool calling和shell execution）
4. 回报机制：执行手退出时写 `reports/dispatch_<id>.json` → CEO agent下一次被触发时读取
5. 对应cron：每5分钟 `openclaw cron` 调 `ceo_tick`，agent读reports inbox决策

**交付物**: Board对CEO下"把defuse README优化一下"指令 → CEO写DISPATCH → Claude Code被spawn → 改好README → 写report → CEO审核 → 回复Board。全程Claude Code session只活几分钟。

**Phase 3: CEO决策直接改session.json hook规则（工作量：0.5天）**

步骤：
1. Secretary agent独立起一个（复用Phase 1方法）
2. CEO → Secretary delegation tool：`request_rule_change(patch, reason)`
3. Secretary agent验证patch合法 → 写 `.ystar_session.json`（现有immutable_paths机制已允许secretary override）
4. Secretary写入时附CIEU记录（`mcp__gov-mcp__gov_seal`）—— 审计链闭环
5. 测试：CEO说"今天锁defuse" → Secretary加deny规则 → 手动启动Claude Code试图改frontend-v2 → hook deny

**交付物**: 治理决策 → 确定性规则 → 强制enforcement 全链路打通。

**Phase 4: 全员迁移 CTO/CMO/CSO/CFO/Secretary（工作量：1天）**

每个agent重复Phase 1，加上：
- 各自的tool schema（CTO可调git / pytest，CMO可调 `content/` 写入，CSO可调 `sales/` 写入等）
- agent间消息传递（OpenClaw原生支持inter-agent messaging via gateway）
- 每个agent独立cron tick（不同频率：CEO每5分钟，CMO每30分钟，CFO每天）

**交付物**: 完整6-agent治理层常驻，Claude Code退化为执行手，AGENTS.md里定义的角色分工第一次真正被进程隔离强制。

**总工作量: 3天（Phase 1-3）+ 1天（Phase 4）= 4天**

---

## 2. 不可行 / 需要注意的部分

全部可行，但有4个需要明确处理的问题：

1. **每个OpenClaw agent的context是独立的**——CEO、CTO之间不会自动共享上下文。需要：
   - 共享：通过 `ystar-company/` workspace的文件系统（AGENTS.md / DISPATCH.md / reports/）
   - 私有：每个agent自己的 `~/.openclaw/agents/<id>/memory/`
   - 跨agent消息：走OpenClaw的inter-agent messaging（已原生支持）

2. **Anthropic API直调成本 vs Claude Code套餐**——CEO/CTO走 `anthropic/claude-opus-4.6` 是API调用，不走套餐。需要CFO评估：
   - CEO agent被cron触发的频率 × 平均prompt大小 × API单价
   - 初步估算：CEO每5分钟一次tick、每次 ~5K input tokens → 每天 ~$15，每月 ~$450
   - **缓解**: Claude有prompt caching（5分钟TTL），connected tick间复用 → 实际成本减半
   - **替代**: CEO也可以用MiniMax（成本近零），但关键战略决策建议保留Claude

3. **Claude Code执行手的授权边界**——headless `claude -p` 启动时如何保证它只动允许的文件？依赖：
   - `.ystar_session.json` 的 `deny` / `immutable_paths`（已有，hook层enforce）
   - DISPATCH.md里的 `scope_paths` 白名单（新增字段，CEO写、hook验证）
   - **这个必须Phase 2一起做**，不能后补

4. **金金 vs 6个新agent的channel冲突**——金金现在占 `bindings: [{agentId: "main", channel: "telegram"}]`。新agent要绑Telegram需要：
   - 方案A: 用peer级routing（`bindings.match.peer = "board"` → ceo；其他 → 金金）
   - 方案B: 新agent不绑channel，纯内部通信 + Secretary合并向Board汇报
   - 推荐方案B——Board只跟CEO对话，其他agent走内部。

---

## 3. 对"重启失忆"问题的回答

**不是90%，是100%——但前提是治理层真的迁移干净。**

现状失忆的根因：**治理状态（角色/记忆/决策/规则）和执行环境（Claude Code session）绑在一起**。Claude Code死 → 状态死 → 要复活。

迁移后的根因消除：**治理状态住在OpenClaw的长期进程里，和Claude Code session解耦**。Claude Code死100次也不影响治理层——因为治理层从来没死过。

残留的"失忆"只会发生在一个场景：**OpenClaw daemon本身crash**。这个用launchd auto-restart + `openclaw doctor` 健康检查 + 定期 `openclaw backup` 处理，是成熟问题，不是架构问题。

**一句话**: 这个架构把"失忆"从**架构缺陷**降级为**运维事故**，后者可以被基础设施解决，前者不能。

---

## 4. 我的建议

立刻开干，按Phase 1 → 2 → 3顺序。3天能跑通到"CEO常驻 + 能派Claude Code干活 + 能改hook规则"闭环。

Phase 4的4个其他agent可以分周推进，不阻塞主链路。

Board批准的话，我让Ryan Park（eng-platform）主导Phase 1-2的脚本化（他最熟 hook daemon 和 OpenClaw 集成），Leo Chen（eng-kernel）做 Phase 3 的 session.json 动态规则引擎。我自己盯Phase整体架构和集成测试。

两个请求：
1. **批准API预算**：CEO/CTO走Anthropic API约 $600-900/月（CFO细化）
2. **Phase 2的破坏性实验窗口**：Phase 2测试时需要真起 Claude Code headless，可能会动文件。建议在 `ystar-bridge-labs/` workspace 试跑，不动 `ystar-company/` 主线。

—— Ethan Wright, CTO
2026-04-11
